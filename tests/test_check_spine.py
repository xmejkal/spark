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

import argparse
import ast
import contextlib
import hashlib
import io
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from spark.design import pin_assigner  # noqa: E402
from spark.records import board_records  # noqa: E402
from spark.build import build_codes  # noqa: E402
import check_spine  # noqa: E402
from spark.build import board_engine  # noqa: E402
from spark.build import build_service  # noqa: E402
from spark.build import requirements_build  # noqa: E402
from spark.build import kept_files  # noqa: E402
from spark.build.stages import Stage  # noqa: E402
from suite_runs import slow  # noqa: E402
from spark.design import loader  # noqa: E402
from spark.design import board_emitter  # noqa: E402
from spark.design import board_sections  # noqa: E402
from spark.design import power_rails  # noqa: E402
import emit_footprint  # noqa: E402
from spark.records import missing_facts  # noqa: E402
import parts  # noqa: E402
from spark.sourcing import part_facts  # noqa: E402
from spark.records import store  # noqa: E402
from spark.breadboard import tabbed_page  # noqa: E402
import test_converter  # noqa: E402
from fakes import FakeBuildService, FakeToolFinder, FakeTscircuitEngine  # noqa: E402


def build_stages(requirements, workdir, toolchain=None, find_tool=None, **inputs):
    """The build as `main` runs it: the real engine over `toolchain` (None: found from the project) and the real emitter,
    with `find_tool` (a test's finder; None: the real one), on `BuildInputs(requirements, workdir, **inputs)`; the stages."""
    return build_service.BuildService.for_toolchain(toolchain, find_tool).build(build_service.BuildInputs(requirements, workdir, **inputs))
from fakes import FakeTscircuitExport, fake_tsci  # noqa: E402


def stage(name, status):
    return Stage(name, status)


class ABoardWithNoCopperIsNotBuiltTest(unittest.TestCase):
    def test_a_circuit_with_traces_and_no_errors_counts_as_built(self):
        traces, errors = build_service.count_in(
            [{"type": "pcb_trace"}, {"type": "pcb_trace"}, {"type": "source_component"}])
        self.assertEqual((traces, errors), (2, []))

    def test_traces_are_counted_not_assumed(self):
        # The whole gate rests on this number, so it is read from the netlist and nothing else.
        self.assertEqual(build_service.count_in([{"type": "source_component"}])[0], 0)

    def test_every_kind_of_error_element_is_found(self):
        # They do not share a prefix — pcb_port_not_connected_error, pcb_trace_missing_error,
        # source_*_error — so the match is on the word, not on a list somebody has to maintain.
        _, errors = build_service.count_in([
            {"type": "pcb_port_not_connected_error"},
            {"type": "pcb_trace_missing_error"},
            {"type": "pcb_trace"}])
        self.assertEqual(len(errors), 2)

    def test_a_warning_is_not_an_error(self):
        # `pcb_component_missing_courtyard_warning` and friends are present on a good board.
        # Counting them would make the gate unpassable, and an unpassable gate gets removed.
        _, errors = build_service.count_in([
            {"type": "pcb_component_missing_courtyard_warning"},
            {"type": "source_unnamed_trace_warning"}])
        self.assertEqual(errors, [])


