"""
Proof that the physics check bites, and that its refusals are not passes.

Every other check in this plugin compares a design to itself. This one does arithmetic, which
means it has a failure mode the others do not: it can be confidently wrong. So the tests below
do two things. They give it designs that violate physics and assert it says so — and they pin
the arithmetic itself against numbers that can be checked by hand, because a check whose formula
is wrong is worse than no check at all.

The rise-time constant is the example. A plausible-looking `ln(1/(1-0.7)) = 1.204` overstates an
I2C rise by 42%, and that error was made on the project this plugin came from: it turned a
pull-up that was fine into one that looked twice over spec. The correct constant is
`ln(0.7/0.3) = 0.847`, because the specification measures between 0.3 and 0.7 of the supply and
not from zero. That is asserted here so it cannot drift back.

    python3 -m unittest discover -s tests
"""

import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import check_footprints  # noqa: E402
import check_physics  # noqa: E402


def component(name, ftype, **fields):
    return dict({"type": "source_component", "source_component_id": name,
                 "name": name, "ftype": ftype}, **fields)


def net(name, **fields):
    return dict({"type": "source_net", "source_net_id": name, "name": name}, **fields)


def port(component_name, pin):
    return {"type": "source_port", "source_port_id": "%s.%s" % (component_name, pin),
            "source_component_id": component_name, "name": pin}


def trace(net_name, endpoints, widths=None, trace_id="t1"):
    """A source trace, plus the routed copper for it if `widths` is given."""
    elements = [{"type": "source_trace", "source_trace_id": trace_id,
                 "connected_source_net_ids": [net_name],
                 "connected_source_port_ids": list(endpoints)}]
    if widths is not None:
        route = [{"x": 0, "y": 0}]
        route += [{"x": index + 1, "y": 0, "width": width}
                  for index, width in enumerate(widths)]
        elements.append({"type": "pcb_trace", "pcb_trace_id": "pcb_" + trace_id,
                         "source_trace_id": trace_id, "route": route})
    return elements


def pcb_component(name, footprint):
    return {"type": "pcb_component", "pcb_component_id": "pcb_" + name,
            "source_component_id": name, "footprinter_string": footprint}


class TheArithmeticItself(unittest.TestCase):
    """The formulas, pinned against values that can be checked by hand."""

    def test_the_i2c_rise_constant_is_measured_between_0_3_and_0_7_of_the_supply(self):
        # NOT ln(1/(1-0.7)) = 1.204, which measures from zero and overstates every rise by 42%.
        self.assertAlmostEqual(check_physics.I2C_RISE_CONSTANT, math.log(0.7 / 0.3), places=6)
        self.assertAlmostEqual(check_physics.I2C_RISE_CONSTANT, 0.8473, places=3)

    def test_trace_capacity_and_required_width_are_inverses(self):
        for current in (0.25, 1.0, 2.5):
            width = check_physics.width_for_current_mm(current, 10)
            self.assertAlmostEqual(
                check_physics.trace_current_capacity_a(width, 10), current, places=4,
                msg="width_for_current_mm(%s) does not carry %s A" % (current, current))

    def test_a_wider_trace_carries_more_and_a_hotter_one_carries_more(self):
        self.assertGreater(check_physics.trace_current_capacity_a(1.0, 10),
                           check_physics.trace_current_capacity_a(0.15, 10))
        self.assertGreater(check_physics.trace_current_capacity_a(0.5, 20),
                           check_physics.trace_current_capacity_a(0.5, 10))

    def test_the_default_trace_width_carries_well_under_an_amp(self):
        # 0.15 mm is what an autorouter leaves you if nobody says otherwise, and the whole point
        # of this check is that it is not a motor supply. IPC-2221 puts it near 0.6 A.
        self.assertLess(check_physics.trace_current_capacity_a(0.15, 10), 0.7)


