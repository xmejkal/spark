# P333: one board on two USB nodes is one board, findings rows

Findings from the plan council, the build and the review of P333 (2026-10-26, Prague, auto mode).

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | One USB serial means one board | plan | acted | not alone: clones share a serial (CP2102 `0001`). The council asked for serial, USB id and product. The refuter showed that two Linux clones (`/dev/ttyUSB0`, `/dev/ttyUSB1`, serial `0001`) still grouped, so a group now also needs a node whose name ends with the serial, as macOS names a CP2104. Test `test_two_clones_with_one_serial_and_no_node_named_by_it_stay_two_boards` |
| 2 | The look need not name the other node | plan | rejected | a deploy erases through the look's port, so the look carries `also_on` and says "If these are two boards, unplug one" |
| 3 | The chosen node is the first by sorted name | plan | rejected | sorting puts COM10 before COM3, and `in` matched a short serial inside another name. The node named by the serial (`endswith`) is chosen |
| 4 | The fixture may use the PO's board serial | plan | rejected | a made-up serial `01A2B3C4`, and the product as mpremote prints it, "Silicon Labs CP2104 ..." (refuter) |
| 5 | `only_port` is still needed | build | closed | no caller left after the look read the Port itself. Removed |
| 6 | `also_on: []` with `--port` is honest | review | acted | the finder is not asked then, so `also_on` is null, as AGENTS.md's "a null is not a value" asks |
| 7 | The port line's sentence is tested | review, refuter | acted | no test read it, and a planted removal passed. `test_the_look_says_the_other_node_and_to_unplug_one_if_they_are_two_boards` reads it |
| 8 | `PortFinder.boards()` returns boards | review | acted | it returns device nodes, beside the new `boards_of`. Renamed `nodes()` (board_doctor, two tests) |
| 9 | Grouping should take at most two rows | review | rejected | two Linux clones are two rows too. The serial-named node is the rule that tells them apart (row 1) |
| 10 | The `--port` help still fits | review | acted | look, live, reach and grant say "(one board on two nodes named by its serial counts once)" |
| 11 | `developing.md` counts 13 goldens | refuter | acted | 14 now |
| 12 | Each new test fails on main | refuter | rejected | the `--port` test passes on main: it guards a regression, and the two `boards_of` tests error on main because the function is new |
| 13 | `live.py` and `reach.py` show `also_on` | review | raised | they do not erase, so the risk is low. A later bench slice (S7a) can print it |
| 14 | The other node works for esptool and mpremote | build | raised | not run: only `/dev/cu.usbserial-<serial>` was read on the bench (2026-10-26). The PO's bench can try `/dev/cu.SLAB_USBtoUART` |
| 15 | The mutation run catches every planted defect | mutation-tester | acted | first run 13 planted, 9 caught: tests for another USB id, another product, a name that only holds the serial, and the port line. Second run 14 planted, 12 caught. `none-serials-grouped`: a node named `...-None` now has a test, and a rerun caught it (352 s) |
| 16 | `fallback-last` is a real defect | mutation-tester | rejected | an equivalent mutant: a board with more than one node always has a node named by its serial, so the fallback only sees one-node boards, where first and last are one node. The row was dropped from the table |
