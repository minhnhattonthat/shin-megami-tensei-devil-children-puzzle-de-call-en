# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** phase 9 (local release) complete 2026-11-01: phase 7 Important fixed and committed (`f41ab0e`),
  both review Minors implemented, 56 line-specific polish edits, all seven chapters approved in a fresh read-only
  Codex pass (`docs/story-review.md`). The final boss HUD fix has red/green runtime evidence and an all-ROM
  literal regression scan. Final ROM `bd858d3c1f07e0e1516de1f9185cd87e5a22fcc5` passes 43 tests, cold boot,
  78 scene warps, the 144-run dialogue tour, three fully completed automatic tutorials, longest-real-name pause
  stress and every active visual/story gate. BPS and ZIP reapplication both reproduce the exact final ROM.
  Local archive: `release/Devil_Children_Puzzle_de_Call_EN_v1.0.zip` (BPS + README only),
  SHA-1 `d7ec8a2bb63d93d98f4652b7b2ab48f21fe91264`. Full results: `docs/release-review.md`.
  Published 2026-11-01 (D10): repo public, GitHub release v1.0 with this ZIP.
  Rescue tour correction: the old demon-ID sweep missed 19 dialogue IDs; new lookup-driven tour covers every
  rescue.001..100 plus shared rescue.000, with runtime pointer logging (`tools/debug/textlog.lua`).
  All 837 text units
  translated (`script/*.json`: `src` = authored English, `en` = rendered with codes), batch check 0 errors,
  reviewer pass on every batch b001-b011 with every Critical/Important fixed (`docs/reviews.md`, incl. the external
  phase 6 review fixes: raw-unit gate, honorific check, whole-word glossary match, rescue.095), Minors in
  `docs/polish.md`.