class TraceCurrentTest(unittest.TestCase):
    def _board(self, widths, current, **rail):
        circuit = [net("MOTOR6V"), port("Load", "VCC"), component("Load", "simple_chip")]
        circuit += trace("MOTOR6V", ["Load.VCC"], widths)
        rules = {"physics": {"rails": {"MOTOR6V": dict({"max_current_a": current}, **rail)}}}
        return check_physics.run(circuit, rules)

    def test_a_rail_thinner_than_its_current_is_caught(self):
        findings = self._board([0.15], 1.5)
        self.assertEqual([f.rule for f in findings], ["trace-current"])
        self.assertEqual(findings[0].severity, "problem")
        self.assertIn("1.50 A", findings[0].detail)

    def test_a_rail_wide_enough_says_nothing(self):
        self.assertEqual(self._board([1.0], 1.5), [])

    def test_the_narrowest_segment_on_THAT_net_decides_it(self):
        # Per net, not per board. An early version compared every rail against the board's
        # globally narrowest trace, so widening the motor loop while leaving signals thin
        # reported the motor rail as thin — it was measuring a different net entirely.
        findings = self._board([1.0, 1.0, 0.15, 1.0], 1.5)
        self.assertEqual(len(findings), 1, "a thin segment on the net must still be caught")
        self.assertIn("0.15 mm", findings[0].detail)


class ARefusalIsNotAPass(unittest.TestCase):
    """
    The property that matters most: not knowing must never look like being fine.

    A project whose worst risk is an unmeasured number should be told that. These assert the
    check reports it, and — separately — that reporting it does not fail the build, because a
    gate that is permanently red for a measurement nobody has taken gets switched off.
    """

    def test_an_unmeasured_rail_is_reported_rather_than_assumed_safe(self):
        circuit = [net("MOTOR6V")] + trace("MOTOR6V", [], [0.15])
        findings = check_physics.run(
            circuit, {"physics": {"rails": {"MOTOR6V": {"max_current_a": None}}}})
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].severity, "needs-measurement")
        self.assertIn("nothing here can be verified", findings[0].detail)

    def test_a_rail_with_no_copper_at_all_is_still_reported_per_rail(self):
        # Nothing routed used to abandon the whole check, which preempted every rule below it.
        findings = check_physics.run(
            [net("MOTOR6V")], {"physics": {"rails": {"MOTOR6V": {"max_current_a": 1.0}}}})
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].severity, "needs-measurement")
        self.assertIn("no routed trace of its own", findings[0].detail)

    def test_an_unmeasured_rail_does_not_fail_the_build(self):
        circuit = [net("MOTOR6V")] + trace("MOTOR6V", [], [0.15])
        findings = check_physics.run(
            circuit, {"physics": {"rails": {"MOTOR6V": {"max_current_a": None}}}})
        self.assertEqual([f for f in findings if f.severity == "problem"], [])

    def test_a_rail_served_by_a_pour_is_recorded_as_unchecked_not_as_clean(self):
        circuit = [net("GND")]
        findings = check_physics.run(circuit, {"physics": {"rails": {
            "GND": {"max_current_a": 1.5, "served_by_pour": True}}}})
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].severity, "needs-measurement")
        self.assertIn("pour", findings[0].detail)


class CapacitorVoltageTest(unittest.TestCase):
    """
    The mechanism by which a 220uF 4V tantalum landed on a 6.4V battery rail: nothing in the
    design stated a voltage at all, so the part was chosen by whatever a supplier matched.
    """

    def _rail_with_cap(self, rating, volts=6.4, chemistry="tantalum"):
        fields = {} if rating is None else {"max_voltage_rating": rating}
        circuit = [net("MOTOR6V"), component("Bulk", "simple_capacitor", **fields),
                   port("Bulk", "pin1")]
        circuit += trace("MOTOR6V", ["Bulk.pin1"])
        findings = check_physics.run(circuit, {"physics": {"rails": {"MOTOR6V": {
            "nominal_volts": volts, "capacitor_chemistry": chemistry}}}})
        return [f for f in findings if f.rule == "capacitor-voltage"]

    def test_a_capacitor_with_no_stated_rating_is_caught(self):
        findings = self._rail_with_cap(None)
        self.assertEqual([f.rule for f in findings], ["capacitor-voltage"])
        self.assertIn("no stated voltage rating", findings[0].detail)

    def test_a_capacitor_rated_below_the_rail_is_caught(self):
        findings = self._rail_with_cap(4.0)
        self.assertEqual(len(findings), 1)
        self.assertIn("rated 4.0 V on a 6.4 V rail", findings[0].detail)

    def test_a_properly_derated_capacitor_says_nothing(self):
        self.assertEqual(self._rail_with_cap(25.0), [])

    def test_a_tantalum_is_derated_harder_than_a_ceramic(self):
        # A tantalum above its rating fails SHORT, which across a battery pack is a fire.
        self.assertGreater(check_physics.VOLTAGE_DERATING["tantalum"],
                           check_physics.VOLTAGE_DERATING["ceramic"])
        self.assertEqual(self._rail_with_cap(10.0, chemistry="ceramic"), [])
        self.assertEqual(len(self._rail_with_cap(10.0, chemistry="tantalum")), 1)


