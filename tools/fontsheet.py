"""Render the 16x16 4bpp glyph font (128 bytes per code, tiles TL TR BL BR) as a labelled sheet.

    python -X utf8 tools/fontsheet.py FONT.bin OUT.png [--zoom 3] [--first 0] [--count 256]
"""
import argparse

from PIL import Image, ImageDraw


def glyph(font, code):
    """16x16 list of rows of 4-bit pixel indices."""
    g = font[code * 128:(code + 1) * 128]
    px = [[0] * 16 for _ in range(16)]
    for t in range(4):
        tx, ty = (t & 1) * 8, (t >> 1) * 8
        for y in range(8):
            for x in range(8):
                b = g[t * 32 + y * 4 + x // 2]
                px[ty + y][tx + x] = (b >> 4) if x & 1 else (b & 15)
    return px


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("font"); ap.add_argument("out")
    ap.add_argument("--zoom", type=int, default=3)
    ap.add_argument("--first", type=int, default=0)
    ap.add_argument("--count", type=int, default=256)
    a = ap.parse_args()
    font = open(a.font, "rb").read()
    cols, cw, ch = 16, 16 * a.zoom + 4, 16 * a.zoom + 14
    rows = (a.count + cols - 1) // cols
    im = Image.new("RGB", (cols * cw, rows * ch), "white")
    dr = ImageDraw.Draw(im)
    shade = {0: (255, 255, 255)}
    for k in range(a.count):
        code = a.first + k
        if (code + 1) * 128 > len(font):
            break
        ox, oy = (k % cols) * cw, (k // cols) * ch
        dr.text((ox + 1, oy), "%02X" % code, fill=(200, 0, 0))
        for y, row in enumerate(glyph(font, code)):
            for x, v in enumerate(row):
                if v:
                    c = 255 - min(255, v * 40)
                    dr.rectangle([ox + x * a.zoom, oy + 12 + y * a.zoom, ox + (x + 1) * a.zoom - 1,
                                  oy + 12 + (y + 1) * a.zoom - 1], fill=(c, c, c))
    im.save(a.out)
    print(a.out)


if __name__ == "__main__":
    main()
