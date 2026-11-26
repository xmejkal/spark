# A1 to A11: the council of three's ratings

Delegated by the PO (D17, "Council proposes"), and his to change. Seats on Fable: the PO assistant, the architect and
the tech lead, one written brief (`ratings-brief.md`), run 2026-11-26 after 12:17 CET and before 12:20 CET. The majority
decides.

| id | importance | votes | the decision it would change, in the seats' words |
| --- | --- | --- | --- |
| A1 | high | 3 of 3 | a refused or unsafe commit redoes the git member, and every slice after slice 0 waits (P1148 D13) |
| A2 | high | 3 of 3 | a failed return redoes D-q3, flips C9 (P1160 Q4), and stops slices 3 to 5 |
| A3 | low | 3 of 3 | only slice 4 waits, and his own words ask for named points |
| A4 | high | 2 of 3 (the PO assistant, the tech lead. The architect: low) | with no outside edits, D-q1 falls back to "board.tsx stays a build output", D14 is not needed for layout files, and slice 5 waits |
| A5 | low | 3 of 3 | D6's C1 becomes two Strategies over one git Adapter, close to the same design, and no slice moves |
| A6 | high | 3 of 3 | one private string in a public history cannot be taken back, so slice 9 stops and D3, D7 and D9 reopen |
| A7 | low | 3 of 3 | the show-flow JSON gains a key, and D-q2 stands |
| A8 | low | 3 of 3 | the clone moves out of the store, and D-q5's shape stays |
| A9 | high | 3 of 3 | with no reader the second epic pauses, and D2 reopens |
| A10 | low, retired | 3 of 3 | D13 already answered it: kept steps go on the checked-out branch |
| A11 | low | 3 of 3 | only pictures wait, and records are still shared |

The riskiest stays A2, 3 of 3: it is high, its evidence from the PO's real repositories points against it, and its
test is about one hour (an estimate) before slice 3. A9 and A6 are the riskiest of the second epic.

Remarks for the cards:

- The architect: A9's test needs a pass line that names a real read in the PO's own use, because a scratch store that
  builds shows feasibility, not a reader.
- The tech lead: P1148 D13's A1 pass line predates D14. Today's `commit --only` exits 1 on a file that git does not
  hold yet (a scratch run, git 2.49.0), so the A2 spike on firebeetle-games writes down how it added that file.
- The PO assistant: slice 7's proof and slice 8's dry run come before anything is pushed to the public repository.

## Searches

none
