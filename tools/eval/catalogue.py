#!/usr/bin/env python3
"""catalogue.py: write the catalogue of every eval case into TESTING.md.

    python3 tools/eval/catalogue.py            rewrite the block between the catalogue markers in TESTING.md
    python3 tools/eval/catalogue.py --print    print it instead

Reads evals/<case>/case.yaml (expected outcome), prompt.md (tags, the request) and graders/*.md (grader types), and
evals/quality/hidden/<case>/ (hidden tests). Cases are grouped by their tags. Stdlib only. Run from the repository root.
"""
import collections
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EVALS = os.path.join(ROOT, "evals")
START, END = "<!-- catalogue:start -->", "<!-- catalogue:end -->"
GROUPS = [
    ("Headroom cases: known failure modes", ("headroom",), "Built to leave room for a gain: a type error that tempts `# type: ignore`, an existing helper to reuse, a vague request, a Pydantic v1/v2 trap, a small flag that tempts a framework."),
    ("Review and audit", ("review", "bugs", "repo-audit", "supply-chain"), "Reviewing a diff, hunting bugs, auditing a repository, CI workflows or dependencies, including seeded audits with known findings."),
    ("Security", ("security",), "Fixing or avoiding a vulnerability: server-side request forgery, ownership checks, secrets, unsafe input."),
    ("Native extensions", ("native-extension", "rust", "cpp", "zig", "unsafe", "porting"), "Rust, C++ and Zig behind a Python API: the GIL, ownership, return policies, porting a hot path."),
    ("Documentation", ("documentation", "docs", "history", "operations", "troubleshooting", "page-types", "agents"), "READMEs, docstrings, decision records, runbooks, troubleshooting pages, a repository's agent file."),
    ("Diagrams, animation and interfaces", ("diagram", "animation", "design-md", "interface", "design"), "Diagrams from a spec, an animation, a docs site or page that must honour a design file, accessibility."),
    ("Asking, scoping and project memory", ("protocol", "intent", "vague", "spec", "scout"), "Whether it asks a short question when the request is vague, writes a spec for a feature with several readings, saves or respects the `## Tabby` section, and reports what it noticed."),
    ("Guards: what it must not do", ("guard",), "Leaves a contradicting test alone, keeps the project's own tools, does not add a framework or a diff nobody asked for."),
    ("Reuse and dependencies", ("dependencies", "ladder", "ecosystem", "uv", "options"), "Standard library before a dependency, a community standard before hand-rolling, vetting a package, uv, ordering of options."),
    ("Services and runtime", ("async", "workers", "observability", "resilience", "configuration", "settings", "application", "transactions", "retries", "circuit-breaker", "logging", "metrics", "idempotency", "concurrency", "resources"), "Endpoints, settings, async code, retries and timeouts, workers, logging and metrics, transactions."),
    ("Design, scope and workflow", ("architecture", "senior", "footprint", "cleanup", "deprecation", "gates", "workflow", "prototype", "data-engineering", "machine-learning", "scripts"), "Design under real limits, the smallest change, clean-up that stays in scope, deprecating instead of deleting, gates for multi-part requests, data and ML scripts."),
    ("Bugs, types and errors", ("debugging", "typing", "annotations", "errors", "toolstack"), "Finding the cause, typed decorators, error handling, keeping the project's tool stack."),
    ("Everyday development", ("development", "baseline", "ci"), "Ordinary tasks in small fixture repositories."),
]


def read(path):
    try:
        return open(path, errors="ignore").read()
    except OSError:
        return ""


def one_line(s):
    return re.sub(r"\s+", " ", s).strip().replace("|", "\\|")


def cases():
    out = []
    for d in sorted(os.listdir(EVALS)):
        if not os.path.isfile(os.path.join(EVALS, d, "case.yaml")):
            continue
        y = read(os.path.join(EVALS, d, "case.yaml"))
        m = re.search(r"expected_outcome:\s*\|?\s*\n((?:[ \t]+.*\n?)+)", y)
        expected = one_line(m.group(1)) if m else ""
        p = read(os.path.join(EVALS, d, "prompt.md"))
        tags = re.search(r"^tags:\s*\[(.*?)\]", p, re.M)
        tags = [t.strip() for t in tags.group(1).split(",")] if tags else []
        request = one_line(p.split("---", 2)[2]) if p.count("---") >= 2 else ""
        types = collections.Counter()
        for g in glob.glob(os.path.join(EVALS, d, "graders", "*.md")):
            mm = re.search(r"^type:\s*(\w+)", read(g), re.M)
            types[mm.group(1) if mm else "?"] += 1
        hidden = os.path.isdir(os.path.join(EVALS, "quality", "hidden", d))
        out.append(dict(name=d, expected=expected, tags=tags, request=request, types=types, hidden=hidden))
    return out


def group_of(c):
    for name, tags, _ in GROUPS:
        if any(t in c["tags"] for t in tags):
            return name
    return "Everyday development"


def build():
    cs = cases()
    by = collections.defaultdict(list)
    for c in cs:
        by[group_of(c)].append(c)
    kinds = collections.Counter()
    for c in cs:
        kinds.update(c["types"])
    lines = [START, "",
             f"{len(cs)} cases, {sum(kinds.values())} graders ({', '.join(f'{v} {k}' for k, v in kinds.most_common())}). "
             f"{sum(c['hidden'] for c in cs)} cases also have hidden tests that `tools/eval/quality.py` runs after the agent finishes. "
             "Regex graders check the files or the final message; `tool_used` and `tool_order` check what the agent did (for example, ran pytest before editing); `llm` graders are judged by a model against a plain-language rule.", "",
             "| Group | Cases | What it covers |", "| --- | --- | --- |"]
    for name, _, desc in GROUPS:
        if by.get(name):
            lines.append(f"| {name} | {len(by[name])} | {desc} |")
    for name, _, desc in GROUPS:
        if not by.get(name):
            continue
        lines += ["", f"#### {name}", "", desc, "", "| Case | Request | Passes when | Graders |", "| --- | --- | --- | --- |"]
        for c in by[name]:
            g = ", ".join(f"{v} {k}" for k, v in sorted(c["types"].items())) + (" + hidden tests" if c["hidden"] else "")
            req = c["request"] if len(c["request"]) <= 160 else c["request"][:157].rsplit(" ", 1)[0] + "..."
            lines.append(f"| `{c['name']}` | {req or '(see prompt.md)'} | {c['expected']} | {g or 'none'} |")
    lines += ["", END]
    return "\n".join(lines)


def main(argv):
    block = build()
    if "--print" in argv:
        print(block)
        return 0
    path = os.path.join(ROOT, "TESTING.md")
    t = read(path)
    if START in t and END in t:
        t = t[:t.index(START)] + block + t[t.index(END) + len(END):]
    else:
        t = t.rstrip("\n") + "\n\n## Case catalogue\n\nGenerated by `python3 tools/eval/catalogue.py` from the files in `evals/`; do not edit by hand.\n\n" + block + "\n"
    open(path, "w").write(t)
    print("wrote", path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
