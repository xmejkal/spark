"""
The breadboard as a picture (P268, #302): breadboard.svg beside the sheet, drawn by spark from the same layout as the
Wokwi diagram, with spark's own pictograms (data/pictograms/).

    python3 -m unittest tests.test_breadboard_svg
"""

import hashlib
import json
import math
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

from spark.breadboard import board_marks as board_marks_module, breadboard_scene, drawing, part_captions, part_pictures, sheet, svg_diagram, wire_pills, wire_routing, wiring_steps  # noqa: E402
from test_breadboard_layout import EPAPER, RECORD_BOARD, epaper_inputs, record_inputs  # noqa: E402

XIAO = ROOT / "tests" / "data" / "breadboard" / "button-light-xiao"
MOTOR = ROOT / "tests" / "data" / "breadboard" / "motor"
NS = {"svg": "http://www.w3.org/2000/svg"}


def in_store():
    return mock.patch.dict(os.environ, {"SPARK_HOME": tempfile.mkdtemp()})


def xiao_svg(pictures=None):
    with in_store():
        read = sheet._read_build(XIAO / "requirements.json")
        layout = sheet._plan_layout(read)
    return svg_diagram.SvgBreadboardDiagram(pictures=pictures).text(layout), layout


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

    def test_a_record_s_own_picture_comes_before_its_type_s_and_another_id_of_the_type_gets_the_box(self):
        # P946: the FireBeetle's Wokwi type is the DevKitC stand-in, so a picture by type would show on every DevKitC too
        pictures = part_pictures.PictogramPartPictures()
        beetle = pictures.picture("board-esp32-s3-devkitc-1", {"id": "firebeetle2-esp32s3"})
        self.assertIn('fill="#16202a"', beetle.markup)
        self.assertEqual(beetle.view_box, (0.0, 0.0, 25.4, 60.0))
        self.assertEqual(pictures.picture("board-esp32-s3-devkitc-1", {"id": "another-board"}),
                         pictures.picture(part_pictures.FALLBACK))
        self.assertEqual(pictures.picture("board-esp32-s3-devkitc-1"), pictures.picture(part_pictures.FALLBACK))

    def test_a_part_with_no_record_picture_keeps_its_type_pictogram(self):
        pictures = part_pictures.PictogramPartPictures()
        led = part_pictures.read_picture((part_pictures.PICTOGRAMS / "wokwi-led.svg").read_text())
        self.assertEqual(pictures.picture("wokwi-led"), led)
        self.assertEqual(pictures.picture("wokwi-led", {"id": "led-with-no-picture"}), led)
        self.assertEqual(pictures.picture("wokwi-led", {"no": "id"}), led)
        self.assertEqual(pictures.picture("wokwi-led", {"id": "../pictograms/module"}), led)  # an id is a plain name only

    def test_a_picture_s_first_title_is_its_credit_and_stays_out_of_its_markup(self):
        picture = part_pictures.read_picture('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2 1"><title>by someone'
                                             '</title><rect width="2" height="1"/></svg>')
        self.assertEqual((picture.credit, "title" in picture.markup, picture.note), ("by someone", False, ""))
        self.assertEqual(part_pictures.read_picture((part_pictures.PICTOGRAMS / "module.svg").read_text()).credit, "")


