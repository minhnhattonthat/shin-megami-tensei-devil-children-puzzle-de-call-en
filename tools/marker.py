"""Marker build: every unit's text replaced by its short id plus filler, in English glyphs -> build/pdc_marker.gba.

    python -X utf8 tools/marker.py [--fill N]    # N = target line width in px (default: the box's measured limit)
Each line of a unit becomes "[<id><a,b,c..>] The quick brown fox..." up to the box's line width (docs/re/vwf.md), with
the unit's own newlines, pages, colours and {name} kept, so every box shows which unit it is and whether a full line
fits. Short ids: block letter + string.unit (s3.12 = story.003.12); record fields and small-font menus get the bare id.
The en map is built here, never written to script/.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import blocks  # noqa: E402
import build  # noqa: E402
import text  # noqa: E402
import vwf  # noqa: E402

OUT = ROOT / "build" / "pdc_marker.gba"
SHORT = {"story": "s", "rescue": "r", "boss": "b", "system": "y", "pause": "p", "yesno": "q", "titlemenu": "t",
         "tutorial": "u", "client_pause": "cp", "client_link": "cl", "names": "N", "trade": "T", "transfer": "X",
         "devidas_menu": "D"}
# drawn with the 8 px font (0800B53A), not the VWF; the multiboot client (client_*) has its own code, no VWF, and its
# strings can't grow past their slot
SMALL = {"pause", "yesno", "titlemenu", "client_pause", "client_link"}
LIMIT = {"story": 224, "msg": 224, "tutorial": 224}  # px per line the engine draws (asm/vwf.s); measured: vwf.md
NAME_PX = 48  # room left for the {name} the game inserts
FILL = "The quick brown fox jumps over the lazy dog. 0123456789 Pack my box with five dozen jugs.".split()


def short_id(uid):
    block, rest = uid.split(".", 1)
    return SHORT[block] + ".".join(str(int(n)) for n in rest.split("."))


def fill(head, limit):
    s = head
    for w in FILL:
        if vwf.width(s + " " + w) > limit:
            break
        s += " " + w
    for c in " " + "1234567890" * 4:  # then single glyphs up to the exact limit: a full line shows clipping
        if vwf.width(s + c) > limit:
            break
        s += c
    return s


def marker(e, block, codec, limit=None):
    sid = short_id(e["id"])
    if "max" in e:
        return sid[:e["max"]]
    if block in SMALL:
        return sid
    limit = limit or LIMIT[codec]
    out, seg, n = [], [], 0
    toks = text.TOKEN.findall(e["jp"]) + ["{n}"]  # sentinel flushes the last line
    for t in toks:
        if t in text.INLINE[codec]:
            if seg:
                codes = [x for x in seg if x.startswith("{col:")][:1]
                name = "{name}" in seg
                head = "[%s%s]" % (sid, "abcdefghijklmnopqrstuvwxyz"[n % 26])
                body = fill(head, limit - (NAME_PX if name else 0))
                if name:
                    body = body.replace("]", "] {name}", 1)
                out.append("".join(codes) + body)
                seg, n = [], n + 1
            out.append(t)
        else:
            seg.append(t)
    return "".join(out[:-1])  # drop the sentinel


def en_map(limit=None):
    d = build.ROM.read_bytes()
    en = {}
    for block, us in text.units(d).items():
        codec = blocks.PACKED[block][3] if block in blocks.PACKED else "msg"
        for e in us:
            if "data" not in e:
                en[e["id"]] = marker(e, block, codec, limit)
    return en


def main():
    a = sys.argv[1:]
    limit = int(a[a.index("--fill") + 1]) if "--fill" in a else None
    en = en_map(limit)
    rom = build.build(build.ROM.read_bytes(), en)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_bytes(rom.out)
    print(f"{OUT.relative_to(ROOT)}: {len(en)} marker units, free space used {rom.free - blocks.FREE[0]:#x} bytes")


if __name__ == "__main__":
    main()
