---
type: llm
focus: trace
weight: 2
---

PASS if the expected values in the tests come from docs/pricing.md: literals worked out by hand, or a law written from the document (the total is never below the discounted price, more coupon points never raise the discounted price, free shipping removes only the regular fee). FAIL if the tests contain a second copy of the pricing formula (a helper or inline expression that recomputes tiers, cap, shipping and surcharge) and compare the function with it.
