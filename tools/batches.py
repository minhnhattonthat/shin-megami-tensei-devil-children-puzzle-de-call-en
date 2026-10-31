"""Translation batches: untranslated units -> work/tl/bNNN.tsv, check an agent's output, merge it into script/*.json.

    python -X utf8 tools/batches.py split [--size 3000] [--only REGEX]   # new batches from units with no `en`
    python -X utf8 tools/batches.py check bNNN [bNNN ...]                # OK, or one line per problem
    python -X utf8 tools/batches.py merge bNNN [bNNN ...]                # checked batches -> script/*.json
    python -X utf8 tools/batches.py fit BLOCK "English text"             # how the text wraps, px per line

Authoring form (what translators write, kept in the unit's `src`; build.py reads the rendered `en`):
- big-font boxes (story, boss, rescue, system, tutorial): plain English; ` // ` = page break (the player presses a
  button); the tool wraps each page into 2 lines (224 px, the page's last line 210 px: the page arrow) and fails a
  page that needs 3. ` / ` forces a line break. Copy `{col:XX}` and `{name}` as in the Japanese.
  Units whose every line starts with the same colour (rescue hints) are shown without it; the tool re-adds it.
- `=` at the start: raw `en` (codes written out), for hand-laid units such as the centred ending lines.
- menus / names / records: one line, checked against the block's px or cell budget (blocks.BUDGET) and byte slot.
Batch input: `id<TAB>speaker<TAB>form<TAB>limit<TAB>jp`, jp with ` / ` for {n} and ` // ` for a page.
"""
import argparse
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import blocks  # noqa: E402
import extract  # noqa: E402
import smallfont  # noqa: E402
import text  # noqa: E402
import vwf  # noqa: E402

SCRIPT, TL, TERMS = ROOT / "script", ROOT / "work" / "tl", ROOT / "build"
PAGE = {"story": "{wait:00}{clr}{box:09}", "msg": "{page}", "tutorial": "{page}"}
ORDER = ["story", "boss", "rescue", "tutorial", "system", "pause", "yesno", "titlemenu", "devidas_menu", "race_menu",
         "trade", "transfer", "client_pause", "client_link", "names"]
# multiboot / link screens print with fonts that only have the game's own ASCII (docs/re/vwf.md "Not hooked")
LINK = {"client_pause", "client_link", "trade", "transfer", "devidas_menu", "race_menu"}
# … is allowed: the client font still has the Japanese ・ at its code (one dot per …)
LINK_OK = set("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz:;?!_/~()+-=&* …")
FACES = {"A3": "Jin", "A4": "Akira", "00": "Rand", "01": "Gale"}  # face byte 1; other values = demon id (names.NNN)
CODE = re.compile(r"\{[^}]*\}")
COL = re.compile(r"\{col:([0-9A-F]{2})\}")
LINES_PER_PAGE, SPRITES = 2, 32  # message printer: at most 32 sprites per page (asm/vwf.s msg_char)


def codec(name):
    return blocks.PACKED[name][3] if name in blocks.PACKED else "msg"


def load(name):
    return json.loads((SCRIPT / f"{name}.json").read_text(encoding="utf-8"))


def rom():
    return extract.ROM.read_bytes()


def lines_of(jp, cd):
    return re.split(re.escape("{n}") + "|" + re.escape(PAGE[cd]), jp)


def line_colour(jp, cd):
    """XX when every line of the unit starts with {col:XX} and no other colour code is used, else None."""
    lines = lines_of(jp, cd)
    heads = [COL.match(ln) for ln in lines]
    if all(heads) and len({m.group(1) for m in heads}) == 1 and len(COL.findall(jp)) == len(lines):
        return heads[0].group(1)
    return None


def jp_view(jp, cd):
    if cd in PAGE and line_colour(jp, cd):
        jp = COL.sub("", jp)
    return jp.replace(PAGE.get(cd, "\0"), " // ").replace("{n}", " / ")


# ---- speakers -------------------------------------------------------------------------------------------------
def speakers(d):
    """{unit id: speaker} for the story: the last face command before each unit."""
    names = {e["id"]: (e.get("en") or e["jp"]) for e in load("names")["entries"]}
    t, out = blocks.table("story"), {}
    for k, raw in enumerate(blocks.unpack_packed(d, "story")):
        face, u = "narration", 0
        for is_unit, piece in text.split("story", t.decode(raw, length=len(raw))[0]):
            if piece.startswith("{face:"):
                hi = piece[6:8]
                face = FACES.get(hi) or names.get(f"names.{int(hi, 16):03}", "demon " + hi)
            elif piece == "{noface}":
                face = "narration"
            if is_unit:
                out[f"story.{k:03}.{u:02}"] = face
                u += 1
    return out


