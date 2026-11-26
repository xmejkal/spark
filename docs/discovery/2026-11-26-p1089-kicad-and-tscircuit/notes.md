# P1089 spike notes: what the runs showed

The raw evidence for the finding, written by the kicad-spike session on 2026-11-26, 06:57 to 07:35 CET. Every run
was in a scratch copy under the session's job folder. Nothing in a project folder or in the store changed. The
architect wrote `finding.md` from these notes.

## Setup

- Boards read: the `dist/board/circuit.json` of 13 projects. These are the walks p934-epaper, p934-display2,
  reaction-game, walk4, t-display, p711-sound-demo, p711-identify-amp and p581-sound-joystick. The others are
  button-light, spark-quickstart, rc-car/car, smartbin-local and irrigation. The main board is the walk's FireBeetle 2
  ESP32-C6 with the 2.9 in e-paper (`spark-walks/p934-epaper`, built 2026-11-22 06:30).
- Toolchain: the project pin is `@tscircuit/cli` 0.1.2113 and `tscircuit` 0.0.2600. They resolve to
  `@tscircuit/core` 0.0.1946, `@tscircuit/capacity-autorouter` 0.0.913, `@tscircuit/checks` 0.0.204 and
  `@tscircuit/copper-pour-solver` 0.0.54. The store's toolchain (`~/.local/share/spark/toolchain`) resolves to the
  same versions. The runtimes are bun 1.4.2 and node 22.23.2.
- Views in Chrome: `tsci dev board.tsx` on port 3091 (PCB, schematic and 3D tabs), and the built SVGs through a
  local page. KiCad: kicad-cli 10.0.6 and KiCad's bundled Python 3.9 with `pcbnew`.
- Scripts in the job folder, not in the repository: `survey.py` and `survey_all.py` count from circuit.json.
  `tosvg.mjs` draws with circuit-to-svg and does not route again. `refill.py` uses pcbnew.

## Question 1: what is wrong with today's boards

The counts come from `survey_all.py` over the 13 boards. The pictures come from Chrome.

