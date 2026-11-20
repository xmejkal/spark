The e-paper project of the walk P934 (#1323) on the DFRobot FireBeetle 2 ESP32-C6, as of 2026-11-20 for P953 (#1359):
the breadboard picture of the walk, with the C6 drawn from its record.

- `requirements.json`: the walk's.
- `boards/firebeetle2-esp32c6.json`: the walk's board record, which holds `physical.features` and `physical.colour`
  (P956), so the C6 is drawn. `boards/active.json` names it, so the folder is a project.
- `parts/epaper-2in9-bwr-mh-et-live.json`: the record of `../epaper/parts/`, which has `short_name` ("e-paper").
- `dist/board/circuit.json` and `built-from.json`: from `check_spine.py requirements.json --keep .` run on a copy of
  this folder (with an empty `.spark/`) on 2026-11-20 at main 7c82991b, with tsci 0.0.2600.

No photo and no kept drawing are here. The golden runs with an empty store, so the e-paper shows its frame picture,
not the red demo screen that the walk's store keeps.
