# P468 the serial warning reads a board fact: rows

What the P468 plan, its two council rounds and the build found. Card: #636. The FireBeetle part is not in this card.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | `check_spine.py` prints the "no serial monitor" warning when `simulation_detail(..., serial=False)`; both callers passed `serial_wired(diagram)` | plan | verified | read in the code; both now pass `serial_heard(diagram, board)` |
| 2 | `serial_wired` reads only the diagram's `$serialMonitor` ends | plan | verified | `serial_heard` is `serial_wired` or the record's `serial_without_wires` being True |
| 3 | `boards.py` does not change (R1 baseline) | plan | verified | `read_simulated_part` reads pins only; the record is read as a plain dict key |
| 4 | `check_spine.py` is at its R1 baseline (1030 lines), so the change is net 0 lines | round 2 | acted | the new function is paid for by two shortened comments and one docstring; the baseline is untouched |
| 5 | The XIAO's `serialInterface` is a gate | round 2 | verified | the kept Wokwi definition (sha256 e5200e01...856a8, read from the store, read only) holds `mcuAttrs.serialInterface: "USB_SERIAL_JTAG"` |
| 6 | `boards/README.md` lists the field as an observation or a definition fact, not behaviour | round 2 | acted | section "Serial without wires" |
| 7 | One `board_alone` test, and a fifth mutation row for a board with no property | round 2 | acted | `tests/test_check_spine.py`; `tests/mutations/p468-serial-warning.json` has 5 rows |
| 8 | Refuter, round 1: walk 2 and walk 3 ran on wokwi-cli 0.27.1, and `commands/build.md` says 0.28.0 stopped wiring the serial monitor by default; the S3 devkit sets no `serialInterface`, so on 0.28.0 the FireBeetle's warning may be true | refuter | acted | this card ships the mechanism and the XIAO only |
| 9 | The FireBeetle's `serial_without_wires` (walk 3 matched `ready` with no connections, on 0.27.1) | refuter, lead | raised | waits for a run on wokwi-cli 0.28.0 and the PO's yes (it changes his installed tool) |
| 10 | `run_scenario.py:432-433` still asks about `$serialMonitor` wires when a run hears nothing, even for a board whose record says it needs none | lead | raised | wording to reconsider with the 0.28.0 run |
| 11 | The plan named the field `serial_without_wires`, since the code says serial (`serial_wired`, `serial_heard`) | lead | acted | used as named |
| 12 | The plan's mutation anchor count: 119 refused on main | brief | verified | 120 refused on main, counted with this table present and again with it stashed; the same 120 with the change |
| 13 | The warning's comment names the record fact | brief | rejected | `tests/mutations/p190-serial.json` anchors that comment line verbatim; changing it makes a new refused anchor. The fact is named in `serial_heard`'s docstring |
| 14 | Main refuses one more mutation row than before (120, not 119) | lead | acted | P487 (#675) changed the tally hint in `parts.py:2282`, and the `p97-cost` row "an unbuilt project is not said to be" lost its anchor; the row follows the text |
