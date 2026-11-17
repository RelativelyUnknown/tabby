import json

import pytest

from onrepeat.cli import main
from onrepeat.loader import load_plays, parse_entry
from onrepeat.stats import build_wrapped


def entry(track="Song", artist="Artist", ms=200_000, ts="2023-05-01T12:00:00Z"):
    return {
        "ts": ts,
        "ms_played": ms,
        "master_metadata_track_name": track,
        "master_metadata_album_artist_name": artist,
    }


def test_parse_entry_basic():
    play = parse_entry(entry())
    assert play.track == "Song"
    assert play.artist == "Artist"
    assert play.played_at.year == 2023
    assert play.played_at.tzinfo is not None


def test_parse_entry_skips_podcasts():
    podcast = {
        "ts": "2023-05-01T12:00:00Z",
        "ms_played": 5000,
        "master_metadata_track_name": None,
        "episode_name": "Ep 1",
    }
    assert parse_entry(podcast) is None


def test_load_folder_reads_audio_files_only(tmp_path):
    (tmp_path / "Streaming_History_Audio_2023_0.json").write_text(json.dumps([entry()]))
    (tmp_path / "Streaming_History_Video_2023.json").write_text(
        json.dumps([entry("Vid")])
    )
    plays = list(load_plays(tmp_path))
    assert [p.track for p in plays] == ["Song"]


def test_load_empty_folder_errors(tmp_path):
    with pytest.raises(FileNotFoundError):
        list(load_plays(tmp_path))


def plays_from(*entries):
    return [p for e in entries if (p := parse_entry(e))]


def test_wrapped_counts_and_filters_year():
    plays = plays_from(
        entry("A", "X"),
        entry("A", "X"),
        entry("B", "Y"),
        entry("Old", "Z", ts="2022-05-01T12:00:00Z"),
    )
    w = build_wrapped(plays, 2023)
    assert w.top_artists[0] == ("X", 2)
    assert w.top_songs[0] == ("X", "A", 2)
    assert all(a != "Z" for a, _ in w.top_artists)


def test_skips_dont_count_as_plays_but_count_as_hours():
    plays = plays_from(entry("A", "X", ms=5_000), entry("B", "Y", ms=3_600_000 - 5_000))
    w = build_wrapped(plays, 2023)
    assert w.hours_listened == pytest.approx(1.0)
    assert w.top_songs == [("Y", "B", 1)]


def test_same_track_name_different_artist_is_different_song():
    plays = plays_from(entry("Home", "X"), entry("Home", "Y"))
    assert len(build_wrapped(plays, 2023).top_songs) == 2


def test_cli_end_to_end(tmp_path, capsys):
    (tmp_path / "Streaming_History_Audio_2023_0.json").write_text(
        json.dumps([entry("Blinding Lights", "The Weeknd")])
    )
    assert main([str(tmp_path), "--year", "2023"]) == 0
    out = capsys.readouterr().out
    assert "The Weeknd" in out and "Blinding Lights" in out


def test_cli_unknown_year(tmp_path, capsys):
    (tmp_path / "Streaming_History_Audio_2023_0.json").write_text(json.dumps([entry()]))
    assert main([str(tmp_path), "--year", "1999"]) == 1


APPLE_CSV = (
    "Song Name,Album Name,Artist Name,Event Start Timestamp,"
    "Play Duration Milliseconds,End Reason Type,Client IP Address\n"
    '"Good Luck, Babe!",Good Luck Babe!,Chappell Roan,2023-07-02T08:14:03.120Z,'
    "215000,NATURAL_END_OF_TRACK,203.0.113.7\n"
    "Espresso,Espresso,Sabrina Carpenter,2023-07-02T08:17:40Z,12000,"
    "TRACK_SKIPPED_FORWARDS,203.0.113.7\n"
    ",,,2023-07-02T09:00:00Z,1000,,\n"
    "Blank,Alb,Someone,2023-07-02T09:00:00Z,,,\n"
)


