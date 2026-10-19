# P330 board walk: findings rows

The walk that adds the PO's TTGO T-Display to spark as a board record (#423), and its plan council (2026-10-19).

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The store has no place for a board definition: boards are read from a project's `boards/` and spark's library, and the store's `boards` folder holds deployed boards by MAC | walk, plan | verified | `scripts/store.py:79-81`; the record goes into a walk project for now |
| 2 | `boards.py --validate` fails before `init_project.py --board` writes `boards/active.json` | refuter, plan | acted | `scripts/boards.py:535`, reproduced on a scratch copy (exit 1); the plan runs init first |
| 3 | `parts.py --keep` keeps a board's document too, but takes a local file and prints a `documents` entry to paste by hand | refuter, plan | raised | `scripts/parts.py:1817-1825`; to try in step 5 |
| 4 | Validation checks only that the nine required keys exist, so a null `wokwi_part_type` and an empty `physical` pass | refuter, plan | raised | `scripts/boards.py:62-63, 353-355`; to try in step 8 |
| 5 | A record cannot say a pin is input-only, and strapping pins are not refused, so the pin assigner can put an output on GPIO 34-39 | tech lead, plan | raised | `scripts/boards.py:95-111`, `scripts/assign_pins.py:129-134`; to try in step 10 |
| 6 | A record cannot say which pins the board itself uses, like the display's | refuter, plan | raised | only `onboard_led` and `onboard_button` (`scripts/boards.py:97-98`) |
| 7 | `/spark:identify` is for modules and cannot run `boards.py` | PO and UX lens, plan | raised | `commands/identify.md:3`; to try in step 1 |
