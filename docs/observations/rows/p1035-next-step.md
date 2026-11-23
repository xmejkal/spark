# P1035: after an ok run that writes to a project, the flow's now step ends `next`: rows

Card: [P1035 #1518](https://github.com/xmejkal/spark/issues/1518), piece 3 of P793 #1105. PR 1 of the card, the next
step. The plan was written on main 3dd1e8e2 and built on main d74439d8 (after #1530). It passed two rounds: round 1 was
the architecture lens (Opus) and the refuter (Opus), round 2 the refuter (Opus). The decisions are spark-main's, in auto
mode, delegated, and they are the PO's to change. A "row" in the last column is a row of
`tests/mutations/p1035-follow-up.json`, counted from 1.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | One hook in the core's RunOptions adds the flow's now step to `next` after a run that writes to a project, after the Operation's own steps, in its text and its `--json`, tested on a pick and a build | the card's Done when | acted | `RunOptions.follow_up`, `core/follow_up.FollowUp`, `run_operation`'s `_followed`, `flow/now_follow_up.FlowFollowUp`. `test_core.TheFollowUpTest`, `test_flow.TheFollowUpTest`. Rows 1 to 19 |
| 2 | The follow-up at every status lets an agent simulate a board it failed to build, and names the failing build again | round 1, the lens and the refuter, must-fix | acted | status `ok` only. Tests of a refused pick, a build that could not run and a build with problems. Row 2 |
| 3 | A text line that fails must never drop a step from the JSON | round 1, the lens | acted | the steps are added first. `test_a_line_that_raises_keeps_the_step`. Row 7 |
| 4 | The wiring of check_spine can drift from the tests | round 1, the lens | acted | `check_spine.HELP`, used by `main`, the flow tests and `fakes.run_build_board`. Row 19 |
| 5 | The core must ask only a run that writes, and the dry-run pick must not ask | round 1, the lens and the refuter | acted | `WRITES` in `effects_of(values)` and a written project. `test_a_dry_run_pick_names_no_flow_step`. Rows 3, 4, 10 |
| 6 | Test 18 reading `NextStep("<op>"` in the source misses `look` | round 2, the refuter | acted | the test calls each `_step` and `_steps` builder of `offer_steps` and `phase_steps` on a fixture, and finds `look` and `init_project`. Row 16 |
| 7 | The brief step has `needs_yes` and no `needs_person`, and holds `<answers.json>` | round 2, the refuter | acted | the line ends with `, needs you` for either. flow.md names both placeholders. `test_the_line_marks_a_step_that_needs_the_person_s_yes_and_names_its_script`. Row 18 |
| 8 | A `FlatJsonLine` data that is no dict must be left as it is | round 2, the refuter, nit | acted | `FlatJsonLine.with_next`. `test_the_flat_line_holds_next_last`. Row 12 |
| 9 | Test 12 of the plan, a refused pick with two open needs, sees no difference: with two open needs the flow names no step | the build, measured | acted | the test has one open need, so the flow names its pick and the refused run names none |
| 10 | After a kept build with firmware, `next` holds the build's own look before the flow's scenario run | the plan's finding 1 | raised | the build's look is the only pointer after a first build. Destination: piece 6 of [P793](https://github.com/xmejkal/spark/issues/1105) |
| 11 | Two forms of a text `next:` line remain: parts.py's short form, and the whole path with the store | the plan's finding 2 | raised | Destination: piece 6 or 7 of [P793](https://github.com/xmejkal/spark/issues/1105) |
| 12 | One folder is written two ways in steps (`/private/var/...` and `/var/...`) | the plan's finding 4 | raised | Destination: a later card under [P793](https://github.com/xmejkal/spark/issues/1105), one form of a project path in a step |
