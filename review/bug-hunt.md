# Hunting bugs

A bug hunt asks the code questions and runs the answers. Reading a function and finding it plausible is how reviews miss things.

**Rules.**

- Start from what the project says must always be true (AGENTS.md, CLAUDE.md, `## Tabby`, ADRs, docstrings that state a rule, the tests that guard a past bug). A change that violates a stated invariant is a bug even when the code looks reasonable.
- Assume the change is broken and look for how. Distrust the comment, the commit message and the tests that say it is not: ask which assertions would still pass if the code were wrong, and whether a test was loosened to go green.
- Every finding is a failure scenario: an input or sequence, the bad outcome, and a `file:line`. "This could be cleaner" is not a finding.
- Run what you can as a throwaway test or one-liner in a scratch folder; never edit the code under review. A probe you did not run is a suspicion, and is labelled.
- Where the code reads data from outside (a file, export, API reply, user text, dates, money), go through the table in [foreseeable-failures](../tabby/development/code/foreseeable-failures.md) and report a missing guard that real data would hit.
- Try to refute each candidate before you report it; the default is refuted. Say "traced" or "ran", not "probably" or "likely"; where you cannot tell, say so and what would settle it.

Bugs that span two places (a check in one file, the use in another) are in "Two places that must agree" below; look for them before you stop.

## Follow the calls (the assumption audit)

