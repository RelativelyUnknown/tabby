import json
from pathlib import Path

import pytest

from onrepeat import apple, spotify
from onrepeat.spotify import ExportError, load_plays
from onrepeat.wrapped import build_wrapped, main

IP = "203.0.113.7"


def row(ts, ms, track="Song A", artist="Artist A"):
    return {
        "ts": ts,
        "ms_played": ms,
        "master_metadata_track_name": track,
        "master_metadata_album_artist_name": artist,
        "ip_addr": IP,
    }


def write_export(folder: Path, rows, name="Streaming_History_Audio_2024_0.json"):
    folder.mkdir(parents=True, exist_ok=True)
    (folder / name).write_text(json.dumps(rows), encoding="utf-8")
    return folder


def test_top_lists_and_hours(tmp_path):
    rows = (
        [row("2024-03-01T10:00:00Z", 60_000)] * 3
        + [row("2024-03-02T10:00:00Z", 60_000, "Song B", "Artist B")] * 2
        + [row("2024-03-03T10:00:00Z", 60_000, "Song C", "Artist C")]
    )
    w = build_wrapped(load_plays(write_export(tmp_path, rows)), 2024)
    assert w.top_artists == [("Artist A", 3), ("Artist B", 2), ("Artist C", 1)]
    assert w.top_songs[0] == (("Song A", "Artist A"), 3)
    assert w.hours == pytest.approx(6 * 60_000 / 3_600_000)


def test_skips_do_not_count_as_plays_but_count_as_hours(tmp_path):
    rows = [row("2024-01-01T00:00:00Z", 29_999), row("2024-01-01T00:01:00Z", 30_000)]
    w = build_wrapped(load_plays(write_export(tmp_path, rows)), 2024)
    assert w.top_songs == [(("Song A", "Artist A"), 1)]
    assert w.hours == pytest.approx(59_999 / 3_600_000)


def test_podcast_rows_count_for_hours_only(tmp_path):
    rows = [row("2024-01-01T00:00:00Z", 600_000, track=None, artist=None)]
    w = build_wrapped(load_plays(write_export(tmp_path, rows)), 2024)
    assert w.top_songs == [] and w.top_artists == []
    assert w.hours == pytest.approx(600_000 / 3_600_000)


def test_year_boundaries(tmp_path):
    rows = [row("2023-12-31T23:59:59Z", 60_000), row("2024-01-01T00:00:00Z", 60_000)]
    plays = load_plays(write_export(tmp_path, rows))
    assert build_wrapped(plays, 2024).top_songs == [(("Song A", "Artist A"), 1)]
    assert build_wrapped(plays, 2022) is None


def test_reads_all_files_in_nested_folder(tmp_path):
    export = tmp_path / "Spotify Extended Streaming History"
    write_export(
        export,
        [row("2024-01-01T00:00:00Z", 60_000)],
        "Streaming_History_Audio_2023_0.json",
    )
    write_export(
        export,
        [row("2024-01-02T00:00:00Z", 60_000)],
        "Streaming_History_Audio_2024_1.json",
    )
    assert len(load_plays(tmp_path)) == 2


