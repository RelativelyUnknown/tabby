#!/usr/bin/env python3
"""detect.py: print the facts a Python task needs from the repo, in about ten lines. Reads files only; runs nothing.

    python3 detect.py [PROJECT_DIR]

Runner, build backend, Python target, tests, formatter and linter, type checker, the project's check command, CI, docs tool,
native extension, house rules (ruff rule families, type-checker strictness, pytest strictness, src/ layout, python floor), existing helper modules, and whether AGENTS.md has a `## Tabby` or `## Python defaults` section. A line says `none found` rather than
guessing. Stdlib only; Python 3.11 or later for tomllib (older: the pyproject lines are skipped).
"""
import pathlib, re, sys

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()


def has(*names):
    return [n for n in names if (root / n).exists()]


def text(name):
    try:
        return (root / name).read_text(errors="ignore")
    except OSError:
        return ""


try:
    import tomllib
    py = tomllib.loads(text("pyproject.toml")) if has("pyproject.toml") else {}
except Exception:
    py = {}
tool = py.get("tool", {})
proj = py.get("project", {})
cfg_text = "\n".join(text(n) for n in ("pyproject.toml", "setup.cfg", "tox.ini", ".pre-commit-config.yaml", "Makefile", "justfile"))
ci_text = "\n".join(p.read_text(errors="ignore") for p in list((root / ".github/workflows").glob("*.y*ml")) + [root / ".gitlab-ci.yml"] if p.exists())
all_text = cfg_text + "\n" + ci_text


