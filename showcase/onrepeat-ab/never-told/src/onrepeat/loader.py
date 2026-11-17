"""Reading the Spotify and Apple Music exports.

Spotify's "Extended streaming history" download is a folder of JSON files
named like ``Streaming_History_Audio_2019-2021_0.json``. Each file is a list
of entries, one per time you played something.

Apple Music's data export has one CSV, ``Apple Music Play Activity.csv``, with
a row per play event.

We only keep the few fields we need and turn each entry into a small, tidy
``Play`` object. Both services end up as the same ``Play``.
"""

from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

APPLE_FILENAME = "Apple Music Play Activity.csv"


class ExportError(Exception):
    """Raised when we can't make sense of the files we were pointed at."""


@dataclass(frozen=True)
class Play:
    """One time you listened to something."""

    when: datetime  # when the play ended (Spotify stores this in UTC)
    ms_played: int  # how long you actually listened, in milliseconds
    track: str | None  # None for podcasts
    artist: str | None  # None for podcasts
    track_uri: str | None  # Spotify's id for the song; None for podcasts and Apple

    @property
    def is_music(self) -> bool:
        return self.track is not None and self.artist is not None


def find_history_files(path: Path) -> list[Path]:
    """Return the Spotify audio history files at ``path`` (a folder or a file)."""
    if path.is_file():
        return [path]
    # rglob so it still works if the zip was extracted into a subfolder
    # (Spotify's zip contains a "Spotify Extended Streaming History" folder).
    # Only *Audio* files: the Video files have a different shape.
    return sorted(path.rglob("Streaming_History_Audio_*.json"))


def find_apple_files(path: Path) -> list[Path]:
    """Return the Apple Music play activity CSVs at ``path`` (a folder or a file)."""
    if path.is_file():
        return [path]
    return sorted(path.rglob(APPLE_FILENAME))


def parse_entry(entry: dict) -> Play:
    """Turn one raw Spotify JSON entry into a Play."""
    return Play(
        # Spotify writes times like "2023-05-01T12:34:56Z". Python < 3.11 can't
        # read the trailing "Z", so we swap it for an explicit UTC offset.
        when=datetime.fromisoformat(entry["ts"].replace("Z", "+00:00")),
        ms_played=int(entry.get("ms_played") or 0),
        track=entry.get("master_metadata_track_name"),
        artist=entry.get("master_metadata_album_artist_name"),
        track_uri=entry.get("spotify_track_uri"),
    )


def _parse_apple_time(text: str) -> datetime:
    """Read Apple's "2026-07-02T08:14:03.120Z" (fraction is sometimes missing)."""
    # Python < 3.11 only accepts 3 or 6 fraction digits, so pad to 6.
    text = re.sub(
        r"\.(\d+)", lambda m: "." + m.group(1)[:6].ljust(6, "0"), text.strip()
    )
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def parse_apple_row(row: dict) -> Play | None:
    """Turn one Apple Music CSV row into a Play (None if it isn't a usable play)."""
    track = (row.get("Song Name") or "").strip()
    artist = (row.get("Artist Name") or "").strip()
    start = (row.get("Event Start Timestamp") or "").strip()
    if not (track and artist and start):
        return None
    try:
        ms = max(int(row.get("Play Duration Milliseconds") or 0), 0)
    except ValueError:
        ms = 0
    # Apple stamps the *start* of a play, Spotify the *end*. Use the end so a
    # play that crosses midnight on New Year's Eve lands in the same year on both.
    return Play(
        when=_parse_apple_time(start) + timedelta(milliseconds=ms),
        ms_played=ms,
        track=track,
        artist=artist,
        track_uri=None,
    )


def _load_spotify(file: Path) -> list[Play]:
    try:
        entries = json.loads(file.read_text(encoding="utf-8"))
        return [parse_entry(e) for e in entries]
    except (json.JSONDecodeError, KeyError, ValueError, TypeError) as err:
        raise ExportError(
            f"{file.name} doesn't look like Spotify history: {err!r}"
        ) from err


def _load_apple(file: Path) -> list[Play]:
    try:
        # utf-8-sig: Apple's CSVs may start with a byte-order mark.
        with file.open(encoding="utf-8-sig", newline="") as f:
            rows = csv.DictReader(f)
            plays = [p for p in map(parse_apple_row, rows) if p is not None]
            if rows.fieldnames is None or "Song Name" not in rows.fieldnames:
                raise ValueError("no 'Song Name' column")
            return plays
    except (csv.Error, ValueError, UnicodeDecodeError) as err:
        raise ExportError(
            f"{file.name} doesn't look like Apple Music play activity: {err!r}"
        ) from err


def load_plays(*paths: Path) -> list[Play]:
    """Load every play from one or more folders (or files).

    Each path can hold a Spotify export, an Apple Music export, or both.
    A single file is read as Apple Music if it ends in ``.csv``, else Spotify.
    """
    plays: list[Play] = []
    for path in paths:
        if not path.exists():
            raise ExportError(f"Can't find {path}")
        if path.is_file():
            if path.suffix.lower() == ".csv":
                plays.extend(_load_apple(path))
            else:
                plays.extend(_load_spotify(path))
            continue
        spotify = find_history_files(path)
        apple = find_apple_files(path)
        if not spotify and not apple:
            raise ExportError(
                f"No Spotify (Streaming_History_Audio_*.json) or Apple Music "
                f"({APPLE_FILENAME}) files found in {path}. "
                "Point me at the folder you unzipped."
            )
        for file in spotify:
            plays.extend(_load_spotify(file))
        for file in apple:
            plays.extend(_load_apple(file))
    return plays
