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

## Second pass

Model: Opus. Read the sections changed in commits ef5ab9e3 and 3fbebe9b, the three arch reports and verification.md. Commands were read-only: `git diff`, `boards.py --help`, a grep in `~/Development/irrigation` and in `scripts/spark/sourcing/matching.py`. Nothing in the tree changed except this section.

### 2. Changed sections against their detail

First-pass corrections:
- Applied as worded: ★C1, ★C2, ★C5, ★C7, ★C9 and ★C10. ★C4's caveat is applied too, and "`--match` already reads drawer functions" holds: matching.py:84 reads "with the live drawer entries that say they are it: their functions and tags join".
- Not applied, though the files around them changed:
  - The TL;DR still says "Twelve tool bugs and gaps". It also says "The record has no field for a picture, a schematic, holes or connectors", which contradicts the corrected ★C2 ("no *typed* field").
  - risks-and-tests.md "usability" still reads "the PO meets about 20 hand steps". The PO met none (USER-34).
  - risks-and-tests.md "viability" ("300 to 800 fetches for 99 records") and the Q2 batch option ("300 to 800 fetches") still multiply by 99, which the corrected ★C10 says not to do.
  - C16 and the chore item still say "the two library records". `vl6180x-breakout` has `pin_order_proof.verified: false`.
  - The as-is journey row 1 still reads "about 19 of 112".
  - story-map.md slice 8 still proves "the sheet draws DFR0995 with its real header". walk/dfr0995/diary.md:62 reads "Header pitch and pad positions: not on the wiki page, the dimension PNG … or the schematic".
- verification.md "the refuter [read the walks] as evidence for it [A1]" is stronger than my first pass, which said "for A1 on 2 of 4, mixed on 2".

Q6 and the class diagram against council/arch-architect.md:
- The diagram is titled "A with C's additions", but it leaves out C's own additions: `Scheduler`, `PlanEntry` and `Budget` (architect :192-210). It also drops A's `RecordWriter`, `DatasheetSource`, `FootprintFileSource` and `DrawingSource`, and it adds a `DocumentSource` that no report names.
- The diagram drops `outside` from `run(subject, project, outside)`. ARCH-16 makes the four interfaces conditional on it: "gets these interfaces for free only if it is an `Operation` and reaches the outside through `OutsideWorld` alone". Option A's "rests on" line ("one core serves the CLI, Claude, a LangGraph node and a person") drops that condition too.
- "The store is a port, so a shared store or a RAG index is a later adapter (D6)" is stated as fact. The architect leaves it open (Q-A9: "is the store port … part of this epic's MVP"), and ARCH-17 says that no port exists today.
- Q6 says "nine detail questions". arch-architect.md:308-317 holds ten (Q-A1 to Q-A10), and Q-A1 is Q6 itself.
- C's caveat keeps "over-designed plan format". It drops the architect's second risk: "the per-source budget duplicates `run_cost`".

The story map against council/arch-ux.md and the architect:
- Slice 0 ("one source kind, the DFRobot site") does not support the proof items.md expects of slice 0 ("`--show sen0526-i2s-mic` with the picture, outline, holes and header row"):
  - The typed geometry home arrives only in slice 3.
  - SEN0526's holes come from a dimension drawing. The architect's `VendorSiteSource` reads "HTML, no AI", and `DrawingSource` answers a `NextStep`.
  - The architect's MVP (:102) has four source kinds and the `physical` block. The UX slice 0 has one kind and no geometry. The map joined the two and kept neither one's proof consistent.
- Slice 6 drops the UX caveat that the LangGraph and RAG slices start no earlier than v0.13: "Neither starts before v0.13" (arch-ux.md:157).
- Slice 4 (an MCP source) drops REUSE-10: "do not plan on a vendor MCP for DFRobot MVP". The reuse lens found no DFRobot MCP, so slice 4 has no DFRobot proof part.
- Slice 1 settles "per person and per project". That is the UX lens's open question 5.
- The pointers are loose:
  - arch-architect.md:275 is the comparison heading. The walking skeleton is at :102 and :269.
  - In jobs-and-journeys.md, the to-be PO rows cite arch-ux.md:65 to :73. Those are two lines early: row 0 is at :67, and step 8 is at :75, not :73.

