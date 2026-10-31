"""English variable-width font for the 16x16 text boxes: fonts/vwf.txt -> the engine's tables (asm/vwf.s).

    python -X utf8 tools/vwf.py [TEXT]     # selftest, or print TEXT's width in px
Glyphs are drawn rows of '#' (body, colour 1) in fonts/vwf.txt; this adds the colour-2 shadow at (+1, +1), places
row 0 at cell row TOP, and gives each glyph an advance of width + 1 (the shadow column). Codes: tbl/en.tbl.
width() is what the wrap check uses, so the line limits in docs/re/vwf.md are in these pixels.
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOP = 3  # cell row of the cap line: rows 3-11 caps, 12-13 descenders, 14 shadow
SHADOW = 2


def en_codes():
    """{char: code} from tbl/en.tbl."""
    out = {}
    for line in (ROOT / "tbl" / "en.tbl").read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#"):
            k, _, v = line.partition("=")
            out[" " if v == r"\s" else v] = int(k, 16)
    return out


def glyphs(path=ROOT / "fonts" / "vwf.txt"):
    """{char: [row strings]} from a glyph file (fonts/vwf.txt, fonts/small.txt)."""
    out, cur = {}, None
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):  # comment (glyph rows have no spaces)
            continue
        if line.startswith("== "):
            name = line[3:]
            cur = out[" " if name == "space" else name] = []
        elif line.strip() and cur is not None:
            cur.append(line.strip())
    return out


def tables():
    """(width: 256 bytes of advances, font: 256 x 64 bytes) for asm/vwf.s."""
    codes, gl = en_codes(), glyphs()
    missing = set(codes) - set(gl)
    if missing:
        raise ValueError(f"fonts/vwf.txt lacks {sorted(missing)}")
    width, font = bytearray(256), bytearray(256 * 64)
    for ch, rows in gl.items():
        code = codes[ch]
        w = max(len(r) for r in rows)
        assert len(rows) <= 11 and w <= 14, ch
        px = [[0] * 16 for _ in range(16)]
        for y, r in enumerate(rows):
            for x, c in enumerate(r):
                if c == "#":
                    px[TOP + y][x] = 1
        for y in range(15, 0, -1):
            for x in range(15, 0, -1):
                if not px[y][x] and px[y - 1][x - 1] == 1:
                    px[y][x] = SHADOW
        width[code] = w + 1
        for y in range(16):
            font[code * 64 + y * 4:code * 64 + y * 4 + 4] = struct.pack("<I", sum(v << (2 * x) for x, v in enumerate(px[y])))
    return bytes(width), bytes(font)


_W = None


def width(s):
    """Pixel width of plain English text (no control codes)."""
    global _W
    if _W is None:
        _W = (en_codes(), tables()[0])
    codes, w = _W
    return sum(w[codes[c]] for c in s)


if __name__ == "__main__":
    w, f = tables()
    assert w[en_codes()["A"]] == 6 and w[en_codes()[" "]] == 4
    assert width("Hello") == 6 + 6 + 3 + 3 + 6, width("Hello")
    if len(sys.argv) > 1:
        print(width(sys.argv[1]))
    else:
        print("selftest ok")
