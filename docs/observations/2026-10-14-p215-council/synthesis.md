# P215 bench council: the synthesis

Five agent runs on 2026-10-14: four lenses on Sonnet (hardware, architecture, user, tests) and a refuter on Opus. The
bench log is [../2026-10-14-p215-bench.md](../2026-10-14-p215-bench.md).

## The short version

The flash works. After esptool's reset, the XIAO ESP32-C6's USB console did not answer mpremote, and the cause is
not proven. Two facts are confirmed in the sources: esptool's reset after a write does not use its USB mode
(`esptool/cmds.py:2832`, `loader.py:2180`), and MicroPython drops console output that no host reads within 200 ms
(`ports/esp32/usb_serial_jtag.c:113-121`, v1.29.0). Neither explains why a replug, with no esptool, also got no
answer. The refuter's guess, not tested: the firmware never reads its input, so the input buffer fills and a Ctrl-C
no longer gets through, and a reset empties it. The `--after watchdog-reset` option falls back to the same reset on
the C6 (`esp32c6.py:19`, `:206-209`), so it is no fix.

## Settled by the evidence

- Keep mpremote's stdout and stderr in the sentence and the board log. mpremote prints `b''` to stdout and the error
  to stderr (refuter, `transport_serial.py:194`, `main.py:640`).
- Retry only the probe that the board answers, never `import main` and never esptool (architecture, refuter).
- A re-check adds a new entry to the store and keeps the earlier `unknown` (architecture, refuter). It writes
  `spark.json` when it is missing, because a failed copy left none (refuter, which every lens missed).
- No layer that finds ports by USB id now: the port name stayed the same (refuter).
- No wait bound is chosen by guess: the bench measures it.
- The red LED is not the firmware's: nothing was wired. Which LED it is waits for the PO (no source names it).

## The proposed order

1. Keep mpremote's words (AT132), with the small refactor: one `BoardLink` class, the one mpremote connection to a
   board, which `BoardFacts` and `BoardReady` both use. It raises an error that holds mpremote's stderr.
2. A bench spike (AT133): a logged matrix of reset and connect sequences on the XIAO. It records the bytes sent and
   what the board answered, and it measures how long the console needs after esptool's reset.
3. The fix that the spike supports, test-driven with one fake board that stays silent for a set number of reads and a
   fake clock. The refuter's smallest candidate: after esptool, open the port, pulse RTS, read until `ready`, then
   run the mpremote steps once. Proof: five deploys in a row, each `ready seen`.
4. `deploy.py --recheck` (AT134): no erase and no yes. It writes `spark.json` when it is missing, runs the ready
   check and adds a store entry.
5. The XIAO record's flash size with its source (AT135), so the look stops exiting 2 for it.
6. The `Deploy` object out of `deploy.main`, when `--json` (P213) needs it. Until then it leans toward v2 (#94).

## Questions for the PO

- Is this order right, and do steps 1 to 5 stay steps of P215, with step 2 as a spike card?
- Does the spike use button-light as it is, or a board-only blink (P236, #233)?
- The user lens asks: how long may deploy.py wait for the board before it says unknown? The spike gives the number.
