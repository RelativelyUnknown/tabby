# Senior-level engineering: questions to ask, not stories to admire

Each section is a question to apply to a design you have not seen before; that is the point, not the stories that show it working. Illustrations are in senior-engineering.md (below); read one to check a doubt, not to learn the rule.

## Make invariants checkable, not implicit

Before trusting a value, ask: what must be true here for what follows to be correct? Turn the answer into a check, not a comment: a comment goes stale silently, a check fails loudly. Check it where the value enters your control, and again where its violation would do damage; the gap between the two is where a corrupted value travels unnoticed. State what must hold, not what must not ("if `index < count`" reads faster than its negation), and split a check that tests two things into two, so a failure says which one broke.

Check a property at two code paths (a pair assertion): validate an argument before it crosses into native code and check what comes back, or assert before a write and again after the read. Bound everything that can grow (queues, batches, retries, loops) so overload fails fast, and give names their unit last (`latency_ms_max`).

In Python this is `assert` for invariants a caller cannot violate ([errors.md](../code/errors.md) draws that line); in Rust, `debug_assert!` plus a real `assert!` where a release build must still catch it; in C, `assert()`, compiled out by `NDEBUG`, so a caller-triggerable violation needs a real error path, not just a check.

## Know every limit before you can measure one

A design touches real limits before any code exists to profile: queue depth, cache size, a connection pool, memory bandwidth. For each resource it depends on, ask: what is the actual number, and what happens at and past it? Unknown, find it (the spec, the source, a five-minute sketch) rather than learn it from an incident. Make "past the limit" a defined, observable event (a rejected request, an assertion, a degraded mode), never silent truncation or unbounded growth.

[fit.md](fit.md) applies this to one case, choosing a data structure: know the workload and its bound first, and make outgrowing it loud and cheap to fix. The same question reaches one level further down, to the hardware or runtime underneath, not only the structures built on it.

## Shrink what has to be trusted without proof

Some code cannot be checked by a compiler or type system: a raw pointer cast, manual memory access, hand-built SQL, a type-checker override. There the question is not "is this correct?" (you cannot fully know) but "how small can the part that has to be right be, and can I write down what must hold for it to be right?" Wrap it in the smallest function, state the precondition where declared and restate why it holds where used, and keep every caller on the normally-checked side of that line. Only one small, marked place should need a human to verify it by reading.

See [library/native/rust.md](../library/native/rust.md) and [library/native/c.md](../library/native/c.md) for this project's own rules for `unsafe`; this is why those rules take the shape they do.

## Decide your own pace instead of reacting to someone else's

For code that reacts to external events one at a time (requests, messages, callbacks), ask who decides when the work happens: the caller, or you? If the caller does, every event costs a context switch and your worst-case latency follows their timing. Where you can, pull events into a loop you control: batch related work, defer what can wait, give the processor large predictable chunks instead of many small interruptions. Not "add a queue everywhere": a question for whenever something external is forcing a reaction.

## Name the layer you are really fixing, and write its expiry date

Before writing a workaround for something broken or slow one layer below (a compiler, a library, the OS), name which layer owns the defect and what change would make the workaround unnecessary; write both down next to the fix as a condition to check later. No trigger means it becomes permanent, because nothing prompts a revisit; this is the general form of the `# shortcut:` convention in [code/minimalism.md](../code/minimalism.md).

The same applies to solving by search instead of understanding (autotuning, trial and error): a legitimate first answer when you cannot yet calculate the result directly, but a debt against your own incomplete model. Once you understand the system, prefer the closed-form answer: faster, more predictable, with no search budget to run out.

## Say why, every time

A decision explained is a decision the next reader can evaluate, not just obey. Costs nothing, always applies: every ADR (`history/adr.md` in the `tabby-docs` skill), every `# shortcut:` comment, every rejected alternative in [fit.md](fit.md) is this rule in practice.

## Before importing a rule from elsewhere, name its workload

A constraint from an admired codebase answers a question you have not asked yet. State in one sentence which workload and failure mode it solved there before adopting it; if you cannot, leave it out rather than carry it over because the source is well regarded.

## Senior-level engineering: illustrations

Real code for each question in the section below. Read one to settle a doubt about how a rule looks in practice; the rule in that file is the instruction, this file is evidence.

### Make invariants checkable, not implicit

TigerBeetle's style guide targets an average of two assertions per function, pairs them across a boundary (validity checked right before a write and again right after the matching read), and states the positive form of each invariant. ruff's `RuleSet` bitset carries a `debug_assert!` that fires the first time a rule id does not fit the array, naming the fix in the message ("Increase the size of the bitset array") instead of failing silently.

### Know every limit before you can measure one

TigerBeetle bounds every loop and queue and sketches network, disk, memory and CPU cost at design time, before any profiler runs. DeepSeek's FlashMLA Ascend kernels show the same question asked one level lower, against real hardware: the instruction cache is 8K to 32K depending on the core, so code size became a hard budget on purpose; the hardware issues instructions in order on each pipe, so the issue sequence had to be designed around that fact rather than discovered by a race; per-token copy requests would have exceeded the hardware's request queue depth, so requests were batched ("gather2") to stay under it; tensors were split across both halves of a banked on-chip memory, with padding added, specifically to avoid a bank conflict. None of the numbers transfer to another chip; the habit of reading the real limit first does.

### Shrink what has to be trusted without proof

polars pairs nearly every unchecked accessor with a safe, bounds-checked twin (`get` beside `get_unchecked`), states the precondition under a `# Safety` heading ("It is the caller's responsibility that `idx < self.len()`"), and keeps the `unsafe` block itself to the one call that needs it. Spark's `Platform` class concentrates every `sun.misc.Unsafe` call used by the whole engine behind one small set of static methods, queried for platform capability once; `UnsafeRow` then builds a documented binary row layout on top of that single audited seam, so the SQL engine touches raw memory through one place instead of many.

### Decide your own pace instead of reacting to someone else's

TigerBeetle's own rule: do not react directly to external events; run your own loop and decide when to look at them, which both keeps control flow under your control and lets you batch instead of context-switching on every one. DeepSeek's DualPipe schedules a bidirectional pipeline specifically so forward and backward passes, and their communication, overlap instead of stalling on each other, deciding the schedule up front rather than letting arrival order decide it. FlashMLA's "gather2" batching is the same move at the hardware-request level.

### Name the layer you are really fixing, and write its expiry date

DeepGEMM's own changelog records a manual low-level instruction-scheduling pass that used to be needed by hand; once a newer compiler release did that scheduling automatically, the manual pass was dropped. DeepEP shows the companion habit: an earlier version autotuned how many streaming multiprocessors and queue pairs a communication kernel should use; once the team understood the relationship well enough, a later version replaced that search with a direct analytical calculation of the same numbers.

### What this is not

TigerBeetle's "zero dynamic allocation after startup" and 70-line function limit are real constraints for the embedded, safety-critical systems they were written for. They are evidence that constraints taken seriously produce good design, not a Python rule to copy; see the last question in senior-engineering.md (below).
