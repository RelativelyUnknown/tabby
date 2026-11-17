import argparse
import sys
from pathlib import Path

from onrepeat.apple import load_apple_plays
from onrepeat.loader import load_plays
from onrepeat.models import Play
from onrepeat.share import render_html, share_text
from onrepeat.stats import MONTH_NAMES, Wrapped, available_years, build_wrapped


def render(w: Wrapped) -> str:
    lines = [
        f"=== Your {w.year} on repeat ===",
        "",
        f"Hours listened: {w.hours_listened:,.1f}",
        "",
        "Top artists",
    ]
    lines += [f"  {i}. {a} ({n} plays)" for i, (a, n) in enumerate(w.top_artists, 1)]
    lines += ["", "Top songs"]
    lines += [
        f"  {i}. {t} - {a} ({n} plays)" for i, (a, t, n) in enumerate(w.top_songs, 1)
    ]
    if w.monthly_top:
        lines += ["", "Your #1 song, month by month"]
        lines += [
            f"  {MONTH_NAMES[m - 1][:3]}  {t} - {a} ({n} plays)"
            for m, (a, t, n) in sorted(w.monthly_top.items())
        ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="onrepeat",
        description="Wrapped for Spotify and/or Apple Music, whenever you want.",
    )
    parser.add_argument(
        "path",
        type=Path,
        nargs="?",
        help="Spotify export folder or a single .json file",
    )
    parser.add_argument(
        "--apple",
        type=Path,
        help="Apple Music 'Play Activity.csv' file (or the folder containing it)",
    )
    parser.add_argument("--year", type=int, help="year to show (default: latest)")
    parser.add_argument("--top", type=int, default=5, help="list length (default 5)")
    parser.add_argument(
        "--share",
        type=Path,
        metavar="FILE.html",
        help="also write a shareable, self-contained HTML card to FILE.html",
    )
    args = parser.parse_args(argv)

    if args.path is None and args.apple is None:
        parser.error("give a Spotify path, --apple, or both")

    try:
        plays: list[Play] = []
        if args.path is not None:
            plays += load_plays(args.path)
        if args.apple is not None:
            plays += load_apple_plays(args.apple)
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    years = available_years(plays)
    if not years:
        print("error: no songs found in that export", file=sys.stderr)
        return 1
    year = args.year or years[-1]
    if year not in years:
        print(f"error: no data for {year}. Years in export: {years}", file=sys.stderr)
        return 1

    wrapped = build_wrapped(plays, year, args.top)
    print(render(wrapped))
    if args.share is not None:
        args.share.write_text(render_html(wrapped), encoding="utf-8")
        print(f"\nShareable card saved to {args.share}\n\n--- paste into a chat ---")
        print(share_text(wrapped))
    return 0


if __name__ == "__main__":
    sys.exit(main())
