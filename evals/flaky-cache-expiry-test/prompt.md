---
tags: [development, testing, debugging]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

`tests/test_cache.py::test_value_is_returned_before_expiry` fails now and then on our slow CI runner. Make the tests reliable. Do not make the suite slower.
