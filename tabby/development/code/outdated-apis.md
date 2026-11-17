# Outdated APIs models still write

Models trained on older code reach for these. Each row is the old form, then the current one. Check the project's Python target and pinned library versions first ([checking-apis-and-python-versions.md](../workflow/checking-apis-and-python-versions.md)); use a row only when the project is on a version that has the new form, and keep the project's own style when it differs.

| Old form | Current form | Since |
| --- | --- | --- |
| `List[int]`, `Dict[str, int]`, `Optional[X]`, `Union[A, B]` | `list[int]`, `dict[str, int]`, `X \| None`, `A \| B` | 3.10 |
| `from typing import Callable, Iterable` | `from collections.abc import Callable, Iterable` | 3.9 |
| `datetime.utcnow()`, `utcfromtimestamp()` (naive) | `datetime.now(UTC)` | 3.12 deprecates the old ones |
| `asyncio.get_event_loop().run_until_complete(f())` | `asyncio.run(f())`; inside a coroutine `asyncio.get_running_loop()` | 3.7, 3.10 |
| `asyncio.gather` that must cancel its siblings on error; `asyncio.wait_for` | `async with asyncio.TaskGroup()`; `async with asyncio.timeout(s)` | 3.11 |
| `os.path.join(...)`, `open(p).read()` | `Path(p) / "x"`, `Path(p).read_text(encoding="utf-8")` | 3.4 |
| `pkg_resources`, `setup.py`, `distutils` | `importlib.metadata`, `pyproject.toml`, `setuptools` or a build backend | `distutils` removed 3.12 |
| `dateutil` to parse `2026-01-02T03:04:05Z` | `datetime.fromisoformat(s)` | 3.11 |
| `tomli`, `str.startswith` then slice, `zip` lengths unchecked | `tomllib`, `removeprefix`, `zip(..., strict=True)` | 3.11, 3.9, 3.10 |
| hand-written batching loop | `itertools.batched(items, n)` | 3.12 |
| `class Color(str, Enum)` | `StrEnum` | 3.11 |
| `-> "Foo"` returning `self` | `-> Self` | 3.11 |
| `subprocess.Popen` plus `communicate()` for a plain call | `subprocess.run(args, capture_output=True, text=True, check=True)` | 3.7 |
| `@dataclass` field `x: list = []` | `x: list[int] = field(default_factory=list)` | always an error |
| pytest `tmpdir`, `py.path` | `tmp_path` (a `Path`) | pytest 3.9 |
| SQLAlchemy `session.query(M).filter(...)`, `declarative_base()` | `session.execute(select(M).where(...)).scalars()`, `class Base(DeclarativeBase)` | 2.0 |
| SQLAlchemy async: lazy load after the session closed | `selectinload(...)` in the query, or `expire_on_commit=False` | 2.0 |
| Pydantic `@validator`, `.dict()`, `class Config`, `parse_obj` | `@field_validator`, `.model_dump()`, `model_config = ConfigDict(...)`, `model_validate` | 2.0 |
| FastAPI `@app.on_event("startup")`; `x: int = Depends(f)` | `lifespan`; `x: Annotated[int, Depends(f)]` | 0.93, 0.95 |
| pandas `df.append(row)`, `inplace=True`, chained `df[a][b] = v` | `pd.concat`, assign the result, `df.loc[a, b] = v` | 2.0 |
| `np.int`, `np.float`, `np.bool` | `int`, `float`, `bool` or `np.int64` | NumPy 1.24 removes them |

A new language feature is not a reason to rewrite code you are not changing. Use the current form in the code you write or touch, and leave the rest.
