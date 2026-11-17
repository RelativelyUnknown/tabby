#!/usr/bin/env python3
"""rescore.py: score a with-only run the way the paired runs were scored.

    python3 tools/eval/rescore.py DIR --like REF_DIR [--out scores.json]

A run made with `--ablation none` scores every grader, including the plugin-fired indicator ("the skill was invoked") and the
graders marked with-only, which a with/without run leaves out of the score. This recomputes each case's mean `with` score
without them. The names to leave out are the indicator graders plus every grader REF_DIR (a with/without run) marked `withOnly`.
Prints the mean over the cases in both directories and writes {case: score} to --out.
"""
import glob, json, os, statistics as st, sys

INDICATOR = ("skill-was-invoked", "indicator-only")


def cases(d):
    out = {}
    for p in glob.glob(os.path.join(d, "*.json")):
        try:
            c = json.load(open(p))["cases"][0]
        except (ValueError, KeyError, IndexError):
            continue
        out[c["name"]] = c
    return out


def left_out(ref_case):
    names = set()
    for runs in (ref_case or {}).get("arms", {}).values():
        for r in runs:
            names |= {g["name"] for g in r.get("graders", []) if g.get("withOnly")}
    return names


def rescore(case, ref_case=None):
    skip, weight = left_out(ref_case), {g["name"]: g.get("weight", 1) for g in case["graders"]}
    scores = []
    for r in case["arms"].get("with", []):
        num = den = 0
        for g in r.get("graders", []):
            if g["name"] in skip or any(k in g["name"] for k in INDICATOR):
                continue
            num += weight[g["name"]] * bool(g.get("passed")); den += weight[g["name"]]
        scores.append(num / den if den else r["score"])
    return st.mean(scores) if scores else None


def main(argv):
    if "--like" not in argv:
        print(__doc__); return 1
    d, ref = argv[0], cases(argv[argv.index("--like") + 1])
    mine = cases(d)
    scores = {n: rescore(c, ref.get(n)) for n, c in mine.items()}
    scores = {n: s for n, s in scores.items() if s is not None}
    both = [n for n in scores if n in ref]
    print(f"{len(scores)} cases rescored, {len(both)} also in the reference; mean {st.mean(scores.values()):.3f}")
    if "--out" in argv:
        json.dump(scores, open(argv[argv.index("--out") + 1], "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
