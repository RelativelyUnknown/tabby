import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "tools" / "eval"))
import rescore  # noqa: E402


def g(name, passed):
    return {"name": name, "passed": passed}


def test_indicator_and_with_only_graders_are_left_out():
    case = {"graders": [{"name": "a", "weight": 2}, {"name": "b", "weight": 1}, {"name": "x-skill-was-invoked", "weight": 1}, {"name": "w", "weight": 1}],
            "arms": {"with": [{"score": 0.5, "graders": [g("a", True), g("b", False), g("x-skill-was-invoked", False), g("w", False)]}]}}
    ref = {"arms": {"with": [{"graders": [{"name": "w", "withOnly": True}]}]}}
    assert abs(rescore.rescore(case, ref) - 2 / 3) < 1e-9
    assert abs(rescore.rescore(case, None) - 2 / 4) < 1e-9
