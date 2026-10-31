# Glossary - Shin Megami Tensei: Devil Children - Puzzle de Call!

Binding for every translator and reviewer. Agents propose additions in reports; only the controller edits this file.
`tools/batches.py check` enforces the tables: when a row's JP appears in a line, one of its EN forms (`;`-separated,
case-insensitive) must appear in the English, and nothing from Avoid may.

## Rulings (asked of the user once; options and reasons in docs/decisions.md)
- Honorifics: kept, hyphenated (Tsunami-chan, Odin-sama). Name order: Western (given name first).
- Romanisation source: official English names from DemiKids Light/Dark Version (Atlus USA 2003; source:
  megatenwiki "Translations in Devil Children Light Book and Dark Book"), else Hepburn without macrons (D2, D8).
- Credits: English.
- Register / flavour: light, kid-friendly adventure; keep JP flavour (honorifics, demon speech quirks).
  Sound effects / cries: *Grr...*, written as plain words ("Gugu..." -> "Ngh...").
- Abbreviations: full names and terms everywhere; the official DemiKids demon names are names, not abbreviations
  (Seryu, Krak, Astar are what the official release calls them). Exception: J. Frost is written Jack Frost (D8).

## Style rules
- Punctuation map: 「」 -> "...", 『』 -> '...', ・・・ / ・・・・・・ -> ... (one ellipsis, or "... ..." for a long
  silence line), ！？ -> !?, ！！ -> !!, ～ -> ~ (only in cries), ♥ stays ♥ (the font has it). Plain ASCII otherwise.
- The game's limited kanji set writes 言 as 会: なに会ってんだよ = なに言ってんだよ ("What are you saying?"),
  会っていた = 言っていた. Read 会う as 言う whenever "meet" makes no sense.
- Katakana-only demon speech (オレ、タスカッタ) = broken, halting speech: short words, no contractions, choppy
  ("Me... saved. You... save me."). Keep it simple, not a caricature.
- Frost demons end lines with ホー / ヒーホー: keep the tic as "-ho" / "Hee-ho!" ("Thanks-ho!", "Hee-ho!").
- Voices: docs/style-reference.md.

## Characters
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| ジン | Jin | | Light Version hero, partner Rand. オレ, brash, じゃん/ぜ: casual, cocky, "c'mon", "seriously?" | |
| アキラ | Akira | | Dark Version hero, partner Gale. オレ, calm, level-headed, dry humour | |
| ランド | Rand | | Jin's partner demon (a Sol Cat), furry. ボク, earnest, cautious, a bit of a show-off at the end | Rando |
| ゲイル | Gale | | Akira's partner demon (a Rox). ボク/オレ, gruff, proud, tsundere: チッ! = "Tch!", ガキ/コドモ = "kids" | Geil |
| アズラエル | Azrael | | Imperium leader of the miniature world, the Emperor's younger brother (not in DemiKids: Hepburn) | Azrail |
| テイコクコウテイ | Emperor of the Imperium; Emperor | | | |
| コウテイ | Emperor | | | |
| クロセル | Crosel | | Imperium boss | |
| オセ | Ozemos | | Imperium boss | |
| グレモリィ | Grimlee | | Imperium boss (female) | |
| ビフロンス | Bifronz | | Imperium boss | |
| カイム | Kyme | | Imperium boss | |

## Places
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| ヴァルハラ | Valhalla | | the heroes' (demon) world | |
| クァドリガ | Quadriga | | Azrael's castle, the Imperium's base | |
| フィーヨルグ | Fjorgyn | | フィーヨルグ雪原 = Fjorgyn Snowfield | |
| 雪原 | Snowfield; snowfield | | | |
| 樹海 | Sea of Trees | | 樹海（ジュカイ） is the word with its reading: translate once, drop the reading | |
| 地下牢 | dungeon | | | |
| 火山 | volcano | | | |
| 草原 | grassland; meadow; plain | | | |
| 泉 | spring | | 泉（いずみ） = spring (the reading in brackets is dropped) | |