class WhatTheExitCodeMeansTest(unittest.TestCase):
    """
    Three outcomes, never two. The distinction this project is built on is that a chain nobody
    could exercise has not passed, and the exit code is where that either survives or is lost.
    """

    def test_everything_ok_is_ok(self):
        self.assertEqual(build_service.verdict([stage("board", check_spine.OK),
                                              stage("build", check_spine.OK)]),
                         check_spine.EXIT_OK)

    def test_a_stage_that_could_not_run_is_not_a_pass(self):
        self.assertEqual(build_service.verdict([stage("board", check_spine.OK),
                                              stage("build", check_spine.COULD_NOT_RUN)]),
                         check_spine.EXIT_COULD_NOT_RUN)

    def test_a_real_problem_outranks_a_stage_that_could_not_run(self):
        # Both present: the thing that is known broken is the more urgent news.
        self.assertEqual(build_service.verdict([stage("schematic", check_spine.PROBLEMS),
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
            build_service.islands_in(self.circuit(ground_the_mcu=False)), ["Mcu reaches no ground"])

    def test_grounding_it_clears_the_finding(self):
        self.assertEqual(
            build_service.islands_in(self.circuit(ground_the_mcu=True)), [])

    def test_a_ground_under_another_name_still_counts(self):
        # A design with an analogue return calls it AGND, and "the net called GND" stops being
        # true. Naming them beats guessing from the netlist.
        circuit = self.circuit(ground_the_mcu=True)
        for element in circuit:
            if element.get("name") == "GND":
                element["name"] = "AGND"
        self.assertEqual(build_service.islands_in(circuit), [])

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
        self.assertEqual(build_service.islands_in(circuit), [])
        dangling = [e for e in circuit if e.get("source_trace_id") != "t5"]
        self.assertEqual(build_service.islands_in(dangling), ["SdaPullup.pin2 (a terminal connected to nothing)"])

    def test_a_component_in_no_trace_at_all_is_not_reported_here(self):
        # Already covered by the generators, which refuse to emit a part they cannot wire.
        # Reporting it twice, in different words, is how a finding gets scrolled past.
        circuit = self.circuit(ground_the_mcu=True) + [
            {"type": "source_component", "source_component_id": "c_lonely", "name": "Lonely"}]
        self.assertNotIn("Lonely", build_service.islands_in(circuit))


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
            build_service.islands_in(self.circuit(feed_the_mcu=False), [("Mcu", "VCC", "V5V")]),
            ["Mcu.VCC is fed by net.V5V in this design and is not on it"])

    def test_wiring_it_clears_the_finding(self):
        self.assertEqual(
            build_service.islands_in(self.circuit(feed_the_mcu=True), [("Mcu", "VCC", "V5V")]), [])

    def test_a_rail_the_build_never_created_is_named_too(self):
        # The failure mode that is easy to miss: the trace was asked for, tscircuit dropped it,
        # and the net does not exist at all. `net_named` returns None and that must not read as
        # "no claim to check".
        circuit = [e for e in self.circuit(feed_the_mcu=True) if e.get("name") != "V5V"]
        self.assertEqual(
            build_service.islands_in(circuit, [("Mcu", "VCC", "V5V")]),
            ["Mcu.VCC is fed by net.V5V in this design and is not on it"])

    def test_no_claims_asks_no_supply_question(self):
        # A button has no supply pin, and asking every component whether it reaches a rail is how
        # a check that fires on correct designs gets ignored. Only what a record states is asked.
        self.assertEqual(build_service.islands_in(self.circuit(feed_the_mcu=False)), [])


class WhichOfTheModulesOwnPadsGetWiredTest(unittest.TestCase):
    """P29's other half, in the generator: a pad that RECEIVES is conditional, one that drives is not."""

    BOARD = {"power_pads": {"GND1": {"rail": "ground", "direction": "out"},
                            "3V3": {"rail": "logic", "direction": "out"},
                            "VCC": {"rail": "5v", "direction": "in"}}}

    @staticmethod
    def part(direction, rail):
        return {"id": "psu", "name": "Psu", "power": [{"pin": "VOUT", "rail": rail, "direction": direction}]}

    def test_a_receiving_pad_is_left_open_when_nothing_drives_its_rail(self):
        wired = {pad: on for pad, _, on in power_rails.mcu_power_nets(self.BOARD, [])}
        self.assertEqual(wired, {"GND1": True, "3V3": True, "VCC": False})

    def test_a_supply_on_that_rail_wires_it(self):
        wired = dict((pad, on) for pad, _, on in
                     power_rails.mcu_power_nets(self.BOARD, [self.part("out", "5v")]))
        self.assertTrue(wired["VCC"])

    def test_another_consumer_of_the_rail_does_not_count_as_a_source(self):
        # Two sinks and no source is a rail nobody drives, which is the state this exists to
        # refuse to paper over.
        wired = dict((pad, on) for pad, _, on in
                     power_rails.mcu_power_nets(self.BOARD, [self.part("in", "5v")]))
        self.assertFalse(wired["VCC"])

    def test_the_generated_file_says_why_a_pad_was_left_open(self):
        # W1's shape: a connection that was reasoned about and one that was forgotten must not
        # look the same in the output.
        lines = "\n".join(board_sections.mcu_power_lines(self.BOARD, [], {}, set()))
        self.assertIn("Mcu.VCC receives net.V5V and NOTHING ON THIS BOARD DRIVES", lines)
        self.assertNotIn('from=".Mcu > .VCC"', lines)

    def test_the_claim_the_spine_checks_is_the_trace_the_generator_wrote(self):
        # One home: if these two could disagree the check would be worthless, and three defects
        # in this file's history are exactly that disagreement.
        parts = [self.part("out", "5v")]
        lines = "\n".join(board_sections.mcu_power_lines(self.BOARD, parts, {}, set()))
        self.assertIn('from=".Mcu > .VCC" to="net.V5V"', lines)
        self.assertIn(("Mcu", "VCC", "V5V"), power_rails.supply_inputs(self.BOARD, parts))

    def test_a_grounds_direction_is_never_asked_about(self):
        # A connector declares its GND as `out` and a module declares its GND as `in`; neither is
        # a rail anybody drives, and making ground conditional would unwire every board.
        board = {"power_pads": {"GND1": {"rail": "ground", "direction": "in"}}}
        self.assertEqual([on for _, _, on in power_rails.mcu_power_nets(board, [])], [True])
        self.assertEqual(power_rails.supply_inputs(board, []), [])


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
        said = [k["line"] for k in kept_files.kept_into(self.workdir(), into)]
        self.assertTrue((into / "board.tsx").is_file())
        self.assertTrue((into / "FireBeetle2Esp32S3.tsx").is_file())
        # dist is the one that matters: it is what design.CIRCUIT_PATHS names.
        self.assertTrue((into / "dist" / "board" / "circuit.json").is_file())
        self.assertTrue(any("every check reads" in line for line in said))

    def test_a_destination_that_does_not_exist_yet_is_made(self):
        into = Path(tempfile.mkdtemp()) / "not" / "there"
        kept_files.kept_into(self.workdir(), into)
        self.assertTrue((into / "board.tsx").is_file())

    def test_a_board_someone_has_edited_is_left_alone_and_said(self):
        # `board.tsx` is the thing a person edits — the smart bin's is hand-maintained. Silently
        # overwriting it is how a tool loses somebody's afternoon.
        into = Path(tempfile.mkdtemp())
        (into / "board.tsx").write_text("// MINE, hand-edited")
        said = [k["line"] for k in kept_files.kept_into(self.workdir(), into)]
        self.assertEqual((into / "board.tsx").read_text(), "// MINE, hand-edited")
        self.assertTrue(any("left alone" in line and "board.tsx" in line for line in said),
                        "an untouched file must be named, not silently skipped: %s" % said)

    def test_dist_is_replaced_because_it_is_pure_output(self):
        into = Path(tempfile.mkdtemp())
        (into / "dist" / "board").mkdir(parents=True)
        (into / "dist" / "board" / "circuit.json").write_text("stale")
        kept_files.kept_into(self.workdir(), into)
        self.assertEqual((into / "dist" / "board" / "circuit.json").read_text(), "[]")

    def test_report_actually_calls_it_and_still_clears_the_temp_directory(self):
        # The helper was tested and its one caller was not — R2.2's shape, and a mutation putting
        # `report` back to printing a /var/folders path escaped a green suite because of it.
        import argparse
        import contextlib
        import io
        work = self.workdir()
        into = Path(tempfile.mkdtemp()) / "project"
        args = argparse.Namespace(json=False, keep=into)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as err:
            check_spine.report([Stage("build", check_spine.OK, "fine")], args, work)
        self.assertTrue((into / "dist" / "board" / "circuit.json").is_file(),
                        "report did not put the board where the checks look")
        self.assertFalse(work.exists(), "the temp directory is still cleared away")
        self.assertIn("every check reads", err.getvalue())

    def test_keeping_a_project_s_build_writes_its_breadboard_sheet_beside_it(self):
        # P191 (#143): the parts and how to wire them, where /spark:build leaves the board.
        import argparse
        import contextlib
        import io
        import shutil
        fixture = Path(__file__).resolve().parent / "data" / "breadboard" / "button-light"
        work = self.workdir()
        shutil.copy(fixture / "dist" / "board" / "circuit.json", work / "dist" / "board" / "circuit.json")
        into = Path(tempfile.mkdtemp()) / "project"
        args = argparse.Namespace(json=False, keep=into, requirements=str(fixture / "requirements.json"))
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as err:
            check_spine.report([Stage("build", check_spine.OK, "fine")], args, work)
        self.assertIn("board D3", (into / "breadboard.md").read_text())
        self.assertIn("the parts and how to wire them on a breadboard", err.getvalue())

    def keep_a_build_of(self, fixture_name):
        """`report` keeping one breadboard fixture's built circuit into a new project folder: the folder, and stderr."""
        import argparse
        import contextlib
        import io
        import shutil
        fixture = Path(__file__).resolve().parent / "data" / "breadboard" / fixture_name
        work = self.workdir()
        shutil.copy(fixture / "dist" / "board" / "circuit.json", work / "dist" / "board" / "circuit.json")
        into = Path(tempfile.mkdtemp()) / "project"
        args = argparse.Namespace(json=False, keep=into, requirements=str(fixture / "requirements.json"))
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as err:
            check_spine.report([Stage("build", check_spine.OK, "fine")], args, work)
        return into, err.getvalue()

    def test_keeping_a_xiao_build_writes_its_drawn_breadboard_beside_the_sheet(self):
        # P267 (#300): the sheet's steps on a Wokwi breadboard, and the build says where.
        into, said = self.keep_a_build_of("button-light-xiao")
        drawn = json.loads((into / "breadboard.json").read_text())
        self.assertEqual(drawn["parts"][0]["type"], "wokwi-breadboard-half")
        self.assertIn("wrote %s — an example layout" % (into / "breadboard.json"), said)
        self.assertIn("An example layout is in breadboard.json", (into / "breadboard.md").read_text())

    def test_a_board_drawn_from_its_record_gets_the_picture_and_no_wokwi_diagram_by_design(self):
        # P412: Wokwi has no part with the FireBeetle's pins, so only breadboard.svg is written
        into, said = self.keep_a_build_of("button-light")
        self.assertFalse((into / "breadboard.json").exists())
        self.assertTrue((into / "breadboard.svg").is_file())
        self.assertIn("no drawn breadboard: ", said)
        self.assertNotIn("not written: ", (into / "breadboard.md").read_text())
        self.assertIn("There is no Wokwi diagram for this board", (into / "breadboard.md").read_text())

    def test_the_kept_entries_say_the_diagram_is_not_written_by_design_and_the_picture_is_from_the_record(self):
        import argparse
        import contextlib
        import io
        import shutil
        fixture = Path(__file__).resolve().parent / "data" / "breadboard" / "button-light"
        work = self.workdir()
        shutil.copy(fixture / "dist" / "board" / "circuit.json", work / "dist" / "board" / "circuit.json")
        into = Path(tempfile.mkdtemp()) / "project"
        into.mkdir()
        (into / "breadboard.json").write_text("{}")  # an old drawing, which describes another build
        args = argparse.Namespace(json=True, keep=into, requirements=str(fixture / "requirements.json"))
        with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
            check_spine.report([Stage("build", check_spine.OK, "fine")], args, work)
        kept = json.loads(out.getvalue())["kept"]
        by_file = {Path(entry["file"]).name: entry for entry in kept if Path(entry["file"]).name.startswith("breadboard.")}
        self.assertEqual((by_file["breadboard.svg"]["did"], by_file["breadboard.svg"]["drawn_from"]), ("wrote", "record"))
        gone = by_file["breadboard.json"]
        self.assertEqual((gone["did"], gone["code"], gone["subject"], gone["expected"]), ("not written", "no_wokwi_part", None, True))
        self.assertFalse((into / "breadboard.json").exists())

    def kept_json_of(self, fixture_name):
        """`report` with --json keeping one breadboard fixture's built circuit: the `kept` entries."""
        import argparse
        import contextlib
        import io
        import shutil
        fixture = Path(__file__).resolve().parent / "data" / "breadboard" / fixture_name
        work = self.workdir()
        shutil.copy(fixture / "dist" / "board" / "circuit.json", work / "dist" / "board" / "circuit.json")
        args = argparse.Namespace(json=True, keep=Path(tempfile.mkdtemp()) / "project", requirements=str(fixture / "requirements.json"))
        with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
            check_spine.report([Stage("build", check_spine.OK, "fine")], args, work)
        return [entry for entry in json.loads(out.getvalue())["kept"] if Path(entry["file"]).name.startswith("breadboard.")]

    def test_a_part_with_no_drawing_fact_names_its_code_and_a_wrote_entry_of_wokwi_geometry_has_no_drawn_from(self):
        for entry in self.kept_json_of("motor"):
            if entry["did"] == "not written" and entry["file"].endswith((".json", ".svg")):
                with self.subTest(file=entry["file"]):
                    self.assertEqual((entry["code"], entry["subject"], entry["expected"]),
                                     ("no_drawing_fact", "L9110sModule", False))
        wrote = [entry for entry in self.kept_json_of("button-light-xiao") if entry["did"] == "wrote"]
        self.assertTrue(wrote)
        self.assertTrue(all("drawn_from" not in entry for entry in wrote))

    def test_a_drawing_spark_does_not_make_yet_is_expected_in_both_kept_entries(self):
        # P783: a rail, an off-board supply or a resistor with both legs joined is a refusal a retry gives again, so
        # both drawings' entries say `expected`, and the agent tells the person to wire it from the sheet's steps
        from spark.breadboard import drawing, sheet
        for renderer in sheet.DRAWING_RENDERERS:
            with self.subTest(drawing=renderer.FILE_NAME):
                one = drawing.NotWritten(Path(renderer.FILE_NAME), renderer, "not_drawn_yet", "VBAT",
                                         "VBAT is not drawn yet")
                entry = kept_files.not_written_entry(one)
                self.assertEqual((entry["file"], entry["did"], entry["code"], entry["subject"], entry["expected"]),
                                 (renderer.FILE_NAME, "not written", "not_drawn_yet", "VBAT", True))
        self.assertEqual(sorted(renderer.FILE_NAME for renderer in sheet.DRAWING_RENDERERS),
                         ["breadboard.json", "breadboard.svg"])
        for code in ("row_full", "planner_fault"):  # a fault to report stays unexpected
            with self.subTest(code=code):
                one = drawing.NotWritten(Path("breadboard.svg"), sheet.DRAWING_RENDERERS[0], code, "x", "why")
                self.assertFalse(kept_files.not_written_entry(one)["expected"])

    def test_a_drawing_from_an_earlier_build_is_removed_when_a_build_does_not_finish(self):
        import argparse
        import contextlib
        import io
        fixture = Path(__file__).resolve().parent / "data" / "breadboard" / "button-light-xiao"
        into = Path(tempfile.mkdtemp()) / "project"
        into.mkdir(); (into / "breadboard.json").write_text("{}")
        args = argparse.Namespace(json=False, keep=into, requirements=str(fixture / "requirements.json"))
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as err:
            check_spine.report([Stage("build", check_spine.PROBLEMS, "1 error")], args, self.workdir())
        self.assertFalse((into / "breadboard.json").exists())
        self.assertIn("no drawn breadboard: the build did not finish in this run; removed", err.getvalue())

    def test_a_breadboard_json_that_holds_parts_is_left_when_a_build_does_not_finish(self):
        # P273: it may hold the person's moves, and a typo in requirements.json must not wipe them.
        import argparse
        import shutil
        from spark.breadboard import sheet
        fixture = Path(__file__).resolve().parent / "data" / "breadboard" / "button-light-xiao"
        into = Path(tempfile.mkdtemp()) / "project"
        shutil.copytree(fixture, into)
        with mock.patch.dict(os.environ, {"SPARK_HOME": tempfile.mkdtemp()}):
            sheet.write(into / "requirements.json", into / "breadboard.md")
        earlier = (into / "breadboard.json").read_text()
        args = argparse.Namespace(json=False, keep=into, requirements=str(fixture / "requirements.json"))
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as err:
            check_spine.report([Stage("build", check_spine.PROBLEMS, "1 error")], args, self.workdir())
        self.assertEqual((into / "breadboard.json").read_text(), earlier)
        self.assertIn("left alone: %s (it may hold your moves" % (into / "breadboard.json"), err.getvalue())
        self.assertFalse((into / "breadboard.svg").exists())

    def test_a_build_that_did_not_finish_writes_no_sheet_and_says_why(self):
        # P191's council: a failed build wrote a sheet from the earlier dist/, wiring parts the requirements had dropped.
        import argparse
        import contextlib
        import io
        fixture = Path(__file__).resolve().parent / "data" / "breadboard" / "button-light"
        into = Path(tempfile.mkdtemp()) / "project"
        args = argparse.Namespace(json=False, keep=into, requirements=str(fixture / "requirements.json"))
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as err:
            check_spine.report([Stage("build", check_spine.PROBLEMS, "1 error")], args, self.workdir())
        self.assertFalse((into / "breadboard.md").exists())
        self.assertIn("no breadboard sheet: the build did not finish", err.getvalue())

    def test_a_sheet_from_an_earlier_build_is_removed_when_a_build_does_not_finish(self):
        # The refuter: it described another board, and sat beside the new requirements.
        import argparse
        import contextlib
        import io
        fixture = Path(__file__).resolve().parent / "data" / "breadboard" / "button-light"
        into = Path(tempfile.mkdtemp()) / "project"
        into.mkdir(); (into / "breadboard.md").write_text("# an earlier build's sheet")
        args = argparse.Namespace(json=False, keep=into, requirements=str(fixture / "requirements.json"))
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as err:
            check_spine.report([Stage("build", check_spine.PROBLEMS, "1 error")], args, self.workdir())
        self.assertFalse((into / "breadboard.md").exists())
        self.assertIn("removed", err.getvalue())

    def keep_with_pins(self, into, requirements=None, stages=None):
        """`report` keeping into `into` with --json: what --json printed under `kept`, and what stderr said."""
        import argparse
        import contextlib
        import io
        fixture = Path(__file__).resolve().parent / "data" / "breadboard" / "button-light"
        args = argparse.Namespace(json=True, keep=into, requirements=str(requirements or fixture / "requirements.json"))
        with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()) as err:
            check_spine.report(stages or [Stage("build", check_spine.OK, "fine")], args, self.workdir())
        return json.loads(out.getvalue())["kept"], err.getvalue()

    def emitted_pins(self, requirements):
        """What `assign_pins.py requirements.json --emit-pins FILE` writes: the card's measure of the kept pin map."""
        import assign_pins
        import contextlib
        import io
        target = Path(tempfile.mkdtemp()) / "pins.py"
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(assign_pins.main([str(requirements), "--emit-pins", str(target)]), 0)
        return target.read_text()

    def test_keeping_a_project_s_build_writes_the_pin_map_its_firmware_imports(self):
        # P196 (#155): after /spark:build the firmware had no pins.py until a second command wrote it.
        fixture = Path(__file__).resolve().parent / "data" / "breadboard" / "button-light"
        into = Path(tempfile.mkdtemp()) / "project"
        kept, err = self.keep_with_pins(into)
        self.assertEqual((into / "firmware" / "pins.py").read_text(), self.emitted_pins(fixture / "requirements.json"))
        self.assertIn({"file": str(into / "firmware" / "pins.py"), "did": "wrote",
                       "why": "the pins the firmware imports"}, kept)
        self.assertIn("wrote %s — the pins the firmware imports" % (into / "firmware" / "pins.py"), err)

    def test_the_pin_map_needs_no_finished_build(self):
        # It is made from the requirements alone, so a machine without the board engine still gets it.
        into = Path(tempfile.mkdtemp()) / "project"
        self.keep_with_pins(into, stages=[Stage("build", check_spine.COULD_NOT_RUN, "no tsci")])
        self.assertTrue((into / "firmware" / "pins.py").is_file())

    def test_a_pin_map_spark_wrote_earlier_is_rewritten(self):
        # It says "Regenerate it; do not edit it.", and one left from an earlier design sends the firmware to wrong pins.
        fixture = Path(__file__).resolve().parent / "data" / "breadboard" / "button-light"
        into = Path(tempfile.mkdtemp()) / "project"
        (into / "firmware").mkdir(parents=True)
        stale = self.emitted_pins(fixture / "requirements.json") + "OLD_SIGNAL = 99\n"
        (into / "firmware" / "pins.py").write_text(stale)
        self.keep_with_pins(into)
        self.assertEqual((into / "firmware" / "pins.py").read_text(), self.emitted_pins(fixture / "requirements.json"))

    def test_a_pins_file_spark_did_not_write_is_left_alone_and_said(self):
        # A person's own pins.py is theirs, as an edited board.tsx is.
        into = Path(tempfile.mkdtemp()) / "project"
        (into / "firmware").mkdir(parents=True)
        (into / "firmware" / "pins.py").write_text("LED = 5  # mine\n")
        kept, err = self.keep_with_pins(into)
        self.assertEqual((into / "firmware" / "pins.py").read_text(), "LED = 5  # mine\n")
        self.assertIn({"file": str(into / "firmware" / "pins.py"), "did": "left alone",
                       "why": "spark did not write it; delete it to have it written"}, kept)
        self.assertIn("left alone: %s" % (into / "firmware" / "pins.py"), err)

    def test_a_pin_map_from_an_earlier_design_is_removed_when_the_pins_cannot_be_placed(self):
        fixture = Path(__file__).resolve().parent / "data" / "breadboard" / "button-light"
        broken = Path(tempfile.mkdtemp()) / "requirements.json"
        broken.write_text(json.dumps({"board": "firebeetle2-esp32s3", "parts": ["no-such-part"]}))
        into = Path(tempfile.mkdtemp()) / "project"
        (into / "firmware").mkdir(parents=True)
        (into / "firmware" / "pins.py").write_text(self.emitted_pins(fixture / "requirements.json"))
        kept, err = self.keep_with_pins(into, requirements=broken)
        self.assertFalse((into / "firmware" / "pins.py").exists())
        self.assertEqual([entry["did"] for entry in kept if entry["file"].endswith("pins.py")], ["removed"])
        self.assertIn("no pin map: ", err)
        self.assertIn("no-such-part", err)

    def test_the_one_command_keeps_the_simulation_project_too(self):
        # JB1: `--keep .` kept the board, dist/ and the sheet, but the Wokwi diagram only with `--sim-dir sim`.
        import contextlib
        import io
        fixture = Path(__file__).resolve().parent / "data" / "breadboard" / "button-light"

        def a_build_that_simulated(requirements, workdir, *rest, **named):
            (workdir / "sim").mkdir()
            (workdir / "sim" / "diagram.json").write_text('{"parts": []}')
            return [Stage("build", check_spine.OK, "fine")]

        into, elsewhere = Path(tempfile.mkdtemp()) / "project", Path(tempfile.mkdtemp()) / "sim"
        with mock.patch.object(requirements_build, "BuildService", FakeBuildService(a_build_that_simulated)), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            check_spine.main([str(fixture / "requirements.json"), "--keep", str(into)])
            self.assertTrue((into / "sim" / "diagram.json").is_file())
            # A --sim-dir of the person's own still decides where it goes.
            other = Path(tempfile.mkdtemp()) / "project"
            check_spine.main([str(fixture / "requirements.json"), "--keep", str(other), "--sim-dir", str(elsewhere)])
        self.assertTrue((elsewhere / "diagram.json").is_file())
        self.assertFalse((other / "sim").exists())

    def a_kept_project(self):
        """(a build's workdir with a sim/ and no note, a project's sim/ with an older note, a diagram and a scenario of the person's)."""
        work, into = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp()) / "sim"
        (work / "sim").mkdir()
        (work / "sim" / "board.json").write_text("{}")
        into.mkdir()
        (into / "diagram.json").write_text('{"parts": ["older"]}')
        (into / "WHAT-THIS-CANNOT-SHOW.md").write_text("- **Old** — from an earlier build\n")
        (into / "scenarios").mkdir()
        (into / "scenarios" / "mine.scenario.yaml").write_text("steps:\n")
        return work, into

    def test_an_older_limits_note_goes_when_the_simulation_stage_finished_and_wrote_none(self):
        # The build runs in a fresh folder and keep_simulation merges into the project's sim/, so only keep_simulation can remove it.
        work, into = self.a_kept_project()
        (work / "sim" / "diagram.json").write_text("{}")
        done = [Stage("build", check_spine.OK, "fine"), Stage("simulation", check_spine.OK, "ran")]
        self.assertEqual(kept_files.keep_simulation(work, into, done)["did"], "wrote")
        self.assertFalse((into / "WHAT-THIS-CANNOT-SHOW.md").exists())
        self.assertTrue((into / "scenarios" / "mine.scenario.yaml").is_file())  # a person's scenarios stay
        self.assertEqual((into / "diagram.json").read_text(), "{}")
        (work / "sim" / "WHAT-THIS-CANNOT-SHOW.md").write_text("- **New** — from this build\n")
        kept_files.keep_simulation(work, into, done)
        self.assertEqual((into / "WHAT-THIS-CANNOT-SHOW.md").read_text(), "- **New** — from this build\n")

    def test_the_older_note_and_diagram_stay_when_the_simulation_stage_did_not_finish(self):
        # The stage writes board.json and wokwi-mapping.json before it can stop; the older diagram stays, so its note must too.
        for status in (check_spine.COULD_NOT_RUN, check_spine.PROBLEMS):
            work, into = self.a_kept_project()
            stopped = [Stage("build", check_spine.OK, "fine"), Stage("simulation", status, "stopped")]
            with self.subTest(status=status):
                kept_files.keep_simulation(work, into, stopped)
                self.assertEqual((into / "WHAT-THIS-CANNOT-SHOW.md").read_text(), "- **Old** — from an earlier build\n")
                self.assertEqual((into / "diagram.json").read_text(), '{"parts": ["older"]}')
        work, into = self.a_kept_project()  # a build that stopped before the simulation stage has no simulation stage at all
        kept_files.keep_simulation(work, into, [Stage("board", check_spine.COULD_NOT_RUN, "no board")])
        self.assertTrue((into / "WHAT-THIS-CANNOT-SHOW.md").is_file())

    def keep_through_main(self, *argv, requirements=None):
        """`main` with a run that simulated, --json: the verdict it printed, and the firmware the run was handed."""
        import contextlib
        import io
        fixture = Path(__file__).resolve().parent / "data" / "breadboard" / "button-light"
        handed = {}

        def a_build_that_simulated(requirements, workdir, *rest, firmware=None, **named):
            handed["firmware"] = firmware
            (workdir / "sim").mkdir()
            (workdir / "sim" / "diagram.json").write_text('{"parts": []}')
            return [Stage("build", check_spine.OK, "fine")]

        with mock.patch.object(requirements_build, "BuildService", FakeBuildService(a_build_that_simulated)), \
                contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
            check_spine.main([str(requirements or fixture / "requirements.json"), "--json"] + [str(a) for a in argv])
        return json.loads(out.getvalue()), handed.get("firmware")

    def test_the_kept_simulation_is_listed_with_the_other_kept_files(self):
        into = Path(tempfile.mkdtemp()) / "project"
        said, _ = self.keep_through_main("--keep", into)
        self.assertIn({"file": str(into / "sim"), "did": "wrote",
                       "why": "the simulation project: diagram.json, wokwi.toml and the chips"}, said["kept"])

    def test_a_keep_into_a_file_still_prints_the_verdict_when_the_build_simulated(self):
        # The refuter: the sim/ copy ran outside any guard, so `--keep <a file>` ended in a traceback and no verdict.
        blocked = Path(tempfile.mkdtemp()) / "a-file"; blocked.write_text("not a folder")
        said, _ = self.keep_through_main("--keep", blocked)
        self.assertEqual(said["status"], "ok")
        self.assertIn("not kept", [entry["did"] for entry in said["kept"] if entry["file"] == str(blocked / "sim")])

    def test_a_firmware_folder_that_cannot_hold_the_pin_map_still_prints_the_verdict(self):
        into = Path(tempfile.mkdtemp()) / "project"
        into.mkdir(); (into / "firmware").write_text("a file where the folder goes")
        said, _ = self.keep_through_main("--keep", into)
        self.assertEqual(said["status"], "ok")
        self.assertEqual([entry["did"] for entry in said["kept"] if entry["file"].endswith("pins.py")], ["not written"])

    def test_a_pins_file_that_is_not_text_is_left_alone(self):
        # A person's own pins.py in another encoding raised UnicodeDecodeError, and the verdict never printed.
        into = Path(tempfile.mkdtemp()) / "project"
        (into / "firmware").mkdir(parents=True)
        (into / "firmware" / "pins.py").write_bytes("LED = 5  # žluťoučký\n".encode("cp1250"))
        said, _ = self.keep_through_main("--keep", into)
        self.assertEqual([entry["did"] for entry in said["kept"] if entry["file"].endswith("pins.py")], ["left alone"])

    def test_pins_that_cannot_be_placed_write_no_pin_map(self):
        # The ordinary refusal is assign_pins.ImpossibleError, not a DesignError: a need no pin can meet.
        wanted = Path(tempfile.mkdtemp()) / "requirements.json"
        wanted.write_text(json.dumps({"board": "firebeetle2-esp32s3", "parts": ["led-red-5mm"],
                                      "signals": [{"name": "X", "needs": ["teleport"]}]}))
        into = Path(tempfile.mkdtemp()) / "project"
        kept, err = self.keep_with_pins(into, requirements=wanted)
        self.assertEqual([entry["did"] for entry in kept if entry["file"].endswith("pins.py")], ["not written"])
        self.assertIn("teleport", err)

    def test_a_need_that_is_not_a_word_is_refused_where_the_file_is_read(self):
        # The refuter: `needs: [["wake"]]` passed the reader and crashed the pin map with an unhashable list.
        wanted = Path(tempfile.mkdtemp()) / "requirements.json"
        wanted.write_text(json.dumps({"board": "firebeetle2-esp32s3", "parts": ["led-red-5mm"],
                                      "signals": [{"name": "X", "needs": [["wake"]]}]}))
        with self.assertRaises(loader.DesignError):
            loader.read(wanted)

    def test_a_rebuild_runs_the_flash_image_the_kept_simulation_already_names(self):
        # The refuter: `--keep .` after the simulate steps rewrote wokwi.toml with its firmware line commented out.
        into = Path(tempfile.mkdtemp()) / "project"
        (into / "sim").mkdir(parents=True)
        (into / "sim" / "wokwi.toml").write_text('[wokwi]\nversion = 1\nfirmware = "flash-with-firmware.bin"\n')
        self.assertEqual(self.keep_through_main("--keep", into)[1], "flash-with-firmware.bin")
        self.assertEqual(self.keep_through_main("--keep", into, "--firmware", "other.bin")[1], "other.bin")

    def rebuild_over(self, toml_text, *argv, writes=True):
        """
        (the firmware the run was handed, stderr) of a `--keep` rebuild over a sim/wokwi.toml of this text (None: no file).
        The run writes a new wokwi.toml unless `writes` is False: a build that stopped before its simulation stage.
        """
        import contextlib
        import io
        into = Path(tempfile.mkdtemp()) / "project"
        (into / "sim").mkdir(parents=True)
        if toml_text is not None:
            (into / "sim" / "wokwi.toml").write_text(toml_text)
        fixture = Path(__file__).resolve().parent / "data" / "breadboard" / "button-light"
        handed = {}

        def a_build_that_simulated(requirements, workdir, *rest, firmware=None, **named):
            handed["firmware"] = firmware
            if writes:
                (workdir / "sim").mkdir()
                (workdir / "sim" / "wokwi.toml").write_text("[wokwi]\n")
            return [Stage("build", check_spine.OK, "fine")]

        with mock.patch.object(requirements_build, "BuildService", FakeBuildService(a_build_that_simulated)), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as err:
            check_spine.main([str(fixture / "requirements.json"), "--keep", str(into)] + list(argv))
        return handed["firmware"], err.getvalue()

    def test_a_rebuild_over_a_firmware_line_it_cannot_read_says_the_line_goes(self):
        # P429: the rewritten wokwi.toml dropped the line without a word
        handed, said = self.rebuild_over("[wokwi]\nversion = 1\nfirmware = 3\n")
        self.assertIsNone(handed)
        self.assertIn("  sim/wokwi.toml line 3 names the firmware in a form spark cannot read. "
                      "The rebuild wrote it again with no image named, and a scenario run then names the default one.\n", said)
        # and nothing for a line it kept, no line, no file, a --firmware of the person's own, or a build that stopped early
        for text in ('firmware = "x.bin"\n', "[wokwi]\nversion = 1\n", None):
            self.assertNotIn("The rebuild wrote it again", self.rebuild_over(text)[1], text)
        handed, said = self.rebuild_over("firmware = 3\n", "--firmware", "other.bin")
        self.assertEqual((handed, said.count("The rebuild wrote it again")), ("other.bin", 0))
        self.assertNotIn("The rebuild wrote it again", self.rebuild_over("firmware = 3\n", writes=False)[1])

    def test_a_file_spark_cannot_read_has_its_own_sentence_in_the_rebuild_line(self):
        with mock.patch.object(requirements_build.sim_project, "firmware_in", return_value=requirements_build.sim_project.FirmwareLine(
                "not-checked", None, "cannot be read: Permission denied.")):
            handed, said = self.rebuild_over("anything")
        self.assertIn("  sim/wokwi.toml cannot be read: Permission denied. The rebuild wrote it again", said)

    def test_that_line_is_one_the_terminal_prints_as_itself(self):
        # a reason that holds a character a terminal does not print: the line goes through guard_lines like the others
        with mock.patch.object(requirements_build.sim_project, "firmware_in", return_value=requirements_build.sim_project.FirmwareLine(
                "not-checked", None, "a\u202eb")):
            handed, said = self.rebuild_over("anything")
        self.assertIn("  sim/wokwi.toml a?b The rebuild wrote it again", said)

    def test_kept_files_reach_the_envelope_as_they_reach_the_text(self):
        # P124 (#58), CH-16: with --json the lines of --keep went to stderr only, so an agent never read which files it
        # wrote and which it left alone.
        import argparse
        import contextlib
        import io
        into = Path(tempfile.mkdtemp()) / "project"
        into.mkdir(); (into / "board.tsx").write_text("// MINE")
        args = argparse.Namespace(json=True, keep=into)
        with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()) as err:
            check_spine.report([Stage("build", check_spine.OK, "fine")], args, self.workdir())
        kept = json.loads(out.getvalue())["kept"]
        self.assertIn({"file": str(into / "board.tsx"), "did": "left alone", "why": "delete it to have it regenerated"}, kept)
        self.assertIn({"file": str(into / "dist"), "did": "wrote", "why": "this is what every check reads"}, kept)
        self.assertIn("left alone: %s" % (into / "board.tsx"), err.getvalue())

    def test_a_keep_that_cannot_write_still_prints_the_verdict_and_says_so(self):
        import argparse
        import contextlib
        import io
        blocked = Path(tempfile.mkdtemp()) / "a-file"; blocked.write_text("not a folder")
        args = argparse.Namespace(json=True, keep=blocked)
        with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()) as err:
            check_spine.report([Stage("build", check_spine.OK, "fine")], args, self.workdir())
        said = json.loads(out.getvalue())
        self.assertEqual((said["status"], said["kept"][0]["did"]), ("ok", "not kept"))
        self.assertIn("not kept", err.getvalue())

    def test_without_it_the_temp_directory_is_still_removed(self):
        import argparse
        import contextlib
        import io
        work = self.workdir()
        args = argparse.Namespace(json=False, keep=None)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            check_spine.report([Stage("build", check_spine.OK, "fine")], args, work)
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
        import contextlib
        import io
        out = io.StringIO()
        with contextlib.redirect_stderr(out), self.assertRaises(SystemExit):
            check_spine.main(["--keep"])
        self.assertIn("expected one argument", out.getvalue())


