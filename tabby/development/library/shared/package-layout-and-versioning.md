# Package setup

## Start

- **Existing project: keep its tools.** Poetry, black, flake8, pyright, setuptools stay. Do the task with them, report what differs from the defaults below as a suggestion, and migrate only if asked. Do not edit CI, lint or pytest config beyond what the task needs.
- **New project: use the defaults** (uv, hatchling, ruff, mypy strict, pytest, `src` layout) from the templates in `development/assets/`.
- Never install a tool or dependency silently.

## New package checklist

1. `pyproject.toml` is the only config file: no `setup.py`, `setup.cfg` or `requirements*.txt`. Start from `development/assets/pyproject.toml`; replace the `<placeholders>` and set the Python versions from the Python target. `requires-python` has a lower bound only.
2. `src/<pkg>/__init__.py` with `__all__`, an empty `src/<pkg>/py.typed`, and `tests/` mirroring the package ([testing-basics-and-fixtures.md](../../testing/testing-basics-and-fixtures.md)).
3. One command runs lint, type check and tests, locally and in CI: copy `development/assets/Makefile` (`make check`; `make` alone lists the targets, and `make test T=path::name` runs one test while you work). When the project must be tested on several Python versions, copy `development/assets/tox.ini` instead (`tox`; `tox -e py313 -- path::name` for one test; `dependency_groups` needs tox 4.22). Or use the equivalent for the project's runner; if the project already has a Makefile, tox or nox setup, keep it.
4. CI: copy `development/assets/ci.yml`. It tests the Python target and the newest release, installs from the lock file, runs only `make check`, grants `contents: read`, and uses no secrets. Pin each action to its latest release tag (`git ls-remote --tags https://github.com/<owner>/<action>`).
5. Dev tools are pinned by the lock file (`uv sync --locked`). Keep runtime dependencies minimal; heavy or niche ones go in extras.
6. The test suite runs with no network, no secrets and no running services.
7. `.gitignore` covers `.venv/`, `__pycache__/`, `dist/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`.

Run `make check` on the result and show its output. A scaffold you did not run is not done.

## Package layout

Packages are organized by component; dependencies point one way. Look at the tree before adding a file.

Layout is a map of who may know about whom. Ask where a new piece belongs by what it owns and what depends on it, not by what kind of code it is; a circular import is the map telling you a boundary is in the wrong place.

- Name packages for what they own (`billing/`, `ingest/`, `auth/`), never for the shape of the code (`models/`, `utils/`, `common/`, `misc/`, `base/`).
- A component is a subpackage with its own `__init__.py` and tests that mirror it. Nest only when a package has distinct components, to about three levels below the source root.
- Each package has a public face: its `__init__.py` re-exports what others may use, and other packages import from it, not from internal modules. Layers point one way (`api` to `services` to `domain`); a circular import means the boundary is in the wrong place, so move the boundary instead of hiding the import inside a function.
- Shared types live in a leaf package that imports nothing internal.
- One primary concept per module. Name files for their contents, without repeating the package name. A module past a few hundred lines is a signal to split by concept.
- **Each fact has one home**: the version, the dependency list, a schema, a default config value. Other files read or link to it. The version lives in `pyproject.toml`; code that needs it uses `importlib.metadata.version("<pkg>")` instead of a second literal.
- Give each kind of content one home: docstrings for API behavior, the README for install and usage, `docs/` for concepts, commit messages for history, config comments for config.
- Never hand-edit generated files; edit the source and regenerate. A new top-level directory needs a reason. Update an architecture file if one exists; do not create one unasked.

## Entry points

A command is `[project.scripts]` with `name = "pkg.cli:main"`. `main()` returns `None` or an exit code; the generated script calls `sys.exit(main())`. After `uv sync`, `uv run name` works, and the wheel's `entry_points.txt` lists it under `[console_scripts]`. Check it in the built wheel, not in the source tree (`unzip -p dist/*.whl '*/entry_points.txt'`).

## Versioning

Pick one and read it everywhere else with `importlib.metadata.version("<dist-name>")`; never type the number twice.

- Static: `version = "2.0.0"` in `[project]` (`uv_build` and `hatchling` both build it). Bump it in the release commit.
- From a file: `dynamic = ["version"]` with `[tool.hatch.version]` and `path = "src/<pkg>/__init__.py"`; hatchling reads `__version__`. Built `0.4.0` from `__version__ = "0.4.0"`.
- From git tags: `requires = ["hatchling", "hatch-vcs"]`, `dynamic = ["version"]`, `[tool.hatch.version] source = "vcs"`, and optionally `[tool.hatch.build.hooks.vcs] version-file = "src/<pkg>/_version.py"` (git-ignored). A build at the tag `v1.2.3` gave `1.2.3`; one commit later it gave `1.2.4.dev1+g<sha>`.

Consequences to plan for:

- A version with a `+g<sha>` part is a local version, and PyPI rejects it. Publish only from a tagged commit, and make CI fetch the tags (a full clone, not a shallow one).
- `importlib.metadata.version(...)` reports the version recorded at install time. In an editable install it stayed `1.2.3` after a new commit until the package was reinstalled.
