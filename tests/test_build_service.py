"""
P706: `BuildService` runs the six stages over the engine and the emitter it is given, in process. The engine is
`FakeTscircuitEngine`; the emitter is the real `BoardEmitter` on the plugin's library, or a subclass that records or
crashes. The goldens of `test_golden_design` hold the CLI's bytes; here the stop rule, the crash sentences, the notes
and the engine's runner. The codes and the limit are literals here, as in test_check_spine.
"""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from fakes import FakeBuildService, FakeTscircuitEngine  # noqa: E402
from golden_design import fed_circuit  # noqa: E402
from spark.build import board_engine, kept_files  # noqa: E402
from spark.build.build_service import BuildInputs, BuildService, board_alone  # noqa: E402
from spark.build.requirements_build import RequirementsBuildService  # noqa: E402
from spark.design import board_emitter  # noqa: E402
from spark.core.outcomes import COULD_NOT_RUN, EXIT_COULD_NOT_RUN, OK, PROBLEMS, SKIPPED  # noqa: E402
from spark.build.build_service import every_part_skipped, verdict, vouches_for_a_build  # noqa: E402

REFERENCE = {"board": "firebeetle2-esp32s3", "parts": ["l9110s-module", "vl6180x-breakout", "jst-ph-2-power-inlet"]}
#: The display whose record skips the simulation (Wokwi has no ST7789V part), and a diagram of the board alone: no wire but the serial monitor's.
DISPLAY = json.loads((ROOT / "tests" / "data" / "parts" / "dfr0664-tft-2in.json").read_text())
BOARD_ALONE_DIAGRAM = {"version": 1, "parts": [{"type": "board-xiao-esp32-c6", "id": "esp"}],
                       "connections": [["esp:TX", "$serialMonitor:RX", "", []], ["esp:RX", "$serialMonitor:TX", "", []]]}


class ARecordingEmitter(board_emitter.BoardEmitter):
    """The real emitter, counting its `emit` calls, with `read` or `emit` raising `crash` when the test gives one."""

    def __init__(self, read_crash=None, emit_crash=None):
        super().__init__(assume_missing_sizes=True)
        self.read_crash, self.emit_crash, self.emitted = read_crash, emit_crash, 0

    def read(self, path, project, board_id=None):
        if self.read_crash:
            raise self.read_crash
        return super().read(path, project, board_id)

    def emit(self, inputs):
        self.emitted += 1
        if self.emit_crash:
            raise self.emit_crash
        return super().emit(inputs)


def a_build(requirements=REFERENCE, engine=None, emitter=None, runner=None, **inputs):
    """The stages of one build in a fresh work folder, with the requirements file written as `main` writes it; `runner`
    runs the converter's command, as BuildService's."""
    workdir = Path(tempfile.mkdtemp())
    (workdir / "requirements.json").write_text(json.dumps(requirements))
    service = BuildService(engine or FakeTscircuitEngine(), emitter or board_emitter.BoardEmitter(assume_missing_sizes=True), runner=runner)
    return workdir, service.build(BuildInputs(requirements, workdir, **inputs))


class TheStopRuleTest(unittest.TestCase):
    def test_a_refused_read_stops_before_the_board_is_emitted(self):
        emitter = ARecordingEmitter()
        _, stages = a_build({"board": "xiao-esp32-c6", "parts": ["led-red-5mm"], "signals": [{"name": "X", "needs": ["teleport"]}]},
                            emitter=emitter)
        self.assertEqual((stages[-1].name, stages[-1].status), ("schematic", COULD_NOT_RUN))
        self.assertIn("X asks for teleport", stages[-1].detail)
        self.assertEqual(emitter.emitted, 0)

    def test_an_engine_nobody_found_is_tool_missing_and_the_build_stage_ends_the_run(self):
        engine = FakeTscircuitEngine(found=False)
        workdir, stages = a_build(engine=engine)
        self.assertEqual((stages[-1].name, stages[-1].status, stages[-1].code), ("build", COULD_NOT_RUN, "tool_missing"))
        self.assertEqual([stage.name for stage in stages], ["board", "schematic", "footprint", "build"])
        self.assertEqual(engine.looked_from, [ROOT])  # the project, resolved: never the work folder
        self.assertTrue((workdir / "board.tsx").is_file())

    def test_a_tool_that_built_nothing_is_probed_and_named_with_its_version(self):
        engine = FakeTscircuitEngine(circuit=None, version="1.2.3-fake", probe=(False, "Cannot find package 'react'"))
        workdir, stages = a_build(engine=engine)
        self.assertEqual((stages[-1].name, stages[-1].status, stages[-1].code), ("build", COULD_NOT_RUN, "tool_cannot_build"))
        self.assertIn("fake-tsci (1.2.3-fake) cannot build even a trivial board", stages[-1].detail)
        self.assertIn("Cannot find package 'react'", stages[-1].detail)
        self.assertEqual(engine.built_in, [workdir])


