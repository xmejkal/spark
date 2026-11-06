# P655 deploy on the core (W4-2, E2, P457): rows

What the plan council's two rounds found, and what the build changed against the plan. Card:
[P655 #879](https://github.com/xmejkal/spark/issues/879). Plan: `~/.claude/plans/p655-deploy-core.md`.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The platform comes as a `_for` builder per project, not an instance, and the builder gets `outside.find_tool` | round 1, architecture lens | acted | `DeployImage(platform_for=None)`, default `MicroPythonPlatform` |
| 2 | Names: `make_consent`, `grant_service`, `ConsentStrategy.yes_kind` | round 1, names lens | acted | outside.py, deploy_image.py, deploy_gate.py |
| 3 | A crash after the erase says the board may be erased; event texts lose their two leading spaces; check 4 compares the printed stream | round 1 | acted | `DeployImage._crashed`, the check-4 test in test_deploy_gate.py |
| 4 | `run_operation` asks `effects_of`, so every frontend declares the same effects | round 1 | acted | cli.py `_guarded_result`, `Operation.effects_of` |
| 5 | The `--no-simulation` dry run declares RUNS, because its compile check runs a child | round 1, refuter | acted | `DeployImage.effects_of`, tested in test_deploy.py |
| 6 | The test that a given consent beats a valid grant goes, and its mutation row with it | round 1 | acted | test deleted, p242 row "grant-beats-the-given-consent" dropped |
| 7 | The echo as a call argument | round 1 | rejected | every look run captures its output, so `echo_to` on ProgramRunner changes no look output |
| 8 | The constructor sentence says "a `_for` builder"; test_core.py:343 takes `lambda effects`; the crash catch comes after the other catches | round 2, refuter | acted | patterns-and-names.md, test_core.py, `DeployImage.run` |
| 9 | Steps 3 to 5 are one commit, because the new `DeployService` signature breaks six callers | round 2 | acted | commit 917bc32e |
| 10 | `DeployImage.run` takes 7 parameters, one per Argument, over R3's five | the build | raised | the Operation contract gives one keyword per Argument; written into the baseline, to be judged in the review |
| 11 | `DeployRun.__init__` took 6 parameters | the build | acted | it takes `service_for(world)`, `outside` and `grants`: three |
| 12 | `T2:tests/test_deploy_gate.py` cannot leave the baseline: `flash_image.interpreter_for` reads `tools.merged(project)` itself, so no finder replaces the `interpreter_for` patch at the no-simulation setup | the build | raised | the baseline holds 1, down from 5. A later card gives `build_entry` a finder |
| 13 | `measure.py --rules --accept` also tightened six values that had fallen on main (assign_pins.assign 118 to 116, boards.validate 148 to 147, check_physics module 662 to 659 and main 39 to 32, parts module 2375 to 2373, tools module 670 to 669 and main 81 to 80) | the build | acted | tests/architecture_baseline.json |
| 14 | The exact-text test cannot copy a golden: no golden reaches ready. It builds today's strings from the fixtures, and the same run on main gave the same bytes but the temp paths | the build | acted | test_every_line_of_a_ready_deploy_is_an_event_printed_as_before_and_none_is_a_result_line |
| 15 | Six mutation rows on `deploy.py`'s print helper were renamed when they moved, because the helper is gone: they now guard the reporter and the diagnostics path | the build | acted | p423-guard-lines.json rows 7, 8, 9, 15, 16, 17, 18 |
| 16 | Twenty rows of other tables anchored on text the move changed (`report` to `look`, `show_line`, `deploy_envelope`); all re-anchored. Four refusals that pre-exist on main stay | the build | acted | `mutate.py --anchors` on the 15 touched tables: 4 refused, all four refused on main too |
| 17 | `tools/check_commit.py --full` and the whole suite were not run by the builder: the push hook is the gate | the build | raised | the coordinator pushes |
