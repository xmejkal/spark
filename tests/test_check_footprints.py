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


class WhereTheFootprintActuallyLivesTest(unittest.TestCase):
    """
    The engine moved `footprinter_string` from `pcb_component` to `cad_component`, and two rules
    read only the old place. On a real board that meant they examined nothing and said nothing.

    Every fixture in this file put the string on `pcb_component`, which is why the suite stayed
    green through the whole life of the bug — the tests described a netlist the engine had
    stopped emitting.
    """

    def _cap_on(self, element_type):
        return [
            {"type": "source_component", "source_component_id": "C1", "name": "C1",
             "ftype": "simple_capacitor", "capacitance": 220e-6},
            {"type": "pcb_component", "pcb_component_id": "pcbC1", "source_component_id": "C1"},
            {"type": element_type, "pcb_component_id": "pcbC1", "source_component_id": "C1",
             "footprinter_string": "cap0805"}]

    def test_a_footprint_on_cad_component_is_found(self):
        findings = check_footprints.check_package_holds_the_value(self._cap_on("cad_component"))
        self.assertEqual(len(findings), 1, "the rule did not see a cad_component footprint")

    def test_a_footprint_on_pcb_component_is_still_found(self):
        # Older netlists put it there, and dropping them would trade one silence for another.
        findings = check_footprints.check_package_holds_the_value(self._cap_on("pcb_component"))
        self.assertEqual(len(findings), 1)

    def test_a_component_with_no_footprint_anywhere_is_simply_absent(self):
        circuit = [{"type": "source_component", "source_component_id": "U1", "name": "U1"},
                   {"type": "pcb_component", "pcb_component_id": "pcbU1",
                    "source_component_id": "U1"}]
        self.assertEqual(check_footprints.footprint_by_component(circuit), {})


class CrossPluggableTest(unittest.TestCase):
    def _two(self, footprint_a, footprint_b, distance, pins_a=2, pins_b=2):
        """
        Two connectors, WITH PADS — because the rule compares pad geometry, not names.

        This fixture used to carry a footprint string and no pads at all. That was fine while the
        rule compared names, and it hid the fact that on a real board the names are not there:
        three components including both plug-in modules carry no footprinter string anywhere,
        because a part whose 3D body comes from a model file does not emit one.
        """
        circuit = []
        for name, footprint, x, pins in (("MotorOut", footprint_a, 0.0, pins_a),
                                         ("Speaker", footprint_b, distance, pins_b)):
            circuit += [
                {"type": "source_component", "source_component_id": name, "name": name},
                {"type": "pcb_component", "pcb_component_id": "pcb_" + name,
                 "source_component_id": name, "footprinter_string": footprint,
                 "center": {"x": x, "y": 0.0}}]
            circuit += [{"type": "pcb_plated_hole", "pcb_component_id": "pcb_" + name,
                         "hole_diameter": 1.0, "outer_diameter": 1.6,
                         "x": x + index * 2.0, "y": 0.0} for index in range(pins)]
        return check_footprints.check_cross_pluggable_connectors(circuit)

    def test_two_identical_connectors_side_by_side_are_caught(self):
        findings = self._two("jst_ph_2", "jst_ph_2", 8.0)
        self.assertEqual(len(findings), 1)
        self.assertIn("either plug fits either socket", findings[0].detail)

    def test_different_series_cannot_be_cross_plugged(self):
        self.assertEqual(self._two("jst_ph_2", "jst_xh_2", 8.0, pins_b=4), [])

    def test_two_identical_module_headers_are_caught_even_with_no_footprint_name(self):
        """
        The case that was missed on the real board, and the reason the rule is geometric now.

        Two pad-identical six-pin rows 24 mm apart, one carrying a 6 V motor supply and the other
        3.3 V logic. The old rule looked for `jst` or `conn` in a footprint NAME, and these two
        carry no name at all — a part whose 3D body comes from a model file emits none — so it
        examined nothing and reported nothing.
        """
        circuit = []
        for name, y in (("MotorDriver", 0.0), ("Mp3Player", 24.0)):
            circuit += [
                {"type": "source_component", "source_component_id": name, "name": name},
                {"type": "pcb_component", "pcb_component_id": "pcb_" + name,
                 "source_component_id": name, "center": {"x": 0.0, "y": y}}]
            circuit += [{"type": "pcb_plated_hole", "pcb_component_id": "pcb_" + name,
                         "hole_diameter": 1.0, "outer_diameter": 1.6,
                         "x": index * 2.54, "y": y} for index in range(6)]
        findings = check_footprints.check_cross_pluggable_connectors(circuit)
        self.assertEqual(len(findings), 1, findings)
        self.assertIn("MotorDriver", findings[0].subject)
        self.assertIn("Mp3Player", findings[0].subject)

    def test_two_identical_passives_are_not_reported(self):
        # Comparing geometry alone reported every pair of 0603s on a real board — twenty findings
        # for one real hazard, which is how a check gets switched off. Nothing plugs into a chip
        # resistor.
        circuit = []
        for name, x in (("R1", 0.0), ("R2", 4.0)):
            circuit += [
                {"type": "source_component", "source_component_id": name, "name": name},
                {"type": "pcb_component", "pcb_component_id": "pcb_" + name,
                 "source_component_id": name, "footprinter_string": "res0603",
                 "center": {"x": x, "y": 0.0}}]
            circuit += [{"type": "pcb_smtpad", "pcb_component_id": "pcb_" + name,
                         "x": x + index * 1.6, "y": 0.0} for index in range(2)]
        self.assertEqual(check_footprints.check_cross_pluggable_connectors(circuit), [])

    def test_two_identical_buttons_are_not_reported_either(self):
        # Four through-holes in a RECTANGLE is a soldered switch, not a socket. Fitting one in
        # the other's place is a silkscreen problem, not a cross-plugging hazard.
        circuit = []
        for name, x in (("BtnOpen", 0.0), ("BtnMode", 10.0)):
            circuit += [
                {"type": "source_component", "source_component_id": name, "name": name},
                {"type": "pcb_component", "pcb_component_id": "pcb_" + name,
                 "source_component_id": name, "footprinter_string": "pushbutton",
                 "center": {"x": x, "y": 0.0}}]
            circuit += [{"type": "pcb_plated_hole", "pcb_component_id": "pcb_" + name,
                         "hole_diameter": 1.0, "outer_diameter": 1.6,
                         "x": x + dx, "y": dy}
                        for dx in (0.0, 6.5) for dy in (0.0, 4.5)]
        self.assertEqual(check_footprints.check_cross_pluggable_connectors(circuit), [])

    def test_far_apart_is_not_reported(self):
        # The failure needs a person holding two plugs over two sockets at once.
        self.assertEqual(self._two("jst_ph_2", "jst_ph_2", 80.0), [])


