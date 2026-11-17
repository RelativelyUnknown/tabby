---
type: llm
focus: trace
weight: 2
---

PASS if the code returns `None` for the largest id when there are no paid orders without raising (for example `max(..., default=None)` or an explicit check), and a test covers that case. FAIL if `max` of an empty sequence can raise or the empty case is untested.
