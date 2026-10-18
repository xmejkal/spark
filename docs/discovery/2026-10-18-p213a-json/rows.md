# P213 PR a: findings rows (not in docs/observations/INDEX.md; P296 #358 moves rows out of it)

| id | raised | verdict | acted |
| --- | --- | --- | --- |
| p213a-1 | refuter, plan: esptool writes to fd 1, so redirecting `sys.stdout` leaves it on stdout | verified | `DeployService(echo_to=2)` passes `stdout=` to the flash run only |
| p213a-2 | refuter, plan: `effects` words outside `writes`/`network`/`deletes` | verified | `["deletes","writes"]` |
| p213a-3 | refuter, plan: a ready-unknown next step that deploys again would erase twice | verified | `watch` step, never `deploy` |
| p213a-4 | tech lead, plan: `status` and exit code can differ if `problems` only holds stops | verified | problems are the lists `LookReport.status` counts |
| p213a-5 | refuter, diff: `data.yes` was filled before the gate, so "no terminal" reported a yes | verified, real | yes set only after `service.deploy` returns (and on a flash failure) |
| p213a-6 | refuter, diff: `look.py --json` dropped the board doctor's result and parsed English | verified, real | `board_doctor.stop_answer`; `data.doctor`, `fix` from its step |
| p213a-7 | reviewer, diff: `watch` argv; stage literals; store-record error not in `notes` | verified | REPL argv, `STAGE_*` constants, notes |
| p213a-8 | reviewer, diff: `watch` fires for `ready not seen` | verified | only `ready unknown` |
| p213a-9 | refuter, diff: a LookStop inside deploy, "no token: ..." and "image changed after the yes" give an empty `next` though the sentence says run look.py | rejected for this PR: a look cannot fix a missing board, and an untested image needs a scenario | row for PR b (`/spark:deploy`) |
| p213a-10 | tech lead: a raise inside `verify` (DeployError, ToolProblem) is a traceback with no envelope; argparse errors print usage only | verified, out of scope (no change to exit codes) | documented in agents.md; card suggested: catch them in `main` with exit 2 |
| p213a-11 | refuter: the R press reaches Claude only after the wait ends (`person_action` is late) | verified, design limit | agents.md: tell the person before the run; PR b |
| p213a-12 | mutation pass: 12 planted, 12 caught, 0 escapes; unplanted: `stop_answer` branches, dry-run step, stderr routing | note | none needed |
