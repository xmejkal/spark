"""
The build as one run of its stages (P705): `run` takes a requirements file through the board, the parts, the schematic,
the footprint and the build to the simulation, and stops at the first stage that cannot feed the next; `board_alone`
does the same for a project with no parts. A function today: `BuildService` comes into this file with its card.
"""

import json
import subprocess
import sys
from pathlib import Path

from spark.records import board_records
from spark.build import board_engine  # find_toolchain is read through it: one patch reaches run and check_spine.main
from spark.build import build_codes
from spark.build import project_setup
from spark.build.board_engine import convert, converter_stage_problem, find_converter, toolchain_can_build, tsci_version
from spark.build.stages import Stage, NO_FOOTPRINT_HINT
from spark.design import board_emitter
from spark.design import footprint_emitter
from spark.design import loader
from spark.design import needs
from spark.design import netlist
from spark.records import onboard_parts
from spark.build import board_alone_input
from spark.firmware import sim_project
from spark.records import tool_finder

from spark.core.outcomes import EXIT_FOR, EXIT_OK, EXIT_COULD_NOT_RUN, COULD_NOT_RUN, OK, PROBLEMS, SKIPPED, status_of
from spark.core.text_guards import clean

#: The CLI that writes board.tsx, run as a child: two folders up from this module (P705).
EMIT_BOARD_SCRIPT = Path(__file__).resolve().parents[2] / "emit_board.py"

#: A real tsci build of a five-part board took 496 s on the P581 bench (the autorouter 231.6 s), so the limit is
#: about 1.8 times that (P659). The probe and the converter are small jobs with their own limit.
BUILD_TIMEOUT_S = 900


def said_of_a_crash(program, crash):
    """
    How a crash in `program` reads as a stage's detail, raw (P430): its last traceback line, as the child's stderr gave it (F5).
    The text is guarded when it is printed (`render`), and `--json` keeps it as it stands.
    """
    return "%s crashed: %s: %s" % (program, type(crash).__name__, str(crash))


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
GROUND_NETS = board_emitter.GROUND_NETS
#: tscircuit's types for the two-terminal parts a generated board places between a pin and a rail.
PASSIVE_FTYPES = ("simple_resistor", "simple_capacitor", "simple_inductor", "simple_diode")


