# P386 R1: archive the finished plans, rows

R1 of P386 ([#495](https://github.com/xmejkal/spark/issues/495), 2026-10-22, Prague). One agent (Opus 5.5) wrote
them. Each claim of the plan's R1 section was checked in the code before the work.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | "15 dated pages, minus 3 living designs and 4 team pages, leaves 8" | plan, R1 step 1 | verified | `ls docs/2026-*` showed 15 pages. The 8 moved with `git mv`. |
| 2 | "`docs/README.md:6` and `tests/test_journey_basic.py:5` need the new path by hand" | plan, R1 step 3 | verified | both changed. The README row used a relative link, so one edit fixed it. |
| 3 | "About 16 files in `docs/discovery/` and `docs/observations/` hold links to the moved pages" | plan, R1 step 3 | verified | 34 citations in 17 files under `docs/` (14 outside `docs/archive/` and `docs/README.md`), counting INDEX.md. One script fixed them, and the diff was read. |
| 4 | The moved pages keep working links | not in the plan | raised, acted | 10 relative links inside the moved pages pointed at siblings that stayed in `docs/` (`guide/`, `observations/`, `discovery/`, `../scrum/`, the p211 design). Each got `../`. |
| 5 | `scrum/VISION.md:60` stays broken until P384 | plan, R1 step 3 | verified | it still names `docs/2026-10-11-replan.md`. Not edited, as the plan says. |
| 6 | "`stale_doc_paths` returns 0 today" | plan, R1 step 4 | verified | 0 on this branch. A throwaway scan before the code gave the same. |
| 7 | "`problems()` (:184)" | plan, R1 step 4 | verified | line 184 before the edit. |
| 8 | `tools/check_docs.py` has MVP markers to extend | task brief | raised | the file had none. The new function and `problems()` carry `# --- MVP ---`. No part is "Later, not MVP". |
| 9 | `docs/archive/README.md` and the 8 pages still say a path "from before the move" is fine | sweep | acted | the intro names the 2026-10-11 move only. The new row carries the 2026-10-22 date. |
| 10 | `tools/check_docs.py` header and `docs/guide/developing.md` list what the check reads | sweep | acted | both name the new rule. |
| 11 | Old text outside the checked folders still names the old paths (`scrum/`, closed issues, `INDEX.md` history) | sweep | raised | `scrum/` is out of scope until P384. The archive README tells readers that old text finds a file by its name. |
| 12 | `docs/archive/2026-10-16-p268-svg-plan.md` links `breadboard.svg` and the p211 plan holds `facts[key]` that look like broken relative links | sweep | closed | both are examples inside code, not links, and they were broken before the move. |
| 13 | About 40 other relative links in `docs/` were already broken on main (INDEX.md, p179 review, the p158 archive) | sweep | raised | not caused by R1. A card for a link check over `docs/` would cover them. |
