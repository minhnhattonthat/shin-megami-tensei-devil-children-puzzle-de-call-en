"""Graphics text: English labels drawn into the LZ graphics blocks (docs/re/graphics.md "Redrawn"). build.py calls
apply(lz) with the unpacked LZ blocks; `python -X utf8 tools/gfx.py preview OUT.png` renders every edited block
(original | English, 3x) for a look before a build.

Lettering: the game's 8x8 menu font with the English glyphs of fonts/small.txt (the font_small block as
asm.edit_lz leaves it), outlined (8-neighbour ring), optionally bold. One style per label class (LABELS).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import vwf  # noqa: E402


# ---- 4bpp sprite images (GBA 1D OBJ mapping: tiles row-major, `cols` tiles per row) -------------------------------
def to_img(data, cols):
    rows = len(data) // 32 // cols
    img = [[0] * (cols * 8) for _ in range(rows * 8)]
    for t in range(len(data) // 32):
        for r in range(8):
            for c in range(8):
                v = data[t * 32 + r * 4 + c // 2]
                img[(t // cols) * 8 + r][(t % cols) * 8 + c] = (v >> 4) if c & 1 else v & 15
    return img


def from_img(img, cols):
    out = bytearray(len(img) * len(img[0]) // 2)
    for y, row in enumerate(img):
        for x, v in enumerate(row):
            t = (y // 8) * cols + x // 8
            i = t * 32 + (y % 8) * 4 + (x % 8) // 2
            out[i] |= v << 4 if x & 1 else v
    return bytes(out)


# ---- lettering ------------------------------------------------------------------------------------------------
def small_mask(s, font, bold=False):
    """Text in the game's 8x8 menu font (font = the edited font_small block): rows 0-7, cap top row 0."""
    codes, mask = vwf.en_codes(), [[] for _ in range(8)]
    for i, ch in enumerate(s):
        c = codes[ch]
        px = [[(font[c * 32 + y * 4 + x // 2] >> (4 * (x & 1))) & 15 for x in range(8)] for y in range(8)]
        cols = [x for x in range(8) if any(px[y][x] for y in range(8))]
        w = (cols[-1] + 1 if cols else 2) + bold
        for y in range(8):
            row = [1 if (x < 8 and px[y][x]) or (bold and x and px[y][x - 1]) else 0 for x in range(w)]
            mask[y] += row + ([0] if i < len(s) - 1 else [])
    while not any(r[-1] for r in mask):
        for r in mask:
            r.pop()
    return mask


def draw(img, m, cx, top, fill, outline, area, s=""):
    """Outlined text mask centred on column cx, top row at top; only pixels inside area (x0, y0, x1, y1)."""
    w = len(m[0])
    x0 = cx - w // 2
    x_lo, y_lo, x_hi, y_hi = area
    put = {}
    for y, row in enumerate(m):
        for x, v in enumerate(row):
            if v:
                put[(x0 + x, top + y)] = fill
    for (x, y) in list(put):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                put.setdefault((x + dx, y + dy), outline)
    for (x, y), v in put.items():
        if not (x_lo <= x <= x_hi and y_lo <= y <= y_hi):
            raise ValueError(f"{s!r}: pixel ({x},{y}) outside {area} (text {w + 2} px wide)")
        img[y][x] = v
    return w + 2


# ---- the labels -----------------------------------------------------------------------------------------------
# block: (tiles per row, erase: indices that are text in the original -> background index, [(text, centre x, cap
# top y)], fill, outline, drawable area)
PANEL = (3, 4, 5, 6, 7, 8, 9)  # title menus: black panel (15) with white (9) text, grey outline/shading (3-8)
# title menus: each item shows only its JP band (rows 8-16 / 19-28 / 32-40 / 43-52; the cursor frame covers the
# gaps), so the label is 9 rows: 7-row caps of the menu font + outline. Caps only (no descender room).
LABELS = {
    "title_menu": (8, PANEL, 15, [("STORY", 32, 9), ("PUZZLE", 32, 21), ("RACE", 32, 33), ("DEMONARY", 32, 44)],
                   9, 4, (1, 5, 62, 58)),
    "title_sub": (8, PANEL, 15, [("NEW GAME", 32, 19), ("TUTORIAL", 32, 34)], 9, 4, (1, 5, 62, 58)),
    "title_sub_hi": (8, PANEL, 15, [("NEW GAME", 32, 14), ("CONTINUE", 32, 27), ("TUTORIAL", 32, 40)], 9, 4,
                     (1, 5, 62, 58)),
}


def edit(name, data, font):
    cols, erase, bg, items, fill, outline, area = LABELS[name]
    img = to_img(data, cols)
    for row in img:
        for x, v in enumerate(row):
            if v in erase:
                row[x] = bg
    for s, cx, top in items:
        draw(img, small_mask(s, font, BOLD), cx, top, fill, outline, area, s)
    return from_img(img, cols)


BOLD = False


def apply(lz):
    """lz = {block: (data, min_disp, end)} from blocks.unpack_lz, edited in place (font_small already English)."""
    font = lz["font_small"][0]
    for name in LABELS:
        data, md, end = lz[name]
        lz[name] = (edit(name, data, font), md, end)


def preview(out):
    import blocks
    import struct
    import zlib
    import smallfont
    orig = (ROOT / "rom").glob("*.gba").__next__().read_bytes()
    font = smallfont.build(blocks.unpack_lz(orig, "font_small")[0])[0]
    grey = [0, 255, 0, 40, 70, 150, 180, 210, 230, 255, 0, 0, 0, 0, 0, 20]
    tiles = []
    for name in LABELS:
        data = blocks.unpack_lz(orig, name)[0]
        a, b = to_img(data, LABELS[name][0]), to_img(edit(name, data, font), LABELS[name][0])
        tiles.append([ra + [0] * 4 + rb for ra, rb in zip(a, b)])
    z = 3
    w = max(len(t[0]) for t in tiles)
    rows = []
    for t in tiles:
        for r in t + [[0] * len(t[0])] * 4:
            line = bytes(grey[v] if (v or True) else 0 for v in r + [0] * (w - len(r)))
            line = b"".join(bytes([p]) * z for p in line)
            rows += [line] * z
    raw = b"".join(b"\0" + r for r in rows)
    png = b"\x89PNG\r\n\x1a\n"
    chunk = lambda k, d: struct.pack(">I", len(d)) + k + d + struct.pack(">I", zlib.crc32(k + d))  # noqa: E731
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", w * z, len(rows), 8, 0, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")
    Path(out).write_bytes(png)
    print(out)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "preview":
        preview(sys.argv[2])
    else:
        sys.exit(__doc__)
