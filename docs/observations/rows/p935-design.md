# P935 PR 3: the design area's codes carry their meaning and fix: rows

Card: [P935 #1330](https://github.com/xmejkal/spark/issues/1330). This file holds the acted, raised and rejected findings
only. The plan check had a lens on Sonnet and the refuter on Opus; the lead's revisions decide where they differ from the
plan. Then come the build's own findings. 2026-11-21.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | `design_codes.CODES` holds 29 codes, so the PR has 31 fix texts with its two variants, not 28 and 30 | the plan check (the refuter measured it) | acted | the PR body holds the table of all 31 |
| 2 | the audit's broken record ("broken: <problems>") names no file, so the records fix "fix the file the sentence names" is false there | the plan check | acted | the variant `RECORD_FILE_BROKEN_AUDIT`, an equal literal of records' word and meaning with the audit's own fix ("fix the record that `subject` names, then run `parts.py --audit` again"); `test_the_audit_s_problems_and_refusals_carry_the_fix_of_their_code` pins it |
| 3 | six fix texts were worded better than the plan's: NO_PROJECT_FOLDER, PART_UNUSABLE, RULES_REFUSED, NO_SUCH_PIN, NO_OUTLINE, OFFER_UNKNOWN | the plan check | acted | the revised texts are in `design_codes.py` and in the PR's table |
| 4 | the notes "(moved, the same bytes)" and "(PAIRS_FIX, moved)" are notes, not part of a fix | the plan check | acted | they are in no text; the moved texts are pinned as literals and green on main too |
| 5 | `UNREADABLE_FIX` goes; the store's refusal at `audit_records.py:101` reads `RECORD_UNREADABLE.fix`, with a comment | the plan check | acted | the row `p707-operations.json:16` is re-anchored |
| 6 | `audit_records.py:96` gives records' `START_FIX` to a core `bad_argument`: p935-core-codes.md row 8 | the plan | rejected | dropped because START_FIX is the records area's own fix, in its own module |
| 7 | a fix that says "the sentence names" is weak for an agent | the plan check (the lens) | rejected | dropped because each `--json` item holds its sentence and its fix together, so an agent reads both |
| 8 | when the store's `catalog/` folder cannot be read, `parts.py --audit --json` answers ok with nothing unchecked (the refuter, chmod 000) | the plan check (the refuter) | raised | card P973 https://github.com/xmejkal/spark/issues/1394 |
| 9 | `ImpossibleError(msg, code)`, `RefusedInputError(stage, why, code)` and the core's `Refusal(text, code)` take a code by position, so the scan does not see them | the plan | raised | "P935 #1330, PR 4b" (PR 4 teaches the scan only the own-class rule; the positional forms move to PR 4b) |
| 10 | most design fixes reach nobody yet: the build turns a caught code into `Finding(..., None)` (`build_service.py:504`) | the plan | raised | the build PR makes them reach the person; this PR claims nothing about them reaching the person |
| 11 | RULES_REFUSED, BOARD_UNUSABLE and NO_PROJECT_FOLDER are equal literals in design and check/build; the leaves cannot import each other (U1) | the plan | raised | the checks and build PRs write the same fix for each, with a test that the pairs are equal |
| 12 | `NO_TRANSCRIPT_FIX` (`tally_cost.py:18`) equals sourcing's `NO_STEP_MARKED.fix`; `show_offer.py:33` and `match_needs.py:41` keep fix null | the plan | raised | [P941 #1343](https://github.com/xmejkal/spark/issues/1343) |
| 13 | meanings that hold a fix (`DRAWER_ENTRY_DANGLING`, `NO_NEEDS_YET`) stay as they are | the plan | raised | dropped because no meaning changes in this PR; a later wording card may move them |
| 14 | P853 rows 8 and 9 were closed by PR 1 | the plan | rejected | this PR closes none of them and says so |
| 15 | the scan did not see `DesignError.of_error` and `SparkError.of_error`; `X.of_error` and `X.of_lines` of a coded error are now read like `X(...)` | the plan | acted | `calls_off_the_table`; a planted test of four lines and a near miss; records' and sourcing's `of_lines` sites join the scan and pass |
| 16 | a variant whose parent is another leaf's word (`RECORD_FILE_BROKEN_AUDIT`) failed the meaning and the parent checks | the build | acted | both helpers take the tables `NAMED_TOO` names; a planted test for each |
| 17 | seven mutation rows of earlier tables had their anchors moved by the edits | the build | acted | `p700-design-codes.json`, `p707-operations.json`, `p726-design-operations.json`, `p935-sourcing-records.json`; `tools/mutate.py --anchors` refuses the same 20 rows as main |
| 18 | ENTRY_PICK_GONE's fix read wrong with a comma after "yes" | review lens | acted | two sentences: "ask the person. On their yes, answer ..."; no test pinned the text |
| 19 | SIGNAL_NAME_UNUSABLE's fix let "1led" pass, which `isidentifier()` refuses | review refuter | acted | the fix says "a Python name (letters, digits and _, not starting with a digit)"; no test pinned the text |
| 20 | NO_PROJECT_FOLDER's fix "keep the requirements file inside the project folder" is false at `footprint_emitter.py:329`, where a working folder is missing | review lens (nit) and review refuter | acted | "give --project a folder that exists, or run from the project folder, with the requirements file in it"; no test pinned the text |

The rows: tests/mutations/p935-design.json.
