# P505 mask the board address: rows

What the P505 fix (card #694) found. The P498 docs council (PR #688) raised it.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | One bench board's full address sat in 4 docs/observations files | P498 writer, row 48 | verified | it sat in 10 lines of 10 files under docs/observations and docs/discovery; all now read `8c:bf:ea:xx:xx:xx` (or the dash form) |
| 2 | The tests used only made-up addresses | lead | rejected | three Espressif-prefixed addresses sat in tests/test_board_doctor.py, tests/test_deploy_record_store.py and tests/test_board_start.py; they map to made-up `8c:bf:ea:00:00:0N`, in both separated and unseparated spellings (a USB serial match needs the second) |
| 3 | A test can name the real address to catch it | plan check | rejected | naming it would leak it; `tests/test_no_board_address.py` fails on any full address that is neither masked nor made up |
| 4 | The guard catches every spelling | lead | raised | it checks separated forms only; an unseparated serial is not checked (none is left in the tree today, counted without printing) |
| 5 | The old commit 958e51d2 is in scope | the PO, 2026-11-01 | rejected | the PO decided that commit stays in history; this card covers today's files only |
| 6 | The XS rule's plan check ran | lead | rejected | folded into the PR refuter for a mechanical change, as for P496 and P499 |
