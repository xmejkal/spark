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


def circuit(components, pin_to_pin=(), to_net=(), resistors=()):
    """
    circuit.json the way tscircuit writes it: components with ports, pin-to-pin traces that name
    no net, and traces to a named net. `components` = {name: [pins]}; a trace endpoint is "Name.PIN".
    """
    elements, port_ids = [], {}
    for index, (name, pins) in enumerate(components.items()):
        cid = "source_component_%d" % index
        elements.append({"type": "source_component", "source_component_id": cid, "name": name,
                         "ftype": "simple_resistor" if name in resistors else "simple_chip"})
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
            elements.append({"type": "source_net", "source_net_id": nets[net_name], "name": net_name,
                             "is_power": net_name == "V33", "is_ground": net_name == "GND"})
        elements.append({"type": "source_trace", "source_trace_id": "source_trace_n%d" % trace_index,
                         "connected_source_port_ids": [port_ids[end]], "connected_source_net_ids": [nets[net_name]],
                         "display_name": "%s to net.%s" % (end, net_name)})
    return elements


class APinWiredPinToPinIsNotFloatingTest(unittest.TestCase):
    def test_a_pin_to_pin_trace_counts_as_a_connection(self):
        # B13: the fixture carries the pull-down a "must not float" input needs; P8's point —
        # a pin-to-pin trace is a net, unnamed — is the connectivity asserted below.
        netlist = compare_design.Netlist(circuit(
            {"Mcu": ["D3", "GND"], "Valve1": ["SIGNAL", "VCC", "GND"], "Rpd": ["pin1", "pin2"]},
            pin_to_pin=[("Mcu.D3", "Valve1.SIGNAL"), ("Valve1.SIGNAL", "Rpd.pin1")],
            to_net=[("V33", "Valve1.VCC"), ("GND", "Valve1.GND"), ("GND", "Mcu.GND"), ("GND", "Rpd.pin2")],
            resistors=("Rpd",)))
        self.assertEqual(compare_design.check_floating_inputs(netlist, [("Valve1", "SIGNAL")]), [])
        self.assertTrue(netlist.nets_of("Valve1", "SIGNAL"), "the trace is a net, unnamed")
        self.assertTrue(netlist.nets_of("Valve1", "SIGNAL") & netlist.nets_of("Mcu", "D3"), "both ends share the wire")

    def test_a_pin_joined_only_to_a_gpio_floats_all_the_same(self):
        # B13: the quickstart's buttons read [ok] with no pull resistor at all.
        netlist = compare_design.Netlist(circuit(
            {"Mcu": ["D3"], "BtnOpen": ["A", "B"]},
            pin_to_pin=[("Mcu.D3", "BtnOpen.A")], to_net=[("GND", "BtnOpen.B")]))
        failures = compare_design.check_floating_inputs(netlist, [("BtnOpen", "A")])
        self.assertEqual([f.subject for f in failures], ["BtnOpen.A"])
        self.assertIn("no resistor to a rail", failures[0].detail)

    def test_a_pad_is_named_by_its_silkscreen_not_its_footprint_number(self):
        # On the quickstart the finding read "joined to Mcu.pin20" — nothing printed on the board says pin20.
        elements = circuit({"Mcu": ["pin20"], "BtnOpen": ["A", "B"]},
                           pin_to_pin=[("Mcu.pin20", "BtnOpen.A")], to_net=[("GND", "BtnOpen.B")])
        for element in elements:
            if element["type"] == "source_port" and element["name"] == "pin20":
                element["port_hints"] = ["pin20", "D11", "20"]
        failures = compare_design.check_floating_inputs(compare_design.Netlist(elements), [("BtnOpen", "A")])
        self.assertIn("Mcu.D11", failures[0].detail)

    def test_the_rules_files_rails_reach_the_check(self):
        elements = circuit({"Mcu": ["D3"], "Drv": ["IN"], "Rpu": ["pin1", "pin2"]},
                           pin_to_pin=[("Mcu.D3", "Drv.IN"), ("Drv.IN", "Rpu.pin1")], to_net=[("MOTOR6V", "Rpu.pin2")], resistors=("Rpu",))
        rules = {"must_not_float": [["Drv", "IN"]], "physics": {"rails": {"MOTOR6V": {}}}}
        self.assertEqual(compare_design.run(elements, rules), [])

    def test_a_series_resistor_is_not_a_pull(self):
        netlist = compare_design.Netlist(circuit(
            {"Mcu": ["D3"], "Rs": ["pin1", "pin2"], "Led": ["A", "K"]},
            pin_to_pin=[("Mcu.D3", "Rs.pin1"), ("Rs.pin2", "Led.A")], to_net=[("GND", "Led.K")], resistors=("Rs",)))
        self.assertTrue(compare_design.check_floating_inputs(netlist, [("Led", "A")]))

    def test_a_rail_named_only_in_the_rules_counts(self):
        # tscircuit flags neither power nor ground on MOTOR6V; the rules file names it a rail.
        netlist = compare_design.Netlist(circuit(
            {"Mcu": ["D3"], "Drv": ["IN"], "Rpu": ["pin1", "pin2"]},
            pin_to_pin=[("Mcu.D3", "Drv.IN"), ("Drv.IN", "Rpu.pin1")], to_net=[("MOTOR6V", "Rpu.pin2")], resistors=("Rpu",)))
        self.assertTrue(compare_design.check_floating_inputs(netlist, [("Drv", "IN")]))
        self.assertEqual(compare_design.check_floating_inputs(netlist, [("Drv", "IN")], rails=["MOTOR6V"]), [])

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


