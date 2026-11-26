# P1197 research: reuse first, with licences

Three research agents on Opus read the sources on 2026-11-26, with one or two searches per question. Each line keeps
its tag: E is a page or a file that was read, with its pointer, and H is a belief with its source. The probe of
[pre-analysis.md](pre-analysis.md), section 4, measured the tscircuit and KiCad rows on this Mac. Nothing was
downloaded, bought or installed.

> In short: the models come from two places. A shape that spark generates from the record's numbers is spark's own
> and free to keep. A vendor or library model is CC-BY-SA or private-use, so spark fetches it at use time into the
> person's store and never commits it.
> STEP is the one format that every engine and Fusion take. tscircuit already exports it and already draws a printed
> case. Fusion's personal licence keeps STEP export, scripts and a local MCP server. Its electronics limits concern
> Fusion Electronics designs, and the old "80 cm²" figure is not on Autodesk's page today.

## 1. Where a model comes from

| Source | What it gives | Licence, as written | In spark's MIT repo | Pointer |
|---|---|---|---|---|
| KiCad packages3D | STEP and WRL. ESP32 modules (WROOM, C3, S3), the Pico, a WEMOS D1 mini. No dev board such as the DevKitC | "Creative Commons CC-BY-SA 4.0 License" with a design exception | no: fetch at use | E https://www.kicad.org/libraries/license/ |
| Espressif kicad-libraries | about 47 module STEP files, no dev board | CC-BY-SA 4.0 with the same exception | no: fetch at use | E https://github.com/espressif/kicad-libraries |
| Adafruit_CAD_Parts | STEP, Fusion and STL of Adafruit boards | "MIT License" | allowed, but a vendor file, so fetch | E https://github.com/adafruit/Adafruit_CAD_Parts |
| SparkFun 3d_models | STEP and STL of some products, last push 2023-10 | CC BY-SA 4.0 | no | E https://github.com/sparkfun/3d_models |
| Seeed, DFRobot, Waveshare | a few STEP files (DFRobot per wiki page, Seeed 4 files) | not found | unclear, treat as no | E search results only |
| SnapEDA, GrabCAD | vendor parts | SnapEDA: CC BY-SA with a 10-file limit per place. GrabCAD: "generally for private use" | no | E https://www.snapeda.com/about/terms/, E https://help.grabcad.com/article/246 |
| EasyEDA/LCSC (through easyeda2kicad, AGPL-3.0) | STEP of LCSC parts | the service terms: a "personal, revocable, limited license" | no | H, search snippet |
| tscircuit jscad-electronics | parametric chip and header shapes | MIT | yes | E gh api |

A shape from the record's numbers: build123d (Apache-2.0) writes STEP with each shape's label as its name, and GLB,
STL and 3MF. It runs headless and needs `cadquery-ocp-novtk`, a 62.5 MB wheel (E, PyPI). CadQuery (Apache) does the
same with vtk, a 103 MB wheel more (E, PyPI). OpenSCAD and JSCAD write meshes only, no STEP (E for JSCAD io, H for
OpenSCAD). KiCad's own model generator is GPL-3.0 (E). tscircuit's `jscad` cadModel is already in the installed
toolchain (pre-analysis section 3).

