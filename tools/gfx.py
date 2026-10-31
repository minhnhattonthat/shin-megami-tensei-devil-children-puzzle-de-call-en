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
def to_img(data, cols, bpp=4):
    ts = 8 * bpp
    rows = len(data) // ts // cols
    img = [[0] * (cols * 8) for _ in range(rows * 8)]
    for t in range(len(data) // ts):
        for r in range(8):
            for c in range(8):
                if bpp == 8:
                    v = data[t * 64 + r * 8 + c]
                else:
                    v = data[t * 32 + r * 4 + c // 2]
                    v = (v >> 4) if c & 1 else v & 15
                img[(t // cols) * 8 + r][(t % cols) * 8 + c] = v
    return img


def from_img(img, cols, bpp=4):
    out = bytearray(len(img) * len(img[0]) * bpp // 8)
    for y, row in enumerate(img):
        for x, v in enumerate(row):
            t = (y // 8) * cols + x // 8
            if bpp == 8:
                out[t * 64 + (y % 8) * 8 + x % 8] = v
            else:
                out[t * 32 + (y % 8) * 4 + (x % 8) // 2] |= v << 4 if x & 1 else v
    return bytes(out)


# ---- lettering ------------------------------------------------------------------------------------------------
def small_mask(s, font, bold=False):
    """Text in the game's 8x8 menu font (font = the edited font_small block): rows 0-7, cap top row 0."""
    codes, mask = vwf.en_codes(), [[] for _ in range(8)]
    for i, ch in enumerate(s):
        c = codes[ch]
        px = [[(font[c * 32 + y * 4 + x // 2] >> (4 * (x & 1))) & 15 for x in range(8)] for y in range(8)]
        cols = [x for x in range(8) if any(px[y][x] for y in range(8))]
        x0 = cols[0] if cols else 0  # glyphs sit at col smallfont.LEFT; labels start at the ink
        w = (cols[-1] + 1 if cols else 2) + bold
        for y in range(8):
            row = [1 if (x < 8 and px[y][x]) or (bold and x and px[y][x - 1]) else 0 for x in range(x0, w)]
            mask[y] += row + ([0] if i < len(s) - 1 else [])
    while not any(r[-1] for r in mask):
        for r in mask:
            r.pop()
    return mask


def tiny_mask(s):
    """Text in fonts/tiny.txt (5-row caps), 1 px between letters."""
    g, mask = vwf.glyphs(ROOT / "fonts" / "tiny.txt"), [[] for _ in range(5)]
    for i, ch in enumerate(s):
        rows = g[ch]
        w = max(map(len, rows))
        for y in range(5):
            r = rows[y] if y < len(rows) else ""
            mask[y] += [1 if x < len(r) and r[x] == "#" else 0 for x in range(w)] + ([0] if i < len(s) - 1 else [])
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
    # character select (8bpp BG0, map rows 0-3 = tiles 1-0x78, rows 16-17 = tiles 0x97-0xD2, 30 per row): shaded
    # plates repainted row by row, text in the VWF font, bold
    dict(block="charselect", at=1, tiles=120, cols=30, bpp=8, plate=[(45, 6, 196, 17)], font="vwf", bold=True,
         fill=0x1F, outline=None, area=(45, 5, 196, 19), text=[("Character Select", 120, 7)]),
    dict(block="charselect", at=0x97, tiles=60, cols=30, bpp=8, plate=[(8, 5, 80, 14), (159, 5, 228, 14)],
         font="vwf", bold=True, fill=0x12, outline=None, area=(8, 4, 228, 14), text=[("Rand", 44, 5), ("Gale", 193, 5)]),
    # puzzle mode select (8bpp BG0 of puzzle_select; map E000): banner tiles = map rows 0-2 cols 9-20, brown plate
    # 0x3F, white 0x7F with a dark 0x31 ring
    dict(block="puzzle_select", grid=[(0x0A, 12), (0x24, 12), (0x3F, 12)], bpp=8, clear=[(8, 4, 87, 14, 0x3F)],
         font="vwf", fill=0x7F, outline=0x31, area=(8, 4, 87, 14), text=[("Puzzle Mode", 48, 5)]),
    # DeviDas (OBJ pal 14): title banner, two 32x16 sprites = tiles 0-15 of bold_kana (light 14, ring 12)
    dict(block="bold_kana", tiles=16, cols=4, sprites=2, clear=[(0, 0, 63, 15, 0)], font="vwf", bold=True, fill=14,
         outline=12, area=(0, 0, 63, 15), text=[("Demonary", 32, 2)]),
    # info labels, one 32x32 sprite (white 1); official DemiKids Class / Type / Align
    dict(block="devidas_labels", cols=4, clear=[(0, 0, 31, 31, 0)], fill=1, outline=None, left=True,
         area=(0, 0, 31, 31), text=[("Class", 0, 0), ("Type", 0, 10), ("Align", 0, 21)]),
] + [
    # floor start / clear call-outs: 64x16 as two 32x16 OBJ (white 1, ring 7); copies in the story HUD set, the
    # puzzle-mode OBJ set and the tail of outlined_kata
    dict(block=b, at=at, tiles=16, cols=4, sprites=2, clear=[(0, 0, 63, 15, 0)], font="vwf", bold=True, fill=1,
         outline=7, area=(0, 0, 63, 15), text=[(s, 32, 3)])
    for b, at, s in [("hud", 0x58, "Clear!!"), ("hud", 0x68, "Start!"), ("hud_puzzle_obj", 0x14, "Clear!!"),
                     ("hud_puzzle_obj", 0x24, "Start!"), ("outlined_kata", 0x200, "Clear!!")]
] + [
    # puzzle stage card (hud_puzzle_obj, 64x16 each): difficulty plate (white 15 on stripes 11 / 6, rows 2-13)
    dict(block="hud_puzzle_obj", at=at, tiles=16, cols=4, sprites=2, font="vwf", bold=True, fill=15, outline=None,
         clear=[(6 if y == 2 else 5, y, 58 if y < 12 else 57, y, 11 if y % 2 == 0 else 6) for y in range(2, 14)],
         area=(5, 2, 57, 13),
         text=[(s, 31, 3)])
    for at, s in [(0xC2, "Easy"), (0xD2, "Normal"), (0xE2, "Hard")]
] + [
    # "ステージ" before the stage number sprite (drawn at x + 60): white 15, ring 6, on 0
    dict(block="hud_puzzle_obj", at=0xF2, tiles=16, cols=4, sprites=2, clear=[(0, 0, 63, 15, 0)], font="vwf",
         bold=True, fill=15, outline=6, area=(0, 0, 63, 15), text=[("Stage", 38, 3)]),
] + [
    # class / type values: 32x16 sprites (8 tiles each), white 1 + shadow 11, left aligned; 5-row caps (GENERAL,
    # THUNDER: 30 px + shadow)
    dict(block="devidas_values", at=8 * k, tiles=8, cols=4, clear=[(0, 0, 31, 15, 0)], font="tiny", fill=1,
         shadow=11, outline=None, left=True, area=(0, 0, 31, 15), text=[(s, 0, 1)])
    for k, s in enumerate(["COMMON", "ELITE", "GENERAL", "KING", "GOOD", "EVIL", "HOLY", "DRAGON", "BIRD", "BEAST",
                           "OGRE", "GHOST", "FIEND", "ALT", "ZOMBIE", "BOSS", "MYTH"])
] + [
    # align (element): 4 tiles each, drawn as 32x8 (asm hook 0x01CADA turns the 16x16 sprite into 32x8)
    dict(block="devidas_elements", at=4 * k, tiles=4, cols=4, clear=[(0, 0, 31, 7, 0)], font="tiny", fill=1,
         shadow=11, outline=None, left=True, area=(0, 0, 31, 7), text=[(s, 0, 1)])
    for k, s in enumerate(["FIRE", "WATER", "ICE", "THUNDER", "EARTH", "WIND", "LIGHT", "DARK"])
] + [
    # race mode banner (8bpp BG1 of race, map E800 rows 0-1 cols 7-21), between the two bullets (the red flourish
    # under テド goes with the lettering)
    dict(block="race", grid=[(0x05, 15), (0x1A, 15)], bpp=8, font="vwf", bold=True, fill=0x7E, outline=0x14,
         clear=[(20, 0, 100, 15, 0x01), (101, 14, 102, 15, 0x01)], area=(20, 0, 99, 15),
         text=[("Race Mode", 60, 3)]),
    # difficulty headers, green 0x73 on 0x07, map rows 7-8; ふつう cols 12-17, かんたん cols 2-8, むずかしい cols 21-28
    # (cols 26 / 27 are tile 0x63 and its mirror: blanked, the text stays in cols 21-25)
] + [dict(block="puzzle_select", grid=g, bpp=8, erase=((0x73,), 0x07), font="vwf", fill=0x73, outline=None,
          area=(0, 0, g[0][1] * 8 - 1, 8 * len(g) - 1), text=t)
     # top row 3: the selected header's cursor frame covers row 2
     for g, t in [([(0x51, 7), (0x67, 7)], [("Easy", 26, 3)]), ([(0x58, 6), (0x71, 6)], [("Normal", 24, 3)]),
                  ([(0x5E, 5), (0x7A, 5)], [("Hard", 20, 3)]), ([(0x63, 2)], []), ([(0x7F, 3)], [])]] + [
    # stage HUD labels (OBJ pal 6/7, 32x8 sprites, the count follows at x + 32): white (15) with a black (11) ring
] + [dict(block=b, at=at, tiles=n, cols=n, clear=[(0, 0, n * 8 - 1, 7, 0)], font="tiny", fill=15, outline=11,
          area=(0, 0, n * 8 - 1, 7), text=[(s, n * 4 - 1, 1)])
     for b, at, n, s in [("hud", 0xBB, 4, "MOVES"), ("hud", 0xBF, 4, "TIME"), ("hud", 0xC3, 4, "LIFE"),
                         ("hud", 0xC7, 8, "DEFEATED"), ("hud", 0xCF, 4, "EGGS"),
                         # puzzle select record: スコア タイム てかず. Only the raw copy is read (the LZ copy
                         # hud_puzzle 0x2AADE0 has no pointer and no room for SCORE: left as is)
                         ("hud_puzzle_raw", 0, 4, "SCORE"), ("hud_puzzle_raw", 4, 4, "TIME"),
                         ("hud_puzzle_raw", 8, 4, "MOVES"),
                         # the OBJ set puzzle mode loads (LZ 0x219630, whole block at OBJ VRAM 0x10000)
                         ("hud_puzzle_obj", 0xA0, 4, "MOVES"), ("hud_puzzle_obj", 0xA4, 4, "TIME"),
                         ("hud_puzzle_obj", 0xA8, 4, "LIFE"), ("hud_puzzle_obj", 0xAC, 4, "BEST"),
                         ("hud_puzzle_obj", 0xB0, 4, "SCORE")]]


def edit(lab, data, font):
    """data with the label's image redrawn. `grid`: [(first tile, count)] per tile row, for a BG region whose rows
    are separate tile runs (all rows the same count; replaces at / tiles / cols)."""
    bpp = lab.get("bpp", 4)
    ts = 8 * bpp
    if "grid" in lab:
        seq = [t for first, n in lab["grid"] for t in range(first, first + n)]
        sub = {k: v for k, v in lab.items() if k != "grid"}
        new = edit(dict(sub, at=0, tiles=len(seq), cols=lab["grid"][0][1]),
                   b"".join(data[t * ts:(t + 1) * ts] for t in seq), font)
        out = bytearray(data)
        for i, t in enumerate(seq):
            out[t * ts:(t + 1) * ts] = new[i * ts:(i + 1) * ts]
        return bytes(out)
    at, cols = lab.get("at", 0), lab["cols"]
    n = lab.get("tiles", len(data) // ts - at)
    img = to_img(data[at * ts:(at + n) * ts], cols, bpp)
    sp = lab.get("sprites", 1)  # several OBJ side by side: their tiles follow each other, so they load stacked
    h = len(img) // sp
    img = [sum((img[k * h + y] for k in range(sp)), []) for y in range(h)]
    for x0, y0, x1, y1 in lab.get("plate", []):  # shaded plates: each row of the rect -> the commonest value of its
        for y in range(y0, y1 + 1):              # 3 end columns on each side (outside the lettering)
            ref = img[y][x0:x0 + 3] + img[y][x1 - 2:x1 + 1]
            img[y][x0:x1 + 1] = [max(ref, key=ref.count)] * (x1 - x0 + 1)
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
        f = lab.get("font")
        m = tiny_mask(s) if f == "tiny" else vwf_mask(s, lab.get("bold")) if f == "vwf" else small_mask(s, font)
        if lab.get("left"):  # cx is the left edge
            cx += len(m[0]) // 2
        if "shadow" in lab:  # 1 px to the right, under the text
            draw(img, m, cx + 1, top, lab["shadow"], None, lab["area"], s)
        draw(img, m, cx, top, lab["fill"], lab["outline"], lab["area"], s)
    img = [r[k * cols * 8:(k + 1) * cols * 8] for k in range(sp) for r in img]
    return data[:at * ts] + from_img(img, cols, bpp) + data[(at + n) * ts:]


# ---- area start cards (outlined_kata 0x2800 + i * 0x400: 128x16 as four 32x16 OBJ, white 15 / ring 6 on a
# striped banner 11 / 6). Names: atwiki devilchildren_pdc (エンベルの泉 ルコッピア草原 プレクト火山 タルタロスの樹海
# フィーヨルグ雪原 クァドリガ), glossary.md Places.
CARDS = ["Embel Spring", "Lucoppia Plain", "Plekt Volcano", "Tartarus Sea of Trees", "Fjorgyn Snowfield", "Quadriga"]
CARD_AT = 0x2800


def card_img(data, i):
    sp = to_img(data[CARD_AT + i * 0x400:CARD_AT + (i + 1) * 0x400], 4)  # the 4 sprites, stacked
    return [sum((sp[k * 16 + y] for k in range(4)), []) for y in range(16)]


def card_bytes(img):
    return b"".join(from_img([r[k * 32:(k + 1) * 32] for r in img], 4) for k in range(4))


def card_banner(cards):
    """The empty banner: per pixel, the commonest value over the cards where no text (15) or its ring touches."""
    from collections import Counter
    out = [[0] * 128 for _ in range(16)]
    for y in range(16):
        for x in range(128):
            near = lambda c: any(c[yy][xx] == 15 for yy in range(max(0, y - 1), min(16, y + 2))  # noqa: E731
                                 for xx in range(max(0, x - 1), min(128, x + 2)))
            vals = Counter(c[y][x] for c in cards if not near(c))
            # covered by text on every card: the stripe of rows 2-11 (11 on even rows, 6 on odd), else empty
            out[y][x] = vals.most_common(1)[0][0] if vals else ((11, 6)[y & 1] if 2 <= y <= 11 else 0)
    return out


def vwf_mask(s, bold=False):
    """Text in fonts/vwf.txt (cap top row 0, baseline row 8, descenders 9-10), 1 px between letters; bold: each
    glyph smeared 1 px right."""
    g, mask = vwf.glyphs(), [[] for _ in range(11)]
    for i, ch in enumerate(s):
        rows = g[ch]
        w = max(map(len, rows))
        for y in range(11):
            r = rows[y] if y < len(rows) else ""
            px_ = [1 if x < len(r) and r[x] == "#" else 0 for x in range(w)]
            if bold:
                px_ = [a | b for a, b in zip(px_ + [0], [0] + px_)]
            mask[y] += px_ + ([0] if i < len(s) - 1 else [])
    return mask


def cards(data):
    imgs = [card_img(data, i) for i in range(len(CARDS))]
    bg = card_banner(imgs)
    for i, s in enumerate(CARDS):
        img = [r[:] for r in bg]
        draw(img, vwf_mask(s), 64, 2, 15, 6, (0, 0, 127, 15), s)
        data = data[:CARD_AT + i * 0x400] + card_bytes(img) + data[CARD_AT + (i + 1) * 0x400:]
    return data


def apply(lz):
    """lz = {block: (data, min_disp, end)} from blocks.unpack_lz, edited in place (font_small already English)."""
    font = lz["font_small"][0]
    for lab in LABELS:
        data, md, end = lz[lab["block"]]
        lz[lab["block"]] = (edit(lab, data, font), md, end)
    data, md, end = lz["outlined_kata"]
    lz["outlined_kata"] = (cards(data), md, end)


def preview(out, z=3):
    """original | English of every label, greyscale by index."""
    import blocks
    import smallfont
    orig = (ROOT / "rom").glob("*.gba").__next__().read_bytes()
    font = smallfont.build(blocks.unpack_lz(orig, "font_small")[0])[0]
    pairs = []
    for lab in LABELS:
        data = blocks.unpack_lz(orig, lab["block"])[0]
        at, cols, bpp = lab.get("at", 0), lab["cols"], lab.get("bpp", 4)
        ts = 8 * bpp
        n = lab.get("tiles", len(data) // ts - at)
        a = to_img(data[at * ts:(at + n) * ts], cols, bpp)
        b = to_img(edit(lab, data, font)[at * ts:(at + n) * ts], cols, bpp)
        if bpp == 8:  # greyscale by index below: fold 8bpp to 0-15
            a, b = ([[v >> 4 for v in r] for r in im] for im in (a, b))
        pairs += [ra + [0] * 4 + rb for ra, rb in zip(a, b)] + [[0] * (len(a[0]) * 2 + 4)] * 4
    kata = blocks.unpack_lz(orig, "outlined_kata")[0]
    new = cards(kata)
    for i in range(len(CARDS)):
        pairs += [ra + [0] * 4 + rb for ra, rb in zip(card_img(kata, i), card_img(new, i))] + [[0] * 260] * 2
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
