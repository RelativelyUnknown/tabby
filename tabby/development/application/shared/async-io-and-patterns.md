# Async code

The Python target decides whether `TaskGroup` and `asyncio.timeout` (3.11+) exist; the test plugin the project uses (`pytest-asyncio`, `anyio`) is part of its defaults.

## When async

- Async pays when many waits on I/O overlap and the libraries are async. CPU-bound work goes to a process pool; a few blocking calls inside an async app go through `asyncio.to_thread` (it copies the current `contextvars`). Match the project: do not add `anyio` or Trio to an asyncio project.
- One `asyncio.run(main())` at the program's entry point. It raises `RuntimeError` inside a running loop, so async code never calls it; sync code that must call async code runs it at the top, not in the middle.

## Rules

- Tasks that belong together run in `async with asyncio.TaskGroup() as tg:`. The first failure cancels the siblings and arrives as an `ExceptionGroup`, caught with `except*`. `asyncio.gather()` raises the first exception but leaves the other awaitables running; with `return_exceptions=True` it returns errors as values that you must check.
- A deadline is `async with asyncio.timeout(seconds):`. It cancels the body and raises `TimeoutError`. One deadline per request or job, set at the edge; inner calls take the time that remains.
- Let `CancelledError` propagate. Timeouts and `TaskGroup` rely on it. Clean up in `finally` or `async with`, then re-raise.
- Bound the fan-out. `asyncio.Semaphore(n)` around the call caps concurrency at `n`. For a stream of work, a `Queue(maxsize=n)` with `n` workers also applies backpressure: workers call `task_done()` in `finally`, the producer awaits `q.join()` after the last `put`, then cancels the workers. Never `gather` an unbounded list.
- An async generator that holds a resource needs `contextlib.aclosing(...)`, or a `break` leaves its `finally` waiting for garbage collection.
- Never block the loop: `time.sleep`, `requests`, a synchronous database driver, a large `json.loads`, a CPU loop. Find offenders with debug mode: `asyncio.run(main(), debug=True)`, `PYTHONASYNCIODEBUG=1` or `python -X dev` log `Executing <Task ...> took 0.25 seconds` for slow steps and warn `coroutine 'x' was never awaited` for a missing `await`.
- Keep a reference to every task you create, or put it in a `TaskGroup`; a task held only by the loop can be garbage collected before it finishes.
- `Lock`, `Queue` and `Event` belong to one loop and are not thread-safe. From another thread use `asyncio.run_coroutine_threadsafe(coro, loop)` or `loop.call_soon_threadsafe`.
- Tests: use the project's plugin (`pytest-asyncio` with `asyncio_mode = "auto"`, or `anyio`), or `unittest.IsolatedAsyncioTestCase`. Wrap the awaited call in `asyncio.timeout(...)` so a hang fails the test instead of freezing the run. Inject the sleep or clock instead of waiting in real time.

Shared HTTP clients, one database session per task and other service-level async rules are in [http-service-design.md](../apis/http/http-service-design.md) and [service-smells.md](../service-smells.md). Runnable examples: async-io-and-patterns.md (below).

## Async patterns

Each block runs as written on Python 3.12 or later.

### Structured concurrency and except*

```python
import asyncio

async def work(name: str, delay: float, log: list[str]) -> None:
    try:
        await asyncio.sleep(delay)
        log.append(f"{name} done")
    except asyncio.CancelledError:
        log.append(f"{name} cancelled")
        raise

async def fail() -> None:
    await asyncio.sleep(0.01)
    raise ValueError("boom")

async def main() -> list[str]:
    log: list[str] = []
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(work("slow", 1, log))
            tg.create_task(fail())
    except* ValueError as group:
        log.append(f"{len(group.exceptions)} ValueError")
    return log

assert asyncio.run(main()) == ["slow cancelled", "1 ValueError"]
```

### Bounded fan-out with a Semaphore

```python
import asyncio

async def main() -> int:
    running = peak = 0
    limit = asyncio.Semaphore(3)

    async def call(i: int) -> int:
        nonlocal running, peak
        async with limit:
            running += 1
            peak = max(peak, running)
            await asyncio.sleep(0.01)
            running -= 1
            return i

    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(call(i)) for i in range(20)]
    assert [t.result() for t in tasks] == list(range(20))
    return peak

assert asyncio.run(main()) == 3
```

### Producer and workers with a Queue

```python
import asyncio

async def main() -> list[int]:
    queue: asyncio.Queue[int] = asyncio.Queue(maxsize=2)  # put() waits when full
    results: list[int] = []

    async def worker() -> None:
        while True:
            item = await queue.get()
            try:
                results.append(item * 2)
            finally:
                queue.task_done()

    workers = [asyncio.create_task(worker()) for _ in range(2)]
    for i in range(6):
        await queue.put(i)
    await queue.join()  # every item has been processed
    for w in workers:
        w.cancel()
    await asyncio.gather(*workers, return_exceptions=True)
    return sorted(results)

assert asyncio.run(main()) == [0, 2, 4, 6, 8, 10]
```

### A deadline for a whole request

```python
import asyncio

async def step(seconds: float) -> None:
    await asyncio.sleep(seconds)

async def handle(budget: float) -> str:
    try:
        async with asyncio.timeout(budget):
            await step(0.02)
            await step(10)  # the remaining budget cancels this
    except TimeoutError:
        return "timed out"
    return "ok"

assert asyncio.run(handle(0.1)) == "timed out"
```

### Calling blocking code from async code

```python
import asyncio
import contextvars
import time

request_id = contextvars.ContextVar("request_id", default="-")

def slow_lookup() -> str:
    time.sleep(0.01)  # blocking: keep it off the event loop
    return request_id.get()

async def main() -> str:
    request_id.set("req-1")
    return await asyncio.to_thread(slow_lookup)  # the context is copied to the thread

assert asyncio.run(main()) == "req-1"
```

### Closing an async generator

```python
import asyncio
from contextlib import aclosing

closed = False

async def rows():
    global closed
    try:
        yield 1
        yield 2
    finally:
        closed = True  # the connection or file would be released here

async def main() -> None:
    async with aclosing(rows()) as it:
        async for row in it:
            break  # stop early; aclosing runs the finally block now

asyncio.run(main())
assert closed
```

### A test that cannot hang

```python
import asyncio

async def fetch() -> int:
    await asyncio.sleep(0.01)
    return 42

async def test_fetch() -> None:
    async with asyncio.timeout(1):  # a hang fails the test
        assert await fetch() == 42

asyncio.run(test_fetch())
```
