# P372 tech-expert lens: what each stage reads from a part record

Read from the code in this worktree on 2026-10-20. File:line is in `scripts/` unless said. "Not read" marks what I did not open.

> **TL and DR:** The chain is strict about five fields and quiet about the rest. A part record is refused when `footprint`, `pin_order`,
> `pin_order_proof`, `body_mm` or `simulation` is absent (`parts.py:102`, `owes`), and for `needs`, `power`, `host_parts` and one
> named current fact it decides the board and the pin map. Everything else the PO would call "knowing the part" (`facts`, `legs`,
> `host_requirements`, `function`, `documents`, `verified` flags) is said to the person and never decides anything. The joystick
> record owes nothing and validates clean, so it is usable today. Its real gaps are four. It has no `function` and its kind
> `joystick` is not in `KIND_FUNCTION`, so `--match` by verb cannot find it. Seven of its eight `facts` are read by no stage.
> Its size and its pin order are guesses that the chain accepts as written. And no schema or stage knows what an analog output
> or a switch is, so "adc" and "pulls to ground" live in free text. The minimum to use a part is the five chain fields plus
> `needs` and `power`. The rest is trust, and trust is only ever said, never enforced.

## 1. Stage by stage

"Stops" means the stage refuses and the exit is 2 (cannot run) or the pick is refused. "Says" means a printed or written sentence
and the stage goes on. "Silent" means no message anywhere.

