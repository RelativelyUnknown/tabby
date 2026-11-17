---
type: llm
focus: trace
weight: 2
---

PASS if the tests the model wrote include a leap-year February (for example 2028-01-31 gives 2028-02-29), a rollover into the next year, and a `months` value above 12 or a multi-month step, and the suite passed. FAIL if any of these three is missing from the tests.
