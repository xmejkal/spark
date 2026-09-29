---
name: spark-design
description: Design an electronic circuit or PCB from a description, especially ESP32 and module-level boards. Use when the user wants to design a circuit, make a real schematic or PCB, wire up a microcontroller with peripherals, or says "design a board for...", "make a schematic for...", "wire up an ESP32 with...". Generates the board from a requirements file through spark's own chain (parts → pin map → board file → build → simulation), builds it headless, and grades it against design rules and the parts library; tscircuit is written by hand only where the generator stops.
---

# spark-design

Design circuits as code (tscircuit), grounded in verified parts and design-rule checklists,
never by inventing pinouts. The winning pattern is: verified parts + reference blocks +
a rule checklist in the loop. Follow it.

## Workflow

1. **Scope the design.** Confirm the target (MCU/module, peripherals), and the power domains.
   State the rule up front: separate motor/high-current supply from logic; the two domains
   share only ground, never a supply rail. A motor or actuator never touches a GPIO.

2. **Resolve every part from the parts library.** `${CLAUDE_PLUGIN_ROOT}/scripts/parts.py --list`
   shows what exists — the shipped records plus the project's own `parts/*.json`, which win by
   name — and `parts.py --show <id>` what a record asks of the host and what nobody has verified.
   A part that is not there is written as a **record**, never resolved into prose:
   `references/part-data.md` has the schema and `parts.py --validate --project .` says what is
   missing. NEVER invent a pinout — a pin map comes from the vendor (`references/vendor-knowledge.md`:
   Espressif's `pins_arduino.h` variant header, the DFRobot wiki `/<sku>/docs/` pinout and the
   `DFRobot_<Part>` GitHub `examples/`, otherwise a datasheet or a JLCPCB/LCSC lookup), recorded
   with provenance and a `verified` flag, and any pin you could not confirm flagged. **First
   confirm which exact board it is** (`boards.py --list`; a Seeed XIAO and a DFRobot FireBeetle
   differ, and one DFRobot SKU is two power designs — see the board file's `hardware_revisions`).

3. **Write the requirements file and run the chain.** The requirements file *is* the design:

   ```json
   {
     "board": "firebeetle2-esp32s3",
     "parts": [
       "l9110s-module",
       "jst-ph-2-power-inlet",
       { "part": "tactile-button", "name": "BtnOpen" },
       { "part": "tactile-button", "name": "BtnMode" }
     ]
   }
   ```

   A module list is a list of *consumers* — the inlet is what sources the motor driver's rail,
   and without it the chain stops at the schematic and says so. Which rail a part sits on is the
   design's: `{"part": "l9110s-module", "rails": {"VCC": "traction"}}` re-points one pin without
   copying the record. Extra pins no part claims go in
   `"signals": [{"name": "LED_STATUS", "needs": []}]`; the file lists each as assigned and
   connected to nothing, for you to wire by hand.

   Then, in this order — each says what it decided and why:
   - `${CLAUDE_PLUGIN_ROOT}/scripts/assign_pins.py requirements.json` — a pin per signal, scarce
     pins (wake, ADC1, the buses) spent last, with the reason beside each.
   - `${CLAUDE_PLUGIN_ROOT}/scripts/emit_board.py requirements.json > board.tsx` — the board file.
     It REFUSES rather than guess: no footprint, no pin order, no measured outline
     (`--assume-missing-sizes` proceeds with the guess declared in the file), two components of one
     name. The file says what it invented and what it could not size.
   - `${CLAUDE_PLUGIN_ROOT}/scripts/check_spine.py requirements.json` — the whole chain,
     `idea → parts → pin map → schematic → footprint → build → simulation`, and the stage that
     stopped it. `????` is could-not-run and never a pass; `!!` is a defect in the design.

   The project is found up from the requirements file, so this works from anywhere. `/spark:build`
   is the same thing as a command.

4. **Apply the design rules the generator cannot.** Read `references/design-rules.md` and check
   the design against it — decoupling at every IC power pin, bulk cap near high-current loads, I2C
   pull-ups sized from the bus, correct pin roles, level compatibility, the ESP32 module specifics.
   The generated file lists every part's `host_requirements` and does **none** of them; those are
   yours, in the board file, by hand.

5. **Write tscircuit by hand only where the generator stops** — a passive network, a connector
   the module list does not know, a layout decision. Model ICs as `<chip>` with `pinLabels`; wire
   with `<trace from=... to=... />` selectors or `sel.*` type-safe references; use `<net>` labels
   for power/ground; pull real footprints from the registry (`tsci add`) or
   `footprint="jlcpcb:C..."`. Prefer `sel.NAME.PIN` references so a wrong pin name fails at
   compile time. **Name every component descriptively** — `MotorDriver`, `OledDisplay`,
   `PullupSda`, `MotorBulkCap`, `BtnOpen`, `IrSensor` — never bare `U1`/`R2`/`SW1`, and clear net
   names (`MOTOR6V`, `GND`, `V33`): the generator does, and the schematic, the selectors and the
   git diff stay self-documenting. Then build and iterate on the errors: `npx tsci build board.tsx`,
   read `dist/<board>/circuit.json` for `*_error` / `*_warning` entries (unconnected pins, missing
   power/ground, overlaps), fix and rebuild until clean. Do not rely on the `tsci check` CLI
   subcommands (work-in-progress) — read the circuit.json errors.

6. **Verify before emitting fab output.** Hand off to `spark-review`, which ends with the fab
   gate: `check_all.py --project .`, then `boards.py --validate --for-fab` and
   `parts.py --unverified <every part on the board>`, then `kicad-cli sch erc` if KiCad is installed. Do NOT produce Gerbers
   while something load-bearing is unverified.

7. **Render and show.** `npx tsci export -f schematic-svg board.tsx`, convert to PNG if needed,
   and show the user the schematic. Summarize what is verified vs still a placeholder.

8. **PCB layout (only when the user wants a board).** Read `references/pcb-layout.md`. State the
   honest limit: AI does a first-pass placement + autoroute + DRC iteration, the human refines and
   signs off — never fab unattended. Enforce good practices with a rule-gate (net classes +
   `.kicad_dru` + `kicad-cli pcb drc`), not AI judgment. Default to Pipeline A (all-in-tscircuit,
   AI edits `.tsx` layout props + human edits via `manual-edits.json`) for module-level boards;
   escalate to Pipeline B (export to KiCad + Freerouting, turn-based single-writer) for complex ones.

## tscircuit command reference

- `npx tsci build board.tsx` -> `dist/<board>/circuit.json` (+ SVGs with flags).
- `npx tsci export -f schematic-svg board.tsx` -> schematic SVG.
- `npx tsci export -f kicad_pcb board.tsx` / `-f gerbers` / `-f step` -> KiCad / fab / 3D.
- `npx tsci add <author>/<pkg>` -> install a registry part/module.
- Install the official tscircuit skill for full syntax: `npx skills add tscircuit/skill`.

## Honest limits (state these to the user)

- tscircuit's autorouter can occasionally emit shorts or unmanufacturable vias — always run a
  DRC pass (the gate at the end of spark-review) before ordering, and never trust
  auto-routing unverified.
- Auto-placement is beta; place major modules yourself.
- Footprints from `jlcpcb:` auto-import are unverified until checked.
- Human review before fabrication is non-negotiable.

## References

- `references/design-rules.md` — general PCB best practices + the ESP32-C6/XIAO checklist.
- `parts/*.json` (`parts.py --list`) — THE parts library the chain reads; `references/verified-parts.md`
  is the older prose list and is not what the generator consults.
- `references/vendor-knowledge.md` — how to pull verified data from Espressif & DFRobot (and others).
- `references/part-data.md` — the part-data backbone: real footprints/3D/datasheets per part, and auto-solve-or-ask for layout.
- `references/verification-loop.md` — the checks-to-fab gate; the enforced version is the
  gate section at the end of `spark-review`.
- `references/pcb-layout.md` — the fab stage: honest AI-layout limits + the two PCB pipelines.
- `references/tscircuit-recipes.md` — PROVEN commands: local run, the cap→net routing fix, real
  footprints (footprinter strings + `tsci convert` from GitHub `.kicad_mod`), auto-solve placement.
