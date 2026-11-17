import csv
from collections.abc import Iterator
from pathlib import Path

from onrepeat.loader import parse_timestamp
from onrepeat.models import Play

FILENAME = "Apple Music Play Activity.csv"


def parse_row(row: dict[str, str]) -> Play | None:
    """Turn one Apple Music CSV row into a Play, or None if it isn't usable.

    Only the song, artist, start time and duration columns are read. The IP
    address column is deliberately ignored.
    """
    track = (row.get("Song Name") or "").strip()
    artist = (row.get("Artist Name") or "").strip()
    ts = (row.get("Event Start Timestamp") or "").strip()
    if not track or not artist or not ts:
        return None
    try:
        played_at = parse_timestamp(ts)
    except ValueError:
        return None
    try:
        ms = int(float(row.get("Play Duration Milliseconds") or 0))
    except ValueError:
        ms = 0
    return Play(played_at=played_at, track=track, artist=artist, ms_played=max(ms, 0))


def find_apple_file(path: Path) -> Path:
    if path.is_file():
        return path
    found = sorted(path.rglob(FILENAME)) if path.is_dir() else []
    if not found:
        raise FileNotFoundError(f"No '{FILENAME}' found in {path}")
    return found[0]


def load_apple_plays(path: Path) -> Iterator[Play]:
    file = find_apple_file(path)
    # utf-8-sig: exports from Apple sometimes start with a BOM.
    with file.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            play = parse_row(row)
            if play is not None:
                yield play
