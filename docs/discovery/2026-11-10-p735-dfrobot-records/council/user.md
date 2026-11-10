# User lens, P735 (#1010): the PO's journey from "I own it" to a wired breadboard and a board page

Persona: the PO, n = 1 (scrum/VISION.md, "The test bench"; the hobbyist row is marked Hypothesis there). Every H below is mine. "Walk" means the four diaries in `docs/discovery/2026-11-10-p735-dfrobot-records/walk/`. The walks were run by Claude, not by the PO, so each friction is what Claude met, not what the PO met (see USER-34).

## Findings

Format: USER-n · claim · tag · pointer · supports only.

### A. The four readers and what each reads today

USER-1 · The breadboard sheet reads a part's `legs`, `host_requirements`, `unused_pins` and `_firmware_pulls`, plus the pin labels of the built circuit. It reads no picture, no outline, no hole and no connector fact of a part. · E · `scripts/spark/breadboard/wiring_steps.py:292` (`legs`), `scripts/spark/breadboard/sheet.py:203-210` (the "before you power it" lines) · supports only: which facts the sheet reads today.

USER-2 · The sheet's step for a part says only "Put <Part> in the breadboard, each pin in its own row." It names no pin order, no edge, no connector type and no orientation. Example: step 2 for `L9110sModule`, step 3 for `JstPh2PowerInlet`. · E · `tests/data/breadboard/motor/breadboard.expected.md` steps 2-3 · supports only: the person must find the part's pin order on the module's silkscreen by himself.

USER-3 · A wire end for a part is `<name> <pin>` and gets a parenthesised leg note only when the record has `legs` for that pin. · E · `scripts/spark/breadboard/wiring_steps.py:292-294` · supports only: where a missing `legs` shows up in the person's wiring.

USER-4 · The drawn breadboard picks a picture by the part's Wokwi type. spark's own pictograms come first and a type without one gets a labelled box (`module.svg`). No record field feeds a picture. · E · `scripts/spark/breadboard/part_pictures.py:1-22`; `scripts/spark/breadboard/drawing.py:2-10` · supports only: a kept product photo or a schematic is read by no code path of the drawing.

USER-5 · A part can be drawn only when its record names a Wokwi part. Code `no_drawing_fact`: "nothing says how to draw a part (no Wokwi part in its record)". · E · `scripts/spark/breadboard/drawing.py` (CODES, NO_DRAWING_FACT); `scripts/spark/breadboard/drawing_catalog.py:35-36` · supports only: a DFRobot module with no Wokwi twin is not drawn.

USER-6 · Of the 8 shelf records in the store, 3 name no Wokwi part (`dfr0664-tft-2in`, `dfr0831-buck-5v`, `sen0217-flow-meter`). The others borrow a stand-in: DFR0457 is `wokwi-led`, SEN0193 is `wokwi-potentiometer`, DS3231 is `wokwi-ds1307`. · E · command: a loop over `~/.local/share/spark/shelf/*.json` printing `simulation.wokwi.part`, run 2026-11-10 · supports only: the picture a person sees for an owned DFRobot module is another part's picture (what Wokwi's twin looks like), or none. Whether the sheet's drawing marks it as a stand-in — (not checked).

USER-7 · The board page (`page.html`) has three tabs: the breadboard (spark's own picture), the schematic and the PCB (both tscircuit's `tsci export`). It loads nothing from the web. · E · `scripts/spark/breadboard/tabbed_page.py:1-12` · supports only: no tab takes a vendor photo, vendor schematic or vendor outline. What the PCB tab reads from a part record (footprint, `body_mm`) — (not checked in full; see section 2).

USER-8 · Claude's readers (the commands) get a part only as far as `--need` finds it. `--need` reads id, name, kind and alias, not the drawer's `function`. In the DFR0457 walk, `--need "switch 12 V load"` answered "nothing in the library matches ... Research it" while the drawer holds 8 pieces with `function: drive load-switch`. · E · `walk/dfr0457/diary.md` steps 3, 31 and the Bugs list · supports only: Claude can send the person to research a part he owns.

USER-9 · The same miss for boards and for display words. `--need ESP32-C6` said nothing matched, although `xiao-esp32-c6` ships. `--need small colour display` found nothing, although `dfr0664-tft-2in` (kind `display`) exists. · E · `walk/dfr1117/diary.md` Bugs; `walk/dfr0995/diary.md` Gaps · supports only: reuse-first can miss a sibling.

