# P735 refuter

Model: Opus. Commands ran with `SPARK_HOME=$HOME/.local/share/spark` inline, against scratch projects in the session scratchpad. Nothing in the repository or the store was changed by me (one exception outside my control: `check_vendor_pins.py` wrote its cached vendor header into the scratch project's `.spark/cache/`). Paths are repo-relative or use `~`.

Check first, for an existing product. The observed problem (PO-17, USER-1, USER-4) is that what spark *shows* reads no geometry: the sheet reads `legs`, `host_requirements`, and a Wokwi type, and one undrawable part stops the drawing. D2 (a research pipeline) addresses how records are *made*. The brief's own Outcome says "spark shows them" and names "the board page or breadboard sheet" as proof, while Scope puts "the breadboard drawing code (P734)" out. So the direction, as scoped, cannot meet its own outcome. That is A2, but the brief carries it as an open assumption instead of a contradiction between Outcome and Scope. What could break for current users is in part 2, last block.

## 1. The ★ claims

- **★C1 · partly.**
  - Read at council/po-assistant.md:38: "Component height and PCB thickness were missing in 3 of 4". The diaries say otherwise:
    - walk/dfr0995/diary.md:53 reads "Board outline: 44.5 x 19.5 mm, PCB 1.6 mm, 4.7 mm overall".
    - walk/sen0526/diary.md:50 reads "PCB 1.0 mm, 2.01 mm over all with mic can".
    - Only DFR0457 (diary:89) and DFR1117 (diary:76) lack them. That makes 2 of 4, not 3 of 4.
  - Read at walk/dfr1117/diary.md:20: "Downloaded the layout zip, which turned out to be DFRobot's KiCad footprint". I listed the kept `layout.zip`, which holds `Beetle ESP32-C6.kicad_mod` and `beetle_esp32-c6.kicad_sym`. That part holds.
  - "Only DFR1117 had a footprint file" is unchecked for the others. The SEN0526 CAD zip was never downloaded (sen0526 diary:55, "Not downloaded"), and the DFR0995 "library zip" was never opened (dfr0995 diary steps 8 and 16 open only the STP zip).
  - "None reached verified hole and pin positions" holds only as a statement about the `verified` flags I read in the four walk JSONs (`pin_order_proof.verified: false` in all three part records, and a board has no per-fact flag). It does not hold as a statement about what DFRobot published:
    - SEN0526: the holes and the header row are dimensioned (diary:51-52).
    - DFR0995: the holes are dimensioned at x = 2.0 and 42.5 on the centreline (diary:55).
    - DFR1117: header coordinates come from DFRobot's own footprint (diary:63).
  - Change the sentence to: "None of the 4 records holds hole and pin positions marked verified: a part record has no field for them, and the rule marks a drawing read unverified. DFRobot dimensioned holes for 2 of 4 (SEN0526, DFR0995) and header positions for 2 of 4 (SEN0526 drawing, DFR1117 footprint). Height or thickness was missing in 2 of 4 (DFR0457, DFR1117). The CAD zips of SEN0526 and DFR0995 were not opened."
- **★C2 · partly.**
  - Read at council/tech-lead.md:9: "The validator is open: a scratch record with top-level `picture` and `mounting_holes` keys was accepted without a word".
  - Reproduced: I added `picture`, `mounting_holes` and `zzz_nonsense` to a skeleton. `parts.py --validate` listed only the four `body_mm`/`pin_order` problems.
  - "No field" is stronger than the code:
    - `facts.<any name>` is an open bag that `--fact-set` writes. The walk's DFR0457 record holds `facts.mounting_holes` with a value, source and cites.
    - `documents` holds the picture and the schematic as entries.
    - `legs` holds pin positions in prose.
    - `footprint` names a connector (`jst_ph_3`).
  - Change it to: "A part record has no *typed* field for a picture, a schematic, hole or header coordinates or connectors. They can only go in as ad hoc `facts` entries or `documents`, which no reader uses."
- **★C3 · holds.**
  - Read at scripts/spark/breadboard/drawing.py:387: `raise NotDrawnError("nothing says how to draw %s in Wokwi" % component, NO_DRAWING_FACT, component)`.
  - Read at drawing.py:150: `"no Wokwi pin positions for %s in data/wokwi-geometry.json"`.
  - Read at sheet.py:276-277: `except drawing.NotDrawnError as stopped: return PlannedLayout(None, stopped, [])`.
  - The `parts` keys of `data/wokwi-geometry.json` are `board-xiao-esp32-c6`, `wokwi-led`, `wokwi-resistor` and `wokwi-pushbutton`. One nuance: a *board* can also be drawn from its own record (`RecordShapeSource`), so the "4 types" limit binds parts only.
- **★C4 · holds, but the "caveat: none" is wrong.**
  - Reproduced: `parts.py --need "load switch"` answers "nothing in the library matches 'load switch'". `--need ESP32-C6` answers "nothing in the library matches 'ESP32-C6'".
  - The drawer file `dfrobot-dfr0457.json` holds `"count": 8`, `"is": {"part": "dfr0457-mosfet-power-controller"}` and `"function": [{"does": "drive", "what": "load-switch"}]`. The shelf holds the record.
  - The dropped caveat: scripts/spark/sourcing/datasheets.py:25-26 reads "`--need`'s matcher (P211). A default changes only with the PO's yes." and `NEED_MATCHER = "name-contains"`.
  - A function- and board-aware matcher already exists (`matching.py:22`: `WEIGHTS = (("functions", 1.0), …)`, and line 89 handles `kind == "board"`). It serves `--match` only, so `--need --matcher word-overlap` answers "word-overlap is no matcher for --need".
  - So the fix is a P211 decision that the PO holds, not a bug. The `--need` item in items.md should say so.
- **★C5 · partly.**
  - Reproduced: `--unverified xiao-esp32-c6` and `--sources xiao-esp32-c6` both answer "parts.py: no part called 'xiao-esp32-c6'." with exit 1.
  - Read in commands/research.md: no step researches a dev board. Holds.
  - "`--skeleton` has no board kind" is wrong as worded: `--skeleton zz-board --kind board --vendor dfrobot --dry-run` answers "would write …/parts/zz-board.json", exit 0.
  - Change it to: "`--skeleton` writes only `parts/<id>.json`; nothing writes a `boards/<id>.json` skeleton."
- **★C6 · holds, all eight reproduced or read.**
  - `--skeleton` writes line 24 `"sourcing": [],` and line 25 `"//sourcing": "Where it can be bought, one entry per listing actually fetched: {seller, url, price_czk, checked}…"`. "With prices" is too strong: it writes an empty list and a comment asking for prices.
  - `--skeleton dfr0457-mosfet-power-controller --dry-run` answers "would write …/parts/dfr0457-mosfet-power-controller.json", with no shelf warning.
  - `--fact-set` with `legs` or `host_requirements` answers "a fact write is a JSON object of facts the chain reads: footprint, pin_order, pin_order_proof, body_mm, simulation, or `facts` entries by name…".
  - `--read` gives `supply_voltage FOUND p3:10 [ABSOLUTE MAXIMUM RATINGS] Supply Voltage | −0.3 to 4.0 | V`, `snr FOUND p12:16 [REVISION HISTORY:]` and `input_high NOT FOUND`.
  - `check_vendor_pins.py` answers `MISMATCH (8 pins against … dfrobot_beetle_esp32c6/pins_arduino.h)`. TL-17 left one point open; I settled it by reading the code: `vendor_pins_check.compare()` (lines 78-97) reads no comment, so a `//pins` comment cannot clear it.
  - `boards.py --validate` answers `active beetle-esp32-c6 (project): ok` on a record with `wokwi_is_stand_in: true` and no `documents["wokwi-board"]`. boards/README.md:185 reads "A stand-in's `documents["wokwi-board"]` entry cites the stand-in's own file".
- **★C7 · refuted.**
  - Read at datasheets.py:31: `KEEPABLE = (".pdf", ".jpg", ".jpeg", ".png", ".webp", ".svg")`. That half holds for `--fetch`.
  - "So they have no route into the store" is false. Today the store holds `sources/068d…/DFR1117_beetle-esp32-c6_datasheet_V1.0.zip`, `sources/8268…/layout.zip` and `sources/eb88…/DFR1117_beetle-esp32-c6_schematics_V1.1.zip`, all kept by `--keep <file> --url`.
  - walk/dfr1117/diary.md:44 reads "`--keep` keeps the zip". TL-20 says the same, and the brief dropped it.
  - Change it to: "`--fetch` skips zips, so a vendor zip needs a hand download and `--keep`. No command reads inside a kept zip."
- **★C8 · holds.**
  - Read at walk/sen0526/sen0526-i2s-mic.json:282: "Wiring the first two by the table swaps 3V3 and GND."
  - WebFetch https://wiki.dfrobot.com/dfr0995/ returned "Operating Voltage" | "3.3V" and "VCC" | "DC3.3V-5V".
  - DFR1117 VIN: I rendered the kept V1.0 schematic myself:
    - The U6 TYPE-C pins A4, A9, B4 and B9 (VBUS) are labelled with the net VUSB.
    - P4 pin 3 is VUSB.
    - D3 1N5819W sits after VUSB, on the way to the RT9080's VIN.
    - So there is no diode between the VIN pad and the host's VBUS. In the V1.1 PDF, text extraction shows the same labels; I did not view that render.
  - No shipped board record (`xiao-esp32-c6`, `firebeetle2-esp32s3`) has `host_requirements` or a warnings key.
  - The caveat should say "a schematic read by Claude (V1.0 viewed), not measured".
- **★C9 · partly.**
  - Reproduced: 112 drawer files, and 99 match `"dfrobot"` (all 99 have maker and seller dfrobot). The composition holds: the `--drawer` output lists "Electric Solenoid Lock", "Monocrystalline Solar Panel (5V 1A)", "DFRobot Black Friday $1 Mystery Box", cables and motors.
  - "About 19 of 112 drawer rows link a record" is wrong. Counted by the `is` key, 16 of 112 entries link a record, and only **8 of the 99 DFRobot entries** do. The 19 is `grep -cE ' (part|board) '` on printed text.
  - Change it to: "16 of 112 drawer entries link a record (an `is` key); 8 of the 99 DFRobot ones do."
  - PO-2's "about 80 unlinked entries" becomes 91.
- **★C10 · partly.**
  - The diary counts:
    - Fetches: DFR0457 "3 of 12", DFR0995 "8 of 12", SEN0526 "1 of 12" plus 5 `--fetch` downloads, DFR1117 "10 of 12".
    - URL checks: 16, 7 and 7. DFR1117 ran none, because `--sources` refuses boards.
  - So the ranges are 3 to 10 fetches and 7 to 16 URL checks over 3 walks, not "3 to 8" and "5 to 16". council/user.md USER-32 already says "3 to 10 fetches", and the brief took the tech lead's narrower figure.
  - The wall times are the agents' estimates. All four started at 09:30 in parallel. The SEN0526 diary:68 says its own clock showed "09:30 to about 09:36", and it estimates 25 min "plus model time".
  - "99 records are 300 to 800" multiplies by 99, which C9 says is not the number of modules.
  - Change it to: "1 to 2 searches, 3 to 10 fetches and 0 to 16 URL checks per record (DFR1117 could not run `--sources`); 7 to 30 min estimated wall time; the product with the scope of Q3, not 99."

## 2. Brief against its detail

Caveats the brief dropped:
- **The walks were Claude's, not the PO's** (council/user.md line 3 and USER-34: "the friction list above is a prediction from walks and code, not from a PO bench session"). risks-and-tests.md "usability" says "the PO meets about 20 hand steps per part", which is stronger than its source. The PO met none, and USER-34 adds that no wiring from a sheet has run yet.
- **The store was written, not only read.** Frame "Start and reach" says "the store and drawer (read)". Today 17 files were added to `~/.local/share/spark/sources/`, 3 of them zips.
- **The `--need` matcher is a P211 decision** (see ★C4). Option "fix the bugs first" and item "`--need` finds an owned part by what it does" treat it as a bug.
- **No reader for the new fields** (TL-27, PO-5, the DFR0457 diary's last gap). The brief puts this only under ★C3's caveat. Its Options and the story map still start with writing holes and pictures.
- **The 16 account questions of the user lens** and its Q17 ("are the walks accepted as stand-ins for the PO's journey") are absent from Questions.
- **PO-27 has its own way out**, in PO-27 itself: P446 lets "a person, Claude or a tool" write a file spark reads as unverified. C13 says the cards "disagree", which is stronger than the source. See part 3.
- **The tech lead's sequencing question Q-TL2** (may a field be written before its reader?) is not carried into Questions or the no-gos.
- **The searches used by the PO assistant.** Frame "Budget" says "3 by the PO assistant". council/po-assistant.md:79 says "3 allowed, 2 made", and its Searches section lists 2.

Claims stronger than their source:
- **TL;DR**: "Twelve tool bugs and gaps make each record a hand job". No file counts twelve: ★C6 lists 8 and items.md proposes 8 items. Give the list or drop the number.
- **A1, "E against it, 0 of 4 (★C1)"**. By A1's own wording ("a dimension drawing with holes and header positions, or a footprint"), the diaries give:
  - SEN0526: both.
  - DFR1117: a footprint, and the board has no holes.
  - DFR0995: holes only.
  - DFR0457: hole spacing only, no edge distances.
  - That is evidence *for* A1 on 2 of 4, mixed on 2. The "0 of 4" counts record flags, not publication. The feasibility row of risks-and-tests.md repeats the error.
- **The A1 pass line**: "at least half of the PCB modules link a dimension drawing". All 4 walked parts link one (PO-10: "4 of 4 a dimension drawing"), so the line is close to met before the spike runs, and it tests a link, not the content. "3 of 5 read drawings give hole positions" was met by 3 of 4 walked parts already. As set, the spike can hardly change the decision.
- **The story map, slice 4 proof**: "the sheet draws DFR0995 with its real header". DFR0995's header pitch and pad positions are "not published" (dfr0995 diary:64), so no strategy that reads DFRobot can meet this proof. Pick SEN0526 or DFR1117.
- **The story map, slice 2 proof**: "the DFR1117 layout zip kept, its footprint read". The zip is already kept (★C7), so only "read" remains.
- **Outcome proof**: "`parts.py --show <id>` for each walked part". `parts.py --show beetle-esp32-c6` answers "no part called 'beetle-esp32-c6'". The proof is unreachable for DFR1117 unless boards join `parts.py`.
- **C16**: "`vl6180x-breakout` and `led-red-5mm` say true". `parts/vl6180x-breakout.json` has `pin_order_proof.verified: false`. Its *schematic-read facts* (for example `i2c_pullup_ohms`) are `true`. Only `led-red-5mm` marks a pin order `true`. The source (sen0526 diary:40) says "schematic readings", and the brief narrowed it to "pin order".
- **USER-25**: "Hole positions in the record are scaled from drawings by Claude". That holds only for DFR0457. DFR0995 and SEN0526 read dimensioned values. This is not in the brief, but jobs-and-journeys.md's Job 3 rests on the user lens.
- **Job 2**: "so I do not swap 3V3 and GND [E ★C8]". ★C8 shows a vendor table that could cause it. No source shows the PO did it (the user lens Q2 is unasked). Tag it H.
- **C12**: "0.6 A against 2 A" are the regulator chips' ratings (RT9080 "up to 600mA", TPS62A02 IOUT 0 to 2 A), not board figures. The wiki gives only the part names. The 14 µA and 37 µA hold, read in the kept wiki: "Sleep Current (Deep Sleep Mode, Battery-Powered) Version 1.0: 14μA Version 1.1: 37μA".

What could break for current users, which no section covers:
- **Renaming in the DFR0457 shelf record** (C15 and items.md "loses the irrigation wording"). The record's `based_on.project` is `irrigation`. Renaming the signal `VALVE_CTRL` would change the pin map that project's firmware imports. The walk renamed it in a scratch copy only. Not checked: whether the irrigation project still reads the shelf copy.
- **Making `boards.py --validate` refuse a stand-in with no `documents["wokwi-board"]`** would fail any user's own project board written that way. The shipped boards pass: both have the entry.
- **Relaxing `check_vendor_pins` for bare numbers** would also pass an invented numeric label. That is the error class its message names.
- **Closing the open validator** (★C2) would refuse the ad hoc keys the walk records already use: `also_known_as`, `sku`, `variant`, `facts.mounting_holes`.

## 3. Rival explanations not ruled out

- **★C1 and A1.**
  - The folder reads: DFRobot does not publish enough geometry.
  - Rival: DFRobot publishes enough for most of the parts walked. Spark has no field to hold the data, and its own rule marks a drawing read unverified (C16), so "verified" can never be reached from a drawing.
  - The diaries support the rival as much as the reading.
- **★C10 and the "hand job" in the TL;DR.**
  - The folder reads: the research flow itself is costly.
  - Rival: these were first-time walks. Each agent read code to learn the flow (dfr0995 step 9 and sen0526 Gaps read datasheets.py), and a second run of the same flow is cheaper. The cost may also be dominated by reading drawings as images, which no pipeline removes. Nothing measures which share is which.
- **★C4.**
  - The folder reads: reuse-first has a bug.
  - Rival: `--need` is name-only by a recorded P211 default, and function matching lives in `--match` (WordOverlap). Before calling it a miss, the folder should show whether `/spark:idea`'s `--match` path finds DFR0457 by function. I did not test `--match`.
- **★C3, PO-17 and D2's value.**
  - The folder reads: records hold too little.
  - Rival: the bottleneck is the drawing code (P734, which waits on another session's split). Fuller records would then add nothing visible, whatever the pipeline, until P734 lands.
- **★C8 and A6.**
  - The folder reads: vendor pages cause wiring harm.
  - Rival: the harm is prospective. The record already carries the SEN0526 swap warning in `host_requirements`, which the sheet prints, so the gap is the board-record warning only (DFR1117 VIN).
- **C13.**
  - The folder reads: P446 and P734 disagree on AI shapes.
  - Rival: P446 forbids a *shape source* that calls an AI at run time. It lets Claude write a file read as unverified (PO-27's own quote). P734's "AI generated and vectorized" can be exactly that file.
- **C11.**
  - The folder reads: the arithmetic is wrong.
  - Rival: the note meant that 12 V is outside DFRobot's stated "3.3~10V DC" logic range (shelf record `logic_signal_range_v`) and named the wrong limit. The fix is a reworded note, not a new limit.
- **C14.**
  - The folder reads: part-data.md is wrong.
  - Rival: the zip entries are dated 10-31-2024 (`unzip -l`), so DFRobot may have added layout zips after the reference was written (2026-10-12 per git), and only for some SKUs. "Wrong for one SKU" is all the folder shows.
- **★C9.**
  - The folder reads: the 99 includes non-modules.
  - Rival for the scope: the drawer marks `maker: dfrobot` on all 99, including a NVIDIA Jetson kit. Maker is set from the seller, so a "DFRobot part" count also needs a maker check.

## 4. Numbers that lack a unit, population, period or provenance

- "6 H" (Stands on): six of what? It is unclear whether this means assumptions A1 to A6 or claims tagged H.
- "Twelve tool bugs and gaps" (TL;DR): no list and no source.
- "the existing 16 records" (Start and reach): 8 library parts plus 8 shelf records. It leaves out the 2 library boards and the catalog's 18 drafts, and it gives no date. TL-30 says "the shelf already holds 9", and the shelf holds 8 JSON files plus one folder.
- "99 DFRobot drawer entries": entries, not pieces (DFR0457 alone is count 8). As of 2026-11-10. "DFRobot" means maker as recorded by the drawer import.
- "about 19 of 112": a text grep, and 16 by the `is` key.
- "H about 50 to 60" PCB modules: read off the list, not counted. No date and no rule for what counts as a PCB module.
- "1 to 2 searches, 3 to 8 fetches, 5 to 16 URL checks": "fetch" mixes WebFetch, curl, `gh api` and `--fetch` downloads. The ranges do not match the diaries (see ★C10). The population is 4 parts picked by Claude for shape variety.
- "7 to 30 minutes of agent time": wall time by four agents started together, estimated. It holds no token or cost figure, and P209 (PO-24) has one: "113k tokens, 5.5 min for one part".
- "300 to 800 fetches": multiplied by 99 entries, not by the in-scope modules.
- "about 20 hand steps per part" (risks-and-tests.md, jobs-and-journeys.md): the diaries hold 17 to 31 numbered steps (commands, reads and edits) and 1 to 3 hand edits each. The unit is undefined.
- "0.6 A against 2 A": regulator-chip limits, not board limits, from the chip datasheets.
- "23 mA at 12 V": calculated with VF 1.2 V typical and a 470 Ω read off a schematic image, unverified.
- "0 circles" (no-gos, DFR0995 STEP): counted by the walker in a file deleted from scratch, and not reproducible now.
- The pass line "at least half of the PCB modules": the denominator waits on Q3.
- "4.56", "2.66" (TL-5) and the sleep figures are fine as stated, with their sources.

## Searches

- WebFetch https://wiki.dfrobot.com/dfr0995/ (read 2026-11-10) · the decision it served: ★C8 holds or not. It served ★C8's DFR0995 half, whether the two voltage rows exist. Used.
No web search was made.

## What I could not check, and why

- Whether the SEN0526 CAD zip or the DFR0995 library zip holds a footprint: neither is in the store, and downloading them was outside my brief.
- Whether `parts.py --match` (WordOverlap) finds DFR0457 by function: it needs a project with needs set up, and I did not build one.
- DFR1117 V1.1: I read the schematic's VIN wiring by text extraction only and did not view a render.
- The SEN0526 and DFR0457 wiki pages: not re-fetched. Their quotes come from the diaries and records.
- The irrigation project's use of the DFR0457 shelf signal name: not checked.
