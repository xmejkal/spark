# P215 council, refuter (2026-10-14)

Read locally: esptool 5.5.0 (in `~/.local`), mpremote 1.29.0, MicroPython v1.29.0 `ports/esp32` from its tag.

## 1. Hardware lens claims

| Claim | Verdict | Where |
|---|---|---|
| 1 `--after` modes | confirmed | `esptool/__init__.py:427-434` |
| 3 USB path waits 0.2 s | confirmed | `reset.py:132-147`, `esp_pylib/serial_reset.py:394-416` |
| 4 no `uses_usb`, "likely cause" | code confirmed, cause refuted | `cmds.py:2832`, `loader.py:2180`. A new mpremote process takes over 0.2 s to start. After the replug (step 6) no esptool ran, and mpremote still got nothing. |
| 2 try `--after watchdog-reset` | refuted for the C6 | `targets/esp32c6.py:19` (`WATCHDOG_RESET_SUPPORTED = False`). Lines 206-209 fall back to the RTS reset. |
| 8 output dropped after 200 ms | confirmed | `usb_serial_jtag.c:113-121`. `terminal_connected` starts false (`:43`). |
| 8 RX unsafe (H) | partly | Ctrl-C is checked byte by byte (`:56-58`). The code reads only as many bytes as the 260-byte stdin ring has free (`:51-55`, `mphalport.c:57`). |
| 9, 10 open with defaults, no retry | confirmed, one fix | `transport_serial.py:52-102, 178-210`. `b''` goes to **stdout** (`:194`) and the error goes to stderr (`main.py:640`). AT132 must keep both. |
| 11 stale handle (H) | weak | Each mpremote call opens the path again. `usbmodem101` names the USB location, not the device. |

## 2. Contradictions

- **Re-check.** The architecture lens appends `kind: "recheck"`. The user lens has `--check` "upgrade" the unknown.
  Appending wins: records are facts, and `remember()` appends. Both miss that a failed copy leaves no `spark.json`,
  so a read-only re-check cannot pass. It must write the file when missing.
- **Wait bound.** The lenses give 10+20 s, 15+2 s × 3, and "the bound". None was measured, and steps 5 to 8
  waited minutes with no answer.
- **Re-resolve by VID:PID.** The evidence favours the architecture lens: the path stays the same. A hard-coded
  `303a:1001` would also be logic written for one part.
- **Retries.** Architecture retries only a probe, and is right: the user lens's retried read reruns `import main`.

## 3. Against AGENTS.md, or too big

- User lens: "the red LED is the charge LED" has no source.
- Architecture steps 4 and 5 (`Deploy`, `DeployResult`) are not the bench fix and lean toward v2, #94.
- Tests lens: `FakeBoard` phases, `FakeClock` and four fixtures are more than a first fix needs. The fixtures must
  hold no home path and no MAC.

## 4. Unexplained

- Steps 7 and 8. A guess (H) from the source: `light.run()` never reads stdin, so every try fills the 260-byte ring.
  When the ring is full, the ISR reads nothing, so Ctrl-C never reaches `:57`. A reset empties the ring, which fits
  "worked right after boot". It does not explain step 6.
- Step 6: a fresh enumeration failed, but step 9's worked.
- The log holds neither the board's state nor the bytes sent, so no theory can be tested.

## The smallest first fix

Only two sequences reached the console: step 7 (port open, then reset, then read) and step 9 (the device came back
with the port open). So after esptool, deploy.py opens the port with pyserial (mpremote already needs it), pulses
RTS and reads until `ready` or 20 s, taking `[Errno 6]` as "came back". Then it runs today's mpremote steps once.
About 20 lines in one class; the boot text goes to the log. **This is H.** To prove it, run five deploys in a row on
the board: each must say `ready seen` with `rst:0x15` in its log. One run with the step off must give `ready unknown`.

## Follow-up stories, in order

1. AT132: keep mpremote's stdout and stderr, the last line in the sentence and all of it in the log.
2. Bench spike: a logged matrix (hard reset with mpremote every 1 s for 60 s; open the port, then pulse RTS;
   replug). Record the bytes sent and the board's state (AT133).
3. The smallest first fix, if the spike supports it.
4. `--recheck`: it appends, and writes `spark.json` when it is missing (AT134).
5. AT135: the flash size, with its source. AT136: the PO names the LED.
6. Architecture steps 1 to 4 as a refactor, once stories 1 to 4 are green.
