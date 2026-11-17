"""The command-line part: read arguments, call the other modules, print."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from onrepeat.loader import ExportError, load_plays
from onrepeat.share import MONTHS, render_html
from onrepeat.stats import (
    DEFAULT_MIN_MS,
    Ranked,
    YearSummary,
    available_years,
    summarize,
)


def _fmt_time(ms: int) -> str:
    minutes = round(ms / 60_000)
    hours, mins = divmod(minutes, 60)
    return f"{hours}h {mins:02d}m" if hours else f"{mins}m"


def _section(title: str, rows: list[Ranked]) -> list[str]:
    lines = ["", title]
    for i, r in enumerate(rows, start=1):
        lines.append(f"  {i:>2}. {r.name}  ({_fmt_time(r.ms)}, {r.plays} plays)")
    return lines


def render(s: YearSummary) -> str:
    lines = [f"=== Your {s.year} on repeat ===", "", f"Hours listened: {s.hours:,.1f}"]
    lines += _section("Top artists", s.top_artists)
    lines += _section("Top songs", s.top_songs)
    lines += ["", "Song of each month"]
    for month, r in zip(MONTHS, s.monthly_top, strict=True):
        what = f"{r.name}  ({r.plays} plays)" if r else "-"
        lines.append(f"  {month}  {what}")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="onrepeat",
        description="Wrapped for Spotify and Apple Music, whenever you want it.",
    )
    p.add_argument(
        "path",
        type=Path,
        nargs="+",
        help="folder(s) or file(s) with your Spotify history JSON and/or "
        "'Apple Music Play Activity.csv'; give several to combine them",
    )
    p.add_argument(
        "-y",
        "--year",
        type=int,
        help="year to show (default: most recent in your data)",
    )
    p.add_argument(
        "-n", "--top", type=int, default=10, help="how many to list (default 10)"
    )
    p.add_argument(
        "--min-seconds",
        type=int,
        default=DEFAULT_MIN_MS // 1000,
        help="ignore plays shorter than this (default 30, like Spotify)",
    )
    p.add_argument(
        "--html",
        type=Path,
        metavar="FILE",
        help="also save a single shareable HTML page (send it to friends)",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        plays = load_plays(*args.path)
    except ExportError as err:
        print(f"onrepeat: {err}", file=sys.stderr)
        return 1

    years = available_years(plays)
    if not years:
        print("onrepeat: that export has no plays in it.", file=sys.stderr)
        return 1
    year = args.year if args.year is not None else years[-1]
    if year not in years:
        have = ", ".join(map(str, years))
        print(
            f"onrepeat: no plays in {year}. Years in your data: {have}", file=sys.stderr
        )
        return 1

    summary = summarize(plays, year, limit=args.top, min_ms=args.min_seconds * 1000)
    print(render(summary))
    if args.html:
        args.html.write_text(render_html(summary), encoding="utf-8")
        print(f"\nSaved shareable page: {args.html}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
