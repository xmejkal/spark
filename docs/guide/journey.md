# The journey

spark takes a gadget from an idea in words toward a board that builds and is checked, with a Wokwi diagram generated
from it. Today the chain starts from a [requirements file](../../GLOSSARY.md#the-requirements-file); nothing yet
writes one from a vague idea with no parts named ([P76](https://github.com/xmejkal/spark/issues/5)). Each step reports
what it could not look at; [what never to assume](agents.md#what-never-to-assume) lists where that does not hold yet.

This page walks each step on real runs: what was typed, what spark printed, what it wrote, and where the step stops
today.

```mermaid
flowchart LR
    drawer["Drawer — partly"] --> idea["Idea — partly"] --> research["Research — partly"]
    research --> build["Build — works"] --> checks["Checks — works"] --> firmware["Firmware — partly"]
    firmware --> simulate["Simulate — partly"] --> bench["Bench — not yet"]
```

The same journey in words:

1. Your drawer says what you own.
2. An idea becomes needs, matched against your drawer and spark's records first.
3. Research fills a real gap.
4. A requirements file becomes a board that builds, with a Wokwi diagram generated from it.
5. The checks say what holds.
6. The firmware imports the pin map.
7. A simulation runs the firmware on the diagram.
8. The bench proves it on hardware.

What the three words mean:

- **works**: it ran end to end for these docs.
- **partly**: it stops before its goal, or part of it was not run here (agents, a conversation, or a paid simulation
  run); the section says which.
- **not yet**: nothing does it yet; the linked issue plans it.

**How these runs were made.**

- When: 2026-10-05, and the exports on 2026-10-06, with spark 0.6.0 and tscircuit 0.0.2600, the version spark pins.
  The tscircuit came from an existing install, linked into the project.
- Where: in two fresh project folders that share one scratch store, so the drawer filled in [Drawer](#drawer) is the
  one [Idea](#idea)'s match reads.
- How: each command typed as shown. In Claude Code you type the `/spark:` command, and Claude runs these scripts for
  you. You, or another AI, can run them directly; [the guide for AI agents](agents.md) says how.
- Paths: `$CLAUDE_PLUGIN_ROOT` is where spark is installed. In outputs, `~/` is the home folder, `<temp>` a temporary
  one, the scratch store is shown as `~/.local/share/spark`, and each project folder by its name.

There are two example projects:

- `plant-alarm` holds the drawer and idea steps. Its goal is the one `/spark:idea`'s own page uses.
- `my-gadget` holds the rest. It uses the requirements file that `/spark:build`'s page documents: a DFRobot
  FireBeetle 2 ESP32-S3, an L9110S motor driver, a power inlet and two buttons.

## Drawer

**Partly.** [`/spark:drawer`](../../commands/drawer.md) keeps what you own in your own store, never in a repository.

You say what you own in plain words. Claude writes the entries to a file and shows what would change:

```json
[
  {"label": "FireBeetle 2 ESP32-S3", "count": 1, "is": {"board": "firebeetle2-esp32s3"}},
  {"label": "red LEDs, pack of 10", "count": 10, "function": [{"does": "indicate", "what": "light"}]}
]
```

The conversation was not run for this page. These entries were written by hand; the commands below are real runs.

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/parts.py" --drawer-set ../drawer.json --dry-run
```

<!-- output: run 2026-10-05, spark 0.6.0 -->
```text
  would add firebeetle-2-esp32-s3: FireBeetle 2 ESP32-S3 × 1 — is board firebeetle2-esp32s3
  would add red-leds-pack-of-10: red LEDs, pack of 10 × 10
```

Without `--dry-run` it writes them. Then the drawer lists them:

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/parts.py" --drawer
```

<!-- output: run 2026-10-05, spark 0.6.0 -->
```text
  FireBeetle 2 ESP32-S3                             1  board firebeetle2-esp32s3
  red LEDs, pack of 10                             10  —
  2 entries
```

Your DFRobot order history can also come in from your logged-in browser, through Claude in Chrome:

- Claude drives your Chrome on dfrobot.com/account/order.
- spark's extractor reads each order page there and hands back only each line's SKU, name and count: no page text,
  address or price.
- Two things are rules Claude follows from the drawer's page, not something code enforces: it reads the order pages no
  other way (no page text, no accessibility tree, no screenshot), and it never types credentials or solves a challenge.
- The same page also lets Claude adapt the extractor when DFRobot changes its pages.

This path was not run here.

## Idea

**Partly.** [`/spark:idea`](../../commands/idea.md) turns a goal in your words into needs, then matches each need
against your drawer and spark's records. It stops once each need is marked: have, have-unknown, know or gap. Not built
yet:

- choosing and reserving parts ([P97](https://github.com/xmejkal/spark/issues/18));
- turning needs into a requirements file ([P76](https://github.com/xmejkal/spark/issues/5)).

In Claude Code, Claude asks at most three questions, one at a time, then writes the needs to a file:

- each need is a verb and a few words;
- no part numbers;
- a `condition` only when it decides a part.

For *"tell me when my plant is thirsty"*:

```json
[
  {"id": "soil", "does": "sense", "what": "soil-moisture", "condition": "indoor pot, short probe; low power"},
  {"id": "alarm", "does": "indicate", "what": "alarm"},
  {"id": "board", "does": "compute", "what": "microcontroller"}
]
```

The conversation was not run for this page. These needs were written by hand from `/spark:idea`'s own example; the
commands below are real runs.

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/parts.py" --needs-set . ../needs.json
```

<!-- output: run 2026-10-07, spark 0.6.0 -->
```text
  set soil: does null → "sense"; what null → "soil-moisture"; condition null → "indoor pot, short probe; low power"
  set alarm: does null → "indicate"; what null → "alarm"
  set board: does null → "compute"; what null → "microcontroller"
```

The same command with `--dry-run` first shows these lines as *would set*. The needs land in `.spark/needs.json`.

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/parts.py" --match .
```

<!-- output: run 2026-10-05, spark 0.6.0 -->
```text
  soil — sense / soil-moisture  (indoor pot, short probe; low power)
                 vl6180x-breakout (library)                     distance [other words]  owes body_mm
  alarm — indicate / alarm
      owned 10   red-leds-pack-of-10 (drawer)                   light [other words]  free 10
                 led-red-5mm (library)                          light [other words]
  board — compute / microcontroller
      owned 1    firebeetle2-esp32s3 (library)                  microcontroller  free 1
                 xiao-esp32-c6 (library)                        microcontroller
```

How to read the matches:

- Owned parts come first, from the drawer above, with how many are free.
- `owes` names facts a [record](../../GLOSSARY.md#record--and-the-three-places-one-lives) lacks:
  - without a footprint or a pin order, the build stops;
  - without an outline (`body_mm`), `/spark:build` draws a declared placeholder size, and every stage still reads
    `[ok]` ([P115](https://github.com/xmejkal/spark/issues/49));
  - without `simulation`, the simulation stage cannot run.
- `[other words]` marks a looser match: the part does the same thing (*sense*, *indicate*) but names a different object
  (*distance*, *light*). Whether that fits is Claude's call, and Claude says so to you.

Here a distance sensor is offered for soil moisture. It senses distance, not moisture, so soil moisture is a real gap.
Research is for that.

## Research

**Partly.** The library comes first:

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/parts.py" --need motor driver --project .
```

<!-- output: run 2026-10-05, spark 0.6.0 -->
```text
  l9110s-module                motor-driver   L9110S dual motor driver module
```

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/parts.py" --need soil moisture --project .
```

<!-- output: run 2026-10-05, spark 0.6.0 -->
```text
  nothing in the library matches 'soil moisture'.
  Research it: /spark:research "soil moisture"  — vendors in order: dfrobot, seeed; sellers: none named in the brief
```

*The brief* is the project's `.spark/project.json`.

A real gap goes to [`/spark:research`](../../commands/research.md), which works through agents:

- For a commodity part (an LED, a button, a connector: one datasheet describes it), `part-finder` finds the exact
  part on the maker's site.
- `datasheet-reader` then fills the record from the datasheet pages the decision needs.
- For a module, `parts-researcher` researches it from primary sources.

Either way the result is a record in the project's `parts/`, with every fact cited and every unconfirmed fact marked.
Another project finds it once `parts.py --promote <id> --project .` copies it into spark's library, or once a drawer
entry links it, which puts a copy on your shelf. That part runs as agents in a conversation and was not run for this
page.

A module you already own can start from a photo instead: [`/spark:identify`](../../commands/identify.md).

## Build

**Works.** Two commands come before the first build, in this order:

1. [`/spark:init`](../../commands/init.md) writes the project's files, guessing nothing, including the `package.json`
   that tscircuit installs into.
2. [`/spark:setup`](../../commands/setup.md) says which tools spark needs, and installs what is missing with one yes.

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

init's last sentence claims more than physics does today; see [what never to assume](agents.md#what-never-to-assume).

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
  ([P82 in the backlog's archive](../../scrum/PRODUCT_BACKLOG.md#p82--setting-up-spark-is-one-step-like-installing-a-package--slice-1-the-pos-request-of-2026-10-03--done-2026-10-03)).
- **Exit 2.** The status exits 2 while any tool is missing. Here only the MicroPython image is missing, and only a
  simulation run needs it ([Simulate](#simulate)).
- **An MCP row's `[ok  ]`** (chip-docs, parts-search) means only that spark declares the server and Node is on the
  PATH. Nothing checks that Claude Code has the server registered or that it answers
  ([P112](https://github.com/xmejkal/spark/issues/46)), or the Node version; espressif-docs needs Node 20 or newer
  ([docs/mcp.md](../mcp.md)).
- **No `[!   ]` simulator row here.** This shell had a Wokwi token set. Without `WOKWI_CLI_TOKEN`, the simulator gets a
  `[!   ]` row: a token only you can make, at wokwi.com/dashboard/ci.

The library's parts, whose ids a requirements file names:

<!-- runs: exit 0 -->
```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/parts.py" --list
```

<!-- output: run 2026-10-06, spark 0.6.0 -->
```text
  dfr0534-module               audio          library   DFRobot DFR0534 voice module
  jst-ph-2-power-inlet         connector      library   JST PH 2-pin power inlet
  l9110s-module                motor-driver   library   L9110S dual motor driver module
  led-red-5mm                  indicator      library   Kingbright L-7113ID 5 mm red LED
  max98357a-dfr0954            audio-amplifier library   DFRobot DFR0954 MAX98357A I2S amplifier
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

What else a requirements file takes ([`/spark:build`'s page](../../commands/build.md#the-requirements-file)):

- each part as an id, or as `{part, name}` when the same part appears twice;
- a part's `rails`, which puts one of its power pins on a rail you name without copying its record;
- `signals`, entries of `{name, needs}`, which add a pin no part claims (an LED, a limit switch).

Then [`/spark:build`](../../commands/build.md) runs the whole chain on it:

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/check_spine.py" requirements.json --keep .
```

<!-- output: run 2026-10-05, spark 0.6.0 -->
```text
wrote <temp>/FireBeetle2Esp32S3.tsx (32 pads, 1.00 mm holes)
  wrote FireBeetle2Esp32S3.tsx
  wrote board.tsx
  wrote dist — this is what every check reads

  idea -> parts -> pin map -> schematic -> footprint -> build -> simulation

  [ok  ] board            DFRobot FireBeetle 2 ESP32-S3
  [ok  ] schematic        22 trace(s) written
  [ok  ] footprint        FireBeetle2Esp32S3.tsx
  [ok  ] build            19 trace(s), 0 errors, tsci 0.0.2600
  [ok  ] simulation       17 wire(s) in the diagram, 1 chip(s): 0 compiled, 1 reused
           what it cannot show, from the records (3):
             BtnMode, BtnOpen: Wokwi's pushbutton: either side of a pair is the same contact; no bounce is modelled
             JstPh2PowerInlet: not simulated at all: a connector is wiring, not a part to simulate; the simulator powers the board itself
             L9110sModule: one channel: reads IA/IB and prints MOTOR: opening/closing/stopped; models no current, so a stall cannot be simulated

  the chain runs end to end
```

19 routed traces carry the 22 written connections: a group of N connected pins needs N−1 traces.

`--keep .` writes the board into the project: `board.tsx`, the board's footprint, and `dist/`, where every check
looks. An existing `board.tsx` is left alone, edited or not, and `dist/` is then built from the requirements file, not
from your `board.tsx` ([P110](https://github.com/xmejkal/spark/issues/44)). Without `--keep`, the chain builds in a
temporary folder and deletes it.

The simulation stage generates the Wokwi diagram and stages the chips in a temporary folder. It deletes them unless
`--sim-dir sim` keeps them; `--keep .` does not ([P116](https://github.com/xmejkal/spark/issues/50)). It does not run a
simulation; see [Simulate](#simulate).

## Checks

**Works.** After a build, running init again with `--force` names the rails from the board. It lists the fields it
writes as `null`. Until a bug is fixed, it lists them even when `.spark/rules.json` already holds your answer
([P114](https://github.com/xmejkal/spark/issues/48)), so the values in that file are what count:

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/init_project.py" --project . --board firebeetle2-esp32s3 --force
```

<!-- output: run 2026-10-05, spark 0.6.0 -->
```text
spark init in my-gadget
  on your projects list as 'my-gadget'
  merged into rules.json — every answer already in it was kept
  wrote project.json
  package.json already exists, left alone
  wrote active.json
  named 3 rail(s) from circuit.json

17 field(s) nobody has answered. Nothing here is guessed, and a check reading a null
reports it as unverifiable rather than passing it:

  rules.json  physics.i2c_hz
  rules.json  physics.i2c_bus_capacitance_pf
  rules.json  physics.rails.GND.nominal_volts
  rules.json  physics.rails.GND.max_current_a
  rules.json  physics.rails.GND.capacitor_chemistry
  rules.json  physics.rails.GND.served_by_pour
  rules.json  physics.rails.MOTOR6V.nominal_volts
  rules.json  physics.rails.MOTOR6V.max_current_a
  rules.json  physics.rails.MOTOR6V.capacitor_chemistry
  rules.json  physics.rails.MOTOR6V.served_by_pour
  rules.json  physics.rails.V33.nominal_volts
  rules.json  physics.rails.V33.max_current_a
  rules.json  physics.rails.V33.capacitor_chemistry
  rules.json  physics.rails.V33.served_by_pour
  project.json  goal
  project.json  prefer
  project.json  sellers
```

Its last sentence overclaims here too, as above. The motor rail's net is named `MOTOR6V` whatever the motor's voltage
([P129](https://github.com/xmejkal/spark/issues/63)). A part's `rails` puts its pin on a rail you name instead.

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/check_all.py" --project .
```

<!-- output: run 2026-10-05, spark 0.6.0 -->
```text
  resolved from .:
    circuit      dist/board/circuit.json
    rules        .spark/rules.json
    package      not found (looked for *-gerbers.zip, fab/*.zip)
    boards       2 definition(s): firebeetle2-esp32s3, xiao-esp32-c6

  [ok  ] vendor-truth       the board definition matches the vendor's own pin header
  [ok  ] buildability       holes take their pins, packages hold their values
           ? JstPh2PowerInlet: pad 1.20 mm around a 0.75 mm hole leaves 0.225 mm of ring: over the 0.18 mm this process can make, under the 0.25 mm it recommends
  [--  ] the-order          the fab package orders the parts the schematic specifies
  [????] physics            the board obeys physics, not just itself
           ! MOTOR6V: draws at least 0 mA; not stated: L9110sModule.VCC: names no fact for its current; JstPh2PowerInlet.VCC: names no fact for its current
           ! 4 resistor(s): could not be assessed: BtnModePullupA, BtnOpenPullupA, L9110sModulePulldownAIA, L9110sModulePulldownAIB. A netlist records neither the current through a resistor nor the voltage across it, and both depend on topology the design does not state
           ? V33: draws 355 mA of 1.50 A, resting on figures nobody has verified: Mcu.3V3: regulator_3v3_a
           ? GND: no maximum current stated, so nothing here can be verified
           ? MOTOR6V: no maximum current stated, so nothing here can be verified; the part records leave it open: L9110sModule.VCC
  [ok  ] rules-vs-netlist   written rules hold in the design that was built

  1 check(s) could not look: physics
  1 not asked for: the-order
  nothing found by the 3 check(s) that completed, of 5
```

Every check ends in one of three outcomes, and `check_all` adds a fourth word, `skipped`
([the glossary](../../GLOSSARY.md#the-three-outcomes--ok-problems-could-not-run)).
[`check_all.py`](../../scripts/check_all.py) prints each as a tag:

- `[ok  ]` is ok: it looked and found nothing.
- `[FAIL]` is problems, each on a `-` line.
- `[????]` is could-not-run, and each `!` line says what it could not check.
- `[--  ]` is skipped: it was [never asked](../../GLOSSARY.md#skipped--the-fourth-word-and-only-check_all-has-it).

`!` lines can also appear under `[FAIL]`: a check that found a problem may also have failed to look at something, and
problems outranks could-not-run. A `?` line is an
[advisory, or a value that needs measuring](../../GLOSSARY.md#needs-measurement-and-advisory--findings-that-do-not-change-the-outcome).
It does not change the outcome.

**Here physics could not look, and neither `!` line is about a rail value:**

1. **What MOTOR6V draws.** The L9110S and power-inlet records name no current on their VCC pins
   ([P120](https://github.com/xmejkal/spark/issues/54)).
2. **Four pull resistors.** Each needs its current stated under its rail, a key init does not write.

What clears each, and its shape, is in [what never to assume](agents.md#what-never-to-assume)
([P118](https://github.com/xmejkal/spark/issues/52)).

Of the 12 rail values init left null, two show, as `?` lines: GND's and MOTOR6V's `max_current_a`.

- V33's is taken from the part records' sum (355 mA), so it shows nothing of its own. V33's `?` line is about its
  supply, the dev board's unverified 1.50 A.
- The other nine print nothing. A null `served_by_pour` is read as false. `nominal_volts` and `capacitor_chemistry` are
  read only for capacitors, and this board has none.

The run exits 2, could-not-run, because physics could not look. Once a rail's `max_current_a` is stated, delete
`board.tsx` and run `/spark:build` again, so the generator sizes that rail's traces.

**`[--  ]` the-order: no fab package yet.** That is the zip of Gerbers and bill of materials a board house takes. The
`spark-design` skill tells Claude to make no Gerbers while anything load-bearing is unverified; nothing in code stops
the export. [From draft to order](#from-draft-to-order) makes one, and the-order then reads it.

**check_all is not the whole answer.** For this board, `parts.py --show` names a CONFLICT on AIA and AIB that no check
reports ([P109](https://github.com/xmejkal/spark/issues/43)). The board's 10 kΩ pull-downs against the module's own
10 kΩ pull-ups hold both inputs HIGH at idle on a supply above 5 V. It exits 0 even so:

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/parts.py" --show l9110s-module --project .
```

<!-- output: run 2026-10-05, spark 0.6.0 -->
```text
L9110S dual motor driver module — motor-driver

  asks the host for:
    MOTOR_IA     -> module pin AIA
    MOTOR_IB     -> module pin AIB

  known:
    input_high_threshold_v       2.5        verified
    continuous_current_a         0.8        verified
    supply_range_v               [2.5, 12.0] verified
    has_enable_pin               False      verified
    onboard_input_pullups_ohms   10000      verified
    schematic_numbers_vcc_and_gnd_opposite_to_the_silkscreen True       verified

  the board must: Pull both inputs down in HARDWARE. The host's pins float for the ~300 ms between reset and firmware, and through any crash or reflash, and a floating CMOS input on an H-bridge can turn both halves on.

  the board must: If a current shunt sits in this module's ground return, the module judges its inputs against ITS OWN ground, which the shunt lifts. Effective input high becomes (host logic level - I x R_shunt), and the margin over 2.5 V is what decides whether the motor turns under load.

  CONFLICT: AIA: the board's 10000 ohm pull-down against the module's own 10000 ohm pull-up to its supply holds the pin at 0.5 of the supply (1.25 V to 6 V over its 2.5-12 V range), so it idles HIGH, not low, on any supply above 5 V (input-high threshold 2.5 V); the module's input-low threshold is not recorded, so below that the level is undefined

  CONFLICT: AIB: the board's 10000 ohm pull-down against the module's own 10000 ohm pull-up to its supply holds the pin at 0.5 of the supply (1.25 V to 6 V over its 2.5-12 V range), so it idles HIGH, not low, on any supply above 5 V (input-high threshold 2.5 V); the module's input-low threshold is not recorded, so below that the level is undefined
```

The next step is the `spark-review` skill: it runs `check_all`, then reviewer agents, then the fabrication gate. It
was not run here; [is it ready?](agents.md#is-it-ready) says what each part covers.

## Firmware

**Partly.** spark does not write your firmware; you or Claude do. It gives the firmware its pins:

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/assign_pins.py" requirements.json --emit-pins firmware/pins.py
```

<!-- output: run 2026-10-05, spark 0.6.0 -->
```text
DFRobot FireBeetle 2 ESP32-S3 — 4 signal(s) placed

  MOTOR_IA        D3    GPIO38  needs nothing special; the cheapest pin left could still pwm, which is spent here  [not_wake_capable]
  MOTOR_IB        A5    GPIO11  needs nothing special; the cheapest pin left could still pwm and wake, which is spent here  [adc2_unusable_with_wifi]
  BTNOPEN_BUTTON  D12   GPIO12  needs nothing special; the cheapest pin left could still pwm and wake, which is spent here  [adc2_unusable_with_wifi]
  BTNMODE_BUTTON  D11   GPIO13  needs nothing special; the cheapest pin left could still pwm and wake, which is spent here  [adc2_unusable_with_wifi]

  still free:
  …
```

Each signal gets a pin with its pad and its reason. The rest of the output lists the pins still free, and the facts
about these parts nobody has verified, each with what depends on it. `firmware/pins.py` holds the same map as plain
integers. The firmware does `import pins`; it never types a GPIO number.

Not built yet: checking the firmware on a Mac against the pin map, before any hardware
([P59](https://github.com/xmejkal/spark/issues/7), [P74](https://github.com/xmejkal/spark/issues/8)).

## Simulate

**Partly.** The build's simulation stage generates the Wokwi diagram and stages the chips: hand-written models of
modules Wokwi has no part for, kept beside a part's record and compiled with `wokwi-cli` only when the binary is
missing or older than its source. It keeps them in `sim/` only with `--sim-dir sim`
([P116](https://github.com/xmejkal/spark/issues/50)).

A run is a separate step:

1. **Build with the simulation kept and a firmware image named:**
   `check_spine.py requirements.json --keep . --sim-dir sim --firmware flash-with-firmware.bin`.
2. **Make the flash image:** `flash_image.py --files firmware -o sim/flash-with-firmware.bin`. It puts MicroPython and
   the project's files into one image, and needs MicroPython for the S3: `/spark:setup add micropython-esp32s3`.
3. **Write a scenario.** spark ships none for this example
   ([P130](https://github.com/xmejkal/spark/issues/64)).
4. **Run `wokwi-cli`,** with a Wokwi account's CI token in `WOKWI_CLI_TOKEN` (wokwi.com/dashboard/ci).

A scenario run spends Wokwi CI minutes; none was run for this page. Watching it live in VS Code needs a Wokwi licence
that includes VS Code, Hobby+ or above per wokwi.com/pricing (read 2026-10-01). `/spark:build`'s page has both routes
([Simulate it](../../commands/build.md#simulate-it--for-real-with-the-values-set-in-the-test)).

## Bench

**Not yet.** No command does this yet. spark's own hardware step is
[P79](https://github.com/xmejkal/spark/issues/16), not designed yet.

A bench session that leaves a verdict a command can read is planned first in a separate project's repository:
[sisuo-brain-transplant](https://github.com/xmejkal/sisuo-brain-transplant), a sensor trash can given a new ESP32
brain. That plan is [P73](https://github.com/xmejkal/sisuo-brain-transplant/issues/2), first used in the bin's
bring-up, [B14](https://github.com/xmejkal/sisuo-brain-transplant/issues/8).

The `spark-reverse-engineer` skill writes a bench protocol, but for a board reverse-engineered from photos, not for a
board spark generated.

Until then, every green result in this guide is a build, a generated diagram or a check. No simulation was run, and
nothing touched hardware.

## From draft to order

Ordering a board of modules is an optional step of the journey, after the firmware works: slice 8 of
[the story map](../../scrum/STORY_MAP.md), not designed yet. The generated board is a draft, and the header of
`board.tsx` says so: its modules sit in a column that does not overlap, it has no mounting holes or connector keying,
and its traces are not sized for current until each rail's current is stated. What exists today, in order:

1. **Look at it** in tscircuit's viewer: [see it](../../commands/build.md#see-it).
2. **State each rail's current,** as `max_current_a` in `.spark/rules.json` or as figures in the part records. The
   generator sizes a rail's traces from it.
3. **Generate the board again.** Delete `board.tsx` and run `/spark:build`, because an existing `board.tsx` is never
   overwritten. If you have already laid it out, move it aside first and carry the new trace widths over by hand.
4. **Lay it out, then build your own `board.tsx`:** `npx --no tsci build board.tsx`. The `spark-design` skill's
   [layout notes](../../skills/spark-design/references/pcb-layout.md) name the routes; they were not run for these docs.
   Until [P110](https://github.com/xmejkal/spark/issues/44) lands, `/spark:build` rebuilds `dist/`, which every check
   reads, from the requirements file, not from your `board.tsx`.
5. **Run the `spark-review` skill:** its reviewer agents, then the fabrication gate
   ([is it ready?](agents.md#is-it-ready)).
   - The gate's `boards.py --validate --for-fab` refuses a dev-board definition that breaks its contract or names no
     footprint.
   - `parts.py --unverified` lists the unverified facts and pin orders of the parts you name
     ([its output on this example](commands.md#skills)).
   - Neither reads the generated board, or lists the dev board's own unverified figures
     ([P126](https://github.com/xmejkal/spark/issues/60)).
6. **A design-rule check, if you have KiCad.** No check here is one, and tscircuit's autorouter can emit shorts (the
   layout notes say so). The build stage stops on any error tscircuit writes into `circuit.json`, on a component that
   shares no net with the supplies, and on a board with no traces; buildability checks each hole against the process.
   Nothing here measures the spacing between nets. Export the board, then run `kicad-cli pcb drc board.kicad_pcb`. The
   export ran here; `kicad-cli` was not installed, so the check did not:

```sh
npx --no tsci export board.tsx -f kicad_pcb -o board.kicad_pcb
```

<!-- output: run 2026-10-06, spark 0.6.0 -->
```text
Exported to board.kicad_pcb!
```

7. **Have a person look at the layout.**
8. **The fab package:**

```sh
npx --no tsci export board.tsx -f gerbers -o board-gerbers.zip
```

<!-- output: run 2026-10-06, spark 0.6.0 -->
```text
Mcu: cannot verify jlcpcb pick-and-place rotation (missing_pin1_location); PCB rotation 0 is unverified.
L9110sModule: cannot verify jlcpcb pick-and-place rotation (missing_pin1_location); PCB rotation 0 is unverified.
JstPh2PowerInlet: cannot verify jlcpcb pick-and-place rotation (missing_supplier_pin1_location); PCB rotation 0 is unverified.
BtnOpen: cannot verify jlcpcb pick-and-place rotation (missing_supplier_pin1_location); PCB rotation 0 is unverified.
BtnMode: cannot verify jlcpcb pick-and-place rotation (missing_supplier_pin1_location); PCB rotation 0 is unverified.
Exported to board-gerbers.zip!
```

This export was made for these docs, on the draft, with five facts about its parts still unverified (the gate's
`parts.py --unverified` lists them: [its output](commands.md#skills)): the skill would not have made it, and nothing in
code stopped it. The five "cannot verify jlcpcb
pick-and-place rotation" lines are the five parts with no JLCPCB part number.

The bill of materials inside gives no part number for the dev board, the motor driver, the inlet or the buttons, and
no footprint for the dev board. Only the four 10 kΩ resistors carry a JLCPCB part number:

```sh
unzip -p board-gerbers.zip bom.csv
```

<!-- output: run 2026-10-06, spark 0.6.0 -->
```text
"Designator","Comment","Value","Footprint","JLCPCB Part #"
"Mcu","",""," ",
"L9110sModule","","","headermodule6",""
"JstPh2PowerInlet","","","jst_ph_2",""
"BtnOpen","","","pushbutton",""
"BtnMode","","","pushbutton",""
"L9110sModulePulldownAIA","10k","10k","res0603","C25804"
"L9110sModulePulldownAIB","10k","10k","res0603","C25804"
"BtnOpenPullupA","10k","10k","res0603","C25804"
"BtnModePullupA","10k","10k","res0603","C25804"
```

With the package in the project, `check_all` finds it and the-order answers `[ok  ]`:

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/check_all.py" --project .
```

<!-- output: run 2026-10-06, spark 0.6.0 -->
```text
  resolved from .:
    circuit      dist/board/circuit.json
    rules        .spark/rules.json
    package      board-gerbers.zip
    boards       2 definition(s): firebeetle2-esp32s3, xiao-esp32-c6

  [ok  ] vendor-truth       the board definition matches the vendor's own pin header
  [ok  ] buildability       holes take their pins, packages hold their values
           ? JstPh2PowerInlet: pad 1.20 mm around a 0.75 mm hole leaves 0.225 mm of ring: over the 0.18 mm this process can make, under the 0.25 mm it recommends
  [ok  ] the-order          the fab package orders the parts the schematic specifies
  [????] physics            the board obeys physics, not just itself
           ! MOTOR6V: draws at least 0 mA; not stated: L9110sModule.VCC: names no fact for its current; JstPh2PowerInlet.VCC: names no fact for its current
           ! 4 resistor(s): could not be assessed: BtnModePullupA, BtnOpenPullupA, L9110sModulePulldownAIA, L9110sModulePulldownAIB. A netlist records neither the current through a resistor nor the voltage across it, and both depend on topology the design does not state
           ? V33: draws 355 mA of 1.50 A, resting on figures nobody has verified: Mcu.3V3: regulator_3v3_a
           ? GND: no maximum current stated, so nothing here can be verified
           ? MOTOR6V: no maximum current stated, so nothing here can be verified; the part records leave it open: L9110sModule.VCC
  [ok  ] rules-vs-netlist   written rules hold in the design that was built

  1 check(s) could not look: physics
  nothing found by the 4 check(s) that completed, of 5
```
