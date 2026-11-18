#!/usr/bin/env python3
"""mutation_probe.py: break one source file on purpose, one change at a time, and see which tests go red.

    python3 mutation_probe.py SOURCE.py [--cmd "python -m pytest -q"] [--max 60] [--timeout 120] [--json]

Runs the test command once as a baseline (it must pass), then makes one small change to SOURCE (flip a comparison, swap + and -, swap
and/or, flip a boolean, move a number by one), runs the tests again and restores the file. It reports:

  survivors:  changes no test noticed (a missing or weak assertion at that line)
  never red:  tests that passed under every change (they may check nothing; judge each one, small files give weak evidence)

A probe, not a replacement for mutmut or cosmic-ray: it needs pytest (it adds --junitxml), mutates one file (run it from the project root), and unparses the file for
each change, so run it on a clean checkout and let it restore the original. A timeout counts as caught. Stdlib only.
"""
import argparse
import ast
import copy
import json
import os
import pathlib
import random
import shlex
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

CMP = {ast.Eq: ast.NotEq, ast.NotEq: ast.Eq, ast.Lt: ast.GtE, ast.GtE: ast.Lt, ast.Gt: ast.LtE, ast.LtE: ast.Gt}
ARITH = {ast.Add: ast.Sub, ast.Sub: ast.Add, ast.Mult: ast.FloorDiv, ast.FloorDiv: ast.Mult}
BOOL = {ast.And: ast.Or, ast.Or: ast.And}


def sites(tree):
    """Every place a change can be made: (index in ast.walk order, line, description, apply(node))."""
    out = []
    for i, node in enumerate(ast.walk(tree)):
        if isinstance(node, ast.Compare):
            for j, op in enumerate(node.ops):
                if type(op) in CMP:
                    out.append((i, node.lineno, f"{type(op).__name__} -> {CMP[type(op)].__name__}", ("cmp", j)))
        elif isinstance(node, ast.BinOp) and type(node.op) in ARITH:
            out.append((i, node.lineno, f"{type(node.op).__name__} -> {ARITH[type(node.op)].__name__}", ("arith", 0)))
        elif isinstance(node, ast.BoolOp):
            out.append((i, node.lineno, f"{type(node.op).__name__} -> {BOOL[type(node.op)].__name__}", ("bool", 0)))
        elif isinstance(node, ast.Constant):
            if isinstance(node.value, bool):
                out.append((i, node.lineno, f"{node.value} -> {not node.value}", ("flip", 0)))
            elif isinstance(node.value, int):
                out.append((i, node.lineno, f"{node.value} -> {node.value + 1}", ("num", 0)))
    return out


def mutate(tree, index, how):
    t = copy.deepcopy(tree)
    node = list(ast.walk(t))[index]
    kind, j = how
    if kind == "cmp":
        node.ops[j] = CMP[type(node.ops[j])]()
    elif kind == "arith":
        node.op = ARITH[type(node.op)]()
    elif kind == "bool":
        node.op = BOOL[type(node.op)]()
    elif kind == "flip":
        node.value = not node.value
    elif kind == "num":
        node.value += 1
    return ast.unparse(ast.fix_missing_locations(t))


def run(cmd, timeout, cwd):
    fd, xml = tempfile.mkstemp(suffix=".xml")
    os.close(fd)
    try:
        r = subprocess.run([*cmd, f"--junitxml={xml}", "-p", "no:cacheprovider"], cwd=cwd, capture_output=True, text=True, timeout=timeout,
                           env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    except subprocess.TimeoutExpired:
        return "timeout", set(), set()
    try:
        root = ET.parse(xml).getroot()
    except ET.ParseError:
        return ("pass" if r.returncode == 0 else "fail"), set(), set()
    finally:
        os.unlink(xml)
    seen, failed = set(), set()
    for tc in root.iter("testcase"):
        name = f"{tc.get('classname', '')}::{tc.get('name', '')}"
        seen.add(name)
        if tc.find("failure") is not None or tc.find("error") is not None:
            failed.add(name)
    return ("pass" if r.returncode == 0 else "fail"), seen, failed


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source")
    ap.add_argument("--cmd", default="python -m pytest -q")
    ap.add_argument("--max", type=int, default=60, help="most changes to try (sampled evenly, fixed seed)")
    ap.add_argument("--timeout", type=int, default=120, help="seconds per test run")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    path = pathlib.Path(a.source).resolve()
    original = path.read_bytes()
    tree = ast.parse(original.decode())
    cmd = shlex.split(a.cmd)
    cwd = None  # run from where the command was started, so test paths resolve

    status, all_tests, _ = run(cmd, a.timeout, cwd)
    if status != "pass":
        sys.exit(f"mutation_probe: the baseline run is not green ({status}); fix the tests first.")

    todo = sites(tree)
    if len(todo) > a.max:
        todo = sorted(random.Random(0).sample(todo, a.max))
    survivors, caught, red = [], 0, set()
    try:
        for i, line, what, how in todo:
            path.write_text(mutate(tree, i, how))
            status, _, failed = run(cmd, a.timeout, cwd)
            if status == "pass":
                survivors.append({"line": line, "change": what})
            else:
                caught += 1
                red |= failed
    finally:
        path.write_bytes(original)

    never_red = sorted(all_tests - red)
    result = {"source": a.source, "tried": len(todo), "caught": caught, "survivors": survivors, "never_red": never_red}
    if a.json:
        print(json.dumps(result, indent=2))
        return
    print(f"{a.source}: {len(todo)} changes tried, {caught} caught, {len(survivors)} survived.")
    for s in survivors:
        print(f"  survived  line {s['line']}: {s['change']}")
    if never_red:
        print(f"{len(never_red)} of {len(all_tests)} tests never went red:")
        for t in never_red:
            print(f"  {t}")
    print("A survivor is a missing or weak assertion at that line, or an equivalent change (check which). Report it; do not weaken a test.")


if __name__ == "__main__":
    main()
