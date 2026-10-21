# Round 3: ten future cases walked through the design

Lens: extensions. Model: Opus. Read-only on the code, 2026-10-19.

> Six of ten cases fit with a small edit. Three seams in section 2.5 promise "one subclass, one line" where the code
> shows more: the firmware platform, the simulator and no MCU. The MCP door and the wiring page need one split in
> `run_door` now, so they do not copy it later.

## The cases

| # | Case | What changes | Verdict |
|---|---|---|---|
| 1 | Arduino or PlatformIO | `firmware`: a `FirmwarePlatform` subclass, Adapters, a `PLATFORMS` line. Also the pin map (`assign_pins` writes `firmware/pins.py`), the image (`flash_image`, `ScenarioRun(micropython=)`), `stand_in/machine.py`, `board_facts` over mpremote | not as written (G1, G2) |
| 2 | A third board | a JSON record in `boards/`. Works for an ESP32 that Wokwi has and MicroPython runs on | no caller edit |
| 3 | A 555 blinker, no MCU | `boards.REQUIRED_KEYS` needs `chip` and `wokwi_part_type`. `boards.load(project, None)` falls back to the active board. `assign_pins` and `emit_board` assume a board | not at all (G3) |
| 4 | Car and remote | two project folders (D12, P318 option C). Later a list of folders | no caller edit |
| 5 | A new check | a `Check`, a line in `CHECKS` (`check_all.py:285`). Its codes go into check_all's Operation `codes`. A new input edits `inputs_for` | small edit (G5) |
| 6 | A second simulator | records (`wokwi_part_type`, `wokwi_pin_naming`, part `simulation.wokwi`), `sim_project` (Wokwi diagram and `wokwi.toml`), `check_spine.board_alone`, Wokwi scenario YAML, the run log deploy reads | not as written (G6) |
| 7 | MCP door | every area's `OPERATIONS`, a schema per Argument, consent, a long-lived process | small edit if split now (G7) |
| 8 | Shared store | `records`: `store.layers` already layers library, store and project. Online is one more layer plus sync | small edit (G8) |
| 9 | Wiring page | P297's `ProjectSession` (rev-checked atomic writes), a local server with events, a TypeScript page | no home (G9) |
| 10 | KiCad or Fusion export | a Renderer over `circuit.json` or the board's `physical` facts, a tool row and an Adapter (tsci, the Fusion MCP) | no home (G10) |

## The gaps

**G1, case 1. The platform key sits on the wrong record.** Section 2.5 keys `PLATFORMS` by the board record's
`firmware` field. The same XIAO runs MicroPython or Arduino, so the language is the project's choice. Fix: key
`PLATFORMS` by requirements.json's `firmware` field, with `micropython` as the default. The board record keeps
`micropython_port` as a fact about what it can run.

**G2, case 1. `FirmwarePlatform` covers only the deploy.** Today it makes the flasher, shell, connection, ready
check and console probe (`firmware_platform.py:41`). The pin map, the image and the stand-in are MicroPython too.
Fix: add `pin_map_text(design)` and `make_image(project)` to the Platform in 2.6's class diagram. `design` may not
import `firmware` (FW points at DES), so `build` passes the platform's pin map writer in, as 2.2 already says for a
flow over two areas. Change the 2.5 row to "a subclass with five factories and two writers".

**G3, case 3. No MCU is not "nothing".** The row "a record with neither field" cannot exist: the board contract
requires `chip` and `wokwi_part_type` (`boards.py:62`). Worse, a requirements file with no `board` silently gets the
active ESP32 (`boards.py:253`). Fix: make `"board": null` the explicit "no MCU" in requirements, give `Design.board`
None, and let every MCU stage answer `skipped`. Change seam test 6 to "a requirements file with no board never loads
the active board". Say in 2.5 that the pin assigner and emitter need a story for it. It is not a free seam.

**G5, case 5. Codes are listed in two places.** Criterion 4 makes `check_all`'s Operation list every code. A new
check then edits that Operation. Fix: each `Check` declares `codes` and `needs`, and the Operation's `codes` is the
union over `CHECKS`. A check that needs a new input still edits `inputs_for` once.

**G6, case 6. The simulator is more than a run.** Wokwi lives in records, in the simulation project and in the gate.
`SimulationEngine` with one `run` cannot swap that. Fix: give the Strategy two steps, `prepare(design)` writes the
simulation folder and `run(scenario)` returns a `RunRecord` that deploy's gate reads. Engine facts sit under
`simulation.<engine>` in records. When the second engine comes, the board's `wokwi_*` fields move there and leave
`REQUIRED_KEYS`, which also helps G3. Scenarios keep the Wokwi steps the stand-in can also run.

**G7, case 7. `run_door` mixes three jobs.** It parses argv, runs and prints. An MCP door needs the run without
argparse or stdout. `Argument` holds argparse keywords with callables such as `type=Path`, so no schema comes out
of it. Fix, in slice 2 at no cost: split out `run_operation(operation, values, **collaborators) -> answer` in
`core`, and let `run_door` call it. Add `Argument.kind` (text, path, number, flag, choice). The catalog D3 dropped
returns with the MCP door as one list of area names, imported one by one, so a broken area loses only its tools.
A step with `needs_yes` returns to the person through the host's confirmation, never as an argument.

**G8, case 8. Origin and network effect.** Two layers can hold one id. Fix: an online layer only syncs into the
local store through one sync Operation with the `network` effect, so every read stays local and no other Operation
changes its effects. Each record read carries its layer, which `RecordSchema` already can report.

**G9, case 9. The page has no area and the server is not a door.** `ProjectSession` writes requirements and then
rebuilds, so it sits above `build`. Fix: add a `project` area on top of `build` for `ProjectSession`. Name the local
server as a door kind that calls `run_operation` (G7). Say that TypeScript is outside S1 to S13 until the page exists.

**G10, case 10. Exports have no registry and fab has no area.** The only renderer registry is
`breadboard.DRAWING_RENDERERS` (`breadboard.py:94`). The layout in 2.1 places neither `fab`, `copper` nor
`emit_footprint`. Fix: put them in `design` with an `EXPORTERS` registry keyed by format. A KiCad or Fusion export is
one Renderer of the design plus a `tools.json` row and an Adapter. Missing part dimensions enter the records by need.

## No gap

Case 2 holds for ESP32 boards. A non-ESP32 chip also needs G2. Case 4 holds because D12 keeps one board per folder
and P318 found that the later folder list needs no rework.
