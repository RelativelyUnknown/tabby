# Page types

Pick by what the reader is doing. One page serves one need; a page that needs two is two pages.

## Tutorial: learn by doing, as a beginner

A lesson. The author is responsible for the reader's success.

- One path, no choices. Pick the options for the reader; mention alternatives only by linking elsewhere.
- Every step produces a visible result early and often ("You should now see ...").
- Concrete, not abstract: a small real project, real data, real commands.
- Minimal explanation; link to explanation pages instead.
- It must work for a beginner on a clean machine. Test it end to end on each release.

Template:

```markdown
# Build your first <thing>

In this tutorial you build <result>. It takes about <N> minutes.

## Before you start
- <exact requirement, with version>

## Create the project
1. Run ...
   You should see ...

## <Next step>
...

## Next steps
- [How to <common next goal>](#next-goal)
```

## How-to: reach a goal the reader already has

A recipe for a reader who already knows what they want.

- Title states the goal: "How to rotate credentials", "Deploy to production".
- Start from a stated precondition, not from zero. Skip teaching.
- Steps in order; branch only where real situations differ ("If you use serverless, ...").
- Leave out everything not needed for the goal, including full option lists; link to reference.
- End when the goal is reached.

## Reference: look something up (API, CLI, config)

A map of the machinery, consulted, not read.

- Structure mirrors the code: one page or section per module, class, command or config file, in a consistent order.
- Each entry: signature or syntax, one-line description, parameters with types and defaults, return value, errors, a short example.
- Complete and accurate beats readable. Generate from the source where possible (autodoc, mkdocstrings, `--help` output) so it cannot drift.
- Neutral tone: describe, do not instruct or persuade.

## Explanation: understand why or how it works

Discussion that builds understanding.

- Answers "why" and "how does it work": design decisions, architecture, trade-offs, history where it explains the present, comparisons with alternatives.
- Can hold opinions and context; is read away from the keyboard.
- Titles are topics: "Consistency model", "Why the scheduler is single-threaded".
