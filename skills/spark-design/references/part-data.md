# Part-data backbone — real footprints, 3D models, datasheets

The single most important thing separating a working tool from a toy: for **every part**, resolve
the authoritative footprint + 3D model + pinout + datasheet from a real source, cache it, and mark
it `verified`. Never ship a generic placeholder footprint to fabrication. This is the verified-parts
waterfall (see `verified-parts.md`) made comprehensive.

## Start from a worked record

Researchers spent about one call in eight learning the schema from spark's source (P80). Read this
one instead — `parts/led-red-5mm.json`, the Kingbright L-7113ID, written from one kept datasheet:

```json
{
  "id": "led-red-5mm", "name": "Kingbright L-7113ID 5 mm red LED", "kind": "indicator",
  "vendor": "kingbright", "sku": "L-7113ID",
  "needs":  [{"signal": "STATUS_LED", "pin": "A", "direction": "out"}],
  "power":  [{"pin": "K", "rail": "ground", "direction": "in"}],
  "pin_order": ["A", "K"],
  "pin_order_proof": {"verified": true, "source": "Package Dimensions: the cathode lead is drawn shorter ...",
                      "cites": {"document": "l-7113id-ver29a", "at": "Package Dimensions, page 1"}},
  "footprint": "pinrow2",
  "facts": {"forward_voltage_v": {"value": 1.9, "verified": true, "source": "typ at IF = 10 mA ...",
                                  "cites": {"document": "l-7113id-ver29a", "at": "Electrical / Optical Characteristics, page 2"}}},
  "host_parts": [{"kind": "series", "pin": "A", "for_current_ma": 5, "why": "limits the current from a 3.3 V GPIO"}],
  "host_requirements": ["On a breadboard: the LONG lead (anode) goes to the resistor ..."],
  "documents": {"l-7113id-ver29a": {"url": "https://www.kingbright.com/...", "sha256": "...", "file": "L-7113ID(Ver.29A).pdf",
                                    "title": "...", "version": "Rev V.29A, 09/04/2020 (Spec No DSAA6645)"}}
}
```

What makes it a good record: every fact cites a page of a kept document; the pin order says how it
was read; the warning a person must see is in `host_requirements`, which spark prints; the series
resistor is asked for by the current it is for, and spark computes the value. What it leaves out on
purpose (W21): prices, stock, and facts no decision reads.

## Source waterfall (try in order; record which source + a link as provenance)
1. **tscircuit registry** — `tsci add <author>/<part>` (e.g. `seeed/xiao-esp32-c6`). Brings a real
   footprint AND a 3D model AND the pin map, usable directly in the `.tsx`. First choice when a part exists.
2. **JLCPCB / LCSC** — the largest single library. Key on the **LCSC part number (C…)**:
   `footprint="jlcpcb:C…"` in tscircuit, or `easyeda2kicad` / the `@jlcpcb/mcp` server → real
   footprint + 3D + parametric data + stock/price. Best for jellybean and catalog parts.
3. **Manufacturer** — the authoritative pinout/dimensions/3D STEP:
   - Espressif: `pins_arduino.h` variant header + the Espressif Docs MCP (datasheets/HDG).
   - Seeed: OPL_Kicad_Library (symbols/footprints; the XIAO family shares one 14-pad footprint) +
     OSHW-XIAO-Series (schematic + STEP + pinout per variant).
   - DFRobot: per-SKU wiki pinout + schematic ZIP + STEP + dimension PDF (derive footprint from the
     dimension PDF; DFRobot ships no KiCad footprints) + the `DFRobot_<Part>` GitHub examples.
   - Bare ICs (TB6612, MAX98357A, DRV8833…): the manufacturer datasheet pinout + KiCad official lib.
4. **Aggregators** — SnapEDA / Ultra Librarian / ComponentSearchEngine: per-part symbol + footprint
   + 3D, fetched on demand. Do NOT mirror wholesale (licensing).
5. **KiCad official libraries** — footprints + 3D for standard passives, connectors, common ICs.

## What to store per part (the cache = the verified-parts library)
- symbolic pin label → physical pin/pad number/GPIO (the indirection AI gets wrong)
- footprint reference (registry id / LCSC C-number / KiCad lib id) and its source
- 3D model reference (registry / STEP file)
- datasheet URL, operating voltage, key ratings
- `verified: true|false` + provenance link. Nothing goes to fab while any pin is unverified.

## Honest environment note
Fetching any of the above needs outbound network to those registries. A **restricted sandbox
(like some cloud sessions) blocks them** — `npm.tscircuit.com`, jsdelivr, easyeda can be denied by
egress policy — so the design falls back to **generic footprints** (soic8/soic14/pinrow) as
placeholders and the 3D looks like anonymous chips. Run the plugin where the network is open (the
user's own machine) to pull the real parts; then the footprints, pad layouts and 3D become the
actual modules. State this to the user rather than pretending the placeholder is the real part.

## Auto-solve or ask (layout)
When placement/DRC errors appear (part off-board, decoupling too far from its pin, overlap), the
plugin should FIX them automatically where the fix is unambiguous — snap decoupling caps hard
against their IC power pin, pull parts inside the board edge, spread overlaps — and only ASK the
user when the intent is ambiguous (board outline, connector positions, which side a part goes).
Never leave the user hand-nudging coordinates. tscircuit's own autorouter is too beta for this
(its 1 mm decoupling-proximity rule can't be satisfied for multi-cap pins); own the
placement + Freerouting + `kicad-cli` DRC-fix loop from `pcb-layout.md` instead.