risks-and-tests.md and the brief:
- The value row says "a reader ships with slice 0". A2's pass line says "the reader is in slice 0 or 4". The rewritten story map puts the reader in slice 8, so A2's line is missed by the map that was proposed at the same time.
- A1's evidence ("3 of 4 … holes or headers") counts with *or*. The pass line ("give hole and header coordinates") counts with *and*. Under the pass line's own rule, the walked sample meets it for 1 of 4 (SEN0526). For DFR1117, a board with no holes, the line cannot be met unless "not applicable" counts.
- The test reads "5 drawings at random". The pass line counts "10 owned PCB modules picked at random, at least 7". items.md's spike says five, so the test cannot produce the count its line needs.
- The Riskiest line is still labelled "the PO assistant's opinion". It now asserts the opposite reading of the walks to the PO assistant's (verification.md Split 1).
- The TL;DR says "DFRobot published most of the geometry". ★C1's caveat says "not how often".

items.md, the chore:
- "renamed only with the PO, because the signal `VALVE_CTRL` is in the irrigation pin map". `~/Development/irrigation/parts/dfr0457-mosfet-power-controller.json` is a project copy, and the project layer is read before the shelf (ARCH-8). So renaming the shelf record leaves irrigation's `firmware/pins.py` untouched. The reason given is not the operative one, and my first pass raised this risk without checking it.

The Outcome line:
- "`boards.py` for a board" names no subcommand. `boards.py --help` lists `--path --id --list --paths --validate --get --resolve`, and `--get` reads the active board only. The proof for DFR1117 stays unreachable as worded.

### 3. Rival explanations for the new interpretations

- **Architect: "C as the target, built as A first", and the batch as "one CLI loop".** Rival: the walk cost is dominated by Claude reading images (UX-11: 3 of 4 walks rendered pages by hand). A and C hand that to the agent as a `NextStep` too, so A's saving over B on a batch is unmeasured. No walk was run through the types (architect :303).
- **Architect: the conflicts list goes in the MVP "because the walks found a conflict in 3 of 4 parts (★C8)".** Rival: only DFR0995 is two sources disagreeing. SEN0526 is a table against a drawing, read as harm, and DFR1117's VIN is a single-source hazard, not a conflict. The basis is 1 to 2 of 4.
- **D5, "parts MCPs from manufacturers".** Rival: none serves DFRobot (REUSE-10). The MCP slot then serves only distributors that need keys, which runs against "free, few and local".
- **Job 5: "stops and questions as data".** Rival: D6 asks for reuse by other interfaces. It does not ask that every stop be typed data. That reading is the UX lens's H, and the architect's `NextStep` already covers it without a typed open list.
- **The story map's split of geometry into slice 3.** Rival: this followed the UX lens's slice order. It was not a decision that slice 0 shows no geometry, and items.md shows the authors still expect geometry in slice 0.
- **The chore's irrigation risk.** Rival: no risk, because irrigation reads its own project copy (part 2).

### 4. Numbers that lack a unit, population, period or provenance

- "Used: 13 in council/": the Searches sections count 10. That is PO assistant 2, tech lead 1, reuse 6, architect 1, UX 0 and refuter 0.
- "22 searches for the council": no source for the per-agent caps. Where the 8 for reuse and the 4 for the refuter come from is not written.
- "nine detail questions": there are ten.
- "6 to 8 / 4 to 5 / 7 to 9 modules": the architect's rough estimate, and "module" is undefined. Only A keeps "rough".
- "3 of 4" (A1, Riskiest, feasibility row): counted with *or*. It is 1 of 4 by the pass line's *and*.
- "10 … at least 7" against "5 drawings": two populations for one test.
- "about 20 hand steps" (usability row, Job 4 today, as-is row 3): the unit is undefined. The diaries hold 17 to 31 numbered steps, with 1 to 3 hand edits.
- "300 to 800 fetches" (Q2 batch option, viability row): multiplied by 99 entries.
- "about 19 of 112" (as-is journey row 1): 16 by the `is` key.
- "no silent 25 minutes" (to-be step 3): one walk's estimate (SEN0526), stated as general.
- "five end states", and "budget 4 requests" in the architect's sequence: design values, not measured.
- UX-16 and REUSE-14 still carry the old "3-8 fetches" and "5-16 URL checks". The brief does not use them, but story-map and Job 5 cite the UX lens.