class ACommandThatRunsPastItsLimitIsCouldNotRunTest(unittest.TestCase):
    """P659: the build's limit fits a real build (496 s on the bench), and a late command is named with its own limit."""

    def main_with(self, *, build=None):
        """`main` on the reference design, every child run late; the verdict as JSON, the exit code and the limits asked."""
        import contextlib
        import io
        limits = []
        really = subprocess.run

        def a_child_that_ran_late(cmd, *rest, **named):
            if "emit_board.py" in str(cmd) or "emit_footprint.py" in str(cmd) or "assign_pins.py" in str(cmd):
                return really(cmd, *rest, **named)
            limits.append(named.get("timeout"))
            raise subprocess.TimeoutExpired(cmd, named.get("timeout"), stderr=b"routing net 3\nrouting net 4\n")

        patches = [mock.patch.object(requirements_build.subprocess, "run", a_child_that_ran_late),
                   mock.patch.object(board_engine, "find_toolchain", lambda start: Path("/x/node_modules/.bin/tsci"))]
        if build:
            patches.append(mock.patch.object(requirements_build, "BuildService", FakeBuildService(build)))
        with contextlib.ExitStack() as stack:
            for patch in patches:
                stack.enter_context(patch)
            out = stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
            stack.enter_context(contextlib.redirect_stderr(io.StringIO()))
            code = check_spine.main(["--json"])
        return json.loads(out.getvalue()), code, limits

    def test_a_build_that_runs_past_its_limit_names_the_command_and_900_seconds(self):
        said, code, limits = self.main_with()
        build = [stage for stage in said["stages"] if stage["name"] == "build"][0]
        self.assertEqual("could-not-run", build["status"])
        self.assertIn("`tsci build` did not finish in 900s", build["detail"])
        self.assertIn("routing net 4", build["detail"])
        self.assertEqual(2, code)
        self.assertEqual([900], limits)

    def test_the_builds_limit_is_at_least_ten_minutes(self):
        _, _, limits = self.main_with()
        self.assertGreaterEqual(limits[0], 600)

    def test_the_probe_that_runs_past_its_limit_names_120_seconds(self):
        def a_build_that_probed(requirements, workdir, **named):
            board_engine.TscircuitEngine(Path("/x/tsci")).probe(workdir)
        said, code, limits = self.main_with(build=a_build_that_probed)
        detail = said["stages"][0]["detail"]
        self.assertIn("`tsci build` did not finish in 120s", detail)
        self.assertEqual(2, code)
        self.assertEqual([120], limits)

    def test_the_converter_that_runs_past_its_limit_names_120_seconds(self):
        def a_build_that_converted(requirements, workdir, **named):
            (workdir / "sim").mkdir()
            with mock.patch.object(board_engine, "converter_command", lambda project, own: ["/x/convert-wokwi", "--circuit"]):
                board_engine.convert(None, None, ["--circuit", "c.json"], workdir / "sim", workdir)
        said, code, limits = self.main_with(build=a_build_that_converted)
        self.assertIn("`convert-wokwi --circuit` did not finish in 120s", said["stages"][0]["detail"])
        self.assertEqual(2, code)
        self.assertEqual([120], limits)


    def test_the_sentence_reads_text_a_string_command_a_runtime_and_no_words(self):
        late = subprocess.TimeoutExpired
        self.assertEqual("`tsci build` did not finish in 900s; its last words: routing net 4",
                         requirements_build.timed_out_sentence(late("/opt/spark/x/tsci build board.tsx", 900, stderr="routing net 4\n")))
        self.assertEqual("`bun run cli.ts` did not finish in 120s",
                         requirements_build.timed_out_sentence(late(["/opt/bun", "run", "/opt/spark/tools/cli.ts"], 120)))
        self.assertEqual("`convert-wokwi --circuit` did not finish in 120s; its last words: wrote 3 parts",
                         requirements_build.timed_out_sentence(late(["convert-wokwi", "--circuit"], 120, output=b"wrote 3 parts\n", stderr=b"")))

    def test_the_last_words_keep_their_end_and_no_more_than_800_characters(self):
        said = requirements_build.timed_out_sentence(subprocess.TimeoutExpired(["tsci", "build"], 900, stderr="x" * 5000 + "END"))
        self.assertTrue(said.endswith("END"))
        self.assertLessEqual(len(said), 900)



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
        self.assertEqual(board_engine.find_toolchain(deep), binary)

    def test_no_toolchain_anywhere_is_none_not_a_guess(self):
        # PATH has to be emptied: this machine has a global tsci, so without it the test passes
        # or fails on what happens to be installed rather than on the function.
        import os
        import tempfile
        original = os.environ.get("PATH", "")
        os.environ["PATH"] = ""
        try:
            self.assertIsNone(board_engine.find_toolchain(Path(tempfile.mkdtemp())))
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
        self.assertEqual(build_service.wires_in({"connections": [["a", "b"], ["c", "d"]]}), 2)

    def test_a_diagram_with_no_connections_counts_zero(self):
        # The same failure shape as a board with no copper: every part placed, nothing joined.
        # It is what an unmapped component looks like once the converter has given up on it.
        self.assertEqual(build_service.wires_in({"parts": [{"id": "mcu"}], "connections": []}), 0)

    def test_the_serial_monitor_s_wires_are_not_counted_so_an_unwired_board_still_counts_zero(self):
        # P190: the two serial wires are in every S3 diagram; counted, the 0-connections guard could never fire.
        serial = [["mcu:TX", "$serialMonitor:RX", "", []], ["mcu:RX", "$serialMonitor:TX", "", []]]
        self.assertEqual(build_service.wires_in({"connections": serial}), 0)
        self.assertEqual(build_service.wires_in({"connections": serial + [["mcu:38", "btn:1.l", "", []]]}), 1)

    def test_a_diagram_with_no_serial_monitor_is_said_in_the_stage_line(self):
        # P190: a board part with no pins named TX and RX gets no serial wires, so a scenario hears nothing.
        self.assertFalse(build_service.serial_wired({"connections": [["mcu:38", "btn:1.l", "", []]]}))
        self.assertTrue(build_service.serial_wired({"connections": [["mcu:TX", "$serialMonitor:RX", "", []]]}))
        said = build_service.simulation_detail(3, {}, 0, [], serial=False)
        self.assertIn("no serial monitor is wired", said)
        self.assertNotIn("serial", build_service.simulation_detail(3, {}, 0, [], serial=True))

    def test_serial_heard_is_wired_or_the_boards_record_says_true(self):
        # P468: a record's `serial_without_wires` counts only as the value true, never "yes", 1 or a missing record
        bare = {"connections": []}
        wired = {"connections": [["mcu:TX", "$serialMonitor:RX", "", []]]}
        self.assertTrue(build_service.serial_heard(bare, {"serial_without_wires": True}))
        self.assertFalse(build_service.serial_heard(bare, {}))
        self.assertFalse(build_service.serial_heard(bare, None))
        self.assertFalse(build_service.serial_heard(bare, {"serial_without_wires": "yes"}))
        self.assertTrue(build_service.serial_heard(wired, {}))

    def test_the_shipped_xiao_and_firebeetle_records_say_their_serial_needs_no_wires(self):
        self.assertIs(board_records.load(ROOT, "xiao-esp32-c6")["serial_without_wires"], True)
        self.assertIs(board_records.load(ROOT, "firebeetle2-esp32s3")["serial_without_wires"], True)

    def test_a_diagram_missing_the_key_entirely_counts_zero_rather_than_raising(self):
        self.assertEqual(build_service.wires_in({}), 0)

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
        self.assertEqual(board_engine.find_converter(deep), converter.resolve())

    def test_a_directory_with_nothing_beside_it_gets_the_plugins_own(self):
        # THE CONTRACT CHANGED WITH P32a, and again with P82: a project with no converter of its own
        # gets the plugin's — now the bundle the tools list names, run on Node, never the plugin's
        # TypeScript source (which needs node_modules an installed plugin lacks).
        import tempfile
        from spark.records import tool_finder
        self.assertIsNone(board_engine.find_converter(Path(tempfile.mkdtemp())))
        with mock.patch.object(tool_finder, "PERSONAL", Path(tempfile.mkdtemp()) / "absent.json"):
            command = board_engine.converter_command(None, None)
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
        self.assertEqual(board_engine.find_converter(root), (mine / "cli.ts").resolve())

    def test_no_converter_at_all_is_could_not_run_not_a_guess(self):
        from unittest import mock
        import tempfile
        from spark.records import tool_finder
        with mock.patch.object(tool_finder, "PLUGIN", Path("/nowhere")):
            stage = board_engine.converter_stage_problem(Path(tempfile.mkdtemp()))
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
        from spark.records import record_kind
        available = set(record_kind.available())
        for part_id in requirements_build.REFERENCE["parts"]:
            with self.subTest(part=part_id):
                self.assertIn(part_id, available)

    def test_it_includes_something_that_sources_a_rail(self):
        # Without it the design has a net with one member, the autorouter skips routing, and the
        # gate's own reference design demonstrates the defect the gate exists to catch.
        from spark.sourcing import part_records
        sources = [part_id for part_id in requirements_build.REFERENCE["parts"]
                   if any(supply.get("direction") == "out"
                          for supply in part_records.load(part_id).get("power") or [])]
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

    def test_two_part_names_that_differ_only_in_capitals_stop_at_the_requirements_stage(self):
        # P163 (#100): the chain built this — two GPIOs on one pad, 0 errors — and the converter's duplicate-id was the only
        # thing that said anything. A requirements file is refused where it is read, naming both spellings; nothing runs.
        path = Path(tempfile.mkdtemp()) / "bin.json"
        path.write_text(json.dumps({"board": "firebeetle2-esp32s3",
                                    "parts": [{"part": "tactile-button", "name": "OpenLid"},
                                              {"part": "tactile-button", "name": "Openlid"}]}))
        code, out = self._main([str(path)], tempfile.mkdtemp())
        self.assertEqual(code, check_spine.EXIT_COULD_NOT_RUN)
        self.assertIn("[????] requirements", out)
        self.assertIn("parts[0] is called OpenLid and parts[1] Openlid", out)
        self.assertIn("capitals do not make two names", out)
        self.assertIn("NOT exercised", out)
        for stage_run in ("] board", "] schematic", "] build"):
            self.assertNotIn(stage_run, out, "nothing ran, nothing was emitted")

    # --- MVP --- (P438)
    def test_a_requirements_file_of_the_wrong_kind_stops_at_the_requirements_stage(self):
        for listed, signals, field in (
                (["tactile-button"], 5, "signals is a number"),
                (["tactile-button"], [{"name": "X", "pin": ["D0"]}], "signals[0].pin is a list"),
                (5, None, "parts is a number"), ("led-red-5mm", None, "parts is text")):
            with self.subTest(field=field):
                path = Path(tempfile.mkdtemp()) / "bin.json"
                path.write_text(json.dumps({"board": "firebeetle2-esp32s3", "parts": listed, "signals": signals}))
                code, out = self._main([str(path)], tempfile.mkdtemp())
                self.assertEqual(code, check_spine.EXIT_COULD_NOT_RUN)
                self.assertIn("[????] requirements", out)
                self.assertIn("bin.json: " + field, out)
                for stage_run in ("] board", "] schematic", "] build"):
                    self.assertNotIn(stage_run, out, "nothing ran")

    def test_a_hand_written_signal_under_an_instances_signal_name_stops_at_the_requirements_stage(self):
        # P163's other route: with `signals` holding OPENLID_BUTTON beside an instance called OpenLid, the generator traced
        # D3 and A5 to one pad, `tsci build` passed and the spine said "the chain runs end to end", exit 0. Refused where
        # the signals are derived — the schematic stage, the first with the part records that say OpenLid asks for
        # BUTTON; the requirements stage reads the file alone — so nothing is emitted and no later stage runs.
        path = Path(tempfile.mkdtemp()) / "bin.json"
        path.write_text(json.dumps({"board": "firebeetle2-esp32s3",
                                    "parts": [{"part": "tactile-button", "name": "OpenLid"}],
                                    "signals": [{"name": "OPENLID_BUTTON", "needs": []}]}))
        code, out = self._main([str(path)], tempfile.mkdtemp())
        self.assertEqual(code, check_spine.EXIT_COULD_NOT_RUN)
        self.assertIn("[????] schematic", out)
        self.assertIn("cannot emit a board: OpenLid's BUTTON and signals[0] are both OPENLID_BUTTON", out)
        self.assertIn("NOT exercised", out)
        for stage_run in ("] footprint", "] build", "] simulation"):
            self.assertNotIn(stage_run, out, "nothing was emitted, nothing built")

    # P280 (#318): a refused file kept nothing and cleaned nothing, so an earlier build's sheet and page stayed beside a
    # requirements file that no longer builds, describing another board.
    EARLIER_BUILD = ("breadboard.md", "breadboard.json", "breadboard.svg", "page.html")

    @staticmethod
    def _main_with_stderr(argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = check_spine.main(argv)
        return code, out.getvalue(), err.getvalue()

    def _an_earlier_build(self, requirements_text="{not json"):
        project = Path(tempfile.mkdtemp())
        for name in self.EARLIER_BUILD:
            (project / name).write_text("from an earlier build")
        (project / "firmware").mkdir()
        (project / "firmware" / "pins.py").write_text(kept_files.pin_assigner.PIN_MODULE_HEADER + "\n")
        if requirements_text is not None:
            (project / "requirements.json").write_text(requirements_text)
        return project

    def test_a_refused_file_removes_the_earlier_build_s_sheet_drawings_page_and_pin_map(self):
        project = self._an_earlier_build()
        code, _, err = self._main_with_stderr([str(project / "requirements.json"), "--keep", str(project)])
        self.assertEqual(code, check_spine.EXIT_COULD_NOT_RUN)
        for name in self.EARLIER_BUILD + ("firmware/pins.py",):
            self.assertFalse((project / name).exists(), name)
        self.assertIn("no breadboard sheet: ", err)
        self.assertIn("not JSON", err)
        self.assertIn("; removed %s" % (project / "breadboard.md"), err)

    def test_with_json_each_removed_file_is_a_kept_entry_with_the_reason(self):
        project = self._an_earlier_build()
        _, out, _ = self._main_with_stderr([str(project / "requirements.json"), "--keep", str(project), "--json"])
        said = json.loads(out)
        detail = said["stages"][0]["detail"]
        by_file = {Path(entry["file"]).name: entry for entry in said["kept"]}
        self.assertEqual(sorted(by_file), sorted(self.EARLIER_BUILD + ("pins.py",)))
        for name in self.EARLIER_BUILD:
            self.assertEqual(by_file[name]["did"], "removed")
            self.assertEqual(by_file[name]["why"], detail + ", and it described an earlier build")
        self.assertEqual(by_file["pins.py"]["did"], "removed")
        self.assertIn("is not JSON", by_file["pins.py"]["why"])

    def test_a_file_that_reads_but_is_refused_gives_its_own_reason(self):
        project = self._an_earlier_build(json.dumps({"board": "firebeetle2-esp32s3",
                                                     "parts": [{"part": "tactile-button", "name": "OpenLid"},
                                                               {"part": "tactile-button", "name": "Openlid"}]}))
        _, _, err = self._main_with_stderr([str(project / "requirements.json"), "--keep", str(project)])
        self.assertFalse((project / "page.html").exists())
        self.assertFalse((project / "firmware" / "pins.py").exists())
        page_line = next(line for line in err.splitlines() if "no page: " in line)
        self.assertIn("parts[0] is called OpenLid and parts[1] Openlid", page_line)

    def test_a_missing_file_removes_nothing(self):
        # A typo in the file's name must not delete a good build of the file that is there.
        project = self._an_earlier_build(requirements_text=None)
        code, _, _ = self._main_with_stderr([str(project / "requirements.jsn"), "--keep", str(project)])
        self.assertEqual(code, check_spine.EXIT_COULD_NOT_RUN)
        for name in self.EARLIER_BUILD + ("firmware/pins.py",):
            self.assertTrue((project / name).exists(), name)

    def test_a_refused_file_touches_nothing_else(self):
        project = self._an_earlier_build()
        (project / "firmware" / "pins.py").write_text("PIN = 4  # mine\n")
        for name in ("board.tsx", "notes.txt", "dist/board/circuit.json"):
            (project / name).parent.mkdir(parents=True, exist_ok=True)
            (project / name).write_text("kept")
        self._main_with_stderr([str(project / "requirements.json"), "--keep", str(project)])
        for name in ("firmware/pins.py", "board.tsx", "notes.txt", "dist/board/circuit.json"):
            self.assertTrue((project / name).exists(), name)

    def test_a_keep_folder_that_is_not_there_is_not_made(self):
        project = self._an_earlier_build()
        self._main_with_stderr([str(project / "requirements.json"), "--keep", str(project / "elsewhere")])
        self.assertFalse((project / "elsewhere").exists())

    def test_without_keep_nothing_is_removed(self):
        project = self._an_earlier_build()
        self._main_with_stderr([str(project / "requirements.json")])
        for name in self.EARLIER_BUILD:
            self.assertTrue((project / name).exists(), name)

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
        with mock.patch.object(board_engine, "find_toolchain", return_value=None):
            code, out = self._main([str(path)], tempfile.mkdtemp())
        self.assertNotIn("no part called", out)
        self.assertIn("[ok  ] schematic", out)
        self.assertIn("[????] build", out)
        self.assertEqual(code, check_spine.EXIT_COULD_NOT_RUN)


# --- MVP --- (P512, #708) a broken trace is named in the verdict, in the text and in --json
class ABrokenTraceIsNamedTest(unittest.TestCase):
    """
    P512: the verdict said "2 error(s): source_trace_not_connected_error" and not which trace. It names the selectors
    of the first 2 errors from their `selectors_not_found` field, and an error's message only when it has none. The
    build is a real one (button-light's kept circuit) with 3 errors added, by a fake tsci the project's node_modules holds.
    """
    FIXTURE = ROOT / "tests" / "data" / "breadboard" / "button-light"
    ERRORS = [{"type": "source_trace_not_connected_error", "message": "Could not find port",
               "selectors_not_found": [".Mcu > .MOSI", ".Mcu > .MISO"]},
              {"type": "pcb_trace_error", "message": "a trace crosses another"},
              {"type": "source_trace_not_connected_error", "selectors_not_found": [".Mcu > .SCK"]}]

    def said(self, errors):
        """The build stage's detail in --json, and the text run's output, for button-light's circuit plus `errors`."""
        root = Path(tempfile.mkdtemp())
        circuit = json.loads((self.FIXTURE / "dist" / "board" / "circuit.json").read_text()) + errors
        fake_tsci(root, "true", circuit, binary=root / "node_modules" / ".bin" / "tsci")
        shutil.copy(self.FIXTURE / "requirements.json", root / "requirements.json")
        said = {}
        for flags in ([], ["--json"]):
            out = io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                check_spine.main([str(root / "requirements.json")] + flags)
            said[bool(flags)] = out.getvalue()
        return next(stage for stage in json.loads(said[True])["stages"] if stage["name"] == "build")["detail"], said[False]

    def test_the_text_and_the_json_name_the_first_two(self):
        for words in self.said(self.ERRORS):
            self.assertIn("3 error(s): pcb_trace_error, source_trace_not_connected_error; first: .Mcu > .MOSI, .Mcu > .MISO; "
                          "a trace crosses another", words)
            self.assertNotIn(".SCK", words)

    def test_an_odd_field_is_said_as_text_and_a_long_one_is_capped(self):
        detail, _ = self.said([{"type": "source_trace_not_connected_error", "selectors_not_found": ".Mcu > .MOSI"}])
        self.assertIn("first: .Mcu > .MOSI", detail)
        detail, _ = self.said([{"type": "source_trace_not_connected_error", "selectors_not_found": [1, ".Mcu > .SCK"]}])
        self.assertIn("first: 1, .Mcu > .SCK", detail)
        detail, _ = self.said([{"type": "source_trace_not_connected_error", "message": "x" * 2000}])
        self.assertLess(len(detail), 400)


# --- MVP --- (P512, #708) Done when: an SPI and an I2C part build with 0 errors on both shipped boards
@slow("four tscircuit builds, about 5 s each, 19.0 s on 2026-11-02")
@unittest.skipUnless(test_converter.node() and board_engine.find_toolchain(ROOT), "needs the board engine and Node")
class AnSpiOrI2cPartBuildsOnEveryShippedBoardTest(unittest.TestCase):
    """
    P512: the emitter traced `.Mcu > .MOSI` where the pad is MO (FireBeetle 2) and `.Mcu > .SDA` where it is D4 (XIAO
    C6), so these builds ended with 2 to 4 errors. The display's record is a fixture copied into a temp project's
    parts/; the store is never read. The build step is asserted, not the whole chain: the XIAO display run's simulation
    stage is skipped (the display has no Wokwi part, P778), exit 0.
    """

    def build_stage(self, board, part, signals=()):
        project = Path(tempfile.mkdtemp())
        (project / ".spark").mkdir()
        (project / "parts").mkdir()
        shutil.copy(ROOT / "tests" / "data" / "parts" / "dfr0664-tft-2in.json", project / "parts")
        (project / "requirements.json").write_text(json.dumps({"board": board, "parts": [part], "signals": list(signals)}))
        self.requirements = project / "requirements.json"
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            check_spine.main([str(project / "requirements.json"), "--json"])
        return next(stage for stage in json.loads(out.getvalue())["stages"] if stage["name"] == "build")

    def test_each_build_ends_with_0_errors(self):
        for board, part in (("firebeetle2-esp32s3", "dfr0664-tft-2in"), ("xiao-esp32-c6", "dfr0664-tft-2in"),
                            ("xiao-esp32-c6", "vl6180x-breakout")):
            with self.subTest(board=board, part=part):
                build = self.build_stage(board, part)
                self.assertEqual(build["status"], check_spine.OK, build["detail"])
                self.assertIn(", 0 errors", build["detail"])

    def test_the_display_builds_with_its_four_gdi_pins_pinned(self):
        # --- MVP --- (P513, #709) Done when: the 4 GDI signals that are no bus line, on the cable's labels, build.
        gdi = [{"name": name, "pin": pin} for name, pin in (("TFT_BL", "D13"), ("TFT_CS", "D6"), ("TFT_RST", "D3"),
                                                              ("SD_CS", "D7"))]
        build = self.build_stage("firebeetle2-esp32s3", "dfr0664-tft-2in", gdi)
        self.assertEqual(build["status"], check_spine.OK, build["detail"])
        self.assertIn(", 0 errors", build["detail"])
        # DC is not pinned (D2 is a strap pin, P527 #726), so it lands on A5, GPIO11 — not the GDI cable's GPIO3.
        self.assertRegex(pin_assigner.pin_module_for(self.requirements).module, r"(?m)^TFT_DC = 11\b")


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
        self.assertEqual(board_engine.modules_for(binary), root / "node_modules")

    def test_a_global_tsci_links_nothing(self):
        # ~/.nvm/versions/node/v18/bin/tsci: its parent.parent is the prefix, not a node_modules.
        prefix = Path(tempfile.mkdtemp())
        binary = prefix / "bin" / "tsci"
        binary.parent.mkdir(parents=True)
        binary.write_text("#!/bin/sh\n")
        self.assertIsNone(board_engine.modules_for(binary))


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
        # `main` writes the requirements into the working directory before the build; this drives
        # the service directly, so it does the same.
        (workdir / "requirements.json").write_text(json.dumps(requirements_build.REFERENCE))
        stages = build_stages(dict(requirements_build.REFERENCE), workdir, toolchain=binary)
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
        self.assertEqual(build_service.verdict(stages), check_spine.EXIT_COULD_NOT_RUN)

    def test_a_tool_that_builds_a_trivial_board_but_not_this_one_is_a_problem(self):
        # The control: same failure on the design, but the preflight passes, so the design is
        # what is broken — and the verdict says the tool was checked.
        build, binary, stages = self._build_stage('[ "$(basename "$PWD")" = "spark-probe" ]')
        self.assertEqual(build.status, check_spine.PROBLEMS, build.detail)
        self.assertIn("no circuit.json was produced", build.detail)
        self.assertIn("does build a trivial board", build.detail)
        self.assertEqual(build_service.verdict(stages), check_spine.EXIT_PROBLEMS)

    def test_the_preflight_reports_what_the_tool_said(self):
        root = Path(tempfile.mkdtemp())
        can, words = board_engine.TscircuitEngine(fake_tsci(root, "false")).probe(root)
        self.assertFalse(can)
        self.assertIn("react", words)
        can, _ = board_engine.TscircuitEngine(fake_tsci(root, "true")).probe(root)
        self.assertTrue(can)

    def test_the_version_is_asked_of_the_tool_and_never_raises(self):
        root = Path(tempfile.mkdtemp())
        self.assertEqual(board_engine.TscircuitEngine(fake_tsci(root, "true")).version(), "0.0.0-fake")
        self.assertEqual(board_engine.TscircuitEngine(root / "no-such-tsci").version(), "unknown version")


class NothingToBuildIsNotAPassTest(unittest.TestCase):
    def test_an_empty_parts_list_is_could_not_run_before_anything_is_emitted(self):
        # Ran end to end as `ok` with two traces — the MCU's own rails — and two wires. A chain
        # proven on nothing has not been proven. (Intake M3, reproduced 2026-09-29.)
        workdir = Path(tempfile.mkdtemp())
        requirements = {"board": "firebeetle2-esp32s3", "parts": []}
        (workdir / "requirements.json").write_text(json.dumps(requirements))
        stages = build_stages(requirements, workdir, toolchain=Path("/nonexistent/tsci"))
        self.assertEqual([s.name for s in stages], ["board", "parts"])
        self.assertEqual(stages[-1].status, check_spine.COULD_NOT_RUN)
        self.assertIn("nothing to build", stages[-1].detail)
        self.assertEqual(build_service.verdict(stages), check_spine.EXIT_COULD_NOT_RUN)
        self.assertIn('"board_only": true', stages[-1].detail)


class TheTabbedPageTest(unittest.TestCase):
    """P271 (#307): page.html beside the kept board, its three tabs from the one circuit.json kept in this run."""

    def setUp(self):
        self.project = Path(tempfile.mkdtemp())
        self.picture = self.project / "breadboard.svg"
        self.picture.write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
        self.kept = [{"file": str(self.project / "dist"), "did": "wrote"},
                     {"file": str(self.picture), "did": "wrote", "why": "a picture"}]
        self.page = self.project / "page.html"

    def keep(self, stages=(Stage("build", check_spine.OK),), exporter=None):
        self.exporter = exporter or FakeTscircuitExport()
        return kept_files.keep_tabbed_page(self.project, list(stages), self.kept, self.exporter)

    def test_a_build_that_finished_writes_three_tabs_from_the_kept_circuit(self):
        entry = self.keep()
        self.assertEqual((entry["file"], entry["did"]), (str(self.page), "wrote"))
        circuit = str(self.project / "dist" / "board" / "circuit.json")
        self.assertEqual(self.exporter.asked, [(circuit, "schematic-svg"), (circuit, "pcb-svg")])
        self.assertEqual(3, self.page.read_text().count("data:image/svg+xml;base64,"))

    def test_the_title_has_two_to_four_words_from_the_folder_name(self):
        self.keep()
        title = re.search(r"<title>(.*?)</title>", self.page.read_text()).group(1)
        self.assertEqual(title, tabbed_page.page_title(self.project.resolve().name))
        self.assertIn(len(title.split()), (2, 3, 4))

    def test_a_failed_build_removes_an_earlier_page(self):
        self.page.write_text("old")
        entry = self.keep(stages=[Stage("build", check_spine.PROBLEMS)])
        self.assertEqual(entry["did"], "removed")
        self.assertIn("the build did not finish in this run", entry["why"])
        self.assertFalse(self.page.exists())

    def test_a_board_only_build_removes_an_earlier_page(self):
        self.page.write_text("old")
        entry = self.keep(stages=[Stage("build", check_spine.SKIPPED)])
        self.assertEqual((entry["did"], entry["line"].split(";")[0]), ("removed", "no page: board only: nothing to draw"))

    def test_a_dist_that_was_not_kept_removes_an_earlier_page(self):
        self.page.write_text("old")
        self.kept = self.kept[1:]
        entry = self.keep()
        self.assertEqual(entry["did"], "removed")
        self.assertIn("the build was not kept in this run", entry["why"])

    def test_a_breadboard_picture_that_was_not_written_gives_its_why(self):
        self.kept[1] = {"file": str(self.picture), "did": "not written", "why": "no layout fits"}
        self.keep()
        self.assertIn("<p>Breadboard: not drawn, because no layout fits.</p>", self.page.read_text())

    def test_a_breadboard_picture_that_cannot_be_read_gives_its_why(self):
        self.picture.write_bytes(b"\xff")
        self.keep()
        self.assertIn("Breadboard: not drawn, because breadboard.svg cannot be read", self.page.read_text())

    def test_a_failed_export_still_writes_the_page_with_its_why(self):
        from spark.breadboard import tabbed_page
        failed = FakeTscircuitExport({"pcb-svg": tabbed_page.SvgExportResult(None, "tsci is not installed")})
        self.assertEqual(self.keep(exporter=failed)["did"], "wrote")
        self.assertIn("<p>PCB: not drawn, because tsci is not installed.</p>", self.page.read_text())


class TheBoardAloneTest(unittest.TestCase):
    """P236: a project that says `"board_only": true` builds the board alone: the board stages are skipped, never ok."""

    def run_alone(self, **extra):
        workdir = Path(tempfile.mkdtemp())
        requirements = dict({"board": "xiao-esp32-c6", "parts": [], "board_only": True}, **extra)
        (workdir / "requirements.json").write_text(json.dumps(requirements))
        return workdir, build_stages(requirements, workdir, toolchain=Path("/nonexistent/tsci"))

    def test_the_board_stages_are_skipped_and_the_simulation_holds_the_board(self):
        workdir, stages = self.run_alone()
        self.assertEqual([(s.name, s.status) for s in stages],
                         [("board", "ok"), ("parts", "skipped"), ("schematic", "skipped"), ("footprint", "skipped"),
                          ("build", "skipped"), ("simulation", "ok")])
        diagram = json.loads((workdir / "sim" / "diagram.json").read_text())
        self.assertEqual([part["type"] for part in diagram["parts"]], ["board-xiao-esp32-c6"])
        self.assertTrue((workdir / "sim" / "wokwi.toml").is_file())
        self.assertEqual(build_service.verdict(stages), check_spine.EXIT_OK)

    # --- MVP ---
    def test_the_board_alone_names_the_button_no_scenario_can_press(self):
        from test_boards import kept_definition_board
        workdir = Path(tempfile.mkdtemp())
        stages = build_service.board_alone(kept_definition_board(), workdir)
        self.assertEqual((stages[-1].name, stages[-1].status), ("simulation", check_spine.OK))
        self.assertIn("ONBOARD_BUTTON (GPIO9): the Wokwi definition of xiao-esp32-c6 has no pin on GPIO9", stages[-1].detail)
        self.assertIn("ONBOARD_BUTTON (GPIO9)", (workdir / "sim" / "WHAT-THIS-CANNOT-SHOW.md").read_text())
        self.assertEqual(build_service.verdict(stages), check_spine.EXIT_OK)

    def test_the_board_alone_warns_of_no_serial_monitor_unless_the_record_says_it_needs_no_wires(self):
        # P468: the XIAO's USB serial needs no wires, so only a record without the fact keeps the warning
        for fact, warned in ((True, False), (None, True)):
            board = board_records.load(ROOT, "xiao-esp32-c6")
            board.pop("serial_without_wires", None)
            if fact:
                board["serial_without_wires"] = fact
            stages = build_service.board_alone(board, Path(tempfile.mkdtemp()))
            self.assertEqual("no serial monitor is wired in the diagram" in stages[-1].detail, warned)

    def test_a_definition_not_checked_is_said_in_json_and_still_exits_0(self):
        # The suite's scratch store holds no Wokwi definition, so the library XIAO's line is "not checked".
        workdir = Path(tempfile.mkdtemp())
        (workdir / "requirements.json").write_text(json.dumps({"board": "xiao-esp32-c6", "parts": [], "board_only": True}))
        done = subprocess.run([sys.executable, str(ROOT / "scripts" / "check_spine.py"), str(workdir / "requirements.json"),
                               "--json"], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)
        simulation = json.loads(done.stdout)["stages"][-1]
        self.assertEqual(simulation["status"], "ok")
        self.assertIn("onboard GPIOs: not checked: spark's store lacks the Wokwi definition", simulation["detail"])
    # --- end MVP ---

    # --- MVP ---
    def test_a_board_without_the_onboard_levels_builds_ok_and_says_what_is_missing_until_the_person_tells_it(self):
        # P464 (#632): the firmware used to guess the LED and button levels; now the build names the gap and `--fact-set` fills it
        from spark.core.result import OperationResult, envelope_item
        from test_missing_facts import levelless
        project = Path(tempfile.mkdtemp()) / "project"
        (project / "boards").mkdir(parents=True)
        (project / ".spark").mkdir()
        board = levelless()
        board["id"] = "levelless-board"
        (project / "boards" / "levelless-board.json").write_text(json.dumps(board))
        (project / "requirements.json").write_text(json.dumps({"board": "levelless-board", "parts": [], "board_only": True}))
        into = project / "kept"

        def build():
            with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()) as err:
                code = check_spine.main([str(project / "requirements.json"), "--keep", str(into), "--json"])
            return code, json.loads(out.getvalue()), err.getvalue()

        code, said, err = build()
        pins = next(entry for entry in said["kept"] if entry["file"].endswith("pins.py"))
        expected = [envelope_item(each) for each in missing_facts.list_missing_facts(board)]
        self.assertEqual((code, said["status"], pins["did"], len(expected)), (0, "ok", "wrote", 2))
        self.assertEqual(pins["missing_facts"], expected)
        self.assertEqual(said["missing_facts"], expected)  # P464: beside `unserved`, so a caller reads it after `status`
        self.assertEqual(pins["missing_facts"], OperationResult(None, missing_facts.list_missing_facts(board)).to_envelope("t", "t")["unchecked"])
        self.assertIn("missing fact: %s. %s" % (expected[0]["sentence"], expected[0]["fix"]), err)
        text = (into / "firmware" / "pins.py").read_text()
        self.assertNotIn("ONBOARD_LED_ON", text)
        levels = project / "levels.json"
        levels.write_text(json.dumps({"pin_roles": {role: {"active_level": {"value": 0, "verified": True, "source": "the bench"}}
                                                    for role in ("onboard_led", "onboard_button")}}))
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(parts.main(["--fact-set", "levelless-board", str(levels), "--project", str(project), "--json"]), 0)
        code, said, _ = build()
        self.assertEqual(code, 0)
        self.assertNotIn("missing_facts", next(entry for entry in said["kept"] if entry["file"].endswith("pins.py")))
        self.assertNotIn("missing_facts", said)
        names = {}
        exec((into / "firmware" / "pins.py").read_text(), names)
        self.assertEqual((names["ONBOARD_LED_ON"], names["ONBOARD_BUTTON_ON"]), (0, 0))

    def test_a_build_without_keep_gives_no_missing_facts_yet(self):
        # P464 rows 1 and 2: the docs say the key comes with --keep, so this pins the absence the docs name
        from test_missing_facts import levelless
        project = Path(tempfile.mkdtemp()) / "project"
        (project / "boards").mkdir(parents=True)
        (project / ".spark").mkdir()
        (project / "boards" / "levelless-board.json").write_text(json.dumps(dict(levelless(), id="levelless-board")))
        (project / "requirements.json").write_text(json.dumps({"board": "levelless-board", "parts": [], "board_only": True}))
        with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
            code = check_spine.main([str(project / "requirements.json"), "--json"])
        self.assertEqual(code, 0)
        self.assertNotIn("missing_facts", json.loads(out.getvalue()))

    def test_the_text_mode_says_each_missing_fact_on_stderr_and_keeps_stdout_to_the_verdict(self):
        # P464: no --json, so the person reads the gap from the kept line
        from test_missing_facts import levelless
        project = Path(tempfile.mkdtemp()) / "project"
        (project / "boards").mkdir(parents=True)
        (project / ".spark").mkdir()
        board = levelless()
        board["id"] = "levelless-board"
        (project / "boards" / "levelless-board.json").write_text(json.dumps(board))
        (project / "requirements.json").write_text(json.dumps({"board": "levelless-board", "parts": [], "board_only": True}))
        with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()) as err:
            code = check_spine.main([str(project / "requirements.json"), "--keep", str(project / "kept")])
        self.assertEqual(code, 0)
        found = missing_facts.list_missing_facts(board)
        self.assertEqual(len(found), 2)
        for each in found:
            self.assertIn("\n  missing fact: %s. %s" % (each.sentence, each.fix), err.getvalue())
        self.assertNotIn("missing fact", out.getvalue())
    # --- end MVP ---

    def test_the_verdict_says_the_board_alone_ran(self):
        _, stages = self.run_alone()
        said = check_spine.render(stages, build_service.verdict(stages))
        self.assertIn("[--  ] build", said)
        self.assertIn("the chain runs end to end for the board alone", said)

    def test_a_board_wokwi_cannot_show_is_could_not_run(self):
        board = {"name": "No Wokwi Board"}
        stages = build_service.board_alone(board, Path(tempfile.mkdtemp()))
        self.assertEqual((stages[-1].name, stages[-1].status), ("simulation", check_spine.COULD_NOT_RUN))

    def test_the_breadboard_line_says_there_is_nothing_to_wire(self):
        workdir, stages = self.run_alone()
        kept = kept_files.keep_breadboard(workdir / "requirements.json", workdir, stages)
        self.assertEqual([entry["line"] for entry in kept], ["no breadboard sheet: board only: nothing to wire",
                                                             "no drawn breadboard: board only: nothing to wire",
                                                             "no breadboard picture: board only: nothing to wire"])

    def test_the_store_is_never_told_a_board_alone_was_built(self):
        _, stages = self.run_alone()
        self.assertFalse(build_service.vouches_for_a_build(stages))
        self.assertTrue(build_service.vouches_for_a_build([Stage("build", check_spine.OK)]))

    def test_an_earlier_build_s_dist_is_removed_and_said(self):
        workdir, stages = self.run_alone()
        (workdir / "dist" / "board").mkdir(parents=True)
        kept = kept_files.drop_an_older_build(workdir, stages)
        self.assertEqual([entry["did"] for entry in kept], ["removed"])
        self.assertFalse((workdir / "dist").exists())
        self.assertEqual(kept_files.drop_an_older_build(workdir, [Stage("build", check_spine.OK)]), [])

    def test_a_string_true_is_not_board_only(self):
        _, stages = self.run_alone(board_only="true")
        self.assertEqual((stages[-1].name, stages[-1].status), ("parts", check_spine.COULD_NOT_RUN))

    def test_the_json_says_ok_and_each_skipped_stage(self):
        workdir = Path(tempfile.mkdtemp())
        (workdir / "requirements.json").write_text(json.dumps({"board": "xiao-esp32-c6", "parts": [], "board_only": True}))
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            code = check_spine.main([str(workdir / "requirements.json"), "--json"])
        said = json.loads(out.getvalue())
        self.assertEqual((code, said["status"]), (0, "ok"))
        self.assertEqual([s["status"] for s in said["stages"]].count("skipped"), 4)

    def test_board_only_with_parts_is_refused(self):
        _, stages = self.run_alone(parts=["tactile-button"])
        self.assertEqual((stages[-1].name, stages[-1].status), ("parts", check_spine.COULD_NOT_RUN))
        self.assertIn("board_only", stages[-1].detail)


