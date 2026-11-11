# P769 the DFR0457 shelf record takes the walk's upgrades: rows

Card: [P769 #1060](https://github.com/xmejkal/spark/issues/1060), chore, S, under P735. The record is the PO's store
data (`<store>/shelf/dfr0457-mosfet-power-controller.json`), so this PR holds the rows and the PR body holds the diff.
Rows 1 to 4 are the implementer, 5 and 6 the PR reviewer (Sonnet). 2026-11-12.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the shelf record took six upgrades from the walk copy: `cites` on the ten schematic facts, `legs`, the "Switch DC only" line, `title` and `version` on the schematic and the drawing, and `mounting_holes` sourced to the wiki table with the drawing cited | implementer | acted | each value was asserted equal to the store's before a `cites` was added. `parts.py --show` prints the legs and the line, `--unverified` and `--validate` exit 0 |
| 2 | the walk copy also carries its notes, its `why_it_matters` texts and the irrigation wording ("valve") that P745 removed | implementer | rejected | out of the card. Only the six upgrades moved, and a check refused any of "valve", "irrigat", "ESP32-S3" in what moved |
| 3 | the walk kept a seventh document, the wiki's pinout picture (`06da2b51…-0x0`), that no `cites` names | implementer | rejected | not in the card, and the record's prose already names the picture's URL where it needs it |
| 4 | `legs.SIGNAL` says "the green wire of the Gravity cable", a wire colour that no document gives (walk diary line 67) | implementer | raised | the store record already says it in `pin_order_proof` and `host_requirements`. A later card sources the colours or drops them from all three |
| 5 | `off_state_current_ua`'s cite names the schematic page, but its 1 uA is the MOSFET's IDSS, a datasheet value | PR reviewer (Sonnet) | acted | the `at` says the sheet shows that no path conducts, and that the 1 uA is the HM70P04K's IDSS, which the page does not give |
| 6 | `vcc_pin_current_ma`'s cite at "P1 pin 2 VCC at grid B2" shows no current | PR reviewer (Sonnet) | rejected | the 0 mA follows from that stub pin, and the fact's `why_it_matters` says so: the cite points at its evidence |
