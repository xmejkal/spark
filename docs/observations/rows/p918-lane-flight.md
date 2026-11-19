# P918: the gate counts the cards in flight per lane, and a card that waits on the PO counts apart: rows

Card: [P918 #1299](https://github.com/xmejkal/spark/issues/1299), with the first slice of
[P928 #1313](https://github.com/xmejkal/spark/issues/1313). The plan: the `architect` agent on Fable. The plan council:
three lenses on Opus (architecture, flow, interface) and the refuter last, then a second round by the refuter alone,
who built the change on a copy of the tree. This file holds the acted, raised and rejected findings only (rules.md).
2026-11-19.

## The plan council

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the plan's board was stale: the PO closed P924 at 11:46 Prague, Review held one card, and the question of the expedite for this PR was gone | the refuter, round 1 | acted | the board was read again at 11:48; the plan dropped the question |
| 2 | "the tests stay green after the `Lane` record" was false: three asserts compared the lane to a string | the architecture lens | acted | `lane_of` returns the `Lane`; the three asserts compare `.name`, changed on purpose |
| 3 | a bin card on a sound slice would fly in the sound lane, against the plan's diagram | the architecture lens | acted | one line in `lane_of`, a test with a bin card on `pixel-games`, a mutation row |
| 4 | the waiting total would take the expedite's extra place if it reused `over()` | the architecture lens | acted | a plain count; a test and a row "the waiting total takes the expedite's place" |
| 5 | the plan's lists of pinned tests and mutation rows were short | the architecture lens, confirmed by the refuter | acted | `tools/mutate.py --anchors` decided: 28 rows moved in step 1 and 11 in step 2 |
| 6 | a frozen `Lane` with a dict of limits is not frozen: the dict can be changed and the record cannot be hashed | the refuter, round 2 | acted | `limits` is a tuple of pairs |
| 7 | the new sentences used a second form for the lane | the interface lens | acted | one constant, `HOLDS`, for every limit sentence: `In flight (spark) holds 5 (…) — its limit is 4` |
| 8 | "ask him for the oldest" does not work in auto mode, and a card moved to Idea looks like plain backlog | the interface lens and the flow lens | acted | the newest card goes back to Idea with its wait kept and a comment that names its stage |
| 9 | the plan dropped the age rule, and the PO's words are "not to leave it get stale" | the flow lens | acted | W6 names the three days and the repeat in every reply; no failure by the calendar |
| 10 | the design raises how many cards can stand in the working stages, and the accepted answer said "no higher total" | the flow lens; the refuter read it as inside the PO's yes | acted | W6 and the PR say the rise plainly: six and four standing, four and two in work |
| 11 | a returned wait can put a stage over its limit, and a wait can be set to pass a limit | the flow lens | acted | three W6 rules that the gate does not see |
| 12 | two of the plan's three measures cannot be counted from what exists | the flow lens | acted | W6 names two measures read from the day closes |
| 13 | the plan's value proof for the waiting slice also passed with the flight per lane alone | the refuter, round 2 | acted | a board that only the waiting total passes: `test_the_board_that_only_the_waiting_total_passes` |
| 14 | "the cap on the open questions to the PO is 4" was false: a wait in Idea or Ready has no cap | the refuter, round 2 | acted | the sentence is gone from the plan and is in no document |
| 15 | `--help` named no slice of the sound lane | the interface lens | acted | `--help` names the slices, the flight and the waiting total per lane, filled from `LANES` |
| 16 | "lane" still meant the expedite in `board.py` and in six comments | the architecture lens, the interface lens | acted | `_flight_marks`; the comments say "the expedite"; a glossary entry "Lane" |
| 17 | the day close prints the flight line too, and its help did not name the mark | the refuter, round 2 | acted | `CLOSE_HELP`, `STATUS_HELP` and `scrum/README.md` name it; a test of the close's body |
| 18 | a broken limit of the sound lane fails spark's pushes, and the sound session does not see it: no pixel-games clone runs the gate, and the session-start hook prints the status in two folders | the interface lens, the flow lens, the refuter | raised | a card: [P930 #1316](https://github.com/xmejkal/spark/issues/1316); W6 names the gap |
| 19 | later slices: the mark for a started card, an age rule with teeth, waits on hardware and outside, the status heading over every wait, the past date in `TRIAL_CHECK`, the slice name `desk lane` | the plan, the flow lens, the interface lens | raised | a line on the card P928 #1313 |
| 20 | split `problems()` into two phases | the architecture lens | rejected | the refuter: the one loop already walks both boards; a fuzz over 20,000 boards found no difference between the old flight and the new |
| 21 | drop a waiting card from the status's flight line | the architecture lens | rejected | the refuter: the waits line shows neither the stage nor the days there; the card is marked |
| 22 | let the branch's own gate pass the card into Review | an option the session asked about | rejected | the flow lens: it grades the change by its own unmerged rule; the question fell away with row 1 |
| 23 | a "places" line in the status | the interface lens | rejected | dropped because only spark's sessions see the status today; it goes with P930 |

## The build

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 24 | the session's own check of the new mutation rows said "escaped: 0" on a copy of the tree whose tests failed with no row planted | the session, by a control run | acted | the copy was built from the tracked files, the control passed, and the rows were planted again; a line in the learned rules |
