# Q0 for the council of three: is this frame right?

The PO is away. A council of three on Fable answers each choice that it can: the PO assistant, the architect and the
tech lead. The answers are recorded as "delegated, the PO's to change". Mark any point that only the
PO can decide, and say why.

Read first: `brief.md` in this folder, the Frame and What we found. Then the card: `gh issue view 1738`. Check a claim
in the code before you rest on it. You are read-only on the tree. Time limit: 10 minutes.

How the facts in the frame were checked: each claim C1 to C14 names its file and line or its command. The counts in
C8 and C14 come from one run each on 2026-11-26. C4 rests on two council files in the PO's store
(`councils/past-breadboard/refuter.md` part 3) and on the P1160 finding, which is in this repository.

## The questions

1. The decision set D-q1 to D-q6. Is one missing, or is one outside this epic? For example: is "the store's shared
   side" one epic with the project timeline, or a second epic that only reuses the seam?
2. The scope. The frame puts the perfboard and the PCB steps in scope, although the flow has no phase for them yet
   (C6). Keep them in, or keep only the steps that exist and name a rule for later steps?
3. The PO's decision of 2026-10-04 (C10) says "not building: pluggable storage backends" and "no sharing of document
   bytes". His words of 2026-11-26 say "our strategies should be configurable" and name "svg pictures". Is this a
   conflict that only the PO can settle, or can the council read his newer words as the answer?
4. The electronics-firmware extension: off, because the epic tracks files and touches no circuit physics?
5. The depth: five lenses on Opus (the PO assistant, the user, the tech lead, the architecture lens, the UX and AI-UX
   lens), the refuter on Opus, and the architect for the synthesis. Too many, too few, or right?

## Answer format

One line per question: the answer and one sentence of reason. If only the PO can decide, add "PO only". Then at most three
lines of anything else the frame gets wrong. At most 250 words in total.
