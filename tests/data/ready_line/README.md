Fixtures for the ready line (P1025): tests/test_ready_probe.py, tests/test_board_console.py and tests/test_deploy_gate.py.

- c6-console-2026-11-22.txt: what the XIAO ESP32-C6's console printed after a deploy in the P934 walk, on
  2026-11-22 at 23:22 CET. It is lines 8 to 15 of that walk's board log `sim/runs/board/2026-11-22T23-22-01.log`. The
  board log's prefix `console with DTR and RTS off: ` is taken off line 8. No other line is copied. The lines after
  it hold mpremote's traceback, so they stay out. The last line, `ready, cpu 80 MHz`, is the firmware's ready line.
