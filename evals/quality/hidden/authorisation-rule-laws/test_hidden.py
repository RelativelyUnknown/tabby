"""Hidden checks for authorisation-rule-laws (never present while the agent works).

Part 1: the agent's can_delete against the rules, all 12 combinations.
Part 2: a mutation grade of the agent's own tests: each broken can_delete below is swapped in
(appended to rules.py in a scratch copy) and the agent's tests must fail. A suite that still
passes on a broken rule does not pin the behaviour.
"""
import itertools
import pathlib
import shutil
import subprocess
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "src"))
from docshare.rules import can_delete  # noqa: E402

TABLE = {
    ("admin", True, True): True, ("admin", True, False): True,
    ("admin", False, True): True, ("admin", False, False): True,
    ("editor", True, False): True,
    ("editor", True, True): False, ("editor", False, True): False, ("editor", False, False): False,
    ("viewer", True, True): False, ("viewer", True, False): False,
    ("viewer", False, True): False, ("viewer", False, False): False,
}


@pytest.mark.parametrize("role,owner,locked", sorted(TABLE))
def test_follows_the_rules(role, owner, locked):
    assert can_delete(role, owner, locked) is TABLE[(role, owner, locked)]


MUTANTS = {
    "refuse_all": "return False",
    "editor_ignores_lock": 'return role == "admin" or (role == "editor" and is_owner)',
    "editor_need_not_own": 'return role == "admin" or (role == "editor" and not locked)',
    "lock_blocks_admin": 'return not locked and (role == "admin" or (role == "editor" and is_owner))',
    "any_owner_may": 'return role == "admin" or (is_owner and not locked)',
    "editors_never": 'return role == "admin"',
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
    rules = proj / "src" / "docshare" / "rules.py"
    rules.write_text(rules.read_text() + f"\n\ndef can_delete(role, is_owner, locked):\n    {MUTANTS[name]}\n")
    assert run_suite(proj) != 0, f"mutant {name} survived: the tests do not pin this behaviour"
