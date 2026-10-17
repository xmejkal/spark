# P239 PR 5: ProjectImage (#238)

## Context

PR 5 of the synthesis (docs/observations/2026-10-14-p239-oo-council/synthesis.md, section e). PRs 1-4 are merged. I read
main at 7554792. `--help`, exit codes, the store record and every printed sentence do not change.

| Item | On main | Touches |
|---|---|---|
| `ProjectImage` | image_check.py: five functions on `(image, runs)`, three hash the image again | image_check.py, deploy.py, board_look.py |
| `command_for` | `runnable(tool)` sits in image_check but is about a tool | tools.py, deploy.py, board_look.py, reach.py, live.py |
| `BOOT_HINT` | sits in image_check, is about esptool | board_look.py, deploy.py |
| `DeployError` | `DeployProblem` | every raiser and catcher |

## Council

Round 1 (tech lead, refuter) changed:
- The constructor does only `image_of`'s two checks and reads no log, so no gate step gets a new error path.
- `sha256` is a `cached_property`; only "a new `ProjectImage` gives the new hash" is tested. Logs are read on each call.
- The Value row in developing.md allows a method that reads files and never writes.
- `main` builds a fresh `ProjectImage` after the flash. `board_facts.facts` still hashes the file itself (not this PR).
- Added: test_ready_check.py:19,95, the deploy.py:44 re-exports go, both `Look.run` cases tested, `DeployError` caught at
  deploy.py:204, 222, 235, and p219-de2.json finds change text.
Round 2 (tech lead, PO-assistant) changed:
- Method names start with a verb: `read_run_logs`, `find_passed_log`. `command_for` stays (the synthesis's name, as `chip_of`).
- `write_board_log`'s caller takes the hash from the fresh `ProjectImage.sha256`; `main` builds one at deploy.py:218 and
  one after the flash (:235), and calls `.find_passed_log()` there. test_board_look.py:17 imports `project_image`.
- The `find_passed_log` row leaves p215-ready.json (moved to p239-pr5.json); `--anchors` runs on both tables.
- The plan is cut to about 90 lines.

## Design

```
 deploy.main / board_look.Look.run
   |-- ProjectImage(project) ---- Value  path, sha256 (cached), runs
   |      .why_untested() -> str|None     .why_other_runs() -> str|None
   |      .find_passed_log() -> Path|None .read_run_logs() -> [(log, verdict, sha256|None)]
   |      raises DeployError (built without toml/image, or a log is unreadable)
   |-- tools.command_for(tool) -> list     (was image_check.runnable)
   `-- board_look.BOOT_HINT                (was image_check.BOOT_HINT)
 image_check.py is deleted; project_image.py holds ProjectImage and DeployError.
```

| Name | Role word | File | Job |
|---|---|---|---|
| `ProjectImage` | Value | project_image.py | The flash image `sim/wokwi.toml` names and the run logs in `sim/runs/` that name it. Its methods read the project's files and never write. |
| `DeployError` | Error | project_image.py | Why the image cannot go on the board yet. Replaces `DeployProblem`. `ProjectImage` raises it and deploy.py and board_look.py already import that module, so deploy.py keeps `deploy.DeployError`. |
| `command_for` | function | tools.py | The command that runs a Tool. Replaces `runnable`. |
| `BOOT_HINT` | constant | board_look.py | What to try when esptool cannot reach the board. The synthesis says "beside the flasher"; no `Flasher` exists until PR 7, so it sits with `EsptoolReader` and PR 7 moves it. |

| Old | New |
|---|---|
| `image_of(project)` | `ProjectImage(project).path` |
| `run_logs(runs)` | `.read_run_logs()` |
| `untested(image, runs)` | `.why_untested()` |
| `tested_another(image, runs)` | `.why_other_runs()` |
| `passed_log(image, runs)` | `.find_passed_log()` |

`Look.run` builds one `ProjectImage` and catches `DeployError` twice: on building it (`image` None) and on an unreadable
log (`image` stays set for the fit check). `Report` keeps carrying a `Path`, so look.py and the token do not change.

## Tests first (red before the fix)

1. tests/test_project_image.py (new): the old behaviours by name. No toml, no image, a passed log, a failed log, a log of
   another image, a log of an older spark (no sha256), an unreadable log, a path that is no file; a new `ProjectImage`
   after the file changed gives the new hash; an unreadable log does not stop the constructor. test_ready_check.py's
   `PassedLogTest` moves here (a project with a toml). Red today: no module.
2. test_tools.py: `command_for` gives `command + ["-m", module]` for a Python tool, else the command.
3. Existing tests take the new names: `deploy.DeployError`, `project_image.run_scenario.run_record` (and the import at
   test_board_look.py:17), and the `find_passed_log` patch in test_deploy_gate.py:276 on `ProjectImage` (`lambda *a`
   still works, `self` is an argument). test_board_look.py pins both `Look.run` cases.
4. `DeployProblem` appears nowhere.
5. tests/mutations/p239-pr5.json: `find_passed_log` ignores the verdict, `why_untested` accepts a failed log,
   `why_other_runs` ignores a log with no sha256, `command_for` drops `-m`, `Look.run` loses the image on an unreadable log.

## Verification

- Re-anchor p215-ready.json (row leaves), p219-reader.json:95-102, p219-de2.json:47-60 (text changes) and p215-facts.json:29.
- `python3 tools/mutate.py --anchors` passes on every table I change. Rows stale on main stay for P284 (#331).
- The suite and the push hook pass.

## Docs

developing.md: the Value row allows a reading method; "Until PRs 5 to 8" moves PR 5 to the merged list; the Error
examples add `DeployError`. Docstrings board_connection.py:51 and board_look.py:5 name `command_for` and
`project_image.py`. agents.md and the commands pages name none of the moved functions. Historic plans keep old names.

## Out of scope

`DeployToken` and `LookReport` (PR 6), `Flasher` (PR 7), `DeployService` (PR 8). `ToolProblem` keeps its name until
v0.13 (#94). No change to `--json`, exit codes or sentences.
