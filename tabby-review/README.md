# review

A skill of the Tabby plugin for reviewing a Python diff, branch or pull request, auditing a project's security, and checking your own change before you report it done. A clean diff or a clean audit gets a short "no findings".

**Entry point:** [`SKILL.md`](SKILL.md), about 130 tokens.

## Layout

```
SKILL.md
changes/self-review.md                       silenced checks, weakened tests, smells, API breaks, new dependencies
bug-hunt.md                                  probes, checks enforced in one place and used in another, Python traps
state-machines.md                            implicit state machines: status fields, flags that travel together
repo-audit.md                                whole-repository audit: bugs, risk, load, missing tests, what to delete
native-boundary.md                           per-function table and checklist for the Python to Rust or C boundary
design.md                                    diagram, animation or interface: a judgment pass and a measured pass, kept apart
security-audit/process-and-reporting.md      trace input to sink, try to disprove each candidate; confirmed / needs-validation / rejected
security-audit/injection-files-crypto.md     SQL, commands, templates, deserialization, paths, uploads, SSRF, cryptography
security-audit/identity-and-config.md        authentication, authorization, fail-open defaults, configuration
security-audit/ci-pipelines.md               workflows as authorization code; AI agents in workflows
security-audit/supply-chain.md               package sources, dependency risk, advisories, the release path
```

The self-review checks a change against the rule and smells files in [`../tabby/development/`](../tabby/development/), so the two modules ship together. The audit approach is adapted in spirit from the Cloudflare security-audit skill (MIT, Cloudflare, Inc.) and written for Python; see `THIRD_PARTY_NOTICES.md` at the repository root.

## Evals

In [`../evals/`](../evals/):

- `clean-diff-no-noise`: a clean diff gets no invented findings.
- `seeded-audit`: a small service with three real vulnerabilities (SQL injection, path traversal, SSRF) and three look-alikes (an allowlisted `ORDER BY`, an allowlisted template name, a constant `subprocess` list with an md5 cache key).

## Licence

MIT.
