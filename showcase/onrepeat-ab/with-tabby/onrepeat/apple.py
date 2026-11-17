"""Read an Apple Music "Play Activity" export.

Only the four fields OnRepeat needs are kept. The export also holds IP
addresses; they are never read into a Play, so they cannot be printed.
"""

import csv
from datetime import datetime
from pathlib import Path

from onrepeat.spotify import ExportError, Play

FILE_NAME = "Apple Music Play Activity.csv"


def load_plays(folder: Path) -> list[Play]:
    """Plays from every Apple Music Play Activity file in folder; none is fine."""
    return [
        play for path in sorted(folder.rglob(FILE_NAME)) for play in _read_file(path)
    ]


def _read_file(path: Path) -> list[Play]:
    try:
        with path.open(encoding="utf-8-sig", newline="") as f:
            return [
                play for row in csv.DictReader(f) if (play := _to_play(row)) is not None
            ]
    except (OSError, UnicodeDecodeError, csv.Error) as e:
        raise ExportError(f"cannot read {path}: {type(e).__name__}") from e
    except (KeyError, TypeError, ValueError) as e:
        # Never echo the row: it contains an IP address.
        raise ExportError(
            f"{path}: a play has missing or odd fields ({type(e).__name__})"
        ) from e


def _to_play(row: dict[str, str]) -> Play | None:
    # Some rows (e.g. library events) have no time or duration: nothing to count.
    if not row["Event Start Timestamp"] or not row["Play Duration Milliseconds"]:
        return None
    return Play(
        played_at=datetime.fromisoformat(row["Event Start Timestamp"]),
        ms_played=int(row["Play Duration Milliseconds"]),
        track=row["Song Name"] or None,
        artist=row["Artist Name"] or None,
    )
