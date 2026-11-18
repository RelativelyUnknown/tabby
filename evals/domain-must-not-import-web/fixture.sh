#!/usr/bin/env bash
# Builds the fixture project for the `domain-must-not-import-web` case in the empty workspace.
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
mkdir -p src/shop/domain
cat > src/shop/domain/__init__.py <<'__FIXTURE_EOF__'

__FIXTURE_EOF__
mkdir -p src/shop/domain
cat > src/shop/domain/pricing.py <<'__FIXTURE_EOF__'
"""Prices. Pure rules."""


def price_cents(unit_cents: int, quantity: int) -> int:
    return unit_cents * quantity
__FIXTURE_EOF__
mkdir -p src/shop/web
cat > src/shop/web/__init__.py <<'__FIXTURE_EOF__'

__FIXTURE_EOF__
mkdir -p src/shop/web
cat > src/shop/web/format.py <<'__FIXTURE_EOF__'
"""Formatting for pages."""


def money(cents: int) -> str:
    return f"${cents / 100:.2f}"
__FIXTURE_EOF__
mkdir -p src/shop/web
cat > src/shop/web/views.py <<'__FIXTURE_EOF__'
from shop.domain.pricing import price_cents
from shop.web.format import money


def price_view(unit_cents: int, quantity: int) -> str:
    return money(price_cents(unit_cents, quantity))
__FIXTURE_EOF__
mkdir -p tests
cat > tests/test_views.py <<'__FIXTURE_EOF__'
from shop.web.views import price_view


def test_price_view():
    assert price_view(250, 4) == "$10.00"
__FIXTURE_EOF__

git init -q -b main
git add -A
git -c user.email=eval@example.com -c user.name=eval commit -qm base
