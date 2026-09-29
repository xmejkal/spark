# spark — checks for a board made of modules

Point it at a design, or at a board you have already built, and it tells you — in a second, item
by item — where the fab package disagrees with the schematic, which capacitors have no voltage
rating, where a drill is too small for the pin that goes in it, and where your board file
disagrees with the vendor's own header.

That is narrower than "AI electronics design", and it is the part that works. The reasoning half
is here too, and it is useful, but the measured value is in the arithmetic: a script runs in a
second, costs nothing, cannot change its mind, and does it identically on the seventieth hole.

## Install

```
/plugin marketplace add xmejkal/spark
/plugin install spark
```

Then, in a project:

```
/spark:init              # writes what the checks need; guesses nothing
/spark:check             # the cheap deterministic pass
```

## The one rule everything here is built around

**A check that could not look must never read as a check that passed.** Every tool reports four
outcomes, not two: `ok`, `problems`, `could-not-run` (it was given what it needs and still could
not look) and `skipped` (it was never asked). The last two are routinely conflated, and the
conflation is dangerous in one direction only — a board nobody examined looks exactly like a
clean one.

The same rule runs through the data: a fact carries a source and whether anyone checked it, an
unverified number must say what depends on it, and a dimension nobody measured makes the board
generator refuse rather than invent one.

## Commands

| | |
| --- | --- |
| `/spark:init` | Writes `.spark/rules.json`, `.spark/project.json` and `boards/active.json`. Names the rails from the built design; leaves **every value null** and lists them. A guessed rail current would poison the one check that does arithmetic. |
| `/spark:check` | The cheap pass: pins, capabilities, shared buses, I²C addresses. Seconds, no agents. |

## Skills

| | |
| --- | --- |
| **spark-review** | Find what is wrong, gate it before fab, and remember it. Runs all seven deterministic checks, then five reviewers (power, signals, thermal-mechanical, manufacturability, firmware-hardware) reading primary artefacts only, into a findings store that survives between sessions. Identity is structural, so the same defect worded differently is one finding, and an anchor the design does not contain refuses the finding outright. |
| **spark-design** | Describe → tscircuit → build headless → grade against design rules and the parts library → render. |
| **spark-simulate** | Test firmware before the hardware exists: a fake `machine` module for offline tests, then Wokwi for the real binary on a simulated chip. Honest about what no simulator proves. |
| **spark-reverse-engineer** | Board photo → copper reading + datasheet pinouts + functional wiring → netlist hypothesis and a bench protocol to confirm it. |

## Scripts

Every one runs standalone and is what the skills above actually call. The checks take
`--json`; `boards`, `check_bom`, `check_design`, `emit_board` and `init_project` do not yet,
and `copper` is a library, not a command.

**The one command**

- `check_all.py --project .` — runs every check below and answers once. Prints the path it
  resolved for each input before reporting anything, because silently picking up a stale artifact
  is the one way discovery is worse than typing the paths.

**The checks**

- `check_design.py` — the mistakes no EDA tool catches, because no EDA format carries the facts:
  a wake source on a pin that cannot wake the chip, an analogue input on a digital-only pin, two
  parts on one GPIO (including one pin brought out under two silkscreen names), a serial module
  on the console UART, and two I²C devices at one address.
- `check_vendor_pins.py` — re-derives the pin map from the vendor's own `pins_arduino.h`. The only
  tool here that consults something outside both the design and the model.
- `check_footprints.py` — drill vs the pin that goes in it, annular ring, via class, package vs
  value, cross-pluggable connectors. Counts the holes it could not read rather than skipping them.
- `check_physics.py` — trace current, capacitor derating, resistor dissipation, I²C rise time.
- `check_bom.py` — the fab package against the schematic it came from.
- `check_firmware.py` — every pin the firmware drives against the board and the agreed pin map,
  matched on GPIO rather than on constant names.
