---
type: llm
focus: trace
weight: 2
---

PASS if each of the two tests that cannot fail (test_returns_a_bool with isinstance, test_result_is_not_none with `is not None`) was removed, rewritten into a real assertion, or is named in the final message as unable to fail and left in place with a reason. FAIL if they stay in the file with no mention.
