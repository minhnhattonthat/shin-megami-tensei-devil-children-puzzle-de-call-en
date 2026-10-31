"""Find u32 pointer arrays (>= MIN consecutive aligned words 0x08xxxxxx) whose targets look like text strings.

    python -X utf8 tools/ptrtables.py [--lo HEX] [--hi HEX] [--min 2] [--show]
A target "looks like text" when its first bytes are glyph codes (< 0xF8) or FD/FC commands and a terminator (>= 0xF8)
follows within 120 bytes, with >= 50% kana among the glyphs. Prints table offset, count, target range, first strings.
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from mk_jp_tbl import chars  # noqa: E402

CH = chars()


def rom():
    return next((ROOT / "rom").glob("*.gba")).read_bytes()


def string_at(d, off, cap=200):
    """Decode until FF; FE=/ FC=| FD xx={xx}. Returns (text, end) or None if it doesn't look like text."""
    out, i, kana, glyphs = [], off, 0, 0
    while i < len(d) and i - off < cap:
        b = d[i]
        if b == 0xFF:
            break
        if b == 0xFE:
            out.append("/")
        elif b == 0xFC:
            out.append("|")
        elif b == 0xFD:
            out.append("{%02X}" % d[i + 1]); i += 1
        elif b >= 0xF8:
            return None
        else:
            out.append(CH[b]); glyphs += 1
            kana += 0x54 <= b <= 0xF6
        i += 1
    else:
        return None
    if glyphs == 0 or kana < 0.5 * glyphs:
        return None
    return "".join(out), i


def tables(d, lo=0, hi=None, minn=2):
    hi = hi or len(d)
    i = lo & ~3
    while i < hi:
        n = 0
        while i + 4 * n + 4 <= len(d):
            v = struct.unpack_from("<I", d, i + 4 * n)[0]
            if not (0x08000000 <= v < 0x08000000 + len(d)):
                break
            if string_at(d, v - 0x08000000) is None:
                break
            n += 1
        if n >= minn:
            yield i, [struct.unpack_from("<I", d, i + 4 * k)[0] - 0x08000000 for k in range(n)]
            i += 4 * n
        else:
            i += 4


def main():
    a = sys.argv[1:]
    lo = int(a[a.index("--lo") + 1], 16) if "--lo" in a else 0
    hi = int(a[a.index("--hi") + 1], 16) if "--hi" in a else None
    minn = int(a[a.index("--min") + 1]) if "--min" in a else 2
    d = rom()
    for off, ptrs in tables(d, lo, hi, minn):
        strs = [string_at(d, p)[0] for p in ptrs]
        print("%06X n=%3d -> %06X-%06X  %s" % (off, len(ptrs), min(ptrs), max(ptrs), " | ".join(strs[:3])[:120]))
        if "--show" in a:
            for p, s in zip(ptrs, strs):
                print("    %06X %s" % (p, s))


if __name__ == "__main__":
    main()
