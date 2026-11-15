# Background jobs

Use the queue the project already has (Celery, RQ, Dramatiq, Arq, Taskiq, a cloud queue); do not add a second one, and do not add Celery for one job.

## Choose

- Work the user must not lose, that takes longer than a request, or that retries: a durable queue or a jobs table. Best-effort work that may vanish on a restart (a cache warm-up, a metrics ping): an in-process task (`BackgroundTasks`, `asyncio.create_task`).
- Low volume with a database already: a `jobs` table and a worker, claimed atomically (`UPDATE ... RETURNING`, or `SELECT ... FOR UPDATE SKIP LOCKED` on PostgreSQL). A runnable version is in background-jobs-and-queues.md (below).
- Time-based work: a scheduler that enqueues; the schedule is not the job.

## Rules

- Delivery is at least once, so a task must be safe to run twice. Give each logical job an idempotency key and make the effect an upsert, a check-then-skip, or a stored outcome. A queue that deduplicates by key narrows the window; it does not remove the need.
- Enqueue after the commit that makes the data visible, not inside the transaction: a fast worker can run before the row exists (`transaction.on_commit` in Django, or an outbox table written in the same transaction).
- Pass ids and small JSON values, not model instances or large payloads; the task reads current state when it runs.
- Retry only errors that can pass (timeouts, 5xx, deadlocks), with exponential backoff and jitter and a maximum number of attempts. A permanent error (bad input) fails at once. Jobs that run out of attempts go to a dead state that someone looks at, with the error kept.
- Set a time limit per task. A lease or visibility timeout must be longer than the longest run: with late acknowledgement, a task that outlives it is delivered to a second worker while the first still runs (Redis broker default: one hour).
- Celery acknowledges before running by default, so a started task never repeats and a worker crash loses it. `acks_late=True` repeats it after a crash, only safe for idempotent tasks; add `reject_on_worker_lost=True` so a killed child is redelivered. Retries: `autoretry_for=(...)`, `retry_backoff=True`, `retry_jitter=True`, `max_retries=n`. Long tasks: `worker_prefetch_multiplier = 1`. (Documentation, not run here.)
- A request that starts a job answers `202 Accepted` with a job id and a status URL. States: `pending`, `running`, `succeeded`, `failed` (and `dead` when attempts ran out). The status endpoint reports the state, the error summary and a link to the result.
- Log the job id, key and attempt on every line; watch queue depth, the age of the oldest job and the failure rate ([logging-metrics-tracing.md](../shared/logging-metrics-tracing.md)).
- Tests: call the task function directly for logic; run it eagerly (`task_always_eager` in Celery, a synchronous worker in RQ) for wiring; keep one test against the real broker for serialization and acknowledgement. Test the second delivery: run the task twice and assert one effect.

## Background job patterns

### A jobs table with an atomic claim, leases and backoff

Standard library only; the block runs as written (checked 9 November 2026). On PostgreSQL the claim is `SELECT ... FOR UPDATE SKIP LOCKED` inside one transaction. A job whose lease ran out is claimed again, which is the at-least-once guarantee: the handler must be idempotent.

```python
import random
import sqlite3
import tempfile
import threading
import time
from collections.abc import Callable
from pathlib import Path

MAX_ATTEMPTS = 3

SCHEMA = """
CREATE TABLE jobs (
    id INTEGER PRIMARY KEY,
    key TEXT UNIQUE NOT NULL,          -- idempotency key: one row per logical job
    payload TEXT NOT NULL,
    state TEXT NOT NULL DEFAULT 'pending',   -- pending, running, succeeded, dead
    attempts INTEGER NOT NULL DEFAULT 0,
    run_after REAL NOT NULL DEFAULT 0,
    lease_until REAL
)
"""

def connect(path: Path) -> sqlite3.Connection:
    db = sqlite3.connect(path, isolation_level=None, timeout=10)
    db.row_factory = sqlite3.Row
    return db

def enqueue(db: sqlite3.Connection, key: str, payload: str) -> None:
    db.execute("INSERT OR IGNORE INTO jobs (key, payload) VALUES (?, ?)", (key, payload))

def claim(db: sqlite3.Connection, now: float, lease: float = 30) -> sqlite3.Row | None:
    """Atomically take one due job. A job whose lease ran out is taken again (at-least-once)."""
    return db.execute(
        """
        UPDATE jobs SET state = 'running', attempts = attempts + 1, lease_until = ?
        WHERE id = (
            SELECT id FROM jobs
            WHERE (state = 'pending' AND run_after <= ?) OR (state = 'running' AND lease_until < ?)
            ORDER BY run_after, id LIMIT 1
        )
        RETURNING id, key, payload, attempts
        """,
        (now + lease, now, now),
    ).fetchone()

def finish(db: sqlite3.Connection, job: sqlite3.Row, now: float, error: Exception | None) -> None:
    if error is None:
        db.execute("UPDATE jobs SET state = 'succeeded' WHERE id = ?", (job["id"],))
    elif job["attempts"] >= MAX_ATTEMPTS:
        db.execute("UPDATE jobs SET state = 'dead' WHERE id = ?", (job["id"],))  # dead-letter: look at it by hand
    else:
        delay = min(60.0, 0.01 * 2 ** job["attempts"]) * random.uniform(0.5, 1.5)  # backoff with jitter
        db.execute("UPDATE jobs SET state = 'pending', run_after = ? WHERE id = ?", (now + delay, job["id"]))

def work(path: Path, handler: Callable[[str, str], None], stop: threading.Event) -> None:
    db = connect(path)
    while not stop.is_set():
        job = claim(db, time.time())
        if job is None:
            time.sleep(0.005)
            continue
        try:
            handler(job["key"], job["payload"])
        except Exception as error:  # noqa: BLE001 - any failure is a retry or a dead job
            finish(db, job, time.time(), error)
        else:
            finish(db, job, time.time(), None)

with tempfile.TemporaryDirectory() as tmp:
    db = connect(Path(tmp, "jobs.db"))
    db.execute(SCHEMA)
    enqueue(db, "crashy", "x")
    enqueue(db, "crashy", "again")  # same key: ignored
    assert db.execute("SELECT count(*) FROM jobs").fetchone()[0] == 1
    # A worker that dies keeps its lease until it runs out; then the job is taken again.
    first = claim(db, now=1000.0, lease=5)
    assert first is not None and first["attempts"] == 1
    assert claim(db, now=1002.0) is None  # lease still valid
    again = claim(db, now=1006.0)
    assert again is not None and again["attempts"] == 2
    for _ in range(MAX_ATTEMPTS):  # failures back off, then dead-letter
        job = claim(db, now=2000.0)
        if job:
            finish(db, job, 2000.0, RuntimeError("boom"))
    print("ok")
```

### Enqueue after commit

From the Django documentation (not run here): `transaction.on_commit(lambda: send_receipt.delay(order.pk))` runs the callback only after the surrounding transaction commits, and not at all if it rolls back. Without Django, write the job row in the same transaction as the data (an outbox table) and let a worker or relay pick it up.
