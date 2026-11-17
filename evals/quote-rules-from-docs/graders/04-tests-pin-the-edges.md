---
type: llm
focus: trace
weight: 3
---

Count which of these six edges of docs/pricing.md the tests for quote_cents pin, by a case or a law that would fail if the behaviour changed by one: (1) both sides of the discount tier boundaries (9/10, 49/50, 199/200 units) and the member bonus of exactly 3 points on a case the cap does not hide; (2) the 25-point cap, and the cap of 40 starting at exactly 1000 units (999 still capped at 25); (3) free shipping at the thresholds, both sides, for a member (2999/3000) and a non-member (4999/5000), judged on the discounted price; (4) the weight steps: 1000 g and 1001 g, 1500 g and 1501 g, 2000 g and 2001 g, and each zone's base fee; (5) the express surcharge: 15% of the regular fee rounded up (a case with a fractional cent) and still charged when shipping is free; (6) every ValueError (quantity 0, negative unit price, coupon 101 or -1, negative weight, unknown zone). PASS if at least five are pinned. FAIL otherwise. A property-based test or a table both count, if they would catch these changes.
