# Q0: the council of three on Fable

Delegated by the PO's standing rule for an away session (spark-main's brief, 2026-11-26), and the PO's to change.
Seats on Fable: the PO assistant, the architect and the tech lead, one written brief (`q0-brief.md`), run 2026-11-26
between 09:03 and 09:05 CET. The majority decides. A point that any seat marked "PO only" goes to the PO.

| Question | Answer | Votes | PO only |
| --- | --- | --- | --- |
| 1. The decision set | One discovery, two build epics: the project timeline (P1152, widened) and the store's shared side (under #123). Add two decisions: D-q7, which slice comes first by the MVP bar, and D-q8, a record's identity and a tombstone before any transport (C11). D-q6 becomes one configuration and one shared git Adapter. Whether one Strategy or two small Strategies sit over it goes to the lenses | 2 of 3 for one discovery (the PO assistant, the architect). The tech lead wants the store as a second epic, which "two build epics" keeps | which central repository, whose account, public or private (the PO assistant). The order of the two epics (the tech lead) |
| 2. The scope | Test only on the steps that exist. Name a rule for later steps: each area declares its kept step's records, so a perfboard or a PCB phase adds a row and the timeline does not change. The person's own files, board.tsx and breadboard.json, are in scope | 3 of 3 | none |
| 3. "Configurable" against 10-04 | No conflict for the seam: P1148 D5 and the Storage seam already passed "pluggable storage backends", and that line is the council's plan text, not one of the PO's four decisions of 10-04 | 3 of 3 | Sharing picture bytes in a public repository: origin and licence decide (the architect, the tech lead). Whether his words of 11-26 replace his trigger of 10-04, "the shared database starts when the first person outside the project researches a part" (the PO assistant) |
| 4. The electronics-firmware extension | Off. The epic keeps files and reads no part, pin or power fact | 3 of 3 | none |
| 5. The depth | Four lenses on Opus: the PO assistant, the tech lead, the architecture lens, and the UX and AI-UX lens, which takes the user's journey. The refuter on Opus, the architect for the synthesis | 2 of 3 for folding the user lens (the architect into UX, the tech lead into the PO assistant). The PO assistant kept five | none |

## What the seats said the frame gets wrong, and what changed

- D-i and C10 gave the "not building" list to the PO. It is the council's plan text (docs/archive/2026-10-04-store-discovery.md:215-217). His decisions are items (1) to (4) at lines 221-227. Fixed in the brief.
- D-q1 reopens P1160's answer "board.tsx stays a build output". The brief now says so, as P1148 D9 named what it replaced.
- breadboard.json is a second file of the person's: `scripts/spark/breadboard/kept_moves.py:1-5` keeps the person's moves across a rebuild. Added as C15.
- D-q2 belongs to the phase readers' stamps. The strategy answers only whether it holds a file as it is (`held_as_is`, `scripts/spark/records/project_commit.py:69`). Added to D-q2.
- The store cannot be the repository, because the shelf is private and refused inside a work tree (C7). "Push the parts" needs a separate clone and a copy step. Added to D-q5.
- The reusable part is `ProjectCommit._git`, which can become its own class under both git Strategies (the architect). A proposal for the synthesis.
- Outcome (4) names a local bare repository as the scratch central repository (the PO assistant).
- By the MVP bar only D-q1 and D-q2 serve a breadboard. Snapshots, compare, merge and sharing are tooling to pause (the tech lead). This becomes D-q7.
- The store's one SVG sits in `sources/` beside vendor documents, so "push pictures" cannot mean "push sources/" (the PO assistant).

## Searches

none
