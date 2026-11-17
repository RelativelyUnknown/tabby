"""Hidden checks for quote-rules-from-docs (never present while the agent works).

Part 1: the agent's quote_cents against docs/pricing.md (a reference built from the same text), over a boundary grid,
and its ValueErrors.
Part 2: a mutation grade of the agent's own tests. Each mutant is the reference with exactly one knob changed, appended
to pricing.py in a scratch copy; the agent's tests must fail on it.
"""
import itertools
import pathlib
import shutil
import subprocess
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "src"))
from shop.pricing import quote_cents  # noqa: E402

REFERENCE = dict(
    t1=10, t2=50, t3=200, member=3, cap=25, lift=1000, caphi=40, half_up=False,
    check_qty=True, check_coupon=True, coupon_counts=True,
    zone_a=500, zone_b=900, zone_c=1500, incl_w=1000, step=500, per_step=190, steps_ceil=True,
    free_non=5000, free_member=3000, free_on_gross=False,
    express_pct=15, express_up=True, express_on_free=True, check_zone=True, check_weight=True,
)

TEMPLATE = '''
def quote_cents(unit_cents, quantity, member, coupon_pct, weight_g, zone, express):
    if {check_qty} and quantity < 1:
        raise ValueError("quantity")
    if unit_cents < 0:
        raise ValueError("unit_cents")
    if {check_coupon} and not 0 <= coupon_pct <= 100:
        raise ValueError("coupon_pct")
    if {check_weight} and weight_g < 0:
        raise ValueError("weight_g")
    base = {{"A": {zone_a}, "B": {zone_b}, "C": {zone_c}}}.get(zone)
    if base is None:
        if {check_zone}:
            raise ValueError("zone")
        base = 0
    points = 15 if quantity >= {t3} else 10 if quantity >= {t2} else 5 if quantity >= {t1} else 0
    points += {member} if member else 0
    points += coupon_pct if {coupon_counts} else 0
    points = min(points, {caphi} if quantity >= {lift} else {cap})
    gross = unit_cents * quantity
    price = (gross * (100 - points) + {half_up_add}) // 100
    over = weight_g - {incl_w}
    if over > 0:
        steps = (over + {step} - 1) // {step} if {steps_ceil} else over // {step}
    else:
        steps = 0
    regular = base + steps * {per_step}
    basis = gross if {free_on_gross} else price
    free = basis >= ({free_member} if member else {free_non})
    surcharge = (regular * {express_pct} + {up_add}) // 100
    total = price + (0 if free else regular)
    if express and (not free or {express_on_free}):
        total += surcharge
    return total
'''


def source(**changes):
    knobs = {**REFERENCE, **changes}
    knobs["half_up_add"] = 50 if knobs["half_up"] else 0
    knobs["up_add"] = 99 if knobs["express_up"] else 0
    return TEMPLATE.format(**knobs)


ns = {}
exec(source(), ns)  # noqa: S102 - the reference rule, from this file
reference = ns["quote_cents"]

QUANTITIES = [1, 9, 10, 50, 199, 200, 999, 1000]
UNITS = [0, 1, 199, 1000, 2999, 3000, 5000]
COUPONS = [0, 10, 50, 100]
WEIGHTS = [0, 1000, 1001, 1500, 1501, 2500]


def test_follows_the_document_on_the_boundary_grid():
    for q, u, m, c, w, z, e in itertools.product(QUANTITIES, UNITS, (False, True), COUPONS, WEIGHTS, "ABC", (False, True)):
        assert quote_cents(u, q, m, c, w, z, e) == reference(u, q, m, c, w, z, e), (u, q, m, c, w, z, e)


def test_raises_value_error_on_bad_input():
    good = (100, 5, False, 0, 500, "A", False)
    for index, bad in [(1, 0), (0, -1), (3, -1), (3, 101), (4, -1), (5, "D")]:
        args = list(good)
        args[index] = bad
        with pytest.raises(ValueError):
            quote_cents(*args)


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
    "zone_a_501": dict(zone_a=501), "zone_b_899": dict(zone_b=899), "zone_c_1501": dict(zone_c=1501),
    "included_999": dict(incl_w=999), "included_1001": dict(incl_w=1001),
    "step_499": dict(step=499), "step_501": dict(step=501),
    "per_step_189": dict(per_step=189), "per_step_191": dict(per_step=191),
    "steps_rounded_down": dict(steps_ceil=False),
    "free_non_4999": dict(free_non=4999), "free_non_5001": dict(free_non=5001),
    "free_member_2999": dict(free_member=2999), "free_member_3001": dict(free_member=3001),
    "member_uses_5000": dict(free_member=5000),
    "free_on_gross": dict(free_on_gross=True),
    "express_14": dict(express_pct=14), "express_16": dict(express_pct=16),
    "express_rounds_down": dict(express_up=False),
    "express_waived_when_free": dict(express_on_free=False),
    "no_zone_check": dict(check_zone=False), "no_weight_check": dict(check_weight=False),
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
