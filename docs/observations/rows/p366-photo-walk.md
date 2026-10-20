# P366 photo walk: findings rows

Gaps, bugs and things to consider from the walk that registered the PO's AliExpress analog joystick from three photos
(2026-10-20, Prague). The journey map is the Miro frame
https://miro.com/app/board/uXjVEavQ4JQ=/?moveToWidget=3458764687869927217. The record is `joystick-module-mh` in the
PO's store, two in his drawer. R10.2 applies: a row becomes a card only if it is a real bug or blocks the next walk.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The walk ran end to end: photos, library search, research, record checks, drawer. A later `--need joystick` from another project finds the record. | walk | verified | `parts.py --validate` "joystick-module-mh ok", `--sources` 4 of 4 ok, `--need joystick` from the spark repository |
| 2 | `--need` found nothing for five names before the research (KY-023, HW-504, analog joystick, thumb joystick, potentiometer) | walk, library | closed | expected: the library had no joystick |
| 3 | `--need` names only the brief's vendors (DFRobot, Seeed) and "sellers: none named in the brief", so an AliExpress module has no search path of its own | walk, library | raised | `--need` output; the PO's settings idea is spike P368 #470 |
| 4 | The PO: "Websearch has to also definitely happen, also image recognition". `/spark:identify` does not require a wide web search or a written image reading apart from the web | the PO, walk | raised | `commands/identify.md` steps 1 to 3; the agent ran 5 searches and 7 fetches after the PO's words reached it |
| 5 | The skill tells the lead to hand the agent "the record schema", but no schema file exists | walk, identify | raised | `commands/identify.md` step 3; the lead pointed at `parts/*.json` and `--validate` |
| 6 | The research rules assume a chip datasheet. A chipless, maker-less module has no rule for citing a look-alike maker's document (Joy-IT KY-023), for a value computed from an unverified fact (0.66 mA), or for naming a board with no name | walk, research | raised | the agent's report; every fact stays `verified: false` |
| 7 | `--fetch` reads URLs only under keys like `sources.datasheet`, so a record whose `sources` is a list "cites no datasheet or image URL to keep" | walk, research | raised | the agent kept both PDFs by hand with `--keep --url` |
| 8 | `--keep` stores a file under its download name (`manual.pdf`, `f8d55a6a-image.jpg`), so `--kept joystick` cannot find it | walk, research, drawer | raised | the agent's report and the lead's `--keep` of the photo |
| 9 | `--kept ky023` says "no record here cites it", although the project record cites it | walk, research | raised | the agent's report; `--kept` seems not to read project records |
| 10 | `--read` returns LABEL ONLY or NOT FOUND on a datasheet table without row labels | walk, research | raised | the Joy-IT one-page datasheet; read with `pdftotext` instead |
| 11 | Every `parts.py` action crashes under `python3 -I` with `ModuleNotFoundError: outcomes`, and `-I` is the rule for downloaded files | walk, research | acted | reproduced by the lead with `--list`; bug P369 |
| 12 | `--skeleton` needs `--kind`, and only its error says so. It also writes `sourcing: []` for an owned part | walk, research | raised | the agent's report |
| 13 | The validator refuses `+5V` as a pin name. The way out (`pin: VCC`, `printed: "+5V"`) is in the error text only | walk, research | raised | the agent's report |
| 14 | `--unverified` lists 9 facts, but not the body size 34 x 26 mm that the agent called a guess | walk, check | raised | `--unverified joystick-module-mh` output |
| 15 | Bench checks wait on the PO: pin order (GND to VCC about 5 kOhm), R1 empty, SW closes to ground, which pot is X, the size by ruler | walk, bench | raised | the record's unverified list; due before the game walk P364 #466 |
| 16 | The PO: the walk photos are not good enough as the part picture for the breadboard and other drawings. A new walk makes the part picture and a schematic symbol, and later a 3D model | the PO, walk | acted | his words on P370 and P371 (Idea) |
