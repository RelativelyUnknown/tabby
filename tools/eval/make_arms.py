#!/usr/bin/env python3
"""make_arms.py: build plugin copies with parts removed, for an ablation of what gives which gain.

    python3 tools/eval/make_arms.py OUT_DIR

Writes OUT_DIR/<arm>/ for each arm below, each a full plugin folder you can pass to run.py with --plugin and --plugin-dir.

    full         the plugin as it is
    no-gate      SessionStart only: core rules and detect output, no ruff hook, no Stop check
    gate-only    PostToolUse and Stop only: no core injection
    skills-only  no hooks at all: the skills and their pages
    core-only    SessionStart only and no skills: just the always-on core rules

Compare two arms with `summarise.py DIR_A --compare DIR_B`. The `without` arm of any run is the no-plugin baseline.
Stdlib only. Copies the repository without .git, results and caches.
"""
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
IGNORE = shutil.ignore_patterns(".git", "results", "__pycache__", "*.pyc", "node_modules")


def keep_hooks(arm, events):
    p = os.path.join(arm, "hooks", "hooks.json")
    if events is None:
        os.remove(p)
        return
    doc = json.load(open(p))
    doc["hooks"] = {k: v for k, v in doc["hooks"].items() if k in events}
    json.dump(doc, open(p, "w"), indent=2)


def main(argv):
    if len(argv) != 1:
        print(__doc__)
        return 1
    out = os.path.abspath(argv[0])
    arms = {"full": ({"SessionStart", "PostToolUse", "Stop"}, True), "no-gate": ({"SessionStart"}, True),
            "gate-only": ({"PostToolUse", "Stop"}, True), "skills-only": (None, True), "core-only": ({"SessionStart"}, False)}
    for name, (events, skills) in arms.items():
        dest = os.path.join(out, name)
        if os.path.exists(dest):
            shutil.rmtree(dest)
        shutil.copytree(ROOT, dest, ignore=IGNORE)
        keep_hooks(dest, events)
        if not skills:
            pj = os.path.join(dest, ".claude-plugin", "plugin.json")
            doc = json.load(open(pj))
            doc["skills"] = []
            json.dump(doc, open(pj, "w"), indent=2)
        print("built", dest)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