class AHoleThisCannotReadIsNotAHoleThisApprovedTest(unittest.TestCase):
    """
    Both hole rules opened with a bare `continue` for an element they could not parse.

    On the board this tool was written for that skipped 10 of 70 plated holes in silence — and
    four of them are `pill`, the obround shape whose vendor-drawn finished hole is the flagship
    defect named in this module's own docstring. It then printed "buildable — holes take their
    pins, packages hold their values".
    """

    @staticmethod
    def _pill(count=4):
        return [{"type": "pcb_plated_hole", "shape": "pill", "pcb_component_id": "pcb_J1",
                 "x": index * 2.54, "y": 0.0} for index in range(count)]

    @staticmethod
    def _round():
        return [{"type": "pcb_plated_hole", "shape": "circle", "pcb_component_id": "pcb_J1",
                 "hole_diameter": 1.0, "outer_diameter": 1.6, "x": index * 2.54, "y": 0.0}
                for index in range(4)]

    def test_a_shape_the_rules_cannot_read_is_reported_not_skipped(self):
        unchecked = check_footprints.unchecked_in(check_footprints.run(self._pill()))
        self.assertTrue(unchecked, "four obround holes went through without a word")
        self.assertTrue(all(f.severity == "could-not-run" for f in unchecked))
        self.assertIn("pill", " ".join(f.detail for f in unchecked))

    def test_it_says_how_many_and_of_what_shape(self):
        # The count is what makes it actionable — "some holes" is not a thing anyone can chase.
        detail = " ".join(f.detail for f in check_footprints.run(self._pill(6)))
        self.assertIn("6 x pill", detail)

    def test_a_hole_it_can_read_produces_no_such_finding(self):
        self.assertEqual(check_footprints.unchecked_in(check_footprints.run(self._round())), [])

    def test_it_is_not_reported_as_a_problem_either(self):
        # "I could not read this" must not be dressed as "this will fail at assembly". A check
        # that cries wolf gets switched off, and then it catches nothing at all.
        self.assertEqual(check_footprints.problems_in(check_footprints.run(self._pill())), [])

    def test_the_rendering_does_not_call_the_board_buildable(self):
        rendered = check_footprints.render(check_footprints.run(self._pill()), "circuit.json")
        self.assertNotIn("buildable", rendered)
        self.assertIn("NOT EXAMINED", rendered)

    def test_a_board_it_could_fully_read_is_still_called_buildable(self):
        rendered = check_footprints.render(check_footprints.run(self._round()), "circuit.json")
        self.assertIn("buildable", rendered)


