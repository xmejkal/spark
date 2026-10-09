"""
Proof that the definition of done cannot be satisfied by a board with no copper on it.

`check_spine` is the one gate that runs the whole chain, so the ways it can be wrong are the ways
every other check here has already been wrong at least once: reporting a pass it did not earn,
and reporting a crash as a verdict.

The load-bearing case is a circuit with zero traces and zero errors. tscircuit produces exactly
that when one net is unroutable — every component placed, every port present, no copper, no
exception. It is what this plugin emitted for weeks, and any gate that only asks "did the build
raise?" calls it a pass.

    python3 -m unittest discover -s tests
"""

import contextlib
import hashlib
import io
import json
import os
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  P172: this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import check_spine  # noqa: E402
import design  # noqa: E402
import emit_board  # noqa: E402
import parts  # noqa: E402
import store  # noqa: E402


def stage(name, status):
    return check_spine.Stage(name, status)


class ABoardWithNoCopperIsNotBuiltTest(unittest.TestCase):
    def test_a_circuit_with_traces_and_no_errors_counts_as_built(self):
        traces, errors = check_spine.count_in(
            [{"type": "pcb_trace"}, {"type": "pcb_trace"}, {"type": "source_component"}])
        self.assertEqual((traces, errors), (2, []))

    def test_traces_are_counted_not_assumed(self):
        # The whole gate rests on this number, so it is read from the netlist and nothing else.
        self.assertEqual(check_spine.count_in([{"type": "source_component"}])[0], 0)

    def test_every_kind_of_error_element_is_found(self):
        # They do not share a prefix — pcb_port_not_connected_error, pcb_trace_missing_error,
        # source_*_error — so the match is on the word, not on a list somebody has to maintain.
        _, errors = check_spine.count_in([
            {"type": "pcb_port_not_connected_error"},
            {"type": "pcb_trace_missing_error"},
            {"type": "pcb_trace"}])
        self.assertEqual(len(errors), 2)

    def test_a_warning_is_not_an_error(self):
        # `pcb_component_missing_courtyard_warning` and friends are present on a good board.
        # Counting them would make the gate unpassable, and an unpassable gate gets removed.
        _, errors = check_spine.count_in([
            {"type": "pcb_component_missing_courtyard_warning"},
            {"type": "source_unnamed_trace_warning"}])
        self.assertEqual(errors, [])


class WhatTheExitCodeMeansTest(unittest.TestCase):
    """
    Three outcomes, never two. The distinction this project is built on is that a chain nobody
    could exercise has not passed, and the exit code is where that either survives or is lost.
    """

    def test_everything_ok_is_ok(self):
        self.assertEqual(check_spine.verdict([stage("board", check_spine.OK),
                                              stage("build", check_spine.OK)]),
                         check_spine.EXIT_OK)

    def test_a_stage_that_could_not_run_is_not_a_pass(self):
        self.assertEqual(check_spine.verdict([stage("board", check_spine.OK),
                                              stage("build", check_spine.COULD_NOT_RUN)]),
                         check_spine.EXIT_COULD_NOT_RUN)

    def test_a_real_problem_outranks_a_stage_that_could_not_run(self):
        # Both present: the thing that is known broken is the more urgent news.
        self.assertEqual(check_spine.verdict([stage("schematic", check_spine.PROBLEMS),
                                              stage("build", check_spine.COULD_NOT_RUN)]),
                         check_spine.EXIT_PROBLEMS)

    def test_the_rendering_never_calls_an_unexercised_chain_a_pass(self):
        rendered = check_spine.render([stage("build", check_spine.COULD_NOT_RUN)],
                                      check_spine.EXIT_COULD_NOT_RUN)
        self.assertIn("NOT exercised", rendered)
        self.assertNotIn("runs end to end", rendered)


class EveryComponentNeedsAGroundTest(unittest.TestCase):
    """
    The defect that prompted this check, and the wrong detector that was tried first.

    A generated board's microcontroller shared a net with NONE of its 32 pins — no ground, no
    3.3 V — while every module around it was correctly wired to a ground the processor was not
    on. It built, it routed, tscircuit reported zero errors, and the gate called it done.
    Nothing in a build flags this: tscircuit checks that each trace you asked for is satisfiable,
    never that you asked for the ones a circuit needs.

    The first attempt compared connections asked for against `pcb_trace` count, and was wrong
    twice: a net with N members needs N-1 traces, and a pin on a poured net (V33 and GND are
    poured — 53 pours on the reference board) is connected by copper with no trace at all. It
    failed a correct board, which is the mirror of the defect it was chasing.
    """

    @staticmethod
    def circuit(*, ground_the_mcu):
        elements = [
            {"type": "source_net", "source_net_id": "n_gnd", "name": "GND"},
            {"type": "source_net", "source_net_id": "n_v33", "name": "V33"},
            {"type": "source_component", "source_component_id": "c_mcu", "name": "Mcu"},
            {"type": "source_component", "source_component_id": "c_mod", "name": "Module"},
            {"type": "source_port", "source_port_id": "p_mcu_sda", "source_component_id": "c_mcu"},
            {"type": "source_port", "source_port_id": "p_mcu_gnd", "source_component_id": "c_mcu"},
            {"type": "source_port", "source_port_id": "p_mod_sda", "source_component_id": "c_mod"},
            {"type": "source_port", "source_port_id": "p_mod_gnd", "source_component_id": "c_mod"},
            # a signal trace: the MCU is wired to something, just not to a ground
            {"type": "source_trace", "source_trace_id": "t1",
             "connected_source_port_ids": ["p_mcu_sda", "p_mod_sda"],
             "connected_source_net_ids": []},
            {"type": "source_trace", "source_trace_id": "t2",
             "connected_source_port_ids": ["p_mod_gnd"],
             "connected_source_net_ids": ["n_gnd"]},
        ]
        if ground_the_mcu:
            elements.append({"type": "source_trace", "source_trace_id": "t3",
                             "connected_source_port_ids": ["p_mcu_gnd"],
                             "connected_source_net_ids": ["n_gnd"]})
        return elements

    def test_a_component_wired_to_signals_but_no_ground_is_caught(self):
        # It has a trace, so "does it connect to anything" would pass it. The question is
        # whether it shares a RETURN PATH, and that is a different question.
        self.assertEqual(
            check_spine.islands_in(self.circuit(ground_the_mcu=False)), ["Mcu reaches no ground"])

    def test_grounding_it_clears_the_finding(self):
        self.assertEqual(
            check_spine.islands_in(self.circuit(ground_the_mcu=True)), [])

    def test_a_ground_under_another_name_still_counts(self):
        # A design with an analogue return calls it AGND, and "the net called GND" stops being
        # true. Naming them beats guessing from the netlist.
        circuit = self.circuit(ground_the_mcu=True)
        for element in circuit:
            if element.get("name") == "GND":
                element["name"] = "AGND"
        self.assertEqual(check_spine.islands_in(circuit), [])

    def test_a_passive_between_a_pin_and_a_rail_is_not_an_island(self):
        # P6 placed the first pull-ups a generated board ever carried, and this check reported
        # them as reaching no ground — which is what a pull-up is. A passive is asked whether an
        # end dangles, not whether it touches ground.
        circuit = self.circuit(ground_the_mcu=True) + [
            {"type": "source_component", "source_component_id": "c_r", "name": "SdaPullup", "ftype": "simple_resistor"},
            {"type": "source_port", "source_port_id": "p_r1", "source_component_id": "c_r", "name": "pin1"},
            {"type": "source_port", "source_port_id": "p_r2", "source_component_id": "c_r", "name": "pin2"},
            {"type": "source_trace", "source_trace_id": "t4", "connected_source_port_ids": ["p_r1", "p_mod_sda"], "connected_source_net_ids": []},
            {"type": "source_trace", "source_trace_id": "t5", "connected_source_port_ids": ["p_r2"], "connected_source_net_ids": ["n_v33"]},
        ]
        self.assertEqual(check_spine.islands_in(circuit), [])
        dangling = [e for e in circuit if e.get("source_trace_id") != "t5"]
        self.assertEqual(check_spine.islands_in(dangling), ["SdaPullup.pin2 (a terminal connected to nothing)"])

    def test_a_component_in_no_trace_at_all_is_not_reported_here(self):
        # Already covered by the generators, which refuse to emit a part they cannot wire.
        # Reporting it twice, in different words, is how a finding gets scrolled past.
        circuit = self.circuit(ground_the_mcu=True) + [
            {"type": "source_component", "source_component_id": "c_lonely", "name": "Lonely"}]
        self.assertNotIn("Lonely", check_spine.islands_in(circuit))


