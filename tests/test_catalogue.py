import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools/eval"))
import catalogue  # noqa: E402


class Catalogue(unittest.TestCase):
    def test_testing_md_is_current(self):
        text = (ROOT / "TESTING.md").read_text()
        current = text[text.index(catalogue.START):text.index(catalogue.END) + len(catalogue.END)]
        self.assertEqual(current, catalogue.build(), "run: python3 tools/eval/catalogue.py")

    def test_every_case_is_grouped(self):
        names = {c["name"] for c in catalogue.cases()}
        self.assertGreater(len(names), 100)


if __name__ == "__main__":
    unittest.main()
