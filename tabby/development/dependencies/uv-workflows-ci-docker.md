# uv

Applies when `runner` is uv; do not move a poetry, pdm or pip project to uv unasked. uv changes quickly, so `uv help <command>` wins over this page.

## Pick the mode

- **Project** (`pyproject.toml` and `uv.lock`): `uv add`, `uv add --dev`, `uv remove`, `uv lock`, `uv sync`, `uv run`. Commit `uv.lock` and `.python-version`; never edit the lock by hand.
- **Script**: `uv add --script s.py pkg` writes a PEP 723 `# /// script` block, then `uv run s.py` builds the environment. A one-off dependency is `uv run --with rich s.py`.
- **Tool**: `uvx ruff check` runs a tool in a throwaway environment; `uv tool install ruff` installs a command-line tool for the user. Neither is a project dependency.
- **pip-compatible** (`uv pip install`): only for a project that is not a uv project. In a uv project, `uv pip install` bypasses the lock and the next `uv sync` removes the package.

## Rules

- Change dependencies with `uv add` and `uv remove`. If you edit `pyproject.toml` by hand, run `uv lock` after.
- Run commands with `uv run <cmd>`: it syncs first and needs no activation. A `VIRTUAL_ENV` that is not the project's is ignored with a warning; `--active` targets it.
- Dev tools go in a dependency group (`uv add --dev pytest` writes `[dependency-groups] dev`, PEP 735), not in an extra; extras are for users of the package. `uv sync` installs `dev` by default; `--no-dev`, `--group x`, `--only-group x`, `--extra x`, `--all-extras` change that.
- In CI and images use `uv sync --locked`: it fails when the lock is out of date with `pyproject.toml`. `--frozen` installs from the lock without checking it is current, so a stale lock is used silently. `uv lock --check` checks without installing. Then run with `uv run --no-sync`.
- Upgrade one package with `uv lock --upgrade-package name`, everything with `uv lock --upgrade`; `uv tree --outdated` shows what is behind. `uv lock --exclude-newer <date>` resolves as of a date.
- `uv python install 3.13` fetches an interpreter; `uv python pin 3.12` writes `.python-version`. `requires-python` is the support floor and the lock resolves for every version it allows, so keep it honest.
- A workspace is several packages with one lock. `uv init packages/x` inside a project registers the member in `[tool.uv.workspace]`; a sibling dependency is `name = { workspace = true }` under `[tool.uv.sources]`. Use `uv sync --package app` and `uv run --package app`.
- `uv sync --no-install-project` installs the dependencies but not the project: the dependency layer of a Docker image, built from `pyproject.toml` and `uv.lock` alone. Layering and a CI job: the "uv in Docker" and "uv in CI" sections below.
- `uv export --no-hashes --no-dev --format requirements-txt` produces a requirements file for tools that need one.
- `uv init --lib` writes the `uv_build` backend in 0.11; do not swap the backend of an existing project. Building and publishing: [release-process.md](../library/shared/release-process.md).
- A private index is `[[tool.uv.index]]` with `explicit = true`, and a package taken from it is pinned under `[tool.uv.sources]`, so its name cannot be filled from the public index.

## uv in CI

### GitHub Actions

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
      - uses: astral-sh/setup-uv@c771a70e6277c0a99b617c7a806ffedaca235ff9 # v9.0.0
        with:
          version: "0.13.7"  # pin uv
      - run: uv sync --locked
      - run: uv run --no-sync pytest
```

The uv guide pins both actions to commit SHAs, as above; this repository's advice is a tag or a SHA (see [choosing-dependencies.md](choosing-dependencies.md)). The guide installs Python with `uv python install`; `setup-uv` and `actions/setup-python` also work.

## uv in Docker

### Docker: dependencies first, source second

```dockerfile
FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:0.11.32 /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /app

# The dependency layer changes only when pyproject.toml or uv.lock change.
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --no-dev

COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

CMD ["uv", "run", "--no-sync", "python", "-m", "app"]
```

- Pin the uv image to a version, not `latest`. The uv guide mounts only `uv.lock` for the dependency layer and uses `--frozen` there, because `pyproject.toml` is not copied yet; copying both files first, as above, lets `--locked` check the lock in that layer too.
- In a workspace, `--no-install-workspace` leaves out the project and every workspace member from the dependency layer; `--no-install-package <name>` leaves out one package.
- `UV_LINK_MODE=copy` avoids hard-link warnings when the cache is a mounted volume; `UV_COMPILE_BYTECODE=1` trades build time for start-up time.
- A multi-stage build copies `/app/.venv` from the build stage into a slim runtime stage and puts `.venv/bin` on `PATH`.
- Run as a non-root user; secrets never go in `COPY` or `ENV`.
