# P1034: the simulate and the deploy name their next step, and the firmware says why it names none: rows

Card: [P1034 #1517](https://github.com/xmejkal/spark/issues/1517), piece 2 of P793 #1105. The plan was written on main
e521db8f. It passed two rounds: round 1 was one lens (Sonnet) and the refuter (Opus), round 2 the refuter (Opus), who
built the plan. The decisions are spark-main's, in auto mode, delegated, and they are the PO's to change. A "row" in the
last column is a row of `tests/mutations/p1034-phase-steps.json`, counted from 1.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | "Core and CLI first": each phase with no offer gives a step in `next` when it is the guide's now, with needs_person where the person acts, and `flow.py show` names it on the NOW line | the PO's order, 2026-11-23, the card's Done when | acted | `scripts/spark/flow/phase_steps.py`, `show_flow.now_steps` and `now_tag`. `TheNextOnlyStepTest`, ten tests |
| 2 | There is no look phase and no flow phase reaches a RESET: the look is the deploy phase's first step, and the deploy's own `watch` step covers a RESET | the plan, measured | verified | `flow_codes.PHASES` holds nine phases. The card's Done when reads "simulate and deploy, the firmware with a reason" |
| 3 | The firmware is not-started only while `firmware/main.py` is missing, so an import check would check nothing there | round 1, the lens, must-fix | acted | no firmware step. `test_a_firmware_now_names_no_step_because_main_py_is_not_written_yet` |
| 4 | `test_the_answer_names_no_home_path` failed on the round-1 plan: the import check's argv held the project path | round 1, the refuter | acted | with no firmware step it passes unchanged. Steps keep `argv` and `env` raw, as P1030's do, and test 10 checks the JSON outside them |
| 5 | The NOW line does not say that the step needs the person | round 1, the lens | acted | `[next: <op>, needs you]`. Rows 14 and 15 |
| 6 | The docs do not say what an op in the form of a script's name is, and no test keeps a next-only op out of the page's runs. flow.md said "one `{op, …}`" | round 1, the lens and the refuter | acted | flow.md's next step. `test_no_next_only_op_is_one_the_page_runs` |
| 7 | The build branch of the simulate keyed on the words of a sentence | round 1, the lens and the refuter | acted | the fact `no-sim-files`, from `ProjectImage`'s own reason `no_sim_toml`. Rows 7, 10, 11 |
| 8 | With no `sim/wokwi.toml`, the NOW sentence asked for the scenario command beside `[next: build-board]` | round 1, the refuter | acted | `SIM_FILES_NOW`, by Claude. `test_a_simulate_with_no_sim_files_names_the_build_in_its_sentence_and_its_step`. Row 12 |
| 9 | The deploy phase never ends: `DeployReader` is always not-started | round 1, spark-main | raised | one docs sentence in flow.md. Destination: piece 6 of P793 #1105, noted by spark-main |
| 10 | Capture stdout with `contextlib.redirect_stdout` and no new `mock.patch`. Add the row `phase.status == flow_codes.NOT_STARTED or (` to `True or (` | round 1, the lens, nits | acted | `show` and `lines_of` capture stdout. Row 5 |
| 11 | Keep the placeholder argv | round 1, the refuter | acted | `needs_person` and `SCENARIO_FIRST_WHY` protect it. Row 3 |
| 12 | `TheOfferStepTest.test_a_relative_project_s_step_names_it_whole_so_no_name_reads_as_a_flag` errors (TypeError str / str): `guide_of` now reads the image fact at not-started, and `read_flow` passes a str project | round 2, the refuter, must-fix | acted | `image_fact` builds `ProjectImage(Path(project))`. A row for it was dropped: its mutant makes the test an error, not a failure |
| 13 | No test covers the common simulate: `sim/wokwi.toml` there and no image | round 2, the refuter | acted | `test_a_simulate_with_its_toml_and_no_image_names_the_scenario_run_which_makes_the_image`. Row 6, `False or (` |
| 14 | Test 10's home check passed with a raw argv, because the test project was in the temp folder | round 2, the refuter | acted | `FlowTest` sets `HOME` in its `mock.patch.dict(os.environ)` to a folder of the test's own, and test 10 puts its projects there. Outside `argv` and `env`, the JSON names neither the home folder nor the project |
| 15 | The plan said that no page request runs the simulate's step. The build-board step is the build phase's offer step, which the page's `run-request` does run. Only `run_scenario` and `look` are refused | round 2, the refuter | acted | flow.md, phase_steps.py's docstring and flow.py's `--help` say so |
| 16 | `board_envelope.look_step` gives `effects: []`, while `LookAtBoard` declares reads, runs, board and asks | the plan | raised | destination: a new card under P793 #1105. Fixing it changes the build's `next` and two goldens |
| 17 | `IMAGE_OLDER_NOW` says "make the image again, then run the scenario", but the scenario run makes the image itself | the plan | raised | destination: piece 6 of P793 #1105 (the sentences), as a note on its card |
| 18 | A breadboard now still names no step | the plan | raised | destination: piece 6 of P793 #1105, as `job_offer`'s docstring says |
| 19 | The first push failed `test_self_confirmation`: the scenario test reads `run_scenario.ARGUMENTS` | the hook, the build | acted | `MAY_READ` lists it as STRUCTURE: the script's own argument table, which the step's argv must parse with. The script has no Operation yet |
| 20 | Rows: 15, none critical, each planted by hand and red as a failure; the two P1030 rows of show_flow re-aimed | the plan, the build | acted | `--anchors`: 4680 mutations in 396 tables, 33 would be refused, as on main |
