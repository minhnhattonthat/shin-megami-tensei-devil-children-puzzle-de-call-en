"""Decode the あそびかた tutorial scripts (pointer table 0x3111F8, 3 entries) with the guessed command lengths.

    python -X utf8 tools/tutorial.py [N]
Commands (guess, parse-consistency only; docs/re/text.md): F8 xx = demo action, args per F8ARGS; FA xx = wait xx frames
(guess); FC = page end (wait for button); FD xx = colour (03 on, 00 off); FE = newline; FF = end.
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from mk_jp_tbl import chars  # noqa: E402

TABLE, COUNT = 0x3111F8, 3
F8ARGS = {0x00: 1, 0x01: 1, 0x02: 2, 0x03: 0, 0x04: 0, 0x05: 2, 0x06: 0, 0x07: 0, 0x08: 0, 0x09: 0, 0x0B: 1,
          0x0C: 0}


def parse(d, off):
    """Return (tokens, end) where end is the offset after FF. Raises on an unknown F8 subcommand."""
    ch, toks, i = chars(), [], off
    while True:
        b = d[i]
        if b == 0xFF:
            return toks, i + 1
        if b == 0xF8:
            sub = d[i + 1]
            if sub not in F8ARGS:
                raise ValueError("unknown F8 %02X at %06X" % (sub, i))
            n = F8ARGS[sub]
            toks.append("{F8 %02X%s}" % (sub, "".join(" %02X" % x for x in d[i + 2:i + 2 + n])))
            i += 2 + n
        elif b in (0xFA, 0xFD):
            toks.append("{%02X %02X}" % (b, d[i + 1])); i += 2
        elif b == 0xFC:
            toks.append("|\n"); i += 1
        elif b == 0xFE:
            toks.append("/"); i += 1
        elif b >= 0xF8:
            raise ValueError("unknown %02X at %06X" % (b, i))
        else:
            toks.append(ch[b]); i += 1


def scripts(d):
    return [struct.unpack_from("<I", d, TABLE + 4 * k)[0] - 0x08000000 for k in range(COUNT)]


if __name__ == "__main__":
    d = next((ROOT / "rom").glob("*.gba")).read_bytes()
    ptrs = scripts(d)
    for k, p in enumerate(ptrs):
        toks, end = parse(d, p)
        nxt = ptrs[k + 1] if k + 1 < len(ptrs) else TABLE
        print("# script %d %06X-%06X (next %06X)" % (k, p, end, nxt))
        if len(sys.argv) > 1 and int(sys.argv[1]) == k:
            print("".join(toks))
