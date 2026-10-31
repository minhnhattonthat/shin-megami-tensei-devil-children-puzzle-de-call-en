"""Reviewer input: JP/EN pairs of a batch (or of story chapters) with neighbouring lines for context.

    python -X utf8 tools/pairs.py bNNN [bNNN ...]       # -> work/tl/bNNN.pairs.txt (from bNNN.out.tsv)
    python -X utf8 tools/pairs.py --chapters             # -> work/qa/story/chapters/<chapter>.txt (merged en)
`>> id | speaker | JP` then `EN` (` / ` line, ` // ` page in JP; ` // ` page in EN). Context lines (`   id`) are the
2 entries before and after each batch entry that are not in the batch.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import batches  # noqa: E402

# story chapters for the story pass (docs/synopsis.md): prologue, Rand's route, Gale's route, bosses, rescues, tutorial
CHAPTERS = [("ch0_prologue", r"^story\.000\."), ("ch1_rand", r"^story\.0(0[1-9]|1[0-4])\."),
            ("ch2_gale", r"^story\.0(1[5-9]|2[0-8])\."), ("ch3_bosses", r"^boss\."), ("ch4_rescue", r"^rescue\."),
            ("ch5_tutorial", r"^tutorial\."), ("ch6_system", r"^(system|pause|yesno|titlemenu|devidas_menu|"
                                                            r"race_menu|trade|transfer|client_)")]


def en_view(src, en):
    s = src if src and not src.startswith("=") else en
    return s.lstrip("=").replace("{wait:00}{clr}{box:09}", " // ").replace("{page}", " // ").replace("{n}", " / ")


def rows():
    """[(id, speaker, jp view, block)] of every unit in story order."""
    spk = batches.speakers(batches.rom())
    out = []
    for b, e in batches.entries():
        sp = spk.get(e["id"]) or batches.SPEAKER.get(b, "menu")
        out.append((e["id"], sp, batches.jp_view(e["jp"], batches.codec(b)), e))
    return out


def write(path, ids, en):
    allr = rows()
    pos = {r[0]: k for k, r in enumerate(allr)}
    keep = sorted({j for i in ids for j in range(pos[i] - 2, pos[i] + 3) if 0 <= j < len(allr)})
    lines, prev = [], None
    for j in keep:
        i, sp, jp, e = allr[j]
        if prev is not None and j != prev + 1:
            lines.append("")
        mark = ">>" if i in ids else "  "
        lines.append(f"{mark} {i} | {sp} | {jp}")
        txt = en.get(i) if i in en else en_view(e.get("src", ""), e.get("en", ""))
        lines.append(f"   {txt or '(untranslated)'}")
        prev = j
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"{path}: {len(ids)} entries")


def main():
    if sys.argv[1:] == ["--chapters"]:
        allr = rows()
        for name, rx in CHAPTERS:
            ids = [r[0] for r in allr if re.search(rx, r[0]) and r[3].get("en")]
            write(ROOT / "work" / "qa" / "story" / "chapters" / f"{name}.txt", ids, {})
        return
    every = {}  # context lines from any batch output, translated or merged
    for p in sorted(batches.TL.glob("b*.out.tsv")):
        every.update(dict(r for r in batches.read_tsv(p) if len(r) == 2))
    for b in sys.argv[1:]:
        out = dict(batches.read_tsv(batches.TL / f"{b}.out.tsv"))
        write(batches.TL / f"{b}.pairs.txt", list(out), every)


if __name__ == "__main__":
    main()
