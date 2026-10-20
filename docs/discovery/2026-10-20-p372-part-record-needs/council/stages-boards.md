# Board records: what each stage reads (P372, board lens)

> A board record that passes `boards.py --validate` is much weaker than a record that works. Validation checks only that
> nine keys exist (`scripts/boards.py:62`). I ran it on a record with `wokwi_part_type: null`, an empty `physical`, empty
> `wake_capable_gpio` and one pin, and it returned no problems. Each later stage then reads its own fields and
> reacts in its own way. Pin assignment and the pin map need only `pins` and `name` (and say so loudly when a
> capability list is empty). The build stops loudly without a footprint block. Simulation stops loudly without a
> `wokwi_part_type` but degrades silently without `wokwi_pin_naming` and `wokwi_size_px`. Deploy stops without
> `micropython_port` and a matching tools entry, and degrades to a warning without `flash_mb`. Nothing reads
> `deep_sleep`, `sku`, `sources` or `hardware_revisions` in code.

I read the code at the cited lines. Prior work on adding a board is
[`docs/discovery/2026-10-19-p331-new-board-works/plan.md`](../../2026-10-19-p331-new-board-works/plan.md) (the
shared `RecordAdder`, the store place, honest validation). I do not repeat it. I only add what each stage reads. The
two examples are `boards/xiao-esp32-c6.json` (XIAO) and `boards/firebeetle2-esp32s3.json` (FireBeetle).

## The gate before every stage: loading

Every stage that calls `boards.load` (`scripts/boards.py:253`) runs `validate` first. So the floor for any stage is the
validation floor, and `load` raises `BoardError` when it fails (a stop, said).

- Required keys: `schema`, `id`, `name`, `chip`, `wokwi_part_type`, `pins`, `wake_capable_gpio`, `adc_gpio`,
  `physical` (`boards.py:62`). Only the key must exist, a null or `{}` passes.
- `id` equals the file name and is a plain key. `pins` is not empty and each value is an int in 0 to 63 (`boards.py:376-390`).
- Names used as code (pin labels, pad names, rails, `footprint_export`) are letters, digits and `_` (`boards.py:477-496`).
- `pin_roles` use only the closed role list, each with `gpio` and a non-empty `note` (`boards.py:95`, `:411-422`).
- `power_pads` entries need a `rail` (`boards.py:462`). `documents` need a sha256 and a file (`parts.py:454`).
- `wokwi_power_pins`, when given as an object, must name every `power_pads` pad (`boards.py:366-372`).
- Forbidden decision keys (`wake_on_high`, `signals`, `pin_assignments`, `i2c_freq`) are refused (`boards.py:76`).

## Table: stage, fields read, if missing

"Stops" means the stage ends with could-not-run or an error that says why. "Silent" means no word at all.
"Said" means the stage goes on and says what is missing.

