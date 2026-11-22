# P1007: the check after the flash reaches the FireBeetle 2 C6's raw REPL: rows

Card: [P1007 #1466](https://github.com/xmejkal/spark/issues/1466). The cause comes from the bench on the PO's C6,
2026-11-22 14:54 to 15:18 CET (comments on the card, and the diary of the p934-display2 walk). The plan check: a lens
on Sonnet and the refuter on Opus, one round. This file holds the acted, raised and rejected findings only.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | mpremote's early Ctrl-C and Ctrl-A, sent while its open restarts the C6, leave MicroPython deaf to the host until a ROM download | the bench, 15:08:08 | acted | `QuietBoardConnection`: mpremote runs through `QUIET_MPREMOTE`, which opens with DTR and RTS off and sends nothing for `SETTLE_S` (2.5 s, 9 of 9 bench runs). Rows 4 and 5 |
| 2 | rebuild nothing of mpremote: patch its open and its raw-REPL entry, then run `mpremote.main` | plan lens 1 | acted | `QUIET_MPREMOTE` keeps mpremote's words, exit codes, soft reset and flushed output. Bench: exec, fs cp, fs cat, a traceback, `import main` for 20 s and reset (15:13 to 15:14) |
| 3 | the fake platform's `make_connection` lacks `usb` | plan lens 2 | acted | `tests/fakes.py` |
| 4 | each caller must pass its row's USB id | plan lens 3 | acted | `reach_board`, `run_live_code` (`row.usb`), `deploy_service` (row 8) |
| 5 | the board shell's Python must come from the tool, not from slicing the command | plan lens 4 | acted | `make_connection` reads `find_tool("board-shell")` and its kind, as `ConsoleProbe.for_tool` does. Rows 1 to 3 |
| 6 | the settle and a vanished port's wait eat the 20 s limits | plan lens 5, refuter 5 | acted | `EXTRA_S` (16 s) is added to the call's limit and to `keep_running_for`. A deploy's `import main` read takes 36 s now. Rows 4 and 5 |
| 7 | a hand-built script loses unflushed output at the time limit | plan lens 6, refuter 4 | acted | mpremote's own `stdout_write_bytes` flushes. Bench: `ready` kept when the read was stopped at 20 s |
| 8 | "holds the chip in reset" is not proven: at 15:08:08 mpremote read `ready` with DTR and RTS on | refuter 1 | acted | the card's comment is corrected; the docs say "restarted" |
| 9 | the hand-built script skips mpremote's soft reset | refuter 2 | acted | gone with row 2: mpremote's own entry runs |
| 10 | the deploy keeps the USB id of its first listing, so an S3 that leaves download mode (303a:1001 to 303a:4001) gets the quiet open, which a TinyUSB console does not answer | refuter 3 | acted | `BoardStartService.usb_of`: each read asks the list for the port's id at that moment. `test_board_start` and `test_deploy_gate.test_each_read_uses_the_usb_id_the_port_has_then`; rows 7 and 8 |
| 11 | choosing by 303a:1001 is unsafe for other boards | refuter 6 | rejected | the refuter's own check: CP210x and CH340 boards keep plain mpremote, the XIAO C6 has the same USB-Serial/JTAG |
| 12 | a person's own mpremote call can still leave the C6 deaf before a reach or a live run | the bench | raised | said in commands/deploy.md and the agents' never-assume page. P1005 #1464 (a live connection in spark) holds the person's console |
| 13 | why the early bytes leave the input deaf inside the chip | the bench | raised | not proven, and the fix avoids the cause. Dropped because the MVP needs no more |
