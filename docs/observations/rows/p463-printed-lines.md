# P463: printed lines that lead to the next step

Findings of P463 (#631), 2026-11-01, Prague, built on main e998d7dd in auto mode. Rows 1-8 are the plan, by an Opus planner with two council rounds. Rows 9-15 are the build. Rows 16-24 are the review (Sonnet reviewer and Opus refuter) and its fix round. Rows 25-27 are the fix-commit refuter (Opus) and the mutation run.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | Item 4 of the card (esptool hyphen names) | plan | closed | done in P471, PR #644 |
| 2 | The store prefix belongs in `deploy.py`'s `rerun_line` | plan draft | rejected | with it there, the grant line in the same sentence writes the grant to the default store. The prefix goes where all printed lines are built (`format_rerun_line`) |
| 3 | `shlex.join` on `SPARK_HOME=/a b` is an assignment | plan draft | rejected | it makes a command name. Only the value is quoted |
| 4 | The card's quoted refusal text, its place in `board_look.py`, and `flash_image.py:143` | card | rejected | P461 changed the text. It is built in `image_evidence.py:416-419`, and the problem sits at `flash_image.py:230` |
| 5 | A test of the line from a passed run shows the store fix | plan draft | rejected | that line never reads the store. The test uses `--no-simulation` and a control run without the prefix |
| 6 | A project tools entry needs only the fields that differ | plan | verified | it merges field by field (`tools.py:80-103`) but must give `kind`, whose default is `path` |
| 7 | XDG_DATA_HOME handling, new classes, a README change | plan round 2 | rejected | cut as more than the Done-when |
| 8 | "a log from an older spark names no image" also shows with an empty `sim/runs/` | plan round 2 | raised (LATER) | not fixed here |
| 9 | `store.py` and `flash_image.main` pass their baselines | plan | rejected, acted | `os.environ` reads went down through one `_spark_home()` reader (baseline 6 to 5). The `--micropython` help became `MICROPYTHON_HELP` (`main` baseline 39 to 36) |
| 10 | Tests can compare the grant constants with the store in the test | builder | rejected, acted | the constants are built at import, so tests use `fakes.line_made_at_import` |
| 11 | `TheOwnBuildHintTest` patches `DOWNLOADS` | plan | rejected | the mock-patch baseline. It uses the suite's scratch `tools.DOWNLOADS` |
| 12 | The new-shell test runs with an empty HOME | builder | acted | it sets `PYTHONUSERBASE` to the real user base. Without it the user-installed esptool 5.5.0 is hidden, and this Mac's system esptool 3.3 fails P471's floor |
| 13 | The project and image paths in the hints | builder | acted | resolved and quoted |
| 14 | The `deploy-no-token` row of `p283-full-path-lines.json` | builder | acted | refused on main already, because the token moved to `board_envelope.deploy_argv`. Dropped in the fix round |
| 15 | `CLAUDE.local.md` is not in the worktree | builder | closed | it is the PO's private file, linked from his store, and git does not hold it |
| 16 | The deploy line runs as printed with a space, an apostrophe and `$` in the store and project paths | refuter | verified | it reaches "no terminal to ask you in", and without the prefix it is refused |
| 17 | The own-build lines are a bare `tools.py`, which exits 127 in sh. They have no prefix, so the install lands in the default store. The hint never says to build the image again | refuter | verified, acted | built with `format_rerun_line`, which moved to `store.py`. The hint names the rebuild. Tested in a new shell |
| 18 | The build command in the no-image sentence and the refusal is a bare `flash_image.py` | refuter | verified, acted | the same fix |
| 19 | `TheOwnBuildHintTest` ran the printed commands in process, which hid rows 17 and 18 | refuter | acted | it runs them in `sh -c` |
| 20 | `store.home()` aliased `os.environ`, which hid reads from the T1 counter | refuter | acted | the alias went. One `_spark_home()` reader serves `home()` and `prefix_home()` |
| 21 | `--json` `next[].argv` carries no environment, so a caller in a fresh environment uses the default store | refuter | raised, card | P473 #647 (Idea, v0.10) |
| 22 | The entry name is printed unquoted | review | acted | `format_rerun_line` quotes every argument |
| 23 | `IMPORT_HOME` and `line_made_at_import` were copied into two test files | review | acted | one copy in `tests/fakes.py` |
| 24 | `held` held bytes, then a tuple, and a help sentence was cut inside a quote | review | acted | renamed `entry`, and the help rewrapped |
| 25 | Every printed line runs in a new shell with a store path that holds a space, an apostrophe, `$` and backticks | fix-commit refuter | verified | the build, `--new`, `--install`, rebuild, deploy and grant lines all land in the run's store, and the look gives a token. Eight more hand-planted defects were all caught |
| 26 | `tests/fakes.py` reads `os.environ["SPARK_HOME"]` at import, so a process that imports `store` before `unittest` with no SPARK_HOME raises KeyError | fix-commit refuter | raised (LATER) | no test does this today |
| 27 | Mutation run on 6da8a570 | mutation-tester | verified | 18 planted, 18 caught, in 939 s: the 15 rows of `p463-printed-lines.json` and the 3 changed rows of `p283-full-path-lines.json`. No anchor refused |
