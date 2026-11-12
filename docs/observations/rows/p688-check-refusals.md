# P688: three check scripts answer bad input with a sentence, a code and exit 2: rows

Card: [P688 #926](https://github.com/xmejkal/spark/issues/926), bug, under #94. A chore: a card and the change; one lens and the
refuter on the PR because it adds a code. Built in parallel with P725 (the PO: "anything we can do in parallel"). 2026-11-12.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | `check_bom.py:58`'s `SystemExit` named by the card is gone on main: `order_rows` answers a Refusal and the CLI exits 2 with its sentence (two goldens pin it) | build | acted | nothing to change for the third script |
| 2 | `check_vendor_pins.py missing.json` died in a `FileNotFoundError`; `check_board` now answers could-not-run with `no_board_file`, and every could-not-run result carries `code` beside `reason` for `--json` | build | acted | `vendor_pins_check.could_not_run`, a new code, a golden |
| 3 | `check_footprints.py --json` printed text for a missing circuit, and its rules refusal had no code | build | acted | one JSON refusal shape with `code`, a golden |
| 4 | `check_bom.py` and `check_vendor_pins.py --json` give no envelope (a list, or no `--json` at all): the card's "`--json` gives the envelope" waits for the checks' output slice W6-C2 | build | raised | the W6-C2 card (checks' codes and envelopes) |
| 5 | the JSON contract test pinned a could-not-run entry to `board`, `reason`, `status`; json.md's shape table said the same and named no refusal shape for check_footprints | build | acted | the test and the two json.md lines say `code` |
| 6 | two old rows anchored on the lines that changed (the `wrote` row of p181, the P434 bare-text row) | build | acted | re-aimed at the new lines; `--anchors`: 3161 rows in 265 tables, every anchor present once |