USER-10 · Few drawer entries link to a record. `parts.py --drawer` prints 112 entries; `grep -c " part \| board "` on that output gave 19. Two of the walked parts (DFR0995 display, SEN0526 microphone) have a drawer entry that "points at no part record", and no step in research.md links them. · E · command `parts.py --drawer` (2026-11-10); `walk/dfr0995/diary.md` Gaps, `walk/sen0526/diary.md` Gaps · supports only: the count is a rough grep, not the validated figure. The card says 8 part records in `parts/` and 18 catalog records (issue #1010 body).

### B. Where he stalls, guesses or comes to harm

USER-11 · Wiring by a wrong pin order. The sheet gives a part's rows and the jumper's far end by pin name; the order on the module (which pin is first, which edge) is in the record only as `pin_order`/`legs`, and `legs` cannot be written by any command. DFR0457: `--fact-set` refuses top-level `legs`, a hand edit was the only way. · E · `walk/dfr0457/diary.md` step 20 and Bugs; `scripts/spark/breadboard/wiring_steps.py:292` · supports only: the one path that gives the person an order is hand-edit only.

USER-12 · Pin order read off a drawing is marked `verified: false` by one rule and `true` by library records. The person sees "verified" either way. · E · `walk/sen0526/diary.md` Gaps (`vl6180x-breakout` schematic readings `true`, `led-red-5mm` pin order `true`) · supports only: the flag does not mean the same across records. What the sheet prints for an unverified pin order — (not checked).

USER-13 · DFR0995 display: 8-pin header BLK DC RES CS MOSI SCLK GND VCC with "VCC on BLK, GND on DC" in the record's own words (reversed supply risk); the `--unverified` command replaced the record's specific `why_it_matters` with a generic sentence. · E · `walk/dfr0995/diary.md` Bugs (first two) and "No place in the record" (Header) · supports only: the specific warning is lost when the person asks which facts are unchecked.

USER-14 · 5 V against a 3.3 V board. DFRobot's own texts conflict for the display ("Operating Voltage 3.3V" against "VCC DC3.3V-5V"). The record has only `verified:false` plus prose, no conflict marker. · E · `walk/dfr0995/diary.md` Gaps · supports only: the person cannot tell from the record which of two figures to trust. For SEN0526 the datasheet contradicts itself (VDD 1.8-3.3 V on p7, 1.6-3.6 V on p3), also only in a `note` (`walk/sen0526/diary.md` Gaps).

USER-15 · A board's VIN is the USB VBUS net directly. Feeding VIN with USB plugged in back-feeds the host. A board record has no `host_requirements`, so the warning sits in a `//` note that nothing prints. · E · `walk/dfr1117/diary.md` "No place in the record" (VIN); `scripts/spark/breadboard/sheet.py:210` prints only `part.get("host_requirements")` · supports only: harm (host USB damage, battery behaviour) with no printed warning for the board. The 3 boards are the PO's (`parts.py --drawer`: Beetle ESP32 C6 Mini x3).

USER-16 · A "DC only" limit on DFR0457 was missing from the shelf record. The product page says "Note: it works with direct current (DC) only!". The walk added it to `host_requirements` in the project copy only; the shelf copy stayed unchanged (sha256 2a7479ed…), with no line that says the shelf is now older. · E · `walk/dfr0457/diary.md` steps 24-25 and "What the existing record had wrong or missing" · supports only: another project that takes the shelf copy would not get the warning.

USER-17 · `host_requirements` prints every line under "the board must:". Walk lines for firmware (I2S slot width) or enclosure (the port must face the hole) land under that heading. · E · `walk/sen0526/diary.md` Gaps · supports only: a line may be read as a wiring instruction when it is not.

USER-18 · A strap (SEL to GND on SEN0526) has no field: `power: {pin: SEL, rail: ground}` is accepted silently and `--signals` does not show it. A floating SEL on the bench is the failure. · E · `walk/sen0526/diary.md` Gaps · supports only: Claude could write a record that validates and leaves a pin floating on the sheet. Whether the sheet prints it — (not checked).

USER-19 · A part with two connectors (DFR0995: 8-pin header and 18-pin GDI FPC) has one `pin_order`; the second has no field. Only the header is the person's wiring path. · E · `walk/dfr0995/diary.md` Gaps · supports only: which connector a step's pin names refers to is not recorded.

USER-20 · Revision. The PO's three Beetle ESP32-C6 boards may be V1.0 or V1.1 (regulator RT9080 vs TPS62A02); "needs a photo of the back". The back silkscreen prints "Beetle ESP32-C6 V1.0.0". The board record has no slot for the revision it is true of. · E · `walk/dfr1117/diary.md` Not found, "No place in the record" (Revision markers), Gaps · supports only: the revision is something only the PO can supply (photo of the back).

USER-21 · Ships-with items matter to wiring. DFR0457 comes with a "Gravity Digital Sensor Cable x1"; the record cable colours (green signal, red VCC, black GND) have no source. Whether SEN0526's header pins ship soldered or loose is not published. · E · `walk/dfr0457/diary.md` "What the existing record had wrong" and "No place"; `walk/sen0526/diary.md` Not found · supports only: whether he needs a soldering step before wiring is not in the record. What the PO's own units have — (a PO answer).

### C. What the PO can supply and what not

USER-22 · The PO can supply: a count (the drawer holds one; `--drawer-set` corrects it), the revision (photo of the back), whether a header came soldered, which cable came in the box, and whether a unit works. `/spark:identify` takes a photo of the module and writes a record with every photo-only fact unverified. · E · `commands/drawer.md` lines 27-29, 77-88 (counts and packs); skill list description of `spark:identify`; `walk/dfr1117/diary.md` Not found · supports only: the ways the person can supply a fact. Whether he has done so for these 99 — (a PO answer).

USER-23 · The PO cannot supply the vendor's unpublished facts: header pitch and pad positions of the DFR0995, the GDI position in mm, the hole offset of DFR0457 from an edge, screw-terminal pitch, component height, supply current of the display, part numbers of the regulator and the buffer (DFR0995), and the USB-C part number (DFR1117). He can only measure them with calipers if he wants to. · E · `walk/dfr0995/diary.md`, `walk/dfr0457/diary.md`, `walk/dfr1117/diary.md` "Not found" · supports only: these are a gap that no research run closes by reading; measurement closes it. Whether he owns calipers or a multimeter — (a PO answer). VISION.md says of the hobbyist: "maybe no meter" (`scrum/VISION.md` persona table).

USER-24 · STEP/CAD sources exist for the DFR0995 and SEN0526 as `.zip` files and `--fetch`/`--keep` cannot keep a `.zip` (KEEPABLE has no `.zip`). For DFR1117 DFRobot publishes no STEP (empty `stpFiles` slot). For DFR0457 no STEP or CAD was found by one search. · E · `walk/dfr0995/diary.md` Gaps and "No place" (STEP); `walk/sen0526/diary.md` Gaps; `walk/dfr1117/diary.md` Not found; `walk/dfr0457/diary.md` step 19 · supports only: one of the PO's words ("holes, connectors") has a source for some parts and none for others.

USER-25 · Hole positions in the record are scaled from drawings by Claude, marked unverified, and held in an ad hoc `facts.mounting_holes` that no code reads (`grep scripts: none` per the DFR0457 diary). DFR0995: 2 holes, Ø2, 40.5 mm apart; SEN0526: 2 holes, Ø2, 12 mm apart; DFR1117: none; DFR0457: 4 holes, Ø3.1 inner. · E · `walk/dfr0457/diary.md` Gaps (last item) and "No place in the record"; `walk/dfr0995/diary.md`; `walk/sen0526/diary.md`; `walk/dfr1117/diary.md` Not found · supports only: no reader of the four reads holes today; a number can be right and still unread.

### D. The research path the PO walks before the breadboard

USER-26 · `research.md` has no path for a part with a record already on the shelf (DFR0457), no path for a dev board (DFR1117, boards live in `boards/README.md`), and no step that links a new record to the drawer entry. The walker guessed `--promote` shelf-to-project from `part_facts.py:139`. · E · `walk/dfr0457/diary.md` Gaps; `walk/dfr1117/diary.md` Gaps; `walk/dfr0995/diary.md` Gaps; `walk/sen0526/diary.md` Gaps · supports only: Claude's route to a full record differs per kind; the PO sees only "it took N steps".

USER-27 · `parts.py --skeleton <id on the shelf> --dry-run` gives no warning that a researched record exists; a project record beats the shelf, so a skeleton would hide the 28 kB record. `--skeleton` also writes `"sourcing": []` with a seller/price field, which the research rules forbid (all four walks hit this). · E · `walk/dfr0457/diary.md` Bugs; `walk/dfr0995/diary.md` Bugs; `walk/sen0526/diary.md` Bugs · supports only: a hand-run of `--skeleton` loses a record or adds a forbidden field.

USER-28 · No command renders a PDF page as an image. `parts.py --read` on a schematic says "read those pages as images" and renders nothing; walkers used `pdftoppm`/`sips` by hand. `--read` also reported FOUND on the wrong row (SEN0526: absolute maximum instead of operating voltage; revision-history row for SNR). · E · `walk/dfr0457/diary.md` step 13-14; `walk/dfr0995/diary.md` Bugs; `walk/sen0526/diary.md` Bugs · supports only: a supply range could be written from an absolute-maximum row. What a person would do instead — (not seen).

USER-29 · `--fetch` leaves `title` and `version` null on documents, names a key by CDN hash or by a wrong extension (`...-jpg` for a `.webp`), and prints a hash prefix instead of the store path `--read` needs. · E · `walk/dfr0457/diary.md` Bugs; `walk/dfr0995/diary.md` Bugs; `walk/sen0526/diary.md` Bugs and Gaps · supports only: the person and Claude cannot tell which document is which from the key.

USER-30 · "Which picture is THE picture" has no field. All four walks list a product picture, a pinout render and a schematic as `documents` entries only. · E · `walk/dfr0457/diary.md` "No place"; `walk/dfr0995/diary.md` "No place"; `walk/sen0526/diary.md` "No place"; `walk/dfr1117/diary.md` "No place" · supports only: a reader that wants a picture must choose by guess.

USER-31 · The PO's earlier words "I bought them from DF Robot" have a drawer with 99 DFRobot entries of 112 (card); `/spark:drawer` imports the order history from the `dfrobot.com` order pages with a script and the person's own tab. Items without a record show "—" in `Part`. · E · issue #1010 body ("What is true today"); `commands/drawer.md` lines 59-64; `parts.py --drawer` output · supports only: the starting point of the journey exists; the tail of "I own this" to "picked for a goal" runs through `--need`, which is USER-8/9.

USER-32 · The walks' own counts: 1 to 2 searches of 8 and 3 to 10 fetches of 12 per part; wall time 7, 12, 25 and 30 minutes (the 7-minute and 12-minute figures are estimates from the diaries' clock lines). · E · "Counts" in each diary · supports only: effort to make one record by this flow. The 99 parts × minutes — (not computed; the parts differ).

