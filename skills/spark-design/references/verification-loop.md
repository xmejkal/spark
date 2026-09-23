# Verification loop (the gate)

The rule that makes spark different from "plausible but dead" AI-PCB output:
**never emit fabrication files while any pin is unverified.** Rigor scales with stakes —
at "just draw the schematic" it is relaxed; approaching a board order it is strict.

## Tiers, cheapest first

1. **Inner loop (in-process, instant, no network).** Call `@tscircuit/checks` on the
   Circuit JSON, or read `dist/<board>/circuit.json` for `*_error` / `*_warning`:
   unconnected/underspecified pins, missing power/ground pins, overlaps, clearance.
   Feed each error back into the tscircuit source and rebuild until clean.

2. **Authoritative ERC gate.** Export to KiCad and run:
   `kicad-cli sch erc --format json --exit-code-violations <sch>`
   (exit 0 = clean, 5 = violations). Parse the `violations[]` array. This is the
   real electrical-rule gate. Also `kicad-cli pcb drc` once a board exists — this is
   what catches an autorouter short before it reaches the fab.

3. **Pin-truth cross-check (the human-in-the-loop tier).** Diff the netlist against the
   verified-parts pin maps. Any pin that is not sourced from a `verified: true` entry is
   flagged for datasheet or bench confirmation. Emit nothing to fab while flags remain.

4. **Firmware simulation (functional).** Wokwi CI for ESP32-C6: assert serial output and
   GPIO/bus activity. Note: some breakouts (e.g. TB6612, MAX98357A) may only be verifiable
   from the MCU side, not the peripheral's real response.

5. **Deferred: analog SPICE (ngspice/PySpice).** Only when a real analog subcircuit exists;
   meaningless for a digital module board with a motor load.

## The gate
- Schematic stage: warnings allowed, shown to the user.
- Pre-fab stage: ERC must exit clean AND every pin must trace to a verified part or an
  explicit bench-confirmed reading. Otherwise: refuse to emit Gerbers, list the open pins.
- Ground truth is always the bench (breadboard the modules before ordering a PCB).
