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
from spark.build import project_setup
from spark.build.board_engine import convert, converter_stage_problem, find_converter
from spark.build.pour_contact import PourContact
from spark.build.stages import (BOARD, BOARD_EMITTER_CRASHED_ENDING, BOARD_ONLY_ENDING, BOARD_ONLY_WITH_PARTS_ENDING,
                                BOARD_UNUSABLE_ENDING, BUILD, CHIP_NOT_COMPILED_ENDING, CIRCUIT_ERRORS_ENDING,
                                DIAGRAM_UNWIRED_ENDING, ENGINE_MISSING_ENDING, EVERY_PART_SKIPPED_ENDING, FACT_MISSING_ENDING,
                                FOOTPRINT, FOOTPRINT_EMITTER_CRASHED_ENDING, NO_CIRCUIT_ENDING, NO_FOOTPRINT_HINT,
                                NO_PARTS_ENDING, NO_WOKWI_PART_TYPE_ENDING, NOT_ROUTED_ENDING, PART_STRANDED_ENDING, PARTS,
                                SCHEMATIC, SCHEMATIC_NOTED_ENDING, SCHEMATIC_NOTES, SCHEMATIC_REFUSED_ENDING, SIMULATION,
                                STAGE_NAMED, TIMED_OUT_ENDING, TOOL_CANNOT_BUILD_ENDING)
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

from spark.core.outcomes import EXIT_FOR, EXIT_OK, COULD_NOT_RUN, PROBLEMS, SKIPPED, status_of
from spark.core.result import Finding
from spark.core.text_guards import clean


#: Wokwi's serial monitor, as a diagram names it: its two wires are the board's own, never a design's (P190).
SERIAL_MONITOR = "$serialMonitor"


def wires_in(diagram, apart=()):
    """Connections between parts; the serial monitor's two are not counted, so all nets failed still counts 0. A wire to
    one of the part ids in `apart` is not counted either: the full build leaves out the stand-ins it adds (P792)."""
    return sum(1 for connection in diagram.get("connections") or []
               if not any(str(end).startswith(SERIAL_MONITOR) or str(end).split(":")[0] in apart for end in connection[:2]))


def serial_wired(diagram):
    """Whether the board's serial port reaches Wokwi's serial monitor, so a scenario hears what the firmware prints."""
    return any(str(end).startswith(SERIAL_MONITOR) for connection in diagram.get("connections") or []
               for end in connection[:2])


def every_part_skipped(mapping):
    """Whether every component in `sim_project.mapping_for`'s mapping is skipped (`simulation.skip`), so the diagram holds
    none of the project's parts, a diagram with no wire is no defect and the stage is SKIPPED (P778). False for an empty mapping: nothing skipped is nothing proven."""
    return bool(mapping) and all("skip" in entry for entry in mapping.values())


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


def islands_in(circuit, claims=(), across=(), no_own_ground=()):
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
    findings, present = _reaches_no_ground(board, names, passives, no_own_ground)
    findings += ["%s.%s (a terminal connected to nothing)"
                 % (names.get(port.get("source_component_id"), "?"), port.get("name") or port_id)
                 for port_id, port in board.ports.items()
                 if port.get("source_component_id") in present & passives
                 and port_id not in board.nets_of_port]
    return sorted(findings + _unfed(board, claims))


