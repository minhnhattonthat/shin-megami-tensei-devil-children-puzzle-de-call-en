# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** phase 3 (identity build) done 2026-11-01; next is phase 4 (extract). `build.py` builds an identical ROM.
- **Done:**
  - Step 0: template, MesenCE 2.2.1 + GBA BIOS in `tools/mesen/`, guard hook proven, pre-commit runs `tools/check.py`,
    `rom.sha1` pinned, original ROM smoke-boots.
  - Phase 1 (docs/re/text.md, docs/re/graphics.md): encoding + `tbl/jp.tbl`, fonts (LZ 0x160698 big, 0x161FD0 small),
    story scripts 0x32A670 (roundtrip test), all other text tables mapped, ROM layout, free space 0x3529D0-0x3FFFFF
    verified, graphics survey (tour + LZ sweep).
  - Phase 2 (docs/re/debug.md): main loop state table 0x0830C408 (12 states), story vars B78 0x03002B78 (area) /
    B7C 0x03002B7C (route), script tables, stage event byte [[0x03002BDC]+0x157C] (floor / boss / puzzle results),
    puzzle-mode stage select (B78 = diff<<4 | stage). `tools/debug/warp.lua` + `scenes.txt` (78 scenes: title menus,
    char select, all 29 story scripts, both endings, 12 area starts with the area card, 12 bosses, area clear ->
    post script, GAME OVER, demon rescue dialogue, pause menu + マップ / はじめから / やめる / セーブ prompts, save
    screen, puzzle select / 3 stages / clear, DeviDas, race, tutorial parts 1-3). `tools/debug/warp_all.py` runs
    all from cold boot: **78/78 ok**, shots `work/qa/warp/_finals/`, states `work/states/<scene>.mss`, `--ppu` VRAM
    dumps; vramfind summaries `work/qa/vf/` (graphics.md updated). `tools/debug/scenelog.lua` logs state changes.
    Test `tests/test_scenes.py`.
  - Phase 3 (docs/re/build.md): `build.py` + `tools/blocks.py` unpack/repack 10 packed string tables (incl. 2 in the
    multiboot client), 4 fixed-record blocks, 36 LZ blocks (fonts + all graphics text) -> byte-identical,
    `tests/test_identity.py` (also relocation to free space, client overflow error, LZ slot overflow error). `lz77.py`
    compressor now reproduces all 556 ROM LZ blocks exactly (`min_disp` 1 or 2, `lz77.mode()`). Smoke ok.
- **Next (phase 4, extract):** `script/*.json` per block from `blocks.py` (`id`, `ptr`, `jp`, `en`, `max`, ...), codecs:
  story = jp.tbl, msg tables need a menu tbl (FF end, FE newline, FC page, FD xx, F9 xx), tutorial commands, records
  (names 8 bytes, trade/transfer two 14-byte FF-padded lines with stale tail bytes: keep raw for unchanged). Roundtrip +
  coverage tests; then build.py reads `en`. Dump must never clobber `en`.
- **Carry-over (non-blocking):**
  - デビライザー screen not reached: needs a devil in デビルいちらん (debug.md "Not reached yet"). Add a scene when
    the devil-list RAM is found.
  - Pin exact tiles for puzzle select / race / DeviDas banners / char select plates; area start card source (guess:
    runtime-built; trace OAM tile writer) — graphics.md.
  - Runtime string log on readers 0800B53A (small font) and 0801B3B0 (story) over `warp_all` (phase 8 text tour);
    rescue dialogue for every demon via `--var RESCUE_ID=n` on scene `rescue`.
  - つづきから (continue with a save) and save-file screens: warp `pause_save`, save in game, keep the .sav as a
    fixture (`--sav`), then add a continue scene.
- **Open bugs:** none.
- **Waiting on the user:** nothing. (GUI keyboard check of `tools/mesen/Mesen.exe` not done: headless session; harmless.)
  Race mode and link trade need a second GBA (link cable): only the waiting screen is reachable.
