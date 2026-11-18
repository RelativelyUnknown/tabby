# Flaky tests: find the cause, then fix it at the cause

A flaky test fails sometimes with no change to the code. It is a real bug in the test, in the code or in the environment, and the failures it hides are real. The first rule stays: no sleeps, reruns or retry decorators until the cause is named ([testing-basics-and-fixtures.md](testing-basics-and-fixtures.md)). This page is the order of work.

## 1. Measure it

Run the one test in a loop and count: `for i in $(seq 50); do pytest path::test -x -q || break; done` gives a failure rate. A test that never fails alone but fails in the suite depends on order or shared state: run the whole file, then `pytest -p no:randomly` to fix the order, then, if the project uses `pytest-randomly`, `pytest --randomly-seed=N` with the failing seed to repeat a bad order (do not add a plugin just for this).

## 2. Find which of these it is

| Cause | Sign | Fix |
| --- | --- | --- |
| **Order or shared state** | passes alone, fails after another test | the first test left state (a global, a file, a DB row, a patched object): `monkeypatch`, `tmp_path`, a transaction per test |
| **Time** | fails near midnight, month end, a DST change, or a slow machine | pass the clock in; freeze it in the test ([foreseeable-failures.md](../code/foreseeable-failures.md)) |
| **Randomness** | fails for some seeds | seed it; if a seed fails, that seed is a real bug: keep it as a test |
| **Concurrency** | fails more under load or with `-n` | a race in the code under test: fix the code, not the test; wait on an event, never a sleep |
| **Real network or service** | fails when the other side is slow or down | a fake at the boundary; one integration test for the real call |
| **Unordered data** | set or dict order, `listdir`, a query with no `ORDER BY` | sort the result or compare as a set |
| **Resource clash** | a fixed port, a fixed filename, a shared database | port 0 and `tmp_path`; a database per worker |

## 3. Fix it, prove it

Write the fix, then repeat the loop of step 1 at the same count with zero failures. Report the rate before and after: `failed 7 of 50 before; 0 of 100 after; cause: fixed port 8000 shared between two workers`. A fix you cannot tie to a cause is a guess; say so.

## Never

- Add `@pytest.mark.flaky`, `retries=`, `sleep()` or a longer timeout as the fix. The one case for a retry is a call to a real external service in an integration test, marked as such, with the cause written next to it.
- Skip or xfail the test to get green ([core rule 1](../../SKILL.md)). A test you cannot fix goes to the user, named, with the failure rate and the causes you ruled out.
- Quarantine without a date and an owner: a skipped test that nobody reads is deleted coverage.
