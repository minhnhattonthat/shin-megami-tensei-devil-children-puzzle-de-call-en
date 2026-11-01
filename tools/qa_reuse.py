"""Reuse approved visual verdicts only for byte-identical contact sheets.

    python tools/qa_reuse.py work/qa/polish/manifest.tsv
Runs after the tour and qa_gate init. Writes inherited.tsv and prints how many
images still need a fresh review. Changed images never inherit a verdict.
"""
import argparse
import sys
from pathlib import Path
from skill import SKILL

sys.path.insert(0, str(Path(SKILL) / "scripts"))
import qa_gate

ROOT = Path(__file__).resolve().parents[1]


def reuse(target):
    approved = {}
    for manifest in sorted((ROOT / "work/qa").rglob("manifest.tsv")):
        if manifest.resolve() == target.resolve():
            continue
        rows, missing, bad, moved = qa_gate.problems(str(manifest), str(manifest.parent / "verdicts"))
        excluded = set(missing) | {i for i, _ in bad} | set(moved)
        for uid, (path, sha, _) in rows.items():
            if uid not in excluded and Path(path).suffix.lower() == ".png" and sha:
                approved[sha] = f"{manifest.relative_to(ROOT).as_posix()}:{uid}"
    lines = []
    rows = qa_gate.read_manifest(str(target))
    for uid, (path, sha, _) in rows.items():
        if sha in approved and qa_gate.sha1(path) == sha:
            lines.append(f"{uid}\tok\tByte-identical to previously reviewed {approved[sha]}; SHA-1 {sha}")
    dest = target.parent / "verdicts/inherited.tsv"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"{len(lines)}/{len(rows)} byte-identical approved images; remaining images require fresh visual review")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    reuse(parser.parse_args().manifest)