| # | Fault | Seen on | Cause | Evidence |
|---|---|---|---|---|
| F1 | The copper pour splits the board into V33 and GND regions on both layers. The borders are staircases that run to the board edge, and they look like traces to nowhere. | 10 of the 11 boards with pours. smartbin-local is written by hand and pours GND only. | spark turns it on with `automaticPoursEnabled` on every board (`scripts/spark/design/board_sections.py:138`). tscircuit's implicit pour gives every free grid cell on every layer to a power net. It then traces the cells into polygons and simplifies the edges by the grid pitch. Source: `@tscircuit/core` 0.0.1946, `dist/index.js` lines 52294 to 52345 (`ImplicitCopperPourPipelineSolver`) and 68859 to 68905 (`Board_doInitialPcbImplicitCopperPourRender`). | e-paper top layer: V33 4843 mm², GND 3987 mm² in 133 pieces, 23 of them under 1 mm². Bottom: GND in 34 pieces. p711-sound-demo: 226 pour pieces. Picture: `pcb-today-automatic-pour.png`. |
| F2 | The pour leaves islands and runs close to the board edge. | e-paper, read by KiCad | tscircuit's implicit pour, as in F1. | `kicad-cli pcb drc` on tsci's KiCad export gives 396 findings. 199 are isolated copper. 128 are zones that intersect, because the export writes each of the 127 pour pieces as its own zone at priority 0. 54 are copper at 0.2 mm from the edge, under KiCad's default of 0.5 mm. 4 are slivers. |
| F3 | The false pour short of P958: a `pcb_placement_error` says that GND pour 39 shorts to the MOSI trace on top. | the 11-22 e-paper build and p934-display2 | tscircuit's checks on the implicit pour, reported upstream at https://github.com/tscircuit/checks/issues/588. It depends on the route. Fresh builds of the same version on 2026-11-26 do not report it. spark's `pour_contact.py` drops it today. | rep1, rep2 and spark's own build today: 0 errors. |
| F4 | The modules' bodies are missing on the PCB and in 3D. The FireBeetle shows pads and a silkscreen box. The 2.9 in e-paper shows only an 8-pin header and no panel. | every board: the components with a 3D model are one fewer than the components | spark's board file. The module footprint has no `cadModel` (`footprint_emitter.py`). A module is a `<chip footprint="pinrowN">` (`board_sections.py:259`), so its body never reaches the PCB. tscircuit warns `pcb_component_missing_courtyard_warning` on every board. | The 3D tab in Chrome. The KiCad render `kicad-3d-render.png`. |
| F5 | Boards are large and mostly empty, with the modules in a column. The e-paper board is 126.4 x 72 mm for two parts. p711-sound-demo is 77.1 x 137.8 mm. | every generated board | spark's placement, `board_components.place` (`board_components.py:143` to 180). It puts the modules in a column. It sizes the board from their bodies, a 6 mm margin and a 4 mm gap. The board file says: "The PLACEMENT is a first draft and nothing more." | The board sizes in circuit.json. |
| F6 | Every trace is 0.15 mm wide, power traces too. | every generated board. rc-car and smartbin-local have wider traces from stated currents. | If no current is stated, spark gives no width (`trace_width_mm` in `board_sections.py`). The file says "UNJUSTIFIED". | The widths in circuit.json. |
| F7 | The schematic names nets by pin: "Mcu_pin4", "Mcu_pin29", "Mcu_pin12" instead of EPD_CS, EPD_BUSY and MOSI. Some labels overlap the pins of the MCU symbol. | every board has `source_unnamed_trace_warning`: 6 on the e-paper, 15 on p711-sound-demo | The names: spark writes each signal as a trace from pin to pin and keeps its name only in a comment (`board_sections.py:289` to 290). The overlap: tscircuit's schematic layout in core 0.0.1946. A more exact cause was not found. | The schematic tab in Chrome. KiCad's export also names each net after its trace, for example ".Mcu > .SCK to .Epaper2in9BwrMhEtLive > .SCLK". |
| F8 | Silkscreen text is 0.7 mm high. | e-paper, read by KiCad | tscircuit's default text size. | 9 `text_height` warnings under KiCad's default of 0.8 mm. |
| F9 | The generated FireBeetle footprint says "The holes are 1.00 mm, NOT the None mm on the vendor drawing." | p934-epaper, `FireBeetle2Esp32C6.tsx` line 3 | spark: `footprint_emitter.py:287` prints a `drill_mm` that the record holds as null. | The file. |
| F10 | The project's `FireBeetle2Esp32C6.tsx` is older than the footprint that its last build used. So `tsci dev` in the project shows another board than `dist/`. | p934-epaper | spark's `--keep` leaves another `.tsx` alone and names it, as `check_spine.py --help` says. | Pad rows: in dist, 14 on the left and 18 on the right. In the project file, 18 on the left and 14 on the right (before P956). |
| F11 | walk4 and p581-sound-joystick have `source_trace_not_connected_error` for `.Mcu > .MOSI` and `.MISO`. | two old dist folders, 11-01 and 11-07 | spark, and fixed by P512: the emitter reads `pad_aliases` through `board_pads.py`. The dist folders are older than the fix. | walk4 diary G29. |

Measured, and not a fault:

- Routing is short. On every board the longest trace is at most 1.4 times the straight line, and the mean is 1.04 to
  1.11.
- Routing repeats. Two fresh builds of the same `board.tsx` gave the same routes (sha1 51e0b27f95 both times). The
  11-22 build differs only because it used the newer footprint (F10).
