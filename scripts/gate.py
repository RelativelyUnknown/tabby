#!/usr/bin/env python3
"""gate.py: Claude Code hook dispatcher for Tabby. Stdlib only.

    gate.py session-start | post-edit | stop      (hook JSON arrives on stdin)

session-start  prints the core rules and detect.py facts as context; records current violations as a baseline
post-edit      runs the project's own ruff on the edited .py file; exit 2 with the problems if it complains
stop           exit 2 if the diff added new shortcuts (guard.py), the project's make/just check fails, or the diff is large
               (over 80 lines or 3 files; once) and the tabby-reviewer subagent has not been asked to read it

Modes: full (default), lite (core rules and the diff check; no ruff hook, no check command, no reviewer request) and off. Set TABBY_MODE,
or {"mode": "lite"} in .claude/tabby.json. Off: TABBY_GATE=off, or {"gate": false} in .claude/tabby.json; {"review": false} turns off only the reviewer request
(`review_lines` and `review_files` set its thresholds). Never loops: a stop already
continued by this hook (stop_hook_active) passes. Any internal error exits 0, so a bug here never blocks work.
"""
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

REVIEW_LINES, REVIEW_FILES = 80, 3
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import guard  # noqa: E402


def read_input():
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def project(data):
    return pathlib.Path(data.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or ".")


def mode(proj):
    """full (default), lite (core rules and the diff check only) or off. TABBY_MODE overrides .claude/tabby.json; gate=false and TABBY_GATE=off mean off."""
    if os.environ.get("TABBY_GATE", "").lower() == "off":
        return "off"
    env = os.environ.get("TABBY_MODE", "").lower()
    cfg = {}
    try:
        cfg = json.loads((proj / ".claude/tabby.json").read_text())
    except Exception:
        pass
    if cfg.get("gate") is False:
        return "off"
    m = env or str(cfg.get("mode", "full")).lower()
    return m if m in ("full", "lite", "off") else "full"


def disabled(proj):
    return mode(proj) == "off"


def settings(proj):
    try:
        return json.loads((proj / ".claude/tabby.json").read_text())
    except Exception:
        return {}


def diff_size(proj):
    """(changed lines, files) over tracked and untracked .py files."""
    lines = files = 0
    for ln in run(["git", "diff", "HEAD", "--numstat", "--", "*.py"], proj).stdout.splitlines():
        a, r, _ = (ln.split("\t") + ["", "", ""])[:3]
        if a.isdigit() and r.isdigit():
            lines += int(a) + int(r)
            files += 1
    for f in run(["git", "ls-files", "--others", "--exclude-standard", "--", "*.py"], proj).stdout.split():
        try:
            lines += len((proj / f).read_text(errors="ignore").splitlines())
            files += 1
        except OSError:
            pass
    return lines, files


def run(cmd, cwd, timeout=120):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)


def current_violations(proj):
    r = run(["git", "diff", "HEAD", "-U0", "--no-color"], proj)
    found = guard.check_diff(r.stdout) if r.returncode == 0 else []
    untracked = run(["git", "ls-files", "--others", "--exclude-standard", "--", "*.py"], proj).stdout.split()
    for f in untracked[:50]:
        try:
            body = (proj / f).read_text(errors="ignore")
        except OSError:
            continue
        fake = f"diff --git a/{f} b/{f}\n--- /dev/null\n+++ b/{f}\n" + "".join("+" + ln + "\n" for ln in body.splitlines())
        found += guard.check_diff(fake)
    return list(dict.fromkeys(found))


def state_file(data):
    return pathlib.Path(tempfile.gettempdir()) / f"tabby-gate-{data.get('session_id', 'x')}.json"


def ruff_configured(proj):
    if (proj / "ruff.toml").exists() or (proj / ".ruff.toml").exists():
        return True
    try:
        return "[tool.ruff" in (proj / "pyproject.toml").read_text(errors="ignore")
    except OSError:
        return False


VOICES = {
    "terse": "Reply voice: terse and technical. Result, evidence, what is left; no explanations of how things work.",
    "explain": "Reply voice: explanatory. Result first, then a short how-it-works in plain words; name each new idea once.",
}


