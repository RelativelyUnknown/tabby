# Without Tabby, never told the plans: the whole conversation

The control run: Claude Code (`claude -p`, Sonnet 5.5) with no plugin, and the first message says nothing about Apple Music, Rust or a card. Each later feature arrives as a surprise. Agent replies are the final message of each turn, unedited.

## Step 1: v1, Spotify (no future plans mentioned)

**Me:**

> yo ok so i'm kinda new to coding (python for like 6 months, school + yt). i wanna build a thing called onrepeat: basically spotify wrapped but whenever i want, not just december. it reads my spotify data export (the extended streaming history json files) and shows my top artists, top songs and hours listened, for a year i pick.
>
> can u build it? uv + pytest + ruff pls. explain a lil as u go

**Agent** *(tools: Bash 6; $0.20)*:

I built onrepeat. It reads your Spotify extended streaming history folder and prints top artists, top songs and hours listened for a year you pick. The 18 pytest tests pass and `ruff check` is clean. I ran the CLI end to end, but only on fake data, so I haven't seen it on a real export. It's committed as one commit.

## How to use it
```
uv run onrepeat path/to/unzipped/spotify/folder
uv run onrepeat path/to/folder --year 2022 --top 20
```
With no `--year`, it uses the most recent year in your data. If you ask for a year you have no plays in, it lists the years you do have.

## How it's laid out
The code is split into three small files under `src/onrepeat/`, so each does one job:
- **`loader.py`** finds the `Streaming_History_Audio_*.json` files, even inside a subfolder. It turns each JSON entry into a small `Play` object. A `@dataclass` is just a class that's mostly data, so it needs very little code. Bad paths or files give a readable error instead of a traceback.
- **`stats.py`** is where the counting happens. It uses `collections.Counter`, which is a dict that adds things up, and `.most_common()` gives you a ranking.
- **`cli.py`** reads the arguments with `argparse` and prints the result.