USER-33 · The PO's own stated target is "the schematic, a picture, the dimensions, the holes and the connectors, each fact with its source ... so that spark displays the part well on the breadboard and the board". · D · the PO, 2026-11-10, issue #1010 "Done when" · supports only: the intended output, in his words.

USER-34 · What he does with the part today after picking is not in any record I read: whether he wired any of the 99 DFRobot parts from the sheet. The README says "No breadboard wired from a sheet has run yet." · E · `README.md` lines 125 and 161 · supports only: the friction list above is a prediction from walks and code, not from a PO bench session. Everything in section B is a candidate for the account questions below.

## What you could not check, and why

- Whether the board page's PCB tab (tscircuit) reads any part fact besides footprint and `body_mm`, and what it draws for a part with no footprint. Reason: I read `tabbed_page.py`'s docstring and `drawing.py`'s head, not the tscircuit adapter or `emit_footprint.py`.
- Whether the sheet or the drawing marks a stand-in picture (USER-6) as a stand-in. Reason: I did not build a sheet with DFR0457 or SEN0193.
- Whether the sheet prints anything for an unverified `pin_order`, and whether a `power` strap is printed (USER-12, USER-18). Reason: I read `sheet.py` lines 195-215 only, not the part table code.
- Whether a voltage mismatch (a 5 V pin on the 3.3 V board) is checked anywhere. I found `part_rules.py` (`host_part_problems`, `conflicts_of`) and `sheet.py:196-199` ("check it against the supply range ... before you connect it", for off-board supplies). I did not read their bodies, so I do not claim a check exists or does not exist for a module pin that is 5 V only.
- The PO's own bench experience. Reason: there is no log of his wiring from a sheet (README: none run yet), and I could not ask him. Every friction moment below is a prediction from walks and code.
- The current counts of the 99 DFRobot entries by kind (display, sensor, board, motor). Reason: I counted only lines of the drawer output with a record (19 of 112) and did not group by kind.
- The files `brief.md`, `items.md`, `jobs-and-journeys.md`, `risks-and-tests.md`, `story-map.md`, `verification.md` in the discovery folder: I opened none (brief.md only its template head, unfilled), so I cannot say what other lenses claim. The long walk JSON records I did not open; I used the diaries.
- `docs/guide/part-data.md` is not at that path (grep failed); I did not find where the schema reference lives, so I did not read it first-hand. The diaries cite it.
- Web: none, by instruction. No vendor page was checked; the vendor facts above are the walks' claims, not mine.

