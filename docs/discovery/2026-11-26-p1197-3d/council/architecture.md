# P1197 3D: the architecture lens

The architecture lens of the P1197 #1745 council, on Opus, 2026-11-26. It read the code at commit ce82c02f on branch
p1197-3d. It read the person's store (`~/.local/share/spark`) and the toolchain the store installs. It read the P934
walk folder `~/Development/spark-walks/p934-epaper` and the cards #1745, #1727, #1728 and #1729 with `gh`. It changed
nothing.
Every name, setting and area below is a proposal (H, this lens) unless a pointer says it exists.

## Findings

- AR-1 · The closest template for a 3D body is not `ShapeSource` but `PartPictureMaker` (P946). Pre-analysis section 2
  and ★C14 name `ShapeSource` only. `ShapeSource` answers one question, the part's 2D frame in px, and has no way to
  say what it needs or why it declined. `PartPictureMaker` already has the whole shape this epic needs. `uses()` gives
  `MakerUses(tools, inputs, cost, asks)`, so a member that needs a tool, costs money or asks first is one more entry.
  `make(request)` gives a candidate or a `Decline(maker, reason, missing)` and never raises. `PictureMakerChain.first`
  asks the members in order. `StoredPictureMaker` reads a record block `{document, made_by, likeness, credit,
  verified}`, follows `document` into `documents`, reads the file under its sha256 in the store's `sources`, and checks
  the bytes. `FramePictureMaker` makes a picture from the record's numbers alone. `MAKERS` maps a name to a class, and
  `BUILD_MAKERS` is the order. So a 3D body family is a sibling of this one, with the same five parts: a base
  `PartBodyMaker` (`uses`, `make`), a `BodyMakerChain` (a Service), `StoredBodyMaker` (a kept STEP file),
  `BoxBodyMaker` (a box from the record's numbers), and later `PhotoBodyMaker` (the box with the kept picture on its
  top face). · E (the template) H (the names) · scripts/spark/breadboard/picture_makers.py:21-31, :48-58, :61-91,
  :94-112, :165-188 · pre-analysis.md section 2 · brief.md ★C14 · supports: the body-source seam, the reuse claim

- AR-2 · `MakerUses` and `Decline` already serve two families. A third family imports them from the breadboard area too.
  `vendor_documents` in sourcing imports both from `spark.breadboard.picture_makers`. A 3D body family that does the
  same makes the breadboard area the home of a shared contract. Proposal: move the two Values to a neutral module in
  `spark.records` or `spark.core` before the third family arrives. Keep the old names as imports for one step.
  · E · scripts/spark/sourcing/vendor_documents.py:14 · scripts/spark/breadboard/picture_makers.py:21-29 · supports:
  nothing twice, the area boundary

- AR-3 · The pre-analysis survey left out the shelf, and the shelf holds the one board a real gadget ran on. The survey
  counted `parts/`, `boards/`, `chips/` and the store's `catalog/`, `boards/` and `known-boards/`. It did not count
  `shelf/` and `shelf/boards/` (P989). There, `firebeetle2-esp32c6.json`, the board of the P934 e-paper clock, holds
  `thickness_mm` 1.6, `mounting_holes` (count 4, 2.0 mm, spacing 22.0 by 56.6 mm, from DFRobot's dimension PDF
  V1.1.0) and `physical.features` with four holes, a USB-C, two buttons and a JST socket, each with x, y, w and h in
  the board's frame, all `verified: false`. The shelf's e-paper module holds a kept picture (`pictures.breadboard-top`)
  and a `body_mm` read from the PO's photo with the header pitch as its scale. So ★C1's "1 of 30" counts for holes,
  heights and pictures are true for the population surveyed, and low for the person's real project. The e-paper walk
  (one board, one module) is a candidate first board for the slice. · E · a `python3` read of
  `~/.local/share/spark/shelf/boards/firebeetle2-esp32c6.json` and `~/.local/share/spark/shelf/*.json`, 2026-11-26 ·
  `~/Development/spark-walks/p934-epaper/requirements.json` (board `firebeetle2-esp32c6`, part
  `epaper-2in9-bwr-mh-et-live`) · pre-analysis.md section 1 (the folders it counted) · supports: the record facts, the
  first slice