class AnEmitBoardCrashIsNotADesignFaultTest(unittest.TestCase):
    """F5: a crash inside the board emitter is could-not-run, never problems (`test_build_service` drives it with a fake
    emitter, P706); here the control: a refusal of the input, in the emitter's own words."""

    def test_a_refusal_of_the_generator_is_could_not_run_in_its_own_words(self):
        # the control: the emitter refusing the input, and its sentence is the stage's detail, whole
        workdir = Path(tempfile.mkdtemp())
        requirements = {"board": "xiao-esp32-c6", "parts": ["led-red-5mm"]}
        (workdir / "requirements.json").write_text(json.dumps(requirements))
        # the board with the gap is the project's own
        import shutil
        from board_library import library_without
        (workdir / "boards").mkdir()
        shutil.copy(library_without("power.io_volts") / "xiao-esp32-c6.json", workdir / "boards")
        stages = build_stages(requirements, workdir, project=workdir)
        self.assertEqual((stages[-1].name, stages[-1].status), ("schematic", check_spine.COULD_NOT_RUN))
        self.assertTrue(stages[-1].detail.startswith("cannot emit a board: led-red-5mm asks for 5 mA"), stages[-1].detail)


class ABoardWithNoFootprintStopsAtTheFootprintStageTest(unittest.TestCase):
    """P407: a board record that cannot give a footprint stops at the footprint stage, names each gap, and says what
    the build still gives a breadboard user."""

    HINT = ("The schematic was not tried. The pin map needs no footprint: with --keep, the kept lines say whether "
            "firmware/pins.py was written. The breadboard sheet and the simulation read the built board, so they wait "
            "for the footprint.")

    def project_without(self, *fields, requirements=None):
        """A project (it holds .spark/) whose own XIAO record lacks each dotted field, with its requirements file."""
        import shutil
        from board_library import library_without
        project = Path(tempfile.mkdtemp()) / "project"
        (project / ".spark").mkdir(parents=True)
        (project / "boards").mkdir()
        record_file = project / "boards" / "xiao-esp32-c6.json"
        shutil.copy(library_without(fields[0]) / "xiao-esp32-c6.json", record_file)
        record = json.loads(record_file.read_text())
        for field in fields[1:]:
            *parents, last = field.split(".")
            holder = record
            for key in parents:
                holder = holder[key]
            del holder[last]
        record_file.write_text(json.dumps(record, indent=2) + "\n")
        wanted = requirements or {"board": "xiao-esp32-c6", "parts": ["led-red-5mm"]}
        (project / "requirements.json").write_text(json.dumps(wanted))
        return project, wanted

    def run_spine(self, project, wanted):
        """The build as `main` runs it: the requirements file in the work folder, the project's own board."""
        workdir = Path(tempfile.mkdtemp())
        (workdir / "requirements.json").write_text(json.dumps(wanted))
        return build_stages(wanted, workdir, project=project)

    def test_no_header_stops_at_the_footprint_stage_and_says_what_still_comes(self):
        project, wanted = self.project_without("physical.header")
        stages = self.run_spine(project, wanted)
        self.assertEqual([(s.name, s.status) for s in stages], [("board", check_spine.OK), ("footprint", check_spine.COULD_NOT_RUN)])
        self.assertEqual(stages[-1].detail,
                         "xiao-esp32-c6 cannot have a footprint generated — these are not recorded, and none of them "
                         "can be derived from the rest:\n  physical.header (no header geometry at all)\n" + self.HINT)
        self.assertEqual(build_service.verdict(stages), check_spine.EXIT_COULD_NOT_RUN)

    def test_a_header_with_no_order_and_no_width_names_each_gap(self):
        project, wanted = self.project_without("physical.header_order", "physical.width_mm")
        stages = self.run_spine(project, wanted)
        self.assertEqual((stages[-1].name, stages[-1].status), ("footprint", check_spine.COULD_NOT_RUN))
        self.assertIn(":\n  physical.width_mm\n  physical.header_order (which label is on which pad — not derivable)\n",
                      stages[-1].detail)

    def edit_record(self, project, edit):
        record_file = project / "boards" / "xiao-esp32-c6.json"
        record = json.loads(record_file.read_text())
        edit(record)
        record_file.write_text(json.dumps(record, indent=2) + "\n")

    def test_a_board_that_disagrees_with_itself_says_how_at_the_footprint_stage(self):
        # P411: the stage said "no footprint could be generated for xiao-esp32-c6", and nothing of what to change
        project, wanted = self.project_without("physical.header.drill_mm")
        self.edit_record(project, lambda record: record["physical"]["header"].update(pins=[6, 6]))
        stages = self.run_spine(project, wanted)
        self.assertEqual([(s.name, s.status) for s in stages][-2:], [("schematic", check_spine.OK), ("footprint", check_spine.COULD_NOT_RUN)])
        self.assertEqual(stages[-1].detail,
                         "the board definition disagrees with itself: header_order.row_left has 7 labels but physical.header.pins says 6 "
                         "— one of the two is wrong, and guessing which would shift every pad after the disagreement")

    def test_a_value_of_the_wrong_kind_in_the_header_stops_the_footprint_stage_too(self):
        # the board file's validation checks no header geometry: a pitch written as text was a TypeError out of the build
        project, wanted = self.project_without("physical.header.drill_mm")
        self.edit_record(project, lambda record: record["physical"]["header"].update(pitch_mm="2.54"))
        stages = self.run_spine(project, wanted)
        self.assertEqual((stages[-1].name, stages[-1].status, stages[-1].detail),
                         ("footprint", check_spine.COULD_NOT_RUN,
                          "the board definition disagrees with itself: physical.header.pitch_mm is not a finite number\n" + self.HINT))

    # --- MVP ---
    def test_a_huge_width_stops_the_footprint_stage_naming_the_field(self):
        # P434: a 400-digit width was an OverflowError out of `board_components.place`, a "crashed" schematic stage
        project, wanted = self.project_without("physical.header.drill_mm")
        self.edit_record(project, lambda record: record["physical"].update(width_mm=10 ** 400))
        stages = self.run_spine(project, wanted)
        self.assertEqual((stages[-1].name, stages[-1].status, stages[-1].detail),
                         ("footprint", check_spine.COULD_NOT_RUN,
                          "the board definition disagrees with itself: physical.width_mm is not a finite number\n" + self.HINT))

    def test_a_project_rule_of_the_wrong_kind_stops_the_inputs_read_naming_the_file(self):
        project, wanted = self.project_without("physical.header.drill_mm")
        (project / ".spark" / "rules.json").write_text(json.dumps({"fabrication": {"drill_step_mm": "0.1"}}))
        workdir, stages = self.run_to_the_footprint(project, wanted)
        self.assertEqual((stages[-1].name, stages[-1].status), ("schematic", check_spine.COULD_NOT_RUN))
        self.assertIn("fabrication.drill_step_mm is not a finite number", stages[-1].detail)
        self.assertEqual(list(workdir.glob("*.tsx")), [])

    def run_to_the_footprint(self, project, wanted):
        """The build with the board engine missing, so it stops after the footprint stage: (the work folder, its stages)."""
        workdir = Path(tempfile.mkdtemp())
        (workdir / "requirements.json").write_text(json.dumps(wanted))
        with mock.patch.object(board_engine, "find_toolchain", return_value=None):
            return workdir, build_stages(wanted, workdir, project=project)

    # --- MVP --- (P432, OC2)
    def test_the_spine_writes_the_footprint_without_calling_the_footprint_cli(self):
        project, wanted = self.project_without("physical.header.drill_mm")
        with mock.patch.object(emit_footprint, "main", side_effect=AssertionError("the footprint CLI ran")):
            workdir, stages = self.run_to_the_footprint(project, wanted)
        footprint = [stage for stage in stages if stage.name == "footprint"]
        self.assertEqual([stage.status for stage in footprint], [check_spine.OK])
        self.assertTrue((workdir / footprint[0].detail).is_file())

    def test_the_spine_s_footprint_is_byte_equal_to_the_cli_s(self):
        project, wanted = self.project_without("physical.header.drill_mm")
        # a drill step of 0.3 mm draws a 1.2 mm hole where the default draws 1.0 mm, so the rules show in the bytes
        (project / ".spark" / "rules.json").write_text(json.dumps({"fabrication": {"drill_step_mm": 0.3}}))
        workdir, stages = self.run_to_the_footprint(project, wanted)
        written = (workdir / [stage for stage in stages if stage.name == "footprint"][0].detail).read_text()
        self.assertNotEqual(written, build_service.footprint_emitter.render(
            board_records.load(project, "xiao-esp32-c6"), None))
        with contextlib.redirect_stdout(io.StringIO()) as printed:
            code = emit_footprint.main(["--board", "xiao-esp32-c6", "--project", str(project)])
        self.assertEqual(code, 0)
        self.assertEqual(written, printed.getvalue())

    def test_the_spine_writes_no_footprint_for_a_board_that_disagrees_with_itself(self):
        project, wanted = self.project_without("physical.header.drill_mm")
        self.edit_record(project, lambda record: record["physical"]["header"].update(pitch_mm="2.54"))
        workdir, stages = self.run_to_the_footprint(project, wanted)
        self.assertEqual(stages[-1].name, "footprint")
        self.assertEqual(list(workdir.glob("*.tsx")), [])  # P434: it stops before the schematic is written, as a missing fact does

    def test_an_unreadable_rules_file_stops_the_build_naming_the_file_and_is_not_no_rules(self):
        project, wanted = self.project_without("physical.header.drill_mm")
        (project / ".spark" / "rules.json").write_text("{not json")
        workdir, stages = self.run_to_the_footprint(project, wanted)
        self.assertEqual((stages[-1].name, stages[-1].status), ("schematic", check_spine.COULD_NOT_RUN))
        self.assertIn("rules.json could not be read", stages[-1].detail)
        self.assertEqual(list(workdir.glob("*.tsx")), [])

    def test_the_board_alone_needs_no_footprint(self):
        # the stop comes after the board-only branch: a board with no header still simulates on its own
        project, wanted = self.project_without("physical.header", requirements={"board": "xiao-esp32-c6", "parts": [],
                                                                                "board_only": True})
        stages = self.run_spine(project, wanted)
        self.assertEqual([(s.name, s.status) for s in stages],
                         [("board", "ok"), ("parts", "skipped"), ("schematic", "skipped"), ("footprint", "skipped"),
                          ("build", "skipped"), ("simulation", "ok")])

    def test_a_part_that_is_not_in_the_library_is_said_before_the_footprint(self):
        project, wanted = self.project_without("physical.header", requirements={"board": "xiao-esp32-c6",
                                                                                "parts": ["no-such-part"]})
        stages = self.run_spine(project, wanted)
        self.assertEqual([(s.name, s.status) for s in stages], [("board", "ok"), ("parts", "could-not-run")])

    def keep_through_main(self, project):
        """`main` with --json --keep into the project, unmocked: the stop comes before any toolchain is needed."""
        home = Path(tempfile.mkdtemp())
        with mock.patch.dict(os.environ, {"SPARK_HOME": str(home)}), \
                contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
            check_spine.main([str(project / "requirements.json"), "--json", "--keep", str(project)])
        return json.loads(out.getvalue())

    def test_with_keep_the_pin_map_is_written_and_no_breadboard_sheet(self):
        project, _ = self.project_without("physical.header")
        said = self.keep_through_main(project)
        self.assertEqual((said["status"], said["stages"][-1]["name"]), ("could-not-run", "footprint"))
        self.assertTrue(said["stages"][-1]["detail"].endswith("\n" + self.HINT), said["stages"][-1]["detail"])
        self.assertEqual([entry["did"] for entry in said["kept"] if entry["file"].endswith("pins.py")], ["wrote"])
        self.assertTrue((project / "firmware" / "pins.py").is_file())
        self.assertFalse((project / "breadboard.md").exists())

    def test_a_fault_in_the_requirements_is_said_before_the_footprint(self):
        # the refuter: the footprint stop hid what emit_board says first, so a person fixed the board and met the typo.
        # Reading the input and placing the pins come first, as in emit_board, then the footprint, then the rest.
        for extra, fields, said in (
                ({"signals": [{"name": "X", "needs": ["teleport"]}]}, (), "X asks for teleport"),
                ({"parts": [{"part": "led-red-5mm", "name": "A"}, {"part": "led-red-5mm", "name": "A"}]}, (),
                 "parts[0] is called A and parts[1] A")):
            with self.subTest(said=said):
                project, wanted = self.project_without("physical.header", *fields, requirements=dict(
                    {"board": "xiao-esp32-c6", "parts": ["led-red-5mm"]}, **extra))
                stages = self.run_spine(project, wanted)
                self.assertEqual([(s.name, s.status) for s in stages], [("board", "ok"), ("schematic", "could-not-run")])
                self.assertTrue(stages[-1].detail.startswith("cannot emit a board: "), stages[-1].detail)
                self.assertIn(said, stages[-1].detail)

    def test_the_stop_says_what_read_inputs_says_on_the_same_project(self):
        # P432: the spine and emit_board refuse in one order, with one function's words; `first` is each case's literal start
        typo = {"signals": [{"name": "X", "needs": ["teleport"]}]}
        gap = "xiao-esp32-c6 cannot have a footprint generated — these are not recorded"
        for fields, extra, first in ((("physical.header",), typo, "cannot emit a board: X asks for teleport, which is not"),
                                     (("physical.header",), {}, gap),
                                     (("physical.width_mm", "physical.header_order"), {}, gap)):
            with self.subTest(fields=fields, extra=extra):
                project, wanted = self.project_without(*fields, requirements=dict(
                    {"board": "xiao-esp32-c6", "parts": ["led-red-5mm"]}, **extra))
                with self.assertRaises(board_emitter.RefusedInputError) as refused:
                    board_emitter.read_inputs(project / "requirements.json", project)
                self.assertTrue(str(refused.exception).startswith(first), str(refused.exception))
                stages = self.run_spine(project, wanted)
                self.assertEqual(stages[-1].name, refused.exception.stage)
                self.assertTrue(stages[-1].detail.startswith(first), stages[-1].detail)
                # only the footprint stop is followed by what the build still gives
                after = "\n" + self.HINT if refused.exception.stage == "footprint" else ""
                self.assertEqual(stages[-1].detail, str(refused.exception) + after)

    def test_a_crash_in_reading_the_input_is_a_stage_and_keeps_the_stages_before_it(self):
        # P432: emit_board ran in a child, so an exception it did not foresee was a stage and not a lost run. A bus written
        # as a list is one (a pin as a list is refused where the file is read, P438).
        project, wanted = self.project_without("physical.header.drill_mm", requirements={
            "board": "xiao-esp32-c6", "parts": ["tactile-button", "led-red-5mm"],
            "signals": [{"name": "X", "needs": ["adc"], "bus": ["i2c"]}]})
        stages = self.run_spine(project, wanted)
        self.assertEqual([(s.name, s.status) for s in stages], [("board", "ok"), ("schematic", check_spine.COULD_NOT_RUN)])
        self.assertEqual(stages[-1].detail, "the board emitter crashed: TypeError: unhashable type: 'list'")

    def test_a_crash_in_drawing_the_footprint_is_a_stage_and_keeps_the_stages_before_it(self):
        project, wanted = self.project_without("physical.header.drill_mm")
        with mock.patch.object(build_service.footprint_emitter, "render", side_effect=ZeroDivisionError("a fault of its own")):
            workdir, stages = self.run_to_the_footprint(project, wanted)
        self.assertEqual([(s.name, s.status) for s in stages],
                         [("board", "ok"), ("schematic", "ok"), ("footprint", check_spine.COULD_NOT_RUN)])
        self.assertEqual(stages[-1].detail, "the footprint emitter crashed: ZeroDivisionError: a fault of its own")

    def said_by_report(self, stages, as_json):
        """`report` for a verdict: what it printed on stdout. A --json run is read back."""
        args = argparse.Namespace(json=as_json, keep=None)
        with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
            check_spine.report(stages, args)
        return json.loads(out.getvalue()) if as_json else out.getvalue()

    # --- MVP --- (P430, #569) a crash's text is stored raw and guarded where it is printed
    def test_a_crash_in_drawing_the_footprint_keeps_its_text_raw_and_the_screen_shows_it_guarded(self):
        project, wanted = self.project_without("physical.header.drill_mm")
        with mock.patch.object(build_service.footprint_emitter, "render", side_effect=RuntimeError("a\u202e\x1bb")):
            _, stages = self.run_to_the_footprint(project, wanted)
        self.assertEqual(stages[-1].detail, "the footprint emitter crashed: RuntimeError: a\u202e\x1bb")
        self.assertEqual(self.said_by_report(stages, True)["stages"][-1]["detail"], stages[-1].detail)
        self.assertIn("the footprint emitter crashed: RuntimeError: a??b", self.said_by_report(stages, False))

    def test_a_crash_in_reading_the_input_keeps_its_text_raw_and_the_screen_shows_it_guarded(self):
        project, wanted = self.project_without("physical.header.drill_mm")
        with mock.patch.object(build_service.board_emitter, "read_inputs", side_effect=ValueError("a\u202e\x1bb")):
            stages = self.run_spine(project, wanted)
        self.assertEqual(stages[-1].detail, "the board emitter crashed: ValueError: a\u202e\x1bb")
        self.assertEqual(self.said_by_report(stages, True)["stages"][-1]["detail"], stages[-1].detail)
        self.assertIn("the board emitter crashed: ValueError: a??b", self.said_by_report(stages, False))

    def test_a_newline_in_a_crash_message_shows_as_a_line_break_in_the_text(self):
        # The decided residual (P430): the text keeps a message's own newlines, so a second line can look like a stage.
        # Only a --json reader gets one detail, whole.
        project, wanted = self.project_without("physical.header.drill_mm")
        with mock.patch.object(build_service.footprint_emitter, "render", side_effect=RuntimeError("a\nb")):
            _, stages = self.run_to_the_footprint(project, wanted)
        self.assertIn("crashed: RuntimeError: a\nb\n", self.said_by_report(stages, False))
        self.assertEqual(self.said_by_report(stages, True)["stages"][-1]["detail"], "the footprint emitter crashed: RuntimeError: a\nb")

    def test_a_fault_in_the_requirements_is_said_without_asking_emit_board(self):
        project, wanted = self.project_without("physical.header_order", requirements={
            "board": "xiao-esp32-c6", "parts": ["led-red-5mm"], "signals": [{"name": "X", "needs": ["teleport"]}]})
        with mock.patch.object(board_emitter.BoardEmitter, "emit", side_effect=AssertionError("the board was emitted")):
            stages = self.run_spine(project, wanted)
        self.assertEqual((stages[-1].name, stages[-1].status), ("schematic", check_spine.COULD_NOT_RUN))
        self.assertIn("X asks for teleport", stages[-1].detail)

    def test_pins_that_cannot_be_placed_write_no_pin_map(self):
        project, _ = self.project_without("physical.header", requirements={
            "board": "xiao-esp32-c6", "parts": ["led-red-5mm"], "signals": [{"name": "X", "needs": ["teleport"]}]})
        said = self.keep_through_main(project)
        self.assertEqual(said["stages"][-1]["name"], "schematic")
        self.assertEqual([entry["did"] for entry in said["kept"] if entry["file"].endswith("pins.py")], ["not written"])
        self.assertFalse((project / "firmware" / "pins.py").exists())