## Questions for the decider

Candidate account questions for the PO (about his own use, past tense):

1. Q1 · Think of the last time you wired a DFRobot module on a breadboard (or on a bench). Where did you find which pin was which, and how long did it take? · Decides: whether `pin_order`/`legs` on the sheet is the first fact to complete (USER-2, 3, 11).
2. Q2 · Did you ever connect a module to the wrong pin or the wrong voltage? What happened to it? · Decides: whether wiring harm is a lived cost or only a risk, and so how strong a printed warning must be (USER-11, 14, 15).
3. Q3 · When you opened `build/breadboard.md` or `page.html` for a part you own, what did you look at first, and what did you want to see that was not there? · Decides: whether a picture, an outline or a connector shows first in the breadboard tab and the board page (USER-4, 7).
4. Q4 · Did a part's picture on the sheet or drawing ever look different from the module in your hand (for example a potentiometer for a soil sensor)? What did you do? · Decides: whether a stand-in picture is acceptable or must be marked (USER-6).
5. Q5 · When did you last search a part by what it does (for example "switch a 12 V load") and not find the one you own? What did you do next? · Decides: whether `--need` must read the drawer's `function` (USER-8, 9).
6. Q6 · Which of the 99 DFRobot parts have you wired into a gadget so far, and which did you buy for a plan? · Decides: the order of the batches ("which parts first") (USER-31, 34).
7. Q7 · For the parts you have in hand, did the pins come soldered, and what cable came in the box? · Decides: whether `ships_with` and a "solder first" note are facts the record must hold (USER-21).
8. Q8 · Did you ever check the revision printed on the back of a module (for example the three Beetle ESP32-C6)? When did a revision matter to you? · Decides: whether a record names a revision and whether the PO's photo of the back is a research step (USER-20).
9. Q9 · Have you ever powered a board from VIN or 5 V while it was also on USB? What did the board do? · Decides: whether a board's `host_requirements` must exist and print (USER-15).
10. Q10 · Which tools do you have at the bench (multimeter, calipers, soldering iron, a second USB cable)? · Decides: whether an unpublished fact (pitch, hole offset, supply current) may ask him to measure (USER-23).
11. Q11 · When spark told you a fact was "unverified", what did you do with that? · Decides: whether `verified:false` is read at all, and what the breadboard sheet should print for it (USER-12, 13).
12. Q12 · When you enclosed or mounted a module, which dimension did you need that you had to measure or look up (holes, height, connector side)? · Decides: whether holes/height are for the board page or for a later enclosure card (USER-25, 24).
13. Q13 · When you looked for a vendor's 3D model, schematic or datasheet, where did you go, and what did you do when only a zip was available? · Decides: whether `.zip` keep matters (USER-24).
14. Q14 · After `/spark:research` wrote a record, how did you learn it was done, and did you link it to your drawer entry? · Decides: whether the drawer link is automatic (USER-10, 26).
15. Q15 · When a vendor's own pages disagreed (3.3 V against 3.3-5 V), which one did you believe, and why? · Decides: whether a "conflict" marker is a field (USER-14).
16. Q16 · Is "I own this" or "it is a good part" the moment you want the full record made: at purchase, when picked for a goal, or at the bench? · Decides: when research runs: all 99 up front, per goal, or on demand.

Questions for the decider that are not about the PO's past use:

17. Q17 · The walks were run by Claude; are they accepted as stand-ins for the PO's journey, or does the discovery need a session of the PO wiring one of the four parts from a sheet? · Decides: whether section B is treated as evidence of his friction or as a prediction (USER-34).
18. Q18 · Which reader wins when a fact serves one reader and costs a field (for example holes: no reader today)? W21 ("a property enters when a check, a stage or the PO needs it") and the PO's request conflict in the DFR0457 walk. · Decides: whether `mounting_holes` and the other "no reader" facts enter the record now (USER-25; `walk/dfr0457/diary.md` last Gap).

## Searches

none
