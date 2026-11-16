# Tabby core: Python work

These rules apply to every Python change. They are the habits a strong model skips by default. Domain detail lives in the Tabby skills. Load the matching skill at the start of the task (`tabby` for Python changes, `tabby-review`, `tabby-docs`, `tabby-diagrams`, `tabby-frontend`), then read only the pages it names for the area you touch.

1. **Solve the real problem and verify it.** Name the command that proves the claim, run it fresh, read the exit code and failure count, then report the result. If you could not run it, say so. Run targeted tests while iterating and the full check once at the end.
2. **Leave existing tests alone.** Do not edit, delete, skip or loosen one to get green. If a test contradicts the spec, finish the rest and report it. A bug fix starts with a failing test that you watch fail.
3. **Find the cause before the fix.** No special-casing inputs, no sleeps or retries that hide a symptom. When asked to raise a timeout or limit so a failure stops, first check why it fails.
4. **Fix tool complaints properly.** Do not add `# type: ignore`, `# noqa`, `Any`, `cast(` or looser config. Narrow the type, fix the code, or explain a justified exception in the line.
5. **Ask when the request is vague.** "Make the reports better" gets one to three short questions with suggested answers before any edit. A request that names the change is done, not discussed.
6. **Reuse before writing.** `git grep` for an existing helper first. Then the standard library, then a dependency already installed, then the community standard, and only then new code. Say which rung you took.
7. **Smallest diff that solves it.** Every changed line traces to the request. Remove only what your change made unused. Match the style of the file around it. No narrating comments, no defensive checks on data your own code produced.
8. **Use the project's own tools.** Runner, formatter, linter, type checker and Python target come from its lock file, Makefile or CI. Do not swap one, add a second, or install silently.
9. **Public names are promises.** Removing or renaming one is a deprecation unless nothing outside the repo can use it. A public API change, a commit or a push happens only when asked.
10. **Treat risky input with care.** Anything taking a URL, path, upload, SQL, shell input, password or token gets validation at the boundary and no secrets in code or logs.
11. **If Bash is read-only, use Write and Edit.** Make the change, run what you can, and say which command could not run. Do not end by pasting code into the reply.
12. **Keep replies short, and end with the result.** The last message says what changed, what you ran and what it showed, and what is left for the user, in that order. It never holds only a verdict from a reviewer or a tool. No filler. Keep "not", "never", "only" and "except" intact.

## Thoughts that mean stop

| If you think | Then |
| --- | --- |
| "The test is wrong, I'll loosen it" | Leave it, finish the rest, report the contradiction |
| "A `# type: ignore` is faster" | Narrow the type or fix the code |
| "`dict[str, Any]` keeps it flexible" | A dataclass, `TypedDict` or model; `Any` hides the next bug |
| "I'll write a small helper" | `git grep` first, then the standard library |
| "A retry or a sleep will make it pass" | Find why it fails; that is the fix |
| "The tests pass, so it is done" | Run the thing the user asked for and quote the result |
| "I'll tidy this unrelated code while I'm here" | Leave it; mention it in one line |
| "I'll ask a question first" (the request names the change) | Do it; ask only when you cannot state it as one change |

Checks that can be automated run as hooks (formatter and linter on the edited file, a diff check at the end of the turn). If a hook reports something, fix it rather than working around it.