class ACrashInTheEmitterIsAStageTest(unittest.TestCase):
    """F5: a crash in the board emitter is could-not-run, named as the emitter's, and keeps the stages before it."""

    def test_a_crash_in_reading_the_input(self):
        _, stages = a_build(emitter=ARecordingEmitter(read_crash=ValueError("a fault of its own")))
        self.assertEqual([(s.name, s.status) for s in stages], [("board", OK), ("schematic", COULD_NOT_RUN)])
        self.assertEqual((stages[-1].detail, stages[-1].code), ("the board emitter crashed: ValueError: a fault of its own", "stage_crashed"))
        self.assertEqual(verdict(stages), EXIT_COULD_NOT_RUN)

    def test_a_crash_in_emitting_the_board(self):
        workdir, stages = a_build(emitter=ARecordingEmitter(emit_crash=RuntimeError("a fault of its own")))
        self.assertEqual((stages[-1].name, stages[-1].status), ("schematic", COULD_NOT_RUN))
        self.assertEqual(stages[-1].detail, "the board emitter crashed: RuntimeError: a fault of its own")
        self.assertFalse((workdir / "board.tsx").exists())


class TheNotesAreOneStageTest(unittest.TestCase):
    def test_a_design_with_notes_has_one_schematic_notes_stage_with_a_line_per_note(self):
        requirements = {"board": "firebeetle2-esp32s3", "parts": ["speaker-terminal"]}  # the two sides of the pair, nothing drives either
        workdir, stages = a_build(requirements)
        notes = board_emitter.design_notes(board_emitter.read_inputs(workdir / "requirements.json", ROOT))
        self.assertEqual(len(notes), 2, notes)
        self.assertTrue(all(note.startswith("note: ") for note in notes), notes)
        said = [stage for stage in stages if stage.name == "schematic-notes"]
        self.assertEqual([(s.status, s.code, s.detail) for s in said], [(PROBLEMS, "schematic_noted", "\n".join(notes))])
        self.assertEqual(said[0].detail.count("\n"), 1)
        self.assertEqual([stage.name for stage in stages[:3]], ["board", "schematic", "schematic-notes"])

    def test_a_design_without_notes_has_none(self):
        _, stages = a_build()
        self.assertNotIn("schematic-notes", [stage.name for stage in stages])


class TheEngineRunsWithTheRunnerItIsGivenTest(unittest.TestCase):
    def test_build_runs_tsci_in_the_work_folder_under_the_builds_limit(self):
        asked = []

        def a_runner(command, **named):
            asked.append((command, named))
            return subprocess.CompletedProcess(command, 0, "", "routed")

        workdir = Path(tempfile.mkdtemp())
        built = board_engine.TscircuitEngine(Path("/x/tsci"), runner=a_runner).build(workdir)
        self.assertEqual(built, (workdir / "dist" / "board" / "circuit.json", "routed"))
        self.assertEqual(asked[0][0], ["/x/tsci", "build", "board.tsx"])
        self.assertEqual((asked[0][1]["cwd"], asked[0][1]["timeout"]), (str(workdir), 900))

    def test_found_from_keeps_its_toolchain_and_its_runner(self):
        runner = object()
        engine = board_engine.TscircuitEngine(Path("/x/tsci"), runner=runner)
        self.assertIs(engine.found_from(ROOT), engine)
        self.assertIs(board_engine.TscircuitEngine(None, runner=runner)._runner, runner)



