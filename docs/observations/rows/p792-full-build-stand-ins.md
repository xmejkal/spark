# P792 the full build wires a stand-in board's own LED and button: rows

Card: [P792 #1100](https://github.com/xmejkal/spark/issues/1100), XS to S. Plan `~/.claude/plans/synthetic-purring-sky.md`. Rows 1 to 10 are
the plan refuter (Opus), 11 and 12 the implementer, 13 to 18 the PR refuter (Opus). 2026-11-16.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | with stand-ins, every FireBeetle full build has 4 wires, so `wires_in == 0` never reports DIAGRAM_UNWIRED for a project whose parts got no wire | plan refuter (Opus) | acted | fixed: `wires_in(diagram, apart)` leaves out the stand-ins; test `test_wires_to_the_stand_ins_alone_are_still_the_unwired_diagram`; mutation rows 4 and 5 |
| 2 | "every part is skipped ... so the diagram holds the board alone" is untrue once stand-ins are wired (build_service, check_spine, commands/build.md) | plan refuter (Opus) | acted | fixed: "so the diagram holds none of the project's parts" in all three |
| 3 | the plan's filter of a stand-in on a GPIO the project took is not needed: the real board's LED and button stay on those GPIOs | plan refuter (Opus) | acted | fixed: no filter; the pick and both builds say the same, and the plan's "not in this card" item is gone |
| 4 | test_check_spine's full-build tests do not use tests/fake_converter.py; five line numbers in the plan were wrong | plan refuter (Opus) | acted | fixed: the tests live in test_build_service with its converter shim; the plan's lines corrected |
| 5 | needs.py, onboard_parts.py (module, OnboardPartReader), commands/build.md and scripts.md also describe stand-ins for the board-only build only | plan refuter (Opus) | acted | fixed in the PR |
| 6 | the converter's name clash must compare lowercased names, as the emitter's part id is the name in lower case | plan refuter (Opus) | acted | fixed: `addNetlist` compares lower case; test with `Onboard_Led` |
| 7 | the bundle ignores an unknown flag, so a project's own older converter wires no stand-in without an error | plan refuter (Opus) | rejected | confirmed, not a defect of the plan: the read-back (`wired_in`) and NOT_WIRED_BY_OLDER_CONVERTER handle it |
| 8 | the board pin is the hub and the board is matched by name; two nets on GND.1 convert | plan refuter (Opus) | rejected | its bundle run: exit 0, 4 parts, 8 wires, 5 of 5 nets |
| 9 | only check-spine-ok.json and -keep.txt change among the goldens | plan refuter (Opus) | rejected | confirmed by the accept run: those two files only |
| 10 | a part-id check is not a press: a free CI Wokwi run would prove the press itself | plan refuter (Opus) | raised | dropped because the card's "a scenario presses" is met at the part-id level without a Wokwi run, as P480's test does; a free CI run is the PO's call |
| 11 | a TypeScript mutation row is caught by the stale sha256 test, whatever the converter's tests say | implementer | acted | no TS row in tests/mutations/p792-full-build-stand-ins.json; `bun test` (53) guards `addNetlist` |
| 12 | the first push failed R1 (`_simulation` 55 lines, limit 40) and T1 (file writes in build_service.py 7 to 8) | implementer | acted | fixed: `board_alone_input.OnboardStandIns` and `StandInsFound` hold the stand-in logic, `BuildService._sim_folder` fills `sim/` in one write loop; mutation row 9 added with its test |
| 13 | the look (`image_evidence.find_limits`) still says no stand-in is wired for a design with parts, so the look and the full build disagree | PR refuter (Opus) | acted | fixed: `limits_of_board(design.board, None, None)` always; test_image_evidence's test says the stand-in is wired with parts or without |
| 14 | `board_engine.convert`'s docstring names only `--circuit` and `--netlist` | PR refuter (Opus) | acted | fixed: it names `--add-netlist` |
| 15 | a person's hand-added part with a stand-in's id is overwritten by the merge with no warning (merge.ts matches by id), and the older-converter note then says "no stand-in" when one is missing | PR refuter (Opus) | raised | the merge: card [P830 #1189](https://github.com/xmejkal/spark/issues/1189); the note: fixed, it names the missing roles |
| 16 | the fake converter adds the stand-in parts but no wires, so the golden's "4 wire(s)" shows the sentences, not the wiring | PR refuter (Opus) | raised | dropped because the -keep golden shows both parts in `sim/diagram.json` and the limits sentences, and tests/test_converter.py proves the wires on the real bundle |
| 17 | a blank line is missing before the new test in tests/test_converter.py | PR refuter (Opus) | acted | fixed |
| 18 | the bundle and its sha256 match the sources, `addNetlist` maps ids, `--check` holds, a kept diagram from before P792 merges, the 9 rows each name a fault a test catches | PR refuter (Opus) | rejected | its own runs: bundle byte-identical, 53 TS tests, 131 Python tests OK |
