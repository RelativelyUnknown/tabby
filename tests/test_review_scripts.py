import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = pathlib.Path(__file__).resolve().parents[1] / "tabby-review/scripts"
GIT = ["git", "-c", "user.email=t@example.com", "-c", "user.name=t"]


def sh(cwd, *cmd):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=True)


class Cochange(unittest.TestCase):
    def repo(self, d):
        sh(d, "git", "init", "-q")
        (pathlib.Path(d) / "a.py").write_text("X = 1\n")
        (pathlib.Path(d) / "b.py").write_text("Y = 1\n")
        (pathlib.Path(d) / "c.py").write_text("import a\n")
        for i in range(6):
            (pathlib.Path(d) / "a.py").write_text(f"X = {i}\n")
            (pathlib.Path(d) / "b.py").write_text(f"Y = {i}\n")
            (pathlib.Path(d) / "c.py").write_text(f"import a\nZ = {i}\n")
            sh(d, *GIT, "add", "-A")
            sh(d, *GIT, "commit", "-qm", f"c{i}")

    def test_pair_without_import_is_listed_and_linked_pair_is_not(self):
        with tempfile.TemporaryDirectory() as d:
            self.repo(d)
            rows = json.loads(sh(d, sys.executable, str(SCRIPTS / "cochange.py"), d, "--json").stdout)
        pairs = {(r["a"], r["b"]) for r in rows}
        self.assertIn(("a.py", "b.py"), pairs)
        self.assertIn(("b.py", "c.py"), pairs)
        self.assertNotIn(("a.py", "c.py"), pairs)  # c imports a

    def test_all_lists_linked_pairs(self):
        with tempfile.TemporaryDirectory() as d:
            self.repo(d)
            rows = json.loads(sh(d, sys.executable, str(SCRIPTS / "cochange.py"), d, "--json", "--all").stdout)
        self.assertTrue(any(r["a"] == "a.py" and r["b"] == "c.py" and r["import_link"] for r in rows))


class MutationProbe(unittest.TestCase):
    def run_probe(self, tests):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d)
            src = "def ok(n):\n    return n >= 18\n"
            (p / "rules.py").write_text(src)
            (p / "test_rules.py").write_text("from rules import ok\n" + tests)
            r = subprocess.run([sys.executable, str(SCRIPTS / "mutation_probe.py"), "rules.py", "--json"],
                               cwd=d, capture_output=True, text=True)
            self.assertEqual((p / "rules.py").read_text(), src, "the source file must be restored")
        return r

    def test_weak_test_leaves_survivors_and_strong_test_does_not(self):
        weak = json.loads(self.run_probe("def test_a():\n    assert ok(30)\ndef test_b():\n    assert ok is not None\n").stdout)
        strong = json.loads(self.run_probe("def test_a():\n    assert ok(18)\ndef test_b():\n    assert not ok(17)\n").stdout)
        self.assertTrue(weak["survivors"])
        self.assertTrue(any("test_b" in t for t in weak["never_red"]))
        self.assertEqual(strong["survivors"], [])

    def test_red_baseline_is_refused(self):
        r = self.run_probe("def test_a():\n    assert not ok(30)\n")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("baseline", r.stderr)


if __name__ == "__main__":
    unittest.main()