For each function under review write down what must be true on entry (the argument's trust level, state read, who the caller is, the clock), what it promises on every path, and what it calls. Then read each callee in full and follow every path through it, not only the one that succeeds. A name is not a check: `session_lookup` suggests the session is live while it compares only the ID. For each assumption say what makes it true; if nothing does, write **nothing enforces it**. Those are the best leads. Keep a list of open questions instead of guessing.

Shapes this finds in Python:

- A lookup that matches identity but ignores state (`get(id=...)` returns a soft-deleted, closed or expired row).
- A function that returns success without setting what it was meant to set, or sets an out-value on the happy path only.
- One of two callers runs outside the lock or transaction the callee assumes. Two handlers that read-modify-write the same row with no transaction are coupled even though neither calls the other.
- A helper whose name and result disagree: `check_restricted(user, perm)` returns `True` when the user *has* the permission; a `return True` on the fall-through path; `or` where `and` was meant; an inverted `if not`.
- `None == None`: `order.owner_id == current_user.id` is `True` when an anonymous user and a guest order both have no ID.
- The same adjustment applied in two places for one event (a balance reduced when the exit is requested and again when it is processed).

## Probes

**Inputs.** Empty, one item, duplicates, a missing key, `None`, zero, negative, very large, `NaN`, whitespace only, very long, non-ASCII (combining marks, emoji), different case, a path with spaces or `..`. Dates: naive against aware, a DST change, 29 February, the 31st, month end, another offset.

**Boundaries.** Off by one at slice and range ends, inclusive against exclusive, `>` against `>=`, the last page of a paginated call, an empty last batch.

**State and order.** Called twice; called in another order; run again after a half-finished first run; the argument mutated by the callee; a mutable default; a module-level cache that outlives the test; an iterator consumed twice; a closure built in a loop.

**Status fields.** A status, a pair of booleans or a nullable timestamp that stands for a state: probe illegal combinations, repeated events and stuck states ([state-machines.md](state-machines.md)).

**Failure halfway.** The third of five calls raises: partial writes, a transaction too narrow or too wide, a resource not closed on the error path, a retry that repeats a side effect, an error swallowed into a default, a timeout that stops waiting but not the work, a secret cleared because of a transient failure.

**Contracts.** What do callers rely on that the change alters: the result on empty input (`None` or `[]`), ordering, the exception type, a default, sync against async, a removed name? Open the callers (`git grep`). Across a boundary: a signature changed on one side but not the other, a new route or command not registered, a missing permission, a migration without the matching code, docs that claim behaviour the code lacks.

**Concurrency.** Check then act; read-modify-write without a lock or transaction; two workers taking the same job; cancellation during an `await`; shutdown mid-job; a fork after threads started. Name the race window (microseconds or seconds), whether an attacker can widen it (a slow disk or network call, load, a symlink swapped between check and open), and whether a second thread or process can reach the data at all. Separate "impossible", "practically infeasible" and "feasible".

**Scale.** A query per item, quadratic work on caller-controlled input, an unbounded list, queue or cache, a whole file read into memory, a client created per request that should be shared.

**Unchecked results.** `subprocess.run` without `check=True`, an HTTP response whose status is never looked at, a function that returns an error value the caller ignores.

**Python traps.** Language behaviours that bite: see "Python traps worth probing" below.

## Native code (Rust, C, C++, Zig behind Python)

A panic or C++ exception crossing the boundary; `unwrap()` on caller data; integer overflow that wraps in release and panics in debug; `as` casts that truncate (a `len()` into `u32` is a finding even when inputs are unlikely: report it as minor, do not drop it); touching a Python object without the GIL, or holding it through a long call; a missing or extra reference count; a buffer that outlives its owner. See [native-boundary.md](native-boundary.md).

## Two places that must agree

Many serious bugs are not on any one line. A rule is enforced in one place and the value it protects is used in another, and they disagree. For each situation below: read both places, then confirm with the cheap probe.

- **Checked in one form, used in another.** The name is tested raw (or lowercased, stripped, unquoted) and a transformed copy (`unicodedata.normalize`, `unquote`, `resolve`, `.lower()`) reaches `open`, a query or a URL. Read: every transform between the check and the use. Confirm: build an input that is harmless before the transform and hostile after (fullwidth dots, `%2e%2e`, a trailing dot or space).
- **A string prefix standing in for a boundary.** `path.startswith("/srv/x")`, `host.endswith("example.com")`. Read: what else begins or ends that way (`/srv/x-private`, `evilexample.com`). Confirm: run the check on that sibling.
- **An identity copied across a hop.** A `user_id`, tenant or role taken from the request body or a header into a queue message, job argument, cache key or log, then trusted by the consumer. Read: where the value first enters and whether the session value replaces it. Confirm: enqueue another user's id and see whose data returns.
- **A check that a default turns off.** An env var read as a string (`"0"`, `"false"` are truthy), an empty key that means "skip", `None == None` when both sides can be absent. Read: the setting's default and how it is parsed. Confirm: `bool("0")`, or call with the field omitted.
- **A state field with several writers.** List every assignment to `status` (`git grep -n "\.status = "`), including jobs, webhooks and admin paths, and compare each with the transition table. A writer that skips the table is the bug.
- **A cache or memo key missing a dimension.** The value depends on the user, tenant, locale or auth state and the key is only a path or an id. Confirm: two users, same key.
- **Check, call, then write.** Read a balance or status, call out (payment, queue, HTTP), then update, with no lock, transaction or idempotency key. Two concurrent requests both pass the check. Confirm: reason through two interleavings, or run two threads against a stub.
- **A limit keyed on what the client chooses.** A rate limit or lockout keyed on a header, a cookie or a self-reported id. Confirm: change the key each request.

Report the pair, not one side: where it is checked, where it is used, and the input that gets between them.

## Python traps worth probing

Use them as probes: write the input, run it, report what happened.

- `os.environ` values are strings, so `"0"` is truthy; `argparse` `type=bool` turns `"False"` into `True`; JSON turns integer keys into strings and `json.dumps(float("nan"))` writes `NaN`, which is not valid JSON.
- `asyncio.gather` without `return_exceptions=True` raises the first error and leaves the other tasks running; a blocking call inside `async def` stalls every task; a task nothing references can be garbage-collected.
- `"{0.cfg.secret}".format(obj)` follows attributes, and through a function it reaches module globals (`{0.__init__.__globals__[__name__]}`): never use a user-supplied string as a `str.format` template. `getattr(obj, name)` with a request-supplied `name` reaches `__class__` and `__dict__`.
- `json.loads('{"admin": false, "admin": true}')` keeps the last duplicate key, so two parsers that disagree on duplicates can be played against each other; Python's JSON keys are case-sensitive. Plain dict parsing ignores unknown fields; use a model that forbids them.
- `re.match(r"^admin$", "admin\n")` matches because `$` also matches before a trailing newline; `re.fullmatch` and `\Z` do not. `"İ".lower()` is two code points and `"STRASSE".lower() == "straße".lower()` is false while `casefold()` makes them equal: compare identifiers exactly, or with `casefold()`. `len("👨‍👩‍👧‍👦")` is 7: slicing user text by code points can split a character.
- `Decimal(0.1)` carries the binary float (`0.1000000000000000055511151231257827…`); write `Decimal("0.1")`. Calling a coroutine without `await` runs nothing and only emits `RuntimeWarning: coroutine ... was never awaited`.
- `asyncio.CancelledError` is not an `Exception`, so `except Exception` lets cancellation through, while `except BaseException` or a bare `except` that does not re-raise swallows it and the task never ends as cancelled.

## Report

Open with the most likely way this breaks in production, in one sentence, then the findings. For each: file and line, the input or situation, the command you ran and what it printed, the smallest fix. Suspicions you could not run come last, labelled. Close with what you could not verify and why. If the probes find nothing, say which you ran; do not invent findings.
