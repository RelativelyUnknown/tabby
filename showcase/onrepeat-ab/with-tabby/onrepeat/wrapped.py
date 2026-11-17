"""Print a Wrapped (top artists, top songs, hours listened) for one year.

Counts Spotify and Apple Music plays together; either one alone is fine.

Example: onrepeat 2024 data/
"""

import argparse
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from onrepeat import apple, spotify
from onrepeat._core import song_key as merged_key
from onrepeat.spotify import ExportError, Play

# Spotify counts a stream only after 30 seconds; shorter plays are skips.
MIN_STREAM_MS = 30_000
TOP_N = 5


@dataclass(frozen=True, slots=True)
class Wrapped:
    year: int
    hours: float
    top_artists: list[tuple[str, int]]
    top_songs: list[tuple[tuple[str, str], int]]


def song_key(play: Play) -> tuple[str, str]:
    """The one place that decides which plays are the same song (done in Rust)."""
    return merged_key(play.track, play.artist)


def _display(variants: Counter[tuple[str, str]]) -> tuple[str, str]:
    """The spelling to show for a merged song: most played, then shortest."""
    return min(variants, key=lambda v: (-variants[v], len(v[0]), v))


def top_songs(streams: list[Play]) -> list[tuple[tuple[str, str], int]]:
    counts: Counter[tuple[str, str]] = Counter()
    spellings: defaultdict[tuple[str, str], Counter[tuple[str, str]]] = defaultdict(
        Counter
    )
    for p in streams:
        key = song_key(p)
        counts[key] += 1
        spellings[key][(p.track, p.artist)] += 1
    return [(_display(spellings[k]), n) for k, n in counts.most_common(TOP_N)]


def load_plays(folder: Path) -> list[Play]:
    plays = spotify.load_plays(folder) + apple.load_plays(folder)
    if not plays:
        raise ExportError(
            "no Streaming_History_Audio_*.json or Apple Music Play Activity.csv "
            f"plays found in {folder}"
        )
    return plays


def build_wrapped(plays: list[Play], year: int) -> Wrapped | None:
    in_year = [p for p in plays if p.played_at.year == year]
    if not in_year:
        return None
    streams = [
        p for p in in_year if p.track and p.artist and p.ms_played >= MIN_STREAM_MS
    ]
    return Wrapped(
        year=year,
        hours=sum(p.ms_played for p in in_year) / 3_600_000,
        top_artists=Counter(p.artist for p in streams).most_common(TOP_N),
        top_songs=top_songs(streams),
    )


def render(w: Wrapped) -> str:
    lines = [
        f"Your {w.year} Wrapped",
        f"Hours listened: {w.hours:,.1f}",
        "",
        "Top artists",
    ]
    lines += [
        f"  {i}. {artist} ({n} plays)" for i, (artist, n) in enumerate(w.top_artists, 1)
    ]
    lines += ["", "Top songs"]
    lines += [
        f"  {i}. {track} - {artist} ({n} plays)"
        for i, ((track, artist), n) in enumerate(w.top_songs, 1)
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("year", type=int)
    parser.add_argument(
        "folder",
        type=Path,
        help="folder with Streaming_History_Audio_*.json and/or "
        "Apple Music Play Activity.csv",
    )
    parser.add_argument(
        "--card",
        type=Path,
        metavar="FILE.html",
        help="also write a shareable HTML card (top 5s and hours only) to this file",
    )
    args = parser.parse_args(argv)

    try:
        wrapped = build_wrapped(load_plays(args.folder), args.year)
    except ExportError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    if wrapped is None:
        print(f"error: no listening found for {args.year}", file=sys.stderr)
        return 1
    print(render(wrapped))
    if args.card:
        from onrepeat.card import render_card  # card imports Wrapped from here

        try:
            args.card.write_text(render_card(wrapped), encoding="utf-8")
        except OSError as e:
            print(f"error: cannot write card: {e}", file=sys.stderr)
            return 1
        print(f"\nCard written to {args.card}")
    return 0
