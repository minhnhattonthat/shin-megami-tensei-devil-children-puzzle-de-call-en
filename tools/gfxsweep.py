"""Static graphics sweep: render ROM ranges and every LZ77 block as labelled 4bpp (GBA linear) greyscale sheets.

    python -X utf8 tools/gfxsweep.py raw LO HI OUTDIR [--chunk 0x8000] [--zoom 2] [--bpp 4|8]   # one sheet per chunk
    python -X utf8 tools/gfxsweep.py lz OUTDIR [--zoom 2] [--maxh 1400] [--bpp 4|8] [--min HEXSIZE]
                                                                                   # all blocks in work/lzscan.txt
Blocks are listed in OUTDIR/index.txt (sheet, block offset, size, kind). Blocks that look like palettes
(<= 512 bytes, every u16 < 0x8000) or tilemaps (u16 entries, tile index < 0x400 for > 95%) are rendered too but tagged,
and every block that could not be decoded is printed with the reason: nothing is skipped silently.
"""
import struct
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from lz77 import decompress  # noqa: E402

COLS = 32
LABEL_W = 64


def rom():
    return next((ROOT / "rom").glob("*.gba")).read_bytes()


def tiles_img(data, zoom, bpp=4):
    """GBA linear tiles (4 or 8 bpp), 32 per row, index 0 white."""
    tb = 8 * bpp
    n = len(data) // tb
    rows = (n + COLS - 1) // COLS
    img = Image.new("L", (COLS * 8, max(rows, 1) * 8), 255)
    px = img.load()
    for t in range(n):
        tx, ty = (t % COLS) * 8, (t // COLS) * 8
        base = t * tb
        for y in range(8):
            for x in range(8):
                if bpp == 8:
                    v = data[base + y * 8 + x]
                    px[tx + x, ty + y] = 255 - (v * 37) % 256 if v else 255
                    continue
                b = data[base + y * 4 + x // 2]
                v = b >> 4 if x & 1 else b & 0xF
                px[tx + x, ty + y] = 255 - v * 17
    if zoom != 1:
        img = img.resize((img.width * zoom, img.height * zoom), Image.NEAREST)
    return img


def kind(data):
    if len(data) % 2:
        return "odd"
    w = struct.unpack("<%dH" % (len(data) // 2), data)
    if len(data) <= 512 and all(v < 0x8000 for v in w):
        return "palette?"
    if sum(1 for v in w if (v & 0x3FF) < 0x200) > 0.95 * len(w) and len(set(w)) > 4:
        return "map?"
    return "tiles"


def labelled(img, zoom, off0, step_bytes):
    """Add a left margin with the offset of every 8th tile row."""
    out = Image.new("RGB", (img.width + LABEL_W, img.height), (255, 255, 255))
    out.paste(img.convert("RGB"), (LABEL_W, 0))
    dr = ImageDraw.Draw(out)
    row_h = 8 * zoom
    for r in range(0, img.height // row_h, 4):
        dr.text((2, r * row_h), "%06X" % (off0 + r * step_bytes), fill=(200, 0, 0))
        dr.line((LABEL_W - 4, r * row_h, LABEL_W, r * row_h), fill=(200, 0, 0))
    return out


def cmd_raw(lo, hi, outdir, chunk, zoom, bpp):
    d = rom()
    outdir.mkdir(parents=True, exist_ok=True)
    for a in range(lo, hi, chunk):
        b = min(a + chunk, hi)
        img = labelled(tiles_img(d[a:b], zoom, bpp), zoom, a, COLS * 8 * bpp)
        img.save(outdir / ("raw_%06X.png" % a))
    print("raw sheets:", (hi - lo + chunk - 1) // chunk, "->", outdir)


def cmd_lz(outdir, zoom, maxh, bpp=4, minsize=0):
    d = rom()
    outdir.mkdir(parents=True, exist_ok=True)
    blocks = []
    for line in (ROOT / "work" / "lzscan.txt").read_text().splitlines():
        p = line.split()
        if int(p[1][5:], 16) < minsize:
            print("skip %s: smaller than --min" % p[0])
            continue
        blocks.append(int(p[0], 16))
    index, sheet, parts, h, sn = [], None, [], 0, 0

    def flush():
        nonlocal parts, h, sn
        if not parts:
            return
        w = max(p.width for p in parts)
        img = Image.new("RGB", (w, sum(p.height for p in parts)), (255, 255, 255))
        y = 0
        for p in parts:
            img.paste(p, (0, y)); y += p.height
        img.save(outdir / ("lz_%03d.png" % sn))
        parts, h, sn = [], 0, sn + 1

    for off in blocks:
        try:
            data, _ = decompress(d, off)
        except ValueError as e:
            print("skip %06X: %s" % (off, e)); continue
        k = kind(data) + ("" if bpp == 4 else " 8bpp")
        img = tiles_img(data, zoom, bpp)
        head = Image.new("RGB", (img.width + LABEL_W, 14), (255, 255, 200))
        ImageDraw.Draw(head).text((2, 1), "LZ %06X size %X %s" % (off, len(data), k), fill=(0, 0, 160))
        body = labelled(img, zoom, 0, COLS * 8 * bpp)
        if h and h + body.height + 14 > maxh:
            flush()
        parts += [head, body]; h += body.height + 14
        index.append("lz_%03d.png %06X %X %s" % (sn, off, len(data), k))
    flush()
    (outdir / "index.txt").write_text("\n".join(index) + "\n")
    print("lz sheets:", sn, "blocks:", len(index), "->", outdir)


if __name__ == "__main__":
    a = sys.argv[1:]
    zoom = int(a[a.index("--zoom") + 1]) if "--zoom" in a else 2
    if a[0] == "raw":
        chunk = int(a[a.index("--chunk") + 1], 16) if "--chunk" in a else 0x8000
        bpp = int(a[a.index("--bpp") + 1]) if "--bpp" in a else 4
        cmd_raw(int(a[1], 16), int(a[2], 16), Path(a[3]), chunk, zoom, bpp)
    elif a[0] == "lz":
        maxh = int(a[a.index("--maxh") + 1]) if "--maxh" in a else 1400
        bpp = int(a[a.index("--bpp") + 1]) if "--bpp" in a else 4
        minsize = int(a[a.index("--min") + 1], 16) if "--min" in a else 0
        cmd_lz(Path(a[1]), zoom, maxh, bpp, minsize)
