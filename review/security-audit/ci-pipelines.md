# Audit classes: CI workflows and AI agents in CI

CI configuration is authorization code: who can make a workflow run, with which token and secrets.

## CI workflows

A workflow is authorization code: it decides whose code runs, with which token and secrets, and what it may change. For each one ask four things: what event starts it, whose code or text does it consume, what credentials exist while it runs, and what may it change? A finding needs the usual four parts ([process-and-reporting.md](process-and-reporting.md)): a lower-trust party, something they control, the trusted job that consumes it, and what they gain. Write the attack as steps (entry, payload, how it executes, impact); if you cannot, it is `needs validation` or a hardening note.

Facts about GitHub Actions here come from GitHub's documentation and public incident write-ups and were not exercised in this repository. Branch protection, environment rules, runner type and org-level settings are not in the files, so a finding that depends on them is `needs validation`.

### Threat model

The attacker is an outsider without write access: they open fork pull requests, issues and comments, and choose branch names, file names and commit text. They cannot push, run `workflow_dispatch` or edit workflows on the default branch. Do not report what needs write access: `workflow_dispatch` inputs, `push`-only workflows on protected branches, `workflow_call` inputs whose callers are all internal. A contributor with write access is a different review (insider risk).

### Read the workflow, then the classes

Read the whole file and its trigger before judging a line; a `grep` hit is a lead. Files to read: `.github/workflows/*`, composite actions (`action.yml`, `.github/actions/*`), and files a job loads that a pull request can change (`Makefile`, scripts, `CLAUDE.md`, `AGENTS.md`, `.cursorrules`).

1. **Pwn request.** `pull_request_target` (or `workflow_run`, or an `issue_comment` command) runs with the base repository's secrets and write token. If any job then checks out the pull request's code (`ref:` set to the head SHA, head ref or `refs/pull/N/merge`) and runs anything from it, the contributor's code runs with those secrets. "Anything" is wide: `npm install` (lifecycle scripts), `pip install .` (`setup.py`), `go run` or `go test` (`init()` functions), `make`, a local action (`uses: ./.github/actions/x` comes from the checkout, so a fork replaces it), a script, a test run. `pull_request_target` with no checkout of the head, or a checkout without `ref:` (the base), is not a finding. Fix by splitting: an unprivileged `pull_request` job builds and tests and uploads an artifact; a privileged job triggered from it uses trusted code only and treats the artifact as data.
2. **Expression injection.** `${{ }}` is replaced before the shell sees the script, so a value with `"; curl ... #` or `$(...)` becomes shell. Dangerous only inside `run:` (and other script bodies). Attacker-chosen values: PR title and body, issue and comment bodies, review bodies, `head_ref` and branch names (shell metacharacters are allowed in them; `${IFS}` and brace expansion write a command without spaces), changed-file names fed through a step output, commit messages on unprotected branches. Safe: numbers (`pull_request.number`, `run_id`), `github.repository`, SHAs, `secrets.*`. Fix: put it in `env:` and use `"$VAR"`, quoted. Do not call the `env:` or `if:` use itself a finding; `with:` of an ordinary action is not shell either, but see AI agents below, where it is the sink.
3. **Commands from comments.** An `issue_comment` or `pull_request_review_comment` workflow that parses `/deploy` or `/version` and does not check the commenter acts for anyone on a public repository. Check `github.event.comment.author_association` against `OWNER`, `MEMBER`, `COLLABORATOR` (`CONTRIBUTOR` means "had a PR merged", `NONE` and the first-timer values are strangers). On a pull request the comment event runs on the base branch and the head must be fetched on purpose, so also look for the checkout in 1. Validate the command's arguments against an allowlist.
4. **Credential reach.** List every secret the job can read and what it can do: a classic personal access token reaches every repository its owner can; a fine-grained one a named set; a deploy key one repository; `GITHUB_TOKEN` whatever `permissions:` grants (no block means the repository default, which may be write); package tokens publish to your users. The question is whether untrusted code or text can reach them (1, 2, 3). Prefer OIDC to stored cloud keys, and check the cloud trust policy: a subject of `repo:org/repo:*` lets any branch or pull request assume the role, where `environment:production` with protection rules does not. Masking hides the secret itself, not `base64` or a slice of it. A secret written to a file then uploaded as an artifact is published.
5. **Permissions.** Start at `permissions: contents: read` for the workflow and add per job. `write-all`, `contents: write` on a pull-request-triggered job, or `id-token: write` on a job that does not deploy are findings only when something untrusted runs in the job; they are what turns the other classes from nuisance into takeover.
6. **Third-party actions.** A tag or branch can be re-pointed, and a deleted repository's name can be re-registered. Pin to a commit SHA (with the version in a comment) for third-party actions in jobs that hold secrets, OIDC, a write token, or that publish, deploy or sign. First-party `actions/*` and `github/*` on version tags, same-repository local actions, and unprivileged read-only CI are not pinning findings. A SHA-pinned action that downloads and runs a script at run time is still exposed to that URL.
7. **Runners, caches and artifacts.** A self-hosted runner is not wiped between jobs, so a fork pull request that runs on one can leave a backdoor and read the previous job's credentials and the internal network; use ephemeral runners and keep untrusted code off them. A cache or artifact written by a job that runs untrusted code and read by a privileged one (a `workflow_run` deploy that downloads the pull request's `dist/`) carries the attacker across the boundary; artifacts are not signed. Key caches by branch or keep PR and release caches separate.

A step that runs a model-driven agent has its own section below, "AI agents in CI".

### Report

