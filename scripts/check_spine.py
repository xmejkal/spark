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

import boards  # noqa: E402
import design  # noqa: E402
import emit_board  # noqa: E402
import init_project  # noqa: E402
import netlist  # noqa: E402
import parts  # noqa: E402
import sim_project  # noqa: E402
import store  # noqa: E402
import tools  # noqa: E402
import emit_footprint  # noqa: E402

from outcomes import EXIT_OK, EXIT_PROBLEMS, EXIT_COULD_NOT_RUN  # noqa: E402

from outcomes import OK, PROBLEMS, COULD_NOT_RUN, EXIT_FOR, STATUS_FOR, status_of  # noqa: E402

#: The design the chain is proven against when nobody names one. A motor driver, a sensor on a
#: bus, and the power inlet that supplies the rail the modules only consume — the smallest set
#: that exercises pin assignment, a bus, a rail with an external source, and two footprint kinds.
REFERENCE = {"board": "firebeetle2-esp32s3",
             "parts": ["l9110s-module", "vl6180x-breakout", "jst-ph-2-power-inlet"]}

BUILD_TIMEOUT_S = 300


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
        return said[-1].strip() if said else "unknown version"
    except (OSError, subprocess.TimeoutExpired):
        return "unknown version"


#: Where the circuit.json -> Wokwi diagram.json converter might be. It is not part of this
#: plugin yet: it lives in the project that proved it, and moving ~1800 lines of TypeScript into
#: a Python plugin is a structural decision nobody has made. Until then this stage is honest
#: about not having run rather than absent, because "the spine reaches simulation" is the whole
#: product goal and a chain that quietly stops at `build` misrepresents it.
#: A project may carry its own converter; otherwise the plugin's is used. The second entry used to
#: be `../smartbin-local/tools/circuit-to-wokwi/cli.ts` — one person's checkout, beside which the
#: chain's last stage was the only place it worked. The same requirements file reached
#: `[ok] simulation` in a bare directory and `[????] no converter found` after running the
#: documented `/spark:init`, because the search then walked up from the plugin and found that
#: repository. v1's last word was true on one machine (backlog P32a).
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


def wires_in(diagram):
    """How many connections the emitted diagram makes."""
    return len(diagram.get("connections") or [])


def count_in(circuit):
    """Traces and errors, which is what 'did it build' actually means."""
    traces = sum(1 for element in circuit if element.get("type") == "pcb_trace")
    errors = [element for element in circuit if "error" in (element.get("type") or "")]
    return traces, errors


#: Nets that are a ground: the generator's list, so this rule and its supply rule agree.
GROUND_NETS = emit_board.GROUND_NETS
#: tscircuit's types for the two-terminal parts a generated board places between a pin and a rail.
PASSIVE_FTYPES = ("simple_resistor", "simple_capacitor", "simple_inductor", "simple_diode")


