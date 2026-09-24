# spark — AI electronics design

Describe a circuit (or hand it a board photo) and get a **verified** tscircuit schematic and
PCB. spark bundles the reference knowledge, the verified-parts library, a reverse-engineering
procedure, and a verification gate that refuses to emit a board with unverified part pins — and
wires up the external tools people actually use.

The philosophy: an AI is good at circuit design not through cleverness but through a **knowledge
layer** — verified parts + reference designs + design-rule checklists in the loop. spark is that
layer, plus the workflow that uses it.

## What's in the box (bundled)

Five skills and their reference knowledge:

| Skill | What it does |
| --- | --- |
| **spark-design** | Describe -> tscircuit -> build headless -> grade against design rules & verified parts -> render. |
| **spark-reverse-engineer** | Board photo -> fuse copper-reading + datasheet pinouts + functional wiring -> netlist hypothesis + part guesses -> a bench test protocol to confirm. |
| **spark-simulate** (+ hook) | Test firmware before the hardware exists: injected fakes and a fake `machine` module for offline tests, then Wokwi (browser / CLI / MCP) for the real binary on a simulated chip. Honest about what no simulator proves. |
| **spark-verify** | The gate: tscircuit checks + `kicad-cli` ERC/DRC + pin cross-check; refuses fab output while any pin is unverified. |
| **spark-check** | The five mistakes no EDA tool catches, because no EDA format carries the facts: a wake source on a pin that cannot wake the chip, an analogue input on a digital-only pin, two parts on one pin, a serial module on the boot-log UART, and two I2C devices at one address. Runs in a second, exits non-zero, names the pin. |

Bundled knowledge (in the skills' `references/`): `design-rules.md` (general PCB best practices +
the ESP32-C6/XIAO checklist), `verified-parts.md` (pin maps + provenance + the Seeed-vs-DFRobot
board discriminator), `vendor-knowledge.md` (how to pull verified pin maps, schematics, EDA files
and code examples from Espressif, Seeed and DFRobot), `verification-loop.md`, and a
`test-protocol-template.md` for the bench.

## Hooks

`hooks/hooks.json` runs `make check` after a design file (`*.tsx`, `config.py`, `*.kicad_sch`) is
edited, if the project has a Makefile with a `check` target — so drift between a board, its
firmware and its simulation surfaces in seconds rather than on the bench. See
`skills/spark-simulate/references/keeping-things-in-sync.md` for the four-layer approach it is
part of.

## What you install alongside (declared, not bundled)

spark points at these — install them where you'll use them (license-clean; their code is theirs):

**Companion skills**
- **tscircuit skill** — the engine's own syntax/CLI knowledge:  `npx skills add tscircuit/skill`
- **kicad-happy** — the mature KiCad DRC/EMC/datasheet/BOM checker skills:
  `/plugin marketplace add aklofas/kicad-happy`

**MCP servers** (declared in `.mcp.json` — install the server, then adjust the command if needed)
- **espressif-docs** — official Espressif documentation MCP (datasheets, hardware design guidelines,
  ESP-IDF docs, with citations). Hosted; runs via `npx -y mcp-remote https://mcp.espressif.com/docs`.
- **jlcpcb** — part lookup. Runs via `npx -y @jlcpcb/mcp` (no install needed if you have Node).
- **sigrok** — your bench scope / logic analyzer (e.g. Hantek 6022BL). Install
  [KenosInc/sigrok-mcp-server](https://github.com/KenosInc/sigrok-mcp-server) + `sigrok-cli` on the
  machine the instrument is plugged into (the Pi is ideal), then point the `sigrok` command at the
  built binary. Logic capture + protocol decode work out of the box; analog scope capture may need
  a small wrapper.
- **wokwi** — run a simulation headless and read its serial output: `npm i -g wokwi-cli`, then a
  token from https://wokwi.com/dashboard/ci in `WOKWI_CLI_TOKEN`. The MCP server is experimental.
- **kicad** — a KiCad MCP for layout/DRC/fab (e.g. `uvx kicad-mcp` or a KiCad-plugin server). Adjust
  the command to your install.

> The MCP servers need their binaries present and, for sigrok, the instrument physically plugged
> in. spark declares the wiring; it can't ship the servers or the hardware.

## Toolchain the skills call

- Node + the tscircuit CLI: `npm i -g @tscircuit/cli` (or `npx tsci ...`).
- KiCad 9/10 for `kicad-cli` (ERC/DRC/Gerbers/STEP).
- Optional: Wokwi CI for firmware simulation; a Raspberry Pi as the bench host.

## Honest limits

Verified parts + reference reuse + rule-checking genuinely work. Autonomous production boards and
good auto-routing do not yet — the autorouter can emit shorts or unmanufacturable vias, so the
verify gate + human review before fabrication are non-negotiable.

---
v0.1.0 · MIT · built with the tscircuit engine and the design-rule research captured in the
project doc.
