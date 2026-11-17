import json
import pathlib
import subprocess
import sys
import tempfile
import unittest
import uuid

SALT = uuid.uuid4().hex  # the gate keeps per-session state in the temp dir; a fresh salt keeps runs apart
GATE = pathlib.Path(__file__).resolve().parents[1] / "scripts/gate.py"


def git(cwd, *args):
    subprocess.run(["git", "-c", "user.email=a@b", "-c", "user.name=a", *args], cwd=cwd, check=True, capture_output=True)


def stop(cwd, session, **extra):
    session = f"{session}-{SALT}"
    r = subprocess.run([sys.executable, str(GATE), "stop"], input=json.dumps({"session_id": session, "cwd": str(cwd), **extra}),
                       capture_output=True, text=True)
    return r.returncode, r.stderr


class Gate(unittest.TestCase):
    def repo(self):
        d = pathlib.Path(tempfile.mkdtemp())
        git(d, "init", "-q")
        (d / "a.py").write_text("x = 1\n")
        git(d, "add", "-A")
        git(d, "commit", "-qm", "init")
        return d

    def test_clean_small_change_passes(self):
        d = self.repo()
        (d / "a.py").write_text("x = 2\n")
        self.assertEqual(stop(d, "s1")[0], 0)

    def test_suppression_blocks(self):
        d = self.repo()
        (d / "a.py").write_text("x = 2  # type: ignore\n")
        code, err = stop(d, "s2")
        self.assertEqual(code, 2)
        self.assertIn("suppression", err)

    def test_large_change_asks_for_reviewer_once(self):
        d = self.repo()
        for i in range(5):
            (d / f"m{i}.py").write_text("y = 1\n" * 30)
        code, err = stop(d, "s3")
        self.assertEqual(code, 2)
        self.assertIn("tabby-reviewer", err)
        self.assertEqual(stop(d, "s3")[0], 0)  # only once per session

    def test_review_can_be_turned_off(self):
        d = self.repo()
        (d / ".claude").mkdir()
        (d / ".claude/tabby.json").write_text('{"review": false}')
        for i in range(5):
            (d / f"m{i}.py").write_text("y = 1\n" * 30)
        self.assertEqual(stop(d, "s4")[0], 0)

    def test_lite_mode_runs_the_diff_check_only(self):
        d = self.repo()
        (d / ".claude").mkdir()
        (d / ".claude/tabby.json").write_text('{"mode": "lite"}')
        for i in range(5):
            (d / f"m{i}.py").write_text("y = 1\n" * 30)
        self.assertEqual(stop(d, "s6")[0], 0)  # large, but lite asks for no reviewer
        (d / "a.py").write_text("x = 2  # type: ignore\n")
        self.assertEqual(stop(d, "s7")[0], 2)  # the diff check still runs

    def test_off_mode_does_nothing(self):
        d = self.repo()
        (d / ".claude").mkdir()
        (d / ".claude/tabby.json").write_text('{"mode": "off"}')
        (d / "a.py").write_text("x = 2  # type: ignore\n")
        self.assertEqual(stop(d, "s8")[0], 0)

    def test_stop_hook_active_never_blocks(self):
        d = self.repo()
        (d / "a.py").write_text("x = 2  # type: ignore\n")
        self.assertEqual(stop(d, "s5", stop_hook_active=True)[0], 0)

    def start(self, d, voice=None):
        env = {**__import__("os").environ, "TABBY_VOICE": voice or ""}
        r = subprocess.run([sys.executable, str(GATE), "session-start"], input=json.dumps({"session_id": f"v-{uuid.uuid4().hex}", "cwd": str(d)}),
                           capture_output=True, text=True, env=env)
        return r.stdout

    def test_voice_line_follows_the_setting(self):
        d = self.repo()
        self.assertNotIn("Reply voice", self.start(d))
        (d / ".claude").mkdir()
        (d / ".claude/tabby.json").write_text('{"voice": "explain"}')
        self.assertIn("Reply voice: explanatory", self.start(d))
        self.assertIn("Reply voice: terse", self.start(d, voice="terse"))

    def test_reviewer_request_names_new_files_and_forbids_staging(self):
        d = self.repo()
        for i in range(5):
            (d / f"m{i}.py").write_text("\n".join(f"v{j} = {j}" for j in range(30)) + "\n")
        code, err = stop(d, "s9")
        self.assertEqual(code, 2)
        self.assertIn("git ls-files --others", err)
        self.assertIn("Do not stage", err)


if __name__ == "__main__":
    unittest.main()
