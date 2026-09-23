---
name: spark-verify
description: Verify a circuit design before fabrication and gate on unverified pins. Use when the user has a schematic or board and asks to "verify", "check the design", "run ERC" or "run DRC", or is about to order/fabricate a board. Runs tscircuit checks and kicad-cli ERC/DRC, cross-checks every pin against the verified-parts library, and refuses to emit fabrication files while any pin is unverified.
---

# spark-verify

The gate that separates a real design from plausible-but-dead AI output:
**never emit fabrication files while any pin is unverified.** Rigor scales with stakes.

## Run the tiers, cheapest first

1. **Inner loop (instant, no network).** Read `dist/<board>/circuit.json` (or call
   `@tscircuit/checks`) for `*_error` / `*_warning`: unconnected or underspecified pins, missing
   power/ground pins, overlaps, clearance. Feed each error back into the source and rebuild clean.

2. **Authoritative ERC.** Export to KiCad, then:
   `kicad-cli sch erc --format json --exit-code-violations <sch>`  (exit 0 = clean, 5 = violations).
   Parse `violations[]`. Once a board exists, `kicad-cli pcb drc` — this is what catches an
   autorouter short or an unmanufacturable via before the fab does.

3. **Pin-truth cross-check.** Diff the netlist against the verified-parts pin maps. Any pin not
   sourced from a `verified: true` entry is flagged for datasheet or bench confirmation.

4. **Firmware simulation (functional).** Wokwi CI for ESP32 firmware: assert serial + GPIO/bus
   activity. Some breakouts are only verifiable from the MCU side.

5. **Analog SPICE (deferred).** Only when a genuine analog subcircuit exists.

## The gate
- **Schematic stage:** warnings allowed; show them to the user.
- **Pre-fabrication stage:** ERC must exit clean AND every pin must trace to a verified part or an
  explicit bench-confirmed reading. Otherwise **refuse to produce Gerbers** and list the open pins.
- Ground truth is always the bench — breadboard the modules before ordering a PCB.

## Honest note
Best current models score only moderately on hardware-design benchmarks; auto-routing is the
weakest link. Human review before fabrication is non-negotiable — say so.
