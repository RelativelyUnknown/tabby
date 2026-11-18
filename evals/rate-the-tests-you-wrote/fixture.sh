#!/usr/bin/env bash
# Builds the fixture project for the `rate-the-tests-you-wrote` case in the empty workspace.
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
cat > src/shop/refunds.py <<'__FIXTURE_EOF__'
"""Refund eligibility. Pure rules: no I/O."""


def can_refund(days_since_purchase: int, amount_cents: int, member: bool) -> bool:
    """Refund within 30 days; members get 60. Nothing is refunded for a zero or negative amount."""
    if amount_cents <= 0:
        return False
    if member and days_since_purchase <= 60:
        return True
    return days_since_purchase <= 30
__FIXTURE_EOF__
mkdir -p tests
cat > tests/test_refunds.py <<'__FIXTURE_EOF__'
from shop.refunds import can_refund


def test_refund_works():
    assert can_refund(10, 500, False)


def test_returns_a_bool():
    assert isinstance(can_refund(10, 500, False), bool)


def test_result_is_not_none():
    assert can_refund(1, 1, True) is not None


def test_member_after_45_days():
    assert can_refund(45, 500, True)
__FIXTURE_EOF__

git init -q -b main
git add -A
git -c user.email=eval@example.com -c user.name=eval commit -qm base
