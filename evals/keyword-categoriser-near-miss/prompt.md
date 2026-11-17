---
tags: [correctness, input]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Write categorize.py that reads export.csv (semicolon separated: Datum;Omschrijving;Bedrag) and prints the total per category. Categories are rent (keyword "rent"), food (keyword "albert heijn") and other. Run it on my export.