class AnEngineBuildPastItsLimitKeepsTheStagesBeforeItTest(unittest.TestCase):
    """P664: a `tsci build` past its limit was one `build` stage that replaced every other; the stages that ran stand."""

    class LateEngine(FakeTscircuitEngine):
        def build(self, workdir):
            raise board_engine.TimedOutError("`tsci build` did not finish in 900s")

    def test_the_stages_before_the_build_stand_and_the_build_names_the_limit(self):
        _, stages = a_build(engine=self.LateEngine())
        self.assertEqual([stage.status for stage in stages[:-1]], [OK] * (len(stages) - 1))
        self.assertGreater(len(stages), 1)
        self.assertEqual((stages[-1].name, stages[-1].status, stages[-1].code, stages[-1].detail),
                         ("build", COULD_NOT_RUN, "stage_timed_out", "`tsci build` did not finish in 900s"))
        self.assertEqual(kept_files.why_not_built(stages, "board only"), "the build did not finish in this run")

    def test_the_engine_turns_its_own_timeout_into_the_sentence(self):
        def late(command, **named):
            raise subprocess.TimeoutExpired(command, named["timeout"], stderr="routing\n")
        with self.assertRaises(board_engine.TimedOutError) as raised:
            board_engine.TscircuitEngine(Path("/x/tsci"), runner=late).build(Path(tempfile.mkdtemp()))
        self.assertEqual(str(raised.exception), "`tsci build` did not finish in 900s; its last words: routing")

    def test_a_probe_past_its_limit_is_said_apart_from_the_build(self):
        def late(command, **named):
            raise subprocess.TimeoutExpired(command, named["timeout"])
        with self.assertRaises(board_engine.TimedOutError) as raised:
            board_engine.TscircuitEngine(Path("/x/tsci"), runner=late).probe(Path(tempfile.mkdtemp()))
        self.assertEqual(str(raised.exception), "the probe on a trivial board: `tsci build` did not finish in 120s")

if __name__ == "__main__":
    unittest.main()


#: Where `a_converter_shim` writes the arguments it was run with.
SHIM_ARGS = "converter-args.json"


def a_converter_shim(folder, diagram):
    """The tools list entry of a diagram converter in `folder` that writes `diagram` to its --out, run by this Python, and
    its arguments to `folder`/SHIM_ARGS."""
    shim = Path(folder) / "fake-circuit-to-wokwi"
    shim.write_text("#!%s\nimport json, sys\nargs = sys.argv[1:]\nwith open(args[args.index('--out') + 1], 'w') as out:\n"
                    "    json.dump(%s, out)\nwith open(%r, 'w') as said:\n    json.dump(args, said)\n"
                    % (sys.executable, json.dumps(diagram), str(Path(folder) / SHIM_ARGS)))
    shim.chmod(0o755)
    return {"circuit-to-wokwi": {"kind": "path", "exe": str(shim), "also": [], "fetch": None, "needs": []}}