class ResistorPowerTest(unittest.TestCase):
    """
    A netlist records neither the current through a resistor nor the voltage across it.

    The rule used to compute I^2 * R with the RAIL's maximum current for every resistor on that
    rail. For a shunt that is exactly right — a shunt is in series with the rail — and these
    tests only ever exercised a shunt, which is why the arithmetic looked sound. For a 100k
    pull-up on the same rail it claims 225 kW.

    It never fired on a real board anyway: `footprint_of` read a field the engine had moved and
    returned None for all 28 components, and the package table was keyed `0603` while the engine
    emits `res0603`. Three independent faults, and being broken is the only reason nobody noticed
    the arithmetic was wrong for everything but the case under test.

    The design current is now stated by the design, because that is a thing a person knows and a
    netlist does not — and a resistor with no stated current is reported as unassessed rather
    than passed.
    """

    def _shunt(self, ohms, footprint, current, state_it=True):
        circuit = [net("MOTOR6V"), component("Shunt", "simple_resistor", resistance=ohms),
                   port("Shunt", "pin1"),
                   # cad_component, which is where the engine actually puts the footprint. The
                   # old fixture used pcb_component with a bare "0805" and so described a netlist
                   # the engine had stopped emitting.
                   {"type": "cad_component", "source_component_id": "Shunt",
                    "footprinter_string": footprint}]
        circuit += trace("MOTOR6V", ["Shunt.pin1"], [1.0])
        rail = {"max_current_a": current}
        if state_it:
            rail["resistor_currents"] = {"Shunt": current}
        return check_physics.run(circuit, {"physics": {"rails": {"MOTOR6V": rail}}})

    def test_a_shunt_beyond_its_package_rating_is_caught(self):
        findings = [f for f in self._shunt(0.33, "res0805", 2.0) if f.rule == "resistor-power"]
        self.assertEqual(len(findings), 1, findings)
        self.assertEqual(findings[0].severity, "problem")
        self.assertIn("0805", findings[0].detail)

    def test_the_same_job_in_a_bigger_package_at_a_lower_value_is_fine(self):
        # The change that made this measurement stop mattering: 0.1R in a 2512 is 0.40 W at 2 A.
        self.assertEqual(
            [f for f in self._shunt(0.1, "res2512", 2.0) if f.rule == "resistor-power"], [])

    def test_a_resistor_with_no_stated_current_is_reported_not_passed(self):
        findings = [f for f in self._shunt(0.33, "res0805", 2.0, state_it=False)
                    if f.rule == "resistor-power"]
        self.assertEqual(len(findings), 1, findings)
        self.assertEqual(findings[0].severity, "could-not-run")
        self.assertIn("could not be assessed", findings[0].detail)

    def test_the_footprint_is_read_from_where_the_engine_puts_it(self):
        # The defect that made every one of these rules inert on a real board. Measured against
        # the reference board before the fix: 0 of 28 components resolved.
        circuit = [component("R1", "simple_resistor", resistance=100),
                   {"type": "cad_component", "source_component_id": "R1",
                    "footprinter_string": "res0603"}]
        self.assertEqual(check_physics.Board(circuit).footprint_of("R1"), "res0603")

    def test_the_package_table_matches_what_the_engine_emits(self):
        # Keyed "0603" and matched with startswith against "res0603", which can never be true.
        self.assertEqual(check_physics.package_of("res0603"), "0603")
        self.assertIn(check_physics.package_of("res0603"), check_physics.PACKAGE_POWER_W)


