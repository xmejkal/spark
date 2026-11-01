# For AI agents

## The contract, first

This guide has four pages. Open the one you need:

| page | open it when |
| --- | --- |
| this page | you start: the contract, Claude Code, the outcomes and their exit codes, and whether a design is ready |
| [the scripts](agents/scripts.md) | you run spark outside Claude Code: set up, the store, what reads and what writes |
| [the JSON](agents/json.md) | you read an answer: check_all's results, each script's keys, `missing_facts`, the look and deploy envelope |
| [what never to assume](agents/never-assume.md) | before you report a pass: each answer that looks like one and is not |

Read these rules before you run a script:

1. **Three words, three exit codes.** `ok` exits 0, `problems` exits 1 and `could-not-run` exits 2. `check_all.py`
   adds `skipped`. A crash also exits 1, so read the JSON, not only the code
   ([the outcomes](#the-outcomes-and-their-exit-codes)).
2. **These are not a pass:** `could-not-run`, `skipped`, `unknown`, a `null` and a `?` line. Never fill in a `null`
   ([what never to assume](agents/never-assume.md)).
3. **`check_all.py` exit 0 means less than it says.** No check that ran found a problem. Read `resolved` to see that
   it found the circuit and the rules ([what exit 0 means](agents/json.md#what-exit-0-means)).
4. **Relay a "passed, but ..." answer whole.** `run_scenario.py` prints it after a pass with no set-control step. A
   bare `passed` clears no caveat ([rule 8](agents/never-assume.md#8-a-passed-run-did-only-what-its-scenarios-steps-say)).
5. **Ask `parts.py --describe --json` first.** It says which `parts.py` operations write and which reach the
   network. Run each write with `--dry-run` first. A network operation needs the person's yes
   ([what reads and what writes](agents/scripts.md#what-reads-and-what-writes)).
6. **Build with `--keep <folder>`, then read `missing_facts`.** `status` can be `ok` while the board record lacks a fact
   the firmware needs. Never guess that fact. Ask the person
   ([`missing_facts`](agents/json.md#check_spinepy)).
7. **Check someone else's project in a scratch store** (`SPARK_HOME`). Never put the person's drawer, history or
   projects list into a URL, a prompt or a commit.

A build of spark's button-and-LED example, shortened with `...`:

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/check_spine.py" requirements.json --keep build --json
```

<!-- output: run 2026-11-01, spark 0.9.0 -->
```text
{"check": "spine", "status": "ok",
 "stages": [{"name": "board", "status": "ok", "detail": "DFRobot FireBeetle 2 ESP32-S3 ..."},
            ...
            {"name": "simulation", "status": "ok", "detail": "7 wire(s) in the diagram\n ... onboard GPIOs: not checked: ..."}],
 "kept": [{"file": "build/breadboard.md", "did": "wrote", "why": "the parts and how to wire them on a breadboard"},
          {"file": "build/breadboard.json", "did": "not written", "code": "no_wokwi_part", "subject": null,
           "expected": true, "why": "Wokwi has no part with this board's pins"},
          {"file": "build/firmware/pins.py", "did": "wrote", "why": "the pins the firmware imports"},
          ...]}
```

Read it in this order. `status` is `ok`, and every stage is `ok`. The simulation stage did not check the board's own
GPIOs, so say so. `breadboard.json` was not written, and `expected: true` says that is by design, so do not retry.
This build has no `missing_facts` key, so the board record names the active level of its onboard LED and button.

This page is for an AI working with spark:

- **in Claude Code,** through the person's commands;
- **anywhere else,** through spark's scripts.

Act on what the scripts answer, the JSON and the exit code, not on what their source seems to say. (spark's own
agents, `part-finder` and the others, are in the [commands guide](commands.md#agents).)

## In Claude Code

The person types a `/spark:` command, and you follow that command's page in [`commands/`](../../commands/). The
[commands guide](commands.md) says when to use which. Skills are picked up from the person's words. The agents
(`part-finder`, `datasheet-reader`, `parts-researcher`, `design-reviewer`) are launched by the commands and skills that
name them.

A command page's `allowed-tools` lists the operations Claude Code lets you run without asking. `parts.py --fetch` and
`--sources`, `tools.py --install` and `--on`, and `check_vendor_pins.py` without `--offline` reach the network and are
on no command's or skill's list, so Claude Code asks the person before any of them runs, and their answer is the yes.
Their own settings can answer first: an allow rule of theirs, or auto mode, can let it run without asking, which is a
yes given in advance, and auto mode can also refuse it. You do not work around either. `parts.py --describe --json`
marks the network operations of `parts.py`.

A new project starts with `/spark:init`, then `/spark:setup`. The [journey guide](journey.md) shows each step on real
runs.

Outside Claude Code, the command pages and skills are plain Markdown, but their agents are Claude Code agent
definitions (`agents/*.md`: a model and a tool list). The scripts their steps call run anywhere; following a command
page outside Claude Code was not tried for these docs.

## The outcomes and their exit codes

The exit codes are defined once, in [`scripts/spark/core/outcomes.py`](../../scripts/spark/core/outcomes.py); the command-line scripts
import them from there. Every script ends in exactly one of three outcomes, never a bare pass or fail:

| exit | word | meaning |
| --- | --- | --- |
| 0 | `ok` | it looked and found nothing |
| 1 | `problems` | it looked and found something |
| 2 | `could-not-run` | it could not look: no input, no toolchain, or a file it could not read |

`check_all.py` adds a fourth word, `skipped`: a check that was never asked, because its input was not given. That is
not the same as one that could not look. More in the glossary:
[the three outcomes](../../GLOSSARY.md#the-three-outcomes--ok-problems-could-not-run) and
[`skipped`](../../GLOSSARY.md#skipped--the-fourth-word-and-only-check_all-has-it).

**What `check_all.py`'s exit 0 means** is less than it says: [check_all's answer](agents/json.md#what-exit-0-means)
gives each case.

**Not yet true everywhere:**

1. `check_vendor_pins.py --json` prints a bare list and says `mismatch` where this table says `problems`, and the
   `--json` shapes differ by script ([P43](https://github.com/xmejkal/spark/issues/11)).
2. **A crash exits 1, which this table reads as `problems`.** [A crash](#a-crash-exits-1) below says which scripts
   crash on what, and which answer 2 instead.
3. A bad command line (an unknown flag, or `CLAUDE_PLUGIN_ROOT` unset) exits 2 with nothing on stdout, except that
   `parts.py --json` answers an argument it cannot run with in its envelope (`status` is `could-not-run`). With
   `CLAUDE_PLUGIN_ROOT` unset, Python never starts the script, so even that prints nothing. A bad command line is not a
   check that could not look, so with `--json`, parse stdout before trusting the code.
4. **`init_project.py`'s exits.**
   - Without `--board`, it exits 1 when every file exists ("nothing to do").
   - With `--board`, it exits 0 even when it wrote nothing.
   - It exits 2 after writing everything when two built designs left the rails unseeded.

   1 is also what a crash returns, so check stdout for the nothing-to-do line before reading exit 1 that way.
5. `parts.py` given an id it does not know ("no part called …") exits 1, and so does `--show` of a record with a
   CONFLICT on verified facts (`data.record` is set then, `null` for an unknown id).

### A crash exits 1

- A script run on its own can crash on an input it cannot read: exit 1, a traceback on stderr, nothing on stdout
  ([P131](https://github.com/xmejkal/spark/issues/65)). So exit 1 with an empty stdout is a crash, not problems.
  check_all reports each crash as could-not-run.
- `look.py` is the exception: it answers a crash with an envelope and exit 2
  ([its envelope](agents/json.md#lookpy-and-deploypys-envelope)).
- `compare_design.py`, `assign_pins.py` and `check_spine.py` answer 2 instead of crashing
  ([check_spine.py's refusals](agents/json.md#check_spinepy)).
- These inputs crash a script:
  - a circuit file that is not JSON (`check_footprints.py`, `check_physics.py`);
  - a board file that is not JSON or not there (`check_vendor_pins.py`);
  - a fab package with no `bom.csv` or that is not a zip, or a `--circuit` that is missing or not JSON
    (`check_bom.py`);
  - an `init_project.py --circuit` that is not JSON.
- Two more crash too:
  - `check_vendor_pins.py` without `gh`, unless given `--offline` ([P119](https://github.com/xmejkal/spark/issues/53));
  - `check_physics.py` on a bus named by nets that carries a pull-up, when `i2c_hz` is stated and
    `i2c_bus_capacitance_pf` is null ([P107](https://github.com/xmejkal/spark/issues/41)).
- `emit_board.py` with the library LED on a board whose file states no `power.io_volts` (the library's XIAO did not
  until P278) is a refusal, not a crash: exit 2, nothing on stdout, and on stderr `cannot emit a board: led-red-5mm asks
  for 5 mA through a series resistor, but the board states no power.io_volts — nothing to compute it from`
  ([P121](https://github.com/xmejkal/spark/issues/55)).

## What never to assume

The rules are on their own page: [what never to assume](agents/never-assume.md).

## Is it ready?

check_all is the deterministic half, run on the last build. Before ordering comes the rest of the `spark-review`
skill: its design-reviewer agents, then its last step, the fabrication gate.

- **The fabrication gate's scripts run anywhere.**
  - `boards.py --validate --for-fab` checks every dev-board definition available, the library's included and not only
    the active one. With `--for-fab` it also requires each to name a footprint (`physical.footprint_module` and
    `footprint_export`). It reads nothing of `board.tsx` or the build, and a problem in an unused library board fails
    it too.
  - `parts.py --unverified` runs for every part. It exits 0 even when items are open, so read its list (with `--json`,
    `assumptions`).
  - Neither lists the dev board's own unverified figures: `boards.py --get power --project .` shows them, such as the
    FireBeetle's `regulator_3v3_a` and `deep_sleep_ua` ([P126](https://github.com/xmejkal/spark/issues/60)).
- **The design-reviewer agents run only in Claude Code.** Outside it, say they were not run.
- **The rest of the journey's [from draft to order](journey.md#from-draft-to-order):**
  - regenerate after the currents are stated;
  - build the person's own `board.tsx`;
  - a design-rule check, then a person's look at the layout. The check:

```sh
npx --no tsci export board.tsx -f kicad_pcb -o board.kicad_pcb
kicad-cli pcb drc --exit-code-violations --format json -o drc.json board.kicad_pcb
```

`--exit-code-violations` makes `kicad-cli` exit 5 when it finds violations, and 0 when it finds none
([KiCad's CLI](https://docs.kicad.org/8.0/en/cli/cli.html)); read `drc.json`. Both exports write into the project.

**What "ready" means.** An open fact is load-bearing for the PCB when its `why_it_matters` names a supply, a pin order,
a current or a footprint. The skill's rule is that each such fact is settled, or accepted out loud by the person. If
the reviewers or the design-rule check could not run (outside Claude Code, or with no KiCad), say so; do not skip them
silently. Whether it is then ready is the person's call.

There is no bench step yet.
