# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** phase 1 (recon) done 2026-11-01; next is phase 2 (debug tool). No build yet.
- **Done:**
  - Step 0: template, MesenCE 2.2.1 + GBA BIOS in `tools/mesen/`, guard hook proven, pre-commit runs `tools/check.py`,
    `rom.sha1` pinned, original ROM smoke-boots.
  - Phase 1 (docs/re/text.md, docs/re/graphics.md):
    - Encoding + `tbl/jp.tbl` (fixed 0x1E=石, 0xF2=口), big font LZ 0x160698, small 8 px font LZ 0x161FD0.
    - Story scripts 0x32A670 (roundtrip test); all other text mapped with pointer tables + xrefs: demon rescue /
      boss dialogue, save messages, pause / title menus, demon names (8-byte records, 167), tutorial (own command
      set, parse test `tests/test_tutorial.py`), link trade / transfer messages, DeviDas menu, multiboot client text.
    - ROM layout incl. multiboot loader + client images; free space 0x3529D0-0x3FFFFF verified (no code pointers,
      read-watch on 3 routes: 0 reads).
    - Graphics survey: tour of title + all 4 modes, static sweep of all 556 LZ blocks (4bpp + 8bpp) and the raw
      8bpp sprite region; every text block listed with offsets.
  - Tools added: `textscan.py`, `ptrtables.py`, `tutorial.py`, `gfxsweep.py`, `traptest.py`.
- **Next (phase 2, debug tool):**
  1. `tools/debug/scenes.txt` + `warp.lua`: find stage/scene id, story flags and save layout in RAM (ramsearch over
     ramdump between stages; watch who reads the story table index byte [0x03000BF3]). Scenes: each story chapter
     (both routes: scripts 0-14 / 15-28), story map, stage clear, boss fight, game over, ending, credits, save screens,
     デビライザー, DeviDas, puzzle mode, あそびかた parts 1-3.
  2. On each warped screen: match unknown graphics with `vramfind.py` vs `work/lzblocks/` (re-make with the snippet in
     git history or `tools/lz77.py dec`), close the "Not checked" list in docs/re/graphics.md.
  3. Runtime string log on readers 0800B53A (small font) and 0801B3B0 (story) during the scene tour.
- **Open bugs:** none.
- **Waiting on the user:** nothing. (GUI keyboard check of `tools/mesen/Mesen.exe` not done: headless session; harmless.)
  Race mode and link trade need a second GBA (link cable): only reachable as text/graphics, not by tour.
