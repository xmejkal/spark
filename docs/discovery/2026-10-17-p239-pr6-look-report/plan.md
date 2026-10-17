# P239 PR 6: LookReport (#238)

## Context

PR 6 of the synthesis, shrunk by the P218 brief (docs/discovery/2026-10-17-p218-finish/brief.md, item 2 and the
decision "keep, shrink PR 6"). I read main at 4414472. `--help`, exit codes, the store record and every printed
sentence do not change. `DeployToken` is dropped (the brief). `looker`, `LookStop` and `board_token` keep their names.

## Council

Not yet run.

## Design

```
 look.py main ----------+                       deploy.py main
   |                    |                          |  (no import of look)
   |   board_look.looker(project, run) -> LookService
   |                          |  .run(project, port, ignore_older_runs)
   |                          v
   |                       LookReport  Value  port, BoardReading, record, image, image_why
   |                          .verdict .status .exit_code() .token() .no_token_reason()
   |                          .to_dict()   (new: the facts as plain JSON values)
   `--- board_look.report_lines(report, token=True) -> [str]    (was look.lines)
 BoardReading = namedtuple chip flash_mb mac       (was Reading)
```

| Old | New | Role | Job |
|---|---|---|---|
| `Report` | `LookReport` | Value | What the look found: the reading against the record, the verdict, the token. Its methods only calculate. |
| `Look` | `LookService` | Service | The look at one project: its record, the port, the reading. Returns a `LookReport`. |
| `Reading` | `BoardReading` | Value | What esptool said: chip, flash_mb, mac. |
| `look.lines(report, token)` | `board_look.report_lines(report, token)` | function | The lines a person reads. deploy.py needs them and must not import a script. |
| `look.RESTART`, `look.TOKEN` | `board_look.RESTART_NOTICE`, `board_look.TOKEN_LINE` | constants | The two sentences `report_lines` prints. `RESTART` already means a regex in board_console.py and a copy in grant.py. |

`LookReport.to_dict()` returns `{"port", "chip", "flash_mb", "mac", "board_record", "fields", "stops", "warnings",
"unknown", "verdict", "status", "token", "no_token_reason"}`: plain strings, numbers, lists and dicts, no `Path`. It is
what `look.py --json` (P213 PR a) will print inside `outcomes.envelope`; nothing prints it in this PR. `token` is the
string or None. `image` is a path of the project and stays out: the token already names it.

## What changes where

- board_look.py: the three renames, `report_lines`, its two constants, `to_dict`. The docstring names the new classes.
- look.py: loses `lines`, `RESTART`, `TOKEN`; `main` calls `board_look.report_lines`. Its imports shrink.
- deploy.py: `import look` goes, and the call at line 214 uses `board_look.report_lines`. Two lines in a file P242
  (PR #342) also edits; a merge conflict, if any, is those two lines. deploy_gate.py and board_grant.py are not touched
  (deploy_gate reads `report` by duck type: `verdict`, `stops`, `warnings`, `token()`).
- Tests: test_board_look.py takes `BoardReading`; test_look.py keeps testing `look.main`'s output.

## Tests first (red before the fix)

1. test_board_look.py: `board_look.BoardReading(...)` in the parser and compare tests (red: no such name).
2. test_board_look.py: `LookReport.to_dict()` for a match, a stop, and a warning with an unknown field and no token:
   exact dict, `json.dumps` accepts it, and `token` equals `report.token()`.
3. test_board_look.py: `report_lines(report)` has the token line, `report_lines(report, token=False)` has none; the lines
   equal what `look.main` prints (test_look.py already pins the sentences).
4. A test that deploy.py does not import `look`: its import names (read with `ast`) hold no `look`, so the seam stays.
5. `Report`, `Look`, `Reading` (as classes) and `look.lines` appear nowhere in scripts/ and tests/.
6. tests/mutations/p239-pr6.json: `to_dict` drops `status`, `to_dict` leaves out `no_token_reason`, `report_lines` prints
   the token line when `token=False`, `report_lines` loses the stop lines, `report_lines` drops the unknown-field plural.

## Verification

- `python3 tools/mutate.py --anchors` on p239-pr6 and on every table whose `find` text moves (p219-reader.json holds
  board_look rows; p239-pr5 `Look.run` row; p251-reach.json:63). p215-ready, p219-reader, p215-facts, p219-de2 were stale
  on main (P284, #331): their stale rows stay.
- The suite and the push hook pass. A real look on the XIAO is the PO's bench step; test_look.py pins the text.

## Docs

developing.md: the paragraph at "Until PRs 6 to 8 merge" moves PR 6 to the merged list and drops `Report`, `Reading`
and `Look` from the old names; the Value examples already name `BoardReading`. agents.md and the commands pages name none
of the renamed classes (checked by grep). Historic plans keep old names.

## Out of scope

`Flasher` (PR 7), `DeployService` (PR 8), `look.py --json` (P213 PR a), `DeployToken` (dropped).
