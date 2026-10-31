"""English 8x8 menu font: the game's small font (LZ 0x161FD0, 32 bytes per code) with fonts/small.txt glyphs added at
their tbl/en.tbl codes, every English glyph moved to the tile's left edge, and an advance per code for the
proportional menu printer (asm/vwf.s small_char).

    python -X utf8 tools/smallfont.py [TEXT]     # selftest, or TEXT's width in px
The multiboot client's copy (LZ 0x337B10) only gets the new glyphs: its printer is the game's fixed 8 px one.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import vwf  # noqa: E402

SPACE = 3  # advance of the space
LEFT = 1  # first ink column of every English glyph (col 0 fell outside the menu highlight bar: "Yes" read "Ses")


def _get(f, c):
    return [[(f[c * 32 + y * 4 + x // 2] >> (4 * (x & 1))) & 15 for x in range(8)] for y in range(8)]


def _put(f, c, px):
    for y in range(8):
        for x in range(0, 8, 2):
            f[c * 32 + y * 4 + x // 2] = px[y][x] | (px[y][x + 1] << 4)


def build(font, normalize=True):
    """(new font bytes, 256 advances) from the game's decompressed small font."""
    f, codes = bytearray(font), vwf.en_codes()
    for ch, rows in vwf.glyphs(ROOT / "fonts" / "small.txt").items():
        assert len(rows) <= 8 and max(map(len, rows)) <= 8, ch
        _put(f, codes[ch], [[1 if y < len(rows) and x < len(rows[y]) and rows[y][x] == "#" else 0
                             for x in range(8)] for y in range(8)])
    width = bytearray(256)
    for ch, c in codes.items():
        px = _get(f, c)
        cols = [x for x in range(8) if any(px[y][x] for y in range(8))]
        if not cols:
            width[c] = SPACE
            continue
        if normalize and cols[0] != LEFT:  # ink from col LEFT: menu highlight bars start 1 px into the tile
            assert cols[-1] - cols[0] < 8 - LEFT, ch
            px = [[0] * LEFT + row[cols[0]:] + [0] * cols[0] for row in px]
            px = [row[:8] for row in px]
            _put(f, c, px)
        width[c] = cols[-1] - cols[0] + 2
    return bytes(f), bytes(width)


_W = None


def width(s):
    global _W
    if _W is None:
        import blocks
        _W = build(blocks.unpack_lz(build_rom(), "font_small")[0])[1]
    codes = vwf.en_codes()
    return sum(_W[codes[c]] for c in s)


def build_rom():
    return next((ROOT / "rom").glob("*.gba")).read_bytes()


if __name__ == "__main__":
    import blocks
    f, w = build(blocks.unpack_lz(build_rom(), "font_small")[0])
    c = vwf.en_codes()
    assert w[c["A"]] == 7 and w[c["i"]] == 2 and w[c[" "]] == SPACE, (w[c["A"]], w[c["i"]])
    if len(sys.argv) > 1:
        print(width(sys.argv[1]))
    else:
        print("selftest ok")