class AConverterLimitIsNotADesignFaultTest(unittest.TestCase):
    def test_a_component_the_converter_cannot_map_is_could_not_look(self):
        # The RC car builds (13 traces) and the converter has no Wokwi part for its servo, buck
        # and inlet; that read as `!! simulation … the chain is broken` (audit B11).
        said = ("3 problem(s) converting the board:\n  - no Wokwi part is mapped to this component. "
                "Add it to lib/mapping.ts, or add a skip rule (component Sg90Servo)")
        self.assertTrue(board_engine.simulation_could_not_look(said))

    def test_any_other_converter_failure_is_still_a_problem(self):
        self.assertFalse(board_engine.simulation_could_not_look("TypeError: cannot read x of undefined"))
        self.assertFalse(board_engine.simulation_could_not_look(""))
        self.assertFalse(board_engine.simulation_could_not_look(None))


class AFileInNoProjectIsSaidToBeTest(unittest.TestCase):
    def test_the_board_stage_says_the_design_came_from_the_library(self):
        # P22: from nowhere the spine builds from the plugin's library; that is a fact about how
        # the design was resolved, said on the board stage — never a `!!` note about the design.
        # The reference design, which sources its own rails: a driver alone would earn a real
        # `!!` note about an unsourced motor rail, which is the design's and not this test's.
        workdir = Path(tempfile.mkdtemp())
        requirements = dict(requirements_build.REFERENCE)
        (workdir / "requirements.json").write_text(json.dumps(requirements))
        with mock.patch.object(board_engine, "find_toolchain", return_value=None):
            stages = build_stages(requirements, workdir, from_library=True)
        self.assertIn("plugin's library", stages[0].detail)
        self.assertEqual(stages[0].status, check_spine.OK)
        self.assertNotIn("schematic-notes", [s.name for s in stages])


