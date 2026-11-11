# Part-data backbone: real footprints, 3D models, datasheets

A working tool differs from a toy in one thing. For **every part**, it resolves the footprint, the 3D model, the
pinout and the datasheet from a real source. It caches them and marks them `verified`. Never ship a generic placeholder
footprint to fabrication. This page extends the waterfall of `verified-parts.md` to every part.

## Start from a worked record

Researchers spent about one call in eight learning the schema from spark's source (P80). Read this record instead.
It is `parts/led-red-5mm.json`, the Kingbright L-7113ID, written from one kept datasheet:

```json
{
  "id": "led-red-5mm", "name": "Kingbright L-7113ID 5 mm red LED", "kind": "indicator",
  "vendor": "kingbright", "sku": "L-7113ID",
  "needs":  [{"signal": "STATUS_LED", "pin": "A", "direction": "out"}],
  "power":  [{"pin": "K", "rail": "ground", "direction": "in"}],
  "pin_order": ["A", "K"],
  "legs": {"A": "the anode, the longer leg", "K": "the cathode, the shorter leg, by the flat of the rim"},
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

What makes it a good record:

- Every fact cites a page of a kept document.
- The pin order says how it was read.
- The series resistor is asked for by the current it is for, and spark computes the value.
- `host_requirements` holds each warning that a person must see, and spark prints it. It is in the record format
  since parts became data (2026-09-24).
- `legs` is optional and keyed by the pin names in `pin_order`. It names each pin as a person finds it on the part,
  and the breadboard sheet prints it ([P191](https://github.com/xmejkal/spark/issues/143)).
- `parts.py --fact-set` writes both keys: `legs` leg by leg, and `host_requirements` as one whole list
  ([P741](https://github.com/xmejkal/spark/issues/1017)).

A pull-up that the board's internal one can do says `"internal_will_do": true`. On a board that states
`internal_pull_up_ohms`, spark places no resistor, and `pins.py` tells the firmware to pull the pin up. A pin that
wakes the chip is the exception ([P204](https://github.com/xmejkal/spark/issues/167)).
What the record leaves out on purpose (W21): prices, stock, and facts no decision reads.

## Source waterfall (try in order, and record the source and a link as provenance)
1. **tscircuit registry**: `tsci add <author>/<part>`, for example `seeed/xiao-esp32-c6`. It brings a real
   footprint, a 3D model and the pin map, usable directly in the `.tsx`. If a part exists there, use it first.
2. **JLCPCB / LCSC**: the largest single library. Key on the **LCSC part number (C…)**:
   `footprint="jlcpcb:C…"` in tscircuit, or `easyeda2kicad` or the `@jlcpcb/mcp` server. These give a real
   footprint, 3D, parametric data, stock and price. Best for jellybean and catalog parts.
3. **Manufacturer**: the authoritative pinout, dimensions and 3D STEP.
   - Espressif: the `pins_arduino.h` variant header and the Espressif Docs MCP (datasheets, HDG).
   - Seeed: OPL_Kicad_Library (symbols and footprints, and the XIAO family shares one 14-pad footprint) and
     OSHW-XIAO-Series (schematic, STEP and pinout per variant).
   - DFRobot: the per-SKU wiki pinout, the schematic ZIP, the STEP, the dimension PDF and the `DFRobot_<Part>`
     GitHub examples. For some SKUs a layout zip holds a KiCad footprint and symbol (DFR1117 for one). For the
     others, derive the footprint from the dimension PDF.
   - Bare ICs (TB6612, MAX98357A, DRV8833…): the manufacturer datasheet pinout and the KiCad official lib.
4. **Aggregators**: SnapEDA, Ultra Librarian, ComponentSearchEngine. They give a symbol, a footprint and 3D per part,
   fetched on demand. Do NOT mirror them wholesale (licensing).
5. **KiCad official libraries**: footprints and 3D for standard passives, connectors and common ICs.

## What to store per part (the cache is the verified-parts library)
- symbolic pin label → physical pin, pad number or GPIO (the indirection AI gets wrong)
- footprint reference (registry id, LCSC C-number or KiCad lib id) and its source
- 3D model reference (registry or STEP file)
- datasheet URL, operating voltage, key ratings
- `verified: true|false` and a provenance link. Nothing goes to fab while any pin is unverified.

## Honest environment note
Fetching any of the above needs outbound network to those registries. **A restricted sandbox, such as some cloud
sessions, blocks them**: egress policy can deny `npm.tscircuit.com`, jsdelivr and easyeda. Then the design falls
back to **generic footprints** (soic8, soic14, pinrow) as placeholders, and the 3D looks like anonymous chips. Run
the plugin where the network is open, on the user's own machine, to pull the real parts. Then the footprints, pad
layouts and 3D become the actual modules. Tell the user this, and do not pretend that the placeholder is the real
part.

## Auto-solve or ask (layout)
Placement and DRC errors include a part off the board, decoupling too far from its pin, and overlap. If the fix is
unambiguous, the plugin fixes them automatically. It snaps decoupling caps hard against their IC power pin, pulls
parts inside the board edge and spreads overlaps. If the intent is ambiguous, it asks the user: the board outline,
the connector positions, which side a part goes. Never leave the user hand-nudging coordinates. tscircuit's own
autorouter is too beta for this. Its 1 mm decoupling-proximity rule cannot be met for pins with more than one cap.
Own the placement, Freerouting and `kicad-cli` DRC-fix loop from `pcb-layout.md` instead.