class APlaceholderIsNotMeasuredTest(unittest.TestCase):
    """
    An XT30 drawn as a JST PH was measured: 0.225 mm annular rings, reported as a defect about a
    part that is not on the board. Worse than noise — a real-sounding finding a person chases.

    Told which components are stand-ins, the rules' findings about them become one could-not-run
    each. Not dropped: a footprint nobody has drawn is precisely a thing this tool could not
    examine, and saying so is the difference between "not yet" and "fine".
    """

    @staticmethod
    def thin_ring_connector(name):
        # A 2-pin connector whose ring is under the process minimum — the real XT30 case.
        return [{"type": "pcb_plated_hole", "shape": "pill", "pcb_component_id": "pcb_" + name,
                 "hole_width": 1.6, "hole_height": 0.75, "outer_width": 2.4, "outer_height": 1.2,
                 "x": i * 2.0, "y": 0.0} for i in range(2)] + named(name)

    def test_a_placeholder_is_reported_as_could_not_run_not_measured(self):
        findings = check_footprints.run(self.thin_ring_connector("Xt30"), placeholders=["Xt30"])
        self.assertEqual(check_footprints.problems_in(findings), [])
        unchecked = check_footprints.unchecked_in(findings)
        self.assertEqual([f.subject for f in unchecked], ["Xt30"])
        self.assertEqual(unchecked[0].rule, "placeholder-footprint")

    def test_the_same_geometry_IS_measured_when_it_is_real(self):
        # The control. Without it the test above passes for a checker that measures nothing.
        findings = check_footprints.run(self.thin_ring_connector("Xt30"))
        self.assertTrue(any(f.rule == "annular-ring" for f in check_footprints.problems_in(findings)))

    def test_a_placeholder_not_on_this_board_is_ignored_rather_than_reported(self):
        # `check_all` unions every requirements file's placeholders, so names from another board
        # arrive here too. They must match nothing, not produce a phantom could-not-run.
        findings = check_footprints.run(self.thin_ring_connector("Xt30"), placeholders=["Other"])
        self.assertEqual([f.subject for f in check_footprints.unchecked_in(findings)], [])
        self.assertTrue(check_footprints.problems_in(findings))

    def test_a_real_component_beside_a_placeholder_is_still_measured(self):
        circuit = self.thin_ring_connector("Xt30") + self.thin_ring_connector("Speaker")
        findings = check_footprints.run(circuit, placeholders=["Xt30"])
        subjects = {f.subject for f in check_footprints.problems_in(findings)}
        self.assertIn("Speaker", subjects)
        self.assertNotIn("Xt30", subjects)


