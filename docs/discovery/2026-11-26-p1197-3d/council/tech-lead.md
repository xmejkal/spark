# P1197 council: the tech lead (feasibility and fit, and the physics lens for mechanical numbers)

Read on 2026-11-26 on branch p1197-3d at commit ce82c02f, in the store (`~/.local/share/spark`) and in the installed
toolchain (`@tscircuit/cli` 0.1.2113, `tscircuit` 0.0.2600). Every probe ran in a scratch folder with its own
`package.json` and a `node_modules` link to the store's toolchain, as `scripts/spark/build/board_engine.py:46` does. The
scratch folder is deleted. Nothing in the repository changed except this file. The probe board is 60 x 40 mm with a
7-pin module `U1` and a 4-pin header `U2`, unless a row says otherwise. Each variant ran once.

## Findings

### Feasibility and fit

- **TL-1** · The smallest end-to-end path runs today with what spark installs, and it needs no new tool. spark writes a
  part's body as `cadModel={{ jscad: plan }}`, where the plan is plain JSON such as
  `{"type":"cuboid","size":[w,d,h],"center":[x,y,z]}` inside a `{"type":"union","shapes":[...]}`. Then
  `tsci export <built circuit.json> -f step` and `-f glb` each run in 2 to 3 s. The STEP holds one solid named `U1` for
  the body, and the GLB holds a node named `U1`. · E · probe: `tsci export v_jscad.tsx -f step --disable-parts-engine`
  gave rc 0 and 471,604 bytes with solids `PCB`, `U1`, `U2`. `-f glb` gave rc 0, 181,092 bytes, with nodes `Box0`,
  `U1`, `U2`. The plan format is from `node -e` on `jscad-planner`'s `jscadPlanner.primitives.cuboid`. ·
  supports only: the tscircuit path on a probe board. It does not show a real spark board, Fusion, or the build time
  with a plan inline in `board.tsx`.

- **TL-2** · In tscircuit's STEP, a part with a STEP body loses its reference name. The merged solids keep the names
  inside the model file, and no solid is named `U1`. The GLB keeps `U1`. So the brief's C4 ("tscircuit's STEP names
  each solid by reference") holds for a box or a jscad body. It does not hold for a STEP body. · E · probe `v_step`:
  `grep -o "MANIFOLD_SOLID_BREP('[^']*'"` lists `PCB`, `U2`, `VL6180X-pcb`, `VL6180X-parts` and `VL6180X-pin1` to `-pin7`,
  and the file holds one `MAPPED_ITEM`. The GLB nodes are `Box0`, `U1`, `U2`. The writer names a box solid by
  `box.label`, the source component's name (`@tscircuit/cli/dist/cli/main.js:179165` to 179220). The STEP merge
  path does not use that label (`main.js:179398`). · supports only: tscircuit 0.0.2600 with one model file.

- **TL-3** · No body form feeds both engines with the reference name today. A jscad body reaches tscircuit's STEP named
  `U1`, but the KiCad export drops it: `kicad_zip` writes a `(model ...)` line only for the `pinrow4` header. A STEP body
  is copied into the zip as `3dmodels/<board>.3dshapes/vl6180x.step` with a model line. kicad-cli then exports it as an
  assembly with the instance named `U1` and the product named `vl6180x`. In tscircuit's STEP the same body has no `U1`
  (TL-2). · E · probe: `grep '(model'` on both `.kicad_pcb` files. `kicad-cli pcb export step --subst-models` ran in
  0.162 s, and its file holds `NEXT_ASSEMBLY_USAGE_OCCURRENCE('2','U1'` and `PRODUCT('vl6180x'`. The research's E,
  circuit-json-to-kicad writes a model line from `stepUrl` or `wrlUrl` only, agrees. · supports only: one probe board.
  It opens one more option, still an H: spark writes one STEP file per placed part and puts the reference in its solid
  names (TL-4 shows that it can). Then the name reaches both engines. Not run.