class TheSupplyThePartRecordsPromiseTest(unittest.TestCase):
    """
    P29. A module whose record says something feeds it, on a board where nothing does.

    Reproduced on the irrigation controller before this was written: its buck's record says
    "Feeds the FireBeetle's 5 V/VCC input and the sensors", `net.V5V` joined the buck's VOUT to
    the flow meter's VCC, no trace reached the processor, and the build stage said `[ok]`.
    """

    @staticmethod
    def circuit(*, feed_the_mcu):
        elements = [
            {"type": "source_net", "source_net_id": "n_gnd", "name": "GND"},
            {"type": "source_net", "source_net_id": "n_5v", "name": "V5V"},
            {"type": "source_component", "source_component_id": "c_mcu", "name": "Mcu"},
            {"type": "source_port", "source_port_id": "p_mcu_gnd", "source_component_id": "c_mcu", "name": "GND1"},
            {"type": "source_port", "source_port_id": "p_mcu_vcc", "source_component_id": "c_mcu", "name": "VCC"},
            {"type": "source_trace", "source_trace_id": "t1",
             "connected_source_port_ids": ["p_mcu_gnd"], "connected_source_net_ids": ["n_gnd"]},
        ]
        if feed_the_mcu:
            elements.append({"type": "source_trace", "source_trace_id": "t2",
                             "connected_source_port_ids": ["p_mcu_vcc"],
                             "connected_source_net_ids": ["n_5v"]})
        return elements

    def test_a_pin_the_design_feeds_and_the_board_does_not_is_named(self):
        self.assertEqual(
            check_spine.islands_in(self.circuit(feed_the_mcu=False), [("Mcu", "VCC", "V5V")]),
            ["Mcu.VCC is fed by net.V5V in this design and is not on it"])

    def test_wiring_it_clears_the_finding(self):
        self.assertEqual(
            check_spine.islands_in(self.circuit(feed_the_mcu=True), [("Mcu", "VCC", "V5V")]), [])

    def test_a_rail_the_build_never_created_is_named_too(self):
        # The failure mode that is easy to miss: the trace was asked for, tscircuit dropped it,
        # and the net does not exist at all. `net_named` returns None and that must not read as
        # "no claim to check".
        circuit = [e for e in self.circuit(feed_the_mcu=True) if e.get("name") != "V5V"]
        self.assertEqual(
            check_spine.islands_in(circuit, [("Mcu", "VCC", "V5V")]),
            ["Mcu.VCC is fed by net.V5V in this design and is not on it"])

    def test_no_claims_asks_no_supply_question(self):
        # A button has no supply pin, and asking every component whether it reaches a rail is how
        # a check that fires on correct designs gets ignored. Only what a record states is asked.
        self.assertEqual(check_spine.islands_in(self.circuit(feed_the_mcu=False)), [])


class WhichOfTheModulesOwnPadsGetWiredTest(unittest.TestCase):
    """P29's other half, in the generator: a pad that RECEIVES is conditional, one that drives is not."""

    BOARD = {"power_pads": {"GND1": {"rail": "ground", "direction": "out"},
                            "3V3": {"rail": "logic", "direction": "out"},
                            "VCC": {"rail": "5v", "direction": "in"}}}

    @staticmethod
    def part(direction, rail):
        return {"id": "psu", "name": "Psu", "power": [{"pin": "VOUT", "rail": rail, "direction": direction}]}

    def test_a_receiving_pad_is_left_open_when_nothing_drives_its_rail(self):
        wired = {pad: on for pad, _, on in emit_board.mcu_power_nets(self.BOARD, [])}
        self.assertEqual(wired, {"GND1": True, "3V3": True, "VCC": False})

    def test_a_supply_on_that_rail_wires_it(self):
        wired = dict((pad, on) for pad, _, on in
                     emit_board.mcu_power_nets(self.BOARD, [self.part("out", "5v")]))
        self.assertTrue(wired["VCC"])

    def test_another_consumer_of_the_rail_does_not_count_as_a_source(self):
        # Two sinks and no source is a rail nobody drives, which is the state this exists to
        # refuse to paper over.
        wired = dict((pad, on) for pad, _, on in
                     emit_board.mcu_power_nets(self.BOARD, [self.part("in", "5v")]))
        self.assertFalse(wired["VCC"])

    def test_the_generated_file_says_why_a_pad_was_left_open(self):
        # W1's shape: a connection that was reasoned about and one that was forgotten must not
        # look the same in the output.
        lines = "\n".join(emit_board.mcu_power_lines(self.BOARD, [], {}, set()))
        self.assertIn("Mcu.VCC receives net.V5V and NOTHING ON THIS BOARD DRIVES", lines)
        self.assertNotIn('from=".Mcu > .VCC"', lines)

    def test_the_claim_the_spine_checks_is_the_trace_the_generator_wrote(self):
        # One home: if these two could disagree the check would be worthless, and three defects
        # in this file's history are exactly that disagreement.
        parts = [self.part("out", "5v")]
        lines = "\n".join(emit_board.mcu_power_lines(self.BOARD, parts, {}, set()))
        self.assertIn('from=".Mcu > .VCC" to="net.V5V"', lines)
        self.assertIn(("Mcu", "VCC", "V5V"), emit_board.supply_inputs(self.BOARD, parts))

    def test_a_grounds_direction_is_never_asked_about(self):
        # A connector declares its GND as `out` and a module declares its GND as `in`; neither is
        # a rail anybody drives, and making ground conditional would unwire every board.
        board = {"power_pads": {"GND1": {"rail": "ground", "direction": "in"}}}
        self.assertEqual([on for _, _, on in emit_board.mcu_power_nets(board, [])], [True])
        self.assertEqual(emit_board.supply_inputs(board, []), [])


