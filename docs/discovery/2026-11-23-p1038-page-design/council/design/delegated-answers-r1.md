# Delegated council after round 1 of the P1038 design: the answers

2026-11-23, about 18:35 CET. Three seats answered [delegated-brief-r1.md](delegated-brief-r1.md) alone: the PO seat (Fable, from his recorded words), the architect seat (a fresh architect agent) and the tech lead seat (Opus). Each answer is delegated, the PO's to change, and is never quoted later as his word. The seats read the same files, so their agreement is not three independent views.

| Q | PO seat | Architect seat | Tech lead seat | Majority, as folded into design.md |
| --- | --- | --- | --- | --- |
| Q-A, a build before his yes | (a) | (a) | (a) | (a), 3 of 3: no build of P1038's sub-issues before the PO confirms the design. Slice 0 (P1043, P1035, under P793) goes on |
| Q-B, the Flash and Deploy button | (a) | (a) | (a) | (a), 3 of 3: the no-go stays through the walk. P820's Q31 stays his |
| Q-C, the share window | (a), not (c) | (a) and a fallback, not (c) | (a) and a fallback | (a), 3 of 3: the audience fails closed. Story 1f's plan first reads what `get_artifact` answers. If it has no owner-only value, no published copy holds issue text, which is (b) |
| Q-D, D23's "writes nothing" | lean (b) | (a) | (b) | (b), 2 of 3: a failed read keeps the old list and its read time and writes only `last_try: {at, code}`. The page names the cause. `last_try` is out of the stamp's newest time and out of the fingerprint. This changes D23, for the PO |
| Q-E, story 1d | (a) | (a), the grouping in 1a | (a), the grouping in 1a | (a), 3 of 3: 1d stays a P1038 card, built after P829's walk. The picks per need with today's buttons go into 1a-ii. The PO hears that D11's "several picks at once" can miss this walk |
| Q-F, the deploy and the page | (a), widen #1518 | (b), a new story | (b), a new story | (b), 2 of 3: story 0c under P793, after P1035 PR 2 and P1043. After a deploy that wrote a board log, the page refresh runs, whatever the status. The flow's steps stay at status ok only |
| Q-G, the shared-copy read | lean (b) | (b) | (b) | (b), 3 of 3: no shared-copy read in this walk. A7's shared half stays open on P834, recorded as not tested, never a pass. Claude's sentence at each publish also says that the page can name his other projects |

## Reasons, one line per seat

- Q-A. PO seat: #1521's Done-when says "No build in this epic before that", and no word of his gives the design's confirmation to a council. Architect: round 1 left must-fixes and a privacy choice that is his. Tech lead: slice 0 stands on D7, D16 and D18.
- Q-B. PO seat: his words on #1521 say "later interactive part", and a deploy erases and writes a board. Architect: a deploy needs a yes typed in his own terminal (scripts/deploy.py:23-24). Tech lead: the deploy's step is next-only (phase_steps.py:4-5).
- Q-C. All three: (b) outright takes the issues off the copy he opens, against D19. (c) cannot fire, because the walk makes no share. The window after a share in the Artifact's own menu stays open and is read to him.
- Q-D. PO seat: D1 says "without asking Claude", and a failed try's time and code are facts spark holds. Tech lead: "writes nothing" was meant to stop a failed read from emptying a good list, and (b) still stops that. Architect, against: `last_try` dirties the project's git on every failure, and the cause already has a home in the Finding.
- Q-E. All three: D11 is the PO's, so no seat cuts its item. D24 and D26 hold `keys` until P829's walk (paused on 2026-11-22, still open).
- Q-F. Architect and tech lead: the follow-up of P1035 runs at status ok only, but a "ready unknown" deploy ends as could-not-run (bench/deploy_image.py:312-318) after it wrote the board log (bench/deploy_service.py:197). So widening #1518 as written does not fix the stand that was wrong, and #1518's plan already passed its round 2. PO seat, against: D16 says "P793 piece 3 grows to do it".
- Q-G. All three: the share route is later (D9, D20), and the "held by" names are in a sentence that only `PartsReader` can split. The architect seat proposes one card on P834: the parts reader keeps the holders as a field.

## For the PO's list

- Q-C: the share window is a privacy risk that he did not accept in words.
- Q-D: D23's "a failed fetch writes nothing" changes.
- Q-E: D11's "several picks at once" can miss this epic's walk.
- Q-F: the deploy story 0c is new, under P793. Its proof on the real board waits on his bench.
- Q-G: A7's shared-copy clause, which he confirmed in D3, stays untested until P834.