def islands_in(circuit, claims=(), across=()):
    """
    Every component the board leaves on an island, said in its own words. `across` names the
    components that sit across a driven pair (`board_emitter.loads_across_a_pair`: a speaker
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
    * **an unfed supply pin** (`claims`, from `board_emitter.supply_inputs`). This is P29's half. The
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
    names = {cid: element.get("name") or "?" for cid, element in board.components.items()}
    passives = {cid for cid, element in board.components.items()
                if element.get("ftype") in PASSIVE_FTYPES or element.get("name") in across}
    findings, present = _reaches_no_ground(board, names, passives)
    findings += ["%s.%s (a terminal connected to nothing)"
                 % (names.get(port.get("source_component_id"), "?"), port.get("name") or port_id)
                 for port_id, port in board.ports.items()
                 if port.get("source_component_id") in present & passives
                 and port_id not in board.nets_of_port]
    return sorted(findings + _unfed(board, claims))


def _reaches_no_ground(board, names, passives):
    """`islands_in`'s first question: each chip wired to something and to no ground, as a finding, and every
    component wired at all."""
    ground_ids = {net_id for net_id, net in board.nets.items()
                  if (net.get("name") or "").upper() in GROUND_NETS}
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
    return findings, present


def _unfed(board, claims):
    """`islands_in`'s third question: each supply pin the design says a net feeds, which the built board does not put
    on that net (P29)."""
    findings = []
    for component, pin, net in claims:
        wanted = board.net_named(net)
        if wanted is None or wanted not in board.nets_of(component, pin):
            findings.append("%s.%s is fed by net.%s in this design and is not on it"
                            % (component, pin, net))
    return findings


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
    if version in (tool_finder.UNKNOWN_VERSION, project_setup.PINNED_CORE):
        return ""
    return "; the documents were measured on core %s" % project_setup.PINNED_CORE


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
    project = project or board_records.PLUGIN_ROOT

    # --- parts and pin assignment, via the generator that owns them ---
    try:
        board = board_records.load(project, requirements.get("board"))
    except Exception as exc:  # noqa: BLE001
        return stages + [Stage("board", COULD_NOT_RUN, str(exc), build_codes.BOARD_UNUSABLE)]
    stages.append(Stage("board", OK, board["name"] + (
        " — from the plugin's library; no project up from the requirements file, so no rules"
        if from_library else "")))

    # Nothing to build is not a pass. An empty parts list came out `ok` end to end (two traces, two wires), which proves
    # nothing about the chain and reads as though it did. Intake row M3 had it as `problems` on 09-25; both were wrong.
    if requirements.get(needs.BOARD_ONLY) is True:
        if requirements.get("parts"):
            return stages + [Stage("parts", COULD_NOT_RUN, "the requirements say board_only and name parts: say one", build_codes.BOARD_ONLY_WITH_PARTS)]
        return stages + board_alone(board, workdir, firmware, project)
    if not requirements.get("parts"):
        return stages + [Stage("parts", COULD_NOT_RUN,
                               "the requirements name no parts, so there is nothing to build; a "
                               "board holding only the microcontroller proves nothing. A project that runs "
                               'on the board alone says "%s": true' % needs.BOARD_ONLY, build_codes.NO_PARTS)]

    # The design's own part records, so the build stage below can ask whether the circuit honoured what they state.
    # `board_emitter` reads the same records; if that succeeded, this cannot fail for a reason not already told.
    try:
        part_list = loader.parts_of(requirements, project)
    except loader.DesignError as broken:
        return stages + [Stage("parts", COULD_NOT_RUN, str(broken), broken.code)]

    # --- MVP --- the input is read, the pins are placed and the footprint is asked for, in the one order `board_emitter.read_inputs`
    # gives (P407, P432): a fault in the requirements is said before a gap in the board record, and the schematic imports
    # the board's footprint, so a record that cannot give one stops here, before the CLI `emit_board.py` is asked.
    try:
        inputs = board_emitter.read_inputs(workdir / "requirements.json", project)
    except board_emitter.RefusedInputError as refused:
        hint = "\n" + NO_FOOTPRINT_HINT if refused.stage == board_emitter.FOOTPRINT_STAGE else ""
        return stages + [Stage(refused.stage, COULD_NOT_RUN, str(refused) + hint, refused.code)]
    except Exception as crash:  # noqa: BLE001 -- emit_board ran in a child until P432, so a crash was a stage (F5), not a lost run
        return stages + [Stage(board_emitter.SCHEMATIC_STAGE, COULD_NOT_RUN, said_of_a_crash("emit_board.py", crash), build_codes.STAGE_CRASHED)]

    board_file = workdir / "board.tsx"
    emitted = subprocess.run(
        [sys.executable, str(EMIT_BOARD_SCRIPT), str(workdir / "requirements.json"),
         "--project", str(project), "--assume-missing-sizes"],
        capture_output=True, text=True)
    if emitted.returncode == EXIT_COULD_NOT_RUN:
        # It refused the input — a part with no measured outline, a resistor nothing sizes — in its own words.
        return stages + [Stage(board_emitter.SCHEMATIC_STAGE, COULD_NOT_RUN, emitted.stderr.strip(), build_codes.SCHEMATIC_REFUSED)]
    if emitted.returncode != 0:
        # `emit_board.py` exits 0 or 2 on purpose, so anything else is a crash: could-not-run, as `main` says of anything
        # unforeseen, with the traceback's last line. Read as problems, it sent people to debug a design nobody examined (F5).
        said = emitted.stderr.strip().splitlines()
        return stages + [Stage(board_emitter.SCHEMATIC_STAGE, COULD_NOT_RUN, "emit_board.py crashed: %s" % (
            said[-1] if said else "exit %d, and nothing said" % emitted.returncode), build_codes.STAGE_CRASHED)]
    board_file.write_text(emitted.stdout)
    traces_asked = emitted.stdout.count(board_emitter.TRACE_TAG)
    stages.append(Stage(board_emitter.SCHEMATIC_STAGE, OK, "%d trace(s) written" % traces_asked))
    if emitted.stderr.strip():
        stages.append(Stage("schematic-notes", PROBLEMS, emitted.stderr.strip(), build_codes.SCHEMATIC_NOTED))

    # --- the footprint the schematic imports ---
    # --- MVP --- drawn here with the design's rules; `read_inputs` already refused a rules file that cannot be read (P432, OC2).
    footprint_board = inputs.design.board
    export = (footprint_board.get("physical") or {}).get("footprint_export")
    rules = inputs.design.rules
    try:
        disagreement = footprint_emitter.why_header_disagrees(footprint_board, rules)
        if disagreement:
            return stages + [Stage(board_emitter.FOOTPRINT_STAGE, COULD_NOT_RUN, disagreement, disagreement.code)]
        text = footprint_emitter.render(footprint_board, rules)
    except Exception as crash:  # noqa: BLE001 -- the footprint script ran apart from this run until P432, so a crash was a stage
        return stages + [Stage(board_emitter.FOOTPRINT_STAGE, COULD_NOT_RUN, said_of_a_crash("emit_footprint.py", crash), build_codes.STAGE_CRASHED)]
    (workdir / ("%s.tsx" % export)).write_text(text)
    stages.append(Stage(board_emitter.FOOTPRINT_STAGE, OK, "%s.tsx" % export))

    # --- the build, which is the only stage that can prove any of the above ---
    # The project's tools file, not the scratch directory's: a broken or pinned project file must be read.
    toolchain = toolchain or board_engine.find_toolchain(project or workdir)
    if toolchain is None:
        try:
            tool_finder.find("board-engine", project or workdir)
            said = "the board engine was not found"
        except tool_finder.ToolError as missing:
            said = str(missing)  # the tools list's own sentence, with what installs it (P82)
        return stages + [Stage("build", COULD_NOT_RUN,
                               "%s — so the chain was not exercised; /spark:setup installs it" % said, build_codes.TOOL_MISSING)]

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
                                   "its own.\n%s" % (toolchain, version, last_words), build_codes.TOOL_CANNOT_BUILD)]
        return stages + [Stage("build", PROBLEMS,
                               "no circuit.json was produced by %s (%s), which does build a "
                               "trivial board\n%s" % (toolchain, version,
                                                      built.stderr.strip()[-800:]), build_codes.DESIGN_NOT_BUILT)]

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
                         board_emitter.supply_inputs(board, part_list),
                         across=board_emitter.loads_across_a_pair(part_list))
    if islands:
        return stages + [Stage("build", PROBLEMS, "%s. A board builds, routes and reports no error with a component joined "
                               "to nothing — the parts around it are wired to nets it is simply not on" % "; ".join(islands),
                               build_codes.PART_STRANDED)]
    if errors:
        first = [error.get("selectors_not_found") or error.get("message", "") for error in errors[:2]]
        first = clean("; ".join(", ".join(map(str, one)) if isinstance(one, list) else str(one) for one in first), 300)
        return stages + [Stage("build", PROBLEMS, "%d error(s): %s; first: %s" % (  # --- MVP --- (P512) names the trace
            len(errors), ", ".join(sorted({element["type"] for element in errors})), first), build_codes.DESIGN_NOT_BUILT)]
    if traces == 0:
        # The failure this file was written for: everything is placed, nothing is connected, and nothing raised.
        return stages + [Stage("build", PROBLEMS, "built with 0 pcb_traces — every component is placed and no copper joins "
                               "any of them. tscircuit skips routing entirely when one net is unroutable, and that does not "
                               "raise", build_codes.NOT_ROUTED)]
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
    loaded = loader.load(workdir / "requirements.json", None if from_library else project)
    mapping, chips, unmapped = sim_project.mapping_for(loaded)
    if unmapped:
        return stages + [Stage("simulation", COULD_NOT_RUN, sim_project.unmapped_detail(unmapped), build_codes.SIMULATION_FACT_MISSING)]
    sim_dir = workdir / "sim"
    sim_dir.mkdir(exist_ok=True)
    (sim_dir / sim_project.MAPPING_FILE).write_text(json.dumps(mapping, indent=2) + "\n")
    (sim_dir / "board.json").write_text(json.dumps(board, indent=2) + "\n")
    staged, chip_problems = sim_project.stage_chips(chips, sim_dir)
    if chip_problems:
        return stages + [Stage("simulation", COULD_NOT_RUN, "\n".join(chip_problems), build_codes.CHIP_NOT_COMPILED)]
    (sim_dir / "wokwi.toml").write_text(sim_project.wokwi_toml(staged, firmware))

    diagram, stopped, notes = convert(project, own, ["--circuit", str(circuit_path)], sim_dir, workdir)
    if stopped:
        return stages + [stopped]
    wires = wires_in(diagram)
    if wires == 0:
        # The same failure shape as a board with no copper: every part placed, nothing joined.
        return stages + [Stage("simulation", PROBLEMS, "a diagram with 0 connections. Every part is placed and none is wired, "
                               "which is what an unmapped component looks like once the converter has given up on it",
                               build_codes.DIAGRAM_UNWIRED)]
    compiled = sum(1 for how in staged.values() if how == "compiled")
    # What the simulation cannot show, in the records' own words, said and kept beside the diagram (P37).
    limits = sim_project.write_limits(sim_dir, loaded, board)
    return stages + [Stage("simulation", OK, simulation_detail(wires, staged, compiled, limits, serial_heard(diagram, board)) + notes)]


def board_alone(board, workdir, firmware=None, project=None):
    """
    The stages after `board` for a project that runs on the board alone (P236): parts, schematic, footprint and build are
    SKIPPED, never ok. The converter wires the board's own LED and button that `onboard_parts` gives (P484), as `run` does;
    with none, the diagram holds the board's part alone. A limit "not checked" stays a limit in an ok stage (P396, P37).
    """
    skipped = [Stage(name, SKIPPED, "board only: nothing to wire") for name in ("parts", board_emitter.SCHEMATIC_STAGE, board_emitter.FOOTPRINT_STAGE, "build")]
    if not board.get("wokwi_part_type"):
        return skipped + [Stage("simulation", COULD_NOT_RUN, "the board record names no wokwi_part_type", build_codes.SIMULATION_FACT_MISSING)]
    sim_dir, project = workdir / "sim", project or board_records.PLUGIN_ROOT
    given, own = board_alone_input.read_board_alone(board, project), find_converter(project)
    stopped = given.wired and (converter_stage_problem(project, own) or (Stage("simulation", COULD_NOT_RUN, given.why, build_codes.SIMULATION_FACT_MISSING) if given.why else None))
    if stopped:
        return skipped + [stopped]
    sim_dir.mkdir(exist_ok=True)
    (sim_dir / "wokwi.toml").write_text(sim_project.wokwi_toml((), firmware))
    for name, data in dict(given.files, **{"board.json": board}).items():
        (sim_dir / name).write_text(json.dumps(data, indent=2) + "\n")
    diagram, stopped, notes = (convert(project, own, ["--netlist", str(sim_dir / board_alone_input.NETLIST)], sim_dir, workdir) if given.wired
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
