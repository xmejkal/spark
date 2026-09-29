---
description: From a requirements file — a board and a list of parts — to a board that builds and simulates, or the stage that stopped it. Deterministic, seconds, no agents.
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/scripts/check_spine.py *), Bash(${CLAUDE_PLUGIN_ROOT}/scripts/emit_board.py *), Bash(${CLAUDE_PLUGIN_ROOT}/scripts/emit_footprint.py *), Bash(${CLAUDE_PLUGIN_ROOT}/scripts/assign_pins.py *), Bash(${CLAUDE_PLUGIN_ROOT}/scripts/parts.py *), Bash(${CLAUDE_PLUGIN_ROOT}/scripts/boards.py *)
---

# spark:build

A module list in, a board that builds out. This is the chain that produced two working boards
before any skill, command or agent named it; a user following the documented flow was told to
write the board file by hand. Now it is one command.

## The requirements file

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

`board` is an id from `boards.py --list`. Each entry in `parts` is a record id from
`parts.py --list` — the shipped library plus the project's own `parts/*.json`, which win by name —
or `{part, name}` when the same part appears more than once: five buttons with no names are one
component with five GPIOs shorted to it, and the generator refuses that. The inlet is there
because a module list is a list of *consumers*: the motor driver's rail needs a source, and
without one the generator says so and the build stops on a net with one member — which is what
the first version of this very example did. Which rail a part's power pin sits on is the design's to say, not the record's: `{"part":
"l9110s-module", "rails": {"VCC": "traction"}}` puts the driver on the pack rail without copying
the record, and a pin the part does not have is refused by name. Parts on one bus share it —
two I2C sensors both land on SDA/SCL — and a bus line named the vendor's way (DIN, CLK, CS) lands
on the board's MOSI, SCK, SS; a line the bus does not have is refused by name, never placed
somewhere quiet. An optional `"signals":
[{"name": "LED_STATUS", "needs": []}]` adds a pin no part record claims (an LED, a limit switch); the file lists it as
*assigned, and connected to nothing*, for you to wire by hand, and the spine flags that.

The project is found up from the requirements file's own directory, so this works from anywhere —
and from nowhere: a file inside no project is built from the plugin's own library, with no rules,
and every command says so. `/spark:init` in a directory makes it a project, which is where a
design's own parts, boards and rules live.

## The one command

```
${CLAUDE_PLUGIN_ROOT}/scripts/check_spine.py requirements.json
```

```
  idea -> parts -> pin map -> schematic -> footprint -> build -> simulation

  [ok  ] board            DFRobot FireBeetle 2 ESP32-S3
  [ok  ] schematic        14 trace(s) written
  [ok  ] footprint        FireBeetle2Esp32S3.tsx
  [ok  ] build            12 trace(s), 0 errors, tsci 0.0.2621
  [ok  ] simulation       12 wire(s) in the diagram

  the chain runs end to end
```

Three outcomes, never two. `ok` means copper reached the board — traces counted, no error
element, every component on a ground. `!!` is a defect in the design, named. `????` is
**could-not-run**: the stage was not exercised — no `tsci`, a tool that cannot build even a
trivial board, a requirements file that is not JSON, an empty parts list — and the exit code (2)
says so. A chain that could not be exercised has not been proven; the difference is the whole
point.

## The steps, when one is wanted on its own

```
${CLAUDE_PLUGIN_ROOT}/scripts/parts.py --list                       # what exists, and where from
${CLAUDE_PLUGIN_ROOT}/scripts/parts.py --show l9110s-module         # what it asks of the host
${CLAUDE_PLUGIN_ROOT}/scripts/assign_pins.py requirements.json      # a pin per signal, with the reason
${CLAUDE_PLUGIN_ROOT}/scripts/emit_board.py requirements.json > board.tsx
${CLAUDE_PLUGIN_ROOT}/scripts/emit_footprint.py --board firebeetle2-esp32s3 -o FireBeetle2Esp32S3.tsx
npx tsci build board.tsx                                            # needs tscircuit; the one command does this in a temp dir
```

The board file imports `./FireBeetle2Esp32S3` — the footprint `emit_footprint.py` writes from
the board file's measured geometry; without that step `tsci build` stops at the import. The
one command writes it for you.

`assign_pins` spends scarce pins last — wake-capable, ADC1, the SPI and I2C pins — and prints why
each signal landed where it did. `emit_board` writes tscircuit you can build and check; the file
says what it invented (a placeholder size, a rail nobody named) and what it could not size (a
rail with no `max_current_a` in `.spark/rules.json`).

## What it refuses, and why

The generator refuses rather than guess, and each refusal says what to record:

| refusal | because |
| --- | --- |
| no footprint recorded for a part | a twelve-pad module on a four-pad guess has no positions past the fourth, and the board comes out with no copper at all |
| no `pin_order` recorded | pads would be numbered from the order pins appear in a file, which is not a fact about the module |
| no outline recorded | every placement would be arranged around an invented size; `--assume-missing-sizes` proceeds with the guess declared in the file |
| two components of one name | tscircuit keeps one and wires every other instance's pins to it |
| a part that is not in the library | `parts.py --need <words>` says what exists; `/spark:research` writes the record from the vendor's own pages, vendor by vendor in the project's order — never a pinout from memory |

A rail nothing sources (a motor rail with no connector) is not a refusal: the file says so and the
build stops on a net with one member. Add the connector to the parts list.

## After it builds

`check_all.py --project .` for the deterministic checks; the `spark-review` skill for the full
gate before anything is fabricated. The generated placement is a column that does not overlap — a draft, and
the file's own header says so.
