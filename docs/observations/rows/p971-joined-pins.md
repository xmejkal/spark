# P971: the pin assigner treats a board's joined pads as one pin: rows

Card: [P971 #1392](https://github.com/xmejkal/spark/issues/1392). Acted, raised and rejected findings only.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | On today's records a joined pair on one GPIO is already one pin, so the change guards joined pads on different GPIOs | plan check, refuter | acted | `JoinedPins` adds the GPIOs of the whole group at every mark; the pin map of the p934 walk is unchanged |
| 2 | The taken tests could read `holds(label) & taken_gpio`, and two mutation rows would then be equivalent | plan check, refuter | rejected | with every mark adding the group, the tests stay `gpio in taken_gpio`; the two rows are dropped |
| 3 | A board_rules rule (the labelled pads of a group share one GPIO) is the other option | plan check, refuter | rejected | not taken: the card's words ask the assigner to treat the group as one pin |
| 4 | The refusal blamed the join when two signals named one label, or an unjoined label on the same GPIO took the pin first | the refuter, PR #1434 | acted | `said` names the group only when a label of another pad of the same group was placed; three tests; two mutation rows |
| 5 | The `len(names) < 2` check in `said` had no test | the refuter, PR #1434 | acted | the check is gone: the rule "a placed label of another pad of the group" covers a group with a pad the board has no pin for, and a test says so |