- AR-4 · The 3D facts grow from blocks that exist. They need no new top-level block. A case needs the outline, the
  board's thickness, the holes, each opening and each body's extent above and below the board. Today: the outline is
  `physical.width_mm` and `height_mm` for a board and `body_mm.width` and `height` for a module. The thickness is
  `physical.thickness_mm`. Holes are `mounting_holes` and features of kind `hole`. Openings are features of kind `usb`,
  `jst`, `button`, `connector` and `fpc`. What is missing is one number per body and per feature: how far it reaches
  above the board (and below it, for a pin header or a part on the back). Which edge an opening faces follows from
  its x, y, w and h against the outline, so it is not stored a second time. Each new number carries the provenance
  that `provenance.fact_problems` and the feature fields already carry (`verified`, `source`). · E (what exists) H
  (what to add) · scripts/spark/records/record_kind.py, `FEATURE_KINDS` and `FEATURE_FIELDS` (lines 46-50 of the
  `pictures` section, 361-365 of the file) · scripts/spark/breadboard/part_shape.py:11-13 · the shelf record of AR-3 ·
  supports: records grow by need

- AR-5 · The word "height" already means a plane dimension, so the new z fact needs another word. `body_mm.height` is
  the second dimension in the board's plane, and the DFR0534 record says so. `PartShape.size` is (width, height) in the
  plane too. A z fact called `height` gives one word two meanings (rule 1). Proposed words, H: `above_mm` and
  `below_mm` for a body, `above_mm` for a feature. The decider or words.md picks. The word "origin" has two meanings in
  this epic as well: where a fact came from (AGENTS.md: "with its origin") and where a model file's zero sits against
  the part. The second is a transform (offset and rotation) and needs its own word. "Model" already means a Wokwi
  simulation model in flow (`NO_MODEL_NOTE`, `no_model`), so a 3D solid is better called a "body" and its file a
  "body file". · E · parts/dfr0534-module.json:120-122 · pre-analysis.md section 1 (the DFR0534 note) ·
  docs/guide/patterns-and-names.md:216-217 (rule 1) · scripts/spark/flow/flow_codes.py (`NO_MODEL_NOTE`) · `grep -o
  model` over scripts/spark: 22 `model`, 15 `no_model` · supports: names, words.md rows before code

- AR-6 · A body file reference reuses the picture block and the documents map, so it is no second copy. A `pictures`
  block points at a `documents` entry (`url`, `sha256`, `file`, `retrieved`, `title`, `version`) and the file sits in
  `sources/<sha256>/`. A body block can be the same block with a transform: `{document, made_by, likeness, credit,
  verified, offset_mm, rotation_deg}`, under a key such as `bodies.step`. `record_kind` then checks both blocks with one
  function, not a copy of `_pictures_problems`. `LIKENESS` (`exact`, `near`, `rough`) already says how near a picture
  is to the real part, and the same three words fit a body: a vendor STEP is exact, a measured box is near, a box from a
  photo is rough. · E (the block, the map, LIKENESS) H (the body block) · scripts/spark/records/record_kind.py:252,
  :319-351 · boards/firebeetle2-esp32s3.json `documents` · scripts/spark/records/store.py:574-600 (`keep`) · supports:
  where a body file lives, nothing twice

- AR-7 · Fetching a library body reuses the one network door and the all-or-nothing keep. `store.fetch` is spark's only
  door to the network, and an Operation reaches it as `outside.fetch` with the effect `fetches`. `DocumentKeep` (P952)
  fetches what a finder named, writes the record dry, keeps the files, then writes the record. `VendorDocumentFinder` is
  a Strategy per maker with `knows`, `uses`, `page_of` and `find`. A body file is one more role beside `top-view` and
  `drawing`, and a library (KiCad packages3D, Espressif's kicad-libraries, Adafruit's CAD parts) is one more finder. So
  a `fetch-part-body` Operation (H) is small, and the build itself never fetches. The licence rule (research.md section
  1) stays a fact of each finder: a finder for a CC-BY-SA library says so in its `uses()` and its credit. · E ·
  scripts/spark/records/store.py:537-554 · scripts/spark/sourcing/find_documents.py:61, :146-175 ·
  scripts/spark/sourcing/vendor_documents.py:18-56 · docs/guide/patterns-and-names.md:61 (`fetch(url)`) · supports:
  where a body comes from, the store keeps it

