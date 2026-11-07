# P686 breadboard golden net (W6-B1): rows

What the plan and build of W6-B1 found, against `docs/discovery/2026-10-19-p323-target-architecture/architecture/wave6-plan.md`
(section "W6-B1, the breadboard golden net"), and the choices it made. Card: [P686 #924](https://github.com/xmejkal/spark/issues/924).

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the breadboard net needs `tsci` faked (the plan's breadboard paragraph) | plan | rejected | `breadboard.py` runs no tool and opens no URL: with `subprocess.run`, `Popen`, `urlopen` and `socket.create_connection` set to raise, `main` on `button-light-xiao` returned 0. `page.html` is `check_spine.keep_tabbed_page`'s (`check_spine.py:894`). The paragraph now says "it runs no tool" |
| 2 | `areas/breadboard.md:17` says the Operation runs `tsci` and writes `page.html` | plan | acted | it now names the sheet, `breadboard.json`, `breadboard.svg` and `wiring-record.json`, and says `page.html` is the build's. Its `tests/fakes.py:137`/`:147` are now `:251`/`:261`, and `breadboard.py:577` is `:575` |
| 3 | the 7 Cases and their exit codes | plan | closed | each probed on a scratch copy first, then by the net: 4 exit 0, 3 exit 2. The run after the accept run matched every golden |
| 4 | the sheet's title is the project folder's name | build | acted | `breadboard.py:451`: each Case copies its fixture under the fixture's own name |
| 5 | the rebuild Case | build | acted | `button-light-xiao`, run, then `button-only-xiao`'s requirements and `dist/` (as `test_breadboard_keep.change_requirements`), run again. Its golden holds 5 `change:` and 2 `not kept:` lines |
| 6 | the scrub needs a new pattern | plan | rejected | no golden holds a run date, a hash or a path of this machine (`test_no_golden_holds_a_path_of_this_machine`). The one date in the sheets is a part record's fixed text |
| 7 | the two folder-wide tests repeat `test_golden_firmware.py` | build | raised, for a card after #915 | every golden has its Case, and no golden holds a machine path. Kept as a repeat, because `golden_bench.py` is in #915's diff. Lift both into `golden_bench` once #915 merges |
| 8 | the markers are reused, not copied | build | acted | `STDERR_MARK` and `LOG_MARK` are imported from `golden_firmware`. `check_golden(golden_dir=...)`, `op_of`, `scrub`, `replacements_of`, `child_env` and `RUN_TIMEOUT_S` from `golden_bench` |
| 9 | refuter: `:596` is `return EXIT_OK`, not an exit 2 | refuter | acted | the section cites `:583` for exit 2 and says "no handled exit 1": a renderer that raises exits 1 with a traceback (`:548`-`:553`, `:559`-`:563`) |
| 10 | refuter: no Case reaches `drawing differs:` (`:592`-`:593`) or the sheet's matching paragraph | refuter | acted | only a mocked `_plan_layout` reaches them. The section names `tests/test_breadboard_match.py:126`-`:137` as their cover |
| 11 | refuter: `golden_bench.child_env` passes the parent's `WOKWI_CLI_TOKEN` and needs two canned files | refuter | acted | `golden_breadboard.child_env` pops the token, and `test_the_child_env_holds_no_wokwi_token` checks it with a pretend token in the parent. It passes the bench's own flash id and device list, which `breadboard.py` never reads |
| 12 | refuter: `areas/breadboard.md:128` repeats the `tsci` error, and `:17` leaves out two written files | refuter | acted | `:128` says `breadboard.py` runs no tool and `FakeTscircuitExport` gives the build's page its tabs. `:17`, see row 2 |
| 13 | `developing.md` names the breadboard goldens | build | acted | beside the firmware ones, with the accept form `SPARK_ACCEPT=breadboard`. 378 lines, within its budget of 379 |
| 14 | the mutation table | build | acted | 7 rows: the scrub skipped, a wrong exit code, the stderr dropped, the written files not appended, the rebuild's first run skipped, the token passed on, and one product row (no `not kept:` lines). Every anchor once (`--anchors`), not run |
| 15 | review: `developing.md:82` is 167 characters | review | acted | the paragraph is wrapped at 120 from that line to its end. 378 lines, within its budget of 379 |
| 16 | review: the token test covers `child_env`, not the run | review | acted | `test_a_child_run_carries_no_wokwi_token` replaces `test_the_child_env_holds_no_wokwi_token` (row 11): `run_child` runs a probe script with a pretend token in the parent, and the child prints none. Mutation row 6 (the `env.pop` in `child_env`) tried by hand: the test fails |
| 17 | review: the test restores the variable by hand | review | acted | `mock.patch.dict(os.environ, ...)`, which T2 allows |
| 18 | review: `areas/breadboard.md` cites `WIRING_VIEWS` at `breadboard.py:82` and `DRAWING_RENDERERS` at `:94` | review | acted | now `:86` and `:96` |
| 19 | review: row 7's status | review | acted | "raised, for a card after #915" |
