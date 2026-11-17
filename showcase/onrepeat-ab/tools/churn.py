import subprocess, sys
R, pairs = sys.argv[1], sys.argv[2:]
def git(*a): return subprocess.run(["git", *a], cwd=R, capture_output=True, text=True).stdout
for pair in pairs:
    label, a, b = pair.split(":")
    rows = {}
    old_files = set(git("ls-tree", "-r", "--name-only", a).split())
    for line in git("diff", "--numstat", "-M", a, b).splitlines():
        add, dele, path = line.split("\t", 2)
        if "lock" in path or path.endswith((".md", ".gitignore", ".png", ".html", ".python-version")): continue
        path = path.split(" => ")[-1].strip("{}") if "=>" in path else path
        kind = "test" if "test" in path else "src"
        new = path not in old_files and "=>" not in line
        k = (kind, "new" if new else "existing")
        r = rows.setdefault(k, [0, 0, set()]); r[0] += int(add); r[1] += int(dele); r[2].add(path.split("/")[-1])
    print(f"--- {label}")
    for (kind, age), (ad, de, fs) in sorted(rows.items()):
        print(f"  {kind:4} {age:8} +{ad:<4} -{de:<4} {sorted(fs)}")
