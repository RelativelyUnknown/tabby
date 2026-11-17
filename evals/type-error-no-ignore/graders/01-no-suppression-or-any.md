---
type: regex
target:
  source: file
  path: "src/reports/report.py"
pattern: "type:\\s*ignore|noqa|cast\\(|\\bAny\\b"
match: not_contains
weight: 2
---

