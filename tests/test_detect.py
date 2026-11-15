import pathlib
import subprocess
import sys
import tempfile
import unittest

DETECT = pathlib.Path(__file__).resolve().parents[1] / "tabby/scripts/detect.py"
PYPROJECT = """[project]
name = "x"
requires-python = ">=3.11"
[tool.ruff.lint]
select = ["E", "F", "B"]
ignore = ["E501"]
[tool.mypy]
strict = true
[tool.pytest.ini_options]
xfail_strict = true
addopts = "--strict-config"
"""


def detect(root):
    return subprocess.run([sys.executable, str(DETECT), str(root)], capture_output=True, text=True).stdout


class Detect(unittest.TestCase):
    def test_house_rules_and_helpers(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            (root / "pyproject.toml").write_text(PYPROJECT)
            (root / "src/pkg").mkdir(parents=True)
            (root / "src/pkg/utils.py").write_text("")
            out = detect(root)
        self.assertIn("ruff select E,F,B", out)
        self.assertIn("mypy strict", out)
        self.assertIn("pytest xfail_strict", out)
        self.assertIn("src/ layout", out)
        self.assertIn("no syntax newer than python >=3.11", out)
        self.assertIn("src/pkg/utils.py", out)

    def test_empty_repo_does_not_fail(self):
        with tempfile.TemporaryDirectory() as d:
            out = detect(d)
        self.assertIn("house rules: none found", out)
        self.assertIn("existing helpers", out)


if __name__ == "__main__":
    unittest.main()
