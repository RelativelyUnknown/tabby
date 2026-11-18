# Reviewing laws and property tests

Read this when the diff touches decision logic (permissions, eligibility, pricing, parsing, state transitions) or adds or changes property tests, contracts or mutation settings. The building side is `../tabby/development/testing/proof-based-testing.md`. A review checks whether the laws could fail, not whether they pass.

## Checks, in order

1. **A law weakened in the diff.** `git diff <base>...<head> -U0 -- '*.py' | grep -nE '^[-+].*(@given|@example|@invariant|@precondition|assume\(|@icontract\.(require|ensure|invariant)|@deal\.|max_examples|suppress_health_check|st\.[a-z_]+\()'`. A removed or narrowed strategy, a new `assume`, a lower `max_examples`, a dropped `@ensure` or `@invariant`, an `@example` deleted with the fix: each needs a stated reason from the spec, or it is a finding. Changing a law to fit new code is the same defect as editing a test to get green.
2. **A law that cannot fail.** Replace the function in a scratch copy (`git archive <base> | tar -x -C "$(mktemp -d)"`) with `return False`, then `return True`, then the first branch deleted. A property that still passes is vacuous or one-sided: it only forbids, or only allows. Quote the stub that passed.
3. **Expected value from the code's own expression.** `assert f(a, b) == a + b` against `def f(a, b): return a + b`. The oracle must be a table, a reference, an inverse, a relation or an invariant.
4. **Missing positive case.** Authorisation or validation tests that only refuse. Ask what a test would say if the function returned "denied" for everyone.
5. **Strategy too wide or too narrow.** A property that fails on input the docstring excludes is a bad strategy; one that never draws the boundary values (`0`, empty, maximum, equal keys) misses the bug. Check `@example` covers the edges.
6. **Mixed core and I/O.** Decision logic that reads the clock, the environment or the database cannot be searched; propose the extraction (pure function plus thin wrapper) rather than asking for more mocks.
7. **Claims.** The description or the tests say "proved" or "verified" for a Hypothesis or CrossHair run: it is "searched with budget N". A green solver run with a timeout, I/O or a C call on the path proves nothing about that path.

## Mutation in a review

Do not run `mutmut` in the repository under review: it writes `mutants/`. Break two or three decisive lines by hand in the scratch copy (flip a comparison, drop one side of an `and`, change a constant at a boundary) and run the tests there. A mutant in an authorisation check or a money calculation that the tests do not notice is a finding; list the line, the change and the test that did not fail. If the author reports a mutation score, ask for the list of survivors, not the percentage.

## Output

Findings use the usual shape (file:line, the input or stub where it goes wrong, the smallest fix). A clean change: `Checked, no findings: laws strengthened, stub test, boundary cases`. Name what you could not run, such as CrossHair on a project that does not use it.
