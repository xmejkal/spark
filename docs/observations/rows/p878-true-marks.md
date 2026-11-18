# P878: `flow.py show` ticks only a judged pass: rows

Card: [P878 #1246](https://github.com/xmejkal/spark/issues/1246), a bug of size S. Two plan rounds (one lens and the
refuter, then the refuter again) and a build to the plan. This file holds the acted and raised findings only
(rules.md). 2026-11-18.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | a board-only build has four skipped stages for good, so `partial` leaves the project at the build and the offer `build` changes nothing | plan lens and refuter, round 1 | acted | the PO, 2026-11-18: "Dot, and move on". The build and the breadboard have no status and say "board only: nothing to wire"; `test_a_board_only_build_gets_no_tick_and_the_project_stands_at_the_firmware` |
| 2 | a full build whose simulation stage alone is skipped (`build_service.py`, P778) is stuck the same way | plan refuter, round 1 | acted | the PO, 2026-11-18: "Dot, and move on". No status, and the words say why; `partial` stays for any other skipped stage, which no build writes today |
| 3 | "nobody judged it" is a third wording beside "not checked by spark" and "spark does not judge the phase" | plan lens | acted | the messages say "spark does not judge the wiring" and "spark did not judge it" |
| 4 | "no other test changes" was false: `BUILT_TABLE`, `tests/test_flow.py` (`"requirements": "ok"`), the no-log end in `tests/test_project_image.py` and `tests/golden-design/flow-ok-page.txt` pin the old behavior | plan refuter, rounds 1 and 2 | acted | the four pins changed on the PO's word and are named in the plan and the PR; the full run showed no other failure |
| 5 | reading the build record before the test for the sheet makes a broken record turn the breadboard `could-not-run` with no sheet | plan refuter, round 2 | acted | `BreadboardReader` keeps `not-started` there; `test_a_missing_sheet_beside_a_build_record_that_cannot_be_read_is_not_started` |
| 6 | a board-only build whose requirements gained parts still said "nothing to wire" | plan refuter, round 2 | acted | the board-only test comes after the stale test in both readers; `test_a_board_only_build_whose_requirements_changed_is_stale_and_its_sheet_not_started` |
| 7 | with no log, "run its scenario again" is untrue | plan lens and refuter | acted | `why_untested` says "run a scenario" with no log, and blames an older spark only for a log that names no image; three tests in `tests/test_project_image.py` |
| 8 | the flow would hold a fourth literal copy of the stage names | plan refuter, round 2 | acted | `BUILD_STAGE` and `SIMULATION_STAGE` in `build/stages.py`, read by `skipped_the_build`, the two write sites of the skipped stages and the flow. The other literals in the build area stay |
| 9 | four mutation rows lost their anchor through this change | plan lens and refuter; `mutate.py --anchors` | acted | three rows of `p825-flow-reader.json` and one of `p463-printed-lines.json` retargeted; the row of the hand-written requirements file turned with the rule and has a new name. `--anchors` over the three tables: 44 rows, each present once |
| 10 | after a `dist/` copy that fails midway the record says ok and the build gets the tick (row 7 of `p891-dist-failure.md`) | PR refuter of P891, the card's comment | raised | P899 #1277: it needs a new fact in the build record, after P898 #1276 |
| 11 | `SIMULATION_SKIPPED_MESSAGE` names the one cause of a skipped simulation from the stage's status alone | plan refuter, round 2 | raised | dropped because the record keeps no stage detail and the build has one cause today; the PR and the constant's comment say it |
| 12 | fifteen rows of other tables are refused by `--anchors` on main too | `mutate.py --anchors` on a copy of main | raised | P897 #1273 owns them; this change adds none |
| 13 | the docstring of `build/stages.py` said every importer imports "the two names" | PR refuter | acted | it names the stage names too |
| 14 | the breadboard's board-only reading does not look at the record's status, and no test pinned it | PR refuter | acted | kept: nothing is there to wire, however the simulation ended. The could-not-run test pins the breadboard's words, and the docstring says it |
| 15 | row 1 of `p878-true-marks.json` was named "gets the tick again", but the mutant reads partly done | PR refuter | acted | the row has a true name |
| 16 | a board-only build offered `build`, which changes nothing | PR refuter (optional), row 1 | acted | no offer on that reading; a build that could not run keeps its offer |
| 17 | the guide's new paragraph opened with "A skipped stage is never a pass" over a list that also holds the sheet and the requirements file | PR lens | acted | the opening names both |
| 18 | "board only: nothing to wire" is a literal in `build_service.board_alone` and a sentence in `flow_codes` | PR lens | raised | dropped because nothing decides on the text and the record keeps no stage detail; P899 #1277's plan may put the detail in the record |
