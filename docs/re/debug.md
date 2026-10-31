# Debug tool: game flow, warp points (phase 2)

Tool: `tools/debug/warp.lua` + `tools/debug/scenes.txt`; `tools/debug/warp_all.py` runs every scene from a cold boot
(shot, `work/states/<scene>.mss`, pass/fail). `tools/debug/scenelog.lua` logs state and story-variable changes.
Everything below is **verified** by the warp runs (logs in `work/qa/warp/<scene>/log.txt`) unless marked guess.

## Main loop (verified)
- 0800038C: `r2` = next state, `call table[r2]` (table **0x0830C408**, 12 u32), the handler returns the next state.
  The state lives only in `r2`: warp.lua hooks 0800038E and replaces `r2` the first time the title (0) is due.
- States: 0 title (08019D01), 1 puzzle select (0801F9B9), 2 DeviDas (0801DAE5), 3 story stage (08000445),
  4 puzzle stage (08000519), 5 race / link (08021621), 6 story text (0801BAE9), 7 tutorial (080005C5),
  8 character select (08000639), 9 save after an area (080006DD), 10 returns to title at once (080003D9),
  11 boot logos (0800075D).
- 0x03000934 / 0x03000938 are VBlank / HBlank callbacks, not scene ids.

## Story variables (verified)
- **0x03002B7C** route: 0 Rand (scripts 0-14), 1 Gale (15-28); copied to 0x03000BF2 at story init.
- **0x03002B78** (B78): story area counter. Story init (0801ACF0) picks the script: B78 0 = script 0 (intro); 1-6 =
  table 0x23BFB0 [route*6 + B78-1] = 1 4 6 8 10 12 / 15 18 20 22 24 26 (before area B78); 7-12 = table 0x23BFBC =
  3 5 7 9 11 13 / 17 19 21 23 25 27 (after area B78-6). Script index at 0x03000BF3.
- Script end (0801BBC2): scripts 0 1 13 15 27 chain to the next (0 -> 1 or 15 by route); others return to the loop.
- Flow, route 0: title -> 8 char select -> 6 (scripts 0, 1, 2) -> 3 area 1 -> 6 (script 3) -> 9 save -> 6 (script 4)
  -> 3 area 2 ... -> 6 (scripts 13, 14 = ending picture + おわり) -> 9 -> title. No staff roll found: no credits text in
  the font encoding (`work/textscan_all.txt`) and none after either ending; the ending is the おわり picture.
- Title (08019D9E): Story submenu はじめから -> B78=0, state 8; あそびかた -> B78 = [0x03002C10] (part 0-2, cycles) ->
  state 7; つづきから -> load 0x030009A0 -> state 6 / 3. Puzzle -> B78=0xFF, state 1. Idle -> attract demo = tutorial
  (B78 = [0x03002C14]). Race needs a link partner (state 5 shows the waiting screen).

## Stage (verified)
- State 3 (08000445) -> 080058E4 stage runner: area = B78-1 (struct [0x03002BD0]+1). Each area is one floor
  (0800EA84) then a boss fight (08012AAC). Floor result 0 -> boss; boss 0x63 -> state 3 returns 6 with B78 += 6
  (post-area script); boss 0x61 -> continue screen 080135BC (GAME OVER, retry/quit); 0x62 -> title.
- Event byte **[[0x03002BDC]+0x157C]**: set by game logic, read by the loop's player-control state 10.
  Floor (loop state r4, dispatch 0800EB34, table 0800EB80): 0x63 floor clear, 0x62 quit, 2 demon rescue dialogue
  (demon id at +0x158D), 0xC restart floor, 0xE retry, 4 = state 30 (nothing visible yet). Boss (r7, 08012B6C, table
  08012BB4): 0x63 win, 0x61 lose, 0x62 quit. A mashed A press writes 1 there (0800CE94), so warp.lua holds a forced
  value until the loop exits.
- In-stage keys: A = pause menu (キャンセル もどす マップ デビライザー やりなおし はじめから やめる セーブ, with the
  デビライザー and デビルいちらん panels), B = block selector.

## Puzzle mode (verified)
- State 4 (08000519) -> 080137BC: B78 = flag<<7 | difficulty<<4 | stage (0-9); loop 08017728 (r6 at 080177CE).
  0x63 at state 10 ends the loop; the returned byte decides: 0x18 = stage cleared (back to select, score shown),
  0x62 quit, else retry. warp.lua: PUZZLE_RESULT=0x63 PUZZLE_EXIT=0x18.

## Not reached yet
- Pause-menu デビライザー screen: the item is greyed and skipped by the cursor on a fresh floor. Drawing greys it
  while a count loaded at 0800BAB0 ([sp]) is 0; forcing that only un-greys it, the cursor code (near 0800CFAC) skips
  it separately. It probably needs a devil in デビルいちらん (a real rescue; the forced RESCUE_ID dialogue adds none).
  Next: find the devil-list RAM (ramsearch before / after a real rescue, or the struct read at 0800B9C0) and poke it.
- Save-file screens (つづきから with a save, the in-stage セーブ result), DeviDas sub-screens, puzzle-mode "all
  stages" run (B78 bit 7), floor result 4. Demon rescue texts: one scene (`rescue`, RESCUE_ID=5); the text tour
  (phase 8) can loop RESCUE_ID over all demons.
