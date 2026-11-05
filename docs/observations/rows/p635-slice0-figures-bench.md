# P635 silhouette people, the plan and slice 0's board bench: rows

What the research, the plan rounds, the review and the refuter found. Card: [P635 #850](https://github.com/xmejkal/spark/issues/850).
PR: https://github.com/xmejkal/pixel-games/pull/36. Rows PR: this file's PR, named in its body.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The research found names with sources: skeletal animation with forward kinematics, Williams' four walk keys, Reynolds 1999's three layers, Jakobsen 2001's Verlet ragdoll. The search limit left no numbers for an older person's stoop or the cane's timing | the Sonnet research agent | acted | the plan's model section, gaps named |
| 2 | Jev is TypeSafe's hosted decision model. No ESP32 version was found. JevOS is a free CPU-only yes/no server, so a JevOS brain answers only "flee?" | web search, plan round 1 | acted | P636 #851's notes, the plan's "Later" section |
| 3 | Plan round 1 (Fable refuter), MUST: the free frame time was 16 ms, not 25 ms, because the plan summed the scene's HUD, not the App's `time` line | the plan, round 1 | acted | the bench reads the `time` line |
| 4 | Plan round 1, MUST: BOOT already cycles the fire's modes in this scene, so a brain switch on BOOT clashed | the plan, round 1 | acted | the switch moved to P636, the MVP has one `RuleBrain` |
| 5 | Plan round 1: `Kind` clashed with the event `kind`, and `gait` had no source | the plan, round 1 | acted | `FigureKind` and Reynolds' `Locomotion` |
| 6 | Plan round 2, MUST: the figures' ground line must be y 240, the screen's bottom edge, where the lowest bodies land | the plan, round 2 | acted | the plan's slice 1 |
| 7 | Through the canvas wrapper one figure costs 2.9 ms, through the driver 0.23 to 0.35 ms. The wrapper costs 8 times a driver call | run116-p635-n0 | acted | the figure painter calls the driver |
| 8 | The refuter, MUST: `fill_polygon` fills only the rows strictly inside a polygon, so the first runs' 1 px quads drew flat bones (the torso) not at all | the PR refuter, s3lcd.c:2391-2397 | acted | 2 to 3 px bands, all five runs redone as run116 |
| 9 | Lesson: a bench of a drawing way must also check that it draws. Nobody saw the figures on the panel | the PR refuter | raised | slice 1's Mac PNG and board run show them. For the retro: a look check per drawing bench |
| 10 | The refuter refuted my claim that `polygon` closes a chain: it draws an open chain | the PR refuter | acted | bench.md fixed |
| 11 | The reviewer, MUST: the canvas way put the second line of each 2 px pair on the wrong side | the PR review | acted | the inverse offsets per orientation |
| 12 | Go: 12 figures add about 3.8 ms walking and 4.7 ms burning, at 23 to 24 fps. 24 figures add 6.8 ms at 23 fps | run116 | closed | bench.md P635 |
| 13 | The probe adds about 54 KB to the heap, so gc is 3.6 ms against 2.0 ms in run89, and the free time in this scene is about 14 ms | run116, the refuter | raised | slice 1 keeps its baked tables small |
| 14 | The PO's new asks during this card: speech and a tiny LLM (P637 #852), flames in front of a burning object (P639 #854), and ordered C and Python layers (P638 #853) | the PO, 2026-11-05 | acted | filed with the PO's words |
