# P351 refuter (Opus), walk 1 lenses

Each claim was checked in the code on p326-walk1, or by a run.

## Tech-lead claims

| Row | Verdict | Evidence |
|---|---|---|
| 1 | HOLDS | `boards.available(walk)` returns `['firebeetle2-esp32s3', 'xiao-esp32-c6']`. `check_all.py:399-404` prints that library list. The active board is resolved at :405 and never printed. Polish, and not P320 #406. |
| 5 | HOLDS | `assign_pins.py:420` writes "its polarity is not in the board record". `boards.py:422-433` checks only `gpio` and `note` in a role. The kept Seeed wiki (sha256 87ab9b88) names GPIO15 "User Light" but gives no level. The origin is the PO's bench (walk record, 2026-10-19), a weak one. Mark it "bench, schematic not read" until someone reads the kept schematic (sha256 510f3f91, R18 on GPIO15). |
| 10 | PARTLY | The fact holds: the kept wiki says "Boot GPIO9 Enter Boot Mode", The name is REJECTED: `boot_button` is not in `PIN_ROLES` (`boards.py:95`), so `validate` refuses it. `onboard_button` already exists there and in `CONFLICTING_ROLES` (`assign_pins.py:98`). Use `onboard_button` and `ONBOARD_BUTTON = 9`, as `ONBOARD_LED` does. |
| 13 | HOLDS | `stand_in/machine.py:52-55` raises ImportError for any name but Pin. `test_import_firmware.py:118` uses PWM as its example. A PWM stand-in is test code, not firmware behaviour. |
| 11 | HOLDS | `flasher.py:40` `IMAGE_OFFSET = "0x0"`. P335 #429 and P330 plan item 4 hold the fix. |
| 6 | PARTLY | The cause (the XIAO part names D0..D10, not TX/RX) is likely, unconfirmed. Polish. |
| 8 | HOLDS, but no card | A spark deploy erases the flash and writes spark.json, so item 1 closes row 8. A "clear stale files" card is REJECTED. |

## PO-UX claims

- Row 7 as the stopper: HOLDS. `ProjectImage.why_untested` (`project_image.py:57`) refuses any image with no passed log, and `deploy_service.plan` (:89-91) raises on it. `flash_image.py` builds the image without a run, so only the gate is missing.
- Fit with AGENTS.md and #431: HOLDS with one condition. The PO wrote on #431 "We really just try the things on the board". AGENTS.md forbids calling a skipped run a pass. So the deploy must say "no simulation tested this image" in the question, in spark.json and in the store record, and write no run log. What replaces the gate: the import check passes, the look matches, the person's yes to that sentence, then the ready read against the image's own files. P337 says the PO decides, so the plan asks his OK first.
- Gap C (a slot for the person's verdict): REJECTED for now. No check or stage reads it. "Records grow by need."
- Gap E (names): PARTLY. The code says "interpreter" for MicroPython (`flash_image.interpreter_path`), and "build" is `/spark:build`. Use firmware, interpreter, image.
- Gap F ("stub"): REJECTED. `scripts/stand_in/` says "stand-in" only.
- Gap B (Ctrl-X): HOLDS. mpremote leaves its console with Ctrl-] or Ctrl-X.
- Its items 3 and 6 in the slice: REJECTED. Item 6 shrinks to the ESP32 offset, for the T-Display walk.

## Duplicates searched

Rows 2 and 3 have no card (#426 keeps pins from being offered, which is not a pick). Rows 5 and 10 need no `onboard_parts`. Row 14 is #270. Row 12 is #445.
