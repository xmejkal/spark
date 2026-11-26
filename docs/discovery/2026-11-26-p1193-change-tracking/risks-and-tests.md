# Risks and tests

## Risks
<!-- One row per type; an active extension adds its own rows. evidence now: tag and ids (★C<n>, A<n>).
status: open · retired · n/a because ….
e.g. `| usability | H no test yet (A2) | a five-person prototype test | open |` -->
| risk | evidence now | cheapest way to retire it | status |
| --- | --- | --- | --- |
| value <!-- REQUIRED:risk-value --> | H: 0 tags in 9 repositories, and 24 hand commits of board.tsx keep J1 by hand today (PO-1). Nobody is blocked against the MVP bar (PO-8). A3, A4, A9 | the A2 spike's count, and slice 1's reading on the PO's own projects | open |
| usability <!-- REQUIRED:risk-usability --> | H: no test of the words for a named point, an outside change or a share (UX-3, UX-8). A7 | slice 1's text view and JSON read by the PO and by Claude on a scratch project | open |
| feasibility <!-- REQUIRED:risk-feasibility --> | E against: a return across the person's own commits and a squash refuses or loses its point (UX-2, UX-10, PO-2). E for: a spark ref survives a squash, n = 1 (synthesis part 3). A1, A2, A5, A8, A11 | the widened A2 spike on temporary clones (Riskiest, below) | open |
| viability <!-- REQUIRED:risk-viability --> | H: the shared repository has one writer and no reader yet, since D2 dropped the trigger (PO-8). A9, A10 | slice 7: the PO's second scratch store builds with a received record | open |
| ethics and safety <!-- REQUIRED:risk-ethics --> | E: `//` notes in 28 of 28 records, his name and a folder under his home in 2 fact sources, `based_on.project` in 7 to 9 records (PO-4, UX-4). A public history keeps what it gets. A6 | slice 8's dry run over the 28 records, before any share (N4) | open |
| power and battery <!-- REQUIRED:electronics-firmware:power --> | n/a | n/a | n/a because D1 turned the electronics-firmware extension off: this epic keeps files and reads no part, pin or power fact |
| current and stall <!-- REQUIRED:electronics-firmware:stall --> | n/a | n/a | n/a because D1 turned the electronics-firmware extension off: this epic keeps files and reads no part, pin or power fact |
| thermal <!-- REQUIRED:electronics-firmware:thermal --> | n/a | n/a | n/a because D1 turned the electronics-firmware extension off: this epic keeps files and reads no part, pin or power fact |
| EMC and ESD <!-- REQUIRED:electronics-firmware:emc-esd --> | n/a | n/a | n/a because D1 turned the electronics-firmware extension off: this epic keeps files and reads no part, pin or power fact |
| sensor drift and calibration <!-- REQUIRED:electronics-firmware:sensor-drift --> | n/a | n/a | n/a because D1 turned the electronics-firmware extension off: this epic keeps files and reads no part, pin or power fact |
| brown-out <!-- REQUIRED:electronics-firmware:brown-out --> | n/a | n/a | n/a because D1 turned the electronics-firmware extension off: this epic keeps files and reads no part, pin or power fact |
| wake and low power <!-- REQUIRED:electronics-firmware:wake --> | n/a | n/a | n/a because D1 turned the electronics-firmware extension off: this epic keeps files and reads no part, pin or power fact |
| the firmware–hardware contract <!-- REQUIRED:electronics-firmware:contract --> | n/a | n/a | n/a because D1 turned the electronics-firmware extension off: this epic keeps files and reads no part, pin or power fact |
| supply and documents <!-- REQUIRED:electronics-firmware:supply --> | n/a | n/a | n/a because D1 turned the electronics-firmware extension off: this epic keeps files and reads no part, pin or power fact |
<!-- EXTEND:risk-rows --><!-- EXTEND:pair-rows -->

