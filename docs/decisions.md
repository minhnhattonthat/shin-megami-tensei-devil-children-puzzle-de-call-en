# Decisions

The user's rulings on scope, style and trade-offs, newest last. Read before asking the user anything; if a later
decision replaces one, mark the old one "replaced by D<n>" instead of deleting it. Binding term spellings live in
`glossary.md`; this file holds the why.

| # | Date | Question | Options offered | Decision and reason |
|---|---|---|---|---|
| D1 | 2026-11-01 | Honorifics and name order | keep (-san), drop; JP or Western order | Keep honorifics; Western order (given name first). Owner's standing answer for one-shot runs. |
| D2 | 2026-11-01 | Romanization source for names | official art, earlier patch, Hepburn | Official English names where they exist (Devil Children / DemiKids localisation), else an earlier fan patch, else Hepburn without macrons. |
| D3 | 2026-11-01 | Credits | stay Japanese, translate | English. |
| D4 | 2026-11-01 | Abbreviations | engine work first (default), abbreviate | Default: full names and terms, engine work first; abbreviate only as a flagged last resort. |
| D5 | 2026-11-01 | Graphics text left in Japanese | none (default), list | Translate all of it (titles, menus, banners, cards); keep the Japanese logo only if it has no official English version. |
| D6 | 2026-11-01 | Specs and plans | need approval, pre-approved | Pre-approved: keep going through checkpoints, report at the end. |
| D7 | 2026-11-01 | Existing saves / states | user supplies, none | None provided; build the debug tool as usual. |
| D8 | 2026-11-01 | Demon / term names (controller default under D2, pre-approved run) | DemiKids official, SMT-standard, Hepburn | DemiKids Light/Dark official names (Sol Cat, Rox, Laksmi, Mini Icy, Imperium, Demiloc, Demonary...) because this game shares their cast; Azrael and places absent from DemiKids in standard English (Azrael, Quadriga, Fjorgyn). Only J. Frost is written Jack Frost (D4: no abbreviations; same character). Source table: megatenwiki "Translations in Devil Children Light Book and Dark Book". |
| D9 | 2026-11-01 | Phase 9 completion and publication | Local verified archive; publish a release | User explicitly authorized completing the current phase, committing and pushing main, and explicitly prohibited release publication and visibility changes. Stop at a built and verified local ZIP. Independent review may use a fresh read-only pass or codex exec because nested Orca workers are unavailable. |
| D10 | 2026-11-01 | Publication (supersedes D9's hold) | keep private, publish | User: "prepare release and publish". Repo made public, description set to the real title, GitHub release v1.0 with the verified local ZIP (unchanged, SHA-1 d7ec8a2b...). |
