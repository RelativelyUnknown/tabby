#!/usr/bin/env python3
"""outline_font.py: turn a font's glyphs into SVG path data, so the README images need no font at display time.

    python3 tools/outline_font.py FONT.ttf OUT.json [--weight 700]

Needs fontTools (a development-time dependency of this script only; `pip install fonttools`). Writes, for every printable ASCII
character, its advance width and outline as a path in font units (y up), plus units-per-em, ascender and descender.
`tools/readme_assets.py` reads the JSON, so it stays standard-library only.
"""
import json
import sys

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 1
    font_path, out = argv[0], argv[1]
    weight = int(argv[argv.index("--weight") + 1]) if "--weight" in argv else 500
    font = TTFont(font_path)
    if "fvar" in font:
        axes = {a.axisTag: a.defaultValue for a in font["fvar"].axes}
        axes["wght"] = weight
        font = instantiateVariableFont(font, axes)
    glyphs, cmap, hmtx = font.getGlyphSet(), font.getBestCmap(), font["hmtx"]
    data = {"upm": font["head"].unitsPerEm, "ascender": font["hhea"].ascent, "descender": font["hhea"].descent, "glyphs": {}}
    for code in range(32, 127):
        name = cmap.get(code)
        if not name:
            continue
        pen = SVGPathPen(glyphs)
        glyphs[name].draw(pen)
        data["glyphs"][chr(code)] = {"adv": hmtx[name][0], "d": pen.getCommands()}
    json.dump(data, open(out, "w"), separators=(",", ":"))
    print(f"wrote {out}: {len(data['glyphs'])} glyphs at weight {weight}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
