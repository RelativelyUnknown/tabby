---
type: regex
target:
  source: file
  path: "src/reports/export.py"
pattern: "raise\\b[\\s\\S]{0,300}?\\bfrom\\s+(?!None\\b)\\w+"
weight: 1
---

The ImportError is chained
