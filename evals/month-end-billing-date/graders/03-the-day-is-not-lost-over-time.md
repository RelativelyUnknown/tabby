---
type: llm
focus: trace
weight: 2
---

PASS if billing from the original start date and `months=2` after a January 31 signup gives March 31 (the day is computed from the start date, not chained from the clamped February date). FAIL if the result is March 28 or the code chains one-month steps.
