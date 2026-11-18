---
tags: [development, testing]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

`tests/test_refunds.py` was written in a hurry. Tell me which of its tests are worth keeping, and bring the file to the point where a change that breaks the refund rule in `src/shop/refunds.py` makes a test fail. Do not change `refunds.py`. Run the tests.
