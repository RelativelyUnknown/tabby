# Architecture rules that run

A rule written in a README ("the domain does not import the web layer") is followed until the first deadline. A rule in CI fails the build that breaks it. A fitness function is that check: a small automated test of a property of the structure, such as who may import whom, that nothing imports in a circle, or that a module stays under a size.

Add one when you create a boundary the design depends on (layers, a core with no I/O, a package that must stay dependency-free), or when a review finds a boundary already broken. Do not add one for a boundary nobody relies on.

## Import rules: import-linter

Declare the contracts in `pyproject.toml`, run `lint-imports` in the check command and in CI. Checked on a small project: with the contracts below kept it prints `Contracts: 2 kept, 0 broken.`; after `shop/domain/pricing.py` imported `shop.web.views` it printed `BROKEN` for both and `shop.domain.pricing -> shop.web.views (l.3)`.

```toml
[tool.importlinter]
root_package = "shop"

[[tool.importlinter.contracts]]
name = "domain does not import web"
type = "forbidden"
source_modules = ["shop.domain"]
forbidden_modules = ["shop.web"]

[[tool.importlinter.contracts]]
name = "layers"
type = "layers"
layers = ["shop.web", "shop.domain"]   # higher may import lower, never the reverse
```

Other contract types: `independence` (sibling packages do not import each other). A `forbidden` contract also catches an indirect path through a third module unless you set `allow_indirect_imports = true`, and a `layers` contract rules out cycles between the layers.

A new dependency follows the ladder and `ask-first:`. When it is not allowed, the stdlib test below does the same job for one rule.

## No tool: an `ast` test

```python
BANNED = {"shop.web", "requests", "sqlalchemy"}

def imported_names(path):
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.Import):
            yield from (a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            yield node.module

def test_domain_imports_nothing_banned():
    for path in pathlib.Path("src/shop/domain").rglob("*.py"):
        bad = [n for n in imported_names(path) if any(n == b or n.startswith(b + ".") for b in BANNED)]
        assert not bad, (path, bad)
```

It misses `from shop import web` (the module it sees is `shop`); the import-linter contract does not.

## Other rules worth a check

- A package that must stay light (a library core, a CLI start-up path) imports nothing outside the standard library: the same test with an allow-list instead of a ban list.
- The public API did not change by accident: [public-surface-budget.md](../library/shared/public-surface-budget.md).
- A function or file over a size you chose when you drew the boundary (a test that counts lines is crude but enough to start the conversation).

## When one fails

The check is right until shown wrong. Fix the code (move the function to the layer that may hold it, pass the value in instead of importing it). Never add an ignore, widen a contract or delete one to get green; a boundary that is wrong goes to the user with the import that needs it ([core rule 1](../../SKILL.md)). Say in the report which contracts exist and that they ran.