class TheSimulationStageOfASkippedDesignTest(unittest.TestCase):
    """P778 (p512 row 3): a diagram with no wire is a defect only while a part that is not skipped exists; a design whose
    every part is skipped is a skipped stage that says so, with the limits, and vouches for no build (the PO, 2026-11-12)."""

    SKIPPED = "Display: not simulated at all: Wokwi has no ST7789V part for a 240x320 panel"
    BOARD = "xiao-esp32-c6"
    #: Whether the board's Wokwi part is another board's (`wokwi_is_stand_in`), so the build adds its own LED and button.
    STAND_IN = False

    FEEDS = (("Mcu", "3V3", "V33"), ("Display", "VCC", "V33"))

    def simulation(self, parts, diagram=BOARD_ALONE_DIAGRAM):
        """The simulation stage of `stages`."""
        return self.stages(parts, diagram)[-1]

    def stages(self, parts, diagram=BOARD_ALONE_DIAGRAM, runner=None, records=(), boards=()):
        """The stages of a build on BOARD whose project holds the display's record, `records` and `boards` ((id, record)),
        and a converter that writes `diagram` (run by `runner` when given); the engine builds a circuit that feeds the board
        and the display, so the build stage passes."""
        project = self.project = Path(tempfile.mkdtemp()) / "sim project"
        (project / ".spark").mkdir(parents=True)
        (project / "parts").mkdir()
        (project / "boards").mkdir()
        for record_id, record in (("dfr0664-tft-2in", DISPLAY),) + tuple(records):
            (project / "parts" / (record_id + ".json")).write_text(json.dumps(record))
        for board_id, board in boards:
            (project / "boards" / (board_id + ".json")).write_text(json.dumps(board))
        (project / ".spark" / "tools.json").write_text(json.dumps(a_converter_shim(project, diagram)))
        self.workdir, stages = a_build({"board": self.BOARD, "parts": parts}, engine=FakeTscircuitEngine(fed_circuit(self.FEEDS)), runner=runner, project=project)
        self.assertEqual(stages[-1].name, "simulation", [(stage.name, stage.status, stage.detail) for stage in stages])
        return stages

    def test_every_part_skipped_is_a_skipped_stage_that_says_so_with_the_limits_and_vouches_for_no_build(self):
        # the PO, 2026-11-12: skipped, not ok, so the store notes no build
        stages = self.stages([{"part": "dfr0664-tft-2in", "name": "Display"}])
        stage = stages[-1]
        self.assertEqual((stage.status, stage.code), (SKIPPED, None))
        self.assertTrue(stage.detail.startswith("every part is skipped from the simulation, so the diagram holds none of the project's parts, 0 wire(s) in the diagram"), stage.detail)
        self.assertIn("what it cannot show (", stage.detail)
        self.assertIn(self.SKIPPED, stage.detail)
        self.assertEqual((verdict(stages), vouches_for_a_build(stages)), (0, False))

    def test_a_converter_past_its_limit_after_a_passed_build_keeps_the_build_and_names_the_simulation(self):
        # P664: the stages before the late one stand, so the build is said to have built and the sheet and page are kept
        def late(command, **named):
            raise subprocess.TimeoutExpired(command, named["timeout"], stderr="placing parts\n")
        stages = self.stages([{"part": "dfr0664-tft-2in", "name": "Display"}], runner=late)
        self.assertEqual([(stage.name, stage.status) for stage in stages][-2:], [("build", OK), ("simulation", COULD_NOT_RUN)])
        self.assertEqual(stages[-1].code, "stage_timed_out")
        self.assertIn("did not finish in 120s; its last words: placing parts", stages[-1].detail)
        self.assertIsNone(kept_files.why_not_built(stages, "board only"))
        self.assertEqual(verdict(stages), EXIT_COULD_NOT_RUN)

    def test_a_skipped_part_beside_a_real_one_with_no_wire_is_still_the_unwired_diagram(self):
        stage = self.simulation([{"part": "dfr0664-tft-2in", "name": "Display"}, {"part": "led-red-5mm", "name": "Led"}])
        self.assertEqual((stage.status, stage.code), (PROBLEMS, "diagram_unwired"))
        self.assertNotIn("every part is skipped", stage.detail)

    def test_the_unwired_diagram_says_its_detail(self):  # P852
        stage = self.simulation([{"part": "dfr0664-tft-2in", "name": "Display"}, {"part": "led-red-5mm", "name": "Led"}])
        self.assertEqual(stage.detail, "a diagram with 0 connections. Every part is placed and none is wired, which is what an "
                                       "unmapped component looks like once the converter has given up on it")

    def test_the_converter_gets_an_added_netlist_only_on_a_stand_in_board(self):  # P792
        self.stages([{"part": "dfr0664-tft-2in", "name": "Display"}])
        self.assertEqual("--add-netlist" in json.loads((self.project / SHIM_ARGS).read_text()), self.STAND_IN)

    def test_an_empty_mapping_is_not_every_part_skipped_and_a_real_part_is_not_either(self):
        self.assertFalse(every_part_skipped({}))
        self.assertFalse(every_part_skipped({"Display": {"skip": "no part"}, "Led": {"wokwiType": "wokwi-led"}}))
        self.assertTrue(every_part_skipped({"Display": {"skip": "no part"}, "Jack": {"skip": "wiring"}}))


