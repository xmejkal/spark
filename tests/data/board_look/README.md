Fixtures for tests/test_board_look.py.

- c6-flash-id.txt, wrong-chip.txt, mpremote-devs-one.txt: the real P228 bench outputs
  (docs/discovery/2026-10-13-p218-deploy-and-board/bench/p228/), trimmed, the MAC masked as xx.
- mpremote-devs-with-bluetooth.txt, mpremote-devs-two.txt: the real one-board line, with the 0000:0000 rows macOS
  lists, and a second CH340 line in the same format. Hand-written, not a bench output.
- esp32-classic-flash-id.txt, s3-flash-id-*.txt, c6-flash-id-kb.txt: hand-written in esptool's format. No classic ESP32
  or FireBeetle S3 was on the bench.
- A failed connect ("Failed to connect") has no fixture: the test for it feeds any non-zero exit and reads no output.
- The C6 fixtures come from `flash-id` (hyphen) on the bench, and the code runs `flash_id` (underscore, which esptool
  5.5.0 still accepts). P219 step 3's recorded run on the PO's XIAO settles whether the output is the same.