Per finding: workflow and line, trigger, confidence, the numbered attack (attacker action first, each hop with its line, the consequence last), impact with the token's permissions, fix. Add the closest real precedent when one fits: branch-name injection (`${IFS}` payload) against a Microsoft repository, file-name injection against a security scanner, `init()` injection and a local-action override against two popular projects (the second stole a classic personal access token and was used to delete releases), an unauthenticated `/version` comment command against a CNCF project, and the `CLAUDE.md` attempt above, all described in StepSecurity's account of one campaign (cited in the third-party notices). List workflows you read and cleared. Zero findings is a valid result: say what you read. More in [process-and-reporting.md](process-and-reporting.md).

## AI agents in CI

Read the "CI workflows" section above first for the threat model and the workflow classes; this page is for a workflow step that runs a model-driven agent.

A workflow that runs a model-driven agent (a review bot, an issue triager; `claude-code-action`, Gemini CLI, Codex, `actions/ai-inference`) treats text as instructions. The injection sink is the agent's input and its power is whatever tools and token the job gives it. Review in this order.

**1. What can the attacker put in front of it?** Any of these reaches the model, and several have no `${{ }}` in the prompt:

- a direct expression in `prompt`, `direct_prompt`, `override_prompt`, `system-prompt`, `prompt-file`, `claude_args` or `codex-args`. For an agent, `with:` is a sink even though it is not a shell;
- through `env:`: `ISSUE_BODY: ${{ github.event.issue.body }}` at workflow, job or step level, and a prompt that says "read `$ISSUE_BODY`". The prompt looks clean and the usual advice to move expressions into `env:` makes it worse here. Follow each `env:` name into the prompt. Also `echo "X=..." >> $GITHUB_ENV` in an earlier step;
- fetched at run time: a prompt that tells the agent to `gh issue view N`, `gh pr diff` or `gh api`, with only the number interpolated. The YAML has no attacker text at all, but the agent reads the body;
- files the agent reads from a checked-out pull request, which is why `pull_request_target` plus a head checkout is worse for an agent than for a build, and why project instruction files (`CLAUDE.md`, `AGENTS.md`, `.cursorrules`, Copilot instructions) from a fork are trusted context. Protect them with `CODEOWNERS` and require review for changes to them;
- CI output: error logs, test output, `workflow_dispatch` inputs or step outputs passed to a "fix the build" agent. A test or compiler error can contain whatever the contributor made it print.

**2. What can it do?** The cost of a successful injection is the agent's reach:

- Shell: `Bash(*)` and a broad `Bash(npm:*) Bash(curl:*)` list, `danger-full-access`, `safety-strategy: unsafe`, sandbox switched off, `--yolo`. A "restricted" list that includes an expandable command (`echo`, `cat`, `printf`) is only restricted by name: the shell runs `$(env)` inside `echo $(env)` first. Demonstrated against Gemini CLI; likely but unconfirmed for the others.
- The token and secrets in its environment: `GITHUB_TOKEN` write scopes, API keys, the base repository's secrets in a `pull_request_target` job.
- Who may trigger it: `allowed_non_write_users: "*"` (Claude Code Action) and `allow-users: "*"` (Codex) let anyone; so do `allowed_bots: "*"` and `allow-bots`. With the field absent the defaults in both are write-access users only, so absence is not a finding. Gemini CLI and AI Inference have no such field, so the workflow trigger and an author check are the only gate. Settings can also live in a file (`settings:` path) the workflow does not show.

**3. What happens to its output?** `eval`, `exec`, an unquoted `$(...)`, or a script that formats the model's JSON into a command line, in a later step that holds the token. The consuming step is the finding; the model is just an untrusted source. Posting the output as a comment, writing it to a file or testing it in `if:` is not code execution (the comment can still carry markup or links).

**Severity.** A sandbox or allowlist weakness, or a wildcard user list, with no injection path is Info or Low; with one, it raises the injection finding. The strongest combinations are an outsider trigger (`pull_request_target`, `issues`, `issue_comment`), a direct or indirect injection path, shell, and secrets in the job. Fork `pull_request` runs without secrets and `push`/`workflow_dispatch` runs lower it.

**Fix by removing power**, not by filtering text: a read-only token, no secrets in the job, no shell (or a fixed list of non-expandable tools), runs for outsiders gated on a label a maintainer adds or an author check, sandbox on, the output treated as untrusted input and validated against a schema before anything acts on it. Do not rely on the model refusing: in the documented `CLAUDE.md` poisoning attempt the agent flagged it and the workflow was still vulnerable.

**Field names changed.** `claude-code-action` v0.x used `direct_prompt`, `override_prompt`, `allowed_tools` (comma-separated), `custom_instructions`; v1 uses `prompt` and `claude_args` (`--allowedTools "Bash(a:*) Bash(b:*)"`). Files pinned at `@v1` or a SHA can still carry old names, so read the names in the file, not the ref, and search for both sets. For other agents read the pinned version's `action.yml` and README rather than trusting a list.

**Hidden agents.** Resolve `uses: ./path` (composite action: read its `action.yml`; JavaScript and Docker actions have no steps to read) and job-level `uses:` (reusable workflow) one level deep and say which references you did not follow. A composite action has no `secrets` context, so `${{ secrets.X }}` written in one is empty and a secret there arrived as an input; a reusable workflow gets secrets named by the caller or all of them with `secrets: inherit`, which raises severity. Inheritance does not pass down a second hop. Name the line that grants the secret.

### Report

Report each finding in the per-finding form of "CI workflows" above, with the agent's tool permissions as the impact.
