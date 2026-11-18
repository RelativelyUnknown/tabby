---
type: llm
focus: trace
weight: 3
---

PASS if the invalid combinations (status shipped with no shipped_at, status cancelled with no reason, shipped and cancelled together) are ruled out in one place: a separate class per state, an enum with a transition table, or one validation function or __post_init__ that every transition passes through. FAIL if ship and cancel each re-check status strings and flags on their own with no shared rule.
