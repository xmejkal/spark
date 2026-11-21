# P935 PR 5: the build area's codes carry their meaning and fix: rows

Card: [P935 #1330](https://github.com/xmejkal/spark/issues/1330). This file holds the acted, raised and rejected findings
only. The plan check had a lens on Sonnet for the texts and the refuter on Opus; the plan check's texts win over the plan's.
Then come the build's own findings. 2026-11-21.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | twelve fix texts were worded better than the plan's first texts: no_parts, stage_crashed and no_diagram, stage_timed_out, schematic_noted, tool_cannot_build, design_not_built, not_routed, chip_not_compiled, board_not_in_wokwi, converter_lacks_part, diagram_unwired, answers_unusable | the plan check | acted | the texts are in `build_codes.py` and `BUILD_FIXES` in `tests/test_json_contracts.py` pins all 26; the PO reads them before the merge |
| 2 | chip_not_compiled's fix cannot test the sentence for "wokwi-cli was not found": `stage_chips` writes "has no compiled binary" with the ToolError's own text, or "did not compile" | the plan check | acted | the fix says "if the sentence says the chip has no compiled binary"; `ACustomChipThatIsNotCompiledIsAStageTest` runs both endings through `BuildService._sim_folder` with nothing mocked inside `stage_chips` |
| 3 | `Finding.of` raises TypeError for a code that is no Code, so 19 tests that plant a non-ok Stage broke (723 ran); the plan listed 11 and the check found `test_check_spine.py:633`, `:3431`, `:3437`, `:3451`, `:3458` and `test_breadboard_record.py:376`, `:383` too | the plan check (the refuter) | acted | each planted Stage holds the Code of its real ending, with a comment naming P935 PR 5; no assertion is weaker |
| 4 | `test_check_spine.py:999` hid a crash: its Stage had no code, `Finding.of` raised, and the test passed because it never read the exit code | the plan check | acted | the Stage holds `design_codes.REQUIREMENTS_UNREADABLE` and the test asserts the run's exit code |
| 5 | the scan sees `build_service.py:504` as `Finding(..., None)`, and `findings_of` passes `stage.code`, which the scan cannot follow | the plan | acted | `Finding.of`, and `FORWARDED_CODES` names ("build_service.py", "findings_of", "stage.code"): each Stage's code is its ending's Code (`test_stages` pins by identity) or a design error's Code (the design scan pins) |
| 6 | `build_record.py:70` and `:72` name `records_codes.RECORD_FILE_BROKEN` | the plan | acted | `NAMED_CODES["build"]` names that one Code; mutation row 10 drops it |
| 7 | five mutation anchors moved: p701 "CODES misses a constant" and "the shared tool_missing says another sentence", p852 "the help names a code without its meaning", and two of p935-positional (the NAMED_CODES and FORWARDED_CODES literals this PR extends) | the build | acted | the five are re-anchored; `tools/mutate.py --anchors` refuses the same 20 rows as main |
| 8 | no Finding's fix reaches an output: `FlatJsonLine` prints data only and `check_spine.py --json` prints a stage's code, not its fix | the plan | raised | P941 https://github.com/xmejkal/spark/issues/1343 |
| 9 | `build_service.py:278` ends the schematic stage with `schematic_refused` for the emitter's Refusal, and loses the Refusal's own design code | the plan | raised | P941 https://github.com/xmejkal/spark/issues/1343 |
| 10 | `records_codes.TOOL_MISSING`'s fix disagrees with `json.md:341` | the plan | raised | P935 #1330, the bench PR |
| 11 | not_routed's text is the PO's choice: "build again with one part fewer" or "report it with the requirements file" | the plan | acted | the text offers the first step and the report; the PR body names the choice for the PO |
| 12 | two codes keep their own fix beside an equal word elsewhere: NO_PROJECT_FOLDER (init_project.py: "run init_project.py from the project folder") against design_codes', and TOOL_MISSING (the build's step) against board_codes', firmware_codes' and records_codes' | the plan | acted | the module docstring says so; the pair tests pin BOARD_UNUSABLE and INPUT_AMBIGUOUS byte-equal only; the PR body names the choice for the PO |

The rows: tests/mutations/p935-build.json.
