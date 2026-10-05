# spark

**From an idea in words to a checked board, for gadgets built from an ESP32 dev board and modules.**

spark is a Claude Code plugin. You describe the gadget, and spark helps turn it into needs and the kinds of module
that meet them. It researches each part from the vendor's own documents and assigns every pin with a reason. It
generates a board that builds and simulates, and checks it.

It refuses rather than guesses. Every check says when it
[**could not look**](docs/guide/agents.md#the-four-outcomes), because a check that could not look must
never read as a check that passed.

```mermaid
flowchart LR
    idea["Idea — partly"] --> drawer["Drawer — works"] --> research["Research — partly"]
    research --> build["Build — works"] --> checks["Checks — works"] --> firmware["Firmware — partly"]
    firmware --> bench["Bench — not yet"]
```

The same journey in words:

1. An idea becomes needs.
2. Your drawer and spark's records are searched first.
3. Research fills a real gap.
4. A requirements file becomes a board that builds and simulates.
5. The checks say what holds and what they could not look at.
6. The firmware gets its pin map.
7. The bench proves it on hardware.

## What works today

The statuses come from runs on 2026-10-05. The [journey guide](docs/guide/journey.md) shows every output, and says
what was not run.

| step | today | with |
| --- | --- | --- |
| [Idea](docs/guide/journey.md#idea) | **partly**: a goal becomes needs, matched against what you own and what spark knows. Turning needs into a board is [P76](https://github.com/xmejkal/spark/issues/5) | `/spark:idea` |
| [Drawer](docs/guide/journey.md#drawer) | **works**: what you own, in your own store, said in plain words or imported from DFRobot orders | `/spark:drawer` |
| [Research](docs/guide/journey.md#research) | **partly**: the library search runs. Research of a new part is done by agents, and was not run for these pages | `/spark:research`, `/spark:identify` |
| [Build](docs/guide/journey.md#build) | **works**: a requirements file to a board that builds and simulates, or the stage that stopped it | `/spark:build` |
| [Checks](docs/guide/journey.md#checks) | **works**: five checks, each saying what it could not look at | `/spark:init`, the `spark-review` skill |
| [Firmware](docs/guide/journey.md#firmware) | **partly**: the pin map is exported for the firmware to import. Checking firmware on a Mac is [P59](https://github.com/xmejkal/spark/issues/7) and [P74](https://github.com/xmejkal/spark/issues/8) | `assign_pins.py --emit-pins` |
| [Bench](docs/guide/journey.md#bench) | **not yet** ([P73](https://github.com/xmejkal/sisuo-brain-transplant/issues/2)) | — |

## Install, and a first run

In Claude Code:

```
/plugin marketplace add xmejkal/spark
/plugin install spark
```

Then, in a project folder:

1. `/spark:setup` shows the tools spark needs, and installs what is missing with one yes.
2. `/spark:init` writes the project's files, guessing nothing.
3. `/spark:build` turns a requirements file into a board.

For the example on [`/spark:build`'s page](commands/build.md) (a FireBeetle 2 ESP32-S3, an L9110S motor driver, a
power inlet and two buttons), the build prints:

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

## Commands, skills and agents

- **Commands**, typed in Claude Code:
  - `/spark:setup`: the tools;
  - `/spark:init`: a project;
  - `/spark:idea`: a goal to needs;
  - `/spark:drawer`: what you own;
  - `/spark:research`: a missing part;
  - `/spark:identify`: a module from a photo;
  - `/spark:build`: a requirements file to a board.
- **Skills**, which Claude picks up from your words:
  - `spark-design`: design a board;
  - `spark-review`: review it and gate it before ordering;
  - `spark-reverse-engineer`: a board from its photo.
- **Agents**, launched by the commands and skills:
  - `part-finder` and `datasheet-reader` for a commodity part;
  - `parts-researcher` for a module;
  - `design-reviewer`, one per review dimension.

Each one, with when to use it and what it writes and refuses: [the commands guide](docs/guide/commands.md).

## For AI agents

In Claude Code, an agent follows the person's commands. Any other AI runs spark's scripts directly: plain Python 3,
with JSON answers and exit codes 0 ok, 1 problems, 2 could-not-run. [`AGENTS.md`](AGENTS.md) points to
[the guide for agents](docs/guide/agents.md), which also says what never to assume.

## What it uses underneath

- **tscircuit** builds the board. `/spark:setup` installs it into the project at the version spark pins.
- **Wokwi** simulates it. The build writes the diagram and chips; a simulation run spends Wokwi CI minutes.
- **MicroPython** is the firmware image for a headless simulation.
- **Two MCP servers**, declared by spark for its research agents: jlcpcb for part search, and espressif-docs for
  Espressif's documentation.
- **Your store**, `~/.local/share/spark`, outside every repository, holds what you own and what research kept.
- **KiCad's `kicad-cli`**, optionally, for the review and design skills' electrical-rule and design-rule checks.

How the scripts, the data and the chain fit together: [how spark works underneath](docs/guide/how-it-works.md).

## Honest limits

- The deterministic checks and the libraries do what they say. Auto-routing does not: tscircuit's autorouter can
  emit shorts and unmanufacturable vias, so the fab gate and human review before ordering are not optional.
- The reviewer half is less established than the checks. The evidence for it is a handful of eval runs at n=1–3, whose
  arms differ by context alone, and none of them exercises a script. Treat "the reviewers help" as plausible and
  unproven rather than measured.
- Nothing here has been validated on hardware by its author. Ground truth is the bench.

## More

- [The glossary](GLOSSARY.md): the words this repository uses its own way, each with the failure that produced it.
- [Developing spark](docs/guide/developing.md): the tests, the gate, and where the work is planned.

---

v0.6.0 · MIT · built with the tscircuit engine.
