---
type: llm
focus: trace
weight: 2
---

PASS if a failed HTTP response cannot be mistaken for data: the code checks the status explicitly, or relies on `urlopen` (or the HTTP library) raising on 4xx and 5xx, and the code or the reply says so. FAIL if a non-2xx response body is parsed as if it were a good result.
