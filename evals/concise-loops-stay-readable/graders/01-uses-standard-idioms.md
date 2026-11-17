---
type: llm
focus: trace
weight: 2
---

PASS if `summarise` uses plain standard tools for the totals and the largest paid order (for example `sum`, `max(..., default=None)`, `defaultdict` or `Counter`). FAIL if it hand-rolls running totals and a best-so-far flag in loops where those would do.
