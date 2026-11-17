#!/usr/bin/env bash
# Builds the fixture project for the `pricing-rule-laws` case in the empty workspace.
# Run by `claude plugin eval --scaffold`. Files only, plus git history.
set -euo pipefail

cat > pyproject.toml <<'__FIXTURE_EOF__'
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "shop"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = []

[dependency-groups]
dev = ["pytest", "hypothesis"]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
__FIXTURE_EOF__
mkdir -p src/shop tests
touch src/shop/__init__.py
cat > src/shop/pricing.py <<'__FIXTURE_EOF__'
"""Prices for order lines. Pure rules: no I/O."""


def line_total_cents(unit_cents: int, quantity: int) -> int:
    """Gross amount for a line, before any discount."""
    return unit_cents * quantity
__FIXTURE_EOF__
cat > tests/test_pricing.py <<'__FIXTURE_EOF__'
from shop.pricing import line_total_cents


def test_line_total_multiplies():
    assert line_total_cents(250, 4) == 1000
__FIXTURE_EOF__

git init -q -b main
git add -A
git -c user.email=eval@example.com -c user.name=eval commit -qm base
