# P239 PR 5: ProjectImage (#238)

## Context

PR 5 of the synthesis (docs/observations/2026-10-14-p239-oo-council/synthesis.md, section e). PRs 1-4 are merged. I read
main at 7554792. `--help`, exit codes and the store record do not change. No printed sentence changes.

| Item | On main | Touches |
|---|---|---|
| `ProjectImage` | image_check.py holds five functions, each takes `(image, runs)`, and three of them hash the image again | image_check.py, deploy.py, board_look.py |
| `command_for` | `runnable(tool)` sits in image_check but is about a tool | image_check.py, tools.py, deploy.py, board_look.py, reach.py, live.py |
| `BOOT_HINT` | sits in image_check, is about esptool | board_look.py (esptool's reader), deploy.py |
| `DeployError` | `DeployProblem` | all raisers and catchers |

## Council

Round 1 ran: tech lead (Sonnet) and refuter (Opus). It changed:
- The constructor does only `image_of`'s two checks (toml, image file). It never reads `sim/runs/`, so `put_facts` and the
  gate cannot get a new error path from an unreadable log.
- `sha256` is a `cached_property`. The "old hash" test is dropped: staleness is not a contract. Only "a new `ProjectImage`
  gives the new hash" is tested. The logs are read on each call (not cached); `why_untested` and `why_other_runs` stay
  separate from `passed_log`.
- Role: Value fits only if a method may read. The Value row in developing.md says so (reads, never writes).
- `main` builds a fresh `ProjectImage` after the flash and for `put_facts`. `board_facts.facts` still hashes the file
  itself: deliberate, it is facts' own job and PR 5 does not change it.
- Callers added: tests/test_ready_check.py:19,95 (rebuilt on a project fixture); the re-exports in deploy.py:44 go.
  `Look.run` keeps two tests: no image (image None) and an unreadable log (image set). `deploy.py:204, 222, 235` catch
  `DeployError`. `project_image.py` calls `run_scenario.run_record` through the module, so the patches work.
- p219-de2.json finds change text (`DeployError`, `.why_other_runs()`), not only lines.
- `BOOT_HINT` in board_look.py differs from the synthesis ("beside the flasher"): deliberate, until PR 7.

## Design

```
 deploy.main / board_look.Look.run
   |-- ProjectImage(project) ------- Value   path, sha256, runs
   |      .why_untested() -> str|None        .why_other_runs() -> str|None
   |      .passed_log()   -> Path|None       .run_logs() -> [(log, verdict, sha256|None)]
   |      raises DeployError (when built, or when a log is unreadable)
   |-- tools.command_for(tool) -> list        (was image_check.runnable)
   `-- board_look.BOOT_HINT                   (was image_check.BOOT_HINT)
 image_check.py is deleted; project_image.py holds ProjectImage and DeployError.
```

| Name | Role word | File | Job |
|---|---|---|---|
| `ProjectImage` | Value | project_image.py | The flash image `sim/wokwi.toml` names and the run logs in `sim/runs/` that name it. Built from the project. Its methods read the project's files and never write. |
| `DeployError` | Error | project_image.py | Why the image cannot go on the board yet. The message is the whole sentence. Replaces `DeployProblem`. |
| `command_for` | function | tools.py | The command that runs a Tool. Replaces `runnable`. |
| `BOOT_HINT` | constant | board_look.py | What to try when esptool cannot reach the board. |

Why `command_for`, not a verb: the synthesis names it, and it is an accessor like `chip_of` and `board_of`.

Why `project_image.py`, not `image_check.py`: the file holds a class now, and "check" no longer says what it is. Why
`DeployError` lives there: `ProjectImage` raises it, and both deploy.py and board_look.py already import that module.
deploy.py keeps the name in its namespace (`deploy.DeployError`) because it catches it.

Why `BOOT_HINT` in board_look.py: there is no Flasher class until PR 7. board_look.py holds `EsptoolReader`, the esptool
code, and deploy.py already imports it. PR 7 moves the constant with the `Flasher`.

Method map (old to new):

| Old | New |
|---|---|
| `image_of(project)` | `ProjectImage(project).path` (raises `DeployError`) |
| `run_logs(runs)` | `.run_logs()` |
| `untested(image, runs)` | `.why_untested()` |
| `tested_another(image, runs)` | `.why_other_runs()` |
| `passed_log(image, runs)` | `.passed_log()` |

`sha256` is read from the file once, when first asked, and cached (the constructor reads no log). A caller that must see a changed file builds a new
`ProjectImage` (`plan()` does, and `main` builds one after the flash). The five functions hashed the file each call.

Callers: `deploy.plan` builds one image and calls its methods. `put_facts` and `main` use `.path`. `Look.run` builds one,
and catches `DeployError` twice: when building it (no image: `image` stays None) and when a log is unreadable (`image`
stays set for the fit check). The `Report` keeps carrying a `Path`, so look.py, deploy_gate.py and the token do not change.

## Tests first (red before the fix)

1. tests/test_project_image.py (new): the five old behaviours by name on the class. No toml, no image, an image with a
   passed log, a failed log, a log of another image, a log of an older spark (no sha256), an unreadable log, a path that
   is no file. Red today: the module does not exist.
2. The same file: `sha256` is the file's hash, and a new `ProjectImage` after the file changed gives the new hash. A
   constructor test: an unreadable log does not stop `ProjectImage(project)`.
3. test_tools.py: `command_for` gives `command + ["-m", module]` for a Python tool and the command for any other.
4. test_board_look.py: `board_look.BOOT_HINT` is shown in the two esptool refusals (the tests already read the text).
5. The existing tests move to the new names: `deploy.DeployError`, `project_image.run_scenario.run_record`, the
   `passed_log` patch in test_deploy_gate.py patches `ProjectImage.passed_log`, and test_ready_check.py's `PassedLogTest`
   builds a project with a toml.
   test_board_look.py pins both `Look.run` cases (no image; an unreadable log keeps the image).
6. `DeployError` is an `Exception` whose name ends in `Error`, and `DeployProblem` no longer exists anywhere.
7. Mutation file tests/mutations/p239-pr5.json: `sha256` re-read each time is not a defect, so the finds are: passed_log
   ignores the verdict (moved from p215-ready.json), why_untested accepts a failed log, why_other_runs ignores an older
   log with no sha256, `command_for` drops `-m`, `Look.run` loses the image on a `DeployError` from a log.

## Verification

- Tables that name image_check.py or the lines of the moved code are re-anchored: p215-ready.json (file path),
  p219-reader.json:95-102, p219-de2.json:47-60, and any p215-facts.json find that names `image_of`.
- `python3 tools/mutate.py --anchors` passes on every table I change. Rows already stale on main stay for P284 (#331).
- The full suite passes, and the push hook passes.

## Docs

developing.md: the paragraph that says PRs 5 to 8 are not merged moves PR 5 to the merged list; `Error` examples add
`DeployError`. board_connection.py:51 and board_look.py:5 docstrings name `command_for` and `project_image.py`. agents.md
and the commands pages name none of the moved functions. Historic plans and observation files keep the old names.

## Out of scope

`DeployToken` and `LookReport` (PR 6), `Flasher` (PR 7), `DeployService` (PR 8). `ToolProblem` keeps its name: the `Error`
suffix spreads to the rest of the repository in v0.13 (#94). No change to `--json`, exit codes or sentences.
