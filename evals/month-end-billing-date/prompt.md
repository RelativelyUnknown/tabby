---
tags: [correctness, time]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Add a function `next_billing_date(start: date, months: int = 1) -> date` to billing.py. A customer who signed up on a date is billed on the same day every month. Python 3.12, standard library only.
