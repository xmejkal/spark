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

import sys
import unittest
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
