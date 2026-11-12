"""
The build as one run of its stages (P705, P706): `BuildService.build` takes a requirements file (`BuildInputs`) through the
board, the parts, the schematic, the footprint and the build to the simulation, and stops at the first stage that cannot
feed the next; `board_alone` does the same for a project with no parts. The board file is written in process by the
`BoardEmitter` the service is given, and `tsci` runs through its `TscircuitEngine`; a test swaps either whole.
"""

import json
from dataclasses import dataclass

from spark.records import board_records
from spark.build import board_engine
from spark.build import build_codes
from spark.build import project_setup
from spark.build.board_engine import convert, converter_stage_problem, find_converter
from spark.build.stages import Stage, NO_FOOTPRINT_HINT
from spark.design import board_emitter  # read by name, so a test's patch of `board_emitter.read_inputs` reaches the emitter
from spark.design import board_sections
from spark.design import power_rails
from spark.design import footprint_emitter
from spark.design import loader
from spark.design import need_requirements
from spark.design import netlist
from spark.records import onboard_parts
from spark.build import board_alone_input
from spark.firmware import sim_project
from spark.records import tool_finder

from spark.core.outcomes import EXIT_FOR, EXIT_OK, COULD_NOT_RUN, OK, PROBLEMS, SKIPPED, status_of
from spark.core.text_guards import clean


def said_of_a_crash(what, crash):
    """
    How a crash in `what` (a phrase: "the board emitter", "the footprint emitter") reads as a stage's detail, raw (P430, F5):
    its kind and its message. The text is guarded when it is printed (`render`), and `--json` keeps it as it stands.
    """
    return "%s crashed: %s: %s" % (what, type(crash).__name__, str(crash))


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
GROUND_NETS = power_rails.GROUND_NETS
#: tscircuit's types for the two-terminal parts a generated board places between a pin and a rail.
PASSIVE_FTYPES = ("simple_resistor", "simple_capacitor", "simple_inductor", "simple_diode")


