# documentation

A skill of the Tabby plugin for writing and editing software documentation by what the reader needs: Diátaxis page types plus decision, operations, troubleshooting and contributing pages, concise style, runnable examples, and no AI filler.

**Entry point:** [`SKILL.md`](SKILL.md), about 540 tokens: the never-miss rules and a workflow that ends in an edit pass for filler. It routes to the nine pages below.

## Layout

```
SKILL.md                       rules, workflow and the routing to each page
page-types.md                  tutorial, how-to, reference, explanation
placing.md                     a page that fits no type or mixes two
docstrings.md                  docstrings and API reference
code-examples.md               code samples and shell commands
readme-changelog-commits.md    README, changelog and release notes, commit messages and PR descriptions
project-docs.md                CONTRIBUTING, decision records, runbooks, troubleshooting by exact message
drift.md                       docs in step with code
voice-and-style.md             voice, word choice, editing pass, AI writing patterns
```

Docstring content rules (no conversation residue, no restated signatures) live in [`../tabby/development/code/minimalism-reuse-names.md`](../tabby/development/code/minimalism-reuse-names.md).

## Evals

In [`../evals/`](../evals/): `three-pages` (a tutorial, a how-to and a reference for one package), `readme-for-small-package`, `numpydoc-docstrings`, `adr-runbook-troubleshooting`, `agents-md-for-a-repo`.

## Licence

MIT.
