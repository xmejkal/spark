"""
Proof that measured features are refused by name when they lie outside the outline, cover a pad, sit off the record's
dimension drawing or name a pad's label, and that the anchors catch a mirrored or wrongly scaled picture (P956 #1362).

    python3 -m unittest tests.test_feature_check
"""

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import suite_temp  # noqa: E402,F401
import features_fixture  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from spark.breadboard import picture_makers  # noqa: E402
from spark.breadboard.feature_check import FeatureCheck  # noqa: E402
from spark.breadboard.feature_measure import MeasuredFeatures  # noqa: E402

#: The C6's geometry and pad order before the walk swapped its rows (row_18 first), and the four anchors measured on
#: DFRobot's top view in the frame's mm (the walk's measurement, 2026-11-20): numbers only, no vendor's bytes.
C6_BEFORE_THE_SWAP = ROOT / "tests" / "data" / "pictures" / "c6-rows-before-the-swap.json"
GOOD_ANCHORS = (("A1", 1.11, 5.0), ("B6", 18.89, 17.7))


def feature(name="F", kind="connector", x=8.0, y=20.0, w=2.0, h=2.0, **more):
    return dict({"name": name, "kind": kind, "x": x, "y": y, "w": w, "h": h, "colour": "#202020", "verified": False,
                 "source": "the suite"}, **more)