class AMissingBoardEngineSaysWhatTheToolsListSaysTest(unittest.TestCase):
    """The cold run (P82 task 7): with bun missing the build said "npm i -g @tscircuit/cli" — a global
    install the tools list does not ask for, and not the thing that was missing."""

    def test_the_build_stage_carries_the_tools_list_s_sentence(self):
        from spark.records import tool_finder
        workdir = Path(tempfile.mkdtemp())
        requirements = dict(requirements_build.REFERENCE)
        (workdir / "requirements.json").write_text(json.dumps(requirements))
        said = "tscircuit needs bun: bun (bun) is not installed — install: npm install -g bun"
        missing = FakeToolFinder({"board-engine": tool_finder.ToolError(said, code="tool_missing")}).find
        with mock.patch.object(board_engine, "find_toolchain", return_value=None):
            stages = build_stages(requirements, workdir, from_library=True, find_tool=missing)
        build = [stage for stage in stages if stage.name == "build"][0]
        self.assertEqual(build.status, check_spine.COULD_NOT_RUN)
        self.assertIn("npm install -g bun", build.detail)
        self.assertNotIn("npm i -g", build.detail)

class TheFinalReviewAtTheEntryPointsTest(unittest.TestCase):
    """The whole-branch review (2026-10-03): the expectations held in tool_finder.find and broke at the real entry
    points."""

    def broken_home(self):
        home = Path(tempfile.mkdtemp())
        (home / ".local" / "share" / "spark").mkdir(parents=True)
        (home / ".local" / "share" / "spark" / "tools.json").write_text('{"tscircuit": {"core": "0.0.1",}}')
        return home

    def test_a_broken_personal_file_is_named_by_the_build_stage(self):
        from spark.records import tool_finder
        workdir = Path(tempfile.mkdtemp())
        requirements = dict(requirements_build.REFERENCE)
        (workdir / "requirements.json").write_text(json.dumps(requirements))
        with mock.patch.object(tool_finder, "PERSONAL",
                               self.broken_home() / ".local" / "share" / "spark" / "tools.json"):
            stages = build_stages(requirements, workdir, from_library=True)
        build = [stage for stage in stages if stage.name == "build"][0]
        self.assertEqual(build.status, check_spine.COULD_NOT_RUN)
        self.assertIn("is not JSON", build.detail)

    def test_a_broken_project_file_is_named_not_reported_as_a_missing_engine(self):
        project = Path(tempfile.mkdtemp())
        (project / ".spark").mkdir()
        (project / ".spark" / "tools.json").write_text('{"tscircuit": {"core": "0.0.1",}}')
        workdir = Path(tempfile.mkdtemp())
        requirements = dict(requirements_build.REFERENCE)
        (workdir / "requirements.json").write_text(json.dumps(requirements))
        with mock.patch.object(board_engine, "find_toolchain", return_value=None):
            stages = build_stages(requirements, workdir, project=project, from_library=True)
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
        self.assertIsNone(board_engine.find_converter(ROOT / "scripts"))
        self.assertIsNone(board_engine.find_converter(ROOT))

    def test_a_project_s_own_converter_runs_with_the_ts_runtime_from_the_list(self):
        from spark.records import tool_finder
        own = Path(tempfile.mkdtemp()) / "cli.ts"
        bun = tool_finder.Tool("bun", "ts-runtime", {"kind": "path"}, ["/opt/bun"])
        finder = FakeToolFinder({"ts-runtime": bun})
        self.assertEqual(board_engine.converter_command(None, own, finder.find), ["/opt/bun", "run", str(own)])
        self.assertEqual(finder.asked[0][0], "ts-runtime")

    def test_the_converter_the_list_names_is_the_one_that_runs(self):
        from spark.records import tool_finder
        swapped = tool_finder.Tool("my-conv", "diagram-converter", {"kind": "path"}, ["/opt/my-conv"])
        node = tool_finder.Tool("node", "js-runtime", {"kind": "path"}, ["/opt/node"])
        bundled = tool_finder.Tool("circuit-to-wokwi", "diagram-converter", {"kind": "bundled"},
                                   ["/plugin/converter.mjs"])
        self.assertEqual(board_engine.converter_command(None, None, FakeToolFinder({"diagram-converter": swapped, "js-runtime": node}).find),
                         ["/opt/my-conv"])
        self.assertEqual(board_engine.converter_command(None, None, FakeToolFinder({"diagram-converter": bundled, "js-runtime": node}).find),
                         ["/opt/node", "/plugin/converter.mjs"])

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
        import shutil
        import subprocess
        if not shutil.which("node"):
            self.skipTest("node is not installed")
        alone = Path(tempfile.mkdtemp()) / "converter.mjs"
        shutil.copy(self.BUNDLE, alone)
        done = subprocess.run(["node", str(alone)], capture_output=True, text=True, timeout=60)
        said = done.stdout + done.stderr
        self.assertNotIn("Cannot find package", said)
        self.assertIn("SPARK_BOARD_JSON is not set", said, "it loaded every module and reached its own first check")

    def test_no_node_means_could_not_run_naming_the_install(self):
        from spark.records import tool_finder
        missing = tool_finder.ToolError("js-runtime (node) is not installed — install: brew install node",
                                          code="tool_missing")
        stage = board_engine.converter_stage_problem(Path(tempfile.mkdtemp()), find_tool=FakeToolFinder({"diagram-converter": missing}).find)
        self.assertEqual(stage.status, check_spine.COULD_NOT_RUN)
        self.assertIn("brew install node", stage.detail)

    def test_the_converter_present_and_node_missing_is_could_not_run(self):
        from spark.records import tool_finder
        real = tool_finder.find

        no_node = FakeToolFinder({"js-runtime": tool_finder.ToolError("js-runtime (node) is not installed — install: brew install node",
                                                                      code="tool_missing")}, fall_back=real)
        stage = board_engine.converter_stage_problem(Path(tempfile.mkdtemp()), find_tool=no_node.find)
        self.assertIsNotNone(stage, "the bundle is here and Node is not: the converter cannot run")
        self.assertIn("brew install node", stage.detail)

    def test_the_plugin_s_converter_is_the_bundle(self):
        from spark.records import tool_finder
        self.assertEqual(tool_finder.find("diagram-converter", None, Path(tempfile.mkdtemp()) / "absent.json").command,
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
        with mock.patch.object(requirements_build, "BuildService", FakeBuildService(lambda *_, **__: stages)), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            check_spine.main([str(self.project / "requirements.json")])
        path = self.home / "history.jsonl"
        return [json.loads(line) for line in path.read_text().splitlines()] if path.is_file() else []

    def answer(self, argv=None):
        """What `check_spine.main` returned and said, stdout then stderr, for a chain whose every stage ended ok."""
        stages = [stage(name, check_spine.OK) for name in ("board", "schematic", "footprint", "build", "simulation")]
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(requirements_build, "BuildService", FakeBuildService(lambda *_, **__: stages)), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = check_spine.main([str(self.project / "requirements.json")] if argv is None else argv)
        return code, out.getvalue(), err.getvalue()

    def meanwhile(self, happens):
        """The history after `check_spine.main` on the person's file, whose chain ends ok and, while it builds, has `happens()` happen."""
        stages = [stage(name, check_spine.OK) for name in ("board", "schematic", "footprint", "build", "simulation")]

        def build(*_, **__):
            happens()
            return stages
        with mock.patch.object(requirements_build, "BuildService", FakeBuildService(build)), \
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
        handed = loader.firmware_pulls(button, board)  # P204: the part as the chain was handed it, on this board
        self.assertEqual((built["board"]["digest"], built["parts"][0]["digest"]),
                         (self.digest_of(board, ("pins", "power_pads", "physical")),
                          self.digest_of(handed, ("needs", "power", "unused_pins", "pin_order", "footprint", "host_parts"))))

    def test_what_the_chain_was_handed_is_what_is_recorded_not_what_the_file_became_meanwhile(self):
        def the_person_edits_the_file():
            (self.project / "requirements.json").write_text(json.dumps({"board": "firebeetle2-esp32s3", "parts": ["l9110s-module"]}))
        built = self.meanwhile(the_person_edits_the_file)
        self.assertEqual([[p["id"] for p in e["parts"]] for e in built], [["tactile-button"]])

    def test_the_facts_recorded_are_those_the_chain_was_handed_not_those_a_record_became_meanwhile(self):
        def the_person_edits_a_record():
            record = json.loads((ROOT / "parts" / "tactile-button.json").read_text())
            record["footprint"] = "pushbutton_id1.2_od2"  # a fact the board's choice of pull-up does not touch (P204)
            (self.project / "parts").mkdir()
            (self.project / "parts" / "tactile-button.json").write_text(json.dumps(record))
        built = self.meanwhile(the_person_edits_a_record)
        button = json.loads((ROOT / "parts" / "tactile-button.json").read_text())
        board = json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())
        self.assertEqual([e["parts"][0]["digest"] for e in built],
                         [self.digest_of(loader.firmware_pulls(button, board),
                                         ("needs", "power", "unused_pins", "pin_order", "footprint", "host_parts"))])

    def test_a_design_that_cannot_be_loaded_records_nothing_and_breaks_nothing(self):
        (self.project / "requirements.json").write_text(json.dumps({"board": "firebeetle2-esp32s3", "parts": ["no-such-part"]}))
        code, said, _ = self.answer()
        self.assertEqual((code, "the chain runs end to end" in said, (self.home / "history.jsonl").exists()), (0, True, False))
        (self.project / "requirements.json").write_text(json.dumps({"board": "firebeetle2-esp32s3", "parts": ["tactile-button"]}))
        with mock.patch.object(requirements_build.loader, "load", side_effect=TypeError("a record of a shape nobody foresaw")):
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
        loaded = loader.load(self.project / "requirements.json", self.project)
        recorder = threading.Thread(target=part_facts.note_built, args=(loaded,))
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
        for refusal in (store.StoreError("the projects list is not JSON", code="record_file_broken"), OSError("the disk is full")):
            with self.subTest(refusal=refusal), mock.patch.object(requirements_build.part_facts, "note_built", side_effect=refusal):
                code, said, complained = self.answer()
                self.assertEqual((code, "the chain runs end to end" in said), (0, True))
                self.assertIn(str(refusal), complained)


    def test_a_reason_with_a_carriage_return_and_an_override_shows_as_question_marks_on_stderr(self):
        # P423: every text print of the script goes through guard_lines
        with mock.patch.object(requirements_build.part_facts, "note_built", side_effect=OSError("full\u202e\rdisk")):
            _, _, complained = self.answer()
        self.assertIn("  the build was not recorded in your history: full??disk\n", complained)