### Searches

No search.

## Third pass

Model: Opus. Read brief.md, verification.md, story-map.md, items.md, risks-and-tests.md and the cited code. Commands were read-only (`sed`, `grep`). Nothing in the tree changed except this section.

### 1. ★C17 and ★C18 against their sources

- **★C17 · partly.**
  - council/fact-tree.md:9 reads "Spark has no single place that says \"this consumer reads this fact\"". The brief says "No code or file says which consumer reads which fact", which drops "single". Code does say it in places: scripts/spark/records/missing_facts.py:15 reads "#: Each role whose active level a stage needs, and what the level means for it", and scripts/spark/records/record_kind.py:36 reads "#: The facts the chain reads from a part record (§5.4)".
  - "tuples in code": `ACTIVE_LEVEL_MEANING` is a dict (missing_facts.py:16, `ACTIVE_LEVEL_MEANING = {`), and `PART_GAPS` is a tuple of (finder function, code, sentence) (board_emitter.py:92), not of fact names.
  - Holds: record_kind.py:37 reads `CHAIN_FACTS = ("footprint", "pin_order", "pin_order_proof", "body_mm", "simulation")`. commands/research.md:65 reads "## 3. The facts each kind needs — and nothing else", with 5 rows (:69-73). No .py in scripts/ or tools/ reads it: the three files that name research.md use it in a docstring or a length budget. `grep -rn --include=*.py -e sel_has_pull -e sd_pulldown_ohms -e needs_mclk scripts tools tests` returned nothing (exit 1).
  - Change to: "No single place says which consumer reads which fact. The need lives in four unconnected forms: tables in code (`CHAIN_FACTS`, `LAYOUT_FACTS`, `PART_GAPS`, `ACTIVE_LEVEL_MEANING`), pointers …"
- **★C18 · partly.**
  - "`OperationResult.next` returns the step a caller must do": result.py:52-53 reads "`next` the NextSteps", and :17 reads "#: Value: a step an agent may take next". "may", not "must". result.py:50 is `class OperationResult(...)`, as cited.
  - "an Operation declares effect words such as `asks`": holds. scripts/spark/core/operation.py:22 reads `READS, RUNS, BOARD, DELETES, WRITES, ASKS = "reads", "runs", "board", "deletes", "writes", "asks"`.
  - "every Operation reaches the outside only through `OutsideWorld`": refuted by the cited page. docs/guide/patterns-and-names.md:69-70 reads "The rest of the outside (the project's files, the store, and the child Python that `image_evidence.CompileCheck` starts) still goes direct, and moves behind the outside with its own card." outside.py:4 reads "the other fields (`write`, `fetch`, `environ`) enter with their first Operation". A research Operation needs `fetch` and the store, which OutsideWorld does not hold yet (ARCH-16's condition).
  - `FakeOutsideWorld`: holds, tests/fakes.py:334.
  - "`GrantStore` with `GrantService` keep a prepared, expiring yes per board for deploy": board_grant.py:147 is `class GrantStore:`, :211 `class GrantService:`. Its docstring (:148) reads "one JSON file per board and scope … grants/…json (live) and grants/…-deploy.json (deploy)". Two scopes, live and deploy, not deploy only.
  - Missed, and the closest fit to D12: the consent Strategy. scripts/spark/bench/deploy_gate.py:50 reads `class ConsentStrategy(abc.ABC):` with "Strategy: how the person says yes to a question". Its subclasses are `TerminalConsentStrategy` (:82, typed live), `RelayedConsentStrategy` (:110, "a yes that another program collected … as MCP's elicitation asks through the client") and `StandingConsentStrategy` (board_grant.py:178, "the yes a valid deploy grant gives … in place of a yes typed per run"). outside.py:19 reads "`make_consent(line)` gives the ConsentStrategy that asks the person for the yes". That is a live, relayed and prepared (scripted) yes behind one interface, which is what D12 asks about.
  - Change to: "… `OperationResult.next` lists the steps a caller may take (`NextStep` has `needs_yes` and `needs_person`), an Operation declares effect words such as `asks`, `OutsideWorld.make_consent` gives it a `ConsentStrategy` (typed in a terminal, relayed by another program, or standing from a grant), and `GrantStore` with `GrantService` keep an expiring yes per board and scope (live or deploy). Files, the store and fetches still go direct, not through `OutsideWorld`. · E … scripts/spark/bench/deploy_gate.py:50, scripts/spark/core/outside.py:19, docs/guide/patterns-and-names.md:69 · caveat: read for this claim, not for a design". verification.md row ★C18 then reads "refuter: partly".

### 2. Hand-off against the D rows

- The D rows' quotes match the other copies: D8 is word for word the quote at council/fact-tree.md:5. D5, D6 and D12 are given verbatim with the typos.
- "A reader shows the geometry within the first four slices (D7, A2)": D7 reads "confirms the ratings, not the pass line". The A2 pass line in risks-and-tests.md:26 ("set 2026-11-10: a reader is in the first four slices") names no decider. The Hand-off states as the PO's what no D holds. Change to "(A2's proposed pass line, not decided)", or get a D.
- "conflicts are kept side by side" in Outcome: this is option C's conflicts list (the architect's H, brief :59), not a D. Mark it H or move it under Options.
- Constraints, "one interaction mechanism for all of spark … built from the parts in ★C18": D12 asks a question and says "maybe" ("Do we have some interface or delegate or anything that we could reuse ? … maybe we could just refactor it for whole spark"), and its last sentence names "the communication with the board in spark". "Built from the parts in ★C18" is Claude's answer to the question, made a constraint, and it rests on a claim that is partly (part 1). Change to "reuse what spark has where it fits (★C18; the PO asked, D12)".
- "Confirmed by the PO (D11)": D11 confirms the jobs and the to-be map, not the Constraints or the Outcome lines above. Say "the jobs and the map confirmed (D11)".
- Stale status after D7 and D10: brief :93 Riskiest still reads "proposed — the PO assistant's opinion, pending Q1", :94 Test reads "proposed — Claude's opinion, after the refuter, pending Q1", and risks-and-tests.md:25 reads "proposed, set 2026-11-10". D10 confirmed that line. Cite D10 and drop "pending Q1".

