# Proof-based testing for pure logic

Example tests check the inputs someone thought of. Here the spec is written as laws that must hold for every input, a solver and a generator hunt for a counterexample, and a mutation run checks that the laws are sharp. Python has no proof checker, so the honest label is "searched, no counterexample found", never "proved". The idea comes from Bend 2's `LAWS.bend` and Microsoft/GitHub Next's PDD Kit; the Python form below was run, not just read.

Use it for pure code whose wrong answer is expensive: authorisation and eligibility rules, money, dates, pricing, parsers, state machines. Skip it for I/O, ORMs, HTTP and C extensions: one thin integration test each.

## Order of work

1. **Write the law as if-and-only-if first.** For each function state what must be allowed and what must be refused, from the spec, before reading the code. A rule that only says "never allow X" is passed by a function that refuses everything (PDD Kit calls a proof of such a rule *vibe verification*). A law whose expected value reuses the code's own expression restates it ([test-smells.md](test-smells.md)).
2. **Split the pure core from the edge.** Decision logic with no clock, file, network or global state goes in plain functions; a thin wrapper does the I/O ([design-patterns-and-layers.md](../architecture/design-patterns-and-layers.md)). Only the core is a candidate; the wrapper gets an integration test.
3. **Pick the oracle**, strongest first: a table or if-and-only-if from the spec; a slow, obvious reference implementation (differential test); an inverse (roundtrip); a metamorphic relation (reorder the input, the output is the same; double the amounts, the total doubles); an invariant; last, "does not crash". Examples and strategies are in [test-rigor-property-and-release.md](test-rigor-property-and-release.md). A mutable object or workflow: `RuleBasedStateMachine` with `@rule`, `@precondition` and an `@invariant` checked after every step.
4. **Search for counterexamples with the solver.** See the next section.
5. **Mutation-audit the core.** Every survivor in logic is a law that is too weak or a missing law ([test-rigor-property-and-release.md](test-rigor-property-and-release.md), mutation section). Strengthen the law, never the code.
6. **Report with a label** (last section).

Never loosen an existing law, contract, `@invariant` or oracle to get green (core rule 1). A law that contradicts the new requirement goes to the user with the line it contradicts.

## Solver search: CrossHair

CrossHair runs the function on symbolic values and asks an SMT solver for inputs that reach each branch, so it finds the one-in-a-million branch that random generation walks past.

On a function with `if pct == 77: return price + 1` (a planted bug) and a Hypothesis bounds property:

- Plain Hypothesis found it in 8 of 15 runs; the default profile is a coin flip for a single-value branch.
- `pytest --hypothesis-profile=crosshair` found it and shrank to `discount(0, 77)`.
- `crosshair check` on the module reported the same input from the `icontract` postcondition.

Setup (dev dependencies; a new dependency follows the ladder and `ask-first:`; versions checked: crosshair-tool 0.0.113, hypothesis-crosshair 0.0.32, Hypothesis 6.170.15):

```python
# tests/conftest.py
from hypothesis import settings
settings.register_profile("crosshair", backend="crosshair", deadline=None, max_examples=200)
```

```
HYPOTHESIS_CROSSHAIR_MAX_UNINTERESTING_ITERATIONS=25 pytest --hypothesis-profile=crosshair
crosshair check --per_condition_timeout=10 src/pkg/core.py    # contracts: icontract, deal or PEP 316 docstrings
```

- Run it as its own CI job, not the default profile. The backend is labelled pre-alpha and prototype by its authors, per-path timeouts end an exploration quietly, and C extensions, I/O, hashing and non-determinism cannot be solved. Floats and long strings are slow.
- A green run means "no counterexample found in the budget". Say that. A red run is a real input: reproduce it with plain Python before reporting it.
- Contracts (`icontract`, `deal`) put the law next to the function and run on every call, so a hot path pays for them. Use them where the project already does, or ask first. Otherwise keep the laws as Hypothesis properties in the test module: no new dependency, and CrossHair runs them through the profile. `deal` was not run here; `icontract` was.

## Mutation settings that exist (mutmut 3.8.1)

Read from `[tool.mutmut]` in `pyproject.toml` or `[mutmut]` in `setup.cfg`:

```toml
[tool.mutmut]
source_paths = ["src/pkg/"]             # paths_to_mutate still works but warns it is deprecated
only_mutate = ["src/pkg/core.py"]       # globs; must end in * or .py, a bare folder draws an "invalid pattern" warning
do_not_mutate = ["*__init__.py"]
mutate_only_covered_lines = true
max_stack_depth = 8                     # ignore mutants only reached through deep call chains
process_isolation = "forkserver"        # POSIX only; default "fork"
forkserver_warmup = "collect"
```

`mutmut run`, `mutmut results`, `mutmut browse`. Exclude logging with `# pragma: no mutate` (one line) or `# pragma: no mutate block`. mutmut writes `mutants/`; keep it in `.gitignore`.

What it showed: `can_edit = role == "admin" or (role == "editor" and owner)` with one example test (`admin` is allowed) left 4 of 8 mutants alive. Adding one if-and-only-if property over `{admin, editor, viewer, ""} x {True, False}` killed 8 of 8. The mutation run found the weak test; the law fixed it.

## Report labels

Per changed function, one label and the assumptions left:

- `searched: hypothesis+crosshair`, plus the budget (iterations, timeout) and mutants killed or surviving
- `property/stateful`: Hypothesis only, no solver
- `boundary: integration test`: I/O or C code, not searched
- `not covered`: with the reason

End with the trusted base in one line: what the laws assume and nothing checks (the database, the clock, a library, the spec itself). Redundant example tests on a function the laws now cover are listed as candidates to remove, not removed (testing never-miss rule 1).
