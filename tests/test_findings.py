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

# The same defect, found again by a reviewer that phrased it completely differently.
MP3_REWORDED = {
    "dimension": "power",
    "anchors": ["net:VBAT", "port:Mp3Player.VCC"],
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


class MeasurementTest(unittest.TestCase):
    def test_supplying_a_number_unblocks_what_rested_on_it(self):
        """What makes 'assume it for now' a bookmark rather than a risk."""
        shelf = store()
        findings.merge(shelf, [MP3], NAMESPACE)
        shelf["findings"][0]["status"] = findings.BLOCKED

        reopened = findings.record_measurement(
            shelf, "mp3-idle-current", "18.4", "mA", "DMM in series with VBAT")

        self.assertEqual(len(reopened), 1)
        self.assertEqual(shelf["findings"][0]["status"], findings.OPEN)
        self.assertEqual(shelf["measurements"]["mp3-idle-current"]["value"], "18.4")

    def test_an_unrelated_measurement_changes_nothing(self):
        shelf = store()
        findings.merge(shelf, [MP3], NAMESPACE)
        shelf["findings"][0]["status"] = findings.BLOCKED
        self.assertEqual(findings.record_measurement(shelf, "motor-stall", "350", "mA", "DMM"), [])
        self.assertEqual(shelf["findings"][0]["status"], findings.BLOCKED)


class PriorityTest(unittest.TestCase):
    def test_blocked_work_comes_first_because_clearing_it_is_cheap(self):
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
