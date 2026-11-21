# P977 PR 1: the flow's guide: rows

Card: [P977 #1407](https://github.com/xmejkal/spark/issues/1407). This file holds the acted, raised and rejected
findings of the plan check (plan v4, rounds 2 and 3) and of PR 1's review (a lens and the refuter, both on Opus).
2026-11-21.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | set aside is its own field, `aside: true`, not a mark; `faults()` checks it through `CHECKS` | plan round 2, round 3 item 6 | acted | `needs.CHECKS["aside"]` allows true or null; `--match --json` gains `aside` |
| 2 | the build phase keeps `could-not-run`, so `show`'s exit does not change | plan round 2 | acted | `test_a_board_wokwi_has_no_model_of_…` asserts exit 2 and status `could-not-run` |
| 3 | one cause only: the board with no Wokwi part gets its own code, `board_not_in_wokwi`, and only that code is counted as done | plan round 3 item 1 | acted | `stages.NO_WOKWI_PART_TYPE_ENDING`; `simulation_fact_missing`, `converter_lacks_part` and a record with no code stay `now` |
| 4 | a simulate with problems or could-not-run after such a build is `now` | plan round 3 item 2 | acted | `test_a_passed_build_with_a_simulate_that_has_problems_…` |
| 5 | done is every phase before now but the breadboard; the generic problems and could-not-run lines; the deploy sentence names the person | plan round 3 items 3 to 5 | acted | `guide.done_of`, `flow_codes.PROBLEMS_NOW`, `COULD_NOT_RUN_NOW`, `DEPLOY_NOW` |
| 6 | a sheet with "Changes since" for a person who wired the old one | plan round 3 item 8 | raised | a card if it bites, as the plan says |
| 7 | the needs sentence "turn your goal into needs" is never reached: spark cannot see the chat, so a fresh project's now is the idea | the build | rejected | no fact tells a goal said from one not said; the plan's own test wants the idea |
| 8 | simulate counted as done only while not started: an old `sim/wokwi.toml` and image give it no status, and now said to run a scenario | review refuter 1 | acted | `no_model_phases` takes not-started or no status; `test_an_old_image_on_a_board_wokwi_has_no_model_of_is_counted_as_done` |
| 9 | a run that failed on the current image: now said run the scenario again | review refuter 2 | acted | `ProjectImage.failed_runs` (why_untested reads it too) gives `RUN_FAILED`, with `RUN_FAILED_NOW`; `test_a_run_that_failed_on_the_image_has_its_own_sentence` |
| 10 | firmware changed after a passed run: done listed the simulate and now was the deploy of the old image | review refuter 3 | acted | `find_newer_files` gives `IMAGE_OLDER`, with `IMAGE_OLDER_NOW`; `test_firmware_changed_after_a_passed_run_leaves_the_simulate_open` |
| 11 | `boards/README.md` named `simulation_fact_missing` for a board with no `wokwi_part_type` | review refuter 4 | acted | now `board_not_in_wokwi` |
| 12 | `parts.py --needs` and the `--match` text do not show a need set aside | review refuter 5 | acted | `[aside]` on its line; `test_the_needs_and_match_text_show_a_need_set_aside` |
| 13 | a hand-written project lists needs and parts as done; with every need set aside, now says to write the parts list from the picks | review refuter | raised | [P980 #1414](https://github.com/xmejkal/spark/issues/1414) |
| 14 | in the two jobs, `now.by` was `claude` while the sentence gives the person the wiring | review lens 6 | acted | `now.by` is a list always, `["you", "claude"]` there; flow.md says so |
| 15 | after the firmware is written the wiring is in no list | review lens 7 | acted | `breadboard (spark cannot see it)` in done once the sheet is current and the wiring is no longer part of now |
| 16 | the guide in its own module, reusing the parts phase's rule for counted and set-aside needs | review lens 8 | acted | `scripts/spark/flow/guide.py`; `phase_readers.counted` and `set_aside` take either needs shape. The guide still reads `.spark/needs.json`, `.spark/build.json` and the image itself: a fact on every Phase would change the phases' JSON contract (a comment says so) |
| 17 | `count_steps` caught a bare `Exception` | review lens 9 | acted | `guide.SHEET_UNREADABLE`: the sheet's refusals and what a malformed circuit.json raises (ValueError, KeyError, TypeError, AttributeError, IndexError, RecursionError); `TheMissingWiringTest` proves each is needed |
| 18 | names: no "pass" for a could-not-run build or a skipped simulate | review lens 10 | acted | `no_model_phases`, `stops_only_for_no_model`, `NO_MODEL_CODES`; "counted as done" in flow.md and the `--help` |
| 19 | three sentences in plainer words | review lens 11 | acted | `NO_SIMULATION_NOW`, `COULD_NOT_RUN_NOW`, `BUILD_PARTIAL_NOW` |
| 20 | flow.md: when now is null, the suffix in parentheses, how a need set aside comes back | review lens 12 | acted | the `guide` item of flow.md |
