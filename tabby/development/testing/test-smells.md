# Testing smells

Same format as [code-smells.md](../code/code-smells.md): the smell, `→`, the fix. The rules are in [testing-basics-and-fixtures.md](testing-basics-and-fixtures.md).

- A test that cannot fail (asserts a mock was called, `is not None`, `assert True`) → assert the result or the behaviour
- An expected value pasted from running the code, or recomputed with the code's own formula (`assert add(a, b) == a + b`) → take it from the spec or a hand calculation; a literal
- A test that breaks when you refactor and behaviour has not changed (it asserts private calls, call order or internal structure) → assert what a caller can see
- A new test you cannot tie to a change that would make it fail → name that change before writing the test; if you cannot, the test checks nothing
- An existing test edited, skipped or xfailed to get green, or an assertion loosened → fix the code; if the test contradicts the spec, leave it and report it
- A bug fix with no test seen failing first → write the test, run it, see it fail for the right reason, then fix
- `if`, `for` or `try` in a test body → `pytest.mark.parametrize` with `ids`
- `time.sleep`, the real clock, unseeded randomness, real network → control time, seed, mock only the external boundary
- State changed and not restored → `monkeypatch`, `tmp_path`
- A new test in a new folder when the project's tests live elsewhere → put it where the project's tests already live, with their naming
- The unit under test mocked → mock only network, clock, randomness and third-party APIs
- A property or contract that only forbids ("never allow X") → add the if-and-only-if: what must be allowed; a function that refuses everything must fail it ([proof-based-testing.md](proof-based-testing.md))
- A law, `@invariant` or `@ensure` loosened, an `assume()` added or a strategy narrowed to get green → fix the code; a law that contradicts the spec goes to the user
- "Proved" or "verified" said of a Hypothesis or CrossHair run → "searched, no counterexample in budget N"
- Tests of trivial getters, the language or a library, added to raise coverage → delete them