class TheBuiltBoardLandsWhereTheChecksLookTest(unittest.TestCase):
    """
    P51. The chain built in a temp directory and deleted it, so after the one documented command a
    stranger's project held only `requirements.json` and `check_all --project .` answered "not
    asked for" — the word **checked** was unreachable from the documented path. `--keep` printed
    the temp path instead, which is not a place anyone looks, and was documented nowhere.
    """

    def workdir(self):
        work = Path(tempfile.mkdtemp())
        (work / "board.tsx").write_text("// the board")
        (work / "FireBeetle2Esp32S3.tsx").write_text("// the footprint")
        (work / "dist" / "board").mkdir(parents=True)
        (work / "dist" / "board" / "circuit.json").write_text("[]")
        return work

    def test_the_board_its_footprint_and_dist_all_arrive(self):
        into = Path(tempfile.mkdtemp()) / "project"
        said = check_spine.keep_into(self.workdir(), into)
        self.assertTrue((into / "board.tsx").is_file())
        self.assertTrue((into / "FireBeetle2Esp32S3.tsx").is_file())
        # dist is the one that matters: it is what design.CIRCUIT_PATHS names.
        self.assertTrue((into / "dist" / "board" / "circuit.json").is_file())
        self.assertTrue(any("every check reads" in line for line in said))

    def test_a_destination_that_does_not_exist_yet_is_made(self):
        into = Path(tempfile.mkdtemp()) / "not" / "there"
        check_spine.keep_into(self.workdir(), into)
        self.assertTrue((into / "board.tsx").is_file())

    def test_a_board_someone_has_edited_is_left_alone_and_said(self):
        # `board.tsx` is the thing a person edits — the smart bin's is hand-maintained. Silently
        # overwriting it is how a tool loses somebody's afternoon.
        into = Path(tempfile.mkdtemp())
        (into / "board.tsx").write_text("// MINE, hand-edited")
        said = check_spine.keep_into(self.workdir(), into)
        self.assertEqual((into / "board.tsx").read_text(), "// MINE, hand-edited")
        self.assertTrue(any("left alone" in line and "board.tsx" in line for line in said),
                        "an untouched file must be named, not silently skipped: %s" % said)

    def test_dist_is_replaced_because_it_is_pure_output(self):
        into = Path(tempfile.mkdtemp())
        (into / "dist" / "board").mkdir(parents=True)
        (into / "dist" / "board" / "circuit.json").write_text("stale")
        check_spine.keep_into(self.workdir(), into)
        self.assertEqual((into / "dist" / "board" / "circuit.json").read_text(), "[]")

    def test_report_actually_calls_it_and_still_clears_the_temp_directory(self):
        # The helper was tested and its one caller was not — R2.2's shape, and a mutation putting
        # `report` back to printing a /var/folders path escaped a green suite because of it.
        import argparse, contextlib, io
        work = self.workdir()
        into = Path(tempfile.mkdtemp()) / "project"
        args = argparse.Namespace(json=False, keep=into)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as err:
            check_spine.report([check_spine.Stage("build", check_spine.OK, "fine")], args, work)
        self.assertTrue((into / "dist" / "board" / "circuit.json").is_file(),
                        "report did not put the board where the checks look")
        self.assertFalse(work.exists(), "the temp directory is still cleared away")
        self.assertIn("every check reads", err.getvalue())

    def test_without_it_the_temp_directory_is_still_removed(self):
        import argparse, contextlib, io
        work = self.workdir()
        args = argparse.Namespace(json=False, keep=None)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            check_spine.report([check_spine.Stage("build", check_spine.OK, "fine")], args, work)
        self.assertFalse(work.exists())

    def test_the_documented_one_command_leaves_the_board_behind(self):
        # The document is the product: a stranger runs what build.md prints, and without `--keep`
        # their project holds only requirements.json after a perfect build (P51).
        import re
        text = (ROOT / "commands" / "build.md").read_text()
        heading = text.index("## The one command")
        block = re.search(r"```\n(.*?)```", text[heading:], re.S).group(1)
        self.assertIn("check_spine.py", block)
        self.assertIn("--keep", block,
                      "the one command builds in a temp directory and deletes it: %r" % block)

    def test_it_is_a_directory_now_not_a_flag(self):
        # W16: the old `--keep` printed a /var/folders path. One behaviour replaced the other.
        import argparse, contextlib, io
        out = io.StringIO()
        with contextlib.redirect_stderr(out), self.assertRaises(SystemExit):
            check_spine.main(["--keep"])
        self.assertIn("expected one argument", out.getvalue())


class FindingTheToolchainTest(unittest.TestCase):
    def test_a_projects_own_tsci_is_preferred_over_the_global_one(self):
        # A project pins a version for a reason; silently building with a different one produces
        # a netlist that does not match what the project's own commands produce.
        import tempfile
        root = Path(tempfile.mkdtemp())
        binary = root / "node_modules" / ".bin" / "tsci"
        binary.parent.mkdir(parents=True)
        binary.write_text("#!/bin/sh\n")
        deep = root / "a" / "b"
        deep.mkdir(parents=True)
        self.assertEqual(check_spine.find_toolchain(deep), binary)

    def test_no_toolchain_anywhere_is_none_not_a_guess(self):
        # PATH has to be emptied: this machine has a global tsci, so without it the test passes
        # or fails on what happens to be installed rather than on the function.
        import os
        import tempfile
        original = os.environ.get("PATH", "")
        os.environ["PATH"] = ""
        try:
            self.assertIsNone(check_spine.find_toolchain(Path(tempfile.mkdtemp())))
        finally:
            os.environ["PATH"] = original


class ReachingSimulationTest(unittest.TestCase):
    """
    The last step of the product goal, and the one the chain used to stop short of.

    A board that builds is not the goal — `idea -> parts -> schema -> simulation` is, in Petr's
    words. A spine that ended at `build` and called itself complete was measuring four fifths of
    the thing and reporting five.
    """

    def test_a_diagram_with_connections_is_counted(self):
        self.assertEqual(check_spine.wires_in({"connections": [["a", "b"], ["c", "d"]]}), 2)

    def test_a_diagram_with_no_connections_counts_zero(self):
        # The same failure shape as a board with no copper: every part placed, nothing joined.
        # It is what an unmapped component looks like once the converter has given up on it.
        self.assertEqual(check_spine.wires_in({"parts": [{"id": "mcu"}], "connections": []}), 0)

    def test_a_diagram_missing_the_key_entirely_counts_zero_rather_than_raising(self):
        self.assertEqual(check_spine.wires_in({}), 0)

    def test_the_converter_is_found_from_a_directory_below_it(self):
        import tempfile
        root = Path(tempfile.mkdtemp())
        converter = root / "tools" / "circuit-to-wokwi" / "cli.ts"
        converter.parent.mkdir(parents=True)
        converter.write_text("// stand-in\n")
        deep = root / "a" / "b"
        deep.mkdir(parents=True)
        # Both sides resolved: on macOS /var is a symlink to /private/var, so the finder's own
        # `.resolve()` — which is right, it normalises what it returns — would otherwise make
        # this fail on a path difference that is not one.
        self.assertEqual(check_spine.find_converter(deep), converter.resolve())

    def test_a_directory_with_nothing_beside_it_gets_the_plugins_own(self):
        # THE CONTRACT CHANGED WITH P32a, and again with P82: a project with no converter of its own
        # gets the plugin's — now the bundle the tools list names, run on Node, never the plugin's
        # TypeScript source (which needs node_modules an installed plugin lacks).
        import tempfile
        import tools
        self.assertIsNone(check_spine.find_converter(Path(tempfile.mkdtemp())))
        with mock.patch.object(tools, "PERSONAL", Path(tempfile.mkdtemp()) / "absent.json"):
            command = check_spine.converter_command(None, None)
        self.assertTrue(command[-1].endswith("dist/converter.mjs"), command)

    def test_the_plugins_converter_is_really_there(self):
        # The fallback is only worth having if it resolves. If this file ever moves, the stage
        # goes quietly back to could-not-run for every project that has no converter of its own.
        bundle = ROOT / "tools" / "circuit-to-wokwi" / "dist" / "converter.mjs"
        self.assertTrue(bundle.is_file(), "%s is gone, so no project without its own converter can simulate" % bundle)

    def test_a_project_with_its_own_converter_still_wins(self):
        # A project may carry a modified one; the plugin's is the fallback, not an override.
        import tempfile
        root = Path(tempfile.mkdtemp())
        mine = root / "tools" / "circuit-to-wokwi"
        mine.mkdir(parents=True)
        (mine / "cli.ts").write_text("// mine\n")
        self.assertEqual(check_spine.find_converter(root), (mine / "cli.ts").resolve())

    def test_no_converter_at_all_is_could_not_run_not_a_guess(self):
        from unittest import mock
        import tempfile
        import tools
        with mock.patch.object(tools, "PLUGIN", Path("/nowhere")):
            stage = check_spine.converter_stage_problem(Path(tempfile.mkdtemp()))
        self.assertEqual(stage.status, check_spine.COULD_NOT_RUN)
        self.assertIn("circuit-to-wokwi", stage.detail)

    def test_the_stage_appears_in_the_rendering(self):
        # If the banner still stops at `build`, a reader is told the chain is shorter than it is.
        rendered = check_spine.render([stage("build", check_spine.OK)], check_spine.EXIT_OK)
        self.assertIn("simulation", rendered)


