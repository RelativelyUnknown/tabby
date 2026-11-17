---
tags: [correctness, dependencies]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

My friends send me their bank exports and they open fine on some and break on others, I think its something about the text encoding. Make `load_rows(path)` in rows.py work for all of them.
