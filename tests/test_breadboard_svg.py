"""
The breadboard as a picture (P268, #302): breadboard.svg beside the sheet, drawn by spark from the same layout as the
Wokwi diagram, with spark's own pictograms (data/pictograms/).

    python3 -m unittest tests.test_breadboard_svg
"""

import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ElementTree
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import suite_temp  # noqa: E402,F401
from fakes import FakePartPictures  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import breadboard  # noqa: E402
import breadboard_drawing  # noqa: E402
import breadboard_steps  # noqa: E402
import part_pictures  # noqa: E402
from test_breadboard_layout import RECORD_BOARD, record_inputs  # noqa: E402

XIAO = ROOT / "tests" / "data" / "breadboard" / "button-light-xiao"
MOTOR = ROOT / "tests" / "data" / "breadboard" / "motor"
NS = {"svg": "http://www.w3.org/2000/svg"}


def in_store():
    return mock.patch.dict(os.environ, {"SPARK_HOME": tempfile.mkdtemp()})


def xiao_svg(pictures=None):
    with in_store():
        read = breadboard._read_build(XIAO / "requirements.json")
        layout = breadboard._plan_layout(read)
    return breadboard_drawing.SvgBreadboardDiagram(pictures=pictures).text(layout), layout


class ThePictogramsTest(unittest.TestCase):
    def test_each_has_a_view_box_and_only_plain_shapes(self):
        # The senior (P268 council): an id, a style or a url( in a file pasted twice would collide in one drawing.
        files = sorted(part_pictures.PICTOGRAMS.glob("*.svg"))
        self.assertGreaterEqual(len(files), 5)
        for path in files:
            text = path.read_text()
            with self.subTest(path.name):
                self.assertIsNotNone(ElementTree.fromstring(text).get("viewBox"))
                for forbidden in (" id=", "<defs", "<style", "<use", "url(", "<?xml"):
                    self.assertNotIn(forbidden, text)

    def test_a_type_with_no_pictogram_gets_the_labeled_box(self):
        pictures = part_pictures.PictogramPartPictures()
        self.assertEqual(pictures.picture("wokwi-servo"), pictures.picture(part_pictures.FALLBACK))


class TheSvgTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text, cls.layout = xiao_svg()
        cls.root = ElementTree.fromstring(cls.text)

    def test_it_is_svg_with_no_link_outside_and_small(self):
        self.assertEqual(self.root.tag, "{http://www.w3.org/2000/svg}svg")
        self.assertTrue(self.text.startswith('<svg xmlns="http://www.w3.org/2000/svg"'), self.text[:80])
        self.assertNotIn("ns0:", self.text)
        self.assertEqual(re.findall(r"https?://[^\"' ]+", self.text), ["http://www.w3.org/2000/svg"])
        self.assertLess(len(self.text.encode()), 30000)
        for attribute in ("width", "height", "viewBox"):
            self.assertTrue(self.root.get(attribute), attribute)

    def test_the_same_layout_gives_the_same_bytes(self):
        self.assertEqual(hashlib.sha256(self.text.encode()).hexdigest(),
                         hashlib.sha256(xiao_svg()[0].encode()).hexdigest())

    def test_the_bytes_are_the_ones_reviewed(self):
        # Seen in a render on 2026-10-16 (P268): a change to the picture is a decision, made by updating this number.
        self.assertEqual(hashlib.sha256(self.text.encode()).hexdigest(),
                         "354a314c3f8de47efd7720833e9459f64191d0526c4d53c9ab8a80ff43851031")

    def test_no_jumper_bends_on_a_hole(self):
        # The refuter (P268): a bend on a hole of another group looks like a joint that is not there.
        holes = [(hole.x, hole.y) for hole in breadboard_drawing.WokwiGeometry.load().surface.holes]
        for path in (p for p in self.root.findall("svg:path", NS) if p.get("fill") == "none"):
            numbers = [float(n) for n in re.findall(r"-?[\d.]+", path.get("d"))]
            for x, y in zip(numbers[2:-2:2], numbers[3:-2:2]):
                self.assertFalse(any(abs(x - hx) < 1 and abs(y - hy) < 1 for hx, hy in holes), (x, y))

    def test_each_part_is_named_once(self):
        names = [text.text for text in self.root.findall("svg:text", NS)]
        for part in self.layout.parts:
            self.assertEqual(names.count(part.id), 1, part.id)

    def test_each_jumper_runs_from_hole_center_to_hole_center_in_its_step_s_color(self):
        # The hole centers come from the data file here, not from the layout the renderer read.
        board = json.loads((ROOT / "data" / "wokwi-geometry.json").read_text())["breadboard"]

        def center(name):
            group, letter = name.split(".")
            return (board["first_column_x"] + board["pitch"] * (int(group[:-1]) - 1), board["letters_y"][letter])

        paths = [path for path in self.root.findall("svg:path", NS) if path.get("fill") == "none"]
        self.assertEqual(len(paths), len(self.layout.jumpers))
        for path, jumper in zip(paths, self.layout.jumpers):
            numbers = [float(n) for n in re.findall(r"-?[\d.]+", path.get("d"))]
            self.assertAlmostEqual(numbers[0], center(jumper.one.name)[0], places=3)
            self.assertAlmostEqual(numbers[1], center(jumper.one.name)[1], places=3)
            self.assertAlmostEqual(numbers[-2], center(jumper.other.name)[0], places=3)
            self.assertAlmostEqual(numbers[-1], center(jumper.other.name)[1], places=3)
            self.assertEqual(path.get("stroke"), breadboard_steps.StepColors().color(jumper.step))

    def test_a_turned_part_turns_about_its_measured_center(self):
        board = next(part for part in self.layout.parts if part.id == breadboard_steps.THE_BOARD)
        groups = [g for g in self.root.findall("svg:g", NS) if "rotate(90 34 44)" in (g.get("transform") or "")]
        self.assertEqual(len(groups), 1)
        self.assertEqual(board.rotate, 90)

    def test_another_pictures_source_changes_only_the_pictures(self):
        faked, _ = xiao_svg(FakePartPictures())
        self.assertIn("fake picture of wokwi-led", faked)
        self.assertEqual(without_pictures(faked), without_pictures(self.text))