| Stage | Fields read (file:line) | If missing | Joystick has it? |
|---|---|---|---|
| Idea, `--need` (NameContains) | `id`, `name`, `kind`, `also_known_as` (`matching.py:176-192`, `parts.py:96-99`) | Silent: the part is not found | Yes. Found by "joystick", "KY-023", "HW-504" (row 1 of the walk rows) |
| Idea, `--match` (SameWords, WordOverlap) | `function` or else `KIND_FUNCTION[kind]` (`parts.py:77-84`), `name`, aliases, `tags`/`about`/`description` from drawer entries (`matching.py:65-90`, `admits` at `:150`) | Silent: a part with no same-verb function is never admitted | **No.** No `function`. `kind: joystick` is not in `KIND_FUNCTION` (`parts.py:66`). `function_of` returns `[]` (I ran it). Not found by "input / joystick" |
| Idea, chooser text | `power`, `body_mm`, `kind` (`matching.py:25`, `describe`) | Silent: line left out | Yes |
| Requirements (`parts.py --requirements`, `needs.py:601`) | `owes(record)`: `REQUIRED_KEYS` (`schema, id, name, kind, needs`, `parts.py:51`) plus `CHAIN_FACTS`. Then `broken_problems` | **Stops** the pick when anything but `body_mm` is owed (`needs.py:428,616`). A missing `body_mm` is placed at a placeholder size and said | Owes nothing (ran `parts.owes`: `[]`) |
| Requirements, power gaps | `power[].rail/pin/direction`, `needs[]` outputs (`needs.py:561`, `emit_board.py`) | Says: "rail with no source", "net with no receiver". Never refuses | Yes. VCC rail `logic`, GND rail `ground` |
| Record check (`parts.validate`, `parts.py:621`) | `schema`, `needs[].signal/pin/direction/bus/needs`, `power[].pin/rail/direction/polarity`, `pin_order`, `footprint`, `body_mm`, `facts[*].verified/value/why_it_matters`, `host_parts`, `documents[*].sha256`, `simulation`, `function` | Stops for the five chain fields. A fact without `verified` and `source` is a problem (`parts.py:839`) | Passes (`broken_problems` is `[]`) |
| Pin assignment (`assign_pins.py`, via `parts.signals_for` `parts.py:861`) | `needs[].signal`, `.needs` (one of `wake adc pwm`), `.pin_on_host`, `.bus` (`:207,248`) | A capability outside the three **stops** (`Impossible`, `:207-211`). No `needs` list means "any pin" and is silent | Yes. `JOY_X`, `JOY_Y` ask `adc`. `JOY_SW` asks nothing, so it gets any pin. The `note` and `direction` are not read here |
| Pin assignment, the person's pull choice (`design.py:285-297`) | `host_parts[kind=pullup].internal_will_do`, `needs[].needs` has `wake`, the board's `internal_pull_up_ohms` | Silent: the resistor stays on the board | Yes. 10k pull-up on SW, `internal_will_do: true`, so the firmware pulls it up |
| Board file emit (`emit_board.py`) | `pin_order` (`:264`), `footprint` (`:291`), `body_mm` (`:245-276`), `power[]` incl. `direction/polarity/rail` (`:203-226`), `needs[].signal/pin` (`:797`), `host_parts[kind,pin,ohms,why,...]` (`:702-752`), `id`, `name` | Stops with exit 2 for a missing `footprint` or `pin_order` (`:1101-1119`). A missing size stops too, except under `--assume-missing-sizes` (`:1122`), which `check_spine` passes (`check_spine.py:393`). The guess is written into the file | Yes to all. `body_mm` 34 x 26 is **unverified** and a guess, and the chain builds on it |
| Board file, current on the rail (`emit_board.py:462-560`) | `power[].draws/can_supply/own_draw/feeds/volts` and the named `facts[x].value/.verified` | Says: `amps: None` with a reason, "complete: false" | `draws: supply_current_ma` points at a real fact (0.66 mA, unverified). **The only fact in the joystick that a stage reads** |
| Build / check (`check_spine.py`, `check_all.py`, `check_physics.py`) | The circuit that came out of the board file, plus `design.parts_of` for names, `placeholders` (footprint_placeholder) and rail loads (`check_all.py:157-215`). Not the record directly | A part with a stand-in footprint is skipped and said (`check_all.py:157`). No `tsci` gives exit 2 (cannot run) | Not special. `verified: false` on the load is said in the rail line (`check_physics.py:309`) |
| Breadboard sheet (`breadboard.py`) | `host_parts` (`:163`), `legs` (`:281`), `unused_pins[].pin/note` (`:333`), `host_requirements` (`:336`), `warnings`/conflicts via `parts.pull_conflicts` (`:330`), `name`, `id` | Silent for `legs`, `host_requirements`, `unused_pins` (empty list). `legs` is read **nowhere else and checked nowhere** (not in `RECORD_TYPES`, `parts.py:311`) | Yes. `legs` for all five pins, 4 `host_requirements`, `unused_pins` is `[]` |
| Breadboard sheet, "what you own" column | The drawer, not the record (`breadboard.py:210-224`) | Says "to get" | Drawer link exists per the walk (row 1) |
| Wokwi diagram and simulation (`sim_project.py:44-100`, `parts.py:548`) | `simulation.skip` or `simulation.wokwi.part/chip/pins/attrs/stand_in/note`, `host_parts` ohms for the passives | A missing `simulation` is owed, so the pick is refused at requirements. The converter says "no simulation in the record" (`sim_project.py:128`) and the board still builds. Missing `stand_in` on a built-in part is a validate problem | Yes. `wokwi-analog-joystick`, 5 pins, `stand_in` text says axes are unmeasured |
| Firmware pin map (`pins.py`, `assign_pins.render` `:368`) | The assignments, with `design.signal_name` (`design.py:311`). Not the record | A part with no `needs` adds no pins | Yes. `JOY_X`, `JOY_Y`, `JOY_SW` |
| Firmware import (`import_firmware.py`) | None. It reads the project's `firmware/` | Not applicable | Not applicable |
| Deploy (`deploy*.py`, `board_facts.py:23`) | None from part records. The facts file holds spark version, project, board, mac, image sha256 | Not applicable | Not applicable |
| Review (`skills/spark-review/SKILL.md:74`) | `parts.py --unverified <parts>` lists `facts[*]` with `verified: false` and `pin_order_proof` (`parts.py:890-899`). `conflicts_of` reads `facts.onboard_input_pullups_ohms`, `input_high_threshold_v`, `supply_range_v` (`:1498`) | Silent for a fact that is not there | 9 questions listed, none for `body_mm` (row 14). `conflicts_of` returns `[]`, because the module has no onboard pull-up fact |
| Drawer (`drawer.py:144-196`) | `id`, `sku`, `also_known_as`, `vendor` (to tell a near number from an exact one) | A part number with no `sku` falls back to id and alias tokens | `sku: null` and `vendor: null`, so a pick by number finds it only through the aliases |
| `init_project.py:100` (`must_not_float` rule) | `needs[].direction == "in"` and `pin` | Silent: the pin gets no float rule | `direction: out` on all three needs, so no float rule from the joystick |

## 2. Joystick `joystick-module-mh` against the stages

Fields it holds: `schema id name kind also_known_as vendor sku sources needs power unused_pins pin_order pin_order_proof legs
footprint body_mm host_parts facts host_requirements simulation documents based_on` and a `//` note.