class AStandInBoardsOwnPartsInTheFullBuildTest(TheSimulationStageOfASkippedDesignTest):
    """P792: on a stand-in board (the FireBeetle's Wokwi part is the S3 devkit), the full build gives the converter the
    board's own LED and button with --add-netlist, as the board-only build wires them, and says only what the diagram holds."""

    BOARD = "firebeetle2-esp32s3"
    STAND_IN = True
    #: What the converter writes for the board and its two stand-ins: the serial monitor and four wires.
    STAND_INS = {"version": 1, "parts": [{"type": "board-esp32-s3-devkitc-1", "id": "mcu"}, {"type": "wokwi-led", "id": "onboard_led"},
                                         {"type": "wokwi-pushbutton", "id": "onboard_button"}],
                 "connections": BOARD_ALONE_DIAGRAM["connections"] + [
                     ["mcu:21", "onboard_led:A", "green", []], ["mcu:GND.1", "onboard_led:C", "black", []],
                     ["mcu:47", "onboard_button:1.l", "green", []], ["mcu:GND.1", "onboard_button:2.l", "black", []]]}
    BUTTON = "ONBOARD_BUTTON (GPIO47): the Wokwi stand-in has no button on GPIO47, so spark wires Wokwi's pushbutton"

    def test_the_stand_ins_reach_the_converter_and_the_limits_and_every_part_skipped_stays_skipped(self):
        stage = self.simulation([{"part": "dfr0664-tft-2in", "name": "Display"}], self.STAND_INS)
        self.assertEqual((stage.status, stage.code), (SKIPPED, None))
        self.assertIn("so the diagram holds none of the project's parts, 4 wire(s) in the diagram", stage.detail)
        self.assertIn(self.BUTTON, stage.detail)
        self.assertIn("ONBOARD_LED (GPIO21): the Wokwi stand-in has no LED on GPIO21", stage.detail)
        args = json.loads((self.project / SHIM_ARGS).read_text())
        self.assertEqual(args[args.index("--add-netlist") + 1], str(self.workdir / "sim" / "netlist.json"))
        mapping = json.loads((self.workdir / "sim" / "wokwi-mapping.json").read_text())
        self.assertEqual(sorted(mapping), ["Display", "onboard_button", "onboard_led"])

    def test_wires_to_the_stand_ins_alone_are_still_the_unwired_diagram(self):
        stage = self.simulation([{"part": "dfr0664-tft-2in", "name": "Display"}, {"part": "led-red-5mm", "name": "Led"}], self.STAND_INS)
        self.assertEqual((stage.status, stage.code), (PROBLEMS, "diagram_unwired"))

    def test_a_stand_in_s_record_without_its_wokwi_part_stops_the_simulation(self):
        led = {key: value for key, value in json.loads((ROOT / "parts" / "led-red-5mm.json").read_text()).items() if key != "simulation"}
        stage = self.stages([{"part": "dfr0664-tft-2in", "name": "Display"}], self.STAND_INS, records=[("led-red-5mm", led)])[-1]
        self.assertEqual((stage.status, stage.code), (COULD_NOT_RUN, "simulation_fact_missing"))
        self.assertIn("the record for 'led-red-5mm' names no signal pin, ground pin or Wokwi part, so spark cannot wire onboard_led", stage.detail)

    def test_a_converter_that_wires_no_stand_in_says_so_and_the_limits_do_not_claim_them(self):
        stage = self.simulation([{"part": "dfr0664-tft-2in", "name": "Display"}], BOARD_ALONE_DIAGRAM)
        self.assertIn("the diagram holds no stand-in for onboard_led and onboard_button: a project's own converter older than P792", stage.detail)
        self.assertNotIn(self.BUTTON, stage.detail)


class ABoardWithNoWokwiPartInTheFullBuildTest(unittest.TestCase):
    """P955: a board whose record names no Wokwi part (the walk's FireBeetle 2 ESP32-C6) builds, and its simulation stage
    could not run with the reason the board-only build gives, before the converter, whose lint crashed on the null type."""

    BOARD = "xiao-with-no-wokwi-part"
    FEEDS = TheSimulationStageOfASkippedDesignTest.FEEDS
    stages = TheSimulationStageOfASkippedDesignTest.stages  # the helper alone: a subclass would run the parent's tests twice

    def test_the_simulation_could_not_run_names_the_missing_part_type_and_the_converter_is_not_run(self):
        board = dict(json.loads((ROOT / "boards" / "xiao-esp32-c6.json").read_text()), id=self.BOARD, wokwi_part_type=None)
        stages = self.stages([{"part": "dfr0664-tft-2in", "name": "Display"}], boards=[(self.BOARD, board)])
        self.assertEqual([(stage.name, stage.status) for stage in stages][-2:], [("build", OK), ("simulation", COULD_NOT_RUN)])
        self.assertEqual((stages[-1].code, stages[-1].detail), ("simulation_fact_missing", "the board record names no wokwi_part_type"))
        self.assertFalse((self.project / SHIM_ARGS).exists())  # the converter never ran
        self.assertEqual((verdict(stages), vouches_for_a_build(stages)), (EXIT_COULD_NOT_RUN, False))


def crashes(*given, **named):
    """A build that raises what no stage catches."""
    raise RuntimeError("boom")


