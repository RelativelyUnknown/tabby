---
tags: [development, headroom]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Add an `Order` model to `src/orders/models.py` with `items: list[Item]` and `email: str`. The email must contain an `@`, reject it otherwise. Add a method or function that returns the order as a dict.
