# Graphics text survey (in progress)

Tile-drawn Japanese seen so far (boot + mash-A tour to frame 40000, `work/qa/explore2`). Static sweep not done yet.

| Screen | Element | Layer | Source guess |
|---|---|---|---|
| Title | 真・女神転生 デビルチルドレン パズルdeコール！ logo | BG | compressed tiles; no official English logo exists (DemiKids never had this game) -> translate per D5 |
| Title | PUSH START BUTTON, はじめから / あそびかた menu | BG/OBJ | はじめから also as text at 0x30E42F? check |
| Title menu (4 items, after Start) | ストーリー / フリー? / レース? / デビダス? (4 labels) | BG | unread; zoom needed |
| Character select | キャラクターセレクト banner, ランド / ゲイル plates | BG | compressed tiles |
| Puzzle HUD | てかず (moves), タマゴ (eggs), タイム (time) | BG | tiles |
| Puzzle pause menu | キャンセル もどす マップ デビライザー やりなおし はじめから やめる セーブ, panel headers デビライザー / デビルいちらん | BG, small 8px font | first four found as text at 0x34FA3x -> small font drawn at runtime; rest unknown |
