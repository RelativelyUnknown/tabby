---
type: regex
target:
  source: file
  path: "tests/test_cache.py"
pattern: "flaky|reruns|retry|retries"
match: not_contains
flags: i
weight: 1
---

No flaky marker, rerun or retry was added to the tests
