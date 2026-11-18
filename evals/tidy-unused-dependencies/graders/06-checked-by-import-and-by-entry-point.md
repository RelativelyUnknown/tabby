---
type: llm
focus: trace
weight: 2
---

PASS if the trace shows the agent searched the code for imports and mapped import names to package names (PIL to pillow, yaml to pyyaml), and looked beyond Python files (the Dockerfile) before deciding. FAIL if it decided from package names alone.
