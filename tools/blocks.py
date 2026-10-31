"""The ROM's text and compressed-graphics blocks: where they are, how to unpack them and how to write them back.

build.py unpacks every block from the original ROM, swaps in edited entries, and packs them into a copy. With no edits
the result is byte-identical to the original (tests/test_identity.py). Layouts: docs/re/text.md, docs/re/build.md.
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import lz77  # noqa: E402
from tbl import Table  # noqa: E402

ROM_BASE = 0x08000000
CLIENT = 0x32CED4  # multiboot client image: runs at 0x02000000, so its pointers are 0x02000000 + (off - CLIENT)
# verified unused (docs/re/text.md); packed blocks that outgrow their slot move here. 0x3F0000+ is the VWF engine
# (tools/asm.py ENGINE).
FREE = (0x3529D0, 0x3F0000)

# Packed string tables: strings back to back from `start`, then 00 padding to 4, then the u32 pointer table, which code
# references by address and so never moves. name: (table, count, start, codec, pointer base, may relocate to FREE)
PACKED = {
    "story": (0x32A670, 29, 0x324AF0, "story", ROM_BASE, True),
    "rescue": (0x30DBDC, 101, 0x30CA34, "msg", ROM_BASE, True),
    "boss": (0x30E224, 13, 0x30DD70, "msg", ROM_BASE, True),
    "system": (0x30E3DC, 14, 0x30E258, "msg", ROM_BASE, True),
    "pause": (0x30E440, 8, 0x30E414, "msg", ROM_BASE, True),
    "yesno": (0x30E468, 2, 0x30E460, "msg", ROM_BASE, True),
    "titlemenu": (0x30E480, 3, 0x30E470, "msg", ROM_BASE, True),
    "tutorial": (0x3111F8, 3, 0x30FD48, "tutorial", ROM_BASE, True),
    # client strings must stay inside the client image (sent over the link cable with a fixed length)
    "client_pause": (0x34FA60, 4, 0x34FA48, "msg", 0x02000000 - CLIENT, False),
    "client_link": (0x34FB60, 7, 0x34FA70, "msg", 0x02000000 - CLIENT, False),
}

# Fixed-size records, edited in place: name: (start, count, size). Text in them is FF-terminated / FF-padded.
RECORDS = {
    "names": (0x30E48C, 167, 8),  # demon names 0-161, then ジン アキラ ランド ゲイル (8-char names have no FF)
    "trade": (0x32A7C0, 13, 0x1C),  # link trade messages, table 0x32A92C points at each record
    "transfer": (0x2AB7A4, 5, 0x1C),  # link transfer messages, table 0x32B390
    "devidas_menu": (0x28B0A4, 1, 0x1C),  # DeviDas trade menu fields (00/FF padded), xrefs 0x1C214 / 0x1C218
    # race mode menu 1カートリッジたいせん / マルチカートリッジたいせん: 30 glyphs DMA'd as 8x8 tiles in a row by 080205FE
    # (32x8 sprites from x 68: row 1 = tiles 0-15, row 2 = tiles 16-29, fixed 8 px pitch; the frame shows 13 cells);
    # found by the marker build, not by strayscan (00-padded, no FF)
    "race_menu": (0x2AB750, 1, 30),
}

# LZ77 blocks holding Japanese text (fonts and graphics text, docs/re/graphics.md): name -> offset
LZ = {
    "font": 0x160698, "font_small": 0x161FD0, "client_font_small": 0x337B10, "client_font_bold": 0x33A2DC,
    "title_logo": 0x232A68, "title_menu": 0x23AEDC, "title_sub": 0x23B1D8, "title_sub_hi": 0x23B4AC,
    "title_emblem": 0x23B9A4, "hud": 0x1C72B8, "hud_puzzle": 0x2AADE0, "hud_puzzle_obj": 0x219630, "puzzle_select": 0x2A8970,
    "puzzle_select2": 0x2AB324, "race": 0x2AB930, "devidas_a": 0x28C998, "devidas_b": 0x2A1658,
    "devidas_c": 0x28BD70, "charselect": 0x22E6D0, "outlined_kata": 0x1C810C, "gameover": 0x201EB8,
    "devidas_labels": 0x28C448, "devidas_elements": 0x28C330, "devidas_values": 0x28BFB4,
    "area_1": 0x28A59C, "area_2": 0x28A758, "area_3": 0x28A93C, "area_4": 0x28AACC, "area_5": 0x28ACE8,
    "area_6": 0x28AED8, "bold_kana": 0x28C50C, "bold_kana2": 0x2B13E4, "client_bold_kana": 0x33BB88,
    "banner_1": 0x22C408, "banner_2": 0x22CD60, "banner_3": 0x22D578, "banner_4": 0x22DE80,
}
# uncompressed graphics: name -> (offset, size). hud_puzzle_raw = the copy of hud_puzzle the puzzle select reads
# (literal at 0801F5A4; the LZ copy at 0x2AADE0 has no pointer)
RAW = {"hud_puzzle_raw": (0x2AAEB0, 0x180)}

# Text fields inside each record: (size, pad). pad FF: text ends at FF (none when it fills the field), bytes after the
# FF are stale and kept for unchanged fields. pad 00: fixed-width text padded with fullwidth spaces (00).
FIELDS = {
    "names": [(8, 0xFF)],
    "trade": [(14, 0xFF), (14, 0xFF)],  # two lines
    "transfer": [(14, 0xFF), (14, 0xFF)],
    "devidas_menu": [(5, 0xFF)] * 4 + [(4, 0x00)] * 2,  # キャンセル こうかん あげる もらう (0x1C214); いいえ はい (0x1C218)
    "race_menu": [(16, 0x00), (14, 0x00)],
}
DATA = {"names.162": "placeholder record (8 x 1C), not a name"}  # entries that decode as text but aren't
# English room where the build moves a record block: names go to 16-byte records (tools/asm.py NAMES, NAME_SIZE)
EN_MAX = {"names": 15}

# Window data (the width gate, docs/re/vwf.md "Measured budgets"): block -> (font, px per line, lines per page, px of a
# page's last line where the page arrow sits, how measured). font: big = fonts/vwf.txt (vwf.width), small = the 8x8 menu
# font (smallfont.width), cell = fixed 8 px cells (budget in glyphs). Byte caps (FIELDS / EN_MAX) apply on top.
VWF_BOX = ("big", 224, 2, 210, "measured: work/qa/torture/s0, work/qa/mk2 (arrow x 225-230)")
BUDGET = {
    "story": VWF_BOX, "boss": VWF_BOX, "rescue": VWF_BOX, "system": VWF_BOX, "tutorial": VWF_BOX,
    "pause": ("small", 48, 1, 48, "measured: work/qa/stress pause, x 184 to highlight end 232"),
    "yesno": ("small", 24, 1, 24, "measured: work/qa/stress pause_save, x 208-232"),
    "titlemenu": ("small", 40, 1, 40, "measured: work/qa/stress gameover, x 100-140"),
    "names": ("small", 67, 1, 67, "measured: work/qa/stress pause devil lists x 88-155 (DeviDas box: 120)"),
    "race_menu": ("cell", 12, 1, 12, "measured: work/qa/stress3 race; 8 px cells from x 68, highlight ends ~x 164"),
    "devidas_menu": ("cell", None, 1, None, "guess: link-only screen, byte slot only"),
    "trade": ("cell", 14, 2, 14, "guess: multiboot client, fixed 8 px, link-only"),
    "transfer": ("cell", 14, 2, 14, "guess: multiboot client, fixed 8 px, link-only"),
    "client_pause": ("cell", None, 1, None, "guess: multiboot client, string can't outgrow its slot"),
    "client_link": ("cell", None, 1, None, "guess: multiboot client, string can't outgrow its slot"),
}

# codec -> table (tbl/, generated by tools/mk_jp_tbl.py)
TABLES = {"story": "jp.tbl", "msg": "msg.tbl", "tutorial": "tutorial.tbl"}
_tables = {}


def table(codec):
    if codec not in _tables:
        _tables[codec] = Table.load(ROOT / "tbl" / TABLES[codec])
    return _tables[codec]


def en_table(codec):
    """The codec's control codes with the English glyphs of tbl/en.tbl: encodes `en` text."""
    key = "en:" + codec
    if key not in _tables:
        lines = (ROOT / "tbl" / TABLES[codec]).read_text(encoding="utf-8").splitlines()
        ctrl = [ln for ln in lines if "={" in ln]
        _tables[key] = Table(ctrl + (ROOT / "tbl" / "en.tbl").read_text(encoding="utf-8").splitlines())
    return _tables[key]


