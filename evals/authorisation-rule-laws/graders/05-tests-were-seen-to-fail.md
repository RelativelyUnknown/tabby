---
type: llm
focus: trace
weight: 1
---

PASS if the trace shows the agent broke can_delete on purpose (a stub that returns False, a flipped or dropped condition, or a mutation tool), saw a test fail, and restored it. FAIL if it never checked that a test can fail.
