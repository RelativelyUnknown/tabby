---
type: llm
focus: trace
weight: 2
---

PASS if tests or runs cover a leap-year February (for example 2028-01-31 gives 2028-02-29) and a December-to-January wrap, and multiple months (`months=12` or more) are handled. FAIL if any of these is missing from what was tested.
