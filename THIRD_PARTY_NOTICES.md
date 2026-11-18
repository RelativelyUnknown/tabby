# Third-party notices

Tabby's own text, code and pictures are MIT-licensed (see `LICENSE`). It was written after reading a lot of other people's work and using a lot of other people's tools, and this page says what came from where.

There are three kinds of debt, and the page is ordered by how much each one binds us:

1. **Files shipped with the package.** Two fonts and an icon set. Their licences travel with them, in the folders named below.
2. **Text adapted from another project.** One source, wshobson/agents. Its copyright line is repeated here, and the MIT licence requires that notice to stay with any copy of the adapted pages.
3. **Ideas only.** Everything else. Each idea was restated in Tabby's own words for Python (and Rust, C, C++ and Zig behind it); no text, example, image or code was copied. The sources are listed as credit, not because a licence asks for it.

A fourth section lists the tools used to build and check the package. None of them is a dependency of Tabby or ships in it.

## At a glance

| Kind | Source | Licence | Where it shows up |
| --- | --- | --- | --- |
| Shipped | Fredoka (font) | SIL OFL 1.1 | `assets/src/fonts/`, used to render the banner |
| Shipped | JetBrains Mono (font) | SIL OFL 1.1 | `assets/src/fonts/`, used to render the banner |
| Shipped | Tabler Icons (outline set) | MIT | `diagrams/assets/icons/` |
| Adapted text | wshobson/agents, python-development plugin | MIT | thirteen pages under `tabby/development/` |
| Ideas | many repositories, guides and talks | various | the pages named in sections 3 and 4 |

## 1. Shipped with the package

