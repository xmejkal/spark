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

from spark.breadboard import drawing, part_pictures, sheet, svg_diagram, wiring_steps  # noqa: E402
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

    def test_it_is_turned_a_quarter_clockwise_never_mirrored_so_each_word_reads(self):
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
                         "b8486835247cd1610c0669bd7a8b174de67075d90a9da2531a5990ea9e43060f")

    def test_no_jumper_bends_on_a_hole(self):
        # The refuter (P268): a bend on a hole of another group looks like a joint that is not there.
        holes = [(hole.x, hole.y) for hole in drawing.WokwiGeometry.load().surface.holes]
        paths = [path for under, color, _ in wires(self.root) for path in (under, color)]
        self.assertEqual(len(paths), 2 * len(self.layout.jumpers))
        for path in paths:
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

        # each jumper has two paths on one route, the white under-stroke and its color (P947); the color one is read
        paths = [color for _, color, _ in wires(self.root)]
        self.assertEqual(len(paths), len(self.layout.jumpers))
        for path, jumper in zip(paths, self.layout.jumpers):
            numbers = [float(n) for n in re.findall(r"-?[\d.]+", path.get("d"))]
            self.assertAlmostEqual(numbers[0], center(jumper.one.name)[0], places=3)
            self.assertAlmostEqual(numbers[1], center(jumper.one.name)[1], places=3)
            self.assertAlmostEqual(numbers[-2], center(jumper.other.name)[0], places=3)
            self.assertAlmostEqual(numbers[-1], center(jumper.other.name)[1], places=3)
            self.assertEqual(path.get("stroke"), wiring_steps.JumperColors().of(
                {one.step: one.role for one in self.layout.jumpers})[jumper.step])

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
        board = self.layout.geometry.part(self.layout.parts[0].type)
        self.assertEqual(len(board["pins"]), 32)
        for pad in board["pins"]:
            self.assertEqual(self.texts.count(pad), 1, pad)

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
        self.assertEqual(self.texts.count(", ".join(note["sentence"] for note in board["notes"])), 1)

    def test_the_surface_has_63_columns_and_no_rail_lines(self):
        holes = re.findall(r"M[\d.]+ [\d.]+h0", [p.get("d") for p in self.root.findall("svg:path", NS)][0])
        self.assertEqual(len(holes), 630)
        self.assertEqual(len(self.root.findall("svg:line", NS)), 0)

    def test_the_same_layout_gives_the_same_bytes(self):
        self.assertEqual(self.text, svg_diagram.SvgBreadboardDiagram().text(self.layout))

    def test_the_picture_is_the_one_looked_at_on_2026_11_20(self):
        # rendered and looked at once (pad labels, rings, USB end, note); regenerate the hash only on purpose. P949: the keys,
        # and the dot of each pin used or free, seen in a render on 2026-11-20. P946: the FireBeetle drawn from the old
        # page's group (no glow), BAT on the RX edge, and no "row side not verified" in the note, seen in a render on 2026-11-20.
        self.assertEqual(hashlib.sha256(self.text.encode()).hexdigest(),
                         "1491e07b02d1ec947019c344f00517131c2edc5976eec7f72d0a4a64b6e63a5e")

    def test_the_board_is_drawn_from_its_record_s_picture_with_its_credit(self):
        board = next(group for group in self.root.findall("svg:g", NS) if group.get("data-part") == wiring_steps.THE_BOARD)
        self.assertTrue(any(rect.get("fill") == "#16202a" for rect in board.iter("{http://www.w3.org/2000/svg}rect")))
        self.assertIn("pixel-master/docs/wiring.html", board.find("svg:title", NS).text)

    def test_the_xiao_has_none_of_it(self):
        text, _ = xiao_svg()
        self.assertNotIn("#cfd8dc", text)
        self.assertNotIn("stroke-dasharray", text)


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
                self.assertTrue(label.get("transform").startswith("rotate(90 "), label.get("transform"))

    def test_a_label_of_a_bottom_edge_row_sits_above_its_pad(self):
        place = svg_diagram.IntoBodyLabels().place(50, 160, {"center": [100, 83]})
        self.assertEqual((place.y < 160, abs(place.x - 50) <= 4.8, place.anchor, place.rotate), (True, True, "end", 90))
        place = svg_diagram.IntoBodyLabels().place(50, 4.8, {"center": [100, 83]})
        self.assertEqual((place.y > 4.8, place.anchor), (True, "start"))

    def test_the_module_draws_no_usb_mark_and_the_board_keeps_its_one(self):
        marks = [rect for rect in self.root.iter("{http://www.w3.org/2000/svg}rect") if rect.get("fill") == "#cfd8dc"]
        self.assertEqual(len(marks), 1)

    def test_the_module_is_named_by_its_short_name(self):
        texts = [element.text for element in self.root.iter("{http://www.w3.org/2000/svg}text")]
        self.assertIn("e-paper", texts)
        self.assertNotIn("Epaper2in9BwrMhEtLive", texts)

    def test_the_canvas_holds_the_module_that_hangs_below_the_holes(self):
        bottom = self.module.top + self.part_px["size"][1]
        self.assertGreater(bottom, max(hole.y for hole in self.layout.geometry.surface.holes))
        self.assertGreaterEqual(float(self.root.get("height")), bottom + svg_diagram.SvgBreadboardDiagram.MARGIN_PX)


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


