# P403: `--match` names who holds a board, findings rows

Findings from planning and building P403 (2026-10-25, Prague). The plan council ran two rounds: one Sonnet 5.5 lens over
code, tests, names and the views of a person and of Claude, then one Opus 5.5 refuter. The build checked each claim of the plan in the code.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | `holders_of` goes into `drawer.py`, because `--drawer` needs it too and `needs.py` already imports `drawer` | round 1 | acted | `drawer.holders_of(entries, mine)`. `test_two_holders_come_sorted`, `test_the_asking_project_is_left_out_and_a_near_miss_is_kept` |
| 2 | The refusal sentence and `_how_to_free` print holders through the guard too | round 1 | acted | `test_a_holder_name_with_a_newline_shows_a_question_mark_in_the_refusal_and_its_fix` |
| 3 | An extra "one refusal" line is false for `--requirements` | round 1 | acted | dropped. The problem lines already say "refused, so nothing was written" |
| 4 | `held by` shows whenever another project holds part of the stock | round 1 | acted | `held_by` is not tied to `free`. `test_a_candidate_nobody_holds_says_no_holder` is the empty case |
| 5 | `drawer.clean` stores a word and `printable` shows one | round 1 | acted | each docstring says which. `printable` moved to `scripts/screen_text.py`, which imports no spark module. A test reads its imports |
| 6 | `_change_line` prints `used_in` keys through `json.dumps`, which lets U+202E through raw | round 2 | verified, acted | the refuter ran it. The line passes `printable`. `--json` keeps the raw values. A test covers U+202E and U+2028 |
| 7 | `plan_pick` has a Counter in `mine`, so it calls `holders_of([entry for _, entry in held], name)` | round 2 | verified | the call is in `plan_pick`. The mutation row "the refusal names the project itself as a holder" follows it |
| 8 | A refused dry run reads `not written: set ...` with one verb, never two | round 2 | acted | the line is built with `_change_line(change, False)`. `test_a_refused_dry_run_reads_not_written_set` |
| 9 | `--drawer` passes no project, so the listing names every holder | round 2 | verified | `commands/drawer.md:18` runs it bare. `holders_of(..., None)` names all. `test_the_listing_gives_each_entry_its_holders` |
| 10 | Placing `held_by` before `owned=` in `_candidate` keeps the anchor `p97-refactors.json:5` | round 2 | verified | `--anchors` refuses the same 102 rows before and after |
| 11 | The plan says the refused change line reads `not written: set <change>` | build check | rejected | a new entry reads `not written: new x`, as the test at `test_drawer.py` line 748 says. The line is `not written:` and the unchanged change line |
| 12 | Four mutation anchors quote the changed words | build check | acted | `--anchors` found them: the two in `p97-picks-detail.json`, `p97-picks.json:33` and `sprint-10-p95-final.json:31`. Each follows the new code |
| 13 | Row 14 of the P401 rows says "no cycle fails" about an import that row 21 removed | build check | acted | row 14 now says the import is gone and there is no cycle |
| 14 | The `--match` test fixture names no project, so the asking project showed as a holder | build check | acted | the test registers `plant-alarm` in `projects.json`, as the older tests do |
| 15 | An unlisted project was named as the holder of its own board in `--match`, while `--pick` accepted the same pick: the two took the asking name from two functions | PR refuter | verified, acted | `needs.match` takes it from `store.add_project(project, dry_run=True)`, as `plan_pick` does. A test, and the old code fails it |
| 16 | Many fields of the printed lines still reached the screen raw: the need's words, the drawer label and skip, problem lines, questions (a refused `--needs-set` printed a raw U+202E) | PR review, PR refuter | verified, acted | `parts._say` guards every text line once, at the edge, piece by piece at the line's own newlines. `--json` stays raw. Holder names and change lines keep their own guard, because a newline in a name would start a new line |
| 17 | The first edge guard turned the newlines that a line holds on purpose into `?` (a module's description) | the suite | acted | the guard splits at the line's own newlines first |
| 18 | `commands/idea.md` said `free 0, held by`, though a partly held stock reads `free 1, held by x` | PR refuter | acted | `free N, held by <project>` |
| 19 | The other scripts (`look.py`, `deploy.py`, `check_spine.py`) print without an edge guard | Claude | raised | for the refactor (P385): one output edge for every command-line script |