class EachEndingSaysItsDetailTest(unittest.TestCase):
    """P852: the detail of each way a stage ends that no golden reaches, filled with known values, word for word."""

    FED = fed_circuit((("Mcu", "3V3", "V33"),))
    LED = {"board": "xiao-esp32-c6", "parts": ["led-red-5mm"]}

    def detail(self, requirements=REFERENCE, **given):
        return a_build(requirements, **given)[1][-1].detail

    def converted(self, said):
        """The Stage `board_engine.convert` stops at when the converter exits 1 and says `said`."""
        project = Path(tempfile.mkdtemp())
        (project / ".spark").mkdir()
        (project / ".spark" / "tools.json").write_text(json.dumps(a_converter_shim(project, {})))
        sim_dir = project / "work" / "sim"
        sim_dir.mkdir(parents=True)
        return board_engine.convert(project, None, ["--circuit", "c.json"], sim_dir,
                                    lambda command, **named: subprocess.CompletedProcess(command, 1, "", said))[1]

    def test_the_parts_stage(self):
        self.assertEqual(self.detail({"board": "firebeetle2-esp32s3", "board_only": True, "parts": ["x"]}),
                         "the requirements say board_only and name parts: say one")
        self.assertEqual(self.detail({"board": "firebeetle2-esp32s3"}),
                         "the requirements name no parts, so there is nothing to build; a board holding only the microcontroller "
                         'proves nothing. A project that runs on the board alone says "board_only": true')

    def test_the_build_stage(self):
        self.assertEqual(self.detail(self.LED, engine=FakeTscircuitEngine(self.FED[:6] + self.FED[7:])),
                         "Mcu reaches no ground. A board builds, routes "
                         "and reports no error with a component joined to nothing — the parts around it are wired to nets it is "
                         "simply not on")
        self.assertEqual(self.detail(self.LED, engine=FakeTscircuitEngine([e for e in self.FED if e["type"] != "pcb_trace"])),
                         "built with 0 pcb_traces — every component is placed and no copper joins any of them. tscircuit skips "
                         "routing entirely when one net is unroutable, and that does not raise")
        self.assertEqual(self.detail(self.LED, engine=FakeTscircuitEngine(self.FED + [{"type": "pcb_trace_missing_error", "message": "x"}])),
                         "1 error(s): pcb_trace_missing_error; first: x")
        self.assertEqual(self.detail(engine=FakeTscircuitEngine(circuit=None, stderr="boom\n")),
                         "no circuit.json was produced by fake-tsci (0.0.0-fake), which does build a trivial board\nboom")
        self.assertEqual(self.detail(engine=FakeTscircuitEngine(circuit=None, version="1.2.3", probe=(False, "no react"))),
                         "fake-tsci (1.2.3) cannot build even a trivial board from here, so this is the toolchain, not the design. "
                         "Use the project's own tsci (npm i @tscircuit/cli in the project) or one that builds on its own.\nno react")
        workdir = Path(tempfile.mkdtemp())
        (workdir / "requirements.json").write_text(json.dumps(REFERENCE))
        service = BuildService(FakeTscircuitEngine(found=False), board_emitter.BoardEmitter(assume_missing_sizes=True),
                               find_tool=lambda name, project: None)
        self.assertEqual(service.build(BuildInputs(REFERENCE, workdir))[-1].detail,
                         "the board engine was not found — so the chain was not exercised; /spark:setup installs it")

    def test_the_simulation_stage(self):
        self.assertEqual(self.converted("no Wokwi part is mapped to Servo").detail,
                         "the converter has no Wokwi part for a component on this board — a mapping to add to its lib/mapping.ts, "
                         "not a defect in the design, which built\nno Wokwi part is mapped to Servo")
        self.assertEqual(self.converted("it broke").detail, "no diagram was produced\nit broke")

    def test_a_board_alone_with_no_wokwi_part(self):
        stages = board_alone({"name": "x"}, Path(tempfile.mkdtemp()))
        self.assertEqual([(stage.name, stage.status, stage.detail) for stage in stages],
                         [(name, SKIPPED, "board only: nothing to wire") for name in ("parts", "schematic", "footprint", "build")]
                         + [("simulation", COULD_NOT_RUN, "the board record names no wokwi_part_type")])

    def test_a_crash_no_stage_caught(self):
        built = RequirementsBuildService(FakeBuildService(crashes)).build()
        self.addCleanup(shutil.rmtree, built.workdir)
        self.assertEqual([(stage.name, stage.detail) for stage in built.stages], [("check_spine", "RuntimeError: boom")])
