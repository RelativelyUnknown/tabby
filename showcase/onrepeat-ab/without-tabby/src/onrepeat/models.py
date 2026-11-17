from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Play:
    """One time you listened to one song.

    This is deliberately NOT Spotify-shaped. The loader turns Spotify's messy
    JSON into Plays, and later an Apple Music loader can do the same. Everything
    after that (stats, the CLI) only ever sees Plays, so adding a new source
    doesn't mean rewriting the rest.
    """

    played_at: datetime  # timezone-aware, UTC
    track: str
    artist: str
    ms_played: int