- AR-8 · A STEP file is the one body form that reaches both engines and Fusion. A generated box written in tscircuit's
  own language reaches tscircuit's STEP but not KiCad. tsci's STEP export removes every component that has a
  `model_step_url` and merges the file, and turns every other component into a box of `circuit-json-to-gltf`'s scene
  (`scene3d.boxes`, `createSceneBoxSolid`). So a `jscad` or `size` cadModel becomes a solid in tsci's STEP. tsci's KiCad
  export writes a `(model ...)` line only from `stepUrl` or `wrlUrl`. The probe saw no model line for a non-STEP body.
  So there are two ways to give a generated box to the engines. (a) Each engine's writer renders the box in its own
  language: a `jscad` or `size` cadModel for tscircuit, nothing for KiCad until a file exists. (b) spark writes the box
  as a STEP file, kept like a fetched one, and every engine takes a file. (b) needs a STEP writer. build123d is 62.5 MB
  (research.md section 1). The one search found no pure-Python writer under a free licence with no OpenCascade. A box is
  a small B-rep, so a writer of spark's own is H. · E (the export path) H (the size key, the own writer) ·
  `~/.local/share/spark/toolchain/node_modules/@tscircuit/cli/dist/cli/main.js:179279-179318`, read 2026-11-26 ·
  research.md section 2 · pre-analysis.md section 4 · search 1 below · supports: where a body comes from, the
  board-engine seam, Q2

