---
tags: [development, testing]
max_turns: 40
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Add `quote_cents(unit_cents, quantity, member, coupon_pct, weight_g, zone, express)` to `src/shop/pricing.py`. It returns the total for an order line as `docs/pricing.md` describes it. Put the tests in `tests/test_pricing.py` and run them.
