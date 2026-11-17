"""Hidden checks for pricing-rule-laws (never present while the agent works).

Part 1: the agent's final_price_cents against the rules, over a grid of boundary inputs, and its ValueErrors.
Part 2: a mutation grade of the agent's own tests. Each mutant is the reference rule with exactly one knob changed,
appended to pricing.py in a scratch copy; the agent's tests must fail on it.
"""
import itertools
import pathlib
import shutil
import subprocess
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "src"))
from shop.pricing import final_price_cents  # noqa: E402

REFERENCE = dict(t1=10, t2=50, t3=200, member=3, cap=25, lift=1000, caphi=40, half_up=False,
                 check_qty=True, check_coupon=True, coupon_counts=True)

TEMPLATE = '''
def final_price_cents(unit_cents, quantity, member, coupon_pct):
    if {check_qty} and quantity < 1:
        raise ValueError("quantity")
    if unit_cents < 0:
        raise ValueError("unit_cents")
    if {check_coupon} and not 0 <= coupon_pct <= 100:
        raise ValueError("coupon_pct")
    points = 15 if quantity >= {t3} else 10 if quantity >= {t2} else 5 if quantity >= {t1} else 0
    points += {member} if member else 0
    points += coupon_pct if {coupon_counts} else 0
    points = min(points, {caphi} if quantity >= {lift} else {cap})
    return (unit_cents * quantity * (100 - points) + {half_up_add}) // 100
'''


def source(**changes):
    knobs = {**REFERENCE, **changes}
    knobs["half_up_add"] = 50 if knobs["half_up"] else 0
    return TEMPLATE.format(**knobs)


ns = {}
exec(source(), ns)  # noqa: S102 - the reference rule, from this file
reference = ns["final_price_cents"]

QUANTITIES = [1, 9, 10, 11, 49, 50, 51, 199, 200, 201, 999, 1000, 1001]
UNITS = [0, 1, 3, 199, 1000]
COUPONS = [0, 1, 5, 10, 17, 22, 23, 25, 40, 50, 100]


def test_follows_the_rules_on_the_boundary_grid():
    for q, u, m, c in itertools.product(QUANTITIES, UNITS, (False, True), COUPONS):
        assert final_price_cents(u, q, m, c) == reference(u, q, m, c), (u, q, m, c)


def test_raises_value_error_on_bad_input():
    for args in [(100, 0, False, 0), (100, -1, False, 0), (-1, 5, False, 0), (100, 5, False, -1), (100, 5, False, 101)]:
        with pytest.raises(ValueError):
            final_price_cents(*args)


MUTANTS = {
    "tier1_after_10": dict(t1=11), "tier1_from_9": dict(t1=9),
    "tier2_after_50": dict(t2=51), "tier2_from_49": dict(t2=49),
    "tier3_after_200": dict(t3=201), "tier3_from_199": dict(t3=199),
    "member_2": dict(member=2), "member_4": dict(member=4),
    "cap_24": dict(cap=24), "cap_26": dict(cap=26),
    "lift_after_1000": dict(lift=1001), "lift_from_999": dict(lift=999),
    "lifted_cap_39": dict(caphi=39), "lifted_cap_41": dict(caphi=41),
    "rounds_half_up": dict(half_up=True),
    "no_quantity_check": dict(check_qty=False), "no_coupon_check": dict(check_coupon=False),
    "coupon_ignored": dict(coupon_counts=False),
}


def run_suite(root):
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-x", "tests"],
        cwd=root, capture_output=True, text=True, timeout=240,
    ).returncode


def scratch(tmp_path):
    dest = tmp_path / "proj"
    shutil.copytree(HERE, dest, ignore=shutil.ignore_patterns(
        ".git", "__pycache__", ".pytest_cache", ".hypothesis", "test_hidden.py"))
    return dest


@pytest.mark.parametrize("name", sorted(MUTANTS))
def test_agent_tests_catch_mutant(name, tmp_path):
    proj = scratch(tmp_path)
    assert run_suite(proj) == 0, "the agent's tests must pass on the agent's own code first"
    pricing = proj / "src" / "shop" / "pricing.py"
    pricing.write_text(pricing.read_text() + "\n" + source(**MUTANTS[name]))
    assert run_suite(proj) != 0, f"mutant {name} survived: the tests do not pin this behaviour"
