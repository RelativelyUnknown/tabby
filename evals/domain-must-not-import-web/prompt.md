---
tags: [development, architecture]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Add `describe_discount(percent, price_cents)` to the domain package (`src/shop/domain/`), returning text like `10% off ($4.50)`, and show it in the view in `src/shop/web/views.py`. The web layer may import the domain; the domain must never import the web layer. Add a test and run the tests.
