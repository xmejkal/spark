# Walk diary: DFR0457 Gravity MOSFET Power Controller (upgrade path), 2026-11-10

Project: walk/dfr0457/project (abbreviated $P below). Every parts.py call ran with `SPARK_HOME=$HOME/.local/share/spark`.
Record: $P/parts/dfr0457-mosfet-power-controller.json. It is true of DFR0457 with the V1.0 silkscreen, the V1.0 schematic (2016/9/2) and the V1.0 drawing.

## Steps
1. `cat commands/research.md`: reuse first (`--need`, `--kept`). "a match is the answer". It has no step for upgrading a record that already exists.
2. Read shelf/dfr0457-mosfet-power-controller.json (28 kB, `based_on.project: irrigation`), drawer/dfrobot-dfr0457.json (count 8, `is.part` = the shelf id, `function: drive load-switch`). The catalog has no DFR0457 entry.
3. `parts.py --need switch 12 V load --project $P` → "nothing in the library matches 'switch 12 V load'. Research it: /spark:research …"
4. `parts.py --need mosfet --project $P` → "dfr0457-mosfet-power-controller mosfet-driver …"
5. `parts.py --kept DFR0457 --project $P` → 9 documents, all `present`, each "(version not read)".
6. `parts.py --help`: `--promote` is "catalog → the project's parts/, or the project's parts/ → the plugin's library". The shelf is not named.
7. `grep shelf docs/ commands/`: how-it-works.md:168 says the shelf beats the library. idea.md:110 says a shelf record is "written in that project" (its home). Nothing says how to bring a shelf record into a NEW project.
8. `parts.py --skeleton dfr0457-mosfet-power-controller … --dry-run` → `would write $P/parts/…json — every null is a fact to record`. It gives no warning that a full record exists on the shelf.
9. `parts.py --promote dfr0457-mosfet-power-controller --project $P --dry-run` → `would promote to $P/parts/…json`. The source layer is not named.
10. Read part_facts.py:139 `promote()`: the code takes the catalog OR the shelf into the project. I used this path.
11. `parts.py --promote … --project $P` → "promoted to $P/parts/dfr0457-mosfet-power-controller.json"
12. `parts.py --validate --project $P` → "dfr0457-mosfet-power-controller ok", plus 15 other records from the library and shelf.
13. `parts.py --read <kept dimension pdf> --want mounting_holes body_mm` → "NOT FOUND … read those pages as images" (exit 1).
14. `pdftoppm` (by hand) rendered the kept dimension drawing and schematic. I viewed both. `pdftotext -bbox` gave the hidden pad designators: PAP103 y=309, PAP102 y=340, PAP101 y=370. PAP201, 202 and 203 run from top to bottom.
15. WebFetch https://wiki.dfrobot.com/dfr0457/ → spec table, including `Mounting Hole Size inner diameter 3.1mm; outer diameter 6mm` and "Interface Type PH2.0-3P". The pinout table lists 1 VIN, 2 GND, 3 VOUT, 4 PH2.0-3Pin. Documents: only Dimension and Schematics.
16. Viewed the kept photos Main_01 and Detail_05 (no fetch): a 3-way barrier terminal with screw clamps and a white side-entry PH2.0 socket.
17. curl of the wiki pinout image https://dfimg.dfrobot.com/60191ece025a892c98c6b90b/wikien/06da2b5111fb5c246e976be2c0f8741c_0x0.png → 200 PNG. It labels the Gravity socket only as a whole ("4") and numbers no pin.
18. WebFetch https://www.dfrobot.com/product-1567.html → `Note: it works with direct current (DC) only!` The shipping list has `Gravity Digital Sensor Cable x1`. It has no STEP and no terminal data.
19. WebSearch "DFR0457 MOSFET Power Controller STEP 3D model" → no STEP or CAD anywhere.
20. `parts.py --fact-set … factset1.json --dry-run` (top-level `legs`, `mounting_holes`) → refused: `a fact write is a JSON object of facts the chain reads: footprint, pin_order, pin_order_proof, body_mm, simulation, or facts entries by name; …`
21. `--fact-set … factset2.json --dry-run` (`{"facts":{"mounting_holes":…}}`) → `would set …`
22. `--fact-set … factset3.json --dry-run` (`host_requirements`) → refused with the same line.
23. `pdfinfo` on the kept PDFs: schematic created 2016-09-02, drawing 2016-09-09, both 1 page, Title "New Output".
24. `--fact-set … factset4.json` (real run): `cites` on 10 schematic facts, `mounting_holes` re-sourced, `pin_order_proof` strengthened → "set dfr0457-mosfet-power-controller ($P/…): facts {…} → {…}". No shelf line. The shelf file stayed unchanged (Oct 4, sha256 2a7479ed…).
25. Hand edit with python, because no command writes these. I added `legs` and a host_requirement (DC only). I filled the title and version of the 2 kept documents. I added the pinout-image URL to `sources`, renamed the signal VALVE_CTRL → LOAD_CTRL and added a provenance sentence to `//`.
26. `parts.py --validate --project $P` → "dfr0457-mosfet-power-controller ok"
27. `parts.py --fetch … --project $P --dry-run` → `would fetch …06da2b51…_0x0.png` (1 URL).
28. `parts.py --fetch … --project $P` → printed all 10 documents with "<-" arrows. The `retrieved` dates show that only the png was new (2026-11-10).
29. `parts.py --unverified … --project $P` → `14 thing(s) nobody has checked` (the report gives the list).
30. `parts.py --sources … --project $P` → all 16 "ok".
31. `parts.py --need load switch` → "nothing in the library matches 'load switch'". `--need 12V` → two buck regulators, not the MOSFET.

