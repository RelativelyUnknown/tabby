# Dependency hygiene

Every declared dependency is code someone else can change under you, an install step that can break and a supply-chain risk. The list should hold exactly what the code uses. Check it when you add or remove an import, before a release, and in a repository audit.

## Four checks

| Problem | Meaning | Tool |
| --- | --- | --- |
| Declared, never imported | dead weight; still installed and trusted | `deptry` (DEP002) |
| Imported, never declared | works only because something else pulled it in | `deptry` (DEP001 missing, DEP003 transitive) |
| Declared as runtime, used only in tests or tools | ships to every user | `deptry` (DEP004), then move it to a dev group |
| Dead code (unused functions, imports, variables) | maintenance and review cost | `vulture` (confidence under 100% is a guess; read each) |

Run them inside the project's environment with the package installed (`uv run deptry .`, `uv run vulture src`): in a `src` layout without the package installed, `deptry` reports the project's own package as a transitive dependency. Checked on a small project with `pyyaml` declared and never imported: `deptry .` printed `DEP002 'pyyaml' defined as a dependency but not used in the codebase`; `vulture src` listed an unused import and an unused function with `(90% confidence)` and `(60% confidence)`.

## Rules

- A new tool follows the ladder and `ask-first:`; the project's own lint config may already include these (ruff's `F401`, `F841`). Use the project's tool before adding one.
- `vulture` and `deptry` find *candidates*. Before removing, apply the dead-code check from [repo-audit.md](../../../tabby-review/repo-audit.md): entry points in `pyproject.toml`, framework registration, `getattr` and plugin loading, and `git log -S<name>`. A public name of a library is never dead because nothing inside calls it.
- A dependency imported only under `TYPE_CHECKING` or in one rarely run script is still a dependency; say which group it belongs to.
- A removal changes the lock file: show the diff, run the tests, and say what else it pulled out.
- Pin the direction, not every version: a library declares ranges, an application locks ([choosing-dependencies.md](choosing-dependencies.md)).

## Reporting

`deps: 14 declared, deptry 0 missing, 1 unused (pyyaml, removed), 2 dev-only moved to the dev group; vulture 3 candidates, 1 removed, 2 kept (entry points)`.
