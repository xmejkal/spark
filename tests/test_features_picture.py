"""
Proof that spark draws a part from its measured features in their colours, as plain shapes that pass the picture rules,
the same bytes for the same record, and that the features maker declines a record it cannot draw (P956 #1362).

    python3 -m unittest tests.test_features_picture

`SPARK_ACCEPT=features python3 -m unittest tests.test_features_picture` writes the golden from today's drawing and fails,
so that a person reads `git diff tests/data/pictures/features-synthetic.svg`.
"""

import json
import os
import shutil
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ElementTree
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import suite_temp  # noqa: E402,F401
import features_fixture  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from spark.breadboard import features_picture, picture_makers  # noqa: E402
from spark.breadboard.feature_measure import FileFeatureMeasurer  # noqa: E402
from spark.breadboard.picture_check import PictureCheck  # noqa: E402
from spark.records import record_kind  # noqa: E402

SVG = "{http://www.w3.org/2000/svg}"


def measured_board():
    """The synthetic board with the synthetic file's features and colour in its record, as `--features-set` writes them."""
    record = features_fixture.board()
    shape = picture_makers.shape_of(record)
    measured = FileFeatureMeasurer(features_fixture.FEATURES_FILE).measure(record, shape)
    record["physical"].update(features=measured.features, colour=measured.colour)
    return record


def make(record):
    return picture_makers.FeaturesPictureMaker().make(
        picture_makers.PictureRequest(record, "breadboard-top", picture_makers.shape_of(record)))


class TheDrawingTest(unittest.TestCase):
    def setUp(self):
        self.record = measured_board()
        self.shape = picture_makers.shape_of(self.record)
        self.svg = features_picture.FeaturesDrawing().svg(self.record, self.shape)

    def test_draws_the_golden_bytes(self):
        if os.environ.get("SPARK_ACCEPT") == "features":
            features_fixture.GOLDEN_SVG.write_text(self.svg)
            self.fail("wrote the golden: read git diff tests/data/pictures/features-synthetic.svg")
        self.assertEqual(self.svg, features_fixture.GOLDEN_SVG.read_text())

    def test_same_bytes_twice(self):
        self.assertEqual(features_picture.FeaturesDrawing().svg(measured_board(), self.shape), self.svg)

    def test_passes_picture_check(self):
        self.assertEqual(PictureCheck(self.shape).problems(self.svg.encode("utf-8")), [])
        self.assertNotIn("<image", self.svg)
        self.assertNotIn("http", self.svg.replace('xmlns="http://www.w3.org/2000/svg"', ""))

    def test_each_kind_has_a_shape(self):
        self.assertEqual(sorted(features_picture.SHAPES), sorted(record_kind.FEATURE_KINDS))

    def test_board_colour_fills_the_outline(self):
        outline = ElementTree.fromstring(self.svg)[0]
        self.assertEqual((outline.tag, outline.get("width"), outline.get("height"), outline.get("fill")),
                         (SVG + "rect", "20", "40", "#0a3d1f"))
        self.record["physical"].pop("colour")
        undrawn = features_picture.FeaturesDrawing().svg(self.record, self.shape)
        self.assertEqual(ElementTree.fromstring(undrawn)[0].get("fill"), "#16202a")

    def test_null_corner_radius_draws_square_corners(self):
        self.assertIsNone(ElementTree.fromstring(self.svg)[0].get("rx"))
        self.record["physical"]["corner_radius_mm"] = 1.5
        rounded = features_picture.FeaturesDrawing().svg(self.record, self.shape)
        self.assertEqual(ElementTree.fromstring(rounded)[0].get("rx"), "1.5")

    def test_sideways_label_when_taller_than_wide(self):
        texts = {text.text: text for text in ElementTree.fromstring(self.svg).iter(SVG + "text")}
        self.assertIsNone(texts["SPARK"].get("transform"))
        self.assertEqual(texts["IO9"].get("transform"), "rotate(-90 12.5 17)")
        self.assertEqual(texts["IO9"].get("font-size"), "0.8")

    def test_labels_come_last_and_pads_are_gold_discs_under_them(self):
        root = ElementTree.fromstring(self.svg)
        tags = [element.tag for element in root]
        self.assertEqual(tags[-2:], [SVG + "text", SVG + "text"])
        pads = [element for element in root if element.tag == SVG + "circle" and element.get("fill") == "#e1b737"]
        self.assertEqual(len(pads), 12)
        self.assertEqual({pad.get("r") for pad in pads}, {"0.75"})

    def test_no_pad_disc_when_the_record_states_no_pad_size(self):
        self.record["physical"]["header"]["pad_mm"] = None
        drawn = ElementTree.fromstring(features_picture.FeaturesDrawing().svg(self.record, self.shape))
        self.assertEqual([element for element in drawn if element.tag == SVG + "circle" and element.get("fill") == "#e1b737"], [])

    def test_a_chip_s_leads_follow_its_sides(self):
        drawing = features_picture.ChipShape()
        chip = {"x": 0, "y": 0, "w": 2.0, "h": 1.0, "colour": "#838383"}
        self.assertEqual(len(drawing.draw(dict(chip, leads="none"))), 1)
        self.assertEqual(len(drawing.draw(dict(chip, leads="top-bottom"))), 1 + 2 * 3)
        self.assertEqual(len(drawing.draw(dict(chip, leads="left-right"))), 1 + 2 * 1)
        self.assertEqual(len(drawing.draw(chip)), 1 + 2 * 3 + 2 * 1)


