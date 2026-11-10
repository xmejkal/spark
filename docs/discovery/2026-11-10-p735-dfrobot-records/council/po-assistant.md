# P735 council: PO assistant (Existing first, Risks and assumptions)

Tags: E (pointer), H (source), D (who, when), — unknown. Paths are repo-relative or use ~. "walk/x" = docs/discovery/2026-11-10-p735-dfrobot-records/walk/x/diary.md.

## 1. Findings

Existing, inside spark

- PO-1 · spark has no command that walks a part from a name to a full record. research.md covers a commodity part (part-finder + datasheet-reader) and a module (parts-researcher); it has no step for upgrading an existing record, no board path, and its `allowed-tools` lists no boards.py/init_project.py/emit_footprint.py/check_vendor_pins.py · E · commands/research.md:1-115; walk/dfr0457 "Gaps in the flow" 1; walk/dfr1117 "Gaps" 1-2 · supports: card claim "several steps by hand"
- PO-2 · The drawer lists 112 entries, 99 are DFRobot (file count: `grep -l '"dfrobot"' ~/.local/share/spark/drawer/*.json` gives 99); about 19 rows show a linked part/board (`parts.py --drawer | grep -cE ' (part|board) '` gave 19, rough, since a name could contain the word) · E · command above · supports: a "full record" job is about 80 unlinked entries, not 99 fresh ones
- PO-3 · The 99 are not 99 modules. The list holds cables (GDI-Line x3, Gravity 4-pin cable, JST/LED-strip connectors), a solar panel, motors, a lock, a solenoid valve, a heatsink, a mystery box (the PO: skip), a Jetson kit, a speaker. For these "holes, schematic, PCB" mostly has no meaning · E · `parts.py --drawer` output · supports: the count of records to make is smaller than 99 and the denominator is undefined (—: how many are PCB modules; H: roughly 50-60, from reading the list, not counted)
- PO-4 · Record fields today: `body_mm`, `footprint` (a bare string, no verified or source), `pin_order` (+proof), `legs`, `simulation`, `documents`, `facts` by name. No image/picture field, no holes, no second connector, no thickness/height, no revision, no schematic summary, no 3D reference · E · walk/dfr0995 "No place in the record"; walk/dfr1117; walk/sen0526; part-data.md:61 lists a "3D model reference" under what to store but no key exists (walk/dfr0457 gaps)
- PO-5 · `mounting_holes` is written by `--fact-set` as an ad hoc fact but no script reads it (grep in the walk) while AGENTS.md says records grow only when a check/stage/PO needs a property. The PO's ask ("holes, connectors") and the rule conflict until a reader (breadboard, board display, enclosure) exists · E · walk/dfr0457 last "Gaps" bullet; AGENTS.md "Records grow by need" · supports: each new field needs a named consumer
- PO-6 · Tools that write a record lack: `--fact-set` refuses `legs` and `host_requirements`; `--fetch` cannot keep a .zip (KEEPABLE = pdf/jpg/jpeg/png/webp/svg), so DFRobot's STEP, CAD and layout zips have no route; `--read` cannot read a schematic and renders no page (the agent uses pdftoppm/sips by hand); `--fetch` names documents by CDN hash and leaves title/version null; `--skeleton` writes a `sourcing` block with prices that research.md forbids; `--need` ignores boards, the drawer's `function`, and synonyms (colour vs TFT, ESP32-C6 vs xiao) · E · scripts/spark/sourcing/datasheets.py:31; walk/dfr0457 Bugs; walk/dfr0995 Bugs; walk/dfr1117 Bugs; walk/sen0526 Bugs · supports: a refactor must fix these first or a 99-part run repeats each by hand
- PO-7 · Silent-wrong readers: `--read --want supply_voltage` reported FOUND on the absolute-maximum row; `--want snr` FOUND on a revision-history row; `--unverified` drops a record's own why_it_matters; `check_vendor_pins.py` exits 1 for any board with bare-GPIO silkscreen · E · walk/sen0526 Bugs 1-2; walk/dfr0995 Bugs 2; walk/dfr1117 Bugs 3 · supports: scale multiplies wrong facts that look checked
- PO-8 · The existing 16-record picture: 8 library parts, 8 shelf records; every one has `body_mm` and `footprint`; 2 of 8 library records name a Wokwi part that the drawing can use · E · file listing of parts/ and ~/.local/share/spark/shelf; P734 #1005 body ("2 of 8 records ... read at b4649788") · supports: more records do not draw more parts unless the drawing code reads record geometry (P734 not built)
- PO-9 · The shelf and the project diverge silently: `--fact-set` on a project copy leaves the shelf older with no line saying so; `--skeleton <id on shelf>` writes an empty project record that beats the 28 kB shelf record; no doc says how to bring a shelf record to a new project · E · walk/dfr0457 steps 8, 24, Bugs 2, Gaps 2 · supports: a "refactor and go over all records" run needs a rule for where the finished record lives

