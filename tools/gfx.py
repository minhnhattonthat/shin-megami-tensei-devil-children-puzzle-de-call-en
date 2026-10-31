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
    for (x, y) in list(put) if outline is not None else []:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                put.setdefault((x + dx, y + dy), outline)
    for (x, y), v in put.items():
        if not (x_lo <= x <= x_hi and y_lo <= y <= y_hi):
            raise ValueError(f"{s!r}: pixel ({x},{y}) outside {area} (text {w + 2} px wide)")
        img[y][x] = v
    return w + 2


# ---- the labels -----------------------------------------------------------------------------------------------
# One dict per edited image: block, first tile `at` and `tiles` (default: the whole block), `cols` tiles per row;
# `erase` (indices, bg): those indices -> bg over the image; `clear`: [(x0, y0, x1, y1, bg)] rects; `text`:
# [(text, centre x, top row)] in `fill` with an `outline` ring (None: no ring), every pixel inside `area`.
PANEL = (3, 4, 5, 6, 7, 8, 9)  # title menus: black panel (15) with white (9) text, grey outline/shading (3-8)
LABELS = [
    # title menus (OBJ pal 4): each item shows only its JP band (rows 8-16 / 19-28 / 32-40 / 43-52; the cursor frame
    # covers the gaps), so a label is 9 rows: 7-row caps of the menu font + outline. Caps: no descender room.
    dict(block="title_menu", cols=8, erase=(PANEL, 15), fill=9, outline=4, area=(1, 5, 62, 58),
         text=[("STORY", 32, 9), ("PUZZLE", 32, 21), ("RACE", 32, 33), ("DEMONARY", 32, 44)]),
    # story submenu with no save file / with one (つづきから)
    dict(block="title_sub", cols=8, erase=(PANEL, 15), fill=9, outline=4, area=(1, 5, 62, 58),
         text=[("NEW GAME", 32, 19), ("TUTORIAL", 32, 34)]),
    dict(block="title_sub_hi", cols=8, erase=(PANEL, 15), fill=9, outline=4, area=(1, 5, 62, 58),
         text=[("NEW GAME", 32, 14), ("CONTINUE", 32, 27), ("TUTORIAL", 32, 40)]),
    # pause panel headers (OBJ pal 6, 64x8 strips of 32x8 sprites): white text on orange (13) / grey (8), rows 0-6
    dict(block="hud", at=0x86, tiles=16, cols=8, clear=[(0, 0, 62, 6, 13), (0, 8, 62, 14, 8)], fill=15,
         outline=None, area=(0, 0, 62, 14), text=[("Demon List", 31, 0), ("Demiloc", 31, 8)]),
]


def edit(lab, data, font):
    """data with the label's image redrawn."""
    at, cols = lab.get("at", 0), lab["cols"]
    n = lab.get("tiles", len(data) // 32 - at)
    img = to_img(data[at * 32:(at + n) * 32], cols)
    if "erase" in lab:
        idx, bg = lab["erase"]
        for row in img:
            for x, v in enumerate(row):
                if v in idx:
                    row[x] = bg
    for x0, y0, x1, y1, bg in lab.get("clear", []):
        for y in range(y0, y1 + 1):
            img[y][x0:x1 + 1] = [bg] * (x1 - x0 + 1)
    for s, cx, top in lab["text"]:
        draw(img, small_mask(s, font), cx, top, lab["fill"], lab["outline"], lab["area"], s)
    return data[:at * 32] + from_img(img, cols) + data[(at + n) * 32:]


def apply(lz):
    """lz = {block: (data, min_disp, end)} from blocks.unpack_lz, edited in place (font_small already English)."""
    font = lz["font_small"][0]
    for lab in LABELS:
        data, md, end = lz[lab["block"]]
        lz[lab["block"]] = (edit(lab, data, font), md, end)


def preview(out, z=3):
    """original | English of every label, greyscale by index."""
    import blocks
    import smallfont
    orig = (ROOT / "rom").glob("*.gba").__next__().read_bytes()
    font = smallfont.build(blocks.unpack_lz(orig, "font_small")[0])[0]
    pairs = []
    for lab in LABELS:
        data = blocks.unpack_lz(orig, lab["block"])[0]
        at, cols = lab.get("at", 0), lab["cols"]
        n = lab.get("tiles", len(data) // 32 - at)
        a = to_img(data[at * 32:(at + n) * 32], cols)
        b = to_img(edit(lab, data, font)[at * 32:(at + n) * 32], cols)
        pairs += [ra + [0] * 4 + rb for ra, rb in zip(a, b)] + [[0] * (len(a[0]) * 2 + 4)] * 4
    w = max(len(r) for r in pairs)
    rows = [[c for v in r + [0] * (w - len(r)) for c in (v * 17,) * 3 * z] for r in pairs for _ in range(z)]
    write_png(out, rows)
    print(out)


SHAPES = {(0, 0): (8, 8), (0, 1): (16, 16), (0, 2): (32, 32), (0, 3): (64, 64), (1, 0): (16, 8), (1, 1): (32, 8),
          (1, 2): (32, 16), (1, 3): (64, 32), (2, 0): (8, 16), (2, 1): (8, 32), (2, 2): (16, 32), (2, 3): (32, 64)}


def write_png(path, rgb_rows):
    import struct
    import zlib
    h, w = len(rgb_rows), len(rgb_rows[0]) // 3
    chunk = lambda k, d: struct.pack(">I", len(d)) + k + d + struct.pack(">I", zlib.crc32(k + d))  # noqa: E731
    raw = b"".join(b"\0" + bytes(r) for r in rgb_rows)
    Path(path).write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)) +
                           chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


def oam(prefix, outdir, zoom=3):
    """Every visible 4bpp sprite of a ppudump (PREFIX.oam/.vram/.pal.bin) as outdir/s<i>_x<x>y<y>_t<tile>_p<pal>.png
    (1D mapping), to see which sprite and tile range carries a label."""
    import struct
    o, v, p = (Path(f"{prefix}.{k}.bin").read_bytes() for k in ("oam", "vram", "pal"))
    Path(outdir).mkdir(parents=True, exist_ok=True)
    for i in range(128):
        a0, a1, a2 = struct.unpack_from("<HHH", o, i * 8)
        y, x, tile, pal = a0 & 255, a1 & 511, a2 & 1023, a2 >> 12
        if (a0 >> 8) & 3 == 2 or y >= 160 or x >= 240 or a0 & 0x2000:
            continue
        w, h = SHAPES[(a0 >> 14, a1 >> 14)]
        img = to_img(v[0x10000 + tile * 32:0x10000 + (tile + w * h // 64) * 32], w // 8)
        cols = [struct.unpack_from("<H", p, 0x200 + pal * 32 + k * 2)[0] for k in range(16)]
        rgb = [tuple((c >> s & 31) * 8 for s in (0, 5, 10)) if k else (255, 0, 255) for k, c in enumerate(cols)]
        rows = [[ch for px in r for ch in rgb[px] * zoom] for r in img for _ in range(zoom)]
        write_png(Path(outdir) / f"s{i:03}_x{x}y{y}_t{tile:03x}_p{pal}.png", rows)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "preview":
        preview(sys.argv[2])
    elif len(sys.argv) == 4 and sys.argv[1] == "oam":
        oam(sys.argv[2], sys.argv[3])
    else:
        sys.exit(__doc__)
