import json

import pytest
from conftest import entry

from onrepeat.loader import ExportError, load_plays, parse_apple_row, parse_entry


def test_parse_music_entry():
    play = parse_entry(entry("2023-05-01T12:00:00Z", 180_000))
    assert play.when.year == 2023
    assert play.ms_played == 180_000
    assert play.track == "Song A"
    assert play.is_music


def test_podcast_is_not_music():
    assert not parse_entry(entry("2023-05-01T12:00:00Z", 1000, track=None)).is_music


def test_load_reads_every_audio_file_and_ignores_video(make_export, tmp_path):
    make_export(
        [entry("2022-01-01T00:00:00Z", 60_000)], "Streaming_History_Audio_2022_0.json"
    )
    make_export(
        [entry("2023-01-01T00:00:00Z", 60_000)], "Streaming_History_Audio_2023_1.json"
    )
    (tmp_path / "Streaming_History_Video_2023.json").write_text('[{"nope": 1}]')
    assert len(load_plays(tmp_path)) == 2


def test_finds_files_in_subfolder(tmp_path):
    sub = tmp_path / "Spotify Extended Streaming History"
    sub.mkdir()
    (sub / "Streaming_History_Audio_2023_0.json").write_text(
        json.dumps([entry("2023-01-01T00:00:00Z", 60_000)])
    )
    assert len(load_plays(tmp_path)) == 1


def test_missing_folder_gives_friendly_error(tmp_path):
    with pytest.raises(ExportError):
        load_plays(tmp_path / "nope")


def test_empty_folder_gives_friendly_error(tmp_path):
    with pytest.raises(ExportError, match="No Spotify"):
        load_plays(tmp_path)


def test_garbage_file_gives_friendly_error(tmp_path):
    (tmp_path / "Streaming_History_Audio_2023_0.json").write_text("not json")
    with pytest.raises(ExportError):
        load_plays(tmp_path)


def test_apple_row_uses_end_time_and_handles_commas_and_fraction():
    row = {
        "Song Name": "Good Luck, Babe!",
        "Artist Name": "Chappell Roan",
        "Event Start Timestamp": "2026-12-31T23:59:30.120Z",
        "Play Duration Milliseconds": "215000",
    }
    play = parse_apple_row(row)
    assert play.track == "Good Luck, Babe!"
    assert play.ms_played == 215_000
    assert play.when.year == 2027  # the play ended after midnight, like Spotify's ts


def test_apple_row_without_time_or_song_is_skipped():
    assert parse_apple_row({"Song Name": "X", "Artist Name": "Y"}) is None
    assert parse_apple_row({"Event Start Timestamp": "2026-01-01T00:00:00Z"}) is None


def test_apple_bad_duration_counts_as_zero():
    row = {
        "Song Name": "X",
        "Artist Name": "Y",
        "Event Start Timestamp": "2026-01-01T00:00:00Z",
        "Play Duration Milliseconds": "-1",
    }
    assert parse_apple_row(row).ms_played == 0


def test_load_apple_csv_from_folder_and_file(make_apple):
    folder = make_apple([("A", "B", "2026-07-02T08:14:03Z", 200_000)])
    assert len(load_plays(folder)) == 1
    assert len(load_plays(folder / "Apple Music Play Activity.csv")) == 1


def test_load_folder_with_both_services(make_export, make_apple):
    folder = make_export([entry("2026-01-01T00:00:00Z", 60_000)])
    make_apple([("A", "B", "2026-07-02T08:14:03Z", 200_000)], folder)
    assert len(load_plays(folder)) == 2


def test_garbage_apple_file_gives_friendly_error(tmp_path):
    (tmp_path / "Apple Music Play Activity.csv").write_text("a,b\n1,2\n")
    with pytest.raises(ExportError, match="Apple Music"):
        load_plays(tmp_path)