def string_end(d, p, codec):
    """Offset just past the string at p (through its {end})."""
    return p + table(codec).decode(d, p, maxlen=0x10000)[1]


def pointers(d, name):
    table, count, _, _, base, _ = PACKED[name]
    return [struct.unpack_from("<I", d, table + 4 * k)[0] - base for k in range(count)]


def unpack_packed(d, name):
    """List of each entry's bytes, in table order. Raises if the layout isn't the packed form above."""
    table, _, start, codec, _, _ = PACKED[name]
    ptrs = pointers(d, name)
    moved = ptrs[0] >= FREE[0]  # a built ROM whose block grew into free space (reading a build back)
    if (ptrs[0] != start and not moved) or ptrs != sorted(set(ptrs)):
        raise ValueError(f"{name}: pointers not unique and ascending from {start:#x}")
    out = []
    for k, p in enumerate(ptrs):
        end = string_end(d, p, codec)
        if k + 1 < len(ptrs) and end != ptrs[k + 1]:
            raise ValueError(f"{name}[{k}] ends {end:#x}, next string at {ptrs[k + 1]:#x}")
        out.append(d[p:end])
    if not moved and (end > table or any(d[end:table])):  # an edited block that shrank leaves more 00 fill
        raise ValueError(f"{name}: {end:#x}..{table:#x} is not 00 padding to the table")
    return out


