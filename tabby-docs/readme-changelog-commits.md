# README, changelog and commit messages


## README

The README is a landing page. A visitor decides in under a minute whether the project solves their problem and how to try it. Model READMEs: HTTPX, Polars, Ruff, uv, Rich.

Order:

1. **Name and one sentence** saying what it is and for whom: "HTTPX is a fully featured HTTP client for Python 3, with sync and async APIs." Not a tagline, not a list of adjectives.
2. **Status badges**, a few at most: version, supported Python versions, CI, license. No badge wall.
3. **Install**: one command (`pip install <pkg>` or `uv add <pkg>`), plus extras if they matter.
4. **Example**: the shortest program that does the main job, with its output. It runs as written, and a test runs it.
5. **Features or why**: optional, three to six concrete points with numbers where they exist ("Parses 1 GB of CSV in 2 s on a laptop; see benchmarks"), not superlatives.
6. **Links**: documentation, changelog, contributing guide, issue tracker.
7. **License** in one line.

Leave out: long API reference, full configuration tables, a table of contents for a short file, "Introduction" headings, emoji headings, roadmap promises.

## Changelog, release notes, deprecation notices

Follow Keep a Changelog (keepachangelog.com) unless the project uses another format or a generator (towncrier, git-cliff, release-please).

```markdown
# Changelog

All notable changes to this project are documented in this file. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.4.0] - 2026-11-03

### Added
- `Client.stream()` yields response chunks without loading the body into memory.

### Deprecated
- `Client.download(path)`; use `Client.stream()` and write the chunks. Removal planned for 2.0.

### Fixed
- Retries no longer double the timeout on each attempt (#412).

[Unreleased]: https://github.com/<owner>/<repo>/compare/v1.4.0...HEAD
[1.4.0]: https://github.com/<owner>/<repo>/compare/v1.3.2...v1.4.0
```

- Sections, in this order, only when non-empty: Added, Changed, Deprecated, Removed, Fixed, Security.
- Newest version first; ISO 8601 dates; one entry per user-visible change.
- Written for users: what changed for them and what they must do. Name the public API, link the issue. Not commit messages, not internal refactors.
- Breaking changes say what breaks and the migration in the entry itself.
- Changes land under `[Unreleased]` with the code; the release moves them under the version.

### Release notes

Release notes are a curated, readable summary of a release, for announcements or a GitHub release:

- Lead with what most users care about (headline features, breaking changes) in two or three sentences.
- Then a migration section for breaking changes with before/after code.
- Then link to the full changelog. Do not paste it.

### Deprecation notices

In reference docs, mark deprecated APIs where readers look them up:

```rst
.. deprecated:: 1.4
   Use :meth:`Client.stream` instead. Removal is planned for 2.0.
```

MkDocs/mkdocstrings projects use an admonition or the docstring's `Deprecated` text. Always name the replacement and, when known, the removal version.

## Commit messages and pull request descriptions

A commit message is read by someone running `git log` or `git blame` on a line they do not understand, long after the conversation that produced it is gone. Ask: what would they need to know that the diff does not show? Almost always that is why, and what else was considered or deliberately left out.

Commit only when asked ([planning-scope-and-shipping.md](../tabby/development/workflow/planning-scope-and-shipping.md)). These rules apply when you are asked to commit or to draft a message.

- The project's convention comes first: read `git log --oneline -20` and CONTRIBUTING. If it uses Conventional Commits (`fix(parser): ...`), a ticket prefix or a sign-off, match it; do not introduce one.
- Subject: imperative mood ("Add", "Fix", "Remove"), what changed for the reader of the log, about 50 characters and never past 72, no trailing period.
- Body only when the subject is not enough. It says why, not what: the problem, the cause for a bug fix, the constraint that shaped the choice. Wrap at 72 characters. The diff already says what changed and which files.
- Always a body for: a breaking change (what breaks, how to migrate), a security fix, a data migration, a revert (what is reverted and why), a workaround (what would make it unnecessary).
- One logical change per commit. A refactor and a behaviour change are two commits, so either can be reverted alone.
- Leave out: "this commit", "I", "we", "now", "as requested", the conversation, praise, emoji, and file lists.
- Reference an issue at the end (`Closes #128`) when one exists; never invent a number.

```
Fix timeout doubling on each retry

The retry loop passed the previous attempt's timeout to backoff(), so
the third attempt waited four times the configured value. Compute the
delay from the attempt number instead.

Closes #412
```

### Pull request description

Written for the reviewer, who decides in a minute where to look:

1. What changes for users or callers, in one or two sentences.
2. Why, and what was ruled out.
3. How it was verified: the commands run and their result; what was not verified.
4. What a reviewer should look at first, and anything deliberately left for later.

Follow the repository's pull request template when there is one. A new dependency, a public API change and a changed or removed test are always stated, never left for the reviewer to find.

### AI assistance and sign-off

Follow the project's rule on disclosing AI assistance (the Linux kernel and Ghostty both require it, stating the tool and how much it did). Never add a `Signed-off-by` for the human: only a person can certify the Developer's Certificate of Origin. Say plainly what was not tested, and send nothing to a maintainer or a tracker unless asked.
