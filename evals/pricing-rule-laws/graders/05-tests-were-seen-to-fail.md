---
type: llm
focus: trace
weight: 1
---

PASS if the trace shows the agent broke final_price_cents on purpose (a stub, a changed boundary or constant, a dropped branch, or a mutation tool), saw a test fail, and restored it. FAIL if it never checked that a test can fail.
