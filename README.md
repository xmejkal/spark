# spark

**From a list of modules to a checked board, for gadgets built from an ESP32 dev board.**

spark is a Claude Code plugin, meant for a hobbyist building a gadget from an ESP32 *dev board* (a module such as the
DFRobot FireBeetle 2 ESP32-S3) and off-the-shelf modules, not for chip-down boards made in volume
([the vision](scrum/VISION.md)). You describe the gadget, and spark helps turn it into needs, which it matches against
the parts you own and the ones it knows. It researches a missing part from the vendor's own documents and writes it as
a [record](GLOSSARY.md#record--and-the-three-places-one-lives): its facts, each with a source and whether anyone
checked it.

From a [requirements file](GLOSSARY.md#the-requirements-file), the dev board and a list of parts, spark generates the
*board*: a printed circuit board your dev board and modules plug into.

- Every pin gets a reason, and the connections come from the parts' records.
- The board builds, with a Wokwi diagram generated from it (kept only with `--sim-dir sim`,
  [P116](https://github.com/xmejkal/spark/issues/50)).
- spark's checks read it.

Its placement is a first draft, which you lay out before ordering. Today the chain starts from that requirements file;
nothing yet writes one from a vague idea with no parts named ([P76](https://github.com/xmejkal/spark/issues/5)).
`--board`, and a requirements file's `board`, name the dev board.

The library defines two dev boards, but only the FireBeetle 2 ESP32-S3 builds. The Seeed XIAO ESP32-C6 is defined for
the pin map only: its file records no header geometry, so `/spark:build` stops at the footprint stage
([P121](https://github.com/xmejkal/spark/issues/55)). The library held 7 parts on 2026-10-06 (`parts.py --list`).

Where a fact is missing, spark refuses, or it goes on with a stand-in that it names in `board.tsx`: a placeholder
outline in its header, the router's default trace width under the power traces it could not size. Its checks are
built so that one that [**could not look**](docs/guide/agents.md#the-outcomes-and-their-exit-codes) never reads as one
that passed. Where that does not hold yet, [what never to assume](docs/guide/agents.md#what-never-to-assume) says so.

## What it shows on the example

On the documented example (a FireBeetle 2 ESP32-S3, an L9110S motor driver, a power inlet and two buttons), from the
runs in [the journey guide](docs/guide/journey.md):

- **A conflict between two parts.** The board's 10 kΩ pull-downs, against the L9110S module's own 10 kΩ pull-ups, hold
  both motor inputs HIGH at idle on a supply above 5 V. `parts.py --show` reports it; `check_all` does not yet
  ([P109](https://github.com/xmejkal/spark/issues/43)).
- **An advisory:** the power inlet's 0.225 mm annular ring is over the 0.18 mm the default process can make, but under
  the 0.25 mm it recommends.
- **A figure nobody verified:** the 3.3 V rail draws 355 mA of the dev board's 1.50 A, a rating nobody has checked.
- **What a check could not look at:** physics, because the motor driver's and the inlet's records state no current
  ([P120](https://github.com/xmejkal/spark/issues/54)) and four resistors' currents are unstated.
- **A reason for every pin:** `MOTOR_IA` goes on pad D3, GPIO38, because it *"needs nothing special; the cheapest pin
  left could still pwm, which is spent here"*.

## What works today

```mermaid
flowchart LR
    drawer["Drawer — partly"] --> idea["Idea — partly"] --> research["Research — partly"]
    research --> build["Build — works"] --> checks["Checks — works"] --> firmware["Firmware — partly"]
    firmware --> simulate["Simulate — partly"] --> bench["Bench — not yet"]
```

The table says the same in words. Each status comes from runs made for these docs, this README and the guides in
`docs/guide/`, on 2026-10-05 and 2026-10-06; [the journey guide](docs/guide/journey.md) shows the output of each step
it describes, and what was not run.

| step | today | with |
| --- | --- | --- |
| [Drawer](docs/guide/journey.md#drawer) | **partly**: what you own, kept in your own store; the scripts that list and write entries ran. Turning your words into entries, and the DFRobot import, were not run here | `/spark:drawer` |
| [Idea](docs/guide/journey.md#idea) | **partly**: a goal becomes needs, matched against what you own and what spark knows; the conversation was not run here. Not built yet: choosing and reserving parts ([P97](https://github.com/xmejkal/spark/issues/18)), and turning needs into a requirements file ([P76](https://github.com/xmejkal/spark/issues/5)) | `/spark:idea` |
| [Research](docs/guide/journey.md#research) | **partly**: the library search runs. Research of a new part is done by agents, not run here | `/spark:research`, `/spark:identify` |
| [Build](docs/guide/journey.md#build) | **works**: a requirements file to a board that builds, with a Wokwi diagram generated from it, or the stage that stopped it | `/spark:build` |
| [Checks](docs/guide/journey.md#checks) | **works**: `check_all.py` runs five deterministic checks in one command. In the journey's run three found nothing, physics could not look, and the-order was skipped: there was no fab package yet. It does not run the generator's CONFLICT test ([P109](https://github.com/xmejkal/spark/issues/43)) or the gate's two commands. The `spark-review` skill runs it and then reviewer agents, not run here | `check_all.py`, after `/spark:init` |
| [Firmware](docs/guide/journey.md#firmware) | **partly**: the pin map is exported for the firmware to import. Not built yet: checking the firmware on a Mac against it ([P59](https://github.com/xmejkal/spark/issues/7), [P74](https://github.com/xmejkal/spark/issues/8)) | `assign_pins.py --emit-pins` |
| [Simulate](docs/guide/journey.md#simulate) | **partly**: the build generates the Wokwi diagram and stages the chips, kept only with `--sim-dir sim` ([P116](https://github.com/xmejkal/spark/issues/50)). A run needs a flash image, a scenario you write, `wokwi-cli` and a Wokwi account's CI token, and it spends Wokwi CI minutes; none was run here | `/spark:build`, then `wokwi-cli` |
| [Bench](docs/guide/journey.md#bench) | **not yet**: spark's hardware step is [P79](https://github.com/xmejkal/spark/issues/16). The first bench will be a separate project's, a sensor trash can given a new ESP32 brain ([P73](https://github.com/xmejkal/sisuo-brain-transplant/issues/2), its bring-up [B14](https://github.com/xmejkal/sisuo-brain-transplant/issues/8)) | — |

- **works**: it ran end to end for these docs.
- **partly**: it stops before its goal, or part of it was not run here (agents, a conversation, or a paid simulation
  run); the row says which.
- **not yet**: nothing does it yet; the linked issue plans it.

Already have a board written by hand in tscircuit? The checks read any built board: build it with
`npx --no tsci build board.tsx`, run `/spark:init`, which names the rails from the build, then
`check_all.py --project .`. That sequence was not run here. A project's own `make check` can also run the checks one by
one ([the glossary](GLOSSARY.md#make-check--a-projects-own-gate)).

## Before you start

- Claude Code, for the commands.
- Python 3.9 or newer.
- Node 20 or newer. On macOS, spark's install lines get Node and pdftotext from Homebrew (`data/tools.json`).

`/spark:setup` then installs the rest with one yes: bun, tscircuit (into the project), `wokwi-cli` and MicroPython. The
runs here were on macOS. `data/tools.json` also has Linux (apt) install lines, which were not run here, and none for
Windows.

## Install, and a first run

In Claude Code:

```
/plugin marketplace add xmejkal/spark
/plugin install spark
```

The marketplace is named `petr-local`, so Claude Code may show the plugin as `spark@petr-local`. This install path was
not run for these docs.

Then, in a project folder:

1. `/spark:init` writes the project's files without guessing, including the `package.json` that tscircuit, the engine
   that builds the board, installs into.
2. `/spark:setup` shows the tools spark needs, and installs what is missing with one yes.
3. Put a `requirements.json` in the folder: the dev board and a list of parts, by the ids `parts.py --list` prints.
   Copy the example on [`/spark:build`'s page](commands/build.md#the-requirements-file), or ask Claude to design the
   board; the `spark-design` skill writes the file with you (not run here).
4. `/spark:build` turns it into a board.
5. `/spark:init` again. It names the rails from the built board, and its page's last step runs
   `check_all.py --project .`.

For the documented example, the build ends:

<!-- output: run 2026-10-05, spark 0.6.0 -->
```text
  …
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

19 routed traces carry the 22 written connections: a group of N connected pins needs N−1 traces
([the full output](docs/guide/journey.md#build)). All green here: the conflict above shows only in `parts.py --show`
and in `board.tsx`'s closing comment.

This ran with tscircuit linked into the project from an existing install, not installed by `/spark:setup`.
tscircuit's install (`tools.py --install`, the step behind setup's one yes) last ran in P82's third cold run on
2026-10-03. The slash command's one yes last ran on 2026-10-04, for the MicroPython build only
([P82 in the backlog's archive](scrum/PRODUCT_BACKLOG.md#p82--setting-up-spark-is-one-step-like-installing-a-package--slice-1-the-pos-request-of-2026-10-03--done-2026-10-03)).

To look at the board, [see it](commands/build.md#see-it) in tscircuit's viewer. From the draft to an order, see
[the journey's last steps](docs/guide/journey.md#from-draft-to-order).

An update replaces the plugin, not your files. Your store and a project's own `boards/`, `parts/` and `.spark/` are
outside it ([how it works](docs/guide/how-it-works.md#your-store)). A record copied into the plugin's own library with
`parts.py --promote` lives inside the plugin.

## Commands, skills and agents

**Commands**, typed in Claude Code:

- `/spark:init`: a project;
- `/spark:setup`: the tools;
- `/spark:drawer`: what you own;
- `/spark:idea`: a goal to needs;
- `/spark:research`: a missing part;
- `/spark:identify`: a module from a photo;
- `/spark:build`: a requirements file to a board.

**Skills**, which Claude picks up from your words: `spark-design` designs a board; `spark-review` reviews it and gates
it before ordering; `spark-reverse-engineer` reads a board from its photo (not run here; its bench-protocol template
was written for the smart bin's original board).

**Agents**, launched by the commands and skills: `part-finder` and `datasheet-reader` for a commodity part (an LED, a
button, a connector: one datasheet describes it), `parts-researcher` for a module, and `design-reviewer`, one per
review dimension (power, signals, thermal-mechanical, manufacturability, firmware-hardware).

Each one, with when to use it and what it writes and refuses: [the commands guide](docs/guide/commands.md).

## Without Claude Code

spark's scripts run in any terminal, for you or another AI: plain Python. They exit 0 ok, 1 problems, 2 could-not-run,
and most answer in JSON with `--json`. Read [the guide for AI agents](docs/guide/agents.md) before trusting an exit
code: `check_all.py` exits 0 even when most checks were never asked, and a crash exits 1.

The conversations need Claude Code: the idea, research, identify, the review's agents and the drawer import.
[`AGENTS.md`](AGENTS.md) points to the same guide.

## What it uses underneath

- **[tscircuit](https://tscircuit.com)** builds the board. `/spark:setup` installs it into the project at the version
  spark pins.
- **Node and bun.** Node runs the diagram converter, npm and the MCP servers; bun runs tscircuit's `tsci`.
- **[Wokwi](https://wokwi.com)** simulates the board.
  - The build generates the diagram and stages the chips: hand-written models of modules Wokwi has no part for, kept
    beside a part's record, and compiled with `wokwi-cli` only when the binary is missing or older than its source.
  - A run needs a Wokwi account's CI token in `WOKWI_CLI_TOKEN` (wokwi.com/dashboard/ci), and it spends CI minutes.
  - Watching it in VS Code needs a Wokwi licence that includes VS Code, Hobby+ or above per wokwi.com/pricing (read
    2026-10-01).
- **[MicroPython](https://micropython.org)** and the project's files make up the flash image a simulation runs.
- **Two MCP servers**, declared by spark for its research agents. Claude Code starts both with `npx -y`, unpinned
  ([P112](https://github.com/xmejkal/spark/issues/46)):
  - `@jlcpcb/mcp`, an unofficial community package ([l3wi/jlc-cli](https://github.com/l3wi/jlc-cli)), for part
    search;
  - `mcp-remote`, which connects to Espressif's hosted documentation server.
- **Claude in Chrome**, for the DFRobot order import only.
- **Your store**, `~/.local/share/spark`, outside every repository, holds what you own and what research kept.
- **[KiCad](https://www.kicad.org)'s `kicad-cli`**, optionally, for the review and design skills' electrical-rule and
  design-rule checks.

How the scripts, the data and the chain fit together: [how spark works underneath](docs/guide/how-it-works.md).

## Before ordering

The generated board is a draft, and the header of `board.tsx` says so. Its modules sit in a column that does not
overlap, and it has no mounting holes or connector keying. Its trace widths are not sized for current until each
rail's current is stated.

1. **State each rail's current,** as `max_current_a` in `.spark/rules.json` or as figures in the part records.
2. **Generate the board again.** Delete `board.tsx` and run `/spark:build`, because an existing `board.tsx` is never
   overwritten. If you have already laid it out, move it aside first and carry the new trace widths over by hand.
3. **Lay it out, then build your own `board.tsx`:** `npx --no tsci build board.tsx`. Until
   [P110](https://github.com/xmejkal/spark/issues/44) lands, `/spark:build` rebuilds `dist/`, which every check reads,
   from the requirements file, not from your `board.tsx`.
4. **Run the `spark-review` skill:** its reviewer agents, then the fabrication gate.
   - The gate's `boards.py --validate --for-fab` refuses a dev-board definition that breaks its contract or names no
     footprint.
   - `parts.py --unverified` lists the unverified facts and pin orders of the parts you name.
   - Neither reads the generated board, or lists the dev board's own unverified figures
     ([P126](https://github.com/xmejkal/spark/issues/60)).
5. **If you have KiCad,** run `npx --no tsci export board.tsx -f kicad_pcb -o board.kicad_pcb`, then
   `kicad-cli pcb drc board.kicad_pcb`. No check here is a design-rule check, and tscircuit's autorouter can emit
   shorts; the build stops only on the errors tscircuit's own routing checks write into `circuit.json`.
6. **Have a person look at the layout.**

[The journey's last steps](docs/guide/journey.md#from-draft-to-order) show the exports run on the example.

## Honest limits

- **The reviewer agents in `spark-review` are less proven than the checks.**
  - The only measurements were a few eval runs, one to three per arm, comparing the plugin with a no-plugin baseline
    ([tabled in the 2026-09-24 audit](docs/audit-2026-09-24/autonomous-agent-readiness.md#on-the-eval-and-the-reprioritisation-it-drove)).
  - Each case graded what the agent found, not a script, and the cases were removed in commit 066c4af.

  Treat "the reviewers help" as plausible, not measured.
- **Nothing here has been validated on hardware by its author.** Ground truth is the bench.

## More

- [The glossary](GLOSSARY.md): the words this repository uses its own way, each with the failure that produced it.
- [Developing spark](docs/guide/developing.md): the tests, the commit gate, and where the work is planned.
- **Found a problem?** [Open an issue](https://github.com/xmejkal/spark/issues/new) with the command you ran, its
  output and spark's version (in `.claude-plugin/plugin.json`). A form for this is
  [P128](https://github.com/xmejkal/spark/issues/62).

---

v0.6.0 · [MIT](LICENSE) · built with the tscircuit engine.
