# Translator brief - Shin Megami Tensei: Devil Children - Puzzle de Call! (GBA, 2002)

You translate part of the Japanese script of Devil Children: Puzzle de Call! into English for a fan patch. A kids'
puzzle-adventure spin-off of DemiKids Light/Dark: Jin, Akira and their partner demons Rand and Gale are sucked into a
miniature world where the Imperium drains captive demons' magic. Light, quick, jokey banter; pompous villains.
Work only on the batches named in your dispatch, one at a time in the order given, each to a passing check before
the next. Do all translation yourself; do not dispatch subagents. Never edit anything except your own
`work/tl/<batch>.out.tsv` files.

## Read first
1. `docs/style-reference.md` - character voices and approved example pairs. Match this voice.
2. `build/terms_<batch>.txt` - binding glossary rows for this batch. `glossary.md` has the full table and the
   style rules (read its "Rulings" and "Style rules" sections once).
3. `docs/synopsis.md` - plot, both routes, who is who. Don't name Azrael as the creator before script 11 (route 1) /
   21 (route 2) reveals it.

## Input: `work/tl/<batch>.tsv`
`id<TAB>speaker<TAB>form<TAB>limit<TAB>Japanese`. ` / ` = line break and ` // ` = page break (the player presses a
button) in the Japanese box. Lines are in story order: use neighbours for context; a unit is often one speech that
runs over several pages - translate it as one utterance. Speaker comes from the portrait (story) or the block
(boss / rescued demon / tutorial = Rand / system / menu).

## Output: `work/tl/<batch>.out.tsv`, written with your file-write tool (never a shell heredoc or echo)
`id<TAB>English`, every input id exactly once, same order. Plain ASCII: straight quotes, `...`, `--`; ♥ only where
the Japanese has ♥. No tabs inside the English, no Japanese, no `\n`, no `\uXXXX`, no backslashes.
- **Text boxes** (limit `2x224px/page`): write the English as plain sentences. Put ` // ` where a new page should
  start. Do NOT break lines yourself: the tool wraps each page into its 2 lines (about 40-45 characters per line).
  A page that needs 3 lines fails the check: add a ` // ` at a sentence or clause end, or tighten the wording. You
  may use more or fewer pages than the Japanese; keep a page break wherever the Japanese has a dramatic pause.
- Copy every `{col:XX}` (colour; e.g. `{col:03}stage{col:00}` highlights a word) and `{name}` (the game inserts a
  demon name there) exactly, around the matching English words. Units shown as "(hint, coloured)" are tinted by the
  tool: write them without codes.
- **Menus / names / link lines** (limit `NNpx` or `NNch`): one short line within the limit. `ch` limits count every
  character including spaces. Link screens (`system (link ...)`) can only show letters, digits, space and
  `: ; ? ! - ( ) / & + = * ~ _` - no `.` `,` `'` `"`.

## Validate
`python -X utf8 tools/batches.py check <batch>` from the repo root; fix every reported id and re-run until it prints
`<batch>: OK`. To see how one text wraps: `python -X utf8 tools/batches.py fit story "Your text // page two"`
(block = story, boss, rescue, system or tutorial).

## Style
- Faithful: keep the information and order of ideas; adapt idiom, not meaning. Don't add details the Japanese doesn't
  state; don't summarise or skip. Adapt wordplay so the joke still lands (no translator notes).
- Keep the speaker audible. JP register markers carry voice and must turn into English devices, not vanish:
  old men's じゃ/のう/わし ("eh?", "my boy"), rough ぜ/ねぇ/っス/ヤロウ ("ain't", "ya", clipped grammar), feminine
  かしら/わよ/のね ("I wonder...", "you know", "dear"), whines and drawls (〜ぅ/なぁ: stretched words), オレさま
  ("the great me", "yours truly"). Katakana-only speech is broken, halting speech. Frost demons keep "-ho" /
  "Hee-ho!". A line any speaker could have said is a mistake.
- **会 is 言** in this game's font: なに会ってんだよ = "What are you talking about?"; 会っていた = "was saying".
  Read 会う as "meet" only when meeting makes sense.
- Use names and terms exactly as in the glossary (DemiKids official names: Rand, Gale, Imperium, Demiloc, Demonary,
  Laksmi, Mini Icy...). Never abbreviate to fit; if a line can't fit without losing meaning, keep the meaning, add a
  page, and only if that's impossible report `LONG: id`.
- Honorifics kept, hyphenated: ミズチちゃん -> Tsunami-chan, オーディンさま -> Odin-sama. But カミさま = God,
  オレさま = "the great me", ごくろうさま = "good work / thanks for your trouble".
- Punctuation: 「」 -> "...", ・・・ -> `...`, a line of only dots -> `......`, ！？ -> `!?`.
- No suffix glued to a placeholder (`{name}th`), no a/an right before `{name}`. `{name}` can be any demon name.
- Reading notes: `樹海（ジュカイ）`, `泉（いずみ）` = the word plus its reading: translate once ("Sea of Trees",
  "spring"). テイコク = Imperium (adj. Imperial), テイコクグン = Imperial Army, かんぶ = Imperial officers.

## Consistency
Never edit `glossary.md`. For a recurring name or term not in it, pick a form, use it consistently, and report it.

## Report (reply with only this)
Files written and entry count per batch; then any lines: `NEW TERM: jp -> en`, `UNSURE: id - note`, `LONG: id - note`.
