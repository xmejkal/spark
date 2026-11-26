# P1197 council: the PO assistant (Existing first, Risks and assumptions)

Read on 2026-11-26 between about 15:30 and 16:30 CET, on branch p1197-3d at commit ce82c02f. I changed nothing. The
one file I wrote is this report. The discovery lead's files are claims to check. Where a finding checks one of them,
it says so.

## Findings

### What already exists

- PA-1 · The PO's own bin project already holds most of this epic's early pieces. The discovery's files do not name
  them. First, a hand-built 3D body of the FireBeetle 2 ESP32-S3 in tscircuit, with WROOM 3.1 mm and USB-C 3.26 mm
  tall. Second, a `board.glb` that its Makefile makes with `tsci export -f glb`. Third, an offline one-page 3D viewer:
  it inlines three.js and the GLB as base64 "so the page needs no network". Fourth, a check that reads each body from
  the GLB and reports overlaps and overhangs against the board outline. The repository is MIT. The files date from
  2026-09-24 to 2026-10-01. · E. Pointers in ~/Development/smartbin-local: `FireBeetle2Esp32S3Body.tsx:1-40`,
  `tools/viewer-3d.js:1-3` (66 lines), `tools/check-module-clearance.py:1-16` (147 lines), `Makefile:72-73`,
  `Makefile:131-136`, `Makefile:198`, `LICENSE`, git log `ee2c638`. · Supports: reuse first for the viewer (J2) and
  for a fit check. It turns research.md section 6's open item "whether a viewer runs from one page with no network"
  into a built example. Whether it still renders today was not run.
- PA-2 · The bin's body file says why it is hand-built and not DFRobot's STEP. The vendor model is 25 MB. It comes
  "inside a RAR inside a ZIP". Its box is 28.7 x 68.2 mm against the board's 25.4 x 60 mm, because it includes a
  camera and its flex cable. The PO also fetched a DFRobot STEP of the DFR0654 by hand, on 2024-01-09. It sits in
  ~/Downloads: 26.6 MB, 889 solids, and every product is named "Document". · E. Pointers: the bin's
  `FireBeetle2Esp32S3Body.tsx:4-9`. For the file in Downloads, `grep -c MANIFOLD_SOLID_BREP` gave 889 and
  `grep PRODUCT(` gave only 'Document'. · Supports: a vendor STEP is heavy, carries extras and no useful names. It
  qualifies brief ★C8 ("no library holds a model of the dev boards spark uses"). A DFRobot model exists for the
  FireBeetle 2 ESP32-E.
- PA-3 · Brief ★C1 and pre-analysis section 1 undercount the height facts. "1 of 30" is wrong. Six records already
  hold a fact above the board plane, under five different keys. They are `physical.thickness_mm` 1.6 (FireBeetle),
  `facts.thickness_mm` 20.0 (DFR0205, verified) and `facts.height_mm` 17.3 (MKDS screw terminal). The others are
  `facts.pcb_thickness_mm` 1.0 (DFR0821), `facts.barrel_axis_height_mm` 6.5 (PJ-002A and DC-005), and
  `facts.cap_height_mm` null (tactile button). Two of them name the case in `why_it_matters`. One says "the
  enclosure hole is centred this far above the board". The other says "the only dimension that decides whether the
  enclosure closes". · E. Pointers: a scan by key name of 35 record files in `parts/`, `boards/`, `chips/` and the
  store's `catalog/`, `boards/`, `known-boards/`. Also `parts/tactile-button.json:64-69`, store
  `catalog/pj-002a-dc-jack.json:150-155`, store `catalog/dfr0205-buck-adjustable.json:105-110`. · Supports: records
  already grow case facts by need, as AGENTS.md asks. A common key is missing, not the habit.
- PA-4 · The word "height" means two things in the records today. In `body_mm.height` and `physical.height_mm` it is
  the second dimension in the board plane. For the FireBeetle that is 60.0, its length. In the MKDS record's
  `facts.height_mm` it is the height above the board, 17.3. · E. Pointers: the scan of PA-3,
  `boards/firebeetle2-esp32s3.json`, store `catalog/mkds-1-5-2-5-08-screw-terminal.json:149-153`. · Supports: a
  naming risk for the new z fact. A reader that takes `height_mm` as z gets 60 mm for the FireBeetle.
