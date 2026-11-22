# Security audit: process and reporting

Find what an outside party can reach and report only what you can show.

## Process

Find what an outside party can reach and report only what you can show.

### 1. Scope and risk

- **A diff:** report what the change adds or makes reachable; the rest is context. **A repository:** start from the entry points. Read the whole diff, and whole files when it is cut off.
- Rank by what a file touches, not its size. High: authentication, authorization, crypto, parsing outside data, anything that builds a command, query or path, money, and any *removed* check. For those: `git log -S "<removed text>"` and `git blame` (why was the check there? one added by a "fix" or "security" commit is the worst to lose), callers of a changed function (`git grep`), and whether any test would fail if the lines broke. A refactor is high risk until shown otherwise.
- Find how the project already does the thing (its validator, authorization decorator, queryset scoping, safe-fetch helper). New code that skips what its siblings do is the best lead. A framework default depends on the pinned version.

### 2. Boundaries and flows

0. **Scanners are leads.** If the project runs `bandit`, `semgrep`, `ruff --select S` or `pip-audit`, read the output as a worklist and say how each hit was judged. A file the tool skipped (semgrep documents skipping files over 1 MB without a JSON warning; not run here) is not cleared. Run semgrep with `--metrics=off`.
1. **Boundaries.** List the entry points (routes, CLI arguments, queue messages, files, environment) and sort each by who may call it: anyone, a logged-in user, a role, another service. Check the check, not its name (`admin_required` may only test a header). A callback or webhook with no caller check is public.
2. **Flows.** Follow each untrusted value from entry through parsing, validation and copies to where it is used. Include batch, retry and error paths. Compare what one function guarantees with what the next assumes.
3. **Read next.** Before you report, open the page for every row whose trigger appears in the code, and name the pages in your coverage line.

| The code shows | Open |
| --- | --- |
| request data reaching `open`, `join`, `startswith`/`endswith`, a redirect, a `unquote` or `normalize`, an id copied into a queue message, job, cache key or log, `status =` assigned in several places, a flag read from the environment, a cache or limit key, read-then-call-then-write | [bug-hunt.md](../bug-hunt.md) ("Two places that must agree") |
| `execute(`, f-string SQL, `subprocess`, `eval`, `pickle`, `yaml.load`, templates, `render` | [injection-files-crypto.md](injection-files-crypto.md) |
| login, session, token, JWT, password reset, roles, `is_admin`, `setattr`/`vars(`/`update(**` on request data, ownership of a record | [identity-and-config.md](identity-and-config.md) |
| uploads, archives, `open`, URLs fetched server-side, hashing, randomness, secrets, TLS | [injection-files-crypto.md](injection-files-crypto.md) |
| `os.environ`, settings, feature flags, defaults, debug switches, empty or zero values | [identity-and-config.md](identity-and-config.md) |
| `.github/workflows`, an AI agent in CI | [ci-pipelines.md](ci-pipelines.md) |
| lock files, indexes, release and publish steps, an advisory | [supply-chain.md](supply-chain.md) |
| C, C++ or Rust beside Python | [native-boundary.md](../native-boundary.md) |

Attacker-controlled: request data, uploads, headers, cookies, messages from other parties, data lower-trust users write. Server-controlled: settings, environment, CLI flags, constants, the project's own output. For a value read from a database or file, find who writes it. Say how much control the attacker has and what is in the way (normalisation, truncation, type coercion).

### 3. Try to disprove each candidate

The default is "refuted" until the evidence says otherwise; reviewers lean toward seeing bugs and overrating them.

- **Restate the claim** in one sentence: the input, the line, the mistake, the effect. If you cannot, drop it.
- **Read the controls on the path:** allowlists, parameter binding, constant arguments, framework escaping, a check in any layer. A check anywhere counts if it holds on every path to the sink.
- **Is the sink reachable?** Earlier conditions can make a dangerous-looking line impossible to reach. Code nothing calls today is not refuted by that: report it lower and say what would make it reachable.
- **What stops it, what only slows it.** A parameterised query stops; a rate limit or hard-to-guess id raises the bar.
- **Check both directions:** are you reporting because it looks dangerous, or dismissing a real hole because the exploit looks complicated? Re-read after you conclude; did you rely on a validation you never saw?
- **What does the attacker already have?** A bug that needs the privilege it grants is not a finding.
- **Do not report:** tests, fixtures, docs, dead code; auto-escaping and parameterised queries (only their escape hatches on user data); denial of service, ReDoS and missing rate limits (a hardening note, unless a small unauthenticated input causes large amplification); missing logs or headers, open redirects outside login flows; SSRF where only the path of a fixed host is controlled; client-side checks (the server decides); memory-safety claims outside C, C++ and `unsafe`; theoretical races and timing; environment variables and CLI flags as attacker input; vulnerable third-party versions in a diff review ([supply-chain.md](supply-chain.md) covers a repository).
- **Confidence:** reached by attacker input with no effective control: confirmed, with a severity. Depends on something you cannot see: `needs validation`, with the question. Anything else is a hardening note at most.

### 4. Variants, then the fix

