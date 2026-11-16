# P860: a net that a powered part drives is no supply from off the board: rows

Card: [P860 #1226](https://github.com/xmejkal/spark/issues/1226). Found in P711's walk 1 (2026-11-16, at the bench).
The PO was in auto mode and said "master po ans tech lead and architect decide f for me". A council put P860 at the
top of Ready. The plan check: one refuter (Opus) on the plan, outside plan mode, because the PO was away. This file
holds the acted, raised and rejected findings only (rules.md). 2026-11-16.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the architect and the tech lead: take away `power_rails.rails_driven_by()` from the supplies | council, architect and tech lead | rejected | the power inlet's VCC is `out` on the motor rail, and its supply truly comes from off the board (`tests/test_breadboard.py`, the motor test); `rails_made_on_board()` counts only a part that also draws power |
| 2 | R2: a ground with no `direction` counts as a power input, so a battery holder with VCC out and a bare GND is called made on the board | plan, refuter | acted | only a non-ground input counts; a test case with a bare GND |
| 3 | R6: the fixture's `circuit.json` is 426 KB and its README says it holds only the parts, ports, traces and nets | plan, refuter | acted | trimmed to the `source_*` elements (86 of 458, 32 KB), as the motor fixture holds |
| 4 | R3: `sheet._supplies` can read the steps' `StepPoint.supply`, which leaves one decision | plan, refuter | rejected | both places call the one predicate `wiring_steps.off_board_supplies()`, so the decision is in one place; the supplies also need their users, which `StepPoint.supply` does not hold |
| 5 | R5: the plan's brief said no code was changed, but the failing test was already written | plan, refuter | acted | the brief was wrong; the test was written first on purpose (it fails without the fix) |
| 6 | L1: `rails_made_on_board`'s docstring blurs it with `rails_driven_by` | PR review, lens | acted | it says "the nets `rails_driven_by` lists, less those of a part with no power input on this board" |
| 7 | L2: `points()` still says a lone named net is a supply from off the board | PR review, lens | acted | "unless a part makes that net (`off_board_supplies`)" |
| 8 | L3: the plan's check that the speaker terminal's pins do not look like a supply has no row | PR review, lens | acted | `test_the_speaker_terminal_is_still_wired_to_the_amplifier` pins its two jumpers, and no supply step names its nets |
| 9 | R5: a made net's `StepPoint.supply` became `""` where it was `None` | PR review, refuter | acted | it is `None` again; every reader tests for empty, so no output changed |
| 10 | the hook: `docs/guide/map.md` was stale, because `tests/test_breadboard.py` now imports `power_rails` | build | acted | `tools/map.py --write` |
