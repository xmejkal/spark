---
name: spark-design
description: Design an electronic circuit or PCB from a description, especially ESP32 and module-level boards. Use when the user wants to design a circuit, make a real schematic or PCB, wire up a microcontroller with peripherals, or says "design a board for...", "make a schematic for...", "wire up an ESP32 with...". Produces tscircuit code, builds it headless, and grades it against design rules and a verified-parts library.
---

# spark-design

Design circuits as code (tscircuit), grounded in verified parts and design-rule checklists,
never by inventing pinouts. The winning pattern is: verified parts + reference blocks +
a rule checklist in the loop. Follow it.

## Workflow

1. **Scope the design.** Confirm the target (MCU/module, peripherals), and the power domains.
   State the rule up front: separate motor/high-current supply from logic; the two domains
   share only ground, never a supply rail. A motor or actuator never touches a GPIO.

2. **Resolve every part from the verified-parts library first.** Read
   `references/verified-parts.md`. Use a part only with a datasheet-checked pin map. If a part
   is missing, resolve it from the vendor (see `references/vendor-knowledge.md`): for Espressif use
   the `pins_arduino.h` variant header + the `espressif-docs` MCP; for DFRobot use the wiki
   `/<sku>/docs/` pinout + the `DFRobot_<Part>` GitHub `examples/` + the Gravity connector class;
   otherwise a JLCPCB/LCSC lookup or datasheet. Record a new library entry with provenance and a
   `verified` flag, and flag any pin you could not confirm. NEVER invent a pinout. **First confirm
   which exact board it is** (Seeed XIAO vs DFRobot FireBeetle/Beetle differ — see verified-parts.md).

3. **Apply the design rules.** Read `references/design-rules.md` and check the design against it
   — decoupling at every IC power pin, bulk cap near high-current loads, I2C pull-ups, correct
   pin roles, level compatibility, and the ESP32 module specifics.

4. **Write the tscircuit board (`.tsx`).** Model ICs as `<chip>` with `pinLabels`; wire with
   `<trace from=... to=... />` selectors or `sel.*` type-safe references; use `<net>` labels for
   power/ground; pull real footprints from the registry (`tsci add`) or `footprint="jlcpcb:C..."`.
   Prefer `sel.NAME.PIN` references so a wrong pin name fails at compile time.
   **Name every component descriptively** — `MotorDriver`, `OledDisplay`, `PullupSda`, `MotorBulkCap`,
   `BtnOpen`, `IrSensor` — never bare `U1`/`R2`/`SW1`. Use clear net names too (`MOTOR6V`, `GND`, `V33`).
   Readable names make the schematic, the selectors, and the git diff self-documenting.

5. **Build and iterate on the errors.** Run `npx tsci build board.tsx`. Read
   `dist/<board>/circuit.json` for `*_error` / `*_warning` entries (unconnected pins, missing
   power/ground, overlaps). Fix and rebuild until clean. Do not rely on the `tsci check` CLI
   subcommands (work-in-progress) — read the circuit.json errors.

6. **Verify before emitting fab output.** Hand off to `spark-review`, which ends with the fab
   gate: `check_all.py --project .`, then `boards.py --validate --for-fab` and
   `parts.py --unverified`, then `kicad-cli sch erc` if KiCad is installed. Do NOT produce Gerbers
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
- `references/verified-parts.md` — the verified-parts library (pin maps + provenance).
- `references/vendor-knowledge.md` — how to pull verified data from Espressif & DFRobot (and others).
- `references/part-data.md` — the part-data backbone: real footprints/3D/datasheets per part, and auto-solve-or-ask for layout.
- `references/verification-loop.md` — the checks-to-fab gate; the enforced version is the
  gate section at the end of `spark-review`.
- `references/pcb-layout.md` — the fab stage: honest AI-layout limits + the two PCB pipelines.
- `references/tscircuit-recipes.md` — PROVEN commands: local run, the cap→net routing fix, real
  footprints (footprinter strings + `tsci convert` from GitHub `.kicad_mod`), auto-solve placement.
