#!/usr/bin/env python3
"""validate_findings.py: check a security-audit report written as JSON against the rules in security-audit/process-and-reporting.md.

    python3 validate_findings.py findings.json [--root REPO]

Prints one line per problem and exits 1 if there are any. With --root, each finding's `file` must exist under REPO and `line`
must be within it. Stdlib only. The shape is described in security-audit/findings.schema.json.
"""
import json
import pathlib
import sys

SEVERITY = ("high", "medium", "low")
LIKELIHOOD = ("high", "medium", "low")
CLASS_STATE = ("clean", "not_applicable", "finding", "unverified")
COMMON = ("id", "bucket", "title", "file", "line")
REQUIRED = {
    "confirmed": ("entry_point", "payload", "mechanism", "effect", "severity", "likelihood", "fix", "regression_test"),
    "needs_validation": ("question", "who_can_answer"),
    "rejected": ("control",),
}


def check(doc, root=None):
    errs = []
    if not isinstance(doc, dict):
        return ["top level must be an object"]
    if not isinstance(doc.get("verdict"), str) or not doc["verdict"].strip():
        errs.append("verdict: one line, required")
    findings = doc.get("findings")
    if not isinstance(findings, list):
        return errs + ["findings: must be a list (empty for a clean audit)"]
    ids = set()
    worst = -1
    for i, f in enumerate(findings):
        tag = f"findings[{i}]" + (f" ({f.get('id')})" if isinstance(f, dict) and f.get("id") else "")
        if not isinstance(f, dict):
            errs.append(f"{tag}: must be an object")
            continue
        for k in COMMON:
            if f.get(k) in (None, ""):
                errs.append(f"{tag}: missing {k}")
        if f.get("id") in ids:
            errs.append(f"{tag}: duplicate id")
        ids.add(f.get("id"))
        bucket = f.get("bucket")
        if bucket not in REQUIRED:
            errs.append(f"{tag}: bucket must be one of {', '.join(REQUIRED)}")
            continue
        for k in REQUIRED[bucket]:
            if f.get(k) in (None, ""):
                errs.append(f"{tag}: a {bucket} finding needs {k}")
        if bucket != "confirmed" and "severity" in f:
            errs.append(f"{tag}: only confirmed findings carry a severity")
        if bucket == "confirmed":
            if f.get("severity") not in SEVERITY:
                errs.append(f"{tag}: severity must be one of {', '.join(SEVERITY)}")
            else:
                worst = max(worst, SEVERITY[::-1].index(f["severity"]))
            if f.get("likelihood") not in LIKELIHOOD:
                errs.append(f"{tag}: likelihood must be one of {', '.join(LIKELIHOOD)}")
        line = f.get("line")
        if not isinstance(line, int) or isinstance(line, bool) or line < 1:
            errs.append(f"{tag}: line must be a positive integer")
        elif root and isinstance(f.get("file"), str):
            p = pathlib.Path(root) / f["file"]
            if not p.is_file():
                errs.append(f"{tag}: file {f['file']} not found under the root")
            elif line > len(p.read_text(errors="ignore").splitlines()):
                errs.append(f"{tag}: line {line} is past the end of {f['file']}")
    overall = doc.get("overall_severity")
    if overall is not None:
        if overall not in SEVERITY:
            errs.append(f"overall_severity must be one of {', '.join(SEVERITY)}")
        elif worst < 0:
            errs.append("overall_severity set but there is no confirmed finding")
        elif SEVERITY[::-1].index(overall) > worst:
            errs.append("overall_severity is higher than the worst confirmed finding")
    cov = doc.get("coverage")
    if not isinstance(cov, dict):
        errs.append("coverage: required (what was read, what was run, what was not checked)")
    else:
        for k in ("read", "ran", "not_checked"):
            if not isinstance(cov.get(k), list):
                errs.append(f"coverage.{k}: must be a list (empty if none)")
        classes = cov.get("classes")
        if not isinstance(classes, dict) or not classes:
            errs.append("coverage.classes: map each class walked to clean, not_applicable, finding or unverified")
        else:
            for name, state in classes.items():
                if state not in CLASS_STATE:
                    errs.append(f"coverage.classes.{name}: {state!r} is not one of {', '.join(CLASS_STATE)}")
    return errs


def main(argv):
    root = None
    if "--root" in argv:
        i = argv.index("--root")
        root = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    if len(argv) != 1:
        print(__doc__)
        return 2
    try:
        doc = json.load(open(argv[0]))
    except (OSError, ValueError) as e:
        print(f"cannot read {argv[0]}: {e}")
        return 2
    errs = check(doc, root)
    print("\n".join(errs))
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
