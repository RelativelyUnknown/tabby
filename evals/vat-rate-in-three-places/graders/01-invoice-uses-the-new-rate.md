---
type: regex
target:
  source: file
  path: "src/shop/invoice.py"
pattern: "1\\.19"
match: not_contains
weight: 1
---

invoice.py no longer has the old 1.19 factor
