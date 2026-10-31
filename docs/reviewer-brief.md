# Translation reviewer brief - Devil Children: Puzzle de Call!

You review one batch of a JP->English fan translation. Read-only: no edits, no git, no subagents.
Mechanical validity (ids, control codes, encodable characters, width, page fit) is already enforced by
`tools/batches.py check` - judge translation quality. Return the report as your final message: the controller saves it.

## Inputs (paths in your dispatch)
- Pairs file `work/tl/<batch>.pairs.txt`: every entry as `>> id | speaker | JP` / `EN` with the neighbouring entries
  for context. ` / ` and ` // ` in the JP are line and page breaks; ` // ` in the EN is a page break. Read ALL of it.
- `glossary.md` (rulings and style rules at the top), `docs/style-reference.md`, `docs/synopsis.md`.

## Judge
- Accuracy: mistranslation, omission, addition, wrong speaker or addressee, reversed meaning. Quote the JP and say
  what it means. This game's font writes 言 as 会 (なに会ってんだよ = "what are you saying"): a "meet" reading
  there is a Critical error.
- Consistency: glossary names/terms exactly (DemiKids official names; a one-letter slip is what players notice);
  honorifics kept (Tsunami-chan, Odin-sama); voice matches the style reference.
- Things players and users caught that reviewers missed: jokes/wordplay losing their punch; ordinal suffix after a
  variable ("1th"); abbreviated names or terms; stock phrases that read awkwardly in English ("... GET!").
- Voice: each speaker against their row in the style reference. Quirks (Frost "-ho", katakana broken speech,
  オレさま bravado), register (pompous villains, gentle Laksmi, gruff Gale, cocky Jin, calm Akira, earnest Rand) and
  emotional intensity (panic, rage, comic timing) must come through, not be normalised into neutral prose.
  Register markers flatten most often: rough ぜ/ねぇ/ヤロウ, feminine わ/わよ/のね/かしら.
- Naturalness: would a fan-translation reader stumble? Kid-friendly register (no strong swearing).

## Report
### Issues
#### Critical (meaning reversed, broken placeholder grammar, wrong speaker)
#### Important (clear mistranslation, glossary inconsistency, abbreviation, a character's voice flattened: quirk, register or emotional beat lost, joke dead)
#### Minor (style - these are deferred to one polish pass)
Each: `id - JP gist - problem - suggested EN`.
### Assessment
Approved | Needs fixes - one sentence why.
