"""Phase 8 text tour: every story script, boss intro, rescue line and tutorial page, shot fully printed, as cropped
text-box contact sheets for visual QA (docs/visual-qa-brief.md).

    python -X utf8 tools/qa_tour.py [--rom build/pdc_en.gba] [--out work/qa/text] [--only REGEX] [--jobs 4]

Each run warps with tools/debug/warp.lua (a scene from tools/debug/scenes.txt, plus RESCUE_ID for the rescues),
presses A every MASH frames and shoots the frame before each press (tools/debug/pageshots.lua): a press while a page
types is ignored, except that A is held 6 frames and a page that finishes during the hold closes at once, never
shown complete: reshoot those runs with another `--mash` (e.g. 97) to move the presses. Sheets: <out>/_sheets/<run>.png (+ _2, _3 ...),
then `qa_gate.py init work/qa/text/manifest.tsv work/qa/text/_sheets`. Exit 1 if a run failed.
"""
import json
import hashlib
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "debug"))
from skill import SKILL  # noqa: E402
import warp_all  # noqa: E402

MASH = 120
STORY_MASH = 97  # avoids closing slow story pages on their final glyph
STORY_BOX, MSG_BOX = "0,104,240,56", "0,114,240,46"


def story_pages():
    pages = {}
    for e in json.loads((ROOT / "script" / "story.json").read_text(encoding="utf-8"))["entries"]:
        k = int(e["id"].split(".")[1])
        pages[k] = pages.get(k, 0) + e.get("en", "").count("{wait:00}") + 1
    return pages


def rescue_targets():
    """Message id -> a demon id that selects it (0800AF78, ROM table 081626A4).

    RESCUE_ID is a demon id, not the rescue string index. The old 0..100
    demon tour omitted 19 unique messages. Index 0 is the common join message.
    """
    import extract
    original = extract.ROM.read_bytes()
    targets = {}
    for demon in range(165):
        message = original[0x1626A5 + 2 * demon] + 1
        targets.setdefault(message, demon)
    if set(targets) != set(range(1, 101)):
        raise ValueError("rescue message mapping does not cover 1..100")
    return targets


def runs():
    """[(run name, warp scene, extra --var list, frames, crop)]"""
    out, pages = [], story_pages()
    for k, n in sorted(pages.items()):
        # the warp intro takes ~800 frames and scenes pause between boxes; the extra shots catch a page whose last
        # glyph lands on a press frame
        out.append((f"story_{k:02}", f"story_{k:02}", ["EXTRA_EVERY=30"], 2400 + n * (STORY_MASH + 140), STORY_BOX))
    for r in (0, 1):
        for a in range(1, 7):
            out.append((f"boss_r{r}_a{a}", f"boss_r{r}_a{a}", ["EXTRA_EVERY=30"], 1900, MSG_BOX))
    for message, demon in sorted(rescue_targets().items()):
        out.append((f"rescue_text_{message:03}", "rescue", [f"RESCUE_ID={demon}", "EXTRA_EVERY=30"], 1600, MSG_BOX))
    for t in (1, 2, 3):
        out.append((f"tutorial_{t}", f"tutorial_{t}", [f"TUTORIAL_ID={t-1}", "EXTRA_EVERY=30"], 60000, MSG_BOX))
    return out


def run(rom, outdir, item):
    name, scene, extra, frames, crop = item
    d = outdir / name
    cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "emu.py"), str(rom), "--out", str(d),
           "--script", str(ROOT / "tools" / "debug" / "warp.lua"), "--var", f"SCENE='{scene}'",
           "--script", str(ROOT / "tools" / "debug" / "pageshots.lua"), "--frames", str(frames),
           "--script", str(ROOT / "tools" / "debug" / "textlog.lua"),
           "--mash", str(0 if name.startswith("tutorial_") else STORY_MASH if name.startswith("story_") else MASH),
           "--timeout", "1500"]
    if name.startswith("tutorial_"):
        cmd += ["--script", str(ROOT / "tools/debug/tutorial_check.lua")]
    for v in extra:
        cmd += ["--var", v]
    with open(str(d) + ".log", "w", encoding="utf-8") as f:
        rc = subprocess.call(cmd, stdout=f, stderr=subprocess.STDOUT)
    if rc == 0 and name.startswith("rescue_text_"):
        expected = f"TEXT rescue.{int(name.rsplit('_', 1)[1]):03}"
        if expected not in (d / "log.txt").read_text(encoding="utf-8"):
            return name, 1
    if rc == 0 and name.startswith("tutorial_"):
        expected = f"TUTORIAL_DONE {int(name.rsplit('_', 1)[1]) - 1}"
        if expected not in (d / "log.txt").read_text(encoding="utf-8"):
            return name, 1
    if rc == 0:
        for old in (outdir / "_sheets").glob(f"{name}.png"):
            old.unlink()
        for old in (outdir / "_sheets").glob(f"{name}_[0-9]*.png"):
            old.unlink()
        rc = subprocess.call([sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "sheet.py"), str(d),
                              "--crop", crop, "--zoom", "2", "--changed", "0.0002", "--cols", "3", "--max", "24",
                              "--from", "300", "--out", str(outdir / "_sheets" / f"{name}.png")],
                             stdout=subprocess.DEVNULL)
    return name, rc


def main():
    a = sys.argv[1:]
    opt = lambda k, d: a[a.index(k) + 1] if k in a else d  # noqa: E731
    rom = Path(opt("--rom", str(ROOT / "build" / "pdc_en.gba")))
    rom_sha1 = hashlib.sha1(rom.read_bytes()).hexdigest()
    outdir = Path(opt("--out", str(ROOT / "work" / "qa" / "text")))
    only = re.compile(opt("--only", "."))
    global MASH, STORY_MASH
    MASH = int(opt("--mash", MASH))
    STORY_MASH = int(opt("--story-mash", STORY_MASH))
    (outdir / "_sheets").mkdir(parents=True, exist_ok=True)
    known = {s[0] for s in warp_all.scenes()}
    todo = [r for r in runs() if only.search(r[0])]
    assert all(r[1] in known for r in todo), "scene missing from tools/debug/scenes.txt"
    with ThreadPoolExecutor(int(opt("--jobs", "4"))) as ex:
        res = list(ex.map(lambda r: run(rom, outdir, r), todo))
    bad = [n for n, rc in res if rc]
    receipt = outdir / "rom.sha1"
    if not bad and hashlib.sha1(rom.read_bytes()).hexdigest() == rom_sha1:
        if {"tutorial_1", "tutorial_2", "tutorial_3"} <= {n for n, _ in res}:
            (outdir / "tutorial.sha1").write_text(rom_sha1 + "\n", encoding="ascii")
        if len(todo) == len(runs()):
            receipt.write_text(rom_sha1 + "\n", encoding="ascii")
        elif receipt.exists() and receipt.read_text().strip() != rom_sha1:
            receipt.unlink()  # a filtered update cannot certify the remaining old runs
    else:
        if receipt.exists():
            receipt.unlink()
        if not bad:
            bad.append("ROM changed during tour")
    for n in bad:
        print(f"FAIL {n} (see {outdir / n}.log)")
    print(f"{len(res) - len(bad)}/{len(res)} runs ok; sheets in {outdir / '_sheets'}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