SPEAKER = {"boss": "Imperium boss", "rescue": "rescued demon", "tutorial": "Rand (tutorial)",
           "system": "system", "client_link": "system (link)", "trade": "system (link trade)",
           "transfer": "system (link transfer)"}


def form_limit(name, e):
    font, px, lines, last, _ = blocks.BUDGET[name]
    if font == "big":
        return ("narration" if name == "story" else "dlg"), f"{lines}x{px}px/page"
    cap = e.get("max")
    if font == "small":
        return ("name" if name == "names" else "menu"), f"{px}px" + (f" {cap}ch" if cap else "")
    n = min(x for x in (px, cap) if x) if (px or cap) else len(text_len(e["jp"]))
    return "menu", f"{n}ch"


def text_len(jp):
    return CODE.sub("", jp)


# ---- glossary -------------------------------------------------------------------------------------------------
def glossary():
    """[(jp, [en alternatives], [avoid])] from the tables in glossary.md (JP | EN | max | notes | Avoid)."""
    rows = []
    for ln in (ROOT / "glossary.md").read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if not ln.startswith("|") or len(cells) < 2 or cells[0] in ("JP", "") or set(cells[0]) <= set("-: "):
            continue
        en = [a.strip() for a in cells[1].split(";") if a.strip()]
        avoid = [a.strip() for a in cells[4].split(";") if a.strip()] if len(cells) > 4 else []
        rows.append((cells[0], en, avoid))
    return rows


def _cls(ch):
    if "゠" <= ch <= "ヿ":
        return "k"
    if "぀" <= ch <= "ゟ":
        return "h"
    if "一" <= ch <= "鿿":
        return "c"
    return "o"


def has_term(jp, term):
    """term in jp as a whole run: the neighbours are not of the same script as the term's ends (ミン not in タイミング)."""
    s = text_len(jp)
    for m in re.finditer(re.escape(term), s):
        a, b = m.start(), m.end()
        if (a == 0 or _cls(s[a - 1]) != _cls(term[0]) or _cls(term[0]) == "o") and \
           (b == len(s) or _cls(s[b]) != _cls(term[-1]) or _cls(term[-1]) == "o"):
            return True
    return False


# ---- rendering ------------------------------------------------------------------------------------------------
_namew = None


def name_width():
    """{name} is any demon name: the widest English name in the big font (16-byte records: 15 glyphs)."""
    global _namew
    if _namew is None:
        ens = [e["en"] for e in load("names")["entries"] if e.get("en")]
        _namew = max([vwf.width(x) for x in ens] or [120])
    return _namew


def px(s):
    return vwf.width(CODE.sub("", s)) + s.count("{name}") * name_width()


def wrap(page, first=224, last=210):
    """Greedy word wrap of one page; returns lines (may be more than 2: the check reports it)."""
    out = []
    for forced in re.split(r"\s+/\s+|^/\s+", page):
        cur = ""
        for w in forced.split():
            cand = f"{cur} {w}" if cur else w
            if cur and px(cand) > first:
                out.append(cur)
                cur = w
            else:
                cur = cand
        out.append(cur)
    if out and px(out[-1]) > last and len(out[-1].split()) > 1:  # move the last word below the arrow line
        head, tail = out[-1].rsplit(" ", 1)
        out[-1:] = [head, tail]
    return out


def render(name, src, jp):
    """(en with codes, problems) for authored English src of a unit whose Japanese is jp."""
    probs = []
    if src.startswith("="):
        en = src[1:]
        return en, probs
    cd = codec(name)
    font, budget, _, _, _ = blocks.BUDGET[name]
    if font != "big":
        return src, probs
    col = line_colour(jp, cd)
    pages = []
    for k, page in enumerate(re.split(r"\s*//\s*", src.strip())):
        lines = wrap(page)
        if len(lines) > LINES_PER_PAGE:
            probs.append(f"page {k + 1} needs {len(lines)} lines (max 2 per page): add a ' // ' page break or "
                         f"rephrase: {' | '.join(lines)}")
        for i, ln in enumerate(lines):
            lim = 210 if i == len(lines) - 1 else 224
            if px(ln) > lim:
                probs.append(f"page {k + 1} line {i + 1} is {px(ln)} px > {lim}: {ln!r}")
        if cd in ("msg", "tutorial"):
            spr = sum(math.ceil(px(seg) / 16) for ln in lines for seg in COL.split(ln)[::2] if seg)
            if spr > SPRITES:
                probs.append(f"page {k + 1} uses {spr} sprites > {SPRITES} (colour runs): fewer colour changes")
        if col:
            lines = ["{col:%s}%s" % (col, ln) for ln in lines]
        pages.append("{n}".join(lines))
    return PAGE[cd].join(pages), probs


