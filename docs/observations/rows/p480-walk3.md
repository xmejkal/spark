# Walk 3: gap rows

The gaps of spark walk 3 (epic #467), on 2026-11-01 in Prague, from 06:57 to 08:39 CET. The diary is `walk3-diary.md` in the same folder. Each claim is the first sentence of the diary's gap. Status `raised` means that nobody checked it after the walk. The column "where it went" names the proposed card in the diary (C1 to C8), or "row only".

| # | claim | source | status | where it went |
|---|---|---|---|---|
| 1 | The goal names "the board that is connected". No spark page tells a new user how to find out which board that is before init. | diary G1, step 1 | raised | proposed C5 |
| 2 | The plugin cache holds spark 0.4.0 from 2026-09-23, with 4 skills and no `commands/`. | diary G2, step 1 | raised | row only |
| 3 | With no `requirements.json` in the folder, the look says "requirements.json names no board". | diary G3, step 2 | raised | proposed C5 |
| 4 | The look and init wait on each other. Init needs a board name. | diary G4, step 2 | raised | proposed C5 |
| 5 | Init writes to the store's `projects.json`, but the init page lists only the files in the project. | diary G5, step 3 | raised | proposed C4 |
| 6 | `check_all.py` still calls the 4 skipped checks "not asked for", when the cause is that nothing is built yet. | diary G6, step 3, still open from walk 2 G1 | raised | row only |
| 7 | No spark command answers "what does spark know about this board?". | diary G7, step 3 | raised | proposed C5 |
| 8 | The idea page tells Claude to run `parts.py --step <project> S`, and later M, C and L, but it does not say that each one writes a line to the store's history. | diary G8, step 4 | raised | proposed C4 |
| 9 | `parts.py <op> <project>` takes a folder path, but init prints the project's name ("on your projects list as 'walk3'"), and the idea page writes only `<project>`. | diary G9, step 5 | raised | proposed C3 |
| 10 | No spark command removes a project from the list or a line from the history. | diary G10, step 5 | raised | proposed C3 |
| 11 | `--match` still lists `xiao-esp32-c6-fresh (button-light)` for all 3 needs, with no word on what it is. | diary G11, step 5, still open from walk 2 G8 | raised | row only |
| 12 | `--offer firebeetle2-esp32s3` still prints "compute microcontroller" twice in its `does` line and cuts the power line in the middle of its JSON. | diary G12, step 5, still open from walk 2 G9 | raised | row only |
| 13 | For the FireBeetle's LED and button, `--match` and `--pick` say "the board record names no Wokwi definition". | diary G13, step 5 | raised | proposed C2 |
| 14 | The idea page says that a `board <key> for <need>` note names the other choice, the first owned part with free stock and a Wokwi model. | diary G14, step 5 | raised | row only |
| 15 | The board doctor read the USB serial `34851842e4100000`, which holds the MAC `34:85:18:42:e4:10`. | diary G15, step 6 | raised | proposed C5 |
| 16 | Spark knows that this board was flashed at 06:23 today with the verdict "ready seen", but its console was silent for 2 s at 07:18. | diary G16, step 6 | raised | row only |
| 17 | The idea page shows `parts.py --step <project> S` with no dry run, but the `--step` dry run is the only output that showed "would list walk3-2" before the write. | diary G17, step 7 | raised | proposed C3 |
| 18 | The look read every field and gave the verdict "match", but it reported `could-not-run` and exit 2, the same status as at 07:18, when it read nothing. | diary G18, step 8 | raised | proposed C5 |
| 19 | After the bootloader buttons, the board stays in its bootloader until RESET. | diary G19, step 8 | raised | proposed C5 |
| 20 | A board-only project gets less output than a project with one added part. | diary G20, step 9 | raised | proposed C2 |
| 21 | Spark has no linter and no type check for firmware. The only compile step is in `scripts/image_evidence.py`, for an image that no simulation tested. | diary G21, step 10 | raised | proposed C8 |
| 22 | No spark page lists the kinds of test in one place, with what each proves, what it costs and when it runs. | diary G22, step 10 | raised | row only |
| 23 | No user page links the discovery `docs/discovery/2026-10-18-p295-own-simulator/finding.md`. | diary G23, step 11 | raised | proposed C1 |
| 24 | Spark has no way to check a PWM must line in a simulation. A Wokwi scenario checks a pin's level (`expect-pin`), not its duty. | diary G24, step 11 | raised | proposed C1, proposed C8 |
| 25 | `check_spine.py` writes `built` to the store's history when the chain runs end to end, but it has no dry run, and its `--help` does not mention the store write. | diary G25, step 12 | raised | proposed C4 |
| 26 | A board-only build writes no serial monitor wires. `board_alone` in `scripts/check_spine.py` writes the diagram by hand with `"connections": []`, and it skips the converter that adds the wires (P190). | diary G26, step 13 | raised | proposed C2 |
| 27 | A board-only build never writes `built` to the store's history. | diary G27, step 13 | raised | proposed C4 |
| 28 | The board-only diagram holds the stand-in S3 devkit alone. It has no LED on GPIO21 and no button on GPIO47, so no scenario can press the FireBeetle's button or see its LED. | diary G28, step 13 | raised | proposed C2 |
| 29 | The FireBeetle's board record names a Wokwi part type but no Wokwi definition in the store. | diary G29, step 13 | raised | proposed C2 |
| 30 | Spark's example firmware still lacks the lines that read the console without waiting. | diary G30, step 15, still open from walk 2 G24 | raised | proposed C8 |
| 31 | Spark still has no command that presses a button and reads a pin or a PWM duty on the Mac. | diary G31, step 15, still open from walk 2 G23 | raised | proposed C8 |
| 32 | The run passed and the verdict reads "passed", but it tested neither must line. | diary G32, step 16 | raised | proposed C6 |
| 33 | Spark keeps some hand edits and overwrites others, and no page lists which. | diary G33, step 17 | raised | proposed C7 |
| 34 | The look could not reach this FireBeetle on its own twice, at 07:18 and at 08:21, and each time it needed the bootloader buttons. | diary G34, step 18 | raised | proposed C5 |
| 35 | The deploy page says that `deploy.py` is in the command's `allowed-tools`, so "Claude Code does not ask before it runs deploy.py", and the gate is inside deploy.py. | diary G35, step 19 | raised | row only |
| 36 | The look's `next` step names `--port`, but one board is on USB, and the deploy page says to leave `--port` out then. | diary G36, step 19, still open from walk 2 G27 | raised | row only |
| 37 | Spark has no place to record a bench result for a must line. | diary G37, step 21 | raised | proposed C6 |
