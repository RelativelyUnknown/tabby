---
type: llm
focus: trace
weight: 2
---

PASS if the trace shows the agent broke the refund rule on purpose (a changed boundary or constant, a dropped branch, a stub, or a mutation script or tool), saw a test fail, and restored refunds.py. FAIL if it never checked that a test can fail.
