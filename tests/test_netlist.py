"""
P35: one walk over a built netlist, and the circuit that proved there were three.

Before this library, `compare_design.Netlist`, `check_physics.Board` and `check_spine`'s ground
walk each read `circuit.json` their own way. On one circuit they gave three different answers, and
one of the three was a false problem that stops a good board's build. The first test here is that
circuit; it is the reason this file exists.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import netlist  # noqa: E402


def circuit(*, key="k1", name_the_trace=False):
    """
    U1.GND wired pin-to-pin to U2.GND — how spark's own generator wires every signal — and
    U2.GND also sitting on the named net GND.
    """
    trace = {"type": "source_trace", "source_trace_id": "t1",
             "connected_source_port_ids": ["p1", "p2"],
             "connected_source_net_ids": ["n_gnd"] if name_the_trace else []}
    if key:
        trace["subcircuit_connectivity_map_key"] = key
    return [
        {"type": "source_net", "source_net_id": "n_gnd", "name": "GND", "is_power": True},
        {"type": "source_component", "source_component_id": "c1", "name": "U1", "ftype": "simple_chip"},
        {"type": "source_component", "source_component_id": "c2", "name": "U2", "ftype": "simple_chip"},
        {"type": "source_port", "source_port_id": "p1", "source_component_id": "c1", "name": "GND"},
        {"type": "source_port", "source_port_id": "p2", "source_component_id": "c2", "name": "GND"},
        trace,
        {"type": "source_trace", "source_trace_id": "t2", "connected_source_port_ids": ["p2"],
         "connected_source_net_ids": ["n_gnd"]},
    ]


class ATraceThatNamesNoNetIsStillAConnectionTest(unittest.TestCase):
    def test_both_ends_of_a_pin_to_pin_trace_sit_on_one_net(self):
        n = netlist.Netlist(circuit())
        self.assertEqual(n.nets_of("U1", "GND"), {"trace:k1"})
        self.assertEqual(n.nets_of("U1", "GND"), n.nets_of("U2", "GND") & {"trace:k1"})

    def test_the_several_traces_of_one_wire_share_its_key(self):
        elements = circuit()
        elements.append({"type": "source_trace", "source_trace_id": "t3",
                         "connected_source_port_ids": ["p1"], "connected_source_net_ids": [],
                         "subcircuit_connectivity_map_key": "k1"})
        self.assertEqual(netlist.Netlist(elements).nets_of("U1", "GND"), {"trace:k1"},
                         "one wire is one net, however many traces draw it")

    def test_without_a_key_the_trace_stands_for_itself(self):
        self.assertEqual(netlist.Netlist(circuit(key=None)).nets_of("U1", "GND"), {"trace:t1"})

    def test_a_pin_on_no_trace_at_all_sits_on_nothing(self):
        elements = [e for e in circuit() if e.get("source_trace_id") != "t1"]
        self.assertEqual(netlist.Netlist(elements).nets_of("U1", "GND"), set())


class MembershipIsNotTransitiveTest(unittest.TestCase):
    """
    U1 reaches GND only through U2's pin. All three walkers treated that as two nets, and this
    library keeps that: making it transitive is a change with its own consequences, not a
    tidy-up. The test exists so the day someone changes it, they change it on purpose.
    """

    def test_the_named_net_holds_only_the_pin_that_names_it(self):
        self.assertEqual(netlist.Netlist(circuit()).components_on("GND"), ["U2"])


class WhatTheRulesAskItTest(unittest.TestCase):
    def setUp(self):
        self.n = netlist.Netlist(circuit())

    def test_a_net_is_found_by_name_and_a_missing_one_is_none(self):
        self.assertEqual(self.n.net_named("GND"), "n_gnd")
        self.assertIsNone(self.n.net_named("V33"))

    def test_it_lists_the_names_that_exist(self):
        self.assertEqual(self.n.net_names(), ["GND"])

    def test_power_nets_are_the_ones_that_say_so(self):
        self.assertEqual(self.n.power_nets(), {"n_gnd"})

    def test_a_component_is_found_by_name_under_either_word(self):
        self.assertEqual(self.n.component("U1")["source_component_id"], "c1")
        self.assertIs(netlist.Netlist.named, netlist.Netlist.component, "one question, two vocabularies")
        self.assertIsNone(self.n.component("U9"))

    def test_components_on_a_net_nobody_named_is_empty_not_an_error(self):
        self.assertEqual(self.n.components_on("V33"), [])


class AMalformedElementIsNotATracebackTest(unittest.TestCase):
    def test_an_element_without_a_type_is_skipped(self):
        # One of the three walkers indexed `e["type"]`, so a circuit element without one was a
        # traceback rather than a finding.
        elements = circuit() + [{"source_component_id": "c9"}, {}]
        self.assertEqual(netlist.Netlist(elements).components_on("GND"), ["U2"])

    def test_a_trace_naming_a_port_that_does_not_exist_is_skipped(self):
        elements = circuit()
        elements.append({"type": "source_trace", "source_trace_id": "t4",
                         "connected_source_port_ids": ["p_missing"], "connected_source_net_ids": ["n_gnd"]})
        self.assertEqual(netlist.Netlist(elements).components_on("GND"), ["U2"])

    def test_an_empty_circuit_walks_to_nothing(self):
        n = netlist.Netlist([])
        self.assertEqual((n.members, n.net_names(), n.components_on("GND")), ({}, [], []))


class TheTwoCallersShareIt(unittest.TestCase):
    def test_the_rules_checker_and_the_physics_checker_answer_alike(self):
        import check_physics
        import compare_design
        elements = circuit()
        self.assertIs(compare_design.Netlist, netlist.Netlist)
        self.assertTrue(issubclass(check_physics.Board, netlist.Netlist))
        self.assertEqual(compare_design.Netlist(elements).nets_of("U1", "GND"),
                         check_physics.Board(elements).nets_of("U1", "GND"))


if __name__ == "__main__":
    unittest.main()
