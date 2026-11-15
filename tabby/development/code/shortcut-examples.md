# Worked examples: the shortcuts to avoid

Each pair is a shortcut an agent takes to get past a checker or finish quickly, and the version to write instead. The rule behind each is in [code-smells.md](code-smells.md) or [minimalism-reuse-names.md](minimalism-reuse-names.md) (which also holds the reuse ladder).

Contents: suppression · weakened test · swallowed error · reuse · over-building · defensive code · typing · Pydantic version

## Suppressing a type error

```python
# ❌ the checker was right; the ignore hides a None
user = repo.find(user_id)  # type: ignore[union-attr]
return user.email

# ✅ handle the case the type is telling you about
user = repo.find(user_id)
if user is None:
    raise UserNotFound(user_id)
return user.email
```

## Making a failing test pass

```python
# ❌ the test failed, so the assertion was loosened
def test_total_rounds_half_up():
    assert total([19.99], discount=15) is not None

# ✅ keep the assertion; fix the code (a bug fix starts with this test failing)
def test_total_rounds_half_up():
    assert total([19.99], discount=15) == Decimal("16.99")
```

A test that contradicts the spec stays as it is. Finish the rest and report it.

## Swallowing an error

```python
# ❌ the caller never learns the parse failed
try:
    config = parse(path.read_text())
except Exception:
    config = {}

# ✅ catch what you can handle, around the one line that raises
try:
    text = path.read_text(encoding="utf-8")
except FileNotFoundError:
    config = DEFAULT_CONFIG
else:
    config = parse(text)  # a bad file is a bug: let it raise
```

## Writing a helper that already exists

```python
# ❌ the repo has `slugify` in `core/text.py`; this is a second one
def make_slug(title):
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")

# ✅ `git grep -n "def .*slug"` first, then use it
from core.text import slugify
```

## Building more than was asked

```python
# ❌ a class with __init__ and one method, a factory for one implementation
class PriceFormatter:
    def __init__(self, currency): self.currency = currency
    def format(self, amount): return f"{self.currency}{amount:.2f}"

class FormatterFactory:
    @staticmethod
    def create(kind): return PriceFormatter("$")

# ✅ a function
def format_price(amount: float, currency: str = "$") -> str:
    return f"{currency}{amount:.2f}"
```

The same rule applies to UI: use the existing input component with `type="date"` rather than a hand-built date picker.

## Defending against your own data

```python
# ❌ `names` was just built by this function; it cannot be None or non-str
def join(names: list[str]) -> str:
    if names is None or not isinstance(names, list):
        raise TypeError("names must be a list")
    return ", ".join(str(n) for n in names if n)

# ✅ validate where untrusted data enters, trust the types inside
def join(names: list[str]) -> str:
    return ", ".join(names)
```

## Avoiding `Any` and `cast`

```python
# ❌ opts out of the checker
def load(raw: Any) -> Config:
    return cast(Config, raw)

# ✅ narrow with a check or a validator that returns the narrowed type
def load(raw: object) -> Config:
    if not isinstance(raw, dict):
        raise ValueError("config must be a mapping")
    return Config(**raw)

# ✅ structural type when callers pass different things
class Reader(Protocol):
    def read(self) -> bytes: ...
```

## Pydantic version

Check the installed version (`uv pip show pydantic` or the lock file) before writing models.

```python
# ❌ v1 API on a v2 project
class User(BaseModel):
    class Config:
        orm_mode = True

    @validator("email")
    def check(cls, v): ...

user.dict()

# ✅ v2
class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    @field_validator("email")
    @classmethod
    def check(cls, v: str) -> str: ...

user.model_dump()
```