def unpack_record(d, name):
    start, count, size = RECORDS[name]
    return [d[start + k * size:start + (k + 1) * size] for k in range(count)]


class Rom:
    """Output buffer that logs every write for romdiff.py --writes, plus a bump allocator over FREE."""

    def __init__(self, orig):
        self.orig, self.out, self.writes, self.free = orig, bytearray(orig), [], FREE[0]

    def put(self, off, data, who):
        if off + len(data) > len(self.out):
            raise ValueError(f"{who}: write past ROM end")
        self.writes.append((off, bytes(self.orig[off:off + len(data)]), bytes(data), who))
        self.out[off:off + len(data)] = data

    def alloc(self, n, who):
        off = self.free
        if off + n > FREE[1]:
            raise ValueError(f"{who}: free space exhausted ({n} bytes)")
        self.free += n
        return off

    def writes_log(self):
        return "".join(f"{o:06X} {a.hex()} {b.hex()} {w}\n" for o, a, b, w in self.writes)


def pack_packed(rom, name, entries):
    """Write entries back to back from `start` (or to FREE when they don't fit before the table) and repoint."""
    table, count, start, _, base, relocatable = PACKED[name]
    assert len(entries) == count, name
    blob = b"".join(entries)
    room = table - start
    if len(blob) <= room:
        at = start
        rom.put(start, blob + bytes(room - len(blob)), name)  # 00 fill up to the table, as the original pads
    elif relocatable:
        at = rom.alloc(len(blob), name)
        rom.put(at, blob, name)
    else:
        raise ValueError(f"{name}: {len(blob)} bytes > {room} and the block can't leave its slot")
    ptrs, p = [], at
    for e in entries:
        ptrs.append(p + base); p += len(e)
    rom.put(table, struct.pack("<%dI" % count, *ptrs), name + " ptrs")


def pack_record(rom, name, entries):
    start, count, size = RECORDS[name]
    assert len(entries) == count and all(len(e) == size for e in entries), name
    rom.put(start, b"".join(entries), name)


def unpack_lz(d, name):
    """(data, min_disp, end): min_disp is the compress() setting that reproduces the original block."""
    data, md, end = lz77.mode(d, LZ[name])
    if md is None:
        raise ValueError(f"{name}: no compress() setting reproduces the block")
    return data, md, end


def pack_lz(rom, name, data, min_disp, end):
    """Recompress in place; the slot runs to the 4-aligned end of the original block."""
    off = LZ[name]
    blob = lz77.compress(data, min_disp)
    room = (end - off + 3) & ~3
    if len(blob) > room:  # grown (redrawn graphics): move it to free space, repoint every literal word naming it
        refs = lz_xrefs(rom.orig, off)
        if not refs:
            raise ValueError(f"{name}: {len(blob)} bytes > slot {room} and no literal pointer to repoint")
        rom.free = (rom.free + 3) & ~3  # the BIOS LZ77 source must be word aligned
        new = rom.alloc(len(blob), name)
        rom.put(new, blob, name)
        for r in refs:
            rom.put(r, struct.pack("<I", ROM_BASE + new), f"{name} ptr")
        return
    rom.put(off, blob, name)


def lz_xrefs(d, off):
    """4-aligned words equal to the block's ROM address (literal pools)."""
    w, out, i = struct.pack("<I", ROM_BASE + off), [], -4
    while (i := d.find(w, i + 4)) >= 0:
        if i % 4 == 0:
            out.append(i)
        else:
            i = i - i % 4
    return out
