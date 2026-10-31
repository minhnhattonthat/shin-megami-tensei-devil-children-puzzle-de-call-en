# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** phase 5 (engine spike + marker build) done 2026-11-01; next is phase 6 (translate). Width gate passed:
  every block has a measured budget (`blocks.BUDGET`, docs/re/vwf.md "Measured budgets").
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
- **Next (phase 6, translate):** set up `docs/translator-brief.md` / `docs/reviewer-brief.md` from the skill assets,
  `glossary.md` (demon names: check an official/English source), batch the 854 units with per-block budgets from
  `blocks.BUDGET` (big font: `vwf.width`, 224 px; last line of a page 210 px; small font: `smallfont.width`; cells:
  glyph count). Names: 15 glyphs and 67 px in the small font. Phase 7 lint reads `blocks.BUDGET`.
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
- **Open bugs:** none.
- **Waiting on the user:** nothing. (GUI keyboard check of `tools/mesen/Mesen.exe` not done: headless session; harmless.)
  Race mode and link trade need a second GBA (link cable): only the waiting screen is reachable.
