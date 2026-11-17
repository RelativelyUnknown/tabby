#!/usr/bin/env bash
# Builds the fixture project for the `month-end-billing-date` case in the empty workspace.
set -euo pipefail
cat > billing.py <<'__FIXTURE_EOF__'
from datetime import date


def invoice_label(d: date) -> str:
    return d.strftime("INV-%Y%m")
__FIXTURE_EOF__
mkdir tests
cat > tests/test_billing.py <<'__FIXTURE_EOF__'
from datetime import date

from billing import invoice_label


def test_invoice_label():
    assert invoice_label(date(2026, 9, 3)) == "INV-202609"
__FIXTURE_EOF__
git init -q -b main
git add -A
git -c user.email=eval@example.com -c user.name=eval commit -qm base
