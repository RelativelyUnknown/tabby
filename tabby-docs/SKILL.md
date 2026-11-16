---
name: tabby-docs
description: "Load at the start for any writing about the code: a README, docstrings, a tutorial, how-to, reference or explanation page, changelog or release notes, ADR, runbook, troubleshooting page, CONTRIBUTING, a commit message or PR description, or checking docs against the code. Applies even to a one-line docstring or commit message."
license: MIT
---

# Writing documentation

Documentation lets a reader do or understand something without asking the author. Every sentence either moves the reader toward that or goes.

Read this first for any documentation task, then the leaf for the page (paths are relative to this skill's folder):

- `page-types.md`: a tutorial, how-to, reference or explanation page; a page that fits none or mixes two: `placing.md`
- `docstrings.md`: docstrings and API reference; `code-examples.md`: code samples and shell commands
- `readme-changelog-commits.md`: a README, a changelog or release notes, a commit message or pull request description
- `project-docs.md`: CONTRIBUTING, an architecture decision record, a runbook, a troubleshooting page
- `drift.md`: docs that must change with a code change; auditing docs against code
- `voice-and-style.md`: voice, word choice and AI writing patterns, for any page

## Never miss

- Name the reader and their need first. One page serves one need; if a page needs two, write two and link them.
- Follow the project's conventions over these defaults: the docs tool (`mkdocs.yml` means MkDocs, `docs/conf.py` means Sphinx), the docstring style (`[tool.ruff.lint.pydocstyle] convention`, or read five existing docstrings), a style guide or `.vale.ini`, the changelog format, the English variety. Report differences as suggestions; do not convert existing docs unasked.
- Read the code and run it before describing it. Documentation that states intended behavior instead of actual behavior is a bug. If the code and the existing docs disagree, report it rather than picking one silently. When the request gives the facts and there is no code to read, write from what you were given, mark anything you inferred `(assumed)`, and say the page was not checked against code; do not refuse to write.
- Be specific (numbers, versions, exact messages) and timeless (no "currently", "now", "new").
- Every example runs as written, and a test runs it.

## Workflow

1. Outline with headings only; check each heading against the page type.
2. Draft. Write the example first, run it, then write the prose around it.
3. Read it as the reader would. Cut every word that carries no information, using the AI-pattern and editing-pass sections of `voice-and-style.md`; judge each one in context, because a quoted word or a technical term can stay.
4. Edit pass. Delete sentences that restate the heading, summarize the page, announce what comes next, or praise the software. Check that every step is an action, every claim is specific, every link works.
5. Report what you changed and which examples you ran, and how.
