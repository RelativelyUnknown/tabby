# Public surface budget

Every name a user can import, every argument, every raised exception and every output format is a promise; with enough users someone depends on every observable behaviour, including the ones you did not mean to offer (Hyrum's law). The surface is a budget: export less, and notice when it changes.

Pair this page with [public-api-design.md](public-api-design.md) for the rules on each name and [deprecation-and-migration.md](../../workflow/deprecation-and-migration.md) for taking one back.

## Keep it small

- A leading underscore on every module and name that is not meant to be imported (`_internal.py`, `_helpers`). Anything without one is public.
- `__all__` in the package's `__init__.py` lists exactly the supported names; nothing else is re-exported by accident from an `import *`.
- Return types that are yours (a dataclass, a `Protocol`) rather than a third-party object or a bare `dict`; exposing a dependency's class makes its version part of your API.
- Arguments keyword-only past the second; an `**options` catch-all is a promise to accept anything.
- Exceptions: raise your own base class; the exact message is not a promise, so say so in the docs.

## Notice when it changes

Compare the current public API with the last release in CI or before tagging. With `griffe` (checked: `griffe check shop -s src -a v0.1.0` against a git tag printed `price(x): Parameter was added as required` after a parameter was added):

```
griffe check <package> -s src -a <last-release-tag>
```

Exit code 1 means a breaking change; read each line and decide if it is intended. An intended break follows the version rules in [package-layout-and-versioning.md](package-layout-and-versioning.md); an accidental one is reverted. As a quick check with no tool, `python -c "import pkg; print(sorted(pkg.__all__))"` before and after.

## Review questions

- Does the diff add a name to `__all__`, a public module or a public argument? Each one needs a user-visible reason, a docstring and a test.
- Is anything exported only because a test imports it? Test the public name or move the test next to the code.
- Does any returned object expose a third-party type, a mutable internal list or an internal ordering?
