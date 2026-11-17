"""Turn a YearSummary into one self-contained HTML page you can send to friends."""

from __future__ import annotations

from html import escape

from onrepeat.stats import Ranked, YearSummary

MONTHS = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]

_CSS = """
:root{--bg:#121212;--fg:#fff;--muted:#b3b3b3;--accent:#1ed760;--card:#1e1e1e}
*{box-sizing:border-box}
body{margin:0;min-height:100vh;display:grid;place-items:center;padding:16px;
background:var(--bg);color:var(--fg);font:16px/1.4 system-ui,sans-serif}
main{width:100%;max-width:420px;background:linear-gradient(160deg,#4b1d8f,#0e5f4a);
border-radius:24px;padding:28px 24px}
h1{margin:0;font-size:1.1rem;color:var(--accent);letter-spacing:.04em;text-transform:uppercase}
.hours{font-size:3.4rem;font-weight:800;margin:.3em 0 0;line-height:1}
.sub{color:var(--muted);margin:0 0 1.4em}
h2{font-size:.85rem;color:var(--muted);text-transform:uppercase;
letter-spacing:.08em;margin:1.4em 0 .4em}
ol{margin:0;padding:0;list-style:none;counter-reset:n}
li{counter-increment:n;display:flex;gap:.7em;padding:.35em 0}
li::before{content:counter(n);color:var(--accent);font-weight:700;min-width:1.5em}
.months li::before{content:none}
.months .m{color:var(--accent);min-width:2.6em}
.months .none{color:var(--muted)}
li small{display:block;color:var(--muted)}
"""


def _fmt_time(ms: int) -> str:
    minutes = round(ms / 60_000)
    hours, mins = divmod(minutes, 60)
    return f"{hours}h {mins:02d}m" if hours else f"{mins}m"


def _list(title: str, rows: list[Ranked]) -> str:
    items = "".join(
        f"<li><span>{escape(r.name)}"
        f"<small>{_fmt_time(r.ms)} · {r.plays} plays</small></span></li>"
        for r in rows
    )
    return f"<h2>{escape(title)}</h2><ol>{items}</ol>"


def _months(rows: list[Ranked | None]) -> str:
    items = "".join(
        f"<li><span class=m>{m}</span><span>{escape(r.name)}</span></li>"
        if r
        else f"<li><span class=m>{m}</span><span class=none>-</span></li>"
        for m, r in zip(MONTHS, rows, strict=True)
    )
    return f"<h2>Song of each month</h2><ol class=months>{items}</ol>"


def render_html(s: YearSummary) -> str:
    title = f"My {s.year} on repeat"
    return (
        "<!doctype html><html lang=en><head><meta charset=utf-8>"
        "<meta name=viewport content='width=device-width,initial-scale=1'>"
        f"<title>{escape(title)}</title><style>{_CSS}</style></head><body><main>"
        f"<h1>{escape(title)}</h1>"
        f"<p class=hours>{s.hours:,.0f}</p><p class=sub>hours listened</p>"
        f"{_list('Top artists', s.top_artists)}{_list('Top songs', s.top_songs)}"
        f"{_months(s.monthly_top)}"
        "</main></body></html>\n"
    )
