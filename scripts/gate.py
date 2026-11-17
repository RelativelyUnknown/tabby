#!/usr/bin/env python3
"""gate.py: Claude Code hook dispatcher for Tabby. Stdlib only.

    gate.py session-start | post-edit | stop      (hook JSON arrives on stdin)

session-start  prints the core rules, detect.py facts and the ## Tabby project memory as context; records current violations
               and already-changed files as a baseline
post-edit      runs the project's own ruff on the edited .py file; exit 2 with the problems if it complains
stop           exit 2 if the diff added new shortcuts (guard.py), the project's make/just check fails, or (once each) this
               session's change is large (over 80 lines or 3 files) and the tabby-reviewer subagent has not read it, or it
               changed the project's shape (build files, new modules, native code) and left the ## Tabby section untouched

Modes: full (default), lite (core rules, project memory, the diff check and the AGENTS.md update request; no ruff hook, no check command,
no reviewer request) and off. Set TABBY_MODE,
or {"mode": "lite"} in .claude/tabby.json. Off: TABBY_GATE=off, or {"gate": false} in .claude/tabby.json; {"review": false} turns off only the reviewer request
(`review_lines` and `review_files` set its thresholds). Never loops: a stop already
continued by this hook (stop_hook_active) passes. Any internal error exits 0, so a bug here never blocks work.
"""
import hashlib
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

SHAPE_FILES = ("pyproject.toml", "Cargo.toml", "setup.py", "setup.cfg", "Makefile", "justfile", "noxfile.py", "tox.ini")
SHAPE_SUFFIXES = (".rs", ".c", ".cpp", ".h", ".zig", ".pyx")


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


def dirty_files(proj):
    """{path: content hash} for every modified or untracked file, so a stop can tell what this session changed."""
    out = {}
    for ln in run(["git", "status", "--porcelain", "-uall", "--no-renames"], proj).stdout.splitlines()[:2000]:
        path = ln[3:].strip().strip('"')
        try:
            out[path] = hashlib.sha1((proj / path).read_bytes()).hexdigest()
        except OSError:
            out[path] = "deleted"
    return out


def session_changes(proj, state):
    """Paths changed since session start; with no recorded baseline, every dirty file counts."""
    before = state.get("dirty", {})
    return {p for p, h in dirty_files(proj).items() if before.get(p) != h}


def diff_size(proj, changed):
    """(changed lines, files) over the .py files in `changed`."""
    numstat = {}
    for ln in run(["git", "diff", "HEAD", "--numstat", "--", "*.py"], proj).stdout.splitlines():
        a, r, path = (ln.split("\t") + ["", "", ""])[:3]
        if a.isdigit() and r.isdigit():
            numstat[path] = int(a) + int(r)
    lines = files = 0
    for f in (p for p in changed if p.endswith(".py")):
        if f in numstat:
            lines += numstat[f]
        else:
            try:
                lines += len((proj / f).read_text(errors="ignore").splitlines())
            except OSError:
                continue
        files += 1
    return lines, files


def tabby_memory(proj):
    """The ## Tabby and ## Python defaults sections of AGENTS.md, or "" when there is no ## Tabby section."""
    try:
        text = (proj / "AGENTS.md").read_text(errors="ignore")
    except OSError:
        return ""
    keep = re.findall(r"^## (?:Tabby|Python defaults)\b.*?(?=^## |\Z)", text, re.M | re.S)
    return "\n\n".join(k.strip() for k in keep) if any(k.startswith("## Tabby") for k in keep) else ""


def shape_changes(proj, changed):
    """Changed files that alter what the ## Tabby section describes: build and check files, new modules, native code."""
    untracked = set(run(["git", "ls-files", "--others", "--exclude-standard"], proj).stdout.split())
    return sorted(
        p for p in changed
        if pathlib.PurePath(p).name in SHAPE_FILES
        or p.endswith(SHAPE_SUFFIXES)
        or (p in untracked and p.endswith(".py") and not re.search(r"(^|/)(tests?/|test_[^/]*\.py$|[^/]*_test\.py$|conftest\.py$)", p))
    )


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
    v = os.environ.get("TABBY_VOICE", "").lower() or str(settings(proj).get("voice", "")).lower() or agents_voice(proj)
    return VOICES.get(v, "")


