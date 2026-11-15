---
type: regex
target:
  source: file
  path: "src/orders/models.py"
pattern: "class Config|@validator|\\.dict\\(|orm_mode|parse_obj"
match: not_contains
weight: 2
---