def lines():
    runner = []
    for f, n in (("uv.lock", "uv"), ("poetry.lock", "poetry"), ("pdm.lock", "pdm"), ("Pipfile", "pipenv"), ("pixi.toml", "pixi"), ("environment.yml", "conda")):
        if has(f):
            runner.append(n)
    if "poetry" in tool and "poetry" not in runner:
        runner.append("poetry")
    if "hatch" in tool and (tool["hatch"] or {}).get("envs"):
        runner.append("hatch")
    if not runner and (list(root.glob("requirements*.txt")) or has("setup.py")):
        runner.append("pip")
    note = "  (two runners: ask which is current)" if len(runner) > 1 else ""
    yield "runner: " + (", ".join(runner) or "none found") + note
    backend = (py.get("build-system") or {}).get("build-backend", "")
    yield "build backend: " + (backend or ("setup.py" if has("setup.py") else "none found"))
    pyv = proj.get("requires-python") or text(".python-version").strip() or "none found"
    yield f"python: {pyv}"
    if "[tool.pytest" in cfg_text or has("pytest.ini", "conftest.py") or list(root.glob("tests/conftest.py")):
        tests = "pytest"
    elif re.search(r"unittest\.TestCase", "".join(p.read_text(errors="ignore") for p in list(root.glob("tests/**/*.py"))[:30])):
        tests = "unittest"
    else:
        tests = "pytest" if list(root.glob("tests/test_*.py")) else "none found"
    extra = has("tox.ini", "noxfile.py")
    yield "tests: " + tests + (f" via {', '.join(extra)}" if extra else "")
    fmt = [n for n, k in (("ruff format", "[tool.ruff"), ("black", "black"), ("isort", "isort"), ("yapf", "yapf")) if k in cfg_text or (k == "[tool.ruff" and has("ruff.toml", ".ruff.toml"))]
    lint = [n for n, k in (("ruff", "[tool.ruff"), ("flake8", "flake8"), ("pylint", "pylint")) if k in cfg_text or (k == "[tool.ruff" and has("ruff.toml", ".ruff.toml"))]
    yield "format/lint: " + (", ".join(dict.fromkeys(fmt + lint)) or "none found")
    types = [n for n, k in (("mypy", "mypy"), ("pyright", "pyright"), ("pyrefly", "pyrefly"), ("ty", "[tool.ty")) if k in cfg_text or (n == "pyright" and has("pyrightconfig.json"))]
    yield "types: " + (", ".join(types) or "none found")
    check = []
    for mk in ("Makefile", "justfile"):
        for m in re.finditer(r"^(check|test|ci|lint|verify)\s*:", text(mk), re.M):
            check.append(f"{'make' if mk == 'Makefile' else 'just'} {m.group(1)}")
    yield "check command: " + (", ".join(check) or "none found (read the CI steps)")
    ci = [str(p.relative_to(root)) for p in list((root / ".github/workflows").glob("*.y*ml"))] + has(".gitlab-ci.yml")
    yield "ci: " + (", ".join(ci) or "none found")
    docs = has("mkdocs.yml") + (["sphinx (docs/conf.py)"] if has("docs/conf.py") else [])
    native = [n for n in ("Cargo.toml", "CMakeLists.txt", "meson.build", "build.zig") if (root / n).exists()] + (["ext_modules"] if "ext_modules" in all_text else []) + [str(p.name) for p in list(root.glob("**/*.pyx"))[:1]]
    yield "docs: " + (", ".join(docs) or "none found") + "; native: " + (", ".join(native) or "none")
    skip_dirs = {".git", ".venv", "venv", "node_modules", "build", "dist", "__pycache__", ".tox", "site-packages"}
    subs = sorted(str(q.parent.relative_to(root)) for pat in ("*/pyproject.toml", "*/*/pyproject.toml", "*/*/*/pyproject.toml") for q in root.glob(pat)
                  if not (skip_dirs & set(q.relative_to(root).parts)))
    if len(subs) > 1 or (subs and has("pyproject.toml")):
        yield f"monorepo: {len(subs)} nested Python project(s): {', '.join(subs[:8])}{' ...' if len(subs) > 8 else ''}; the facts above are for this folder, run detect.py on the one you change and use that project's tools"
    ruff = tool.get("ruff", {}) or {}
    lintcfg = ruff.get("lint", ruff) or {}
    sel = lintcfg.get("select") or []
    rules = []
    if sel:
        rules.append("ruff select " + ",".join(sel[:14]) + ("..." if len(sel) > 14 else ""))
    if lintcfg.get("ignore"):
        rules.append(f"{len(lintcfg['ignore'])} ruff ignores")
    mypy = tool.get("mypy", {}) or {}
    if mypy.get("strict"):
        rules.append("mypy strict")
    elif mypy:
        rules.append("mypy configured (not strict)")
    pyr = tool.get("pyright", {}) or {}
    if pyr.get("typeCheckingMode"):
        rules.append(f"pyright {pyr['typeCheckingMode']}")
    pt = (tool.get("pytest", {}) or {}).get("ini_options", {}) or {}
    if pt.get("xfail_strict"):
        rules.append("pytest xfail_strict")
    if "--strict" in str(pt.get("addopts", "")):
        rules.append("pytest " + " ".join(a for a in str(pt["addopts"]).split() if a.startswith("--strict")))
    if (root / "src").is_dir():
        rules.append("src/ layout")
    floor = [f"no syntax newer than python {proj['requires-python']}"] if proj.get("requires-python") else []
    if rules or floor:
        yield "house rules: " + "; ".join(rules + floor)
    skip = {".git", ".venv", "venv", "node_modules", "build", "dist", "__pycache__", ".tox", ".mypy_cache", ".ruff_cache"}
    names = {"utils.py", "_utils.py", "helpers.py", "common.py", "_compat.py", "compat.py", "errors.py", "exceptions.py", "conftest.py"}
    found = []
    for p in sorted(root.glob("*/*.py")) + sorted(root.glob("*/*/*.py")) + sorted(root.glob("*/*/*/*.py")):
        rel = p.relative_to(root)
        if p.name in names and not (skip & set(rel.parts)):
            found.append(str(rel))
    if found:
        yield "existing helpers (reuse before writing new): " + ", ".join(found[:12]) + (" ..." if len(found) > 12 else "")
    mem = text("AGENTS.md") + text("CLAUDE.md")
    nested = sorted(str(q.parent.relative_to(root)) for pat in ("*/AGENTS.md", "*/*/AGENTS.md", "*/*/*/AGENTS.md") for q in root.glob(pat)
                    if not (skip_dirs & set(q.relative_to(root).parts)))
    if nested:
        yield f"nested AGENTS.md: {', '.join(nested[:8])}{' ...' if len(nested) > 8 else ''} (the one nearest the file you edit wins over the root's)"
    yield "project memory: " + ("## Tabby section" if "## Tabby" in mem else "no ## Tabby section") + (", ## Python defaults" if "## Python defaults" in mem else "") + (f"; {', '.join(has('AGENTS.md', 'CLAUDE.md'))}" if has("AGENTS.md", "CLAUDE.md") else "; no AGENTS.md or CLAUDE.md")


NOTHING = re.compile(r"^[^:]+: none( found)?( \(read the CI steps\))?(; native: none)?$")
print("Detected from the repo (files only; nothing was run):")
try:
    for ln in lines():
        if not NOTHING.match(ln):  # a line that found nothing adds tokens, not information
            print("- " + ln)
except Exception as e:  # never fail the skill that runs this
    print(f"- (detect.py stopped: {type(e).__name__}; read the repo instead)")