def voice_line(proj):
    """The reply-voice line for session start: TABBY_VOICE or {"voice": ...} in .claude/tabby.json; auto (the default) adds nothing."""
    v = os.environ.get("TABBY_VOICE", "").lower() or str(settings(proj).get("voice", "auto")).lower()
    return VOICES.get(v, "")


def session_start(data):
    proj = project(data)
    if disabled(proj):
        return 0
    print((ROOT / "core/TABBY-CORE.md").read_text())
    r = run([sys.executable, str(ROOT / "tabby/scripts/detect.py"), str(proj)], proj, 20)
    print(r.stdout)
    voice = voice_line(proj)
    if voice:
        print(voice)
    if not disabled(proj):
        try:
            state_file(data).write_text(json.dumps({"baseline": current_violations(proj), "checked": False}))
        except Exception:
            pass
    return 0


def post_edit(data):
    proj = project(data)
    path = (data.get("tool_input") or {}).get("file_path", "")
    if mode(proj) != "full" or not path.endswith(".py") or not ruff_configured(proj):
        return 0
    ruff = shutil.which("ruff")
    if not ruff or not pathlib.Path(path).exists():
        return 0
    run([ruff, "format", path], proj)
    r = run([ruff, "check", "--fix", "--output-format=concise", path], proj)
    if r.returncode != 0:
        print(f"ruff reports problems in {path}; fix them without adding noqa:\n{r.stdout.strip()[:1500]}", file=sys.stderr)
        return 2
    return 0


def check_command(proj):
    for mk, tool in (("Makefile", "make"), ("justfile", "just")):
        try:
            text = (proj / mk).read_text(errors="ignore")
        except OSError:
            continue
        m = re.search(r"^(check|test|ci|verify)\s*:", text, re.M)
        if m and shutil.which(tool):
            return [tool, m.group(1)]
    return None


def stop(data):
    proj = project(data)
    if disabled(proj) or data.get("stop_hook_active"):
        return 0
    sf = state_file(data)
    try:
        state = json.loads(sf.read_text())
    except Exception:
        state = {"baseline": [], "checked": False}
    new = [v for v in current_violations(proj) if v not in state["baseline"]]
    if new:
        print("Tabby gate: the diff added shortcuts. Fix each, then finish with your full summary of the change as the final message (what changed, what you ran and the result), not only the fix-up.\n- " + "\n- ".join(new[:10]), file=sys.stderr)
        return 2
    if mode(proj) == "lite":
        return 0
    cmd = check_command(proj)
    changed = run(["git", "status", "--porcelain", "--", "*.py"], proj).stdout.strip()
    if cmd and changed and not state.get("checked"):
        state["checked"] = True
        sf.write_text(json.dumps(state))
        r = run(cmd, proj, 540)
        if r.returncode != 0:
            tail = "\n".join((r.stdout + r.stderr).strip().splitlines()[-25:])
            print(f"Tabby gate: `{' '.join(cmd)}` failed. Fix the cause, do not weaken tests. Then finish with your full summary as the final message:\n{tail}", file=sys.stderr)
            return 2
    cfg = settings(proj)
    if cfg.get("review") is not False and not state.get("review_asked"):
        lines, files = diff_size(proj)
        if lines > int(cfg.get("review_lines", REVIEW_LINES)) or files > int(cfg.get("review_files", REVIEW_FILES)):
            state["review_asked"] = True
            sf.write_text(json.dumps(state))
            print(f"Tabby gate: this is a large change ({lines} changed lines in {files} Python files). Run the `tabby-reviewer` subagent once, "
                  "giving it the task in the user's words, the command `git diff HEAD` and the command `git ls-files --others --exclude-standard` for new files (it reads them in full). Do not stage files to make them show up. Fix what it confirms, then finish with your full summary of the change as the final message (what you changed, what you ran and the result, what you declined and why), not only the reviewer's verdict. "
                  "Turn this off with {\"review\": false} in .claude/tabby.json.", file=sys.stderr)
            return 2
    return 0


def main():
    handlers = {"session-start": session_start, "post-edit": post_edit, "stop": stop}
    try:
        return handlers[sys.argv[1]](read_input())
    except Exception:
        return 0


if __name__ == "__main__":
    sys.exit(main())