def islands_in(circuit, claims=(), across=()):
    """
    Every component the board leaves on an island, said in its own words. `across` names the
    components that sit across a driven pair (`power_rails.loads_across_a_pair`: a speaker
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
    * **an unfed supply pin** (`claims`, from `power_rails.supply_inputs`). This is P29's half. The
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


@dataclass(frozen=True)
class BuildInputs:
    """
    Value: what one build is given. `requirements` as `loader.read` gave them, `workdir` where the build writes, `project`
    where the design's parts and rules live, resolved by the CLI from the requirements FILE, never from the current
    directory (resolved from `cwd`, a run from anywhere but inside the project said `no part called 'sg90-servo'` about a
    part sitting beside the file); None means the plugin's own library, which the reference design is built from.
    `from_library` says so on the board stage, and `firmware` is the flash image wokwi.toml names.
    """

    requirements: dict
    workdir: object
    project: object = None
    from_library: bool = False
    firmware: object = None


class BuildService:
    """
    Service: runs the six stages of a build, in order, over the two collaborators it is given, a board engine
    (`board_engine.TscircuitEngine`) and a board emitter (`board_emitter.BoardEmitter`), and stops at the first stage that
    cannot produce input for the next. Each stage method appends to `stages` and returns its product, or None when the
    build ends there. A test swaps either collaborator for a Fake; the CLI takes `for_toolchain`.
    """

    def __init__(self, engine, emitter):
        self.engine = engine
        self.emitter = emitter

    @classmethod
    def for_toolchain(cls, toolchain):
        """The real engine over `toolchain` (None: found from the project at build time) and the emitter that lays out around
        a guessed size, as the CLI `check_spine.py` builds."""
        return cls(board_engine.TscircuitEngine(toolchain), board_emitter.BoardEmitter(assume_missing_sizes=True))

    def build(self, inputs):
        """Every stage, in order, stopping at the first that cannot produce input for the next: the list of `Stage`s."""
        stages = []
        project = inputs.project or board_records.PLUGIN_ROOT
        board = self._board(inputs, project, stages)
        if board is None:
            return stages
        part_list = self._parts(inputs, project, board, stages)
        if part_list is None:
            return stages
        board_inputs = self._schematic(inputs, project, stages)
        if board_inputs is None or not self._footprint(board_inputs, inputs.workdir, stages):
            return stages
        built = self._build_circuit(inputs, project, board, part_list, stages)
        if built is not None:
            self._simulation(inputs, project, board, built, stages)
        return stages

    def _board(self, inputs, project, stages):
        """The board record, said to come from the library when the design did."""
        try:
            board = board_records.load(project, inputs.requirements.get("board"))
        except Exception as exc:  # noqa: BLE001
            stages.append(Stage("board", COULD_NOT_RUN, str(exc), build_codes.BOARD_UNUSABLE))
            return None
        stages.append(Stage("board", OK, board["name"] + (
            " — from the plugin's library; no project up from the requirements file, so no rules"
            if inputs.from_library else "")))
        return board

    def _parts(self, inputs, project, board, stages):
        """The design's own part records, so the build stage can ask whether the circuit honoured what they state; a
        board-only project ends here through `board_alone`."""
        requirements = inputs.requirements
        # Nothing to build is not a pass. An empty parts list came out `ok` end to end (two traces, two wires), which proves
        # nothing about the chain and reads as though it did. Intake row M3 had it as `problems` on 09-25; both were wrong.
        if requirements.get(need_requirements.BOARD_ONLY) is True:
            if requirements.get("parts"):
                stages.append(Stage("parts", COULD_NOT_RUN, "the requirements say board_only and name parts: say one", build_codes.BOARD_ONLY_WITH_PARTS))
            else:
                stages.extend(board_alone(board, inputs.workdir, inputs.firmware, project))
            return None
        if not requirements.get("parts"):
            stages.append(Stage("parts", COULD_NOT_RUN,
                                "the requirements name no parts, so there is nothing to build; a "
                                "board holding only the microcontroller proves nothing. A project that runs "
                                'on the board alone says "%s": true' % need_requirements.BOARD_ONLY, build_codes.NO_PARTS))
            return None
        # `board_emitter` reads the same records; if that succeeded, this cannot fail for a reason not already told.
        try:
            return loader.parts_of(requirements, project)
        except loader.DesignError as broken:
            stages.append(Stage("parts", COULD_NOT_RUN, str(broken), broken.code))
            return None

    def _schematic(self, inputs, project, stages):
        """board.tsx written by the emitter, in process: the input read (a fault in the requirements is said before a gap in
        the board record, P407, P432), the file emitted, the notes as the `schematic-notes` stage. Its `BoardInputs`, or None."""
        workdir = inputs.workdir
        try:
            board_inputs = self.emitter.read(workdir / "requirements.json", project)
            text, refusal = self.emitter.emit(board_inputs)
            notes = [] if refusal else self.emitter.notes(board_inputs)
        except board_emitter.RefusedInputError as refused:
            hint = "\n" + NO_FOOTPRINT_HINT if refused.stage == board_emitter.FOOTPRINT_STAGE else ""
            stages.append(Stage(refused.stage, COULD_NOT_RUN, str(refused) + hint, refused.code))
            return None
        except Exception as crash:  # noqa: BLE001 -- a crash in the emitter is a stage (F5), not a lost run
            stages.append(Stage(board_emitter.SCHEMATIC_STAGE, COULD_NOT_RUN, said_of_a_crash("the board emitter", crash), build_codes.STAGE_CRASHED))
            return None
        if refusal:
            # It refused the input — a part with no measured outline, a resistor nothing sizes — in its own words.
            stages.append(Stage(board_emitter.SCHEMATIC_STAGE, COULD_NOT_RUN, str(refusal), build_codes.SCHEMATIC_REFUSED))
            return None
        (workdir / "board.tsx").write_text(text)
        stages.append(Stage(board_emitter.SCHEMATIC_STAGE, OK, "%d trace(s) written" % text.count(board_sections.TRACE_TAG)))
        if notes:
            stages.append(Stage("schematic-notes", PROBLEMS, "\n".join(notes), build_codes.SCHEMATIC_NOTED))
        return board_inputs

    def _footprint(self, board_inputs, workdir, stages):
        """The footprint the schematic imports, drawn with the design's rules (`read` already refused a rules file that
        cannot be read, P432, OC2). Whether the build goes on."""
        footprint_board = board_inputs.design.board
        export = (footprint_board.get("physical") or {}).get("footprint_export")
        rules = board_inputs.design.rules
        try:
            disagreement = footprint_emitter.why_header_disagrees(footprint_board, rules)
            if disagreement:
                stages.append(Stage(board_emitter.FOOTPRINT_STAGE, COULD_NOT_RUN, disagreement, disagreement.code))
                return False
            text = footprint_emitter.render(footprint_board, rules)
        except Exception as crash:  # noqa: BLE001 -- a crash in drawing the footprint is a stage (F5), not a lost run
            stages.append(Stage(board_emitter.FOOTPRINT_STAGE, COULD_NOT_RUN, said_of_a_crash("the footprint emitter", crash), build_codes.STAGE_CRASHED))
            return False
        (workdir / ("%s.tsx" % export)).write_text(text)
        stages.append(Stage(board_emitter.FOOTPRINT_STAGE, OK, "%s.tsx" % export))
        return True

    def _build_circuit(self, inputs, project, board, part_list, stages):
        """The build, the only stage that can prove the ones before it: the engine found from the project (its tools file,
        not the scratch directory's: a broken or pinned project file must be read), run, and asked its version; a tool that
        built nothing is probed on a trivial board. The `BuildResult` when the circuit passed, else None."""
        engine = self.engine.found_from(project)
        if engine is None:
            try:
                tool_finder.find("board-engine", project)
                said = "the board engine was not found"
            except tool_finder.ToolError as missing:
                said = str(missing)  # the tools list's own sentence, with what installs it (P82)
            stages.append(Stage("build", COULD_NOT_RUN,
                                "%s — so the chain was not exercised; /spark:setup installs it" % said, build_codes.TOOL_MISSING))
            return None
        built = engine.build(inputs.workdir)
        version = engine.version()
        if not built.circuit_path.is_file():
            # Nothing came out. Before blaming the design, ask the same tool for a resistor on a
            # board: a tool that cannot build that is not reporting on the design at all.
            can, last_words = engine.probe(inputs.workdir)
            if not can:
                stages.append(Stage("build", COULD_NOT_RUN,
                                    "%s (%s) cannot build even a trivial board from here, so this "
                                    "is the toolchain, not the design. Use the project's own tsci "
                                    "(npm i @tscircuit/cli in the project) or one that builds on "
                                    "its own.\n%s" % (engine.toolchain, version, last_words), build_codes.TOOL_CANNOT_BUILD))
                return None
            stages.append(Stage("build", PROBLEMS,
                                "no circuit.json was produced by %s (%s), which does build a "
                                "trivial board\n%s" % (engine.toolchain, version, built.stderr.strip()[-800:]), build_codes.DESIGN_NOT_BUILT))
            return None
        traces = self._circuit_verdict(built.circuit_path, board, part_list, stages)
        if traces is None:
            return None
        stages.append(Stage("build", OK, "%d trace(s), 0 errors, tsci %s%s" % (traces, version, core_note(version))))
        return built

    def _circuit_verdict(self, circuit_path, board, part_list, stages):
        """What the built circuit says of the design: its trace count when it passed, else None after the stage that stops it."""
        circuit = json.loads(circuit_path.read_text())
        traces, errors = count_in(circuit)
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
        islands = islands_in(circuit, power_rails.supply_inputs(board, part_list),
                             across=power_rails.loads_across_a_pair(part_list))
        if islands:
            stages.append(Stage("build", PROBLEMS, "%s. A board builds, routes and reports no error with a component joined "
                                "to nothing — the parts around it are wired to nets it is simply not on" % "; ".join(islands),
                                build_codes.PART_STRANDED))
            return None
        if errors:
            first = [error.get("selectors_not_found") or error.get("message", "") for error in errors[:2]]
            first = clean("; ".join(", ".join(map(str, one)) if isinstance(one, list) else str(one) for one in first), 300)
            stages.append(Stage("build", PROBLEMS, "%d error(s): %s; first: %s" % (  # --- MVP --- (P512) names the trace
                len(errors), ", ".join(sorted({element["type"] for element in errors})), first), build_codes.DESIGN_NOT_BUILT))
            return None
        if traces == 0:
            # The failure this file was written for: everything is placed, nothing is connected, and nothing raised.
            stages.append(Stage("build", PROBLEMS, "built with 0 pcb_traces — every component is placed and no copper joins "
                                "any of them. tscircuit skips routing entirely when one net is unroutable, and that does not "
                                "raise", build_codes.NOT_ROUTED))
            return None
        return traces

    def _simulation(self, inputs, project, board, built, stages):
        """The simulation project, the last step of the product goal: the converter found from the project (not from `cwd`:
        run from /tmp the converter beside the project was "not found"), the stand-ins from the records (P31), the diagram."""
        workdir = inputs.workdir
        own = find_converter(project)
        missing = converter_stage_problem(project, own)
        if missing:
            stages.append(missing)
            return
        # Read again with None for a library design, which lets a project above TMPDIR win (loader.py:192); equal otherwise.
        loaded = loader.load(workdir / "requirements.json", None if inputs.from_library else project)
        mapping, chips, unmapped = sim_project.mapping_for(loaded)
        if unmapped:
            stages.append(Stage("simulation", COULD_NOT_RUN, sim_project.unmapped_detail(unmapped), build_codes.SIMULATION_FACT_MISSING))
            return
        sim_dir = workdir / "sim"
        sim_dir.mkdir(exist_ok=True)
        (sim_dir / sim_project.MAPPING_FILE).write_text(json.dumps(mapping, indent=2) + "\n")
        (sim_dir / "board.json").write_text(json.dumps(board, indent=2) + "\n")
        staged, chip_problems = sim_project.stage_chips(chips, sim_dir)
        if chip_problems:
            stages.append(Stage("simulation", COULD_NOT_RUN, "\n".join(chip_problems), build_codes.CHIP_NOT_COMPILED))
            return
        (sim_dir / "wokwi.toml").write_text(sim_project.wokwi_toml(staged, inputs.firmware))
        diagram, stopped, notes = convert(project, own, ["--circuit", str(built.circuit_path)], sim_dir, workdir)
        if stopped:
            stages.append(stopped)
            return
        wires = wires_in(diagram)
        if wires == 0:
            # The same failure shape as a board with no copper: every part placed, nothing joined.
            stages.append(Stage("simulation", PROBLEMS, "a diagram with 0 connections. Every part is placed and none is wired, "
                                "which is what an unmapped component looks like once the converter has given up on it",
                                build_codes.DIAGRAM_UNWIRED))
            return
        compiled = sum(1 for how in staged.values() if how == "compiled")
        # What the simulation cannot show, in the records' own words, said and kept beside the diagram (P37).
        limits = sim_project.write_limits(sim_dir, loaded, board)
        stages.append(Stage("simulation", OK, simulation_detail(wires, staged, compiled, limits, serial_heard(diagram, board)) + notes))


def board_alone(board, workdir, firmware=None, project=None):
    """
    The stages after `board` for a project that runs on the board alone (P236): parts, schematic, footprint and build are
    SKIPPED, never ok. The converter wires the board's own LED and button that `onboard_parts` gives (P484), as `BuildService` does;
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

    Separated from the simulation stage so a test can reach it: that stage needs a toolchain and a converter, so what was
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
