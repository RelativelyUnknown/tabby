import copy
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tabby-review/scripts"))
from validate_findings import check  # noqa: E402

GOOD = {
    "verdict": "request changes: one SQL injection",
    "overall_severity": "high",
    "findings": [
        {"id": "F1", "bucket": "confirmed", "title": "SQL built from query string", "file": "app/db.py", "line": 2,
         "entry_point": "GET /users?sort=", "payload": "id; drop table users", "mechanism": "f-string into execute",
         "effect": "arbitrary SQL", "severity": "high", "likelihood": "high", "fix": "allowlist the column",
         "regression_test": "tests/test_sort.py::test_rejects_unknown_column"},
        {"id": "F2", "bucket": "needs_validation", "title": "Proxy trust", "file": "app/db.py", "line": 1,
         "question": "Does the proxy strip X-Forwarded-For?", "who_can_answer": "platform team"},
        {"id": "F3", "bucket": "rejected", "title": "pickle in cache", "file": "app/db.py", "line": 3, "control": "cache is written only by this process"},
    ],
    "coverage": {"read": ["app/db.py"], "ran": [], "not_checked": ["deployment"], "classes": {"sql": "finding", "xss": "not_applicable"}},
}


class Validate(unittest.TestCase):
    def test_good_report(self):
        self.assertEqual(check(GOOD), [])

    def test_confirmed_needs_every_field(self):
        d = copy.deepcopy(GOOD)
        del d["findings"][0]["regression_test"]
        self.assertTrue(any("regression_test" in e for e in check(d)))

    def test_severity_only_on_confirmed(self):
        d = copy.deepcopy(GOOD)
        d["findings"][1]["severity"] = "low"
        self.assertTrue(any("only confirmed" in e for e in check(d)))

    def test_overall_cannot_exceed_worst_confirmed(self):
        d = copy.deepcopy(GOOD)
        d["findings"][0]["severity"] = "low"
        self.assertTrue(any("higher than the worst" in e for e in check(d)))

    def test_file_and_line_checked_against_root(self):
        with tempfile.TemporaryDirectory() as r:
            p = pathlib.Path(r) / "app"
            p.mkdir()
            (p / "db.py").write_text("a\nb\nc\n")
            self.assertEqual(check(GOOD, r), [])
            d = copy.deepcopy(GOOD)
            d["findings"][0]["line"] = 40
            self.assertTrue(any("past the end" in e for e in check(d, r)))

    def test_coverage_required(self):
        d = copy.deepcopy(GOOD)
        del d["coverage"]
        self.assertTrue(any("coverage" in e for e in check(d)))


if __name__ == "__main__":
    unittest.main()
