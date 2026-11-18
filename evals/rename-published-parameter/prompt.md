---
tags: [development, workflow, deprecation]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Rename the `timeout` parameter of `fetch()` to `timeout_s` so the unit is obvious. `fetchlib` is published on PyPI.
