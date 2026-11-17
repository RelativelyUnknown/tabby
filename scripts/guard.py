#!/usr/bin/env python3
"""guard.py: find the shortcuts a coding agent takes to get green, in a unified diff. Stdlib only.

    git diff HEAD -U0 | python3 guard.py        prints one line per violation, exits 1 if there are any

Flags only lines the diff adds (or, for tests, removes):
- a suppression (`# type: ignore`, `# noqa`) without a reason after ` -- `
- `Any`, `cast(` in non-test code
- `pytest.mark.skip` / `xfail` without `reason=`
- a bare `except:` or `except Exception: pass`
- in test files: fewer assertions than before, or a deleted test function
"""
import re
import sys

SUPPRESS = re.compile(r"#\s*(type:\s*ignore|noqa)\b(?!.*--\s*\S)")
ANY = re.compile(r"\bAny\b")
CAST = re.compile(r"\bcast\(")
MARK = re.compile(r"pytest\.mark\.(skip|xfail|skipif)\b")
BARE = re.compile(r"^\s*except\s*(\(?\s*BaseException\s*\)?(\s+as\s+\w+)?)?\s*:\s*(pass\s*)?$|^\s*except\s*\(?\s*Exception\s*\)?(\s+as\s+\w+)?\s*:\s*pass\s*$")
ASSERT = re.compile(r"^\s*(assert\b|self\.assert\w+\(|with\s+pytest\.raises\b)")
TESTDEF = re.compile(r"^\s*(?:async\s+)?def\s+(test\w*)\(")


def is_test(path):
    name = path.rsplit("/", 1)[-1]
    return name.startswith("test_") or name.endswith("_test.py") or name == "conftest.py" or "/tests/" in "/" + path


def parse(diff):
    """Yield (path, added_lines, removed_lines) per .py file in a unified diff."""
    path, add, rem = None, [], []
    for ln in diff.splitlines():
        if ln.startswith("diff --git"):
            if path and path.endswith(".py"):
                yield path, add, rem
            path, add, rem = None, [], []
        elif ln.startswith("+++ "):
            path = ln[4:].removeprefix("b/") if ln[4:] != "/dev/null" else None
        elif ln.startswith("--- "):
            if path is None:
                path = ln[4:].removeprefix("a/") if ln[4:] != "/dev/null" else None
        elif ln.startswith("+") and not ln.startswith("+++"):
            add.append(ln[1:])
        elif ln.startswith("-") and not ln.startswith("---"):
            rem.append(ln[1:])
    if path and path.endswith(".py"):
        yield path, add, rem


def check_diff(diff):
    out = []
    for path, add, rem in parse(diff):
        test = is_test(path)
        for i, ln in enumerate(add):
            code = ln.split("#", 1)[0]
            if SUPPRESS.search(ln):
                out.append(f"{path}: suppression added ({ln.strip()[:60]}); fix the cause, or explain after ` -- `")
            if not test and ANY.search(code):
                out.append(f"{path}: `Any` added; use a concrete type, Protocol or TypeVar")
            if not test and CAST.search(code):
                out.append(f"{path}: `cast(` added; narrow with a check or a validator instead")
            if MARK.search(code) and "reason" not in ln:
                out.append(f"{path}: skip/xfail without reason=; do not skip a test to get green")
            if BARE.match(ln) or (re.match(r"^\s*except\b.*:\s*$", ln) and i + 1 < len(add) and add[i + 1].strip() == "pass" and re.search(r"\b(Base)?Exception\b|except\s*:", ln)):
                out.append(f"{path}: bare or swallowed exception; catch the narrow error and handle it")
        if test:
            gone = {m.group(1) for ln in rem if (m := TESTDEF.match(ln))} - {m.group(1) for ln in add if (m := TESTDEF.match(ln))}
            for name in sorted(gone):
                out.append(f"{path}: test `{name}` deleted; leave existing tests, report one that contradicts the spec")
            fewer = sum(bool(ASSERT.match(ln)) for ln in rem) - sum(bool(ASSERT.match(ln)) for ln in add)
            if fewer > 0 and not gone:
                out.append(f"{path}: {fewer} assertion(s) removed from an existing test; do not weaken tests to get green")
    return list(dict.fromkeys(out))


if __name__ == "__main__":
    found = check_diff(sys.stdin.read())
    print("\n".join(found))
    sys.exit(1 if found else 0)
