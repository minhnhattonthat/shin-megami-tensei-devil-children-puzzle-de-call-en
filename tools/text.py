"""Translatable units of every text block, and how edited `en` text goes back into the block bytes.

Packed strings (blocks.PACKED) are split into a skeleton of commands and *units*: maximal runs of glyphs plus the
inline codes of their codec (newlines, pages, colour), trimmed so a unit starts and ends with text. Only units are
translated; the skeleton (faces, waits, scene commands, {end}) is rebuilt from the original ROM on every build, so a
unit's `en` replaces exactly its `jp`. `en` may hold the inline codes too (extra {n} / pages).
Record fields (blocks.RECORDS / FIELDS) are one unit each; `en` is padded to the field size on insert.

Unit ids: <block>.<string>.<unit> (packed), <block>.<record>[.<field>] (records). docs/re/build.md "Script files".
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import blocks  # noqa: E402

TOKEN = re.compile(r"\{[^}]*\}|\[[0-9A-F]{2}\]|.", re.S)
# layout codes kept inside a unit but trimmed off its ends; colour codes ({col:xx}) stay inside, ends included.
# story pages are {wait:00}{clr}{box:09} (button wait, clear, standard box)
INLINE = {"story": {"{n}", "{wait:00}", "{clr}", "{box:09}"}, "msg": {"{n}", "{page}"}, "tutorial": {"{n}", "{page}"}}
COLOUR = re.compile(r"\{col:[0-9A-F]{2}\}$")


def is_glyph(tok):
    return not tok.startswith(("{", "[")) or len(tok) == 1


def split(codec, s):
    """[(is_unit, text), ...] whose texts join back to s."""
    toks = TOKEN.findall(s)
    inline = lambda t: is_glyph(t) or t in INLINE[codec] or bool(COLOUR.match(t))  # noqa: E731
    out, i = [], 0
    while i < len(toks):
        j = i
        while j < len(toks) and inline(toks[j]):
            j += 1
        if j == i:
            out.append((False, toks[i])); i += 1
            continue
        run = toks[i:j]
        a, b = 0, len(run)  # trim layout codes off both ends
        while a < b and run[a] in INLINE[codec]:
            a += 1
        while b > a and run[b - 1] in INLINE[codec]:
            b -= 1
        if any(is_glyph(t) for t in run[a:b]):
            out += [(False, t) for t in run[:a]] + [(True, "".join(run[a:b]))] + [(False, t) for t in run[b:]]
        else:
            out += [(False, t) for t in run]
        i = j
    return out


def _packed_units(d, name):
    codec = blocks.PACKED[name][3]
    t = blocks.table(codec)
    for k, (raw, p) in enumerate(zip(blocks.unpack_packed(d, name), blocks.pointers(d, name))):
        s = t.decode(raw, length=len(raw))[0]
        u = 0
        for is_unit, piece in split(codec, s):
            if is_unit:
                yield {"id": f"{name}.{k:03}.{u:02}", "ptr": f"{p:06X}", "jp": piece}
                u += 1
            p += len(t.encode(piece))


def field_text(raw, pad):
    """The field's text bytes: up to the first FF (pad FF) or without trailing 00 fill (pad 00)."""
    if pad == 0xFF:
        return raw.split(b"\xff", 1)[0]
    return raw.rstrip(b"\x00")


def _record_units(d, name):
    t = blocks.table("msg")
    fields = blocks.FIELDS[name]
    start, _, size = blocks.RECORDS[name]
    for k, rec in enumerate(blocks.unpack_record(d, name)):
        at = 0
        for f, (n, pad) in enumerate(fields):
            uid = f"{name}.{k:03}" + (f".{f}" if len(fields) > 1 else "")
            b = field_text(rec[at:at + n], pad)
            e = {"id": uid, "ptr": f"{start + k * size + at:06X}", "jp": t.decode(b, length=len(b))[0], "max": n}
            if uid in blocks.DATA:
                e["data"] = blocks.DATA[uid]
            yield e
            at += n


def units(d):
    """{block: [unit dict (id, ptr, jp[, max, data])]} for the ROM d."""
    out = {name: list(_packed_units(d, name)) for name in blocks.PACKED}
    out.update({name: list(_record_units(d, name)) for name in blocks.RECORDS})
    return out


def packed_entries(d, name, en):
    """The block's strings with every unit whose id is in `en` replaced; others keep their original bytes."""
    codec = blocks.PACKED[name][3]
    t = blocks.table(codec)
    out = []
    for k, raw in enumerate(blocks.unpack_packed(d, name)):
        pieces, u, edited = [], 0, False
        for is_unit, piece in split(codec, t.decode(raw, length=len(raw))[0]):
            if is_unit:
                uid = f"{name}.{k:03}.{u:02}"
                if uid in en:
                    piece, edited = en[uid], True
                u += 1
            pieces.append(piece)
        out.append(t.encode("".join(pieces)) if edited else raw)
    return out


def record_entries(d, name, en):
    t = blocks.table("msg")
    fields = blocks.FIELDS[name]
    out = []
    for k, rec in enumerate(blocks.unpack_record(d, name)):
        rec, at = bytearray(rec), 0
        for f, (n, pad) in enumerate(fields):
            uid = f"{name}.{k:03}" + (f".{f}" if len(fields) > 1 else "")
            if uid in en:
                b = t.encode(en[uid])
                if len(b) > n:
                    raise ValueError(f"{uid}: {len(b)} bytes > field {n}: {en[uid]!r}")
                rec[at:at + n] = b + bytes([pad]) * (n - len(b))
            at += n
        out.append(bytes(rec))
    return out


if __name__ == "__main__":
    s = "{c05}ジンと{n}アキラ{wait:00}{clr}{box:09}は{col:03}行{col:00}{wait:00}{clr}{box:09}{face:0101}{end}"
    sp = split("story", s)
    assert "".join(x for _, x in sp) == s
    assert [x for u, x in sp if u] == ["ジンと{n}アキラ{wait:00}{clr}{box:09}は{col:03}行{col:00}"], sp
    assert [x for u, x in split("msg", "{f9:A3}{n}ナカマ。{page}{end}") if u] == ["ナカマ。"]
    assert not [x for u, x in split("msg", "{n}{page}{end}") if u]
    print("selftest ok")
