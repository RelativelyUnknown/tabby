---
type: regex
target:
  source: file
  path: "tests/test_client.py"
pattern: "deprecated_call|pytest\\.warns|DeprecationWarning"
weight: 1
---

A test checks the warning
