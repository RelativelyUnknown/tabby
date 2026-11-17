# OnRepeat

Prints a "Wrapped" (top 5 artists, top 5 songs, hours listened) for any year, from your own Spotify and/or Apple Music data export.

1. Request your **Extended streaming history** at spotify.com/account/privacy and unzip it into `data/` (git ignores this folder; the export contains IP addresses).
2. From privacy.apple.com request **Apple Music activity**, and put `Apple Music Play Activity.csv` anywhere inside `data/`. It is added to your Spotify plays.
3. Run:

   ```
   uv run onrepeat 2024 data/
   ```

   To type just `onrepeat 2024 data/` from anywhere, install it once with `uv tool install .` (make sure uv's tool folder is on your PATH: `uv tool update-shell`).

4. To share it, add `--card`: `uv run onrepeat 2024 data/ --card wrapped-2024.html` writes one self-contained HTML file (year, hours, top 5 artists and songs; nothing else from your export). Send the file or screenshot it. `wrapped-*.html` is git-ignored.

Notes:

- Spotify and Apple Music are each optional, but you need at least one. Apple Music rows without a time or duration are ignored.
- Songs and artists are ranked by plays of 30 seconds or more (shorter plays are skips). Hours count everything, podcasts included.
- The same song is counted once across versions and services: remaster and "feat." tags are ignored, the first artist decides, and curly/straight apostrophes match. Other tags ("sped up", "live", "remix") make a different song. Only a tag made of "remaster", a year and "version" is ignored, so "Live at Wembley 2011 Remaster" stays a different song. The first artist is cut at `,` `&` `;`, so "Earth, Wind & Fire" counts as "Earth" (only a problem if two such artists share a song title). The song shown is the spelling you played most. Top artists are not merged yet. The logic is Rust in `src/merge.rs`, so you need `cargo` (rustup.rs); after editing it, run `uv run --reinstall-package onrepeat pytest`.
- The year is taken from the UTC timestamp, so a play near midnight on 31 Dec can land in the neighbouring year.

Check: `uv run ruff check && uv run pytest`, and for the Rust: `cargo fmt --check && cargo clippy --all-targets -- -D warnings && cargo test`
