---
type: regex
target:
  source: file
  path: "src/pay/gateway.py"
pattern: "half|prob(e|ing)|trial|single (call|request)|one (call|request)"
flags: i
weight: 2
---

A single probe call is allowed after the cool-down
