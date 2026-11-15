---
type: regex
target:
  source: file
  path: "src/cleaner/**/*.py"
pattern: "^class |Strategy|Factory|Protocol"
match: not_contains
weight: 2
---

