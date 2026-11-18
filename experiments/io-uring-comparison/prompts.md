# Prompts

Every message the two agents received, word for word. Nothing else was said to them except the working-folder line shown under each arm.

## Request (both arms, identical)

> Hi! I'm a junior developer, about 2 years in. I want a Python library backed by Rust that uses io_uring to read lots of files really fast. Can you build it?

No mention of tests, docs, benchmarks or packaging: the point was to see what each agent decides when the request is vague.

## Round 1, without Tabby

Working-folder line: `Work ONLY inside <empty git repo>. Never push. Do not read or use anything under <the tabby checkout>.` Then the request above, then: `You cannot ask me questions mid-task; decide sensibly yourself. When completely finished, reply with what you built, what you ran and the real results, and a count of your own tool calls.`

## Round 1, with Tabby

Working-folder line: `Tabby skills are installed at <checkout>. Start by running its interview skill: read interview/SKILL.md and follow it exactly. You cannot talk to me directly, so when the interview says to ask its first round of questions, stop and return those questions (with their recommended answers) as your final reply. I will answer and resume you. After the interview is saved, carry on with the request below using the tabby skills.` Then the request above and the same closing line.

The interview stopped after its first round. The reply, standing in for the user (a junior developer who accepts the recommended answers):

> Thanks, that's helpful! My answers (I'm a junior dev, so I'm going with your recommendations since I don't know better yet):
> 1. Name: `uringread` is fine. Purpose as you wrote it.
> 2. Users: me and my team first, loading lots of small files (datasets, logs). `read_files(paths)` returning bytes sounds right. Normal installable library.
> 3. Success: faster than a plain Python loop (and ideally a thread pool), same bytes as a normal read, a missing file shouldn't crash the whole batch, and it should still work if io_uring isn't available (my teammates use Macs). I don't want claims of speed that weren't measured.
> For rounds 2 and 3, your defaults are fine (growth: ranges, buffers, writes later; Python 3.10+, Linux-first with fallback; uv + maturin + pytest + ruff + clippy; no network I/O, no new runtime Python deps). Please carry on: restate, and if that all looks right, treat this as my yes, save the ## Tabby section, then go ahead and build the library.

## Round 2: the vague optimisation request (both arms, identical)

> Thanks, it works! Could you make it faster? It still feels slower than it should be. (Same folder as before. When finished, reply with what you changed, what you ran and the real results, and a count of your own tool calls. If you need to ask me something, stop and ask.)

The plain arm did not ask anything and changed the code. The Tabby arm changed nothing, asked which workload felt slow and whether it could use `unsafe`, and got this answer:

> Thanks for checking before changing things! My answers (junior dev here, so I'm guessing a bit): it's mostly cold cache. My team loads datasets from a local SSD, around 20,000 to 100,000 files, anywhere from 4 KB up to about 1 MB each. Large files and a 4-core laptop/server are the normal case. I don't know unsafe well, but yes, you may use it if it gives a real, measured speed-up. Please keep it small and explain the risk in comments, since I'll have to maintain it. Go ahead with the options you listed, and keep only what measurably helps. Same reply format as before, with your tool-call count.
