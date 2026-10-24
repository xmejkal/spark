# P345 PR 1: a passed run says what its scenario did, findings rows

Findings from planning and building P345 PR 1 (2026-10-24, Prague). The plan council ran two rounds: two Sonnet 5.5
lenses (technology and tests, architecture and naming and UX), then one Opus 5.5 refuter. The build checked each claim of the plan in the code.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | One caveat string cannot grow: PR 2 would append to it and undo this PR | round 1 (architecture) | acted | `caveats(image)` returns a list, and `require_open_gate` takes a list |
| 2 | Reading caveats outside the look's guard can crash a look, or print `simulation: passed` without a pass | round 1 (technology) | acted | `LookService.run` sets `simulation` and `caveats` only when `why_not_ready` is None. `test_a_refused_image_is_not_asked_for_its_caveats` |
| 3 | A blink would be told that it pressed nothing | round 1 (UX) | acted | the rules use `set-control` and `expect-pin`, so a scenario that only reads a pin gets the shorter caveat |
| 4 | `ScenarioSteps` should always exist, with `unread`, as the P400 diagram draws it | round 1 (architecture) | acted | `unread` is True for a log with no counts line, a malformed line, a file that cannot be read and a step with no key |
| 5 | The counts line in the board's output can forge the counts | round 1 (technology) | acted | `from_log` reads the header only. `test_what_the_board_printed_cannot_set_the_counts` |
| 6 | Wokwi has 10 step kinds, and a `delay` must not make a log unread | round 2 (refuter) | acted | the counter counts every kind. `test_a_kind_this_does_not_name_is_counted_and_a_log_with_only_a_delay_is_not_unread` |
| 7 | The caveats must say only what the counts show | round 2 (refuter) | acted | three sentences, one per case of the counts. The wording is copied from the plan |
| 8 | The grant print adds a second copy of the caveats | round 2 (refuter) | acted | cut. deploy.py prints the look's lines before the question, and under a grant Claude reads them |
| 9 | One log is counted, not a merge of several | round 2 (refuter) | raised | two passed logs on one image: only the first is counted (`project_image.py:73-76`, as `expected_files` today). A later card |
| 10 | Both envelopes read `report.simulation`, so one source fills `data.simulation` | round 2 (refuter) | acted | `board_envelope.py`. A dry run has no look, so its `data.simulation` is now null. `test_the_dry_run_json_names_the_look_step_with_the_flag` and the golden say so |
| 11 | The person sees the caveats twice in `deploy.py`, in the look and in the question | plan | rejected | the question is where the yes is typed |
| 12 | The plan gave `caveats=()` as a default of `require_open_gate` | build check | acted | no caller omits it, and a default hides a dropped argument (learned rule 6.1). The argument is required |
| 13 | The plan named mutation anchors `p337b:41,47` and `p130:17` only | build check | acted | `p215-hashes.json` and `p239-pr6.json` quoted the log format and `to_dict`, and `--anchors` refused them after the change. All four tables follow the code. The count of refused rows is as before the PR |
| 14 | The plan said the hand-written logs in four tests gain a counts line | build check | rejected | none of them needs one: the whole suite passed without it, because those tests read no caveat |
| 15 | The plan said item 8 goes at `agents.md:576` | build check | acted | `:576` is the heading of the section. Item 8 follows item 7 at the end of the list |
| 16 | Six goldens changed: the caveat, the `caveats` key and a null `simulation` where the evidence refused the image | build | acted | accepted with `SPARK_ACCEPT=look` and `deploy`, and the diff read line by line |
| 17 | An aborted mutation run left a mutant in `scripts/image_evidence.py` | build | acted | the run was stopped with a signal while a mutant was planted. Found by reading `git diff`, and restored. A mutation run is never stopped before it ends |