class AnEmptyRulesFileIsNotACleanBoardTest(unittest.TestCase):
    """
    `spark init` writes `rails: {}` and `i2c_hz: null` on purpose — it guesses nothing. So the
    default state of every new project was the state in which three of this tool's four rules did
    not run, and `check_all` rendered the silence as `[ok  ] physics`.

    `commands/init.md` promises the opposite in as many words: "a check reading a null reports it
    as unverifiable rather than passing it."
    """

    def test_no_rails_stated_is_reported_not_passed(self):
        findings = check_physics.run([net("V33")], {"physics": {"rails": {}}})
        rails = [f for f in findings if f.rule == "rails-not-stated"]
        self.assertEqual(len(rails), 1, findings)
        self.assertEqual(rails[0].severity, "could-not-run")
        self.assertIn("three of this tool's four rules", rails[0].detail)

    def test_a_board_with_an_i2c_bus_and_no_clock_is_reported(self):
        findings = check_physics.run([net("SDA"), net("SCL")], {"physics": {"rails": {}}})
        i2c = [f for f in findings if f.rule == "i2c-rise-time"]
        self.assertEqual(len(i2c), 1, findings)
        self.assertEqual(i2c[0].severity, "could-not-run")

    def test_a_board_with_no_bus_is_not_nagged_about_i2c(self):
        # The first version of this fix asked every board about I2C, including boards with none
        # — while its own remedy text said an empty list should stop it asking. A check that
        # nags about what is not there is how a check earns a reputation for noise.
        findings = check_physics.run([net("V33")], {"physics": {"rails": {}}})
        self.assertEqual([f for f in findings if f.rule == "i2c-rise-time"], [])


class I2cRiseTimeTest(unittest.TestCase):
    def _bus(self, ohms, bus_hz=400_000, capacitance_pf=100):
        circuit = [net("SDA")]
        for index, value in enumerate(ohms):
            name = "Pullup%d" % index
            circuit += [component(name, "simple_resistor", resistance=value), port(name, "pin1")]
            circuit += trace("SDA", ["%s.pin1" % name], trace_id="t%d" % index)
        findings = check_physics.run(circuit, {"i2c_buses": ["SDA"], "physics": {
            "i2c_hz": bus_hz, "i2c_bus_capacitance_pf": capacitance_pf, "rails": {}}})
        return [f for f in findings if f.rule == "i2c-rise-time"]

    def test_a_pullup_too_weak_for_the_bus_speed_is_caught(self):
        findings = self._bus([10_000])
        self.assertEqual([f.rule for f in findings], ["i2c-rise-time"])
        self.assertIn("300 ns", findings[0].detail)

    def test_the_same_pullup_is_fine_at_a_slower_bus_speed(self):
        # Changing the bus speed is free; changing a resistor costs a board revision.
        self.assertEqual(self._bus([10_000], bus_hz=100_000), [])

    def test_parallel_pullups_pull_harder_and_are_combined(self):
        # Two 4.7k in parallel is 2.35k, which passes where one 4.7k would not.
        self.assertEqual(len(self._bus([4_700])), 1)
        self.assertEqual(self._bus([4_700, 4_700]), [])



class OneCopyOfPackageOfTest(unittest.TestCase):
    def test_package_of_is_check_footprints_own_function_not_a_copy(self):
        # Audit A7: loaded by file path, `check_footprints` was instantiated a second time and
        # `package_of` here was a different function object from the one every test of it runs.
        self.assertIs(check_physics.package_of, check_footprints.package_of)