Existing, outside spark (what each does and does not)

- PO-10 · DFRobot's own downloads per SKU vary. DFR1117: schematic zip, dimension PNG, datasheet zip, and a layout zip that is a KiCad footprint+symbol (holes at 0.9 mm with coordinates); no STEP. DFR0995: dimension PNG, schematic PDF, STEP zip (B-spline only, hole positions not readable without CAD), library zip. SEN0526: dimension PDF, schematic, CAD zip, STEP zip. DFR0457: dimension + schematic only, no STEP anywhere · E · walk/dfr1117 steps 7-15, Not found; walk/dfr0995 step 8, 16; walk/sen0526 step 7; walk/dfr0457 steps 15, 19 · supports: 2 of 4 have a STEP, 1 of 4 a machine-readable footprint, 4 of 4 a dimension drawing; the rest of each geometry is scaled from images
- PO-11 · spark's own reference says "DFRobot ships no KiCad footprints"; the DFR1117 walk found one in its layout zip. The reference is wrong at least for that SKU · E · skills/spark-design/references/part-data.md:51-52 against walk/dfr1117 step 15 · supports: the source waterfall text is stale; do not rely on it for planning
- PO-12 · Wokwi: no FireBeetle element exists; a custom chip appears on a default green breakout; nothing found lets a person give a part its own picture. Date read 2026-10-12 (P209) · E · issue #178 evaluation section; #597 body · supports: a Wokwi diagram of an owned DFRobot module is a stand-in at best; unchanged since 2026-10-12 not re-checked (—)
- PO-13 · EasyEDA/LCSC and tscircuit registry are in the waterfall for bare ICs and jellybean parts (key on C-number); DFRobot modules are not mentioned there as covered · E · part-data.md:42-47 · supports: H that LCSC rarely holds a DFRobot breakout; no check made (—)
- PO-14 · SnapEDA/SnapMagic: models may be used in a design and the design conveyed under your own terms; sharing the model files themselves (e.g. a public repo) is restricted; text read 2026-11-10 through a search summary, not the licence file · E (secondary) · https://www.snapeda.com/questions/question/clarification-on-licensing ; https://scancode-licensedb.aboutcode.org/snapeda-design-exception-1.0.json · supports: SnapEDA files cannot go into spark's public repo; they could only be fetched into a person's store
- PO-15 · DFRobot's licence for its wiki downloads: I found no official terms page. Only a forum user says schematics on the site can be used for own projects. A DFRobot GitHub repo (DFResources) exists, licence not read · H forum post https://www.dfrobot.com/forum/topic/339015 (user statement) · supports: —; licence of wiki PDFs/STEP/KiCad files is unknown, so the safe rule is AGENTS.md: point (URL + sha256), keep only in the person's store, commit nothing
- PO-16 · Fritzing parts: no check made. DFRobot Fritzing files, if they exist, are not in any walk · — · supports: —

