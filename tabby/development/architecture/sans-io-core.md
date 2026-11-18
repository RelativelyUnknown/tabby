# Sans-I/O: put the logic where nothing can fail on the network

A protocol, parser, state machine or retry policy written as a function from *values in* to *values out* needs no socket, clock, file or thread to test, and runs unchanged under sync code, async code and a test. A thin shell does the I/O and feeds bytes, events and timestamps in. This is the pure-core split from [proof-based-testing.md](../testing/proof-based-testing.md), made into a design.

Use it for code that parses a wire or file format, speaks a protocol, schedules work, decides when to retry, or keeps a state machine. Skip it for a one-call script: a function that reads a file and prints a line gains nothing.

## Shape

```python
class Machine:                      # the core: no I/O, no clock, no sleep
    def feed(self, data: bytes) -> list[Event]: ...       # input in, events out
    def next_deadline(self, now: float) -> float | None: ...   # time passed in
    def pending(self) -> bytes: ...                       # bytes to send

def run(sock, machine):             # the shell: ~20 lines, one integration test
    while True:
        for ev in machine.feed(sock.recv(4096)): handle(ev)
        sock.sendall(machine.pending())
```

An async shell and a sync shell can drive the same `Machine`. Examples in the wild: `h11` (HTTP/1), `wsproto`, `hyperframe` and `h2`; the common thread is that their tests are tables of bytes in and events out.

## Rules

- The core takes the clock as a value (`now`), randomness as a seed or an argument, and returns what to send or do. It does not import `socket`, `asyncio`, `time.sleep`, `open` or `requests`.
- Errors are values the core returns or exceptions it raises about the data; connection errors are the shell's.
- Test the core with tables and laws; give the shell one test against a real local socket or a recorded fixture. Mocking `socket` to test logic is the smell this removes ([test-mocking.md](../testing/test-mocking.md)).
- Do not split a core out of code that has no logic, only calls. Count the branches: under three, leave it together.

## Before finishing

Can the core's tests run with the network cable out and the clock frozen? If not, find the import or the call that says otherwise and pass it in.
