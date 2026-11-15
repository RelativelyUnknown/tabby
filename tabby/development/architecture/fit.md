# Design fit: the structure that fits the workload and the plans

A smart design often beats clever code. The right data structure, representation or algorithm depends on facts that are not in the function you are editing: the workload, the constraints, and the project's past, present and future. Tabby holds those facts; use them. Without them, take the plain structure, say what you assumed, and ask when a wrong guess would be expensive to undo. This applies to Rust, C and C++ below the Python boundary, and to Python above it.

## What to know before choosing

- **Workload, in numbers.** How many items and how big; reads against writes; lookup, iteration or set algebra; hot or cold path; lifetime (per request or the whole program); threads. Measured is best; assumed is fine if labelled.
- **Constraints.** Memory and latency budgets, platforms, determinism, `no_std`, and the Python boundary: across it pass flat buffers and integer ids, not objects.
- **The past.** Why it is shaped this way: ADRs, `git log -S<name>`, `git blame`, comments. A structure that looks wasteful may encode a constraint you cannot see, so find the reason before replacing it ([refactoring.md](../workflow/refactoring.md)).
- **The future.** `growth:` and `constraints:` in `## Tabby`. Know what is expensive to change later (a public API, an on-disk or wire format, an FFI layout) and what is cheap (private internals).

## Method

1. State the workload in one sentence with numbers.
2. Start from the plain structure (list, dict, struct). Keep it unless the workload says it fails; decide from sizes and a measurement, not from taste.
3. Read the shape of the data against the table below: dense small ids, a fixed or bounded universe, mostly small, mostly read-only, many cross-references, repeated strings.
4. Say when the choice stops fitting, make that failure loud and cheap to fix (one constant, one module). Add both pieces: an assertion on the size, and a test that builds the structure from every variant or id and checks each one.
5. Hide it behind a small interface; use typed ids, not bare integers.
6. Record the assumed workload, the alternatives you rejected and the trigger to revisit, in one comment or ADR (`# shortcut:` for a known limit).

## Fit table

| Data shape | Structure | Stops fitting when |
| --- | --- | --- |
| A fixed, dense universe of small ids; membership and set algebra dominate | bitset: `[u64; N]`, `bitflags`, `std::bitset<N>` | the universe is large, sparse or unbounded: use a hash set or a compressed bitmap |
| Records that refer to each other | an index or typed id into a `Vec` instead of pointers: `IndexVec`, arrays plus indices | records are removed and ids reused: add generations (`slotmap`) |
| Mostly tiny, occasionally large | a packed or inline fast path with a full fallback: `smallvec`, LLVM `SmallVector`, a `u64` for the common case | the "small" case stops being the common one |
| A boolean or null flag per value, in bulk | a bit-packed mask | per-element mutation dominates: use a mutable builder |
| Many equal strings or tokens | interning: id to string table | ids must outlive the table |
| Many short-lived allocations that die together | an arena or bump allocator | objects need individual lifetimes |
| A key set known at build time | a static table: sorted array, `match`, perfect hash | the keys change at runtime |
| Hot lookups of one key type | a hash table specialised for that type | keys are heterogeneous |

## The same reasoning applies elsewhere

Algorithm (batch or stream, sort or partition), layout (struct of arrays or array of structs, columnar), caching against recomputing, error representation (an enum or an exception), API shape (a builder or an options struct). Same inputs, same record.

## Smells

- A structure chosen with no stated workload ("faster", with no numbers).
- A clever structure for a few dozen elements.
- A representation that leaks into a public or FFI signature.
- A structure with no loud failure when the data outgrows it.
- A bare integer standing in for an id of a particular table.

Worked examples from real code: the section below.

## Design fit: worked examples

Real code, read from the repositories. Each example gives the workload, the structure, why it fits, and what keeps it honest as the project changes.

### ruff `RuleSet` (Rust): a bitset for a fixed universe

- **Workload.** A fixed enum of rules, each with a dense small id (`Rule as u16`). Sets of rules are built from selectors with union and subtraction, and membership is asked for constantly.
- **Structure.** `RuleSet([u64; 16])`: bit `id % 64` of word `id / 64`. Union and subtract are word-wise `|` and `& !`; `len` sums `count_ones`; iteration takes the lowest set bit of each word and clears it. `contains`, `union` and `subtract` are `#[inline] const fn` (written with `while`, because `for` is not allowed in `const`).
- **Why it fits.** The universe is dense and bounded; a set is a small value (128 bytes) that is `Clone`, `Eq` and hashable for free, with no allocation and almost no branching.
- **What keeps it honest.** 16 words is 1,024 ids. A `debug_assert!` fails with "Increase the size of the bitset array" the first time an id does not fit, and a test builds a set from every rule and checks that iteration returns them all in order. The one `unsafe` (`transmute` from `u16` to `Rule`) carries a `SAFETY:` comment resting on the invariant that only valid rules are stored. The future (more rules) is a loud failure and one constant.
- **Stops fitting** when ids are sparse or unbounded, or sets hold one or two elements.

### ruff `IndexVec` (Rust): ids that cannot be mixed up

`IndexVec<I, T>` is a `#[repr(transparent)]` wrapper over `Vec<T>` indexed by a newtype `I: Idx` (the crate says it is inspired by `rustc_index`). Records refer to each other by index, not reference; an id of one table cannot index another table, because the types differ, at no runtime cost. Stops fitting when records are deleted and ids reused: add generations.

### uv `Version` (Rust): a packed fast path with a full fallback

- **Workload (the code's own comment).** Resolution compares versions constantly, and almost all versions are small: epoch 0, at most four release segments, no local part, at most one pre, dev or post component.
- **Structure.** `enum VersionInner { Small, Full }`. `VersionSmall` packs those versions into one `u64`, laid out so that `u64::cmp` equals PEP 440 ordering. Its setters return `false` when a value does not fit, and the caller switches to the `Full` form (an `Arc`). A `NonZero<u8>` niche keeps the enum at two words.
- **Why it fits.** The common case is small and hot, the rare case stays correct, and the choice hides behind `Version`.
- **What keeps it honest.** The comment records the limits and why they were chosen, and an earlier encoding that was abandoned after a bug (`1.0dev1 > 1.0a1`). That record is the project's past, written where the next maintainer will read it.

### polars `Bitmap` (Rust): one bit per value

A column of millions of values may be null in places. The validity mask is semantically `Arc<Vec<bool>>`, stored as bytes with one bit per value plus an offset and a length so slicing copies nothing: eight times smaller than a byte per flag. Building one by pushing values uses the mutable twin, `MutableBitmap`: the immutable form is for sharing, the mutable form for construction.

### pandas `khash` (C): one hash table, specialised per type

pandas vendors klib's `khash.h` and generates a typed hash table for each dtype (`Int64`, `Float64`, `String`, `UInt8` and others) from one template, `hashtable_class_helper.pxi.in`. Hot lookups on a single key type avoid boxing and indirect comparison. Stops fitting when keys are heterogeneous: pandas keeps an object table for those.

### Same choices in other languages

Names to look up, not verified here. C++: `std::bitset<N>` (size fixed at compile time), `boost::dynamic_bitset` (sized at run time), LLVM `SmallVector`. Rust: `bitflags`, `smallvec`, `slotmap`, `bumpalo`, `indexmap`. C: arrays plus indices, arena allocators, `uint64_t` arrays as bitsets. Python: an `int` as a bitmask or `enum.IntFlag`, `array`, `memoryview`, `__slots__`.
