"""Static scan for non-story text: runs of kana-heavy bytes (jp.tbl) ended by FF / FE / 00, grouped into regions.

    python -X utf8 tools/textscan.py [--min 4] [--gap 64] [--show]
Prints one line per region (start, end, string count, first strings). Story scripts (0x324AF0-0x32A66F) are skipped.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from mk_jp_tbl import chars  # noqa: E402

CH = chars()
STORY = (0x324AF0, 0x32A670)
FONT = (0x160698, 0x161FD0)


def is_kana(b):
    return 0x54 <= b <= 0xF6


def runs(d, minlen=4):
    """Yield (start, end) of runs of glyph bytes (<0xF8, FE allowed inside) with >= minlen kana and >= 60% kana."""
    i, n = 0, len(d)
    while i < n:
        if d[i] >= 0xF8 or d[i] == 0:
            i += 1
            continue
        j = i
        while j < n and (d[j] < 0xF8 or d[j] == 0xFE) and j - i < 200:
            j += 1
        seg = d[i:j]
        k = sum(1 for b in seg if is_kana(b))
        if (k >= minlen and k >= 0.6 * len(seg) and len(set(seg)) >= 0.6 * len(seg)
                and j < n and (d[j] >= 0xF8 or d[j] == 0)):
            yield i, j
        i = j + 1


def text(seg):
    return "".join("/" if b == 0xFE else CH[b] for b in seg)


def main():
    a = sys.argv[1:]
    minlen = int(a[a.index("--min") + 1]) if "--min" in a else 4
    gap = int(a[a.index("--gap") + 1]) if "--gap" in a else 64
    rom = next((ROOT / "rom").glob("*.gba")).read_bytes()
    regions = []
    for s, e in runs(rom, minlen):
        if STORY[0] <= s < STORY[1] or FONT[0] <= s < FONT[1]:
            continue
        if regions and s - regions[-1][1] <= gap:
            regions[-1][1] = e
            regions[-1][2].append((s, e))
        else:
            regions.append([s, e, [(s, e)]])
    for s, e, items in regions:
        if len(items) < 2 and "--all" not in a:
            continue
        head = " | ".join(text(rom[x:y]) for x, y in items[:4])
        print("%06X-%06X n=%3d  %s" % (s, e, len(items), head))
        if "--show" in a:
            for x, y in items:
                print("    %06X %s" % (x, text(rom[x:y])))


if __name__ == "__main__":
    main()
