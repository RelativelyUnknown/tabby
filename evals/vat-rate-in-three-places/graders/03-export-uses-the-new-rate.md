---
type: regex
target:
  source: file
  path: "src/shop/export.py"
pattern: "\\b19\\b"
match: not_contains
weight: 1
---

export.py no longer has the old 19 percent
