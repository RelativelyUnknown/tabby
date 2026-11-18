---
type: llm
focus: trace
weight: 1
---

PASS if an illegal transition raises a specific exception (a named error class or ValueError with a message that names the order's state) rather than returning silently, returning False or using assert. FAIL otherwise.