- **Fredoka** (SIL Open Font License 1.1, copyright 2016 The Fredoka Project Authors, https://github.com/hafontia/Fredoka-One). File: `assets/src/fonts/Fredoka-Variable.ttf`; licence: `assets/src/fonts/OFL-Fredoka.txt`. It renders the lettering in the README banner and the animated cards, and nothing else.
- **JetBrains Mono** (SIL Open Font License 1.1, copyright 2020 The JetBrains Mono Project Authors, https://github.com/JetBrains/JetBrainsMono). File: `assets/src/fonts/JetBrainsMono-Variable.ttf`; licence: `assets/src/fonts/OFL-JetBrainsMono.txt`. It renders the terminal text in the banner and logo. The ASCII cat is original.
- **Tabler Icons** (MIT, copyright (c) 2020-2026 Pawel Kuna, https://github.com/tabler/tabler-icons). The outline set is vendored as one JSON file, `diagrams/assets/icons/tabler-outline.json`, with its licence in `diagrams/assets/icons/LICENSE.tabler`. The diagram builder draws its icon tiles from it.

An earlier version of the banner used "Pizza is my FAVORITE Font" by Kimberly Geswein (freeware). It is no longer used and the font file was never in the repository.

## 2. Text adapted from wshobson/agents

- Upstream: https://github.com/wshobson/agents, the `python-development` plugin.
- Copyright (c) 2024 Seth Hobson, MIT License. Read at commit `4bde3168b43c0655c4d00ea2726e631719908a6d`.
- `provenance/development-SOURCE.md` records the upstream URL, the pinned commit and what changed on each page. The unmodified upstream skills are not in this repository.

| Upstream skill | Adapted into |
| --- | --- |
| `python-resource-management` | `tabby/development/code/files-connections-locks.md` |
| `python-type-safety` | `tabby/development/code/type-annotations.md` |
| `uv-package-manager` | `tabby/development/dependencies/uv-workflows-ci-docker.md` |
| `async-python-patterns` | `tabby/development/application/shared/async-io-and-patterns.md` |
| `python-observability` | `tabby/development/application/shared/logging-metrics-tracing.md` |
| `python-configuration` | `tabby/development/application/shared/settings-and-secrets.md` |
| `python-resilience` | `tabby/development/application/shared/retries-timeouts-circuit-breakers.md` |
| `python-error-handling` | `tabby/development/code/errors-validation-logging.md` |
| `python-design-patterns` | `tabby/development/architecture/design-patterns-and-layers.md` (three principles) |
| `python-testing-patterns` | one section of `tabby/development/testing/test-mocking.md`; the rest was already covered |
| `python-performance-optimization` | `tabby/development/performance/performance-profiling.md`; the profiler tutorial was not copied |
| `python-packaging`, `python-project-structure` | `tabby/development/library/shared/package-layout-and-versioning.md` and `build-and-lint-tooling.md`; the rest was already covered |
| `python-code-style` | a pointer only; nothing copied |

## 3. Ideas from other skill collections and agent repositories

Each entry says what idea was taken and where it went. Licences are as the repository states them; where none is stated, only the idea was taken.

### Writing less, and reviewing what was written

- **DietrichGebert/ponytail** (MIT): ask first whether the code needs to exist; a list of what minimalism never cuts; code that is moved keeps its checks; review against the expected load; a marked shortcut is a decision, not a defect; audit order (bug, risk, load, test, speed, lean); a ledger of shortcut markers. In `tabby/development/code/minimalism-reuse-names.md`, `tabby/development/workflow/refactoring.md`, `review/changes/self-review.md`, `review/repo-audit.md` and the `debt` skill.
- **JuliusBrussee/caveman** (Apache-2.0): when short replies must become full sentences; existing comments are not yours to shorten; why-first commit messages. In `tabby/development/workflow/planning-scope-and-shipping.md`, `tabby/development/code/minimalism-reuse-names.md` and `docs/readme-changelog-commits.md`.
- **joe-bell/cva `deslop`** (Apache-2.0), **pedronauck/skills `deslop`**, **boraoztunc/skills `adversarial-review`** (the last two state no licence): the accidental-complexity list and what to keep; assume the change is broken, distrust tests and comments, end with what was not verified. In `code/minimalism-reuse-names.md` and `review/changes/self-review.md`.
- **CodeAesthetic and ArjanCodes videos**: flatten nesting with early returns and a depth ceiling; named constants and conditions instead of comments; abstraction is coupling, so abstract at the third variant; code smells and low coupling. In `tabby/development/code/code-smells.md`, the rubric in `tools/eval/judge.py` and the nesting metric in `tools/eval/quality.py`. See section 6 for how these were read.

### Security, bugs and debugging

- **cloudflare/security-audit-skill** (MIT): the boundary-and-result requirement, a source-to-sink trace, an attempt to disprove each candidate, confirmed / needs-validation / rejected buckets with severity only for confirmed findings, a fix with a regression test; CI configuration as authorisation code; the boundary table and FFI bug classes behind `review/native-boundary.md`. In `review/security-audit/`.
- **getsentry/skills** (Apache-2.0, copyright 2025 Functional Software, Inc.): confidence tiers; attacker-controlled against server-controlled data; a check in any layer counts but must hold on every path; the outsider threat model for CI; expression injection only inside `run:`; pin third-party actions only where the job is privileged. In `review/security-audit/`, `review/bug-hunt.md` and the CI pages.
- **trailofbits/skills** (the plugins state CC BY-SA 4.0 in their README; ideas only, restated): differential review, false-positive checks, variant analysis, post-patch validation, sharp edges and insecure defaults, mutation and property-based testing, constant-time and zeroisation review for native code. In `review/`, `tabby/development/testing/test-rigor-property-and-release.md`, `workflow/debugging.md` and `code/input-and-secrets-security.md`.
- **anthropics/claude-code-security-review** (MIT, copyright (c) 2025 Anthropic): report only confident, newly added problems, with an exclusion list for low-value findings.
- **stas00/the-art-of-debugging** (CC BY-SA 4.0, ideas only): a fast one-command reproduction loop with inline environment variables, confirming that the code you edited is the code that runs, bisecting, the timing effect of observing, post-mortem debugging. In `tabby/development/workflow/debugging.md`.
- **adamentwistle/fable-skills `edge-case-sweep`** (MIT, copyright 2026 Adam Entwistle): handle, reject loudly or note each foreseeable failure; "handled" needs an observed run; do not guard inputs the code cannot receive; the checklist families. In `tabby/development/code/foreseeable-failures.md`. **getsentry/warden** (Functional Source License) confirmed three high-signal Python patterns; nothing copied.
- **TigerBeetle** (Apache-2.0): pair assertions, bounds on everything, deterministic simulation and fault injection, one core with many callers. In `tabby/development/testing/test-rigor-property-and-release.md`, `architecture/design-under-real-limits.md` and `library/native/native-extension-architecture.md`.

### Native extensions

- **OoriData/Amara `python-c`** (Apache-2.0): when to go native, interface choice, a visible pure-Python fallback, modern C-API hygiene.
- **pganssle/dotfiles** (Apache-2.0): CPython C review rules (fallible calls, borrowed references, GC lifecycle slots). The persona framing is not used.
- **VincentChuWaiChow/vanguard-frontier-agentic `python-native-extension-interop`** (Apache-2.0): severity-ordered review of reference ownership, buffers and exception translation.
- **morganlinton/BeautifulRust** (MIT): rules for a PyO3-free core crate, listing observable behaviour including the quiet parts, porting the tests first, keeping and flagging the original's bugs, and a lints block (run under clippy). In `tabby/development/library/native/native-rust.md`, `native-porting-a-function.md` and `tabby/development/assets/native/Cargo.lints.toml`.
- **wjakob/nanobind** and **pybind/pybind11** (BSD-3-Clause): the C++ page was written from their documentation. In `native-cpp.md`.
- **NumPy** and **pandas** (BSD-3-Clause): C error paths, overflow-checked sizes, `Python.h` first, banned borrowed-reference calls, the sanitizer and `-Werror` CI split. In `native-c.md` and `native-ci-wheels.md`.
- **Linux kernel documentation** (GPL-2.0; only the process and dev-tools pages were read, nothing copied): goto cleanup, return conventions, no `strcpy` or VLAs, disclosure rules for generated content. In `native-c.md` and `docs/readme-changelog-commits.md`.
- **ghostty-org/ghostty** (MIT): what a large Zig codebase does (tests everywhere, `errdefer`, arenas), uniform C-API rules (result codes with out-parameters, NULL handles return an error, enum values fixed, a max-value sentinel), data layout (offsets instead of pointers, zero as a valid empty state, a generation number on handles), and a targeted-test form for the `commands:` line of project memory. In `native-zig.md`, `native-c.md` and `native-extension-architecture.md`. Its AI policy was not adopted.
- **Layouts and CI practice studied, file trees and build files only**: astral-sh/uv and ruff, pola-rs/polars, pydantic/pydantic-core, ijl/orjson, pyca/cryptography, jcrist/msgspec.

### Planning, workflow and project memory

- **addyosmani/agent-skills** (MIT): observable behaviour becomes contract; a state-dependent record as a union; when to write an ADR; details that must survive an edit; a timeout is an unknown outcome; a short spec with boundaries and success criteria; thin vertical slices; deprecation questions (advisory against compulsory, strangler, code nobody owns); interview cadence for the `interview` skill. In `tabby/development/library/shared/public-api-design.md`, `workflow/specs-and-slices.md`, `workflow/deprecation-and-migration.md`, `application/shared/retries-timeouts-circuit-breakers.md`, `docs/project-docs.md` and `docs/voice-and-style.md`.
- **pbakaus/impeccable** (Apache-2.0): context before visuals; a list of known defaults to refuse; a detector that runs in code with exit codes; critique split into judgment and detector assessments. In `frontend/interfaces/` and `review/design.md`.
- **Leonxlnx/unlazy** (MIT): acceptance gates written before the work, each with a runnable check and an expected result; gates that cannot fail are linted; the request is re-read and every claim re-measured before reporting. In `tabby/development/workflow/multi-outcome-gates.md`.
- **github/awesome-copilot** (MIT): a refactor plan with rollback and risks; both sides of a docs mismatch. In `workflow/refactoring.md` and `docs/drift.md`.
- **mukul975/Anthropic-Cybersecurity-Skills** (Apache-2.0): dependency-confusion and typosquat checks, as pointers. In `review/security-audit/supply-chain.md`.
- **Skill-authoring guidance**: Anthropic's skill authoring best practices and community guides on skill loading. The lesson: pointers written as conditions ("before the first edit, read X when the task does Y"), not a topic menu, and no hedged "if needed" wording.

### Diagrams, animation and interfaces

- **cathrynlavery/diagram-design** and **caru-ini/stack-diagram** (MIT): node treatment by role; connector rules (orthogonal elbows, a gap before labels, no overlaps, one attach point per connector); per-type node budgets; a 4 px grid; labelled group containers; a node is its tile plus its text; a pictogram for an abstract node, never emoji; mechanical geometry and accessibility checks; render in both themes and look before delivering. In `diagrams/diagrams/` and `diagrams/assets/diagram/`.
- **Leonxlnx/taste-skill** (MIT): diagrams as small specs with a few layouts (hub, lanes, fan-in, sync, timeline); every motion gets a written purpose or is cut; a finish gate that runs the checker in a real browser, with documented waivers; a copy-slop vocabulary. In `diagrams/animation/` and `frontend/interfaces/`.
- **lemomo-ai/lemo-opuscar** (docs CC BY-NC 4.0, code MIT; ideas only): each frame is a pure function of time and recorded frame by frame; one timeline drives every move; anticipation, action and follow-through; a hook early in the loop. In `tools/readme_film/`.

### Process ideas used for this package's own pages

- **Proof-based testing** (`tabby/development/testing/proof-based-testing.md`): laws written as if-and-only-if before the code, from Bend 2's `LAWS.bend` and Microsoft/GitHub Next's PDD Kit.
- The pages added with the coupling, test-quality, flaky-test, dependency and migration guidance draw on well-known ideas, listed in section 4.

## 4. Ideas from books, articles and tool documentation

Written from general knowledge of these ideas and from the tools' own documentation; nothing copied. The names are credit.

| Idea | Credit | Page |
| --- | --- | --- |
| Connascence, as a vocabulary for kinds of coupling | Meilir Page-Jones; popularised by Jim Weirich | `tabby/development/architecture/coupling-and-connascence.md` |
| Architectural fitness functions | Neal Ford, Rebecca Parsons and Patrick Kua, *Building Evolutionary Architectures* | `architecture-fitness-functions.md` |
| Parse, don't validate; making illegal states unrepresentable | Alexis King; Yaron Minsky | `parse-dont-validate.md` |
| Sans-I/O protocol cores | the sans-io project; the h11, wsproto and h2 libraries as examples | `sans-io-core.md` |
| Hyrum's law | Hyrum Wright | `tabby/development/library/shared/public-surface-budget.md` |
| Expand and contract (parallel change) | Joshua Kerievsky; common database-migration practice | `workflow/deprecation-and-migration.md` |
| Walking skeleton and tracer bullet | Alistair Cockburn; Andrew Hunt and David Thomas | `workflow/specs-and-slices.md` |
| Chesterton's fence | G. K. Chesterton | `workflow/refactoring.md` |
| Pre-mortem | Gary Klein | `workflow/planning-scope-and-shipping.md` |
| Mutation testing as a test-quality check | the mutation-testing literature; the tools below | `testing/test-quality-scorecard.md` |

## 5. Tools used to build and check the package

Not dependencies and not shipped. They were run here to make and verify the pages and the cards, and commands quoted on the pages were run with them.

| Tool | Licence | Used for |
| --- | --- | --- |
| Claude Code and `claude plugin eval` | Anthropic's terms | running the eval cases, with and without Tabby |
| Playwright with Chromium | Apache-2.0 | rendering the animated README cards and the logo |
| FFmpeg with libwebp | LGPL-2.1+ / BSD | encoding the animated WebP files (looping forever) |
| CPython 3.13, gcc, rustc and clippy | PSF, GPL, MIT/Apache-2.0 | running the Python, C and Rust behaviours cited on the review and native pages |
| uv and pytest | MIT / Apache-2.0 | the project runner and the test runner in fixtures and checks |
| Hypothesis (6.170.15) | MPL-2.0 | the property-testing examples |
| CrossHair (crosshair-tool 0.0.113) | MIT | the solver-search example in `proof-based-testing.md` |
| hypothesis-crosshair (0.0.32) | see its repository | the Hypothesis backend that runs CrossHair, same page |
| mutmut (3.8.1) | BSD-3-Clause | the mutation audit in `proof-based-testing.md` |
| import-linter (2.16) | BSD-2-Clause | the layering contracts in `architecture-fitness-functions.md` |
| deptry (0.25.1) and vulture (2.16) | MIT | the dependency and dead-code checks in `dependency-hygiene.md` |
| griffe (2.4.1) | ISC | the public-API comparison in `public-surface-budget.md` |

Versions are the ones the quoted output came from. The GitHub Actions behaviour, Semgrep's file-size skipping and Python 3.14 `pdb` attach were not run and are marked as such on their pages.

## 6. How the sources were read

- Most repositories were cloned and the files named above were opened and read in full. Shallow clones were used for the large ones (TigerBeetle, NumPy, pandas, Linux, Ghostty); for Linux only the process and dev-tools documentation was checked out.
- Not read, and so not used: orchestration code, report generators and runners of the Trail of Bits plugins; the compiler-pipeline pages of `zeroize-audit`; smart-contract references; CodeQL and SARIF skills.
- The CodeAesthetic and ArjanCodes material was read through third-party summaries and an example repository, not by watching the videos, so details may be off. Two of those items had no usable source and nothing was taken. Five Tsoding Daily and aarthificial streams had no transcript or write-up anywhere public, so nothing was taken from them. YouTube blocks transcript requests from the build network, and no block-evasion was attempted.
- Where a source claim was wrong, or could not be confirmed by running it, it was left out. Where a source and a run disagreed, the run won (the Python bytecode table in the constant-time material is one example). Claims that were run are marked "checked" on their pages.

### Read, nothing taken

blader/humanizer (MIT), softaworks/agent-toolkit `writing-clearly-and-concisely` (MIT), heydamir/unslop (CC BY 4.0; its copy rules are already in `docs/voice-and-style.md`), vercel-labs/agent-skills (no licence file; its one-rule-per-file layout was weighed against Tabby's smells lists and not adopted), ComposioHQ/awesome-claude-skills, olshansk/agent-skills `cmd-pr-edgecase`, and wshobson `python-anti-patterns` (already covered by `code-smells.md`). Earlier unmodified copies of humanizer, writing-clearly-and-concisely and the wshobson Python skills were removed from the repository.
