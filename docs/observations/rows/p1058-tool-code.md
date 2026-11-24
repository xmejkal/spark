# P1058: a tools file spark cannot read keeps its own code and fix in the bench and the build: rows

Card: [P1058 #1555](https://github.com/xmejkal/spark/issues/1555). This file holds the acted, raised and rejected findings
only. The plan had its council, a lens (Sonnet) and the refuter (Opus), and spark-main decided each item (auto mode,
delegated, the PO's to change). The PR's review was one lens (Sonnet) and the refuter (Opus); spark-main
decided each item the same way. The PR waits for the PO's read of the two new build fixes. 2026-11-24.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | `bench.py record` loses its AGAIN fix for a tools-file stop, because `_stopped` adds it only where the stop names no fix, so bench.md's "its fix names the next command" goes untrue | the plan council, the refuter (A) | acted | fixed: `_stopped` keeps the AGAIN fix for `TOOLS_FILE_CODES`; `ABrokenToolsFileTest.test_record_keeps_its_again_fix_for_a_tools_file_stop`, a child on a real broken tools file, and a mutation row pin it |
| 2 | `EveryCodeHoldsItsFixTest.BUILD_FIXES` ("as the PO read it") fails, and its count goes from 26 to 28 | the plan council, the refuter (B) | acted | fixed: the two build fixes are in BUILD_FIXES on purpose; the PR's first lines show them to the PO |
| 3 | four of the five `tools_list_broken` sentences name no fix, so stop_result should give these codes their fix line on stderr | the plan council, the refuter (C) | raised | card [P1086 #1595](https://github.com/xmejkal/spark/issues/1595): not built here, because the second line makes `test_grant` and `test_reach` (`test_a_newline_in_the_project_path_cannot_fake_a_line_of_a_tool_problem`, one stderr line) red; the Finding carries the fix in `--json` |
| 4 | the build's new fixes should say "or move it away", not "delete it" | the plan council, the lens (D) | acted | fixed: both build fixes say to move the file away, then build again |
| 5 | only the records list of `TheBenchCodesTableTest` changes; the build's `shared` stays | the plan council, the refuter (E) | acted | fixed: the records list and its pairwise meanings changed, `shared` did not |
| 6 | the critical tier is full (50 rows) | the plan council, the refuter (F) | acted | fixed: no row of `tests/mutations/p1058-tool-code.json` is critical |
| 7 | the mutation row of the tools-list ending must name the constant, because both endings share their message | the plan council, the refuter (G) | acted | fixed: the row's `find` holds `TOOLS_LIST_BROKEN_ENDING = ` |
| 8 | the `check_spine.py --json` child test must pass with tsci on PATH and without it | the plan council, the lens (H) | acted | fixed: run both ways, green both times |
| 9 | look.py and deploy.py still say `tool_missing` for a tools file | the plan, out 1 (I) | raised | [P1083 #1590](https://github.com/xmejkal/spark/issues/1590); stop_result's docstring says reason_of folds this in later (P1083) |
| 10 | `tool_entry_broken` and the other ToolError codes still read as `tool_missing` | the plan, out 2 (I) | raised | [P1084 #1591](https://github.com/xmejkal/spark/issues/1591) |
| 11 | init_project says `tools_file_unreadable` where the bench and the build say `file_refused` | the plan, out 5 (I) | raised | [P1085 #1592](https://github.com/xmejkal/spark/issues/1592) |
| 12 | the converter stage could meet a tools-file error too | the plan, out 3 | rejected | dropped because the build stage reads the same tools files first and stops the run; a board-only build reads no tools list |
| 13 | `find_toolchain` could raise instead of returning None | the plan, out 4 | rejected | dropped because `requirements_build._work_folder` calls it outside the stage guard (F1); its docstring says so |
| 14 | `check_spine.py --json` prints the store's path whole in the detail | the plan, out 6 | rejected | dropped because check_spine is not a bench script, and the path is the person's own |
| 15 | the plan's `ENGINE_ENDING_OF` table hides both new endings from `test_stages`' call-site test, which reads only names passed to `ended` | the build | acted | fixed: `_build_circuit` ends with each new ending in its own `ended` call; no table |
| 16 | `test_stages.ENDS_AS`, which lists every ending of every stage, lacks the two new endings; the plan did not name it | the build | acted | fixed: two rows added, no row changed |
| 17 | p920's mutation row "a stop that names no fix names no next command" lost its anchor in `record_deploy._stopped` | the build | acted | fixed: the row's `find` moved to the new line; planted by hand and caught |
| 18 | the first hook run failed twice: the new tests read `records_codes` constants as their expectation (`test_self_confirmation`), and a new `tool_finder` import in test_bench_record.py changed the generated map, a file of the held PRs | the build, the hook | acted | fixed: the tests compare with literals, and the record test is a child on a real broken tools file, so test_bench_record.py imports no `tool_finder` and map.md does not change |
| 19 | a stray edit changed `test_what_the_chain_was_handed_is_what_is_recorded_not_what_the_file_became_meanwhile` (test_check_spine.py:2846): a global replace of its requirements line | the PR review, the refuter (1) | acted | fixed: the line is main's `["l9110s-module"]` again |
| 20 | test_json_contracts.py's comment "four build codes are equal literals of another leaf" is stale beside records_codes' two | the PR review, the refuter (2) | acted | fixed: the comment names the four and records_codes' two (P1058) |
| 21 | the decision on council C is made, so row 3 names its card | the PR review, the lens | acted | fixed: row 3 is raised to P1086 #1595 |
| 22 | the bench's records fix says "or delete it" for a broken tools file, the build's says "move the file away": two advices for one file | the PR review, the lens | raised | card [P1086 #1595](https://github.com/xmejkal/spark/issues/1595), noted there |
| 23 | the build's `file_refused` fix reads "or its permissions, or move it away": "it" is unclear | the PR review, the lens (nit 3) | acted | fixed: "fix the file the sentence names or its permissions, or move the file away, then build again"; BUILD_FIXES and the PR's first lines match |
| 24 | stop_result's docstring has a line past 120 characters, and "live.py and reach.py not yet (P1057)" is stale since #1596 | the PR review, the lens (nit 4); P1057's raised row | acted | fixed: re-wrapped, and it names grant.py, bench.py record, live.py and reach.py |
| 25 | `test_stages.ENDS_AS` is a test the plan did not name (row 16) | the PR review | rejected | the rows stay: a new ending pinned on purpose, no assertion weaker (spark-main, delegated) |