## Items / skills / terms
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| テイコク | Imperium; Imperial | | 帝国 (official DemiKids) | Empire |
| テイコクグン | Imperial Army; Imperial soldier; Imperial troops | | | |
| かんぶ | | | テイコクのかんぶ = Imperial officers / commanders | |
| 魔力 | magic | | "magic power" or "magic"; マリョク in katakana speech too | mana |
| マリョク | magic | | | |
| デビル | demon | | | devil |
| デビルチルドレン | DemiKid | | official | Devil Children |
| デビライザー | Demiloc | | official (the device that summons demons) | Devilizer |
| デビダス | Demonary | | official (the demon list / save record) | Devidas |
| ミニチュア | miniature | | the model of Valhalla that sucks the heroes in | |
| アストラルボディ | astral body | | | |
| コントロール | control | | | |
| ステージ | stage | | | |
| ボスステージ | boss stage | | | |
| マルチプレイステージ | multiplayer stage | | | |
| マホウジン | magic circle | | the stage exits | |
| タマゴ | egg | | demons are trapped in eggs on the stages | |
| ショウガイブツ | obstacle | | | |
| ドア | door | | rotating doors | |
| ナカマ | | | ally / party: "joined your party", "ally" | |
| ケイヤク | contract | | a demon offers a contract | |
| ヒーホー | Hee-ho | | | |