- **TL-4** · spark can write a STEP body for a module itself, with the Python standard library and with no build123d. A
  spike of about 110 lines wrote an AP214 file for the VL6180X record: a 12.7 x 17.8 x 1.02 mm PCB, a 1.2 mm parts
  box and 7 pins at 2.54 mm. The file was 56,340 bytes with 9 named solids and one product, `VL6180X`. Three readers
  took it. occt-import-js 0.0.23 read 9 meshes. tscircuit merged it into its STEP and its GLB. kicad-cli 10.0.6 exported
  it, with the bytes copied unchanged into the zip (`cmp` gave "same-bytes"). · E · probe commands as above. · supports
  only: boxes, made of planes and straight edges. A cylinder, a hole, a fillet or a boss needs circles and curved
  surfaces. That is more of spark's own code, or build123d (62.5 MB wheel, research.md section 1). OCCT read the file,
  and KiCad uses OCCT. Fusion uses another kernel, and no import into Fusion ran.

- **TL-5** · What is installed for 3D, read in the toolchain. `@jscad/modeling` 2.13.0 is MIT. `jscad-planner` 0.0.13
  has an MIT LICENSE.md, and its package.json names no licence. `jscad-to-gltf` 0.0.5 and `circuit-json-to-gltf`
  0.0.128 are there too. `occt-import-js` 0.0.23 is LGPL-2.1. `@tscircuit/create-fdm-enclosure` 0.0.4 is MIT.
  `@tscircuit/manifold-2d` 0.0.6 is Apache-2.0. None of them writes STEP. occt-import-js only reads it. tscircuit's
  STEP writer (`circuit-json-to-step` with `stepts`) is bundled inside the 30 MB `@tscircuit/cli/dist/cli/main.js`
  (line 179057). It is not a package that spark can import. · E · each `package.json` in the toolchain's
  `node_modules`, and `grep` on `main.js`. · supports only: what the pinned versions hold.

- **TL-6** · spark can make the case after the build with no rebuild. A direct call of `createFdmEnclosure` took 5 ms
  and gave plans for a base and a lid. A script added them as two `cad_component` records to a copy of a built
  `circuit.json`. Then `tsci export` wrote a STEP with the solids `Casebase` and `Caselid`, and a GLB. Both exited 0.
  The other way is `<enclosure.fdm.box>` inside `board.tsx`. It needs `import { assembly, enclosure } from "tscircuit"`.
  Without that line, the export stops with `ReferenceError: assembly is not defined`. The element also adds a
  `pcb_component` to `circuit.json` (`pcb_component_2` in the probe). Every reader of `circuit.json` then sees it. It
  also needs a new build of the board. · E for the runs. The commands were `node enc.mjs`, `node inject.mjs`
  and `tsci export j_case.circuit.json -f step`. · H: the risk is in the appended records. They are fields of tscircuit's `circuit.json` that spark does not
  own (`model_jscad`, `model_origin_alignment`), so a tscircuit upgrade can change them. The installed README says
  that the feature "spans unreleased branches" (`create-fdm-enclosure/README.md`, "Current coordinated branches").