class TheReferenceDesignTest(unittest.TestCase):
    def test_it_names_only_parts_the_library_actually_has(self):
        # If it drifts, the gate fails for a reason that has nothing to do with the chain, and
        # somebody switches it off.
        import parts
        available = set(parts.available())
        for part_id in check_spine.REFERENCE["parts"]:
            with self.subTest(part=part_id):
                self.assertIn(part_id, available)

    def test_it_includes_something_that_sources_a_rail(self):
        # Without it the design has a net with one member, the autorouter skips routing, and the
        # gate's own reference design demonstrates the defect the gate exists to catch.
        import parts
        sources = [part_id for part_id in check_spine.REFERENCE["parts"]
                   if any(supply.get("direction") == "out"
                          for supply in parts.load(part_id).get("power") or [])]
        self.assertTrue(sources, "no part in the reference design supplies a rail")



class TheInputIsReadBeforeAnythingRunsTest(unittest.TestCase):
    """
    Two of the audit's claims (A8, A10) in one place: the requirements file was read outside any
    `try`, so malformed JSON was a traceback and exit 1 — "the chain is broken" — and the project
    was resolved from the current directory, so from anywhere else the spine could not find a
    part sitting beside the file.
    """

    @staticmethod
    def _main(argv, cwd):
        out = io.StringIO()
        was = os.getcwd()
        os.chdir(cwd)
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                code = check_spine.main(argv)
        finally:
            os.chdir(was)
        return code, out.getvalue()

    def test_malformed_requirements_are_could_not_run_not_a_traceback(self):
        path = Path(tempfile.mkdtemp()) / "bad.json"
        path.write_text("{not json")
        code, out = self._main([str(path)], tempfile.mkdtemp())
        self.assertEqual(code, check_spine.EXIT_COULD_NOT_RUN)
        self.assertIn("NOT exercised", out)
        self.assertIn("not JSON", out)

    def test_the_project_is_the_files_not_the_current_directory(self):
        # A project with a part of its own, run from elsewhere. The schematic stage has to find
        # the part; the build stage is could-not-run because no toolchain is offered, which is
        # what keeps this test off tsci and under a second.
        root = Path(tempfile.mkdtemp())
        (root / ".spark").mkdir()
        (root / "parts").mkdir()
        (root / "parts" / "probe.json").write_text(json.dumps(
            {"schema": 1, "id": "probe", "name": "probe", "kind": "connector", "needs": [],
             "power": [{"pin": "VCC", "rail": "logic", "direction": "in"},
                       {"pin": "GND", "rail": "ground", "direction": "in"}],
             "pin_order": ["VCC", "GND"], "pin_order_proof": {"verified": False, "source": "a test fixture"}, "footprint": "jst_ph_2",
             "body_mm": {"width": 5, "height": 5, "verified": True, "source": "t"}}))
        path = root / "car.requirements.json"
        path.write_text(json.dumps({"board": "firebeetle2-esp32s3", "parts": ["probe"]}))
        with mock.patch.object(check_spine, "find_toolchain", return_value=None):
            code, out = self._main([str(path)], tempfile.mkdtemp())
        self.assertNotIn("no part called", out)
        self.assertIn("[ok  ] schematic", out)
        self.assertIn("[????] build", out)
        self.assertEqual(code, check_spine.EXIT_COULD_NOT_RUN)


def fake_tsci(root, builds_when):
    """
    A `tsci` that answers `--version` and builds — writes a circuit.json — only when
    `builds_when` (a shell test on the working directory) holds. Instant, so the build stage can
    be driven without tscircuit installed.
    """
    binary = root / "fake-tsci"
    binary.write_text("#!/bin/sh\n"
                      "[ \"$1\" = \"--version\" ] && { echo 0.0.0-fake; exit 0; }\n"
                      "if %s; then mkdir -p dist/board; echo '[]' > dist/board/circuit.json; exit 0; fi\n"
                      "echo \"Cannot find package 'react'\" >&2\n"
                      "exit 1\n" % builds_when)
    binary.chmod(0o755)
    return binary


class OnlyAProjectsOwnModulesAreLinkedTest(unittest.TestCase):
    """
    Audit A9, at its cause. The spine linked `toolchain.parent.parent` into the working
    directory as `node_modules`. For a project-local tsci that IS the node_modules; for a global
    one it is the Node prefix, and a `node_modules` with no `react` in it broke a toolchain that
    built the same board on its own. The spine then called that "the chain is broken".
    """

    def test_a_project_local_tsci_names_its_node_modules(self):
        root = Path(tempfile.mkdtemp())
        binary = root / "node_modules" / ".bin" / "tsci"
        binary.parent.mkdir(parents=True)
        binary.write_text("#!/bin/sh\n")
        self.assertEqual(check_spine.modules_for(binary), root / "node_modules")

    def test_a_global_tsci_links_nothing(self):
        # ~/.nvm/versions/node/v18/bin/tsci: its parent.parent is the prefix, not a node_modules.
        prefix = Path(tempfile.mkdtemp())
        binary = prefix / "bin" / "tsci"
        binary.parent.mkdir(parents=True)
        binary.write_text("#!/bin/sh\n")
        self.assertIsNone(check_spine.modules_for(binary))


