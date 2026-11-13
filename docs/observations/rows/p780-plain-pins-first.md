# P780: a plain signal takes a bus pin after the plain pins and before a scarce one, and the docs say so: rows

Card: [P780 #1078](https://github.com/xmejkal/spark/issues/1078), from P776's pruning (p330 board walk, row 27). Plan
`~/.claude/plans/p780-plain-pins-first.md` (XS: one plan check, the refuter on Opus 5.5; one PR refuter). The PO's choice,
2026-11-13: "Docs follow the code". This file holds the acted, raised and rejected findings only (rules.md). 2026-11-13.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | row 27 holds: on the T-Display fixture with a button and an LED, `assign_pins.py` put the LED on IO21 (I2C) while IO13, 25 and 32 were free; `_cost` gives IO17 8, IO21 13, IO32 24, IO25 25 | plan, plan refuter | acted | the order is the design's: commit 831f7563 (2026-09-29, P3) chose "plain pins first, then the bus, then anything scarce"; the word "last" in the docs was loose from the start |
| 2 | the PO's choice between the docs following the code and the code following the docs | plan | acted | the PO, 2026-11-13: "Docs follow the code" (asked in the session, the plan check's facts beside each option) |
| 3 | the plan's new tests (1) plain < bus and (2) bus < scarce repeat `ABusIsSpentLastTest` (`tests/test_parts.py:471`), which pins plain < bus < ADC1 through `_cost` (`:548`) and 0 < penalty < `CAPABILITY_COST` (`:520`) | plan refuter | acted | (1) and (2) dropped; the class is renamed `ABusPinComesAfterThePlainPinsTest`, its docstring says the order and that it is the design's |
| 4 | the walk's own case is pinned nowhere | plan | acted | `TheWalksBoardTest.test_the_led_takes_the_i2c_pin_and_leaves_the_wake_and_adc_pins_free`: the T-Display fixture, `{"BUTTON": "IO17", "STATUS_LED": "IO21"}`, IO13, 25 and 32 free |
| 5 | the texts that said "last": the comment and the two role strings in `board_rules.py:57-61`, `boards/xiao-esp32-c6.json:174`, `boards/firebeetle2-esp32s3.json:280`, `commands/build.md:229`, `skills/spark-design/SKILL.md:62` | plan, plan refuter | acted | each says the order: plain, then the buses, then the scarce ones (wake, ADC1); the two anchors of `sprint-3-p3.json` on the role strings re-aimed with their mutants kept |
| 6 | the `pin_assigner.py:81-92` comment's measurement is stale (the plan) | plan | rejected | dropped because the comment already says the order ("a bus, spent after plain pins and before scarce ones"; "a plain signal still takes a bus pin before it wastes an ADC1 pin"), and its 2026-09-29 measurement is history, dated |
| 7 | the board notes' copies in `tests/data/snapshot/*` still say "taken last" | build | rejected | dropped because a snapshot holds a store as it was on its date; rewriting it would make it lie |
| 8 | no golden moves | plan refuter | closed | the design and breadboard and records goldens ran OK with the change (no golden holds a role string or a board note) |
| 9 | the ADC2 side finding: a plain signal takes an ADC1 pin before an ADC2 pin, though ADC1 is the scarcer one with WiFi on | plan, plan refuter | raised | P798 #1120 (Idea, under P794 #1106) |
| 10 | my first test read `a["name"]`; `assign` returns `signal`, `pin`, `gpio`, `why`, `roles` | build | acted | the test reads `a["signal"]` |
