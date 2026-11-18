#!/usr/bin/env bash
# Builds the fixture project for the `vat-rate-in-three-places` case in the empty workspace.
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
dev = ["pytest"]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
__FIXTURE_EOF__
mkdir -p src/shop
cat > src/shop/__init__.py <<'__FIXTURE_EOF__'

__FIXTURE_EOF__
mkdir -p src/shop
cat > src/shop/invoice.py <<'__FIXTURE_EOF__'
"""Invoices."""


def invoice_total_cents(net_cents: int) -> int:
    """Gross total on an invoice."""
    return round(net_cents * 1.19)
__FIXTURE_EOF__
mkdir -p src/shop
cat > src/shop/checkout.py <<'__FIXTURE_EOF__'
"""Checkout."""


def checkout_preview_cents(net_cents: int) -> int:
    """Price shown to the customer before they pay."""
    return net_cents * 119 // 100
__FIXTURE_EOF__
mkdir -p src/shop
cat > src/shop/export.py <<'__FIXTURE_EOF__'
"""Accounting export."""


def export_gross_cents(net_cents: int) -> int:
    """Gross amount written to the monthly export."""
    return net_cents + net_cents * 19 // 100
__FIXTURE_EOF__
mkdir -p tests
cat > tests/test_vat.py <<'__FIXTURE_EOF__'
from shop.checkout import checkout_preview_cents
from shop.export import export_gross_cents
from shop.invoice import invoice_total_cents


def test_invoice_total():
    assert invoice_total_cents(1000) == 1190


def test_checkout_preview():
    assert checkout_preview_cents(1000) == 1190


def test_export_gross():
    assert export_gross_cents(1000) == 1190
__FIXTURE_EOF__

git init -q -b main
git add -A
git -c user.email=eval@example.com -c user.name=eval commit -qm base