class TheFireBeetlePictureTest(unittest.TestCase):
    """P946: the FireBeetle drawn from the PO's old wiring page's group (MIT), turned a quarter into spark's frame."""

    PATH = part_pictures.PICTOGRAMS / "firebeetle2-esp32s3.svg"

    def test_it_is_turned_a_quarter_clockwise_never_mirrored(self):
        root = ElementTree.fromstring(self.PATH.read_text())
        group = root.find("svg:g", NS)
        a, b, c, d, e, f = [float(n) for n in re.findall(r"-?[\d.]+", group.get("transform"))]
        self.assertGreater(a * d - b * c, 0)
        self.assertEqual((a, d), (0.0, 0.0))
        self.assertGreater(b, 0)  # the old page's length (x) runs down spark's frame, toward the USB end

        def place(x, y):
            return (a * x + c * y + e, b * x + d * y + f)

        usb = next(rect for rect in group.findall("svg:rect", NS) if rect.get("fill") == "#b9c0c5")
        corners = [place(float(usb.get("x")) + dx, float(usb.get("y")) + dy)
                   for dx in (0, float(usb.get("width"))) for dy in (0, float(usb.get("height")))]
        self.assertGreater(min(y for _, y in corners), 50)
        outline = next(rect for rect in group.findall("svg:rect", NS) if rect.get("fill") == "#16202a")
        top_left = place(float(outline.get("x")), float(outline.get("y")) + float(outline.get("height")))
        self.assertAlmostEqual(top_left[0], 0, places=1)
        self.assertAlmostEqual(top_left[1], 0, places=1)

    def test_it_fits_its_frame_holds_no_pad_label_and_credits_the_po_s_page(self):
        from spark.breadboard import part_shape
        from spark.breadboard.picture_check import PictureCheck
        board = json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())
        self.assertEqual(PictureCheck(part_shape.RecordShapeSource().find_shape(board)).problems(self.PATH.read_bytes()), [])
        self.assertEqual(part_pictures.read_picture(self.PATH.read_text()).credit,
                         "FireBeetle 2 ESP32-S3: drawing from the PO's pixel-games wiring page (pixel-master/docs/wiring.html), MIT")

    def test_the_battery_socket_is_on_the_rx_edge_as_the_po_s_board_has_it(self):
        # The PO's bench look (2026-11-20): USB-C at the near edge, RX on the left edge, BAT on the same edge as RX
        root = ElementTree.fromstring(self.PATH.read_text())
        group = root.find("svg:g", NS)
        a, b, c, d, e, f = [float(n) for n in re.findall(r"-?[\d.]+", group.get("transform"))]
        bat = next(text for text in group.findall("svg:text", NS) if text.text == "BAT")
        x = a * float(bat.get("x")) + c * float(bat.get("y")) + e
        self.assertLess(x, 25.4 / 2)


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
        # P949: the keys data-step and data-part, and the dot of each pin used or free, seen in a render on 2026-11-20.
        self.assertEqual(hashlib.sha256(self.text.encode()).hexdigest(),
                         "64800cebc45098b861a511c5b436b764c33310e76e1ad7cd5f22c110a0c61e0e")  # P953: the wires around the parts; ground through the - rail; PR 4a: a pill on each wire and the palette's hex, pill 7 clear of the rail signs; PR 4b: a caption per part outside its body, at its left edge (the review of PR #1379), seen in a render on 2026-11-20

    def test_no_jumper_bends_on_a_hole(self):
        # The refuter (P268): a bend on a hole of another group looks like a joint that is not there.
        holes = [(hole.x, hole.y) for hole in drawing.WokwiGeometry.load().surface.holes]
        paths = [path for under, color, _ in wires(self.root) for path in (under, color)]
        self.assertEqual(len(paths), 2 * len(self.layout.jumpers))
        for path in paths:
            numbers = [float(n) for n in re.findall(r"-?[\d.]+", path.get("d"))]
            for x, y in zip(numbers[2:-2:2], numbers[3:-2:2]):
                self.assertFalse(any(abs(x - hx) < 1 and abs(y - hy) < 1 for hx, hy in holes), (x, y))

    def test_each_jumper_runs_from_hole_center_to_hole_center_in_its_step_s_color(self):
        # The hole centers come from the data file here, not from the layout the renderer read.
        board = json.loads((ROOT / "data" / "wokwi-geometry.json").read_text())["breadboard"]

        def center(name):
            group, letter = name.split(".")
            if group in board["rails_y"]:  # P953: a rail hole, tp.3, counted along its rail in blocks
                number = int(letter) - 1
                return (board["first_rail_x"] + board["pitch"] * (number + number // board["rail_block"]),
                        board["rails_y"][group])
            return (board["first_column_x"] + board["pitch"] * (int(group[:-1]) - 1), board["letters_y"][letter])

        # each jumper has two paths on one route, the white under-stroke and its color (P947); the color one is read
        paths = [color for _, color, _ in wires(self.root)]
        self.assertEqual(len(paths), len(self.layout.jumpers))
        for path, jumper in zip(paths, self.layout.jumpers):
            numbers = [float(n) for n in re.findall(r"-?[\d.]+", path.get("d"))]
            self.assertAlmostEqual(numbers[0], center(jumper.one.name)[0], places=3)
            self.assertAlmostEqual(numbers[1], center(jumper.one.name)[1], places=3)
            self.assertAlmostEqual(numbers[-2], center(jumper.other.name)[0], places=3)
            self.assertAlmostEqual(numbers[-1], center(jumper.other.name)[1], places=3)
            self.assertEqual(path.get("stroke"), WIRE_HEX[wiring_steps.JumperColors().of(
                {one.step: one.role for one in self.layout.jumpers})[jumper.step]])  # P953: the word's hex

    def test_a_turned_part_turns_about_its_measured_center(self):
        board = next(part for part in self.layout.parts if part.id == wiring_steps.THE_BOARD)
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
        read = sheet._read_build(RECORD_BOARD / "requirements.json")
    layout = drawing.BreadboardPlanner(*record_inputs(read)).plan(read.steps)
    return svg_diagram.SvgBreadboardDiagram().text(layout), layout


class TheRecordBoardSvgTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text, cls.layout = record_svg()
        cls.root = ElementTree.fromstring(cls.text)
        cls.texts = [element.text for element in cls.root.iter("{http://www.w3.org/2000/svg}text")]

    def test_every_pad_label_is_written_once_beside_its_pin(self):
        # P953 PR 4b: in the steps' words, so the S3's GND1, GND2 and GND3 are three labels GND
        board = self.layout.geometry.part(self.layout.parts[0].type)
        self.assertEqual(len(board["pins"]), 32)
        labels = [text.text for text, _ in pad_labels(self.root)]
        self.assertEqual(len(labels), 32)
        for pad in board["pins"]:
            word = "GND" if pad in ("GND1", "GND2", "GND3") else pad
            self.assertEqual(labels.count(word), 3 if word == "GND" else 1, pad)

    def test_a_doubtful_pad_has_a_dashed_ring_and_the_others_have_none(self):
        rings = [c for c in self.root.iter("{http://www.w3.org/2000/svg}circle") if c.get("stroke-dasharray")]
        self.assertEqual(len(rings), 2)

    def test_the_usb_end_is_marked_with_no_word_of_its_own(self):
        marks = [rect for rect in self.root.iter("{http://www.w3.org/2000/svg}rect") if rect.get("fill") == "#cfd8dc"]
        self.assertEqual(len(marks), 1)
        self.assertNotIn("USB-C", self.texts)

    def test_the_note_is_the_unverified_groups_of_the_board_once_and_the_board_keeps_its_ground_and_doubts(self):
        board = self.layout.geometry.part(self.layout.parts[0].type)
        self.assertEqual((board["ground"], board["doubtful"]), ("GND2", ["GND1", "GND3"]))
        # P953 PR 4b: one line for the board, its groups by their words after its caption's name
        self.assertEqual(self.texts.count("DFRobot FireBeetle 2 ESP32-S3: pads, USB end and the pads in a dashed ring not "
                                          "verified."), 1)

    def test_the_surface_has_63_columns_and_four_rails_of_50_holes(self):
        # P953: the full board got rails, a drawing convention as on the old page
        terminal, rails = [p.get("d") for p in self.root.findall("svg:path", NS)][:2]
        self.assertEqual(len(re.findall(r"M[\d.]+ [\d.]+h0", terminal)), 630)
        self.assertEqual(len(re.findall(r"M[\d.]+ [\d.]+h0", rails)), 200)
        self.assertEqual(len(self.root.findall("svg:line", NS)), 4)

    def test_the_same_layout_gives_the_same_bytes(self):
        self.assertEqual(self.text, svg_diagram.SvgBreadboardDiagram().text(self.layout))

    def test_the_picture_is_the_one_looked_at_on_2026_11_20(self):
        # rendered and looked at once (pad labels, rings, USB end, note); regenerate the hash only on purpose. P949: the keys,
        # and the dot of each pin used or free, seen in a render on 2026-11-20. P946: the FireBeetle drawn from the old
        # page's group (no glow, each word upright or sideways on the sheet), BAT on the RX edge, and no "row side not verified" in the note, seen in a render on 2026-11-20.
        self.assertEqual(hashlib.sha256(self.text.encode()).hexdigest(),
                         "9b6aceacfe058a6b1fc01ef3502466322512f847f5d4c8f78af999ce5651209a")  # P953: the wires around the parts; ground through the - rail; PR 4a: a pill on each wire and the palette's hex; PR 4b: the pads in the steps' words read bottom to top, a caption per part and its note line, seen in a render on 2026-11-20

    def test_the_board_is_drawn_from_its_record_s_picture_with_its_credit(self):
        board = next(group for group in self.root.findall("svg:g", NS) if group.get("data-part") == wiring_steps.THE_BOARD)
        self.assertTrue(any(rect.get("fill") == "#16202a" for rect in board.iter("{http://www.w3.org/2000/svg}rect")))
        self.assertIn("pixel-master/docs/wiring.html", board.find("svg:title", NS).text)

    def test_the_xiao_has_none_of_it(self):
        text, _ = xiao_svg()
        self.assertNotIn("#cfd8dc", text)
        # no doubtful pad's dashed ring; P953: a wire that bends more than 4 times is dashed too, so the rings are counted
        self.assertEqual(len([circle for circle in svg_all(ElementTree.fromstring(text), "circle")
                              if circle.get("stroke-dasharray")]), 0)


class TheModuleSvgTest(unittest.TestCase):
    """P945: the e-paper drawn from its record beside the FireBeetle: its pads named into its body, no USB mark."""

    @classmethod
    def setUpClass(cls):
        with in_store():
            read = sheet._read_build(EPAPER / "requirements.json")
        geometry, catalog = epaper_inputs(read)
        cls.layout = drawing.BreadboardPlanner(geometry, catalog).plan(read.steps)
        cls.text = svg_diagram.SvgBreadboardDiagram().text(cls.layout)
        cls.root = ElementTree.fromstring(cls.text)
        cls.module = next(part for part in cls.layout.parts if part.id == "Epaper2in9BwrMhEtLive")
        cls.part_px = geometry.part(cls.module.type)

    def test_each_label_of_a_top_edge_row_sits_below_its_pad_within_half_a_pitch_turned_along_the_column(self):
        labels = {element.text: element for element in self.root.iter("{http://www.w3.org/2000/svg}text")
                  if element.text in self.part_px["pins"]}
        self.assertEqual(sorted(labels), sorted(["VCC", "GND", "SDI", "SCLK", "CS", "D/C", "Reset", "Busy"]))
        for pad, (x, y) in self.part_px["pins"].items():
            with self.subTest(pad=pad):
                label = labels[pad]
                self.assertLessEqual(abs(float(label.get("x")) - x), 4.8)
                self.assertGreater(float(label.get("y")), y)
                # P953 PR 4b: turned back a quarter, so it reads bottom to top
                self.assertTrue(label.get("transform").startswith("rotate(-90 "), label.get("transform"))

    def test_a_label_of_a_bottom_edge_row_sits_above_its_pad(self):
        # P953 PR 4b: it reads bottom to top, on a module turned by 0 or half round
        place = svg_diagram.IntoBodyLabels().place(50, 160, {"center": [100, 83]}, 0)
        self.assertEqual((place.y < 160, abs(place.x - 50) <= 4.8, place.anchor, place.rotate), (True, True, "start", -90))
        place = svg_diagram.IntoBodyLabels().place(50, 4.8, {"center": [100, 83]}, 0)
        self.assertEqual((place.y > 4.8, place.anchor), (True, "end"))
        place = svg_diagram.IntoBodyLabels().place(50, 4.8, {"center": [100, 83]}, 180)
        self.assertEqual((place.y > 4.8, abs(place.x - 50) <= 4.8, place.anchor, (180 + place.rotate) % 360),
                         (True, True, "start", 270))

    def test_the_module_draws_no_usb_mark_and_the_board_keeps_its_one(self):
        marks = [rect for rect in self.root.iter("{http://www.w3.org/2000/svg}rect") if rect.get("fill") == "#cfd8dc"]
        self.assertEqual(len(marks), 1)

    def test_the_module_is_named_by_its_record_s_name(self):
        # P953 PR 4b: its caption, the record's name up to its first comma, in place of its short name in its body
        texts = [element.text for element in self.root.iter("{http://www.w3.org/2000/svg}text")]
        self.assertIn("MH-ET LIVE 2.9 Inch E-paper Module", texts)
        self.assertNotIn("Epaper2in9BwrMhEtLive", texts)

    def test_the_canvas_holds_the_module_that_hangs_below_the_holes(self):
        bottom = self.module.top + self.part_px["size"][1]
        self.assertGreater(bottom, max(hole.y for hole in self.layout.geometry.surface.holes))
        self.assertGreaterEqual(float(self.root.get("height")), bottom + svg_diagram.SvgBreadboardDiagram.MARGIN_PX)

    def test_the_canvas_holds_each_body_when_no_wire_or_caption_reaches_past_it(self):
        # P969 PR 3: the canvas reads each body of the scene; here the wires run round the module and its caption sits
        # below it, so the scene is drawn with no wire and each caption moved onto the board
        scene = breadboard_scene.BreadboardSceneMaker().make(self.layout)
        board = scene.board
        bare = scene._replace(jumpers=(), parts=tuple(part._replace(caption=part.caption._replace(
            x=board.left + 10, y=board.top + 10)) for part in scene.parts))
        x, y, width, height = [float(n) for n in ElementTree.fromstring(
            svg_diagram.SvgBreadboardDiagram().draw(bare)).get("viewBox").split()]
        self.assertGreater(max(part.body.bottom for part in scene.parts), board.bottom + 19.2)
        for part in scene.parts:
            with self.subTest(part.part.id):
                self.assertLessEqual(x, part.body.left - 19.2 + 0.01)
                self.assertLessEqual(y, part.body.top - 19.2 + 0.01)
                self.assertGreaterEqual(x + width, part.body.right + 19.2 - 0.01)
                self.assertGreaterEqual(y + height, part.body.bottom + 19.2 - 0.01)


WALK = ROOT / "tests" / "data" / "breadboard" / "walk-c6"


def walk_svg(palette=None):
    with in_store():
        layout = sheet._plan_layout(sheet._read_build(WALK / "requirements.json"))
    return svg_diagram.SvgBreadboardDiagram(palette=palette).text(layout), layout


def svg_all(root, tag):
    return list(root.iter("{http://www.w3.org/2000/svg}%s" % tag))


class TheBoardLookTest(unittest.TestCase):
    """P953 (#1359): the breadboard in the old page's look (the README's wiring page): a white page, the board's warm body
    with its edge, the gap's band, square holes, four rails with their lines and signs, the letters and the numbers."""

    @classmethod
    def setUpClass(cls):
        cls.text, cls.layout = walk_svg()
        cls.root = ElementTree.fromstring(cls.text)
        cls.rects = svg_all(cls.root, "rect")
        cls.texts = svg_all(cls.root, "text")

    def test_the_page_is_white_and_covers_the_whole_view_box(self):
        x, y, width, height = [float(n) for n in self.root.get("viewBox").split()]
        page = self.rects[0]
        self.assertEqual(page.get("fill"), "#ffffff")
        self.assertEqual([float(page.get(key)) for key in ("x", "y", "width", "height")], [x, y, width, height])
        self.assertEqual((float(self.root.get("width")), float(self.root.get("height"))), (width, height))

    def test_the_board_has_its_body_edge_and_gap_band(self):
        board, gap = self.rects[1], self.rects[2]
        self.assertEqual((board.get("fill"), board.get("stroke"), board.get("rx")), ("#f4f1ea", "#c9c3b6", "4.3"))
        self.assertEqual(gap.get("fill"), "#e7e2d7")
        # the gap lies between row e (89.4) and row f (118.2), 24 px high, across the board's width
        self.assertEqual((float(gap.get("y")), float(gap.get("height"))), (91.8, 24))
        self.assertEqual((gap.get("x"), gap.get("width")), (board.get("x"), board.get("width")))
        surface = self.layout.geometry.surface
        left, top = float(board.get("x")), float(board.get("y"))
        self.assertEqual((left, top), (round(min(h.x for h in surface.holes) - 19.2, 3), round(min(h.y for h in surface.holes) - 19.2, 3)))

    def test_the_terminal_holes_are_square_and_8d969c_and_the_rail_holes_c2c0b8(self):
        terminal, rails = svg_all(self.root, "path")[:2]
        self.assertEqual((terminal.get("stroke"), terminal.get("stroke-width"), terminal.get("stroke-linecap")),
                         ("#8d969c", "2.7", "square"))
        self.assertEqual((rails.get("stroke"), rails.get("stroke-width"), rails.get("stroke-linecap")),
                         ("#c2c0b8", "2.35", "square"))
        self.assertEqual(len(re.findall(r"M[\d.]+ [\d.]+h0", terminal.get("d"))), 630)
        self.assertEqual(len(re.findall(r"M[\d.]+ [\d.]+h0", rails.get("d"))), 200)

    def test_there_are_four_rail_lines_and_four_signs_in_their_colours(self):
        lines = svg_all(self.root, "line")
        self.assertEqual([(line.get("stroke"), line.get("stroke-width"), line.get("stroke-opacity")) for line in lines],
                         [("#d0202a", "0.8", "0.6"), ("#1668c7", "0.8", "0.6")] * 2)
        # the lines frame each pair: red above the + rail, blue below the - rail, 0.4 pitch off the holes
        self.assertEqual([float(line.get("y1")) for line in lines], [8.76, 26.04, 181.56, 198.84])
        signs = [(text.text, text.get("fill")) for text in self.texts if text.text in ("+", "−")]
        self.assertEqual(signs, [("+", "#d0202a"), ("−", "#1668c7")] * 2)

    def test_the_letters_a_to_j_are_at_the_left_edge_once(self):
        letters = [text for text in self.texts if text.text and len(text.text) == 1 and text.text in "abcdefghij"]
        self.assertEqual([text.text for text in letters], list("abcdefghij"))
        self.assertEqual({(text.get("x"), text.get("fill"), text.get("font-size")) for text in letters},
                         {("16.4", "#6b7176", "5.9")})

    def test_the_numbers_are_1_and_every_5_above_and_below(self):
        numbers = [text for text in self.texts if text.text and text.text.isdigit() and text.get("fill") == "#6b7176"]
        said = ["1"] + [str(n) for n in range(5, 64, 5)]
        self.assertEqual([text.text for text in numbers], said + said)
        self.assertEqual({float(text.get("x")) for text in numbers[:2]}, {26, 64.4})
        top, bottom = {text.get("y") for text in numbers[:13]}, {text.get("y") for text in numbers[13:]}
        self.assertEqual((len(top), len(bottom)), (1, 1))
        self.assertLess(float(top.pop()), 12.6)
        self.assertGreater(float(bottom.pop()), 195)

    def test_the_same_layout_gives_the_same_bytes(self):
        self.assertTrue(self.text == svg_diagram.SvgBreadboardDiagram().text(self.layout))

    def test_the_font_family_is_set_once_on_the_root(self):
        # a part's own picture may set its own font; every text spark writes takes the root's
        self.assertEqual(self.root.get("font-family"), "Helvetica,Arial,sans-serif")
        own = ElementTree.fromstring(self.text)
        for group in own.findall("svg:g[@data-part]", NS):
            own.remove(group)
        self.assertEqual(ElementTree.tostring(own, encoding="unicode").count("font-family="), 1)

    def test_another_palette_changes_only_the_colours(self):
        palette = svg_diagram.BoardPalette.load()
        other = palette._replace(colors=dict(palette.colors, board="#000001"))
        text, _ = walk_svg(other)
        self.assertEqual(text.count("#000001"), 1)
        self.assertTrue(text.replace("#000001", "#f4f1ea") == self.text)


def wires(root):
    """Each drawn jumper's group: (under-stroke path, color path, end dots), in the order they are drawn."""
    found = []
    for group in root.findall("svg:g[@class='wire']", NS):
        paths, dots = group.findall("svg:path", NS), group.findall("svg:circle", NS)
        found.append((paths[0], paths[1], dots))
    return found


def segments(path):
    """The straight pieces of a jumper's path, ((x1, y1), (x2, y2)) each."""
    numbers = [float(n) for n in re.findall(r"-?[\d.]+", path.get("d"))]
    points = list(zip(numbers[::2], numbers[1::2]))
    return list(zip(points, points[1:]))


def shared_lines(drawn):
    """Each pair of pieces of two jumpers that lie on one line and overlap by more than 0 px."""
    pieces = [(number, piece) for number, path in enumerate(drawn) for piece in segments(path)]
    shared = []
    for index, (one, ((ax1, ay1), (ax2, ay2))) in enumerate(pieces):
        for other, ((bx1, by1), (bx2, by2)) in pieces[index + 1:]:
            if one == other:
                continue
            if ay1 == ay2 and by1 == by2 and abs(ay1 - by1) < 0.01:
                overlap = min(max(ax1, ax2), max(bx1, bx2)) - max(min(ax1, ax2), min(bx1, bx2))
            elif ax1 == ax2 and bx1 == bx2 and abs(ax1 - bx1) < 0.01:
                overlap = min(max(ay1, ay2), max(by1, by2)) - max(min(ay1, ay2), min(by1, by2))
            else:
                continue
            if overlap > 0.01:
                shared.append((one, other, ax1, ay1, overlap))
    return shared


def golden_svgs():
    """{golden file: its breadboard.svg}, for every golden sheet that holds a picture."""
    found = {}
    for path in sorted((ROOT / "tests" / "golden-breadboard").glob("breadboard-ok-*.txt")):
        text = path.read_text()
        if "--- breadboard.svg ---\n" in text:
            found[path.name] = text.split("--- breadboard.svg ---\n", 1)[1].split("\n--- ", 1)[0]
    return found


def epaper_svg():
    with in_store():
        read = sheet._read_build(EPAPER / "requirements.json")
    layout = drawing.BreadboardPlanner(*epaper_inputs(read)).plan(read.steps)
    return svg_diagram.SvgBreadboardDiagram().text(layout), layout


class TheWireStyleTest(unittest.TestCase):
    """P947, the praised page's wire: a white under-stroke, the color on the same path, and a dot at each end, the
    color by what the jumper carries."""

    @classmethod
    def setUpClass(cls):
        cls.text, cls.layout = epaper_svg()
        cls.root = ElementTree.fromstring(cls.text)

    def test_each_jumper_is_one_group_with_an_under_stroke_its_color_and_two_end_dots_at_its_holes(self):
        drawn = wires(self.root)
        self.assertEqual(len(drawn), len(self.layout.jumpers))
        for (under, color, dots), jumper in zip(drawn, self.layout.jumpers):
            with self.subTest(step=jumper.step):
                self.assertEqual((under.get("stroke"), under.get("d")), ("#ffffff", color.get("d")))
                self.assertGreater(float(under.get("stroke-width")), float(color.get("stroke-width")))
                self.assertEqual([(float(dot.get("cx")), float(dot.get("cy")), dot.get("fill")) for dot in dots],
                                 [(round(hole.x, 3), round(hole.y, 3), color.get("stroke"))
                                  for hole in (jumper.one, jumper.other)])
                self.assertEqual(segments(color)[0][0], (round(jumper.one.x, 3), round(jumper.one.y, 3)))
                self.assertEqual(segments(color)[-1][1], (round(jumper.other.x, 3), round(jumper.other.y, 3)))

    def test_3v3_is_red_gnd_is_black_and_no_signal_is_either(self):
        colors = {jumper.step: color.get("stroke") for (_, color, _), jumper in zip(wires(self.root), self.layout.jumpers)}
        # P953: power and ground go through the rails, so 3V3 has two jumpers (3, 4) and GND two (9, 10)
        # P953 PR 4a: red and black drawn in the palette's hex
        self.assertEqual((colors[3], colors[4], colors[9], colors[10]), ("#d0202a", "#d0202a", "#20262b", "#20262b"))
        self.assertFalse({"#d0202a", "#20262b"} & {colors[step] for step in colors if step not in (3, 4, 9, 10)})


#: The fixtures whose pictures the pill tests read with their layouts: the walk's and those of the golden sheets.
PILL_FIXTURES = ("walk-c6", "button-light-xiao", "button-light", "epaper")
#: The colour of each word a jumper's colour is named by (P953, the visual spec's palette; revision 8 keeps "cyan").
WIRE_HEX = {"red": "#d0202a", "black": "#20262b", "green": "#0b7a43", "blue": "#1668c7", "purple": "#7a3fc0",
            "orange": "#b85c00", "magenta": "#b0127a", "cyan": "#0b7fa8", "gray": "#5f6b73"}


def fixture_svg(fixture):
    """(the sheet's picture of one fixture, its layout), planned and drawn as a build draws it, with an empty store."""
    with in_store():
        layout = sheet._plan_layout(sheet._read_build(ROOT / "tests" / "data" / "breadboard" / fixture / "requirements.json"))
        renderer = next(one for one in sheet.DRAWING_RENDERERS if isinstance(one, svg_diagram.SvgBreadboardDiagram))
        return renderer.text(layout), layout


def pill_of(group):
    """The pill group inside one jumper's group."""
    return group.find("svg:g[@class='pill']", NS)


def pill_box(pill):
    """(left, top, right, bottom) of a pill as drawn: its rect, turned about its centre when its group turns it."""
    rect = pill.find("svg:rect", NS)
    x, y, width, height = (float(rect.get(key)) for key in ("x", "y", "width", "height"))
    turn = re.search(r"rotate\((-?[\d.]+) (-?[\d.]+) (-?[\d.]+)\)", pill.get("transform") or "")
    if not turn:
        return x, y, x + width, y + height
    angle, cx, cy = (float(n) for n in turn.groups())
    cos, sin = round(math.cos(math.radians(angle))), round(math.sin(math.radians(angle)))
    corners = [(cx + (px - cx) * cos - (py - cy) * sin, cy + (px - cx) * sin + (py - cy) * cos)
               for px in (x, x + width) for py in (y, y + height)]
    return (min(px for px, _ in corners), min(py for _, py in corners), max(px for px, _ in corners),
            max(py for _, py in corners))


def board_marks(root):
    """(text, box) of each mark printed on the board itself, the root's own centred texts (a caption and a note line
    start at their x): each row letter, column number and rail sign, its box 0.6 of its size wide a character, from 0.75
    of its size above its baseline to 0.25 below, about its x."""
    marks = []
    for text in root.findall("svg:text", NS):
        if text.get("text-anchor") == "middle":
            x, y, size = float(text.get("x")), float(text.get("y")), float(text.get("font-size"))
            half = 0.3 * size * len(text.text)
            marks.append((text.text, (x - half, y - 0.75 * size, x + half, y + 0.25 * size)))
    return marks


def boxes_meet(one, other, by=0):
    """True when two boxes (left, top, right, bottom) overlap or come closer than `by`."""
    return (one[0] - by <= other[2] and other[0] - by <= one[2] and one[1] - by <= other[3] and other[1] - by <= one[3])


class ThePillsTest(unittest.TestCase):
    """P953 PR 4a: every jumper carries one pill, the PO's "7  SDI to D11": its step's number in a white disc, then the
    two pads it joins, the board's last; on its wire, clear of every body, end dot, other wire and other pill."""

    @classmethod
    def setUpClass(cls):
        cls.drawn = {fixture: fixture_svg(fixture) for fixture in PILL_FIXTURES}
        cls.pictures = dict(golden_svgs(), **{fixture: text for fixture, (text, _) in cls.drawn.items()})

    def test_each_jumper_has_exactly_one_pill_inside_its_group(self):
        dashed = 0
        for name, text in self.pictures.items():
            with self.subTest(name):
                root = ElementTree.fromstring(text)
                groups = root.findall(".//svg:g[@class='wire']", NS)
                self.assertGreaterEqual(len(groups), 2)
                for group in groups:
                    self.assertEqual(len(group.findall("svg:g[@class='pill']", NS)), 1, group.get("data-step"))
                    self.assertEqual(pill_of(group).findall("svg:text", NS)[0].text, group.get("data-step"))
                    dashed += bool(group.findall("svg:path", NS)[1].get("stroke-dasharray"))
                self.assertEqual(len(root.findall(".//svg:g[@class='pill']", NS)), len(groups))
        self.assertGreaterEqual(dashed, 4)  # a dashed wire (the walk's 6, 7, 10 and 11) carries its pill too

    def test_the_walk_s_pills_read_as_the_po_said(self):
        # read from the walk's sheet: 3 board 3V3 to a free + rail, 6 board D3 to the row of e-paper CS, 8 board GND to a
        # free - rail, 10 board MOSI to the row of e-paper SDI, ...
        root = ElementTree.fromstring(self.drawn["walk-c6"][0])
        words = {int(group.get("data-step")): pill_of(group).findall("svg:text", NS)[1].text
                 for group in root.findall(".//svg:g[@class='wire']", NS)}
        self.assertEqual(words, {3: "3V3 to + rail", 4: "3V3_2 to + rail", 5: "VCC to + rail", 6: "CS to D3",
                                 7: "D/C to D7", 8: "GND to - rail", 9: "GND to - rail", 10: "SDI to MOSI",
                                 11: "SCLK to SCK", 12: "Busy to SCL", 13: "Reset to SDA"})

    def test_the_number_is_in_the_disc_before_the_words(self):
        for name, text in self.pictures.items():
            with self.subTest(name):
                for group in ElementTree.fromstring(text).findall(".//svg:g[@class='wire']", NS):
                    color = group.findall("svg:path", NS)[1].get("stroke")
                    pill = pill_of(group)
                    rect, disc = pill.find("svg:rect", NS), pill.find("svg:circle", NS)
                    number, words = pill.findall("svg:text", NS)
                    self.assertEqual((rect.get("height"), rect.get("rx"), rect.get("fill"), rect.get("stroke"),
                                      rect.get("stroke-width")), ("9.6", "4.8", color, "#ffffff", "0.53"))
                    self.assertEqual((disc.get("r"), disc.get("fill")), ("3.4", "#ffffff"))
                    self.assertAlmostEqual(float(disc.get("cx")) - float(rect.get("x")), 4.8, places=2)
                    self.assertEqual((number.get("x"), number.get("text-anchor"), number.get("font-size"),
                                      number.get("font-weight"), number.get("fill")),
                                     (disc.get("cx"), "middle", "5.3", "800", color))
                    self.assertGreaterEqual(float(words.get("x")), float(disc.get("cx")) + 3.4 + 1.6 - 0.01)
                    self.assertEqual((words.get("font-size"), words.get("font-weight"), words.get("fill")),
                                     ("6.1", "700", "#ffffff"))
                    self.assertAlmostEqual(float(rect.get("width")), 9.6 + 3.6 + 3.57 * len(words.text), places=2)

    def test_no_two_pill_boxes_touch(self):
        for name, text in self.pictures.items():
            with self.subTest(name):
                boxes = [(group.get("data-step"), pill_box(pill_of(group)))
                         for group in ElementTree.fromstring(text).findall(".//svg:g[@class='wire']", NS)]
                self.assertGreaterEqual(len(boxes), 2)
                self.assertEqual([(one, other) for index, (one, a) in enumerate(boxes) for other, b in boxes[index + 1:]
                                  if boxes_meet(a, b)], [])

    def test_no_pill_touches_a_body_an_end_dot_or_another_wire(self):
        for fixture, (text, layout) in self.drawn.items():
            with self.subTest(fixture):
                groups = ElementTree.fromstring(text).findall(".//svg:g[@class='wire']", NS)
                bodies = [(box.left, box.top, box.right, box.bottom) for box in (
                    svg_diagram.BodyBox.of(part, layout.geometry.part(part.type)) for part in layout.parts)]
                dots = [(float(dot.get("cx")), float(dot.get("cy")), float(dot.get("r")) + float(dot.get("stroke-width")) / 2)
                        for group in groups for dot in group.findall("svg:circle", NS)]
                self.assertEqual(len(dots), 2 * len(layout.jumpers))
                for group in groups:
                    box = pill_box(pill_of(group))
                    with self.subTest(step=group.get("data-step")):
                        self.assertFalse([body for body in bodies if boxes_meet(box, body)])
                        self.assertFalse([dot for dot in dots if boxes_meet(box, (dot[0], dot[1], dot[0], dot[1]), dot[2])])
                        for other in groups:
                            if other is group:
                                continue
                            under, color = other.findall("svg:path", NS)[:2]
                            half = float(under.get("stroke-width")) / 2
                            near = [piece for piece in segments(color) if boxes_meet(box, (
                                min(piece[0][0], piece[1][0]), min(piece[0][1], piece[1][1]),
                                max(piece[0][0], piece[1][0]), max(piece[0][1], piece[1][1])), half)]
                            self.assertEqual(near, [], other.get("data-step"))
        # the review of PR #1377: no pill meets a printed mark of the board, a row letter, a column number or a rail's
        # sign, on every fixture and every golden picture (the rebuild's too); PR 4b: nor a part's caption
        for name, text in self.pictures.items():
            with self.subTest(name):
                root = ElementTree.fromstring(text)
                marks = board_marks(root) + [(words, caption_box(caption)) for words, caption in captions(root).items()]
                self.assertGreaterEqual(len([mark for mark, _ in marks if mark in ("+", "−")]), 2)
                self.assertGreaterEqual(len(captions(root)), 2)
                for group in root.findall(".//svg:g[@class='wire']", NS):
                    box = pill_box(pill_of(group))
                    self.assertEqual([mark for mark, other in marks if boxes_meet(box, other)], [], group.get("data-step"))

    def test_every_pill_finds_a_free_place_on_every_fixture(self):
        # no pill falls back to its longest run's middle: each sits on a straight piece of its own wire, centred across
        # it, or, on a stub too short to hold it (a jumper into a rail), beside it or past its end, within 6 px of it
        for fixture, (_, layout) in self.drawn.items():
            with self.subTest(fixture):
                bodies = [svg_diagram.BodyBox.of(part, layout.geometry.part(part.type)) for part in layout.parts]
                marks = board_marks_module.BoardMarks(layout.geometry.surface, board_marks_module.BoardPalette.load().sizes)
                obstacles = marks.obstacles(bodies)
                paths = wire_routing.TrackJumperRouter().route(layout, obstacles)
                signs = marks.sign_boxes()
                self.assertEqual(len(signs), 4)
                pills = wire_pills.PillLayout(4.0, 3.4, breadboard_scene.PxLabelMeasure(7)).place(layout.jumpers, paths,
                                                                                                  obstacles._replace(marks=obstacles.marks + signs))
                self.assertEqual(sorted(pills), sorted(jumper.step for jumper in layout.jumpers))
                for step, pill in pills.items():
                    box = pill.box()
                    pieces = list(zip(paths[step].points, paths[step].points[1:]))
                    on = [piece for piece in pieces if
                          (piece[0][1] == piece[1][1] == pill.y and not pill.turned
                           and min(piece[0][0], piece[1][0]) < box.left and box.right < max(piece[0][0], piece[1][0])) or
                          (piece[0][0] == piece[1][0] == pill.x and pill.turned
                           and min(piece[0][1], piece[1][1]) < box.top and box.bottom < max(piece[0][1], piece[1][1]))]
                    beside = [piece for piece in pieces if boxes_meet(
                        (box.left, box.top, box.right, box.bottom), (min(piece[0][0], piece[1][0]), min(piece[0][1], piece[1][1]),
                                                                     max(piece[0][0], piece[1][0]), max(piece[0][1], piece[1][1])), 6)]
                    self.assertEqual((pill.free, bool(on or beside)), (True, True), (step, pill))


def affine(transform):
    """The matrix (a, b, c, d, e, f) of an SVG transform list: translate, rotate about a point, scale and matrix."""
    matrix = (1, 0, 0, 1, 0, 0)
    for name, numbers in re.findall(r"(\w+)\(([^)]*)\)", transform or ""):
        n = [float(one) for one in re.findall(r"-?[\d.]+(?:e-?\d+)?", numbers)]
        if name == "translate":
            step = (1, 0, 0, 1, n[0], n[1] if len(n) > 1 else 0)
        elif name == "scale":
            step = (n[0], 0, 0, n[1] if len(n) > 1 else n[0], 0, 0)
        elif name == "matrix":
            step = tuple(n)
        else:
            cos, sin = math.cos(math.radians(n[0])), math.sin(math.radians(n[0]))
            cx, cy = (n[1], n[2]) if len(n) > 1 else (0, 0)
            step = (cos, sin, -sin, cos, cx - cos * cx + sin * cy, cy - sin * cx - cos * cy)
        matrix = compose(matrix, step)
    return matrix


def compose(one, other):
    """The matrix that applies `other`, then `one`."""
    a, b, c, d, e, f = one
    p, q, r, s, t, u = other
    return (a * p + c * q, b * p + d * q, a * r + c * s, b * r + d * s, a * t + c * u + e, b * t + d * u + f)


def sheet_texts(root):
    """(text element, the matrix that puts it on the sheet) of every text: its ancestors' transforms and its own."""
    found = []

    def walk(element, matrix):
        matrix = compose(matrix, affine(element.get("transform")))
        if element.tag == "{http://www.w3.org/2000/svg}text":
            found.append((element, matrix))
        for child in element:
            walk(child, matrix)

    walk(root, (1, 0, 0, 1, 0, 0))
    return found


def turn_of(matrix):
    """The turn of a matrix on the sheet, in degrees from 0 to 360."""
    return round(math.degrees(math.atan2(matrix[1], matrix[0]))) % 360


def text_box(text, matrix):
    """(left, top, right, bottom) of a text on the sheet: 0.6 of its size wide a character, from 0.75 of its size above
    its baseline to 0.25 below, by its anchor, turned by its matrix."""
    x, y, size = float(text.get("x")), float(text.get("y")), float(text.get("font-size"))
    width = 0.6 * size * len(text.text)
    left = x - {"middle": width / 2, "end": width}.get(text.get("text-anchor"), 0)
    corners = [(matrix[0] * px + matrix[2] * py + matrix[4], matrix[1] * px + matrix[3] * py + matrix[5])
               for px in (left, left + width) for py in (y - 0.75 * size, y + 0.25 * size)]
    return (min(px for px, _ in corners), min(py for _, py in corners), max(px for px, _ in corners),
            max(py for _, py in corners))


def caption_box(text):
    """(left, top, right, bottom) of a caption: 0.55 of its size wide a character plus half its size (Chrome draws the
    fixtures' names 0.50 to 0.54), from 0.75 of its size above its baseline to 0.25 below."""
    x, y, size = float(text.get("x")), float(text.get("y")), float(text.get("font-size"))
    return x, y - 0.75 * size, x + (0.55 * len(text.text) + 0.5) * size, y + 0.25 * size


def captions(root):
    """{words: text element} of each part's caption."""
    return {text.text: text for text in root.findall("svg:text[@class='caption']", NS)}


def pad_labels(root):
    """(text element, its matrix on the sheet) of each pad label of every part drawn from its record."""
    labels = {id(text) for group in root.iter("{http://www.w3.org/2000/svg}g") if group.get("class") == "pad-labels"
              for text in group.findall("svg:text", NS)}
    return [(text, matrix) for text, matrix in sheet_texts(root) if id(text) in labels]


class TheLabelsTest(unittest.TestCase):
    """P953 PR 4b: a pad's label says the steps' word for it, every turned text reads bottom to top, and each part has one
    caption outside its body with its human name, where no wire runs."""

    @classmethod
    def setUpClass(cls):
        cls.drawn = {fixture: fixture_svg(fixture) for fixture in PILL_FIXTURES}
        cls.pictures = dict(golden_svgs(), **{fixture: text for fixture, (text, _) in cls.drawn.items()})
        cls.walk = ElementTree.fromstring(cls.drawn["walk-c6"][0])

    def test_a_ground_pad_reads_gnd_and_an_nc_pad_reads_nc_muted(self):
        # the steps' function: the C6's GND1 and GND2 are "board GND" in the walk's sheet, its NC1 to NC5 no end at all
        self.assertEqual([wiring_steps.pad_word(pad) for pad in ("GND1", "GND2", "GND", "NC5", "NC12", "ENC1", "D3")],
                         ["GND", "GND", "GND", "NC", "NC", "ENC1", "D3"])
        board = [text for text, _ in pad_labels(self.walk) if text.text not in
                 ("VCC", "SDI", "SCLK", "CS", "D/C", "Reset", "Busy")]  # the e-paper's own, but its GND
        words = [text.text for text in board]
        self.assertEqual((len(words), words.count("GND"), words.count("NC")), (33, 3, 5))  # the C6's 32 and the e-paper's GND
        self.assertEqual({text.get("fill") for text in board if text.text == "NC"}, {"#8d969c"})
        for name, text in self.pictures.items():
            with self.subTest(name):
                self.assertEqual([one.text for one, _ in pad_labels(ElementTree.fromstring(text))
                                  if re.fullmatch(r"(GND|NC)\d+", one.text)], [])

    def test_3v3_2_stays_as_the_steps_say_it(self):
        golden = (ROOT / "tests" / "golden-breadboard" / "breadboard-ok-c6.txt").read_text()
        self.assertIn("4. Run a jumper from board 3V3_2 to the 3V3 rail.", golden)
        words = [text.text for text, _ in pad_labels(self.walk)]
        self.assertEqual((words.count("3V3_2"), words.count("3V3")), (1, 1))

    def test_a_used_pad_reads_bold_yellow_and_the_others_dim_each_with_a_dark_outline(self):
        # read from the walk's sheet: the board's ends are 3V3, 3V3_2, D3, D7, GND, MOSI, SCK, SCL and SDA; every e-paper pad
        labels = [text for text, _ in pad_labels(self.walk)]
        used = sorted(text.text for text in labels if text.get("fill") == "#ffd34d")
        self.assertEqual(used, sorted(["3V3", "3V3_2", "D3", "D7", "GND", "MOSI", "SCK", "SCL", "SDA", "VCC", "GND", "SDI",
                                       "SCLK", "CS", "D/C", "Reset", "Busy"]))
        for text in labels:
            with self.subTest(text.text):
                bold = text.get("fill") == "#ffd34d"
                self.assertEqual((text.get("font-size"), text.get("font-weight")), ("5.2", "700") if bold else ("5", None))
                self.assertIn(text.get("fill"), ("#ffd34d", "#b8c2ca", "#8d969c"))
                self.assertEqual((text.get("stroke"), text.get("stroke-width"), text.get("paint-order")),
                                 ("#121820", "1.3", "stroke"))

    def test_every_turned_text_reads_bottom_to_top(self):
        # replaces the record board's check that no word reads upside down: one way only, 0 or -90 on the sheet, for
        # the pad labels, the pills, the parts' own pictures and the board's marks
        turned = 0
        for name, text in self.pictures.items():
            with self.subTest(name):
                for element, matrix in sheet_texts(ElementTree.fromstring(text)):
                    self.assertIn(turn_of(matrix), (0, 270), element.text)
                    turned += turn_of(matrix) == 270
        self.assertGreaterEqual(turned, 100)

    def test_no_wire_touches_a_label_or_a_caption(self):
        for name, text in self.pictures.items():
            with self.subTest(name):
                root = ElementTree.fromstring(text)
                boxes = [(one.text, text_box(one, matrix)) for one, matrix in pad_labels(root)] + [
                    (words, caption_box(one)) for words, one in captions(root).items()]
                self.assertGreaterEqual(len(boxes), 2)
                for under, color, _ in wires(root):
                    half = float(under.get("stroke-width")) / 2
                    for (x1, y1), (x2, y2) in segments(color):
                        piece = (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
                        self.assertEqual([words for words, box in boxes if boxes_meet(box, piece, half)], [],
                                         (x1, y1, x2, y2))

    def test_each_part_has_one_caption_outside_its_body_with_its_human_name(self):
        expected = {"walk-c6": ["DFRobot FireBeetle 2 ESP32-C6", "MH-ET LIVE 2.9 Inch E-paper Module"],
                    "button-light-xiao": ["Seeed Studio XIAO ESP32-C6", "6x6 mm tactile push button",
                                          "Kingbright L-7113ID 5 mm red LED", "R1"],
                    "button-light": ["DFRobot FireBeetle 2 ESP32-S3", "6x6 mm tactile push button",
                                     "Kingbright L-7113ID 5 mm red LED", "R1"],
                    "epaper": ["DFRobot FireBeetle 2 ESP32-S3", "MH-ET LIVE 2.9 Inch E-paper Module"]}
        for fixture, (text, layout) in self.drawn.items():
            with self.subTest(fixture):
                root = ElementTree.fromstring(text)
                found = captions(root)
                self.assertEqual(len(root.findall("svg:text[@class='caption']", NS)), len(layout.parts))
                self.assertEqual(sorted(found), sorted(expected[fixture]))
                bodies = [svg_diagram.BodyBox.of(part, layout.geometry.part(part.type)) for part in layout.parts]
                for words, caption in found.items():
                    self.assertFalse([body for body in bodies if boxes_meet(caption_box(caption), body)], words)
                    self.assertEqual((caption.get("font-size"), caption.get("font-weight")), ("7", "600"))
                    if words != "R1":
                        self.assertEqual(caption.get("fill"), "#20262b")
                for words in ("board", "Epaper2in9BwrMhEtLive", "firebeetle2-esp32c6", "epaper-2in9-bwr-mh-et-live"):
                    self.assertNotIn(">%s<" % words, text)

    def test_the_walk_s_board_caption_sits_at_its_body_s_left_edge_inside_the_canvas(self):
        # the review of PR #1379: slid right along the board it sat under pill 12 and read as that pill's words
        _, layout = self.drawn["walk-c6"]
        board = next(part for part in layout.parts if part.id == wiring_steps.THE_BOARD)
        body = svg_diagram.BodyBox.of(board, layout.geometry.part(board.type))
        caption = captions(self.walk)["DFRobot FireBeetle 2 ESP32-C6"]
        self.assertAlmostEqual(float(caption.get("x")), body.left, places=2)
        self.assertLessEqual(caption_box(caption)[3], body.top)
        left, top = (float(n) for n in self.walk.get("viewBox").split()[:2])
        self.assertGreater(caption_box(caption)[1], top)
        self.assertGreaterEqual(caption_box(caption)[0], left)

    def test_a_part_with_no_name_is_captioned_by_its_id_muted(self):
        self.assertEqual(captions(ElementTree.fromstring(self.drawn["button-light-xiao"][0]))["R1"].get("fill"), "#6b7176")

        def part(record):
            return drawing.PlacedPart("LedRed5mm", "wokwi-led", {}, 0, 0, 0, {}, record)

        self.assertEqual([part_captions.PartCaption.words(part(record)) for record in (
            {"id": "led-x", "name": "Maker LED, red, 5 mm"}, {"id": "led-x", "name": ""}, {"id": "led-x"}, None, {"name": 7})],
            [("Maker LED", True), ("led-x", False), ("led-x", False), ("LedRed5mm", False), ("LedRed5mm", False)])


class TheNoteTest(unittest.TestCase):
    """P953 PR 4b: the note under the picture, one line per part with its human name and no record id."""

    def test_one_line_per_part_with_its_human_name_and_no_record_id(self):
        lines = {}
        for fixture in ("walk-c6", "button-light"):
            root = ElementTree.fromstring(fixture_svg(fixture)[0])
            notes = root.findall("svg:text[@class='note']", NS)
            self.assertEqual({(note.get("font-size"), note.get("fill")) for note in notes}, {("6", "#6b7176")})
            lines[fixture] = [note.text for note in notes]
        self.assertEqual(lines, {
            "walk-c6": ["DFRobot FireBeetle 2 ESP32-C6: pads, row side and USB end not verified.",
                        "MH-ET LIVE 2.9 Inch E-paper Module: pads and header side not verified.",
                        "wires 6, 7, 10 and 11 bend more than 4 times to go around the parts and are drawn dashed"],
            "button-light": ["DFRobot FireBeetle 2 ESP32-S3: pads, USB end and the pads in a dashed ring not verified."]})

    def test_a_part_names_its_id_only_when_its_record_has_no_name(self):
        # the review of PR #1379: the note follows the caption's rule, so a record id shows only where no name is
        class Geometry:
            def part(self, part_type):
                return {"notes": [{"words": "pads"}, {"words": "header side"}]}

        parts = [drawing.PlacedPart(part_id, "spark-module-x", {}, 0, 0, 0, {}, record) for part_id, record in (
            ("Named", {"id": "named-module", "name": "Maker Module, rev 2"}), ("Nameless", {"id": "nameless-module"}),
            ("NoRecord", None))]
        layout = drawing.BreadboardLayout(None, parts, [], Geometry())
        pictures = {part.id: part_pictures.Picture("", (0, 0, 1, 1), "") for part in parts}
        self.assertEqual(part_captions.PartNotes.lines(layout, pictures), [
            "Maker Module: pads and header side not verified.", "nameless-module: pads and header side not verified.",
            "NoRecord: pads and header side not verified."])


def contrast(one, other):
    """The WCAG contrast ratio of two #rrggbb colours."""
    def luminance(color):
        channels = [int(color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
        linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
        return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]
    high, low = sorted((luminance(one), luminance(other)), reverse=True)
    return (high + 0.05) / (low + 0.05)


class TheWirePaletteTest(unittest.TestCase):
    """P953 PR 4a: the wires in the visual spec's palette (data/breadboards.json's palette.wires), the sheet's words
    unchanged, and the wire's sizes of the old page at spark's pitch."""

    @classmethod
    def setUpClass(cls):
        cls.text, cls.layout = fixture_svg("walk-c6")
        cls.root = ElementTree.fromstring(cls.text)

    def test_each_word_draws_its_hex(self):
        self.assertEqual(svg_diagram.BoardPalette.load().colors["wires"], WIRE_HEX)
        words = wiring_steps.JumperColors().of({jumper.step: jumper.role for jumper in self.layout.jumpers})
        drawn = {int(group.get("data-step")): group.findall("svg:path", NS)[1].get("stroke")
                 for group in self.root.findall(".//svg:g[@class='wire']", NS)}
        self.assertEqual(drawn, {step: WIRE_HEX[word] for step, word in words.items()})
        self.assertEqual(len(set(drawn.values())), 8)  # red, black and the six signals

    def test_the_sixth_signal_keeps_its_word_cyan_on_the_sheet_and_draws_0b7fa8(self):
        # revision 8: no rename to teal; the sheet's word names the wire in hand, the picture draws it darker. The walk's
        # golden sheet holds both: its colour line, then its picture
        golden = (ROOT / "tests" / "golden-breadboard" / "breadboard-ok-c6.txt").read_text()
        self.assertIn("12 magenta, 13 cyan.", golden)
        root = ElementTree.fromstring(golden_svgs()["breadboard-ok-c6.txt"])
        group = next(one for one in root.findall(".//svg:g[@class='wire']", NS) if one.get("data-step") == "13")
        self.assertEqual(group.findall("svg:path", NS)[1].get("stroke"), "#0b7fa8")
        self.assertNotIn('"cyan"', golden_svgs()["breadboard-ok-c6.txt"])

    def test_every_wire_colour_has_4_5_to_1_on_white_and_3_to_1_on_the_board(self):
        # 4.5:1 (WCAG 1.4.3): a pill's white words on the wire's colour, its number in that colour on the white disc;
        # 3:1 (WCAG 1.4.11): the wire on the board's body
        palette = svg_diagram.BoardPalette.load().colors
        for word, color in palette["wires"].items():
            with self.subTest(word):
                self.assertGreaterEqual(contrast(color, "#ffffff"), 4.5)
                self.assertGreaterEqual(contrast(color, palette["board"]), 3.0)

    def test_the_wire_is_2_2_on_a_4_white_under_stroke_and_its_end_dot_3_with_a_0_8_ring(self):
        for group in self.root.findall(".//svg:g[@class='wire']", NS):
            under, color = group.findall("svg:path", NS)[:2]
            self.assertEqual((float(under.get("stroke-width")), float(color.get("stroke-width"))), (4.0, 2.2))
            for dot in group.findall("svg:circle", NS):
                self.assertEqual((float(dot.get("r")), dot.get("stroke"), float(dot.get("stroke-width"))), (3.0, "#ffffff", 0.8))


class TheJumperLanesTest(unittest.TestCase):
    """P947: one lane per jumper, so no two jumpers share a drawn line (P953: no two pills touch, ThePillsTest), on the walk's
    e-paper sheet and on every golden sheet with a picture."""

    @classmethod
    def setUpClass(cls):
        text, cls.layout = epaper_svg()
        cls.pictures = dict(golden_svgs(), epaper=text)

    def test_every_golden_sheet_with_a_picture_is_read(self):
        self.assertEqual(sorted(self.pictures), ["breadboard-ok-c6.txt", "breadboard-ok-firebeetle.txt", "breadboard-ok-module.txt",
                                                 "breadboard-ok-rebuild.txt", "breadboard-ok-xiao.txt", "epaper"])

    def test_no_two_jumpers_share_a_drawn_line(self):
        for name, text in self.pictures.items():
            with self.subTest(name):
                drawn = [color for _, color, _ in wires(ElementTree.fromstring(text))]
                self.assertGreaterEqual(len(drawn), 2)
                self.assertEqual(shared_lines(drawn), [])

    def test_each_run_lies_at_least_half_a_pitch_off_every_row_of_holes(self):
        rows = sorted({hole.y for hole in self.layout.geometry.surface.terminal})
        half = self.layout.geometry.surface.pitch / 2
        for (_, color, _) in wires(ElementTree.fromstring(self.pictures["epaper"])):
            runs = [y1 for (x1, y1), (x2, y2) in segments(color) if y1 == y2 and x1 != x2]
            for y in runs:
                self.assertGreaterEqual(min(abs(y - row) for row in rows), half - 0.01, y)

    def test_the_e_paper_s_eight_runs_take_eight_lines(self):
        # P953: the picture's wires go around the parts on tracks (tests/test_wire_routing.py); the lanes stay a Strategy
        lines = wire_routing.LaneJumperRouter().lines(self.layout.jumpers, self.layout.geometry.surface.pitch)
        self.assertEqual(len(set(lines.values())), 8)

    def test_overlapping_spans_take_lines_one_pitch_apart_toward_their_first_end_the_shorter_first(self):
        def hole(column, y):
            return drawing.Hole("%d" % column, 10 * column, y, "%d" % column, column)
        long_up = drawing.Jumper(hole(1, 150), hole(9, 50), 4)
        short_up = drawing.Jumper(hole(3, 150), hole(6, 50), 5)
        down = drawing.Jumper(hole(4, 50), hole(7, 150), 6)
        lines = wire_routing.LaneJumperRouter().lines([long_up, short_up, down], 10)
        self.assertEqual(lines, {5: 55, 4: 65, 6: 145})

    def test_spans_more_than_a_pitch_apart_share_a_line(self):
        def hole(column, y):
            return drawing.Hole("%d" % column, 10 * column, y, "%d" % column, column)
        lines = wire_routing.LaneJumperRouter().lines([drawing.Jumper(hole(1, 150), hole(3, 50), 1),
                                                 drawing.Jumper(hole(5, 150), hole(7, 50), 2)], 10)
        self.assertEqual(lines, {1: 55, 2: 55})

    def test_two_legs_never_share_a_column(self):
        # The review: jumpers 1a to 5j and 1j to 8a both have a leg in column 1; the second runs past the first one's end.
        def hole(column, y):
            return drawing.Hole("%d" % column, 10 * column, y, "%d" % column, column)
        jumpers = [drawing.Jumper(hole(1, 50), hole(5, 150), 1), drawing.Jumper(hole(1, 150), hole(8, 50), 2)]
        lines = wire_routing.LaneJumperRouter().lines(jumpers, 10)
        legs = [sorted((50, lines[1])), sorted((150, lines[2]))]
        self.assertLessEqual(min(legs[0][1], legs[1][1]) - max(legs[0][0], legs[1][0]), 0, lines)
        self.assertEqual(lines, {1: 145, 2: 155})

    def test_spans_less_than_a_pitch_apart_take_two_lines(self):
        def hole(column, y):
            return drawing.Hole("%d" % column, 10 * column, y, "%d" % column, column)
        lines = wire_routing.LaneJumperRouter().lines([drawing.Jumper(hole(1, 150), hole(3, 50), 1),
                                                 drawing.Jumper(hole(4, 150), hole(6, 50), 2)], 10)
        self.assertEqual(lines, {1: 55, 2: 65})


class TheKeysTest(unittest.TestCase):
    """P949: a player finds each jumper by its step and each part by its id, as data attributes, never as an id."""

    @classmethod
    def setUpClass(cls):
        cls.drawn = {"xiao": xiao_svg(), "epaper": epaper_svg()}

    def test_each_jumper_is_one_group_keyed_by_its_step_once(self):
        for name, (text, layout) in self.drawn.items():
            with self.subTest(name):
                groups = ElementTree.fromstring(text).findall(".//*[@data-step]")
                self.assertEqual(sorted(int(group.get("data-step")) for group in groups),
                                 sorted(jumper.step for jumper in layout.jumpers))
                self.assertGreaterEqual(len(groups), 2)
                jumpers = {jumper.step: jumper for jumper in layout.jumpers}
                for group in groups:
                    jumper = jumpers[int(group.get("data-step"))]
                    color = group.findall("svg:path", NS)[1]
                    self.assertEqual((segments(color)[0][0], segments(color)[-1][1]),
                                     ((round(jumper.one.x, 3), round(jumper.one.y, 3)),
                                      (round(jumper.other.x, 3), round(jumper.other.y, 3))))

    def test_each_part_is_one_group_keyed_by_its_id_once(self):
        for name, (text, layout) in self.drawn.items():
            with self.subTest(name):
                groups = ElementTree.fromstring(text).findall(".//*[@data-part]")
                self.assertEqual(sorted(group.get("data-part") for group in groups),
                                 sorted(part.id for part in layout.parts))
                self.assertGreaterEqual(len(groups), 2)
        board = [group for group in ElementTree.fromstring(self.drawn["xiao"][0]).findall(".//*[@data-part]")
                 if group.get("data-part") == wiring_steps.THE_BOARD]
        self.assertEqual(len(board), 1)
        self.assertIn("rotate(90 34 44)", board[0].get("transform"))

    def test_no_key_is_an_id(self):
        for name, (text, _layout) in self.drawn.items():
            with self.subTest(name):
                self.assertNotIn(" id=", text)


def pad_states(text, layout):
    """{(part id, pin): the data-pad of the dot drawn on its hole}."""
    dots = {(float(dot.get("cx")), float(dot.get("cy"))): dot.get("data-pad")
            for dot in ElementTree.fromstring(text).iter("{http://www.w3.org/2000/svg}circle") if dot.get("data-pad")}
    return {(part.id, pin): dots.get((round(hole.x, 3), round(hole.y, 3)))
            for part in layout.parts for pin, hole in part.holes.items()}


class ThePadStatesTest(unittest.TestCase):
    """P949: the dot on each pin says whether its row joins a wire or another part (in use) or nothing (free)."""

    def test_a_pin_is_used_when_its_row_joins_a_jumper_or_another_part_and_free_otherwise(self):
        text, layout = xiao_svg()
        # read from the fixture's steps: jumpers 5 to 8 end on D8, D10, GND, the button's 1.l and 2.l, the LED's C and R1's
        # 1; the LED's A shares its row with R1's 2
        used = {("board", "D8"), ("board", "D10"), ("board", "GND"), ("TactileButton", "1.l"), ("TactileButton", "2.l"),
                ("LedRed5mm", "A"), ("LedRed5mm", "C"), ("R1", "1"), ("R1", "2")}
        states = pad_states(text, layout)
        self.assertEqual(len(states), 22)
        self.assertEqual({pin for pin, state in states.items() if state == "used"}, used)
        self.assertEqual({pin for pin, state in states.items() if state == "free"}, set(states) - used)
        fills = {dot.get("data-pad"): dot.get("fill") for dot in ElementTree.fromstring(text).iter(
            "{http://www.w3.org/2000/svg}circle") if dot.get("data-pad")}
        self.assertEqual(fills, {"used": "#ffd34d", "free": "#c9a24b"})

    def test_no_pin_is_drawn_held(self):
        # held needs the board record's onboard roles, which the breadboard does not read yet (P950)
        for name, (text, layout) in {"xiao": xiao_svg(), "epaper": epaper_svg(), "record": record_svg()}.items():
            with self.subTest(name):
                states = pad_states(text, layout)
                self.assertGreaterEqual(len(states), 10)
                self.assertEqual(set(states.values()), {"used", "free"})
                self.assertNotIn("#5bc0eb", text)


class TheSheetShowsItTest(unittest.TestCase):
    def test_the_sheet_s_picture_is_the_file_written_beside_it(self):
        project = Path(tempfile.mkdtemp()) / "xiao"
        shutil.copytree(XIAO, project)
        with in_store():
            sheet.write(project / "requirements.json", project / "breadboard.md")
        link = re.search(r"!\[[^\]]*\]\(([^)]+)\)", (project / "breadboard.md").read_text()).group(1)
        self.assertTrue((project / link).is_file())

    def test_a_sheet_with_no_drawing_shows_no_picture(self):
        project = Path(tempfile.mkdtemp()) / "motor"
        shutil.copytree(MOTOR, project)
        (project / "breadboard.svg").write_text("<svg/>")
        with in_store():
            sheet.write(project / "requirements.json", project / "breadboard.md")
        self.assertNotIn("![", (project / "breadboard.md").read_text())
        self.assertIn("breadboard.json and breadboard.svg not written: ", (project / "breadboard.md").read_text())
        self.assertFalse((project / "breadboard.svg").exists())


if __name__ == "__main__":
    unittest.main()
