# P192 final review, 2026-10-12

One reviewer (Opus) read the whole branch `p192-deploy` against the cards [P192 (#144)](https://github.com/xmejkal/spark/issues/144) and [P193 (#145)](https://github.com/xmejkal/spark/issues/145) and the plan (`docs/2026-10-12-p192-deploy-plan.md`). It changed nothing. A Sonnet implementer made the fixes on the same branch.

Verdict before the fixes: not ready, because of one bug (DE1). The fix commits call the findings R1 to R9. The cards were met. `tools.py --status` lists `flasher` and `board-shell`, a test pins the dry run's flash lines, P193's dry run always prints a line, and the journey test reaches the deploy stage. The journey ran in full, with the build.

## Findings

| ID | Severity | Finding | Outcome |
| --- | --- | --- | --- |
| DE1 | should-fix | `deploy.untested()` read the logs beside the image, but `run_scenario.py` writes them to `sim/runs/`. An image in a subfolder of `sim/` whose run passed was refused, with a wrong reason. Reproduced with `firmware = "images/flash.bin"`. | acted: the logs come from `<project>/sim/runs/`, with a test. |
| DE2 | should-fix, the PO's call | A log that tested another image was ignored. Scenario A failed on image X, the firmware changed, only B ran and passed on Y, and deploy flashed Y without a word about A. | acted as a note, not a refusal: deploy names each log that tested another image. Refusing instead is the PO's call. |
| DE3 | note | A log that cannot be read crashed deploy with a traceback (a folder named `x.log`). | acted: a path that is not a file is skipped, and a read error is a sentence. |
| DE4 | note | `commands/build.md` gave `mpremote connect <port> repl`, but deploy prints `python -m mpremote ...`, and a bare `mpremote` is often not on the PATH after `pip install --user`. | acted: the page points at the line deploy prints, and says that the port name can change after the flash. |
| DE5 | note | `commands/build.md` did not name the log's new sha256 line. | acted. |
| DE6 | note | The README's Bench row named no command. | acted: `deploy.py`. |
| DE7 | note | `deploy.py`'s `--port` help had a semicolon. | acted. |
| DE8 | note | `_deploy` in the journey test had no test that proves it goes red. | acted: a test, in the style of `_run_log`'s. |
| DE9 | note | `tools.py` finds a `kind: python` tool by its module and never compares it with its pin. Here esptool 3.3 reads as "already here" although the pin is 5.5.0. This behaviour is older than P192. | raised. deploy's commands work on esptool 3.3 to 5.5 (decision 4 of the plan), so nothing breaks today. A version check for Python tools is a card of its own if the PO wants one. |

## What only the bench can answer (item c)

- MicroPython's ESP32-S3 build probably brings its own USB serial port, and esptool talks to the chip's built-in one. The port name can then change after the flash. The reviewer is about 75% sure.
- Whether esptool can put a board that runs MicroPython into its bootloader by itself, or whether the person must hold BOOT and press RESET every time.
