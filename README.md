# spark

**From a list of modules to a checked board, for gadgets built from an ESP32 dev board.**

spark is a Claude Code plugin. You describe the gadget, and spark helps turn it into needs, which it matches against
the parts you own and the ones it knows. It researches a missing part from the vendor's own documents and assigns
every pin with a reason. From a requirements file it generates a printed circuit board that your dev board and modules
plug into:

- the board builds;
- its connections are derived from the parts' records;
- a Wokwi diagram is generated from it;
- spark's checks read it.

Its placement is a first draft, which you lay out before ordering. Today the chain starts from that requirements
file; nothing yet writes one from an idea ([P76](https://github.com/xmejkal/spark/issues/5)). Two dev boards are
defined, the DFRobot FireBeetle 2 ESP32-S3 and the Seeed XIAO ESP32-C6; another one needs a board file
([boards/README.md](boards/README.md)). From here on, *board* means the generated PCB and *dev board* the ESP32
module.

Where a fact is missing, spark refuses, or it goes on with a stand-in that it names in the header of `board.tsx`, such
as a placeholder outline or the router's default trace width. Its checks are built so that one that
[**could not look**](docs/guide/agents.md#the-outcomes-and-their-exit-codes) never reads as one that passed. Where
that does not hold yet, [what never to assume](docs/guide/agents.md#what-never-to-assume) says so.

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

## What works today

The statuses come from runs on 2026-10-05. The [journey guide](docs/guide/journey.md) shows the output of each step
it describes, and says what was not run.

| step | today | with |
| --- | --- | --- |
| [Drawer](docs/guide/journey.md#drawer) | **partly**: what you own, kept in your own store; the scripts that list and write entries ran. Turning your words into entries (a conversation) and importing your DFRobot orders (Claude driving your logged-in browser) were not run for these pages | `/spark:drawer` |
| [Idea](docs/guide/journey.md#idea) | **partly**: a goal becomes needs, matched against what you own and what spark knows; the conversation that writes the needs was not run for these pages. Not built yet: choosing and reserving parts ([P97](https://github.com/xmejkal/spark/issues/18)), and turning needs into a requirements file ([P76](https://github.com/xmejkal/spark/issues/5)) | `/spark:idea` |
| [Research](docs/guide/journey.md#research) | **partly**: the library search runs. Research of a new part is done by agents, and was not run for these pages | `/spark:research`, `/spark:identify` |
| [Build](docs/guide/journey.md#build) | **works**: a requirements file to a board that builds, with a Wokwi diagram generated from it, or the stage that stopped it | `/spark:build` |
| [Checks](docs/guide/journey.md#checks) | **works**: `check_all.py` runs the deterministic checks in one command. Here four of the five were asked (the-order needs a fab package); three completed, and physics could not look. The `spark-review` skill runs it and then reviewer agents, which were not run for these pages | `check_all.py`, after `/spark:init` |
| [Firmware](docs/guide/journey.md#firmware) | **partly**: the pin map is exported for the firmware to import. Not built yet: checking the firmware on a Mac against it ([P59](https://github.com/xmejkal/spark/issues/7), [P74](https://github.com/xmejkal/spark/issues/8)) | `assign_pins.py --emit-pins` |
| [Simulate](docs/guide/journey.md#simulate) | **partly**: the build generates the Wokwi diagram and the chips, and keeps them only with `--sim-dir sim` ([P116](https://github.com/xmejkal/spark/issues/50)). A run needs a flash image, a scenario you write and `wokwi-cli`, and it spends Wokwi CI minutes; none was run for these pages | `/spark:build`, then `wokwi-cli` |
| [Bench](docs/guide/journey.md#bench) | **not yet**: spark's hardware step is [P79](https://github.com/xmejkal/spark/issues/16); the first bench will be the smart-bin project's ([P73](https://github.com/xmejkal/sisuo-brain-transplant/issues/2)) | — |

What the three words mean:

- **works**: it ran end to end for these pages.
- **partly**: it stops before its goal, or its scripts ran and the rest (agents, or a conversation) was not run for
  these pages; the row says which.
- **not yet**: nothing does it yet; the linked issue plans it.

## Install, and a first run

In Claude Code:

```
/plugin marketplace add xmejkal/spark
/plugin install spark
```

Then, in a project folder:

1. `/spark:init` writes the project's files without guessing, including the `package.json` that tscircuit installs
   into.
2. `/spark:setup` shows the tools spark needs, and installs what is missing with one yes.
3. Put a `requirements.json` in the folder: the dev board and a list of parts. Copy the example on
   [`/spark:build`'s page](commands/build.md#the-requirements-file), or ask Claude to design the board; the
   `spark-design` skill writes the file with you (not run for these pages). Nothing yet turns a vague idea with no
   parts named into this file ([P76](https://github.com/xmejkal/spark/issues/5)).
4. `/spark:build` turns it into a board.

For the example on `/spark:build`'s page (a FireBeetle 2 ESP32-S3, an L9110S motor driver, a power inlet and two
buttons), the build prints:

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

19 routed traces carry the 22 written connections: a group of N connected pins needs N−1 traces. This ran with
tscircuit already installed in the project. The one-yes install was not run for this page; it last ran in P82's cold
run on 2026-10-03 ([the backlog's archive](scrum/PRODUCT_BACKLOG.md)).

## Commands, skills and agents

- **Commands**, typed in Claude Code:
  - `/spark:init`: a project;
  - `/spark:setup`: the tools;
  - `/spark:drawer`: what you own;
  - `/spark:idea`: a goal to needs;
  - `/spark:research`: a missing part;
  - `/spark:identify`: a module from a photo;
  - `/spark:build`: a requirements file to a board.
- **Skills**, which Claude picks up from your words:
  - `spark-design`: design a board;
  - `spark-review`: review it and gate it before ordering;
  - `spark-reverse-engineer`: a board from its photo.
- **Agents**, launched by the commands and skills:
  - `part-finder` and `datasheet-reader` for a commodity part (an LED, a button, a connector: one datasheet describes
    it);
  - `parts-researcher` for a module;
  - `design-reviewer`, one per review dimension.

Each one, with when to use it and what it writes and refuses: [the commands guide](docs/guide/commands.md).

## For an AI using spark

In Claude Code, Claude follows the person's `/spark:` commands. Any other AI runs spark's scripts directly. They are
plain Python 3 and exit 0 ok, 1 problems, 2 could-not-run. Most of them answer in JSON with `--json`;
[the guide for agents](docs/guide/agents.md) lists which.

Two cases to know before trusting an exit code:

- `check_all.py` exits 0 when every check that ran found nothing, even if most checks were never asked.
- `init_project.py` exits 1 when it has nothing to do.

[`AGENTS.md`](AGENTS.md) points to the guide, which also says what never to assume.

## What it uses underneath

- **tscircuit** builds the board. `/spark:setup` installs it into the project at the version spark pins.
- **Node and bun.** Node runs the diagram converter, npm and the MCP servers; bun runs tscircuit's `tsci`.
- **Wokwi** simulates it. The build generates the diagram and the chips (simulated models of modules Wokwi lacks),
  and keeps them in `sim/` only with `--sim-dir sim`. A simulation run spends Wokwi CI minutes.
- **MicroPython** is the firmware image for a headless simulation.
- **Two MCP servers**, declared by spark for its research agents. Claude Code starts both with `npx -y`, unpinned
  ([P112](https://github.com/xmejkal/spark/issues/46)):
  - `@jlcpcb/mcp`, an unofficial community package ([l3wi/jlc-cli](https://github.com/l3wi/jlc-cli)), for part
    search;
  - `mcp-remote`, which connects to Espressif's hosted documentation server.
- **Your store**, `~/.local/share/spark`, outside every repository, holds what you own and what research kept.
- **KiCad's `kicad-cli`**, optionally, for the review and design skills' electrical-rule and design-rule checks.

How the scripts, the data and the chain fit together: [how spark works underneath](docs/guide/how-it-works.md).

## Honest limits

- **The generated board is a draft.** Its modules sit in a column that does not overlap, and it has no mounting holes
  or connector keying. Its trace widths are not sized for current until each rail's current is stated
  (`max_current_a` in `.spark/rules.json`, or figures in the part records) and the board is regenerated. The header
  of `board.tsx` says so itself.
- **No check here is a design-rule check, and tscircuit's autorouter can emit shorts.**
  - The build stage stops on the errors that tscircuit's own routing checks write into `circuit.json` (overlapping
    traces, pour shorts, some clearances).
  - Buildability checks each via's hole and pad.
  - Beyond that, `check_all`'s five checks and the fabrication gate's two commands do not look at spacing,
    clearance or shorts.

  Before ordering:
  1. Run the `spark-review` skill. Its last step, the fabrication gate, refuses a board definition that lacks what a
     PCB needs, and lists every fact nobody has checked.
  2. If you have KiCad, run `kicad-cli pcb drc` after `npx tsci export -f kicad_pcb board.tsx`. Neither was run for
     these pages.
  3. Have a person look at the layout.

  Each of the five checks is tested in its own suite on an input that makes it find a problem
  ([Developing spark](docs/guide/developing.md#the-tests)).
- **The reviewer agents in `spark-review` are less proven than the checks.** The only measurements were a few eval
  runs, one to three per arm, comparing the plugin with a no-plugin baseline
  ([tabled in the 2026-09-24 audit](docs/audit-2026-09-24/autonomous-agent-readiness.md#on-the-eval-and-the-reprioritisation-it-drove)).
  Each case graded what the agent found, not a script, and the cases were removed in commit 066c4af. Treat "the
  reviewers help" as plausible, not measured.
- **Nothing here has been validated on hardware by its author.** Ground truth is the bench.

## More

- [The glossary](GLOSSARY.md): the words this repository uses its own way, each with the failure that produced it.
- [Developing spark](docs/guide/developing.md): the tests, the commit gate, and where the work is planned.

---

v0.6.0 · MIT · built with the tscircuit engine.
