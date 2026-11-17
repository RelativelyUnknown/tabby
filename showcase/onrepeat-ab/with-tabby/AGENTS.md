## Tabby
reviewed: 2026-11-17 @ no commits yet
purpose: terminal tool that makes a "Wrapped" for any year you pick, from your own Spotify export
users: just you, in the terminal; friends maybe later
goals: for a chosen year, print top 5 artists, top 5 songs and hours listened; later, add Apple Music data (it replaces Spotify from June) and merge duplicate songs
growth: 1) Apple Music export; 2) merge duplicate songs (Rust, after the Python version works); 3) shareable card
workload: one person, run on demand; about 8 JSON files, ~12 MB each, read into memory (assumed)
map: not written yet; the repo is empty
conventions: the song-merging is one separate function, so Rust can replace it later
gotchas: the export contains IP addresses and listening history
out-of-scope: Spotify API and logins, accounts, a website, the shareable card (for now)
constraints: Python 3.12+ (assumed); no new dependencies without asking (assumed)
always: run `uv run pytest` and `uv run ruff check` before reporting done (assumed)
ask-first: new dependency, adding Rust or maturin, changing the output format (assumed)
never: commit anything in data/, print or log IP addresses, commit secrets
kind: code
modules: development
docs: README (assumed)
commands: check = `uv run ruff check && uv run pytest`; one test = `uv run pytest path::name` (assumed)
open: the exact fields in your Spotify files; Rust setup

## Python defaults
runner: uv
test: pytest
lint: ruff (also formats)
types: none yet (assumed)
build: none yet (library packaging isn't needed)
ci: none yet
python: 3.12+ (assumed)
