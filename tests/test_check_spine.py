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
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import check_spine  # noqa: E402


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
            check_spine.components_not_on_ground(self.circuit(ground_the_mcu=False)), ["Mcu"])

    def test_grounding_it_clears_the_finding(self):
        self.assertEqual(
            check_spine.components_not_on_ground(self.circuit(ground_the_mcu=True)), [])

    def test_a_ground_under_another_name_still_counts(self):
        # A design with an analogue return calls it AGND, and "the net called GND" stops being
        # true. Naming them beats guessing from the netlist.
        circuit = self.circuit(ground_the_mcu=True)
        for element in circuit:
            if element.get("name") == "GND":
                element["name"] = "AGND"
        self.assertEqual(check_spine.components_not_on_ground(circuit), [])

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
        self.assertEqual(check_spine.components_not_on_ground(circuit), [])
        dangling = [e for e in circuit if e.get("source_trace_id") != "t5"]
        self.assertEqual(check_spine.components_not_on_ground(dangling), ["SdaPullup.pin2 (a terminal connected to nothing)"])

    def test_a_component_in_no_trace_at_all_is_not_reported_here(self):
        # Already covered by the generators, which refuse to emit a part they cannot wire.
        # Reporting it twice, in different words, is how a finding gets scrolled past.
        circuit = self.circuit(ground_the_mcu=True) + [
            {"type": "source_component", "source_component_id": "c_lonely", "name": "Lonely"}]
        self.assertNotIn("Lonely", check_spine.components_not_on_ground(circuit))


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

    def test_no_converter_anywhere_is_none_not_a_guess(self):
        import tempfile
        self.assertIsNone(check_spine.find_converter(Path(tempfile.mkdtemp())))

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
             "pin_order": ["VCC", "GND"], "footprint": "jst_ph_2",
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

if __name__ == "__main__":
    unittest.main()
