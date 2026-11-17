from conftest import entry

from onrepeat.loader import parse_apple_row, parse_entry
from onrepeat.stats import available_years, summarize

MIN = 60_000


def plays(*entries):
    return [parse_entry(e) for e in entries]


def test_top_artists_ranked_by_time_not_play_count():
    data = plays(
        entry("2023-01-01T00:00:00Z", 40_000, "Short", "Frequent"),
        entry("2023-01-02T00:00:00Z", 40_000, "Short", "Frequent"),
        entry("2023-01-03T00:00:00Z", 10 * MIN, "Long", "Marathon"),
    )
    top = summarize(data, 2023).top_artists
    assert [a.name for a in top] == ["Marathon", "Frequent"]
    assert top[1].plays == 2


def test_only_chosen_year_counts():
    data = plays(
        entry("2022-12-31T23:00:00Z", 60 * MIN, "Old", "Then"),
        entry("2023-01-01T01:00:00Z", 60 * MIN, "New", "Now"),
    )
    s = summarize(data, 2023)
    assert [a.name for a in s.top_artists] == ["Now"]
    assert s.hours == 1.0


def test_short_plays_are_ignored():
    data = plays(entry("2023-01-01T00:00:00Z", 5_000))
    s = summarize(data, 2023)
    assert s.hours == 0
    assert s.top_songs == []


def test_podcasts_count_toward_hours_but_not_top_lists():
    data = plays(entry("2023-01-01T00:00:00Z", 60 * MIN, track=None))
    s = summarize(data, 2023)
    assert s.hours == 1.0
    assert s.top_artists == [] and s.top_songs == []


def test_same_title_different_artist_are_different_songs():
    data = plays(
        entry("2023-01-01T00:00:00Z", 3 * MIN, "Intro", "A", uri="spotify:track:1"),
        entry("2023-01-02T00:00:00Z", 3 * MIN, "Intro", "B", uri="spotify:track:2"),
    )
    assert len(summarize(data, 2023).top_songs) == 2


def test_song_label_and_limit():
    data = plays(
        entry("2023-01-01T00:00:00Z", 3 * MIN, "One", "X"),
        entry("2023-01-01T01:00:00Z", 2 * MIN, "Two", "Y"),
    )
    s = summarize(data, 2023, limit=1)
    assert [r.name for r in s.top_songs] == ["One - X"]


def test_available_years_sorted_unique():
    data = plays(
        entry("2023-01-01T00:00:00Z", 1),
        entry("2021-01-01T00:00:00Z", 1),
        entry("2023-06-01T00:00:00Z", 1),
    )
    assert available_years(data) == [2021, 2023]


def test_same_song_from_spotify_and_apple_is_merged():
    spotify = parse_entry(
        entry("2023-01-01T00:00:00Z", 3 * MIN, "Espresso", "Sabrina Carpenter")
    )
    apple = parse_apple_row(
        {
            "Song Name": "espresso",
            "Artist Name": "Sabrina Carpenter",
            "Event Start Timestamp": "2023-01-02T00:00:00Z",
            "Play Duration Milliseconds": str(3 * MIN),
        }
    )
    top = summarize([spotify, apple], 2023).top_songs
    assert len(top) == 1 and top[0].plays == 2 and top[0].ms == 6 * MIN


def apple(song, artist, start="2023-01-01T00:00:00Z", ms=3 * MIN):
    return parse_apple_row(
        {
            "Song Name": song,
            "Artist Name": artist,
            "Event Start Timestamp": start,
            "Play Duration Milliseconds": str(ms),
        }
    )


def test_same_song_across_versions_and_services_is_one_song():
    data = plays(
        entry("2023-01-01T00:00:00Z", 3 * MIN, "Blinding Lights", "The Weeknd"),
        entry(
            "2023-01-02T00:00:00Z",
            3 * MIN,
            "Blinding Lights - Remastered 2020",
            "The Weeknd",
        ),
        entry(
            "2023-01-03T00:00:00Z",
            3 * MIN,
            "Die With A Smile (feat. Bruno Mars)",
            "Lady Gaga",
        ),
        entry("2023-01-04T00:00:00Z", 3 * MIN, "Don't Stop Me Now", "Queen"),
    ) + [
        apple("Die With A Smile", "Lady Gaga & Bruno Mars", "2023-02-01T00:00:00Z"),
        apple("Don’t Stop Me Now", "Queen", "2023-02-02T00:00:00Z"),
        apple("Don’t Stop Me Now", "Queen", "2023-02-03T00:00:00Z"),
    ]
    top = summarize(data, 2023).top_songs
    assert [(s.plays) for s in top] == [3, 2, 2]
    assert len(top) == 3


def test_sped_up_is_its_own_song():
    data = plays(
        entry("2023-01-01T00:00:00Z", 3 * MIN, "Espresso", "Sabrina Carpenter"),
        entry(
            "2023-01-02T00:00:00Z", 3 * MIN, "Espresso (sped up)", "Sabrina Carpenter"
        ),
    )
    assert len(summarize(data, 2023).top_songs) == 2


def test_merged_song_is_labelled_with_the_most_listened_spelling():
    data = plays(
        entry("2023-01-01T00:00:00Z", 2 * MIN, "Blinding Lights", "The Weeknd"),
        entry(
            "2023-01-02T00:00:00Z",
            5 * MIN,
            "Blinding Lights - Remastered 2020",
            "The Weeknd",
        ),
    )
    (song,) = summarize(data, 2023).top_songs
    assert song.name == "Blinding Lights - Remastered 2020 - The Weeknd"
    assert song.plays == 2


def test_monthly_top_song_picks_each_months_number_one():
    data = plays(
        entry("2023-01-05T00:00:00Z", 5 * MIN, "Jan Hit", "A"),
        entry("2023-01-06T00:00:00Z", 3 * MIN, "Other", "B"),
        entry("2023-03-05T00:00:00Z", 4 * MIN, "Mar Hit", "C"),
        entry("2022-02-05T00:00:00Z", 9 * MIN, "Wrong Year", "D"),
    )
    top = summarize(data, 2023).monthly_top
    assert len(top) == 12
    assert top[0].name == "Jan Hit - A"
    assert top[1] is None  # no plays in February
    assert top[2].name == "Mar Hit - C"
