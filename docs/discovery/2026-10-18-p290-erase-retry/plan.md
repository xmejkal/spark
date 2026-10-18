# P290 (#347): deploy retries esptool's erase once

## Council

Round 1 ran: a tech lead and architecture lens (Sonnet) and a refuter (Opus). It changed the plan in five ways.

- Retry the erase only, as the card says, because a failed write after a good erase can be a real fault.
- The retry line names the exit code, not a cause. Exit 2 is every esptool stop: a failed connect, a missing port,
  a wrong chip, a usage error (refuter ran them on esptool 5.5.0).
- The grant can end during the wait, so `consent.require_ready()` runs again before the second erase.
- The tests count failing erases (`fails=1`, `fails=2`), and a flasher with no retry code never retries.
- The refuter rejected a fixed wait before every erase: it costs 5 s on each deploy, and the retry costs time only
  when the connect fails.

Round 2 ran: the PO's assistant, the tech lead and a senior engineer, in one Sonnet agent. It changed four things.

- The flasher, not the service, holds the retry line (`RETRY_LINE`), because generic code must not name esptool.
- The flasher's docstring says that only the first command, its erase, is retried.
- The fake fails the first plan command by position, not by the name `erase_flash`, so the no-hint flasher's test at
  `tests/test_deploy_gate.py:229` still fails. A separate `write_fails` covers the failed write.
  `tests/test_deploy_json.py:192` also passes `fails=2`, and both test helpers patch the sleep.
- One word: "retry" in the constants, the line and the docs.

## Context

At the PO's bench run of P242 on 2026-10-18, the first `deploy.py` failed at `esptool ... erase_flash` with
"Failed to connect to ESP32-C6: No serial data received". Deploy's own look had just reset the board (`flash_id`
ends with esptool's hard reset). The same command 5 s later connected. The card asks for one retry, on esptool's
exit code, named in the output, with tests for one failure then success and for two failures. It is done at the
bench when 3 deploys of 3 go through on the first call.

esptool 5.5.0 exits with code 2 for every `FatalError` (`esptool/__init__.py:1374`), and the connect failure is one
(`esptool/loader.py:916`). A second erase is idempotent (it has the same result when run twice), so a retry on exit 2
is safe. spark never compares esptool's English text.

## Design

```
DeployService.deploy                         Flasher (strategy)
  for index, command in plan.commands:         RETRY_EXIT_CODE = None   (never retry)
    run(command)                               RETRY_WAIT_S = 0
    on CalledProcessError:                   EsptoolFlasher
      index == 0 and                           RETRY_EXIT_CODE = 2   (every esptool stop, a failed connect among them)
      code == flasher.RETRY_EXIT_CODE:         RETRY_WAIT_S = 5      (one bench observation, 2026-10-18)
        show_line(retry line)
        sleep(RETRY_WAIT_S)
        consent.require_ready()
        run(command) once more
      else, or it fails again: FlashError, as today, with BOOT_HINT
```

The flasher knows what its tool's exit code means and how long to wait. The service owns the loop. The wait is a
class attribute, `DeployService.sleep = staticmethod(time.sleep)`, the idiom of `board_console.SystemClock`
(`board_console.py:83`), so the tests patch it and `deploy.main` keeps its arguments.

The retry line is `EsptoolFlasher.RETRY_LINE`, formatted with the command and the code, and goes through
`show_line` (stderr under `--json`):
`  retry in 5 s: <command> stopped with exit 2 (esptool's exit for any stop, a failed connect among them)`.
The base `Flasher` has `RETRY_LINE = ""` and never retries.
The `--json` envelope gets no new field: a retry that worked is a normal deploy.

## Steps (typed task sub-issues of #347, R9 theme 6)

1. Test.
   - tests/test_deploy_gate.py: the fake `run` takes `fails=0`, the number of times the first plan command exits
     with `fail_code=2` before it succeeds, and `write_fails` for the later commands. The `deploy` helper here and the
     helper in tests/test_deploy_json.py patch `deploy_service.DeployService.sleep`, so no test waits.
   - One failure then success: exit 0, flashed `["erase_flash", "erase_flash", image]`, one retry line, sleep(5).
   - Two failures: exit 2, flashed `["erase_flash", "erase_flash"]`, one retry line, the BOOT hint
     (`test_a_failed_erase_writes_nothing_and_says_what_to_try` passes `fails=2`).
   - Exit 1: no retry. OSError: no retry. A failed write: no retry.
   - A grant that ends during the wait: no second erase.
   - The test at `:229` with a flasher that has no hint passes `fails=1` and sees no retry.
   - tests/test_flasher.py: `Flasher` has no retry code. `EsptoolFlasher` has 2 and 5.
   - tests/test_deploy_json.py: a success after one retry gives the usual envelope, and the retry line is on stderr.
     `test_a_failed_flash_says_the_board_may_be_erased` (`:192`) passes `fails=2`.
2. Implementation: scripts/flasher.py (`RETRY_EXIT_CODE`, `RETRY_WAIT_S`, `RETRY_LINE` with their source comments,
   and the `Flasher` docstring says that only the first command is retried), scripts/deploy_service.py (`sleep`, the
   loop).
3. Docs: `commands/build.md` near lines 312 and 337, `docs/guide/agents.md` near lines 657 to 664, and the
   `deploy.py` EPILOG near lines 46 to 47. Each says that deploy makes one retry of a failed erase after 5 s,
   before the BOOT hint. The README's bench note and `tools/journey.py` change after the bench run only.
4. Bench (the PO): 3 deploys with a deploy grant on the XIAO ESP32-C6, each right after its look. The README's note
   says what he saw.

Rows file: `docs/observations/rows/p290-erase-retry.md`. Review: under 50 lines of logic, so one reviewer (Sonnet),
the refuter (Opus) and one mutation run on the branch. Work in a worktree on branch `p290-erase-retry`.

## Verification

- `python3 -m pytest tests/test_deploy_gate.py tests/test_flasher.py tests/test_deploy_json.py -q`, then the full
  suite through the push hook.
- The PO's bench run, step 4.
