# P400 refuter: which claims hold in the code

> Most claims hold in the code, the store and the transcript. Three fail: P397's "learned it only after the paid run", P398's done-when, and AI N3 against the vision.
> Nineteen hold only in part. The biggest: Claude made the O14 claim three times, G18's cause stays open, and the lenses use plan classes that do not exist.
> Verdicts: 51 HOLDS, 19 PARTLY, 3 REJECTED, 3 NOT CHECKED. Opus 5.5 read each line itself, with no Wokwi run and no web lookup. Times are CEST.

## The cards and the I5 comment
| # | claim | verdict | evidence |
|---|---|---|---|
| K1 | P396: the project picked the board's BOOT button, and `pins.py` names it `ONBOARD_BUTTON = 9` | HOLDS | `walk2/firmware/pins.py:6`, diary row 21:13 |
| K2 | P396: the simulation stage passed with the board alone | HOLDS | `check_spine.py:558` returns `OK`, diary row 21:28 |
| K3 | P396, P398: Wokwi's XIAO part has no button and no pin on GPIO9, and spark keeps it | HOLDS | store file, 1506 bytes, sha256 `e5200e01…` as in `boards/xiao-esp32-c6.json:369-376`. 14 pins, D9 is GPIO20 (`:26`), LED on `$gpio15` (`:33,45`) |
| K4 | P396: "So no scenario can press the button" | PARTLY | It rests on the JSON alone. No run tried, and I read no Wokwi page on hidden controls. |
| K5 | P396: nobody tried `$gpio15` | HOLDS | walk 2's scenario has one step, `wait-serial` (`the-firmware-starts.scenario.yaml:10`). I ran no repo-wide grep. |
| K6 | P396 done-when: "A test reads the part definition that spark keeps in its store" | PARTLY | Under unittest, `store.py:40-42` sets a scratch `SPARK_HOME`. It holds only with a fixture kept in that scratch store. |
| K7 | P396 to P399: the PO's words at "06:44 CEST" | PARTLY | The words are verbatim, but he typed them at 06:41:52 (transcript `04:41:52Z`). "yes please, go on, …" at 06:51:46 holds. |
| K8 | P397: at step C the person picked the board's button, as the idea page says | HOLDS | `commands/idea.md:93-97`, diary row 21:13 on 2026-10-22 |
| K9 | P397: "The person learned it only after the paid Wokwi run" | REJECTED | At 01:14:20 Claude wrote "a simulation cannot press the button" (transcript `2026-10-22T23:14:20Z`). The run started at 01:15:58 (diary row 01:15). ai.md says the same. |
| K10 | P397: it builds on P389 (#504) | HOLDS | #504 is OPEN and in Ready (`gh project item-list 2`) |
| K11 | P397 done-when: `--match` says it | PARTLY | `--match` does not offer the XIAO for press today (diary G7, record `functions: null`). The line has no place before P389. |
| K12 | P397 done-when: a tactile button on a header pad is the other choice | PARTLY | The PO on this XIAO: "I actually haven't soldered any legs to it" (#506 body, #6 comment `2026-10-22T16:17:07Z`). |
| K13 | P398: the person asked whether spark used a wrong name | HOLDS | transcript `04:41:52Z`, diary row 06:44 |
| K14 | P398: a scenario's names exist "but no file lists them" | PARTLY | `sim/diagram.json` lists ids and wired pins (`check_spine.py:554-556`, `commands/build.md:255-256`). No file lists built-in controls (K15). |
| K15 | P398 done-when: the build lists `tactilebutton` with `pressed` for `button-light` | REJECTED | The fixture has no `sim/`. No test reaches the full simulation stage (`check_spine.py:565-566`). `pressed` is only prose (`parts/tactile-button.json:20,49`), and the converter has 0 hits. |
| K16 | P399: the free checks run first, with no name check | HOLDS | `run_scenario.py:140` checks that two files exist, `:246-257` |
| K17 | P399: "a wrong name costs a paid run" | NOT CHECKED | Walk 2 had no wrong name. I did not check when wokwi-cli refuses a part id. |
| K18 | P399: no dry run, but `--pick`, `--drawer-set` and deploy have one | HOLDS | `parts.py:1668`, `deploy.py:163`, 0 hits of "dry" in `run_scenario.py` |
| K19 | I5: the scenario only waited for "ready", and the run passed | HOLDS | scenario `:10`, run log `:2` `verdict: passed` |
| K20 | I5: "The look then said simulation: passed" | PARTLY | Only `--json` says it (`board_envelope.py:76`). The text look prints `report_lines` (`look.py:71`), with 0 hits of "simulation" in `board_look.py`. |
| K21 | I5: deploy.py flashed the image as a tested one | HOLDS | board log `2026-10-23T06-55-29.log:3` `simulation: passed`, and the store's walk2 entry |
| K22 | I5 and diary row 07:44: P345 "covers it" | PARTLY | The title does. The body (552 characters) quotes the PO on new boards and names `run_scenario.py:212`, now a docstring of `run_record`. |

## technology.md
| # | claim | verdict | evidence |
|---|---|---|---|
| T1 | `--match` never offers the XIAO for press or light | HOLDS | diary G7, `functions: null` in the record, P355 (#453) and P389 (#504) open. I did not run `--match` again. |
| T2 | the pick note fits at `needs.py:339-342` | HOLDS | the F12 footprint note, inside `plan_pick` (`needs.py:282`) |
| T3 | tests force a scratch `SPARK_HOME` | HOLDS | `store.py:40-42`, `tests/test_needs.py:47` |
| T4 | the kept file is not strict JSON | HOLDS | my `json.load`: "line 32 column 5 (char 1241)", the `/* Virtual pins */` line |
| T5 | no command keeps the file | HOLDS | `parts.py:930` keeps PDFs and images only, `p229-xiao-board.md:42,213`, one `.json` under `sources/` |
| T6 | a grep of `boards/*.json` finds one `wokwi-board` | PARTLY | It finds two files. The FireBeetle hit is prose (`firebeetle2-esp32s3.json:106`), and its part is a stand-in (`:107`). |
| T7 | run tests write `{}` and name `tactilebutton` | HOLDS | `tests/test_run_scenario.py:29-34,104,193` |
| T8 | the converter registry lists `$gpio15` | HOLDS | `converter.mjs:2807,3949` |
| T9 | "reach" means a board on USB | HOLDS | `reach.py:2`, `board_reach.py:2` |

## ai.md
| # | claim | verdict | evidence |
|---|---|---|---|
| A1 | `passed` is the value for any wokwi-cli exit 0 | HOLDS | `run_scenario.py:103-104` |
| A2 | it reaches `data.simulation`, the board log, `spark.json` and the store | HOLDS | through a second constant, `image_evidence.py:18`: `board_envelope.py:76`, `deploy_service.py:43`, `board_facts.py:23-28`, the store's walk2 entry |
| A3 | 17 deploys: 12 blink-c6, 4 button-light, 1 walk2 | HOLDS | my count of `boards/8c-bf-ea-cc-97-70.json` |
| A4 | Claude said "replaces reaction-game's firmware" twice, at 06:45 and 06:53 | PARTLY | Three times. The first is at 21:33 on 10-22 (`19:33:26Z`), "overwrite whatever reaction-game put on the board", in the question that asked the PO to go on. |
| A5 | G18: CLI v0.27.1 against 0.28.0, and a board-only build skips the converter | PARTLY | Log `:21`, `data/tools.json:51` and `check_spine.py:554-558` hold. But `build.md:276` dates the change "CLI 0.28.0, API 2026-10-09", and log `:22` shows API `1.0.0-20261022`. The cause stays open. |
| A6 | the part is 1,506 bytes, the diagram 219 bytes | HOLDS | `wc -c`, `ls -la walk2/sim` |
| A7 | no "never assume" item covers `passed` | HOLDS | 7 items in `agents.md:572-730`, item 1 at `:574` |
| A8 | no script reads `must` | HOLDS | only `init_project.py:218` writes it. No `["must"]` or `get("must")` in `scripts/`. |
| A9 | lines 1 to 63 of `run_scenario.py` are 3.4 KB | HOLDS | 3442 bytes |
| A10 | 216 calls returned 207 KB | NOT CHECKED | the transcript now also holds the council's calls |
| A11 | the `--no-simulation` route exists for such firmware | HOLDS | `commands/deploy.md:67-73` (P337) |

## architecture.md
| # | claim | verdict | evidence |
|---|---|---|---|
| R1 | no plan models what a simulator offers | HOLDS | `areas/firmware.md:39`: the port has `prepare` and `run` only |
| R2 | round 3 G6 names `board_alone` and gives it no fix | HOLDS | `council/round3-extensions.md:18`, "not as written (G6)" |
| R3 | the cards extend `SimulationEngine`, `SimulationStage`, `NeedsService`, `FakeSimulationEngine` | PARTLY | None of them exists in `scripts/` or `tests/`. Only `ScenarioRun` exists. They come in stage 5, three PRs per area (`refactor-plan.md:360-371`). |
| R4 | chips list their controls (`parts.py:606-618`) | HOLDS | `control_problems` reads `controls` from a chip definition |
| R5 | P397 waits on P389, which P391 puts in stage 4, later | PARTLY | P389 holds. But P391 says "Stage 4 waits for P389" (`design.md:243`), the reverse. P389 is in Ready. |
| R6 | rule U1: the design area cannot import the engine | HOLDS | `architecture/README.md:64-65`, the pick is in design (`areas/design.md:18`) |
| R7 | `reach.py` is a bench tool | HOLDS | `reach.py:2`: "the PO's bench tool (P251)" |
| R8 | "usable" at `assign_pins.py:57` | PARTLY | the word there is "unusable" |
| R9 | `check_spine.run` is 192 lines | HOLDS | `def run` at `:348`, its last line at `:539` |
| R10 | the `button-light` fixture has no `sim/` | HOLDS | `ls tests/data/breadboard/button-light` |

## product.md
| # | claim | verdict | evidence |
|---|---|---|---|
| P1 | P100: "each stall is filed as a card" | HOLDS | #6 body |
| P2 | the text of R10.2, and "yes, plus bugs" | HOLDS | `scrum/RETROSPECTIVES.md:266` |
| P3 | 45 cards opened and 16 closed since 10-20 | HOLDS | my count of 338 issues, the same from 00:00 UTC and from 00:00 CEST |
| P4 | each gap G1 to G29 has a row | HOLDS | each appears in rows 2 to 16. Titles of #375, #388, #445 match G3, G8, G16. |
| P5 | G25 rides on P345 | PARTLY | #440 names `run_scenario.py:212` and says nothing on zones |
| P6 | Ready holds #479, #493, #504, #505 | HOLDS | `gh project item-list 2` |
| P7 | the PO's pin words, "comment on #6, 2026-10-22 16:17" | PARTLY | The words hold. 16:17:07Z is 18:17 CEST, and the time names no zone. |
| P8 | walk 1 did not run its scenario | HOLDS | `docs/observations/2026-10-19-p326-walk1.md:57` |
| P9 | Wokwi's free minutes and the 30 s stop | NOT CHECKED | the lens names a search summary only |
| P10 | P137 is parked (`STORY_MAP.md:38`) | PARTLY | line 38 names P137. I did not check "parked". |

## ux.md
| # | claim | verdict | evidence |
|---|---|---|---|
| U1 | `check_spine.py:558` leaves the slot empty for a board-only build | HOLDS | `()` as limits. The slot is at `:576-579`, shown at `journey.md:363-366`. |
| U2 | the PO said that no pins are soldered | HOLDS | #506 body and the #6 comment: "I actually haven't soldered any legs to it" |
| U3 | no deploy script reads `used_in` | HOLDS | 0 hits in 7 files. Only `breadboard.py`, `drawer.py`, `needs.py`, `parts.py` read it. |
| U4 | the last deploy before walk 2 is blink-c6, `2026-10-19T09:24:50+02:00` | HOLDS | latest non-walk2 entry by time. 14 of the 17 stored times have no zone, so "zone not stored" has cases. |
| U5 | the question names only what it writes | HOLDS | `deploy_gate.py:100` |
| U6 | the deploy page tells Claude to omit `--port` with one board | HOLDS | `commands/deploy.md:22,40` |
| U7 | N3, a bench result, is a new card | PARTLY | P374 (#479) in Ready, "a bench result cannot be written back", is related. The lens does not name it. |

## predictions-score.md
| # | claim | verdict | evidence |
|---|---|---|---|
| S1 | #496 merged at 13:37, #500 at 14:14, #503 at 16:08 | HOLDS | `mergedAt` 11:37:54Z, 12:14:05Z, 14:08:44Z |
| S2 | walk 1 showed a hold on the XIAO | HOLDS | `walk1.md:34`: "the drawer held the one XIAO for plant-alarm" |
| S3 | at `0ffbcbf`: 0 `board_only` and 1 `active_level`, now 3 and 2 | HOLDS | `git show` and `grep -c` |
| S4 | 9 hit, 3 miss, 4 partly, 5 not tested. M: 3 of 7 hit, E: 6 of 14. | HOLDS | my count of its table |

## Proposals against the direction (no other proposal goes against `VISION.md`, `refactor-plan.md:39-50` or P391 `design.md:216-243`)
| # | proposal | verdict | evidence |
|---|---|---|---|
| D1 | AI N3: a spark command checks the LED after press and release | REJECTED | `scrum/VISION.md:70`: "anything that writes behaviour" is not a goal (P56). `build.md:252-253`: spark ships no scenario. With steps that Claude writes, it fits `VISION.md:31`. |
| D2 | architecture: P397 reads `simulation.wokwi.skip` on the board's onboard entry | HOLDS | P391 `design.md:219`: onboard parts enter "as facts with sources" |
| D3 | architecture: `SparkBenchEngine` gives its own table | PARTLY | No card needs a second engine now. `VISION.md:75`: nothing designed on paper before a design needs it. |

## Contradictions
1. P398: technology splits it, AI and UX merge it into P399, product drops it to a row, and architecture rewrites it after a controls card.
2. Order: product puts P345 first (finding 17). Architecture and technology put P396 first.
3. A must line that no scenario names: AI field B puts it in `unchecked`, and UX finding 5 puts it in `notes`. Facts: `outcomes.py:46` turns any `unchecked` into `could-not-run`. `agents.md:475` keeps the deploy step whatever the status. `agents.md:715-716` keeps a grant from answering a look with a warning or an unknown field.
4. P397's other choice: the card, technology and architecture name `tactile-button` on a pad. UX names the bench test first. Product names a drawer button, or none.
5. The LED: architecture calls `ONBOARD_LED` defined through `$gpio15`. Technology prints "not tried", product "not known", and technology and UX ask for a spike.
6. P399's home: architecture tests it with `FakeSimulationEngine`, but its finding 4 says the cards do not pull the firmware move. Technology uses `problem()` and `tests/fake_wokwi_cli.py`, which exist.
7. G18: AI blames the CLI version. Architecture, UX and product blame `serialInterface: USB_SERIAL_JTAG` and drop the warning for that part.

## Blind spots
1. Each lens adds `run_scenario.py --dry-run` that "runs every free check". But `problem()` calls `image_in` (`run_scenario.py:147`), which writes the image name into `sim/wokwi.toml` when the build named none (`:90-91`). The diary saw that write (O11). In spark, `--dry-run` means "say what it would do, and do nothing" (`parts.py:1668`).
2. Setup said `[ok]` on 12 rows (diary row 21:19), and the run then used wokwi-cli v0.27.1 (O11). `data/tools.json:51` installs 0.28.0. No lens asks setup to show the version gap.
3. The kept part is a copy from 2026-10-13 at commit `4294fca6` (`boards/xiao-esp32-c6.json:370-373`). The run used Wokwi's live API (log `:22`), and the walk needed GitHub to trust the copy (the button question, answer 4). No card says when "cannot press" goes stale.
4. Walk 2 ran on a used store: 112 drawer entries and holds by two projects (O2, O3). S2 and G9 to G13 come from that state. No lens asks which stalls a hobbyist with a new store meets (`VISION.md:38`).
