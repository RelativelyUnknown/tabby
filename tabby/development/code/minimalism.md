# Minimalism and names

Aim for the fewest concepts a reader must learn, not the fewest characters. Write like a senior engineer who golfs, never at the cost of clarity.

Every function, class, constant and exception is something a reader must look up. Each must earn its place.

The question for every piece you add: what does the reader lose if this is gone? If nothing, it is cost without value. Indirection (a wrapper, a hook, a constant, a base class) is worth it only when it hides a real decision or protects a rule that must stay consistent; "flexibility" nobody asked for is a guess about the future, paid for now. The lines below are that question applied to common cases.

- First ask whether it needs to exist. Then climb the ladder: what the project already has, the standard library, the community's standard library, and only then niche libraries or new code (the ladder is in "Reuse before you write" below). Skip options and flexibility nobody asked for, and name what you skipped in one line.
- Keep values in the form they arrive in. Do not convert a type, wrap a value or add a model class unless a rule needs enforcing there ([errors.md](errors.md)).
- A function must hide real logic or enforce a rule that has to stay consistent. Deletion test: if inlining it leaves every call site as short and clear, delete it. No one-line wrappers around expressions, stdlib calls or library methods (`def quote(s): return f'"{s}"'`).
- A method that never reads `self` is a function; a class with `__init__` and one method is a function. No wrapper classes that only forward; no ABCs, Protocols, factories or registries with one implementation; no parameters, options or hooks "for flexibility"; no `**kwargs` unless forwarding.
- Defaults are literals in the signature or the dataclass field (`timeout: float = 30`), so hovering over a function in an editor shows the value. No `DEFAULT_*` constant and no `DEFAULTS` dict standing in for a default, and "easy to change later" is no reason: a caller can pass the value and a developer edits one line. A constant is for a value the body uses; a value used once stays inline. Mutable defaults are never allowed: use `None` and build the object in the body.
- No `utils.py` or `helpers.py`; put code where it is used. No variable assigned only to be returned on the next line. No single-use type alias, base class or Enum "for consistency".
- Shorter only when also clearer: no nested comprehensions beyond one level, no walrus chains, no single-letter names outside tight loops.

- Names say what a thing is, in the codebase's vocabulary: `users`, not `user_list`. No vague names (`data`, `result`, `info`, `temp`, `obj`, `helper`, `manager`, `handler`), no `new_`/`old_`/`v2`/`final`/`fixed`/`robust`. Booleans read as predicates (`is_expired`). One word per concept: not `fetch`, `get` and `load` for the same thing.
- Core logic takes values and returns values; I/O and state stay at the edges. No module-level mutable state, singletons or global clients; pass dependencies in. Early returns over nesting. `with` for resources. Sets for membership checks in loops; batch queries and HTTP calls. Async code never calls blocking I/O, and a function that never awaits is not `async`.
- A shortcut with a known limit gets one comment: `# shortcut: <the limit>, <when to upgrade>` (for example `# shortcut: linear scan, move to an index past 10k rows`). A shortcut without a named trigger is a smell. The review lists them with `git grep -nE "# ?shortcut:"`.

## Write it right the first time

Slop is easier to avoid than to remove. While you write, not after:

- Before a helper, a constant or a class: `git grep` for the thing that already does it, and use that.
- A comment only for why; never for what the next line does. No "Step 1" or "now we...".
- Check inputs where untrusted data enters (a request, a file, a queue message). Code that only receives the project's own values does not re-check them; no `try`/`except` around a call that cannot fail in a way you can handle.
- If the type checker complains, fix the type. A cast, `Any` or `# type: ignore` to get past it is a smell of its own ([smells.md](smells.md)).
- Match the file you are in: its naming, its error style, its test layout. No reformatting of lines you did not change.
- Leave no scratch files, prints, commented-out code or half-finished branches behind.

Minimal applies to the solution, never to the job. Never cut: validation where untrusted data enters, error handling that prevents data loss, security checks, a test for new logic that can fail, anything the user asked for.

## Reuse before you write

