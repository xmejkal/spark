# P723: a check_spine test gets a fake build engine, and a new project's package.json names project_setup: rows

Card: [P723 #979](https://github.com/xmejkal/spark/issues/979), a chore under #94 (v0.13, one core), two findings of P705's refuter. A chore:
the card and the change, no plan (rules.md); one PR refuter on the best model. This file holds the acted, raised and rejected findings only.
2026-11-12.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | `test_a_converter_that_fails_beside_a_copied_diagram_fails_the_stage` built with `board_engine.find_toolchain(ROOT)`: on a machine with `tsci` on PATH it ran the real tool | the card (P705's refuter) | acted | `BuildService(FakeTscircuitEngine(circuit=...), BoardEmitter(assume_missing_sizes=True))`: the P706 fake writes a circuit that passes the build stage (one `pcb_trace`, the MCU grounded, its 3V3 on net V33, the supply claim of the fixture), so the faked converter is what fails; `[{"type": "pcb_trace"}]` alone stopped at the build stage with "Mcu.3V3 is fed by net.V33 in this design and is not on it" |
| 2 | `project_setup.py:384` wrote "see init_project.PINNED_TSCI and PINNED_CORE" into every new project's `package.json`; the pins live in `project_setup` since P705 (`:360`, `:364`) | the card (P705's refuter) | acted | the sentence names `project_setup`; no test or golden pinned the old words (grep of tests/ and tests/golden*) |
| 3 | no logic changes: no mutation row; `--anchors` over all tables | build | closed | 3170 mutation(s) in 269 table(s): every anchor present, once |
| 4 | nothing pinned the new `//` sentence either, so the card's "with its golden or test updated" had nothing to update | PR refuter | acted | `test_a_package_file_is_written_so_tscircuit_stops_its_walk_at_the_project` asserts the sentence names `project_setup` |
| 5 | the inline circuit is no copy of the file's two `circuit()` helpers (`:149`, `:225`: a Module with no 3V3 feed; a V5V pin, no pcb_trace), neither passes this fixture's build stage | PR refuter | closed | the inline list stays; a shared minimal passing circuit in fakes.py is a later thought, not a card |