- **Done:**
  - Phase 7 external review Important #1 fixed: actual `en` validated without `src`; final-build coverage includes
    every non-empty original name/record/string, with an empty committed reasoned keep-list and explicit test modes.
    Regression checks cover missing sources, empty translations, direct-English overflow and incomplete name maps.
  - Step 0: template, MesenCE 2.2.1 + GBA BIOS in `tools/mesen/`, guard hook proven, pre-commit runs `tools/check.py`,
    `rom.sha1` pinned, original ROM smoke-boots.
  - Phase 1 (docs/re/text.md, docs/re/graphics.md): encoding + `tbl/jp.tbl`, fonts (LZ 0x160698 big, 0x161FD0 small),
    story scripts 0x32A670, all other text tables mapped, ROM layout, free space 0x3529D0-0x3FFFFF verified, graphics
    survey.
  - Phase 2 (docs/re/debug.md): `tools/debug/warp.lua` + `scenes.txt` (78 scenes), `tools/debug/warp_all.py`
    (`--rom`, `--out`, `--only`; a build's states go to a subfolder). 78/78 ok on the original.
  - Phase 3 (docs/re/build.md): `build.py` repacks every text table, record block and LZ block byte-identical.
  - Phase 4 (docs/re/build.md "Script files"): `tools/extract.py` -> `script/*.json`, 15 files, 854 units.
  - Phase 5 (docs/re/vwf.md): English engine in `asm/vwf.s` (keystone via `tools/asm.py`, Thumb-2 refused), at
    0x3F0000: VWF for story / message / tutorial boxes (224 px lines), proportional pen for the 8x8 menu font, DeviDas
    name bitmap, names moved to 16-byte records (15 glyphs). `tbl/en.tbl` shared by all codecs; fonts
    `fonts/vwf.txt`, `fonts/small.txt` (drawn, MIT). Marker build `tools/marker.py` (`--set ID=TEXT|TORTURE|TORTURE2`,
    `--out`): 78/78 scenes, independent visual-QA verdict (`work/qa/verdicts/p5_marker.tsv`; 2 issues resolved),
    torture lines clean in both boxes. Race menu labels (00-padded, missed by strayscan) found and extracted
    (`script/race_menu.json`, 16 + 14 bytes). Test: every block has a budget.
  - Phase 6: `tools/batches.py` (split / check / merge / fit: auto-wraps each page to 224 px + 210 px last line,
    fails 3-line pages, msg sprite cap 32/page, small-font px, cell / byte slots, glossary whole-run match, codes,
    link-font charset), `tools/pairs.py` (reviewer pairs, `--chapters` for the story pass), `tests/test_batches.py`
    (every merged `src` re-renders to `en` and passes). Glossary: official DemiKids names (D8; Imperium, Demiloc,
    Demonary, Sol Cat, Rox...). Docs: `docs/synopsis.md`, `docs/style-reference.md` (pilot = prologue, checked
    in-game `work/qa/pilot`), translator / reviewer briefs. Batches b001-b011 in `work/tl/` (gitignored). Centred
    ending lines and multiboot link lines are raw `=` units (hand-laid). Story speakers come from face codes
    (`batches.FACES`: A3 Jin, A4 Akira, 00 Rand, 01 Gale, else demon id = names index).
  - Phase 7 (docs/re/build.md "Checks"): `build.verify` gates every `build.py` and `tests/test_build_en.py`:
    romdiff write log, writes only inside `build.allowed()`, every string read back through its pointer with its
    control codes, no stale pointer into a moved block's old slot, no branch into a hook. `jp_left.py` doesn't apply
    (English reuses the kana byte codes); read-back is the text-side leftover check. English tour
    `warp_all.py --rom build/pdc_en.gba --out work/qa/p7`: 78/78 ok (sheets `work/qa/p7/_finals`, no verdicts yet).
    Build sha1 814f33e6..., smoke ok.
- **Phase 8 (QA in the emulator) done 2026-11-01:** build sha1 30fce11a..., smoke ok; `qa_gate.py check` exits 0 on
  `work/qa/text` (238 boss / rescue / tutorial sheets; its 46 story rows moved out to `manifest.full.tsv`, story is
  covered by text3), `work/qa/text3` (267 story sheets) and `work/qa/p8` (78 warp scenes + 3 extra shots on the final
  build, graphics checked English by visual-QA, verdicts `work/qa/p8/verdicts`). Superseded by phase 9 above.
  - Menu font fix from QA: English small-font ink starts at tile col 1 (`smallfont.LEFT`); col 0 fell outside the
    highlight bars ("Yes" read "Ses", "Back" read "Sack").
  - Text tour `tools/qa_tour.py` (`--only REGEX --mash N --out DIR --jobs N`; no `--help`: unknown args run the
    full tour): story 0-28, boss x12, rescue 0-100, tutorial 1-3; cropped 2x sheets + gate (`qa_gate.py`).
    Round 1-2 (`work/qa/text*`): one-word last lines -> `batches.wrap` splits 2-line segments evenly and prefers a
    sentence end. Round 4-5 story reshoot `work/qa/text3` (`--mash 97`, 267 sheets, verdicts
    `work/qa/text3/verdicts/*.tsv`): no text faults; the only issues were pages closed by an A press on their last
    glyph, rechecked in `work/qa/text4` (`--mash 83`, verdict `r5_reshoot.tsv`). Verdict files must have unique
    names per round (round 4 overwrote round 3's chunk_00N.tsv; redone as r5_*).
  - Graphics text `tools/gfx.py` (LABELS; `oam PREFIX DIR` dumps on-screen sprites; `preview` breaks on grid
    labels): English = title menu, story submenus, pause headers, stage HUD, puzzle HUD + select record (raw copy
    0x2AAEB0, `blocks.RAW`), area start cards (Embel Spring ... Quadriga, atwiki names), Start! / Clear!!, puzzle
    stage card (Easy / Normal / Hard, Stage), char select, puzzle select banner + headers, race banner, DeviDas
    banner / labels / values / elements (official DemiKids terms; element sprite 16x16 -> 32x8 hook 0x1CADA).
    All checked in game (`work/qa/g14`-`g18`, `work/qa/cards`). Kept JP: title logo (D5: no official English logo),
    the six area_N plates (loaded, never seen on screen), unreferenced LZ twin 0x2AADE0. Clear!! not seen in game
    (no reachable floor-clear call-out); same format as Start!, which renders right.
  - Pause map / Demiloc / save prompt / game over menu: English (`work/qa/g12/_finals`).
- **Carry-over (non-blocking):**
  - Link trade, multiboot-client gameplay and two-GBA races remain untested; their text is translated but layout
    budgets are conservative slot limits. Fixed-cell race-menu text has wide spacing.
  - Original-game save migration, other emulators and real hardware are not certified.
  - Japanese title logo, six unobserved area plates and an unreferenced puzzle-label duplicate are retained;
    translated Clear!! is not observed in-game. See the release README for these disclosed limits.
- **Phase 9 QA corrections:** boss HUD interior pointer relocated; actual rescue-message mapping now covers
  all 100 messages; automatic tutorials run without button presses and require completion markers. The older
  tutorial-labelled text sheets actually skipped into the prologue and are superseded by `tutorial_final`.
  Full 144-run final-ROM capture is complete; final scene gate 85/85 and no-input tutorial gate 56/56 pass.
  Longest-real-name pause stress, boss.000 substitution, Mecci's symbols and ending centring are checked.
  Capture-only punctuation gaps have complete-page reshoot evidence in `work/qa/final_evidence`.
- **Completion recheck (2026-11-01):** release commit `0991a23` confirmed on `origin/main`; all 43 tests,
  all ten active QA manifests and the polish checklist pass again. Fresh cold boot passes in
  `work/qa/completion_smoke`. The existing ZIP and standalone BPS were checked without repackaging;
  applying the archived patch to the pinned original reproduces the final ROM hash above exactly.
- **Next:** none; v1.0 published. Handle player bug reports from GitHub issues.
- **Open bugs:** none known after final visual review; untested configurations are disclosed above.
- **Waiting on the user:** nothing. (GUI keyboard check of `tools/mesen/Mesen.exe` not done: headless session; harmless.)
  Race mode and link trade need a second GBA (link cable): only the waiting screen is reachable.
