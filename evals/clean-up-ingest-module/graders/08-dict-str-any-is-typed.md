---
type: regex
target:
  source: file
  path: "src/reports/ingest.py"
pattern: "dict\\[str,\\s*Any\\]"
match: not_contains
weight: 1
---

The `dict[str, Any]` annotation was replaced by a typed shape (dataclass, TypedDict or a concrete type)