A model from photos: a box with the photo as its top face gives the exact outline and height from measurements (H,
the agent's judgement). Photogrammetry handles thin, shiny boards badly, and one-image AI models (TripoSR and
TRELLIS, both MIT) have no metric scale (H). Hunyuan3D-2's licence "DOES NOT APPLY IN THE EUROPEAN UNION" (E, its
LICENSE), so the PO in Czechia cannot use it. Meshy is paid: Pro is Kč 420 a month at list price (E,
https://www.meshy.ai/pricing). Its free tier publishes outputs under CC BY 4.0.

Where models are kept elsewhere: KiCad uses path variables (`KICAD9_3DMODEL_DIR`, `KIPRJMOD`). It can also embed a
model in the board file as `kicad-embed://` (E, https://docs.kicad.org/9.0/en/kicad/kicad.html). tscircuit takes a URL or
a local import (E, https://docs.tscircuit.com/elements/cadmodel). No tool found keeps a per-user cache keyed by URL
and sha256. spark's store already keeps sources that way (`sources/<sha256>/`).

## 2. How each engine takes a model

tscircuit: a chip's `cadModel` takes one model file or shape: `stlUrl`, `objUrl`, `gltfUrl`, `glbUrl`, `stepUrl`,
`wrlUrl` or `jscad`. Keys such as `size`, `positionOffset`, `rotationOffset` and `zOffsetFromSurface` place it (E,
installed `@tscircuit/props` types and https://github.com/tscircuit/props, `lib/common/cadModel.ts`). Its STEP
export reads a local STEP file from the working folder (E, cli `load-local-step-model-fs-map.ts`). The probe
measured that a local STEP body merges and an STL body does not (pre-analysis section 4). Its KiCad export writes the
`(model ...)` line from `stepUrl` or `wrlUrl` only (E, circuit-json-to-kicad source).

KiCad: the footprint's `(model "${KICAD10_3DMODEL_DIR}/....step" (offset ...) (scale ...) (rotate ...))` (E, a
KiCad 10 library footprint). kicad-cli 9 exports step, brep, xao, glb, vrml, stl and ply, and version 10 adds stpz,
u3d and 3dpdf (E, https://docs.kicad.org/9.0/en/cli/cli.html and the 10.0 source). Each placed part is named by its
reference (E, `step_pcb_model.cpp`). The probe saw the name `U2` on the one part that had a model.

So one fact per record, a STEP body placed by its offset and rotation, feeds both engines. The record gives the
numbers and the store gives the file.

## 3. Fusion 360

| Question | Answer | Pointer |
|---|---|---|
| Personal licence: STEP export | allowed: "continue to allow STEP export for personal, non-commercial users", with STL. 10 active documents. | E Autodesk blog of 2020-09-25, Wayback copy of 2026-08-15 |
| Personal licence: electronics | "2 sheets per schematic", "4 signal layers", board area "Unlimited". The compare page ticks no "File export" and no "Work with non-native data" for personal use. | E Wayback copy of the compare page, 2026-11-17 |
| Does the electronics limit touch a STEP import? | no source ties it to mechanical bodies | H, no source says otherwise |
| Scripts and add-ins on the personal licence | "you still have access to scripts and add-ins" | E the same 2020 blog |
| Official MCP server | built into Fusion: Preferences > General > API > "Fusion MCP Server (runs locally on this device)", at `http://127.0.0.1:27182/mcp`, "only available while Fusion is open". The page names no licence tier. | E help.autodesk.com, ADSKMCP-FusionDesktopMcp |
| Community MCP servers | faust-machines/fusion360-mcp-server (MIT, an add-in on a local socket), JustusBraitinger (MIT) | E their GitHub pages |
| A CLI or a headless mode | none supported | H, forum snippets (forum returned 403) |
| STEP import | component names survive, and body names become "Body 1" in some reports | H, forum snippets |
| KiCad import | "KiCad v7 files or higher", the page names no tier | E help.autodesk.com, ECD-KICAD-IMPORTER |

autodesk.com returned HTTP 403 to every direct read, so each Autodesk line comes from a Wayback copy or the help site.
The compare page's missing "File export" tick and the 2020 blog's STEP line do not agree. Only a run on the PO's
Fusion settles it. The P1089 finding's "2 layers, 80 cm²" figure is not on the compare page of 2026-11-17.

## 4. A case, a viewer and print files

| Job | Best fit found | Licence | Pointer |
|---|---|---|---|
| A case from the board, already installed | tscircuit `<enclosure.fdm.box>` (create-fdm-enclosure 0.0.4): base and lid with a lip, cut-outs per part. No bosses yet. | MIT | E installed README, probe |
| A case from a `.kicad_pcb` | TurboCase: posts at `MountingHole` footprints, cut-outs from the F.Fab box and a `Height` property, writes OpenSCAD | MIT | E https://codeberg.org/MartijnBraam/TurboCase |
| A parametric box to learn from | YAPP_Box v3 (OpenSCAD), CadQuery's "Parametric Enclosure" example | MIT, Apache | E github, cadquery docs |
| Not reusable | PCBCase (GPL v3), Ultimate Box Maker (CC BY-NC), keeb_snakeskin (AGPL-3.0), SBC_Case_Builder (GPLv3) | | E or H |
| A CAD tool Claude drives | build123d. For an MCP server: build123d-mcp (Apache-2.0) | Apache-2.0 | E github |
| Heavier CAD | FreeCAD 1.1.4 (LGPL-2.1, a 650 MB dmg), OpenSCAD (GPL, 28.8 MB, meshes only) | | E |
| A viewer on one HTML page | three.js with GLTFLoader and a base64 GLB | MIT | H for the one-page claim |
| tscircuit's viewer | `@tscircuit/3d-viewer` (React `CadViewer`, takes circuit.json or GLB data) | MIT | E npm, needs a bundle step (H) |
| STEP in a browser | occt-import-js, a 7.6 MB wasm | LGPL-2.1 | E jsDelivr |
| Print files | STL and 3MF in mm, one body per printed part. Slicers (PrusaSlicer, OrcaSlicer, Bambu Studio, CuraEngine) are all AGPL-3.0. | | E gh api |

The agent's advice is to stop at STL and 3MF and leave slicing to the person's slicer, which holds the printer
profile (H). PrusaSlicer is installed on this Mac (E, `/Applications`).

## 5. Related ideas found on the way

- kicad-cli writes a raytraced PNG (`pcb render`) and GLB. The P1089 finding used the render.
- Pogo-pin test fixtures are generated from a board (OpenFixture, pogojig, pcb-jigify). They are a printed jig, the
  same idea as P1198's flat sculpture jig.
- No 3D model or generator for a perfboard or a stripboard was found. A perfboard is a box with a hole grid, which a
  shape generator makes from its pitch and size.

## 6. Not checked

- Whether the official Fusion MCP server runs on the personal licence, and which export formats that licence allows
  today beyond the 2020 statements.
- Whether Fusion keeps the solid names `U1` and `U2` from tscircuit's STEP, or the instance names from KiCad's STEP.
- The terms of Ultra Librarian, Component Search Engine, grabcad.com/terms, EasyEDA and modelcdn.tscircuit.com.
- The installed size of build123d, measured. The PyPI wheel sizes are download sizes.
- Whether the newer tsci (cli issue #5654, closed 2026-11-20) fixes the GLB failure with an STL body.
- Whether a viewer runs from one page with no network.