- AR-9 · The board-engine seam does not exist in code yet, and the body must not land in today's TSX text by hand. There
  is no base `BoardEngine`. `TscircuitEngine` is the one Adapter, built by name in `build_service.py:211` and
  `board_engine.py:129` (P1184 #1728 holds the seam). The chip line is written straight as TSX text in
  `board_sections.component_lines`. `board_sections.emit` already has 7 parameters against R3's limit of 5, held at 7
  by the baseline, so an 8th parameter for bodies fails the rules test. The P1089 council's architect said that the
  engine and its board writer are one choice and that the export asks the engine through a method of the Strategy. So
  the body reaches the engine as a resolved Value on each part (made once before `emit`, by the body chain), and only
  the tscircuit writer turns it into a `cadModel`. The KiCad writer, later, turns the same Value into a `(model ...)`
  line. P1185 #1729 (a box per module) then sits on P1184's writer side, or it hard-codes a tscircuit fact in the
  design area. · E · scripts/spark/design/board_sections.py:240-262 (the chip line at :259) · tests/architecture_baseline.json:54
  (`R3:...board_sections.py:emit: 7`) · tools/measure.py:245 · scripts/spark/build/build_service.py:211 ·
  docs/discovery/2026-11-26-p1089-kicad-and-tscircuit/council-answers.md:32-39 · supports: the board-engine seam, the
  order of P1184 and P1185

- AR-10 · The 3D export has an Adapter to reuse, so it adds no third wrapper of `tsci`. `TscircuitExport` already wraps
  `tsci export` with a limit, never raises and says why an export failed. It makes SVG only (`export_svg(circuit,
  form)`), and two places build it (`build_board.py:141`, `kept_files.py:577`). P1183 #1727's `export-board` adds STEP
  and KiCad files. So the step and GLB forms are one more form of the same export, reached through the engine Strategy's
  export method (P1089 council), with kicad-cli as a second exporter behind its own role (`board-exporter` or the role
  P1183 names). The Operation `export-board` (in `build_operations`, effects `reads`, `runs`, `writes`) is the one
  place a person, Claude or a later MCP server asks for a STEP. · E · scripts/spark/breadboard/tabbed_page.py:32-65 ·
  scripts/spark/build/build_board.py:141 · scripts/spark/build/kept_files.py:577 · gh issue view 1727 ·
  docs/discovery/2026-11-26-p1089-kicad-and-tscircuit/council-answers.md:18, :39 · supports: the export seam, nothing
  twice

- AR-11 · tscircuit's printed case is written in the engine's language, so it is an engine capability and not a neutral
  case maker. `<enclosure.fdm.box>` is an element inside `board.tsx`. A case made that way is lost when the engine
  changes, does not exist for a perfboard (which has no engine), and lands in the board's own STEP as two more solids
  (the probe: `unnamed_enclosure_fdm_box_1`). The build writes `board.tsx` again on each run, so a hand edit is lost
  (jobs-and-journeys.md, Claude's step 3). Proposal: a `CaseMaker` Strategy whose input is one neutral Value of the
  board's mechanics (AR-12). Its members: `TscircuitCaseMaker`, an Adapter that writes its own small TSX with the
  enclosure beside a copy of the board and exports it through AR-10's export, never into the build's `board.tsx`. Then
  a spark generator, a build123d member, and "by hand", which hands the facts and the STEP to Claude and a CAD tool.
  The member's `uses()` (AR-1's `MakerUses`) says which tool it needs, so the tscircuit member says it needs the
  tscircuit engine. · E (the element, the probe, the rewrite) H (the seam) · pre-analysis.md sections 3 and 4 ·
  brief.md ★C5 · scripts/spark/build/build_service.py:284 (writes board.tsx) · supports: the case seam

- AR-12 · One Value of the board's mechanics is the centre that keeps every later member DRY. Every case maker, the
  facts Claude reads (J7), a viewer and a later perfboard all need the same numbers: the outline, the thickness, the
  holes, each placed body (its reference, x, y, rotation, side, above and below), and each opening with its edge. Today
  they are spread over the board record, each part record and the built `circuit.json` (the placements). Proposal: one
  Value, for example `BoardMechanics`, built once by one Service from the records and the placements, and one Operation
  that shows it, for example `show-board-mechanics` (effects `reads`, no tool). It has at least two readers in the first
  slice (the case maker and Claude's JSON), so it passes P1089's test that a Value with one reader is a guess. A missing
  number stays `null` with its field named, as `NotDrawnError` names one today, so Claude never fills it in. · E (the
  facts are spread, the rule on null) H (the Value, the Operation) · AGENTS.md ("a `null` is not a value to fill in") ·
  scripts/spark/breadboard/part_shape.py:143-148 · docs/discovery/2026-11-26-p1089-kicad-and-tscircuit/finding.md:296-297
  (the "one reader" line in section 4) · supports: the case seam, J7, the perfboard's fit

- AR-13 · "Claude drives Fusion" is not a member that spark's code can run. The tools list already has the kind `mcp`
  for a server that Claude calls (`jlcpcb`, `espressif-docs`, `wokwi-mcp`, `sigrok`), off by default where it costs or
  needs hardware. Fusion's MCP server runs only while Fusion is open (research.md section 3). So spark's part of the
  Fusion path is an `mcp` entry (off, the PO's to turn on), the STEP from `export-board`, and the facts from
  `show-board-mechanics`. The case design in Fusion is Claude's work, as the firmware is (spark exports facts, never
  behaviour). The misfit to guard: a skill or command that holds case numbers (a wall, a clearance, a hole size) in its
  prompt. Those numbers belong in settings and in the Value of AR-12, and the prompt only names the Operations. · E ·
  data/tools.json (the four `mcp` entries) · scripts/spark/records/tool_choices.py:65 (`is_mcp_server`) · AGENTS.md
  (principles: facts never behaviour, an agent prompt never repeats logic) · supports: the CAD-tool seam, the misfit list

- AR-14 · A case's wall, fit clearance and lid are choices, not facts, so each is a setting with a default and a layer.
  AGENTS.md says spark never writes thresholds. A board's outline is a fact. A 2 mm wall is a choice. tscircuit's
  enclosure has its own defaults inside the package. If spark uses them silently, the choice is hidden in a tool. So
  each case maker reads its numbers from named settings, and the case's answer names each number and whose word it is
  (P1194 D13, D14). · E (the rule) H (the settings) · AGENTS.md (principles) ·
  docs/discovery/2026-11-26-p1194-settings/brief.md D13, D14 · supports: the settings table

- AR-15 · The browser viewer cannot be a tab of today's page without changing that page's rule. `TabbedHtmlPage` says
  "The page has no script and loads nothing from the web". A GLB view needs a script (three.js, or `@tscircuit/3d-viewer`
  with a bundle step). So the viewer is either its own Renderer and file (for example `board-3d.html` with three.js and
  the GLB inline), or the decider lifts the rule for one tab. The flow page has its own script (`page_script.js`) and is
  an Artifact, a third home. The viewer is not needed to reach a STEP in Fusion or a printed case, so it can wait. · E ·
  scripts/spark/breadboard/tabbed_page.py:10-11 · docs/guide/patterns-and-names.md:40 (`page_script.js`) ·
  research.md section 4 · supports: the viewer seam waits

- AR-16 · Print files are a form of a case maker's answer, not a seam of their own. A case maker gives solids in mm.
  STL and 3MF are two writings of them. tsci's 3MF export fails in the installed CLI (★C6), and slicing stays the
  person's slicer (research.md section 4). So the case Operation takes a format argument with a project default, and
  each member says which forms it can write in `uses()`. A separate `PrintFileWriter` Strategy waits until two members
  share a writer. · E (★C6, the slicer line) H (the shape) · brief.md ★C6 · research.md section 4 · supports: the print
  files wait

- AR-17 · Where the code lives. The areas already import each other in cycles at package level: design and build import
  each other, so do breadboard and build, and so do sourcing and breadboard. `part_shape` (the 2D frame in mm) sits in
  breadboard and imports `design.footprint_emitter`. P1199's architecture lens proposes a new area `scripts/spark/layout`
  that imports only `spark.core`, with `PartShape` moved there as the body in mm. Proposal for this epic: a new area for
  the mechanical side, for example `scripts/spark/mechanical` (H, the name: industry splits ECAD and MCAD), holding the
  body chain, the mechanics Value and its Service, the case makers and their Operations. It imports `spark.core` and
  `spark.records` and takes the 2D frame as a Value. It never imports breadboard, design or build. `export-board` stays
  in build, where P1183 puts it. The reason for a new area: the body serves the PCB, the perfboard, the case and the
  sculpture, and none of today's areas owns all four. · E (the imports) H (the area) · a `grep` of `from spark.<area>`
  per area over scripts/spark, 2026-11-26 · scripts/spark/breadboard/part_shape.py:21-23 ·
  docs/discovery/2026-11-26-p1199-layout-core/council/architecture.md:36 (ARCH-15) · supports: the area, Q5

- AR-18 · The body is modelled three times today, and a 3D box from the wrong source is a fourth copy and invents a
  fact. P1199's ARCH-12 counts `BodyBox` (px), `board_components.body_of` (mm, with an invented 16 by 12 mm default)
  and `PartShape` (mm, refuses a missing `body_mm`). A box built from `body_of` gives every module with no outline a
  16 by 12 mm solid in Fusion. The P1089 council's Q10 answer already says "A null height gives no box, and the build
  says so." So `BoxBodyMaker` reads `PartShape` (or its successor in the layout core), declines with the missing field,
  and never reads `body_of`. · E · docs/discovery/2026-11-26-p1199-layout-core/council/architecture.md:30 (ARCH-12) ·
  scripts/spark/design/board_components.py:17-22 · docs/discovery/2026-11-26-p1089-kicad-and-tscircuit/council-answers.md:23
  · supports: nothing twice, the first slice

- AR-19 · A fetched vendor body can leak into the person's project and its git. tsci reads a local STEP from its working
  folder (research.md section 2). The build's work folder is removed after the build, but `--keep` and `export-board`
  write into the project. A STEP that merges a CC-BY-SA or private-use body is then a file in a folder that P1193 may
  sync to a public place, and P1194's D2 says what syncs is a setting. Proposal: the body file is linked or copied into
  the work folder only, the exported assembly says in its answer which bodies came from which licence, and spark's
  section of the project's `.gitignore` (P1150's `IgnoreList`) lists the 3D outputs until the person says otherwise.
  · E (the read, the keep, the sync setting) H (the leak, the proposal) · research.md section 2
  (`load-local-step-model-fs-map.ts`) · docs/guide/patterns-and-names.md:40 (`BuildBoard` removes the work folder,
  `IgnoreList`) · docs/discovery/2026-11-26-p1194-settings/brief.md D2 · supports: where a body file lives, the misfit list

- AR-20 · Two files on the path are at their limit. `kept_files.py` has 600 lines, R1's limit for a module, so a keep
  of a 3D file there needs a split first. `board_sections.emit` holds 7 parameters (AR-9). · E · `wc -l
  scripts/spark/build/kept_files.py` gives 600 · tools/measure.py:242 · tests/architecture_baseline.json:54 · supports:
  the first slice's size

- AR-21 · The frame leaves room for the perfboard without building for it. A perfboard has no engine, so its 3D needs
  three inputs: the perfboard's record (pitch, holes, size), the layout core's plan (P1199: whole holes with a pitch in
  mm) and the bodies. All three feed AR-12's Value through a second filler, beside the PCB's filler that reads
  `circuit.json`. The case makers and the viewer read only the Value, so they need no change. Writing the perfboard's
  assembly as a STEP then needs an assembler of spark's own (a later `AssemblyWriter` member, for example build123d),
  because no engine writes it. None of this is built in the first slice. The only thing the first slice must not do is
  read `circuit.json` inside a case maker. · E (no perfboard code, the layout core's unit) H (the fit) · brief.md
  ★C16 · scripts/spark/flow/flow_codes.py:479 · docs/discovery/2026-11-26-p1199-layout-core/brief.md D-q1 (a) ·
  supports: the perfboard's fit

- AR-22 · The frame leaves room for the circuit sculpture P1198 #1746 too. A flat printed jig is a plate with holes or
  pockets at each part's place. That is one more `CaseMaker` member, or a sibling Strategy with the same input, AR-12's
  Value. The research found the same idea in pogo-pin fixtures (OpenFixture, pogojig, pcb-jigify). Nothing is built for
  it. · E (the related tools) H (the fit) · research.md section 5 · supports: P1198's fit

- AR-23 · The journey already names the step. `UNBUILT_STEPS` holds `case` ("At the printer: a case for the board."),
  greyed on the station line. The first Operation that makes a case needs a phase reader in flow's `phase_readers` and
  a next step, and the README's "What works today" and `tools/journey.py` change in the same PR (AGENTS.md).
  P1039's seam S8 ("phases that end and go past deploy") is the frame for it. · E · scripts/spark/flow/flow_codes.py:477-482
  · docs/discovery/2026-11-23-p1039-rd-direction/direction.md:138 · AGENTS.md (keep the journey current) · supports:
  the first slice's done line

- AR-24 · Two pointers in the discovery's files are wrong. jobs-and-journeys.md says an agent exports a STEP "by the
  doc recipe" at docs/guide/agents.md:170-176. That recipe exports `kicad_pcb` and runs a DRC. The STEP line is in
  skills/spark-design/SKILL.md:129 (`-f step`). The rest checked holds: ★C2's chip line is board_sections.py:259, and
  ★C14's tools list has 14 roles and no 3D role. · E · docs/guide/agents.md:170-176 ·
  skills/spark-design/SKILL.md:129 · scripts/spark/design/board_sections.py:259 · data/tools.json `roles` · supports:
  the facilitator's claims

- AR-25 · The seams, their names, their Operations and their settings. Every name and setting is H, this lens's
  proposal, until P1194 #1740 holds the settings. The layers are P1194's: spark's default, yours (the store), this
  project, and the empty account slot. A choice that shares the person's data or spends money is his alone (P1194 D12).

  | seam | job, in one sentence | base · members (Adapters carry the tool's name) | Operation · area | setting · default · layer | reuses | first slice? |
  | --- | --- | --- | --- | --- | --- | --- |
  | body facts | hold how far each body and feature reaches above and below the board | none, record fields in `physical`, `body_mm` and `physical.features` | `parts.py` setters on the records area | none: a fact, not a choice | `record_kind`, `provenance` | yes, by need |
  | body file | point at a kept STEP and its transform | none, a block in `bodies` beside `pictures` | `fetch-part-body` · sourcing | `body-libraries`: the finders asked, in order · none (no fetch until asked) · user | `DocumentKeep`, `VendorDocumentFinder`, `store.fetch`, `sources/<sha256>` | no |
  | body source | give each record's body, or decline with the missing field | `PartBodyMaker` · `StoredBodyMaker`, `BoxBodyMaker`, later `PhotoBodyMaker` | none of its own, called by the board writer and the mechanics Service · mechanical | `body-makers`: the order · `stored`, then `box` · spark, then user | `MakerUses`, `Decline`, the chain's shape (AR-1, AR-2), `PartShape` | yes, with `box` only |
  | body to engine | turn a body Value into the engine's language | the board writer of `BoardEngine` (P1184) · `TscircuitBoardEngine`, later `KicadBoardEngine` | `build-board` · build | the `board-engine` role · `tscircuit` · user, project | P1184's seam, the tools list | yes, the tscircuit side |
  | 3D export | write the built board as STEP or GLB | the engine Strategy's export method, plus a kicad-cli Adapter behind a role | `export-board` (P1183) · build | `--form` with a project default `step` · the exporter role (P1183) · `tscircuit` · user | `TscircuitExport`, generalised from SVG | yes, STEP only |
  | mechanics | give the board's outline, holes, bodies and openings as one Value | Service `BoardMechanicsReader` (H), Value `BoardMechanics` · a PCB filler now, a perfboard filler later | `show-board-mechanics` · mechanical | none | the records, `circuit.json`'s placements | yes |
  | case | make a printable case around the mechanics | `CaseMaker` · `TscircuitCaseMaker`, later a spark generator and `Build123dCaseMaker`, and the hand-off to Claude | `make-case` · mechanical | `case-maker` · `tscircuit` · user, project. `case-wall-mm`, `case-clearance-mm`, `case-lid` · spark's numbers, said in the answer · project | AR-12's Value, AR-10's export | yes, one member |
  | CAD tool | let Claude open the board and design around it | none in code: an `mcp` entry for Fusion's server | none: Claude calls the server with the outputs of `export-board` and `show-board-mechanics` | `fusion-mcp` entry `on` · off · user (his alone) | the tools list's `mcp` kind | no, the PO turns it on |
  | print files | write the case's solids as STL or 3MF | none until two members share a writer | the format argument of `make-case` | `print-format` · `stl` · user | the case maker's own writer | with the case |
  | viewer | show the assembled board in a browser | a Renderer, for example `Board3dHtmlPage` | none of its own, written by `export-board` | `board-viewer` · `none` · user | the GLB from AR-10, three.js | no |
  | assembly writer | write an assembly STEP where no engine does | `AssemblyWriter` · later `Build123dAssemblyWriter` | `export-board` for a perfboard · mechanical | none until a second member | AR-12's Value | no |

  · H (the table) E (each "reuses" pointer, in the findings above) · supports: every seam question, Q1 to Q6

- AR-26 · The seams as one diagram. Solid lines are the first slice proposed here. Dotted lines wait.

  ```mermaid
  flowchart TD
    CLI["CLIs: parts.py, check_spine.py, a mechanics CLI"] --> OPS
    CL["Claude, a later MCP server, LangGraph"] --> OPS
    subgraph OPS["Operations in the catalogue"]
      BB["build-board"]
      EB["export-board (P1183)"]
      SM["show-board-mechanics"]
      MC["make-case"]
      FB["fetch-part-body"]
    end
    REC["Records: physical, body_mm, features, mounting_holes, bodies block, documents"] --> CH
    ST["Store: sources by sha256"] --> CH
    FB -.-> DK["DocumentKeep and a library finder"] -.-> ST
    FB -.-> REC
    SET["Settings: spark's default, yours, this project, account slot"] -. "chooses" .-> CH
    SET -. "chooses" .-> CM
    SET -. "chooses" .-> EN
    CH{{"PartBodyMaker chain"}} --> BOX["BoxBodyMaker: from PartShape and the z facts"]
    CH -.-> STO["StoredBodyMaker: a kept STEP"]
    CH -.-> PH["PhotoBodyMaker: the box with the kept picture"]
    BB --> EN{{"BoardEngine (P1184) and its board writer"}}
    CH --> EN
    EN --> TS["TscircuitBoardEngine: cadModel per part"]
    EN -.-> KC["KicadBoardEngine: model line per part"]
    TS --> CJ["circuit.json"]
    EB --> EX{{"the engine's export method"}}
    EX --> STEP["board.step, later GLB"]
    EX -.-> KX["kicad-cli exporter"]
    SM --> MS["BoardMechanicsReader"]
    CJ --> MS
    REC --> MS
    CH --> MS
    MS --> BM["BoardMechanics Value"]
    LAY["P1199 layout plan, a perfboard"] -.-> MS
    MC --> CM{{"CaseMaker"}}
    BM --> CM
    CM --> TCM["TscircuitCaseMaker: its own small TSX, never board.tsx"]
    CM -.-> OWN["spark's generator"]
    CM -.-> B1["Build123dCaseMaker"]
    CM -.-> JIG["a printed jig for P1198"]
    TCM --> PF["case.stl"]
    BM --> JSON["facts as JSON for Claude"]
    STEP --> F360["Fusion 360 through its MCP server, Claude's work"]
    JSON --> F360
    BM -.-> AW["AssemblyWriter for a perfboard"]
    STEP -.-> VW["Board3dHtmlPage viewer"]
  ```

  · H · supports: every seam question

- AR-27 · What the first slice must set, and what waits. It must set four things, because later members plug into them
  and a wrong shape now costs a rewrite. (1) The z facts and their words (AR-4, AR-5), because every member reads them.
  (2) The body chain with `box` as its one member (AR-1, AR-18), because a second member is then one class and one
  name in a list. (3) The body reaches the engine only through P1184's writer (AR-9), because a cadModel line written
  in `board_sections` today is a tscircuit fact in the design area. (4) The mechanics Value and its Operation
  (AR-12), because every case maker, Claude and the perfboard read it. The export is P1183's card and only needs its
  STEP form. One case member (tscircuit's, which is installed and costs nothing) proves the case seam. These wait:
  fetched bodies and the body-file block (AR-6, AR-7), photos, KiCad's writer, the assembly writer, the viewer, 3MF,
  and Fusion's MCP entry. This holds if the PO's first slice is "a STEP in Fusion and a printed case", the brief's
  proposed outcome. · H (this lens's order) E (the outcome line) · brief.md, the outcome line · supports: Q1, the first
  slice

- AR-28 · Where the epic risks a misfit with the core, in one list. (a) A tool name in a base: a base called
  `EnclosureMaker` or `StepExporter` names tscircuit's word or a format. `CaseMaker` and the engine's export method say
  the job (rule 2). (b) Logic in a prompt: case numbers or a body's size typed in a skill for Claude to use in Fusion
  (AR-13). (c) A second copy of a fact: an opening's edge stored beside its x and y, a z fact in both `body_mm` and a
  new block, a body block that copies the picture block's check, the 16 by 12 mm default reaching 3D (AR-4, AR-6,
  AR-18). (d) A third wrapper of `tsci export` (AR-10). (e) A case written into the build's `board.tsx`, so the build's
  output depends on a case choice (AR-11). (f) A thick interface: one Operation that builds, exports, makes a case and
  opens a viewer. Each job is its own Operation with its own effects, so a person can say yes to a fetch without saying
  yes to a write (AR-25). (g) A shared contract that lives in the breadboard area (AR-2). · E (each pointer above) H
  (the list) · docs/guide/patterns-and-names.md:216-220 · supports: the misfit question

## What I could not check, and why

- Whether a `jscad` or `size` cadModel sets the size of the box in tsci's STEP. The code path that turns a component
  into a scene box exists (AR-8), but I did not run a build, because the brief asks the lens to read and change nothing.
- Whether Fusion keeps the solid names `U1` and `U2` from tsci's STEP. No file was opened in Fusion (pre-analysis
  section 5).
- Whether a box writer of spark's own is small. The search found no ready writer under a free licence (search 1). The
  size of a hand-written STEP box is my estimate, not a measurement.
- Whether `TscircuitCaseMaker` can run on its own small TSX beside a copy of the built board, without the board's
  `board.tsx`. I did not read the `create-fdm-enclosure` API beyond the pre-analysis's summary.
- The licence terms of each library finder named in AR-7. research.md section 6 lists those it did not read.
- Whether the shelf's FireBeetle 2 C6 record and the e-paper module's record differ from the walk folder's copies in a
  fact the 3D slice reads. `cmp` shows that the e-paper files differ at line 473. I did not read the difference.
- Whether the proposed `mechanical` area passes a cycle check between areas. No test enforces area imports today
  (P1199 ARCH-15), so I only read the imports.

## Questions for the decider

- Q1 · Is the first slice "a STEP in Fusion and a printed case" for the e-paper clock's board, with the four seams of
  AR-27 set and the rest waiting? · decides: the first slice's scope and which seams it sets
- Q2 · Does a generated box reach the engines as a STEP file that spark writes (one form for every engine and Fusion,
  a new writer or build123d's 62.5 MB), or in each engine's own language (no new tool, no body in KiCad's export)? ·
  decides: the body source's output form and whether a 3D tool enters the install (AR-8)
- Q3 · Does P1185 #1729 (a box per module) wait for P1184 #1728 (the engine seam), so that the cadModel line is written
  only by the tscircuit writer? · decides: the order of the two cards (AR-9)
- Q4 · Which words name the z facts and the body file's transform, instead of "height", "origin" and "model"? ·
  decides: the words.md rows before code (AR-5)
- Q5 · Does the mechanical side get a new area (for example `scripts/spark/mechanical`) that imports only core and
  records, or does it live in an existing area? · decides: the import direction and where the body chain, the
  mechanics Value and the case makers live (AR-17)
- Q6 · Are the case's wall, clearance and lid settings that spark names in each answer, with spark's numbers as the
  default, rather than tscircuit's built-in values? · decides: whether a case choice can hide in a tool (AR-14)
- Q7 · May a kept export or a kept case in the project hold a fetched vendor body, or do the 3D outputs go to spark's
  `.gitignore` section until you say otherwise? · decides: the licence risk of AR-19
- Q8 · When the viewer comes, is it its own file with a script, or does the page's no-script rule change for one tab? ·
  decides: the viewer's home (AR-15)

## Searches

- "pure python STEP AP214 writer box solid no OpenCascade MIT library" · the decision it served: whether a generated
  box can be written as STEP with no heavy dependency (Q2, AR-8) · used: it found no ready pure-Python writer under a
  free licence. steputils (MIT) says it is "in planning state", and breptile and mesh2cad run on OpenCascade.
  https://pypi.org/project/steputils/0.1a2, https://pypi.org/project/breptile/, https://socket.dev/pypi/package/mesh2cad,
  read 2026-11-26