- State the root cause in one sentence: "[untrusted data] reaches [dangerous operation] without [required protection]", or for a logic bug the invariant broken. Then search for siblings: write a pattern that matches only the known instance, generalise one element at a time (function, argument, module, framework), read all matches after each step, and stop when more than half are noise. Look beyond the module: other routes, jobs and commands reaching the same sink.
- Widen first: other names with the same role (`is_active`, `is_admin`; `user_id`, `owner_id`), other slips of the same kind (inverted condition, `return True` on the fall-through, `or` for `and`, `None == None`), functions whose behaviour contradicts their name.
- A fix is checked with evidence, not the diff or the author. A test that states the safe outcome must fail on the old code and pass on the new, and you must read the old-code failure to be sure it is your assertion and not an `ImportError`. Add a benign control, and a variant through a different path (another entry point, streaming against buffered, error and cleanup paths, empty and maximum inputs), not the same payload with another literal. "The original proof no longer works" is not a fix until an independent variant also fails. A comment saying the caller must check is not a fix.
- A confirmed finding comes with a regression test that fails before the fix ("Reporting" below).

### Limits

Static reading first. Run target code only with no network, a scrubbed environment, dummy secrets and writes limited to a scratch directory; if you cannot isolate it, say so and do not run it. Never install a tool to audit. Facts outside the repository (proxy, identity provider, deployment) are not proof either way: `needs validation`, with who can answer. Write-time rules: `tabby/development/code/input-and-secrets-security.md`.

## Reporting

Three buckets, in this order, each finding under one root cause:

- **Confirmed**: you traced untrusted input to a sink with no effective control and can say what an attacker gets. Only these carry a severity.
- **Needs validation**: it depends on something you cannot see (deployment, a framework version, a runtime value). State the question and who can answer it. No severity.
- **Rejected**: looked suspicious, disproved. One line each with the control that stops it, so it is not raised again.

For each confirmed finding: `file:line`, the **entry point** (who sends what), the **payload**, how it **executes** or reaches the sink, **what the attacker gets**, severity, the smallest fix at the last point where the data is trusted, and a **regression test** that fails before the fix, passes after it, and fails again when you revert the fix (a quick way to know the test tests the fix). Run the failing test against the old code and read its output: it must fail on your assertion, not on an import error. Do not adjust the reproduction until it agrees with the claim. If you cannot write all four of entry point, payload, mechanism and effect, it is `needs validation`. The fix has to enforce in code (a scoped query, a check that raises); a comment saying the caller must check is not a fix.

Rate **severity** (the damage if it is real) and **likelihood** (how easily it triggers in supported use: low for an unusual configuration, high for routine operation) separately, each with a reason; neither makes a finding valid. Severity follows the damage you can state: high when an outside party defeats an explicit control with real consequences (data read or changed, code run, other tenants' data), medium when a control is weakened but the damage is limited, low for hardening. If you cannot state concrete damage, rate lower. The overall severity never exceeds the worst confirmed finding.

**Rating a severity.** List the facts first (what is vulnerable, how the attacker reaches it, which privileges they need, what they get, whether a user must act), then judge each impact on its own and take the reasonable worst case, marking missing facts as assumed. Do not compute a numeric score by hand: give the CVSS 4.0 vector and let the calculator produce the number, only when asked.

**Coverage.** End with what you checked and what you did not (a result that only read the code says so; it is not the same as one that ran the behaviour), so a clean result can be trusted: the files read in full, the classes walked (each clean, not applicable, finding or unverified), the endpoints or flows not reviewed, and anything that needed a deployment fact you could not see. For an access-control review add one line on how this project enforces authorization.

Do not pad: a missing header or rate limit with no victim is a note at the end, not a finding. A clean audit says what was checked and found nothing.

### Machine-readable report

When the user wants a report a tool can read (CI, a ticket import, a diff between two audits), write it as JSON in the shape of [findings.schema.json](findings.schema.json) and check it with `python3 ../scripts/validate_findings.py findings.json --root <repo>` (paths relative to this folder). It enforces what this page says: a confirmed finding has entry point, payload, mechanism, effect, fix and a regression test; only confirmed findings carry a severity; the overall severity never exceeds the worst confirmed one; every `file:line` exists; coverage lists what was read, run and not checked, and the state of every class walked. Fix what it reports before you hand the file over. The prose report still follows the shape below.

## Report shape

Short means no filler, never a missing fact. Verdict first, in one line. Then one entry per finding: `file:line`, the path from entry to sink in at most two sentences, the fix in one. No preamble, no restating the task, no announcing what you will do, no closing recap or offer, and no mention of this guide or of checks you skipped. Say each thing once; related observations go in one trailing line. Leave out clean code, stubs, style and "no tests"; a hardening note is one line each at the end. Coverage is three lines: read, ran, not checked. Never cut `not`, `never`, `no`, `only`, numbers, paths, function names or a quoted error; use full sentences for a warning about something irreversible. With `report: terse`, give only the verdict and one line per finding.

### An independent check before you report

Disproving your own candidate in the context that produced it is weak. When you can run a subagent, give each confirmed candidate to a fresh one with only the candidate (trace, files, claimed effect) and this prompt, then keep what survives:

> You did not write this finding. Try to refute it from the source. Check every file and line in the trace, find the strongest control on the path (validation, authorization, framework behaviour, a constant argument) and say whether it stops the claimed effect. Reply `holds` with the reason, `refuted` with the control that stops it, or `needs validation` with the one fact you cannot see.

The verifier reads and runs nothing that touches the network or writes outside a scratch directory. Without subagents, do the same pass yourself starting from the sink and walking back, and say that you did.
