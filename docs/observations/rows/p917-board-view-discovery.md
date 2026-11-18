# P917: the discovery of which project uses a connected board: rows

Card: [P917 #1298](https://github.com/xmejkal/spark/issues/1298), a discovery, PR #1300. Docs only: three lenses on
Sonnet and one refuter on Opus ran inside the discovery, and their reports are in
`docs/discovery/2026-11-18-p917-board-holder/council/`. One more refuter on Opus read the branch for the PR. Its
verdict: stands with fixes. This file holds that refuter's acted, raised and rejected findings only (rules.md).
2026-11-18.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the items promise that the view names pixel-games after `box.py deploy`, but the store keys a deploy by the MAC and `box.py` reports no port and no USB serial | the PR's refuter | acted | fixed: item 3 and the hand-off say that `box.py` names the board of a deploy, and the card [P921 #1303](https://github.com/xmejkal/spark/issues/1303) holds it |
| 2 | item 3 waited for A6's test, and A6's pass line needs item 3 as a card | the PR's refuter | acted | fixed: item 3 depends on item 2 only |
| 3 | the hand-off named the jobs J1 and J2, and J2 needs a holder record that D8 keeps out | the PR's refuter | acted | fixed: the hand-off names J1 |
| 4 | five lines were older than the decision that answered them (D3, D6, D8, D9, and A6 "met" against "met in part") | the PR's refuter | acted | fixed in brief.md and items.md |
| 5 | items.md named P917 as the highest number, and P918 #1299 exists | the PR's refuter | acted | fixed. The filing read the number again: P919 to P921 |
| 6 | verification.md marked C15 (which touch restarts a board) as not reproduced, and the risk rows use it | the PR's refuter | acted | fixed: each part is read in the code, with its line |
| 7 | the folder holds a full board address and a USB serial, in a public repository | the PR's refuter, as a question | acted | fixed: the push hook's test `test_no_tracked_file_holds_a_real_full_mac` (P505) failed on it. Each address is masked, in every commit of the branch |
| 8 | the folder did not record the PO's yes to items.md and to the comment | the PR's refuter | acted | fixed: D11 in brief.md, the items are filed, and the comment is on #1298 |
| 9 | item 3 has no epic and no label | the PR's refuter, as a question | raised | P921 #1303 is filed with the label story under P365 #467. The epic stays the PO's choice, and the card says so |
| 10 | a lens report holds `~/` paths and the name of a local plugin source | the PR's refuter, as a question | rejected | dropped because a `~` path names no user, main holds the same form, and the name is the repository owner's public first name |