def test_cli_prints_wrapped_without_ip(tmp_path, capsys):
    write_export(tmp_path, [row("2024-01-01T00:00:00Z", 60_000)])
    assert main(["2024", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "Artist A" in out and "Song A" in out
    assert IP not in out


def test_cli_empty_year_fails(tmp_path, capsys):
    write_export(tmp_path, [row("2024-01-01T00:00:00Z", 60_000)])
    assert main(["1999", str(tmp_path)]) == 1
    assert "no listening found for 1999" in capsys.readouterr().err


def test_cli_no_files_fails(tmp_path, capsys):
    assert main(["2024", str(tmp_path)]) == 1
    assert "no Streaming_History_Audio_" in capsys.readouterr().err


@pytest.mark.parametrize(
    "content",
    ["not json", '{"a": 1}', json.dumps([{"ts": "2024-01-01T00:00:00Z"}])],
)
def test_bad_file_gives_clear_error_without_row_contents(tmp_path, content):
    (tmp_path / "Streaming_History_Audio_2024_0.json").write_text(
        content, encoding="utf-8"
    )
    with pytest.raises(ExportError) as e:
        load_plays(tmp_path)
    assert IP not in str(e.value)


def test_bad_row_error_does_not_leak_ip(tmp_path):
    (tmp_path / "Streaming_History_Audio_2024_0.json").write_text(
        json.dumps([{"ts": "garbage", "ms_played": 1, "ip_addr": IP}]), encoding="utf-8"
    )
    with pytest.raises(ExportError) as e:
        load_plays(tmp_path)
    assert IP not in str(e.value)


APPLE_HEADER = (
    "Song Name,Album Name,Artist Name,Event Start Timestamp,"
    "Play Duration Milliseconds,End Reason Type,Client IP Address\n"
)
APPLE_SAMPLE = (
    '"Good Luck, Babe!",Good Luck Babe!,Chappell Roan,2026-07-02T08:14:03.120Z,'
    f"215000,NATURAL_END_OF_TRACK,{IP}\n"
    f"Espresso,Espresso,Sabrina Carpenter,2026-07-02T08:17:40Z,12000,"
    f"TRACK_SKIPPED_FORWARDS,{IP}\n"
)


def write_apple(folder: Path, body: str = APPLE_SAMPLE):
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "Apple Music Play Activity.csv").write_text(
        APPLE_HEADER + body, encoding="utf-8-sig"
    )


def test_apple_plays_are_read_with_quoted_commas_and_skips(tmp_path):
    write_apple(tmp_path)
    plays = apple.load_plays(tmp_path)
    assert [(p.track, p.artist, p.ms_played) for p in plays] == [
        ("Good Luck, Babe!", "Chappell Roan", 215_000),
        ("Espresso", "Sabrina Carpenter", 12_000),
    ]


def test_apple_without_file_is_empty(tmp_path):
    assert apple.load_plays(tmp_path) == []


def test_apple_rows_without_time_or_duration_are_ignored(tmp_path):
    write_apple(tmp_path, f"X,Y,Z,,,,{IP}\nA,B,C,2026-07-02T08:14:03Z,,,{IP}\n")
    assert apple.load_plays(tmp_path) == []


def test_apple_bad_file_error_does_not_leak_ip(tmp_path):
    write_apple(tmp_path, f"A,B,C,garbage,1000,,{IP}\n")
    with pytest.raises(ExportError) as e:
        apple.load_plays(tmp_path)
    assert IP not in str(e.value)


def test_cli_counts_spotify_and_apple_together(tmp_path, capsys):
    write_export(
        tmp_path, [row("2026-07-01T10:00:00Z", 60_000, "Espresso", "Sabrina Carpenter")]
    )
    write_apple(tmp_path)
    assert main(["2026", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "Chappell Roan (1 plays)" in out
    assert "Espresso - Sabrina Carpenter (1 plays)" in out
    assert "Hours listened: 0.1" in out
    assert IP not in out


def test_cli_apple_only(tmp_path, capsys):
    write_apple(tmp_path)
    assert main(["2026", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "Chappell Roan (1 plays)" in out
    assert IP not in out


def test_spotify_only_still_works(tmp_path, capsys):
    write_export(tmp_path, [row("2024-01-01T00:00:00Z", 60_000)])
    assert main(["2024", str(tmp_path)]) == 0


def test_versions_and_services_merge_into_one_top_song(tmp_path):
    spotify_rows = [
        row("2026-07-01T10:00:00Z", 60_000, "Blinding Lights", "The Weeknd"),
        row("2026-07-01T11:00:00Z", 60_000, "Blinding Lights", "The Weeknd"),
        row("2026-07-01T12:00:00Z", 60_000, "Espresso", "Sabrina Carpenter"),
        row("2026-07-01T13:00:00Z", 60_000, "Espresso (sped up)", "Sabrina Carpenter"),
    ]
    write_export(tmp_path, spotify_rows)
    write_apple(
        tmp_path,
        f"Blinding Lights - Remastered 2020,A,The Weeknd,2026-07-02T08:00:00Z,"
        f"200000,,{IP}\n"
        f"Don’t Stop Me Now,A,Queen,2026-07-02T09:00:00Z,200000,,{IP}\n"
        f"Don't Stop Me Now,A,Queen,2026-07-02T10:00:00Z,200000,,{IP}\n",
    )
    songs = dict(
        build_wrapped(
            spotify.load_plays(tmp_path) + apple.load_plays(tmp_path), 2026
        ).top_songs
    )
    assert songs[("Blinding Lights", "The Weeknd")] == 3
    assert sum(n for (t, _), n in songs.items() if "Stop Me Now" in t) == 2
    assert songs[("Espresso", "Sabrina Carpenter")] == 1
    assert songs[("Espresso (sped up)", "Sabrina Carpenter")] == 1


def test_card_has_top_lists_and_escapes_html_without_ip(tmp_path, capsys):
    rows = [row("2024-03-01T10:00:00Z", 60_000, "<b>Hi</b> & Bye", "Artist A")]
    folder = write_export(tmp_path / "data", rows)
    card = tmp_path / "wrapped.html"
    assert main(["2024", str(folder), "--card", str(card)]) == 0
    html = card.read_text(encoding="utf-8")
    assert "My 2024 Wrapped" in html
    assert "&lt;b&gt;Hi&lt;/b&gt; &amp; Bye" in html
    assert "<b>Hi</b>" not in html
    assert IP not in html
    assert IP not in capsys.readouterr().out


def test_card_unwritable_path_is_a_clean_error(tmp_path, capsys):
    folder = write_export(tmp_path / "data", [row("2024-03-01T10:00:00Z", 60_000)])
    bad = tmp_path / "missing-dir" / "c.html"
    assert main(["2024", str(folder), "--card", str(bad)]) == 1
    assert "cannot write card" in capsys.readouterr().err