## Demon names (names.NNN; official DemiKids names, D2)
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| ソルレオン | Sol Cat | | Rand's species | |
| ヘイロン | Rox | | Gale's species | |
| カーリー | Kali | | | |
| アバドン | Abaddon | | | |
| メッチー | Mecci | | | |
| アガシオン | Agathion | | | |
| フェアリー | Fairy | | | |
| ナハトコボルト | Kobold | | | |
| ガネーシャ | Nesha | | | |
| オーディン | Odin | | | |
| ネコマタ | Two-Tail | | | |
| アンズー | War Lion | | | |
| とけいウサギ | Tik Tok | | | |
| ストラス | Talon | | | |
| ヌエ | Nue | | | |
| スサノオ | Boltar | | | |
| スカアハ | Scatha | | | |
| クラーケン | Krak | | | |
| ピクシー | Pixy | | | Pixie |
| イエティ | Yeti | | | |
| タロス | Talos | | | |
| ゴーレム | Golem | | | |
| スケルトン | Skeltos | | | |
| ソンゴクウ | Goku | | | |
| ロボット | Groid | | | |
| ドワーフ | Dwarf | | | |
| オニ | Ogre | | | |
| ギリメカラ | Mekra | | | |
| カミナリさま | Thundar | | | |
| タタリモッケ | Hooty | | | |
| ペガサス | Pegasus | | | |
| シーサー | Leogard | | | |
| スザク | Suzak | | | |
| ケツアルカトル | Quetza | | | |
| バロン | Barone | | | |
| ガルーダ | Garuda | | | |
| ゲンブ | Gembu | | | |
| ハデス | Hades | | | |
| ニスロク | Chefros | | | |
| キューピッド | Cupid | | | |
| ニケー | Nikare | | | |
| エンゼル | Angel | | | |
| コアクマ | Temptina | | | |
| デュナミス | Shadomas | | | |
| オファニム | Ironhoof | | | |
| ケルビム | Cherubim | | | |
| プチフロスト | Mini Icy | | Frost: -ho tic | |
| ユキンコ | Ice Baby | | | |
| ジャックフロスト | Jack Frost | | official J. Frost, written out (D8) | J. Frost |
| イチゴフロスト | Icyberry | | | |
| ジャックランタン | Punkin | | | |
| カマイタチ | Razor | | | |
| レモンフロスト | Icylemon | | | |
| オルトロス | Orthros | | | |
| テング | Goblin | | | |
| ミズチ | Tsunami | | ミズチちゃん = Tsunami-chan | |
| サラマンダー | Sizzard | | | |
| バジリスク | Basilisk | | | |
| オロチ | Orochi | | | |
| セイリュウ | Seryu | | | |
| ウロボロス | Urboros | | | |
| ケットシー | Caitsith | | | |
| ザントマン | Slumber | | | |
| まくらがえし | Pilox | | | |
| オニビ | Demipyre | | | |
| ファントム | Phantom | | | |
| バンパイア | Vampire | | | |
| バク | Baku | | | |
| モコイ | Mokoy | | | |
| ナイトメア | Nitemare | | | |
| キュウキ | Kyuki | | | |
| アンクー | Ankuu | | | |
| オシリス | Osiris | | | |
| ミノタウロス | Minotaur | | | |
| アメノウズメ | Aminoz | | | |
| ジコクテン | Lord Ton | | | |
| ゾウチョウテン | Lord Nan | | | |
| コウモクテン | Lord Sha | | | |
| タモンテン | Lord Pey | | | |
| サンダーバード | Boltbird | | | |
| トウテツ | Shoklam | | | |
| サカタノキントキ | Bushido | | | |
| ドヴェルガー | Dwelgar | | | |
| テスカポリトカ | Teskarot | | | |
| サイクロプス | Cyclops | | | |
| ポセイドン | Poseidon | | | |
| アスモデル | Asmodel | | | |
| アドナキエル | Irontaur | | | |
| ラクシュミ | Laksmi | | | Lakshmi |
| アモン | Amon | | | |
| クルースニク | Kresnik | | | |
| クドラク | Bloodbat | | | |
| アプサラス | Apsaras | | | |
| ラミア | Lamia | | | |
| スルト | Surt | | | |
| スレイプニル | Slepnir | | | |
| ケルベロス | Nex | | | |
| グリフォン | Gef | | | |
| ビビサナ | Bibisana | | | |
| ヴリトラ | Vrtra | | | |
| インドラ | Indra | | | |
| フェンリル | Fenrir | | | |
| パイモン | Paimon | | | |
| ラファエル | Raphael | | | |
| アイラーヴァタ | Airavata | | | |
| ヘルハウンド | Helldog | | | |
| アスタロト | Astar | | | |
| シルフ | Sylph | | | |
| ヒッポウ | Krane | | | |
| ユニコーン | Unicorn | | | |
| ホウオウ | Redwing | | | |
| コマイヌ | Dredogs | | | |
| ネコショウグン | Shogun | | | |
| ラー | Ra | | | |
| ビャッコ | Byako | | | |
| イツァムナー | Solarius | | | |
| ヴァーチャー | Virtue | | | |
| ドミニオン | Dominion | | | |
| アークエンゼル | Guardian | | | |
| フロストエース | Icy Ace | | | |
| キングフロスト | King Icy | | | |
| コントン | Konton | | | |
| トウコツ | Tork | | | |
| ダハーカ | Trinos | | | |
| ヤマタノオロチ | Octorex | | | |
| リンドブルム | Lindwurm | | | |
| かぞえヒツジ | Shepp | | | |
| ウミボウズ | Seaboz | | | |
| ヤタガラス | War Crow | | | |
| リッチ | Lich | | | |
| ガーゴイル | Gargoyle | | | |
| ダイダラボッチ | Dydra | | | |
| シュクユウ | Pyrosia | | | |
| キンタロウ | Bearlord | | | |
| タケミカヅチ | Warbolt | | | |
| タム・リン | Tamlin | | | |
| ジークフリート | Zypher | | | |
| ルーグ | Roog | | | |
| ペロボーグ | Whiskers | | | |
| ネメシス | Nemesis | | | |
| マルキダエル | Aries | | | |
| アムブリエル | Gemini | | | |
| アクアエレメント | Aqualok | | | |
| フレアエレメント | Flarlok | | | |
| ネメア | Nemea | | | |
| ウォフマナフ | Vomana | | | |
| アールマティ | Pathlite | | | |
| ギュウマオウ | Bulmax | | | |
| パズズ | Pazu | | | |
| アゼル | Azel | | | |
| ベヒモス | Brute | | | |
| スキンファクシ | Firemare | | | |
| フリンファクシ | Windmare | | | |
| ケサランパサラン | Kesra | | | |
| ルシファフロスト | Lucifroze | | | |
| いっすんぼうし | Thumurai | | | |

## Decisions from earlier batches
- b006 あのおかた -> "my lord" (the bosses' unnamed master; never named, keep gender-neutral where possible)
- b005 ちょぞうこ -> "reservoir" (magic reservoir)
- b008/b009 石 -> stone, 穴 -> hole, 出っぱり -> the door's arms; ゲームのあそびかた その1 -> How to Play: Part 1;
  （ボタンを押せばちゅうし） -> (Press a button to skip)
- b008 ケツアルコアトル (variant spelling in rescue.066) -> Quetza, same demon as ケツアルカトル
- b008 コンゴトモヨロシク -> "I look forward to our time together..."
- b010 pause menu: Cancel, Undo, Map, Demiloc, Retry, Restart, Quit, Save; title: Start, Load, Quit
- b011 ending: おわり -> The End (centred by hand, raw `=` units)