- **TL-7** · Print files do not come from tsci today. Its export formats include no STL. `component-box-3mf` failed
  again with `ENOENT ... @tscircuit/cli/dist/cli/manifold.wasm` (C6 reproduced). A 30-line Node script wrote binary STL
  files from the case plans: the base had 28 triangles and the lid 44. The base spans z 0 to 13.60 and the lid z 9.60 to
  15.60, so they overlap by the 4 mm lip. An exact-vertex edge count found 16 of 50 edges (base) and 32 of 82 edges (lid)
  that two triangles do not share. These are T-junctions from jscad's polygons. · E · probe `node stl.cjs
  enc.circuit.json`, and `tsci export --help`. · H: a slicer usually repairs such edges. Whether PrusaSlicer repairs
  these files without a warning was not checked.

- **TL-8** · A missing model file passes in silence. The build ignores it: `tsci build` with `stepUrl:
  "/nonexistent/missing.step"` exited 0 in 2 s. The STEP export exits 0 too. It prints `Failed to merge STEP model
  ... Only HTTP(S) URLs are supported`, and the part has no body (solids `PCB` and `U2` only). So an export
  Operation has to check every model file before it runs, and it has to say which body is missing. A STEP with a part
  left out must never count as a pass (docs/guide/agents/never-assume.md). · E · probe folder `b`, `log2.txt`.

- **TL-9** · A model kept in the store at an absolute path works. STEP, GLB and `kicad_zip` all ran with it, and so did
  an export from a built `circuit.json` run from another folder. A relative path is resolved against the current
  folder (`path35.resolve(process.cwd(), modelUrl)`, `main.js:180291`). `TscircuitExport` runs `tsci` with no `cwd`
  (`scripts/spark/breadboard/tabbed_page.py:49`), so a relative path points to the wrong place. An `https` URL is
  fetched during the export (`readStepFile` calls `fetch`, `main.js:179384`). So an export with a remote model reaches
  the network, and its Operation must declare `fetches` (`scripts/spark/operation_catalogue.py`, `NETWORK`). · E ·
  probe folder `proj`: `grep -c "VL6180X-pcb" abs.step` gave 1, and `unzip -l abs-kicad.zip` listed the model.

- **TL-10** · The STL rows of the pre-analysis came out the same. The STEP export ran, and a 10 x 10 x 5 mm STL box
  landed at z -4.30 to 0.70 with the board top at 0.70, so it hangs down through the board. The GLB export failed with
  `RangeError: Out of bounds access` in `parseBinarySTL` (`circuit-json-to-gltf/dist/index.js:16174`). This time the STL
  was ASCII, and the loader read it as binary. · E · probe `v_stl`. · supports only: tsci 0.0.2600. The pre-analysis
  calls the STL path not working. The run shows a mirrored placement and a loader fault. A `rotationOffset` was not
  tried on the placement.

- **TL-11** · Two documents disagree on the GLB. The P1089 finding, section 2.3: "`tsci export -f glb` did not run". The
  card #1745 repeats it: "`tsci export -f glb` did not run." The pre-analysis, section 4: "plain, no model | 254 KB,
  ran". Here the GLB ran on every variant except the STL one (plain: rc 0, 205,928 bytes). · E · the three documents and
  the probe. · supports only: tsci 0.0.2600 on this Mac. This run does not show why the P1089 run failed.

- **TL-12** · The brief's C8 and the FireBeetle record disagree. C8: "No library found holds a model of the dev boards
  spark uses (DevKitC, C6 DevKitC, XIAO, FireBeetle)." `boards/firebeetle2-esp32s3.json`, `//max_component_height`:
  "The STEP model suggests ~7 mm above the top face". The same note says that the model includes the camera and its
  FPC, so the record holds no number. So someone read a STEP of the FireBeetle 2 ESP32-S3, but the record names no URL and no licence. · E ·
  the brief and the record. · supports only: that such a model exists. Its terms are —.

- **TL-13** · What each part of the epic touches, by area. Read in the code, H where it says so.

  | Area | What it takes | Pointer |
  |---|---|---|
  | `records` | A height fact with `{value, verified, source}` and its rule. A per-feature height is a schema change, because a feature with an extra field is refused ("holds d, which is no field of a feature"). A place in the store for fetched models: the `sources/<sha256>/` pattern exists. | `provenance.py:13`, `record_kind.py:363` |
  | `sourcing` | A reader of the new fact in `part_facts`. The research skill and the datasheet reader ask for it. | `scripts/spark/sourcing/part_facts.py` (H: not read line by line) |
  | `design` | Emit `cadModel` on each part (`board_sections.py:259`). Emit it on the board's `Mcu` too (`board_sections.py:139`). The footprint module spreads `{...props}` (`footprint_emitter.py:308`), so a `cadModel` passes through. The body maker turns a record into a plan or into STEP text. It is a Strategy family next to `ShapeSource` (`part_shape.py:61`). Which area holds it is open. | read |
  | `build` | Nothing for a body. A `cadModel` is data in `board.tsx`, and the build does not read the model file (TL-8). | probe |
  | the export (P1183) | A new Operation `export-board`. It holds an Adapter over `tsci export` on the built `circuit.json`, a copy of `TscircuitExport`. It also holds the model-file check of TL-8, the case of TL-6 and the STL writer of TL-7. KiCad's STEP is the optional second Adapter. `data/tools.json` has no role for any of these jobs. | `tabbed_page.py:32`, `data/tools.json` `roles` |
  | `checks` | A clearance check of the tallest height against the lid, from the same facts (PHY-2). | H |
  | `operation_catalogue` | One more table or entry. No 3D Operation exists today. | `operation_catalogue.py:26` |
  | `flow` and the docs | The journey's status, the README's "What works today" and `tools/journey.py` (AGENTS.md, "Keep the journey current"). | AGENTS.md |