class FeatureCheckTest(unittest.TestCase):
    def setUp(self):
        self.record = features_fixture.board()
        self.check = FeatureCheck(picture_makers.shape_of(self.record), self.record)

    def problems(self, features=(), anchors=GOOD_ANCHORS):
        return [(problem.code, problem.feature) for problem in self.check.problems(MeasuredFeatures(list(features), anchors, None, ""))]

    def test_good_features_and_anchors_pass(self):
        self.assertEqual(self.problems([feature()]), [])

    def test_outside_outline_is_refused_by_name(self):
        self.assertEqual(self.problems([feature("Far", x=19.0, w=2.0)]), [("feature_outside", "Far")])  # 1 mm past the right edge
        self.assertEqual(self.problems([feature("Low", y=39.0, h=1.6)]), [("feature_outside", "Low")])

    def test_up_to_half_a_mm_past_an_edge_is_pulled_back_inside(self):
        self.assertEqual(self.problems([feature("Flush", x=-0.5)]), [])
        self.assertEqual(self.problems([feature("Past", x=-0.75)]), [("feature_outside", "Past")])
        self.assertEqual(self.check.fitted(feature(x=-0.5))["x"], 0)
        self.assertEqual(self.check.fitted(feature(x=18.5, w=2.0))["x"], 18.0)

    def test_a_usb_socket_may_hang_2_mm_past_the_usb_edge_and_keeps_its_overhang(self):
        self.assertEqual(self.problems([feature("USB", "usb", y=39.0, h=3.0)]), [])
        self.assertEqual(self.problems([feature("USB", "usb", y=39.0, h=3.5)]), [("feature_outside", "USB")])
        self.assertEqual(self.check.fitted(feature("USB", "usb", y=39.0, h=3.0))["y"], 39.0)
        self.assertEqual(self.problems([feature("Not USB", y=39.0, h=1.5)]), [])
        self.assertEqual(self.problems([feature("Not USB", y=39.0, h=2.0)]), [("feature_outside", "Not USB")])
        self.assertEqual(self.problems([feature("USB", "usb", y=-1.0)]), [("feature_outside", "USB")])  # only past the USB edge

    def test_over_a_pad_is_refused_by_name(self):
        # A1 is at (1.11, 5.0) and its pad is 1.5 mm across: a box 0.7 mm right of its centre covers it, 0.8 mm does not
        self.assertEqual(self.problems([feature("Near", x=1.81, y=4.0)]), [("feature_over_pad", "Near")])
        self.assertEqual(self.problems([feature("Clear", x=1.91, y=4.0)]), [])

    def test_a_hole_over_a_pad_is_refused_too(self):
        self.assertEqual(self.problems([feature("H", "hole", x=0.3, y=4.2, w=1.6, h=1.6)]),
                         [("feature_over_pad", "H"), ("feature_off_drawing", "H")])

    def test_anchor_beyond_tolerance_is_refused_by_name(self):
        self.assertEqual(self.problems(anchors=(("A1", 1.11, 5.75), GOOD_ANCHORS[1])), [("feature_off_drawing", "A1")])

    def test_feature_within_tolerance_passes(self):
        # exactly 0.5 mm passes, 0.51 mm is refused
        self.assertEqual(self.problems(anchors=(("A1", 1.11, 5.5), GOOD_ANCHORS[1])), [])
        self.assertEqual(self.problems(anchors=(("A1", 1.11, 5.51), GOOD_ANCHORS[1])), [("feature_off_drawing", "A1")])

    def test_mirrored_rows_fail_the_anchor(self):
        check = FeatureCheck(picture_makers.shape_of(features_fixture.mirrored_board()), self.record)
        refused = check.problems(MeasuredFeatures([], GOOD_ANCHORS, None, ""))
        self.assertEqual([(problem.code, problem.feature) for problem in refused],
                         [("feature_off_drawing", "A1"), ("feature_off_drawing", "B6")])
        self.assertIn("17.78 mm", refused[0].sentence)

    def test_the_c6_s_real_anchors_fail_on_the_old_row_order_and_pass_once_swapped(self):
        held = json.loads(C6_BEFORE_THE_SWAP.read_text())
        anchors = tuple(tuple(anchor) for anchor in held["anchors_mm"])
        before = held["board"]
        refused = FeatureCheck(picture_makers.shape_of(before), before).anchor_problems(anchors)
        self.assertEqual([(problem.code, problem.feature) for problem in refused],
                         [("feature_off_drawing", pad) for pad in ("RST", "RX", "VIN", "NC4")])
        self.assertIn("22.9", refused[0].sentence)
        swapped = json.loads(json.dumps(before))
        order = swapped["physical"]["header_order"]
        swapped["physical"]["header_order"] = {"row_14": order["row_14"], "row_18": order["row_18"]}
        swapped["physical"]["header"]["pins"] = [14, 18]
        self.assertEqual(FeatureCheck(picture_makers.shape_of(swapped), swapped).anchor_problems(anchors), [])

    def test_hole_off_the_mounting_holes_is_refused(self):
        # the record's holes are 16 x 36 mm apart about the centre: (2, 2) is one, (3, 2) is 1 mm off it
        self.assertEqual(self.problems([feature("H1", "hole", x=1.2, y=1.2, w=1.6, h=1.6)]), [])
        self.assertEqual(self.problems([feature("H2", "hole", x=2.2, y=1.2, w=1.6, h=1.6)]), [("feature_off_drawing", "H2")])

    def test_a_hole_that_is_no_circle_is_refused_even_with_no_mounting_holes(self):
        # the review of PR #1368: a 3.0 x 0.2 mm hole box beside A1 drew a disc of 1.5 mm across the pad
        record = features_fixture.board()
        del record["physical"]["mounting_holes"]
        check = FeatureCheck(picture_makers.shape_of(record), record)
        flat = feature("Flat", "hole", x=0.9, y=3.0, w=3.0, h=0.2)
        self.assertEqual([(problem.code, problem.feature) for problem in check.drawn_problems([flat])],
                         [("feature_off_drawing", "Flat")])
        self.assertEqual(check.drawn_problems([feature("Round", "hole", x=8.0, y=20.0, w=1.6, h=2.1)]), [])  # 0.5 mm apart

    def test_a_hole_off_the_record_s_diameter_is_refused(self):
        # the record's holes are 1.6 mm across: 2.1 passes (0.5 mm off), 2.2 is refused
        self.assertEqual(self.problems([feature("H1", "hole", x=0.95, y=0.95, w=2.1, h=2.1)]), [])
        self.assertEqual(self.problems([feature("H1", "hole", x=0.9, y=0.9, w=2.2, h=2.2)]), [("feature_off_drawing", "H1")])

    def test_fewer_than_two_anchors_is_refused(self):
        self.assertEqual(self.problems(anchors=GOOD_ANCHORS[:1]), [("feature_no_anchor", None)])
        self.assertEqual(self.problems(anchors=(("A1", 1.11, 5.0), ("A2", 1.11, 7.54))), [("feature_no_anchor", None)])
        self.assertEqual(self.problems(anchors=(("Z9", 1.0, 1.0),) + GOOD_ANCHORS), [("feature_no_anchor", "Z9")])

    def test_label_that_is_a_pad_label_is_refused(self):
        self.assertEqual(self.problems([feature("Word", "label", text="B6")]), [("feature_pad_label", "Word")])
        self.assertEqual(self.problems([feature("Word", "label", text="BOOT")]), [])

    def test_label_with_http_is_refused(self):
        self.assertEqual(self.problems([feature("Link", "label", text="HTTP://x")]), [("feature_pad_label", "Link")])
        self.assertEqual(self.problems([feature("Site", "label", text="WWW.dfrobot.com")]), [("feature_pad_label", "Site")])


if __name__ == "__main__":
    unittest.main()
