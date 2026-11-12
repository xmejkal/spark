# P333: one board on two USB nodes is one board, findings rows

Findings from the plan council, the build and the review of P333 (2026-10-26, Prague, auto mode).

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The other node works for esptool and mpremote | build | raised | not run: only `/dev/cu.usbserial-<serial>` was read on the bench (2026-10-26). The PO's bench can try `/dev/cu.SLAB_USBtoUART` — P776: waits on the PO: Needs the PO's bench to try /dev/cu.SLAB_USBtoUART with esptool and mpremote. — P776: waits on the PO: Needs the PO's bench to try /dev/cu.SLAB_USBtoUART with esptool and mpremote. |
