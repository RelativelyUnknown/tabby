import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

INSTALL = pathlib.Path(__file__).resolve().parents[1] / "tools/install.py"


def install(cwd, *args):
    return subprocess.run([sys.executable, str(INSTALL), *args], cwd=cwd, capture_output=True, text=True)


class Install(unittest.TestCase):
    def test_opencode_gets_subagent_file(self):
        with tempfile.TemporaryDirectory() as d:
            r = install(d, "opencode")
            self.assertEqual(r.returncode, 0, r.stderr)
            text = pathlib.Path(d, ".opencode/agents/tabby-reviewer.md").read_text()
        self.assertIn("mode: subagent", text)
        self.assertIn("You review a change you did not write", text)

    def test_copilot_agent_suffix_and_tools(self):
        with tempfile.TemporaryDirectory() as d:
            install(d, "github")
            text = pathlib.Path(d, ".github/agents/tabby-reviewer.agent.md").read_text()
        self.assertIn('tools: ["read", "search", "execute"]', text)

    def test_agents_target_has_no_agent_dir_and_flag_skips(self):
        with tempfile.TemporaryDirectory() as d:
            install(d, "agents")
            install(d, "opencode", "--no-agent")
            self.assertFalse(os.path.exists(os.path.join(d, ".agents/agents")))
            self.assertFalse(os.path.exists(os.path.join(d, ".opencode/agents")))


if __name__ == "__main__":
    unittest.main()
