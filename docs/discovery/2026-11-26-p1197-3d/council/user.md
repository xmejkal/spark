# P1197 council: the user's journey

The lens: the maker (the PO, n = 1), the hobbyist H with no Fusion and no KiCad, and Claude as the second user. Read on
2026-11-26 between 15:20 and 15:40 CET, on branch p1197-3d. I read the repository and the store (`~/.local/share/spark`).
I also read the PO's walk diaries (`~/Development/spark-walks`) and his earlier bin project (`~/Development/smartbin-local`).
Last, I read the PrusaSlicer settings and the Fusion folders on this Mac. I changed nothing. Tags: E is a pointer to what I read, H is a
belief with its source, and D is a decision with who and when. A dash (—) marks an unknown.

## Findings

### What the maker did before spark had a 3D step

- US-1 · The PO already had a 3D board, real module bodies and an offline browser viewer in his bin project, before
  spark. The project has `board.glb` (1.7 MB, 2026-10-01) and `board-viewer.html` (4.3 MB). The viewer embeds the GLB
  and inlines the three.js that tscircuit installs, so it "opens from a download folder with no network". The project
  also has `tools/check-module-clearance.py`, which reads the bodies back from the GLB and reports overlaps and
  overhangs. Bodies came from `cadModel`: a hand-built FireBeetle 2 S3 body, a STEP URL for the L9110S, and jscad boxes
  and cylinders · E · `~/Development/smartbin-local/tools/build-viewer.py:1-17`, `board.tsx:60-135`,
  `tools/check-module-clearance.py:1-40`, `git log` there ("Real module bodies, and only for what is really on the
  board", 2026-09-23. "B4: the viewer is made by make, from the exports", 2026-10-01) · supports only: J1 and J2 have
  a working precedent in his own history. The jobs file's "Today they…" (J1 "nothing", J2 "pads and a box") leaves it
  out. research.md marks the one-page viewer H (section 4) and lists "whether a viewer runs from one page with no
  network" as not checked (section 6). This project built one. I did not open it in a browser today.
- US-2 · A 3D picture that nobody regenerates goes stale and misleads. In the bin project the hand-made viewer "still
  showed the XIAO board of 2026-09-22, two boards ago", so it became a make target · E · `build-viewer.py:5-8` ·
  supports only: a viewer or a STEP that is not rebuilt with the board harms the maker. He then checks the fit against
  an old board.
- US-3 · In the same project a module's 3D body was lower than its own stated height. The DFR0954 amplifier is a
  jscad cuboid 3.2 mm tall. The comment above it says "18 x 18 mm, 7.1 mm tall with the JST socket". A case sized
  from that model leaves 3.9 mm too little room above the socket · E · `~/Development/smartbin-local/board.tsx:98` and `:105` ·
  supports only: "a case that does not close because a height was guessed" happened once already, in a model, though
  not in a print. A height typed per board drifts from the height in the record.
- US-4 · The Fusion step is in the plans since September, and it never ran. The bin project's notes say "Export STEP
  for the Fusion 360 enclosure" (next step 3). They also say the KiCad leg with "STEP for Fusion, DXF outlines" is
  "still the plan rather than the practice". The same goal comes back four times: #163 (2026-10-11), #313 (2026-10-16),
  P269's D9 (2026-10-16) and #1745 (2026-11-26) · E · `~/Development/smartbin-local/docs/archive/PCB_PIPELINE.md:64-80`,
  `docs/archive/FORMATS.md:141-170`, the issues · supports only: J3 is stuck at "never tried" after about two months.
  The cheapest unknown (does the STEP open in his Fusion, with names?) is a run of minutes that nobody made. The
  old notes also make two claims. Meshes "come in as decoration you cannot model against". A DXF outline "is usually
  all an enclosure needs". That is H, a past Claude session's view with no run behind it.
- US-5 · One known way he gets a case: he bought one. His drawer holds two DFRobot FIT0725 boxes, "Plastic Project Box
  Enclosure for FireBeetle - 3.15 x 1.61 x 0.79 inch" (about 80 x 41 x 20 mm) · E · `~/.local/share/spark/drawer/dfrobot-fit0725.json`,
  `drawer-import/dfrobot-orders.json` items[64] (read from his DFRobot order history on 2026-10-04, with no dates
  kept) · supports only: a bought box is one of his options today. A "does my board fit the box I own" check is a job
  the jobs file does not list. Whether he used the box is an account question.

### What the maker can supply, and what not

- US-6 · Before a physical step he asks for exact numbers himself. On the e-paper walk he asked: "what about the
  dimensions and precise holes locations, and also the bottom , cause there's also the side connector, do you have all
  the details in the record?" The answer was no · E · `~/Development/spark-walks/p934-epaper/diary.md:283-297`
  (2026-11-20 14:07) · supports only: the maker values exact facts over a picture. A case from guessed numbers fails his
  own test.
- US-7 · On the spot he supplies photos, not measurements. "The PO has no ruler at hand and expects the datasheet to
  give the size" (2026-11-19 23:41). The outline then came from a photo scaled by the header pitch: "about 85 x 44 mm,
  error about 5% (4 mm long, 2 mm short)", with holes "about 2 to 2.5 mm across" · E · `p934-epaper/diary.md:76-90`,
  `~/.local/share/spark/shelf/epaper-2in9-bwr-mh-et-live.json` `body_mm` · supports only: a photo outline at ±4 mm
  cannot carry a case, whose fit needs well under 1 mm. "Make the shape from pictures" (J1) is good for the look and
  not for the fit.
- US-8 · He also supplies looks at his own board, one look per question. These include the FireBeetle S3's row side ("the PO's look
  at his own FireBeetle 2 ESP32-S3 on 2026-11-20") and the XIAO's buttons from his photo · E ·
  `boards/firebeetle2-esp32s3.json` `physical.header.row_side`, `boards/xiao-esp32-c6.json` `physical.buttons` ·
  supports only: a yes/no or "which side" question about the board in his hand works. An orientation or opening-side
  question fits that habit.
- US-9 · A calliper measurement happened once and was not dated. The L9110S outline says "measured with calipers on
  the module in hand". P735's user lens left "whether he owns calipers" as an open PO answer on 2026-11-10 · E ·
  `parts/l9110s-module.json` `body_mm.source`, `docs/discovery/2026-11-10-p735-dfrobot-records/council/user.md:59` · H
  (that he owns callipers, from "the module in hand") · supports only: the brief's outcome ("callipers on the printed
  case against the board") rests on a tool and a habit that nobody checked.
- US-10 · The store's dimension drawings give outlines, not heights. I looked at `DFR1025_Dim_02.jpg` and
  `DFR0831_Dim_02.jpg`. Each is a top-view photo between two rulers, with no side view. The DFR0831's 5.5 mm height
  came from the wiki's table ("43.5x20.3x5.5mm"), not from the drawing. His XIAO photo of 2026-10-14 is top-down with
  no ruler · E · `~/.local/share/spark/sources/<sha>/DFR1025_Dim_02.jpg` and `DFR0831_Dim_02.jpg` (viewed),
  `shelf/dfr0831-buck-5v.json` `facts.thickness_mm`, `boards/photos/xiao-esp32-c6-front-2026-10-14.jpg` (viewed) ·
  supports only: pre-analysis section 1's "20 of these are dimension drawings" counts sources for x and y, not z. The
  height is the fact that photos and most drawings do not give.
- US-11 · His printer and habit: PrusaSlicer 2.9.0 with the preset "Original Prusa i3 MK3S & MK3S+", "Prusament PETG"
  and "0.20mm QUALITY @MK3". The settings file changed on 2026-11-21. The last output went to a removable volume named
  after the MK3S. All five recent projects are downloaded 3MF models of toys · E ·
  `~/Library/Application Support/PrusaSlicer/PrusaSlicer.ini` (`[presets]`, `[recent_projects]`,
  `last_output_path_removable`) · supports only: he prints, on an MK3S, from downloaded 3MF files. The recent list
  holds no case of his own design. J5's "print it on my own printer" has evidence as a habit. Fit tolerances for PETG
  on an MK3S are his printer's facts, not spark's.
- US-12 · Fusion 360 is on this Mac since at least 2021 (the `CAM360` folder is dated 2021-11-22). Its support
  folder last changed on 2026-10-07 to 10-09, with add-in lists dated 2026-09-20 and 2026-10-07 for build 2705.1.15.
  Autodesk's built-in MCP server appeared around April 2026 · E for the dates
  (`ls -la ~/Library/Application Support/Autodesk/`) · H for the MCP date (search 1, blog metadata and a third-party
  post) · — whether he modelled anything: an update writes these files with no use · supports only: his installed
  Fusion is likely new enough for the built-in MCP server. Whether Fusion is his working CAD tool, or a wish, is an
  account question. His words "Make it all parametric in fusion 360" (#163, 2026-10-11) state the wish, not a past use.

### What Claude needs as data, and how it reads what exists

- US-13 · For a case with no guessed number, Claude needs these facts per part. Each one has a pointer to show where it
  stands today:
  1. the board's outline, thickness and holes. These are present for the FireBeetles. They are missing elsewhere or in
     other shapes (US-15).
  2. each body's height above the board. Present as a field for 3 records, and as prose in several more (US-15).
  3. how each module sits on the board: soldered, in female headers, or on a ribbon. This sets its height. No record
     or requirement holds it. The bin's clearance check says a plug-in module is "a 29 x 23 mm circuit board standing
     12 mm tall" (`check-module-clearance.py:5-8`).
  4. each opening's place, side and size: USB, a jack, a button cap, a display window, a sensor's line of sight. One
     board holds the in-plane half (US-16). One jack holds an axis height (`catalog/pj-002a-dc-jack.json`
     `facts.barrel_axis_height_mm` 6.5, unverified).
  5. the person's intent per part: which part must show through the lid, sit behind a grille, or stay off the board.
     The bin project put the rangefinder and the speaker on ribbons because one "has to look out through the lid" and
     the other "sits behind a grille" (`smartbin-local/board.tsx:41-44`, `:85-89`). No record holds this.
  6. which variant the person owns, where the variant changes the height. The tactile button record says "Height is
     4.3, 5, 8 or 12 mm depending on variant and is the only thing to check against an enclosure". The drawer row is
     "6×6 tactile buttons (a bag)" with no variant (`parts/tactile-button.json` `body_mm.note`,
     `drawer/6-6-tactile-buttons-a-bag.json`).
  · E for each pointer · H that this list is complete (my reading of the bin project and the enclosure README) ·
  supports only: J7's "outline, holes, each body's size and height, each opening" misses items 3, 5 and 6.
- US-14 · tscircuit's installed case does not stop a tall part. Its `topHeadroom` default is 6 mm, "clearance above
  the PCB, not above the tallest arbitrary component". "Parts without apertures do not report an envelope to this
  solver", and "full component-body clearance" is "future work". Each opening must be authored per part (`width`,
  `height`, `margin`, a direction) · E ·
  `~/.local/share/spark/toolchain/node_modules/@tscircuit/create-fdm-enclosure/README.md` ("Enclosure sizing and
  defaults", "Aperture dimensions") · supports only: with today's records, a part taller than 6 mm meets the lid with
  no warning. Examples: the DFR0205 at 20 mm (verified), the 5 mm LED at 8.6 mm, the 8 or 12 mm button variants, the
  DFR0954 at 7.1 mm, and any module in female headers. ★C5 gives a box, not a fit. The headroom and the openings are
  facts that Claude or spark must hand to it.
- US-15 · The physical facts that Claude reads exist in more records than pre-analysis section 1 counts. They come in
  at least five shapes, and two words mean two things each:
  - The survey left out the store's `shelf/` folder: 11 records and 2 boards.
  - `thickness_mm` means the bare board in the boards and in `data/fact-needs.json` ("How thick is the module's board,
    without its parts?"). It means the overall height in `catalog/dfr0205-buck-adjustable.json` (20.0, "the tallest
    of the candidates") and in `shelf/dfr0831-buck-5v.json` (5.5, "the height over the inductor, which is what the
    enclosure lid clears").
  - `body_mm.height` is the second dimension in the board plane (pre-analysis section 1).
  - Mounting holes come as a list of `{x_mm, y_mm, drill_mm}` (the contract, `scripts/spark/sourcing/part_records.py:265-268`),
    as `{count, diameter_mm, inset_mm, spacing_x_mm, spacing_y_mm}` (`boards/firebeetle2-esp32s3.json`), as features
    of kind `hole` (`shelf/boards/firebeetle2-esp32c6.json`), as a text string (`parts/dfr0534-module.json`,
    `catalog/dfr0469-…`, `catalog/dfr0821-…`) and as a bare count (`shelf/ds3231-…`, `shelf/dfr0831-…`).
  - Heights also live in prose notes: DFR0954 "7.1 mm total height", VL6180X "1.02 mm thick with 1.2 mm of parts above
    it", the LED "8.6 … mm above the lead exit", PJ-002A "14.4 x 9 x 11".
  · E · the files named, and a survey script run on 2026-11-26 over `parts/`, `boards/` and the store's `catalog/`,
  `boards/`, `known-boards/` and `shelf/` · supports only: ★C1 ("1 of 30 records holds a height") undercounts what a
  reader finds. It also overcounts what a generator can use. A Claude that takes `thickness_mm` 20 as a board's
  thickness, or 1.6 as a module's height, draws a wrong case and believes it.
- US-16 · One board already holds the in-plane half of its openings. The FireBeetle 2 C6 shelf record has
  `physical.features` with 45 items in mm. They include the USB-C (9.0 x 7.37 mm at y 53.91, so 1.28 mm past the 60 mm
  edge), the RST and BOOT buttons, the BAT JST socket, the GDI connector and four holes. Claude measured them from
  DFRobot's top view on 2026-11-20, all `verified: false`, and none has a height. The same record says of the height:
  "Not stated by DFRobot. The STEP zip on the wiki could give it; not opened" · E ·
  `~/.local/share/spark/shelf/boards/firebeetle2-esp32c6.json` `physical.features`, `physical.//max_component_height_mm` ·
  supports only: a shape from "the record's numbers" can place openings for this board today. Only the z of each
  feature is missing.
- US-17 · Vendor models exist for his FireBeetles but cannot be used as they are. DFRobot's S3 model "is 25 MB, it is
  served inside a RAR inside a ZIP rather than at a URL tscircuit could fetch, and its bounding box is 28.7 x 68.2 mm
  against the board's 25.4 x 60 because it includes an OV2640 camera and its flex cable". The S3 board record gives no
  height for the same reason · E · `~/Development/smartbin-local/FireBeetle2Esp32S3Body.tsx:1-15`,
  `boards/firebeetle2-esp32s3.json` `physical.//max_component_height` · supports only: this refines ★C8. A vendor file
  can show a part he does not have (the camera) and break a fit check. The "similar enough general shape" that he
  accepts (#1745) can be safer than the vendor's exact file.
- US-18 · The bin project fetched bodies by URL at build time, with the licence only in a comment. One was an L9110
  STEP from an unrelated GitHub repository ("a real model of this module (CC0)"). Others were OBJ files from
  `modelcdn.tscircuit.com` by LCSC number · E · `~/Development/smartbin-local/board.tsx:73-79`, `:129-134` · supports
  only: his past practice is "fetch at use", as ★C7 proposes, but with no record, no sha256 and no kept source.
- US-19 · Claude already has a way to say what is missing. An Operation puts each question in `data.open`,
  with `asked_of` (`person`, `agent` or `either`), `answer_form`, `example` and `cites`. The run exits 2 with
  `needs_reply`, and a replies file holds the answers. A fact the vendor did not publish goes into `physical_proof.not_published`. The question
  list in `data/fact-needs.json` covers `body_mm`, `physical.thickness_mm`, `physical.mounting_holes`,
  `physical.header` and `physical.features`. It has no question for a height above the board, a mounting style, an
  opening, a plug or a variant · E · `docs/guide/agents/replies.md:1-40`, `:172-186`, `data/fact-needs.json` ·
  supports only: J7's "say what is missing" can reuse a shape that the person already answers in a terminal. The case
  facts of US-13 have no question yet.
- US-20 · spark's own rule for a shape from a picture already exists. Sources "never call an AI or a program. A person,
  Claude or a tool writes a file, and spark reads it as unverified until the person says yes" (the P446 design,
  2026-10-29) · E · #597 body · D · the PO, 2026-10-29 (approved the design) · supports only: a 3D shape that Claude
  makes from photos fits this rule as an unverified file. That covers J1's "from the pictures" without an AI model
  service.

### Friction moments on the journeys today

- US-21 · The USB opening depends on the person's cable, not only on the board. His XIAO photo shows his own cable
  plugged in, and its overmold is visibly wider than the receptacle. I estimate about 12 mm against about 9 mm, scaled
  by the board's 17.8 mm width. USB-C fixes no overmold size except for right-angle plugs (12.8 x 7 mm at most). One
  open project sets a 13 x 8 mm relief · E (the photo, viewed) · H (my pixel estimate) · E (search 2: an OpenFlexure
  commit comment and a PINE64 thread, read as search summaries) · supports only: an opening sized from the receptacle
  in a record can be too small for his cable. The plug is a person fact (a photo beside the board, or callipers) or a margin
  that the person accepts.
- US-22 · The e-paper gadget, his most recent walk, shows only an 8-pin header in 3D and no panel. Its record holds no
  place for the screen's window, which is the case's most visible opening · E ·
  `docs/discovery/2026-11-26-p1089-kicad-and-tscircuit/notes.md:31`, the e-paper record (no window or active-area
  fact) · supports only: for the board that he most likely puts in a case next, the decisive opening is unrecorded.
- US-23 · A command that the person types meets the friction of the bench notes of 2026-11-25. One long command was
  cut by his paste ("--files: expected one argument"). Other lines had absolute paths. Developer output stood in
  place of one plain next line · E · `~/.local/share/spark/bench-2026-11-25.md` notes 1, 6, 11 and 14 · supports only: J3 today is a typed
  `tsci export -f step` from `docs/guide/agents.md:170-176`. It will meet the same friction unless the export is one
  short command, a page button or Claude's job.
- US-24 · The journey already names the case step. `flow_codes.py:481` holds `("case", "Case", "At the printer: a case
  for the board.")`, and P1102's plan lists it as `unbuilt:case` · E · `scripts/spark/flow/flow_codes.py:481`,
  `~/.local/share/spark/plans/p1102-plan.md:140` · supports only: the person meets a named step with no Operation
  behind it. The words "At the printer" assume a printer at home. H possibly has none.
- US-25 · The hobbyist H has no Fusion, no KiCad and maybe no meter. No person outside the project installed
  spark. For H the free path to 3D is the page or a GLB. The free path to a case is a print file and someone's
  printer · H · `scrum/VISION.md:38` (the persona table), the jobs file's H journey · supports only: a case path that
  needs callipers, Fusion or the MCP server leaves H out. A viewer or a print file with stated defaults is H's path.
- US-26 · Claude's journey today breaks at three points (my walk of the jobs file's Claude table against what I read):
  1. Claude reads the records and meets two meanings of "thickness" and five shapes of holes (US-15).
  2. A hand edit of `board.tsx` for `<enclosure.fdm.box>` is lost at the next build (jobs file, Claude step 3).
  3. The enclosure takes 6 mm of headroom unless told otherwise (US-14).

  So Claude has two ways, and both are bad. It asks the person for every height, with no `fact-needs` row for any
  (US-19). Or it writes a case that looks right and possibly does not close · E for each step's pointer · H for the outcome (no case was made
  or printed) · supports only: J7 needs both a reader-safe shape for the facts and a rule for what Claude does with
  a null: refuse, or use a named default that the person accepts.

## What I could not check, and why

- Whether the bin's `board-viewer.html` still opens offline today, and whether the PO ever opened it. I did not run a
  browser. The Google Fonts link in its template needs the network for the fonts only, by my reading.
- Whether the PO used the FIT0725 boxes. The drawer says "bought", not "used".
- Whether he printed anything recently, or designed any print himself. The slicer's recent list shows only files that
  were opened, and I did not read his downloads or the SD card.
- Whether he models in Fusion. Folder dates show an update or a start, not use. I did not open Fusion, and did not
  read his cloud projects.
- Which Fusion release added the built-in MCP server. Search 1 gave blog dates, not a release note, and I did not
  check that build 2705.1.15 has the setting.
- Whether his USB cable's overmold is really about 12 mm. This is my estimate from a photo with no ruler.
- Whether he owns callipers. No log says so (US-9).
- The bin's cavity fit ("The outline still has to be checked against the bin's own cavity", `board.tsx:47`): I found
  no note that it was checked.
- tscircuit's enclosure branch state. The README says the full feature "spans unreleased branches". I did not test
  which parts of it work in the installed 0.0.2600 beyond the probe in pre-analysis section 4.
- I read no other project in `~/Development` beyond the bin project, the walks and the file list of `rc-car` (which
  holds `car.tsx` and no 3D file).

## Questions for the decider

- How did you get a case or a holder for the last board you used outside the breadboard: the FIT0725 box, a print, or
  none? (account) · decides: whether the first slice is a printed case, a fit check against a box you own, or an
  export for Fusion.
- When did you last open Fusion 360, and what did you make in it? (account) · decides: whether Fusion is the first
  target of J3 and J4, or a CLI case and a print file come first.
- What did you last print on the MK3S, and did you draw any part of it yourself? (account) · decides: whether spark
  must make the case (J4), or only hand over a body that you or Claude design around (J3).
- When you had the bin's `board.glb` and `board-viewer.html` in October, did you open them, and what did you look for?
  (account) · decides: the value of a browser viewer (J2) against a STEP for Fusion.
- When did you last measure a part with callipers, and which part was it? (account) · decides: whether heights that a
  person measures are a real source, or Claude must use stated defaults that the person accepts.
- On the e-paper walk you asked whether the record held the exact holes and the side connector. What did you want to
  do with those numbers? (account) · decides: whether the first real board for a case is the e-paper gadget, and
  whether a display window is a first-slice fact.
- Have you had a board in a box where a cable, a button or the lid did not fit? What happened, and what did you do?
  (account) · decides: which fit failure the first slice must catch (a height, a plug or a hole).
- Which gadget did you last want a case for, and what stopped you? (account) · decides: the board for the walking
  skeleton and its proof.
- When a height is unknown, does Claude refuse to write the case and ask, or write it with a named default (for
  example 6 mm of headroom) that you accept out loud? · decides: the rule for a null in J7, under "a null is not a
  value to fill in".
- Is a generated box from the record's numbers enough as a part's 3D body, even where a vendor model exists but shows
  extra parts (the FireBeetle S3's camera)? · decides: the order of the model sources in J1.
- Does spark keep your own cable's plug size as a fact (one photo or one measurement), or use one margin for every
  USB opening? · decides: whether the person's cable is a record.
- Do the case facts (height above the board, how a module sits, each opening, the variant) become questions in the
  existing open-question and replies shape, answered at the bench? · decides: the interface of J7 for a person and for
  Claude.
- Do "thickness" and "height" get one meaning each in the records before any 3D work reads them? · decides: the
  record contract and the words table.
- Do you want Fusion's built-in MCP server turned on for a test, on this Mac? · decides: whether J4's Fusion path can
  be tried (it is your setting to turn on).

## Searches

- `Fusion "MCP server" built-in which Fusion release added it 2026` · served: whether J4's Fusion MCP path works on the
  PO's installed Fusion without an update · used (US-12, as H). Results:
  [Introducing the Fusion MCP](https://www.autodesk.com/products/fusion-360/blog/introducing-the-fusion-mcp/),
  [Bringing Fusion to Claude, APS blog, 28 Apr 2026](https://aps.autodesk.com/blog/bringing-fusion-claude-creative-work),
  [Autodesk Fusion connector](https://claude.com/connectors/autodesk-fusion),
  [Fusion Data MCP Server](https://www.autodesk.com/products/fusion-360/blog/introducing-the-autodesk-fusion-data-mcp-server/).
- `USB-C plug overmold size enclosure cutout clearance 3D printed case dev board` · served: whether a USB opening can
  be sized from the board's record alone, or needs the person's cable · used (US-21). Results:
  [OpenFlexure commit](https://gitlab.com/openflexure/openflexure-microscope/commit/5c8f7b5aeaca5e8b463594f6e7ca36cdf888ad12),
  [PINE64 forum thread](https://forum.pine64.org/printthread.php?tid=9817),
  [Flashforge on cut-outs](https://www.flashforge.com/blogs/news/how-to-make-custom-cut-outs). Read as search
  summaries, not opened.
