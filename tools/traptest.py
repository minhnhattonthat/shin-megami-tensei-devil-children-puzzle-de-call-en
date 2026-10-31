"""Trap-test free space: watch every CPU read of a ROM range while playing the mode-tour routes.

    python -X utf8 tools/traptest.py [--lo 3529D0] [--hi 3FFFFF] [--frames 12000] [--rom ROM]
Uses the skill's watch.lua probe (read mode) on the original ROM by default; logs land in work/qa/trap_<mode>/log.txt.
Exit 1 if any route read the range. (Screenshot diffs are useless here: shots of two runs of the same ROM differ.)
A clean run only covers the routes it took; the static check is "no code pointer into the range" (docs/re/text.md).
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL  # noqa: E402

# title menu: Story, Puzzle, Race, DeviDas; Race needs a link partner, so it is left out
MODES = {"story": 0, "puzzle": 1, "devidas": 3}


def route(downs):
    return "600 -;6 start;200 -" + "".join(";6 down;30 -" for _ in range(downs)) + ";6 a;120 -"


def main():
    a = sys.argv[1:]
    lo = int(a[a.index("--lo") + 1], 16) if "--lo" in a else 0x3529D0
    hi = int(a[a.index("--hi") + 1], 16) if "--hi" in a else 0x3FFFFF
    frames = a[a.index("--frames") + 1] if "--frames" in a else "12000"
    rom = Path(a[a.index("--rom") + 1]) if "--rom" in a else next((ROOT / "rom").glob("*.gba"))
    probe = Path(SKILL) / "scripts" / "lua" / "probes" / "watch.lua"
    procs = {}
    for m, downs in MODES.items():
        out = ROOT / "work" / "qa" / ("trap_" + m)
        procs[m] = (out, subprocess.Popen(
            [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "emu.py"), str(rom), "--out", str(out),
             "--route-str", route(downs), "--frames", frames, "--mash", "50", "--script", str(probe),
             "--var", "WATCH_LO=0x%08X" % (0x08000000 + lo), "--var", "WATCH_HI=0x%08X" % (0x08000000 + hi),
             "--var", "WATCH_MODE='read'"], stdout=subprocess.DEVNULL))
    bad = 0
    for m, (out, p) in procs.items():
        rc = p.wait()
        hits = [ln for ln in (out / "log.txt").read_text().splitlines() if " read pc=" in ln]
        print("%-8s exit %d, %d reading PCs %s" % (m, rc, len(hits), hits[:3]))
        bad += len(hits) + (rc != 0)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
