# P1122: Claude's jobs as chat offers with a tell, shown under "Ask Claude": rows

Card: [P1122 #1652](https://github.com/xmejkal/spark/issues/1652), with [P1115 #1644](https://github.com/xmejkal/spark/issues/1644)
and [P1128 #1659](https://github.com/xmejkal/spark/issues/1659) riding. The plan (revision 3) had two council rounds,
each a lens (Sonnet) and the refuter (Opus). This file holds the acted, raised and rejected findings only. A "row" in the
last column is a row of a `tests/mutations/` table, counted from 1.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | Two rows of `p1102-design-basis.json`, "from_page ignores SENDABLE" and "from_page ignores IN_CHAT", plant one mutant once `from_page` reads the row of `OFFER_KINDS` | build | acted | Merged into row 6, "from_page ignores the row's from_page", which T6's swap of build's row catches. The plan's new p1122 row of the same mutant is that row, so it is not written twice |
