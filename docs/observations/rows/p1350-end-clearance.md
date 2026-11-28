# P1350: one end rule for the router and its tests: rows

Card: [P1350 #1937](https://github.com/xmejkal/spark/issues/1937). The PO delegated the choice of the rule (4 spots or
8); the council chose 4 spots, as a distance in px, by 2 of 3 on 2026-11-28 at 10:50 CET. This file holds the acted,
raised and rejected findings only. Written 2026-11-28 11:07 CET.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | Measured from the hole's px, the XIAO's 3 off-grid rail ends would get new rings and routes would move | plan council, refuter | acted | `rings` measures from the end's cell centre, `self.grid.point((u, v))`. S1's run: the points of every step of every fixture are equal on main and on the branch; taken and expanded too |
| 2 | On P1334 the e-paper pin moves under either rule | plan council | acted | S1's run on p1334-firebeetle-rows with the router diff: dashed {4, 6, 11, 12}, no search cut short. That pin moves in P1334's rebase, not here |
| 3 | The router and the routes test measure the XIAO's 3 off-grid rail ends from different points (the cell and the hole, about 2 px apart) | plan council | raised | a card of its own, which the lead files: one point for both, with every crossing a pitch from an end |
| 4 | One pitch of space (the bare 2 in `_band_full`, `_moves`, `_estimate`) stays unnamed | plan council | raised | destination P1194 #1740 (settings in layers) |
| 5 | `_estimate` counts 3 bends where 1 is enough | plan council | raised | a card of its own, which the lead files |
| 6 | The goal-leg check | plan | rejected | dropped because S1 shows no search cut short |
| 7 | Row 3 of the plan's mutation rows (`<` to `<=`) | plan council | rejected | dropped because no case lies exactly at 5.8 px without a float doubt |
| 8 | The dashed note wrote "4" a second time | plan | acted | `DASHED_NOTE` reads `TrackRouting.MAX_BENDS`; the three literal tests stay green unchanged |
| 9 | The old routes test flagged the diagonals | council | acted | by the delegated choice the diagonal holes are no longer kept clear; the dissent (1 px of white is thin once scaled or printed) stays the risk; `END_CLEARANCE_PX` 6.8 or more gives 8 spots |
