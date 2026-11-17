from conftest import entry

from onrepeat.cli import main


def test_defaults_to_latest_year(make_export, capsys):
    path = make_export(
        [
            entry("2022-01-01T00:00:00Z", 180_000, "Old Song", "Old Artist"),
            entry("2023-01-01T00:00:00Z", 180_000, "New Song", "New Artist"),
        ]
    )
    assert main([str(path)]) == 0
    out = capsys.readouterr().out
    assert "2023" in out and "New Artist" in out and "Old Artist" not in out


def test_year_flag(make_export, capsys):
    path = make_export(
        [
            entry("2022-01-01T00:00:00Z", 180_000, "Old Song", "Old Artist"),
            entry("2023-01-01T00:00:00Z", 180_000, "New Song", "New Artist"),
        ]
    )
    assert main([str(path), "--year", "2022"]) == 0
    assert "Old Artist" in capsys.readouterr().out


def test_unknown_year_lists_available(make_export, capsys):
    path = make_export([entry("2023-01-01T00:00:00Z", 180_000)])
    assert main([str(path), "--year", "1999"]) == 1
    assert "2023" in capsys.readouterr().err


def test_bad_path_returns_error(tmp_path, capsys):
    assert main([str(tmp_path / "nope")]) == 1
    assert "onrepeat:" in capsys.readouterr().err


def test_counts_spotify_and_apple_together(make_apple, tmp_path, capsys):
    spotify = tmp_path / "spotify"
    apple = tmp_path / "apple"
    spotify.mkdir()
    apple.mkdir()
    (spotify / "Streaming_History_Audio_2026_0.json").write_text(
        '[{"ts":"2026-01-01T00:00:00Z","ms_played":180000,'
        '"master_metadata_track_name":"S","master_metadata_album_artist_name":"Both",'
        '"spotify_track_uri":"spotify:track:1"}]'
    )
    make_apple([("A", "Both", "2026-07-02T08:14:03Z", 180_000)], apple)
    assert main([str(spotify), str(apple)]) == 0
    out = capsys.readouterr().out
    assert "Both  (6m, 2 plays)" in out
    assert "Hours listened: 0.1" in out


def test_apple_only(make_apple, tmp_path, capsys):
    assert main([str(make_apple([("A", "B", "2026-07-02T08:14:03Z", 200_000)]))]) == 0
    assert "B" in capsys.readouterr().out


def test_html_share_page_is_escaped(make_export, tmp_path, capsys):
    path = make_export([entry("2023-01-01T00:00:00Z", 180_000, "S<b>", "A&B")])
    out = tmp_path / "wrapped.html"
    assert main([str(path), "--html", str(out)]) == 0
    html = out.read_text()
    assert "A&amp;B" in html and "S&lt;b&gt;" in html and "<b>" not in html


def test_monthly_songs_in_terminal_and_html(make_export, tmp_path, capsys):
    path = make_export([entry("2023-02-03T00:00:00Z", 3 * 60_000, "Feb Jam", "Z")])
    out = tmp_path / "wrapped.html"
    assert main([str(path), "--html", str(out)]) == 0
    text = capsys.readouterr().out
    assert "Song of each month" in text and "Feb  Feb Jam - Z" in text
    assert "Jan  -" in text
    assert "Feb Jam - Z" in out.read_text()
