# Native extensions: Python with Rust, C or C++

A library whose hot or low-level part is written in Rust, C, C++ or (rarely) Zig and called from Python. Everything for a pure-Python library (`../shared/`) still applies.

- native-extension-architecture.md: whether to go native, which layer, the layout, the seam, how the two sides are tested.
- native-rust.md: PyO3 and maturin: errors, the GIL, ownership, stubs, lints, `unsafe`.
- native-c.md: the CPython C API: reference counts, errors, init, threads, the stable ABI, sanitizers.
- native-porting-a-function.md: moving a Python function to Rust, C++, C or Zig: the behaviour list, tests first, differences in arithmetic, rounding and ordering.
- native-cpp.md: C++ with nanobind or pybind11: ownership and return policies, exceptions, the GIL, stubs, the stable ABI.
- native-zig.md: Ziggy Pydust, when the project already uses Zig or wants its comptime model; prefer Rust for new native code.
- native-smells.md: native boundary mistakes in Rust, PyO3, the C API and C++ bindings. Read before finishing a native change.
- native-ci-wheels.md: build backends, wheels, CI jobs, release checks.

Formatters and linters (the project's own config wins):

- Python: `ruff check` and `ruff format`, a type checker.
- Rust: `cargo fmt --check`, `cargo clippy --all-targets -- -D warnings`, `cargo test`; lints configured in `Cargo.toml` `[lints]`, never `#![deny(warnings)]` in source.
- C and C++: `clang-format` with the project's `.clang-format`, `-Wall -Wextra -Werror` in CI, `clang-tidy` if configured.
- Zig: `zig fmt --check`, `zig build test`.

Reviewing a native change: the `tabby-review` skill has a boundary checklist (`native-boundary.md`).
