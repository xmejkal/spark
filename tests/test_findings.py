"""
The findings store, and the four mechanisms that decide whether it is usable.

Identity has to survive rewording, hallucinated anchors have to be refused, a wrong finding has
to be retirable, and a fix that comes undone has to be noticed. Miss any one and the tool is
noise by its third run — so each has a test that fails without it.

    python3 -m unittest discover -s tests
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import findings  # noqa: E402

# The real bin's namespace, small enough to write out and real enough to mean something.
NAMESPACE = {
    "comp:XIAO", "comp:Mp3Player", "comp:MotorDriver", "comp:LipoBattery",
    "net:VBAT", "net:V33", "net:GND", "net:MOTOR6V",
    "port:Mp3Player.VCC", "port:XIAO.SDA",
}

MP3 = {
    "dimension": "power",
    "anchors": ["port:Mp3Player.VCC", "net:VBAT"],
    "what": "Mp3Player.VCC connects directly to net.VBAT with no switch or enable",
    "consequence": "~15-25 mA idle, roughly 40x everything else; deep sleep buys days not months",
    "severity": "caveat",
    "rests_on": ["mp3-idle-current"],
}

# The same defect, found again by a reviewer that phrased it completely differently — and that
# listed its anchors in another order, with one repeated, which is what a second reviewer
# actually does.
MP3_REWORDED = {
    "dimension": "power",
    "anchors": ["net:VBAT", "port:Mp3Player.VCC", "net:VBAT"],
    "what": "The DFR0534 can never be powered down; it has no enable pin and sits on the cell",
    "consequence": "Idle draw dominates the battery budget",
    "severity": "caveat",
}


def store():
    return {"schema": findings.SCHEMA, "findings": []}


class IdentityTest(unittest.TestCase):
    def test_the_same_defect_worded_differently_is_one_finding(self):
        """The whole reason identity is structural rather than a name."""
        shelf = store()
        findings.merge(shelf, [MP3], NAMESPACE)
        added, _, duplicates, _ = findings.merge(shelf, [MP3_REWORDED], NAMESPACE)

        self.assertEqual(added, [])
        self.assertEqual(len(duplicates), 1)
        self.assertEqual(len(shelf["findings"]), 1)

    def test_anchor_order_does_not_change_identity(self):
        self.assertEqual(
            findings.key_for("power", ["net:VBAT", "port:Mp3Player.VCC"]),
            findings.key_for("power", ["port:Mp3Player.VCC", "net:VBAT"]))

    def test_the_same_anchors_in_a_different_dimension_are_a_different_finding(self):
        self.assertNotEqual(
            findings.key_for("power", ["net:VBAT"]),
            findings.key_for("thermal", ["net:VBAT"]))


class HallucinationTest(unittest.TestCase):
    def test_a_finding_about_a_net_that_does_not_exist_is_refused(self):
        invented = dict(MP3, anchors=["net:V5_SW"])
        added, refused, _, _ = findings.merge(store(), [invented], NAMESPACE)

        self.assertEqual(added, [])
        self.assertEqual(len(refused), 1)
        self.assertIn("net:V5_SW", refused[0][1])

    def test_a_finding_missing_its_consequence_is_refused(self):
        vague = dict(MP3)
        del vague["consequence"]
        _, refused, _, _ = findings.merge(store(), [vague], NAMESPACE)
        self.assertIn("no consequence", refused[0][1])

    def test_requirement_and_file_anchors_are_not_checked_against_the_netlist(self):
        """They are real anchors; they just do not name circuit elements."""
        self.assertEqual(findings.unresolved(["req:0", "file:power.py"], NAMESPACE), [])


class RetiringAWrongFindingTest(unittest.TestCase):
    def test_a_rejected_finding_is_not_raised_again(self):
        """
        An LLM reviewer is confidently wrong as a matter of course. Without this the same wrong
        finding returns on every run and the tool becomes something you stop reading.
        """
        shelf = store()
        findings.merge(shelf, [MP3], NAMESPACE)
        shelf["findings"][0]["status"] = findings.REJECTED

        added, _, duplicates, _ = findings.merge(shelf, [MP3_REWORDED], NAMESPACE)
        self.assertEqual(added, [])
        self.assertEqual(len(duplicates), 1)
        self.assertEqual(shelf["findings"][0]["status"], findings.REJECTED)

    def test_rejected_findings_are_not_offered_as_work(self):
        self.assertEqual(findings.rank([dict(MP3, status=findings.REJECTED, key="x")]), [])


class RegressionTest(unittest.TestCase):
    def test_a_resolved_finding_that_comes_back_is_flagged_not_reopened(self):
        """The oscillation detector: something undid a fix, and that needs a person."""
        shelf = store()
        findings.merge(shelf, [MP3], NAMESPACE)
        shelf["findings"][0]["status"] = findings.RESOLVED

        added, _, _, regressions = findings.merge(shelf, [MP3_REWORDED], NAMESPACE)
        self.assertEqual(added, [])
        self.assertEqual(len(regressions), 1)
        self.assertEqual(shelf["findings"][0]["status"], findings.REGRESSED)


class ForgeryTest(unittest.TestCase):
    """
    A reviewer says what it found. It does not get to say what a person decided about it.

    The whole value of `accepted` and `rejected` is that they mean a human ruled. merge() used to
    copy the incoming object wholesale, so an LLM could write a resolution record claiming
    sign-off and it would persist looking exactly like one.
    """

    def test_a_reviewer_cannot_write_a_decision(self):
        forged = dict(MP3, resolution={"reason": "signed off by Petr"}, status="accepted")
        shelf = store()
        findings.merge(shelf, [forged], NAMESPACE)
        stored = shelf["findings"][0]
        self.assertNotIn("resolution", stored)
        self.assertEqual(stored["status"], findings.BLOCKED)

    def test_a_reviewer_cannot_backdate_when_a_finding_was_first_seen(self):
        shelf = store()
        findings.merge(shelf, [dict(MP3, first_seen="2020-01-01")], NAMESPACE, today="2026-09-24")
        self.assertEqual(shelf["findings"][0]["first_seen"], "2026-09-24")


class MeasurementTest(unittest.TestCase):
    """
    A number in the store must be a number somebody obtained, and must say how.

    This is not paperwork. The example value from the documentation once walked into a real
    project's store and sat there looking exactly like a reading, while the handover note still
    said the number had never been taken. Every test here exists because of that.
    """

    def test_a_finding_waiting_on_a_number_is_blocked_on_arrival(self):
        """Otherwise the reopen path can never fire, and the whole loop is decorative."""
        shelf = store()
        findings.merge(shelf, [MP3], NAMESPACE)
        self.assertEqual(shelf["findings"][0]["status"], findings.BLOCKED)

    def test_a_finding_resting_on_nothing_is_simply_open(self):
        shelf = store()
        findings.merge(shelf, [dict(MP3, rests_on=[])], NAMESPACE)
        self.assertEqual(shelf["findings"][0]["status"], findings.OPEN)

    def test_supplying_a_number_unblocks_what_rested_on_it(self):
        shelf = store()
        findings.merge(shelf, [MP3], NAMESPACE)

        reopened = findings.record_measurement(
            shelf, "mp3-idle-current", "18.4", "mA", "measured", "DMM in series with VBAT")

        self.assertEqual(len(reopened), 1)
        self.assertEqual(shelf["findings"][0]["status"], findings.OPEN)
        self.assertEqual(shelf["measurements"]["mp3-idle-current"]["source"], "measured")

    def test_a_measurement_must_say_where_it_came_from(self):
        with self.assertRaises(ValueError) as refused:
            findings.record_measurement(store(), "x", "18.4", "mA", "DMM in series")
        self.assertIn("source must be one of", str(refused.exception))

    def test_a_measured_value_must_name_its_instrument(self):
        """A reading with no instrument is not reproducible, so it is not a reading."""
        with self.assertRaises(ValueError) as refused:
            findings.record_measurement(store(), "x", "18.4", "mA", "measured")
        self.assertIn("instrument", str(refused.exception))

    def test_an_estimate_needs_no_instrument_and_is_marked_as_one(self):
        shelf = store()
        findings.record_measurement(shelf, "x", "15", "mA", "estimate")
        self.assertEqual(shelf["measurements"]["x"]["source"], "estimate")

    def test_replacing_a_number_keeps_the_one_it_replaced(self):
        """A second reading that disagrees with the first is information, not a correction."""
        shelf = store()
        findings.record_measurement(shelf, "x", "15", "mA", "estimate")

        with self.assertRaises(ValueError) as refused:
            findings.record_measurement(shelf, "x", "18.4", "mA", "measured", "DMM")
        self.assertIn("--supersede", str(refused.exception))

        findings.record_measurement(
            shelf, "x", "18.4", "mA", "measured", "DMM", supersede=True)
        entry = shelf["measurements"]["x"]
        self.assertEqual(entry["value"], "18.4")
        self.assertEqual(entry["superseded"][0]["value"], "15")

    def test_a_number_that_moves_regresses_what_was_fixed_on_it(self):
        shelf = store()
        findings.merge(shelf, [MP3], NAMESPACE)
        shelf["findings"][0]["status"] = findings.RESOLVED

        findings.record_measurement(
            shelf, "mp3-idle-current", "2.1", "mA", "measured", "DMM")
        self.assertEqual(shelf["findings"][0]["status"], findings.REGRESSED)

    def test_an_unrelated_measurement_changes_nothing(self):
        shelf = store()
        findings.merge(shelf, [MP3], NAMESPACE)
        self.assertEqual(
            findings.record_measurement(shelf, "motor-stall", "350", "mA", "estimate"), [])
        self.assertEqual(shelf["findings"][0]["status"], findings.BLOCKED)

    def test_unfilled_says_which_numbers_are_still_missing(self):
        shelf = store()
        findings.merge(shelf, [MP3], NAMESPACE)
        self.assertEqual(findings.unfilled(shelf["findings"][0], shelf), ["mp3-idle-current"])


class PriorityTest(unittest.TestCase):
    def test_blocked_work_comes_first_because_clearing_it_is_cheap(self):  # noqa: D102
        ordered = findings.rank([
            dict(MP3, key="a", status=findings.OPEN, severity="caveat"),
            dict(MP3, key="b", status=findings.BLOCKED, severity="caveat"),
            dict(MP3, key="c", status=findings.OPEN, severity="problem"),
        ])
        self.assertEqual([f["key"] for f in ordered], ["b", "c", "a"])

    def test_problems_outrank_caveats(self):
        ordered = findings.rank([
            dict(MP3, key="caveat", status=findings.OPEN, severity="caveat"),
            dict(MP3, key="problem", status=findings.OPEN, severity="problem"),
        ])
        self.assertEqual(ordered[0]["key"], "problem")


class AnchorNamespaceTest(unittest.TestCase):
    #: A netlist in the shape tscircuit emits, small enough to read. The real thing is 999
    #: elements for a 24-component board, and 93% of it is geometry this never looks at.
    CIRCUIT = [
        {"type": "source_component", "source_component_id": "c1", "name": "Mp3Player"},
        {"type": "source_component", "source_component_id": "c2", "name": "XIAO"},
        {"type": "source_net", "name": "VBAT"},
        {"type": "source_net", "name": "GND"},
        {"type": "source_port", "source_component_id": "c1", "name": "VCC"},
        {"type": "source_port", "source_component_id": "c2", "name": "SDA"},
        {"type": "pcb_trace", "route": []},
    ]

    def test_it_names_components_nets_and_qualified_ports(self):
        namespace = findings.anchor_namespace(self.CIRCUIT)
        self.assertEqual(namespace, {
            "comp:Mp3Player", "comp:XIAO", "net:VBAT", "net:GND",
            "port:Mp3Player.VCC", "port:XIAO.SDA"})

    def test_a_port_is_qualified_so_two_parts_may_share_a_pin_name(self):
        circuit = self.CIRCUIT + [
            {"type": "source_port", "source_component_id": "c2", "name": "VCC"}]
        namespace = findings.anchor_namespace(circuit)
        self.assertIn("port:Mp3Player.VCC", namespace)
        self.assertIn("port:XIAO.VCC", namespace)

    def test_it_is_built_from_the_real_circuit_json(self):
        import json
        circuit_path = ROOT.parent / "smartbin-local" / "dist" / "board" / "circuit.json"
        if not circuit_path.exists():
            self.skipTest("the bin has not been built")

        namespace = findings.anchor_namespace(json.loads(circuit_path.read_text()))
        self.assertIn("comp:Mp3Player", namespace)
        self.assertIn("net:VBAT", namespace)
        self.assertIn("port:Mp3Player.VCC", namespace)
        self.assertNotIn("net:V5_SW", namespace)


if __name__ == "__main__":
    unittest.main()


class SimulatedMeasurementTest(unittest.TestCase):
    """
    A pretend reading must be useful for a demo and useless as evidence.

    The reason this is a separate source rather than a convincing `measured` is the incident that
    prompted it: a documentation example ended up in a live store with an instrument and a date,
    indistinguishable from a real reading.
    """

    def test_a_simulated_value_needs_no_instrument_and_is_marked(self):
        shelf = store()
        findings.record_measurement(shelf, "x", "15.3", "mA", "simulated")
        self.assertEqual(shelf["measurements"]["x"]["source"], "simulated")

    def test_it_is_not_evidence(self):
        self.assertIn("simulated", findings.NOT_EVIDENCE)
        self.assertNotIn("measured", findings.NOT_EVIDENCE)
        self.assertNotIn("datasheet", findings.NOT_EVIDENCE)

    def test_it_prints_with_a_warning_attached(self):
        shown = findings._measurement(
            "x", {"value": "15.3", "unit": "mA", "source": "simulated"})
        self.assertIn("NOT A READING", shown)

    def test_a_real_reading_carries_no_warning(self):
        shown = findings._measurement(
            "x", {"value": "15.3", "unit": "mA", "source": "measured", "instrument": "DMM"})
        self.assertNotIn("NOT A READING", shown)

    def test_a_simulated_value_still_unblocks_so_the_loop_can_be_demonstrated(self):
        shelf = store()
        findings.merge(shelf, [MP3], NAMESPACE)
        reopened = findings.record_measurement(
            shelf, "mp3-idle-current", "15.3", "mA", "simulated")
        self.assertEqual(len(reopened), 1)


class BenchSimulatorTest(unittest.TestCase):
    def setUp(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        import bench_sim
        self.bench = bench_sim

    def test_the_same_seed_gives_the_same_reading(self):
        """Otherwise a test that depends on a simulated value is flaky by construction."""
        self.assertEqual(self.bench.simulate("mp3-idle-current", seed=7)["value"],
                         self.bench.simulate("mp3-idle-current", seed=7)["value"])

    def test_a_reading_lands_inside_the_model_it_claims(self):
        reading = self.bench.simulate("mp3-idle-current", seed=1)
        low, high = self.bench.BENCH["mp3-idle-current"]["range"]
        self.assertGreaterEqual(reading["value"], low)
        self.assertLessEqual(reading["value"], high)

    def test_a_derived_reading_shows_its_arithmetic(self):
        """A number a demo cannot explain is the thing this exists to avoid."""
        reading = self.bench.simulate("motor-stall-current", seed=1)
        self.assertIn("/", reading["working"])
        self.assertEqual(reading["unit"], "A")

    def test_it_refuses_to_invent_a_measurement_it_has_no_model_for(self):
        with self.assertRaises(SystemExit) as refused:
            self.bench.simulate("cavity-depth", seed=1)
        self.assertIn("no bench model", str(refused.exception))
