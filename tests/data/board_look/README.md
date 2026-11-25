Fixtures for tests/test_board_look.py.

- c6-flash-id.txt, wrong-chip.txt, mpremote-devs-one.txt: the real P228 bench outputs
  (docs/discovery/2026-10-13-p218-deploy-and-board/bench/p228/), trimmed, the MAC masked as xx.
- mpremote-devs-with-bluetooth.txt, mpremote-devs-two.txt: the real one-board line, with the 0000:0000 rows macOS
  lists, and a second CH340 line in the same format. Hand-written, not a bench output.
- mpremote-devs-made-up-mac.txt: a native S3 line whose serial is a made-up MAC with no colon, as the game box's
  serial is its MAC (P920: bench.py record takes the MAC from it). Hand-written.
- esp32-classic-flash-id.txt, s3-flash-id-*.txt, c6-flash-id-kb.txt: hand-written in esptool's format. No classic ESP32
  or FireBeetle S3 was on the bench.
- s3-flash-id-16mb-other-mac.txt: s3-flash-id-16mb.txt with a made-up MAC (de:ad:be:ef:12:34, the made-up form
  of test_no_board_address), so the look reads another board than the one the goldens keep (P1032). Hand-written.
- c6-flash-id-kept-mac.txt: c6-flash-id.txt with the masked MAC of the board the goldens keep (dc:da:0c:xx:xx:xx), so a
  deploy reads the kept board and stops at its chip, an esp32c6 for an esp32s3 project (P478). Hand-written.
- A failed connect ("Failed to connect") has no fixture: the test for it feeds any non-zero exit and reads no output.
- The C6 fixtures come from `flash-id` (hyphen) on the bench, and the code runs `flash-id` too. P219 step 3's recorded run on the PO's XIAO settles whether the output is the same.
