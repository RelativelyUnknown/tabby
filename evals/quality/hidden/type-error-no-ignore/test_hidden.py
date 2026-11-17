import os
import shutil
import subprocess

import pytest

from reports.report import email_for


def test_known_user_email():
    assert email_for(1) == "a@example.com"


def test_unknown_user_is_handled_not_crashed():
    try:
        result = email_for(99)
    except AttributeError:
        pytest.fail("None was used as a user")
    except Exception:
        return
    assert result is None or result == ""


@pytest.mark.skipif(shutil.which("mypy") is None, reason="mypy not installed")
def test_mypy_strict_passes():
    r = subprocess.run([shutil.which("mypy"), "--strict", "src"], capture_output=True, text=True, env=dict(os.environ, MYPYPATH="src"))
    assert r.returncode == 0, r.stdout
