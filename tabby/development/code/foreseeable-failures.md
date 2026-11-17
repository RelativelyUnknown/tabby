# Foreseeable failures: what real data does to your code

Code that touches data you did not make (a file from a bank or vendor, an API reply, user text, the clock, another operating system) meets inputs your sample never had. Before you finish such code, ask once: **what would a real one look like on a bad day?** Guard the likely failures now, test one, and mention the rest in a line. Do not add defensive checks on data your own code produced ([code-smells.md](code-smells.md)).

## When to guard now

Guard it when all four hold:

1. The data comes from outside the program.
2. This failure is known: it has happened to other people (the table below is a list of them).
3. The guard is one parameter or about three lines.
4. Without it the failure is a traceback the user cannot act on, or worse, a silently wrong result.

Otherwise name it in the final message ("an export in another encoding would stop it with a clear error") and move on. A guard that needs a design, a flag and a config file is a feature: ask first.

## The usual suspects

| Input | What goes wrong | Guard now | A package, when the guard is not enough |
| --- | --- | --- | --- |
| A text file from another system | `UnicodeDecodeError`; a BOM glued to the first column name (`﻿Datum`); mojibake (`cafÃ©`) | `open(path, encoding="utf-8-sig", newline="")`; catch `UnicodeDecodeError` and print one line naming the file and the encoding to try (`--encoding`); `errors="replace"` only for logs | `charset-normalizer` detects the encoding of files you do not control; `ftfy` repairs mojibake already in the text |
| CSV | `;` or tab for `,`; a quoted newline; short or long rows; header names with spaces; a missing column | `csv.DictReader`, `newline=""`, check the required columns up front and name the missing ones, `csv.Sniffer` only as a hint | `clevercsv` for messy dialects; `polars` or `pandas` when it no longer fits in memory |
| Numbers in a local format | `2.450,00` read as 2.45 or a crash; `float` drift | one `parse_amount` function, `Decimal`, a test with a thousands separator | `babel` (`parse_decimal`) for many locales |
| Money | `0.1 + 0.2`; rounding differs from the statement | `Decimal`, round once at the end, say the rounding mode | `py-moneyed` for currencies |
| Dates and times | naive datetimes; `03/04` is March or April; DST gaps; `20260903` | `datetime.strptime` with one explicit format, `datetime.now(UTC)`, `zoneinfo`; reject an ambiguous format instead of guessing | `python-dateutil` or `dateparser` for free-form text only |
| Text compared or used as a key | `é` as one or two code points; `Straße`; trailing spaces; case | `unicodedata.normalize("NFC", s).strip().casefold()` once, at the boundary | `python-slugify` for slugs; `regex` for Unicode-aware patterns |
| Keyword or substring tests on free text | `"rent"` also matches "current" | whole-word `re.search(r"\bword\b", text)` and a near-miss test | `rapidfuzz` only for fuzzy matching, not for exact rules |
| Empty or huge input | `max([])`; a header-only file prints nothing; 2 GB read at once | decide what empty gives and print it; read line by line or in chunks | `polars` or `duckdb` past memory |
| Paths and operating systems | `\` against `/`; `~`; spaces; Windows reserved names; case-insensitive disks | `pathlib`, `expanduser()`, never build paths with `+` | `platformdirs` for config, cache and data folders |
| Console output | `UnicodeEncodeError` printing `é` or `▲` on a Windows terminal | `sys.stdout.reconfigure(encoding="utf-8")` in the CLI entry point, or say `PYTHONUTF8=1` | `rich` if you want real terminal handling |
| HTTP replies | an HTML error page where JSON was promised; 429; redirects; no timeout | `timeout=`, `raise_for_status()`, check `Content-Type` before `.json()` | `tenacity` for retries with backoff ([retries-timeouts-circuit-breakers.md](../application/shared/retries-timeouts-circuit-breakers.md)) |
| JSON from outside | `NaN`; huge integers; the wrong shape | validate the shape at the boundary | `pydantic` for shapes; `orjson` for speed |
| Email, URL, phone | a regex that rejects real ones | `urllib.parse`, `email.utils.parseaddr` | `email-validator`, `phonenumbers` |
| A job that runs twice or stops halfway | a half-written file; double inserts | write a temp file and `os.replace`; make the write idempotent | `filelock` for one-at-a-time |
| Tests that depend on the clock or network | flaky on a different day | pass the clock in; no network in unit tests | `time-machine` or `freezegun` |

Add a row's guard only when its input applies to this code.

## When a package is the better answer

Tell the user, once, in one line, in the final message:

- **Name the problem it solves, what you did instead and where that stops.** "I handled UTF-8 with a BOM and print a clear error for anything else. If your exports come in other encodings, `charset-normalizer` detects them."
- **Take the guard first, the package second.** A one-line guard beats a dependency. Recommend the package when the guard would grow into a feature (detecting encodings, parsing many locales, repairing damaged text), or when the standard library cannot do it at all.
- **Follow the ladder** in [minimalism-reuse-names.md](minimalism-reuse-names.md): already installed, standard library, the community standard, then niche. Check [choosing-dependencies.md](../dependencies/choosing-dependencies.md) for health (maintained, a release in the last year, licence).
- **Never install silently.** If the project's `ask-first:` line covers dependencies, or `constraints:` says standard library only, recommend and wait. Otherwise recommend, and install only when the user says yes. Optional features go in an extra with a lazy import.

## What to report

One line naming each failure you guarded ("a BOM and a bad byte give a clear error, tested") and one line for each you only named. The user then knows what the code covers without reading it.
