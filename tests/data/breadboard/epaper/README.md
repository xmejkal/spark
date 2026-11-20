The e-paper project of the walk P934 (#1323), as built on 2026-11-20 for P945 (#1348): a FireBeetle 2 ESP32-S3 and the
MH-ET LIVE 2.9 inch e-paper module. The module has no Wokwi part, so the drawn breadboard draws it from its record.

`parts/epaper-2in9-bwr-mh-et-live.json` is the walk's own record, with two additions: `short_name` ("e-paper", the PO's
word) and a `physical` block with its `physical_proof`, read from the walk's back.jpg and not verified. No photo is
kept here. `dist/board/circuit.json` and `built-from.json` come from `check_spine.py requirements.json --keep .` run on
a copy of this folder, before the record had a drawing.
