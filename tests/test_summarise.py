import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "tools" / "eval"))
import summarise  # noqa: E402


def run(**passed):
    return {"graders": [{"name": n, "passed": p} for n, p in passed.items()]}


def test_dead_and_vacuous_graders_are_found():
    cases = {"c": {"arms": {
        "with": [run(always=True, never=False, mixed=True, **{"x-skill-was-invoked-indicator-only": True})],
        "without": [run(always=True, never=False, mixed=False, **{"x-skill-was-invoked-indicator-only": False})],
    }}}
    dead, vacuous = summarise.grader_health(cases)
    assert dead == ["c/never"]
    assert vacuous == ["c/always"]


def test_indicator_that_fails_without_the_plugin_is_not_dead():
    cases = {"c": {"arms": {"with": [run(**{"s-skill-was-invoked": False})], "without": [run(**{"s-skill-was-invoked": False})]}}}
    assert summarise.grader_health(cases) == ([], [])
