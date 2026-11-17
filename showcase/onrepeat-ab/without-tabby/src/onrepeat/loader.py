import json
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path

from onrepeat.models import Play


def parse_timestamp(ts: str) -> datetime:
    # Spotify writes "2023-05-01T18:22:10Z". Older Pythons choke on the "Z",
    # so we swap it for an explicit UTC offset.
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def parse_entry(entry: dict) -> Play | None:
    """Turn one raw Spotify record into a Play, or None if it isn't a song.

    Podcast episodes have no track name, and a few rows are missing the artist,
    so we skip anything we can't describe as "artist - track".
    """
    track = entry.get("master_metadata_track_name")
    artist = entry.get("master_metadata_album_artist_name")
    if not track or not artist:
        return None
    return Play(
        played_at=parse_timestamp(entry["ts"]),
        track=track,
        artist=artist,
        ms_played=entry.get("ms_played", 0),
    )


def find_history_files(path: Path) -> list[Path]:
    """Accept either a single .json file or the folder you unzipped."""
    if path.is_file():
        return [path]
    # Only the audio files. There are also Streaming_History_Video_*.json files
    # (music videos / podcasts video) with a different shape.
    return sorted(path.rglob("Streaming_History_Audio_*.json"))


def load_plays(path: Path) -> Iterator[Play]:
    files = find_history_files(path)
    if not files:
        raise FileNotFoundError(
            f"No Streaming_History_Audio_*.json files found in {path}"
        )
    for file in files:
        with file.open(encoding="utf-8") as f:
            for entry in json.load(f):
                play = parse_entry(entry)
                if play is not None:
                    yield play
