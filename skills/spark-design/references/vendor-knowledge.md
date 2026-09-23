# Vendor knowledge sources (how to pull verified data into the parts library)

Never hand-invent a part when the vendor publishes it. Priority sources and how to ingest them.

## Espressif (the authority for ESP32)

- **Authoritative pin maps = `pins_arduino.h`.** Each board is a machine-readable C header under
  arduino-esp32 `variants/`. Parse it for every named pin, GPIO, and default bus (I2C/SPI/UART/ADC).
  This is the primary source for an ESP32 verified-parts entry.
  Raw: `raw.githubusercontent.com/espressif/arduino-esp32/master/variants/<board>/pins_arduino.h`
- **Espressif Documentation MCP Server (official, hosted)** — semantic search over datasheets,
  TRMs, the Hardware Design Guidelines, ESP-IDF docs, with source citations. Endpoint
  `https://mcp.espressif.com/docs` (declared in this plugin's `.mcp.json` as `espressif-docs`).
  Tool: `search_espressif_sources(query, language)`. Use it for grounded datasheet lookups instead
  of scraping PDFs.
- **Hardware Design Guidelines schematic checklists** (per chip) = reusable reference sub-schematics
  (power, reset RC + timing, USB, flash, crystal, RF matching, strapping). Cite the section URL.
  `docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/<chip>/schematic-checklist.html`
- **ESP Component Registry** (`components.espressif.com`, API `api.components.espressif.com`,
  OpenAPI at `/apidocs/`) — drivers/BSPs with dependency metadata.
- **Code snippets:** `esp-idf/examples/<category>/<example>/main` and
  `arduino-esp32/libraries/*/examples`. Pair each hardware block with its init snippet.
- **Datasheets** (stable URLs): `espressif.com/sites/default/files/documentation/<part>_datasheet_en.pdf`.

## DFRobot (well-structured; scrape wiki + GitHub — no official API/MCP)

- **Wiki per-SKU** is the canonical hub. New structured format `wiki.dfrobot.com/<sku>/docs/<id>`
  has a tabbed pinout/API reference (semi-structured); legacy format is
  `wiki.dfrobot.com/<Product>_SKU_<SKU>`. Each page offers **pinout table + datasheet ZIP +
  schematic ZIP + dimension PDF + STEP 3D**, and sample code. **The SKU (DFR/SEN/DRI…) is the
  stable primary key** — join wiki, product page, and GitHub library on it.
- **Code + I2C addresses = GitHub org** `github.com/orgs/DFRobot/repositories` (~497 MIT repos,
  strict `DFRobot_<Part>` names, each with `examples/`). Ground-truth for wiring and addresses.
- **CAD:** STEP + schematic ZIP + dimension PDF are provided; **no native KiCad/Eagle footprints** —
  derive the footprint from the dimension PDF (FireBeetle/Beetle pitch is 2.54 mm) and attach STEP.
- **Gravity ecosystem** (model as a first-class field): standardized plug-and-play connectors,
  PH2.0 pitch. 3-pin: green = digital, blue = analog. 4-pin: red = I2C, blue = UART. When a module
  is Gravity, its "connection" collapses to {bus type, color} instead of a bespoke pinout.

## Ingest → verified-parts entry (both vendors)
1. Identity: SKU / board name + revision; source URL (prefer the structured pinout page/header).
2. Pin map: parse the header (Espressif) or wiki table (DFRobot); cross-verify against the schematic
   or a library `examples/` default-pins block. Flag mismatches; mark `verified: true` only when two
   independent sources agree.
3. Footprint: registry/KiCad-lib if it exists, else derive from the dimension PDF + STEP; mark
   "derived, needs verification".
4. Provenance: store every source URL (+ GitHub commit) so each field is traceable.

## Seeed Studio (best-structured for ingestion — open markdown wiki + official EDA libs)

- **The whole wiki is markdown in a public repo:** `github.com/Seeed-Studio/wiki-documents` — each
  product is a `.md` with a consistent `Resources` block (schematic PDF, KiCad footprint, datasheet).
  Scrape the raw `.md`, not the rendered HTML.
- **Official EDA libraries:** `github.com/Seeed-Studio/OPL_Kicad_Library` (a `Seeed Studio XIAO Series
  Library` folder = `.kicad_sym` + `.kicad_mod` + 3D for all XIAO variants and Grove modules); Eagle:
  `OPL_Eagle_Library`. The **whole XIAO family shares ONE 14-pad footprint**, so one entry keys the family.
- **Per-board hardware (best provenance):** `github.com/Seeed-Studio/OSHW-XIAO-Series` — schematic +
  STEP + dimensions + pinout + factory firmware per variant (ESP32-C6 included).
- **Pinout source of truth:** arduino-esp32 `variants/XIAO_ESP32C6/pins_arduino.h` (machine-readable) +
  the C6 pin-multiplexing wiki + the schematic PDF on files.seeedstudio.com.
- **Grove ecosystem** (model as a connector field): standardized 4-pin, fixed order — pin1 yellow =
  SIG/SCL/RX, pin2 white = SIG2/SDA/TX, pin3 red = VCC, pin4 black = GND; types digital/analog/I2C/UART.
  Grove I2C is electrically Qwiic/STEMMA-QT compatible.
- **Code:** `github.com/Seeed-Studio` org (~500 repos, `Seeed_Arduino_*`); XIAO ESP32 uses the espressif
  arduino-esp32 core. No official API/MCP — the GitHub repos ARE the structured feed.

## Other maker vendors
Adafruit & SparkFun (open-source board repos + KiCad/Eagle libs, proven power/USB/reset sub-blocks),
Wokwi (part models for simulation). Prefer a vendor's own verified footprint over any auto-conversion.