### 3. Second-pass findings

verification.md:24 says four were fixed. Checked:
- Fixed: TL;DR number and "typed field"; the usability, viability and Q2 batch rows; the as-is row "16 of 112"; the slice proof moved from DFR0995 to SEN0526; the store port shown as open (Q-A9); "ten detail questions"; `outside` back in `run`; the reader now in slice 3 (within A2's line); slice 0 has two source kinds and a geometry home; the irrigation reason in items.md:88; brief Riskiest counts with "and".
- Not fixed:
  - C16 (brief :123) and items.md:88 still say both library records mark a drawn pin order true. `vl6180x-breakout` has `pin_order_proof.verified: false` (first and second pass).
  - verification.md:21 still says the refuter read the walks "as evidence for it". The first pass said "for A1 on 2 of 4, mixed on 2".
  - risks-and-tests.md:8 and :25 still count A1's evidence with "or" (3 of 4) against a pass line with "and".
  - Option A's "rests on" (brief :57) still drops ARCH-16's condition ("only if it is an `Operation` and reaches the outside through `OutsideWorld` alone"). Part 1 shows that condition is not met today for files, the store and fetches.
  - Option C's caveat still drops "the per-source budget duplicates `run_cost`".
  - story-map.md slice 4 (MCP) still carries no REUSE-10 note (no DFRobot MCP found), slice 6 no "neither starts before v0.13" (arch-ux.md:157), slice 1 still settles "per person and per project" (UX open question 5), and story-map.md:5 still cites arch-architect.md:275 (the comparison heading).
  - jobs-and-journeys.md:65-73 still cite arch-ux.md:65 to :73. Row 0 is at :67 and step 8 at :75.
  - Outcome (brief :13) still proves a board with "`boards.py`", which names no subcommand that shows a record.
- New in slice 0: "Geometry has a typed home (the board record's `physical` keys)" for SEN0526, a part. `physical` is read for boards only (council/fact-tree.md:19, TREE-11). Say whether a part record gains `physical` or what its home is.

### Searches

No search.