## Assumptions
<!-- About ten at most. type: value, usability, feasibility, viability or ethics. importance: "— (decider)" until
the decider rates it, then "high D<n>" or "low D<n>". pass line: written, with its date, before any result.
status: open, or retired with the date of its Results row.
e.g. `| A2 | Assignees never see new tasks | value | H ★C2 | — (decider) | query opened-within-48h | under 50 %, set 2026-10-06 | over 80 % | open |` -->
| id | belief | type | evidence now | importance | cheapest test | pass line, dated | result that would change the decision | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 <!-- REQUIRED:assumptions --> | Spark's commits in a person's repository happen and are safe | feasibility | open since P1148 D13, never run (PO-6) | — (decider) | P1155's A1 walk | P1148 D13's: 3 of 3 kept lines, 0 tracked files the ignore list covers, set 2026-11-25 | a refused or unsafe commit: the git member is redone | open |
| A2 | A return to a named point runs in the maker's real repositories, with his own commits, a PR flow and a squash between spark's steps | feasibility | against: UX-10, PO-1, PO-2, UX-2. For: the synthesis's scratch run, n = 1 | — (decider) | the widened A2 spike on temporary clones of three repositories (Riskiest, below) | proposed, set 2026-11-26 before any result: in 3 of 3 clones the records equal the named point byte for byte, 0 other files change, an uncommitted edit survives or the return refuses in plain words, and the point survives the squash in 3 of 3 | a changed file outside the records or a lost point: D-q3 is redone. P1160 Q4 refuses 2 or more of 3: C9 flips | open |
| A3 | The maker wants named points and a way back from spark, beyond git by hand | value | 0 tags in 9 repositories (PO-1) | — (decider) | the PO's use of slice 4 on one walk | none set, 2026-11-26: waits for Q1 (P9) | he never names a point in a walk: slice 4 waits | open |
| A4 | A person or Claude edits board.tsx or breadboard.json outside spark often enough to keep it | value | 24 hand commits of board.tsx (PO-1) against 0 of 6 files that differ from what spark wrote (UX-6) | — (decider) | slice 1's count of "board file changed" lines over the PO's projects | none set, 2026-11-26: waits for Q1 (P9) | 0 in all his projects: slice 5 waits | open |
| A5 | One lower Strategy serves both Services and stays small | feasibility | H ARCH-1, ARCH-14, no code yet (brief ★C1) | — (decider) | slice 0's test with a second, fake caller | none set, 2026-11-26: waits for Q1 (P9) | the seam needs a verb only one caller uses: two Strategies after all | open |
| A6 | An allow-list and a check of free text keep every private string out of the public repository | ethics | against: `//` keys in 28 of 28, his name in 2 fact sources (PO-4, UX-4) | — (decider) | N4's dry run over the 28 records | none set, 2026-11-26: waits for Q1 (P9) | one private string in what would go: no share until the check catches it | open |
| A7 | A person and Claude read "changed outside spark" and know the one next step, with no git word | usability | H UX-8's sketch, no test | — (decider) | slice 1's text view and JSON read by the PO and by Claude | none set, 2026-11-26: waits for Q1 (P9) | Claude parses English to find the file: the JSON gains the key | open |
| A8 | A clone in a sub-folder of the store works as one more layer, and a receive at a fixed point runs | feasibility | half E (TL-2's shelf write), half H (no fetch or checkout run) | — (decider) | slice 7 in a scratch store | none set, 2026-11-26: waits for Q1 (P9) | the store refuses the clone or a private write: the clone moves out of the store | open |
| A9 | Someone reads the shared repository: at least the PO's own second project builds with a received record | viability | n = 1, the 10-04 trigger is gone (PO-8, D2) | — (decider) | slice 7's proof | none set, 2026-11-26: waits for Q1 (P9) | no read in the PO's own use: the shared side pauses | open |
| A10 | Kept steps on the checked-out branch of a PR-flow project are what the PO expects | viability | P1148 A8 and Q14, still queued | — (decider) | the PO's answer to P6 | none set, 2026-11-26: waits for Q1 (P9) | he wants a branch of spark's own: the git member changes | open |
| A11 | D4 can be read from a record | feasibility | not today: `--made-by` is a free word (UX-5) | — (decider) | slice 8's closed `made_by` set over today's pictures | none set, 2026-11-26: waits for Q1 (P9) | a picture's maker cannot be told: no picture is shared | open |

## Collection plan
<!-- One row per gap. e.g. `| Do assignees open new tasks? | Q2 | Lena, from analytics | one query | this week |` -->
| question | decision it blocks | who can answer | how | when |
| --- | --- | --- | --- | --- |
| Does a return to a named point work in the PO's real repositories (A2)? <!-- REQUIRED:collection --> | D-q3, C9, slice 4 and 5 | a spike agent, on temporary clones, originals read-only | the widened A2 spike, about one hour | after the PO sets the pass line (P9), before slice 3 |
| Do spark's commits happen in a new project (A1)? | the later slices of P1152 | P1155's builder | the A1 scratch walk | after slice 0 |
| What would a share of today's 28 records carry (A6)? | slice 8, P1 | a spike agent, read-only on the store | N4's dry run with a draft allow-list | after the PO answers P1 |
| How often is board.tsx or breadboard.json edited outside spark (A4)? | slice 5 | spark itself | slice 1's reading over the PO's projects | after slice 1 |

## Results
<!-- Filled on a return; may stay empty until then. One row per result: what was tested, what was seen (verbatim,
with its pointer), the pass line met or missed, what it changes. -->
| date | source and pointer | what was seen | pass line met or missed | what it changes |
| --- | --- | --- | --- | --- |

## Budgets <!-- REQUIRED:electronics-firmware:budgets -->
<!-- Energy per mode · peaks per rail against the source · dissipation per part, each number with its provenance and
the rung that would settle it (electronics-firmware:R<n>). "n/a — no battery, motor, radio or regulator" is allowed. -->
n/a — no battery, motor, radio or regulator: the epic keeps files, and D1 turned the extension off
<!-- EXTEND:risks-sections -->
