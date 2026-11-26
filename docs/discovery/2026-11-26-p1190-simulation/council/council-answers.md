# The delegated council's answers, tallied

Three seats on Fable answered [delegated-brief.md](delegated-brief.md) on 2026-11-26: the PO assistant
([delegated-po-assistant.md](delegated-po-assistant.md)), the architect ([delegated-architect.md](delegated-architect.md))
and the tech lead ([delegated-tech-lead.md](delegated-tech-lead.md)). The session acts on the majority. Every row is
delegated, the PO's to change, and is never quoted as his word.

| Q | The majority | Votes | What differs between the seats |
| --- | --- | --- | --- |
| Q0 the frame | yes, with fixes: the outcome's proof adds a fixture board with no Wokwi part (the clock proves "grey, with a reason" after P999). "Must not get worse" names old build records, the exit codes, and a free check that never blocks a deploy. The brief says that a part simulated by a script off Wokwi is in no slice. The README's claim range is fixed | 3 of 3 | the tech lead also fixed the questions' range in the frame |
| Q2 the first slice | (d), split into separate PRs: P999 and item 4 first, then `check-firmware` (the import check and the project's own tests only), then P1078, then the seam with no behaviour change (the guard moves into `coverage` and keeps its ending), then one small PR that flips the ending to `skipped` after the PO's Q11 | 3 of 3 for (d) | the architect and the PO assistant put `check-firmware` before P1078, the tech lead after it. So that part of the order is 2 of 3, the session's pick |
| Q3 the runner | not now. Item 14 stays parked until A1's result and the PO's reading of the non-goals | 3 of 3 | none |
| Q4 the setting | (a) one setting, the `simulator` role. "Off" reads `skipped` with "you turned it off", never `could-not-run` | 3 of 3 | the architect proposes "off" as a Null Object Adapter behind the role, because the tool's `on` flag also stops the free chip compile. An H for the seam's plan |
| Q6 the slider | (a) a value in a scenario step, drawn on the page with its range. The PO is told that the bar does not move | 3 of 3 | none |
| Q7 the chip spike | yes, in slice 3, in two halves: the free half (the licence, and whether wokwi-cli resolves a `github:` chip) and the run, which waits on the PO's yes for its minutes | 3 of 3 | none |
| Q8 the project's own tests | yes: run and count, claim nothing of their cover. The record lives under `.spark/`, never in `sim/runs/`, and has a timeout. A failed own test blocks no deploy until the PO decides | 3 of 3 | a project with no `tests/`: no row (the architect), `skipped` (the tech lead), a plain fact (the PO assistant). The plan picks, and it never reads as a pass or a fault |
| Q12 the words | the existing tiers and P308's "grade", added to `docs/guide/words.md` by the first card that prints them. The page shows plain words, never "T3" | 3 of 3 | none |
| Q1 ratings (a proposal to the PO) | high: A1, A3, A8, A9. Low: A2, A4, A5, A6, A7 | A1, A3, A8: 3 of 3. A9: 2 of 3. A5: 1 of 3 high | the PO assistant rates A5 high and A9 low |
| Q1 the pass line (a proposal to the PO) | split use from yield. Use: on the next walk the free checks run before the first deploy, and the log says who started them. Yield: over the next 3 walks, at least 1 fault whose fix is a firmware change is found by `check-firmware` before the first deploy. A walk with no fault anywhere gives no information. A false alarm counts against. The test gates the screens of slices 2 and 3, not `check-firmware` itself | 3 of 3 on the split | the wording follows the architect and the PO assistant |

## Corrections to the synthesis that the council made

1. `check-firmware` is the move of `scripts/import_firmware.py` onto the core, not a second command beside it. It
   absorbs that line of #1105 (the architect seat).
2. Its first version calls no strategy. The dry run joins it as the strategy's `problem` in the seam card (the
   architect seat).
3. One generic lookup from a role's contract to an Adapter class, written by whichever seam card runs first. Each
   seam keeps its own table as data. No shared base class (the architect seat).
4. Coverage is computed once, by the build stage, and kept in the build record. The flow and `check-firmware` read
   it (the architect seat).
5. After the flip, a build with a skipped stage exits 0, and the store does not vouch for it as built
   (`scripts/spark/build/build_service.py:506-521`). The flip PR says both in `docs/guide/agents/flow.md`, and
   `NO_MODEL_CODES` stays as a reader of old records (the architect and PO assistant seats).

## Advice to the PO on his own questions

All three seats advise: gate A shows the simulation as evidence, and can use the free condition that already exists
(no failed run on the current image). Q9 is asked about one concrete walk (p711, where the agent held the run).
Q10 and Q11: yes, with old records still counting as done. Q3's non-goal reading: a runner of the person's own
`main.py` on the generic fake is the T1 test rig, and a device model per part is "writes behaviour". "The editor"
edits the scenario's steps and values, through Claude. Another author's chip: by reference only, permissive
licences only.

## Searches

none. This file made no web search.
