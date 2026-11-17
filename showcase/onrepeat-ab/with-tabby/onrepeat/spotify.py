"""Read a Spotify "Extended streaming history" export.

Only the four fields OnRepeat needs are kept. The export also holds IP
addresses; they are never read into a Play, so they cannot be printed.
"""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


class ExportError(Exception):
    """The export is missing or not in the expected shape."""


@dataclass(frozen=True, slots=True)
class Play:
    played_at: datetime
    ms_played: int
    track: str | None
    artist: str | None


def load_plays(folder: Path) -> list[Play]:
    """Plays from every Spotify history file in folder; none is fine."""
    files = sorted(folder.rglob("Streaming_History_Audio_*.json"))
    return [play for path in files for play in _read_file(path)]


def _read_file(path: Path) -> list[Play]:
    try:
        rows = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as e:
        raise ExportError(f"cannot read {path}: {type(e).__name__}") from e
    if not isinstance(rows, list):
        raise ExportError(f"{path}: expected a list of plays")
    try:
        return [
            Play(
                played_at=datetime.fromisoformat(row["ts"]),
                ms_played=int(row["ms_played"]),
                track=row.get("master_metadata_track_name"),
                artist=row.get("master_metadata_album_artist_name"),
            )
            for row in rows
        ]
    except (KeyError, TypeError, ValueError, AttributeError) as e:
        # Never echo the row: it contains an IP address.
        raise ExportError(
            f"{path}: a play has missing or odd fields ({type(e).__name__})"
        ) from e