- `compare_design.py` — written rules against the design that was built.

**The libraries and the generators**

- `boards.py` — the board library. A project's own `boards/<id>.json` beats the shipped one.
  Board files carry facts, never decisions, and `--validate` enforces the difference.
- `parts.py` — the parts library, same override rule. Every fact carries a value, a source and
  whether anyone checked; `--unverified` lists what nobody has.
- `assign_pins.py` — a pin map with a reason per pin, spending scarce pins last.
- `emit_board.py` — a module list and a pin map, as tscircuit you can build.
- `init_project.py` — what `/spark:init` runs.
- `findings.py` — the findings store: structural identity, anchor validation, status transitions,
  and a measurement registry so a finding resting on an unmeasured number says so.

## Libraries

`boards/` holds board definitions (Seeed XIAO ESP32-C6, DFRobot FireBeetle 2 ESP32-S3) and
`parts/` holds module definitions. Both are small and both are extensible: a project's own file
of the same name wins, so what you verified yourself is never replaced by an update. See
`boards/README.md` for the schema and for the fact-versus-decision rule that keeps a board file
swappable.

## Hooks

`hooks/hooks.json` runs `make check` after a design file is edited, if the project has a Makefile
with a `check` target — so drift between a board, its firmware and its simulation surfaces in
seconds rather than on the bench.

## What you install alongside (declared, not bundled)

**Companion skills**

- **tscircuit skill** — the engine's own syntax and CLI knowledge: `npx skills add tscircuit/skill`
- **kicad-happy** — mature KiCad DRC/EMC/datasheet/BOM skills:
  `/plugin marketplace add aklofas/kicad-happy`

**MCP servers** (declared in `.mcp.json`; install the server, then adjust the command if needed)

- **espressif-docs** — official Espressif documentation with citations, via
  `npx -y mcp-remote https://mcp.espressif.com/docs`.
- **jlcpcb** — part lookup, via `npx -y @jlcpcb/mcp`.
- **sigrok** — a bench scope or logic analyzer. Needs
  [KenosInc/sigrok-mcp-server](https://github.com/KenosInc/sigrok-mcp-server) plus `sigrok-cli` on
  the machine the instrument is plugged into.
- **wokwi** — headless simulation: `npm i -g wokwi-cli`, plus a token in `WOKWI_CLI_TOKEN`.
- **kicad** — a KiCad MCP for layout/DRC/fab, e.g. `uvx kicad-mcp`.

> These need their binaries present, and sigrok needs the instrument physically plugged in. spark
> declares the wiring; it cannot ship the servers or the hardware.

## Toolchain the skills call

Node and the tscircuit CLI (`npm i -g @tscircuit/cli`, or `npx tsci`). KiCad 9/10 for `kicad-cli`.
Optionally Wokwi CI, and a Raspberry Pi as a bench host.

## Honest limits

The deterministic checks and the libraries do what they say. Auto-routing does not: tscircuit's
autorouter can emit shorts and unmanufacturable vias, so the fab gate and human review before
ordering are not optional.

The reviewer half is less established than the checks. The evidence for it is a handful of eval
runs at n=1–3 whose arms differ by context alone, and none of them exercises a script — so treat
"the reviewers help" as plausible and unproven rather than measured. What is measured is that
every defect found by a script this year was found identically, every time, for free.

Nothing here has been validated on hardware by its author. Ground truth is the bench.

## Tests

```
python3 -m unittest discover -s tests -t tests
```

265 of them, and the rule they follow: a test must **run** the thing, not read it. No assertion on
source text, none that is an arithmetic identity of the function under test, and every check
exercised through the runner with an input that makes it fail. That rule exists because the test
written to catch "a check nobody invokes" asserted that a string appeared in the runner's source
— it verified the check was named, not that it ran, and it stayed green for the whole life of the
bug it was written to prevent.

---
v0.6.0 · MIT · built with the tscircuit engine.