The tests build fake exports in a temp folder (that's the `make_export` fixture in `tests/conftest.py`), so your real data is never involved.

## Choices I made (easy to change)
- **Ranking is by time listened, not play count.** I think that's closer to what Wrapped does. Play counts still show next to each row.
- **Plays under 30 seconds are ignored**, since Spotify doesn't count those as streams either. `--min-seconds` changes it.
- **Podcasts count toward hours but aren't in the top lists.**
- **Songs are matched by Spotify's track ID, not by title.** Two different songs both called "Intro" stay separate.
- **Years use UTC**, which is how Spotify stores timestamps. A play at 11pm on Dec 31 in your timezone might land in the next year.

## Things to know
- I wrote this from my memory of the export format and tested it on fake data. If your real export has a surprise, send me the error. Don't paste the data itself.
- The `.gitignore` blocks `Streaming_History*.json`, so your listening data can't get committed by accident.
- I didn't add `--year all` or a nicer visual output. Those would be good next steps, for example a `rich` table or a small HTML page.

## Step 2: Apple Music (new session, a surprise)

**Me:**

> yooo i got my apple music data export!! there's a file called "Apple Music Play Activity.csv". can u add it so my wrapped counts spotify AND apple music together? here's the top of the file:
>
> Song Name,Album Name,Artist Name,Event Start Timestamp,Play Duration Milliseconds,End Reason Type,Client IP Address
> "Good Luck, Babe!",Good Luck Babe!,Chappell Roan,2026-07-02T08:14:03.120Z,215000,NATURAL_END_OF_TRACK,203.0.113.7
> Espresso,Espresso,Sabrina Carpenter,2026-07-02T08:17:40Z,12000,TRACK_SKIPPED_FORWARDS,203.0.113.7

**Agent** *(tools: Bash 6; $0.21)*:

Your wrapped now counts Spotify and Apple Music together. I haven't run it on your real CSV, because it isn't in this repo. I tested with the two rows you pasted, plus new tests (27 pass, lint clean). In that run the 12-second Espresso skip was dropped and "Good Luck, Babe!" counted. The comma in the title parsed correctly.

To use it, point `onrepeat` at one or more folders or files. Each can hold Spotify files, the Apple CSV, or both:
```
uv run onrepeat path/to/spotify path/to/apple
uv run onrepeat path/to/apple/"Apple Music Play Activity.csv" --year 2026
```

**Behaviour changes**
- **Same song on both services counts once.** Apple has no track IDs, so songs are now matched on title and artist, ignoring case. The same title by a different artist stays separate. This also means Spotify songs with different track IDs but the same title and artist (say, a single and its album version) now merge. Tell me if you'd rather keep those apart.
- **Year is based on when a play ended.** Apple logs the start time and Spotify logs the end time, so I add the listening time to the Apple start. A play that crosses midnight on New Year's Eve lands in the same year on both services.
- **Rows I skip or zero.**
  - Apple rows with no song, artist or timestamp are skipped.
  - Blank or negative durations count as 0.
  - Under-30s plays are still dropped, which covers your Espresso skip.
- **Better error messages.** An empty folder now says it found neither Spotify nor Apple files, and a malformed CSV gets its own message.

**Privacy:** the Apple CSV has your IP address in every row. The code never reads or prints that column. I also added `Apple Music*` and `*.csv` to `.gitignore` so the file can't be committed by accident.

I updated the README with the Apple data request steps, which I wrote from memory: privacy.apple.com, then "Apple Media Services information". Check them against what you actually did. The changes are in the working tree and not committed.

## Step 3: merge songs in Rust (new session, a surprise)

**Me:**

> ok now the dream feature 🦀 merge the same song across versions and services, and do it in rust bc i wanna learn rust. like these should all be one song in my top 5:
> - "Blinding Lights" and "Blinding Lights - Remastered 2020"
> - "Die With A Smile" on apple and "Die With A Smile (feat. Bruno Mars)" on spotify
> - "Don’t Stop Me Now" vs "Don't Stop Me Now" (curly apostrophe, apple does that)
> but "Espresso (sped up)" is NOT the same as "Espresso", sped up is its own song lol
> go!

**Agent** *(tools: Bash 10, Write 1; $0.38)*:

Songs now merge across versions and services, and the matching is written in Rust. All your examples behave as you described, and I ran them end to end through `uv run onrepeat` on fake Spotify and Apple data. The 11 Rust tests and the 30 Python tests pass, and `ruff` and `clippy` are clean.

I haven't committed anything. The tree already had uncommitted changes from before, which I left alone.

## How it works
- **Rust:** `rust/lib.rs` has `song_key(title, artist)`, which returns a key like `"dont stop me now|queen"`. Two listings are the same song when their keys are equal. `rust/py.rs` is a 10-line PyO3 wrapper.
- **Build:** `pyproject.toml` now builds with maturin instead of `uv_build`, and `uv run` compiles the Rust for you. `cargo test` runs the Rust tests without Python.
- **Python:** `stats.py` groups plays by that key. A merged song is labelled with the spelling you listened to most.

## What counts as the same song
| Case | Result |
|---|---|
| `Blinding Lights - Remastered 2020`, `(Remastered)`, `- 2011 Remaster` | same song |
| `(feat. Bruno Mars)`, `[with …]`, `- feat. …`, or the guest in the artist field | same song |
| `Don’t` vs `Don't`, case, accents, `&` vs `and` | same song |
| `Espresso (sped up)`, `(Live)`, `(Remix)`, `(Acoustic)`, `(Slowed + Reverb)` | separate songs |

I made the rule a list of known boilerplate to strip: remaster, feat/with, deluxe, mono/stereo, single/album/radio version, anniversary edition, bonus track and explicit/clean. Any bracket not on that list stays in the key. That way an unfamiliar tag like "sped up" is kept rather than merged. The cost is that an unfamiliar boilerplate tag will leave two copies of a song apart. If you see that, add it to the `NOISE` regex.

The artist side keeps only the first credited artist. That's why `Lady Gaga & Bruno Mars` matches `Lady Gaga`. It also means `Simon & Garfunkel` and `Simon` would merge, which I accepted as rare. `Tyler, The Creator` is special-cased so it isn't split.

## Things to know
- **Top artists is unchanged and still splits.** In my test run the top artists list showed `Lady Gaga` and `Lady Gaga & Bruno Mars` as separate artists. You asked about songs, so I left it. The same primary-artist rule would fix it, but then Bruno Mars gets no credit on duets. Say if you want it.
- **Labels:** the label is the most-listened spelling, so it can read `Blinding Lights - Remastered 2020` if that's the one you played most. I could pick the cleanest spelling instead.
- **A bug the tests caught:** Japanese が was being merged with か. Accent stripping split it into a base letter plus a mark, and my punctuation cleanup then threw the mark away. Recomposing the characters at the end of `fold` fixed it.

If you're reading the Rust to learn: `normalize_title` and `strip_noise` in `rust/lib.rs` are the best places to start.

## Step 4: a vague request (new session)

**Me:**

> yo my friends wanna see my wrapped 👀 make it shareable

**Agent** *(tools: Bash 6; $0.12)*:

Wrapping up: the share feature is done and the lint and tests pass.

I added a `--html` flag to onrepeat that saves your wrapped as one self-contained page. It's a phone-friendly card with your hours, top artists and top songs. You can send the file to friends or host it anywhere.

```
uv run onrepeat path/to/your/data --html my-wrapped.html
```

- **Escaping:** Song and artist names are HTML-escaped, and a test covers that.
- **Checks:** All 31 tests pass and `ruff` is clean. The code is in `src/onrepeat/share.py`, wired up in `cli.py`, and the README mentions the flag.
- **Not run on real data:** I haven't generated a page from real listening history, because your Spotify or Apple export isn't in this environment. I'd run it once on your data and check how the card looks before sending it.
- **Not published or committed:** I haven't published it anywhere or committed the changes. The page contains your full listening history, so I didn't want to put it online without you asking. If you'd like a private link, I can publish it as an artifact once you've generated it.

## Step 5: an unplanned feature (new session)

**Me:**

> new idea!! can u add a month by month thing? like my #1 song for every month of the year. it should show in the terminal AND on the share card

**Agent** *(tools: Bash 7; $0.16)*:

Your #1 song for each month now shows up in the terminal and on the share card. All 33 tests pass and lint is clean. I checked the terminal output by running it on sample data, but I haven't looked at the share card in a browser.

**What it looks like**
- **Terminal:** a new "Song of each month" section after Top songs. It has 12 lines, Jan to Dec, each with the song and its play count.
- **Share card:** the same 12 months as a list under Top songs, with the month in green on the left, in the same style as the rest of the card.
- **Empty months:** a month with no music shows `-` instead of being skipped.

**How the #1 is picked**
- **Same rules as the yearly list:** the top song for a month uses the same ranking as Top songs, so remasters, "(feat. …)" versions and Spotify plus Apple plays count as one song. It's the most time listened, with the same 30-second minimum.
- **Months use UTC:** this matches how the years are counted.

**Where the changes are**
- **`stats.py`:** a new `monthly_top` field on the yearly summary. I moved the song-grouping code into one helper so the year and each month share it.
- **`cli.py` and `share.py`:** the new section in the terminal output and on the card.
- **Tests and README:** one test for the month picking, one for terminal plus HTML output, and the README mentions the feature.

The card is now noticeably longer, since it gains 12 lines. If you'd rather have a compact two-column grid so it stays closer to phone-screenshot size, I can switch it.
