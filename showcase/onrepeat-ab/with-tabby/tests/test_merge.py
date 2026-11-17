import pytest
from onrepeat._core import song_key

from tests.reference_merge import song_key as reference

SAME = [
    (
        "Blinding Lights",
        "The Weeknd",
        "Blinding Lights - Remastered 2020",
        "The Weeknd",
    ),
    ("Blinding Lights", "The Weeknd", "Blinding Lights (2011 Remaster)", "The Weeknd"),
    (
        "Die With A Smile",
        "Lady Gaga",
        "Die With A Smile (feat. Bruno Mars)",
        "Lady Gaga & Bruno Mars",
    ),
    (
        "Die With A Smile",
        "Lady Gaga",
        "Die With A Smile - feat. Bruno Mars",
        "Lady Gaga",
    ),
    ("Don’t Stop Me Now", "Queen", "Don't Stop Me Now", "Queen"),
    ("Don't Stop Me Now", "Queen", "DON'T  STOP ME NOW", "queen"),
    ("Lose Yourself [Remastered]", "Eminem", "Lose Yourself", "Eminem"),
    ("Song", "Artist", "Song (with Someone)", "Artist, Someone"),
    ("Song", "Artist", "Song - 2009 Digital Remaster", "Artist"),
]

DIFFERENT = [
    ("Espresso", "Sabrina Carpenter", "Espresso (sped up)", "Sabrina Carpenter"),
    ("Espresso", "Sabrina Carpenter", "Espresso - Sped Up", "Sabrina Carpenter"),
    ("Song", "Artist", "Song (Live)", "Artist"),
    ("Song", "Artist", "Song (Acoustic)", "Artist"),
    ("Song", "Artist", "Song - Remix", "Artist"),
    ("Song", "Queen", "Song - Live at Wembley 2011 Remaster", "Queen"),
    ("Song", "Queen", "Song (Sped Up Remastered)", "Queen"),
    ("Song", "Artist A", "Song", "Artist B"),
    ("Song", "Artist", "Other Song", "Artist"),
]


@pytest.mark.parametrize("impl", [song_key, reference], ids=["rust", "python"])
@pytest.mark.parametrize(("t1", "a1", "t2", "a2"), SAME)
def test_same_song(impl, t1, a1, t2, a2):
    assert impl(t1, a1) == impl(t2, a2)


@pytest.mark.parametrize("impl", [song_key, reference], ids=["rust", "python"])
@pytest.mark.parametrize(("t1", "a1", "t2", "a2"), DIFFERENT)
def test_different_song(impl, t1, a1, t2, a2):
    assert impl(t1, a1) != impl(t2, a2)


EDGE = [
    ("", ""),
    ("(Remastered)", "Artist"),
    ("(feat. X)", "feat. X"),
    ("Song (unclosed", "Artist"),
    ("Song ((Remastered))", "Artist"),
    ("Song (Remastered) [feat. X] - 2011 Remaster", "Artist"),
    ("A - B - C", "Artist"),
    ("Ünïcödé Straße", "ÉMILIE & Friends"),
    ("Σίσυφος ΑΣ", "Σ"),
    ("Song name", "Artist\tname"),
    ("Rock - Remastered", "Earth, Wind & Fire"),
    ("Song", "Simon & Garfunkel"),
    ("Song", "Tyler x Someone with Other ft. Third"),
    ("It’s “quoted” – dash", "Artist"),
    ("日本語の曲", "歌手"),
    ("Remastered", "Artist"),
    ("Song (2009 Digital Remaster)", "Artist"),
    ("Song - Remastered Version", "Artist"),
    ("Song - Live Remastered", "Artist"),
    ("", "with\x1c"),
    ("a\x1fb (feat.\x1dx)", "x\x1e ft. y"),
]


@pytest.mark.parametrize(("track", "artist"), EDGE)
def test_rust_matches_reference_on_awkward_input(track, artist):
    assert song_key(track, artist) == reference(track, artist)


def test_remaster_keeps_original_when_only_noise():
    assert song_key("(Remastered)", "Artist")[0] == "(remastered)"
