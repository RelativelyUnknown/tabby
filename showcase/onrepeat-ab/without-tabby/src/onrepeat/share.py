"""Render a Wrapped as a single self-contained HTML page you can send to friends.

No external fonts, scripts or images, so the file works offline and can be
attached to a chat, hosted anywhere, or screenshotted. It only contains the
summary numbers (no timestamps, no raw history).
"""

from html import escape

from onrepeat.stats import Wrapped

_PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>My {year} on repeat</title>
<meta property="og:title" content="My {year} on repeat">
<meta property="og:description" content="{hours} hours listened. Top artist: {top_artist}.">
<style>
  :root {{ --bg:#120b24; --fg:#fff; --muted:#b9aee0; --accent:#b6ff5c; --card:#1d1238; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; min-height:100vh; display:grid; place-items:center; padding:16px;
    background:var(--bg); color:var(--fg);
    font:16px/1.4 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif; }}
  .card {{ width:100%; max-width:420px; padding:32px 24px; border-radius:28px;
    background:linear-gradient(160deg,#4b1d95 0%,#1d1238 55%,#0e2a3a 100%); }}
  .year {{ color:var(--accent); font-weight:800; letter-spacing:.12em; text-transform:uppercase; font-size:13px; }}
  h1 {{ margin:6px 0 20px; font-size:34px; line-height:1.1; }}
  .hours {{ background:var(--card); border-radius:18px; padding:18px; margin-bottom:24px; }}
  .hours b {{ display:block; font-size:52px; line-height:1; color:var(--accent); }}
  .hours span {{ color:var(--muted); }}
  h2 {{ font-size:12px; letter-spacing:.12em; text-transform:uppercase; color:var(--muted); margin:22px 0 8px; }}
  ol {{ margin:0; padding:0; list-style:none; }}
  li {{ display:flex; gap:12px; align-items:baseline; padding:7px 0; border-bottom:1px solid #ffffff14; }}
  li i {{ font-style:normal; font-weight:800; color:var(--accent); width:1.2em; }}
  li div {{ flex:1; min-width:0; overflow-wrap:anywhere; }}
  li small {{ display:block; color:var(--muted); }}
  li em {{ font-style:normal; color:var(--muted); font-size:13px; white-space:nowrap; }}
  button {{ margin-top:26px; width:100%; padding:14px; border:0; border-radius:999px; cursor:pointer;
    background:var(--accent); color:#120b24; font:700 16px inherit; font-family:inherit; }}
  .brand {{ margin-top:18px; text-align:center; color:var(--muted); font-size:12px; }}
  @media print {{ button {{ display:none; }} }}
</style>
</head>
<body>
<main class="card">
  <div class="year">{year} wrapped</div>
  <h1>My year on repeat</h1>
  <div class="hours"><b>{hours}</b><span>hours listened</span></div>
  <h2>Top artists</h2>
  <ol>{artists}</ol>
  <h2>Top songs</h2>
  <ol>{songs}</ol>
  <button id="share" type="button">Share</button>
  <div class="brand">made with onrepeat</div>
</main>
<script>
  const text = {text_js};
  const btn = document.getElementById("share");
  btn.addEventListener("click", async () => {{
    try {{
      if (navigator.share) {{ await navigator.share({{ title: document.title, text }}); }}
      else {{ await navigator.clipboard.writeText(text); btn.textContent = "Copied!"; }}
    }} catch (e) {{ /* user cancelled or clipboard blocked */ }}
  }});
</script>
</body>
</html>
"""


def share_text(w: Wrapped) -> str:
    """Plain-text version, handy for pasting into a chat."""
    lines = [f"My {w.year} on repeat 🎧", f"{w.hours_listened:,.0f} hours listened", ""]
    lines += ["Top artists"]
    lines += [f"{i}. {a}" for i, (a, _) in enumerate(w.top_artists, 1)]
    lines += ["", "Top songs"]
    lines += [f"{i}. {t} - {a}" for i, (a, t, _) in enumerate(w.top_songs, 1)]
    return "\n".join(lines)


def render_html(w: Wrapped) -> str:
    import json

    artists = "".join(
        f"<li><i>{i}</i><div>{escape(a)}</div><em>{n} plays</em></li>"
        for i, (a, n) in enumerate(w.top_artists, 1)
    )
    songs = "".join(
        f"<li><i>{i}</i><div>{escape(t)}<small>{escape(a)}</small></div>"
        f"<em>{n} plays</em></li>"
        for i, (a, t, n) in enumerate(w.top_songs, 1)
    )
    top_artist = w.top_artists[0][0] if w.top_artists else "-"
    # "</" would let a song title close the <script> tag early.
    text_js = json.dumps(share_text(w)).replace("</", "<\\/")
    return _PAGE.format(
        year=w.year,
        hours=f"{w.hours_listened:,.0f}",
        top_artist=escape(top_artist, quote=True),
        artists=artists,
        songs=songs,
        text_js=text_js,
    )
