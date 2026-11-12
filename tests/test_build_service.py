"""
P706: `BuildService` runs the six stages over the engine and the emitter it is given, in process. The engine is
`FakeTscircuitEngine`; the emitter is the real `BoardEmitter` on the plugin's library, or a subclass that records or
crashes. The goldens of `test_golden_design` hold the CLI's bytes; here the stop rule, the crash sentences, the notes
and the engine's runner. The codes and the limit are literals here, as in test_check_spine.
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from fakes import FakeTscircuitEngine  # noqa: E402
from golden_design import fed_circuit  # noqa: E402
from spark.build import board_engine  # noqa: E402
from spark.build.build_service import BuildInputs, BuildService  # noqa: E402
from spark.design import board_emitter  # noqa: E402
from spark.core.outcomes import COULD_NOT_RUN, EXIT_COULD_NOT_RUN, OK, PROBLEMS  # noqa: E402
from spark.build.build_service import every_part_skipped, verdict  # noqa: E402

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


def a_build(requirements=REFERENCE, engine=None, emitter=None, **inputs):
    """The stages of one build in a fresh work folder, with the requirements file written as `main` writes it."""
    workdir = Path(tempfile.mkdtemp())
    (workdir / "requirements.json").write_text(json.dumps(requirements))
    service = BuildService(engine or FakeTscircuitEngine(), emitter or board_emitter.BoardEmitter(assume_missing_sizes=True))
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


if __name__ == "__main__":
    unittest.main()


def a_converter_shim(folder, diagram):
    """The tools list entry of a diagram converter in `folder` that writes `diagram` to its --out, run by this Python."""
    shim = Path(folder) / "fake-circuit-to-wokwi"
    shim.write_text("#!%s\nimport json, sys\nargs = sys.argv[1:]\nwith open(args[args.index('--out') + 1], 'w') as out:\n"
                    "    json.dump(%s, out)\n" % (sys.executable, json.dumps(diagram)))
    shim.chmod(0o755)
    return {"circuit-to-wokwi": {"kind": "path", "exe": str(shim), "also": [], "fetch": None, "needs": []}}


class TheSimulationStageOfASkippedDesignTest(unittest.TestCase):
    """P778 (p512 row 3): a diagram with no wire is a defect only while a part that is not skipped exists; a design whose
    every part is skipped is an ok stage that says so, with the limits."""

    SKIPPED = "Display: not simulated at all: Wokwi has no ST7789V part for a 240x320 panel"

    FEEDS = (("Mcu", "3V3", "V33"), ("Display", "VCC", "V33"))

    def simulation(self, parts, diagram=BOARD_ALONE_DIAGRAM):
        """The simulation stage of a build on the XIAO whose project holds the display's record and a converter that writes
        `diagram`; the engine builds a circuit that feeds the board and the display, so the build stage passes."""
        project = Path(tempfile.mkdtemp()) / "sim project"
        (project / ".spark").mkdir(parents=True)
        (project / "parts").mkdir()
        (project / "parts" / "dfr0664-tft-2in.json").write_text(json.dumps(DISPLAY))
        (project / ".spark" / "tools.json").write_text(json.dumps(a_converter_shim(project, diagram)))
        _, stages = a_build({"board": "xiao-esp32-c6", "parts": parts}, engine=FakeTscircuitEngine(fed_circuit(self.FEEDS)), project=project)
        self.assertEqual(stages[-1].name, "simulation", [(stage.name, stage.status, stage.detail) for stage in stages])
        return stages[-1]

    def test_every_part_skipped_is_ok_and_says_so_with_the_limits(self):
        stage = self.simulation([{"part": "dfr0664-tft-2in", "name": "Display"}])
        self.assertEqual((stage.status, stage.code), (OK, None))
        self.assertTrue(stage.detail.startswith("every part is skipped from the simulation, so the diagram holds the board alone, 0 wire(s) in the diagram"), stage.detail)
        self.assertIn("what it cannot show (", stage.detail)
        self.assertIn(self.SKIPPED, stage.detail)

    def test_a_skipped_part_beside_a_real_one_with_no_wire_is_still_the_unwired_diagram(self):
        stage = self.simulation([{"part": "dfr0664-tft-2in", "name": "Display"}, {"part": "led-red-5mm", "name": "Led"}])
        self.assertEqual((stage.status, stage.code), (PROBLEMS, "diagram_unwired"))
        self.assertNotIn("every part is skipped", stage.detail)

    def test_an_empty_mapping_is_not_every_part_skipped_and_a_real_part_is_not_either(self):
        self.assertFalse(every_part_skipped({}))
        self.assertFalse(every_part_skipped({"Display": {"skip": "no part"}, "Led": {"wokwiType": "wokwi-led"}}))
        self.assertTrue(every_part_skipped({"Display": {"skip": "no part"}, "Jack": {"skip": "wiring"}}))