def without_pictures(text):
    """The SVG with each part's picture and credit taken out: what no pictures source may change."""
    root = ElementTree.fromstring(text)
    for group in root.findall("svg:g", NS):
        for child in list(group):
            if child.tag.endswith("title") or (child.get("transform") or "").startswith("scale"):
                group.remove(child)
    return ElementTree.tostring(root, encoding="unicode")


def record_svg():
    with in_store():
        read = breadboard._read_build(RECORD_BOARD / "requirements.json")
    layout = breadboard_drawing.BreadboardPlanner(*record_inputs(read)).plan(read.steps)
    return breadboard_drawing.SvgBreadboardDiagram().text(layout), layout


class TheRecordBoardSvgTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text, cls.layout = record_svg()
        cls.root = ElementTree.fromstring(cls.text)
        cls.texts = [element.text for element in cls.root.iter("{http://www.w3.org/2000/svg}text")]

    def test_every_pad_label_is_written_once_beside_its_pin(self):
        board = self.layout.geometry.part(self.layout.parts[0].type)
        self.assertEqual(len(board["pins"]), 32)
        for pad in board["pins"]:
            self.assertEqual(self.texts.count(pad), 1, pad)

    def test_a_doubtful_pad_has_a_dashed_ring_and_the_others_have_none(self):
        rings = [c for c in self.root.iter("{http://www.w3.org/2000/svg}circle") if c.get("stroke-dasharray")]
        self.assertEqual(len(rings), 2)

    def test_the_usb_c_end_is_marked_once(self):
        self.assertEqual(self.texts.count("USB-C"), 1)

    def test_the_note_names_the_doubtful_pads_and_the_row_side_once(self):
        notes = [text for text in self.texts if text and "GND1" in text and "GND3" in text]
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0].count(","), 1)

    def test_the_surface_has_63_columns_and_no_rail_lines(self):
        holes = re.findall(r"M[\d.]+ [\d.]+h0", [p.get("d") for p in self.root.findall("svg:path", NS)][0])
        self.assertEqual(len(holes), 630)
        self.assertEqual(len(self.root.findall("svg:line", NS)), 0)

    def test_the_same_layout_gives_the_same_bytes(self):
        self.assertEqual(self.text, breadboard_drawing.SvgBreadboardDiagram().text(self.layout))

    def test_the_xiao_has_none_of_it(self):
        text, _ = xiao_svg()
        self.assertNotIn("USB-C", text)
        self.assertNotIn("stroke-dasharray", text)


class TheSheetShowsItTest(unittest.TestCase):
    def test_the_sheet_s_picture_is_the_file_written_beside_it(self):
        project = Path(tempfile.mkdtemp()) / "xiao"
        shutil.copytree(XIAO, project)
        with in_store():
            breadboard.write(project / "requirements.json", project / "breadboard.md")
        link = re.search(r"!\[[^\]]*\]\(([^)]+)\)", (project / "breadboard.md").read_text()).group(1)
        self.assertTrue((project / link).is_file())

    def test_a_sheet_with_no_drawing_shows_no_picture(self):
        project = Path(tempfile.mkdtemp()) / "motor"
        shutil.copytree(MOTOR, project)
        (project / "breadboard.svg").write_text("<svg/>")
        with in_store():
            breadboard.write(project / "requirements.json", project / "breadboard.md")
        self.assertNotIn("![", (project / "breadboard.md").read_text())
        self.assertIn("breadboard.json and breadboard.svg not written: ", (project / "breadboard.md").read_text())
        self.assertFalse((project / "breadboard.svg").exists())


if __name__ == "__main__":
    unittest.main()
