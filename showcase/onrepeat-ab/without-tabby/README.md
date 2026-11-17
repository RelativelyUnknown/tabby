# onrepeat

Spotify Wrapped, whenever you want. Reads your Spotify **Extended streaming history**
export and shows top artists, top songs, hours listened and your #1 song of every month for a year you pick.

## Get your data
Spotify → Account → Privacy → "Download your data" → tick **Extended streaming history**.
It takes up to ~30 days to arrive. Unzip it somewhere.

For Apple Music: privacy.apple.com → "Request a copy of your data" → Apple Media Services
information. You want `Apple Music Play Activity.csv`.

## Use
```
uv run onrepeat "path/to/Spotify Extended Streaming History" --year 2024
uv run onrepeat --apple "Apple Music Play Activity.csv"
uv run onrepeat "path/to/Spotify..." --apple "Apple Music Play Activity.csv"   # both combined
```
Leave out `--year` to use the latest year. `--top 10` changes list length.

## Dev
Song merging is written in Rust (`rust/`) and compiled into the Python package by maturin
(needs a Rust toolchain: https://rustup.rs). `uv run` rebuilds it automatically when `rust/` changes.
```
cargo test          # the matching rules, pure Rust
```

```
uv run pytest
uv run ruff check . && uv run ruff format .
```

## Share it
```
uv run onrepeat "path/to/Spotify..." --year 2024 --share my-wrapped.html
```
Writes one self-contained HTML card (no internet needed). Send the file, host it anywhere,
or open it and screenshot. The Share button opens your phone's share sheet. It also prints a
plain-text version for pasting into chats. The card includes the month-by-month list too. Only the summary is included, not your raw history.
