# Specs and slices

The cheapest place to find a wrong assumption is before code exists; the next cheapest is in a slice small enough to throw away. Ask: can I say in one sentence what done looks like? If yes, do the task. If no, write down what you would build and what you are unsure of, and let that be reviewed before the code is.

## When a spec is worth it

A spec is for a request that names an outcome but not its edges, touches more than one module, or has several plausible readings ("add scheduled report emails"). It is not for a request that names the change ("add a `--json` flag"). A request too open to even write a spec for gets one to three questions instead ([SKILL.md](../../SKILL.md)).

## The spec

One page, in the project's convention (`docs/specs/<name>.md` if it has a docs folder, otherwise in the reply). Five headings, each as short as it can be:

- **Objective:** one sentence, and who it is for.
- **Commands:** how to run it and how to test it, from the repo.
- **Boundaries:** what you will always do, what needs asking first, what you will not touch.
- **Success criteria:** observable and testable ("a report arrives by 07:00 UTC on Mondays"), each one a test you could write.
- **Open questions:** each with the answer you would assume. Unanswered, they become `(assumed)` in the report.

## Slices

- Build one **vertical slice** at a time: the smallest change that works from input to output through every layer it touches, not a layer at a time. A slice leaves the tests green and can be committed alone.
- Order by risk first (the part most likely to prove the design wrong), then by dependency. With two sides that must agree, fix the contract first, in a type or a test.
- Each slice names its test and the command that shows it works. After two or three slices, stop and check the result against the success criteria before going on.
- Build slice one, report it, and say what the next slices would be. Do not build the whole plan on assumptions nobody has confirmed.

## Walking skeleton: the first slice of something new

For a new feature or service that crosses several layers (input, logic, storage, output), make slice one a *walking skeleton*: the thinnest path that runs from the real entry point to the real output with each part as a stub that does one fixed thing. A request goes in, a hard-coded answer comes out through every layer, and one end-to-end test and the run command exist. Then fill each part in, one slice at a time, with that test green throughout.

It finds the wrong assumptions that cost most (a library that cannot do it, a format that does not match, a layer that needs a different shape) while they are cheap. Skip it for a change inside one layer, and do not let the skeleton grow into the full design before the second slice.

## Task list

For work over several slices: numbered tasks, each with the files it touches, its test, and its verify command; a checkpoint line after each group of two or three. Keep it in the reply or the spec, not as a new tracking file nobody asked for.
