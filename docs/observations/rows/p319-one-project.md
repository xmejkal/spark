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
