"""Warp to every scene in tools/debug/scenes.txt from a cold boot: shot, savestate, pass/fail per scene.

    python -X utf8 tools/debug/warp_all.py [--rom ROM] [--jobs 4] [--only REGEX] [--out work/qa/warp] [--ppu]
--ppu also dumps VRAM/palette/OAM on the last frame (<out>/<name>/ppu_*.vram.bin) for vramfind.py.
Per scene: <out>/<name>/ (emu.py output, final.png = the proof shot), work/states/<name>.mss, and
<out>/_finals/<name>.png for one contact sheet (<out>/_finals/sheet*.png). Exit 1 if any scene failed: emu.py
error, or its log lacks "warp NAME" or the scene's expected text. Regenerate after engine, font or graphics changes.
"""
import re
import shlex
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL  # noqa: E402


def scenes(path=ROOT / "tools" / "debug" / "scenes.txt"):
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0]
        if not line.strip():
            continue
        parts = [p.strip() for p in line.split("|")] + ["", ""]
        name = parts[0].split()[0]
        out.append((name, shlex.split(parts[1]) or ["--frames", "900"], parts[2]))
    return out


def run(rom, outdir, scene, ppu=False):
    name, args, expect = scene
    if ppu:  # VRAM/palette/OAM dump on the last frame, for vramfind.py
        args = args + ["--script", str(Path(SKILL) / "scripts" / "lua" / "probes" / "ppudump.lua")]
    out = outdir / name
    state = ROOT / "work" / "states" / (name + ".mss")
    state.parent.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "emu.py"), str(rom), "--out", str(out),
           "--script", str(ROOT / "tools" / "debug" / "warp.lua"), "--var", "SCENE='%s'" % name,
           "--state-out", str(state)] + args
    with open(str(out) + ".log", "w", encoding="utf-8") as f:
        rc = subprocess.call(cmd, stdout=f, stderr=subprocess.STDOUT)
    log = (out / "log.txt").read_text(encoding="utf-8") if (out / "log.txt").exists() else ""
    ok = rc == 0 and ("warp %s:" % name) in log and expect in log
    if (out / "final.png").exists():
        shutil.copy(out / "final.png", outdir / "_finals" / (name + ".png"))
    return name, ok, rc, expect


def main():
    a = sys.argv[1:]
    opt = lambda k, d: a[a.index(k) + 1] if k in a else d  # noqa: E731
    rom = Path(opt("--rom", str(next((ROOT / "rom").glob("*.gba")))))
    outdir = Path(opt("--out", str(ROOT / "work" / "qa" / "warp")))
    only = re.compile(opt("--only", "."))
    todo = [s for s in scenes() if only.search(s[0])]
    (outdir / "_finals").mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(int(opt("--jobs", "4"))) as ex:
        res = list(ex.map(lambda s: run(rom, outdir, s, "--ppu" in a), todo))
    bad = [r for r in res if not r[1]]
    for name, ok, rc, expect in res:
        print("%-16s %s%s" % (name, "ok" if ok else "FAIL", "" if ok else " (exit %d, want %r)" % (rc, expect)))
    subprocess.call([sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "sheet.py"),
                     *[str(outdir / "_finals" / (r[0] + ".png")) for r in res if (outdir / "_finals" / (r[0] + ".png")).exists()],
                     "--out", str(outdir / "_finals" / "sheet.png")], stdout=subprocess.DEVNULL)
    print("%d/%d scenes ok; sheets in %s" % (len(res) - len(bad), len(res), outdir / "_finals"))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
