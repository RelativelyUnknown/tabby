#!/usr/bin/env python3
"""readme_assets.py: draw the README's SVGs (logo, hero banner, results card), each in a light and a dark variant.

    python3 tools/readme_assets.py            writes assets/tabby-{logo,hero,results}-{light,dark}.svg

Plain SVG with CSS animation only (slow breathing); GitHub shows it in an <img>. Animation is switched off under
prefers-reduced-motion. Numbers for the results card are the RESULTS constants below: update them after a new full run.
"""
import json
import pathlib

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"
FONTS = {name: json.loads((OUT / "src" / f"fredoka-{name}.json").read_text()) for name in ("bold", "medium")}  # outlines made by outline_font.py

# Results of the last full paired run (see TESTING.md).
RESULTS = {"without": 0.812, "with": 0.902, "gain_headroom": "+0.141", "better": 34, "worse": 6, "same": 72, "cases": 112}

THEMES = {
    "light": {"bg": "#fffaf3", "ink": "#16110d", "muted": "#7a6a5a", "whisker": "#5a4636", "panel": "#f6ead9", "line": "#e5d3bb", "bar_off": "#c9b9a4"},
    "dark": {"bg": "#17120d", "ink": "#f4e9da", "muted": "#a8978a", "whisker": "#e9dccb", "panel": "#241c14", "line": "#3a2d20", "bar_off": "#6a5a4a"},
}
FUR, FUR_DARK, TEAL = "#e8903a", "#b3541a", "#2a8f89"

STYLE = """
<style>
  .breathe { transform-box: fill-box; transform-origin: 50% 100%; animation: breathe 4.5s ease-in-out infinite; }
  .walker { opacity: 0; animation: walk 3.4s cubic-bezier(.25,.7,.35,1) both, vanish .45s ease-in 3.4s both; }
  .plop { transform-box: fill-box; transform-origin: 50% 100%; animation: plop .7s ease-out 3.45s both; }
  .bob { animation: bob .5s ease-in-out infinite; }
  .legA, .legB { transform-box: fill-box; transform-origin: 50% 10%; }
  .legA { animation: stride .5s ease-in-out infinite alternate; }
  .legB { animation: stride .5s ease-in-out infinite alternate-reverse; }
  .in1, .in2, .in3 { animation: appear .9s ease-out both; }
  .in1 { animation-delay: 4.1s; } .in2 { animation-delay: 4.7s; } .in3 { animation-delay: 5.3s; }
  @keyframes breathe { 0%, 100% { transform: scale(1, 1); } 50% { transform: scale(1.012, 1.03); } }
  @keyframes walk { from { transform: translateX(-520px); opacity: 1; } to { transform: translateX(0); opacity: 1; } }
  @keyframes vanish { from { opacity: 1; } to { opacity: 0; } }
  @keyframes plop { from { opacity: 0; transform: scale(.9, .72); } 60% { opacity: 1; } to { opacity: 1; transform: scale(1, 1); } }
  @keyframes bob { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-4px); } }
  @keyframes stride { from { transform: rotate(-26deg); } to { transform: rotate(26deg); } }
  @keyframes appear { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: translateY(0); } }
  @media (prefers-reduced-motion: reduce) { .breathe, .walker, .plop, .bob, .legA, .legB, .in1, .in2, .in3 { animation: none; } }
</style>"""


def txt(font, text, x, y, size, fill, cls=""):
    """Text as outlined paths (no font needed to display it). Returns (svg, width)."""
    f, k, cx, parts = FONTS[font], size / FONTS[font]["upm"], x, []
    for ch in text:
        g = f["glyphs"].get(ch)
        if not g:
            continue
        if g["d"]:
            parts.append(f'<path transform="translate({cx:.2f} {y}) scale({k:.5f} {-k:.5f})" d="{g["d"]}"/>')
        cx += g["adv"] * k
    return f'<g fill="{fill}" class="{cls}">{"".join(parts)}</g>', cx - x


def walker(t):
    """The same cat walking, in profile, facing right: 360 x 210 box with its feet on y = 196."""
    ink = THEMES[t]["ink"]
    leg = lambda x, cls: f'<line class="{cls}" x1="{x}" y1="122" x2="{x}" y2="190" stroke="{ink}" stroke-width="24" stroke-linecap="round"/>'
    return f"""<g>
  <defs><mask id="cutw" maskUnits="userSpaceOnUse" x="0" y="0" width="380" height="220">
    <rect width="380" height="220" fill="#fff"/>
    <g fill="none" stroke="#000" stroke-linecap="round"><path d="M126 62 Q142 86 132 112 M168 60 Q184 84 174 110 M210 62 Q226 84 218 108" stroke-width="10"/></g>
    <circle cx="302" cy="72" r="5.5" fill="#000"/>
  </mask></defs>
  {leg(104, "legA")}{leg(222, "legB")}
  <g class="bob">
    <g mask="url(#cutw)" fill="{ink}">
      <path d="M72 84 Q72 60 104 60 L236 60 Q268 60 268 100 Q268 140 232 140 L104 140 Q72 140 72 110 Z"/>
      <circle cx="292" cy="74" r="44"/>
      <path d="M258 52 L262 12 L296 40 Z M298 34 L326 12 L330 56 Z"/>
      <path d="M72 96 Q34 84 40 34 Q44 10 66 16" fill="none" stroke="{ink}" stroke-width="22" stroke-linecap="round"/>
    </g>
    <path d="M52 24 Q58 14 66 16" fill="none" stroke="{TEAL}" stroke-width="22" stroke-linecap="round"/>
  </g>
  {leg(130, "legB")}{leg(248, "legA")}
</g>"""


