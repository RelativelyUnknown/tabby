---
type: llm
focus: trace
weight: 3
---

PASS if fetch(url, timeout=5) still works after the change (the old keyword is accepted and mapped to the new one) and the existing test that calls it was left unchanged and passes. FAIL if the old keyword now raises TypeError or the existing test was edited to use the new name.
