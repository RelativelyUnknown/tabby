from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass

from onrepeat import _songmatch  # compiled from rust/ (see Cargo.toml)
from onrepeat.models import Play

# Spotify itself only counts a stream once you've listened for 30 seconds,
# so a song you skipped after 5s shouldn't count as a "play" in your top songs.
MIN_PLAY_MS = 30_000


@dataclass(frozen=True)
class Wrapped:
    year: int
    hours_listened: float
    top_artists: list[tuple[str, int]]  # (artist, plays)
    top_songs: list[tuple[str, str, int]]  # (artist, track, plays)


def plays_in_year(plays: Iterable[Play], year: int) -> list[Play]:
    # Spotify timestamps are UTC, so "year" means the UTC year. A listen at
    # 11:30pm on Dec 31st in your timezone might land in the next year.
    return [p for p in plays if p.played_at.year == year]


def build_wrapped(plays: Iterable[Play], year: int, top_n: int = 5) -> Wrapped:
    year_plays = plays_in_year(plays, year)

    # Hours counts every millisecond you actually had the music on.
    total_ms = sum(p.ms_played for p in year_plays)

    # Top lists only count "real" plays (30s+).
    real = [p for p in year_plays if p.ms_played >= MIN_PLAY_MS]
    artists = Counter(p.artist for p in real)
    # Song merging is done in Rust: "Blinding Lights" and "Blinding Lights -
    # Remastered 2020" (or the Spotify and Apple spellings of one song) count as
    # one, but "Espresso (sped up)" stays separate. See rust/canon.rs.
    songs = _songmatch.top_songs([(p.artist, p.track) for p in real], top_n)

    return Wrapped(
        year=year,
        hours_listened=total_ms / 3_600_000,
        top_artists=artists.most_common(top_n),
        top_songs=songs,
    )


def available_years(plays: Iterable[Play]) -> list[int]:
    return sorted({p.played_at.year for p in plays})
