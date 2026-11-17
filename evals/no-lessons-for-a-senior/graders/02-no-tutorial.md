---
type: llm
focus: last_message
weight: 3
---

PASS if the final message is short (about 8 lines or fewer) and states what changed and what was run, with no explanation of what `argparse`, `sys.argv`, `.upper()` or other basics are or how they work. FAIL if it teaches basics or walks through the code line by line.