Somebody has usually already written the thing well. Before writing a piece of code, ask which rung of the ladder answers the need, and take the highest rung that does the job well. What exists on each rung, job by job: [ecosystem.md](../ecosystem.md).

### The ladder

1. **What the project already uses** for the job: its validator, HTTP client, test tool, config loader. Use it. Do not add a second mechanism or rewrite working code to switch. A project with pydantic models gets a pydantic model; a project without pydantic does not get it for one function.
2. **The standard library**, when it does the job well.
3. **The community's standard library**: the libraries the ecosystem treats as its de facto standard for a job (an HTTP client, pydantic for structured input, pytest, numpy, SQLAlchemy, click or typer). Take one without apology when the standard library does not do the job well. This is a peer of rung 2, not an exception to it. In Rust, whose standard library is deliberately small, this rung is the norm (serde, thiserror, clap, tokio); in C++ it is fmt, abseil, Boost components.
4. **A niche library, or your own code.** The burden of proof is here. A niche library needs the vetting in [dependencies.md](../dependencies/dependencies.md). Your own code needs a reason: the job is a few lines, nothing above covers it, or the dependency would cost more than the code.

Rung 3 or rung 4? Signals, not a list: the ecosystem's own documentation points to it; most projects in that niche already depend on it; an organisation or several maintainers stand behind it; its API has stayed stable across versions; it is already installed because something you use needs it.

### Rules

- Do not hand-roll what rung 2 or 3 does well (HTTP with retries and pooling, time zones and free-form dates, hashing passwords, HTML sanitising, untrusted XML). Do not take a rung-3 library for a job rung 2 does in a few lines (two arguments to check: `if ... raise ValueError(...)`, not a model class).
- Never regex-parse a structured format: dates, URLs, HTML, JSON, CSV, versions. Quote for a shell, JSON or CSV with `shlex.quote`, `json.dumps` and `csv`, never by hand. Never write your own crypto, password hashing or token handling.
- Weigh the cost of a dependency: a dev-only one costs users nothing, a runtime one does. A library's dependencies become its users', so keep its base install small and put heavy ones in extras; an application or a single-file script may take more (PEP 723 `# /// script` declares a script's dependencies inline). Count install size, import time, transitive packages, licence and maintenance ([dependencies.md](../dependencies/dependencies.md)).
- When you add one, say so in the report: the package, the rung, the reason. Check that the exact name exists on the index before adding it.

### Validation ladder

- One function, one to three arguments: `if not ...: raise ValueError(f"unknown region {region!r}; expected one of {sorted(REGIONS)}")`
- A few related records you construct: a frozen dataclass with `__post_init__` checks
- Untrusted nested JSON, many models, coercion, error lists, schema output: pydantic, or the project's validator
- Config file: `tomllib` and a dataclass. Command-line arguments: argparse `type=` and `choices=`

Version-gated features follow [checking-apis.md](../workflow/checking-apis.md).

## Docstrings and comments

The one home for these rules; the self-review in the `review` module checks against them.

Write for a reader a year from now who never saw this conversation.

Ask what the reader cannot get from the code: the reason a choice was made, a constraint that is invisible, what a caller may rely on. Write that, and nothing the code already says. Anything that only makes sense with this conversation or this week's state belongs in the commit message, where it stays true.

- Say what a function does, returns and raises, in positive terms ("Return a new list", not "Don't modify the input"). The summary line follows the project's docstring convention: imperative under PEP 257 and numpydoc ("Return ..."), descriptive is allowed under Google style ("Returns ..."); never mix them. Do not restate the signature or types. Private and self-explanatory functions get no docstring. A module docstring is one line of purpose, or none.
- No conversation residue: "as discussed", "per requirements", "we decided", "intentionally", "now uses", "no longer", "previously", "changed from", "fixed". History and rationale go in the commit message.
- Leave existing comments and docstrings alone unless your change makes them wrong: do not delete, shorten or reword one you were not asked to change.
- Comments explain a non-obvious why; they never narrate the next line. A rule the code must keep is enforced by structure or a test, not a docstring. No references to internal docs, tickets or sections.
