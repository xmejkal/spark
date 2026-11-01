# P502 agents split: rows

What the P502 plan, its two council rounds and the build found. Card: #691.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | agents.md (1,036 lines) splits into the contract page and three pages under `docs/guide/agents/`: scripts.md (old 75-379), json.md (old 380-722), never-assume.md (old 799-1002) | plan | acted | commit 1; the sort diff shows only added lines and link rewrites |
| 2 | The council text said `agents-json.md` and `agents-scripts.md`; the folder form matches `docs/guide/journey/` (P501) | council round 1 | acted | file names under `docs/guide/agents/`; the card's Done when names the folder pages |
| 3 | agents.md keeps a stub "What never to assume" heading and "Is it ready?", so journey.md's links stay valid in either merge order with P501 | lead | acted | journey.md is not edited; its links to agents.md anchors still resolve |
| 4 | The exit codes keep their home in agents.md's outcomes section, not in the JSON page | lead | acted | README's and json.md's repeats became links to it in commit 2 |
| 5 | The split line is 379/380, not 319: line 319 sits inside the "What reads and what writes" bullet | refuter (round 1) | acted | scripts.md ends at old 379; json.md starts at "check_all's answer" |
| 6 | The CELL_LIMITS key must follow the four long cells to json.md in commit 1, or the cell check fails there | refuter (round 1) | acted | commit 1 renames the key; commit 2 removes it |
| 7 | More links than the plan listed: commands/deploy.md:22 names a moved heading, old line 378 says "see rule 5 below", how-it-works.md:69 names the `--json` list | round 2 | acted | all three point at their new page; rule 5 is a link to never-assume.md |
| 8 | parts.py:1628 cites "parts.py's envelope", a heading that did not exist (it was a bold label) | round 2 | acted | json.md's bold label became the heading "parts.py's envelope"; the help names json.md |
| 9 | The examples use `$CLAUDE_PLUGIN_ROOT`, so the new folder does not change what they run | refuter (round 1) | verified | check_docs runs every marked example from the new pages and they pass |
| 10 | No test asserts the docstrings that name agents.md (look.py, deploy.py, parts.py, core/operation.py, core/codes.py) | plan | verified | `git grep 'docs/guide/agents' tests` finds only the two readers, which now read every page |
| 11 | Turning the four long cells into bullets grew json.md from 346 to 395 lines in commit 2, so its budget rose within the PR | build | raised | still under the 400 default, and every budget on main went down or away; a later prune of json.md's envelope section can lower it |
| 12 | `check_spine.py`'s `missing_facts` was said three times (its key cell twice, the `missing_fact` code row, never-assume rule 1) | build | acted | one home: json.md's "check_spine.py" section; the other three link it |
| 13 | P501 also edits `BUDGETS` and may edit README, so the second of the two PRs to merge gets a conflict in `tools/check_docs.py` | build | raised | resolve by keeping both pages' entries |
