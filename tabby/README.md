# tabby

The main skill of the Tabby plugin. It loads at the start of any Python code task (fix a bug, add a feature, refactor, add tests or types, speed something up, add a dependency, set up CI, cut a release, bind Rust, C, C++ or Zig) and holds the rules the agent always follows plus the reference pages for each area. Reviews, docs, diagrams and web pages use the sibling skills (`review`, `docs`, `diagrams`, `frontend`).

**Entry point:** [`SKILL.md`](SKILL.md) (a short router, about 95 lines). The pages are loaded one at a time, only for the area the task touches, so the agent reads a few hundred lines for a task, not the 75 files in this folder.

## How a task goes

1. **It runs `scripts/detect.py` once**, before reading project files. It reads files only and reports the runner, Python target, test, format, lint and type tools, the check command, CI, native parts and any existing helpers, so the agent uses the project's own tools and does not search for them. Output on a small project:

   ```
   - runner: none found
   - python: >=3.12
   - tests: pytest
   - format/lint: none found
   - check command: none found (read the CI steps)
   - house rules: src/ layout; no syntax newer than python >=3.12
   - project memory: no ## Tabby section; no AGENTS.md or CLAUDE.md
   ```
2. **It applies the "Never miss" rules**: done means run and verified, never edit or skip an existing test to get green, find the cause before the fix, no silencing the type checker, reuse before writing, smallest diff, use the project's tools. Three situations name a page to read before the first edit: a bug or failing test reads `development/workflow/debugging.md`; code that takes a URL, a path, an upload, SQL or shell input or a secret reads `development/code/input-and-secrets-security.md`; code that decides something (a permission, a price, a parser, a state transition) reads `development/testing/proof-based-testing.md` before the tests are written.
3. **It reads the page for each area the task reaches**, when it reaches it, and skips the rest.
4. **It reads the `## Tabby` section** if the project has one (see [`../interview/`](../interview/)) and lets it decide the design.

## What is in the folder

| Folder under `development/` | Read when the task | Pages |
| --- | --- | --- |
| `code/` | changes more than a few lines, adds a name, reads outside data, loops, raises or catches errors, opens files, uses threads, adds types, writes a script | smells, minimalism and reuse, foreseeable failures, concise code, errors and logging, security, files and locks, threads, types, outdated APIs, scripts, dataframes |
| `testing/` | writes or changes tests | basics and fixtures, smells, mocking, property tests and mutation, [`proof-based-testing.md`](development/testing/proof-based-testing.md), a [test-quality scorecard](development/testing/test-quality-scorecard.md) with a risk map, [flaky tests](development/testing/flaky-tests.md) |
| `workflow/` | fixes a bug, plans, refactors, removes something, has several outcomes or several readings | debugging, specs and slices (walking skeleton), refactoring, deprecation (expand, migrate, contract), pre-mortem, multi-outcome gates, shipping |
| `architecture/` | picks a pattern, data structure or design under real limits | patterns and layers, [coupling and connascence](development/architecture/coupling-and-connascence.md), [architecture fitness functions](development/architecture/architecture-fitness-functions.md), [parse, don't validate](development/architecture/parse-dont-validate.md), [sans-I/O cores](development/architecture/sans-io-core.md), data structures, limits, systems-project lessons |
| `dependencies/` | adds or chooses a package, touches CI or Docker | choosing dependencies, [dependency hygiene](development/dependencies/dependency-hygiene.md), uv workflows |
| `performance/` | is slow | profiling |
| `application/` | is an HTTP service, worker or scheduler | service smells, HTTP design, FastAPI and Django, async, settings, logging, database, deployment, retries and timeouts |
| `library/` | is a library others import, or Rust, C, C++ or Zig behind Python | public API, [public surface budget](development/library/shared/public-surface-budget.md), packaging, release, and one page per native language, porting a function and building wheels |
| `assets/` | needs a template | `Makefile`, `ci.yml`, `pyproject.toml`, `release.yml`, `tox.ini`, native build files |

Other pieces:

- [`references/growth.md`](references/growth.md): options and seams for a request that adds an API, queue, cache, ORM or async, or that a `growth:` item touches.
- [`references/memory-check.md`](references/memory-check.md): the drift check on the `## Tabby` section.
- [`scripts/detect.py`](scripts/detect.py): the project detection above.
- `development/stdlib-vs-community-libraries.md` and `development/project-kind-detection.md`: the reuse ladder and how a project's kind is decided.

## What it does not do

- It does not switch your tools. It uses your runner, formatter, linter, test framework and type checker, never Tabby's own preferences.
- It does not commit, push or change a public API unless asked, and it asks before adding a dependency when `ask-first:` says so.
- It does not interview you before a task. Without a `## Tabby` section it infers the project and marks guesses `(assumed)`.
- It does not review or document. A request to review a diff, write docs or draw a diagram loads the matching sibling skill.