class AToolchainFaultIsNotADesignFaultTest(unittest.TestCase):
    """
    The build stage's three outcomes, driven with a fake tsci so no tscircuit is needed.

    A tool that cannot build a resistor on a board is not reporting on the design. Calling that
    "the chain is broken" is W1's mirror image — a check that could not look, reading as a check
    that failed — and it sends somebody to debug a design nobody examined.
    """

    def _build_stage(self, builds_when):
        root = Path(tempfile.mkdtemp())
        workdir = root / "work"
        workdir.mkdir()
        binary = fake_tsci(root, builds_when)
        # `main` writes the requirements into the working directory before `run`; this drives
        # `run` directly, so it does the same.
        (workdir / "requirements.json").write_text(json.dumps(check_spine.REFERENCE))
        stages = check_spine.run(dict(check_spine.REFERENCE), workdir, toolchain=binary)
        build = next((stage for stage in stages if stage.name == "build"), None)
        if build is None:
            self.fail("the chain stopped before the build stage: %s" % stages)
        return build, binary, stages

    def test_a_tool_that_builds_nothing_at_all_is_could_not_run_and_named(self):
        build, binary, stages = self._build_stage("false")
        self.assertEqual(build.status, check_spine.COULD_NOT_RUN, build.detail)
        self.assertIn(str(binary), build.detail)
        self.assertIn("0.0.0-fake", build.detail)
        self.assertIn("toolchain, not the design", build.detail)
        self.assertIn("Cannot find package", build.detail)
        self.assertEqual(check_spine.verdict(stages), check_spine.EXIT_COULD_NOT_RUN)

    def test_a_tool_that_builds_a_trivial_board_but_not_this_one_is_a_problem(self):
        # The control: same failure on the design, but the preflight passes, so the design is
        # what is broken — and the verdict says the tool was checked.
        build, binary, stages = self._build_stage('[ "$(basename "$PWD")" = "spark-probe" ]')
        self.assertEqual(build.status, check_spine.PROBLEMS, build.detail)
        self.assertIn("no circuit.json was produced", build.detail)
        self.assertIn("does build a trivial board", build.detail)
        self.assertEqual(check_spine.verdict(stages), check_spine.EXIT_PROBLEMS)

    def test_the_preflight_reports_what_the_tool_said(self):
        root = Path(tempfile.mkdtemp())
        can, words = check_spine.toolchain_can_build(fake_tsci(root, "false"), root)
        self.assertFalse(can)
        self.assertIn("react", words)
        can, _ = check_spine.toolchain_can_build(fake_tsci(root, "true"), root)
        self.assertTrue(can)

    def test_the_version_is_asked_of_the_tool_and_never_raises(self):
        root = Path(tempfile.mkdtemp())
        self.assertEqual(check_spine.tsci_version(fake_tsci(root, "true")), "0.0.0-fake")
        self.assertEqual(check_spine.tsci_version(root / "no-such-tsci"), "unknown version")


class NothingToBuildIsNotAPassTest(unittest.TestCase):
    def test_an_empty_parts_list_is_could_not_run_before_anything_is_emitted(self):
        # Ran end to end as `ok` with two traces — the MCU's own rails — and two wires. A chain
        # proven on nothing has not been proven. (Intake M3, reproduced 2026-09-29.)
        workdir = Path(tempfile.mkdtemp())
        requirements = {"board": "firebeetle2-esp32s3", "parts": []}
        (workdir / "requirements.json").write_text(json.dumps(requirements))
        stages = check_spine.run(requirements, workdir, toolchain=Path("/nonexistent/tsci"))
        self.assertEqual([s.name for s in stages], ["board", "parts"])
        self.assertEqual(stages[-1].status, check_spine.COULD_NOT_RUN)
        self.assertIn("nothing to build", stages[-1].detail)
        self.assertEqual(check_spine.verdict(stages), check_spine.EXIT_COULD_NOT_RUN)


class AnEmitBoardCrashIsNotADesignFaultTest(unittest.TestCase):
    def test_a_crash_of_the_generator_is_could_not_run_with_its_last_words(self):
        # F5: emit_board exits 0 or 2 on purpose, so any other exit is a crash — and it read as `[!!  ] schematic`, problems,
        # "the chain is broken", for a design nobody had examined. A real one here: a Python that raises, in its place.
        import subprocess
        real_run = subprocess.run
        for crash, said in (("raise ValueError('a fault of its own')", "emit_board.py crashed: ValueError: a fault of its own"),
                            ("import sys; sys.exit(3)", "emit_board.py crashed: exit 3, and nothing said")):
            with self.subTest(crash=crash):
                workdir = Path(tempfile.mkdtemp())
                requirements = dict(check_spine.REFERENCE)
                (workdir / "requirements.json").write_text(json.dumps(requirements))

                def emit_board_crashes(command, *args, **kwargs):
                    if any(str(word).endswith("emit_board.py") for word in command):
                        command = [sys.executable, "-c", crash]
                    return real_run(command, *args, **kwargs)

                with mock.patch.object(subprocess, "run", side_effect=emit_board_crashes):
                    stages = check_spine.run(requirements, workdir, from_library=True)
                self.assertEqual((stages[-1].name, stages[-1].status, stages[-1].detail), ("schematic", check_spine.COULD_NOT_RUN, said))
                self.assertEqual(check_spine.verdict(stages), check_spine.EXIT_COULD_NOT_RUN)

    def test_a_refusal_of_the_generator_is_could_not_run_in_its_own_words(self):
        # the control: exit 2 is emit_board refusing the input, and its sentence is the stage's detail, whole
        workdir = Path(tempfile.mkdtemp())
        requirements = {"board": "xiao-esp32-c6", "parts": ["led-red-5mm"]}
        (workdir / "requirements.json").write_text(json.dumps(requirements))
        stages = check_spine.run(requirements, workdir, from_library=True)
        self.assertEqual((stages[-1].name, stages[-1].status), ("schematic", check_spine.COULD_NOT_RUN))
        self.assertTrue(stages[-1].detail.startswith("cannot emit a board: led-red-5mm asks for 5 mA"), stages[-1].detail)


class AConverterLimitIsNotADesignFaultTest(unittest.TestCase):
    def test_a_component_the_converter_cannot_map_is_could_not_look(self):
        # The RC car builds (13 traces) and the converter has no Wokwi part for its servo, buck
        # and inlet; that read as `!! simulation … the chain is broken` (audit B11).
        said = ("3 problem(s) converting the board:\n  - no Wokwi part is mapped to this component. "
                "Add it to lib/mapping.ts, or add a skip rule (component Sg90Servo)")
        self.assertTrue(check_spine.simulation_could_not_look(said))

    def test_any_other_converter_failure_is_still_a_problem(self):
        self.assertFalse(check_spine.simulation_could_not_look("TypeError: cannot read x of undefined"))
        self.assertFalse(check_spine.simulation_could_not_look(""))
        self.assertFalse(check_spine.simulation_could_not_look(None))


class AFileInNoProjectIsSaidToBeTest(unittest.TestCase):
    def test_the_board_stage_says_the_design_came_from_the_library(self):
        # P22: from nowhere the spine builds from the plugin's library; that is a fact about how
        # the design was resolved, said on the board stage — never a `!!` note about the design.
        # The reference design, which sources its own rails: a driver alone would earn a real
        # `!!` note about an unsourced motor rail, which is the design's and not this test's.
        workdir = Path(tempfile.mkdtemp())
        requirements = dict(check_spine.REFERENCE)
        (workdir / "requirements.json").write_text(json.dumps(requirements))
        with mock.patch.object(check_spine, "find_toolchain", return_value=None):
            stages = check_spine.run(requirements, workdir, from_library=True)
        self.assertIn("plugin's library", stages[0].detail)
        self.assertEqual(stages[0].status, check_spine.OK)
        self.assertNotIn("schematic-notes", [s.name for s in stages])


