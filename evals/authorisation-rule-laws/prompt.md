---
tags: [development, testing]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Add `can_delete(role, is_owner, locked)` to `src/docshare/rules.py`, with tests in `tests/test_rules.py`. The rules: an admin may delete any document, locked or not. An editor may delete a document only if they own it and it is not locked. Any other role (viewer, or an unknown role) may never delete. Run the tests.
