# Parse, don't validate

A function that checks its input and returns nothing leaves the data exactly as unsafe as before: the next function has to check again, or forgets to. A function that turns raw input into a type that can only hold valid values does the check once, at the edge, and every function after it receives a value that cannot be wrong. The same idea, stated the other way: make illegal states unrepresentable.

Use it at the boundary where data comes in (a request body, a file row, an environment variable, a CLI argument) and for any object with a lifecycle (an order, a job, a connection).

## Edge: parse into a type

- Parse once, at the edge, into a dataclass, `pydantic` model or `NewType` that holds only valid values. Everything inside takes that type, never the raw dict or string. See [errors-validation-logging.md](../code/errors-validation-logging.md) for where validation errors go.
- A value with a rule gets a type with the rule: `Email`, `PositiveInt`, `NonEmpty[list]`. A frozen dataclass with `__post_init__` that raises, a pydantic constrained type, or a `NewType` built only by one `parse_x()` function.
- Callers inside the core do not re-validate what the type already guarantees; that check is dead code ([code-smells.md](../code/code-smells.md)).

```python
# before: every function re-checks, one forgets
def discount(order: dict) -> int:
    if not order.get("items"): raise ValueError
    ...

# after: parsed once; an empty order cannot be built
@dataclass(frozen=True)
class Order:
    items: tuple[Item, ...]
    def __post_init__(self):
        if not self.items:
            raise ValueError("an order needs at least one item")
def discount(order: Order) -> int: ...
```

## Objects: no impossible combinations

Smell: a record with flags or optional fields whose valid combinations are fewer than the type allows.

| Smell | Illegal state it allows | Representation that cannot |
| --- | --- | --- |
| `status: str` plus `shipped_at: datetime \| None` | `status="pending"` with a `shipped_at`; `"shipped"` without one | one class per state (`Pending`, `Shipped(at)`) in a `Union`, matched with `match` |
| `is_loading`, `error`, `data` as three fields | loading and failed at once | one field holding one of three small classes |
| `(start, end)` where `end >= start` is assumed | `end < start` | a `Range` that checks in its constructor |
| `open()` then `use()` then `close()` | `use()` before `open()` | a context manager that only hands out the usable object |
| `str` for ids of several kinds | passing a `user_id` where an `order_id` goes | `NewType("OrderId", str)` |

`Literal["a", "b"]` or an `Enum` for a closed set, a `match` with `assert_never` in the default arm so a new state is a type error everywhere it is missed, `frozen=True` so a valid value stays valid.

## Limits

- Do not build a type for a rule used once; a plain check at the one place is simpler.
- Python does not enforce types at run time. The parse function is the enforcement; the annotation lets the checker find a caller that skips it.
- This is also what makes [proof-based testing](../testing/proof-based-testing.md) cheap: the smaller the set of possible inputs, the fewer laws are needed and the stronger each one is.
