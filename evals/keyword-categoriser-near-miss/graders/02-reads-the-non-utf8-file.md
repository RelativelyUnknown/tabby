---
type: llm
focus: trace
weight: 3
---

PASS if the script ran to completion on `export.csv`, which has a non-UTF-8 byte (`\xe9`), without a UnicodeDecodeError traceback reaching the user: it opens the file with an encoding that fits (cp1252 or latin-1), uses `errors="replace"`, or fails with one clear line that names the encoding to try. FAIL if the final run crashed with a traceback.