def number_boxes(root):
    """Each step number's box: 0.6 of the 9 px font wide per digit, 9 px high, above its baseline, from its x as its
    text-anchor places it."""
    boxes = []
    for text in root.iter("{http://www.w3.org/2000/svg}text"):
        if text.get("font-weight") == "bold" and (text.text or "").isdigit():
            x, y, width = float(text.get("x")), float(text.get("y")), 0.6 * 9 * len(text.text)
            left = x - width / 2 if text.get("text-anchor") == "middle" else x
            boxes.append((text.text, left, left + width, y - 9, y))
    return boxes


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
        self.assertEqual((colors[3], colors[8]), ("red", "black"))
        self.assertFalse({"red", "black"} & {colors[step] for step in colors if step not in (3, 8)})


class TheJumperLanesTest(unittest.TestCase):
    """P947: one lane per jumper, so no two jumpers share a drawn line and no step numbers overlap, on the walk's
    e-paper sheet and on every golden sheet with a picture."""

    @classmethod
    def setUpClass(cls):
        text, cls.layout = epaper_svg()
        cls.pictures = dict(golden_svgs(), epaper=text)

    def test_every_golden_sheet_with_a_picture_is_read(self):
        self.assertEqual(sorted(self.pictures), ["breadboard-ok-firebeetle.txt", "breadboard-ok-module.txt",
                                                 "breadboard-ok-rebuild.txt", "breadboard-ok-xiao.txt", "epaper"])

    def test_no_two_jumpers_share_a_drawn_line(self):
        for name, text in self.pictures.items():
            with self.subTest(name):
                drawn = [color for _, color, _ in wires(ElementTree.fromstring(text))]
                self.assertGreaterEqual(len(drawn), 2)
                self.assertEqual(shared_lines(drawn), [])

    def test_no_step_numbers_overlap(self):
        for name, text in self.pictures.items():
            with self.subTest(name):
                boxes = number_boxes(ElementTree.fromstring(text))
                self.assertGreaterEqual(len(boxes), 2)
                meeting = [(a[0], b[0]) for index, a in enumerate(boxes) for b in boxes[index + 1:]
                           if a[1] < b[2] and b[1] < a[2] and a[3] < b[4] and b[3] < a[4]]
                self.assertEqual(meeting, [])

    def test_each_run_lies_at_least_half_a_pitch_off_every_row_of_holes(self):
        rows = sorted({hole.y for hole in self.layout.geometry.surface.terminal})
        half = self.layout.geometry.surface.pitch / 2
        for (_, color, _) in wires(ElementTree.fromstring(self.pictures["epaper"])):
            runs = [y1 for (x1, y1), (x2, y2) in segments(color) if y1 == y2 and x1 != x2]
            for y in runs:
                self.assertGreaterEqual(min(abs(y - row) for row in rows), half - 0.01, y)

    def test_the_e_paper_s_eight_runs_take_eight_lines(self):
        runs = {segments(color)[1][0][1] for _, color, _ in wires(ElementTree.fromstring(self.pictures["epaper"]))}
        self.assertEqual(len(runs), 8)

    def test_overlapping_spans_take_lines_one_pitch_apart_toward_their_first_end_the_shorter_first(self):
        def hole(column, y):
            return drawing.Hole("%d" % column, 10 * column, y, "%d" % column, column)
        long_up = drawing.Jumper(hole(1, 150), hole(9, 50), 4)
        short_up = drawing.Jumper(hole(3, 150), hole(6, 50), 5)
        down = drawing.Jumper(hole(4, 50), hole(7, 150), 6)
        lines = svg_diagram.JumperLanes().lines([long_up, short_up, down], 10)
        self.assertEqual(lines, {5: 55, 4: 65, 6: 145})

    def test_spans_more_than_a_pitch_apart_share_a_line(self):
        def hole(column, y):
            return drawing.Hole("%d" % column, 10 * column, y, "%d" % column, column)
        lines = svg_diagram.JumperLanes().lines([drawing.Jumper(hole(1, 150), hole(3, 50), 1),
                                                 drawing.Jumper(hole(5, 150), hole(7, 50), 2)], 10)
        self.assertEqual(lines, {1: 55, 2: 55})

    def test_two_legs_never_share_a_column(self):
        # The review: jumpers 1a to 5j and 1j to 8a both have a leg in column 1; the second runs past the first one's end.
        def hole(column, y):
            return drawing.Hole("%d" % column, 10 * column, y, "%d" % column, column)
        jumpers = [drawing.Jumper(hole(1, 50), hole(5, 150), 1), drawing.Jumper(hole(1, 150), hole(8, 50), 2)]
        lines = svg_diagram.JumperLanes().lines(jumpers, 10)
        legs = [sorted((50, lines[1])), sorted((150, lines[2]))]
        self.assertLessEqual(min(legs[0][1], legs[1][1]) - max(legs[0][0], legs[1][0]), 0, lines)
        self.assertEqual(lines, {1: 145, 2: 155})

    def test_spans_less_than_a_pitch_apart_take_two_lines(self):
        def hole(column, y):
            return drawing.Hole("%d" % column, 10 * column, y, "%d" % column, column)
        lines = svg_diagram.JumperLanes().lines([drawing.Jumper(hole(1, 150), hole(3, 50), 1),
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
