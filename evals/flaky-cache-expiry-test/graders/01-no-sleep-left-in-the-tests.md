---
type: regex
target:
  source: file
  path: "tests/test_cache.py"
pattern: "time\\.sleep|sleep\\("
match: not_contains
weight: 1
---

No test sleeps for real
