# P612 where flappy's frame time goes: rows

What the plan rounds, the board runs, the review and the refuter found. Card: [P612 #817](https://github.com/xmejkal/spark/issues/817), with P604 [#805](https://github.com/xmejkal/spark/issues/805) folded in.
PR: https://github.com/xmejkal/pixel-games/pull/33. Rows PR: https://github.com/xmejkal/spark/pull/845. The finding is `docs/discovery/2026-11-05-p612-frame-time/README.md` in pixel-games.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The card's premise was stale: P602 measured flappy with fire at 21 to 23 fps, not 16 to 17, and the PO took the fire out of flappy | the plan, bench.md P602 | acted | the finding's first lines say it, and R2 rebuilt the fire case from 324c23d |
| 2 | Plan round 1 (Fable refuter), one MUST: PIE was already researched in `p580-finding.md`, and P583 #784 is its build card. The plan re-researched it | the plan, round 1 | acted | Part B read P580 first and researched only the fire's gap |
| 3 | Lesson: a spike plan reads the earlier findings on its topic before it plans research. P580 sat in the repo root, not in `docs/discovery/` | the plan, round 1 | closed | a lesson for the retro: findings in one place, found by topic — P776: done by P580 #771 (closed) |
| 4 | Plan round 1: a bare `FireLayer` puts no heat in, so R2 needed `FireTrail` too | the plan, round 1 | acted | R2 copied P602's wiring and constants verbatim |
| 5 | Without the 40 ms pace, flappy on master runs at 28 fps, and the send grows from 3.5 to 8 ms | run92, run109, run111 | closed | the finding's table, the send's cause stays unsplit — P776: the pixel-games lane's: Flappy frame time. |
| 6 | Python's own work is about 1 to 3 ms of a 35.7 ms frame, summed from the step and the loop, not measured as one number. Pixels through PSRAM take about 22 ms | run109 | closed | the finding: moving Python to C saves little in flappy — P776: the pixel-games lane's: Flappy frame time. |
| 7 | The sky picture is painted every frame on the s3lcd path (`lcd.py:182`), 7.3 ms | run109 | acted | P629 #842, one C pass for the background |
| 8 | A late frame still sleeps 1 ms (`app.py:180`) | the code | acted | P630 #843 |
| 9 | P604: the strip's redraw is not the cause. R3d, with no redraw and 24 glyphs, paints slowest (14.4 ms) | run112, run113 | acted | the finding's P604 section, P631 #844 |
| 10 | The refuter proposed R3d during the review. One more run changed the P604 conclusion from "the redraw path" to "the heap's small objects" | the PR refuter, round 1 | closed | lesson for the retro: a refuter that proposes a deciding probe is worth one run — P776: done by P604 #805 (closed) |
| 11 | Review round 1 (Sonnet): "cap" meant three things (no pace, a 33 ms pace, the 60 ms dt cap), and two code pointers were wrong | the PR review | acted | one word per meaning: pace and dt cap, pointers fixed |
| 12 | Refuter round 1: R3c's strip address was not "the same", and rank 2's "4 full-screen layers" was wrong (the layers are part height) | the PR refuter | acted | 0x3c1dfb00, the arithmetic of about 157,000 px and about 5 ms |
| 13 | Refuter round 2: "the rain's paint allocates every frame" had no evidence, and the code was written to allocate nothing | the PR refuter, round 2 | acted | tagged H, P631's first step reads `gc.mem_alloc()` around the paint |
| 14 | PIE fits P583 #784 if slice 0 names `fx_fire_step` and `fx_fire_blend`, adds the C-twin build rule, and if the PO decides sway | research, p580-finding.md | acted | a comment on #784. Sway is the PO's decision |
| 15 | The fire's 8.85 ms is not split into scroll and step | the finding | closed | "Not checked" in the finding — P776: the pixel-games lane's: Fire step split. |
| 16 | Also open: the PIE numbers are estimates (P583 slice 0 measures them), the send's growth is unsplit, and run109 and run111 differ by 1.5 ms in send on the same code path | the finding, "Not checked" | closed | the finding's "Not checked" list — P776: tracked by P583 #784 (open) |
| 17 | The style hook flagged 13 hits in the first draft, mostly trailing conditions and modals | the simple-english hook | acted | fixed before the commit |
