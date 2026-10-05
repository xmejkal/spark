# The journey

spark takes a gadget from an idea in words to a board that builds, simulates and is checked. At every step it says
what it could not look at. This page walks each step on real runs: what was typed, what spark printed, what it wrote,
and where the step stops today.

```mermaid
flowchart LR
    idea["Idea — partly"] --> drawer["Drawer — works"] --> research["Research — partly"]
    research --> build["Build — works"] --> checks["Checks — works"] --> firmware["Firmware — partly"]
    firmware --> bench["Bench — not yet"]
```

In words, the steps run in this order:

1. An idea becomes needs.
2. Each need is matched against your drawer and spark's records first.
3. Research fills a real gap.
4. A requirements file becomes a board that builds and simulates.
5. The checks say what holds and what could not be looked at.
6. The firmware imports the pin map.
7. The bench proves it on hardware.

**Works**, **partly** and **not yet** say what each step does today. Each section below says where a partial step
stops.

**How these runs were made.**

- When: 2026-10-05, with spark 0.6.0 and tscircuit 0.0.2600, the version spark pins. The tscircuit came from an
  existing install.
- Where: in fresh project folders, with a store of their own.
- How: each command typed as shown. In Claude Code you type the `/spark:` command, and Claude runs these scripts for
  you. You, or another AI, can run them directly.
- Paths: `$CLAUDE_PLUGIN_ROOT` is where spark is installed. In outputs, `~/` is the home folder and `<temp>` a
  temporary one.

There are two example projects:

- `plant-alarm` holds the idea step. Its goal is the one `/spark:idea`'s own page uses.
- `my-gadget` holds the rest. It uses the requirements file that `/spark:build`'s page documents: a DFRobot
  FireBeetle 2 ESP32-S3, an L9110S motor driver, a power inlet and two buttons.

## Idea

**Partly.** [`/spark:idea`](../../commands/idea.md) turns a goal in your words into needs, then matches each need
against your drawer and spark's records. It stops there: nothing yet turns needs into a requirements file. That is
[P76](https://github.com/xmejkal/spark/issues/5).

First, Claude asks at most three questions, one at a time. Then it writes the needs to a file:

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

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/parts.py" --needs-set . ../needs.json
```

<!-- output: run 2026-10-05, spark 0.6.0 -->
```text
  set soil: does → "sense", what → "soil-moisture", condition → "indoor pot, short probe; low power"
  set alarm: does → "indicate", what → "alarm"
  set board: does → "compute", what → "microcontroller"
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

- Owned parts come first, with how many are free.
- `owes` names what a record still lacks before it can build.
- `[other words]` means the candidate does the need's verb in other words. Whether it fits is Claude's call, said
  to you.

Here a distance sensor is offered for soil moisture. It senses, but not this, so the need is a real gap, which is what
research is for.

## Drawer

**Works.** [`/spark:drawer`](../../commands/drawer.md) keeps what you own in your own store,
`~/.local/share/spark`, never in a repository.

You say what you own in plain words. Claude writes the entries to a file and shows what would change:

```json
[
  {"label": "FireBeetle 2 ESP32-S3", "count": 1, "is": {"board": "firebeetle2-esp32s3"}},
  {"label": "red LEDs, pack of 10", "count": 10, "function": [{"does": "indicate", "what": "light"}]}
]
```

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

Your DFRobot order history can also come in from your logged-in browser. Only each order's lines are read, never
the account pages, which hold your address, phone and payment details. That path is not run here; the drawer's page
describes it.

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

A real gap goes to [`/spark:research`](../../commands/research.md), which works through agents:

- For a commodity part, `part-finder` finds the exact part on the maker's site.
- `datasheet-reader` then fills the record from the datasheet pages the decision needs.
- For a module, `parts-researcher` researches it from primary sources.

Either way the result is a record with every fact cited and every unconfirmed fact marked, so the next project finds
it. That part runs as agents in a conversation and was not run for this page.

A module you already own can start from a photo instead: [`/spark:identify`](../../commands/identify.md).

## Build

**Works.** Two commands come before the first build:

- [`/spark:setup`](../../commands/setup.md) says which tools spark needs and installs what is missing with one yes.
- [`/spark:init`](../../commands/init.md) writes the project's files, guessing nothing.

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

It exits 2 because one tool is missing: the MicroPython image, which only the firmware step needs.

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

Then [`/spark:build`](../../commands/build.md) runs the whole chain on the requirements file:

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

`--keep .` writes the board into the project: `board.tsx`, the board's footprint, and `dist/`, where every check
looks. Without it, the chain builds in a temporary folder and deletes it.

The simulation stage writes the [Wokwi](https://wokwi.com) diagram and stages the chips. It does not run a
simulation. Running one is a separate step on `/spark:build`'s page, with `wokwi-cli` and your Wokwi account.

## Checks

**Works.** After a build, running init again with `--force` names the rails from the board. It lists every value
nobody has given yet:

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

Every check answers with one of [four words](../../GLOSSARY.md#the-three-outcomes--ok-problems-could-not-run), as
[`check_all.py`](../../scripts/check_all.py) prints them:

- `[ok  ]` means it looked and found nothing.
- `[FAIL]` means it found problems, each on a `-` line.
- `[????]` means it **could not look**, and each `!` line says what it could not check. Here, physics cannot run
  until the rails' values are stated in `.spark/rules.json`.
- `[--  ]` means it was [never asked](../../GLOSSARY.md#skipped--the-fourth-word-and-only-check_all-has-it). Here
  there is no fab package yet.

A `?` line is an
[advisory, or a value that needs measuring](../../GLOSSARY.md#needs-measurement-and-advisory--findings-that-do-not-change-the-outcome).
It does not change the outcome.

The run exits 2, could-not-run, rather than 0. A value nobody measured stays `null`, and the check says so instead of
passing.

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

Each signal gets a pin with its pad and its reason. The rest of the output lists the pins still free and the facts
about these parts nobody has verified, each with what depends on it. `firmware/pins.py` holds the same map as plain
integers, and the firmware does `import pins`; it never types a GPIO number.

What is not yet built:

- Checking the firmware on a Mac against the pin map, before any hardware. That is
  [P59](https://github.com/xmejkal/spark/issues/7) and [P74](https://github.com/xmejkal/spark/issues/8).

What exists but was not run here:

- A flash image needs MicroPython for the S3: `/spark:setup add micropython-esp32s3`.
- Simulating the firmware runs `wokwi-cli` on your Wokwi account. `/spark:build`'s page has the commands.

## Bench

**Not yet.** No command does this yet. A bench session that leaves a verdict a command can read is
[P73](https://github.com/xmejkal/sisuo-brain-transplant/issues/2). The first real bench is the bin's bring-up,
[B14](https://github.com/xmejkal/sisuo-brain-transplant/issues/8).

Until then, every green result in this guide is a build, a check or a simulation, not hardware.
