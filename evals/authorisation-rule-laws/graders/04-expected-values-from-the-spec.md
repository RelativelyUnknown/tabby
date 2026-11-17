---
type: llm
focus: trace
weight: 2
---

PASS if the expected values in the tests come from the stated rules (literals, a table, or a condition written from the rules independently of the implementation). FAIL if a test recomputes the answer with the same expression as the implementation (for example `assert can_delete(r, o, l) == (r == "admin" or (r == "editor" and o and not l))` copied from the code).
