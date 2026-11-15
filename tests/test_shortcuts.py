import pathlib
import subprocess
import sys
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "tabby-debt/scripts/shortcuts.py"


def run(root, *flags):
    return subprocess.run([sys.executable, str(SCRIPT), str(root), *flags], capture_output=True, text=True)


class Shortcuts(unittest.TestCase):
    def test_ledger_and_flags(self):
        with tempfile.TemporaryDirectory() as d:
            (pathlib.Path(d) / "a.py").write_text(
                "a = 1  # shortcut: linear scan, move to an index past 10k rows\nb = 2  # shortcut: hard-coded UTC\n")
            r = run(d, "--check")
        self.assertEqual(r.returncode, 1)
        self.assertIn("a.py:1 | linear scan | move to an index past 10k rows | -", r.stdout)
        self.assertIn("a.py:2 | hard-coded UTC | - | no trigger", r.stdout)

    def test_clean_repo_passes_check(self):
        with tempfile.TemporaryDirectory() as d:
            (pathlib.Path(d) / "a.py").write_text("a = 1  # shortcut: single worker, add a queue past 50 jobs a minute\n")
            self.assertEqual(run(d, "--check").returncode, 0)

    def test_none_found(self):
        with tempfile.TemporaryDirectory() as d:
            (pathlib.Path(d) / "a.py").write_text("a = 1\n")
            self.assertIn("No `# shortcut:` comments", run(d).stdout)


if __name__ == "__main__":
    unittest.main()
