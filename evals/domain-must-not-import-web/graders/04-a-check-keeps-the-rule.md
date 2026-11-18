---
type: llm
focus: trace
weight: 3
---

PASS if the change adds an automated check that fails when a domain module imports the web layer (an import-linter contract in pyproject.toml, a test that parses the domain files' imports, or equivalent) and the trace shows it ran. FAIL if the rule is only stated in a comment, the docs or the reply.
