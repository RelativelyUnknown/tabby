"""Time `uringread.read_files` against a plain loop and a 16-thread pool.

    python cmpbench.py DIR N SIZE_BYTES

Creates N random files of SIZE_BYTES in DIR on the first run and reuses them
after that, checks the library returns the same bytes as a plain loop, then
prints the median of 3 runs in milliseconds, cold cache first and warm second.
Cold needs permission to write /proc/sys/vm/drop_caches (root); without it the
cold line is skipped and says so. Delete DIR when you are done.
"""

import os
import pathlib
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import uringread


def loop(paths):
    out = []
    for path in paths:
        with open(path, "rb") as handle:
            out.append(handle.read())
    return out


def pool(paths):
    def read(path):
        with open(path, "rb") as handle:
            return handle.read()

    with ThreadPoolExecutor(16) as executor:
        return list(executor.map(read, paths))


def drop_caches():
    with open("/proc/sys/vm/drop_caches", "w") as handle:
        handle.write("3")


def median_ms(fn, paths, cold):
    times = []
    for _ in range(3):
        if cold:
            drop_caches()
        start = time.perf_counter()
        fn(paths)
        times.append(time.perf_counter() - start)
    return statistics.median(times) * 1000


def main():
    directory = pathlib.Path(sys.argv[1])
    count, size = int(sys.argv[2]), int(sys.argv[3])
    paths = [str(directory / f"f{i}") for i in range(count)]
    if not directory.exists():
        directory.mkdir(parents=True)
        for path in paths:
            with open(path, "wb") as handle:
                handle.write(os.urandom(size))
        os.sync()
    assert uringread.read_files(paths) == loop(paths), "library returned different bytes"
    for cold in (True, False):
        label = "cold" if cold else "warm"
        try:
            row = {
                "loop": median_ms(loop, paths, cold),
                "pool16": median_ms(pool, paths, cold),
                "uringread": median_ms(uringread.read_files, paths, cold),
            }
        except PermissionError:
            print(f"{label}: skipped (cannot write /proc/sys/vm/drop_caches)")
            continue
        print(label, "  ".join(f"{name} {ms:.0f}" for name, ms in row.items()), "ms")


if __name__ == "__main__":
    main()
