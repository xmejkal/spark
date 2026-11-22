# P984: the needs phase says what is true when the last need was dropped: rows

Card: [P984 #1428](https://github.com/xmejkal/spark/issues/1428). Acted, raised and rejected findings only.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | `--needs-drop` of the last need keeps requirements.json, and the phases said "a hand-written project", which is false | P980 plan check, refuter | acted | `without_needs` reads `needs.FILE`: with it, the needs phase says `NO_NEED_LEFT_MESSAGE` and the parts phase `NO_PICK_BEHIND_MESSAGE`; with no needs file the hand-written sentence stays; flow.md names both |
| 2 | The requirements phase of both states says `NOTHING_TO_COMPARE_MESSAGE`, which is true of both | this build | rejected | it names no origin, so it needs no change |
| 3 | A dropped last need with no requirements.json still says "no needs yet: Claude writes them" | this build | rejected | true: no need is written and Claude may write them |