class ABusLineNamedByItsPinTest(unittest.TestCase):
    """
    P45. spark's own generator wires every signal PIN TO PIN, so no net is ever called SDA.

    A rule naming the net could only ever answer "no net of that name" on a board this tool
    produced — which is why `i2c_buses` stayed empty and unusable on every generated project.
    A line may now be written `Component.PIN`, and the pull-up is looked for on whatever net
    that pin is actually on.
    """

    @staticmethod
    def circuit(*, pull_up=True):
        elements = [
            {"type": "source_component", "source_component_id": "c_m", "name": "Mcu"},
            {"type": "source_component", "source_component_id": "c_s", "name": "Sensor"},
            {"type": "source_net", "source_net_id": "n_v33", "name": "V33", "is_power": True},
            {"type": "source_port", "source_port_id": "p_m", "source_component_id": "c_m",
             "name": "pin9", "port_hints": ["pin9", "SDA", "9"]},
            {"type": "source_port", "source_port_id": "p_s", "source_component_id": "c_s", "name": "SDA"},
            # the signal, pin to pin and naming no net — which is how spark wires everything
            {"type": "source_trace", "source_trace_id": "t1", "subcircuit_connectivity_map_key": "k",
             "connected_source_port_ids": ["p_m", "p_s"], "connected_source_net_ids": []},
        ]
        if pull_up:
            elements += [
                {"type": "source_component", "source_component_id": "c_r", "name": "SensorPullupSDA",
                 "ftype": "simple_resistor", "resistance": 4700},
                {"type": "source_port", "source_port_id": "p_r1", "source_component_id": "c_r", "name": "pin1"},
                {"type": "source_port", "source_port_id": "p_r2", "source_component_id": "c_r", "name": "pin2"},
                {"type": "source_trace", "source_trace_id": "t2", "subcircuit_connectivity_map_key": "k",
                 "connected_source_port_ids": ["p_r1", "p_s"], "connected_source_net_ids": []},
                {"type": "source_trace", "source_trace_id": "t3",
                 "connected_source_port_ids": ["p_r2"], "connected_source_net_ids": ["n_v33"]},
            ]
        return elements

    def failures(self, buses, **kwargs):
        netlist = compare_design.Netlist(self.circuit(**kwargs))
        return compare_design.check_i2c_pullups(netlist, buses)

    def test_a_pulled_up_line_named_by_a_pin_passes(self):
        self.assertEqual(self.failures(["Sensor.SDA"]), [])

    def test_the_host_pins_silkscreen_name_finds_the_same_line(self):
        # The pad is called pin9 in the netlist; SDA is the only name anyone writes down.
        self.assertEqual(self.failures(["Mcu.SDA"]), [])

    def test_an_unpulled_line_named_by_a_pin_still_fails(self):
        # The rule has to be able to fail, or seeding it is decoration.
        failures = self.failures(["Sensor.SDA"], pull_up=False)
        self.assertEqual([f.rule for f in failures], ["i2c-pullups"])
        self.assertIn("nothing pulls it up", failures[0].detail)

    def test_a_name_that_is_neither_a_net_nor_a_pin_is_said(self):
        failures = self.failures(["Sensor.SCL"])
        self.assertIn("nothing of that name", failures[0].detail)

    def test_a_pin_on_more_than_one_net_is_searched_on_all_of_them(self):
        # A pad can sit on a NAMED net and be joined pin-to-pin to something else at the same
        # time — which is exactly the smart bin's shape, where SDA is a net and the pull-up
        # reaches the sensor's pad. Searching only the first net found the named one and missed
        # the resistor.
        circuit = self.circuit() + [
            {"type": "source_net", "source_net_id": "n_sda", "name": "SDA"},
            {"type": "source_trace", "source_trace_id": "t5",
             "connected_source_port_ids": ["p_s"], "connected_source_net_ids": ["n_sda"]},
        ]
        netlist = compare_design.Netlist(circuit)
        self.assertGreater(len(netlist.nets_of("Sensor", "SDA")), 1, "the fixture must span two nets")
        self.assertEqual(compare_design.check_i2c_pullups(netlist, ["Sensor.SDA"]), [])

    def test_a_net_name_still_works(self):
        # Both forms, because a hand-written board.tsx names its nets and the smart bin's does.
        circuit = self.circuit() + [
            {"type": "source_net", "source_net_id": "n_bus", "name": "SCL"},
            {"type": "source_port", "source_port_id": "p_s2", "source_component_id": "c_s", "name": "SCL"},
            {"type": "source_trace", "source_trace_id": "t4",
             "connected_source_port_ids": ["p_s2"], "connected_source_net_ids": ["n_bus"]},
        ]
        failures = compare_design.check_i2c_pullups(compare_design.Netlist(circuit), ["SCL"])
        self.assertIn("nothing pulls it up", failures[0].detail)


if __name__ == "__main__":
    unittest.main()
