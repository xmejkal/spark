# P698 the wave 6 plan, design with build: rows

What the plan council found while Fable 5.1 refined the design-with-build group of the wave 6 plan. Card:
[P698 #943](https://github.com/xmejkal/spark/issues/943). Plan:
`docs/discovery/2026-10-19-p323-target-architecture/architecture/wave6-plan.md`, whose Council section ("P698 round 1")
lists each change. Round 1 ran on 9428ddb2 (the refuter on Opus, an architecture lens on Sonnet). A row "acted" names
the plan section that changed. The coordinator decided rows 1 and 2.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | the `check_spine` split into `build_service.py`, `board_engine.py` and a kept module makes no cycle | refuter, round 1 (blocking) | acted | `convert` (`:566`, `:568`) and `converter_stage_problem` (`:233`) build `Stage`, and `run` calls `said_of_a_crash` (`:412`, `:445`), which the plan left in the CLI. `Stage` goes to `stages.py` (the page's name) and `said_of_a_crash` to `build_service.py`. `run` stays a function there until the `BuildService` card, in the same file. W6-U3 |
| 2 | a fake `tsci` on a `PATH` of the shim folder alone drives the build stage | refuter, round 1 (blocking, reproduced) | acted | `mkdir` and `cp` print "command not found" and exit 0 with no `circuit.json`, a `#!/usr/bin/env python3` fake exits 127, and `tools.find` refuses `tscircuit` ("needs bun") and `circuit-to-wokwi` ("needs node") with `kind`, `exe` and `also` set. The fakes call `/bin/mkdir`, `/bin/cp` and an absolute Python, and the override sets `"needs": []`. Three tests prove the fakes run. W6-D1 |
| 3 | `SCRIPTS.parent` (`:373`, `:582`) is the plugin folder | refuter | acted | under `scripts/spark/build/` it is `scripts/spark`. Both read `boards.PLUGIN_ROOT`, and W6-D1 gains `ok-reference.json` (no argument). W6-U3, W6-D1 |
| 4 | `run` returns 12 refusal Stages from `:409` | refuter | acted | 20 from `:379`, `convert` 2, `converter_stage_problem` 1, `main`'s third at `:750`. Est. 14 codes. W6-U2 |
| 5 | `DesignError` 31 sites, `Impossible` 12, `emit_footprint.main` 2 | refuter | acted | 30, 11 and 3 (`:323`). W6-D2 |
| 6 | `MAY_READ` has 17 keys on the 13, 15 change | refuter | acted | 21 keys (`:50` to `:80`), 16 change, `emit_footprint.*` becomes `footprint_emitter.*`. The moves |
| 7 | `part_shape.py` has one `NotDrawn` site | refuter | acted | six: `:110` returns one, five raise, and only `:226` has no code. W6-D3b |
| 8 | `part_shape`'s move to breadboard is said once | lens | acted | a named done-item of W6-D3b, after W6-B3 (P694), with `areas/design.md`, `areas/breadboard.md`, `refactor-plan.md:639` and the W6-B2 sentence at `wave6-plan.md:521` |
| 9 | the split and `EMIT_BOARD_SCRIPT` sit in the move's text with no mark | lens | acted | the split is its own commit before the `git mv`. `EMIT_BOARD_SCRIPT` (`parents[2]`) is named as the one logic-adjacent change. W6-U3 |
| 10 | `Stage.code` and the `:843` entry's `code` are library-only | lens | acted | the `kept[].code` key is in the JSON, so W6-U2 updates `docs/guide/agents/json.md` and says the key is new |
| 11 | `kept_build.py` beside breadboard's `kept_moves.py` is two meanings of `kept_` | lens | acted | `kept_files.py`: the noun after `kept_` is what a run keeps between runs, in both. `areas/build.md` gains the row |
| 12 | the 26 lazy imports | refuter, note | acted | 12 in `scripts/`, 14 in tests |
| 13 | `breadboard.REFUSALS` and `refusal_code` | refuter, note | acted | after P694 they live in `spark.breadboard.sheet`, cited so. A second hand-written tuple at `:962` (`keep_pins`) joins the `:843` prune. W6-U2 |
| 14 | W6-D2 reads `Refusal` from `spark/core/result.py` | refuter, note | acted | that is P693's move, so W6-D2 waits for P693 |
| 15 | `emit_board.py`'s `R1:<module>` key moves with `--accept-new` | refuter, note | acted | `measure.py:705` to `:711`, precedent P441 row 4. The W6-D3b PR body names it for the PO, the value does not rise, and a card for the `emit_board.py` split is filed with the plan's cards |