- The routes are clean in KiCad. `refill.py` keeps tscircuit's routes and replaces its 127 pour pieces with one GND
  zone per layer, filled by KiCad with 0.3 mm clearance and islands removed. `kicad-cli pcb drc` then gives 11
  findings: 9 text heights, 2 library warnings, 0 errors and 0 unconnected items.
- Build time is not measured. The same build took 2 to 4 minutes while the browser routed and two builds ran
  together. Alone afterwards, it took 6 to 7 s. There is no claim on speed.

### The cheapest fix inside tscircuit, tried

The test removed `automaticPoursEnabled` from `board.tsx` and added `<copperpour connectsTo="net.GND" layer="top" />`
and the same line for `bottom`. `tsci build` gave 0 errors, 3 GND pour pieces (1 top, 2 bottom), 10 traces and 4
vias. Picture: `pcb-one-gnd-pour.png`. KiCad on its export gave 212 findings: 199 isolated copper, 2 copper to edge,
9 text heights and 2 library warnings. After `kicad-cli pcb drc --refill-zones` it gave the same 11 as above. So
tscircuit's own fill still leaves what KiCad calls isolated copper, and KiCad's refill removes it. 3V3 reaches the
e-paper by a trace in every build, with or without this change. The refuter found that the export's netclass
clearance is 0.1 mm, and that at 0.2 mm both boards give 6 clearance errors.

### The fair pair, after the council (07:45 to 07:48 CET, read from the clock)

The council's PO assistant found that the first two pictures used two footprints. `spk/` is spark's own build of
today, with today's footprint (14-pin row on the left). `spkgnd/` is the same board with one GND pour per layer.

- spk: 1 V33 and 37 GND pieces on top, 2 V33 and 25 GND on the bottom, 0 errors, 10 traces, 3 vias.
- spkgnd: 1 GND piece per layer, 0 errors, 10 traces, 2 vias. `tsci build` took 4.5 s.
- p711-sound-demo with its own `board.tsx`: the automatic pour gives 61 V33 and 165 GND pieces. One GND pour per layer
  gives 1 piece per layer. Both have 0 errors, 25 traces and 24 vias.
- `tsci export -f step` on spkgnd ran in about 2 s with no KiCad. It wrote 618 KB with one product named "PCB" and no
  module bodies.
- The two pictures in this folder are now spk and spkgnd.

## Question 2: KiCad

### What ran

- `tsci export board.tsx -f kicad_zip` wrote `board.kicad_pcb` (file version 20241229, generator
  circuit-json-to-kicad 0.0.1), `board.kicad_sch` (20250114), `board.kicad_pro` and one STEP model, the 8-pin header.
  tsci 0.1.2113 also exports `kicad_pcb`, `kicad_sch`, `kicad-library`, `specctra-dsn`, `step` and `glb`, as
  `tsci export --help` lists.
- kicad-cli 10.0.6 ran headless on the export:
  - `pcb drc`, also with `--refill-zones` and `--save-board`.
  - `sch erc`: 53 findings. 24 are off grid, 22 are pins not connected and 7 are library warnings.
  - `pcb render`: two PNG views in 8 s.
  - `pcb export svg`.
  - `pcb export step`: 0.5 s and 288 KB. Only the header has a body.
- KiCad's bundled Python (`pcbnew`) worked without the GUI. It removed zones, added zones and filled them. It wrote a
  Specctra DSN of the unrouted board (5190 bytes).

### What did not run

- Freerouting 2.6.0 (released 2026-11-25, GPL-3.0). Its macOS arm64 CLI build,
  `freerouting-cli-2.6.0-macos-arm64.tar.gz`, is 22,967,212 bytes. It was downloaded to scratch, and its sha256
  (3ddca951…f5e) matches the release's checksum file. The session's permission check refused to run the downloaded
  binary. It waits on the PO's yes. The DSN to route is ready.
- No KiCad MCP server was installed.

### Facts from sources

A research agent read these on 2026-11-26.