| Stage | Fields read (file:line) | If missing |
|---|---|---|
| Pin assignment, `assign_pins.py` | `pins` (:152, :224, :240, :243), `wake_capable_gpio` (:129), `adc_gpio` (:131), `pwm_gpio` optional (:133), `pin_roles.*.gpio` (:139), `pin_roles.*.note` (:388), `name` (:369, :404), `id` (:493) | `wake_capable_gpio` or `adc_gpio` empty: a signal that needs wake or ADC has no pin, so `Impossible` with the reason (:294). `pin_roles` absent: no pin is avoided, silent. `pwm_gpio` absent: every pin does PWM (an ESP32 fact, said in the docstring :120) |
| Pin map `pins.py`, `--emit-pins` | `name` (:404), `physical.pad_aliases` (:409), `pin_roles` notes (:388), `pin_roles.onboard_led.gpio` (:416) | No `onboard_led`: no `ONBOARD_LED` line, silent. No aliases: pad shows the label, silent |
| Role effects in assignment | `strapping` is never offered (:61, :154). `console_uart`, `onboard_button`, `onboard_led` are penalised (:73-78, :98). `spi`, `i2c` spent last (:196) | A role not in the closed list is a validation error (`boards.py:411`). `adc2_unusable_with_wifi`, `not_wake_capable` have no reader beyond a weight or a note |
| Emit board (schematic), `emit_board.py` | `physical.footprint_export` (:592, :631, :1083), `physical.width_mm`, `height_mm` (:357-358, default 25 and 60), `power_pads` (:500, :852, :900), `power.io_volts` (:679), `power.*` current facts via the pad's `can_supply`, `own_draw`, `volts` pointers (:526-529), `name` (:595) | No `footprint_export`: stops (:1083). No `power_pads`: a comment in the output says the processor is wired to no rail (:900), the build goes on, said in the file only. Size absent: silent default. `io_volts` absent: a series resistor from `for_current_ma` stops (:684). A null current fact: the rail check reports it as not stated (:461-465), said |
| Footprint, `emit_footprint.py` | `physical.header.{rows,pins,pitch_mm,row_spacing_mm,first_pad_from_edge_mm}`, `physical.{width_mm,height_mm,header_order,footprint_export}` (:85-100), `drill_mm` (:163), `id` (:160) | Any gap: stops, lists each gap (:212). The same rule marks the board "stops at the footprint stage" when offered (`boards.py:250`, `needs.py:145`, `parts.py:165`) |
| Pad names | `header_order` must hold every `pins` key or its alias (`boards.py:395-410`) | Validation error when `header_order` is given. When `header_order` is absent, the check does not run, and the footprint gap stops later |
| Build and check, `check_spine.py` | `name` (:365), `physical.footprint_export` (:411), `wokwi_part_type` (:547, board-alone only). Stage order: board, parts, schematic, footprint, build, simulation | A board with `footprint_gaps` builds nothing but pin-map work (`board_alone` skips parts, schematic, footprint, build as SKIPPED, :540-545) |
| Vendor pin check, `check_vendor_pins.py` | `vendor.arduino_variant` (:204), `pins` (:84) | Absent: `could-not-run` with the reason (:206), not a pass |
| Physics and rail checks | `power.regulator_3v3_a`, `module_peak_a`, `io_volts` as facts the pad pointers name (`emit_board.py:499`, `:526`) | Null value: reported "is not stated", not assumed safe. XIAO `regulator_3v3_a` is null today (`boards/xiao-esp32-c6.json:209`) |
| Internal pull-up | `power.internal_pull_up_ohms.value` (`design.py:290`) | Absent: every pull-up resistor stays on the board, silent |
| Wokwi diagram, converter | `wokwi_part_type` (`mapping.ts:115`, `placement.ts:38`, `geometry.ts:29`), `wokwi_pin_naming` (`mapping.ts:82`), `pins` (`mapping.ts:95`), `physical.pad_aliases` (:94), `wokwi_power_pins` (:108), `physical.wokwi_size_px` (`geometry.ts:29`) | `wokwi_part_type` null: `board_alone` stops with "names no wokwi_part_type" (`check_spine.py:548`), the normal path hands Wokwi a null type. `wokwi_pin_naming` absent: treated as `silkscreen`, silent, so a GPIO-named part fails later on pin names. `wokwi_power_pins` absent: power pads are not mapped, wires to them fail. `wokwi_size_px` absent: default 80 by 60, silent |
| Simulation run, `run_scenario.py` | `micropython_port` (through `flash_image.interpreter_path`, :149), then `wokwi_part_type` in the diagram. The Wokwi cloud must know the part type | Same as the image row below. Wokwi not knowing the type: the converter or `wokwi-cli` fails, reported `could-not-run` (`check_spine.py:516-521`) |
| Breadboard sheet and drawing, `breadboard.py` | `name`, `id` (:237), `header_order`, `pins`, `power_pads`, `pad_aliases` (:149-152), `wokwi_part_type`, `wokwi_pin_naming` (:381-384), and `data/wokwi-geometry.json` keyed by the type | The sheet text is written from `name`, pins and aliases. The drawing exists only for a type in `data/wokwi-geometry.json`, today the XIAO's `board-xiao-esp32-c6` only. For FireBeetle the drawing is said to be missing (`breadboard.py:27`, `:420`). No geometry is not in the record |
| Image build, `flash_image.py` | `micropython_port` (:89, :114) and `data/tools.json` entries with the same `micropython_port` and `meets` `micropython-esp32-bin` | Absent in the record: `ToolProblem`, stops (:90). No tools entry: `ToolProblem`, stops (:117). Flash size and filesystem offset are fixed in code, 4 MB and 0x200000 (:30-31), not read from the record |
| Look before deploy, `board_look.py` | `chip` (:160, :191), `flash_mb` (:161, :195), `id` (:229) | `chip` is required. `flash_mb` absent: the field is "unknown", the verdict is warning (:185-199), said. Chip differs: stop |
| Deploy, `deploy.py`, `deploy_service.py`, `firmware_platform.py` | `chip` to esptool `--chip` (`firmware_platform.py:38`), `physical.buttons` (`boards.py:ButtonPlaces`, used by `flasher`, `board_doctor`, `download_mode`, `deploy_service.py:149`), `id` through the look and the store record | `buttons` absent or partial: plain hint "the BOOT button", "RESET" with no place, said as a shorter hint (`boards.py:~290`, README "Button places"). `chip` wrong: esptool refuses |
| Live try and console, `live.py`, `board_live.py` | `pin_roles.usb`, `pin_roles.flash` (`restricted_pins.py:19`, :56), `pins` and `pin_roles.*.gpio` (`board_live.py:57-60`) | No `usb` or `flash` role: `pins_checked` is false and the try says no pin was checked (`board_live.py`, `has_none`), said. A broken role raises `BrokenRecordError` |
| Drawer, matching, `init_project.py` | `id`, `name` and the footprint gaps (`drawer.py:133`, `needs.py:189`, `init_project.py:400`) | Gaps are listed beside the board when offered, never hidden |
| Build history digest | `pins`, `power_pads`, `physical` (`parts.py:985`, :1007) | A change in any of the three makes an old "built" proof stale. `pin_roles` and capability lists are not in the digest |
| Not read by any script I found | `deep_sleep`, `hardware_revisions`, `sku`, `sources`, `//` notes | The TypeScript type lists `deep_sleep` (`board.ts:44`) but no code reads it. These are for people |

