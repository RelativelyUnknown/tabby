---
type: llm
focus: trace
weight: 2
---

PASS if the final tests/test_refunds.py checks the day boundaries on both sides (30 allowed and 31 refused for a non-member; 60 allowed and 61 refused for a member), in plain tests or a parametrized table. FAIL if any of those four cases is missing.
