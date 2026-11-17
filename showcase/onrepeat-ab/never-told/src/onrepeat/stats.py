"""Crunching the numbers: pick a year, then total things up."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from onrepeat._songkey import song_key
from onrepeat.loader import Play

# Spotify itself only counts a stream if you listened for 30+ seconds,
# so by default we ignore accidental taps and quick skips too.
DEFAULT_MIN_MS = 30_000


@dataclass(frozen=True)
class Ranked:
    name: str
    ms: int  # total time listened
    plays: int


@dataclass(frozen=True)
class YearSummary:
    year: int
    hours: float  # all listening (music + podcasts) in the year
    top_artists: list[Ranked]
    top_songs: list[Ranked]
    # Your #1 song for each month, January first. None = no music that month.
    monthly_top: list[Ranked | None]


def available_years(plays: list[Play]) -> list[int]:
    return sorted({p.when.year for p in plays})


def _rank(totals: Counter, counts: Counter, limit: int) -> list[Ranked]:
    # Counter.most_common sorts biggest-first. Ties keep first-seen order.
    return [Ranked(name, ms, counts[name]) for name, ms in totals.most_common(limit)]


def _top_songs(plays: list[Play], limit: int) -> list[Ranked]:
    # Group songs by song_key (written in Rust, see rust/lib.rs), not Spotify's
    # id, so remasters, "(feat. ...)" and curly-vs-straight apostrophes all
    # count as one song, on either service. "(Sped Up)" etc. stay separate.
    # Each song is labelled with whichever spelling you listened to most.
    song_ms: Counter[str] = Counter()
    song_plays: Counter[str] = Counter()
    label_ms: dict[str, Counter[str]] = {}
    for p in plays:
        if not p.is_music:
            continue
        key = song_key(p.track, p.artist)
        label_ms.setdefault(key, Counter())[f"{p.track} - {p.artist}"] += p.ms_played
        song_ms[key] += p.ms_played
        song_plays[key] += 1
    return [
        Ranked(label_ms[r.name].most_common(1)[0][0], r.ms, r.plays)
        for r in _rank(song_ms, song_plays, limit)
    ]


def summarize(
    plays: list[Play], year: int, limit: int = 10, min_ms: int = DEFAULT_MIN_MS
) -> YearSummary:
    in_year = [p for p in plays if p.when.year == year]
    counted = [p for p in in_year if p.ms_played >= min_ms]

    artist_ms: Counter[str] = Counter()
    artist_plays: Counter[str] = Counter()
    for p in counted:
        if p.is_music:
            artist_ms[p.artist] += p.ms_played
            artist_plays[p.artist] += 1

    monthly_top = []
    for month in range(1, 13):
        in_month = [p for p in counted if p.when.month == month]
        top = _top_songs(in_month, 1)
        monthly_top.append(top[0] if top else None)

    return YearSummary(
        year=year,
        hours=sum(p.ms_played for p in counted) / 3_600_000,
        top_artists=_rank(artist_ms, artist_plays, limit),
        top_songs=_top_songs(counted, limit),
        monthly_top=monthly_top,
    )
