# P512 (#708): the board emitter traces the pad: rows

The plan council's findings on the plan of P512, the build's own finds, and what the PR did with each, on 2026-11-02
in auto mode. `acted` means the PR took it, `verified` that it holds and needs nothing here, `raised` that a card
or the PO takes it.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | The no-tool board test must go through `emit_board.emit`, on both shipped boards | plan council, lens M1 | acted | `tests/test_emit_board.py` `EveryTraceReachesAFootprintPadTest`; mutation row "emit passes empty pads" |
| 2 | The rows said to be caught by `test_breadboard.py:216,225` escape: 216 answers MI by the fallback, 225 uses A5 with no alias | plan council, refuter 6 | acted | new tests: the XIAO's SDA gives D4, a board with no header rows gives MO, a requirements signal on MOSI is said as MO |
| 3 | XIAO + `dfr0664-tft-2in` still exits 1 after the fix, at the simulation: "a diagram with 0 connections" (the display has no Wokwi part) | plan council, refuter | raised | [ran] build `10 trace(s), 0 errors`, then the simulation stage fails. The tests assert the build step only. The coordinator files the card |
| 4 | Keep the board-level pad check once, through emit; do not repeat the validator at `boards.py:691-701` | plan council, S1 | acted | `BoardPadsTest` holds unit tests only |
| 5 | Drop `has_alias`; ask `pads.alias_pads()` | plan council, S2 | acted | `has_alias` dropped. The PR's first claim, "an alias key is a pin label", is false: see row 16 |
| 6 | The grep test names its scope: not `tests/`, not the TypeScript copies | plan council, S3 | acted | `OnlyBoardPadsReadsThePadAliasesTest` docstring |
| 7 | The fixture's bench line names a person and a time; the temp project needs `.spark/` and its own `parts/` | plan council, S4 | acted | `tests/data/parts/dfr0664-tft-2in.json` says "bench, the PO, 2026-11-01"; the build test never reads the store |
| 8 | Re-anchor the P36 row on the `pad_of` line | plan council, S7 | acted | `tests/mutations/sprint-8-p36.json`; its 7 rows were caught |
| 9 | The comment at `boards.py:839` says board.tsx writes `.Mcu > .<label>` | plan council | acted | it says `.Mcu > .<pad>` now |
| 10 | The verdict reads `selectors_not_found`, and the English message only when an error has none | plan council | acted | `check_spine.py` build stage; `ABrokenTraceIsNamedTest` drives a real kept circuit with 3 errors through `main`, text and `--json` |
| 11 | `BoardPads` cannot live in `boards.py`: the module is over 600 lines, and rule R1 refuses any growth (967 lines) | build | acted | `scripts/board_pads.py`, a module with one Value; the card said `boards.py` |
| 12 | A new test file may not add a `mock.patch` (rule T2), and `check_spine.py` may not grow (R1) | build | acted | the verdict test puts a fake tsci in the temp project's `node_modules/.bin`, so `find_toolchain` finds it; the verdict stays 3 lines |
| 13 | `dfr0664-tft-2in` is not in the repository, only in the PO's store | plan | acted | a fixture copy; putting it into `parts/` is out of scope |
| 14 | The three builds take 14.1 s together | build | acted | `@slow`, listed in `tests/test_suite_runs.py`; they run in the full run |
| 15 | The converter's TypeScript copies (`board.ts:102,112`, `mapping.ts:94`) still read the key | card | verified | they keep both spellings, so a pad in a trace still maps; out of scope |
| 16 | `printed_label` lost the alias-key lookup: the XIAO's TX and RX are aliases with no `pins` key and no header label, so hints `["TX"]` gave TX, not D6 | PR review, refuter 1 and reviewer SHOULD 3 | acted | verified on the PR head; `known` holds `set(pads.aliases)` again; the XIAO TX, `pin16`+TX and RX cases in `test_breadboard.py`; mutation row |
| 17 | The record validator still read the key raw, so the guard allowed two files | PR review, reviewer SHOULD 1 | acted | the validator reads `BoardPads.from_record(board).aliases`; the guard allows only `scripts/board_pads.py`; boards.py did not grow (the comment of row 18 lost a line); mutation row |
| 18 | The comment at `boards.py:839` said each pad is checked as a name; the loop checks the `pins` and `power_pads` keys | PR review, reviewer SHOULD 2 | acted | verified; reworded to what the checks read |
| 19 | The verdict: a test with one selector per error cannot see a join that keeps only the first; a field that is no list is spelt letter by letter; the detail has no cap | PR review, reviewer SHOULD 4 and refuter 6 | acted | verified (the field case printed `., M, c, u`); a canned error with 2 selectors, a string field and a 2000-character message in `ABrokenTraceIsNamedTest`; `str()` for each, `clean(..., 300)`; 3 mutation rows |
| 20 | P512 opened a gap: the emitter now writes the alias pad into `.Mcu > .%s`, and nothing checked an alias value as a name, so a FireBeetle record with `MISO` → `MI" />` passed `validate()` | fix-commit refuter (MUST) | acted | verified (`validate()` gave `[]`); the P87 name loop in `boards.py` checks each alias pad too (its local `import parts` lives there, so not in `_pad_problems`); `AnAliasIsWrittenAsCodeTest`; mutation row. Row 18's "verified" covered the comment only |
| 21 | The `str()` on each selector in the verdict was untested: `map(str, one)` → `one` survived | fix-commit refuter (SHOULD) | acted | a canned error with `"selectors_not_found": [1, ".Mcu > .SCK"]`; mutation row |
