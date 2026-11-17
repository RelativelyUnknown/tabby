# onrepeat

Wrapped, whenever you want it. Reads your Spotify **extended streaming
history** and/or your **Apple Music** data export, and shows your top artists,
top songs, your #1 song of every month, and hours listened for any year, with both services counted together.

## Get your data
1. Go to Spotify > Account > Privacy settings > **Download your data**.
2. Tick **Extended streaming history** and request it (it takes days to arrive, not minutes).
3. Unzip the file you get by email.

### Apple Music (optional)
1. Go to privacy.apple.com > **Request a copy of your data** > tick **Apple Media Services information**.
2. Unzip what Apple sends. Inside is `Apple Music Play Activity.csv` (it may be in a nested zip).

## Use it
```
uv run onrepeat path/to/unzipped/folder            # latest year in your data
uv run onrepeat path/to/folder --year 2022 --top 20
uv run onrepeat spotify_folder apple_folder        # combine both services
uv run onrepeat folder --html my-wrapped.html   # shareable page for friends
uv run onrepeat --help
```

Give it as many folders or files as you like; each can hold Spotify files, the
Apple CSV, or both. The same song on both services is counted as one, and so are its remasters,
`(feat. ...)` variants and curly-vs-straight apostrophes. Edits like
`(Sped Up)`, `(Live)` or `(Remix)` stay separate songs.

Notes: plays under 30s are ignored (like Spotify does; change with `--min-seconds`).
Hours include podcasts, the top lists are music only. Years use UTC time. Apple only logs when a play
started, so we add the listening time to get when it ended (as Spotify does).

## Develop
The song-matching lives in Rust (`rust/lib.rs`) and is built into Python with
[maturin](https://www.maturin.rs); `uv run` builds it for you (needs `cargo`).
```
cargo test           # the Rust matching rules
uv run pytest        # tests
uv run ruff check .  # lint
uv run ruff format . # format
```
