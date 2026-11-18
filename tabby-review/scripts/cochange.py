#!/usr/bin/env python3
"""cochange.py: find files that change together in git history but do not import each other.

    python3 cochange.py [PROJECT_DIR] [--since 12.months] [--min-commits 5] [--min-ratio 0.6] [--max-files 30] [--all] [--json]

A pair that changes together often and has no import link between its two files shares something no import shows: a format, a magic
string, a column list, a duplicated rule. That is hidden coupling (connascence of meaning or algorithm). The ratio is the share of the
less-changed file's commits that also touched the other. Commits touching more than --max-files files (renames, formatting, releases)
are skipped. With --all, pairs that do import each other are listed too. Reads git history and the Python files; stdlib only.
"""
import argparse
import ast
import itertools
import json
import os
import pathlib
import subprocess
import sys
from collections import Counter


def git(root, *args):
    r = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"cochange: git {' '.join(args)} failed: {r.stderr.strip()}")
    return r.stdout


def commits(root, since, max_files, tracked):
    out = git(root, "log", f"--since={since}", "--name-only", "--no-renames", "--pretty=format:@@")
    for chunk in out.split("@@"):
        names = [n for n in chunk.split("\n") if n in tracked]
        if 2 <= len(names) <= max_files:
            yield names


def module_name(path):
    parts = list(pathlib.PurePosixPath(path).with_suffix("").parts)
    if parts and parts[0] == "src":
        parts = parts[1:]
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def imports(root, files):
    """file -> set of project files it imports (best effort, from `import` and `from ... import` statements)."""
    mods = {module_name(f): f for f in files if f.endswith(".py")}
    links = {f: set() for f in files}
    for f in files:
        if not f.endswith(".py"):
            continue
        try:
            tree = ast.parse((pathlib.Path(root) / f).read_text(errors="replace"))
        except (SyntaxError, OSError):
            continue
        here = module_name(f).split(".")
        is_pkg = f.endswith("__init__.py")
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                base = node.module or ""
                if node.level:
                    keep = len(here) - node.level + (1 if is_pkg else 0)
                    base = ".".join(here[:max(keep, 0)] + ([node.module] if node.module else []))
                names = [base] + [f"{base}.{a.name}" for a in node.names]
            for n in names:
                if n in mods and mods[n] != f:
                    links[f].add(mods[n])
    return links


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project", nargs="?", default=".")
    ap.add_argument("--since", default="12.months")
    ap.add_argument("--min-commits", type=int, default=5)
    ap.add_argument("--min-ratio", type=float, default=0.6)
    ap.add_argument("--max-files", type=int, default=30)
    ap.add_argument("--all", action="store_true", help="also list pairs that import each other")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    tracked = set(git(a.project, "ls-files").splitlines())
    per_file, per_pair = Counter(), Counter()
    for names in commits(a.project, a.since, a.max_files, tracked):
        per_file.update(names)
        per_pair.update(itertools.combinations(sorted(names), 2))
    links = imports(a.project, tracked)

    rows = []
    for (x, y), n in per_pair.items():
        ratio = n / min(per_file[x], per_file[y])
        if n < a.min_commits or ratio < a.min_ratio:
            continue
        linked = y in links.get(x, ()) or x in links.get(y, ())
        if linked and not a.all:
            continue
        rows.append({"a": x, "b": y, "together": n, "ratio": round(ratio, 2), "import_link": linked})
    rows.sort(key=lambda r: (-r["together"], -r["ratio"]))

    if a.json:
        print(json.dumps(rows, indent=2))
        return
    if not rows:
        print(f"No file pairs changed together {a.min_commits}+ times with ratio >= {a.min_ratio} and no import link since {a.since}.")
        return
    print(f"{'together':>8}  {'ratio':>5}  {'import':<6}  pair")
    for r in rows:
        print(f"{r['together']:>8}  {r['ratio']:>5.2f}  {'yes' if r['import_link'] else 'no':<6}  {r['a']}  <->  {r['b']}")
    print("\nFor each pair with no import link, open both files and name what they share (a format, a key, a rule written twice).")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:  # output piped to `head` and closed early
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        sys.exit(0)
