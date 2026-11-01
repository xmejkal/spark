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
