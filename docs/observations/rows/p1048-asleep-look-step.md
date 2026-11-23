# P1048: a no-board stop with a deepsleep call gives a look step in `next` that needs the person: rows

Card: [P1048 #1538](https://github.com/xmejkal/spark/issues/1538). The plan was written on main eec363a3 and had one plan
check (the refuter, Opus), whose findings A to C won over the plan. A "row" in the last column is a row of
`tests/mutations/p1048-asleep-look-step.json`, counted from 1.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | After P1049 the asleep fix's step 1 says "run look.py again", but `next` is empty, so an agent that reads `next` has no step | the card | acted | `board_envelope.asleep_next` gives the look step (no `--port`, the run's evidence flags, `needs_person`) for the asleep fix only; look.py, deploy.py and `stops.stop_result` put it in `next`. Rows 1 to 6 |
| 2 | look.py's own stop names the same look: no loop, because the step needs the person (D1) | plan | acted | `test_no_board_with_a_deepsleep_call_names_the_look_that_needs_the_person` pins `needs_person` and the why. Rows 2, 4 |
| 3 | deploy cannot find the asleep fix again in `_steps`: a ready_unknown fix opens with the same words (D4) | plan | acted | `refuse_at_look` keeps the step in `reached["asleep_next"]`; `_steps` returns it first. Row 5 |
| 4 | grant.py `--minutes` has no `--json` (argparse refuses it), so the plan's "prints nothing on a stop" was wrong | plan check A | acted | no test or help sentence about it; grant.py's epilog says that `--minutes` has no `--json`, so its step reaches no agent. `--check --json` ends with `next` (`test_the_check_s_json_ends_with_the_look_that_needs_the_person`) |
| 5 | deploy's test without an evidence flag checks no flags | plan check B | acted | the deploy test runs with `--ignore-older-runs`, and the step's argv holds it. Rows 3, 5 |
| 6 | look.py's step named the project unresolved, deploy's resolved | plan check C | acted | `_stopped` passes `platform.project.resolve()`. Row 4 |
| 7 | bench.py record's fix and step name look.py on record's `--project`, a folder that can hold no board record; the step to name is `bench.py record NAME` again | plan, out 1 | raised | destination: a card for spark-main to file |
| 8 | The board doctor's own steps (`plug_in`, `press_reset`, ...) say "run the same command again" but give no step in `next` | plan, out 2 | raised | destination: a card for spark-main to file |
| 9 | live.py and reach.py get the asleep fix and this step through `stop_result`'s `doctor_for` | plan, out 3 | raised | destination: P1057 #1554 |
| 10 | grant.py `--minutes` carries no JSON, so its step reaches no agent | plan, out 4 and plan check A | raised | destination: P1055 #1552 |