def cat(t, x=0, y=0, scale=1.0):
    """A curled, sleeping tabby in one solid shape with the details cut out: ears, cheek, stripes, closed eyes.
    Drawn in a 440 x 340 box (from 60,130 in its own units) at (x, y) with a scale; the tail tip is teal."""
    ink = THEMES[t]["ink"]
    return f"""<g transform="translate({x} {y}) scale({scale}) translate(-60 -130)">
  <defs><mask id="cut" maskUnits="userSpaceOnUse" x="40" y="110" width="480" height="380">
    <rect x="40" y="110" width="480" height="380" fill="#fff"/>
    <g fill="none" stroke="#000" stroke-linecap="round" stroke-linejoin="round">
      <path d="M232 318 L236 254 L276 284 Q304 272 332 284 L370 252 L378 322 Q384 384 330 400" stroke-width="13"/>
      <path d="M262 346 Q278 362 296 346 M326 346 Q342 362 360 346" stroke-width="9"/>
      <path d="M150 196 Q182 222 170 262 M198 176 Q226 204 218 240 M112 262 Q146 276 142 308" stroke-width="12"/>
    </g>
  </mask></defs>
  <g class="breathe">
    <g mask="url(#cut)" fill="{ink}">
      <path d="M92 300 C82 206 188 150 288 158 C392 166 444 238 434 322 C424 402 332 444 240 440 C148 436 100 388 92 300 Z"/>
      <path d="M420 392 Q452 440 488 416" fill="none" stroke="{ink}" stroke-width="34" stroke-linecap="round"/>
    </g>
    <path d="M472 421 Q480 419 488 416" fill="none" stroke="{TEAL}" stroke-width="34" stroke-linecap="round"/>
  </g>
</g>"""


def svg(width, height, body, t, title, desc):
    c = THEMES[t]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-labelledby="t d">
<title id="t">{title}</title><desc id="d">{desc}</desc>{STYLE}
{body}
</svg>
"""


def logo(t):
    return svg(440, 340, cat(t), t, "Tabby", "A tabby cat asleep in a curl, drawn as a solid shape with the ears, cheek, stripes and closed eyes cut out.")


def hero(t):
    c = THEMES[t]
    stripes = "".join(f'<path d="M{x} 0 L{x - 60} 360" stroke="{c["line"]}" stroke-width="26" opacity="0.55"/>' for x in range(780, 1500, 120))
    title, _ = txt("bold", "Tabby", 520, 196, 128, c["ink"], "in1")
    tag, _ = txt("medium", "Agent skills for careful Python.", 524, 246, 32, c["muted"], "in2")
    pills, x = [], 524
    for label in ("cause before fix", "small diffs", "tests stay green"):
        _, w = txt("medium", label, 0, 0, 22, "#fff")
        pills.append(f'<rect x="{x}" y="276" width="{w + 36:.0f}" height="40" rx="20" fill="{TEAL}"/>' + txt("medium", label, x + 18, 304, 22, "#fff")[0])
        x += w + 36 + 12
    body = f"""<rect width="1280" height="360" rx="28" fill="{c['panel']}"/>
<clipPath id="r"><rect width="1280" height="360" rx="28"/></clipPath>
<g clip-path="url(#r)">{stripes}
  <g class="plop">{cat(t, 70, 44, 0.8)}</g>
  <g transform="translate(70 116) scale(0.9)"><g class="walker">{walker(t)}</g></g>
</g>
{title}
{tag}
<g class="in3">{''.join(pills)}</g>"""
    return svg(1280, 360, body, t, "Tabby: agent skills for careful Python", "A cat walks in from the left and lies down; then the name Tabby, the line Agent skills for careful Python and three habits appear: cause before fix, small diffs, tests stay green.")


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
        for name, fn in (("logo", logo), ("hero", hero), ("results", results)):
            (OUT / f"tabby-{name}-{t}.svg").write_text(fn(t))
    print("wrote", ", ".join(sorted(p.name for p in OUT.glob("tabby-*.svg"))))


if __name__ == "__main__":
    main()
