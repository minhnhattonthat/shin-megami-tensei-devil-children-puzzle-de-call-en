"""Dump every text unit of the original ROM to script/<block>.json, keeping all translation work already there.

    python -X utf8 tools/extract.py
Entry keys: id, ptr (file offset of the unit), jp, en ("" = untranslated, the build keeps the original bytes), max
(record fields: bytes), data (not text: never translate). Units: tools/text.py. An existing entry keeps its `en` and
any extra keys (notes); if its `jp` changed (table fix), it gets "recheck": true. Entries whose id vanished are kept
under "orphans" so no `en` is ever lost. build.py reads `en` from these files.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import blocks  # noqa: E402
import check_rom  # noqa: E402
import text  # noqa: E402

SCRIPT = ROOT / "script"
ROM = ROOT / "rom" / "Shin Megami Tensei Devil Children - Puzzle de Call! (Japan).gba"


def codec(name):
    return blocks.PACKED[name][3] if name in blocks.PACKED else "msg"


def load(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def merge(old, fresh):
    """fresh units + the en/extra keys of old entries with the same id."""
    prev = {e["id"]: e for e in old.get("entries", [])}
    out = []
    for e in fresh:
        o = prev.pop(e["id"], None)
        e = dict(e, en="")
        if o:
            extra = {k: v for k, v in o.items() if k not in ("ptr", "jp", "max", "data")}
            if o.get("jp") != e["jp"] and o.get("en"):
                extra["recheck"] = True
            e.update(extra)
        out.append(e)
    orphans = old.get("orphans", []) + [o for o in prev.values() if o.get("en")]
    return out, orphans


def dump(path, name, fresh):
    entries, orphans = merge(load(path), fresh)
    doc = {"block": name, "codec": codec(name), "entries": entries}
    if orphans:
        doc["orphans"] = orphans
    write_doc(path, doc)
    return len(entries), len(orphans)


def write_doc(path, doc):
    """One entry per line (diffable); tools/batches.py merge writes through here too."""
    body = ",\n".join(json.dumps(e, ensure_ascii=False) for e in doc["entries"])
    head = json.dumps({k: v for k, v in doc.items() if k != "entries"}, ensure_ascii=False)[:-1]
    path.write_text(head + ', "entries": [\n' + body + "\n]}\n", encoding="utf-8", newline="\n")


def en_map():
    """{unit id: en} for every translated unit in script/*.json (what build.py inserts)."""
    out = {}
    for path in sorted(SCRIPT.glob("*.json")):
        for e in load(path)["entries"]:
            if e.get("en"):
                if "data" in e:
                    raise ValueError(f"{e['id']}: has en but is data ({e['data']})")
                out[e["id"]] = e["en"]
    return out


def keep_jp():
    """Explicit untranslated exceptions, each with a reviewable reason."""
    kept = {}
    for line in (SCRIPT / "keep_jp.txt").read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        uid, sep, reason = line.partition("\t")
        if not sep or not reason.strip() or uid in kept:
            raise ValueError(f"invalid keep_jp entry: {line!r}")
        kept[uid] = reason
    return kept


def main():
    check_rom.check()
    SCRIPT.mkdir(exist_ok=True)
    for name, fresh in text.units(ROM.read_bytes()).items():
        n, orph = dump(SCRIPT / f"{name}.json", name, fresh)
        print(f"script/{name}.json: {n} units" + (f", {orph} orphans" if orph else ""))


if __name__ == "__main__":
    main()