def agents_voice(proj):
    """A `voice: terse|explain` line in AGENTS.md (the `## Tabby` section); Claude Code protects .claude/, so the skill writes it here."""
    try:
        m = re.search(r"^voice:\s*(\w+)", (pathlib.Path(proj) / "AGENTS.md").read_text(), re.M)
    except OSError:
        return ""
    return m.group(1).lower() if m else ""


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
    memory = tabby_memory(proj)
    if memory:
        print("Project memory from AGENTS.md, saved by the interview. It is already set up: never suggest running the interview. "
              "Decide with it: before designing, name the lines that bear on the task (goals, growth, constraints, out-of-scope, "
              "ask-first, never) and build so the next growth item is cheap; a choice that a line rules out is a bug, not a style "
              "question. Do not re-ask what it records as decided. When the work changes a fact in it, update the section in the "
              "same task.\n\n" + memory)
    try:
        state_file(data).write_text(json.dumps({"baseline": current_violations(proj), "checked": False, "dirty": dirty_files(proj)}))
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


SCRATCH = re.compile(r"(^|/)(\.?scratch[^/]*|[^/]*_scratch[^/]*|[^/]*_tmp\.[a-z]+|tmp_[^/]*|probe[^/]*)(/|$)", re.I)


def scratch_files(proj):
    """Untracked files and folders whose names say they are throwaway (scratch, probe, tmp)."""
    out = run(["git", "ls-files", "--others", "--exclude-standard"], proj).stdout.split("\n")
    return sorted({f for f in out if f and SCRATCH.search(f)})


def memory_ask(proj, state, session):
    """Once per session: the session changed the project's shape but left the ## Tabby section as it was."""
    if state.get("memory_asked") or "AGENTS.md" in session or not tabby_memory(proj):
        return ""
    shape = shape_changes(proj, session)
    if not shape:
        return ""
    state["memory_asked"] = True
    return ("This change touched " + ", ".join(shape[:6]) + " but not AGENTS.md. Its ## Tabby section is what the next session decides from. "
            "Compare it with what you built: a growth item that is now real moves to goals (with an ADR if it is hard to reverse); "
            "update map, commands, constraints, kind and open where they changed, record decisions the user made in this conversation "
            "(an approval, a changed requirement) in decided:, and set reviewed:. Edit only the lines that changed. If nothing in it changed, "
            "say \"AGENTS.md still matches\" in your final message.")


def ask(sf, state, asks):
    """Send the pending requests in one message (exit 2), or pass."""
    asks = [a for a in asks if a]
    if not asks:
        return 0
    sf.write_text(json.dumps(state))
    print("Tabby gate: " + "\n\n".join(asks) + "\n\nThen finish with your full summary of the change as the final message "
          "(what you changed, what you ran and the result, what you declined and why), not only a verdict.", file=sys.stderr)
    return 2


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
    if not state.get("scratch_asked"):
        left = scratch_files(proj)
        if left:
            state["scratch_asked"] = True
            sf.write_text(json.dumps(state))
            print("Tabby gate: throwaway files are still in the project: " + ", ".join(left[:6]) + ". Delete them (or move them out of the project), then finish with your full summary of the change as the final message. If you cannot delete them, say so in that message.", file=sys.stderr)
            return 2
    session = session_changes(proj, state)
    if mode(proj) == "lite":
        return ask(sf, state, [memory_ask(proj, state, session)])
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
    asks = []
    if cfg.get("review") is not False and not state.get("review_asked"):
        lines, files = diff_size(proj, session)
        if lines > int(cfg.get("review_lines", REVIEW_LINES)) or files > int(cfg.get("review_files", REVIEW_FILES)):
            state["review_asked"] = True
            asks.append(f"This is a large change ({lines} changed lines in {files} Python files). Run the `tabby-reviewer` subagent once, "
                        "giving it the task in the user's words, the command `git diff HEAD` and the command `git ls-files --others --exclude-standard` for new files (it reads them in full). Do not stage files to make them show up. Fix what it confirms. "
                        "Turn this off with {\"review\": false} in .claude/tabby.json.")
    asks.append(memory_ask(proj, state, session))
    return ask(sf, state, asks)


def main():
    handlers = {"session-start": session_start, "post-edit": post_edit, "stop": stop}
    try:
        return handlers[sys.argv[1]](read_input())
    except Exception:
        return 0


if __name__ == "__main__":
    sys.exit(main())
