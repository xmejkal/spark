# P487 pages say what: rows

What the P487 build (card #666) checked in the code before it wrote each sentence. Source: N6 in the P480 walk 3 council.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | Init lists the project in the store's `projects.json` (G5) | N6, p480-walk3 row 5 | acted | `init_project.py:430` calls `store.add_project`, `store.py:86` maps `projects` to `projects.json`. Sentence in `commands/init.md` |
| 2 | `--step` writes a line to the history (G8) | N6, p480-walk3 row 8 | acted | `parts.py` `_op_step` calls `store.append_event`. Sentence in `commands/idea.md` |
| 3 | `--step` has a dry run, and the idea page shows it first (G17) | N6, p480-walk3 row 17 | acted | `_op_step` prints `would start` and `would list` under `--dry-run`. Sentence in `commands/idea.md` |
| 4 | The other-choice note comes only with a pin limit (G14) | N6, p480-walk3 row 14 | acted | `needs.py:377`: `_other_choice` runs only when `limits.no_pin`. Sentence changed in `commands/idea.md` |
| 5 | A board-only build writes no `built` (G27) | N6, p480-walk3 row 27 | acted | `check_spine.py:389` returns `board_alone` with skipped stages, and `vouches_for_a_build` refuses a skipped stage (line 621). Sentence in `commands/build.md` and `docs/guide/agents.md`, tally hint in `parts.py`, pinned in `tests/test_cost.py` |
| 6 | The deploy page says what to do when the host refuses the run (G35) | N6, p480-walk3 row 35 | acted | Walk 3 diary: auto mode refused the run as "Production Deploy" before deploy.py printed its line. The page now says to give the look's `next` step as the terminal line. I did not write that auto mode always refuses |
| 7 | The firmware step shows the lines that read the console without waiting (G30) | N6, p480-walk3 row 30 | acted | No page has a firmware step, and no example in the repo holds the lines. The nearest page is the ready contract in `commands/build.md`. The lines come from the blink firmware outside the repo (`select.poll`, `register(sys.stdin, POLLIN)`, `poll(0)`, `read(1)`). No spark test runs them |
| 8 | The example firmware in `tests/data/breadboard/button-light/firmware/` has no console lines | found | raised | `light.py` never reads the console. Left alone: a fixture change is a separate card (C8) |
| 9 | `docs/guide/journey.md:1286` says "as the blink does", and the blink lives outside the repo | found | raised | The new build page text does not depend on it. The journey sentence stays for the next sweep |
| 10 | The page may ship console-reading code taken from a project outside the repo | reviewer (MUST 1, 2) | rejected | spark exports facts, never behaviour; no test runs the code on an S3 USB console. The page now states the P215 bench re-run's record and points to MicroPython's `select.poll` docs |
| 11 | A firmware that never reads its console ignores Ctrl-C | reviewer (SHOULD 3) | rejected | a cause no record shows; the page states only what the P215 bench re-run recorded |
| 12 | The deploy page's "its auto mode did on walk 3" implies the refusal is stable | reviewer (SHOULD 5) | acted | the parenthesis is gone |
| 13 | journey.md's "as the blink does" points outside the repo | reviewer | acted | the clause is gone |
| 14 | The build page's console record is from walk 2 | refuter 1 | rejected | journey.md has no walk 2; the record is the P215 bench re-run, 2026-10-15; the page and rows say so |
| 15 | The select.poll docs say it polls `sys.stdin` without waiting | refuter 2 | rejected | the docs say only a stream and a timeout in ms; the page says that |
| 16 | A note that names a pin limit always names the other choice | refuter 3 | rejected | `needs.py:351-356` gives ALL_HELD or nothing; the idea page says so, as agents.md:193-195 does |
| 17 | The look's `next` step is a line to run | refuter 4 | rejected | it is `{op, argv}` without the script, and only `--json` prints it; the page says `deploy.py` plus its argv |
| 18 | init writes its files when the store refuses | refuter 5 | acted | `init_project.py:429-432` catches only StoreProblem; SPARK_HOME on a file raises FileExistsError and writes nothing. Older code: a bug card; fixed by P496 (#678, PR #683) |
