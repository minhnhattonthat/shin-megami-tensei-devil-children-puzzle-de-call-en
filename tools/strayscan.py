"""Scan the whole ROM for Japanese sentences outside the extracted blocks (the extraction coverage check).

    python -X utf8 tools/strayscan.py
A hit is a run of glyph bytes ended by FF / FE / FC that holds at least two common kana words (です, ます, した...):
graphics and code bytes that happen to decode as kana almost never do. Prints each hit outside blocks.PACKED/RECORDS.
Verified 2026-11-01: 0 hits; the same scan finds every message in the extracted blocks (tests/test_extract.py).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import blocks  # noqa: E402
from mk_jp_tbl import chars  # noqa: E402

CH = chars()
WORDS = ("です", "ます", "した", "して", "ない", "った", "この", "には", "から", "まで", "だよ", "だね", "よう", "いる",
         "する", "ません", "ください", "ている", "んだ", "のか", "かな", "デビル")


def runs(d):
    """Yield (start, end, text) of every glyph run (< F8) ended by FF / FE / FC with >= 2 WORDS hits."""
    i, n = 0, len(d)
    while i < n:
        j = i
        while j < n and d[j] < 0xF8:
            j += 1
        if j < n and d[j] in (0xFC, 0xFE, 0xFF) and 4 <= j - i <= 64:  # lines are <= 2 x 14 chars; noise runs long
            t = "".join(CH[b] for b in d[i:j])
            if sum(t.count(w) for w in WORDS) >= 2 and sum(0x54 <= b <= 0xF6 for b in d[i:j]) >= 0.7 * (j - i):
                yield i, j, t
        i = j + 1


def ranges():
    out = [(start, table) for table, _, start, *_ in blocks.PACKED.values()]
    out += [(start, start + count * size) for start, count, size in blocks.RECORDS.values()]
    return out


NOISE = {0x071329: "8bpp sprite frame bytes (sprite area 0x30000-0x160697, swept in phase 1)"}


def strays(d):
    rs = ranges()
    return [(s, e, t) for s, e, t in runs(d) if s not in NOISE and not any(a <= s < b for a, b in rs)]


if __name__ == "__main__":
    d = next((ROOT / "rom").glob("*.gba")).read_bytes()
    hits = strays(d)
    for s, e, t in hits:
        print("%06X-%06X %s" % (s, e, t))
    print(len(hits), "hits outside the extracted blocks")
