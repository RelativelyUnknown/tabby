---
type: llm
focus: trace
weight: 1
---

PASS if the trace shows docs/pricing.md was read before the rule was written, with any tool (the Read tool, or `cat` or similar in Bash). FAIL if the agent wrote the function without opening it.