class AMissingBoardEngineSaysWhatTheToolsListSaysTest(unittest.TestCase):
    """The cold run (P82 task 7): with bun missing the build said "npm i -g @tscircuit/cli" — a global
    install the tools list does not ask for, and not the thing that was missing."""

    def test_the_build_stage_carries_the_tools_list_s_sentence(self):
        import tools
        workdir = Path(tempfile.mkdtemp())
        requirements = dict(check_spine.REFERENCE)
        (workdir / "requirements.json").write_text(json.dumps(requirements))
        said = "tscircuit needs bun: bun (bun) is not installed — install: npm install -g bun"
        with mock.patch.object(check_spine, "find_toolchain", return_value=None), \
                mock.patch.object(tools, "find", side_effect=tools.ToolProblem(said)):
            stages = check_spine.run(requirements, workdir, from_library=True)
        build = [stage for stage in stages if stage.name == "build"][0]
        self.assertEqual(build.status, check_spine.COULD_NOT_RUN)
        self.assertIn("npm install -g bun", build.detail)
        self.assertNotIn("npm i -g", build.detail)

class TheFinalReviewAtTheEntryPointsTest(unittest.TestCase):
    """The whole-branch review (2026-10-03): the expectations held in tools.find and broke at the real entry points."""

    def broken_home(self):
        home = Path(tempfile.mkdtemp())
        (home / ".local" / "share" / "spark").mkdir(parents=True)
        (home / ".local" / "share" / "spark" / "tools.json").write_text('{"tscircuit": {"core": "0.0.1",}}')
        return home

    def test_a_broken_personal_file_is_named_by_the_build_stage(self):
        import tools
        workdir = Path(tempfile.mkdtemp())
        requirements = dict(check_spine.REFERENCE)
        (workdir / "requirements.json").write_text(json.dumps(requirements))
        with mock.patch.object(tools, "PERSONAL", self.broken_home() / ".local" / "share" / "spark" / "tools.json"):
            stages = check_spine.run(requirements, workdir, from_library=True)
        build = [stage for stage in stages if stage.name == "build"][0]
        self.assertEqual(build.status, check_spine.COULD_NOT_RUN)
        self.assertIn("is not JSON", build.detail)

    def test_a_broken_project_file_is_named_not_reported_as_a_missing_engine(self):
        project = Path(tempfile.mkdtemp())
        (project / ".spark").mkdir()
        (project / ".spark" / "tools.json").write_text('{"tscircuit": {"core": "0.0.1",}}')
        workdir = Path(tempfile.mkdtemp())
        requirements = dict(check_spine.REFERENCE)
        (workdir / "requirements.json").write_text(json.dumps(requirements))
        with mock.patch.object(check_spine, "find_toolchain", return_value=None):
            stages = check_spine.run(requirements, workdir, project=project, from_library=True)
        build = [stage for stage in stages if stage.name == "build"][0]
        self.assertIn(".spark/tools.json is not JSON", build.detail)

    def test_the_commands_start_with_a_broken_personal_file_and_say_so(self):
        import subprocess
        env = {key: value for key, value in os.environ.items() if key not in ("SPARK_HOME", "XDG_DATA_HOME")}
        env["HOME"] = str(self.broken_home())
        helped = subprocess.run([sys.executable, str(ROOT / "scripts" / "check_spine.py"), "--help"],
                                capture_output=True, text=True, env=env, timeout=60)
        self.assertEqual(helped.returncode, 0, helped.stderr[-600:])
        project = Path(tempfile.mkdtemp())
        init = subprocess.run([sys.executable, str(ROOT / "scripts" / "init_project.py"), "--project", str(project),
                               "--board", "firebeetle2-esp32s3"], capture_output=True, text=True, env=env, timeout=60)
        self.assertEqual(init.returncode, check_spine.EXIT_COULD_NOT_RUN, init.stderr[-600:])
        self.assertIn("is not JSON", init.stderr)
        self.assertNotIn("Traceback", init.stderr)

    def test_the_plugin_s_own_converter_source_is_never_what_runs(self):
        # A requirements file in no project resolves to the plugin, whose cli.ts needs node_modules an
        # installed plugin does not have; the bundle is what ships (B10).
        self.assertIsNone(check_spine.find_converter(ROOT / "scripts"))
        self.assertIsNone(check_spine.find_converter(ROOT))

    def test_a_project_s_own_converter_runs_with_the_ts_runtime_from_the_list(self):
        import tools
        own = Path(tempfile.mkdtemp()) / "cli.ts"
        bun = tools.Tool("bun", "ts-runtime", {"kind": "path"}, ["/opt/bun"])
        with mock.patch.object(tools, "find", return_value=bun) as asked:
            self.assertEqual(check_spine.converter_command(None, own), ["/opt/bun", "run", str(own)])
        self.assertEqual(asked.call_args[0][0], "ts-runtime")

    def test_the_converter_the_list_names_is_the_one_that_runs(self):
        import tools
        swapped = tools.Tool("my-conv", "diagram-converter", {"kind": "path"}, ["/opt/my-conv"])
        node = tools.Tool("node", "js-runtime", {"kind": "path"}, ["/opt/node"])
        bundled = tools.Tool("circuit-to-wokwi", "diagram-converter", {"kind": "bundled"}, ["/plugin/converter.mjs"])
        with mock.patch.object(tools, "find", side_effect=lambda role, *rest: swapped if role == "diagram-converter" else node):
            self.assertEqual(check_spine.converter_command(None, None), ["/opt/my-conv"])
        with mock.patch.object(tools, "find", side_effect=lambda role, *rest: bundled if role == "diagram-converter" else node):
            self.assertEqual(check_spine.converter_command(None, None), ["/opt/node", "/plugin/converter.mjs"])

class TheConverterShipsAsOneFileTest(unittest.TestCase):
    """B10 / P82: an installed spark has no node_modules in tools/circuit-to-wokwi, so the converter ships built."""

    BUNDLE = ROOT / "tools" / "circuit-to-wokwi" / "dist" / "converter.mjs"

    def test_the_bundle_is_built_from_the_sources_as_they_are(self):
        import hashlib
        folder = ROOT / "tools" / "circuit-to-wokwi"
        sources = [folder / "cli.ts"] + sorted((folder / "lib").rglob("*.ts"))
        digest = hashlib.sha256(b"".join(path.read_bytes() for path in sources)).hexdigest()
        self.assertEqual((folder / "dist" / "converter.sources.sha256").read_text().strip(), digest,
                         "the converter changed and the bundle was not rebuilt: sh tools/circuit-to-wokwi/bundle.sh")

    def test_the_bundle_runs_on_node_with_no_node_modules(self):
        import shutil, subprocess
        if not shutil.which("node"):
            self.skipTest("node is not installed")
        alone = Path(tempfile.mkdtemp()) / "converter.mjs"
        shutil.copy(self.BUNDLE, alone)
        done = subprocess.run(["node", str(alone)], capture_output=True, text=True, timeout=60)
        said = done.stdout + done.stderr
        self.assertNotIn("Cannot find package", said)
        self.assertIn("SPARK_BOARD_JSON is not set", said, "it loaded every module and reached its own first check")

    def test_no_node_means_could_not_run_naming_the_install(self):
        import tools
        with mock.patch.object(tools, "find", side_effect=tools.ToolProblem("js-runtime (node) is not installed — install: brew install node")):
            stage = check_spine.converter_stage_problem(Path(tempfile.mkdtemp()))
        self.assertEqual(stage.status, check_spine.COULD_NOT_RUN)
        self.assertIn("brew install node", stage.detail)

    def test_the_converter_present_and_node_missing_is_could_not_run(self):
        import tools
        real = tools.find

        def no_node(name, *rest):
            if name == "js-runtime":
                raise tools.ToolProblem("js-runtime (node) is not installed — install: brew install node")
            return real(name, *rest)
        with mock.patch.object(tools, "find", side_effect=no_node):
            stage = check_spine.converter_stage_problem(Path(tempfile.mkdtemp()))
        self.assertIsNotNone(stage, "the bundle is here and Node is not: the converter cannot run")
        self.assertIn("brew install node", stage.detail)

    def test_the_plugin_s_converter_is_the_bundle(self):
        import tools
        self.assertEqual(tools.find("diagram-converter", None, Path(tempfile.mkdtemp()) / "absent.json").command,
                         [str(self.BUNDLE)])


