# P331 new-board plan: findings rows

The refuter of the plan `docs/discovery/2026-10-19-p331-new-board-works/plan.md` (Opus, 2026-10-19), with the
lenses' checks of the P325 predictions.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | Most of the reused part functions do not work on a board record: `unverified` and `fetch_documents` find no part by its id, `open_questions_of` calls the XIAO settled, `parts.validate` refuses it | refuter, plan | acted | runs on `boards/xiao-esp32-c6.json`; the board kind gets its own finder, reader and validator; the core is L |
| 2 | The store's `boards` place holds the deploy records by MAC, so a board-definition layer there would read them as boards | refuter, plan | acted | `scripts/board_facts.py:64-73`; the plan asks for a new place |
| 3 | The live vendor check refuses a board file that no project owns, so a store board needs an owner rule | refuter, plan | acted | `scripts/check_vendor_pins.py:123`; in the store-place card |
| 4 | Walk 1 is not blocked by the physics could-not-run: the deploy asks only for a passed run, a look and a yes | refuter, plan | acted | `scripts/project_image.py:57-69`; the order says walk 1 runs now |
| 5 | A built-in display cannot be drawn in the Wokwi diagram today, alone or with parts | refuter, plan | acted | `scripts/check_spine.py:508-513, 543-555`; in P332 |
| 6 | A display driver from spark conflicts with "never drivers" unless it is a third-party pinned download, with the PO's yes | refuter, plan | acted | AGENTS.md; in P336 |
| 7 | Refusing a null `wokwi_part_type` would lock out the T-Display everywhere | refuter, plan | acted | honest validation counts it as an open fact instead |
| 8 | The P327 plan's "check_all exits 2 on a board-alone project" is false: `blink-c6` answered ok, exit 0 | architect, plan | verified | a run on `~/Development/blink-c6` (path not in the repo) |
| 9 | The P326 plan's "the second button's name breaks the import check" does not hold: only the constant's name changes | architect, plan | rejected | `scripts/design.py:312` |
