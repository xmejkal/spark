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
| 11 | a returned wait can put a stage over its limit, and a wait can be set to pass a limit | the flow lens | acted | three of the four W6 rules that the gate does not see (the fourth is row 9's) |
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

## The final review

A code lens on Opus, a documents lens on Sonnet, then the refuter. Its verdict: stands with fixes.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 25 | the card's line "Discovery, Design and Review stay shared" had no test: a gate that counted only spark's cards there passed all 199 tests | the refuter | acted | `test_discovery_design_and_review_are_held_across_both_lanes` and a mutation row |
| 26 | the PR said "Closes #1299", and the card's Done-when asks that the PO's rules say the same totals; that file is his | the refuter | raised | fixed: the PR says "Refs #1299"; the card closes when his rules file holds the totals and the proof is posted |
| 27 | no test pinned that a card that waits on the PO in Review is still asked for its Needed by and its slice | the code lens, confirmed by the refuter | acted | a test and a mutation row |
| 28 | the status's mark on a bench session of the bin that waits was untested, and two docstrings and the status help said that the gate counts such a card | the code lens, confirmed by the refuter | acted | the test holds the bench card; the docstrings and the help say what the gate does |
| 29 | W6 did not say which card "the newest" is; on the same day the gate names the later card in the board's order, not the higher number | the documents lens; the refuter ran the tie | acted | W6 says the latest Waiting since, an undated wait as the latest, and the board's order on the same day |
| 30 | W6's first sentence read as if Build were no working stage | the documents lens, confirmed by the refuter | acted | "Discovery, Design and Review each hold two cards" |
| 31 | a session can set a wait on its own card and pull the next one, and the PR's text for the PO did not say so | the refuter | acted | W6 and the PR say it; the gate reads fields, not comments, so no cheap check exists |
| 32 | "the first group of commits can merge alone" held for the tests and the anchors, but the documents of both steps are one commit | the refuter | acted | the PR says so |
| 33 | the PR said "eight literal sentences"; it is the constant and seven | the refuter | acted | the PR's count is corrected |
| 34 | the counting rule stood three lines long under the glossary's "Waiting on" beside W6 and the flow | the documents lens; the refuter kept the numbers in the flow, as the card asks | acted | the glossary holds one clause and a link |
| 35 | two inserted help lines were 270 and 191 characters long | the code lens | acted | wrapped like the lines around them |
| 36 | "the expedite's lane" names a third lane | the documents lens | rejected | the refuter: it is the expedite card's own lane, as in the code; the sentence now says "the lane of the card that carries `expedite`" |
| 37 | a bare "waiting total" can be read as a wait on hardware | the documents lens | rejected | the refuter: every use follows a sentence that names the PO |
| 38 | old row names and test comments say "the lane" for the expedite, and a repeat of `" (%s)" % lane.name` | the code lens | rejected | the refuter: "the expedite lane" is the glossary's own name; row names are the ledger's keys; the repeat is three short uses |
