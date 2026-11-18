# How good is this test?

Coverage says a line ran, not that anything checked it. A test is good when it would fail if the behaviour it names broke, fails for one reason and says which, and survives a refactor that changes no behaviour. Use the scorecard on tests you wrote before reporting them, and in review on tests a diff adds or relies on. The smells in [test-smells.md](test-smells.md) are the fast checklist; this page rates a test and finds the risks no test covers.

## The break-it check comes first

A test you cannot make go red is not a test. For each new or relied-on test, change the code under it on purpose (flip the comparison, return early, drop the branch), run the test, see it fail for the right reason, and put the code back. [`../../review/scripts/mutation_probe.py`](../../../review/scripts/mutation_probe.py) does it for a whole file:

```
python3 <review folder>/scripts/mutation_probe.py src/pkg/pricing.py --cmd "python -m pytest -q tests/test_pricing.py"
```

On a refund rule with five tests it printed `9 changes tried, 8 caught, 1 survived`, the survivor `line 2: 0 -> 1` (the `amount <= 0` boundary was never pinned at 1), and `test_trivial` as never red (it asserted `is not None`). Each survivor is a missing or weak assertion, or an equivalent change you decide is harmless; each never-red test is deleted or given an assertion. For decision logic use the full audit in [proof-based-testing.md](proof-based-testing.md) (mutmut); the probe is the cheap version for a file.

## Scorecard

Score each test 0 or 1 on the first five; a test under 4 gets fixed or deleted.

| Question | Fails when |
| --- | --- |
| **Breaks:** goes red if the behaviour breaks | survives the break-it check; asserts a mock was called, `is not None`, or nothing |
| **One reason:** one behaviour, one failure cause | several unrelated asserts; a long test where the first failure hides the rest |
| **Independent:** passes alone, in any order, repeated | needs another test's data, a shared file, the order of the run |
| **Behaviour, not structure:** survives a refactor | asserts private calls, call order or internals; breaks on a rename that changes nothing a caller sees |
| **Readable failure:** the message names what is wrong | `assert x` with no context; a name like `test_1`; a fixture hiding what the input is |
| Speed (note only) | over a second for a unit test |

A test name that states the behaviour (`test_refund_refused_after_30_days_for_non_members`) is part of the fifth question: the failure line should be enough to start from.

## Risk map: what is left untested

List what can go wrong, each as one line from the code and its spec, then mark which test would catch it:

| What can go wrong | Caught by |
| --- | --- |
| a member refunded on day 61 | `test_member_too_old` |
| amount exactly 0 | `test_zero` |
| amount 1 (the boundary) | nothing |
| a negative amount | nothing |

Rows marked `nothing` are the untested risks: write the test, or report the row. Sources for rows: each `if` and exit in the function, each input an outside source can send ([foreseeable-failures.md](../code/foreseeable-failures.md)), each line of the spec, each earlier bug. A coverage percentage cannot show this; it counts lines that ran.

## Reporting

One line per file or change: `tests: 6; break-it check 8 of 9 caught, survivor line 2 (amount boundary), test_trivial never red; risk map: 2 rows uncovered (amount 1, negative amount)`. A test you rated under 4 and left is named with the reason.
