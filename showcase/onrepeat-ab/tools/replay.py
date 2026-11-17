import json, subprocess, sys, pathlib, shutil
S = pathlib.Path("/tmp/claude-0/-home-user-tabby/3fb2cd70-88cf-56b8-80cc-cb7d5e9b86ac/scratchpad")
arm, steps = sys.argv[1], sys.argv[2:]
R = S / "replay" / arm
shutil.rmtree(R, ignore_errors=True); R.mkdir(parents=True)
run = lambda *a: subprocess.run(a, cwd=R, capture_output=True, text=True)
run("git", "init", "-q"); run("git", "config", "user.email", "r@x"); run("git", "config", "user.name", "replay")
src = str(S / "ws" / arm)
for step in steps:
    for line in open(S / "logs" / f"{arm}-{step}.jsonl"):
        try: e = json.loads(line)
        except ValueError: continue
        if e.get("type") != "assistant" or e.get("parent_tool_use_id"): continue
        for c in e["message"]["content"]:
            if c.get("type") != "tool_use": continue
            i = json.loads(json.dumps(c["input"]).replace(src, str(R)))
            if c["name"] == "Write":
                p = pathlib.Path(i["file_path"]); p.parent.mkdir(parents=True, exist_ok=True); p.write_text(i["content"])
            elif c["name"] == "Edit":
                p = pathlib.Path(i["file_path"]); t = p.read_text()
                if i["old_string"] not in t: print("EDIT MISS", step, p.name); continue
                p.write_text(t.replace(i["old_string"], i["new_string"]) if i.get("replace_all") else t.replace(i["old_string"], i["new_string"], 1))
            elif c["name"] == "Bash":
                subprocess.run(["bash", "-c", i["command"]], cwd=R, capture_output=True, text=True, timeout=600)
    run("git", "add", "-A", "--", ".", ":!.venv", ":!target", ":!**/__pycache__", ":!*.so", ":!.pytest_cache", ":!.ruff_cache", ":!dist")
    run("git", "commit", "-q", "-m", step, "--allow-empty")
    print("committed", step)