class EveryShapeTscircuitEmitsTest(unittest.TestCase):
    """
    The rules read `hole_diameter` and `outer_diameter` and nothing else, so two of the three
    shapes tscircuit actually emits went past them unread. That is not a gap in the footprint
    library — the geometry was in the netlist all along — it is a gap in the reader, and the
    difference matters because one is a week of importing and the other is a function.

    Measured on the reference board the moment these landed: two connectors whose pill holes
    leave 0.225 mm of annular ring, under the 0.25 mm a cheap process guarantees. Both had been
    sitting in the "could not examine" bucket, on a board declared ready to fabricate.
    """

    @staticmethod
    def pill(hole_w, hole_h, pad_w, pad_h, count=4, **extra):
        return [dict({"type": "pcb_plated_hole", "shape": "pill", "pcb_component_id": "pcb_J1",
                      "hole_width": hole_w, "hole_height": hole_h,
                      "outer_width": pad_w, "outer_height": pad_h,
                      "x": index * 2.54, "y": 0.0}, **extra)
                for index in range(count)]

    @staticmethod
    def rect_pad(hole, pad_w, pad_h, count=4, **extra):
        return [dict({"type": "pcb_plated_hole", "shape": "circular_hole_with_rect_pad",
                      "pcb_component_id": "pcb_J1", "hole_diameter": hole,
                      "rect_pad_width": pad_w, "rect_pad_height": pad_h,
                      "x": index * 2.54, "y": 0.0}, **extra)
                for index in range(count)]

    # --- what a pin has to fit through ---

    def test_an_obround_hole_is_measured_across_its_narrow_way(self):
        # The wide way is free clearance; only the narrow way stops the pin.
        self.assertEqual(check_footprints.hole_span_mm(
            {"shape": "pill", "hole_width": 1.6, "hole_height": 0.8}), 0.8)

    def test_a_rectangular_pad_still_has_a_round_hole(self):
        self.assertEqual(check_footprints.hole_span_mm(
            {"shape": "circular_hole_with_rect_pad", "hole_diameter": 1.0}), 1.0)

    def test_an_element_that_states_no_size_is_still_unreadable(self):
        # The honest None. Teaching the reader more shapes must not turn "it did not say" into a
        # number — that is how a check starts approving things it never saw.
        self.assertIsNone(check_footprints.hole_span_mm({"shape": "pill"}))

    def test_an_obround_header_hole_too_narrow_for_its_pin_is_now_caught(self):
        circuit = self.pill(1.6, 0.8, 2.2, 1.4, count=6) + named("J1")
        findings = check_footprints.problems_in(check_footprints.run(circuit))
        self.assertTrue(any(f.rule == "through-hole-drill" for f in findings), findings)

    # --- how much copper is left around it ---

    def test_a_rectangular_pad_is_measured_on_its_tight_axis(self):
        # 3.0 wide and 1.4 tall around a 1.0 hole: generous across, 0.2 up and down. Averaging,
        # or taking the width, would call this fine.
        self.assertAlmostEqual(check_footprints.annular_ring_mm(
            {"hole_diameter": 1.0, "rect_pad_width": 3.0, "rect_pad_height": 1.4}), 0.2)

    def test_an_obround_pad_is_measured_on_its_tight_axis_too(self):
        self.assertAlmostEqual(check_footprints.annular_ring_mm(
            {"hole_width": 1.6, "hole_height": 0.8, "outer_width": 2.6, "outer_height": 1.2}), 0.2)

    def test_a_hole_pushed_off_centre_loses_ring_on_the_side_it_moved_toward(self):
        # The field is in the netlist and describes exactly this. Ignoring it reports the ring
        # the pad would have had if the hole were centred, which it is not.
        centred = {"hole_diameter": 1.0, "rect_pad_width": 2.0, "rect_pad_height": 2.0}
        self.assertAlmostEqual(check_footprints.annular_ring_mm(centred), 0.5)
        self.assertAlmostEqual(check_footprints.annular_ring_mm(
            dict(centred, hole_offset_x=0.3)), 0.2)

    def test_a_thin_ring_on_an_obround_pad_is_caught(self):
        circuit = self.pill(1.6, 0.75, 2.4, 1.2) + named("J1")
        findings = check_footprints.problems_in(check_footprints.run(circuit))
        self.assertTrue(any(f.rule == "annular-ring" for f in findings), findings)

    def test_a_generous_ring_on_an_obround_pad_is_not(self):
        circuit = self.pill(1.6, 1.0, 3.0, 2.4) + named("J1")
        self.assertEqual([f for f in check_footprints.problems_in(check_footprints.run(circuit))
                          if f.rule == "annular-ring"], [])

    # --- and nothing is left in the unread bucket ---

    def test_a_fully_dimensioned_obround_hole_is_no_longer_unexaminable(self):
        self.assertEqual(
            check_footprints.unchecked_in(check_footprints.run(self.pill(1.6, 1.0, 3.0, 2.4))), [])

    def test_a_rect_pad_hole_is_no_longer_unexaminable(self):
        self.assertEqual(
            check_footprints.unchecked_in(check_footprints.run(self.rect_pad(1.0, 1.8, 1.8))), [])



class TheExitCodeFollowsTheStatusTest(unittest.TestCase):
    """
    P42. `main` ended with its own three-way expression, and the suite asserted none of it: a
    mutation returning EXIT_OK for everything stayed green. The exit code is what a Makefile
    reads, so it is what a caller acts on.
    """

    def _exit(self, circuit):
        import contextlib
        import io
        import json
        import tempfile
        path = Path(tempfile.mkdtemp()) / "circuit.json"
        path.write_text(json.dumps(circuit))
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return check_footprints.main([str(path)])

    def test_a_shape_it_cannot_read_exits_could_not_run(self):
        pill = [{"type": "pcb_plated_hole", "shape": "pill", "pcb_component_id": "pcb_J1",
                 "x": index * 2.54, "y": 0.0} for index in range(4)]
        self.assertEqual(self._exit(pill), check_footprints.EXIT_COULD_NOT_RUN)

    def test_a_hole_too_small_for_its_pin_exits_problems(self):
        tight = [{"type": "pcb_plated_hole", "shape": "circle", "pcb_component_id": "pcb_J1",
                  "hole_diameter": 0.5, "outer_diameter": 1.6, "x": index * 2.54, "y": 0.0}
                 for index in range(4)]
        self.assertEqual(self._exit(tight), check_footprints.EXIT_PROBLEMS)

    def test_a_board_with_nothing_to_answer_for_exits_ok(self):
        fine = [{"type": "pcb_plated_hole", "shape": "circle", "pcb_component_id": "pcb_J1",
                 "hole_diameter": 1.0, "outer_diameter": 1.6, "x": index * 2.54, "y": 0.0}
                for index in range(4)]
        self.assertEqual(self._exit(fine), check_footprints.EXIT_OK)

if __name__ == "__main__":
    unittest.main()
