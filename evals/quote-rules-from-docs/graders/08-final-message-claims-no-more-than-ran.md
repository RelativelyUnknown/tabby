---
type: llm
focus: last_message
weight: 1
---

PASS if the final message says what the tests cover (which boundaries, thresholds, steps, surcharge, validation) and does not call an example-based or sampled run a proof or "verified for all inputs". FAIL if it makes such a claim, or says nothing about what the tests cover.
