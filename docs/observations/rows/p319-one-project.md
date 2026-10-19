# P319 one project: findings rows

The plan council and the review of P319 (#403): the build and `check_all --project` read one project.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | `inputs_for` puts `--project` back over a resolved project, so the first draft never reached the checks | plan lens and refuter, round 1 | acted | `inputs["project"]` stays the folder; the project lives in `CheckedFolder` |
| 2 | A parent root stops the folder's own `requirements.json` from being read, and its notes vanish | refuter, round 1 | acted | the helpers glob the folder and call `design.load` and `design.project_for` per file |
| 3 | Reuse the build's lookup, no second walk up | plan lens and refuter, round 1 | acted | `CheckedFolder.at` calls `boards.project_or_library` |
| 4 | `active = boards.definition_path(project)` is a dead line | plan lens, round 1 | rejected | it says "no board selection at ..." when no board is chosen (seen in the hand run) |
| 5 | Callers of `discover` or `inputs_for` break | refuter, round 1 | rejected | only `tests/test_check_all.py` calls them |
| 6 | The notes use `relative_to(project)`, and a rules file under the parent raises `ValueError` | refuter, round 2 | acted | a note under the parent is absolute |
| 7 | The test read the project from English text | refuter, round 2 | acted | `--json` has a `project` key; the tests read it |
| 8 | A mistyped `--project` walks up to a project nobody named | refuter, round 2 | acted | `could-not-run`, no `project` key, a test |
| 9 | The tests could pass on the person's own store | refuter, round 2 | acted | `SPARK_HOME` is a temp store; the part id is `p319-probe` |
| 10 | Old fixtures held `parts/` and no `.spark/`, which the build reads as no project | lead, tests | acted | the fixtures make `.spark/`, as init leaves it |
| 11 | No test for a folder in no project, and its note can be dropped silently | reviewer and mutation-tester, PR | acted | `test_a_folder_in_no_project_says_so_and_names_none` |
| 12 | `"project"` in the library case is the plugin's install path, a home path that looks like a project | reviewer, PR | acted | `null` there; agents.md says so |
| 13 | agents.md's key table omits `project`, and its wording is wrong for the library case | reviewer, PR | acted | the table and the paragraph |
| 14 | `active = boards.definition_path(project)` is a dead variable | reviewer, PR | rejected | row 4 |
| 15 | `inputs_for` called directly with a missing folder raises, `main` prints `[????]` | reviewer, PR | rejected | `main` is the one caller that prints; a library caller gets the `DesignError` with its reason |
| 16 | `"project"` echoed `--project` as typed (`.`, a symlink) when the folder is the project | refuter, PR | acted | resolved, as `design.project_for` resolves; the test compares resolved paths |
| 17 | The library note left out the parts; the agents.md sample has no `project` key | refuter, PR | acted | the note says "parts and boards"; the sample is labeled older than P319 |
| 18 | Six attacks: relative path, symlinked parent, the plugin's rules, two circuits, the JSON shape, the split helpers | refuter, PR | rejected | each reproduced and held |
| 19 | 12 planted, 9 caught: `elsewhere`, the library note and the project note escaped | mutation-tester, PR | acted | `test_the_notes_name_the_parent` and the library test; each escape fails a test now; the table in `tests/mutations/p319-one-project.json` with a 13th row for the could-not-run branch |
