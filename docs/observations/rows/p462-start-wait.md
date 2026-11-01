# P462: deploy waits for a real start and finds MicroPython's port

Findings of P462 (#630), 2026-11-01, Prague, built on main 67c37600 in auto mode. Rows 1-6 are the plan, by an Opus planner with two council rounds. Rows 7-13 are the build. Rows 14-26 are the review (Sonnet reviewer and Opus refuter) and its fix round. Rows 27-31 are the fix-commit refuter (Opus) and the second fix round. Rows 32-33 are the mutation runs.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | A record field or `if chip` code chooses the reset | plan draft | rejected | esptool 5.5.0 chooses per chip: the S3's own `watchdog_reset` (targets/esp32s3.py:337-345), and the base falls back to `hard_reset` (loader.py:2218-2223) |
| 2 | The watchdog reset works after a BOOT entry | plan | raised (bench) | the bench tried it only after `machine.bootloader()` (P472 bench.log 23:29:16). The RESET wait stays as the fallback. The PO's bench run after the merge settles it |
| 3 | The P461 log's "reset seen" proves a RESET press | plan | rejected | unproven. Now a restart counts only after mpremote answers |
| 4 | MicroPython's port has another name | plan | rejected | the name stayed `/dev/cu.usbmodem1101`. The USB id and serial form change, and the serial's first 6 bytes are the MAC (micropython v1.29.0 ports/esp32/usb.c:67-73) |
| 5 | No-hands download-mode entry, a "pressed RESET" input, a USB-id field | plan round 2 | rejected | cut as more than the Done-when. The entry belongs with P469 #637 |
| 6 | The C6 entered with BOOT | plan round 2 | raised (bench) | it gets the RESET wait. Untried |
| 7 | Two goldens change | plan | rejected | three: `deploy-could-not-run-no-terminal.json` also holds the write command. Only `--after watchdog-reset` changed |
| 8 | `FirmwarePlatform` takes a new init parameter | plan | rejected | its init is at the baseline, so `make_port_finder(run)` is a method |
| 9 | `BoardStartResult` holds the log lines | plan | rejected | the lines live in `BoardStartService.heard`, and the service takes `places` for the button text |
| 10 | `board_grant.mac_key` makes the match key | plan | rejected | the match lower-cases the MAC and drops its colons |
| 11 | `person_action` is set in `_deploy` | plan | rejected | `_deploy` is at its baseline, so `board_envelope.py` sets it |
| 12 | Tests patch the start clock | builder | acted | they set `DeployService.start_clock` with a cleanup (T2 baseline). It stays a class attribute, because the init is at its baseline |
| 13 | Mutation rows of `wait_for_reset` | builder | acted | dropped with the function. Rows in p213b1, p213b2, p215-facts, p243, p245 and p433 re-anchored. Older refusals in p243 and p213b2 were there on main |
| 14 | NO_RESET says the port did not come back after a restart that did | refuter, review | verified, acted | "the board still waits in download mode after 60 s" |
| 15 | On `port_gone` the `--json` envelope keeps a `watch` step with `mpremote repl` and no `connect` | refuter | verified, acted | `next` is empty and `repl_command` null on a gone port |
| 16 | Nothing stops a console read on a moved or 303a:4001 port | review | verified, acted | `board_start.console_may_be_read` skips the probe. A moved-port test asserts no probe |
| 17 | flasher.py cites bench.log 23:29:34 for the watchdog reset | refuter | verified, acted | that try ran a hard reset. The comment cites 23:29:16 and esptool's doc |
| 18 | "The other chips fall back" | refuter | verified, acted | false for the S2, C3 and P4. It names the C6 and classic ESP32 |
| 19 | A match on the vendor part of the MAC survives the tests | refuter | verified, acted | `OTHER` shares the first 3 MAC bytes |
| 20 | Trying the old port name before the MAC survives the tests | refuter | verified, acted | a test lists another board on the old name |
| 21 | A failed `devs` at the deadline becomes `port_gone` | review | acted | a failed list is asked once more before `port_gone` |
| 22 | The EPILOG states the S3 behaviour as fact | review | acted | it says the behaviour comes from esptool's source, untried after a BOOT entry |
| 23 | No test shows a moved port in `repl_command` | review | acted | a json test asserts `connect /dev/cu.usbmodem2101 repl` |
| 24 | `port_gone()` names a state, and code outside appends to `heard` | review | acted | `gone_result()` and `note()`. `POLL_S` is described as spark's own pace |
| 25 | At esptool's exit the ROM port can still be listed, and `find_port` can take it | review, refuter | raised (bench) | plausible, untried. The PO's bench run shows it |
| 26 | P472's bench.log line 52 holds the full MAC | refuter | acted | masked on the P472 branch. The PO squash-merges #645 so that the old commit stays out of main |
| 27 | Every first-round fix holds: 9 old defects planted back, each fails a test | fix-commit refuter | verified | one survivor, a retry even when the list did not fail, costs one extra `devs` |
| 28 | A failed `devs` in the middle of the wait counts as gone, so an unmoved board looks restarted | fix-commit refuter | verified, acted | a failed list is never gone. Second fix round |
| 29 | A change from 303a:1001 to 303a:4001 between two polls is not a restart, so NO_RESET can be false | fix-commit refuter | verified, acted | a change of the USB id counts as gone and back. Second fix round |
| 30 | The EPILOG, deploy.md and agents.md say the console is read whenever ready is unknown | fix-commit refuter | verified, acted | they say: on the look's port, unless it is 303a:4001 |
| 31 | The EPILOG credits esptool's source for leaving download mode | fix-commit refuter | verified, acted | the source only sets the watchdog. The troubleshooting page says it |
| 32 | Mutation run on d01d4713: 102 planted, 101 caught, 4 refused | mutation-tester | acted | 2,479 s over six whole tables. The escape: no test checked `person_action` after a restart that counted. The moved-port json test asserts it is None. The 4 refusals were older rows. The escape and the second round's rows ran again on the head |
| 33 | Re-run of the escape and the second round's 3 rows on the head: 4 planted, 3 caught | mutation-tester (lead) | acted | 670 s. "the wait is not told the port's USB id" escaped: the wait took its first listing as the baseline. A gate test changes the id before the wait's first listing. It passes, and it fails with the mutant planted by hand |
