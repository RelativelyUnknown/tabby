---
type: llm
focus: trace
weight: 3
---

PASS if the trace shows `next_billing_date(date(2026, 1, 31))` (or an equal 31st-to-short-month case) was run and returned a valid date (the last day of February, 2026-02-28) instead of raising `ValueError`. FAIL if it was not run or raised.
