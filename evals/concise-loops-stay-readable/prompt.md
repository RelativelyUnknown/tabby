---
tags: [development, headroom]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Add `summarise(orders)` to the shop package: it returns the total of the paid orders per customer, and the id of the largest paid order (`None` when there are no paid orders). Add a test.
