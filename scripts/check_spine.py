#!/usr/bin/env python3
"""
The one thing that has to work: a module list in, a board that builds out.

    check_spine.py                       # the reference design that ships with spark
    check_spine.py my-requirements.json  # your own
    check_spine.py --json

WHY THIS EXISTS

spark is a chain — parts, pin assignment, schematic, footprint, build — and every link had its
own tests, all green, while the chain itself had never once been run end to end. It produced a
board with zero traces for weeks under a docstring that said it "BUILDS", and four independent
defects were sitting in it, each alone enough to cause that:

  * a part file whose footprint said five pads and whose pinout named seven,
  * a missing footprint quietly defaulting to a four-pad one,
  * a rule named `rails_without_a_source` that never looked for a source,
  * and its mirror, warning that a correctly-supplied rail went nowhere.

None of them was findable from a unit test, because each component did exactly what its own
tests asked. They were only visible by running the whole thing and counting what came out.

WHAT IT MEANS TO PASS

Not "no exception was raised". A board is only built if copper reached it:

    the build succeeds, AND at least one pcb_trace exists, AND no *_error element is present

The trace count is the load-bearing clause. tscircuit's autorouter can fail on a single
unroutable net and skip routing entirely, which does not raise — it returns a circuit with every
component placed, every port present, and no copper at all. That artefact passes every structural
check that does not think to count traces, and it is exactly what this tool shipped.

WHAT IT REFUSES TO CALL A PASS

If `tsci` is not installed, the build stage is `could-not-run` and the exit code says so. A chain
that could not be exercised has not been proven; it has been skipped, and the difference is the
whole point of this file.

If it IS installed and cannot build a trivial board from the working directory, the same. A tool
that fails on a resistor is not reporting on the design, and "the chain is broken" for a broken
tool sends somebody to debug a design nobody examined — the mirror image of a false pass, and as
misleading. Every build verdict names the tsci that produced it, because "exit 0" once depended
on which one PATH found first, and nothing said so.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

import assign_pins  # noqa: E402
import boards  # noqa: E402
import breadboard  # noqa: E402
import breadboard_drawing  # noqa: E402
import design  # noqa: E402
import emit_board  # noqa: E402
import init_project  # noqa: E402
import needs  # noqa: E402
import netlist  # noqa: E402
import onboard_parts  # noqa: E402
import parts  # noqa: E402
import sim_project  # noqa: E402
import store  # noqa: E402
import tabbed_page  # noqa: E402
import tools  # noqa: E402
import emit_footprint  # noqa: E402

from spark.core.outcomes import EXIT_OK, EXIT_PROBLEMS, EXIT_COULD_NOT_RUN, NOT_CHECKED, OK, PROBLEMS, COULD_NOT_RUN, SKIPPED, EXIT_FOR, STATUS_FOR, status_of  # noqa: E402
from spark.core.result import envelope_item  # noqa: E402
from spark.core.text_guards import guard_lines  # noqa: E402

#: The design the chain is proven against when nobody names one. A motor driver, a sensor on a
#: bus, and the power inlet that supplies the rail the modules only consume — the smallest set
#: that exercises pin assignment, a bus, a rail with an external source, and two footprint kinds.
REFERENCE = {"board": "firebeetle2-esp32s3",
             "parts": ["l9110s-module", "vl6180x-breakout", "jst-ph-2-power-inlet"]}

BUILD_TIMEOUT_S = 300

#: Where --keep puts the pin map, the path every document gives `--emit-pins` (P196).
PIN_MODULE = Path("firmware") / "pins.py"

#: The stage that reads the requirements file; its detail is why a refused file built nothing (P280).
REQUIREMENTS_STAGE = "requirements"
#: The `did` of a kept entry for a part the person moved in breadboard.json that the build could not keep (P273).
MOVE_NOT_KEPT = "move not kept"
#: The `did` of a kept entry for one thing a rebuild asks a person to change on the bench (P300).
CHANGED = "changed"
#: The `did` of a kept entry for one end the drawn breadboard joins differently from circuit.json's points (P279).
DRAWING_DIFFERS = "drawing differs"
# --- MVP ---
#: What a build stopped at the footprint stage still gives, after the gaps `emit_footprint.why_no_footprint` lists (P407).
NO_FOOTPRINT_HINT = ("The schematic was not tried. The pin map needs no footprint: with --keep, the kept lines say "
                     "whether firmware/pins.py was written. The breadboard sheet and the simulation read the built "
                     "board, so they wait for the footprint.")


def said_of_a_crash(program, crash):
    """
    How a crash in `program` reads as a stage's detail, raw (P430): its last traceback line, as the child's stderr gave it (F5).
    The text is guarded when it is printed (`render`), and `--json` keeps it as it stands.
    """
    return "%s crashed: %s: %s" % (program, type(crash).__name__, str(crash))


class Stage:
    """One link, and what became of it."""

    def __init__(self, name, status, detail=""):
        self.name, self.status, self.detail = name, status, detail

    def __repr__(self):
        return "Stage(%r, %r)" % (self.name, self.status)


def find_toolchain(start):
    """
    `tsci`, or None — the board-engine from the tools list (P82): the project's own node_modules,
    upward from `start`, then the PATH — the same places a person would look, and in that order
    because a project's own pinned version beats whatever is installed globally.
    """
    try:
        return Path(tools.find("board-engine", start).command[0])
    except tools.ToolProblem:
        return None


def modules_for(toolchain):
    """
    The `node_modules` a project-local tsci lives in, or None for a global one.

    tsci resolves the emitted board's imports upward from the build directory, so a project's
    own `node_modules` has to be reachable from the working directory; `main` links it in. A
    GLOBAL tsci resolves them from its own install and needs nothing linked — and linking
    `toolchain.parent.parent` for it, which is the Node prefix and not a `node_modules`, put a
    directory with no `react` in it first on the path and broke a toolchain that built the same
    board on its own. That was the "toolchain fault" of audit A9: the spine's fault, not the
    tool's. Measured 2026-09-29: nvm's global 0.0.2600 builds with no link, and fails with the
    prefix linked.
    """
    modules = toolchain.parent.parent
    if toolchain.parent.name == ".bin" and modules.name == "node_modules":
        return modules
    return None


#: The smallest board that should build anywhere: what the preflight asks of a toolchain that
#: produced nothing, to tell "the design is broken" from "the tool is".
TRIVIAL_BOARD = """export default () => (
  <board width="10mm" height="10mm">
    <resistor name="R1" resistance="1k" footprint="0402" />
  </board>
)
"""


def toolchain_can_build(toolchain, workdir):
    """
    Whether this tsci builds a trivial board from this working directory at all.

    Run only after a build produced no circuit.json, so the happy path pays nothing. Returns
    (built, the tool's last words) — the words matter, because "Cannot find package 'react'"
    names a broken install where "no circuit.json" names nothing.
    """
    probe = workdir / "spark-probe"
    probe.mkdir(exist_ok=True)
    (probe / "board.tsx").write_text(TRIVIAL_BOARD)
    result = subprocess.run([str(toolchain), "build", "board.tsx"], cwd=str(probe),
                            capture_output=True, text=True, timeout=BUILD_TIMEOUT_S)
    return (probe / "dist" / "board" / "circuit.json").is_file(), result.stderr.strip()[-400:]


def tsci_version(toolchain):
    """What `tsci --version` says, or "unknown version" — never an exception, never nothing."""
    try:
        said = subprocess.run([str(toolchain), "--version"], capture_output=True, text=True,
                              timeout=60).stdout.strip().splitlines()
        return said[-1].strip() if said else tools.UNKNOWN_VERSION
    except (OSError, subprocess.TimeoutExpired):
        return tools.UNKNOWN_VERSION


#: Where a project may carry its own converter, for its developer; otherwise the tools list's diagram-converter, the
#: plugin's bundle, runs (B10, P82). Searched up from the project, never from the current folder (backlog P32a).
CONVERTER_PATHS = ("tools/circuit-to-wokwi/cli.ts",)


def find_converter(start):
    """A project's own TypeScript converter, for its developer — or None, and the tools list's converter runs.

    Never the plugin's own source: a requirements file in no project resolves to the plugin, and its
    cli.ts needs node_modules an installed plugin does not have (the final review of P82). What the
    plugin ships is the bundle, which the tools list names as the diagram-converter (B10).
    """
    for directory in boards.walk_up(start):
        for relative in CONVERTER_PATHS:
            candidate = (directory / relative).resolve()
            # A spark checkout's own source — this plugin, or another found walking up — is never a project's.
            if candidate.is_file() and not (directory / "scripts" / "check_spine.py").is_file():
                return candidate
    return None


def converter_command(project, own):
    """The command that converts: a project's own cli.ts under the ts-runtime; else the tools list's
    diagram-converter — the bundle under the js-runtime, or a swapped converter as it is."""
    if own is not None:
        return tools.find("ts-runtime", project).command + ["run", str(own)]
    converter = tools.find("diagram-converter", project)
    if converter.entry.get("kind") == "bundled":
        return tools.find("js-runtime", project).command + converter.command
    return converter.command


def converter_stage_problem(project, own=None):
    """None when the converter and what runs it are here; else the could-not-run Stage saying which and how to install it."""
    try:
        converter_command(project, own)
    except tools.ToolProblem as missing:
        return Stage("simulation", COULD_NOT_RUN, str(missing))
    return None


#: What the converter says when it has no Wokwi part for a component. That is a limit of the
#: converter's mapping table, not a defect in the design — the board built — and reporting it as
#: "the chain is broken" sent a reader to debug a design that was fine (audit B11, A9's shape at
#: the last stage). Matched on the converter's own words, which its tests pin.
CONVERTER_HAS_NO_PART = "no Wokwi part is mapped"


def simulation_could_not_look(said):
    """Whether the converter's output describes its own limit rather than the design's."""
    return CONVERTER_HAS_NO_PART in (said or "")


#: Wokwi's serial monitor, as a diagram names it: its two wires are the board's own, never a design's (P190).
SERIAL_MONITOR = "$serialMonitor"


def wires_in(diagram):
    """Connections between parts; the serial monitor's two are not counted, so all nets failed still counts 0."""
    return sum(1 for connection in diagram.get("connections") or []
               if not any(str(end).startswith(SERIAL_MONITOR) for end in connection[:2]))


def serial_wired(diagram):
    """Whether the board's serial port reaches Wokwi's serial monitor, so a scenario hears what the firmware prints."""
    return any(str(end).startswith(SERIAL_MONITOR) for connection in diagram.get("connections") or []
               for end in connection[:2])


def serial_heard(diagram, board):
    """P468: wired, or the board's record says its serial needs no wires (`serial_without_wires`, True only)."""
    return serial_wired(diagram) or (board or {}).get("serial_without_wires") is True


def count_in(circuit):
    """Traces and errors, which is what 'did it build' actually means."""
    traces = sum(1 for element in circuit if element.get("type") == "pcb_trace")
    errors = [element for element in circuit if "error" in (element.get("type") or "")]
    return traces, errors


#: Nets that are a ground: the generator's list, so this rule and its supply rule agree.
GROUND_NETS = emit_board.GROUND_NETS
#: tscircuit's types for the two-terminal parts a generated board places between a pin and a rail.
PASSIVE_FTYPES = ("simple_resistor", "simple_capacitor", "simple_inductor", "simple_diode")


def islands_in(circuit, claims=(), across=()):
    """
    Every component the board leaves on an island, said in its own words. `across` names the
    components that sit across a driven pair (`emit_board.loads_across_a_pair`: a speaker
    terminal, C-3) — asked, as a passive is, whether an end dangles, never whether they reach ground.

    Three questions, because a component can be stranded in three ways and a board builds,
    routes and reports no error for any of them:

    * **no ground.** A part can be perfectly placed, carry every pad, route its signals and share
      no return path with anything. tscircuit checks that each trace you asked for is satisfiable,
      never that you asked for the ones a circuit needs.
    * **a terminal on nothing.** A two-terminal passive is asked a different question — a pull-up,
      or the top of a divider, sits between a pin and a rail and reaches no ground BY DESIGN, and
      was reported here as an island the evening P6 placed the first ones. What must hold for it
      is that neither end dangles.
    * **an unfed supply pin** (`claims`, from `emit_board.supply_inputs`). This is P29's half. The
      irrigation controller's buck record says "Feeds the FireBeetle's 5 V/VCC input and the
      sensors"; net.V5V joined the buck to a flow meter, the processor was on no 5 V net at all,
      and the stage read `[ok]`. `claims` is what the design STATES, so this compares the built
      circuit against the file rather than against a guess about which nets look like rails —
      tscircuit's own `is_power` flag would not do: it is a name heuristic, and it calls the smart
      bin's MOTOR6V a signal.

    Connection is counted through the source netlist rather than through copper, because a pin on
    a poured net has no trace of its own and is connected all the same. The walk itself is
    `netlist.Netlist`, shared with `compare_design` and `check_physics` — on one circuit the three
    private copies of it gave three different answers (backlog P35).
    """
    board = netlist.Netlist(circuit)
    ground_ids = {net_id for net_id, net in board.nets.items()
                  if (net.get("name") or "").upper() in GROUND_NETS}
    names = {cid: element.get("name") or "?" for cid, element in board.components.items()}
    passives = {cid for cid, element in board.components.items()
                if element.get("ftype") in PASSIVE_FTYPES or element.get("name") in across}
    grounded, present = set(), set()
    for port_id, net_ids in board.nets_of_port.items():
        owner = board.ports[port_id].get("source_component_id")
        present.add(owner)
        if net_ids & ground_ids:
            grounded.add(owner)
    # A component with no trace at all is a separate complaint, already covered by the parts that
    # refuse to emit. Report only those that are wired to something and to no ground — for a chip.
    findings = ["%s reaches no ground" % names.get(owner, "?")
                for owner in present - grounded if owner not in passives]
    findings += ["%s.%s (a terminal connected to nothing)"
                 % (names.get(port.get("source_component_id"), "?"), port.get("name") or port_id)
                 for port_id, port in board.ports.items()
                 if port.get("source_component_id") in present & passives
                 and port_id not in board.nets_of_port]
    for component, pin, net in claims:
        wanted = board.net_named(net)
        if wanted is None or wanted not in board.nets_of(component, pin):
            findings.append("%s.%s is fed by net.%s in this design and is not on it"
                            % (component, pin, net))
    return sorted(findings)


def core_note(version):
    """
    What to add when the `tscircuit` core is not the one the documents were measured on.

    `tsci --version` prints the CORE, not the CLI, and `@tscircuit/cli` takes `tscircuit: "*"` as a
    peer dependency — so a project whose package file pins only the CLI gets whatever core is
    newest, and every number this plugin publishes was measured on a different one. That is not
    hypothetical: it is how P33 came to pin `0.0.2600` as a version of the CLI, which does not
    exist, and nobody noticed for a sprint because a global CLI carrying the right core sat on
    this machine's PATH (P51).

    Silence means they agree. A build is never failed for this — a newer core may be perfectly
    good — but it is never passed in silence either.
    """
    if version in (tools.UNKNOWN_VERSION, init_project.PINNED_CORE):
        return ""
    return "; the documents were measured on core %s" % init_project.PINNED_CORE


def run(requirements, workdir, toolchain=None, project=None, from_library=False, firmware=None):
    """
    Every stage, in order, stopping at the first that cannot produce input for the next.

    `project` is where the design's parts and rules live, resolved by `main` from the
    requirements FILE — never from the current directory. Resolved from `cwd`, a run from
    anywhere but inside the project said `no part called 'sg90-servo'` about a part sitting
    beside the file. None means the plugin's own library, which is what the reference design is
    built from and must not require a surrounding project for.
    """
    stages = []
    project = project or SCRIPTS.parent

    # --- parts and pin assignment, via the generator that owns them ---
    try:
        board = boards.load(project, requirements.get("board"))
    except Exception as exc:  # noqa: BLE001
        return stages + [Stage("board", COULD_NOT_RUN, str(exc))]
    stages.append(Stage("board", OK, board["name"] + (
        " — from the plugin's library; no project up from the requirements file, so no rules"
        if from_library else "")))

    # Nothing to build is not a pass. An empty parts list came out `ok` end to end (two traces, two wires), which proves
    # nothing about the chain and reads as though it did. Intake row M3 had it as `problems` on 09-25; both were wrong.
    if requirements.get(needs.BOARD_ONLY) is True:
        if requirements.get("parts"):
            return stages + [Stage("parts", COULD_NOT_RUN, "the requirements say board_only and name parts: say one")]
        return stages + board_alone(board, workdir, firmware, project)
    if not requirements.get("parts"):
        return stages + [Stage("parts", COULD_NOT_RUN,
                               "the requirements name no parts, so there is nothing to build; a "
                               "board holding only the microcontroller proves nothing. A project that runs "
                               'on the board alone says "%s": true' % needs.BOARD_ONLY)]

    # The design's own part records, so the build stage below can ask whether the circuit honoured what they state.
    # `emit_board` reads the same records; if that succeeded, this cannot fail for a reason not already told.
    try:
        part_list = design.parts_of(requirements, project)
    except design.DesignError as broken:
        return stages + [Stage("parts", COULD_NOT_RUN, str(broken))]

    # --- MVP --- the input is read, the pins are placed and the footprint is asked for, in the one order `emit_board.read_inputs`
    # gives (P407, P432): a fault in the requirements is said before a gap in the board record, and the schematic imports
    # the board's footprint, so a record that cannot give one stops here, before emit_board is asked.
    try:
        inputs = emit_board.read_inputs(workdir / "requirements.json", project)
    except emit_board.RefusedInput as refused:
        hint = "\n" + NO_FOOTPRINT_HINT if refused.stage == emit_board.FOOTPRINT_STAGE else ""
        return stages + [Stage(refused.stage, COULD_NOT_RUN, str(refused) + hint)]
    except Exception as crash:  # noqa: BLE001 -- emit_board ran in a child until P432, so a crash was a stage (F5), not a lost run
        return stages + [Stage(emit_board.SCHEMATIC_STAGE, COULD_NOT_RUN, said_of_a_crash("emit_board.py", crash))]

    board_file = workdir / "board.tsx"
    emitted = subprocess.run(
        [sys.executable, str(SCRIPTS / "emit_board.py"), str(workdir / "requirements.json"),
         "--project", str(project), "--assume-missing-sizes"],
        capture_output=True, text=True)
    if emitted.returncode == emit_board.EXIT_COULD_NOT_RUN:
        # It refused the input — a part with no measured outline, a resistor nothing sizes — in its own words.
        return stages + [Stage(emit_board.SCHEMATIC_STAGE, COULD_NOT_RUN, emitted.stderr.strip())]
    if emitted.returncode != 0:
        # emit_board exits 0 or 2 on purpose, so anything else is a crash: could-not-run, as `main` says of anything
        # unforeseen, with the traceback's last line. Read as problems, it sent people to debug a design nobody examined (F5).
        said = emitted.stderr.strip().splitlines()
        return stages + [Stage(emit_board.SCHEMATIC_STAGE, COULD_NOT_RUN, "emit_board.py crashed: %s" % (
            said[-1] if said else "exit %d, and nothing said" % emitted.returncode))]
    board_file.write_text(emitted.stdout)
    traces_asked = emitted.stdout.count(emit_board.TRACE_TAG)
    stages.append(Stage(emit_board.SCHEMATIC_STAGE, OK, "%d trace(s) written" % traces_asked))
    if emitted.stderr.strip():
        stages.append(Stage("schematic-notes", PROBLEMS, emitted.stderr.strip()))

    # --- the footprint the schematic imports ---
    # --- MVP --- drawn here with the design's rules; `read_inputs` already refused a rules file that cannot be read (P432, OC2).
    footprint_board = inputs.design.board
    export = (footprint_board.get("physical") or {}).get("footprint_export")
    rules = inputs.design.rules
    try:
        disagreement = emit_footprint.why_header_disagrees(footprint_board, rules)
        if disagreement:
            return stages + [Stage(emit_board.FOOTPRINT_STAGE, COULD_NOT_RUN, disagreement)]
        text = emit_footprint.render(footprint_board, rules)
    except Exception as crash:  # noqa: BLE001 -- the footprint script ran apart from this run until P432, so a crash was a stage
        return stages + [Stage(emit_board.FOOTPRINT_STAGE, COULD_NOT_RUN, said_of_a_crash("emit_footprint.py", crash))]
    (workdir / ("%s.tsx" % export)).write_text(text)
    stages.append(Stage(emit_board.FOOTPRINT_STAGE, OK, "%s.tsx" % export))

    # --- the build, which is the only stage that can prove any of the above ---
    # The project's tools file, not the scratch directory's: a broken or pinned project file must be read.
    toolchain = toolchain or find_toolchain(project or workdir)
    if toolchain is None:
        try:
            tools.find("board-engine", project or workdir)
            said = "the board engine was not found"
        except tools.ToolProblem as missing:
            said = str(missing)  # the tools list's own sentence, with what installs it (P82)
        return stages + [Stage("build", COULD_NOT_RUN,
                               "%s — so the chain was not exercised; /spark:setup installs it" % said)]

    built = subprocess.run([str(toolchain), "build", "board.tsx"],
                           cwd=str(workdir), capture_output=True, text=True,
                           timeout=BUILD_TIMEOUT_S)
    version = tsci_version(toolchain)
    circuit_path = workdir / "dist" / "board" / "circuit.json"
    if not circuit_path.is_file():
        # Nothing came out. Before blaming the design, ask the same tool for a resistor on a
        # board: a tool that cannot build that is not reporting on the design at all.
        can, last_words = toolchain_can_build(toolchain, workdir)
        if not can:
            return stages + [Stage("build", COULD_NOT_RUN,
                                   "%s (%s) cannot build even a trivial board from here, so this "
                                   "is the toolchain, not the design. Use the project's own tsci "
                                   "(npm i @tscircuit/cli in the project) or one that builds on "
                                   "its own.\n%s" % (toolchain, version, last_words))]
        return stages + [Stage("build", PROBLEMS,
                               "no circuit.json was produced by %s (%s), which does build a "
                               "trivial board\n%s" % (toolchain, version,
                                                      built.stderr.strip()[-800:]))]

    traces, errors = count_in(json.loads(circuit_path.read_text()))
    # NOT a trace count. Comparing connections asked for against `pcb_trace`s is wrong twice
    # over, and was tried here first: a net with N members needs N-1 traces, and a pin on a
    # poured net (V33 and GND are poured, 53 pours on this board) is connected by copper with no
    # trace at all. That rule failed a correct board, which is the mirror of the defect it was
    # chasing.
    #
    # The real invariant is grounding. The defect that prompted this was a microcontroller
    # sharing a net with NONE of its 32 pins — no ground, no 3.3 V — on a board that built,
    # routed and reported zero errors, while every module around it was correctly wired to a
    # ground the processor was not on.
    islands = islands_in(json.loads(circuit_path.read_text()),
                         emit_board.supply_inputs(board, part_list),
                         across=emit_board.loads_across_a_pair(part_list))
    if islands:
        return stages + [Stage("build", PROBLEMS,
                               "%s. A board builds, routes and reports no error with a component "
                               "joined to nothing — the parts around it are wired to nets it is "
                               "simply not on" % "; ".join(islands))]
    if errors:
        kinds = sorted({element["type"] for element in errors})
        return stages + [Stage("build", PROBLEMS, "%d error(s): %s" % (len(errors),
                                                                      ", ".join(kinds)))]
    if traces == 0:
        # The failure this file was written for. Everything is placed, nothing is connected, and
        # no exception was raised anywhere.
        return stages + [Stage("build", PROBLEMS,
                               "built with 0 pcb_traces — every component is placed and no "
                               "copper joins any of them. tscircuit skips routing entirely when "
                               "one net is unroutable, and that does not raise")]
    stages.append(Stage("build", OK, "%d trace(s), 0 errors, tsci %s%s"
                        % (traces, version, core_note(version))))

    # --- simulation: the last step of the product goal -------------------------
    # From the project, not from `cwd`: the same defect the project resolution had, one stage
    # later — run from /tmp the converter beside the project was "not found".
    own = find_converter(project)
    missing = converter_stage_problem(project, own)
    if missing:
        return stages + [missing]

    # What stands in for each part comes from the records (P31), not from a table in the
    # converter's repo: a record that says nothing stops here, naming itself.
    loaded = design.load(workdir / "requirements.json", None if from_library else project)
    mapping, chips, unmapped = sim_project.mapping_for(loaded)
    if unmapped:
        return stages + [Stage("simulation", COULD_NOT_RUN, sim_project.unmapped_detail(unmapped))]
    sim_dir = workdir / "sim"
    sim_dir.mkdir(exist_ok=True)
    (sim_dir / sim_project.MAPPING_FILE).write_text(json.dumps(mapping, indent=2) + "\n")
    (sim_dir / "board.json").write_text(json.dumps(board, indent=2) + "\n")
    staged, chip_problems = sim_project.stage_chips(chips, sim_dir)
    if chip_problems:
        return stages + [Stage("simulation", COULD_NOT_RUN, "\n".join(chip_problems))]
    (sim_dir / "wokwi.toml").write_text(sim_project.wokwi_toml(staged, firmware))

    diagram, stopped, notes = convert(project, own, ["--circuit", str(circuit_path)], sim_dir, workdir)
    if stopped:
        return stages + [stopped]
    wires = wires_in(diagram)
    if wires == 0:
        # The same failure shape as a board with no copper: every part placed, nothing joined.
        return stages + [Stage("simulation", PROBLEMS,
                               "a diagram with 0 connections. Every part is placed and none is "
                               "wired, which is what an unmapped component looks like once the "
                               "converter has given up on it")]
    compiled = sum(1 for how in staged.values() if how == "compiled")
    # What the simulation cannot show, in the records' own words, said and kept beside the diagram (P37).
    limits = sim_project.write_limits(sim_dir, loaded, board)
    return stages + [Stage("simulation", OK, simulation_detail(wires, staged, compiled, limits, serial_heard(diagram, board)) + notes)]


def convert(project, own, source, sim_dir, workdir):
    """
    The converter run on `source` (["--circuit", path] or ["--netlist", path]) and what `sim_dir` holds, merging into the
    person's kept diagram (P482): (the diagram, None, the merge notes), or (None, the Stage that stopped it, "").
    """
    diagram_path = sim_dir / "diagram.json"
    bad_kept = sim_project.copy_kept_diagram(workdir / sim_project.KEPT_DIAGRAM, sim_dir)
    made = subprocess.run(converter_command(project, own) + source + ["--out", str(diagram_path), "--mapping", str(sim_dir / sim_project.MAPPING_FILE),
                                                                      "--chips", str(sim_dir / "chips")], cwd=str(own.parent if own else sim_dir),
                          capture_output=True, text=True, timeout=BUILD_TIMEOUT_S, env=dict(os.environ, SPARK_BOARD_JSON=str(sim_dir / "board.json")))
    if made.returncode or not diagram_path.is_file():
        said = (made.stderr or made.stdout)[-800:]
        if simulation_could_not_look(said):
            return None, Stage("simulation", COULD_NOT_RUN, "the converter has no Wokwi part for a component on this board — a mapping "
                               "to add to its lib/mapping.ts, not a defect in the design, which built\n" + said), ""
        return None, Stage("simulation", PROBLEMS, "no diagram was produced\n" + said), ""
    notes = "".join("\n           " + note for note in (bad_kept, sim_project.kept_note(made.stdout), *sim_project.hand_added_warnings(made.stdout)) if note)
    return json.loads(diagram_path.read_text()), None, notes


def board_alone(board, workdir, firmware=None, project=None):
    """
    The stages after `board` for a project that runs on the board alone (P236): parts, schematic, footprint and build are
    SKIPPED, never ok. The converter wires the board's own LED and button that `onboard_parts` gives (P484), as `run` does;
    with none, the diagram holds the board's part alone. A limit "not checked" stays a limit in an ok stage (P396, P37).
    """
    skipped = [Stage(name, SKIPPED, "board only: nothing to wire") for name in ("parts", emit_board.SCHEMATIC_STAGE, emit_board.FOOTPRINT_STAGE, "build")]
    if not board.get("wokwi_part_type"):
        return skipped + [Stage("simulation", COULD_NOT_RUN, "the board record names no wokwi_part_type")]
    sim_dir, project = workdir / "sim", project or SCRIPTS.parent
    given, own = onboard_parts.read_board_alone(board, project), find_converter(project)
    stopped = given.wired and (converter_stage_problem(project, own) or (Stage("simulation", COULD_NOT_RUN, given.why) if given.why else None))
    if stopped:
        return skipped + [stopped]
    sim_dir.mkdir(exist_ok=True)
    (sim_dir / "wokwi.toml").write_text(sim_project.wokwi_toml((), firmware))
    for name, data in dict(given.files, **{"board.json": board}).items():
        (sim_dir / name).write_text(json.dumps(data, indent=2) + "\n")
    diagram, stopped, notes = (convert(project, own, ["--netlist", str(sim_dir / onboard_parts.NETLIST)], sim_dir, workdir) if given.wired
                               else (given.files["diagram.json"], None, ""))
    if stopped:
        return skipped + [stopped]
    limits = sim_project.write_limits(sim_dir, None, board, onboard_parts.say_wired_gpios(given.wired))
    return skipped + [Stage("simulation", OK, given.lead + simulation_detail(wires_in(diagram), {}, 0, limits, serial_heard(diagram, board)) + notes)]


def simulation_detail(wires, staged, compiled, limits, serial=True):
    """
    What the simulation stage says, including what it cannot show.

    Separated from `run` so a test can reach it: run's simulation stage needs a toolchain and a converter, so what was
    written inside it was guarded by nobody (two of P37's own mutations escaped on that).
    """
    detail = "%d wire(s) in the diagram%s" % (
        wires, ", %d chip(s): %d compiled, %d reused"
        % (len(staged), compiled, len(staged) - compiled) if staged else "")
    if not serial:  # P190: no pins named TX and RX, or an older converter of the project's own
        detail += ("\n           no serial monitor is wired in the diagram (a board part with no pins named TX and RX, or "
                   "a project's own converter older than P190), so a scenario's wait-serial may hear nothing")
    if limits:
        detail += "\n           what it cannot show (%d):" % len(limits)
        for component, sentence in limits:
            detail += "\n             %s: %s" % (component, sentence)
    return detail


def verdict(stages):
    """The chain's exit code, by the same rule a single check answers by (P42)."""
    return EXIT_FOR[status_of(
        problems=[s for s in stages if s.status == PROBLEMS],
        unchecked=[s for s in stages if s.status == COULD_NOT_RUN])]


def vouches_for_a_build(stages):
    """Whether the store may note that the board was built: the chain ran end to end, and no stage was skipped (P236)."""
    return verdict(stages) == EXIT_OK and not any(stage.status == SKIPPED for stage in stages)


def left_off(requirements):
    """
    The needs the requirements file says it leaves off the board (C-2: the note `parts.py --requirements` writes, `unserved`),
    each as `soil (no pick)` or `battery (no record: lipo)` — so "the chain runs end to end" never stands alone over a goal the
    board does not serve. A note in no shape spark writes says nothing, as a file with no note does.
    """
    note = requirements.get("unserved") if isinstance(requirements, dict) else None
    return ["%s (%s%s)" % (item["need"], item.get("why"), ": " + ", ".join(map(str, item["picks"])) if item.get("picks") else "")
            for item in (note if isinstance(note, list) else []) if isinstance(item, dict) and isinstance(item.get("need"), str)]


def render(stages, code, unserved=()):
    mark = {OK: "ok  ", PROBLEMS: "!!  ", COULD_NOT_RUN: "????", SKIPPED: "--  "}
    lines = ["", "  idea -> parts -> pin map -> schematic -> footprint -> build -> simulation", ""]
    for stage in stages:
        lines.append("  [%s] %-16s %s" % (mark[stage.status], stage.name, stage.detail))
    lines.append("")
    lines.append({
        EXIT_OK: "  the chain runs end to end" + (" for the board alone: nothing to wire, so no board was built"
                                                  if any(stage.status == SKIPPED for stage in stages) else ""),
        EXIT_PROBLEMS: "  the chain is broken",
        EXIT_COULD_NOT_RUN: "  the chain was NOT exercised — this is not a pass",
    }[code] + (" — but not every need is on the board: %s" % ", ".join(unserved) if unserved and code == EXIT_OK else ""))
    return "\n".join(lines) + "\n"


def design_handed_to(workdir, project):
    """
    The design the chain is about to be handed (§5.7): the work folder's copy of the requirements, with the board and the
    part records they name, loaded once, now. `built` names this — what the chain ran on — and not what the person's files
    say by the time the build has finished, minutes later. None when it cannot be loaded: `run` says why, as a stage, and a
    chain that did not run end to end records nothing.
    """
    try:
        return design.load(workdir / "requirements.json", project)
    except Exception:  # noqa: BLE001 — whatever is wrong with the input, `run` names it; only the record of the build goes without
        return None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("requirements", nargs="?",
                        help="a requirements.json; omit for the reference design. \"board_only\": true with no parts builds the board alone")
    parser.add_argument("--json", action="store_true",
                        help="the verdict as one JSON object: check, status, stages, and kept with --keep or --sim-dir")
    parser.add_argument("--keep", metavar="DIR", type=Path,
                        help="write the built board into DIR: board.tsx, its footprint and "
                             "dist/, where every check already looks. Existing .tsx files are "
                             "left alone and named; with --json, each file is listed under kept. With a requirements "
                             "file it also writes breadboard.md, the parts and how to wire them on a breadboard, "
                             "breadboard.json, the same wiring drawn on a Wokwi breadboard (the XIAO ESP32-C6 today; a part "
                             "you moved in it, a resistor or a jumper too, stays where you put it, or the build names it as "
                             "`move not kept`; an end the drawing joins differently from the points is a `drawing differs` entry), "
                             "breadboard.svg, that drawing as a picture, "
                             "a rebuild also lists what to change on the bench (one `changed` entry for each line), page.html, the breadboard, schematic and PCB "
                             "in three tabs to open in a browser or to publish as an Artifact, and "
                             "firmware/pins.py, the pins the firmware imports, with one `missing_facts` item for each fact the board record lacks. The simulation project goes to DIR/sim")
    parser.add_argument("--sim-dir", type=Path, metavar="DIR",
                        help="keep the simulation project here instead of DIR/sim: diagram.json, wokwi.toml, the chips")
    parser.add_argument("--firmware", metavar="IMAGE",
                        help="the flash image wokwi.toml names, relative to the sim dir (flash_image.py writes one); "
                             "without it, the image a kept wokwi.toml names is kept")
    args = parser.parse_args(argv)

    # The input is read before anything runs, and read AS input: a malformed file is a stage that could not run, not a
    # traceback with exit 1 (which says "the chain is broken"). The project is the file's, up from its own directory, so a
    # design belongs to its parts wherever it is typed; a file in no project is built from the plugin's library.
    source = Path(args.requirements).resolve() if args.requirements else None
    try:
        requirements = design.read(source) if source else dict(REFERENCE)
    except design.DesignError as broken:
        return report([Stage(REQUIREMENTS_STAGE, COULD_NOT_RUN, str(broken))], args)
    # A file in no project is built from the plugin's library, and the board stage says so.
    project = design.project_for(source) if source else None
    from_library = bool(source) and design.is_library(project)

    workdir = Path(tempfile.mkdtemp(prefix="spark-spine-"))
    (workdir / "requirements.json").write_text(json.dumps(requirements))
    # tsci needs its toolchain reachable from the build directory.
    toolchain = find_toolchain(source.parent if source else Path.cwd())
    modules = modules_for(toolchain) if toolchain is not None else None
    if modules is not None and not (workdir / "node_modules").exists():
        os.symlink(modules, workdir / "node_modules")

    # What `built` will name is loaded now, once, before anything can change under it.
    handed = design_handed_to(workdir, project) if source and not from_library else None

    # A rebuild runs the flash image the kept wokwi.toml already names, unless --firmware names another.
    simulation = simulation_dir(args)
    if simulation and (simulation / "diagram.json").is_file():  # P482: run() merges into a copy, never the person's file
        shutil.copy(simulation / "diagram.json", workdir / sim_project.KEPT_DIAGRAM)
    firmware, kept = args.firmware, None
    if not firmware and simulation:
        kept = sim_project.firmware_in(simulation / "wokwi.toml")
        firmware = kept.name
    try:
        stages = run(requirements, workdir, toolchain, project, from_library, firmware=firmware)
    except subprocess.TimeoutExpired:
        stages = [Stage("build", COULD_NOT_RUN,
                        "the build did not finish in %ds" % BUILD_TIMEOUT_S)]
    except Exception as exc:  # noqa: BLE001
        # Anything unforeseen is could-not-run, never problems. An exception says this tool
        # failed, which is not the same as the chain failing, and reporting one as the other
        # sends somebody to debug a design that was never examined.
        stages = [Stage("check_spine", COULD_NOT_RUN,
                        "%s: %s" % (type(exc).__name__, exc))]

    # P429: a line this could not read goes with the file the build writes again, so that is said, but only when it did.
    if kept is not None and kept.state == NOT_CHECKED and (workdir / "sim" / "wokwi.toml").is_file():
        print(guard_lines("  sim/wokwi.toml %s The rebuild wrote it again with no image named, and a scenario run then names "
                          "the default one." % kept.why), file=sys.stderr)

    # The history says a build ran end to end (§5.7) — written here, by the chain itself, never on anyone's say-so.
    # A history that cannot be kept is said, and the verdict stands: the chain ran, whatever the store thinks of it.
    if handed is not None and vouches_for_a_build(stages):
        try:
            parts.note_built(handed)
        except (store.StoreProblem, OSError) as unrecorded:
            print(guard_lines("  the build was not recorded in your history: %s" % unrecorded), file=sys.stderr)

    return report(stages, args, workdir, requirements, tabbed_page.TscircuitExport(toolchain))


def kept_into(workdir, destination):
    """
    Put the built board where a person — and every check — will look for it.

    The chain builds in a temp directory and deletes it, which is right for a check and wrong for
    the one command a stranger is told to run: after `/spark:build` their project held only
    `requirements.json`, so `check_all --project .` answered "not asked for" and the word
    **checked** was unreachable from the documented path. `--keep` used to print the temp path
    instead, which is not a place anyone looks, and was documented nowhere (backlog P51).

    `dist/` is pure build output and is replaced. A `.tsx` file is NOT: `board.tsx` is the thing a
    person edits — the smart bin's is hand-maintained — so an existing one is left alone and
    named. Delete it to have it regenerated. One behaviour, no flag to get it wrong with.

    Each file is {file, did, why, line}: `did` is `wrote` or `left alone`, and `line` what stderr says. With --json the
    report carries the rest under `kept` (P124, #58), so an agent reads what a person reads.
    """
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    kept = []
    for source in sorted(workdir.glob("*.tsx")):
        target = destination / source.name
        if target.exists():
            kept.append({"file": str(target), "did": "left alone", "why": "delete it to have it regenerated",
                         "line": "left alone: %s (delete it to have it regenerated)" % target})
        else:
            shutil.copy2(source, target)
            kept.append({"file": str(target), "did": "wrote", "why": None, "line": "wrote %s" % target})
    built = workdir / "dist"
    if built.is_dir():
        shutil.copytree(built, destination / "dist", dirs_exist_ok=True)
        kept.append({"file": str(destination / "dist"), "did": "wrote", "why": "this is what every check reads",
                     "line": "wrote %s — this is what every check reads" % (destination / "dist")})
    return kept


def _kept(workdir, destination):
    """`kept_into`, or one entry saying why nothing could be kept: the verdict is printed either way."""
    try:
        return kept_into(workdir, destination)
    except OSError as refused:
        return [{"file": str(destination), "did": "not kept", "why": str(refused),
                 "line": "not kept: %s — %s" % (destination, refused)}]


def drop_an_older_build(destination, stages):
    """
    For the board alone (P236): an earlier build's `dist/` describes another board, and every check reads it, so it
    is removed and said, as the breadboard sheet is. Returns the kept entries, none when there is nothing to remove.
    """
    old = Path(destination) / "dist"
    if not any(stage.status == SKIPPED for stage in stages) or not old.is_dir():
        return []
    shutil.rmtree(old)
    why = "board only: no board was built, and it described an earlier build"
    return [{"file": str(old), "did": "removed", "why": why, "line": "removed %s: %s" % (old, why)}]


def keep_breadboard(requirements, destination, stages=()):
    """
    The breadboard sheet beside the kept board (P191, #143), and its drawn breadboard (P267), as kept entries {file,
    did, why, line}. Only from a build that finished in this run, which it records (dist/board/built-from.json) for
    breadboard.py to compare; a sheet or a drawing left from an earlier build is removed, since it describes another
    board.
    """
    sheet = Path(destination) / breadboard.SHEET
    drawings = [(Path(destination) / renderer.FILE_NAME, renderer) for renderer in breadboard.DRAWING_RENDERERS]
    why = why_not_built(stages, "board only: nothing to wire")
    if why:
        return [_left_from_earlier(sheet, "breadboard sheet", why)] + [
            _left_from_earlier_drawing(path, renderer, why) for path, renderer in drawings]
    try:
        breadboard.record_built_from(requirements, Path(destination) / breadboard.BUILT_FROM)
        written = breadboard.write(requirements, sheet, Path(destination) / breadboard.CIRCUIT)
    except (breadboard.NotBuilt, design.DesignError, store.StoreProblem, OSError, ValueError) as stopped:
        return [{"file": str(sheet), "did": "not written", "why": str(stopped),
                 "line": "no breadboard sheet: %s" % stopped}] + [
            _left_from_earlier_drawing(path, renderer, "the sheet was not written") for path, renderer in drawings]
    why = "the parts and how to wire them on a breadboard"
    kept = [{"file": str(written.sheet), "did": "wrote", "why": why, "line": "wrote %s — %s" % (written.sheet, why)}]
    kept += [{"file": str(path), "did": "wrote", "why": renderer.PURPOSE_MESSAGE, "line": "wrote %s — %s" % (path, renderer.PURPOSE_MESSAGE),
              **({"drawn_from": written.drawn_from} if written.drawn_from else {})} for path, renderer in written.drawings]
    kept += [{"file": str(one.path), "did": "not written", "code": one.code, "subject": one.subject,
              "expected": one.code in breadboard_drawing.BY_DESIGN, "why": one.why,
              "line": "no %s: %s" % (one.renderer.NOUN, one.why)} for one in written.not_written]
    # what the person changes on the bench since the last sheet (P300)
    kept += [{"file": str(written.sheet), "did": CHANGED, "code": change.code, "subject": change.name,
              "color": change.color, "why": breadboard.CHANGE_LIST.line(change),
              "line": "%s: %s" % (CHANGED, breadboard.CHANGE_LIST.line(change))} for change in written.changes]
    # a part the person moved in breadboard.json that the build could not keep (P273)
    kept += [{"file": str(Path(destination) / breadboard.EDITABLE_DRAWING.FILE_NAME), "did": MOVE_NOT_KEPT,
              "subject": named.subject, "code": named.code, "why": named.why,
              "line": "move not kept: %s" % named.line} for named in written.not_kept]
    # an end the drawing joins differently from the points (P279): the sheet's steps stand, the drawing is wrong
    kept += [{"file": str(Path(destination) / breadboard.EDITABLE_DRAWING.FILE_NAME), "did": DRAWING_DIFFERS,
              "subject": differs.subject, "code": differs.code, "why": differs.why,
              "line": "%s: %s" % (DRAWING_DIFFERS, differs.why)} for differs in written.differs]
    return kept


def why_not_built(stages, board_only_why):
    """Why no build finished in this run, or None when one did: the refused requirements file's own reason (P280),
    `board_only_why` for a board-only design, else that the build did not finish."""
    if any(stage.name == "build" and stage.status == OK for stage in stages):
        return None
    refused = next((stage.detail for stage in stages if stage.name == REQUIREMENTS_STAGE and stage.status != OK), None)
    if refused:
        return refused
    if any(stage.status == SKIPPED for stage in stages):
        return board_only_why
    return "the build did not finish in this run"


def why_no_page(destination, stages, kept):
    """Why the page (P271) cannot be drawn in this run, or None: its three tabs read the one circuit.json kept in this
    run, so a refused requirements file, a build that did not finish, a board-only one, or a dist/ that was not copied
    leaves no page."""
    why = why_not_built(stages, "board only: nothing to draw")
    if why:
        return why
    if not any(entry["file"] == str(Path(destination) / "dist") and entry["did"] == "wrote" for entry in kept):
        return "the build was not kept in this run"
    return None


def keep_tabbed_page(destination, stages, kept, exporter):
    """
    The page beside the kept board (P271, #307): the breadboard picture the sheet's step just wrote, and tscircuit's
    schematic and PCB of the same kept circuit.json, as one kept entry {file, did, why, line}. A page left from an
    earlier build is removed when this run cannot draw one, since it describes another board.
    """
    page = Path(destination) / tabbed_page.TabbedHtmlPage.FILE_NAME
    why = why_no_page(destination, stages, kept)
    if why:
        return _left_from_earlier(page, tabbed_page.TabbedHtmlPage.NOUN, why)
    circuit = Path(destination) / breadboard.CIRCUIT
    tabs = [_breadboard_tab(destination, kept),
            tabbed_page.exported_tab("Schematic", exporter.export_svg(circuit, "schematic-svg")),
            tabbed_page.exported_tab("PCB", exporter.export_svg(circuit, "pcb-svg"))]
    try:
        title = tabbed_page.page_title(Path(destination).resolve().name)
        page.write_text(tabbed_page.TabbedHtmlPage().text(tabs, title=title), encoding="utf-8")
    except OSError as refused:
        return {"file": str(page), "did": "not written", "why": str(refused), "line": "no page: %s" % refused}
    why = tabbed_page.TabbedHtmlPage.PURPOSE_MESSAGE
    return {"file": str(page), "did": "wrote", "why": why, "line": "wrote %s — %s" % (page, why)}


def _breadboard_tab(destination, kept):
    """The breadboard tab: the picture this run wrote, or why it did not."""
    picture = str(Path(destination) / breadboard_drawing.SvgBreadboardDiagram.FILE_NAME)
    entry = next((entry for entry in kept if entry["file"] == picture), None)
    if entry is not None and entry["did"] == "wrote":
        try:
            return tabbed_page.Tab("Breadboard", Path(picture).read_text(encoding="utf-8"), None)
        except (OSError, ValueError) as unread:
            return tabbed_page.Tab("Breadboard", None, "breadboard.svg cannot be read: %s" % unread)
    return tabbed_page.Tab("Breadboard", None, entry["why"] if entry else "the breadboard picture was not written")


def _left_from_earlier_drawing(path, renderer, why):
    """`_left_from_earlier` for a drawing, except the one a person edits: breadboard.json is left in place when it holds
    parts, since it may hold their moves, which the next build that finishes keeps where they still fit (P273)."""
    if renderer is breadboard.EDITABLE_DRAWING and path.exists() and breadboard.holds_parts(path):
        return {"file": str(path), "did": "left alone", "why": "no %s: %s; it may hold your moves, which the next build "
                "keeps where they fit" % (renderer.NOUN, why),
                "line": "left alone: %s (it may hold your moves; no %s: %s)" % (path, renderer.NOUN, why)}
    return _left_from_earlier(path, renderer.NOUN, why)


def _left_from_earlier(path, what, why):
    """One kept entry for a file this run did not write: removed when an earlier build left it, else not written."""
    if path.exists():
        path.unlink()
        return {"file": str(path), "did": "removed", "why": why + ", and it described an earlier build",
                "line": "no %s: %s; removed %s, which described an earlier build" % (what, why, path)}
    return {"file": str(path), "did": "not written", "why": why, "line": "no %s: %s" % (what, why)}


def keep_pins(requirements, destination):
    """
    The pin map the firmware imports, beside the kept board (P196, #155), as one kept entry {file, did, why, line}: what
    `assign_pins.py requirements.json --emit-pins` writes, from the same code, and from the requirements alone, so it
    needs no finished build. One spark wrote is rewritten, since it says not to edit it, and is removed when the pins
    cannot be placed: it describes another design. A `pins.py` spark did not write is left alone, as `board.tsx` is.
    """
    target = Path(destination) / PIN_MODULE
    ours = target.is_file() and target.read_bytes().startswith(assign_pins.PIN_MODULE_HEADER.encode())
    if target.exists() and not ours:
        why = "spark did not write it; delete it to have it written"
        return {"file": str(target), "did": "left alone", "why": why, "line": "left alone: %s (%s)" % (target, why)}
    try:
        module = assign_pins.pin_module_for(str(requirements))
    except (assign_pins.Impossible, design.DesignError, store.StoreProblem, OSError, ValueError) as stopped:
        if ours:
            target.unlink()
            return {"file": str(target), "did": "removed", "why": "%s, and it described an earlier design" % stopped,
                    "line": "no pin map: %s; removed %s, which described an earlier design" % (stopped, target)}
        return {"file": str(target), "did": "not written", "why": str(stopped), "line": "no pin map: %s" % stopped}
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(module.module)
    why, missing = "the pins the firmware imports", [envelope_item(each) for each in module.missing_facts]
    return dict({"file": str(target), "did": "wrote", "why": why, "line": "wrote %s — %s%s" % (target, why, "".join(
        "\n  missing fact: %s. %s" % (item["sentence"], item["fix"]) for item in missing))}, **{"missing_facts": missing} if missing else {})


def _kept_pins(requirements, destination):
    """`keep_pins`, or one entry saying why the file system refused it: the verdict is printed either way."""
    try:
        return keep_pins(requirements, destination)
    except OSError as refused:
        target = Path(destination) / PIN_MODULE
        return {"file": str(target), "did": "not written", "why": str(refused), "line": "no pin map: %s" % refused}


def simulation_dir(args):
    """Where the simulation project is kept: --sim-dir, else DIR/sim under --keep DIR (JB1, P116), else nowhere."""
    if getattr(args, "sim_dir", None):
        return Path(args.sim_dir)
    return Path(args.keep) / "sim" if getattr(args, "keep", None) else None


def keep_simulation(workdir, destination, stages):
    """
    The simulation project the last stage wrote, copied to `destination` as one kept entry {file, did, why, line}, or None
    when the stage wrote none. It is merged into what is there, so a person's scenarios stay. When the simulation stage is OK
    (it ran to the end, so `write_limits` has had its say), a limits note from an earlier build goes if this build wrote none.
    Any other outcome leaves the project's note, since the older diagram stays too.
    """
    if not (workdir / "sim").is_dir():
        return None
    try:
        simulated = any(stage.name == "simulation" and stage.status == OK for stage in stages)
        if simulated and not (workdir / "sim" / sim_project.LIMITS_NOTE).is_file():  # the copy merges, so an older note would stay for the next run
            (Path(destination) / sim_project.LIMITS_NOTE).unlink(missing_ok=True)
        shutil.copytree(workdir / "sim", destination, dirs_exist_ok=True)
    except OSError as refused:  # shutil.Error is one
        return {"file": str(destination), "did": "not kept", "why": str(refused),
                "line": "not kept: %s — %s" % (destination, refused)}
    why = "the simulation project: diagram.json, wokwi.toml and the chips"
    return {"file": str(destination), "did": "wrote", "why": why, "line": "wrote %s — %s" % (destination, why)}


def report(stages, args, workdir=None, requirements=None, exporter=None):
    """
    The verdict, rendered the way it was asked for — with the needs the requirements file leaves off the board, when it says
    any (`left_off`; with --json its own note, under `unserved`), and the facts the board record lacks (`missing_facts`, P464) — and the working directory kept or removed. What
    --keep wrote and left alone is said on stderr and, with --json, carried under `kept` (P124). With no workdir, a
    requirements file that is there but refused still removes what an earlier build left (P280); a missing one, which
    may be a typo, removes nothing.
    """
    code = verdict(stages)
    requirements_file = getattr(args, "requirements", None)
    keeps = args.keep and (workdir is not None or bool(requirements_file) and Path(requirements_file).is_file())
    kept = (_kept(workdir, args.keep) if workdir is not None else []) if keeps else None
    if kept is not None and requirements_file:
        kept += keep_breadboard(Path(args.requirements), Path(args.keep), stages)
        kept += drop_an_older_build(Path(args.keep), stages)
        kept.append(_kept_pins(Path(args.requirements), Path(args.keep)))
        kept.append(keep_tabbed_page(Path(args.keep), stages, kept, exporter or tabbed_page.TscircuitExport(None)))
    simulation = keep_simulation(workdir, simulation_dir(args), stages) if workdir is not None and simulation_dir(args) else None
    if simulation is not None:
        kept = (kept or []) + [simulation]
    if args.json:
        said = {"check": "spine", "status": STATUS_FOR[code], "stages": [{"name": s.name, "status": s.status, "detail": s.detail} for s in stages],
                **({"unserved": requirements["unserved"]} if left_off(requirements) else {}),
                **({"missing_facts": held} if (held := [item for entry in kept or [] for item in entry.get("missing_facts", [])]) else {})}
        if kept is not None:
            said["kept"] = [{key: value for key, value in entry.items() if key != "line"} for entry in kept]
        print(json.dumps(said))
    else:
        sys.stdout.write(guard_lines(render(stages, code, left_off(requirements))))
    for entry in kept or []:
        print(guard_lines("  %s" % entry["line"]), file=sys.stderr)
    if workdir is not None:
        shutil.rmtree(workdir, ignore_errors=True)
    return code


if __name__ == "__main__":
    sys.exit(main())
