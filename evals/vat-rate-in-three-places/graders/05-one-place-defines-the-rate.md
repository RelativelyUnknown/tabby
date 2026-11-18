---
type: llm
focus: trace
weight: 3
---

PASS if, after the change, the VAT rate (21, 0.21, 1.21 or 121) is defined in exactly one place (a constant or a function) that the invoice, checkout and export modules all use. FAIL if the new rate is written out separately in two or more modules.
