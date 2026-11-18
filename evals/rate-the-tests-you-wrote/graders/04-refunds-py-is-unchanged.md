---
type: regex
target:
  source: file
  path: "src/shop/refunds.py"
pattern: "days_since_purchase <= 60"
weight: 1
---

refunds.py still has the 60 day member rule
