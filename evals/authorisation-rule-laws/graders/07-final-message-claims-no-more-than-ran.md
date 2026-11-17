---
type: llm
focus: last_message
weight: 1
---

PASS if the final message says what was checked and how (for example all twelve combinations in a table, or a property run) and does not call a sampled or example-based run a proof. FAIL if it says the rule is "proved" or "verified for all inputs" when only some inputs ran, or says nothing about what the tests cover.
