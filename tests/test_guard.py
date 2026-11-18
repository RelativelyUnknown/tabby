import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
from guard import check_diff  # noqa: E402


def diff(path, added=(), removed=()):
    body = "".join(f"-{ln}\n" for ln in removed) + "".join(f"+{ln}\n" for ln in added)
    return f"diff --git a/{path} b/{path}\n--- a/{path}\n+++ b/{path}\n@@ -1 +1 @@\n{body}"


class Guard(unittest.TestCase):
    def test_clean_diff(self):
        self.assertEqual(check_diff(diff("src/a.py", ["x = 1"])), [])

    def test_suppression(self):
        self.assertTrue(check_diff(diff("src/a.py", ["x = f()  # type: ignore"])))
        self.assertTrue(check_diff(diff("src/a.py", ["import os  # noqa: F401"])))

    def test_suppression_with_reason_ok(self):
        self.assertEqual(check_diff(diff("src/a.py", ["x = f()  # type: ignore[misc]  -- stub lacks overload"])), [])

    def test_any_and_cast(self):
        self.assertTrue(check_diff(diff("src/a.py", ["def f(x: Any) -> None: ..."])))
        self.assertTrue(check_diff(diff("src/a.py", ["y = cast(int, x)"])))
        self.assertEqual(check_diff(diff("tests/test_a.py", ["y = cast(int, x)"])), [])

    def test_skip_needs_reason(self):
        self.assertTrue(check_diff(diff("tests/test_a.py", ["@pytest.mark.skip"])))
        self.assertEqual(check_diff(diff("tests/test_a.py", ['@pytest.mark.skip(reason="needs network")'])), [])

    def test_bare_except(self):
        self.assertTrue(check_diff(diff("src/a.py", ["    except:"])))
        self.assertTrue(check_diff(diff("src/a.py", ["    except Exception:", "        pass"])))
        self.assertEqual(check_diff(diff("src/a.py", ["    except KeyError:", "        pass"])), [])

    def test_except_exception_that_records_or_reraises_is_allowed(self):
        self.assertEqual(check_diff(diff("src/a.py", ["    except Exception as error:", "        failures.append(error)"])), [])
        self.assertEqual(check_diff(diff("src/a.py", ["    except Exception:", "        lock.release()", "        raise"])), [])
        self.assertTrue(check_diff(diff("src/a.py", ["    except Exception as error:", "        pass"])))
        self.assertTrue(check_diff(diff("src/a.py", ["    except BaseException as error:"])))

    def test_deleted_test_and_assertions(self):
        self.assertTrue(check_diff(diff("tests/test_a.py", [], ["def test_x():", "    assert f() == 1"])))
        self.assertTrue(check_diff(diff("tests/test_a.py", ["    assert f()"], ["    assert f() == 1", "    assert g() == 2"])))
        self.assertEqual(check_diff(diff("tests/test_a.py", ["    assert f() == 2"], ["    assert f() == 1"])), [])

    def test_deleting_a_test_that_cannot_fail_is_allowed(self):
        self.assertEqual(check_diff(diff("tests/test_a.py", [], ["def test_type():", "    assert isinstance(f(), bool)"])), [])
        self.assertEqual(check_diff(diff("tests/test_a.py", [], ["def test_x():", "    assert f() is not None"])), [])
        self.assertEqual(check_diff(diff("tests/test_a.py", [], ["def test_t():", "    assert True"])), [])
        # one real assertion, or none at all, keeps the flag
        self.assertTrue(check_diff(diff("tests/test_a.py", [], ["def test_x():", "    assert f() is not None", "    assert f() == 1"])))
        self.assertTrue(check_diff(diff("tests/test_a.py", [], ["def test_x():", "    f()"])))
        # removing a vacuous assertion from a test that keeps its real one is not weakening
        self.assertEqual(check_diff(diff("tests/test_a.py", ["    assert f() == 1"], ["    assert f() is not None", "    assert f() == 1"])), [])

    def test_non_python_ignored(self):
        self.assertEqual(check_diff(diff("README.md", ["# noqa"])), [])


if __name__ == "__main__":
    unittest.main()
