---
type: regex
target:
  source: file
  path: "src/blog/authors.py"
pattern: "re\\.sub|def .*slug"
match: not_contains
weight: 2
---

