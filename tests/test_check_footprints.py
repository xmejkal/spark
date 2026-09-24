"""
Proof that the buildability check bites, and — mostly — that it does not cry wolf.

This check is unusual in that its dangerous failure is the FALSE POSITIVE. Every rule here fires
on a board that passes DRC and looks right, so the only thing standing between it and being
switched off is that when it speaks, it is correct. Its first version asked "does a 0.64 mm
square header pin fit?" of every plated hole on the board and reported four JST connectors and a
radial capacitor as unbuildable. None of those take a header pin.

So the tests below weigh both ways: the real defect is caught, and the parts that merely have
small holes for their own good reasons are left alone.

    python3 -m unittest discover -s tests
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import check_footprints  # noqa: E402


def holes(component, drill, pad, positions):
    return [{"type": "pcb_plated_hole", "pcb_component_id": "pcb_" + component,
             "hole_diameter": drill, "outer_diameter": pad, "x": x, "y": y}
            for x, y in positions]


def named(component):
    return [{"type": "source_component", "source_component_id": component, "name": component},
            {"type": "pcb_component", "pcb_component_id": "pcb_" + component,
             "source_component_id": component}]


def row(count, pitch):
    return [(index * pitch, 0.0) for index in range(count)]


class HeaderDetectionTest(unittest.TestCase):
    """Decided from geometry, because a footprint's name is not always available or honest."""

    def test_a_2_54_row_is_a_header(self):
        self.assertTrue(check_footprints.is_header(row(6, 2.54)))

    def test_a_jst_at_2_0_is_not(self):
        self.assertFalse(check_footprints.is_header(row(4, 2.0)))

    def test_a_radial_capacitor_at_2_5_is_not(self):
        # Only 0.04 mm from a header's pitch, with round leads half the thickness. This is the
        # case that made the first version report a working capacitor as unbuildable.
        self.assertFalse(check_footprints.is_header(row(2, 2.5)))

    def test_two_holes_are_never_a_header(self):
        self.assertFalse(check_footprints.is_header(row(2, 2.54)))


class ThroughHoleDrillTest(unittest.TestCase):
    def test_a_header_drilled_too_small_for_its_pin_is_caught(self):
        circuit = named("Mcu") + holes("Mcu", 0.9, 1.5, row(6, 2.54))
        findings = check_footprints.check_through_hole_drills(circuit)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].subject, "Mcu")
        self.assertIn("does not go in", findings[0].detail)

    def test_the_same_header_at_1_0_mm_is_fine(self):
        circuit = named("Mcu") + holes("Mcu", 1.0, 1.7, row(6, 2.54))
        self.assertEqual(check_footprints.check_through_hole_drills(circuit), [])

    def test_a_connector_with_its_own_thinner_leads_is_left_alone(self):
        circuit = named("Speaker") + holes("Speaker", 0.75, 1.2, row(2, 2.0))
        self.assertEqual(check_footprints.check_through_hole_drills(circuit), [])

    def test_one_finding_per_footprint_not_per_hole(self):
        # 32 identical messages about one footprint is how a real finding gets scrolled past.
        circuit = named("Mcu") + holes("Mcu", 0.9, 1.5, row(32, 2.54))
        self.assertEqual(len(check_footprints.check_through_hole_drills(circuit)), 1)


class ViaAndRingTest(unittest.TestCase):
    def test_default_vias_below_a_cheap_process_are_caught(self):
        circuit = [{"type": "pcb_via", "hole_diameter": 0.2, "outer_diameter": 0.3}]
        findings = check_footprints.check_vias(circuit)
        self.assertEqual(len(findings), 1)
        self.assertIn("0.3/0.6", findings[0].detail)

    def test_vias_a_cheap_process_will_quote_are_fine(self):
        circuit = [{"type": "pcb_via", "hole_diameter": 0.3, "outer_diameter": 0.6}]
        self.assertEqual(check_footprints.check_vias(circuit), [])

    def test_a_thin_annular_ring_is_caught(self):
        circuit = named("Mcu") + holes("Mcu", 1.0, 1.2, row(3, 2.54))
        findings = check_footprints.check_annular_rings(circuit)
        self.assertEqual(len(findings), 1)
        self.assertIn("ring", findings[0].detail)


class PackageHoldsItsValueTest(unittest.TestCase):
    def _cap(self, farads, footprint):
        circuit = [
            {"type": "source_component", "source_component_id": "C1", "name": "C1",
             "ftype": "simple_capacitor", "capacitance": farads},
            {"type": "pcb_component", "pcb_component_id": "pcbC1",
             "source_component_id": "C1", "footprinter_string": footprint}]
        return check_footprints.check_package_holds_the_value(circuit)

    def test_220uF_on_an_0805_is_caught(self):
        findings = self._cap(220e-6, "cap0805")
        self.assertEqual(len(findings), 1)
        self.assertIn("220 uF in a 0805", findings[0].detail)

    def test_100nF_on_an_0603_is_fine(self):
        self.assertEqual(self._cap(100e-9, "cap0603"), [])

    def test_a_through_hole_package_is_not_judged_by_this_rule(self):
        # radial_d6.3_p2.5 holds 220 uF happily; the rule is about chip packages.
        self.assertEqual(self._cap(220e-6, "radial_d6.3_p2.5"), [])


class CrossPluggableTest(unittest.TestCase):
    def _two(self, footprint_a, footprint_b, distance):
        circuit = []
        for name, footprint, x in (("MotorOut", footprint_a, 0.0),
                                   ("Speaker", footprint_b, distance)):
            circuit += [
                {"type": "source_component", "source_component_id": name, "name": name},
                {"type": "pcb_component", "pcb_component_id": "pcb_" + name,
                 "source_component_id": name, "footprinter_string": footprint,
                 "center": {"x": x, "y": 0.0}}]
        return check_footprints.check_cross_pluggable_connectors(circuit)

    def test_two_identical_connectors_side_by_side_are_caught(self):
        findings = self._two("jst_ph_2", "jst_ph_2", 8.0)
        self.assertEqual(len(findings), 1)
        self.assertIn("either plug fits either socket", findings[0].detail)

    def test_different_series_cannot_be_cross_plugged(self):
        self.assertEqual(self._two("jst_ph_2", "jst_xh_2", 8.0), [])

    def test_far_apart_is_not_reported(self):
        # The failure needs a person holding two plugs over two sockets at once.
        self.assertEqual(self._two("jst_ph_2", "jst_ph_2", 80.0), [])


if __name__ == "__main__":
    unittest.main()
