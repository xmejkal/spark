# P826: the wiring steps and the "Before you power it" lines as data: rows

Card: [P826 #1184](https://github.com/xmejkal/spark/issues/1184), PR [#1222](https://github.com/xmejkal/spark/pull/1222).
Plan `~/.claude/plans/p826-steps-and-checks-as-data.md` (round 1: lens Sonnet and refuter Opus; round 2: refuter Opus).
The PR review: one lens (Sonnet, L1 to L10) and the refuter (Opus, R1 to R9). Both `breadboard.expected.md` files are
byte-equal before and after. This file holds the acted, raised and rejected findings only (rules.md). 2026-11-16.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | L5 (round 1): the data must hold facts, not sentences: the supply line and the closing line print `parts.py --show`, which no page may show | plan, lens | acted | the sentences and their spans stay in `BeforePowerList`; a check's own words are a fact, in `said` |
| 2 | L1, L2 (round 1): `PowerCheck` reads as a check class, and `SUPPLY` is already a step act | plan, lens | acted | `BeforePowerItem`, and the kind `OFF_BOARD_SUPPLY` |
| 3 | L3, L4, R6 (round 1): no reader needs a step's `act` yet | plan, lens and refuter | acted | `NumberedStep` holds number, words and edge only |
| 4 | R2 (round 1): only the two renderers call `walk()`; drawing.py and bench_changes.py number `anchored()` themselves | plan, refuter | acted | `numbered()` replaces `walk()`; the other two stay as they are |
| 5 | R3, R4 (round 1): `pull_conflicts` holds only text, and a supply needs its users | plan, refuter | acted | a CONFLICT's pin comes from `part_rules.conflicts_of`; a supply carries its users, sorted |
| 6 | L8, R1, R8, R9, L9 (round 1): the sheet must print from the same data the test pins; the five old mutation rows; `records` sorted once; map.md; every motor item's fields pinned | plan, lens and refuter | acted | `sheet()` renders `wiring_data(...).before_power`; the five rows moved to `before_power.py`; `of()` sorts; `tools/map.py --write`; `TheMotorDataTest` |
| 7 | R2-1, R2-3, R2-4, R2-5, R2-6 (round 2): an unused pin with no note says "", the docstrings and mvp-plan.md name `numbered()`, the moved supply row anchors without its indent, no row for a host requirement said twice | plan, refuter | acted | as listed; the p191 row "a record's warnings repeat" covers the requirement said once |
| 8 | L6 (round 1): `subject` has two meanings | plan, lens | rejected | one meaning, the name the line opens with; `record` links each part line to its record |
| 9 | L11 (round 1): rename `numbered()`, which a test module's helper also names | plan, lens | rejected | a method and a test module's helper do not clash |
| 10 | L3, R1: no test pins `said == ""` for an unused pin with no note; `pin.get("note")` escaped 45 tests | PR review, lens and refuter | acted | `AnUnusedPinWithNoNoteTest` on a made-up part, with literal expectations, and a row in `tests/mutations/p826-steps-and-checks-as-data.json`; planted by hand in a scratch copy, the test fails |
| 11 | L5: `BeforePower`'s docstring says the records are sorted, but only `of()` sorts them | PR review, lens | acted | the docstring says "`of` sorts them" |
| 12 | R2: wiring_steps.py's docstring calls `numbered()` the one source of the step numbers, but the drawing and the bench changes number `anchored()` themselves | PR review, refuter | acted | it numbers the step list and the diagram and gives the data a page reads; the two others are named |
| 13 | R3: test_architecture's MODULES follows the area page, whose components table has no row for `before_power` | PR review, refuter | acted | a row in `docs/discovery/2026-10-19-p323-target-architecture/architecture/areas/breadboard.md` |
| 14 | L9: `wiring_data` reads the supplies a second time, after `sheet()` already did | PR review, lens | rejected | the plan accepted it (R2-8): the pass is cheap and keeps the signature small |
| 15 | the plan did not name test_architecture's MODULES list, or test_self_confirmation's rule against a test that reads the module's own constants | build | acted | `before_power` added to MODULES; the new test writes the kinds and the code as literals |