- **TL-14** · Fit with the technical direction, point by point. tscircuit stays the board engine: every probe used only
  the pinned toolchain (E). kicad-cli stays an optional export: its only extra in this epic is the named assembly of TL-3
  (E). The build stays free of any 3D tool: a body is data in `board.tsx`, and the case and the print files come after
  the build (TL-6, TL-7, E). The build time with a jscad plan inline was not measured, so that point is H. Free and local:
  everything that ran is MIT, Apache-2.0 or LGPL-2.1 and installed (E, TL-5). The CLI comes first: every step ran as a
  command (E). KiCad stays optional for a person: nothing in TL-1, TL-6 or TL-7 needs it (E). The MVP bar: a body and a
  case do not move a basic project closer to a breadboard with working firmware. The card says the epic comes after
  the MVP (D · spark-main · 2026-11-26, the brief's "Already decided"). Version risk: create-fdm-enclosure is 0.0.4, and
  its README points to unreleased forks (E), so the case path holds only for the pinned version (H).

- **TL-15** · Claims and the cheapest way to settle each. A read or a short spike settled most of them here. The settled
  claims are these. The STEP merge and the names. The KiCad path. A STEP written by spark. The case without a rebuild.
  STL from the plans. A missing model, a model in the store, and the GLB. A short spike that did not run here can
  settle three more. The first is the build time with jscad plans inline: one `tsci build` of the amplifier fixture with
  them, and one without. The second is a STEP per placed part that carries the reference into both engines (TL-3). The
  third is a `rotationOffset` for an STL. Only the
  PO's own setup can settle three: whether Fusion keeps the names, whether the personal licence limits the import, and
  whether a print fits (PHY-7). · E for the settled ones (the rows above). The rest is H.

- **TL-16** · Fusion and names: forum posts say that Fusion keeps the names of components from a STEP file and renames
  bodies "Body 1", "Body 2". If that holds, tscircuit's flat file (one product `PCB` with bodies `U1`, `U2`) loses the
  names in Fusion. By the same reports, KiCad's assembly (instances named `U1`) keeps them, and so does an assembly that spark
  writes. · H ·
  the search below (forums.autodesk.com threads "step-file-import-renames-bodies" and "Imported assembly file structure
  has bodies vs components", read 2026-11-26 through search snippets). · supports only: what users report. It settles
  nothing for Fusion today.

- **TL-17** · The Fusion area figure, done with arithmetic. The P1089 finding, section 2.3: "the licence limits
  electronics to 2 sheets, 2 layers and 80 cm² of board". research.md, section 3, says that the figure "is not on
  the compare page of 2026-11-17". The two fixture boards fall under 80 cm² either way. The
  amplifier board is 59.4 x 72.0 mm = 42.8 cm². The motor board is 77.6 x 72.0 mm = 55.9 cm². The e-paper board of P1089
  is 126.4 x 72.0 mm = 91.0 cm². · E · `board_components.place` run on the records with `PYTHONPATH=scripts`. ·
  supports only: today's first-draft layouts.

- **TL-18** · The smallest first slice that runs end to end on a real spark board. It is a proposal, and the decider
  decides. The board is the amplifier fixture (`tests/data/breadboard/amplifier/requirements.json`: firebeetle2-esp32s3,
  max98357a-dfr0954, speaker-terminal). All three records hold an outline. The FireBeetle record also holds a thickness
  and four mounting holes as numbers. The slice has five steps. (1) A height fact for the three records (see PHY-1 for
  what is missing), and the module's mount: socket or soldered (PHY-2). (2) P1185 #1729's box, emitted as a jscad
  `cadModel` for each part and for `Mcu`. (3) P1183 #1727's `export-board`, which runs `tsci export -f step` and `-f glb`
  on `dist/board/circuit.json` and checks every model first (TL-8). (4) The case, from the solver called direct. Its
  `topHeadroom` is the tallest fact plus a clearance. STL files of the base and the lid come from it (TL-6, TL-7). (5) The PO
  imports the STEP into Fusion and prints the base. tscircuit's enclosure element is not needed inside `board.tsx`.
  A smaller cut is steps 1 to 3 only: a named STEP and a GLB, with no case. · E for the pieces (TL-1, TL-6, TL-7,
  TL-8). Putting them together on the real fixture is H: it did not run.

### Physics: the mechanical numbers

- **PHY-1** · The numbers that a case needs, where each one is today, and its origin. A record states a fact as
  `{value, verified, source}` (`provenance.py:13`). It has no field for the kind of origin. "Datasheet", "drawing",
  "calliper" or "Wokwi drawing" appear only in the words of `source` or in a note. So a reader cannot tell a typical
  value from a maximum, or a datasheet value from a measured one, without reading the prose. · E · the survey below,
  run with a script over `parts/*.json`, `boards/*.json` and the store's `catalog/*.json`.

  | Number | Where it is today | Origin as written | Missing for |
  |---|---|---|---|
  | Carrier board outline | `board_components.place`: 59.4 x 72.0 mm for the amplifier | calculated, and "ordinal, not designed" (`board_components.py:13`) | none (but it is a first draft) |
  | Carrier thickness | `data/fabrication.json:21`, 1.6 mm | stated (spark's process default) | none |
  | A module's PCB thickness | FireBeetle `physical.thickness_mm` 1.6 · DFR0821 `facts.pcb_thickness_mm` 1.0 · VL6180X 1.02 and MAX98357A 1.6 in note prose | datasheet drawings (DFR0821's read off an image, `verified: false`) | XIAO ("Not stated in any source read"), DFR0534, L9110S and the other modules |
  | Height above the board | structured: MKDS `facts.height_mm` 17.3 · DFR0205 `facts.thickness_mm` 20.0 · DC-005 and PJ-002A `barrel_axis_height_mm` 6.5. In prose: MAX98357A "7.1 mm total height including the JST socket". VL6180X "1.2 mm of parts above it". LED "8.6 mm above the lead exit". DC jacks 11. WJ500V 14.0. Tactile button "4.3, 5, 8 or 12 mm", with `cap_height_mm` null | datasheet or seller drawings. MKDS and DFR0205 are `verified: true`, the jack axes `false` | FireBeetle: "NOT stated by DFRobot". About 7 mm comes from a STEP with a camera, and it is not recorded. Also XIAO · DFR0534 ("NOT published") · L9110S · JST PH |
  | Connector overhang past the edge | PJ-002A "3.50 is the overhanging lip" (prose) · XIAO 23.4 - 21.0 = 2.4 mm | datasheet · arithmetic on Wokwi's drawing, "not a Seeed fact" | FireBeetle: the outline is "the PCB only, not the USB-C overhang" (`part_shape.py:8`) |
  | Opening size and place | DC-005 "Ø6.4 opening" (prose). The feature schema has the kinds `usb`, `jst`, `button` and `hole` (`record_kind.py:361`), but no record uses `physical.features` | seller drawing | every USB-C, micro-USB, JST and button position |
  | Mount holes | FireBeetle 4 x Ø2.0, inset 1.7, spacing 22.0 x 56.6, as numbers. DFR0534 "2 holes, 15.00 mm apart, both 3.50 mm in", as words, verified. DFR0821 "2 x Ø2.00 mm ... 15.00 mm apart", as words, unverified. DFR0469 15 mm apart, with no diameter. VL6180X "two 2.2 mm" in prose. MAX98357A "NO MOUNTING HOLES". | vendor drawings | the carrier itself: spark emits no holes ("Not decided here ... mounting holes", `board_sections.py:126`) |
  | How a module sits on the carrier (socket or soldered) | nowhere: `grep` for female header, pin socket and standoff finds no fact | — | every module |
  | Parts under a module | DFR0821: the cell holder "is on the reverse (inferred)" (prose) | inferred | all others |
  | Wall, clearance and fit for an FDM print | none in spark. tscircuit's defaults: wall 2, `boardClearance` 1, standoff 4, `topHeadroom` 6, lid 2, lip 4, `slidingFitClearance` 0.3 | stated by the tool (`create-fdm-enclosure/dist/index.js:722` to 732) | the PO's printer, nozzle and material: — |

  The pre-analysis counts "1 of 30" records with a z-height and "1 of 30" with mounting holes as numbers. This survey
  finds 6 records with a z number under a structured key: FireBeetle, DFR0821, DFR0205, MKDS, DC-005 and PJ-002A. At
  least 8 more hold a z number in prose. It finds 4 records with mounting holes as a fact: 1 as numbers and 3 as words.
  "1 of 30" holds only for one key name, read strictly.

- **PHY-2** · tscircuit's default case does not clear spark's boards. Its `topHeadroom` is counted "from the PCB top
  surface", and "parts without apertures do not report an envelope" (`create-fdm-enclosure` README, "Enclosure sizing
  and defaults", and `@tscircuit/props` `EnclosureFdmBoxProps`). In the probe, the module's top is at z 11.42. The
  lid's underside is at 8.70 - 2 = 6.70. So the module goes 4.72 mm into the lid. For the amplifier board, this is the arithmetic
  (FireBeetle at about 7 mm of parts, the unrecorded value of TL-12):
  height = mount + module PCB + parts. The default cavity is 6.0 mm above the carrier.
  On an 8.5 mm female socket (H, a common size): FireBeetle 8.5 + 1.6 + 7.0 = 17.1 mm, and MAX98357A 8.5 + 7.1 = 15.6 mm.
  The lid then sits 11.1 mm into the FireBeetle. The case needs a depth of 2 + 4 + 1.6 + 17.1 + 1 + 2
  = 27.7 mm, not 15.6 mm. Soldered with a 2.5 mm pin spacer (H): 11.1 mm and 9.6 mm, so the lid sits 5.1 mm into the FireBeetle, and the
  depth is 21.7 mm. A direct solver call with `topHeadroom` 18.1 gave a depth of 27.7 mm, which matches. · E for the
  probe and the solver call, the arithmetic in a Python run. H for the socket and spacer heights and the 7 mm. ·
  supports only: that the case needs the tallest height and the mount. Which mount the PO uses is a question.

- **PHY-3** · Two fact names already mean two things each. `height` means the second dimension in the board's plane in
  `body_mm.height` and `physical.height_mm`, and the height above the board in MKDS's `facts.height_mm`. `thickness_mm`
  means the PCB's thickness in the FireBeetle's `physical`, and the whole module's height (20 mm) in DFR0205's `facts`.
  A new z fact needs one name for "the height above the board surface" and one for "the PCB thickness". It also needs a
  rule that moves the existing keys. · E · the survey of PHY-1.

- **PHY-4** · An edge connector sits inboard of the carrier's edge. `MARGIN_MM = 6` (`board_components.py:15`) puts the
  FireBeetle's USB end (72.0 / 2) - (60.0 / 2) = 6.0 mm in from the carrier's edge. Through the 1 mm clearance and the
  2 mm wall, the receptacle is 9.0 mm in from the case's outer face. A plug can reach it only through an opening wider
  than the cable's overmold, and the overmold's size depends on the cable (—). The layout, not the case, moves the
  connector to the edge. That is the layout core P1199 #1747's job. · E for the arithmetic and the constant. H for the
  plug.

- **PHY-5** · Nothing holds the board in the case. The carrier has no mounting holes (PHY-1), and create-fdm-enclosure
  0.0.4 has no bosses: "Mounting bosses, inserts, fasteners ... remain future work" (its README). The default 4 mm
  standoff leaves the carrier resting on its lead tails, with 1 mm of play on each side. · E for the README and the
  emitter. H for how the board rests.

- **PHY-6** · The FDM numbers, done with arithmetic. A 2 mm wall is 2 / 0.4 = 5 lines with a 0.4 mm nozzle. A 1 mm
  board clearance covers Pololu's stated ±0.3 mm board-edge tolerance (VL6180X `body_mm.source`). A shrink of 0.2 to
  0.5 % over the 78 mm case is 0.16 to 0.39 mm. The lid lip's 0.3 mm sliding fit is the tool's default and is not tied
  to the PO's printer. · E for the arithmetic and the defaults. H for the nozzle size and the shrink rates. The printer,
  nozzle and material are — (PrusaSlicer is installed, pre-analysis section 3).

- **PHY-7** · The cheapest rung for each open physical question, and what it cannot show.

  | Open question | Cheapest rung | What it cannot show |
  |---|---|---|
  | The height above the board, the PCB thickness and the USB-C overhang of each owned module (FireBeetle, XIAO, DFR0534, L9110S, JST PH) | a calliper on the parts in the PO's drawer, about 15 minutes. The fact becomes "measured". | another unit or another board revision |
  | Socket or soldered, and the socket's height | a calliper on the socket he uses, and his answer | — |
  | The opening for his USB-C cable | a calliper on the cable's overmold | another cable |
  | The lip fit (0.3 mm) and the board clearance (1 mm) | a test print of a low ring: the bottom 3 to 5 mm of the base wall with the lip, and the real board dropped in | the full height, warping of a large lid, and the fit after weeks of use |
  | Whether the case clears the tallest part | the STEP of TL-18 opened in Fusion (a section view), before any print | a wrong fact about the real part |
  | Whether Fusion keeps the names | importing the three STEP files (tscircuit with a jscad body, KiCad's assembly, one written by spark) and a screenshot of the browser tree | the Fusion MCP path and other licence limits |

- **PHY-8** · The two engines place one STEP body nearly the same way. tscircuit puts the model's z = 0 on the board's
  top face: the module PCB's bottom is at z 9.20, with the board's top at 0.70, so 8.50 mm up, as written. kicad-cli
  puts the same file 1.59 to 1.60 mm above the bottom of KiCad's board solid, whose top reads 1.51. That is about
  0.08 mm apart, well under the FDM tolerances of PHY-6. · E · `node bounds.cjs` on `v_step.step` and `kz_step.step`. ·
  supports only: one part with no rotation.

## What I could not check, and why

- No file was opened in Fusion 360, and no Fusion MCP server ran. The brief says the server is not connected, and
  turning it on is the PO's.
- Nothing was printed or measured. That needs the PO's printer and callipers.
- No real spark board was built with a body on each part. So the build time with jscad plans inline in `board.tsx` is
  not measured, and a real build can take up to 496 s (`board_engine.py:23`).
- No STEP file per placed part, with the reference in its names, was tried (TL-3).
- No `rotationOffset` for an STL body was tried, and no newer tsci was tried. Installing one is not allowed here.
- PrusaSlicer was not run on the STL files of TL-7, so whether it repairs the open edges is unknown.
- The FireBeetle STEP named in the record: its URL and its licence. The record names neither, and a second search does
  not settle a licence.
- build123d was not installed, so its size on disk is unknown.
- `@tscircuit/3d-viewer` and a one-page viewer were not tried.
- The terms of the model sites in research.md, section 6, were not read.
- `part_facts.py` was not read line by line, so the `sourcing` row of TL-13 is H.

## Questions for the decider

- How do you mount a module on a PCB or a perfboard: in female sockets, or soldered straight in? And how tall is the
  socket you use? · decides the case's depth (PHY-2: 27.7 or 21.7 mm on the amplifier board) and a new fact for each
  module.
- Which body comes first? One choice is a jscad body inside `board.tsx`: tscircuit's STEP names it `U1`, and KiCad gets
  no body. The other is a STEP file that spark writes for each placed part: both engines get a body. To carry the name, spark
  must write it into the file. ·
  decides the shape of P1185 #1729 and which engine's STEP goes to Fusion.
- Do you accept a case made after the build, from the solver and a copy of `circuit.json`? Then `board.tsx` and the
  build stay as they are. The other way is tscircuit's `<enclosure.fdm.box>` inside the board file. · decides whether the
  build file changes, and whether a case needs a new build.
- Is the amplifier fixture the real board of the first slice? Will you import three STEP files into your Fusion and send
  a screenshot of the browser tree? · decides the riskiest open question, the names in Fusion (TL-16), and the slice's
  board.
- Do you want one name for "height above the board" and one for "PCB thickness", with the existing keys moved
  (PHY-3)? ·
  decides the records' schema before the first height fact lands.
- Must a print file have no open edges, or is the slicer's repair enough? · decides how much the STL writer of TL-7 must
  do.

## Searches

- "Fusion 360 STEP import solid body names preserved MANIFOLD_SOLID_BREP single product multiple bodies" · served: the choice
  between tscircuit's flat STEP and an assembly from KiCad or spark. It turns on whether Fusion keeps each part's name ·
  used, as H in TL-16 (forum reports only, nothing on the entity itself). Sources:
  [step-file-import-renames-bodies](https://forums.autodesk.com/t5/fusion-support-forum/step-file-import-renames-bodies/td-p/11324521),
  [Imported assembly file structure has bodies vs components](https://forums.autodesk.com/t5/fusion-support-forum/imported-assembly-file-structure-has-bodies-vs-components/m-p/12726217),
  [When exporting to STEP file, all Body names and Folders are lost](https://forums.autodesk.com/t5/fusion-support-forum/when-exporting-to-step-file-all-body-names-and-folders-are-lost/td-p/10758938).