## Bugs
- `--need load switch` / `--need switch 12 V load` → "nothing … matches … Research it". The drawer holds 8 of DFR0457 with `function: [{does: drive, what: load-switch}]`. `--need` reads only id, name, kind and alias, so it sends the person to research a part they own 8 of.
- `--skeleton <id that is on the shelf> --dry-run` → `would write $P/parts/<id>.json` with no warning. A project record beats the shelf (how-it-works.md:168), so the empty skeleton hides the 28 kB researched record.
- `--fact-set` refuses `legs` (step 20). part-data.md:20/35 documents `legs`, and breadboard/wiring_steps.py:292 reads it. The only way to write it is a hand edit.
- `--fact-set` refuses `host_requirements` (step 22). That is where "every warning a person must see goes", and no command adds one, so a hand edit is the only way.
- Docs: `--promote` help and research.md say "catalog → the project's parts/". part_facts.py:150 also takes the shelf. The dry run does not say which layer it copies from.
- `--skeleton` writes `"sourcing": []` and `"//sourcing": "Where it can be bought … {seller, url, price_czk, checked}"` (part_facts.py skeleton()). This contradicts W21 ("No seller listings, prices or stock") and the agent brief.
- `--fetch` (real run) prints already-kept and newly downloaded documents alike ("<-"), so its output does not tell what reached the network. The dry run tells it (1 URL).
- `--fetch` named the new document `06da2b5111fb5c246e976be2c0f8741c-0x0` (a CDN hash), with `title`/`version` null. The key is unreadable in a `cites`.

## Gaps in the flow
- research.md has no "upgrade a record that exists" path. Reuse ends at "a match is the answer". I guessed `--promote` shelf→project from the code (part_facts.py:139), not the docs.
- No command and no doc sends a project upgrade back to the shelf or the home project (irrigation). `--fact-set` on the project copy printed no "shelf copy refreshed/not refreshed" line, so the shelf is now silently older than the project copy.
- research.md step 1 says "Ask: does the person already have one?" but names only /spark:drawer. No reuse command matches a need's words against the drawer's `function`.
- My instructions say "open a page whole only for a drawing", but no parts.py command renders a page as an image. I used pdftoppm by hand. `--read` says only "read those pages as images".
- `legs` has no `verified`/`source` slot, so legs read off a drawing cannot be marked unverified.
- `--unverified` lists `pin_order` and `facts.gravity_header_pin_order` as two items for one fact.
- No command fills a kept document's `title`/`version` after keeping. All 9 were null, though the schematic's title block states Revision V1.0, 2016/9/2.
- Budget: `--sources` asks 16 URLs and `--fetch` downloads. The brief does not say whether these count against the "twelve fetches". I counted them separately (below).
- A doubled download: the agent brief makes me view a drawing before `--fetch`, so the wiki pinout PNG was downloaded twice (curl, then `--fetch`). `--keep <file> --url` avoids that. Nothing in the flow suggests it.
- part-data.md lists "3D model reference (registry / STEP file)" under "What to store per part" but has no key for it.
- `mounting_holes` is an ad hoc fact name that no code reads (grep scripts: none). By W21 it does not earn its place, but the PO wants it. The rule and the ask conflict.

