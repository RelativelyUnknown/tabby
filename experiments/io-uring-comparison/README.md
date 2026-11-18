# Experiment: the same vague request, with and without Tabby

One run of one task: ask an agent for "a Python library backed by Rust that uses io_uring to read lots of files really fast", then, once it works, "make it faster". One agent had Tabby, the other did not. This folder holds the prompts, the benchmark script and the numbers, so you can repeat it.

**Read [Bias and limits](#bias-and-limits) before you read the results.** This is one run per arm, judged by the same model that built both libraries.

## What was compared

| | Arm A: no Tabby | Arm B: Tabby |
| --- | --- | --- |
| Setup | empty git repo, no skills | empty git repo, Tabby's core rules and skills, interview first |
| Round 1 | the request, nothing else | `interview`, then the request |
| Round 2 | "make it faster" | "make it faster" |

Both arms were Claude subagents run from one Claude Code session on a 4-CPU Linux 6.18 container (io_uring allowed, ext4, root). The exact messages are in [`prompts.md`](prompts.md).

The user in the experiment is played by the person running it. In round 1 the Tabby interview asked three questions and the reply accepted its recommended answers. In round 2 the Tabby arm asked about the workload and about `unsafe` before changing anything, and got a short answer. The plain arm cannot ask and was told to decide itself, so the arms did not get the same information.

## Results

All figures below are from my own re-runs with [`cmpbench.py`](cmpbench.py), not from the agents' reports. Times are the median of 3 runs, in ms, lower is better. The same files were used for both arms in each row.

### After round 1 (the first working version)

| Check | Arm A | Arm B |
| --- | --- | --- |
| Tests | 8 pass | 22 pass, 2 skipped (need a non-root user) |
| Lint and format | `cargo clippy` clean; no fmt or ruff setup | `make check` clean (fmt, clippy, cargo test, ruff, pytest) |
| Result-ordering bug injected on purpose | 1 test fails | 5 tests fail |
| Falls back when io_uring is missing | no | yes (plain-Python backend) |
| One bad file | raises, or `None` with `errors="ignore"` | returned as an `OSError` in the list |
| Lines, lockfiles excluded | 426 in 8 files | 1,001 in 14 files |

| Workload (cold / warm) | plain loop | Arm A | Arm B |
| --- | --- | --- | --- |
| 20,000 × 16 KB | 1,737 / 355 and 1,790 / 367 | 529 / 333 | 642 / 404 |
| 2,000 × 1 MB | 4,020 / 1,979 and 4,147 / 2,287 | 3,522 / 2,616 | 3,124 / 2,882 |

Neither was clearly faster. Both use the same design: one ring, four operations per file.

### After round 2 ("make it faster")

| | Arm A | Arm B |
| --- | --- | --- |
| First response | changed the code at once | profiled, tried two ideas, reverted both, asked what was slow and whether `unsafe` was allowed |
| Change | one ring per thread; read straight into the returned `bytes` | the same two ideas, after the answer; `unsafe` limited to a `Buffer` trait with the contract written down |
| Tests added | 0 (8 in total) | 2 (25 in total) |
| README after | now wrong: still says "single ring/thread" and "not faster than a thread pool" | updated, and says a thread pool still wins around 1 MB |

| Workload (cold / warm) | plain loop | thread pool | Arm A | Arm B |
| --- | --- | --- | --- | --- |
| 20,000 × 4 KB | 1,177–1,444 / 155–256 | 3,370–3,933 / 3,373–4,312 | 269–319 / 281–332 | **187–210 / 99–117** |
| 20,000 × 16 KB | 2,259–2,334 / 382–429 | 4,495–5,035 / 3,524–4,070 | **382** / 324 | 603 / **355** |
| 2,000 × 1 MB | 4,230–4,700 / 1,972–2,323 | 1,523–1,767 / 1,161–1,497 | **1,194–1,206 / 561–619** | 2,638 / 1,562 |

Ranges are the repeats I ran. In short: Arm B was faster on small files, Arm A was 2–3x faster on 1 MB files and beat the thread pool there, and Arm B did not. Arm A's own report said 289,000 files/s on 4 KB files warm; I measured about 60,000–70,000.

### Cost (harness figures)

| | Arm A | Arm B |
| --- | --- | --- |
| Round 1 | 74k tokens, 6 tool uses, 3.7 min | 145k tokens, 45 tool uses, 12.7 min |
| Round 2 | 81k tokens, 4 tool uses, 3.3 min | 132k tokens, 27 tool uses, 43 min |

Token counts may be cumulative for a resumed agent, and Arm B's wall time includes waiting for an answer. In round 2 Arm B was a fresh agent, because the round-1 agent had been stopped: it had only the saved `AGENTS.md` and the code. Arms reported tool-call counts that differed from the harness's by a few; use the harness's.

## Run it yourself

Needs Linux 5.6+ with io_uring not blocked by seccomp, `cargo`, `uv`, Python 3.10+, and Claude Code. Root is only needed for the cold-cache lines.

1. Make two empty git repos, `arm-a` and `arm-b`. Do not put Tabby in `arm-a`'s session.
2. Arm A: open Claude Code in `arm-a` and send the request from `prompts.md`. Arm B: install Tabby (`/plugin install tabby@tabby`), open Claude Code in `arm-b`, run `/tabby:interview`, send the request, and answer the interview.
3. When both work, send the round-2 message to each. Answer the Tabby arm's questions if it asks any.
4. Check both yourself, in each repo: the tests (`pytest`, and `make check` if it exists) and a lint pass.
5. Mutation check: change the line that stores each file's result so it stores into the wrong slot (for example index `i / 2 * 2`), rebuild, and count the failing tests. A test suite that cannot see a result going to the wrong place is a weak suite.
6. Benchmark both on the same files, after a release build (`maturin develop --release`):

   ```
   python cmpbench.py /tmp/uringbench 20000 4096
   python cmpbench.py /tmp/uringbench-big 2000 1048576
   rm -rf /tmp/uringbench /tmp/uringbench-big
   ```

   Run each at least three times and compare ranges, not single numbers. On this machine the plain loop alone swung by 30% or more between runs.

I ran the experiment as subagents inside one Claude Code session, so the steps above are the same protocol typed by hand, and I have not run them that way. Your agents will build different libraries. The libraries from this run are not committed here: each was about a thousand generated lines, and a rerun is the point.

## Bias and limits

I am Claude. I built both arms, ran the experiment, wrote the user's replies, checked the results and wrote this page, so here is how that can skew it.

- **Same model on both sides, and as judge.** Both arms and the scorer are one model family. I may prefer code and docs that look like what I would write, and I may rate long, well-documented output higher than it deserves. Tests, docs and decision records are what Tabby tells an agent to produce, and they were also on my scorecard, so the scorecard favours Tabby by construction. Diff size and cost, which favour the plain arm, were on it too, but I chose how to weigh them.
- **I played the user.** I wrote the answers to the interview and to the round-2 questions. The fallback and "a missing file should not crash the batch" came from those answers, so some of Arm B's extra scope came from me, not from Tabby. I also said yes to `unsafe` for the user. The plain arm was never asked, so it had no chance to get the same answers.
- **The arms were not treated the same.** Arm B got an extra first line pointing at Tabby and a different round-1 flow. Arm A was told it could not ask questions. Round 2 used a fresh agent for Arm B. Any of these could move the result.
- **I know which arm is which.** I read the code knowing it, and I wanted the experiment to be a fair test of a repo I was working in. That can push me to explain a Tabby loss kindly or to look harder for flaws in the plain arm. I tried to guard against it by re-running every number and reporting a failure where I saw one, but I cannot rule it out.
- **n = 1.** One run per arm. A second run could swap the speed results. The 16 KB and 1 MB differences in particular may be luck in which design each agent happened to choose.
- **A noisy machine.** A shared 4-CPU container; the plain loop varied by 30% or more across runs. I report ranges and ran the close cases again, but small gaps are noise.
- **The agents' own reports were wrong in places.** Arm A reported speed-ups I could not reproduce and a tool-call count that was off. I replaced those with my measurements. The other figures in this page come from reports and I did not re-check them (token counts and wall times, for example).
- **A restart.** I stopped and restarted the first attempt because its prompt named tests and docs, which the person who set the experiment up did not want. The restart is the one reported here, so no results from the first attempt were used or dropped for being inconvenient.
- **One task, one language pair.** Rust, PyO3 and io_uring, a library of about a thousand lines. It says little about web services, data pipelines or other languages, and the repository's own [evals](../../evals/) are a better source for the general effect.

What I would trust: both libraries build, pass their tests and return the right bytes, and the specific differences in the tables above. What I would not: any claim that Tabby makes an agent faster, slower, better or worse overall.