def codes_of(s):
    for p in PAGE.values():
        s = s.replace(p, "")
    return sorted(c for c in CODE.findall(s) if c != "{n}")


def problems(name, e, src):
    """Every rule the unit's authored English breaks."""
    jp, out = e["jp"], []
    if not src.strip():
        return ["empty"]
    if "\t" in src or "\\" in src:
        out.append("tab or backslash in the English")
    en, out2 = render(name, src, jp)
    out += out2
    plain = CODE.sub("", en)
    bad = sorted({c for c in plain if c not in vwf.en_codes()})
    if bad:
        out.append(f"characters not in tbl/en.tbl: {''.join(bad)!r} (plain ASCII, ... for an ellipsis)")
    if name in LINK:
        bad = sorted({c for c in plain if c not in LINK_OK})
        if bad:
            out.append(f"link screen font lacks {''.join(bad)!r}: letters, digits, : ; ? ! - only")
    raw, cd = src.startswith("="), codec(name)
    want = codes_of(jp if raw or cd not in PAGE or not line_colour(jp, cd) else COL.sub("", jp))
    have = codes_of(en if raw else src)
    if want != have:
        out.append(f"control codes differ: JP {want} vs EN {have}")
    if re.search(r"\{name\}(st|nd|rd|th)\b", src):
        out.append("ordinal suffix glued to {name}")
    if re.search(r"\b(a|an|A|An)\s+\{name\}", src):
        out.append("a/an before {name}")
    font, budget, _, _, _ = blocks.BUDGET[name]
    cap = e.get("max")
    if font == "small" and smallfont.width(plain) > budget:
        out.append(f"{smallfont.width(plain)} px > {budget} px (small font)")
    if font == "cell" and budget and len(plain) > budget:
        out.append(f"{len(plain)} chars > {budget} cells")
    if cap and len(blocks.en_table("msg").encode(en)) > cap:
        out.append(f"{len(plain)} chars > {cap}-byte slot")
    # cell blocks with no budget (multiboot client strings): the whole block must fit its slot; build.py enforces it
    words = " ".join(CODE.sub("", s) for s in re.split(r"\{n\}|" + "|".join(map(re.escape, PAGE.values())), en))
    words = re.sub(r"\s+", " ", words)  # a term the wrap split over two lines still counts
    for term, ens, avoid in glossary():
        if has_term(jp, term) and ens and not any(a.lower() in words.lower() for a in ens):
            out.append(f"glossary: {term} -> {' or '.join(ens)} missing")
        for a in avoid:
            if re.search(r"\b" + re.escape(a) + r"\b", words):
                out.append(f"glossary: avoid {a!r}")
    return out


# ---- batches --------------------------------------------------------------------------------------------------
def entries():
    """[(block, entry)] of every text unit, in ORDER."""
    return [(n, e) for n in ORDER for e in load(n)["entries"] if "data" not in e]


def read_tsv(path):
    rows = []
    for ln in path.read_text(encoding="utf-8").splitlines():
        if ln.strip():
            rows.append(ln.split("\t"))
    return rows


