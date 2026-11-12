# P400 walk 2 council: findings rows

Findings of the P400 council on walk 2's cards (2026-10-23, Prague). Six agents on Sonnet 5.5: technology, product, architecture, AI, UX and the predictions scorer. The refuter and the synthesis on Opus 5.5. The plan is `docs/observations/2026-10-23-p400-walk2-council/plan.md`.

The council's new cards: N1 is P401 (#518), N2 is P402 (#519) and N3 is P403 (#520), filed on 2026-10-23 by the session spark-51. A lens's own number, such as "architecture N1", names a proposal in that lens's report.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | G1: `check_all.py` labels the 4 skipped checks "not asked for", though nothing is built yet | diary G1, product 13, UX 12 | closed | `scripts/check_spine.py:547` gives another reason for the same word. Rides in P118 (#52)'s PR — P776: tracked by #52 (open), P118 #52 (open) |
| 2 | G2: outside a git repository, init writes no git exclude and does not say so | diary G2, product 12 | closed | P137 (#71), "init says only what it did" — P776: tracked by #71 (open), P137 #71 (open) |
| 3 | G3: the init page does not say what an empty `prefer` or `sellers` does | diary G3, product 14 | closed | P309 (#375), refuter P4 — P776: tracked by #375 (open), P309 #375 (open) |
| 4 | G4: no command writes the brief | diary G4, product 10 | closed | beside N2 — P776: card #1075 (init and brief gaps) |
| 5 | G5: a second init run lists no open fields | diary G5, product 10 | closed | beside N2, with G21 — P776: card #1075 (init and brief gaps) |
| 6 | G6: no script reads the brief's goal, and the idea page does not name the brief (stall S1) | diary G6, product 1 and 10, AI 14 | acted | new card N2 |
| 7 | G7: `--match` offers neither the board's LED nor its BOOT button | diary G7, technology 7, product 9 | verified | refuter T1. P389 (#504), whose test gains the BOOT button (product 9). See row 78 |
| 8 | G8: `--match` lists another project's `xiao-esp32-c6-fresh` with no word on why | diary G8, product 14 | closed | P314 (#388) and P390 (#505), refuter P4 — P776: tracked by #388 (open), #505 (open), P314 #388 (open), P390 #505 (open) |
| 9 | G9: `--offer` prints the function twice and cuts the XIAO's power line in its JSON | diary G9, product 11 | closed | code not checked. If the cut is not a designed limit, it is a bug for N3's PR — P776: card #1080 (offer output duplicates) |
| 10 | G10: `--match` shows "free 0" and names no holder | diary G10, product 11, UX 9 | acted | new card N3 |
| 11 | G11: the `--pick` dry run does not say that one refusal stops every pick | diary G11, product 11 | acted | new card N3 |
| 12 | G12: `--drawer` shows no `used_in` | diary G12, product 11 | closed | rides in N3 only if it is one line — P776: fixed since: --drawer prints `held by` per entry (list_drawer.py) and --offer KEY shows one entry (P211) |
| 13 | G13: no way to show one drawer entry | diary G13, product 11 | closed | row only — P776: fixed since: --drawer prints `held by` per entry (list_drawer.py) and --offer KEY shows one entry (P211) |
| 14 | G14: the idea page names a part "1b" that it does not have | diary G14, product 14 | closed | P389 (#504) edits `commands/idea.md` — P776: done by #504 (closed), P389 #504 (closed) |
| 15 | G15: the idea page does not say to change a need's mark after a pick | diary G15, product 14 | closed | P389 (#504) — P776: done by #504 (closed), P389 #504 (closed) |
| 16 | G16: setup's firmware-image row names the S3 image for a C6 board | diary G16, product 14 | closed | P349 (#445), refuter P4 — P776: tracked by #445 (open), P349 #445 (open) |
| 17 | G17: init's `package.json` stays unused | diary G17, product 15 | closed | the prune list of P385 (#494) — P776: done by #494 (closed), P385 #494 (closed) |
| 18 | G18: the build warned that no serial monitor is wired, and the run heard "ready" all the same | diary G18, AI 7, architecture N2, UX 11 | closed | refuter A5: the log shows wokwi-cli v0.27.1, the tools list installs 0.28.0, and the definition says `USB_SERIAL_JTAG`. The cause stays open. One run on 0.28.0, with the PO's yes, decides it — P776: tracked by card  (?): P468 (#636) serial-monitor warning reads serialInterface, closed. |
| 19 | G19: moving a hold tells the other project nothing, and no build, check, run or deploy reads holds | diary G19, product 16, UX 9 | closed | refuter U3: no deploy script reads `used_in`. The hold stays out of N1 — P776: stale note: dropped by P776: a design remark with no action |
| 20 | G20: after a board-only build, init's advice to build and run it again loops | diary G20, product 12 | closed | a real bug inside the open bug card P137 (#71) — P776: tracked by #71 (open), P137 #71 (open) |
| 21 | G21: init `--force` lists only the 2 I²C fields | diary G21, product 10 | closed | the same cause as G5, beside N2 — P776: card #1075 (init and brief gaps) |
| 22 | G22: after the build, `check_all.py` still says "not asked for" | diary G22, product 13, UX 12 | closed | with G1 in P118 (#52) — P776: tracked by #52 (open), P118 #52 (open) |
| 23 | G23: no scenario can press the BOOT button, no page says so, and the verdict still says passed | diary G23, every lens | acted | refuter K1 to K3, A1, A2. P396 (the build), P345 PR 1 (the verdict), P397 (the pick). The press test is row 74 |
| 24 | G24: the journey page's example has no lines that read the console without waiting | diary G24, product 15 | closed | P77 (#13), or the next PR on `docs/guide/journey.md`. "no board ran them yet" is stale: "ready seen" at 06:55 — P776: tracked by #13 (open), P77 #13 (open) |
| 25 | G25: the run log's date carries no zone | diary G25, product 14 | acted | P345 PR 1, see row 47. 14 of 17 stored deploy times have no zone (refuter U4), so N1 prints them as stored |
| 26 | G26: `run_scenario.py` has no dry run | diary G26 | acted | refuter K18. P399 PR 2, which writes nothing (row 55) |
| 27 | G27: the deploy page keeps `--port` for two boards, and the look names it for one | diary G27, UX 10 | acted | refuter U6: `commands/deploy.md:22,40`. UX's two sentences ride in N1's PR |
| 28 | G28: deploy.py calls esptool's deprecated `erase_flash` and `write_flash` | diary G28, product 15 | closed | the next PR that edits the flasher — P776: tracked by card  (?): P471 (#642) esptool underscore commands; flasher.py:44 now uses erase-flash and write-flash, closed. |
| 29 | G29: before the erase, nothing says what the board runs now | diary G29, AI 1, UX 8 | acted | refuter A3, U4, U5. New card N1 |
| 30 | P397: "The person learned it only after the paid Wokwi run" | card #513 | rejected | refuter K9: Claude wrote "a simulation cannot press the button" at 01:14:20, and the run started at 01:15:58. plan.md replaces the sentence |
| 31 | P398's "Done when": the build lists `tactilebutton` with `pressed` for `button-light` | card #514 | rejected | refuter K15: the fixture has no `sim/`, no test reaches the full simulation stage, and `pressed` is prose only. P398 merges into P399 |
| 32 | AI N3: a spark command checks the LED after press and release | ai.md | rejected | refuter D1: `scrum/VISION.md:70`, spark writes no behaviour (P56). A version with steps that Claude writes fits `scrum/VISION.md:31`: row 74 |
| 33 | P396: "So no scenario can press the button" | card #512 | acted | refuter K4: it rests on the JSON alone. P396's line says "spark knows no way for a scenario to press it" |
| 34 | P396: a test reads the definition that the store keeps | card #512 | acted | refuter K6: tests set a scratch store (`scripts/store.py:40-42`). The test keeps a hand-made fixture there |
| 35 | P396 to P399: the PO's words at "06:44 CEST" | cards #512 to #515 | acted | refuter K7: verbatim, typed at 06:41:52. P396, P397, P399 and the walk 2 diary now say 06:41. P398 is closed and keeps its text |
| 36 | P397: `--match` says it | card #513 | acted | refuter K11: `--match` does not offer the XIAO for press before P389. P397 waits on P389 |
| 37 | P397: a tactile button on a header pad is the other choice | card #513 | acted | refuter K12: the PO's XIAO has no soldered pins (#506). The bench comes first |
| 38 | P398: a scenario's names exist "but no file lists them" | card #514 | acted | refuter K14: `sim/diagram.json` lists ids and wired pins, and only controls are missing. P398 merges into P399 |
| 39 | I5: "The look then said simulation: passed" | #440 comment | acted | refuter K20: only `--json` says it. The new comment says so, and P345 PR 1 adds the text line |
| 40 | I5: P345 "covers it" | #440 comment, diary 07:44 | acted | refuter K22: the title does, and the body does not. The new comment says so |
| 41 | a grep of `boards/*.json` finds one `wokwi-board` | technology 2 | acted | refuter T6: two files, and the FireBeetle hit is prose. P396 prints "not checked" for a board with no kept definition |
| 42 | Claude said "replaces reaction-game's firmware" twice | AI 1 | acted | refuter A4: three times, the first at 21:33 on 2026-10-22. N1 says three |
| 43 | G18's cause is the CLI version | AI 7 | closed | refuter A5: `commands/build.md:276` dates the change to CLI 0.28.0, and the log shows API `1.0.0-20261022`. Row 18 — P776: stale note: A cause note about the CLI version |
| 44 | the cards extend `SimulationEngine`, `SimulationStage`, `NeedsService` and `FakeSimulationEngine` | architecture 1 to 4 | acted | refuter R3: none exists. plan.md names today's module and the later class for each card |
| 45 | P391 puts P389 in stage 4 | architecture 3 | acted | refuter R5: stage 4 waits for P389 (`docs/discovery/2026-10-22-p391-boards-as-modules/design.md:243`). P389 is in Ready |
| 46 | "usable" at `assign_pins.py:57` | architecture, names | acted | refuter R8: the word is "unusable". plan.md uses neither |
| 47 | G25 rides on P345 | product 14 | acted | refuter P5: #440 said nothing on zones. P345 PR 1 names it now |
| 48 | the PO's pin words, "comment on #6, 2026-10-22 16:17" | product 5 | closed | refuter P7: 16:17:07Z is 18:17 CEST. A cited time carries its zone — P776: stale note: A cited time zone correction in a council note |
| 49 | P137 is parked | product 12 | closed | refuter P10: `scrum/STORY_MAP.md:38` names P137, and "parked" is not checked — P776: tracked by P137 #71 (open) |
| 50 | UX N3, a bench result, is a new card | UX | acted | refuter U7: P374 (#479) in Ready is related. Row 75 |
| 51 | `SparkBenchEngine` gives its own table | architecture | acted | refuter D3: no card needs a second engine now (`scrum/VISION.md:75`). plan.md adds no port method |
| 52 | P399: "a wrong name costs a paid run" | card #515 | closed | refuter K17: not checked when wokwi-cli refuses a part id. P399's new title drops the claim — P776: done by P399 #515 (closed) |
| 53 | 216 calls returned 207 KB | AI 12 | closed | refuter A10: not checked, the transcript now holds the council's calls too — P776: stale note: A call count |
| 54 | Wokwi's free minutes and the 30 s stop | product 7 | closed | refuter P9: not checked, a search summary only. No card rests on it — P776: stale note: Unchecked search summary; no card rests on it |
| 55 | a `--dry-run` through `problem()` writes `sim/wokwi.toml` | refuter, blind spot 1 | acted | `scripts/run_scenario.py:90-91`. P399's dry run writes nothing |
| 56 | setup said `[ok]` with wokwi-cli v0.27.1, and the tools list installs 0.28.0 | refuter, blind spot 2 | closed | diary O11, `data/tools.json:51`. With row 18 — P776: stale note: dropped by P776: wokwi-cli pin, one line; redo if seen again |
| 57 | the kept definition is a copy from 2026-10-13 at `4294fca6`, and no card says when "cannot press" goes stale | refuter, blind spot 3 | closed | `boards/xiao-esp32-c6.json:370-373`. P396's sha256 check catches a changed file, not a changed Wokwi — P776: done by P396 #512 (closed) |
| 58 | walk 2 ran on a used store, so S2 and G9 to G13 come from that state | refuter, blind spot 4 | closed | diary O2, O3, `scrum/VISION.md:38`. The next walk's map says which stalls a new store meets — P776: stale note: A note about walk state |
| 59 | P398: split, merge, row or rewrite | refuter, contradiction 1 | acted | merge into P399 (plan.md, decision 1) |
| 60 | order: P345 first or P396 first | refuter, contradiction 2 | acted | P396 first (decision 2) |
| 61 | a must line that no scenario names: `unchecked` or a note | refuter, contradiction 3 | acted | a note (decision 3), because of `scripts/outcomes.py:46` |
| 62 | P397's other choice: a pad button, the bench or a drawer button | refuter, contradiction 4 | acted | the bench first (decision 4) |
| 63 | the LED: defined through `$gpio15`, not tried, or not known | refuter, contradiction 5 | acted | no line, and the read stays row 67 (decision 5) |
| 64 | P399's home: `FakeSimulationEngine` or `problem()` | refuter, contradiction 6 | acted | `problem()` and `tests/fake_wokwi_cli.py` (decision 6) |
| 65 | G18: the CLI version or `serialInterface` | refuter, contradiction 7 | acted | no card until a run shows the cause (decision 7) |
| 66 | only the XIAO has a kept Wokwi definition, and no command keeps one | technology 2 and its new card 1 | closed | refuter T5: `scripts/parts.py:930` keeps PDFs and images only. Goes to P391's stage 4 (plan.md) — P776: done by P391 #506 (closed) |
| 67 | nobody tried whether a scenario reads the LED on `$gpio15` | technology 6 and its new card 2, UX N2 | closed | refuter K5. The next walk's paid run adds one `expect-pin` step on it, with the PO's yes — P776: stale note: Next walk adds an expect-pin step |
| 68 | the build can read `serialInterface` from the definition and drop the serial warning | architecture N2, UX 11 | closed | refuter A5: the cause is open. Waits on row 18 — P776: tracked by card  (?): P468 (#636) reads serialInterface from the definition, closed. |
| 69 | no "never assume" item says what a `passed` run covers | AI 4 and N4 | acted | refuter A7: 7 items at `docs/guide/agents.md:572-730`. Item 8 rides in P345 PR 1 |
| 70 | no part record lists the controls of its Wokwi part, so no list of controls and pins per type exists | architecture N1, technology 9, P398 | closed | `scripts/parts.py:606-618` reads the controls of chips only. Reopen when a run fails on a control or a pin name — P776: stale note: dropped by P776: no card needs it |
| 71 | no script reads the brief's `must` | AI 6 | acted | refuter A8. A `Brief` Value in P345 PR 2 |
| 72 | the AI spent a paid start-only run and named no `--no-simulation` route | AI 8 | closed | refuter A11: `commands/deploy.md:67-73`. No card — P776: stale note: Refuter says no card |
| 73 | the cards save few tokens: the part is 1,506 bytes and the diagram 219 | AI 12 | verified | refuter A6. The cards rest on turns and errors |
| 74 | the press test before the bench was a scratch script, and no spark command runs it | AI N3 and 9, product 3 | closed | G23, and R10.1 counts steps outside spark. With steps that Claude writes, refine it after P345 (product) — P776: done by P345 #440 (closed) |
| 75 | a bench result is nowhere in spark | UX N3 | closed | refuter U7. A comment on P374 (#479) — P776: done by #479 (closed), P374 #479 (closed) |
| 76 | P345 and P308 (#374) both change what the gate says | product 2 | closed | plan P345 PR 1 with P308 in view — P776: tracked by #374 (open), P308 #374 (open), P345 #440 (closed) |
| 77 | 45 cards opened and 16 closed since 2026-10-20 | product 8 | verified | refuter P3. This plan opens 3 and merges 1. R10.2's check at R11 |
| 78 | P355 (#453) sits inside P389 (#504) | product 8 and 9 | closed | the PO decides whether to close it into P389 — P776: done by #453 (closed), #504 (closed), P355 #453 (closed), P389 #504 (closed) |
| 79 | one word, "button", covers the real board and the Wokwi model | UX 1 | acted | P396's line names the Wokwi definition and the GPIO |
| 80 | the text look prints no simulation line | UX 4 | acted | refuter K20. P345 PR 1 |
| 81 | the plans model how to run a simulator, not what it models of a board | architecture 1 | acted | refuter R1. plan.md, the refactor plans |
| 82 | round 3 names `board_alone` with no fix, and `check_spine.run` is 192 lines | architecture 4 | acted | refuter R2, R9. plan.md, the refactor plans |
| 83 | P396's line reaches no later reader | technology 16 | acted | P345 PR 1 copies `sim/WHAT-THIS-CANNOT-SHOW.md` into the run log |
| 84 | every run test writes `diagram.json` as `{}` | technology 13 | acted | refuter T7. P399's "Done when" changes `ProjectCase.setUp` |
| 85 | only the two onboard constants are in doubt, because wired pins sit on header pads | technology 5 | acted | `scripts/assign_pins.py:147,423` (technology). P396 checks `pin_roles` only |
| 86 | a pin check against wired pins refuses a valid read | technology 12 | acted | `scripts/check_spine.py:555-556`. P399 checks ids only |
| 87 | a step reader that guesses passes a wrong scenario | architecture 7 | acted | `ScenarioSteps` answers `not checked` for a shape that it cannot read |
| 88 | `check_spine.py --json` gets a top-level `limits` list | AI, field C | closed | P396 prints the text and the file. The JSON key waits for an agent that needs it — P776: done by P396 #512 (closed) |
| 89 | the next walk needs P345 first, and a radio walk needs P347 (#442) and P348 (#443) | product 18 | closed | the PO picks the walk — P776: tracked by #442 (open), #443 (open), P345 #440 (closed), P347 #442 (open), P348 #443 (open) |
| 90 | walk 2's predictions: 9 hit, 3 miss, 4 partly, 5 not tested | predictions | verified | refuter S4 |
| 91 | three (M) facts went stale between the map and the walk, and the map named 1 of 4 stalls | predictions | closed | refuter S1, S3. The next map writes the commit beside each (M), runs its looks again, and looks at holds and the kept definition — P776: stale note: Walk-map procedure note |
| 92 | P323's invariant 1 names `tests/golden.py`, and the repo has `tests/golden_bench.py` | synthesis | closed | my `ls` of `tests/`. plan.md, the refactor plans — P776: done by P323 #413 (closed) |
| 93 | no refactor plan names a `FakeSimulationEngine` | synthesis | verified | my grep of `docs/discovery`, `scripts` and `tests`: 0 hits |
| 94 | the push hook printed "009f0db as committed" while it pushed 3580c4e, because commits landed during the push | process, P400 | closed | the push hook's own output — P776: tracked by card #889 (open): P661 open: the push hook output names failing tests; its commit hash mismatch is the same hook output family |
| 95 | The docs review (Sonnet 5.5): plan.md lagged the live cards, a wrong line for `ProjectCase.setUp`, three lens numbers, `limits_for`, the P323 glossary's "tested", and P398's close comment | review | acted | each fixed on 2026-10-23. `ProjectCase.setUp` is at `tests/test_run_scenario.py:100-104`. The review sent the diagram's text to mermaid.ink to parse it. Its doubt on row 94 is rejected: the hook printed 009f0db while it pushed 3580c4e |
