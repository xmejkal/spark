# Story map
<!-- Proposed, not applied: this map stays here until the decider confirms it; nothing changes the product's own
map file. -->
**Status:** proposed, not applied <!-- REQUIRED:map-status -->

## Backbone
<!-- The activities, left to right, as the user does them. e.g. `Assign → Notice → Act → Close` -->
plan with predictions <!-- REQUIRED:backbone --> → drawer → idea (needs → match → pick → requirements) → research the gap (round B) → build → checks → simulate (paid, his yes) → firmware (the conversation writes it) → runs on hardware he owns → score the predictions, file the gaps — the product's own spine (STORY_MAP rows 0–10), walked three times (D6: rounds A, B, C)

## Slices
<!-- Walking skeleton first: the thinnest slice that runs end to end. One row per story. job: a job in
jobs-and-journeys.md. tag: as in the brief. proof: something the decider can read.
e.g. `| 0 | Notice | the assignee gets one daily digest | job 1 | H ★C2 | the digest log for one team |` -->
| slice | activity | story | job | tag | proof |
| --- | --- | --- | --- | --- | --- |
| 0 walking skeleton <!-- REQUIRED:slices --> | decide the board (Q3), write the three pass lines, record irrigation's break | before any round, the diary holds the board decision, the pass lines and ★C4's cause | job 3 | H ★C1, ★C4, ★C6 | the diary's first entry, dated before round A's first command |
| A — owned parts | drawer → idea → build → checks → firmware → runs | a small project the library serves reaches a running board, as documented (no goal is shown served fully today — USER-5's S3 + probe left `batt` and `report` unserved; the plant alarm's real requirements are a XIAO + probe + amplifier) | job 1 | H ★C3 (the menu domains are not servable; what IS fully servable is open — Q4) | `check_spine` exit 0 with every need on the board; the pass line observed on hardware |
| B — new parts | research → record → build with it | a project whose sensor is an owned part with no record (SCD41 / VEML7700) or a bought part gets a cited record and builds | job 1, job 3 | H ★C3, C11 | a record the person can read, `--validate` clean, the build using it |
| C — irrigation | find the break → onto the store → add a feature → still builds | the existing project improves by one feature without losing its build | job 2 | E ★C4, ★C5 | `check_spine` exit 0 on irrigation, before and after |

## Delta to the product's map <!-- REQUIRED:spark-process:map-delta -->
- STORY_MAP.md slice 1b names P100 as "a new idea and an existing project": the discovery splits the new idea into A (owned parts) and B (new parts) by D6 — no change to the map's rows, one more round under the same slice.
- STORY_MAP scenario 4.2 marks irrigation's `check_all` no-[FAIL] "yes" (2026-09-29); it FAILs since B13 (★C4, F1) — the map's "yes" needs its date, or the fix. VISION's v1 line is a "done when" target, not a status (refuter). Proposed, not applied.
<!-- The rows to add or change in the repository's own story map file, in that file's table shape, with its journey
step numbers; proposed, not applied. "n/a — no map file" is allowed. -->
| 4.2 | irrigation · `check_all` · no `[FAIL]` | the command | **yes (2026-09-29)** — FAIL since 4daa58f (2026-10-03): date the yes, or fix F1 | (journey C step 1)
| 1b | P100 — a new idea and an existing project | round 0 (a board record for an owned C6), A (owned parts), B (new parts), C (irrigation) | three diaries and a round-0 diary | (journeys A, B, C)
| 2 | Your own dev board — "this was not run for these docs" | run on 2026-10-09 (round 0): a building record in 14 minutes, ten documentation gaps G0.1–G0.10 | council/round-0-runner.md | (round 0 steps 1–5)
<!-- EXTEND:map -->
