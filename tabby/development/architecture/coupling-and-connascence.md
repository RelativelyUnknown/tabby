# Coupling: say which kind

"Reduce coupling" is not a finding. Two parts of the code are coupled when a change to one forces a change to the other; the useful question is *which kind*, how strong it is and how far apart the two parts sit. Connascence names the kinds. Use it to describe a design problem in review and to choose the smallest fix when you write code.

## Kinds, weakest first

| Kind | Two parts must agree on | Example | Fix toward the one above |
| --- | --- | --- | --- |
| Name | the name of a thing | a caller uses `load_user` | none needed; this is normal coupling |
| Type | the type of a thing | a function takes a `list[int]` | annotate it; the checker enforces it |
| Meaning | what a value stands for | `status == 3`, `"ADMIN"` typed in two files | an `Enum` or named constant, defined once |
| Position | the order of values | `row[4]`, `f(a, b, True, None)` | a `NamedTuple` or dataclass; keyword-only arguments |
| Algorithm | how to compute or encode something | one file signs a token, another checks it with its own copy of the recipe | one function both call |
| Execution order | the order of calls | `connect()` before `query()` or it fails | one call that does both; a context manager; a constructor that returns a ready object |
| Timing | when things happen | a sleep so the other side is ready | an event or a return value, not a delay |
| Identity | that two names point at one object | two modules sharing one mutable list | pass a copy or a value; own it in one place |

Each step down is harder to see in the code and costs more per change. A strong kind is acceptable when the two parts are close (one function, one small class). The same kind across modules, packages or services is the finding.

## Three questions

1. **Strength:** which row of the table is it?
2. **Locality:** same function, same file, same package, or across a deployable boundary? Strength matters more the farther apart the parts are.
3. **Degree:** how many places agree? Three files sharing a magic string is worse than two.

Fix by lowering the strength, moving the two parts closer, or cutting the degree, in that order of preference. Do not remove coupling that the problem needs: two parts that must agree on a format will always agree on it; the aim is one place that says what it is.

## In review

A finding names both places, the kind and the input or change that breaks it: `billing/invoice.py:88 and web/forms.py:41 both write the tax rounding as round(x * 1.19, 2) (algorithm): changing the rate in one leaves the other charging the old amount. Move it to one function.` Without the second place and a change that breaks it, it is a smell, not a finding.

[`review/scripts/cochange.py`](../../../review/scripts/cochange.py) finds pairs the imports do not show: files that change together in git history with no import between them are usually sharing a meaning or an algorithm. See [architecture-fitness-functions.md](architecture-fitness-functions.md) to keep a boundary from decaying once it is drawn.

## When writing code

- Before adding a second copy of a literal, a format, a rounding rule or a regex, check whether the first lives anywhere reusable (`git grep`). Two copies are connascence of meaning or algorithm waiting for its change.
- Positional values past two or three: a dataclass or keyword-only parameters. A boolean flag in a call (`save(x, True)`): a keyword (`save(x, overwrite=True)`).
- A required call order is a state machine nobody wrote down: make the wrong order impossible ([parse-dont-validate.md](parse-dont-validate.md)) or see [`review/state-machines.md`](../../../review/state-machines.md).
