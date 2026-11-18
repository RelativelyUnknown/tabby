---
type: regex
target:
  source: file
  path: "pyproject.toml"
pattern: "\\\"rich\\\""
match: not_contains
weight: 1
---

rich is removed from pyproject.toml
