# P792 the full build wires a stand-in board's own LED and button: rows

Card: [P792 #1100](https://github.com/xmejkal/spark/issues/1100), XS to S. Plan `~/.claude/plans/synthetic-purring-sky.md`. Rows 1 to 10 are
the plan refuter (Opus), 11 the implementer. 2026-11-16.

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