def islands_in(circuit, claims=()):
    """
    Every component the board leaves on an island, said in its own words.

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
                if element.get("ftype") in PASSIVE_FTYPES}
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
    if version in ("unknown version", init_project.PINNED_CORE):
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

    # Nothing to build is not a pass. An empty parts list came out `ok` end to end — two traces
    # (the processor's own ground and 3.3 V) and two wires — which proves nothing about the chain
    # and reads as though it did. Intake row M3 had it as `problems` on 09-25; both were wrong.
    if not requirements.get("parts"):
        return stages + [Stage("parts", COULD_NOT_RUN,
                               "the requirements name no parts, so there is nothing to build; a "
                               "board holding only the microcontroller proves nothing")]

    # The design's own part records, so the build stage below can ask whether the circuit
    # honoured what they state. `emit_board` reads the same records in its subprocess; if that
    # succeeded, this cannot fail for a reason the reader has not already been told.
    try:
        part_list = design.parts_of(requirements, project)
    except design.DesignError as broken:
        return stages + [Stage("parts", COULD_NOT_RUN, str(broken))]

    board_file = workdir / "board.tsx"
    emitted = subprocess.run(
        [sys.executable, str(SCRIPTS / "emit_board.py"), str(workdir / "requirements.json"),
         "--project", str(project), "--assume-missing-sizes"],
        capture_output=True, text=True)
    if emitted.returncode != 0:
        # emit_board distinguishes the two, and so must this. "It refused because a part has no
        # measured outline" and "it produced a broken design" send a person to different places.
        refused = emitted.returncode == emit_board.EXIT_COULD_NOT_RUN
        return stages + [Stage("schematic", COULD_NOT_RUN if refused else PROBLEMS,
                               emitted.stderr.strip())]
    board_file.write_text(emitted.stdout)
    traces_asked = emitted.stdout.count("<trace ")
    stages.append(Stage("schematic", OK, "%d trace(s) written" % traces_asked))
    if emitted.stderr.strip():
        stages.append(Stage("schematic-notes", PROBLEMS, emitted.stderr.strip()))

    # --- the footprint the schematic imports ---
    export = (board.get("physical") or {}).get("footprint_export")
    footprint = emit_footprint.main(
        ["--board", board["id"], "--project", str(project),
         "-o", str(workdir / ("%s.tsx" % export))])
    if footprint != emit_footprint.EXIT_OK:
        return stages + [Stage("footprint", COULD_NOT_RUN,
                               "no footprint could be generated for %s" % board["id"])]
    stages.append(Stage("footprint", OK, "%s.tsx" % export))

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
                         emit_board.supply_inputs(board, part_list))
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
    (sim_dir / "wokwi-mapping.json").write_text(json.dumps(mapping, indent=2) + "\n")
    (sim_dir / "board.json").write_text(json.dumps(board, indent=2) + "\n")
    staged, chip_problems = sim_project.stage_chips(chips, sim_dir)
    if chip_problems:
        return stages + [Stage("simulation", COULD_NOT_RUN, "\n".join(chip_problems))]
    (sim_dir / "wokwi.toml").write_text(sim_project.wokwi_toml(staged, firmware))

    diagram_path = sim_dir / "diagram.json"
    made = subprocess.run(
        converter_command(project, own) + [
            "--circuit", str(circuit_path), "--out", str(diagram_path),
            "--mapping", str(sim_dir / "wokwi-mapping.json"), "--chips", str(sim_dir / "chips")],
        cwd=str(own.parent if own else sim_dir), capture_output=True, text=True, timeout=BUILD_TIMEOUT_S,
        env=dict(os.environ, SPARK_BOARD_JSON=str(sim_dir / "board.json")))
    if not diagram_path.is_file():
        said = (made.stderr or made.stdout)[-800:]
        if simulation_could_not_look(said):
            return stages + [Stage("simulation", COULD_NOT_RUN,
                                   "the converter has no Wokwi part for a component on this board "
                                   "— a mapping to add to its lib/mapping.ts, not a defect in the "
                                   "design, which built\n" + said)]
        return stages + [Stage("simulation", PROBLEMS, "no diagram was produced\n" + said)]

    wires = wires_in(json.loads(diagram_path.read_text()))
    if wires == 0:
        # The same failure shape as a board with no copper: every part placed, nothing joined.
        return stages + [Stage("simulation", PROBLEMS,
                               "a diagram with 0 connections. Every part is placed and none is "
                               "wired, which is what an unmapped component looks like once the "
                               "converter has given up on it")]
    compiled = sum(1 for how in staged.values() if how == "compiled")
    # What the simulation cannot show, in the records' own words. Every stand-in record is
    # required to carry this sentence and no command printed one, so a green scenario read exactly
    # like a bench result (backlog P37). It goes beside the diagram as well, because the terminal
    # gets closed and the sim directory is what somebody opens a week later.
    limits = sim_project.write_limits(sim_dir, loaded)
    return stages + [Stage("simulation", OK, simulation_detail(wires, staged, compiled, limits))]


def simulation_detail(wires, staged, compiled, limits):
    """
    What the simulation stage says, including what it cannot show.

    Separated from `run` so it can be tested at all: no test on this machine reaches run's
    simulation stage, which needs a toolchain and a converter, so everything written inside it was
    guarded by nobody — the verification lens's finding, and two of P37's own mutations escaped on
    exactly that.
    """
    detail = "%d wire(s) in the diagram%s" % (
        wires, ", %d chip(s): %d compiled, %d reused"
        % (len(staged), compiled, len(staged) - compiled) if staged else "")
    if limits:
        detail += "\n           what it cannot show, from the records (%d):" % len(limits)
        for component, sentence in limits:
            detail += "\n             %s: %s" % (component, sentence)
    return detail


def verdict(stages):
    """The chain's exit code, by the same rule a single check answers by (P42)."""
    return EXIT_FOR[status_of(
        problems=[s for s in stages if s.status == PROBLEMS],
        unchecked=[s for s in stages if s.status == COULD_NOT_RUN])]


