# P1197 pre-analysis: what spark holds for 3D today

Card P1197 [#1745](https://github.com/xmejkal/spark/issues/1745). Read on 2026-11-26 at commit d14acce2, branch
p1197-3d, and in the person's store (`~/.local/share/spark`). The probe ran in a scratch folder at 15:14 CET. No
probe file is kept in the repository.

> In short: spark holds a 2D outline for 34 of 40 records and a body's height above the board for 3, as a field. No record holds a 3D model.
> spark already installs tscircuit 0.0.2600. It takes a body per part and exports STEP and GLB. A body it generates
> keeps the part's reference as its name, and a STEP body does not. It also draws a two-part printed case
> (`enclosure.fdm.box`).
> The gaps are spark's: no height fact, no model per record, no place to keep a fetched model, and no Operation for
> 3D. Nothing ran in Fusion yet.

## 1. The records

The count covers every record with pins, a kind or a `physical` block: 12 in the repository (`parts/`, `boards/`,
`chips/`), and 31 in the store's `catalog/`, `boards/`, `known-boards/` and `shelf/`. 13 of the 31 are on the shelf.
Drawer rows (what a person owns) are not part records and are not counted. The first count missed the shelf. The
architecture lens found it (council/architecture.md, AR-3), and this table is the recount.

| Fact | Records | Pointer |
|---|---|---|
| An outline, `body_mm.width` and `body_mm.height` (both in the board plane) | 30 of 43 | survey script, E |
| A z number, under six different keys | 8 of 43. The board's thickness (`physical.thickness_mm` 1.6 in both FireBeetle 2 boards, `facts.pcb_thickness_mm` 1.0), a body's overall height (`facts.thickness_mm` 20 in DFR0205 and 5.5 in DFR0831, `facts.height_mm` 17.3 in the MKDS terminal) and a jack's axis height (`facts.barrel_axis_height_mm` 6.5, twice) | key scan, E |
| A body's overall height above the board | 3 of 43 (DFR0205, DFR0831, MKDS). `thickness_mm` means the bare board in two records and the overall height in two others. `physical.height_mm` is a plane size (60 mm for the FireBeetle's length) | key scan, E, and council/user.md US-15 |
| A `mounting_holes` block | 8 of 43, for example the FireBeetle 2 S3 (4 holes, 2.0 mm, inset 1.7 mm) | survey, E |
| A `physical.header` block (the pin row's place) | 3 of 43 | survey, E |
| A 3D model, a model URL or a photo field | 0 of 43 | survey, E |

The word "height" in `body_mm` is the second plane dimension, not the height above the board. The DFR0534 record
says so in its note: "Thickness and component height are NOT published by DFRobot ... measure them before designing
an enclosure" (`parts/dfr0534-module.json`, `body_mm.note`). A record with no outline gets the placeholder 16 x 12 mm
(`DEFAULT_BODY_MM`, `scripts/spark/design/board_components.py:17`).

The store's `sources/` folder holds 153 kept sources. 47 files in it are pictures, and 20 of these are dimension
drawings by file name (for example `DFR1025_Dim_02.jpg`). There is one photo of an owned board
(`boards/photos/xiao-esp32-c6-front-2026-10-14.jpg`). The store holds no STEP file of a part.

## 2. The code

- A module goes to the board as `<chip footprint="pinrowN">` with no `cadModel`
  (`scripts/spark/design/board_sections.py:259`). This is F4 of the P1089 finding, card P1185 #1729.
- The 2D drawing of a part is a Strategy family: `ShapeSource` with `WokwiGeometryShapeSource`, `RecordShapeSource`
  and `ModuleShapeSource` (`scripts/spark/breadboard/part_shape.py:61` to 263).
- A part's picture comes from a chain of exchangeable makers, `PartPictureMaker` (P946). Each maker says what it uses
  (`MakerUses`: tools, inputs, a cost, whether it asks first) and gives a candidate or a `Decline`
  (`scripts/spark/breadboard/picture_makers.py:1-60`). This is the closest template for a 3D body source.
- The tools list maps a role to a tool (`data/tools.json`, `roles`): 14 roles today, among them `board-engine` →
  `tscircuit`. No role exists for a 3D job.
- The Operation catalogue (`scripts/spark/operation_catalogue.py`) lists 8 area tables. No Operation exports or shows
  3D. The Operation `export-board` is a card, P1183 #1727, not code.
- The perfboard is a journey step with a name and a sentence (`scripts/spark/flow/flow_codes.py:479`). It has no
  layout and no drawing. A perfboard in 3D has nothing to start from.
- The setting layers come from P1194 #1740: spark's default, yours (the store), this project, and an empty account
  slot (`docs/discovery/2026-11-26-p1194-settings/brief.md`, Q2).

## 3. The toolchain spark already installs

The store's toolchain (`toolchain/package.json`) pins `@tscircuit/cli` 0.1.2113 and `tscircuit` 0.0.2600, the
versions in `data/tools.json`. Its `node_modules` already holds these 3D packages:

| Package | Version | Licence (its package.json or LICENSE) | What it does |
|---|---|---|---|
| `@tscircuit/create-fdm-enclosure` | 0.0.4 | MIT | "Generate FDM enclosure geometry from board dimensions and wall apertures": a base and a lid with a friction lip, cut-outs per part. Its README says mounting bosses and full body clearance are "future work". |
| `@tscircuit/modelprinter` | 0.0.2 | MIT | parametric model strings, like footprint strings ("experimental", with one model today, `flexscreen`) |
| `circuit-json-to-gltf` | 0.0.128 | MIT (LICENSE file) | the board and parts as GLTF or GLB |
| `occt-import-js` | 0.0.23 | LGPL-2.1 | reads STEP in Node or a browser |
| `three` | 0.179.1 | MIT (H: not read in the folder) | the 3D library under the viewers |
| `@tscircuit/simple-3d-svg` | 0.0.41 | none in package.json | a small 3D-to-SVG renderer |

`tsci export -f` lists `gltf`, `glb`, `step`, `kicad_zip` and `component-box-3mf` (E, `tsci export --help`).

Also on this Mac (E, `/Applications` and `which`): KiCad with `kicad-cli` 10.0.6, Autodesk Fusion 360 (its
`Application Support` folder exists), and PrusaSlicer. FreeCAD and OpenSCAD are not installed.

## 4. The probe

A 50 x 36 mm board with a 10-pin module and a 4-pin header, in four variants, exported with
`tsci export <file> -f <format> --disable-parts-engine`. The probe needed its own `package.json` and a link to the
toolchain's `node_modules`, as spark's build does (`scripts/spark/build/board_engine.py:46`).

| Variant | GLB | STEP | What the STEP holds (read with `occt-import-js` and grep) |
|---|---|---|---|
| plain, no model | 254 KB, ran | 1054 KB, ran | one product "PCB", with solids named `PCB`, `U1`, `U2` (the generic header bodies) |
| with `<enclosure.fdm.box>` | 263 KB, ran | 1142 KB, ran | as plain, plus two solids `unnamed_enclosure_fdm_box_1`, 56 x 42 x 15.4 mm (brief ★C5) |
| module with a local `stepUrl` | 198 KB, ran | 318 KB, ran | the local STEP body is merged as a solid on the board top (z from 1.4 mm) |
| module with a local `stlUrl` | failed: "RangeError: Out of bounds access". A later run with an absolute path ran (brief ★C3) | 315 KB, ran | the STL lands as loose faces, z from -5.3 to 0.7 mm: through the board, not on it |

Other results:

- `component-box-3mf` failed: `ENOENT ... @tscircuit/cli/dist/cli/manifold.wasm`. The installed CLI lacks the file.
- `kicad_zip` ran. Its board file has a `(model ...)` line only for the plain header
  (`${KIPRJMOD}/3dmodels/tscircuit_builtin.3dshapes/pinrow4.step`). The module with the STL body got no model line.
- `kicad-cli pcb export step --subst-models` on that board ran in 4.1 s. It is an assembly. The instance with a
  model is named `U2`, its product is named after the model (`pinrow4`), and the board is `board_PCB`.
- `kicad-cli pcb export glb` ran: 109 KB.

So a STEP body reaches both engines today. It loses the part's reference in tscircuit's STEP (council/tech-lead.md
TL-2), and a JSCAD body keeps the name but replaces the header's own body (brief ★C33). These are single runs on one
probe board: they show that a path works, not how often it works.

## 5. What did not run

- No file was opened in Fusion 360. Whether Fusion keeps the solid names `U1` and `U2` is unknown.
- No real spark board was exported with a body per module. P1185 #1729 makes the box.
- No GLB was opened in a browser viewer.
- The enclosure was not printed and not measured against the board.
- No model was fetched from a library.
