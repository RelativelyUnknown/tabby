"""Render a Wrapped as one self-contained HTML file you can send to friends."""

from html import escape

from onrepeat.wrapped import Wrapped

_PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>My {year} Wrapped</title>
<style>
  body {{ margin: 0; min-height: 100vh; display: grid; place-items: center;
    background: #121212; font-family: system-ui, sans-serif; color: #fff; }}
  .card {{ box-sizing: border-box; width: min(100%, 420px); margin: 16px;
    padding: 32px 24px; border-radius: 24px;
    background: linear-gradient(160deg, #6a11cb, #2575fc 60%, #1db954); }}
  h1 {{ margin: 0; font-size: 2rem; }}
  .hours {{ margin: 8px 0 24px; font-size: 1.1rem; opacity: .9; }}
  .hours b {{ font-size: 2.4rem; display: block; }}
  h2 {{ margin: 24px 0 8px; font-size: .85rem; letter-spacing: .1em;
    text-transform: uppercase; opacity: .8; }}
  ol {{ margin: 0; padding-left: 1.4em; }}
  li {{ margin: 6px 0; font-weight: 600; overflow-wrap: anywhere; }}
  li span {{ display: block; font-weight: 400; opacity: .85; font-size: .9rem; }}
</style>
</head>
<body>
<main class="card">
  <h1>My {year} Wrapped</h1>
  <p class="hours"><b>{hours:,.0f}</b> hours listened</p>
  <h2>Top artists</h2>
  <ol>{artists}</ol>
  <h2>Top songs</h2>
  <ol>{songs}</ol>
</main>
</body>
</html>
"""


def render_card(w: Wrapped) -> str:
    artists = "".join(
        f"<li>{escape(artist)}<span>{n} plays</span></li>"
        for artist, n in w.top_artists
    )
    songs = "".join(
        f"<li>{escape(track)}<span>{escape(artist)} · {n} plays</span></li>"
        for (track, artist), n in w.top_songs
    )
    return _PAGE.format(year=w.year, hours=w.hours, artists=artists, songs=songs)