def _reaches_no_ground(board, names, passives, no_own_ground=()):
    """`islands_in`'s first question: each chip wired to something and to no ground, as a finding, and every
    component wired at all. A component named in `no_own_ground` (`power_rails.parts_without_a_ground_pin`, P1026) is
    not asked: a button between a pin and a rail has two pins and no ground pin, and its return is its other pin."""
    ground_ids = {net_id for net_id, net in board.nets.items()
                  if (net.get("name") or "").upper() in GROUND_NETS}
    grounded, present = set(), set()
    for port_id, net_ids in board.nets_of_port.items():
        owner = board.ports[port_id].get("source_component_id")
        present.add(owner)
        if net_ids & ground_ids:
            grounded.add(owner)
    grounded |= {owner for owner in present if names.get(owner) in no_own_ground}
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

    def __init__(self, engine, emitter, find_tool=None, runner=None):
        self.engine = engine
        self.emitter = emitter
        self.find_tool = find_tool  # (a name, a project) -> Tool, for the build's and the converter's sentences; the real finder when None (P725)
        self.runner = runner  # what runs the converter's command, subprocess.run when None (P664)

    @classmethod
    def for_toolchain(cls, toolchain, find_tool=None):
        """The real engine over `toolchain` (None: found from the project at build time) and the emitter that lays out around
        a guessed size, as the CLI `check_spine.py` builds; `find_tool` as `__init__`'s."""
        return cls(board_engine.TscircuitEngine(toolchain), board_emitter.BoardEmitter(assume_missing_sizes=True), find_tool)

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
            stages.append(BOARD.ended(BOARD_UNUSABLE_ENDING, exc))
            return None
        stages.append(BOARD.ok(board["name"] + (
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
                stages.append(PARTS.ended(BOARD_ONLY_WITH_PARTS_ENDING))
            else:
                stages.extend(board_alone(board, inputs.workdir, inputs.firmware, project, self.runner))
            return None
        if not requirements.get("parts"):
            stages.append(PARTS.ended(NO_PARTS_ENDING, need_requirements.BOARD_ONLY))
            return None
        # `board_emitter` reads the same records; if that succeeded, this cannot fail for a reason not already told.
        try:
            return loader.parts_of(requirements, project)
        except loader.DesignError as broken:
            stages.append(PARTS.stopped_by(broken))
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
            stages.append(STAGE_NAMED[refused.stage].stopped_by(refused, hint))
            return None
        except Exception as crash:  # noqa: BLE001 -- a crash in the emitter is a stage (F5), not a lost run
            stages.append(SCHEMATIC.ended(BOARD_EMITTER_CRASHED_ENDING, type(crash).__name__, crash))
            return None
        if refusal:
            # It refused the input — a part with no measured outline, a resistor nothing sizes — in its own words.
            stages.append(SCHEMATIC.ended(SCHEMATIC_REFUSED_ENDING, refusal))
            return None
        (workdir / "board.tsx").write_text(text)
        stages.append(SCHEMATIC.ok("%d trace(s) written" % text.count(board_sections.TRACE_TAG)))
        if notes:
            stages.append(SCHEMATIC_NOTES.ended(SCHEMATIC_NOTED_ENDING, "\n".join(notes)))
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
                stages.append(FOOTPRINT.stopped_by(disagreement))
                return False
            text = footprint_emitter.render(footprint_board, rules)
        except Exception as crash:  # noqa: BLE001 -- a crash in drawing the footprint is a stage (F5), not a lost run
            stages.append(FOOTPRINT.ended(FOOTPRINT_EMITTER_CRASHED_ENDING, type(crash).__name__, crash))
            return False
        (workdir / ("%s.tsx" % export)).write_text(text)
        stages.append(FOOTPRINT.ok("%s.tsx" % export))
        return True

    def _build_circuit(self, inputs, project, board, part_list, stages):
        """The build, the only stage that can prove the ones before it: the engine found from the project (its tools file,
        not the scratch directory's: a broken or pinned project file must be read), run, and asked its version; a tool that
        built nothing is probed on a trivial board. The `BuildResult` when the circuit passed, else None."""
        engine = self.engine.found_from(project)
        if engine is None:
            try:
                (self.find_tool or tool_finder.find)("board-engine", project)
                said = "the board engine was not found"
            except tool_finder.ToolError as missing:
                said = str(missing)  # the tools list's own sentence, with what installs it (P82)
            stages.append(BUILD.ended(ENGINE_MISSING_ENDING, said))
            return None
        ran = self._run_engine(engine, inputs.workdir, stages)
        if ran is None:
            return None
        built, can, last_words = ran
        version = engine.version()
        if not built.circuit_path.is_file():
            if not can:
                stages.append(BUILD.ended(TOOL_CANNOT_BUILD_ENDING, engine.toolchain, version, last_words))
                return None
            stages.append(BUILD.ended(NO_CIRCUIT_ENDING, engine.toolchain, version, built.stderr.strip()[-800:]))
            return None
        verdict = self._circuit_verdict(built.circuit_path, board, part_list, stages)
        if verdict is None:
            return None
        traces, notes = verdict
        stages.append(BUILD.ok("; ".join(["%d trace(s), 0 errors, tsci %s%s" % (traces, version, core_note(version))] + notes)))
        return built

    @staticmethod
    def _run_engine(engine, workdir, stages):
        """
        (the BuildResult, whether the engine builds a trivial board, its last words), or None when a run passed its limit:
        the build stage then names the late command, and the stages before it stand (P664). A build that left nothing is
        probed on a trivial board: a tool that cannot build that is not reporting on the design at all.
        """
        try:
            built = engine.build(workdir)
            can, last_words = (True, "") if built.circuit_path.is_file() else engine.probe(workdir)
        except board_engine.TimedOutError as late:
            stages.append(BUILD.ended(TIMED_OUT_ENDING, late))
            return None
        return built, can, last_words

    def _circuit_verdict(self, circuit_path, board, part_list, stages):
        """What the built circuit says of the design: (its trace count, a note for each pour short its copper disproves) when
        it passed, else None after the stage that stops it."""
        circuit = json.loads(circuit_path.read_text())
        traces, errors = count_in(circuit)
        errors, notes = PourContact(circuit).disproved(errors)
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
                             no_own_ground=power_rails.parts_without_a_ground_pin(part_list),
                             across=power_rails.loads_across_a_pair(part_list))
        if islands:
            stages.append(BUILD.ended(PART_STRANDED_ENDING, "; ".join(islands)))
            return None
        if errors:
            first = [error.get("selectors_not_found") or error.get("message", "") for error in errors[:2]]
            first = clean("; ".join(", ".join(map(str, one)) if isinstance(one, list) else str(one) for one in first), 300)
            stages.append(BUILD.ended(CIRCUIT_ERRORS_ENDING,  # --- MVP --- (P512) names the trace
                                      len(errors), ", ".join(sorted({element["type"] for element in errors})), first))
            return None
        if traces == 0:
            stages.append(BUILD.ended(NOT_ROUTED_ENDING))
            return None
        return traces, notes

    def _simulation(self, inputs, project, board, built, stages):
        """The simulation project, the last step of the product goal: the converter found from the project (not from `cwd`:
        run from /tmp the converter beside the project was "not found"), the stand-ins from the records (P31) and the board's own (P792), the diagram."""
        workdir = inputs.workdir
        stopped = no_wokwi_part(board)
        if stopped:
            stages.append(stopped)
            return
        own = find_converter(project)
        missing = converter_stage_problem(project, own, self.find_tool)
        if missing:
            stages.append(missing)
            return
        # Read again with None for a library design, which lets a project above TMPDIR win (loader.py:192); equal otherwise.
        loaded = loader.load(workdir / "requirements.json", None if inputs.from_library else project)
        mapping, chips, unmapped = sim_project.mapping_for(loaded)
        stand_ins = board_alone_input.OnboardStandIns(board, project)
        why = sim_project.unmapped_detail(unmapped) if unmapped else stand_ins.why
        if why:
            stages.append(SIMULATION.ended(FACT_MISSING_ENDING, why))
            return
        written = self._sim_folder(inputs, board, stand_ins.files(mapping), chips, stages)
        if written is None:
            return
        sim_dir, staged = written
        diagram, stopped, notes = convert(project, own, ["--circuit", str(built.circuit_path)] + stand_ins.source(sim_dir), sim_dir, self.runner)
        if stopped:
            stages.append(stopped)
            return
        # The project's mapping, before the stand-ins joined it: a project of skipped parts stays skipped (P792).
        wires, skipped, found = wires_in(diagram), every_part_skipped(mapping), stand_ins.found_in(diagram)
        if wires_in(diagram, found.ids) == 0 and not skipped:
            stages.append(SIMULATION.ended(DIAGRAM_UNWIRED_ENDING))
            return
        compiled = sum(1 for how in staged.values() if how == "compiled")
        # What the simulation cannot show, in the records' own words, said and kept beside the diagram (P37).
        limits = sim_project.write_limits(sim_dir, loaded, board, found.gpios)
        detail = simulation_detail(wires, staged, compiled, limits, serial_heard(diagram, board)) + notes + found.note
        stages.append(SIMULATION.ended(EVERY_PART_SKIPPED_ENDING, detail) if skipped else SIMULATION.ok(detail))

    def _sim_folder(self, inputs, board, files, chips, stages):
        """`sim/` in the work folder with `files` ({file name: JSON value}), the board record, the chips staged and wokwi.toml:
        (the folder, how each chip was staged), or None after the could-not-run stage of a chip that does not compile."""
        sim_dir = inputs.workdir / "sim"
        sim_dir.mkdir(exist_ok=True)
        for name, data in dict(files, **{"board.json": board}).items():
            (sim_dir / name).write_text(json.dumps(data, indent=2) + "\n")
        staged, chip_problems = sim_project.stage_chips(chips, sim_dir, find_tool=self.find_tool)
        if chip_problems:
            stages.append(SIMULATION.ended(CHIP_NOT_COMPILED_ENDING, "\n".join(chip_problems)))
            return None
        (sim_dir / "wokwi.toml").write_text(sim_project.wokwi_toml(staged, inputs.firmware))
        return sim_dir, staged


def no_wokwi_part(board):
    """The could-not-run simulation stage of a board whose record names no Wokwi part, or None: one guard for the full
    build and the board-only build (P955). It speaks before the converter, whose lint crashed on the null type, and before
    a missing converter or an unmapped part, so a person who adds the board's Wokwi part sees the next cause next."""
    if not board.get("wokwi_part_type"):
        return SIMULATION.ended(NO_WOKWI_PART_TYPE_ENDING)
    return None


def board_alone(board, workdir, firmware=None, project=None, runner=None):
    """
    The stages after `board` for a project that runs on the board alone (P236): parts, schematic, footprint and build are
    SKIPPED, never ok. The converter wires the board's own LED and button that `onboard_parts` gives (P484), as `BuildService` does;
    with none, the diagram holds the board's part alone. The full build adds the same parts to its circuit (P792). A limit "not checked" stays a limit in an ok stage (P396, P37).
    """
    skipped = [definition.ended(BOARD_ONLY_ENDING) for definition in (PARTS, SCHEMATIC, FOOTPRINT, BUILD)]
    stopped = no_wokwi_part(board)
    if stopped:
        return skipped + [stopped]
    sim_dir, project = workdir / "sim", project or board_records.PLUGIN_ROOT
    given, own = board_alone_input.read_board_alone(board, project), find_converter(project)
    stopped = given.wired and (converter_stage_problem(project, own) or (SIMULATION.ended(FACT_MISSING_ENDING, given.why) if given.why else None))
    if stopped:
        return skipped + [stopped]
    sim_dir.mkdir(exist_ok=True)
    (sim_dir / "wokwi.toml").write_text(sim_project.wokwi_toml((), firmware))
    for name, data in dict(given.files, **{"board.json": board}).items():
        (sim_dir / name).write_text(json.dumps(data, indent=2) + "\n")
    diagram, stopped, notes = (convert(project, own, ["--netlist", str(sim_dir / board_alone_input.NETLIST)], sim_dir, runner) if given.wired
                               else (given.files["diagram.json"], None, ""))
    if stopped:
        return skipped + [stopped]
    limits = sim_project.write_limits(sim_dir, None, board, onboard_parts.say_wired_gpios(given.wired))
    return skipped + [SIMULATION.ok(given.lead + simulation_detail(wires_in(diagram), {}, 0, limits, serial_heard(diagram, board)) + notes)]


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


def findings_of(stages):
    """The Findings of the chain, by the rule `verdict` answers by (P804): one for each stage that found problems or could
    not run, of its status, with the stage's name as the subject, its detail as the sentence and its own code."""
    return [Finding.of(stage.status, stage.name, stage.code, stage.detail) for stage in stages if stage.status in (PROBLEMS, COULD_NOT_RUN)]


def vouches_for_a_build(stages):
    """Whether the store may note that the board was built: the chain ran end to end, and no stage was skipped (P236)."""
    return verdict(stages) == EXIT_OK and not any(stage.status == SKIPPED for stage in stages)
