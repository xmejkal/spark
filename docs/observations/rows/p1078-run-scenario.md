# P1078: run-scenario, the scenario run as an Operation on the core: rows

Card: [P1078 #1582](https://github.com/xmejkal/spark/issues/1582), with the council lines of P1251 #1809. The plan (v3)
had two rounds: a lens (Sonnet), the architecture lens (Opus) and the refuter (Opus), then a second pass. The council of
three on Opus answered O1 to O4 as delegated, the PO's to change. This file holds the acted, raised and rejected findings
only. A "row" is a row of `tests/mutations/p1078-run-scenario.json`, counted from 1.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | `ScenarioRun.run(cli)` exists, so a `run` attribute for the world's runner clashes | plan refuter (R1) | acted | the world is `self.outside`, and `run(cli)` keeps its name |
| 2 | A constructor with `find_tool` and `run` has 6 parameters, and R3 allows 5 | plan refuter (R2) | acted | `ScenarioRun(project, scenario, micropython, timeout_ms, *, outside)`: five |
| 3 | With no `headline`, `TextReport.render` gives only `lines` | plan refuter (R3) | acted | every answer of `RunScenario` has a Headline |
| 4 | A gone baseline entry fails `test_architecture` | plan refuter (R4) | acted | `R1:scripts/run_scenario.py:main` left `tests/architecture_baseline.json` |
| 5 | Rows of p1035-follow-up, p399-scenario-ids and p130 anchor on lines that move | plan refuter (R5) | acted | each re-anchored; `mutate.py --anchors` finds every anchor once |
| 6 | `test_flow.py:1913` and `check-spine-ok-keep.txt:18` pin the script | plan refuter (R6) | acted | test_flow expects `run-scenario`; the design golden keeps its bytes (`script_of` gives `check_spine.py`) |
| 7 | P1081's done-when is wider than a map entry | plan refuter (R7) | acted | O1: `test_every_catalogue_op_a_step_names_has_its_script` landed, so P1081 #1585 can close |
| 8 | The v1 O2 loosened the `needs_yes` contract (`json.md:398-401`, `board_envelope.py:8`) | architecture lens (A1) | raised | the contract stays, and the step keeps `needs_yes` false. The question is the PO's on [P1221 #1770](https://github.com/xmejkal/spark/issues/1770) |
| 9 | The catalogue lists a paid Operation with no yes inside it | architecture lens (A2) | raised | the summary names the cost ("A run spends Wokwi CI minutes"). On [P1221 #1770](https://github.com/xmejkal/spark/issues/1770), no new card |
| 10 | Four places build `<op>.py` | architecture lens (A3) | acted | one `renderers.script_of`. `step_command`, `board_envelope.next_text` and `FlowFollowUp.line` read it; the yes clause keeps `% step.op` (row 22) |
| 11 | `find_simulator` still takes `(name, project)` | architecture lens (A4) | acted | it takes a one-name finder, the world's `find_tool` (row 21) |
| 12 | `outside` is required, with no `subprocess.run` fallback | architecture lens (A5) | acted | `outside` is keyword-only and required; row 2 plants `subprocess.run` and `test_firmware_scenario` catches it; its setUp drops `WOKWI_CLI_TOKEN` |
| 13 | Do not repeat bench's builder | architecture lens (A6) | acted | `tool_finder.build_tool_outside_world`; bench's `build_project_outside_world` calls it with its consent and replies |
| 14 | The step builder makes the project absolute itself | architecture lens (A7) | acted | `paid_run_step` writes `Path(project).absolute()` |
| 15 | `scenario_operation` reads like a base class | architecture lens (A8) | acted | the module is `firmware_scenario`, beside `firmware_check` |
| 16 | The log sections need a test, not a read diff | plan lens (L1) | acted | `TheLogSectionsHoldTest` pins the sha256 of the log section of `run-scenario-ok.txt` and `run-scenario-problems-never-ready.txt`; both still hold after the rewrite |
| 17 | `golden_bench.py:178`, `test_architecture.py:385`, `test_routes.py:342`, `test_project_image.py:173-192` | plan lens (L2) | acted | golden_bench hands a world; the other three name the script, which stays, and pass unchanged |
| 18 | `flow.md:313` and `commands/page.md:111`; run-request still refuses the step | plan lens (L3) | acted | `flow.md` names `run-scenario`; `test_flow`'s run-request test expects `run-scenario` and `look` outside `STEP_OPERATIONS` |
| 19 | New codes would need the contracts' tables | plan lens (L5) | acted | no new code; the Findings carry `firmware_codes`' words with the Operation's own fix sentence |
| 20 | O1's smaller form, one entry per map | plan lens (L6) | rejected | `step_command` has no map, so the small form adds one |
| 21 | The plan kept `find_simulator(project, find_tool)`; with a one-name finder its `project` is unused | build | acted | `find_simulator(find_tool)` and `free_checks(run)`; the find_simulator test hands only the finder, with its expectations |
| 22 | The plan's step 1 had the yes clause read `script_of`, which changes `renderers.py:111` | build | acted | the brief keeps the yes sentence and row p1032 as they are (O2 deferred), so `YES_MESSAGE % step.op` stays; no step with `needs_yes` names an op whose script differs |
| 23 | A paid run's not-checked lines as events and as lines print twice in the text | build | acted | before the paid run they are events, and in the answer they are `assumptions`; a dry run, which reports no event, has them as lines. Rows 7 and 8 |
| 24 | The caveat is the headline's sentence and a note, so `TextReport` printed it twice | build | acted | `RunReport` leaves out a note the status line holds. Rows 10 and 11 |
| 25 | `tool_finder.py` grew to 601 lines (R1, at most 600) | build, test_architecture | acted | its four `spark.records` imports are one line, and `ToolFinder`'s docstring drops what the module docstring says |
| 26 | Four text assertions of `test_run_scenario` read the old layout | build | acted | the move changes the layout, not the facts. `splitlines()[0]` of two caveat tests: `lights.v2.scenario.yaml: passed, but ...` became `✓ run-scenario: ok. lights.v2.scenario.yaml: passed, but ...`; the guard test's `run_scenario.py: simulator is not installed?? THE LINE` became `    - simulator is not installed?? THE LINE`; the wrong-id dry run's `self.stdout == ""` became its first line `? run-scenario: could-not-run. lights.v2.scenario.yaml: not run, so no Wokwi minute was spent` |
| 27 | `run_with` and the relative-project test build a `ScenarioRun` too, which the plan did not list | build | acted | both hand `program_world(project)` (a ProgramRunner over the fake CLI), expectations unchanged |
| 28 | The rows on `run_scenario.py` lose their lines | build | acted | p399 "a dry run deletes the older log" and p485 "a pass with a caveat is no ok answer" moved to `firmware_scenario.py`; p1034 "the scenario run goes without the person" to `paid_run_step` |
| 29 | p399 "a dry run prints its refusal on stdout" and p423 "run_scenario prints the tool's sentence without the guard" have no line left | build | rejected | retired: the core prints every status on stdout and guards each sentence through `TextReport` (p1032's rows), and `run_scenario.py` prints nothing itself |
| 30 | A row that keeps a relative project in the step survives: every test's project is absolute | build | rejected | dropped before it was written; `offer_steps.whole`'s own rows hold the rule |
| 31 | Row 2 would hand a real `subprocess.run` the test simulator's command | build | acted | the test simulator is `python -c "raise SystemExit(97)"`, never a wokwi-cli on the PATH, so the row starts no Wokwi run |
| 32 | The no-sim and no-token goldens change on purpose | build | acted | the refusal was `--- stderr ---` and `run_scenario.py: <sentence>`; it is the text view on stdout: the status line `? run-scenario: could-not-run. s.scenario.yaml: not run, so no Wokwi minute was spent`, the sentence under Not checked with its fix, and Next |
| 33 | D6, the paid run as a step with `needs_yes`, changes the PO's decisions | the council of three (O2, D6) | raised | the step only renames its op. [P1221 #1770](https://github.com/xmejkal/spark/issues/1770), with rows 8 and 9; the card's done-when line on it stays open |
