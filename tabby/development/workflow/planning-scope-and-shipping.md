# Planning a change

Planning is cheap compared with undoing a wrong change. Ask: what is the smallest change that solves the real problem, who else depends on what I am touching, and what would a wrong guess cost? Spend thought where a wrong guess is expensive (public API, data, migrations) and move fast where it is not.

- Before a non-trivial change, state the approach in a few lines. Read the code and its callers first; find every caller (code, tests, scripts, config, docs) before renaming or changing a signature.
- For a change across several files, list before editing: the files to change, their callers and dependencies, the tests that cover them, one existing example to follow, and the risks (public API, schema or migration, configuration). Review that map with the user when it is large.
- Ask first when requirements are ambiguous and a wrong guess is expensive. If a rule conflicts with the request, say so and ask.
- Smallest diff that solves the problem properly. No unrelated refactors, renames or reformatting; mention what you noticed. No summary, changelog or demo files nobody asked for; delete scratch files. Do not edit CI, lint or pytest config unless that is the task.
- Prefix commands with the project's `runner`. Keep the project's existing tools (poetry, black, pyright, ...); never add a second tool for the same job. Never install a tool or dependency silently.
- **Stop and report** instead of working around a problem when a test contradicts the spec or task; the task cannot be done properly with the code and dependencies available; the fix needs a new dependency, a public API change or a deleted file; or you catch yourself justifying test-specific behavior with a reason like "backward compatibility".
- Do not commit, push or run destructive commands (`git reset --hard`, `rm -rf`, force-push, dropping tables) unless asked. Never skip hooks with `--no-verify`. Deleting data or files, dropping columns, changing a public API or irreversible migrations need approval first.

## Shipping and reporting

Done means the real problem is solved, verified by running the code, and explainable. Passing tests are evidence, not the goal. Before you report done (for a multi-part request, run the gates from `workflow/multi-outcome-gates.md` first): run the full suite and the project's check command, list every new dependency and every changed or removed test, and check the diff once for anything you did not mean to change (an unrelated edit, a scratch file, a leftover print). Write against [code-smells.md](../code/code-smells.md) as you go; do not rely on a cleanup pass.

### Report (`report`, default `normal`)

Plain and factual. No "production-ready", "robust" or "comprehensive", no celebration, no emojis. Show the exact command and its real output; separate what you verified from what should work.

- `terse`: Verdict, commands run with pass/fail counts, deviations. At most 10 lines. A new dependency, a changed or removed test, or a stopped task always counts as a deviation.
- `normal`: What changed and why, commands with real output, verified vs unverified, every new dependency, every test changed or removed with the reason.
- `audit`: `normal`, plus every shortcut, assumption, skipped check and known limitation (or "none"), everything noticed and left alone, and any rule conflict and which rule won.

### When short is wrong

Short means no filler, never a missing fact. Write full sentences for: a security warning, an action that cannot be undone (confirm before doing it), steps whose order matters, a question you ask the user, and anything a reader repeats back as not understood. Quote an error by its one decisive line, exactly. Text that outlives the conversation (comments, commits, docs, issues) follows the `documentation` module, not the reply style.
