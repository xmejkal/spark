"""
Proof that a features file read off a maker's top view is scaled by its outline and turned into the part's frame, never
mirrored, with a source on every feature (P956 #1362).

    python3 -m unittest tests.test_feature_measure
"""

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import suite_temp  # noqa: E402,F401
import features_fixture  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from spark.breadboard import picture_makers  # noqa: E402
from spark.breadboard.feature_measure import FileFeatureMeasurer, MeasuredFeatures  # noqa: E402


class MeasureTest(unittest.TestCase):
    def setUp(self):
        self.folder = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.folder, True)
        self.record = features_fixture.board()
        self.shape = picture_makers.shape_of(self.record)

    def measure(self, held=None, record=None):
        path = self.folder / "features.json"
        path.write_text(json.dumps(held if held is not None else features_fixture.features_file()))
        return FileFeatureMeasurer(path).measure(record or self.record, self.shape)

    def one(self, feature, usb_edge="top", outline=(10, 10, 210, 410)):
        """The one feature of a file that holds only `feature`, measured with the edge and the outline given."""
        held = features_fixture.features_file()
        held["picture"].update(usb_edge=usb_edge, outline_px=list(outline))
        held["features"] = [dict({"name": "F", "kind": "connector", "colour": "#202020"}, **feature)]
        measured = self.measure(held)
        self.assertIsInstance(measured, MeasuredFeatures, measured)
        return measured.features[0]

    def box(self, feature):
        return tuple(feature[key] for key in ("x", "y", "w", "h"))

    def test_scales_each_axis_by_the_outline(self):
        # an outline of 100 x 800 px for a 20 x 40 mm frame: 5 px to the mm across, 20 along
        self.assertEqual(self.box(self.one({"x_px": 0, "y_px": 0, "w_px": 10, "h_px": 40}, "bottom", (0, 0, 100, 800))),
                         (0.0, 0.0, 2.0, 2.0))

    def test_turns_usb_at_top_by_180_degrees(self):
        # the picture's top-left corner is the frame's bottom-right; the size is kept
        self.assertEqual(self.box(self.one({"x_px": 10, "y_px": 10, "w_px": 30, "h_px": 50})), (17.0, 35.0, 3.0, 5.0))

    def test_turns_a_header_edge_by_90_degrees(self):
        # USB end on the picture's left: the picture is 400 px wide along the frame's 40 mm, 200 px tall across its 20 mm
        left = self.one({"x_px": 0, "y_px": 0, "w_px": 40, "h_px": 20}, "left", (0, 0, 400, 200))
        self.assertEqual(self.box(left), (0.0, 36.0, 2.0, 4.0))
        right = self.one({"x_px": 0, "y_px": 0, "w_px": 40, "h_px": 20}, "right", (0, 0, 400, 200))
        self.assertEqual(self.box(right), (18.0, 0.0, 2.0, 4.0))

    def test_a_quarter_turn_swaps_a_chip_s_lead_sides(self):
        chip = {"kind": "chip", "leads": "top-bottom", "x_px": 100, "y_px": 50, "w_px": 40, "h_px": 20}
        self.assertEqual(self.one(chip, "left", (0, 0, 400, 200))["leads"], "left-right")
        self.assertEqual(self.one(chip)["leads"], "top-bottom")

    def test_never_mirrors(self):
        # a feature on the picture's left lands on the frame's right after the 180-degree turn, never on its left
        feature = self.one({"x_px": 10, "y_px": 200, "w_px": 20, "h_px": 20})
        self.assertGreater(feature["x"], 10)
        self.assertEqual(self.box(feature), (18.0, 19.0, 2.0, 2.0))

    def test_every_synthetic_feature_lands_where_it_was_made(self):
        measured = self.measure()
        boxes = {feature["name"]: self.box(feature) for feature in measured.features}
        self.assertEqual(boxes["MCU"], (8.0, 25.0, 4.0, 4.0))
        self.assertEqual(boxes["USB"], (8.0, 38.5, 4.0, 3.0))
        self.assertEqual(measured.anchors, (("A1", 1.11, 5.0), ("B6", 18.89, 17.7)))
        self.assertEqual(measured.colour["value"], "#0a3d1f")
        self.assertIs(measured.colour["verified"], False)

    def test_source_names_document_and_px_box(self):
        mcu = next(feature for feature in self.measure().features if feature["name"] == "MCU")
        self.assertEqual(mcu["source"], "measured by the suite on documents.synthetic-top-view (top.png, sha256 000000000000), "
                                        "box 90,120,40,40 px of the outline 10,10,210,410 px")
        self.assertEqual(mcu["leads"], "four")

    def test_verified_is_false(self):
        self.assertEqual({feature["verified"] for feature in self.measure().features}, {False})

    def test_unknown_document_declines(self):
        held = features_fixture.features_file()
        held["picture"]["document"] = "not-kept"
        declined = self.measure(held)
        self.assertIsInstance(declined, picture_makers.Decline)
        self.assertIn("'not-kept'", declined.reason)

    def test_a_broken_file_declines_and_never_raises(self):
        for name, change in (("no anchors", lambda held: held.pop("anchors")),
                             ("an edge that is no edge", lambda held: held["picture"].update(usb_edge="front")),
                             ("an outline of nothing", lambda held: held["picture"].update(outline_px=[10, 10, 10, 410])),
                             ("a box of no width", lambda held: held["features"][0].update(w_px=0)),
                             ("a number that is text", lambda held: held["features"][0].update(x_px="left"))):
            with self.subTest(name):
                held = features_fixture.features_file()
                change(held)
                self.assertIsInstance(self.measure(held), picture_makers.Decline)
        (self.folder / "broken.json").write_text("{")
        self.assertIsInstance(FileFeatureMeasurer(self.folder / "broken.json").measure(self.record, self.shape), picture_makers.Decline)


if __name__ == "__main__":
    unittest.main()
