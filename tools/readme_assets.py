#!/usr/bin/env python3
"""readme_assets.py: draw the README's SVGs (logo, hero banner, results card), each in a light and a dark variant.

    python3 tools/readme_assets.py            writes assets/tabby-{logo,hero,results}-{light,dark}.svg

Plain SVG with CSS animation only (a blink and an ear flick); GitHub shows it in an <img>. Animation is switched off under
prefers-reduced-motion. Numbers for the results card are the RESULTS constants below: update them after a new full run.
"""
import pathlib

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"

# Results of the last full paired run (see TESTING.md).
RESULTS = {"without": 0.812, "with": 0.902, "gain_headroom": "+0.141", "better": 34, "worse": 6, "same": 72, "cases": 112}

THEMES = {
    "light": {"bg": "#fffaf3", "ink": "#2b2118", "muted": "#7a6a5a", "whisker": "#5a4636", "panel": "#f6ead9", "line": "#e5d3bb", "bar_off": "#c9b9a4"},
    "dark": {"bg": "#17120d", "ink": "#f4e9da", "muted": "#a8978a", "whisker": "#e9dccb", "panel": "#241c14", "line": "#3a2d20", "bar_off": "#6a5a4a"},
}
FUR, FUR_DARK, MUZZLE, EAR, TEAL, EYE = "#e8903a", "#b3541a", "#f7cf9a", "#f2a6a0", "#2a8f89", "#7fc96b"

STYLE = """
<style>
  .blink { transform-box: fill-box; transform-origin: center; animation: blink 5.5s infinite; }
  .ear { transform-box: fill-box; transform-origin: 50% 100%; animation: flick 9s infinite; }
  @keyframes blink { 0%, 93%, 100% { transform: scaleY(1); } 96% { transform: scaleY(0.08); } }
  @keyframes flick { 0%, 90%, 100% { transform: rotate(0); } 93% { transform: rotate(-7deg); } 96% { transform: rotate(2deg); } }
  @media (prefers-reduced-motion: reduce) { .blink, .ear { animation: none; } }
</style>"""


def cat(t, x=0, y=0, scale=1.0):
    """The tabby head: 512 x 540 units, drawn at (x, y) with a scale."""
    w = THEMES[t]["whisker"]
    return f"""<g transform="translate({x} {y}) scale({scale})">
  <g class="ear"><path d="M104 132 L112 92 Q116 84 124 90 L196 168 Z" fill="{FUR}"/><path d="M128 120 L124 112 L172 164 L146 160 Z" fill="{EAR}"/></g>
  <g class="ear" style="animation-delay:1.3s"><path d="M408 132 L400 92 Q396 84 388 90 L316 168 Z" fill="{FUR}"/><path d="M384 120 L388 112 L340 164 L366 160 Z" fill="{EAR}"/></g>
  <path d="M112 118 L196 168 Q256 150 316 168 L400 118 Q442 250 420 330 Q392 438 256 442 Q120 438 92 330 Q70 250 112 118 Z" fill="{FUR}"/>
  <g stroke="{FUR_DARK}" stroke-width="15" stroke-linecap="round" fill="none">
    <path d="M256 176 L256 236"/><path d="M222 182 Q214 214 220 236"/><path d="M290 182 Q298 214 292 236"/>
    <path d="M96 296 L146 304"/><path d="M92 336 L142 336"/><path d="M416 296 L366 304"/><path d="M420 336 L370 336"/>
  </g>
  <ellipse cx="256" cy="372" rx="84" ry="62" fill="{MUZZLE}"/>
  <g class="blink"><ellipse cx="186" cy="290" rx="30" ry="34" fill="{EYE}"/><ellipse cx="186" cy="290" rx="7" ry="26" fill="#1a130c"/><circle cx="196" cy="276" r="7" fill="#fff"/></g>
  <g class="blink"><ellipse cx="326" cy="290" rx="30" ry="34" fill="{EYE}"/><ellipse cx="326" cy="290" rx="7" ry="26" fill="#1a130c"/><circle cx="336" cy="276" r="7" fill="#fff"/></g>
  <path d="M238 340 Q256 332 274 340 Q268 360 256 364 Q244 360 238 340 Z" fill="{EAR}" stroke="#c9736c" stroke-width="3" stroke-linejoin="round"/>
  <path d="M256 364 L256 378 M256 378 Q244 396 226 390 M256 378 Q268 396 286 390" fill="none" stroke="#5a3a28" stroke-width="5" stroke-linecap="round"/>
  <g stroke="{w}" stroke-width="4" stroke-linecap="round" fill="none" opacity="0.9">
    <path d="M176 366 L70 346"/><path d="M176 378 L66 384"/><path d="M180 390 L80 420"/>
    <path d="M336 366 L442 346"/><path d="M336 378 L446 384"/><path d="M332 390 L432 420"/>
  </g>
  <path d="M170 430 Q256 460 342 430 L338 454 Q256 484 174 454 Z" fill="{TEAL}"/>
  <circle cx="256" cy="488" r="24" fill="{TEAL}" stroke="{THEMES[t]['bg']}" stroke-width="4"/>
  <g stroke="#fff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" fill="none">
    <path d="M247 480 L239 488 L247 496"/><path d="M265 480 L273 488 L265 496"/><path d="M260 478 L252 498"/>
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
    body = f'<rect width="560" height="560" rx="96" fill="{THEMES[t]["bg"]}" opacity="0"/>\n' + cat(t, 24, 10, 1.0)
    return svg(560, 560, body, t, "Tabby", "A tabby cat's head with a teal collar and a code-bracket tag.")


def hero(t):
    c = THEMES[t]
    stripes = "".join(f'<path d="M{x} 0 L{x - 60} 360" stroke="{c["line"]}" stroke-width="26" opacity="0.55"/>' for x in range(760, 1500, 120))
    body = f"""<rect width="1280" height="360" rx="28" fill="{c['panel']}"/>
<clipPath id="r"><rect width="1280" height="360" rx="28"/></clipPath>
<g clip-path="url(#r)">{stripes}</g>
{cat(t, 70, -4, 0.66)}
<text x="470" y="170" font-family="'Segoe UI','Helvetica Neue',Arial,sans-serif" font-size="108" font-weight="800" fill="{c['ink']}" letter-spacing="-2">Tabby</text>
<text x="474" y="222" font-family="'Segoe UI','Helvetica Neue',Arial,sans-serif" font-size="30" fill="{c['muted']}">Agent skills for careful Python.</text>
<g font-family="'Segoe UI','Helvetica Neue',Arial,sans-serif" font-size="22" font-weight="600">
  <rect x="474" y="258" width="196" height="40" rx="20" fill="{TEAL}"/><text x="572" y="285" text-anchor="middle" fill="#fff">cause before fix</text>
  <rect x="682" y="258" width="190" height="40" rx="20" fill="{TEAL}"/><text x="777" y="285" text-anchor="middle" fill="#fff">small diffs</text>
  <rect x="884" y="258" width="210" height="40" rx="20" fill="{TEAL}"/><text x="989" y="285" text-anchor="middle" fill="#fff">tests stay green</text>
</g>"""
    return svg(1280, 360, body, t, "Tabby: agent skills for careful Python", "The Tabby cat beside the name and three habits: cause before fix, small diffs, tests stay green.")


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
