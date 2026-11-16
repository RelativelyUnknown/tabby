---
type: llm
focus: trace
weight: 2
---

PASS if, after the change, the version number 0.4.0 is written as a literal in exactly one place and the other location is derived from it (for example hatch reads the version dynamically from `__version__`, or `__version__` comes from `importlib.metadata` with a safe fallback when the package is not installed). FAIL if both `pyproject.toml` and `src/minilib/__init__.py` hold a hardcoded "0.4.0".
