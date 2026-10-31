"""Phase 4: every text unit roundtrips, the units cover all text, script/*.json is the current dump, en goes in."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))
import blocks  # noqa: E402
import build  # noqa: E402
import extract  # noqa: E402
import strayscan  # noqa: E402
import text  # noqa: E402

pytestmark = pytest.mark.skipif(not build.ROM.is_file(), reason="no ROM dump in rom/")


@pytest.fixture(scope="module")
def orig():
    return build.ROM.read_bytes()


@pytest.fixture(scope="module")
def units(orig):
    return text.units(orig)


def test_packed_roundtrip(orig):
    for name, (_, _, _, codec, _, _) in blocks.PACKED.items():
        t = blocks.table(codec)
        for k, raw in enumerate(blocks.unpack_packed(orig, name)):
            s = t.decode(raw, length=len(raw))[0]
            assert "[" not in s, (name, k, s)  # no unknown byte anywhere
            assert t.encode(s) == raw, (name, k)
            pieces = text.split(codec, s)
            assert "".join(p for _, p in pieces) == s
            assert not [p for u, p in pieces if not u and text.is_glyph(p)], (name, k)  # no text left in skeleton


def test_record_roundtrip(orig, units):
    t = blocks.table("msg")
    for name, fields in blocks.FIELDS.items():
        assert sum(n for n, _ in fields) == blocks.RECORDS[name][2], name
    for us in units.values():
        for e in us:
            if "max" not in e:
                continue
            p = int(e["ptr"], 16)
            b = t.encode(e["jp"])
            assert orig[p:p + len(b)] == b, e["id"]
            name = e["id"].split(".")[0]
            n, pad = blocks.FIELDS[name][int(e["id"].split(".")[2]) if e["id"].count(".") == 2 else 0]
            rest = orig[p + len(b):p + n]  # the ROM field; `max` is the English room (blocks.EN_MAX)
            assert (rest == b"" or rest[0] == 0xFF) if pad == 0xFF else not any(rest), e["id"]


def test_unit_ptrs(orig, units):
    for name, us in units.items():
        codec = extract.codec(name)
        for e in us:
            p, b = int(e["ptr"], 16), blocks.table(codec).encode(e["jp"])
            assert orig[p:p + len(b)] == b, e["id"]


def test_coverage(orig, units):
    """No Japanese sentence outside the blocks, and every sentence the scan finds inside them is in a unit."""
    assert strayscan.strays(orig) == []
    spans = [(int(e["ptr"], 16), int(e["ptr"], 16) + len(blocks.table(extract.codec(n)).encode(e["jp"])))
             for n, us in units.items() for e in us]
    hits = list(strayscan.runs(orig))
    assert len(hits) > 150
    for s, _, t in hits:
        if s in strayscan.NOISE:
            continue
        # the scan may start on a command's id/argument bytes (FF 09 A3 00 = face, F8 06 = demo), up to 3 before the text
        assert any(a <= x < b for a, b in spans for x in range(s, s + 4)), (hex(s), t)


def test_script_files_are_current(units):
    for name, us in units.items():
        doc = extract.load(extract.SCRIPT / f"{name}.json")
        assert doc.get("block") == name and "orphans" not in doc, name
        got = [{k: v for k, v in e.items() if k in ("id", "ptr", "jp", "max", "data")} for e in doc["entries"]]
        assert got == us, f"script/{name}.json is stale: run tools/extract.py"
        assert not [e["id"] for e in doc["entries"] if e.get("recheck")], name


def test_every_block_has_a_budget(units):
    assert sorted(units) == sorted(blocks.BUDGET)  # the width gate: no block without window data


def test_en_goes_in(orig):
    en = {"pause.000.00": "Back", "story.000.01": "Test{n}Test!{wait:00}{clr}{box:09}One more",
          "rescue.001.00": "{name} joins you.", "trade.000.1": "Yes", "devidas_menu.000.4": "Ye"}
    # every unit of story 0 in English: a half-English string can't be read back with one table
    en.update({e["id"]: f"Unit {k}" for k, e in enumerate(text.units(orig)["story"])
               if e["id"].startswith("story.000.") and e["id"] not in en})
    out = bytes(build.build(orig, en).out)
    got_en = {e["id"]: e["jp"] for us in text.units(out, "en").values() for e in us}
    got = {e["id"]: e["jp"] for us in text.units(out).values() for e in us}
    want = {e["id"]: e["jp"] for us in text.units(orig).values() for e in us}
    assert {k: got_en[k] for k in en} == en
    assert {k: v for k, v in got.items() if k not in en} == {k: v for k, v in want.items() if k not in en}
    assert out[0x28B0BA:0x28B0BC] == b"\x00\x00"  # pad-00 field refilled with spaces


def test_names_move_to_wide_table(orig):
    import asm
    out = bytes(build.build(orig, {"names.000": "Jack Frost"}).out)
    rec = out[asm.NAMES:asm.NAMES + asm.NAME_SIZE]
    assert blocks.en_table("msg").decode(rec, length=10)[0] == "Jack Frost" and rec[10:] == b"\xff" * 6
    assert out[asm.NAMES + asm.NAME_SIZE:asm.NAMES + asm.NAME_SIZE + 8] == orig[0x30E494:0x30E49C].split(b"\xff")[0].ljust(8, b"\xff")
    assert out[0x30E48C:0x30E9C4] == orig[0x30E48C:0x30E9C4]  # the old table stays (nothing reads it)
    assert int.from_bytes(out[0x62BC:0x62C0], "little") == asm.NAMES + 0x08000000


def test_record_overflow_refused(orig):
    with pytest.raises(ValueError, match="bytes >"):
        build.build(orig, {"names.000": "Sixteen chars ok"})
    with pytest.raises(ValueError, match="bytes >"):
        build.build(orig, {"trade.000.1": "Fifteen glyphs!"})


def test_dump_keeps_en(tmp_path):
    fresh = [{"id": "x.000.00", "ptr": "0", "jp": "あ"}, {"id": "x.001.00", "ptr": "2", "jp": "い"}]
    path = tmp_path / "x.json"
    extract.dump(path, "x", fresh)
    doc = extract.load(path)
    doc["entries"][0].update(en="A", note="keep")
    doc["entries"][1]["en"] = "I"
    path.write_text(__import__("json").dumps(doc, ensure_ascii=False), encoding="utf-8")
    extract.dump(path, "x", [dict(fresh[0]), {"id": "x.002.00", "ptr": "4", "jp": "う"}])
    doc = extract.load(path)
    assert doc["entries"][0] == {"id": "x.000.00", "ptr": "0", "jp": "あ", "en": "A", "note": "keep"}
    assert doc["entries"][1]["en"] == ""
    assert doc["orphans"][0]["en"] == "I"  # vanished id: kept, never dropped