def test_apple_loader_parses_rows(tmp_path):
    from onrepeat.apple import load_apple_plays

    f = tmp_path / "Apple Music Play Activity.csv"
    f.write_text(APPLE_CSV, encoding="utf-8")
    plays = list(load_apple_plays(f))
    assert [p.track for p in plays] == ["Good Luck, Babe!", "Espresso", "Blank"]
    assert plays[0].ms_played == 215_000
    assert plays[0].played_at.tzinfo is not None
    assert plays[2].ms_played == 0


def test_apple_loader_finds_file_in_folder(tmp_path):
    from onrepeat.apple import load_apple_plays

    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "Apple Music Play Activity.csv").write_text(APPLE_CSV)
    assert len(list(load_apple_plays(tmp_path))) == 3


def test_cli_combines_spotify_and_apple(tmp_path, capsys):
    spot = tmp_path / "Streaming_History_Audio_2023_0.json"
    spot.write_text(json.dumps([entry("Good Luck, Babe!", "Chappell Roan")]))
    apple = tmp_path / "Apple Music Play Activity.csv"
    apple.write_text(APPLE_CSV)
    assert main([str(spot), "--apple", str(apple), "--year", "2023"]) == 0
    out = capsys.readouterr().out
    assert "Chappell Roan (2 plays)" in out


def test_cli_apple_only(tmp_path, capsys):
    apple = tmp_path / "Apple Music Play Activity.csv"
    apple.write_text(APPLE_CSV)
    assert main(["--apple", str(apple)]) == 0
    assert "Chappell Roan" in capsys.readouterr().out


def test_same_song_merges_across_versions_and_services():
    plays = plays_from(
        entry("Blinding Lights", "The Weeknd"),
        entry("Blinding Lights - Remastered 2020", "The Weeknd"),
        entry("Die With A Smile", "Lady Gaga & Bruno Mars"),
        entry("Die With A Smile (feat. Bruno Mars)", "Lady Gaga"),
        entry("Don’t Stop Me Now", "Queen"),
        entry("Don't Stop Me Now", "Queen"),
        entry("Espresso", "Sabrina Carpenter"),
        entry("Espresso (sped up)", "Sabrina Carpenter"),
    )
    top = {t: n for _, t, n in build_wrapped(plays, 2023).top_songs}
    assert sorted(top.values()) == [1, 1, 2, 2, 2]
    assert top["Espresso"] == 1 and top["Espresso (sped up)"] == 1


def test_monthly_top_song_per_month():
    plays = plays_from(
        entry("Jan Hit", "X", ts="2023-01-05T12:00:00Z"),
        entry("Jan Hit", "X", ts="2023-01-06T12:00:00Z"),
        entry("Jan Other", "Y", ts="2023-01-07T12:00:00Z"),
        entry("Mar Hit", "Z", ts="2023-03-01T12:00:00Z"),
        entry("Skipped", "Q", ms=1_000, ts="2023-04-01T12:00:00Z"),
    )
    m = build_wrapped(plays, 2023).monthly_top
    assert m == {1: ("X", "Jan Hit", 2), 3: ("Z", "Mar Hit", 1)}


def test_monthly_shows_in_terminal_and_share_card(tmp_path, capsys):
    (tmp_path / "Streaming_History_Audio_2023_0.json").write_text(
        json.dumps([entry("Jan <b>Hit", "X", ts="2023-01-05T12:00:00Z")])
    )
    card = tmp_path / "card.html"
    assert main([str(tmp_path), "--year", "2023", "--share", str(card)]) == 0
    out = capsys.readouterr().out
    assert "month by month" in out and "Jan  Jan <b>Hit - X" in out
    html = card.read_text(encoding="utf-8")
    assert "Month by month" in html and "Jan &lt;b&gt;Hit" in html