| Field | Read by | Status | Why it is the way it is |
|---|---|---|---|
| `needs`, `power`, `pin_order`, `footprint`, `simulation`, `host_parts` | assign, emit, sim, sheet | Present, so usable | Chain fields. Taken from Joy-IT's KY-023 documents and the photos |
| `pin_order_proof.verified` | `--unverified` only (`parts.py:895`) | `false` | Order read from labels in photos, no meter check. **No stage refuses an unverified order.** It is said and the board builds |
| `body_mm` 34 x 26 | emit | `verified: false`, a guess | Joy-IT gives 34 x 39 x 26 and does not say which two figures. No ruler in frame. The chain accepts it as a number, and the `--unverified` list leaves it out (row 14) |
| `facts.*` (8 of them) | Only `supply_current_ma` by `power[VCC].draws`. `supply_range_v` is touched by `conflicts_of` only for a motor-style module | All `verified: false` | Sources are a different seller's board (Joy-IT) and a SparkFun page. Rule `verified: false` for a look-alike (note `//`) |
| `facts.runs_at_3v3`, `axis_output_is_ratiometric`, `pot_resistance_ohms`, `module_has_switch_pullup`, `switch_closes_to_ground`, `axis_assignment` | No stage (grepped `scripts tools lib agents skills`, found only the record) | Free text for people and Claude | The record says what each decides ("decides the host pull-up"), but the host pull-up was already written as a `host_part`, so the fact repeats it |
| `host_requirements` (4) | Sheet and `--show` only (`breadboard.py:336`, `parts.py:1563`) | Present | Advice in prose. "Feed +5V from 3.3 V" never reaches a check |
| `legs` | Sheet only (`breadboard.py:281`) | Present | Unvalidated free map |
| `function`, `tags`, `about`, `description` | `--match` (`matching.py`) | **Absent** | Research rules have no step that writes `function`. `KIND_FUNCTION` has no `joystick`. The audit counts such records ("say nothing of what they do", `parts.py:~190`, not read in detail) |
| `vendor`, `sku` | Drawer number match | `null` | A chipless, maker-less AliExpress module has neither (walk row 6) |
| `documents` (2) with sha256 | `--sources`, `--keep` | Present | A look-alike maker's PDFs, kept with sha256 |
| `needs[].direction` | Schema checks it is a string. `init_project.py:100` reads `in` | `out` on all | From the module's side. Nothing says it is analog or a switch |

## 3. Fields the records hold that no stage reads

- `facts`: six of the joystick's eight (grepped). Elsewhere `supply_range_v` and `input_high_threshold_v` are read by `conflicts_of`
  only. Any fact is read only when a `power.draws/can_supply/own_draw/volts` pointer names it (`emit_board.py:462-494`) or by the
  two conflict names.
- `needs[].note`, `power[].note`, `needs[].optional` (shown by `describe` at `parts.py:1551`, not used by `signals_for`).
- `host_requirements`, `legs`, `unused_pins[].note`: said on the sheet, never checked.
- `also_known_as` beyond search, `sources`, `//`, `based_on`: provenance only.
- `simulation.wokwi.stand_in`: copied into "what this simulation cannot show" (`sim_project.py:91`), never compared with the record.
- `pin_order_proof.source` and `cites`: read by the sources audit (`parts.py:1240-1290`, not read in detail).

## 4. Gaps, in order of what they cost

1. **No stage can tell a verified chain fact from a guess.** `pin_order_proof.verified`, `body_mm.verified` and `footprint` are
   written and printed but gate nothing. A guessed size and a measured size both pass `owes`. Only `--unverified` shows them,
   and it misses `body_mm`.
2. **`function` is optional and the joystick has none.** `--match` by verb cannot find it. `--need joystick` can, by words. A new
   part kind (joystick, encoder, potentiometer) needs a code edit to `KIND_FUNCTION` or a `--function-set` with a dry run.
3. **Capabilities are three words** (`wake adc pwm`) and an unknown one stops pin assignment. Nothing records "analog output",
   "switch", "output only", "closes to ground". They sit in `note` and `facts` text, so no check can use them.
4. **Facts are not tied to a decision.** Six joystick facts say "why_it_matters" but no stage reads them. A host pull-up is
   decided by the human-written `host_parts`, not by `module_has_switch_pullup`. The two can disagree and nothing compares them.
5. **`legs` and `host_requirements` are untyped** (`RECORD_TYPES` has no entry, `parts.py:311`). A typo drops them silently.
6. **Direction has two meanings.** On `needs` it is the module's side (`out` for a sensor) and read only by `init_project`
   for `in`. On `power` it is read by `emit_board`. No schema line says which side the word is spoken from.
7. **Stages that read no record at all:** firmware import, deploy and the pin map's text. They depend on the earlier stages
   being right, so a bad guess in a record reaches the bench unchanged.

## 5. What I did not read

`board_*.py` beyond `board_facts.py:23`, `breadboard_drawing.py` and `breadboard_steps.py` in detail (grepped for record
fields, found none), `compare_design.py` rules, `tools/`, the MCP side, `part_pictures.py` (grepped, no record fields),
`spark-design` references (`part-data.md`, `verified-parts.md`), the audit text in `parts.py` near line 190, and any bench
behaviour of the board file under `tsci`.
