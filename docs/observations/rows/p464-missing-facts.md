# P464 missing facts: rows

What the P464 build (PR #655), its review and its refuter found, and what the plan claimed wrongly. Card: #632.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | A `pins.py` that spark left alone (someone edited it) gets no missing-fact items, so the gap is not said | plan cut | raised | later row: `_kept_pins` returns "left alone" before the pin map is built |
| 2 | A build without `--keep` gives no missing-fact signal: only the kept `pins.py` entry and the top-level key carry it | plan cut | raised | `check_spine.report`; later row |
| 3 | The `_kept_pins` duplicate-target fold was not needed once two imports merged | plan | rejected | line budget held without it |
| 4 | Only the onboard LED and button levels are missing facts today; other facts a stage needs (display size, divider) are not listed | plan | raised | `missing_facts.ACTIVE_LEVEL_MEANING` is the one table to grow |
| 5 | Refuter 1: the missing facts lived only inside `kept[]`, so an agent that reads `status` and `unchecked` never saw them | refuter | acted | top-level `missing_facts` beside `unserved`, only when there are items; agents.md says `ok` is not "no facts missing"; test_json_contracts pins the key |
| 6 | Refuter 2: `--fact-set --project other` wrote another listed project's board | refuter | acted | `board_write_problems` refuses a board outside this project's `boards/`; test in test_parts |
| 7 | Refuter 3: `pin_roles` skipped the text scrub and the key check (control characters, 5000-char source, a key with NUL written raw) | refuter | acted | `pin_roles` joined `drawer.PROVENANCE_KEYS`; tests in test_parts |
| 8 | Refuter 4 and reviewer: a write could empty a level (`value: null` over a verified one) | refuter, reviewer | acted | `level_write_problems` refuses a null value; test in test_parts |
| 9 | Refuter 5: journey.py and the svg said "no reset press", but the PO had put the board in download mode by hand before the look | refuter | acted | now "deploy needed no reset press after the flash"; svg regenerated |
| 10 | Text mode (no `--json`) of the `missing fact:` line had no test | reviewer | acted | test in test_check_spine |
| 11 | The unplanted defects (kind guard, validate subtraction, the `_ON` line's words, the stderr line, value 2, fixes 6 to 8) had no mutation row | reviewer | acted | rows added to `tests/mutations/p464-missing-facts.json` |
| 12 | `merged_roles` has a dead branch for a non-dict entry | reviewer | rejected | not dead: `_set_by_name` merges before `level_write_problems` refuses, so a non-dict entry reaches it |
| 13 | The pins.py comment said "not in the board record"; the finding says "has no active level" | reviewer | acted | the comment now says "Its active level is missing" |
| 14 | `PinModuleResult` could have a better name | reviewer | rejected | kept: it names what `pin_module_for` returns |
| 15 | Wrong plan claim: result.py is `scripts/spark/core/result.py`, its Finding comment at :20-37 | plan | verified | read in the code |
| 16 | Wrong plan claim: `pin_module_for` has two callers (check_spine and one test) | plan | verified | grep |
| 17 | Wrong plan claim: parts.py `LIBRARY` is the parts folder; `boards.LIBRARY` is separate, so the guard needed both | plan | verified | guard in `_set_in_home` |
| 18 | Wrong plan claim: `_record_path(kinds=("part",))`; a tuple would force a 6th parameter on `_set_in_home` (R3), so it is `kind=` | plan | verified | `_record_path` |
| 19 | Wrong plan claim: a `boards/levelless-board.json` in the repo; the test builds one in a temp project from the XIAO | plan | verified | tests/test_missing_facts.py |
| 20 | An unchecked item with a `subject` was claimed for `missing_fact`; the items are never in `unchecked` | agents.md text | acted | the sentence is removed |
| 21 | Refuter, second round: `missing_facts` shows only with `--keep` (it is built from the kept entries), while the docs said "always" | refuter | acted | docs say "with `--keep`, when spark writes pins.py"; rows 1 and 2 name the gap; a test pins the absence without `--keep` |
| 22 | Refuter, second round: run from the project folder without `--project`, the refusal said "(None)" | refuter | acted | the refusal says "pass --project <the folder of the project that owns it>"; the `fix` command carries `--project .`; tests run it as written |
