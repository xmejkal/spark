# P897: the mutation rows whose anchor lost its line: rows

Card: [P897 #1273](https://github.com/xmejkal/spark/issues/1273), PR 1 of 2 (the push-hook guard follows in PR 2). On
`origin/main` 37323447, `mutate.py --anchors tests/mutations/*.json` refused 33 of 4932 rows in 23 tables on 15 files (16
after the two file moves). 32 got a new `find` and `replace` with the same meaning and one was removed. Every row was
planted by hand in a scratch copy of the tree (its near test modules, or the module named in the row), each on its own
copy and in parallel, because a sequential plant took 7 minutes a row on a loaded machine. The last plants (rows 1, 9, 11) ran under pyenv Python 3.10.0, the team's. The hook under Homebrew Python 3.13.5 fails `tests.test_suite_runs` ([P1100 #1618](https://github.com/xmejkal/spark/issues/1618)), not this change; the hook of the push ran under 3.10.0. Every red test was run clean as
its control. "Moved by" is the commit that moved the line (`git log -S`). Rows 1 to 33 are acted, in the table order of
the PR body.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | `p124-every-field[20]`: `_kept` passes the record's sha256s and `finished` | P874 35c3dace | acted | re-anchored on `{}, finished)\n    except OSError`. Plant red under Python 3.10.0 (control OK): `test_check_spine` `test_a_keep_that_cannot_write_still_prints_the_verdict_and_says_so` and `test_a_keep_into_a_file_still_prints_the_verdict_when_the_build_simulated` |
| 2 | `p190-serial[2]`: `wires_in` gained `apart` | P792 8fb76fef | acted | re-anchored, drops only the serial clause. Plant red: `test_build_service` `test_a_skipped_part_beside_a_real_one_with_no_wire_is_still_the_unwired_diagram` |
| 3 | `p219-gate[11]`: the evidence is built first | P865 2412b738 | acted | `evidence_for(project, False, False,`. Plant red: `test_look` `test_a_fake_child_that_names_a_syntax_error_is_the_no_token_sentence_and_no_real_child_runs` |
| 4 | `p429-firmware-line[15]`: indented under `if toml.is_file():` | P1001 ed3eebd5 | acted | same text at 12 and 16 spaces. Plant red: `test_project_image` `test_an_image_outside_sim_is_a_deploy_error_as_it_is_a_refused_run` |
| 5 | `p458-look-outside[2]`: as row 3 | P865 2412b738 | acted | the call without `run=`. Plant red: `test_look` (the test of row 3) |
| 6 | `p462-start-wait[1]`: `_key` is now `known_board.comparable_key` | P865 2ca8c2a5 | acted | file moves to `bench/known_board.py`, find and replace unchanged, `test_board_start` added to the near tests. Plant red: `test_bench_show` `test_a_live_grant_is_asked_by_the_serial_and_a_deploy_grant_by_the_mac` |
| 7 | `p462-start-wait[18]`: `usb_of` holds the same `if` | P1007 review 1d6f746c | acted | a 3-line find, so it mutates the deadline `if` (board_start.py:117), the one the old find named; `usb_of`'s (line 85) is not touched. Plant GREEN on `test_board_start`, `test_board_questions`, `test_board_live`, `test_deploy_gate` (row 34) |
| 8 | `p468-serial-warning[5]`: `+ notes + found.note` | P792 66960c26 | acted | Plant red: `test_check_spine` `test_a_full_build_on_a_board_heard_without_wires_gives_no_serial_warning` |
| 9 | `p484-onboard-parts[7]`: `netlist: designed` in cli.ts | P792 f22d9dd0 | acted | Plant red under bun (scratch copy after `bun install` from the lockfile): `bun test` 52 pass, 1 fail, the clean tree 53 pass: "a netlist given as JSON (--netlist) > the cli wires the board's own LED and button from the spine's netlist and mapping"; `test_converter` also fails |
| 10 | `p507-event-seam-e1[6]`: the look's `run` is reordered | P865 2412b738 | acted | a 14-line find, the BEGIN moved after `service.run`. Plant red: `test_known_board` `test_10_the_begin_comes_before_the_list` |
| 11 | `p677-bench-privacy[13]`: `PASTED_CODES` gained codes | P865 2ca8c2a5, P1029 | acted | Plant red under Python 3.10.0 (control OK, with `test_json_contracts`): `test_golden_bench` `test_look_could_not_run_last_deploy_not_checked_json` |
| 12 | `p737-live[10]`: `reply_strategy_for` moved to the core | P865 c20ad7df | acted | file moves to `core/replies.py`, find and replace unchanged. Plant red: `test_research` `test_the_frontend_chains_the_file_before_a_live_terminal_and_builds_no_terminal_under_json` |
| 13 | `p778[6]`: `write_limits` takes `found.gpios` | P792 | acted | `write_limits(sim_dir, loaded, board)`. Plant red: `test_build_service` `test_a_converter_that_wires_no_stand_in_says_so_and_the_limits_do_not_claim_them` |
| 14 | `p778[7]`: `and not skipped` | P792 | acted | Plant red: the same test as row 13 |
| 15 | `p802-idea-area-checks[0]`: `flow_codes` joined `LEAVES` | P825 fbc71f5d | acted | `test_architecture` added. Plant red: `test_u1_every_module_that_calls_itself_a_leaf_is_one_of_the_leaves` |
| 16 | `p829-run-request[11]`: the line has a with-note branch | P1008 6219e8a9 | acted | `else line_of(offer.key, result)`. Plant red: `test_run_request` `test_a_pick_runs_the_pick_with_the_need_and_the_part_of_its_key` |
| 17 | `p97-council[46]`: adoption lines follow the step's line | P1006 8fdeff82 | acted | `mark_step.py` has no near test, so `test_cost`, `test_init_project` and `test_needs` ran. Plant red: `test_cost` `test_a_step_says_what_it_started_or_would_start` |
| 18 | `p97-final[24]`: `orphan_home` joined the test | P1006 8fdeff82 | acted | Plant red: `test_parts` `test_a_board_of_another_listed_project_or_of_no_project_is_refused` |
| 19 | `p97-final[29]`: the constant `WOULD_REFRESH` | P1006 review 5a9f8e0d | acted | Plant red: `test_parts` `test_a_dry_run_says_it_would_adopt_and_the_json_names_the_adopted_ids` |
| 20 | `p97-one-writer-fix[0]`: `locked()` rewritten | P922 b095f026 | acted | `if not fcntl:`. Plant red: `test_store` `test_a_lock_taken_inside_a_lock_does_not_wait_for_itself` |
| 21 | `p97-one-writer-fix[1]`: as row 20 | P922 | acted | `holder = (0, ...)`. Plant red: `test_store` `test_another_thread_waits_for_a_store_taken_a_second_time` |
| 22 | `p97-one-writer-fix[2]`: as row 20, 8 spaces | P922 | acted | Plant red: `test_store` `test_another_thread_waits_for_a_store_taken_a_second_time` |
| 23 | `p97-one-writer[1]`: the `flock` moved into `_take` | P922 | acted | removed, not re-anchored: `p922-store-lock.json[0]` plants the same mutant (`fcntl.flock(held, fcntl.LOCK_EX)` to `pass`) at its new indent, and a copy would plant it twice. The removed row carried `"tier": "critical"` and `p922-store-lock[0]` carries none, see row 37 |
| 24 | `p97-one-writer[6]` (now index 5): the lock is the store's own folder | P922 | acted | `Path(tempfile.gettempdir())` in `_hold_home`. Plant red: `test_store` `test_a_home_that_is_a_file_is_the_store_s_own_refusal`. The mutant has a second defect: it also stops `locked()` from creating the store's folder, so the waiter test at tests/test_store.py:507-522 likely catches it for that reason, not for a shared lock |
| 25 | `p97-picks-detail[41]`: the listing moved to `record_home.list_project` | P1006 8fdeff82 and 5a9f8e0d | acted | `list_project(target, True)`. Plant red: `test_needs` `test_a_pick_puts_the_project_on_the_list_so_what_it_reserved_stays_free_to_it`; GREEN on its near modules `test_flow` and `test_run_request` |
| 26 | `p97-picks-detail[42]`: `add_project` left the block | P1006 8fdeff82 | acted | Plant red: `test_needs` `test_a_dry_run_says_what_it_would_do_and_writes_nothing`; GREEN on `test_flow`, `test_run_request` |
| 27 | `p97-picks-detail[43]`: an `"adopted"` key follows | P1006 review | acted | Plant red: the test of row 26; GREEN on `test_flow`, `test_run_request` |
| 28 | `p97-picks[8]`: as row 26 | P1006 8fdeff82 | acted | Plant red: `test_flow` `test_a_refused_pick_names_no_flow_step` |
| 29 | `p97-picks[22]`: as row 26 | P1006 8fdeff82 | acted | `needs.write` before `drawer.apply`. Plant red: `test_needs` `test_a_store_that_refuses_the_history_leaves_the_project_file_untouched_and_a_retry_finishes_the_pick`; GREEN on `test_flow`, `test_run_request` |
| 30 | `p989-board-shelf[6]`: `list_project` holds the same line | P1006 8fdeff82 | acted | the comment `# P989` joins the find. Plant red: `test_parts` `test_a_shelf_copy_of_a_listed_project_s_board_is_filled_in_that_project_and_shelved_again` |
| 31 | `sprint-10-p95-4[7]`: `notes += listed` | P1006 hook 57ca21c7 | acted | Plant red: `test_init_project` `test_init_puts_the_project_on_the_list` |
| 32 | `sprint-7-p51b[1]`: the branch writes only a missing target | P874 35c3dace | acted | `if not target.is_symlink():`. Plant red: `test_check_spine` `test_a_kept_file_that_cannot_be_read_is_not_compared_and_the_rest_is_kept` |
| 33 | `sprint-7-p51b[2]`: the entry comes from `_left_alone` | P874 | acted | Plant red: the test of row 32 |
| 34 | row 7: the plant stays green | the plants | raised | the meaning holds (the deadline `if`), and no test asserts that a failed list at the deadline is asked once more. Left as re-anchored. Destination: a card for the missing test: in `test_board_start`, a start whose last list at the deadline fails once and then lists the board must end `DOWNLOAD_MODE_STAYED`, not port gone |
| 35 | row 9: the `.ts` row | the plants | closed | proved with `bun test` in a scratch copy, see row 9. The first plant ran without `node_modules` and was green; that was the missing install, not a missing test |
| 36 | rows 1 and 11: no verdict under Python 3.13 | the plants | closed | both are red under Python 3.10.0, see rows 1 and 11. The first 900 s run on row 1 and the failing control of row 11 were the 3.13 environment |
| 37 | `p922-store-lock[0]` lacks the `critical` tier of the removed row | the removal | acted | `"tier": "critical"` added to `p922-store-lock.json[0]`, so the removed row's guard stays |
