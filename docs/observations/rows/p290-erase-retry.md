# P290 erase retry: findings rows

The plan councils of P290 (#347). Plan: [`plan.md`](../../discovery/2026-10-18-p290-erase-retry/plan.md).

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | A retry of any command hides a real fault in the write, and the card names the erase | tech lead, round 1 | acted | only the first command is retried |
| 2 | Exit 2 is every esptool stop (a failed connect, a missing port, a wrong chip, a usage error), so a line that names the connect as the cause can be false | tech lead and refuter, round 1 | acted | refuter ran them on esptool 5.5.0; the line names the exit code |
| 3 | A deploy grant can end during the 5 s wait | refuter, round 1 | acted | `consent.require_ready()` before the retry; a test |
| 4 | Tests that pass `fails=True` would succeed after the retry | refuter, round 1; round 2 | acted | `fails` counts failures; the callers pass 1 or 2 |
| 5 | A fixed wait before every erase is safer | refuter, round 1 | rejected | it costs 5 s on every deploy; the retry costs time only on a failure |
| 6 | A Ctrl-C during the wait prints no `--json` envelope | refuter, round 1 | closed | the same gap exists today for any step (`deploy.py:174-196`); no card |
| 7 | Generic service code must not name esptool in the retry line | round 2 | acted | `Flasher.RETRY_LINE` |
| 8 | "retry", "again" and "once more" named one thing | round 2 | acted | "retry" everywhere |
| 9 | The service test `test_a_failed_flash_is_a_deploy_error_with_the_sentence_and_the_hint` would wait 5 s for real | the full suite | acted | its case patches `DeployService.sleep` |
| 10 | A yes that ends during the wait gave `stage: gate` and "not flashed", but the first erase ran and can stop halfway with exit 2 | refuter, PR review | acted | `_run_flash` raises a `FlashError`: `stage: flash`, `board_state: may_be_erased`; a gate test and a `--json` test |
| 11 | Two tests bound `problems` and never used it | reviewer, PR review | acted | removed |
| 12 | The mutation run: 12 planted, 12 caught | mutation tester, PR review | closed | `tools/mutate.py --copy`, the whole suite, 411 s |
| 13 | The bench, 2026-10-18 14:32 to 14:35 Prague, XIAO ESP32-C6, blink-c6, a 30-minute deploy grant: 3 deploys of 3 exit 0 with `ready seen`; no erase needed the retry, so the bench did not reproduce the failed connect | the PO's bench | closed | board logs `sim/runs/board/2026-10-18T14-33-07.log`, `14-34-18.log`, `14-35-14.log` in blink-c6 |
| 14 | The `yes: standing yes typed by ...` line prints its times in UTC (`+00:00`), not in the person's zone | the PO's bench | acted | card P315 #393 in Idea |
| 15 | The board-log names and row 13's Prague times can disagree if the log moment is UTC | reviewer, PR #394 | rejected | the moment is `datetime.datetime.now()`, the machine's zone (`deploy_service.py`, `verify`); the logs `14-33-07` to `14-35-14` match the clock at the run, 14:32 to 14:35 |