## What the existing record had wrong or missing
- `facts.mounting_holes` was `verified:false` with source = the drawing only. The hole size is the wiki's own spec-table text (https://wiki.dfrobot.com/dfr0457/), and the "bottom pair is assumed to mirror the top" wording is wrong: the drawing draws all 4 holes. I re-sourced it. It stays false, because no hole is dimensioned from an edge.
- No "DC only" warning. The product page says "Note: it works with direct current (DC) only!" (https://www.dfrobot.com/product-1567.html). Added to host_requirements.
- `pin_order_proof` did not say that DFRobot ships its own "Gravity Digital Sensor Cable x1" (product page). I added it. It stays unverified.
- No fact read from a kept document carried `cites {document, at}`. Each named only the URL. Added on the 10 schematic facts. The mosfet_*/optocoupler_* facts still have none, because I did not re-read those datasheets.
- `documents.*.title` and `.version` were null on all 9. Filled for the schematic (V1.0, 2016/9/2) and the drawing (V1.0, 2016-09-09).
- `legs` was null, though the drawing places P1-1 at the bottom and P1-3 beside 'D'. Filled.
- Irrigation project wording leaked into a shelf record every project finds: signal `VALVE_CTRL`, "four valves", "ESP32-S3" in needs, facts and host_requirements. I renamed the signal to LOAD_CTRL. The prose stays as it was.
- `pin_order_proof` states "Gravity wire colours: green signal, red VCC, black GND" with no source.
- `operating_temperature_c` [-55, 155] is `verified:true` (the vendor's text), while its own note calls the value implausible (the EL357N's limit is +110 C). The flag says trust it. The note says do not.
- The kind `mosfet-driver` and the drawer function `load-switch` share no word with the need. The user's words "switch a 12 V load" do not find the record.

## No place in the record
- Product picture: https://dfimg.dfrobot.com/enshop/DFR0457/DFR0457_Main_01.jpg. It is kept as `documents.dfr0457-main-01`, but nothing marks it as THE picture.
- Pinout picture: https://dfimg.dfrobot.com/60191ece025a892c98c6b90b/wikien/06da2b5111fb5c246e976be2c0f8741c_0x0.png (kept now). It shows terminals 1 VIN, 2 GND, 3 VOUT and the Gravity socket as "4".
- Connection diagram (not viewed): https://dfimg.dfrobot.com/enshop/image/data/DFR0457/DFR0457-Connection_0x0.jpg (from the product page).
- Schematic: https://dfimg.dfrobot.com/wiki/17549/DFR0457_mosfet-power-control-module_schematics_V1.0.pdf. It shows P1 (1 Single, 2 VCC with a stub, 3 GND). R1 2k feeds the L1 LED, and R4 470R feeds the LED of U1, an EL357N-class opto. R2 3.3k goes to the gate. R3 33k pulls the gate up to VCC1, with the D1 12 V zener across it. The Q1 P-MOSFET has its source on VCC1 and its drain on P2-3. P2-1 is VCC1 (VIN) and P2-2 is GND1. The control GND and GND1 are separate nets. Rev V1.0, 2016/9/2, drawn by Hudianjiang. The file is kept. The record has no field for what it shows.
- Board outline: 44 x 32 mm (`body_mm`, wiki + drawing) with rounded corners. The corner radius is not dimensioned.
- Mounting holes: 4. Inner Ø3.1 mm, outer ring Ø6 mm (wiki spec table). Spans 20 mm (horizontal) and 25 mm (vertical) (drawing). Positions SCALED from the drawing, unverified, terminal on the left, from the top-left: ≈(20.5, 3.5), (40.5, 3.5), (20.5, 28.5), (40.5, 28.5) mm. The terminal edge has no holes. Kept as the ad hoc `facts.mounting_holes`, with no x/y slot.
- Screw terminal P2: 3 positions, barrier type with screw clamps (photos Main_01/Detail_05), along the left 32 mm edge. Order top to bottom VIN(1), GND(2), VOUT(3) (wiki pinout table, schematic P2, drawing silkscreen). Pitch SCALED ≈8.3 mm: the pad designators are 125 pt apart at ≈15.1 pt/mm (dimension PDF). Unverified.
- Gravity connector P1: PH2.0-3P (wiki "Interface Type PH2.0-3P"), side-entry with the opening off the right 32 mm edge (drawing + photo), centred ≈16 mm from the top (scaled). Pin 1 Single at the bottom, pin 3 GND at the top beside the 'D' mark (schematic + hidden pad designators). The host side is in pin_order/legs. The module-side edge and orientation have no field.
- Ships with: "Gravity Digital Sensor Cable x1" (https://www.dfrobot.com/product-1567.html). In pin_order_proof prose only.

## Not found
- STEP/3D model: none. The wiki has only Dimension and Schematics. The product page links only the "Product Wiki". The WebSearch "DFR0457 MOSFET Power Controller STEP 3D model" found none.
- Screw terminal pitch, wire gauge, torque and part number: not on the wiki or the product page. The drawing gives no dimension.
- Hole positions from a board edge and the corner radius: not dimensioned on the V1.0 drawing.
- Component height and PCB thickness: not on the wiki, the product page or the drawing.
- Weight: not on the wiki or the product page.
- Per-pin Gravity labels on the board or in the wiki image: the silkscreen shows only 'D', and the wiki pinout image only "4".

## Counts
- Searches: 1 of 8 (WebSearch, step 19).
- Fetches: 3 of 12 by me (WebFetch wiki, curl pinout PNG, WebFetch product page). parts.py added 1 download (`--fetch`: the same PNG again) and 16 URL checks (`--sources`).
- Wall time: about 12 minutes (09:30–09:42 CET).