- PA-5 · The PO prints. PrusaSlicer 2.6.1 is installed, and its settings file was last saved on 2026-11-21. Its chosen
  presets are "Original Prusa i3 MK3S & MK3S+", "0.20mm QUALITY @MK3" and "Prusament PETG". ~/Downloads holds 26
  print files (STL, 3MF, gcode). Gcode names carry "MK3S" and an MMU. A Fusion add-in folder "3D Print Plus" exists.
  · E. Pointers: `defaults read` of the app's Info.plist, `PrusaSlicer.ini:164-167` and its mtime, `find ~/Downloads
  -maxdepth 4`, ~/Library/Application Support/3DPrintPlusForFusion360/readme.txt. · Supports: the printer row of
  the jobs file's journey step 7, which it marks H. The newest gcode in Downloads is from 2023-11. So how often he
  prints now is still an account question.
- PA-6 · PrusaSlicer takes STEP since version 2.5.0 (2022). It meshes the STEP on import. So a STEP case can go to his
  slicer with no STL or 3MF step. · E. Pointers:
  https://blog.prusa3d.com/prusaslicer-2-5-is-here-new-perimeter-generator-step-file-support-lightning-infill-and-more_70562/
  and https://www.help.prusa3d.com/article/supported-file-formats_1772 (search results, read 2026-11-26). ·
  Supports: brief ★C6 (the 3MF export fails) does not block a first print. One STEP file that holds the board, the
  parts and the case puts all of them on the print plate. So the case parts need their own file, or the PO deletes
  bodies in the slicer. That last point is H, from how a slicer treats a multi-body import.
- PA-7 · The Fusion on the PO's Mac is version 2705.1.15, installed 2026-09-08. It carries the strings "Fusion MCP
  Server (runs locally on this device)" and "Enables external AI tools to access your Fusion session via MCP". · E.
  Pointers: `defaults read` of the newest webdeploy app's Info.plist. `grep -i mcp` in its
  `Libraries/Neutron/StringTable/en-US/` files `NaFusion10.xml`, `NsBaseCore10.xml` and `NuBase10.xml`. · Supports:
  brief ★C11's caveat in part. The installed version has the setting. Whether it runs on his licence, and whether it
  is on, are not checked.
- PA-8 · tscircuit's enclosure is young, and its work paused. `@tscircuit/create-fdm-enclosure` had 6 releases from
  2026-07-21 to 2026-08-19, and none since. The newest, 0.0.7, still lists "Mounting bosses, inserts, fasteners,
  assembly DRC, full component-body clearance" as future work. Its README says the full feature "spans unreleased
  branches". These branches are on a personal fork (addibble) of five tscircuit repositories. · E. Pointers: `npm
  view @tscircuit/create-fdm-enclosure time --json`, its 0.0.7 readme at line 17, the installed README's section
  "Current coordinated branches". · Supports: brief ★C5, with a maturity caveat. A first slice on it is a bet on a
  package that can stall.
- PA-9 · The enclosure's sizing ignores tall parts unless they own an aperture. `topHeadroom` defaults to 6 mm. The
  README says that this headroom "is clearance above the PCB". It is "not above the tallest arbitrary component". It
  also says "parts
  without apertures do not report an envelope to this solver." `standoffHeight` is 4 mm and the walls are 2 mm. · E.
  Pointer: the installed README, section "Enclosure sizing and defaults". · Supports: a risk. The bin's audio module
  stands 12 mm tall (PA-1's clearance docstring), and the DFR0205 is 20 mm. Under 6 mm of headroom the lid does not
  close, unless spark states the headroom from the tallest height fact.
- PA-10 · spark's pinned tscircuit lags far behind. The toolchain pins `@tscircuit/cli` 0.1.2113 (released
  2026-09-21) and `tscircuit` 0.0.2600. The newest are 0.1.2490 and 0.0.3300, both released today. · E. Pointers:
  `npm view @tscircuit/cli time --json`, `npm view tscircuit version`, pre-analysis section 3. · Supports: research.md
  section 6 asks whether newer tsci fixes the STL GLB fault (cli #5654). That test needs a version bump. A bump is its
  own risk to every reader of `circuit.json`.
- PA-11 · Each outside tool does one piece. These are the ones research.md read, with their licences, checked where
  marked. tscircuit (MIT) gives the engine, the 3D tab, GLB, STEP with solids named by reference, and the FDM case.
  kicad-cli 10.0.6 gives an assembly STEP named by reference, GLB and a render, and it is optional for a person.
  Fusion 360 has a KiCad v7+ importer for its electronics workspace and a local MCP server. Its personal use is
  non-commercial. PrusaSlicer 2.6.1 (AGPL, run by the person only) imports STEP and STL. TurboCase (MIT) makes a case
  from a `.kicad_pcb`, not run. build123d (Apache-2.0) writes named STEP from numbers, not installed. None of them
  keeps a model per record with its origin. · E. Pointers: the probe in pre-analysis section 4, P1089 finding section
  2.1, research.md sections 2 to 4, PA-6, PA-7. · Supports: the gap is spark's records and the hand-over, not a
  missing tool.
- PA-12 · The Fusion electronics path is a second, untested route to a 3D PCB. The PO asked on 2026-10-11 for the
  design to open in Fusion "along with all the functionality and the parts and values". A comment on #163 found that
  tsci's `kicad_zip` gives Fusion's KiCad importer its input. No one uploaded it. · E. Pointer: #163, comments of
  2026-10-11 20:52Z and 21:08Z. · Supports: the brief's frame names only the STEP route for Fusion. The PO's older
  words name the electronics route too.

### Who is blocked, and what overlaps

- PA-13 · No one is blocked today. The MVP walk P100 #6 is parked since 2026-11-05, until "he has bench time". No
  perfboard code exists. The backlog review of 2026-11-24 proposed to close P275 #311 "as not now". I found no record
  of a fab order for a board that spark generated. The RC car project is the PO's north star for 3D (#163). It was
  last changed on 2026-09-30, and nothing of it is built. · E. Pointers: `gh issue view 6` (comment of 2026-11-05),
  store `backlog-review-2026-11-24.md:143`, `gh issue view 311` (open), the mtimes of ~/Development/rc-car `PLAN.md`
  and `DIARY.md`. · H that no order exists, because absence in the store's notes is not proof. · Supports: the epic
  is a pull from the vision (scrum/VISION.md:16, :70), not from a stall. This matches the D that it comes after the
  MVP.
- PA-14 · A spark board is a carrier PCB with the dev board on it, not the dev board. The T-Display project's
  `board.tsx` is a 54.29 x 63.49 mm board. `TtgoTDisplay` is one part on it, with a button and an LED. Its header
  says "mounting holes ... Not decided here, and it must be". · E. Pointers: ~/Development/spark-walks/t-display
  `board.tsx:1-20` and `requirements.json`. · Supports: a case for "a real spark board" needs that carrier made
  first, by a fab order or a perfboard. Neither exists (PA-13).
- PA-15 · The FireBeetle 2 ESP32-S3 is the one record that holds what a case needs. It has an outline of 25.4 x 60 mm,
  a thickness of 1.6 mm and four mounting holes (2.0 mm, inset 1.7 mm). The PO owns one (DFR0975, in #6's body). The
  bin's hand body adds the WROOM and USB-C heights (PA-1). The XIAO C6 record says its thickness is "Not recorded
  rather than guessed". · E. Pointers: pre-analysis section 1 table, `boards/xiao-esp32-c6.json:34`, `gh issue view
  6`. · Supports: the cheapest real object to case is the FireBeetle alone, on facts spark already holds.
- PA-16 · The backlog holds overlapping cards that this epic must absorb or order. The card names P203 #163, P210
  #180, P277 #313, P371 #473, P446 #597, P449 #601, P1185 #1729 and P1183 #1727. Neither the card nor the brief names
  these: P735 #1010, P734 #1005, P1161 #1697, P1164 #1700, P1038 #1521, P310 #376, P275 #311 and P1199 #1747. P735
  asks for a full record of each DFRobot part, with "dimensions, holes, connectors". P734 asks for each module with
  its real holes and pins. P1161 is the catalogue editor, which P269 D9 puts before the Fusion export. P1164 reads the
  real circuit from a photo. P1038 is the page, the place for a 3D tab. P310 is the RC car's first slice. P275 and
  P1199 hold the perfboard. P915 #1295 is a "3D rendering engine" for the games box. It is a different thing with a
  near name. · E. Pointers: `gh issue list --label epic --state open --limit 60`, `gh issue view 1010`. · Supports:
  the facts a case needs (holes, openings, heights) are the facts P735 asks research to fill. Two epics then write
  them.
- PA-17 · The Operation the epic extends already has a card. P1183 #1727 is `export-board`, which writes a STEP
  through kicad-cli. P1185 #1729 is the module box from `body_mm` "with a height fact". The P1089 finding orders P1185
  before P1183. · E. Pointers: `gh issue view 1727`, `gh issue view 1729`, P1089 finding section 4, steps 2 and 4. ·
  Supports: the first brick of P1197 is already a card with a done line: a height per record and a body per module.
  A new slice that writes it again builds it twice.

### Claims in the discovery lead's files that I checked

- PA-18 · jobs-and-journeys.md J3 and journey step 3 point at docs/guide/agents.md:170-176 for a STEP recipe. Those
  lines export `kicad_pcb` and run a DRC. They name no STEP export. The STEP line is in
  `skills/spark-design/SKILL.md:129` and `skills/spark-design/references/pcb-layout.md:43`. · E. Pointer: the lines
  read. · Supports: a pointer fix in the jobs file only.
- PA-19 · Card #1745 says "`tsci export -f glb` did not run". The P1089 finding means it was not tried. Its line 431
  is under "Not checked". The bin ran it on 2026-10-01, and the probe ran it today (254 KB). · E. Pointers:
  finding.md:431, PA-1, pre-analysis section 4. · Supports: GLB is not an open risk on a board with no STL body.
- PA-20 · Journey "Claude", step 3, says that a hand edit of `<enclosure.fdm.box>` in `board.tsx` does not stay. The
  build writes the file again. · E. Pointer: `scripts/spark/build/build_service.py:284` writes `board.tsx` on each
  build. · Supports: the claim. Claude's hand-made case is lost at the next build. So the case must come from facts
  that spark emits, or live in its own file.
- PA-21 · The brief's "Already decided" cites P269 D9 for "the Fusion export comes after the catalogue editor". D8 and
  D9 read so. J8, "export for Fusion 360", is new and comes after step 7, the catalogue editor. · E. Pointer:
  docs/discovery/2026-10-16-p269-views-and-editors/brief.md:107-108. · Supports: the D. It also means the epic's
  Fusion slice waits on P1161 #1697, or on a new D from the PO.

### What must be true for the epic to pay off

- PA-22 · Seven conditions, each with its state today. · Supports: the value test below.
  1. A physical board exists that wants a case. Today none that spark made exists (PA-13, PA-14). E.
  2. The PO wants a printed case for it, not only a picture. His words ask for both (#1745). Whether he prints one in
     the next month is not known. —
  3. Each part in it has a height above the board and its openings, with an origin. Today 6 records of 35 hold a z
     fact, under 5 keys (PA-3). E.
  4. The case closes and holds the board. The enclosure has no bosses, and it ignores tall parts without an aperture
     (PA-8, PA-9). E for the gap. Whether it matters on a real board is —
  5. The case survives a rebuild, so it comes from facts that spark writes (PA-20). E.
  6. The print path needs no Fusion and no 3MF, because PrusaSlicer takes STEP (PA-6). E.
  7. The pinned tscircuit keeps working, or a bump is cheap (PA-10). —

### Riskiest belief, its cheapest test, and the pre-mortem

- PA-23 · The riskiest belief, in my opinion: "a case that spark generates from record facts fits a real board on the
  first print." That means the lid closes, the board sits still, and the USB opening lines up. It carries
  conditions 3, 4 and 5 at once. If it fails, every later slice rests on hand fixes: Fusion, the viewer and the
  sculpture. · H. Source: the PO assistant, from PA-3, PA-8, PA-9 and PA-20. · Supports: the riskiest row, pending
  Q1.
- PA-24 · The cheapest test has two steps. The first step costs nothing. Put `<enclosure.fdm.box>` on a board with
  only the FireBeetle, in a scratch folder, and export STEP. Then compare the case's inner height and openings with
  the record's facts and the bin's body heights (PA-1, PA-15). A proposed pass line: the inner height clears the
  tallest part by at least 1 mm. The USB-C opening's centre lies within 0.5 mm of the connector's centre. The second
  step is a print in PETG on the MK3S, base and lid. It takes about one to two hours (H, from a box of about 33 x 66
  x 15 mm). Measure with callipers and fit the real FireBeetle. A proposed pass line: the board drops in by hand. The
  lid closes. A USB-C cable plugs in with the case shut. · H. Source: proposed by the PO assistant, not dated by the
  decider. · Supports: Q1. Spark's rules ask for a pass line dated before any result, so the decider sets it.
- PA-25 · Pre-mortem: "six months after it shipped, it failed. Why?" Nine causes, the most likely first. Each is H,
  from the evidence named. · Supports: the risks table.
  1. Nothing to put in it. The PCB was never ordered, and the perfboard was never built. So the Operation made cases
     for boards that exist only as files (PA-13, PA-14).
  2. The lid did not close. Most records had no height, so the case used 6 mm of headroom over a 12 to 20 mm module
     (PA-3, PA-9).
  3. The board rattled. It sat on 4 mm standoffs with nothing to hold it. The enclosure has no bosses, and spark's
     boards state no mounting holes (PA-8, PA-14).
  4. tscircuit moved on. The enclosure lived on a fork and stalled. Or a bump to a newer tsci broke the build's
     readers (PA-8, PA-10).
  5. The PO and Claude went to Fusion for every case, so spark's case went unused. Fusion must be open for its MCP.
     Its licence and its handling of names were never run (PA-7, research.md section 3).
  6. Vendor models drowned it. Fetched STEP files of 25 MB with camera extras made the viewer slow and tripped the fit
     check, as the bin's file warns (PA-2).
  7. It was built twice. P735, P446, P1185 and P1197 each added size and hole facts in their own shape (PA-16, PA-17).
  8. The settings for five strategies came before one printed case. The five are the source, the engine, the CAD
     tool, the case maker and the viewer. This breaks "Anything designed on paper before a design needs it"
     (scrum/VISION.md:83). The 09-29 cut deleted 5,962 lines built that way.
  9. A reader took a z fact named `height` as the plane height, and a case came out 60 mm tall (PA-4).

### The fit to P1198, the circuit sculpture

- PA-26 · The frame fits P1198 at three seams and misses at one. It fits where the shape source is per record,
  because a sculpture uses the same part bodies. It fits where the export takes any set of solids. It fits where the
  print file is not tied to a case. It misses where every path runs through a board engine. tscircuit's STEP and its
  enclosure both need a `<board>`, and a sculpture has none. A sculpture also needs the point where each lead leaves
  a body in 3D. A box from `body_mm` and a height does not give it. · H. Source: the PO assistant, from PA-11 and the
  store's `preanalysis/2026-11-26-circuit-sculpture.md` ("a fourth surface ... It has no holes"). · Supports: one
  seam rule to keep now, at no build cost. A part's 3D body and its pin points belong to the record's shape source,
  not to the board engine.
- PA-27 · The jig's medium differs between sources. The pre-analysis says "Spark prints the jig 1:1 on paper". Card
  #1746's title says "a printed jig". research.md section 5 puts it next to pogo-pin fixtures, which are 3D printed.
  · E. Pointers: store `preanalysis/2026-11-26-circuit-sculpture.md` ("The smallest first try"), `gh issue view
  1746`, research.md:101-102. · Supports: a question. A paper jig needs only the 2D sheet path (P269). A printed jig
  needs a print path that takes any solid.

### The first slice that gives the PO a case soonest

- PA-28 · Three candidate targets, in order of the time to a case in his hand. · H. Source: the PO assistant, from
  PA-13 to PA-15. · Supports: Q2. I decide nothing.
  1. The FireBeetle 2 ESP32-S3 alone. He owns it, and it runs firmware. The record has its outline, thickness and
     holes. The path: the record's facts and a stated headroom, then tscircuit's enclosure, then STEP, then
     PrusaSlicer, then a print. It needs no fab order, no Fusion and no 3MF. It takes days, not weeks. It walks a real
     object end to end, as AGENTS.md asks. But it is a dev board's case, not a project's case.
  2. A spark carrier PCB, such as T-Display's. It needs a fab order first, which is paid and waits on his yes. Then
     the shipping. It takes weeks.
  3. A perfboard. No perfboard code exists (PA-13). It takes months.
- PA-29 · By the MVP bar, no slice of this epic moves a basic project closer to a breadboard with working firmware.
  One piece also serves the PCB stage: P1185 #1729, a body per module with a height. The P1089 finding counts the
  missing body as fault F4 of today's boards. · E. Pointers: AGENTS.md "Principles", P1089 finding sections 2.3 and
  5. · Supports: if the decider wants one brick before the MVP, P1185 is the candidate. The rest stays after the MVP,
  as decided.

## What I could not check, and why

- Whether Fusion keeps the solid names `U1` and `U2`, and which licence the PO's Fusion runs on. It needs Fusion open
  and his sign-in. I read files only.
- Whether the Fusion MCP server is on and runs on a personal licence. The strings exist (PA-7). The setting's value
  is in Fusion's own preferences, and I did not open the app.
- Whether a real case fits. Nothing was printed or measured. I ran no tsci export myself. The discovery lead's probe
  did.
- Whether the PO owns the MK3S or only has its preset. A preset is not proof of a printer.
- Whether the bin's viewer still renders with today's three.js. I did not open it in a browser.
- Whether a build of the FireBeetle alone gives a `<board>` with the dev board's own outline. The enclosure needs one
  as `boardRef`. I read only the name of `board_alone_input`, not its output.
- Whether DFRobot's STEP files carry a licence. The file in Downloads has no licence text in its header. I did not
  read the wiki's terms.
- Whether a fab order of a spark board happened outside the store's notes.
- Whether newer tsci (0.1.2490) fixes the STL body and the 3MF export. It needs an install, which changes the store.

## Questions for the decider

- Which physical object gets the first case: the FireBeetle alone, a spark carrier PCB that needs a fab order, or a
  perfboard? · Decides: the first slice's target, and whether a paid order sits on its path (PA-28).
- Does a case for a dev board alone count as walking a real project end to end? Or must the first case hold a board
  that spark generated? · Decides: whether slice 1 can start before any PCB or perfboard exists (PA-14, PA-29).
- Is the print path STEP straight into PrusaSlicer, with no STL or 3MF export in the first slice? · Decides: the
  print-file scope (PA-6).
- Which Fusion licence do you use? Do you want its MCP server on for this work? · Decides: whether Fusion is in slice
  1 or later, and whether Claude can drive it (PA-7, PA-21).
- Does P269's D9 still hold, that the Fusion export waits on the catalogue editor? · Decides: the order of the Fusion
  slice against P1161 #1697 (PA-21).
- Does spark take in the bin's viewer and its clearance check, which your own sessions wrote under MIT? · Decides:
  whether the viewer and the fit check are a port or new work (PA-1).
- Who writes the size, hole and opening facts: P735's research run, P446's shapes, P1185, or this epic? · Decides:
  one owner for the facts, so nothing is built twice (PA-16, PA-17).
- Is the sculpture jig of P1198 on paper or 3D printed? · Decides: whether the print path must take any solid, not
  only a case (PA-27).
- Does P1185 #1729, a body per module with a height, go before the MVP, as the one piece that also serves the PCB
  stage? · Decides: whether any of this epic moves before the MVP (PA-29).

## Searches

- "PrusaSlicer STEP file import supported version" · The decision it served: whether the first slice needs an STL or
  3MF export, given that tscircuit's 3MF fails. · Used: PA-6.
- No second web search. The `npm view` calls to the npm registry (PA-8, PA-10) are registry reads, not web searches.
