# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** phase 6 (translate) done 2026-11-01; next is phase 7 (insert, fit, check). All 837 text units
  translated (`script/*.json`: `src` = authored English, `en` = rendered with codes), batch check 0 errors,
  reviewer pass on every batch with every Critical/Important fixed (`work/tl/reviews.md`), Minors in `docs/polish.md`.
- **Done:**
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
- **Next (phase 7, insert / fit / check):** lint is in place (`batches.lint`, run by the check); add `romdiff.py`
  with the build's write log to the check, confirm control codes per block, then a QA tour of the English build
  (`warp_all.py --rom build/pdc_en.gba --out work/qa/p6` was run at the end of phase 6: see its log). Then phase 8
  visual QA, story pass (`tools/pairs.py --chapters`), polish pass (`docs/polish.md`).
- **Carry-over (non-blocking):**
  - Race menu printer (080205FE) is fixed 8 px cells, English glyphs sit left in their cell (`R0. 0`): proportional
    pen or a centred copy of the font there = phase 7 polish. Race needs a link partner; only the menu is reachable.
  - Pause screen OBJ pool: very long names in all lists + long items ran it dry in a stress build; re-check with the
    longest real names after translation (docs/re/vwf.md).
  - Small font `q` looks like `9` (game glyph); redraw if a menu word needs `q`.
  - Multiboot client strings (client_*, trade, transfer) and devidas_menu: link-only, budgets are slot guesses.
  - デビライザー screen not reached (needs a devil in デビルいちらん); つづきから / save-file screens need a .sav fixture.
  - Graphics text (title plates, banners, list headers, area cards): phase 7/8 (docs/re/graphics.md).
  - Warp scenes are timed for Japanese; marker / English text types slower (ending_r0 needs ~9000 frames to reach
    おわり). Re-time scenes in phase 8 if shots catch text mid-print.
  - In-game checks the reviewers asked for: boss.000 "{name}, let's go!!!" (who is {name}?), rescue.025 (symbols
    line), tutorial pages with many colour runs, ending centring (story.014.31 / 028.34), title "Start" at 40 px.
  - Client pause block is exactly full (24 bytes: Back / Undo / Retry / Stage 1).
- **Open bugs:** none.
- **Waiting on the user:** nothing. (GUI keyboard check of `tools/mesen/Mesen.exe` not done: headless session; harmless.)
  Race mode and link trade need a second GBA (link cable): only the waiting screen is reachable.
