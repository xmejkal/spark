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
