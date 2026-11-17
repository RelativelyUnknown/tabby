#!/usr/bin/env python3
"""readme_assets.py: draw the README's results card, in a light and a dark variant.

    python3 tools/readme_assets.py            writes assets/tabby-results-{light,dark}.svg

The numbers are the RESULTS constants below: update them after a new full run. The hero loop and the logo are made by
tools/readme_film/ (see its build.mjs).
"""
import pathlib

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"

# Results of the last full paired run (see TESTING.md).
RESULTS = {"without": 0.812, "with": 0.902, "gain_headroom": "+0.141", "better": 34, "worse": 6, "same": 72, "cases": 112}

THEMES = {
    "light": {"bg": "#fffaf3", "ink": "#16110d", "muted": "#7a6a5a", "whisker": "#5a4636", "panel": "#f6ead9", "line": "#e5d3bb", "bar_off": "#c9b9a4"},
    "dark": {"bg": "#17120d", "ink": "#f4e9da", "muted": "#a8978a", "whisker": "#e9dccb", "panel": "#241c14", "line": "#3a2d20", "bar_off": "#6a5a4a"},
}
FUR, FUR_DARK, TEAL = "#e8903a", "#b3541a", "#2a8f89"

STYLE = ""


def svg(width, height, body, t, title, desc):
    c = THEMES[t]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-labelledby="t d">
<title id="t">{title}</title><desc id="d">{desc}</desc>{STYLE}
{body}
</svg>
"""


def results(t):
    c, r = THEMES[t], RESULTS
    full = 520
    wo, wi = round(full * r["without"]), round(full * r["with"])
    tot = r["better"] + r["worse"] + r["same"]
    bar = 688
    sb, sw = round(bar * r["better"] / tot), max(round(bar * r["worse"] / tot), 16)
    f = "font-family=\"'Segoe UI','Helvetica Neue',Arial,sans-serif\""
    body = f"""<rect width="760" height="358" rx="22" fill="{c['panel']}" stroke="{c['line']}" stroke-width="2"/>
<text x="36" y="52" {f} font-size="26" font-weight="700" fill="{c['ink']}">Measured effect</text>
<text x="36" y="78" {f} font-size="15" fill="{c['muted']}">{r['cases']} cases, 3 runs each, Claude Haiku 5.5, the same agent with and without Tabby</text>
<text x="36" y="124" {f} font-size="16" fill="{c['muted']}">Without</text>
<rect x="130" y="106" width="{full}" height="26" rx="13" fill="{c['line']}"/><rect x="130" y="106" width="{wo}" height="26" rx="13" fill="{c['bar_off']}"/>
<text x="{130 + full + 14}" y="125" {f} font-size="17" font-weight="700" fill="{c['ink']}">{r['without']:.3f}</text>
<text x="36" y="168" {f} font-size="16" fill="{c['muted']}">With Tabby</text>
<rect x="130" y="150" width="{full}" height="26" rx="13" fill="{c['line']}"/><rect x="130" y="150" width="{wi}" height="26" rx="13" fill="{FUR}"/>
<text x="{130 + full + 14}" y="169" {f} font-size="17" font-weight="700" fill="{c['ink']}">{r['with']:.3f}</text>
<text x="36" y="226" {f} font-size="44" font-weight="800" fill="{TEAL}">+{r['with'] - r['without']:.3f}</text>
<text x="36" y="250" {f} font-size="14" fill="{c['muted']}">mean score, all cases</text>
<text x="250" y="226" {f} font-size="44" font-weight="800" fill="{FUR_DARK if t == 'light' else FUR}">{r['gain_headroom']}</text>
<text x="250" y="250" {f} font-size="14" fill="{c['muted']}">on the cases where it scores under 0.95 without</text>
<text x="36" y="290" {f} font-size="14" fill="{c['muted']}">Change per case of 0.10 or more</text>
<rect x="36" y="300" width="{bar}" height="16" rx="8" fill="{c['line']}"/>
<rect x="36" y="300" width="{sb}" height="16" rx="8" fill="{TEAL}"/>
<rect x="{36 + bar - sw}" y="300" width="{sw}" height="16" rx="8" fill="#d6564a"/>
<text x="36" y="338" {f} font-size="14" fill="{c['ink']}"><tspan fill="{TEAL}" font-weight="700">{r['better']} better</tspan>   ·   <tspan fill="{c['muted']}">{r['same']} about the same</tspan>   ·   <tspan fill="#d6564a" font-weight="700">{r['worse']} worse</tspan></text>"""
    return svg(760, 358, body, t, "Measured effect", f"Mean score {r['without']} without Tabby and {r['with']} with it over {r['cases']} cases.")


def main():
    OUT.mkdir(exist_ok=True)
    for t in THEMES:
        for name, fn in (("results", results),):
            (OUT / f"tabby-{name}-{t}.svg").write_text(fn(t))
    print("wrote", ", ".join(sorted(p.name for p in OUT.glob("tabby-*.svg"))))


if __name__ == "__main__":
    main()
