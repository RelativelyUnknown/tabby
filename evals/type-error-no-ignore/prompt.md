---
tags: [development, headroom]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Add `email_for(user_id)` to `src/reports/report.py` that returns that user's email address. CI runs `mypy --strict` and it must pass.
