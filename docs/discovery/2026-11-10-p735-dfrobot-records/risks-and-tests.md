# Risks and tests

## Risks
| risk | evidence now | cheapest way to retire it | status |
| --- | --- | --- | --- |
| value <!-- REQUIRED:risk-value --> | H the records change nothing on screen until a reader exists (A2, ★C3) | order the slices so that a reader ships with slice 0 | open |
| usability <!-- REQUIRED:risk-usability --> | E the PO meets about 20 hand steps per part (walk diaries) | the walk of slice 0 with no hand edit | open |
| feasibility <!-- REQUIRED:risk-feasibility --> | E 0 of 4 walks reached verified holes and pins (★C1, A1) | the geometry count spike | open |
| viability <!-- REQUIRED:risk-viability --> | E 300 to 800 fetches for 99 records (★C10, A5) | size the batch to the scope of Q3 | open |
| ethics and safety <!-- REQUIRED:risk-ethics --> | E vendor tables swap supply pins and disagree on voltage (★C8, A6). H the licence of DFRobot downloads is unknown (PO-15) | keep vendor files in the store only, carry conflicts as a field | open |
| power and battery <!-- REQUIRED:electronics-firmware:power --> | E DFR1117 revisions differ in sleep current, 14 µA against 37 µA, stated (C12) | a photo of the board's back (Q4) | open |
| current and stall <!-- REQUIRED:electronics-firmware:stall --> | n/a because no motor or driver is chosen here | none | n/a |
| thermal <!-- REQUIRED:electronics-firmware:thermal --> | H the DFR1117 V1.0 LDO runs near its 0.43 W package rating on USB, calculated with an assumed diode drop (PHYS-16) | a record fact, not a decision here | n/a because no decision here rests on it |
| EMC and ESD <!-- REQUIRED:electronics-firmware:emc-esd --> | n/a because records hold no layout decision | none | n/a |
| sensor drift and calibration <!-- REQUIRED:electronics-firmware:sensor-drift --> | n/a because no sensor reading is used here | none | n/a |
| brown-out <!-- REQUIRED:electronics-firmware:brown-out --> | H 0.5 A charge plus 0.354 A radio peak is 0.854 A, calculated, above a 500 mA USB 2 port (PHYS-15) | a record warning, not a decision here | n/a because no decision here rests on it |
| wake and low power <!-- REQUIRED:electronics-firmware:wake --> | n/a because no wake source is chosen here | none | n/a |
| the firmware–hardware contract <!-- REQUIRED:electronics-firmware:contract --> | E a floating SEL pad has no field to tie it to a rail (walk/sen0526/diary.md) | a `straps` field in the design | open |
| supply and documents <!-- REQUIRED:electronics-firmware:supply --> | E two DFR1117 revisions under one SKU, DFRobot pages disagree (C12, ★C8) | a record names its revision and carries conflicts | open |
<!-- EXTEND:risk-rows --><!-- EXTEND:pair-rows -->

## Assumptions
| id | belief | type | evidence now | importance | cheapest test | pass line, dated | result that would change the decision | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 <!-- REQUIRED:assumptions --> | DFRobot publishes enough geometry (a dimension drawing with holes and header positions, or a footprint) for most owned PCB modules | feasibility | E against it, 0 of 4 (★C1). H the rest behave the same | — (decider) | the geometry count spike | proposed, set 2026-11-10: at least half link a dimension drawing, and 3 of 5 read drawings give hole positions | under that line, the pipeline needs a second strategy (the person measures, or a photo) before the batch | open |
| A2 | A full record changes what the PO sees only when the sheet or the board page reads it | value | E ★C3, PO-17 | — (decider) | read P734's plan for a record-geometry reader | set 2026-11-10: the reader is in slice 0 or 4 | if no reader comes soon, the geometry fields wait | open |
| A3 | Swappable strategies (site, datasheet, clicking through, a text description) fill one record shape, so a reader does not care which strategy filled a field | feasibility | D2. H no second strategy exists yet | — (decider) | slice 2: one part filled by two strategies | set 2026-11-10: the same keys from both | if the shapes differ, the record needs a per-strategy layer | open |
| A4 | Parts and boards fit one geometry model (P446 `PartShape`) without a second model | feasibility | E a board has `physical`, a part has `body_mm` (★C2, TL-1) | — (decider) | the design council reads both | set 2026-11-10: one model holds both | two models mean two pipelines | open |
| A5 | A batch over the owned modules fits "free, few and local" | viability | E 3 to 8 fetches a record (★C10) | — (decider) | count the scope (Q3) and multiply | set 2026-11-10: under one day of runs | over that, the batch runs on demand per goal | open |
| A6 | A full record with conflicts and "not published" marked keeps the PO from wiring harm | ethics | E ★C8 | — (decider) | the sheet prints each conflict for the walked parts | set 2026-11-10: each conflict printed | a conflict nobody sees changes the record design | open |

## Collection plan
| question | decision it blocks | who can answer | how | when |
| --- | --- | --- | --- | --- |
| How much geometry does DFRobot publish for the owned modules? <!-- REQUIRED:collection --> | A1, the strategy order | Claude | the geometry count spike | after Q1 sets the pass line |
| Which owned parts are in scope? | A5, the batch size | the PO | Q3 | at Q1 |
| Which DFR1117 revision does the PO own? | the DFR1117 record | the PO | a photo of the back (Q4) | at his bench |

## Results

| date | source and pointer | what was seen | pass line met or missed | what it changes |
| --- | --- | --- | --- | --- |

## Budgets <!-- REQUIRED:electronics-firmware:budgets -->
n/a because the item makes records. It chooses no battery, motor, radio or regulator. The figures found (C12, PHYS-15, PHYS-16) go into the records as facts.
<!-- EXTEND:risks-sections -->
