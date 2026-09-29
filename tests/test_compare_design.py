"""
P8: the floating-input rule against the connectivity spark's own generator emits.

Three projects in a row: a pin wired by a pin-to-pin trace — which names no net — was reported
as connecting to nothing, and the finding named neither component nor pin (I10).
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import check_all  # noqa: E402
import compare_design  # noqa: E402


def circuit(components, pin_to_pin=(), to_net=()):
    """
    circuit.json the way tscircuit writes it: components with ports, pin-to-pin traces that name
    no net, and traces to a named net. `components` = {name: [pins]}; a trace endpoint is "Name.PIN".
    """
    elements, port_ids = [], {}
    for index, (name, pins) in enumerate(components.items()):
        cid = "source_component_%d" % index
        elements.append({"type": "source_component", "source_component_id": cid, "name": name, "ftype": "simple_chip"})
        for pin_index, pin in enumerate(pins):
            pid = "source_port_%d_%d" % (index, pin_index)
            port_ids["%s.%s" % (name, pin)] = pid
            elements.append({"type": "source_port", "source_port_id": pid, "source_component_id": cid, "name": pin, "pin_number": pin_index + 1})
    nets = {}
    for trace_index, ends in enumerate(pin_to_pin):
        elements.append({"type": "source_trace", "source_trace_id": "source_trace_p%d" % trace_index,
                         "connected_source_port_ids": [port_ids[end] for end in ends], "connected_source_net_ids": [],
                         "display_name": " to ".join(ends)})
    for trace_index, (net_name, end) in enumerate(to_net):
        if net_name not in nets:
            nets[net_name] = "source_net_%d" % len(nets)
            elements.append({"type": "source_net", "source_net_id": nets[net_name], "name": net_name, "is_power": net_name in ("V33", "GND")})
        elements.append({"type": "source_trace", "source_trace_id": "source_trace_n%d" % trace_index,
                         "connected_source_port_ids": [port_ids[end]], "connected_source_net_ids": [nets[net_name]],
                         "display_name": "%s to net.%s" % (end, net_name)})
    return elements


class APinWiredPinToPinIsNotFloatingTest(unittest.TestCase):
    def test_a_pin_to_pin_trace_counts_as_a_connection(self):
        netlist = compare_design.Netlist(circuit(
            {"Mcu": ["D3", "GND"], "Valve1": ["SIGNAL", "VCC", "GND"]},
            pin_to_pin=[("Mcu.D3", "Valve1.SIGNAL")], to_net=[("V33", "Valve1.VCC"), ("GND", "Valve1.GND"), ("GND", "Mcu.GND")]))
        self.assertEqual(compare_design.check_floating_inputs(netlist, [("Valve1", "SIGNAL")]), [])
        self.assertTrue(netlist.nets_of("Valve1", "SIGNAL"), "the trace is a net, unnamed")
        self.assertEqual(netlist.nets_of("Valve1", "SIGNAL"), netlist.nets_of("Mcu", "D3"), "both ends sit on the same one")

    def test_a_pin_on_no_trace_at_all_is_still_reported_by_name(self):
        netlist = compare_design.Netlist(circuit(
            {"Mcu": ["D3"], "Valve1": ["SIGNAL", "GND"]}, to_net=[("GND", "Valve1.GND")]))
        failures = compare_design.check_floating_inputs(netlist, [("Valve1", "SIGNAL")])
        self.assertEqual([f.subject for f in failures], ["Valve1.SIGNAL"])

    def test_two_traces_of_one_wire_share_their_connectivity_key(self):
        elements = circuit({"Mcu": ["D3"], "A": ["IN"], "B": ["IN"]}, pin_to_pin=[("Mcu.D3", "A.IN"), ("Mcu.D3", "B.IN")])
        for element in elements:
            if element["type"] == "source_trace":
                element["subcircuit_connectivity_map_key"] = "wire_7"
        netlist = compare_design.Netlist(elements)
        self.assertEqual(netlist.nets_of("A", "IN"), netlist.nets_of("B", "IN"), "one wire, one net")


class TheFindingNamesItsPinTest(unittest.TestCase):
    def test_check_all_prints_the_component_and_the_pin(self):
        tmp = Path(tempfile.mkdtemp())
        (tmp / "c.json").write_text(json.dumps(circuit({"Mcu": ["D3"], "Valve1": ["SIGNAL", "GND"]}, to_net=[("GND", "Valve1.GND")])))
        (tmp / "r.json").write_text(json.dumps({"must_not_float": [["Valve1", "SIGNAL"]]}))
        check = next(c for c in check_all.CHECKS if c.name == "rules-vs-netlist")
        result = check.run({"circuit": str(tmp / "c.json"), "rules": str(tmp / "r.json")})
        self.assertEqual(result["status"], check_all.PROBLEMS)
        self.assertIn("Valve1.SIGNAL", result["problems"][0], result["problems"])


if __name__ == "__main__":
    unittest.main()
