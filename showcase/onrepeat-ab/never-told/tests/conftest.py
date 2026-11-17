import json

import pytest


def entry(ts, ms, track="Song A", artist="Artist A", uri=None):
    """Build one fake Spotify entry. track=None makes it a podcast."""
    return {
        "ts": ts,
        "ms_played": ms,
        "master_metadata_track_name": track,
        "master_metadata_album_artist_name": artist if track else None,
        "spotify_track_uri": (uri or f"spotify:track:{track}") if track else None,
        "episode_name": None if track else "Some Episode",
    }


@pytest.fixture
def make_export(tmp_path):
    """Write entries to a fake export folder and return the folder path."""

    def _make(entries, name="Streaming_History_Audio_2023_0.json"):
        (tmp_path / name).write_text(json.dumps(entries))
        return tmp_path

    return _make


APPLE_HEADER = (
    "Song Name,Album Name,Artist Name,Event Start Timestamp,"
    "Play Duration Milliseconds,End Reason Type,Client IP Address"
)


@pytest.fixture
def make_apple(tmp_path):
    """Write rows (song, artist, start, ms) to a fake Apple Music CSV; return folder."""
    import csv

    def _make(rows, folder=None):
        folder = folder or tmp_path
        with (folder / "Apple Music Play Activity.csv").open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(APPLE_HEADER.split(","))
            for song, artist, start, ms in rows:
                w.writerow(
                    [
                        song,
                        "Album",
                        artist,
                        start,
                        ms,
                        "NATURAL_END_OF_TRACK",
                        "1.2.3.4",
                    ]
                )
        return folder

    return _make
