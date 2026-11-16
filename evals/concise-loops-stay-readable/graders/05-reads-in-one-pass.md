---
type: llm
focus: trace
weight: 3
---

PASS if the new `summarise` reads in one pass: no nested comprehension, no chained conditional expression, no side effect inside a comprehension or lambda, no `or`/`and` trick, and no single-letter names outside a tiny scope. FAIL if any line needs to be decoded, or if it is written as several hand-rolled loops with flags where `sum`, `max(..., default=None)` or a counter would do.
