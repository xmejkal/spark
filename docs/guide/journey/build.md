# Build

Step 4 of 8 in [the journey](../journey.md). Next: [Checks](checks.md).

**Works.** On 2026-11-01 an SPI and an I2C part built with 0 errors on the FireBeetle 2 and the XIAO ESP32-C6 ([P512](https://github.com/xmejkal/spark/issues/708)). A display on the XIAO still stops at the simulation, because the display has no Wokwi part. Two commands come before the first build, in this order:

1. [`/spark:init`](../../../commands/init.md) writes the project's files, guessing nothing, including the `package.json`
   that tscircuit installs into.
2. [`/spark:setup`](../../../commands/setup.md) says which tools spark needs, and installs what is missing in one go once
   you have seen the commands and said yes.

**The plugin's name.** Claude Code can show the plugin as `spark@<marketplace>`. The marketplace name is the `name` field
of spark's `.claude-plugin/marketplace.json`.

**Before you start.** You need Claude Code for the commands, Python 3.9 or newer, and Node 20 or newer. On macOS,
spark's install lines get Node and pdftotext from Homebrew (`data/tools.json`). `/spark:setup` then installs the rest
in one go, after you see the commands and say yes: bun, tscircuit (into the project), `wokwi-cli`, MicroPython and
`littlefs-python`. The runs here were on macOS. Every build for these docs used an existing tscircuit install, not one
that `/spark:setup` made.

**On Linux,** `data/tools.json` has apt lines only for pdftotext and `sigrok-cli`, so you install Node yourself.
If Node's global folder is yours, as with nvm, `/spark:setup` then installs bun with `npm install -g bun`. With a Node
from apt, root owns that folder. Then that line fails, `tools.py` says so and exits 2, and you install bun yourself too.
None of this was run on Linux here. `data/tools.json` has no lines for Windows.

**An update replaces the plugin, not your files.** Your store and a project's own `boards/`, `parts/` and `.spark/` are
outside it ([how it works](../how-it-works.md#your-store)). Three things write inside the plugin, and an update replaces
what they wrote:

- `parts.py --promote` copies a record into spark's library. To keep the record, copy it out first.
- `check_vendor_pins.py` run without `--offline` on a board spark ships refreshes the vendor's pin header that spark
  keeps for that board.
- `/spark:build` can compile a library part's simulation chip beside its record.

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/init_project.py" --project . --board firebeetle2-esp32s3
```

<!-- output: run 2026-10-05, spark 0.6.0 -->
```text
spark init in my-gadget
  on your projects list as 'my-gadget'
  wrote rules.json
  wrote project.json
  wrote package.json
  wrote active.json
  no built design found, so the rails are empty — build, then re-run with --force

5 field(s) nobody has answered. Nothing here is guessed, and a check reading a null
reports it as unverifiable rather than passing it:

  rules.json  physics.i2c_hz
  rules.json  physics.i2c_bus_capacitance_pf
  project.json  goal
  project.json  prefer
  project.json  sellers
```

init's last sentence claims more than physics does today; see [what never to assume](../agents/never-assume.md).

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/tools.py" --status --project .
```

<!-- output: run 2026-10-05, spark 0.6.0 -->
```text
  spark's tools — personal: ~/.local/share/spark/tools.json · project: .spark/tools.json

  [off ] bench             sigrok is off unless you turn it on — /spark:setup add sigrok
  [ok  ] board-engine      tscircuit — my-gadget/node_modules/.bin/tsci
  [ok  ] chip-docs         espressif-docs (MCP, spark's own)
  [ok  ] diagram-converter circuit-to-wokwi — $CLAUDE_PLUGIN_ROOT/tools/circuit-to-wokwi/dist/converter.mjs
  [????] firmware-image    firmware-image (micropython-esp32s3) is not installed — install: /spark:setup add micropython-esp32s3
  [ok  ] js-runtime        node — ~/.nvm/versions/node/v22.23.2/bin/node
  [ok  ] littlefs          littlefs-python — ~/.pyenv/versions/3.10.0/bin/python3
  [ok  ] parts-search      jlcpcb (MCP, spark's own)
  [ok  ] pdf-text          pdftotext — /opt/homebrew/bin/pdftotext
  [ok  ] simulator         wokwi-cli — ~/.local/bin/wokwi-cli
  [ok  ] ts-runtime        bun — /opt/homebrew/bin/bun
  [off ] wokwi-mcp         wokwi-mcp is off unless you turn it on — /spark:setup add wokwi-mcp

  1 to install: micropython-esp32s3
```

What this status shows:

- **tscircuit was linked in, not installed.** It was linked into the project from an existing install, so
  board-engine reads `[ok  ]`. In a fresh folder it reads `[????]` until `/spark:setup` installs it. On this Mac,
  before the link, the last line read `2 to install: tscircuit micropython-esp32s3`. Setup's install of tscircuit
  (`tools.py --install`) last ran on 2026-10-03, in P82's third cold run; the slash command's one yes last ran on
  2026-10-04, for the MicroPython build only
  ([P82 in the backlog's archive](../../../scrum/PRODUCT_BACKLOG.md#p82--setting-up-spark-is-one-step-like-installing-a-package--slice-1-the-pos-request-of-2026-10-03--done-2026-10-03)).
- **Exit 2.** The status exits 2 while any tool is missing. Here only the MicroPython image is missing, and only a
  simulation run needs it ([Simulate](simulate.md#simulate)).
- **An MCP row's `[ok  ]`** (chip-docs, parts-search) means only that spark declares the server and Node is on the
  PATH. Nothing checks that Claude Code has the server registered or that it answers
  ([P112](https://github.com/xmejkal/spark/issues/46)), or the Node version; espressif-docs needs Node 20 or newer
  ([docs/mcp.md](../../mcp.md)).
- **No `[!   ]` simulator row here.** This shell had a Wokwi token set. Without `WOKWI_CLI_TOKEN`, the simulator gets a
  `[!   ]` row: a token only you can make, at wokwi.com/dashboard/ci.

The library's parts, whose ids a requirements file names:

<!-- runs: exit 0 -->
```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/parts.py" --list
```

<!-- output: run 2026-10-08, spark 0.7.0 -->
```text
  dfr0534-module               audio          library   DFRobot DFR0534 voice module
  jst-ph-2-power-inlet         connector      library   JST PH 2-pin power inlet
  l9110s-module                motor-driver   library   L9110S dual motor driver module
  led-red-5mm                  indicator      library   Kingbright L-7113ID 5 mm red LED
  max98357a-dfr0954            audio-amplifier library   DFRobot DFR0954 MAX98357A I2S amplifier
  speaker-terminal             connector      library   2-pin speaker terminal (JST PH)
  tactile-button               button         library   6x6 mm tactile push button
  vl6180x-breakout             rangefinder    library   VL6180X time-of-flight rangefinder breakout
```

`parts.py --audit` names what each record still owes.

Save the requirements file as `requirements.json` in the project:

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

What else a requirements file takes ([`/spark:build`'s page](../../../commands/build.md#the-requirements-file)):

- each part as an id, or as `{part, name}` when the same part appears twice — names that differ only in capitals are
  one name, and the requirements stage refuses the file, naming both, before anything is emitted;
- a part's `rails`, which puts one of its power pins on a rail you name without copying its record;
- `signals`, entries of `{name, needs}`, which add a pin no part claims (an LED, a limit switch).

Then [`/spark:build`](../../../commands/build.md) runs the whole chain on it:

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/check_spine.py" requirements.json --keep .
```

The lines are a dated record. Since 2026-10-12 the two buttons use the board's internal pull-up
([P204](https://github.com/xmejkal/spark/issues/167)), so today's run writes 18 traces, routes 15 and wires 13.

<!-- output: run 2026-10-11, spark 0.8.1 -->
```text
wrote <temp>/FireBeetle2Esp32S3.tsx (32 pads, 1.00 mm holes)
  wrote FireBeetle2Esp32S3.tsx
  wrote board.tsx
  wrote dist — this is what every check reads
  wrote breadboard.md — the parts and how to wire them on a breadboard

  idea -> parts -> pin map -> schematic -> footprint -> build -> simulation

  [ok  ] board            DFRobot FireBeetle 2 ESP32-S3
  [ok  ] schematic        22 trace(s) written
  [ok  ] footprint        FireBeetle2Esp32S3.tsx
  [ok  ] build            19 trace(s), 0 errors, tsci 0.0.2621; the documents were measured on core 0.0.2600
  [ok  ] simulation       17 wire(s) in the diagram, 1 chip(s): 0 compiled, 1 reused
           what it cannot show, from the records (3):
             BtnMode, BtnOpen: Wokwi's pushbutton: either side of a pair is the same contact; no bounce is modelled
             JstPh2PowerInlet: not simulated at all: a connector is wiring, not a part to simulate; the simulator powers the board itself
             L9110sModule: one channel: reads IA/IB and prints MOTOR: opening/closing/stopped; models no current, so a stall cannot be simulated

  the chain runs end to end
```

19 routed traces carry the 22 written connections: a group of N connected pins needs N−1 traces.

`--keep .` writes the board into the project: `board.tsx`, the board's footprint and `dist/`, where every
check looks. An existing `board.tsx` is left alone, edited or not, and `dist/` is then built from the requirements file, not
from your `board.tsx` ([P110](https://github.com/xmejkal/spark/issues/44)). It also writes `firmware/pins.py`, the pins
that the firmware imports ([P196](https://github.com/xmejkal/spark/issues/155)). Without `--keep`, the chain builds in a temporary
folder and deletes it.

The simulation stage generates the Wokwi diagram and stages the chips. `--keep .` keeps them in `sim/`, and `--sim-dir DIR`
keeps them in DIR ([P116](https://github.com/xmejkal/spark/issues/50)). It does not run a simulation; see [Simulate](simulate.md#simulate).

**Today, in full.** A requirements file becomes a board that builds, with a Wokwi diagram generated from it, or the
stage that stopped it. `--board`, and a requirements file's `board`, name the dev board. With `--keep`, the build also
writes:

- a breadboard sheet, `breadboard.md`: the parts and how to wire them ([an example](recorded-run.md#a-recorded-run-a-button-and-an-led))
- for a XIAO ESP32-C6, the same wiring drawn on a Wokwi breadboard ([P267](https://github.com/xmejkal/spark/issues/300)) and as a picture that the sheet shows
  ([P268](https://github.com/xmejkal/spark/issues/302))
- for a FireBeetle 2 ESP32-S3, a picture alone, drawn from its record ([P412](https://github.com/xmejkal/spark/issues/538))
- a page with the breadboard, schematic and PCB in three tabs ([P271](https://github.com/xmejkal/spark/issues/307))

A rebuild keeps the parts, jumpers and resistors you moved in `breadboard.json`. It names those it cannot keep
([P273](https://github.com/xmejkal/spark/issues/309), [P287](https://github.com/xmejkal/spark/issues/340)). A rebuild lists what to change on the bench, by each jumper's ends and color
([P300](https://github.com/xmejkal/spark/issues/366)). The build names an end that the drawing joins differently from the circuit ([P279](https://github.com/xmejkal/spark/issues/317)). With
`"board_only": true`, the build skips the parts, schematic, footprint and build stages and simulates the board alone,
for firmware that uses only the board's own LED and button ([P236](https://github.com/xmejkal/spark/issues/233)). Where a fact is missing, the build names its stand-in in `board.tsx`: a placeholder outline in its
header, or the router's default trace width under a power trace it was unable to size.

**The XIAO ESP32-C6, then and now.** On 2026-10-08 the library defined two dev boards and held 8 parts
(`boards.py --list`, `parts.py --list`). Only the FireBeetle 2 ESP32-S3 built then. The Seeed XIAO ESP32-C6 was defined
for the pin map only. Its file recorded no header geometry and no `power.io_volts`. So `/spark:build` stopped at the
schematic stage ([P121](https://github.com/xmejkal/spark/issues/55)). Since 2026-10-18 its file holds the facts of the record that was checked at the
bench, with their cites. Button + LED on `"board": "xiao-esp32-c6"` builds with `--keep` ([P278](https://github.com/xmejkal/spark/issues/314)). A
board file with no header geometry still stops at the footprint stage.
