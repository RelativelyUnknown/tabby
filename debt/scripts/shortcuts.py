#!/usr/bin/env python3
"""shortcuts.py: list the deliberate shortcuts in a repository as a ledger.

    python3 shortcuts.py [PROJECT_DIR] [--check] [--json]

A shortcut is a comment `# shortcut: <the limit>, <when to upgrade>` (also `//` and `--` comment styles). The ledger lists file, line,
the limit and the trigger. A comment that names no trigger is flagged, because nothing will ever prompt a revisit. With --check the exit
code is 1 when any is flagged. Reads tracked files through git when there is a repository, else walks the folder. Stdlib only.
"""
import json
import os
import pathlib
import re
import subprocess
import sys

PAT = re.compile(r"(?:#|//|--)\s*shortcut:\s*(.+?)\s*$", re.I)
SKIP = {".git", ".venv", "venv", "node_modules", "build", "dist", "__pycache__", ".tox"}
TEXT = {".py", ".pyi", ".rs", ".c", ".h", ".cpp", ".cc", ".hpp", ".zig", ".js", ".ts", ".sql", ".toml", ".yaml", ".yml", ".sh", ".cfg"}


def files(root):
    r = subprocess.run(["git", "ls-files"], cwd=root, capture_output=True, text=True)
    if r.returncode == 0 and r.stdout.strip():
        return [pathlib.Path(root) / f for f in r.stdout.splitlines()]
    out = []
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP]
        out += [pathlib.Path(dp) / f for f in fns]
    return out


def split(text):
    """(limit, trigger). The trigger is what follows the last comma, or after ' until ' / ' when ' / ' once ' / ' past '."""
    m = re.search(r"\b(until|when|once|past|beyond|if|above|over)\b.*$", text, re.I)
    if "," in text:
        limit, _, trig = text.rpartition(",")
        return limit.strip(), trig.strip()
    if m and m.start() > 0:
        return text[:m.start()].strip(" ,;"), text[m.start():].strip()
    return text.strip(), ""


def ledger(root):
    rows = []
    for p in files(root):
        if p.suffix not in TEXT:
            continue
        try:
            lines = p.read_text(errors="ignore").splitlines()
        except OSError:
            continue
        for n, ln in enumerate(lines, 1):
            m = PAT.search(ln)
            if m:
                limit, trig = split(m.group(1))
                rows.append({"file": str(p.relative_to(root)), "line": n, "limit": limit, "trigger": trig, "flag": "" if trig and limit else "no trigger" if limit else "no limit"})
    return rows


def main(argv):
    flags = {a for a in argv if a.startswith("--")}
    args = [a for a in argv if not a.startswith("--")]
    root = pathlib.Path(args[0] if args else ".").resolve()
    rows = ledger(root)
    if "--json" in flags:
        print(json.dumps(rows, indent=2))
    elif not rows:
        print("No `# shortcut:` comments found.")
    else:
        print("| File | Limit | Trigger to revisit | Flag |\n| --- | --- | --- | --- |")
        for r in rows:
            print(f"| {r['file']}:{r['line']} | {r['limit']} | {r['trigger'] or '-'} | {r['flag'] or '-'} |")
        bad = sum(1 for r in rows if r["flag"])
        print(f"\n{len(rows)} shortcut(s); {bad} flagged.")
    return 1 if "--check" in flags and any(r["flag"] for r in rows) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
