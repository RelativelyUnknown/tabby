# Tabby core: Python work

These rules apply to every Python change. They are the habits a strong model skips by default. Domain detail lives in the Tabby skills. Load the matching skill at the start of the task (`tabby` for Python changes, `tabby-review`, `tabby-docs`, `tabby-diagrams`, `tabby-frontend`), then read only the pages it names for the area you touch.

1. **Solve the real problem and verify it.** Name the command that proves the claim, run it fresh, read the exit code and failure count, then report the result. If you could not run it, say so. Run targeted tests while iterating and the full check once at the end.
2. **Leave existing tests alone.** Do not edit, delete, skip or loosen one to get green. If a test contradicts the spec, finish the rest and report it. A bug fix starts with a failing test that you watch fail. When the user changes a requirement ("Apple-only must work"), a test that pins the old behaviour is updated to the new one in the same change and named in the reply; never leave the requested behaviour unbuilt to keep an old test or message intact.
3. **Find the cause before the fix.** No special-casing inputs, no sleeps or retries that hide a symptom. When asked to raise a timeout or limit so a failure stops, first check why it fails.
4. **Fix tool complaints properly.** Do not add `# type: ignore`, `# noqa`, `Any`, `cast(` or looser config. Narrow the type, fix the code, or explain a justified exception in the line. An existing suppression that already states its reason stays; remove only the bare ones.
5. **Ask when the request is vague.** "Make the reports better" gets one to three short questions with suggested answers before any edit. A request that names the change is done, not discussed.
6. **Reuse before writing.** `git grep` for an existing helper first. Then the standard library, then a dependency already installed, then the community standard, and only then new code. Say which rung you took. For HTTP with retries and pooling, free-form dates or validation, take the community rung and name it; approval is needed only when the project's `ask-first:` line says so.
7. **Smallest diff that solves it.** Every changed line traces to the request. Remove only what your change made unused. Match the style of the file around it. Small does not mean incomplete: a tool others will use needs its README line, clear errors for missing input and the obvious crash path handled, and a similar earlier change (`git show`) lists the files this one must touch (tests, docs, changelog, completions). Do them; do not offer them. No narrating comments, no defensive checks on data your own code produced.
8. **Use the project's own tools.** Runner, formatter, linter, type checker and Python target come from its lock file, Makefile or CI. Do not swap one, add a second, or install silently.
9. **Public names are promises.** Removing or renaming one is a deprecation unless nothing outside the repo can use it. A public API change, a commit or a push happens only when asked, and nothing is staged otherwise (no `git add`, not even `-N`).
10. **Treat risky input and private data with care.** Anything taking a URL, path, upload, SQL, shell input, password or token gets validation at the boundary and no secrets in code or logs. A project that reads personal or financial files (bank exports, customer dumps, `.env`) gets them in `.gitignore` before the first commit; only made-up samples are committed.
11. **If Bash is read-only, use Write and Edit.** Make the change, run what you can, and say which command could not run. If a write is refused, try the other tool (Edit, Write, `mkdir -p`) before reporting; never stop to ask for permission you may not get. Write and Edit are refused outside the project directory, so a spec or a probe that Bash cannot place elsewhere goes in one `.scratch/` folder, and you delete it before you finish (say so if you cannot). Do not create scratch files for checks you can run inline. Do not end by pasting code into the reply.
12. **The project's memory decides.** If AGENTS.md has a `## Tabby` section (the interview's answers), read it before designing. Name in one line the entries that shape this task (`goals:`, `growth:`, `constraints:`, `out-of-scope:`, `ask-first:`, `never:`, `decided:`) and design with them: build the seam the next `growth:` item needs (`references/growth.md` in the `tabby` skill), and treat a choice an entry rules out as a bug (keying records by one service's id when `growth:` names a second service). Check the result against `goals:` before reporting; a goal left unmet in the area you touched is not "out of scope". Do not re-ask what the section, the code or the git history records as decided. In the same task, update the lines your work made untrue: a `growth:` item now built moves to `goals:`, `map:`, `commands:` and `open:` follow the code, and a decision the user made in the conversation goes in `decided:`. A section exists, so never suggest the interview.
13. **Keep replies short, match the reader, end with the result.** The last message says what changed, what you ran and what it showed, and what is left for the user, in that order. When the work forced a choice (kept plain SQL, no ORM; stdlib over a dependency), name it with the reason in one line. It never holds only a verdict from a reviewer or a tool. No filler. Keep "not", "never", "only" and "except" intact. If the user says they are learning ("new to Python", "how does that work"), keep the result first, then add a short how-it-works in plain words and name each new idea once. With an experienced user, give no lessons. `/tabby:voice` sets this by hand.

## Thoughts that mean stop

| If you think | Then |
| --- | --- |
| "The test is wrong, I'll loosen it" | Leave it, finish the rest, report the contradiction |
| "A `# type: ignore` is faster" | Narrow the type or fix the code |
| "`dict[str, Any]` keeps it flexible" | A dataclass, `TypedDict` or model; `Any` hides the next bug |
| "I'll write a small helper" | `git grep` first, then the standard library |
| "The sample rows are fine, so it works" (data from a file, API or user) | Ask what a real one does on a bad day: encoding, locale numbers, empty input, near-miss matches. Guard the likely ones, test one, name the rest |
| "I'll import the optional package at the top" | Declare an extra, import inside the function, `raise ImportError("... pip install pkg[extra]") from e` |
| "A retry or a sleep will make it pass" | Find why it fails; that is the fix |
| "The tests pass, so it is done" | Run the thing the user asked for and quote the result |
| "I'll tidy this unrelated code while I'm here" | Leave it; mention it in one line |
| "I'll ask a question first" (the request names the change) | Do it; ask only when you cannot state it as one change |
| "This key or layout is fine for today" (AGENTS.md lists growth) | Check it against each `growth:` item; pick the one that keeps the next item cheap |
| "Allowing this would change an existing test" (the user changed the requirement) | Update that test to the new requirement and name it; do not drop the request |
| "I'll update AGENTS.md later" | Update the lines your work changed now; the next session decides from them |
| "Was this approved?" (the code or `decided:` already has it) | It was; build on it |

Checks that can be automated run as hooks (formatter and linter on the edited file, a diff check at the end of the turn). If a hook reports something, fix it rather than working around it.