class TheMakerTest(unittest.TestCase):
    def test_draws_a_candidate_with_its_credit(self):
        made = make(measured_board())
        self.assertIsInstance(made, picture_makers.PictureCandidate)
        self.assertEqual((made.view_box, made.made_by, made.likeness, made.credit),
                         ((0.0, 0.0, 20.0, 40.0), "features", "near", "spark's drawing of 14 measured features of synthetic-board"))

    def test_no_features_declines_with_the_command(self):
        made = make(features_fixture.board())
        self.assertIsInstance(made, picture_makers.Decline)
        self.assertEqual(made.missing, ("physical.features: parts.py --features-set FILE --part synthetic-board --project .",))

    def test_refused_feature_declines_by_name(self):
        record = measured_board()
        record["physical"]["features"][2].update(x=0.5, y=4.5)  # MCU over the pad A1
        made = make(record)
        self.assertIsInstance(made, picture_makers.Decline)
        self.assertTrue(made.reason.startswith("MCU breaks feature_over_pad"), made.reason)
        record["physical"]["features"][2]["kind"] = "robot"
        self.assertIn("physical.features[2] (MCU) is of kind 'robot'", make(record).reason)

    def test_skips_no_picture_rule_of_its_own(self):
        record = measured_board()
        record["physical"]["features"][-1]["text"] = "<b>"  # escaped, still a plain text
        self.assertIsInstance(make(record), picture_makers.PictureCandidate)
        broken = picture_makers.FeaturesPictureMaker(drawing=_BrokenDrawing())
        made = broken.make(picture_makers.PictureRequest(record, "breadboard-top", picture_makers.shape_of(record)))
        self.assertIsInstance(made, picture_makers.Decline)
        self.assertIn("picture_element", made.reason)

    def test_uses_says_it_reads_the_features_and_costs_nothing(self):
        self.assertEqual(picture_makers.FeaturesPictureMaker().uses(), picture_makers.MakerUses((), ("physical", "features"), None, False))


class _BrokenDrawing(features_picture.FeaturesDrawing):
    """A drawing that breaks a picture rule: a script element."""

    def svg(self, record, shape):
        return super().svg(record, shape).replace("</svg>", "<script>1</script></svg>")


class TheBuildTest(unittest.TestCase):
    """The build draws the board from its features, and says why when it cannot."""

    def setUp(self):
        self.home = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.home, True)

    def picture(self, record):
        pictures = picture_makers.MadePartPictures(picture_makers.PictureMakerChain(
            picture_makers.MAKERS[name]() for name in picture_makers.BUILD_MAKERS), _Pictogram())
        return pictures.picture("board-x", record)

    def test_a_board_with_features_is_drawn_from_them(self):
        picture = self.picture(measured_board())
        self.assertEqual(picture.credit, "spark's drawing of 14 measured features of synthetic-board")
        self.assertEqual(picture.note, "")

    def test_features_note_when_refused(self):
        record = measured_board()
        record["physical"]["features"][2].update(x=0.5, y=4.5)
        picture = self.picture(record)
        self.assertEqual(picture.markup, "pictogram")
        self.assertTrue(picture.note.startswith("synthetic-board: measured features not shown (MCU breaks feature_over_pad"), picture.note)

    def test_no_features_no_note(self):
        self.assertEqual(self.picture(features_fixture.board()).note, "")


class _Pictogram:
    def picture(self, wokwi_type, record=None):
        from spark.breadboard.part_pictures import Picture
        return Picture("pictogram", (0, 0, 1, 1), "")


if __name__ == "__main__":
    unittest.main()