class EachRuleHasANameTest(unittest.TestCase):
    """
    Audit B16: the four rules were reached only through `run`. Each is named here for the one
    property every rule in this plugin owes (W1): with nothing to look at, or a limit it does not
    know, it says so — a `could-not-run` or `needs-measurement` finding, never a silent pass.
    """

    def test_i2c_rise_time_with_a_bus_speed_it_has_no_limit_for_is_could_not_run(self):
        findings = check_physics.check_i2c_rise_time(check_physics.Board([]), {}, 123456, 100)
        self.assertEqual([f.severity for f in findings], ["could-not-run"])
        self.assertIn("no rise-time limit known", findings[0].detail)

    def test_trace_currents_with_no_rails_stated_finds_nothing_and_says_nothing(self):
        # Nothing was asked, so nothing is answered — `check_all` reports the unasked separately.
        self.assertEqual(check_physics.check_trace_currents(check_physics.Board([]), {}, 10), [])

    def test_trace_currents_for_a_rail_with_no_trace_does_not_pass_it(self):
        rails = {"X": {"max_current_a": 1.0}}
        findings = check_physics.check_trace_currents(check_physics.Board([]), rails, 10)
        self.assertTrue(findings, "a rail with a stated current and no copper was passed in silence")
        self.assertNotEqual(findings[0].severity, "problem")   # it could not measure, it did not fail it

    def test_capacitor_voltages_with_no_rails_finds_nothing(self):
        self.assertEqual(check_physics.check_capacitor_voltages(check_physics.Board([]), {}), [])

    def test_resistor_power_with_no_resistors_finds_nothing(self):
        self.assertEqual(check_physics.check_resistor_power(check_physics.Board([]), {}), [])


class TheExitCodeFollowsTheFindingsTest(unittest.TestCase):
    """
    P34, and W12. Three mutations escaped this suite when the fix landed — the status built from
    `problems` alone, the exit code not following the status, and the renderer assuming every
    could-not-run carries a `reason` — because nothing here had ever called `main()`. A file whose
    docstring says an unchecked rail must never look like a passing one answered `status: ok`,
    exit 0, over findings that were every one of them could-not-run.
    """

    CIRCUIT = [
        {"type": "source_component", "source_component_id": "c1", "name": "U1", "ftype": "simple_chip"},
        {"type": "source_net", "source_net_id": "n1", "name": "V33"},
        {"type": "source_port", "source_port_id": "p1", "source_component_id": "c1", "name": "VCC"},
        {"type": "source_trace", "source_trace_id": "t1",
         "connected_source_port_ids": ["p1"], "connected_source_net_ids": ["n1"]},
    ]

    def _run(self, rules, json_flag=False):
        import contextlib
        import io
        import json as json_module
        import tempfile
        root = Path(tempfile.mkdtemp())
        (root / "circuit.json").write_text(json_module.dumps(self.CIRCUIT))
        (root / "rules.json").write_text(json_module.dumps(rules))
        argv = [str(root / "circuit.json"), "--rules", str(root / "rules.json")]
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            code = check_physics.main(argv + (["--json"] if json_flag else []))
        return code, out.getvalue()

    def test_a_run_whose_findings_are_all_could_not_run_says_so_and_exits_two(self):
        import json as json_module
        code, said = self._run({"physics": {}}, json_flag=True)
        payload = json_module.loads(said)
        self.assertEqual(payload["status"], "could-not-run", said)
        self.assertEqual(code, check_physics.EXIT_COULD_NOT_RUN)
        self.assertTrue(payload["findings"], "the fixture must produce a finding to be worth anything")
        self.assertEqual({f["severity"] for f in payload["findings"]}, {"could-not-run"})

    def test_the_human_output_renders_that_run_rather_than_raising(self):
        # The renderer read `reason` unconditionally, which only the early refusals carry.
        code, said = self._run({"physics": {}})
        self.assertEqual(code, check_physics.EXIT_COULD_NOT_RUN)
        self.assertIn("could-not-run", said)
        self.assertIn("rails", said)

    def test_a_rail_fully_stated_leaves_nothing_unchecked(self):
        code, said = self._run({"physics": {"rails": {"V33": {"nominal_volts": 3.3, "max_current_a": 0.5}}}},
                               json_flag=True)
        self.assertEqual(code, check_physics.EXIT_OK, said)

if __name__ == "__main__":
    unittest.main()
