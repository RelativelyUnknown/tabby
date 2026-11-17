---
tags: [development, testing]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Add `final_price_cents(unit_cents, quantity, member, coupon_pct)` to `src/shop/pricing.py`, with tests in `tests/test_pricing.py`. It returns the price in whole cents for `quantity` units at `unit_cents` each, after discounts.

The rules: the quantity tier gives 0 points off below 10 units, 5 points from 10 to 49, 10 points from 50 to 199 and 15 points from 200. A member gets 3 more points. `coupon_pct` (a whole number, 0 to 100) adds that many more points. The points add up but are capped at 25, except for an order of 1000 units or more, where the cap is 40. The price is the gross amount (`unit_cents * quantity`) times (100 minus the points) over 100, rounded down to a whole cent. A quantity below 1, a negative unit price or a `coupon_pct` outside 0 to 100 raises `ValueError`. Run the tests.
