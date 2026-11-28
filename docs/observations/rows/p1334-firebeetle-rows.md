# P1334: the FireBeetle 2 ESP32-S3's header rows, on the edge the board has them

Card: [P1334 #1913](https://github.com/xmejkal/spark/issues/1913). This file holds the acted, raised and rejected
findings only. 2026-11-28.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | The two records compared with their makers' pinouts. `firebeetle2-esp32s3`: DFRobot's wiki pinout, board pictures, STEP model, schematic V1.3 and dimension drawing V1.3 show the 14-pin row on the left (parts up, USB-C near); the record had the 18-pin row first. `xiao-esp32-c6`: the sheet matches Seeed's front pinout (compared 2026-11-27, no mirror), but the footprint looks mirrored on paper (`footprint_emitter.pads` puts the first row at -x with the first label away from USB-C, the record lists D6 to D0 there) | the plan, S1 | acted for the FireBeetle, raised for the XIAO | the FireBeetle: the PO's bench look of 2026-11-28 ("14, D10 by battery") and four anchors on DFRobot's top view (`tests/data/pictures/s3-top-view-anchors.json`) agree, so the record's rows swap (`pins` `[14, 18]`, `row_14` first). The XIAO footprint: card P1347 #1933 |
| 2 | The PO's look of 2026-11-20 (RX and BAT on the left edge) was wrong | the bench look, 2026-11-28 | acted | `row_side.source` now holds the new look and says it corrects the old one; `test_the_battery_socket_is_on_the_d10_edge_as_the_po_s_board_has_it` |
| 3 | `tests.test_emit_footprint.ItMatchesAnIndependentlyMadeFootprintTest` compares the generated footprint with the file `smartbin-local/FireBeetle2Esp32S3.tsx` beside the repository. That file holds the old order (RX first at -x). It goes red after the swap, and the plan does not name it | the build | raised | to the lead, not changed by the builder: decide whether the reference is stale (it is from 2026-09-24) |
| 4 | `boards/firebeetle2-esp32s3.json` named `tools/generate-firebeetle-footprint.py`, a file that does not exist | the plan, A1 | acted | the `//footprint` line names `scripts/emit_footprint.py` |
