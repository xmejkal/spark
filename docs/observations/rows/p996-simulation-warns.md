# P996: an owed simulation stance is a warning, never a stop: rows

Card: [P996 #1453](https://github.com/xmejkal/spark/issues/1453). The PO, 2026-11-22: "The simulation step should not
stop us if we want and can deploy directly." The plan was written by the session. Its claims were checked in the code
and on a copy of p934-display before the build. This file holds the acted, raised and rejected findings only. 2026-11-22.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | `--requirements` refuses a pick that owes only its simulation stance | the card; on main the copy said `refused, so nothing was written: epaper-2in9-bwr-mh-et-live — owes simulation — …`, exit 1 | acted | `SIMULATION_FACTS`: an owed stance is left out of the refusal test. The pick is written with the line `no simulation stance — <id>: …` and `data.no_simulation_stance`. Rows 1 to 4 of `tests/mutations/p996-simulation-warns.json` |
| 2 | the build may crash on a part with no simulation stance (plan step 3) | the plan | rejected | on the copy, a build from a hand-written file on main and from the written file on the branch gives board, schematic, footprint and build `ok`, and `[????] simulation` with `the chain was NOT exercised — this is not a pass`. No guard needed. The simulation stops at the board here (`the board record names no wokwi_part_type`), not at the e-paper |
| 3 | the page hides Write the parts list for an owed stance (after P993) | the card | acted | with no problems from the rule, the offer stands, and the phase says the stance as a warning (`NO_STANCE_MESSAGE`). Row 5 |
| 4 | /spark:deploy needs a change | the plan, step 5 | rejected | no change: commands/deploy.md step 3 and `deploy.py --no-simulation` ask the person's typed yes for an image that no simulation tested (read, not run: it needs the board on USB) |
| 5 | an existing test pinned `owes body_mm, simulation` as a refusal | the plan | acted | `test_a_pick_that_owes_its_outline_and_a_fact_the_circuit_needs_is_still_refused` now owes `body_mm, footprint`, which is still refused. A new test pins `body_mm, simulation` as written with both warnings |
| 6 | two P97 rows anchor on the `placeholder` line, which now tests the layout facts | `tools/mutate.py --anchors` | acted | re-anchored in `tests/mutations/p97-council.json`, each planted by hand and caught |
