# P1352: the perfboard step's discovery: rows

Card: [P1352 #1939](https://github.com/xmejkal/spark/issues/1939). Four lenses on Opus (PO assistant, user, tech lead, architecture), then the refuter on Opus twice (council/refuter.md). This file holds the acted, raised and rejected findings only. The full verdicts are in the discovery's verification.md. 2026-11-28.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the first slice skips the only observed account (P1039 D11, the clock and the bin), and P1074 #1575 is missing from the frame | refuter 1 | acted | the frame lists P1074 #1575; option D-q6 (d); the PO chose the spike first (D5, D6) |
| 2 | the join seam (★C12) is weaker than it reads, and the lenses split on it | refuter 1 | acted | ★C12 rewritten; verification.md's Agree / split names the split for the design |
| 3 | the ConnectedGroups card is not byte-neutral: the check's public codes change for agents | refuter 1 | acted | items.md item 1 names the codes and docs/guide/agents/scripts.md:219-220 |
| 4 | the build's time is not measured | refuter 1 | acted | assumption A11 with a pass line |
| 5 | "9 of 9 goldens" reads stronger than it is: at most 5 draw a placement or a route | refuter 1 | acted | A4, A6 and item 1 say "at most 5" |
| 6 | ★C9, ★C11, ★C21 and ten more claims hold only in part | refuter 1 | acted | each rewritten with the refuter's narrower words; verification.md |
| 7 | D-d, D-a and D-q5 (a) are stretched past their sources | refuter 1 | acted | D-d names the team's bulk-approved text; D-a carries Q2; D-q5 (a)'s caveat names P1199 D7 |
| 8 | readiness "design" breaks the brief's own rule, because D5 chose a test before an option | refuter 2 | acted | Ready for: an experiment, the clock spike P1074 |
| 9 | D4, D5, D6, D12 and D3 say more than the options he picked | refuter 2 | acted | each D narrowed to his option; D16 later settled D4's scope |
| 10 | A2 is met by D7 but still open; items.md's depends-on lines are stale | refuter 2 | acted | A2 retired with a Results row; items.md updated |
| 11 | D13 answers half of Q9, and "like a page" has a rival reading | refuter 2 | acted | Q9 marked half answered; D13 carries both readings, ★C8's caveat says how another person turns it is unknown |
| 12 | the 2.0 mm JST PH speaker terminal does not fit a 2.54 mm grid | spark-artifact's canvas round | raised | P1359 [#1949](https://github.com/xmejkal/spark/issues/1949), the text plan refuses it or offers a 2.54 mm terminal (brief.md C28) |
| 13 | the free hole between nets cannot hold where a wire leaves a header pin | spark-artifact's canvas round | raised | P1239 [#1792](https://github.com/xmejkal/spark/issues/1792), the join router spike (brief.md C28) |
| 14 | the README is stale: filing, button-light, D15 to D22 missing, "no design and no refactor" too strong | refuter 3 | acted | README table, diagram and next steps updated |
| 15 | button-light stays the example after D20 and D21 | refuter 3 | acted | the story map, the journey, A3, A5, A8, A11, the Hand-off and P1360's line name the console |
| 16 | D17, D21 and D22 say more than his words; D18's photos are not kept | refuter 3 | acted | each D marks the team's reading as H; D18 says its details cannot be checked here |
| 17 | the D18 Results row marks A7 met without a measurement | refuter 3 | acted | the row says partly, nothing measured; A7 stays open |
| 18 | the Riskiest line, the board actions and the Hand-off's Outcome are stale; A1 still counts | refuter 3 | acted | each updated; A1 retired as accepted, not tested, with a Results row |
| 19 | D24 says more than his answer ("the perfboard reuses its layout core") and its "first" does not say before what | refuter 4 (PR #1954) | acted | the extra clause dropped; D24 says the spike runs before the perfboard design and that no decision orders it against P1237 |
| 20 | C30 names the wrong board range: Table I has five boards, from 10x6 to 12x18 holes | refuter 4 (PR #1954) | acted | C30 says five boards from 10x6 to 12x18 holes, reproduced from the paper's Table I |
| 21 | C30 says jumpers are future work, but the paper draws them, and "C29's plan stands" is drawn from finding nothing | refuter 4 (PR #1954) | acted | C30 says only the optimization of jumper routing is future work, and marks the conclusion H with the caveat that the paper covers placement only |
| 22 | the new lines use semicolons | refuter 4 (PR #1954) | acted | commas and full stops in D24 and C30 |
| 23 | items.md's P1359 line and P1359 #1949 on GitHub do not name P1237 | refuter 4 (PR #1954) | acted | items.md's depends-on line names P1237 #1790 through P275 #311. No link on #1949: it is a sub-issue of P275, which spark-main set as blocked by P1237 (D24) |
| 24 | risks-and-tests.md still points at Q2 as open | refuter 4 (PR #1954) | acted | both lines name D5 and D24 |
| 25 | brief.md has 163 lines, over the guide's 150 | refuter 4 (PR #1954) | dropped because the check warns and passes, and the brief holds 24 decisions that the design reads |
