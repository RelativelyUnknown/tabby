---
tags: [development, architecture]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Add `ship(order, when)` and `cancel(order, reason)` to `src/shop/orders.py`, with tests. A shipped order cannot be cancelled, a cancelled order cannot be shipped, and neither can happen twice. Run the tests.
