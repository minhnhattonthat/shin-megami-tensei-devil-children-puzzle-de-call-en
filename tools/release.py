"""Build, test, cold-boot, tour, gate and package a local BPS release (never publish).

    python -X utf8 tools/release.py --version 1.0
After reviewing newly captured sheets, rerun with --skip-tour to reuse the exact
same ROM's tour. No version's artifacts are overwritten without --force.
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import bps
import build
import extract
from skill import SKILL

QA = ROOT / "work/qa"
TOUR = QA / "p9"
STEM = "Devil_Children_Puzzle_de_Call_EN_v"


def run(*args):
    subprocess.run([sys.executable, "-X", "utf8", *map(str, args)], cwd=ROOT, check=True)


def digest(data):
    return hashlib.sha1(data).hexdigest()


def gate(manifest):
    run(Path(SKILL) / "scripts/qa_gate.py", "check", manifest, manifest.parent / "verdicts")


def polish_gate(path):
    pending = re.findall(r"^\s*-\s*\[ \].*$", path.read_text(encoding="utf-8"), re.M)
    if pending:
        raise ValueError(f"{len(pending)} unticked polish findings:\n" + "\n".join(pending))


def package(original, translated, version, destination):
    name = STEM + version
    patch = bps.make(original, translated)
    if bps.apply(original, patch) != translated:
        raise ValueError("finished BPS did not reproduce the build")
    readme = (ROOT / "docs/release-readme.txt").read_text(encoding="utf-8")
    for token, value in {
        "VERSION": version, "BASE_SIZE": str(len(original)),
        "BASE_SHA1": digest(original), "BASE_MD5": hashlib.md5(original).hexdigest(),
        "BASE_CRC32": f"{zlib.crc32(original):08X}", "PATCHED_SHA1": digest(translated),
        "PATCHED_CRC32": f"{zlib.crc32(translated):08X}", "PATCH_SHA1": digest(patch),
        "PATCH_NAME": name + ".bps",
    }.items():
        readme = readme.replace("{{" + token + "}}", value)
    if "{{" in readme:
        raise ValueError("unexpanded README placeholder")
    destination.mkdir(parents=True, exist_ok=True)
    patch_path, zip_path = destination / (name + ".bps"), destination / (name + ".zip")
    patch_path.write_bytes(patch)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(name + ".bps", patch)
        archive.writestr("README.txt", readme)
    with zipfile.ZipFile(zip_path) as archive:
        if set(archive.namelist()) != {name + ".bps", "README.txt"} or archive.testzip():
            raise ValueError("invalid release ZIP contents")
        if bps.apply(original, archive.read(name + ".bps")) != translated:
            raise ValueError("ZIP's BPS did not reproduce the build")
    print(f"Verified {zip_path.relative_to(ROOT)}; ROM SHA-1 {digest(translated)}")
    return zip_path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", default="1.0")
    parser.add_argument("--force", action="store_true", help="overwrite this version's local artifacts")
    parser.add_argument("--skip-tour", action="store_true", help="reuse a completed tour of this exact ROM")
    args = parser.parse_args(argv)
    if not re.fullmatch(r"[0-9]+\.[0-9]+(?:\.[0-9]+)?", args.version):
        parser.error("version must be numeric X.Y or X.Y.Z")
    destination = ROOT / "release"
    if not args.force and any((destination / (STEM + args.version + ext)).exists() for ext in (".bps", ".zip")):
        parser.error("version already exists; choose a new version or explicitly use --force")
    run(ROOT / "build.py")  # actual-en lint, original SHA-1, complete coverage and ROM read-back
    run(ROOT / "tools/check.py")  # includes original roundtrip, fresh identity/English builds, ROM write/branch checks
    run(Path(SKILL) / "scripts/emu.py", build.OUT, "--out", QA / "release_smoke",
        "--route", ROOT / "tools/routes/boot.txt", "--smoke")
    original, translated = build.ROM.read_bytes(), build.OUT.read_bytes()
    # The English codec reuses kana byte codes; jp_left.py would flag English as
    # kana. build.verify checks every reachable unit against its English instead.
    if any(re.search(r"[\u3040-\u30ff\u4e00-\u9fff]", en) for en in extract.en_map().values()):
        raise ValueError("Japanese remains in English text")
    receipt = TOUR / "rom.sha1"
    if args.skip_tour:
        if not receipt.is_file() or receipt.read_text().strip() != digest(translated):
            raise ValueError("no completed tour of this exact ROM; omit --skip-tour")
    else:
        run(ROOT / "tools/debug/warp_all.py", "--rom", build.OUT, "--out", TOUR)
        run(Path(SKILL) / "scripts/qa_gate.py", "init", TOUR / "manifest.tsv", TOUR / "_finals", "--glob", "*.png")
        receipt.write_text(digest(translated) + "\n", encoding="ascii")
        run(ROOT / "tools/qa_tour.py", "--rom", build.OUT, "--out", QA / "tutorial_final", "--only", "^tutorial_")
        run(Path(SKILL) / "scripts/qa_gate.py", "init", QA / "tutorial_final/manifest.tsv",
            QA / "tutorial_final/_sheets", "--glob", "*.png")
    # Regenerate review input from the current script so old story verdicts
    # cannot approve a changed chapter merely because its pairs file was stale.
    run(ROOT / "tools/pairs.py", "--chapters")
    run(Path(SKILL) / "scripts/qa_gate.py", "init", QA / "story/manifest.tsv", QA / "story/chapters", "--glob", "*.txt")
    required = [TOUR / "manifest.tsv", QA / "story/manifest.tsv", QA / "text/manifest.tsv",
                QA / "text3/manifest.tsv", QA / "p8/manifest.tsv", QA / "polish/manifest.tsv",
                QA / "tutorial_final/manifest.tsv"]
    if any(not p.is_file() for p in required):
        raise ValueError("required visual, polish or story QA manifest is missing")
    text_receipt = QA / "polish/rom.sha1"
    if not text_receipt.is_file() or text_receipt.read_text().strip() != digest(translated):
        raise ValueError("full text tour must be bound to this exact ROM")
    tutorial_receipt = QA / "tutorial_final/tutorial.sha1"
    if not tutorial_receipt.is_file() or tutorial_receipt.read_text().strip() != digest(translated):
        raise ValueError("complete no-input tutorial tour must match this ROM")
    for part in range(3):
        log = (QA / f"tutorial_final/tutorial_{part + 1}/log.txt").read_text(encoding="utf-8")
        if f"TUTORIAL_DONE {part}" not in log:
            raise ValueError(f"tutorial {part + 1} was skipped or did not finish")
    for manifest in sorted(QA.rglob("manifest.tsv")):
        gate(manifest)
    polish_gate(ROOT / "docs/polish.md")
    # Debug warps are host-side Lua passed only to the emulator, never linked
    # into build.py's release image. Ensure QA did not mutate the playable ROM.
    if build.OUT.read_bytes() != translated:
        raise ValueError("ROM changed during QA")
    package(original, translated, args.version, destination)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, subprocess.CalledProcessError) as exc:
        sys.exit(str(exc))
