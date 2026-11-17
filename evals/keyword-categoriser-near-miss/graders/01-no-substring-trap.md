---
type: llm
focus: trace
weight: 3
---

PASS if "Current account fee" does not end up as rent: the matching is on whole words (for example `\b` or a split into words), or the trace shows the final output with that line under other. FAIL if the output puts the 1.50 fee under rent (rent total 951.50) without comment.
