# Polish pass (completed findings and runtime checks)

One line per finding; the polish pass ticks each `[x]`, fixed or `waived: reason`. Release refuses while any is open.
Sources: reviewer reports per batch (`work/tl/reviews.md`).

## b002 (prologue, pilot)
- [x] story.000.00 - "a powerful magic" -> "powerful magic" — fixed in the phase 9 line-by-line polish pass; actual en lint passes.
- [x] story.000.12 - Gale, きっと dropped -> "There's gotta be something close by..." — fixed in the phase 9 line-by-line polish pass; actual en lint passes.
- [x] story.000.15 - "What is it? Well..." -> "What... Well..." (keeps the hesitation) — fixed in the phase 9 line-by-line polish pass; actual en lint passes.

## b003 (Rand's route 1-10)
- [x] story.001.08 - Baku "all robbed" lacks object -> "Other demons... too... all... had magic taken." — fixed in the phase 9 line-by-line polish pass; actual en lint passes.
- [x] story.001.09 - Rand そんな -> "That's terrible..." — fixed in the phase 9 line-by-line polish pass; actual en lint passes.
- [x] story.001.11 - "He's right, though." adds a speaker -> "Still, if this keeps up, we're in danger too." — fixed in the phase 9 line-by-line polish pass; actual en lint passes.
- [x] story.003.01 - Laksmi ", you know" stagey -> "Though I doubt that was enough to finish him." — fixed in the phase 9 line-by-line polish pass; actual en lint passes.
- [x] story.005.03 - Jin ランドか！！ -> "Rand! Rand, it's you!!" — fixed in the phase 9 line-by-line polish pass; actual en lint passes.
- [x] story.005.10 - "He's the one" -> "That's the one controlling this world, after all." — fixed in the phase 9 line-by-line polish pass; actual en lint passes.
- [x] story.007.09 - まるで dropped -> "it's practically a Sea of Trees." — fixed in the phase 9 line-by-line polish pass; actual en lint passes.
- [x] story.008.02 - word order -> "Yeah. Especially from deep inside, // I can feel a really suspicious presence." — fixed in the phase 9 line-by-line polish pass; actual en lint passes.
- [x] story.009.01 - Osiris うう -> "Uhh......" (separate from Baku's "Ngh") — fixed in the phase 9 line-by-line polish pass; actual en lint passes.
- [x] story.009.03 - "either" -> "I am afraid I do not know that myself." — fixed in the phase 9 line-by-line polish pass; actual en lint passes.
- [x] story.009.05 - Rand "They were kinda pushy" -> "Though the way they went about it was a little rough." — fixed in the phase 9 line-by-line polish pass; actual en lint passes.
- [x] story.009.12 - Osiris fragment -> "That demon was most likely taken to the Fjorgyn Snowfield." — fixed in the phase 9 line-by-line polish pass; actual en lint passes.
- [x] story.009.14 - も dropped -> "...go back to Valhalla too." — fixed in the phase 9 line-by-line polish pass; actual en lint passes.

## b004 (Rand's route 11-14)
- [x] story.014.06 - Akira ひどい目 -> "So we both had it rough." — fixed in the phase 9 line-by-line polish pass; actual en lint passes.
- [x] story.014.09 - Gale "ya" -> "Talking whatever nonsense you like, just 'cause you think we weren't watching." — fixed in the phase 9 line-by-line polish pass; actual en lint passes.
- [x] story.014.11 - Gale "ya" -> "Yeah, yeah. Then why don't you show me this power of yours, huh?" — fixed in the phase 9 line-by-line polish pass; actual en lint passes.
- [x] story.014.17 - Jin -> "I'm definitely getting payback for what happened in that world!" — fixed in the phase 9 line-by-line polish pass; actual en lint passes.
- [x] story.014.25 - Jin "Oh, brother." -> "Man, those two." — fixed in the phase 9 line-by-line polish pass; actual en lint passes.
- [x] story.014.28 - Jin "Shall we" -> "Let's just head out ahead, Akira." — fixed in the phase 9 line-by-line polish pass; actual en lint passes.

## b005 (Gale's route 15-25)
- [x] story.017.10 - "Count on it." is an addition (optional) — waived: Count on it conveys the assurance in きっと and Gale's confidence (fresh story review).
- [x] story.021.02 - "snooping around" -> "poking around" — fixed in the phase 9 line-by-line polish pass; actual en lint passes.
- [x] story.023.03 - Baku ソウカ -> "I see!... Now... friends... saved." — fixed in the phase 9 line-by-line polish pass; actual en lint passes.
- [x] story.023.07 - "He needs treatment" -> "He needs tending to" (optional) — waived: treatment naturally conveys 手あて; tending to is a stylistic alternative.
- [x] story.023.08 - Laksmi -> "I'll take care of him. You two hurry on ahead." — fixed in the phase 9 line-by-line polish pass; actual en lint passes.
- [x] story.025.10 / 025.14 - "take the control" -> "seize control"; "as long as he holds control" — fixed in the phase 9 line-by-line polish pass; actual en lint passes.

## b006 (Gale's route 25-28, bosses)
- [x] boss.002.00 - merge "Oho." page with the spring clause; "How sloppy of Crosel, losing to a child." — fixed in the phase 9 line-by-line polish pass; actual en lint passes.
- [x] boss.005.00 - "Quite the exploits you've had." — fixed in the phase 9 line-by-line polish pass; actual en lint passes.
- [x] boss.006.00 - "our ideals" -> "our thinking" — fixed in the phase 9 line-by-line polish pass; actual en lint passes.
- [x] boss.008.00 - "You, wretch, are a being that disrupts the order of this world." — fixed in the phase 9 line-by-line polish pass; actual en lint passes.
- [x] boss.010.00 - "I will follow my lord to the very end!!" — fixed in the phase 9 line-by-line polish pass; actual en lint passes.
- [x] boss.011.00 - feminine menace (optional) "I'll make it nice and easy for you, right here." — waived: put you out of your misery already carries the threatening kindness.
- [x] story.028.03 - Gale -> "Tch, Rand could've just stayed behind." — fixed in the phase 9 line-by-line polish pass; actual en lint passes.
- [x] story.028.08 - Gale -> "Thank me for my hard work too, you know." (optional) — waived: the demanding wording preserves Gale's pride.
- [x] boss.000.00 — resolved: `{name}` reads the current demon field at RAM base + 0x158D. The normal boss selector starts at entry 1; a host-only pointer probe selected entry 0 and rendered "Sol Cat, let's go!!" correctly (`work/qa/runtime/boss_zero_dense/f001014.png`).

## b007 (rescue 000-065)
- [x] rescue.001 - ナッテヤロウ condescension -> "Me join you. You lucky." — fixed in the phase 9 line-by-line polish pass; actual en lint passes.
- [x] rescue.002 - コンゴトモヨロシク -> "...I see. I thank you. From now on... please... treat me well..." — fixed in the phase 9 line-by-line polish pass; actual en lint passes.
- [x] rescue.003/017/039/052 - オレさま: one form, "the great me" (017 also "yours truly") — waived: great me / yours truly retain self-importance; uniform wording would flatten distinct voices. See fresh story review.
- [x] rescue.006 - gruff 助けてやってくれ -> "Save the other demons too, would you?" — fixed in the phase 9 line-by-line polish pass; actual en lint passes.
- [x] rescue.010 - "......Glad to be with you." — fixed in the phase 9 line-by-line polish pass; actual en lint passes.
- [x] rescue.012 / 058 - comma splices — fixed in the phase 9 line-by-line polish pass; actual en lint passes.
- [x] rescue.014 - "...so I'll trust you♥" — fixed in the phase 9 line-by-line polish pass; actual en lint passes.
- [x] rescue.020 - "I refuse to accept that someone like me would suffer such a fate!" — fixed in the phase 9 line-by-line polish pass; actual en lint passes.
- [x] rescue.025 — resolved: Mecci (demon 4) selects this line, confirmed by runtime pointer logging. All symbols, including the heart, fit on one complete line (`work/qa/polish/_sheets/rescue_text_025.png`); waived the original two-line layout because the symbols have no word/phrase boundary to preserve.
- [x] rescue.029 - "Thanks. You've made me feel way better." — fixed in the phase 9 line-by-line polish pass; actual en lint passes.
- [x] rescue.031 - "It was you... who freed me...?" — fixed in the phase 9 line-by-line polish pass; actual en lint passes.
- [x] rescue.034 - キーッ -> "Eeek!" / "Argh!" — fixed in the phase 9 line-by-line polish pass; actual en lint passes.
- [x] rescue.039 - "My famous flame, the pride of the great me, nearly went out, man!" — waived: the boast and casual man remain clear; the literal possessive is eccentric but comprehensible. Fresh review rated this Minor.
- [x] rescue.042 - "Kee, kee! Thank you... very much. Still... this place... little hot." — fixed in the phase 9 line-by-line polish pass; actual en lint passes.
- [x] rescue.045 - "Me waited... for this moment. Me fight with you too." — fixed in the phase 9 line-by-line polish pass; actual en lint passes.
- [x] rescue.057 - "worried if" -> "worried whether" — fixed in the phase 9 line-by-line polish pass; actual en lint passes.

## b008 (rescue 066-100, tutorial 0)
- [x] rescue.066 - よろしくたのむ -> "I'd be grateful if you'd look after him."; confirm 066/067 speakers (Quetza / Teskarot) — resolved: ROM 0x1626A5 + 2*id selects rescue.066 for Quetza (id 33), .067 for Teskarot (83); help him out preserves the request. Runtime shots in polish rescue_text_066/067.
- [x] rescue.072 - "Uoooooooh!" romanised -> "Rooaaar!" — fixed in the phase 9 line-by-line polish pass; actual en lint passes.
- [x] rescue.075 - "My," -> "Hmm, this place gives me the creeps." — waived: My / Come now conveys the mannered voice more clearly than Hmm.
- [x] rescue.076-080 - よろしく renderings vary (optional unify) — waived: varying greetings preserve distinct われ / わたし / ぼく registers.
- [x] rescue.085 - "I will permit you to form a contract with me." — fixed in the phase 9 line-by-line polish pass; actual en lint passes.
- [x] rescue.093 - "But really... an amazing guy." — waived: amazing one keeps the halting insult-to-compliment turn.
- [x] rescue.094 - "gufufufu" -> "Heh heh heh..." — fixed in the phase 9 line-by-line polish pass; actual en lint passes.
- [x] rescue.095 - katakana voice lost (Important, phase 6 review): now "You... clear this place... Impressive. //
  Your power... I recognize it."
- [x] tutorial.000.02 - Rand "gonna" -> "I'll teach you" — fixed in the phase 9 line-by-line polish pass; actual en lint passes.
- [x] tutorial.000.34 - クセモノ -> "a bit of a tricky customer" (optional) — waived: a little tricky conveys クセモノ naturally.
- [x] tutorial.000.35/36/064 - ジク "axis" -> "pivot" — 35/36 fixed in the phase 9 line-by-line polish pass; 64 already describes the arms without "axis". Actual en lint passes.

## b009 (tutorial 1-2)
- [x] tutorial.001.07 - "Simple:" addition (harmless) — waived: Simple is harmless instructional connective wording.
- [x] tutorial.001.08 - "Let me give it a quick try!" — fixed in the phase 9 line-by-line polish pass; actual en lint passes.
- [x] tutorial.001.44 - "Let me show you my attack!!" (optional) — waived: Behold my attack is Crosel's pompous boast, not Rand's line.
- [x] tutorial.002.02 - "Almost done, so remember it well!" — fixed in the phase 9 line-by-line polish pass; actual en lint passes.
- [x] tutorial.002.11-13 - "That's because" if it fits — waived: Why? followed by the explanation reads naturally across entries.
- [x] tutorial.002.22 - "they vanish" (matches .19) — fixed in the phase 9 line-by-line polish pass; actual en lint passes.

## b010 (menus / link)
- [x] pause.005 / client_pause.003 はじめから: both "Stage 1" (system.011 confirms it returns to the first stage); キャンセル "Back" in all three menus (client block is 24 bytes)
- [x] titlemenu.000 - "New Game" doesn't fit 40 px; "Start" kept unless the menu can widen — waived: Start clearly identifies the action, is unabridged English and fits the measured 40 px slot.
- [x] race_menu.000.0 - "Single-Pak VS" (13) doesn't fit 12 cells; "1-Pak VS" kept — waived: flagged 1-Pak VS fits 12 cells and clearly contrasts Multi-Pak VS; link-only engineering is not certified.
- [x] trade.005-007 - "!" consistency ("Demon received!" is 15 > 14) — waived: all three results are clear; punctuation need not be identical in 14-byte fields.
- [x] trade.008 / 010.1 / 012 - clunky link lines (14-char cap): "Records hold / 99 per demon" — waived: current two-line messages communicate mode check, destination and per-demon limit within 14-byte fields.
- [x] system.003/007/010 - "Press any button." (optional) — waived: Please press any button is natural and consistent.

## b011 (ending, link)
- [x] story.028.34 - "it's our turn now"; "you did well too" (optional) — waived: did good suits Gale's colloquial voice; next it's our turn preserves the transition.
- [x] client_link.005 - "...to go to the title" if it fits — waived: button for the title communicates the action within the fixed client image slot.


## Fresh whole-chapter review (2026-11-01)
No Critical/Important findings in any chapter; full report: `docs/story-review.md`.
- [x] story.001.11 — waived: the loss of magic and inability to help are explicit across adjacent sentences; awkward `undo his stolen magic` is a Minor wording preference, not a missing plot beat.
- [x] story.025.14 — waived: `this world's control` reflects the literal mechanism; the following sentence explicitly explains winning control by defeating Azrael.
- [x] boss.005.00 — waived: the formal exploits / trouble my lord phrasing is understandable and retains the pompous threat; reviewer marked optional.
- [x] Phase 7 review Minor #2 — fixed: raw and forced multiline paragraphs reject final lines under six visible characters; blank-positioned ending utterances remain valid.
- [x] Phase 7 review Minor #3 — fixed: meaningful outer spacing is checked around formatting codes and placeholders; reviewed per-ID layout exceptions are in `script/layout_exceptions.json`.
- [x] Final visual review, story.009.03 — waived as a pacing Minor: the English uses three deliberate beats for
  "some of them were saying" / "call to Valhalla for help" / "until their magic ran out completely", versus two
  in Japanese. Each clause is intact and readable, with no orphan word, omitted meaning or clipping; the pauses
  stage the rescue-call revelation in the same way as this speaker's surrounding multi-page explanation.
  The whole-chapter reviewer accepted the exchange. This is an editorial layout disposition, not a rendering fix.