class ABuildThatRunsEndToEndIsRecordedTest(unittest.TestCase):
    """P97 (§5.7, §8 T): when the chain runs end to end for a project on the person's list, the history says it was built."""

    def setUp(self):
        self.home, self.project = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp()) / "plant-alarm"
        (self.project / ".spark").mkdir(parents=True)
        (self.project / "requirements.json").write_text(json.dumps({"board": "firebeetle2-esp32s3", "parts": ["tactile-button"]}))
        (self.home / "projects.json").write_text(json.dumps({"plant-alarm": str(self.project.resolve())}))
        patcher = mock.patch.dict(os.environ, {"SPARK_HOME": str(self.home)})
        patcher.start()
        self.addCleanup(patcher.stop)

    def spine(self, last):
        stages = [stage(name, check_spine.OK) for name in ("board", "schematic", "footprint", "build")] + [stage("simulation", last)]
        with mock.patch.object(check_spine, "run", return_value=stages), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            check_spine.main([str(self.project / "requirements.json")])
        path = self.home / "history.jsonl"
        return [json.loads(line) for line in path.read_text().splitlines()] if path.is_file() else []

    def answer(self, argv=None):
        """What `check_spine.main` returned and said, stdout then stderr, for a chain whose every stage ended ok."""
        stages = [stage(name, check_spine.OK) for name in ("board", "schematic", "footprint", "build", "simulation")]
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(check_spine, "run", return_value=stages), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = check_spine.main([str(self.project / "requirements.json")] if argv is None else argv)
        return code, out.getvalue(), err.getvalue()

    def meanwhile(self, happens):
        """The history after `check_spine.main` on the person's file, whose chain ends ok and, while it builds, has `happens()` happen."""
        stages = [stage(name, check_spine.OK) for name in ("board", "schematic", "footprint", "build", "simulation")]

        def build(*_, **__):
            happens()
            return stages
        with mock.patch.object(check_spine, "run", side_effect=build), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            check_spine.main([str(self.project / "requirements.json")])
        path = self.home / "history.jsonl"
        return [json.loads(line) for line in path.read_text().splitlines()] if path.is_file() else []

    @staticmethod
    def digest_of(record, facts):
        """The sha256 of the facts of a record, written out here as the history means it (§5.7) rather than asked of parts.py."""
        shown = {key: record[key] for key in facts if key in record}
        return hashlib.sha256(json.dumps(shown, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    def test_a_chain_that_runs_end_to_end_is_recorded_once_with_each_digest(self):
        self.spine(check_spine.OK)
        built = self.spine(check_spine.OK)
        self.assertEqual([(e["event"], e["project"], e["board"]["id"], [p["id"] for p in e["parts"]]) for e in built],
                         [("built", "plant-alarm", "firebeetle2-esp32s3", ["tactile-button"])])
        self.assertEqual((len(built[0]["board"]["digest"]), len(built[0]["parts"][0]["digest"])), (64, 64))

    def test_a_chain_that_did_not_run_end_to_end_records_nothing(self):
        self.assertEqual(self.spine(check_spine.COULD_NOT_RUN), [])

    def test_each_digest_is_of_the_facts_a_build_reads(self):
        board = json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())
        button = json.loads((ROOT / "parts" / "tactile-button.json").read_text())
        built = self.spine(check_spine.OK)[0]
        self.assertEqual((built["board"]["digest"], built["parts"][0]["digest"]),
                         (self.digest_of(board, ("pins", "power_pads", "physical")),
                          self.digest_of(button, ("needs", "power", "unused_pins", "pin_order", "footprint", "host_parts"))))

    def test_what_the_chain_was_handed_is_what_is_recorded_not_what_the_file_became_meanwhile(self):
        def the_person_edits_the_file():
            (self.project / "requirements.json").write_text(json.dumps({"board": "firebeetle2-esp32s3", "parts": ["l9110s-module"]}))
        built = self.meanwhile(the_person_edits_the_file)
        self.assertEqual([[p["id"] for p in e["parts"]] for e in built], [["tactile-button"]])

    def test_the_facts_recorded_are_those_the_chain_was_handed_not_those_a_record_became_meanwhile(self):
        def the_person_edits_a_record():
            record = json.loads((ROOT / "parts" / "tactile-button.json").read_text())
            record["host_parts"][0]["ohms"] = 4700
            (self.project / "parts").mkdir()
            (self.project / "parts" / "tactile-button.json").write_text(json.dumps(record))
        built = self.meanwhile(the_person_edits_a_record)
        button = json.loads((ROOT / "parts" / "tactile-button.json").read_text())
        self.assertEqual([e["parts"][0]["digest"] for e in built],
                         [self.digest_of(button, ("needs", "power", "unused_pins", "pin_order", "footprint", "host_parts"))])

    def test_a_design_that_cannot_be_loaded_records_nothing_and_breaks_nothing(self):
        (self.project / "requirements.json").write_text(json.dumps({"board": "firebeetle2-esp32s3", "parts": ["no-such-part"]}))
        code, said, _ = self.answer()
        self.assertEqual((code, "the chain runs end to end" in said, (self.home / "history.jsonl").exists()), (0, True, False))
        (self.project / "requirements.json").write_text(json.dumps({"board": "firebeetle2-esp32s3", "parts": ["tactile-button"]}))
        with mock.patch.object(check_spine.design, "load", side_effect=TypeError("a record of a shape nobody foresaw")):
            code, said, _ = self.answer()
        self.assertEqual((code, "the chain runs end to end" in said, (self.home / "history.jsonl").exists()), (0, True, False))

    def test_a_project_that_is_not_on_the_list_keeps_no_history(self):
        (self.home / "projects.json").write_text("{}")
        self.assertEqual(self.spine(check_spine.OK), [])

    def test_the_reference_design_has_no_project_and_records_nothing(self):
        # even when the person listed the plugin's own folder, which a design with no file is built from
        (self.home / "projects.json").write_text(json.dumps({"spark": str(ROOT)}))
        code, said, _ = self.answer(argv=[])
        self.assertEqual((code, "the chain runs end to end" in said, (self.home / "history.jsonl").exists()), (0, True, False))

    def test_a_design_built_from_the_plugin_s_library_is_recorded_for_no_project(self):
        # even when the person listed the plugin's own folder: a file in no project is built from it, and belongs to nobody
        alone = Path(tempfile.mkdtemp()) / "requirements.json"
        alone.write_text(json.dumps({"board": "firebeetle2-esp32s3", "parts": ["tactile-button"]}))
        (self.home / "projects.json").write_text(json.dumps({"spark": str(ROOT)}))
        code, _, _ = self.answer(argv=[str(alone)])
        self.assertEqual((code, (self.home / "history.jsonl").exists()), (0, False))

    def test_the_line_waits_while_another_holds_the_store(self):
        loaded = design.load(self.project / "requirements.json", self.project)
        recorder = threading.Thread(target=parts.note_built, args=(loaded,))
        with store.locked():
            recorder.start()
            time.sleep(0.5)
            self.assertFalse((self.home / "history.jsonl").exists(), "it wrote while another held the store")
        recorder.join(timeout=60)
        self.assertEqual(len((self.home / "history.jsonl").read_text().splitlines()), 1)

    def test_a_history_that_cannot_be_kept_does_not_hide_the_verdict(self):
        (self.home / "history.jsonl").write_text("this is not an event\n")
        code, said, complained = self.answer()
        self.assertEqual((code, "the chain runs end to end" in said), (0, True))
        self.assertIn("history.jsonl line 1 is not a history event", complained)

    def test_whatever_stops_the_recording_the_verdict_stands_and_the_reason_is_said(self):
        for refusal in (store.StoreProblem("the projects list is not JSON"), OSError("the disk is full")):
            with self.subTest(refusal=refusal), mock.patch.object(check_spine.parts, "note_built", side_effect=refusal):
                code, said, complained = self.answer()
                self.assertEqual((code, "the chain runs end to end" in said), (0, True))
                self.assertIn(str(refusal), complained)


class ALoadAcrossAPairNeedsNoGroundTest(unittest.TestCase):
    """
    C-3 (the council on PR #98): a speaker terminal sits across the amplifier's bridged output — its return is the pair's
    other side, and a ground on either pin would short the amplifier. It is asked what a two-terminal passive is asked, that
    neither end dangles, and not whether it reaches ground.
    """

    @staticmethod
    def circuit(*, both_ends=True):
        elements = [
            {"type": "source_net", "source_net_id": "n_gnd", "name": "GND"},
            {"type": "source_net", "source_net_id": "n_p", "name": "SPEAKER_P"},
            {"type": "source_net", "source_net_id": "n_n", "name": "SPEAKER_N"},
            {"type": "source_component", "source_component_id": "c_amp", "name": "Amp"},
            {"type": "source_component", "source_component_id": "c_spk", "name": "SpeakerTerminal"},
            {"type": "source_port", "source_port_id": "p_amp_gnd", "source_component_id": "c_amp", "name": "GND"},
            {"type": "source_port", "source_port_id": "p_amp_p", "source_component_id": "c_amp", "name": "SPK_P"},
            {"type": "source_port", "source_port_id": "p_amp_n", "source_component_id": "c_amp", "name": "SPK_N"},
            {"type": "source_port", "source_port_id": "p_spk_p", "source_component_id": "c_spk", "name": "SPK_P"},
            {"type": "source_port", "source_port_id": "p_spk_n", "source_component_id": "c_spk", "name": "SPK_N"},
            {"type": "source_trace", "source_trace_id": "t1", "connected_source_port_ids": ["p_amp_gnd"], "connected_source_net_ids": ["n_gnd"]},
            {"type": "source_trace", "source_trace_id": "t2", "connected_source_port_ids": ["p_amp_p", "p_spk_p"], "connected_source_net_ids": ["n_p"]},
            {"type": "source_trace", "source_trace_id": "t3", "connected_source_port_ids": ["p_amp_n"], "connected_source_net_ids": ["n_n"]}]
        if both_ends:
            elements.append({"type": "source_trace", "source_trace_id": "t4", "connected_source_port_ids": ["p_spk_n"],
                             "connected_source_net_ids": ["n_n"]})
        return elements

    def test_a_terminal_across_a_pair_is_asked_only_whether_an_end_dangles(self):
        self.assertEqual(check_spine.islands_in(self.circuit()), ["SpeakerTerminal reaches no ground"])
        self.assertEqual(check_spine.islands_in(self.circuit(), across=("SpeakerTerminal",)), [])
        self.assertEqual(check_spine.islands_in(self.circuit(both_ends=False), across=("SpeakerTerminal",)),
                         ["SpeakerTerminal.SPK_N (a terminal connected to nothing)"])

    def test_the_build_stage_hands_the_loads_across_a_pair_to_the_island_check(self):
        root = Path(tempfile.mkdtemp())
        workdir = root / "work"
        workdir.mkdir()
        requirements = {"board": "firebeetle2-esp32s3", "parts": ["max98357a-dfr0954", "speaker-terminal"]}
        (workdir / "requirements.json").write_text(json.dumps(requirements))
        with mock.patch.object(check_spine, "islands_in", return_value=[]) as islands:
            check_spine.run(requirements, workdir, toolchain=fake_tsci(root, "true"), from_library=True)
        self.assertEqual(islands.call_args.kwargs["across"], ["SpeakerTerminal"])


class TheVerdictSaysWhatIsNotOnTheBoardTest(unittest.TestCase):
    """C-2 (the PO, 2026-10-08): "the chain runs end to end" never stands alone over needs the requirements file left off the
    board — `--requirements` writes them into the file (`unserved`), and the closing line reads them from there."""

    UNSERVED = [{"need": "soil", "why": "no pick", "picks": []}, {"need": "smell", "why": "a gap", "picks": []},
                {"need": "battery", "why": "no record", "picks": ["lipo", "spare-lipo"]}]

    def answer(self, requirements, *flags):
        path = Path(tempfile.mkdtemp()) / "requirements.json"
        path.write_text(json.dumps(requirements))
        stages = [stage(name, check_spine.OK) for name in ("board", "schematic", "footprint", "build", "simulation")]
        out = io.StringIO()
        with mock.patch.object(check_spine, "run", return_value=stages), contextlib.redirect_stdout(out), \
                contextlib.redirect_stderr(io.StringIO()):
            code = check_spine.main([str(path)] + list(flags))
        return code, out.getvalue()

    def test_needs_the_file_leaves_off_the_board_are_said_on_the_verdict_s_line(self):
        code, said = self.answer({"board": "firebeetle2-esp32s3", "parts": ["tactile-button"], "unserved": self.UNSERVED})
        self.assertEqual(code, 0)
        self.assertTrue(said.endswith("  the chain runs end to end — but not every need is on the board: soil (no pick), smell (a gap), "
                                      "battery (no record: lipo, spare-lipo)\n"), said)

    def test_with_json_the_needs_left_off_are_part_of_the_answer(self):
        code, said = self.answer({"board": "firebeetle2-esp32s3", "parts": ["tactile-button"], "unserved": self.UNSERVED}, "--json")
        self.assertEqual((code, json.loads(said)["unserved"]), (0, self.UNSERVED))

    def test_a_file_that_leaves_nothing_off_says_the_verdict_alone(self):
        for requirements in ({"board": "firebeetle2-esp32s3", "parts": ["tactile-button"]},
                             {"board": "firebeetle2-esp32s3", "parts": ["tactile-button"], "unserved": []}):
            with self.subTest(requirements=requirements):
                code, said = self.answer(requirements)
                self.assertTrue(said.endswith("\n  the chain runs end to end\n"), said)
                self.assertNotIn("unserved", json.loads(self.answer(requirements, "--json")[1]))


if __name__ == "__main__":
    unittest.main()
