# P1012: /spark:idea says that a bench result writes host_requirements: rows

Card: [P1012 #1471](https://github.com/xmejkal/spark/issues/1471). Seen in the p934-display2 walk, 2026-11-22 13:14
CET. Docs only: the review was one refuter on Opus. This file holds the acted, raised and rejected findings only.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | `--fact-set` cannot change a record's host notes | the card | rejected | the council's check: `--fact-set` writes `host_requirements` and `legs` since P741 (set_facts.py:4). Only /spark:idea did not say so |
| 2 | /spark:idea's fact section names neither `host_requirements` nor `legs` | the council | acted | commands/idea.md says both, with their shapes |
| 3 | the `legs` sentence gives no shape and no merge rule | PR refuter 1 | acted | fixed: {pin of `pin_order`: how to tell that leg apart}, merged leg by leg |
| 4 | "replaced as a whole" does not say to copy the lines that still hold | PR refuter 2 | acted | fixed |
| 5 | "the driver that draws" is unclear | PR refuter | acted | fixed: the driver whose picture shows on the screen |
| 6 | the PO's own e-paper record still names the SSD1675/SSD1680 driver | the walk, row 15 | raised | a store change he did not order: it waits for his yes |