def split(size, only):
    TL.mkdir(parents=True, exist_ok=True)
    TERMS.mkdir(exist_ok=True)
    existing = sorted(TL.glob("b[0-9][0-9][0-9].tsv"))
    queued = {r[0] for p in existing for r in read_tsv(p)}
    n = len(existing) + 1
    spk = speakers(rom())
    todo = [(b, e) for b, e in entries() if not e.get("en") and e["id"] not in queued and text_len(e["jp"]).strip()
            and (not only or re.search(only, e["id"]))]
    groups, cur, chars, last = [], [], 0, None
    for b, e in todo:
        key = b if b != "story" else ("story-a" if int(e["id"].split(".")[1]) < 15 else "story-b")
        if cur and (chars + len(text_len(e["jp"])) > size or (key != last and chars > size * 0.6)):
            groups.append(cur)
            cur, chars = [], 0
        cur.append((b, e))
        chars += len(text_len(e["jp"]))
        last = key
    if cur:
        groups.append(cur)
    terms = glossary()
    for g in groups:
        name = f"b{n:03}"
        path = TL / f"{name}.tsv"
        if path.exists():
            sys.exit(f"{path} exists; refusing to overwrite")
        rows = []
        for b, e in g:
            form, limit = form_limit(b, e)
            sp = spk.get(e["id"]) or SPEAKER.get(b, "menu")
            if b == "story" and sp == "narration":
                form = "narration"
            elif b == "story":
                form = "dlg"
            jp = jp_view(e["jp"], codec(b))
            if b == "rescue" and line_colour(e["jp"], "msg"):
                sp += " (hint, coloured)"
            rows.append("\t".join([e["id"], sp, form, limit, jp]))
        path.write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")
        hits = [f"{jp} -> {'; '.join(en)}" + (f" (avoid: {'; '.join(av)})" if av else "")
                for jp, en, av in terms if any(has_term(e["jp"], jp) for _, e in g)]
        (TERMS / f"terms_{name}.txt").write_text("\n".join(hits) + "\n", encoding="utf-8", newline="\n")
        print(f"{name}: {len(g)} units, {sum(len(text_len(e['jp'])) for _, e in g)} JP chars, {len(hits)} terms")
        n += 1


def by_id():
    return {e["id"]: (b, e) for b, e in entries()}


def check(name, quiet=False):
    """problems list of batch `name` (empty = OK)."""
    src_rows = read_tsv(TL / f"{name}.tsv")
    out_path = TL / f"{name}.out.tsv"
    if not out_path.exists():
        return [f"{out_path} missing"]
    ids = [r[0] for r in src_rows]
    got, probs = {}, []
    for r in read_tsv(out_path):
        if len(r) != 2:
            probs.append(f"{r[0]}: expected id<TAB>English, got {len(r)} columns")
            continue
        if r[0] in got:
            probs.append(f"{r[0]}: duplicate id")
        got[r[0]] = r[1]
    probs += [f"{i}: missing" for i in ids if i not in got]
    probs += [f"{i}: not in {name}.tsv" for i in got if i not in ids]
    units = by_id()
    for i in ids:
        if i in got:
            b, e = units[i]
            probs += [f"{i}: {p}" for p in problems(b, e, got[i])]
    return probs


def merge(names):
    for name in names:
        probs = check(name)
        if probs:
            sys.exit(f"{name}: {len(probs)} problems; run check")
    for name in names:
        got = dict(read_tsv(TL / f"{name}.out.tsv"))
        touched = {}
        units = by_id()
        for i, src in got.items():
            b, _ = units[i]
            touched.setdefault(b, {})[i] = src
        for b, edits in touched.items():
            doc = load(b)
            for e in doc["entries"]:
                if e["id"] in edits:
                    e["src"] = edits[e["id"]]
                    e["en"] = render(b, e["src"], e["jp"])[0]
            extract.write_doc(SCRIPT / f"{b}.json", doc)
        print(f"{name}: merged {len(got)} units into {', '.join(sorted(touched))}")


def lint():
    """Problems of every merged unit (src re-rendered); used by tests/test_batches.py."""
    out = []
    for b, e in entries():
        if "src" in e:
            out += [f"{e['id']}: {p}" for p in problems(b, e, e["src"])]
            if render(b, e["src"], e["jp"])[0] != e["en"]:
                out.append(f"{e['id']}: en is not the render of src (re-merge)")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("split")
    s.add_argument("--size", type=int, default=3000)
    s.add_argument("--only")
    for c in ("check", "merge"):
        sub.add_parser(c).add_argument("batch", nargs="+")
    f = sub.add_parser("fit")
    f.add_argument("block")
    f.add_argument("text")
    a = ap.parse_args()
    if a.cmd == "split":
        split(a.size, a.only)
    elif a.cmd == "check":
        bad = 0
        for b in a.batch:
            probs = check(b)
            print(f"{b}: OK" if not probs else "\n".join(probs))
            bad += bool(probs)
        sys.exit(1 if bad else 0)
    elif a.cmd == "merge":
        merge(a.batch)
    else:
        en, probs = render(a.block, a.text, a.text)
        for k, page in enumerate(en.split(PAGE.get(codec(a.block), "\0"))):
            for ln in page.split("{n}"):
                print(f"p{k + 1} {px(ln):3} px | {ln}")
        print("\n".join(probs) or "fits")


if __name__ == "__main__":
    main()
