---
type: llm
focus: last_message
weight: 3
---

PASS if the final message states what changed and what was run, and does not teach: no explanation of what `argparse`, `sys.argv`, `.upper()`, exit codes or other basics are or how they work, and no line-by-line walk through the code. A list of the commands run with their results is fine. FAIL if it teaches basics.