def render(stages, code):
    mark = {OK: "ok  ", PROBLEMS: "!!  ", COULD_NOT_RUN: "????"}
    lines = ["", "  idea -> parts -> pin map -> schematic -> footprint -> build -> simulation", ""]
    for stage in stages:
        lines.append("  [%s] %-16s %s" % (mark[stage.status], stage.name, stage.detail))
    lines.append("")
    lines.append({
        EXIT_OK: "  the chain runs end to end",
        EXIT_PROBLEMS: "  the chain is broken",
        EXIT_COULD_NOT_RUN: "  the chain was NOT exercised — this is not a pass",
    }[code])
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
                        help="a requirements.json; omit for the reference design")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--keep", metavar="DIR", type=Path,
                        help="write the built board into DIR: board.tsx, its footprint and "
                             "dist/, where every check already looks. Existing .tsx files are "
                             "left alone and named")
    parser.add_argument("--sim-dir", type=Path, metavar="DIR",
                        help="keep the simulation project here: diagram.json, wokwi.toml, the chips")
    parser.add_argument("--firmware", metavar="IMAGE",
                        help="the flash image wokwi.toml names, relative to the sim dir (flash_image.py writes one)")
    args = parser.parse_args(argv)

    # The input is read before anything runs, and read AS input: a malformed file is a stage
    # that could not run, not a traceback with exit 1 — which is "the chain is broken" to anyone
    # reading the code. The project is the file's, up from its own directory, so a design
    # belongs to its parts wherever the command is typed; a file inside no project at all is
    # built from the plugin's library, like the reference design.
    source = Path(args.requirements).resolve() if args.requirements else None
    try:
        requirements = design.read(source) if source else dict(REFERENCE)
    except design.DesignError as broken:
        return report([Stage("requirements", COULD_NOT_RUN, str(broken))], args)
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

    try:
        stages = run(requirements, workdir, toolchain, project, from_library, firmware=args.firmware)
    except subprocess.TimeoutExpired:
        stages = [Stage("build", COULD_NOT_RUN,
                        "the build did not finish in %ds" % BUILD_TIMEOUT_S)]
    except Exception as exc:  # noqa: BLE001
        # Anything unforeseen is could-not-run, never problems. An exception says this tool
        # failed, which is not the same as the chain failing, and reporting one as the other
        # sends somebody to debug a design that was never examined.
        stages = [Stage("check_spine", COULD_NOT_RUN,
                        "%s: %s" % (type(exc).__name__, exc))]

    # The history says a build ran end to end (§5.7) — written here, by the chain itself, never on anyone's say-so.
    # A history that cannot be kept is said, and the verdict stands: the chain ran, whatever the store thinks of it.
    if handed is not None and verdict(stages) == EXIT_OK:
        try:
            parts.note_built(handed)
        except (store.StoreProblem, OSError) as unrecorded:
            print("  the build was not recorded in your history: %s" % unrecorded, file=sys.stderr)

    if args.sim_dir and (workdir / "sim").is_dir():
        shutil.copytree(workdir / "sim", args.sim_dir, dirs_exist_ok=True)
        print("simulation project kept in %s" % args.sim_dir, file=sys.stderr)
    return report(stages, args, workdir)


def keep_into(workdir, destination):
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
    """
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    said = []
    for source in sorted(workdir.glob("*.tsx")):
        target = destination / source.name
        if target.exists():
            said.append("left alone: %s (delete it to have it regenerated)" % target)
        else:
            shutil.copy2(source, target)
            said.append("wrote %s" % target)
    built = workdir / "dist"
    if built.is_dir():
        shutil.copytree(built, destination / "dist", dirs_exist_ok=True)
        said.append("wrote %s — this is what every check reads" % (destination / "dist"))
    return said


def report(stages, args, workdir=None):
    """The verdict, rendered the way it was asked for; the working directory kept or removed."""
    code = verdict(stages)
    if args.json:
        print(json.dumps({"check": "spine", "status": STATUS_FOR[code],
                          "stages": [{"name": s.name, "status": s.status, "detail": s.detail}
                                     for s in stages]}))
    else:
        sys.stdout.write(render(stages, code))
    if workdir is None:
        return code
    if args.keep:
        for line in keep_into(workdir, args.keep):
            print("  %s" % line, file=sys.stderr)
    if workdir.exists():
        shutil.rmtree(workdir, ignore_errors=True)
    return code


if __name__ == "__main__":
    sys.exit(main())
