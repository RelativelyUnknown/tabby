---
type: llm
focus: trace
weight: 3
---

PASS if `load_rows` now copes with a UTF-8 file that starts with a BOM (first column name has no `﻿`) and with a file in another single-byte encoding such as cp1252, or fails with one clear message naming the file and the encoding to try, and the trace shows this was run or tested. FAIL if a UnicodeDecodeError traceback is still the outcome for such a file.