class ARequirementsBuildServiceTest(unittest.TestCase):
    """P783 PR 3: `requirements_build.RequirementsBuildService` is check_spine's whole run, given a fake BuildService
    (no patch): a refused file is one requirements stage and makes no work folder, a build past its limit and a crash
    are each one stage that could not run with its code, and a history it cannot keep is one diagnostics line."""

    def setUp(self):
        self.home, self.project = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp()) / "plant-alarm"
        (self.project / ".spark").mkdir(parents=True)
        self.requirements = self.project / "requirements.json"
        self.requirements.write_text(json.dumps({"board": "firebeetle2-esp32s3", "parts": ["tactile-button"]}))
        (self.home / "projects.json").write_text(json.dumps({"plant-alarm": str(self.project.resolve())}))
        patcher = mock.patch.dict(os.environ, {"SPARK_HOME": str(self.home)})
        patcher.start()
        self.addCleanup(patcher.stop)

    def run_with(self, build):
        """The RequirementsBuildResult of the person's file over a fake BuildService whose build is `build`; its work folder removed after."""
        run = requirements_build.RequirementsBuildService(FakeBuildService(build)).build(self.requirements)
        if run.workdir is not None:
            self.addCleanup(shutil.rmtree, run.workdir, True)
        return run

    def test_a_refused_file_is_one_requirements_stage_with_its_code_and_no_work_folder(self):
        self.requirements.write_text("{not json")
        folders = set(Path(tempfile.gettempdir()).glob("spark-spine-*"))
        run = self.run_with(lambda *_, **__: self.fail("the build ran on a refused file"))
        self.assertEqual([(stage.name, stage.status) for stage in run.stages], [("requirements", "could-not-run")])
        self.assertTrue(run.stages[0].code)
        self.assertEqual((run.workdir, run.requirements, run.toolchain, run.diagnostics), (None, None, None, []))
        self.assertEqual(set(Path(tempfile.gettempdir()).glob("spark-spine-*")), folders)

    def test_a_build_past_its_limit_is_stage_timed_out(self):
        def late(*_, **__):
            raise subprocess.TimeoutExpired(["/x/node_modules/.bin/tsci", "build"], 900)
        run = self.run_with(late)
        self.assertEqual([(stage.name, stage.status, stage.code) for stage in run.stages], [("build", "could-not-run", "stage_timed_out")])
        self.assertIn("`tsci build` did not finish in 900s", run.stages[0].detail)
        self.assertTrue(run.workdir.is_dir())

    def test_any_other_exception_is_stage_crashed(self):
        def broken(*_, **__):
            raise ValueError("a fault of its own")
        run = self.run_with(broken)
        self.assertEqual([(stage.name, stage.status, stage.code, stage.detail) for stage in run.stages],
                         [("check_spine", "could-not-run", "stage_crashed", "ValueError: a fault of its own")])

    def test_a_history_it_cannot_keep_is_one_diagnostics_line(self):
        (self.home / "history.jsonl").write_text("this is not an event\n")
        stages = [stage(name, check_spine.OK) for name in ("board", "schematic", "footprint", "build", "simulation")]
        run = self.run_with(lambda *_, **__: stages)
        self.assertEqual(run.stages, stages)
        self.assertEqual(len(run.diagnostics), 1)
        self.assertTrue(run.diagnostics[0].startswith("  the build was not recorded in your history: "), run.diagnostics)
        self.assertIn("history.jsonl line 1 is not a history event", run.diagnostics[0])


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
        self.assertEqual(build_service.islands_in(self.circuit()), ["SpeakerTerminal reaches no ground"])
        self.assertEqual(build_service.islands_in(self.circuit(), across=("SpeakerTerminal",)), [])
        self.assertEqual(build_service.islands_in(self.circuit(both_ends=False), across=("SpeakerTerminal",)),
                         ["SpeakerTerminal.SPK_N (a terminal connected to nothing)"])

    def test_the_build_stage_hands_the_loads_across_a_pair_to_the_island_check(self):
        root = Path(tempfile.mkdtemp())
        workdir = root / "work"
        workdir.mkdir()
        requirements = {"board": "firebeetle2-esp32s3", "parts": ["max98357a-dfr0954", "speaker-terminal"]}
        (workdir / "requirements.json").write_text(json.dumps(requirements))
        with mock.patch.object(build_service, "islands_in", return_value=[]) as islands:
            build_stages(requirements, workdir, toolchain=fake_tsci(root, "true"), from_library=True)
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
        with mock.patch.object(requirements_build, "BuildService", FakeBuildService(lambda *_, **__: stages)), contextlib.redirect_stdout(out), \
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

    def test_a_need_with_an_override_and_a_carriage_return_shows_as_question_marks_and_the_json_keeps_it(self):
        # P423: the verdict's text goes through guard_lines (its own newlines stay); --json carries the raw text
        unserved = [{"need": "soil\u202e\rx", "why": "no pick", "picks": []}]
        requirements = {"board": "firebeetle2-esp32s3", "parts": ["tactile-button"], "unserved": unserved}
        code, said = self.answer(requirements)
        self.assertEqual(code, 0)
        self.assertTrue(said.endswith("  the chain runs end to end — but not every need is on the board: soil??x (no pick)\n"), said)
        self.assertEqual(json.loads(self.answer(requirements, "--json")[1])["unserved"], unserved)

    def test_a_kept_line_with_an_override_shows_as_a_question_mark_on_stderr(self):
        stages = [stage("board", check_spine.OK)]
        args = argparse.Namespace(keep="kept", json=False, requirements=None, sim_dir=None)
        err = io.StringIO()
        with mock.patch.object(check_spine, "_kept", return_value=[{"file": "f", "did": "wrote", "why": "w", "line": "wrote a\u202eb"}]), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            check_spine.report(stages, args, workdir=Path(tempfile.mkdtemp()))
        self.assertEqual(err.getvalue(), "  wrote a?b\n")

    def test_a_file_that_leaves_nothing_off_says_the_verdict_alone(self):
        for requirements in ({"board": "firebeetle2-esp32s3", "parts": ["tactile-button"]},
                             {"board": "firebeetle2-esp32s3", "parts": ["tactile-button"], "unserved": []}):
            with self.subTest(requirements=requirements):
                code, said = self.answer(requirements)
                self.assertTrue(said.endswith("\n  the chain runs end to end\n"), said)
                self.assertNotIn("unserved", json.loads(self.answer(requirements, "--json")[1]))