Who is blocked

- PO-17 · No walk, card or diary shows anyone blocked by a missing DFRobot record. The visible block is P734: build prints `no breadboard picture: nothing says how to draw Max98357aDfr0954 in Wokwi`, though that record already has `pin_order` and `body_mm`. So the missing piece for the PO's wiring view is the drawing code, not record fields · E · issue #1005 body "What is true today" · supports: a records run does not unblock the breadboard picture by itself
- PO-18 · Memory notes the sound lane (pixel-games PR #50) waits on the PO wiring the amp at his bench; that is a bench step, not a record · H memory spark-scrum-state (PO session 11-10) · supports: no one else named as blocked; the only user is the PO (n = 1)
- PO-19 · VISION names the PO as bench and the hobbyist as primary; the hobbyist's owned parts are not DFRobot's 99. Value of 99 records accrues to the PO's drawer first, to the hobbyist only if records become shared (the store epic is "later") · E · scrum/VISION.md personas table, versions table "later" row · supports: the epic's value is a PO-bench value until the store ships

Cost and scale

- PO-20 · The four walks took about 7, 12, 25 and 30 minutes each, by an agent, for one part each, and still left holes/pins "scaled, unverified" and many Not found items. 99 x 7-30 min is about 12-50 hours of agent time before any per-part human check (H: arithmetic on the walk times, includes no review) · E walk/*/diary.md Counts · supports: the run needs batching, a stop rule per part, and a choice of which parts
- PO-21 · Each walk found geometry not published: DFR0457 hole edge distances and corner radius; DFR0995 header pitch/positions and GDI position; SEN0526 pad ring; DFR1117 USB-C part number and thickness. Component height and PCB thickness were missing in 3 of 4 · E · each diary "Not found" · supports: "full record" is not reachable from public data; the record must carry "not published" as a value

Overlapping cards (read with gh issue view, 2026-11-10)

- PO-22 · P329 #421 (import from DFRobot and AliExpress, via Chrome, tests prove it); P340 #434 under it (research works from open facts, asks to look further). P329 still includes AliExpress, which P735 does not; P329 was "not before walk 1"; P330 #423 is closed · E · gh issue view 421, 434, 423 · supports: P735 narrows P329 to DFRobot; AliExpress remains homeless
- PO-23 · P206 #170 (chain-deciding facts sourced from DFRobot and Espressif; "NOT: records for parts nobody owns"; size and value "to refine") · E · gh issue view 170 · supports: P206 is facts, P735 adds geometry and pictures; both say "start from the drawer"
- PO-24 · P209 #178 (one way from look-up to a store record; "ready" is undefined: validates? drawer linked? sim stand-in? footprint?; its evaluation says 113k tokens, 5.5 min for one part with no maker data) · E · gh issue view 178 · supports: the "done" of P735 and the "ready" of P209 are the same open question
- PO-25 · P446 #597 (shape as data, `PartShape` in mm, sources are strategies that never call an AI or a program, created shape is unverified until bench, word is "shape" not "look"); 4 child cards P447-P450 open, 0/4 · E · gh issue view 597 · supports: P735's "holes, connectors, outline" is the content P446's model should hold
- PO-26 · P734 #1005 (breadboard with real holes; sources incl. DFRobot drawings/DXF, photo, vectorised, AI-generated and vectorised; waits on the other session's spark/breadboard split) · E · gh issue view 1005 · supports: P734 is the consumer of the records; blocked by that split

Where the cards disagree

- PO-27 · AI-made shapes: P446 says sources "never call an AI or a program" (a person, Claude or a tool writes a file spark reads as unverified); the PO's P734 words list "AI generated and vectorized" as a spark strategy. Who runs it is unsettled · E · #597 design block; #1005 "Sources the PO named" · supports: whether the P735 run may create a shape at all
- PO-28 · Fact scope: P206 wants the facts the chain decides on (no geometry); P446/P734 want geometry; AGENTS.md/W21 want only what a reader uses. `mounting_holes` has no reader (PO-5) · E · #170; #597; AGENTS.md · supports: order of fields: breadboard first or chain first
- PO-29 · Where the data lives: P446 plans a new `PartShape` model plus `part_shape.ShapeSource`; P734 says the record already holds `body_mm` and `pin_order` and shape/pictures are already strategies; P735 says "no record holds a picture, a schematic, holes". The three describe the same code differently. Did not read part_shape.py to settle it · E (cards) · #597, #1005, #1010 · supports: —: whether record fields or a separate shape file carries holes
- PO-30 · Method: P329 says "together through Chrome"; P209 wants a script/skill/agent; P735 says "one refactored research run". Chrome is not in the walks (they used WebFetch/curl) · E · #421, #178, #1010 vs walk diaries · supports: whether a Chrome step is needed (CDN pages, `javascript:;` buy link seen in sen0526)
- PO-31 · Board vs part: boards live in `boards/<id>.json` with `physical`, validated by boards.py, not parts.py; `parts.py --unverified/--sources` refuse a board. P735's "records" spans both; P446 is board-first (FireBeetle), P735 part-first · E · walk/dfr1117 Bugs 2, Gaps 1 · supports: two record kinds, two toolchains in one epic
- PO-32 · Scope trap: P735 gets 5 sub-issues but P340 stays under P329; P329 (parent #1010) then has a child (P340) that P735 does not own · E · #1010 comment; #421 "parent" field · supports: tidy board only

Riskiest assumptions

- PO-33 · Riskiest belief: DFRobot publishes enough per SKU (dimension drawing with hole/connector coordinates, or a CAD file) to build holes and connectors for most of the PCB-module subset without a human at the bench. Evidence against: 0 of 4 walks reached verified hole/pin positions; only 1 of 4 had a machine-readable footprint; 3 of 4 lack height/thickness · E walk Not found sections · H that the other ~50 behave the same. Opinion: PO assistant, proposed.
- PO-34 · Cheapest test for PO-33: one script, no AI, fetches the 80 or so wiki pages for the PCB-type drawer entries and counts which list a dimension file, a schematic, a STEP zip, a layout/CAD zip; then open 5 at random and read whether hole/connector coordinates are dimensioned. Pass line to be set by the decider before the run. Cost: an hour; reads only what a person could read. Alternative cheaper: ask the PO which 5-10 parts he will wire in the next 3 projects and size the first run to those (D needed).
- PO-35 · Second belief: that picture + holes in a record produce a drawing the PO values. P734 notes the PO "loves how it looks now, with the colored holes"; the Wokwi stand-in route stays even with full records · E #1005 PO words · cheapest test: draw one module (e.g. DFR0995 or SEN0526) from the walk's JSON by hand and show it to the PO.
- PO-36 · Third belief: a Claude run that writes 99 records is trustworthy. Evidence: four walks logged wrong or ambiguous reads (PO-7), DFRobot's own texts conflict (DFR0995 3.3 V vs 3.3-5 V; wiring BLK->D7 vs code D4), and the existing DFR0457 record had a wrong claim ("bottom holes assumed to mirror") plus a verified:true temperature range its own note calls implausible · E walk/dfr0457 "What the existing record had wrong"; walk/dfr0995 Gaps · cheapest test: the same agent redoes one shelf record that already exists; diff by a person.

Pre-mortem (Klein): six months on, it failed. Why (all H, from the evidence above)

- PO-37 · The run produced ~50 records with `verified:false` geometry scaled from images; nobody consumes them because the breadboard drawing (P734) was still blocked behind the spark/breadboard split; the PO still hand-wires.
- PO-38 · A new field (holes, connectors, image) was added per walk, each of the five cards extended it differently (PartShape vs record vs boards `physical`), and a later refactor (v0.13 "one core") moved them again.
- PO-39 · The batch stopped at the first part whose data DFRobot never published; the "full record" stayed an unreachable ideal and the epic never closed (PO-21).
- PO-40 · A vendor file or a derived SVG/footprint made from one got committed or shared (AGENTS.md rule; licence unknown PO-15), forcing a history purge in a public MIT repo.
- PO-41 · A wrong pin or hole position (read off an image) reached the bench or a PCB order through a record marked ok; no one re-read it (PO-7, PO-36). A batch makes that error appear 50 times.
- PO-42 · Cost and token use ran far above plan (PO-20); the PO paused the run after 15 parts and the store holds a mix of old and new record shapes.
- PO-43 · Stale: DFRobot changed a wiki or revised a board (DFR1117 has V1.0 and V1.1; the record said V1.0 only, and nothing says which revision the PO owns), and the records no longer match the PO's boards.
- PO-44 · The PO never played the result (feel slices wait for the PO per memory); the run finished unreviewed.

## 2. What you could not check, and why

- Whether DFRobot's licence permits copying, deriving a drawing from, or sharing its PDFs, STEP and KiCad files: no terms page found in one search; the forum post is a user's word.
- SnapEDA's actual licence text: only search summaries, not the licence file.
- Fritzing, EasyEDA/LCSC and tscircuit registry coverage of DFRobot modules: no search budget used (3 allowed, 2 made, neither on these).
- Wokwi's current state (read 2026-10-12 in #178; not re-read).
- The real count of PCB-type items among the 99, and how many wiki pages publish dimension, STEP or layout files: no scan made (read-only role, no web scraping).
- `part_shape.py`, `part_pictures`, the breadboard drawing code: not read, so PO-29 is a comparison of card texts only.
- The number of drawer rows with a linked record (19) came from a grep of the printed table.
- The walk JSON records themselves were not opened; findings come from the diaries.
- The brief/jobs/risks files in the discovery folder are unfilled templates; nothing there to check.
- The in-flight memory claim (PO-18) was not confirmed against GitHub.

## 3. Questions for the decider

- Which of the 99 count as in scope (PCB modules and boards only, or cables, motors, panels too)? · decides: the size of the run and the denominator of "done".
- Which 5-10 parts will the PO wire in his next projects? · decides: whether the first run is the whole drawer or a short list.
- Is "full" a record with every field filled, or with every field either sourced, marked unverified, or marked "not published"? · decides: the done-line and whether PO-21 gaps end the epic.
- May a spark run create a shape when DFRobot gives none (scaled from a drawing, vectorised, AI-made), and if so unverified until the bench? · decides: PO-27 conflict between P446 and P734.
- Where does a finished record live: the PO's shelf, the project, the plugin library? · decides: PO-9 divergence and whether records are ever shared.
- Does P735 take over AliExpress (P329) and Chrome, or are they out? · decides: the scope split with P329/P340.
- Do board records (boards/) and part records share one run? · decides: one toolchain or two.
- Is a licence check on DFRobot's downloads needed before any derived drawing is kept? · decides: whether derived artefacts stay in the person's store only.
- Does the PO accept the breadboard drawing code (P734) as a prerequisite or parallel, given it waits on the other session? · decides: ordering of P734 vs the record run.
- Which hardware revision does the PO own for boards with several (DFR1117 V1.0/V1.1)? · decides: whether the run needs photos of the back of the board.

## 4. Searches

- `DFRobot wiki downloads license terms of use CAD STEP schematic reuse` · decision served: may spark keep and derive from DFRobot's downloads (licence) · used: yes (PO-10 context, PO-15); found no official terms.
- `SnapEDA license terms of use downloaded footprint models redistribute` · decision served: whether an aggregator is a usable source under spark's public-MIT, no-vendor-file rule · used: yes (PO-14).
