---
type: llm
focus: trace
weight: 3
---

PASS if the fix removes the dependence on real elapsed time: the cache takes a clock (a callable or parameter) that the tests control, or the tests patch time.monotonic. FAIL if it only lengthens the ttl or the sleeps, adds a retry, or skips the test.
