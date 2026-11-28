# P1350: one end rule for the router and its tests: rows

Card: [P1350 #1937](https://github.com/xmejkal/spark/issues/1937). The PO delegated the choice of the rule (4 spots or
8); the council chose 4 spots, as a distance in px, by 2 of 3 on 2026-11-28 at 10:50 CET. This file holds the acted,
raised and rejected findings only. Written 2026-11-28 11:07 CET.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | Measured from the hole's px, the XIAO's 3 off-grid rail ends would get new rings and routes would move | plan council, refuter | acted | `rings` measures from the end's cell centre, `self.grid.point((u, v))`. S1's run: the points of every step of every fixture are equal on main and on the branch; taken and expanded too |
| 2 | On P1334 the e-paper pin moves under either rule | plan council | acted | S1's run on p1334-firebeetle-rows with the router diff: dashed {4, 6, 11, 12}, no search cut short. That pin moves in P1334's rebase, not here |
| 3 | The router and the routes test measure the XIAO's 3 off-grid rail ends from different points (the cell and the hole, about 2 px apart) | plan council | raised | [P1353 #1940](https://github.com/xmejkal/spark/issues/1940): one point for both, with every crossing a pitch from an end |
| 4 | One pitch of space (the bare 2 in `_band_full`, `_moves`, `_estimate`) stays unnamed | plan council | raised | destination P1194 #1740 (settings in layers) |
| 5 | `_estimate` counts 3 bends where 1 is enough | plan council | raised | [P1351 #1938](https://github.com/xmejkal/spark/issues/1938), narrowed to the cell beside the goal |
| 6 | The goal-leg check | plan | rejected | dropped because S1 shows no search cut short |
| 7 | Row 3 of the plan's mutation rows (`<` to `<=`) | plan council | rejected | dropped because no case lies exactly at 5.8 px without a float doubt |
| 8 | The dashed note wrote "4" a second time | plan | acted | `DASHED_NOTE` reads `TrackRouting.MAX_BENDS`; the three literal tests stay green unchanged |
| 9 | The old routes test flagged the diagonals | council | acted | by the delegated choice the diagonal holes are no longer kept clear; the dissent (1 px of white is thin once scaled or printed) stays the risk; `END_CLEARANCE_PX` 6.8 or more gives 8 spots |
| 10 | The rows file named no card for rows 3 and 5 | PR review, lens | acted | P1353 #1940 and P1351 #1938 named (2026-11-28 11:18 CET) |
| 11 | The agents' page said the wire keeps off "the 4 holes" beside an end; the ring cells are track spots, not holes. Its sentence was about 200 characters | PR review, refuter and lens | acted | rewritten in short sentences: the 4 track spots half a pitch beside the end, `END_CLEARANCE_PX` (5.8 px) |
| 12 | The agents' page said no wire comes closer than 5.8 px to another end, but a dashed wire's last try may | PR review, refuter | acted | the page says a dashed wire may pass beside another wire's end on its last try |
| 13 | `test_the_dashed_note_names_the_router_s_most_bends` builds its expected words from `MAX_BENDS` itself, so it cannot fail | PR review, refuter | acted | removed; the three literal note tests pin the words at 4 |
| 14 | `TrackRouting.__init__` nested 4 deep (rule R2), so the first push's hook failed | push hook | acted | the ring of one end is the method `_ring`; the mutation row's find follows its line |
| 15 | The `Search` comment ran past 120 characters | PR review, lens | acted | wrapped |
| 16 | `END_CLEARANCE_PX`'s comment is inline, not a `#:` line like its neighbours | PR review, lens | rejected | dropped because the three mutation rows anchor on that whole line; a style change is not worth moving them |