class TheVerdictNamesTheFirmwareStepTest(unittest.TestCase):
    """P517 (#713): a build that reaches ok in a project names the step that comes next: write the firmware from the pin map."""

    WHY = "first write firmware/main.py from pins.py"

    def answer(self, stages, json_out=False, library=False, folder="lamp"):
        project = (Path(tempfile.mkdtemp()) / folder).resolve()
        project.mkdir()
        if not library:
            (project / ".spark").mkdir()
        args = argparse.Namespace(keep=None, json=json_out, requirements=str(project / "requirements.json"), sim_dir=None)
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            code = check_spine.report(stages, args)
        return code, out.getvalue(), project

    def ok(self):
        return [stage(name, check_spine.OK) for name in ("board", "schematic", "footprint", "build", "simulation")]

    def test_with_json_next_is_a_look_step_for_the_project(self):
        code, said, project = self.answer(self.ok(), True)
        step = json.loads(said)["next"]
        self.assertEqual(code, 0)
        self.assertEqual([(each["op"], each["why"]) for each in step], [("look", self.WHY)])
        self.assertEqual(Path(step[0]["argv"][1]).resolve(), project)
        self.assertEqual(step[0]["argv"][0], "--project")

    def test_the_text_ends_with_the_same_step(self):
        _, said, project = self.answer(self.ok())
        last = said.rstrip("\n").split("\n")[-1]
        self.assertTrue(last.startswith("  next: "), last)
        self.assertTrue(last.endswith("look.py --project %s — %s" % (project, self.WHY)), last)

    def test_the_step_carries_the_store_and_the_line_quotes_a_space(self):
        home = Path(tempfile.mkdtemp(), "home store").resolve()
        with mock.patch.dict(os.environ, {"SPARK_HOME": str(home)}):
            step = json.loads(self.answer(self.ok(), True, folder="my lamp")[1])["next"][0]
            _, said, project = self.answer(self.ok(), folder="my lamp")
        self.assertEqual(step["env"], {"SPARK_HOME": str(home)})
        last = said.rstrip("\n").split("\n")[-1]
        self.assertTrue(last.startswith("  next: SPARK_HOME=%s " % shlex.quote(str(home))), last)
        self.assertIn("--project %s — " % shlex.quote(str(project)), last)

    def test_a_problem_a_could_not_run_and_a_library_run_name_no_step(self):
        for label, stages, library in (("problem", [stage("build", check_spine.PROBLEMS)], False),
                                       ("could not run", [stage("build", check_spine.COULD_NOT_RUN)], False),
                                       ("library", self.ok(), True)):
            with self.subTest(label):
                _, said, _ = self.answer(stages, True, library)
                self.assertNotIn("next", json.loads(said))
                self.assertNotIn("  next: ", self.answer(stages, library=library)[1])


class ARebuildMergesIntoTheKeptDiagramTest(unittest.TestCase):
    """P482 (#661): the build copies the kept sim/diagram.json in before the converter, whose merge keeps the person's edits."""
    FIXTURE = ROOT / "tests" / "data" / "breadboard" / "button-light"

    def build(self, into):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            check_spine.main([str(self.FIXTURE / "requirements.json"), "--keep", str(into)])
        return out.getvalue()

    @unittest.skipUnless(test_converter.node() and board_engine.find_toolchain(ROOT), "needs the board engine and Node")
    def test_a_second_build_keeps_a_moved_part_a_hand_added_part_and_its_wire(self):
        into = Path(tempfile.mkdtemp()) / "project"
        first = self.build(into)
        self.assertNotIn("kept from your diagram", first)
        path = into / "sim" / "diagram.json"
        diagram = json.loads(path.read_text())
        diagram["parts"][1]["left"] = 999
        diagram["parts"].append({"type": "wokwi-gnd", "id": "mine", "top": 5, "left": 6, "attrs": {"handAdded": "true"}})
        diagram["connections"].append(["mine:GND", "mcu:GND.3", "red", []])
        path.write_text(json.dumps(diagram))
        second = self.build(into)
        again = json.loads(path.read_text())
        self.assertEqual({part["id"]: part["left"] for part in again["parts"]}["tactilebutton"], 999)
        self.assertIn("mine", [part["id"] for part in again["parts"]])
        self.assertIn(["mine:GND", "mcu:GND.3", "red", []], again["connections"])
        self.assertIn("kept from your diagram: ", second)
        self.assertIn("hand-added: mine", second)

    @unittest.skipUnless(test_converter.node() and board_engine.find_toolchain(ROOT), "needs the board engine and Node")
    def test_a_hand_added_led_passes_and_an_unwired_one_is_a_warning(self):
        # P497: the linter knows wokwi-led's attributes, not the handAdded mark, and warns on a part in no wire
        into = Path(tempfile.mkdtemp()) / "project"
        self.build(into)
        path = into / "sim" / "diagram.json"
        diagram = json.loads(path.read_text())
        for name, top in (("wired", 5), ("lone", 6)):
            diagram["parts"].append({"type": "wokwi-led", "id": name, "top": top, "left": 6, "attrs": {"handAdded": "true"}})
        diagram["connections"] += [["wired:A", "mcu:4", "green", []], ["wired:C", "mcu:GND.3", "black", []]]
        path.write_text(json.dumps(diagram))
        second = self.build(into)
        again = json.loads(path.read_text())
        self.assertEqual([part["id"] for part in again["parts"] if part["id"] in ("wired", "lone")], ["wired", "lone"])
        self.assertIn("hand-added: wired, lone", second)
        self.assertIn("lone was added by hand and has no wire yet. It stays in the diagram.", second)
        self.assertNotIn("wired was added by hand and has no wire yet", second)
        self.assertNotIn("no diagram was produced", second)

    @unittest.skipUnless(test_converter.node() and board_engine.find_toolchain(ROOT), "needs the board engine and Node")
    def test_a_failing_rebuild_prints_no_hand_added_warning(self):
        # P497: a blocking problem (a misspelt attribute) beside an unwired hand-added part: the build stops and warns nothing
        into = Path(tempfile.mkdtemp()) / "project"
        self.build(into)
        path = into / "sim" / "diagram.json"
        diagram = json.loads(path.read_text())
        diagram["parts"].append({"type": "wokwi-led", "id": "lone", "top": 6, "left": 6, "attrs": {"handAdded": "true", "colr": "red"}})
        path.write_text(json.dumps(diagram))
        second = self.build(into)
        self.assertIn("colr", second)
        self.assertNotIn("was added by hand and has no wire yet", second)

    @unittest.skipUnless(test_converter.node() and board_engine.find_toolchain(ROOT), "needs the board engine and Node")
    def test_a_full_build_on_a_board_heard_without_wires_gives_no_serial_warning(self):
        # P468: the XIAO's Wokwi part has no TX and RX, so its diagram gets no $serialMonitor wires, and its record says a
        # run heard it without them
        folder = Path(tempfile.mkdtemp())
        (folder / "requirements.json").write_text('{"board": "xiao-esp32-c6", "parts": ["tactile-button", "led-red-5mm"]}')
        into, out = folder / "project", io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            check_spine.main([str(folder / "requirements.json"), "--keep", str(into)])
        said = out.getvalue()
        wires = json.loads((into / "sim" / "diagram.json").read_text())["connections"]
        self.assertFalse([wire for wire in wires if any(str(end).startswith("$serialMonitor") for end in wire[:2])])
        self.assertNotIn("no serial monitor", said)

    def test_a_converter_that_fails_beside_a_copied_diagram_fails_the_stage(self):
        requirements = json.loads((self.FIXTURE / "requirements.json").read_text())
        workdir = Path(tempfile.mkdtemp())
        (workdir / "requirements.json").write_text(json.dumps(requirements))
        (workdir / "kept-diagram.json").write_text('{"parts": [], "connections": []}')
        broken = subprocess.CompletedProcess([], 1, "", "converter exploded")
        real = subprocess.run
        self.addCleanup(setattr, requirements_build.subprocess, "run", real)
        requirements_build.subprocess.run = lambda command, *rest, **named: broken if "--circuit" in command else real(command, *rest, **named)
        # P723: a fake engine, so no real tsci runs on a machine that has one; its circuit passes the build stage (one
        # trace, the MCU grounded and its 3V3 on the net the design feeds it from), and the faked converter is what fails
        circuit = [{"type": "source_net", "source_net_id": "n_gnd", "name": "GND"},
                   {"type": "source_net", "source_net_id": "n_v33", "name": "V33"},
                   {"type": "source_component", "source_component_id": "c_mcu", "name": "Mcu"},
                   {"type": "source_port", "source_port_id": "p_3v3", "source_component_id": "c_mcu", "name": "3V3"},
                   {"type": "source_port", "source_port_id": "p_gnd", "source_component_id": "c_mcu", "name": "GND"},
                   {"type": "source_trace", "source_trace_id": "t1", "connected_source_port_ids": ["p_3v3"], "connected_source_net_ids": ["n_v33"]},
                   {"type": "source_trace", "source_trace_id": "t2", "connected_source_port_ids": ["p_gnd"], "connected_source_net_ids": ["n_gnd"]},
                   {"type": "pcb_trace"}]
        service = build_service.BuildService(FakeTscircuitEngine(circuit=circuit), board_emitter.BoardEmitter(assume_missing_sizes=True))
        stages = service.build(build_service.BuildInputs(requirements, workdir, project=ROOT))
        self.assertEqual((stages[-1].name, stages[-1].status), ("simulation", check_spine.PROBLEMS))
        self.assertIn("no diagram was produced", stages[-1].detail)


# --- MVP ---
class EachStopOfTheBuildCarriesItsCodeTest(unittest.TestCase):
    """P701: every Stage that does not end ok names its code (build_codes, or the design error's own), and the sheet's
    `not written` entry carries its code into --json's `kept`. The codes are literals here."""

    #: Each Stage that is not ok, in the order the build area builds them (P705): board_engine's converter_stage_problem
    #: and convert, build_service's BuildService and board_alone, requirements_build's RequirementsBuildService. A code a design error carries is named by the
    #: expression that passes it on.
    CODES_IN_ORDER = [
        "tool_missing",
        "converter_lacks_part", "no_diagram",
        "board_unusable", "board_only_with_parts", "no_parts", "broken.code", "refused.code", "stage_crashed",
        "schematic_refused", "schematic_noted", "disagreement.code", "stage_crashed", "tool_missing",
        "tool_cannot_build", "design_not_built", "part_stranded", "design_not_built", "not_routed",
        "simulation_fact_missing", "chip_not_compiled", "diagram_unwired",
        "simulation_fact_missing", "simulation_fact_missing",
        "broken.code", "stage_timed_out", "stage_crashed",
    ]

    def test_each_stage_that_is_not_ok_names_its_code(self):
        stops = []
        for source in ("spark/build/board_engine.py", "spark/build/build_service.py", "spark/build/requirements_build.py"):
            tree = ast.parse((ROOT / "scripts" / source).read_text())
            stops += sorted((node.lineno, node.col_offset, node) for node in ast.walk(tree)
                            if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "Stage" and len(node.args) > 1
                            and getattr(node.args[1], "id", None) in ("COULD_NOT_RUN", "PROBLEMS"))

        def code(call):
            if len(call.args) < 4:
                return None
            named = call.args[3]
            if isinstance(named, ast.Attribute) and getattr(named.value, "id", None) == "build_codes":
                return getattr(build_codes, named.attr)
            return ast.unparse(named)
        self.assertEqual([code(call) for _, _, call in stops], self.CODES_IN_ORDER)

    def test_a_board_nobody_has_parts_said_twice_and_no_parts_are_caught_with_their_codes(self):
        workdir = Path(tempfile.mkdtemp())
        for requirements, wanted in (({"board": "no-such-board", "parts": ["x"]}, ("board", "board_unusable")),
                                     ({"board": "firebeetle2-esp32s3", "board_only": True, "parts": ["x"]},
                                      ("parts", "board_only_with_parts")),
                                     ({"board": "firebeetle2-esp32s3"}, ("parts", "no_parts")),
                                     ({"board": "firebeetle2-esp32s3", "parts": ["no-such-part"]}, ("parts", "part_unusable"))):
            last = build_stages(requirements, workdir)[-1]
            self.assertEqual((last.name, last.code), wanted, requirements)
        self.assertIsNone(build_stages({"board": "firebeetle2-esp32s3"}, workdir)[0].code)  # the board stage, ok

    def test_a_sheet_not_written_carries_its_code_into_the_json(self):
        project = Path(tempfile.mkdtemp())
        (project / "requirements.json").write_text(json.dumps({"board": "firebeetle2-esp32s3", "parts": []}))
        built = [Stage("build", check_spine.OK)]
        entry = kept_files.keep_breadboard(project / "requirements.json", project, built)[0]
        self.assertEqual((entry["did"], entry["code"]), ("not written", "file_unusable"))  # no dist/board to record in
        (project / "dist" / "board").mkdir(parents=True)
        entry = kept_files.keep_breadboard(project / "requirements.json", project, built)[0]
        self.assertEqual((entry["did"], entry["code"]), ("not written", "not_built"))
        self.assertTrue(entry["line"].startswith("no breadboard sheet: nothing is built at "), entry["line"])

    def test_a_sheet_that_crashed_on_a_value_error_carries_stage_crashed(self):
        project = Path(tempfile.mkdtemp())
        (project / "requirements.json").write_text("{not json")  # record_built_from reads it: a ValueError, no refusal
        (project / "dist" / "board").mkdir(parents=True)
        entries = kept_files.keep_breadboard(project / "requirements.json", project, [Stage("build", check_spine.OK)])
        self.assertEqual((entries[0]["did"], entries[0]["code"]), ("not written", "stage_crashed"))
        self.assertTrue(entries[0]["line"].startswith("no breadboard sheet: "), entries[0]["line"])
        self.assertEqual(len(entries), 3)
        for drawn in entries[1:]:
            self.assertEqual(drawn["did"], "not written")
            self.assertTrue(drawn["line"].endswith(": the sheet was not written"), drawn["line"])
# --- end MVP ---


if __name__ == "__main__":
    unittest.main()


class AnAllSkippedSimulationKeepsTheBuildTest(unittest.TestCase):
    """P778 PR round: a full build whose simulation stage is skipped (every part's record skips the simulation) built its
    board, so the kept dist/ stays, the page is drawn and the closing line says what happened; only a board-only build
    (its build stage skipped) drops an older dist/."""

    FULL = [Stage("build", check_spine.OK, "3 trace(s)"), Stage("simulation", check_spine.SKIPPED, "every part is skipped")]
    ALONE = [Stage("build", check_spine.SKIPPED, "board only: nothing to wire"), Stage("simulation", check_spine.OK, "4 wire(s)")]

    def test_the_kept_dist_stays_and_nothing_says_no_board_was_built(self):
        workdir = Path(tempfile.mkdtemp())
        (workdir / "dist").mkdir()
        self.assertEqual(kept_files.drop_an_older_build(workdir, self.FULL), [])
        self.assertTrue((workdir / "dist").is_dir())
        self.assertIsNone(kept_files.why_not_built(self.FULL, "board only: nothing to draw"))
        self.assertEqual(kept_files.why_not_built(self.ALONE, "board only: nothing to draw"), "board only: nothing to draw")
        self.assertEqual(kept_files.drop_an_older_build(workdir, self.ALONE)[0]["did"], "removed")

    def test_the_closing_line_says_every_part_is_skipped_and_the_board_only_line_stays(self):
        self.assertEqual(check_spine.render(self.FULL, check_spine.EXIT_OK).splitlines()[-1],
                         "  the chain runs end to end; every part is skipped from the simulation, so the diagram holds the board alone")
        self.assertEqual(check_spine.render(self.ALONE, check_spine.EXIT_OK).splitlines()[-1],
                         "  the chain runs end to end for the board alone: nothing to wire, so no board was built")
        self.assertEqual(check_spine.render([Stage("build", check_spine.OK, "x"), Stage("simulation", check_spine.OK, "y")], check_spine.EXIT_OK).splitlines()[-1],
                         "  the chain runs end to end")

