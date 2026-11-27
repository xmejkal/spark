# P1247: the 3D spikes S0 to S2: rows

Card: [P1247 #1804](https://github.com/xmejkal/spark/issues/1804). The findings are in
`docs/discovery/2026-11-26-p1197-3d/spikes/`. This file holds the acted, raised and rejected findings of the PR's own
review (one refuter on Opus, docs only). 2026-11-27.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | S2's "The pages state no terms for the files" is too soft, because the page says all rights reserved | PR refuter (Opus), finding 2 | acted | fixed in s2-vendor-models.md. Both wiki footers were read again with `curl` |
| 2 | S2 marks the amplifier's pin line "Met by calculation", but the file that ran had no turn | PR refuter (Opus), finding 3 | acted | fixed in s2-vendor-models.md: "Not run", with the calculated result |
| 3 | The PO's note of 2026-11-27 holds two readings that cannot both be true (14 pins on the battery edge, and `RX` on it), so one look at the board is still owed | PR refuter (Opus), not checked list | raised | fixed in the card: it stays in the "Done when" of P1334 #1913 |
