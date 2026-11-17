#!/usr/bin/env bash
# Builds the fixture project for the `quote-rules-from-docs` case in the empty workspace.
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
mkdir -p src/shop tests docs
touch src/shop/__init__.py
cat > docs/pricing.md <<'__FIXTURE_EOF__'
# How an order line is priced

All amounts are whole cents. The total of a line is the discounted price, plus shipping, plus the express surcharge.

## Discounted price

The gross amount is `unit_cents * quantity`. The discount is given in points; one point is one percent.

| Quantity | Tier points |
| --- | --- |
| under 10 | 0 |
| 10 to 49 | 5 |
| 50 to 199 | 10 |
| 200 or more | 15 |

A member gets 3 more points. The coupon (`coupon_pct`, 0 to 100) adds its value in points. The points add up and are capped at 25; an order of 1000 units or more is capped at 40 instead.

The discounted price is the gross amount times (100 minus the points), divided by 100, rounded down to a whole cent.

## Shipping

Shipping is charged per order line from the zone and the weight (`weight_g`, whole grams).

| Zone | Base fee |
| --- | --- |
| A | 500 |
| B | 900 |
| C | 1500 |

The base fee covers up to 1000 g. Every 500 g started above that adds 190: 1001 g to 1500 g costs 190 more, 1501 g to 2000 g costs 380 more, and so on. The regular shipping fee is the base fee plus the weight surcharge.

Shipping is free when the discounted price is at least 5000, or at least 3000 for a member. Free shipping removes the regular shipping fee from the total.

## Express

Express delivery adds 15% of the regular shipping fee, rounded up to a whole cent. It is charged even when shipping itself is free.

## Invalid input

A quantity below 1, a negative unit price, a coupon outside 0 to 100, a negative weight or an unknown zone raises `ValueError`.
__FIXTURE_EOF__
cat > src/shop/pricing.py <<'__FIXTURE_EOF__'
"""Prices for order lines. Pure rules: no I/O. The rules are in docs/pricing.md."""


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
