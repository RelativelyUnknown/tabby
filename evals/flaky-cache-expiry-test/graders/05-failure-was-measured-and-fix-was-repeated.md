---
type: llm
focus: trace
weight: 2
---

PASS if the trace shows the agent repeated the test many times (a loop, a repeat flag or a plugin) to see the failure rate or the failure before the fix, and repeated it again after the fix. FAIL if it ran the test once or twice and called it fixed.