## Minimum per stage, from the code

Stage letters follow the question. Each list adds to the loading floor above.

(a) Assign pins and write the pin map.
- Loading floor: the nine keys, with real `pins` (label to GPIO), `name`, `chip`.
- Real `wake_capable_gpio` and `adc_gpio`, because the assigner reads both and an empty list makes a wake or ADC signal impossible.
- Nothing about footprints, Wokwi or flash. A record with `wokwi_part_type: null` and `physical: {}` still assigns.
- Not needed but changes the answer: `pin_roles` with `strapping`, `console_uart`, `onboard_led`, `spi`, `i2c`, and `pad_aliases`.

(b) Build (parts, schematic, footprint, board engine, checks).
- Everything in (a).
- `physical.footprint_export` and `physical.footprint_module` for fabrication (`REQUIRED_FOR_FAB`, `boards.py:67`).
- `physical.width_mm`, `height_mm`, `header.{rows,pins,pitch_mm,row_spacing_mm,first_pad_from_edge_mm}`, and `header_order` that covers every `pins` key or alias (`emit_footprint.py:85-100`).
- `power_pads` with a rail for each pad, or the processor is wired to nothing.
- To build a design that uses a series resistor or a rail sum: `power.io_volts` and the current facts the pads point at.
- The board engine tool (`tools.find("board-engine")`) must be installed, not a record field.

(c) Simulate.
- Everything in (b) for a design with parts, or only (a) plus the next two for a board alone (`board_alone`, `check_spine.py:540`).
- A non-null `wokwi_part_type` that Wokwi really has. If it does not, a same-chip devkit stands in with `wokwi_is_stand_in: true` (FireBeetle). That flag is for people, no script reads it.
- `wokwi_pin_naming` set to the truth (`gpio` or `silkscreen`), because absent means `silkscreen` and is silent.
- `wokwi_power_pins` for each power pad when the Wokwi part names them differently (FireBeetle `GND1`, `VCC`). Validation checks this.
- `physical.wokwi_size_px` is optional (a default is used).
- A firmware image: see (d), because the run uses `micropython_port` too.

(d) Deploy.
- `chip` as esptool names it (the look compares it with what esptool reads, and esptool gets it as `--chip`).
- `micropython_port` plus a `data/tools.json` entry for the same build, with its file and sha256. This is a vendor file, kept in the store, never in the repo.
- `flash_mb` (number or list). Without it the look warns and a standing deploy grant does not apply.
- `physical.buttons` so the BOOT and RESET hints name a place. Optional.
- A passed simulation or the person's yes for an untested image (`deploy_gate.py`). That is a project fact, not a record field.
- The image layout is the same for all boards: 4 MB, filesystem at 0x200000 (`flash_image.py:30-31`). A board with more flash or another layout needs code, not a field (P335 in the plan).

## What makes a board fully usable

All of the following hold, and none is a must for the stage above:
- Every key above has a value, with `//` source notes beside each fact, and `documents` keeps the sources by sha256.
- `vendor.arduino_variant` is set, so `check_vendor_pins.py` can re-derive `pins` (without it the check is could-not-run).
- Power facts are verified: `regulator_3v3_a`, `module_peak_a`, `io_volts`, `internal_pull_up_ohms`. XIAO `regulator_3v3_a` is null today.
- `pin_roles` are complete (`usb`, `flash` for live-try safety, `strapping`, `console_uart`, `onboard_led`, buses).
- `data/wokwi-geometry.json` holds the part, so the breadboard drawing exists. Today only the XIAO is there. This is a file outside the record.
- A tools entry for the MicroPython build, in `data/tools.json`. This is also outside the record.

## Gaps found

1. Validation passes a record that every later stage stops on or silently degrades with (`wokwi_part_type: null`, `physical: {}`, empty capability lists). The plan's "honest validation" card covers the count of open facts. It does not say which stage each missing field costs. This table is that list.
2. Two silent defaults hide a wrong record: `wokwi_pin_naming` absent means silkscreen (`mapping.ts:82`), and a missing `wokwi_size_px` means a default size (`geometry.ts:29`, `sizeOf`).
3. Three things a stage needs live outside the board record: the Wokwi geometry (`data/wokwi-geometry.json`), the tools entry for the build (`data/tools.json`), and the Wokwi cloud's own part list. A new-board path must write or check all three.
4. `flash_image.py` fixes the layout for every board (4 MB, 0x200000), so `flash_mb` is a check only, never an input.
5. The record keeps fields that no code reads (`deep_sleep`, `hardware_revisions`, `sku`, `sources`). They are notes for people, and nothing tells a person which fields are notes and which are inputs. `boards/README.md` does not list the inputs per stage.