- KiCad MCP servers:
  - mixelpixx/KiCAD-MCP-Server: MIT, v2.9.0 on 2026-11-12, Python and TypeScript, Node 18+ and Python 3.11+. It works
    through KiCad's SWIG Python API and has an experimental IPC backend. Its tools place, route, autoroute through
    Freerouting "via Java/Docker", run DRC and export (docs/TOOL_INVENTORY.md lines 92 to 145 and 437).
  - oaslananka/kicad-mcp-pro: AGPL-3.0, release on 2026-11-25.
  - claynicholson/copper-kicad-mcp: MIT, v1.1.1. On the first autoroute it downloads Freerouting and a Java runtime,
    about 120 MB.
  - Seeed-Studio/kicad-mcp-server: no licence field. It installs into KiCad's Python.
  - lamaalrajih/kicad-mcp: MIT, last push 2025-10-17, analysis only.
  - Orchis-ai-LLC/Konnect-EDA: closed source, free for personal use only.
- KiCad's IPC API in KiCad 9 and 10 "only supports communication with a running instance of the KiCad GUI". Headless
  use through kicad-cli comes in KiCad 11. Source:
  https://dev-docs.kicad.org/en/apis-and-binding/ipc-api/for-addon-developers/index.html, "API Status and Goals".
- kicad-cli 10.0 has no command that places or routes (https://docs.kicad.org/10.0/en/cli/cli.html).
- Freerouting runs headless with `-de board.dsn -do board.ses` and `--gui.enabled=false`. It targets Java 25, and the
  CLI build bundles what it runs (README "Command Line Interface", docs/command_line_arguments.md lines 236 and 299 at
  v2.6.0). KiCad 10.0.6's Python has `pcbnew.ImportSpecctraSES`. kicad-cli has no SES import.
- Fusion: the KiCad importer reads KICAD_PRO, KICAD_SCH and KICAD_PCB, and it needs "KiCad v7 files or higher". Source:
  https://help.autodesk.com/cloudhelp/ENU/Fusion-ECAD/files/ECD-KICAD-IMPORTER.htm, read through a search summary.
- Fusion's personal-use licence limits electronics to 2 schematic sheets, 2 layers and 80 cm² of board. Source:
  https://www.autodesk.com/products/fusion-360/personal.html, read through a search summary. The e-paper board is
  126.4 x 72 mm, which is 91 cm². Fusion imports a STEP file as bodies.
- Install weight: the KiCad 10.0.8 macOS download is 1.4 GB, and the installed app on this Mac is 4.8 GB. The Windows
  10.0.8 download is 969 MB. KiCad asks for up to 10 GB of disk (https://www.kicad.org/help/system-requirements/). No
  smaller install without the 3D libraries was found for KiCad 10. tscircuit in a scratch project is 298 npm packages.

## How it sits in spark today

- `data/tools.json` has roles and contracts. The role `board-engine` is the tool `tscircuit`, which meets the contract
  `tscircuit-board`. A person or a project can point a role at another tool (`tool_finder.py`, P82).
- `scripts/spark/build/board_engine.py` holds `TscircuitEngine`, an Adapter with `build`, `version` and `probe`.
  `BuildService` counts every element whose type holds "error" (`build_service.py:71` to 74).
- spark already owns what every engine shares:
  - the requirements, and the part and board records with pads and bodies
  - the pin assignment (`assign_pins`) and the power rails (`power_rails.py`)
  - the placement (`board_components.place`). The netlist is not shared yet: `netlist.Netlist` reads the built
    `circuit.json` (`netlist.py:41`), as the architect found.
  - the trace widths (`copper.py`) and the fab numbers (`data/fabrication.json`)
- These are tscircuit's alone today: the board file's language (`board.tsx`, written by `board_sections.py`), the
  autorouter, the pour, the schematic layout, the views (`tsci dev`, circuit-to-svg) and `circuit.json`. The Wokwi
  converter, the breadboard and every check read `circuit.json`.
