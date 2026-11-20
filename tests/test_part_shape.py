"""
Proof that a part's shape is read from its record into mm, projected to the px the drawn breadboard plans with, and
that a board whose record lacks a fact or disagrees with itself is refused with a code (P412, epic P446).

    python3 -m unittest tests.test_part_shape
"""

import ast
import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from spark.breadboard import drawing  # noqa: E402
from spark.breadboard import part_shape  # noqa: E402
from spark.records import provenance  # noqa: E402

GEOMETRY = json.loads((ROOT / "data" / "wokwi-geometry.json").read_text())
RECORD = part_shape.RecordShapeSource()


def firebeetle():
    return json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())


def xiao():
    return json.loads((ROOT / "boards" / "xiao-esp32-c6.json").read_text())


def refusal(board):
    """(code, subject) of the refusal that RecordShapeSource gives the board."""
    with unittest.TestCase().assertRaises(drawing.NotDrawnError) as caught:
        RECORD.find_shape(board)
    return caught.exception.code, caught.exception.subject


class TheShapeIsReadFromTheRecordTest(unittest.TestCase):
    def test_the_firebeetle_has_32_pins_in_a_25_4_by_60_mm_outline(self):
        shape = RECORD.find_shape(firebeetle())
        self.assertEqual(len(shape.pins), 32)
        self.assertEqual(shape.size, (25.4, 60.0))
        self.assertEqual(shape.pins["RX"], (1.27, 5.2))
        self.assertEqual(shape.pins["D10"], (24.13, 5.2))

    def test_projected_to_px_the_body_is_96_by_226_8_and_the_pins_keep_their_places(self):
        part_px = part_shape.project_to_px(RECORD.find_shape(firebeetle()))
        self.assertEqual(part_px["size"], [96.0, 226.772])
        self.assertEqual(part_px["center"], [48.0, 113.386])
        self.assertEqual(part_px["pins"]["RX"], [4.8, 19.654])
        self.assertEqual(part_px["pins"]["D10"], [91.2, 19.654])
        self.assertTrue(part_px["covers_holes"])
        self.assertEqual((part_px["source"], part_px["wokwi_part"], part_px["pad_labels"], part_px["full_surface"]),
                         ("record", False, True, True))
        self.assertEqual(part_px["doubtful"], ["GND1", "GND3"])

    def test_ground_is_the_one_pad_the_record_does_not_doubt(self):
        shape = RECORD.find_shape(firebeetle())
        self.assertEqual(shape.ground, "GND2")
        self.assertEqual(RECORD.find_pin_names(firebeetle())["GND"], "GND2")

    def test_a_step_to_a_doubtful_pad_finds_no_pin(self):
        names = RECORD.find_pin_names(firebeetle())
        self.assertEqual([pad for pad in ("GND1", "GND3") if pad in names], [])
        self.assertIn("GND1", RECORD.describe_part(firebeetle())["pins"])

    def test_a_pad_the_steps_print_under_an_alias_is_a_pad_of_the_shape(self):
        # the steps print MISO as MI (wiring_steps.printed_label), the label the shape's pad has
        self.assertEqual(RECORD.find_pin_names(firebeetle())["MI"], "MI")

    def test_each_fact_group_holds_under_the_provenance_rule(self):
        groups = RECORD.find_shape(firebeetle()).groups
        self.assertEqual(sorted(groups), ["doubtful_pads", "pads", "row_side", "usb_end"])
        for name, group in groups.items():
            with self.subTest(group=name):
                self.assertEqual(provenance.fact_problems(name, group), [])
        # P946: the row side is the PO's bench look (2026-11-20), the one group verified
        self.assertEqual({name: group["verified"] for name, group in groups.items()},
                         {"pads": False, "row_side": True, "usb_end": False, "doubtful_pads": False})
        self.assertIn("2026-11-20", groups["row_side"]["source"])

    def test_the_unverified_groups_become_notes_in_order(self):
        notes = part_shape.project_to_px(RECORD.find_shape(firebeetle()))["notes"]
        self.assertEqual([note["group"] for note in notes], ["pads", "usb_end", "doubtful_pads"])
        self.assertTrue(all(note["sentence"] and note["why"] for note in notes))

    def test_a_board_whose_record_says_nothing_of_its_row_side_keeps_the_convention_unverified(self):
        for held in (None, "row 0 on the left", {"value": "row 0 on the left", "verified": "yes", "source": "a look"},
                     {"value": "row 0 on the left", "verified": True, "source": ""}):
            with self.subTest(held=held):
                board = firebeetle()
                board["physical"]["header"]["row_side"] = held
                group = RECORD.find_shape(board).groups["row_side"]
                self.assertEqual((group["verified"], group["source"]),
                                 (False, "footprint_emitter.pads, which puts row 0 at -x"))

    def test_a_row_side_fact_that_is_not_the_drawing_s_refuses_the_board(self):
        for value in ("row 0 on the right", None):
            with self.subTest(value=value):
                board = firebeetle()
                board["physical"]["header"]["row_side"]["value"] = value
                self.assertEqual(refusal(board), ("header_disagrees", "physical.header.row_side"))


class ABoardWithSeveralGroundPadsIsDrawnTest(unittest.TestCase):
    """P955: the walk's FireBeetle 2 ESP32-C6 has two ground pads, GND1 and GND2, on one net (DFRobot's V1.1 schematic).
    The drawing wires the step word GND to the first ground pad of `power_pads` that is not doubtful."""

    def test_the_round0_c6_with_two_grounds_and_no_doubtful_pad_draws_with_gnd1_as_gnd(self):
        board = json.loads((ROOT / "tests" / "data" / "snapshot" / "round0-c6-record" / "boards" / "firebeetle2-esp32c6.json").read_text())
        board["physical"]["header"]["doubtful_pads"] = []  # in memory: test_snapshot reads the fixture as it is
        shape = RECORD.find_shape(board)
        self.assertEqual(shape.ground, "GND1")
        self.assertTrue({"GND1", "GND2"} <= set(shape.pins), sorted(shape.pins))
        self.assertNotIn("doubtful_pads", shape.groups)
        names = RECORD.find_pin_names(board)
        self.assertEqual((names["GND"], names["GND2"]), ("GND1", "GND2"))

    def test_two_grounds_left_draw_with_the_first_as_gnd(self):  # was test_two_grounds_left_is_not_one (P412's refusal)
        board = firebeetle()
        board["physical"]["header"]["doubtful_pads"] = ["GND1"]
        self.assertEqual(RECORD.find_shape(board).ground, "GND2")
        names = RECORD.find_pin_names(board)
        self.assertEqual((names["GND"], names["GND3"]), ("GND2", "GND3"))


class ABoardThatCannotBeDrawnIsRefusedWithACodeTest(unittest.TestCase):
    def test_a_record_with_no_header_names_the_field(self):
        board = firebeetle()
        del board["physical"]["header"]
        self.assertEqual(refusal(board), ("no_header_fact", "physical.header"))

    def test_a_missing_outline_field_is_the_subject(self):
        board = firebeetle()
        del board["physical"]["height_mm"]
        self.assertEqual(refusal(board), ("no_header_fact", "physical.height_mm"))

    def test_a_value_of_the_wrong_kind_disagrees(self):
        board = firebeetle()
        board["physical"]["header"]["pitch_mm"] = "2.54"
        self.assertEqual(refusal(board), ("header_disagrees", "physical.header.pitch_mm"))

    def test_a_number_too_big_for_a_float_disagrees_instead_of_crashing(self):
        board = firebeetle()
        board["physical"]["width_mm"] = 10 ** 400
        self.assertEqual(refusal(board), ("header_disagrees", "physical.width_mm"))

    def test_a_header_the_pad_code_cannot_place_names_the_field(self):
        for field, value in (("flush_edge", "-y"), ("rows", 3), ("pitch_mm", 0), ("pins", [18, 14, 2])):
            with self.subTest(field=field):
                board = firebeetle()
                board["physical"]["header"][field] = value
                if field == "pins":
                    board["physical"]["header"]["rows"] = 3
                    board["physical"]["header_order"]["row_2"] = ["X", "Y"]
                self.assertEqual(refusal(board)[0], "header_disagrees")
                self.assertEqual(refusal(board)[1].split(".")[-1], "pins" if field == "pins" else field)

    def test_a_missing_flush_edge_is_refused_too(self):
        board = firebeetle()
        del board["physical"]["header"]["flush_edge"]
        self.assertEqual(refusal(board), ("header_disagrees", "physical.header.flush_edge"))

    def test_a_size_that_is_not_a_finite_number_above_nothing_names_its_field(self):
        nan, inf = float("nan"), float("inf")
        for path, value in (("header.row_spacing_mm", -22.86), ("header.row_spacing_mm", 0), ("header.row_spacing_mm", nan),
                            ("header.first_pad_from_edge_mm", -50), ("header.pitch_mm", inf), ("header.pitch_mm", -2.54),
                            ("width_mm", -25.4), ("width_mm", 0), ("height_mm", -60.0), ("header.pitch_mm", 0)):
            with self.subTest(field=path, value=value):
                board = firebeetle()
                *where, field = path.split(".")
                node = board["physical"][where[0]] if where else board["physical"]
                node[field] = value
                code, subject = refusal(board)
                self.assertEqual((code, subject), ("header_disagrees", "physical." + path))

    def test_rows_must_be_a_whole_number_and_not_a_flag(self):
        board = firebeetle()
        board["physical"]["header"]["rows"] = True
        board["physical"]["header"]["pins"] = [18]
        del board["physical"]["header_order"]["row_14"]
        self.assertEqual(refusal(board), ("header_disagrees", "physical.header.rows"))

    def test_a_pad_outside_the_outline_names_the_field_that_puts_it_out(self):
        for field, value, named in (("row_spacing_mm", 40.0, "row_spacing_mm"), ("first_pad_from_edge_mm", 61.0, "first_pad_from_edge_mm"),
                                    ("pitch_mm", 4.0, "pitch_mm"), ("height_mm", 1.0, "first_pad_from_edge_mm")):
            with self.subTest(field=field, value=value):
                board = firebeetle()
                (board["physical"] if field == "height_mm" else board["physical"]["header"])[field] = value
                self.assertEqual(refusal(board), ("header_disagrees", "physical.header." + named))

    def test_pads_that_meet_name_the_dimension_that_makes_them_meet(self):
        for field, value in (("pitch_mm", 1e-9), ("row_spacing_mm", 1e-9), ("pitch_mm", 1e308)):
            with self.subTest(field=field, value=value):
                board = firebeetle()
                board["physical"]["header"][field] = value
                self.assertEqual(refusal(board), ("header_disagrees", "physical.header." + field))

    def test_a_pad_order_that_does_not_fit_the_pin_counts_disagrees(self):
        board = firebeetle()
        board["physical"]["header"]["pins"] = [18, 13]
        self.assertEqual(refusal(board), ("header_disagrees", "physical.header.pins"))

    def test_two_pads_with_one_label_are_refused_with_the_label(self):
        board = firebeetle()
        board["physical"]["header_order"]["row_14"][0] = "RX"
        self.assertEqual(refusal(board), ("duplicate_pad_label", "RX"))

    def test_a_record_without_doubtful_pads_is_refused(self):
        board = firebeetle()
        del board["physical"]["header"]["doubtful_pads"]
        self.assertEqual(refusal(board), ("no_doubtful_pad_fact", None))

    def test_a_null_doubtful_pads_is_refused_and_the_refusal_says_to_write_an_empty_list_after_checking(self):  # P955
        board = firebeetle()
        board["physical"]["header"]["doubtful_pads"] = None
        with self.assertRaises(drawing.NotDrawnError) as caught:
            RECORD.find_shape(board)
        self.assertEqual((caught.exception.code, caught.exception.subject), ("no_doubtful_pad_fact", None))
        self.assertIn("write [] when none is doubtful, after checking", str(caught.exception))

    def test_a_ground_pad_that_is_no_header_pad_is_refused(self):  # P955
        board = firebeetle()
        board["power_pads"]["GND9"] = {"rail": "ground", "direction": "out"}
        self.assertEqual(refusal(board), ("ground_not_one", "GND2, GND9"))

    def test_no_ground_left_is_not_one(self):
        board = firebeetle()
        board["physical"]["header"]["doubtful_pads"] = ["GND1", "GND2", "GND3"]
        self.assertEqual(refusal(board), ("ground_not_one", None))

    def test_the_t_display_fixture_lacks_its_header(self):
        board = json.loads((ROOT / "tests" / "data" / "boards" / "lilygo-t-display.json").read_text())
        self.assertEqual(refusal(board)[0], "no_header_fact")

    def test_every_code_has_one_sentence(self):
        self.assertEqual(sorted(drawing.CODES), sorted([
            "no_header_fact", "header_disagrees", "no_doubtful_pad_fact", "ground_not_one", "duplicate_pad_label",
            "no_hole_left", "no_wokwi_part", "no_pin_position", "no_drawing_fact", "no_wokwi_pin", "row_full",
            "not_drawn_yet", "planner_fault"]))
        self.assertTrue(all(sentence and "\n" not in sentence for sentence in drawing.CODES.values()))

    def test_every_not_drawn_raise_names_a_code(self):
        """P691: no NotDrawnError under scripts/spark/ is made without a code, so an agent decides on the code."""
        uncoded = []
        for module in sorted((ROOT / "scripts" / "spark").rglob("*.py")):
            for node in ast.walk(ast.parse(module.read_text())):
                name = getattr(node, "func", None)
                name = getattr(name, "attr", None) or getattr(name, "id", None)
                if not (isinstance(node, ast.Call) and name == "NotDrawnError"):
                    continue
                code = node.args[1] if len(node.args) > 1 else next(
                    (keyword.value for keyword in node.keywords if keyword.arg == "code"), None)
                if code is None or (isinstance(code, ast.Constant) and code.value is None):
                    uncoded.append("%s:%d" % (module.relative_to(ROOT), node.lineno))
        self.assertEqual(uncoded, [])

    def test_a_refusal_made_without_a_code_is_a_type_error(self):
        """P783: `code` is required, so a NotDrawnError made with its message alone fails where it is made."""
        with self.assertRaises(TypeError):
            drawing.NotDrawnError("no room")

    def test_a_board_no_source_describes_has_a_code(self):
        with self.assertRaises(drawing.NotDrawnError) as refused:
            part_shape.find_source({"id": "board-x"}, ())
        self.assertEqual((refused.exception.code, refused.exception.subject), ("no_drawing_fact", "board-x"))


MODULE = part_shape.ModuleShapeSource()


def epaper():
    """The walk's e-paper record, with its physical block: the header on the back, 8 pins, the first 34.5 mm from the
    left edge seen from the back (P945)."""
    return json.loads((ROOT / "tests" / "data" / "breadboard" / "epaper" / "parts" / "epaper-2in9-bwr-mh-et-live.json").read_text())


def module_refusal(record):
    """(code, subject) of the refusal that ModuleShapeSource gives the record."""
    with unittest.TestCase().assertRaises(drawing.NotDrawnError) as caught:
        MODULE.find_shape(record)
    return caught.exception.code, caught.exception.subject


class AModuleIsDrawnFromItsPhysicalBlockTest(unittest.TestCase):
    """P945: one row of header pins along the module's top edge, seen from above as it sits in the breadboard."""

    def test_eight_pads_sit_one_pitch_apart_on_one_row_half_a_pitch_from_the_edge(self):
        shape = MODULE.find_shape(epaper())
        self.assertEqual(shape.size, (85, 44))
        self.assertEqual(len(shape.pins), 8)
        self.assertEqual({y for _, y in shape.pins.values()}, {1.27})
        xs = sorted(x for x, _ in shape.pins.values())
        self.assertEqual({round(right - left, 4) for left, right in zip(xs, xs[1:])}, {2.54})

    def test_a_header_on_the_back_reads_mirrored_from_above(self):
        pins = MODULE.find_shape(epaper()).pins
        self.assertEqual(pins["VCC"], (50.5, 1.27))
        self.assertEqual(pins["Busy"], (32.72, 1.27))
        self.assertEqual(sorted(pins, key=lambda label: pins[label][0]),
                         ["Busy", "Reset", "D/C", "CS", "SCLK", "SDI", "GND", "VCC"])

    def test_a_header_on_the_front_keeps_the_order(self):
        record = epaper()
        record["physical"]["header"]["face"] = "front"
        pins = MODULE.find_shape(record).pins
        self.assertEqual(pins["VCC"], (34.5, 1.27))
        self.assertEqual(sorted(pins, key=lambda label: pins[label][0]),
                         ["VCC", "GND", "SDI", "SCLK", "CS", "D/C", "Reset", "Busy"])
        self.assertNotIn("face", MODULE.find_shape(record).groups)

    def test_a_row_counted_from_the_right_edge_starts_there(self):
        record = epaper()
        record["physical"]["header"].update(flush_edge="+x", face="front")
        pins = MODULE.find_shape(record).pins
        self.assertEqual(pins["VCC"], (50.5, 1.27))
        self.assertEqual(pins["GND"], (47.96, 1.27))

    def test_each_missing_field_is_refused_by_its_name(self):
        for field in ("body_mm.width", "body_mm.height", "pin_order", "physical.header.rows", "physical.header.pins",
                      "physical.header.pitch_mm", "physical.header.flush_edge", "physical.header.first_pad_from_edge_mm",
                      "physical.header.face"):
            record = epaper()
            *path, last = field.split(".")
            block = record
            for key in path:
                block = block[key]
            del block[last]
            with self.subTest(field=field):
                self.assertEqual(module_refusal(record), ("no_header_fact", field))

    def test_two_rows_are_refused_by_rows(self):
        record = epaper()
        record["physical"]["header"].update(rows=2, pins=[4, 4])
        self.assertEqual(module_refusal(record), ("header_disagrees", "physical.header.rows"))

    def test_a_pin_count_that_is_not_the_pin_order_s_is_refused_by_pins(self):
        record = epaper()
        record["physical"]["header"]["pins"] = [7]
        self.assertEqual(module_refusal(record), ("header_disagrees", "physical.header.pins"))

    def test_an_unknown_face_or_edge_is_refused_by_its_field(self):
        for field, value in (("face", "top"), ("face", ["back"]), ("flush_edge", "+y"), ("flush_edge", ["-x"])):
            record = epaper()
            record["physical"]["header"][field] = value
            with self.subTest(field=field, value=value):
                self.assertEqual(module_refusal(record), ("header_disagrees", "physical.header." + field))

    def test_a_size_that_is_not_a_finite_number_above_nothing_names_its_field(self):
        for field, value in (("pitch_mm", 0), ("first_pad_from_edge_mm", -1), ("pitch_mm", float("nan")), ("pitch_mm", True)):
            record = epaper()
            record["physical"]["header"][field] = value
            with self.subTest(field=field, value=value):
                self.assertEqual(module_refusal(record), ("header_disagrees", "physical.header." + field))

    def test_a_pad_outside_the_body_is_refused_by_first_pad_from_edge_mm(self):
        record = epaper()
        record["physical"]["header"]["first_pad_from_edge_mm"] = 70
        self.assertEqual(module_refusal(record), ("header_disagrees", "physical.header.first_pad_from_edge_mm"))

    def test_a_record_with_no_physical_block_is_declined(self):
        record = epaper()
        del record["physical"]
        self.assertIsNone(MODULE.find_shape(record))
        self.assertIsNone(MODULE.describe_part(record))

    def test_a_module_s_part_px_has_no_usb_mark_and_its_labels_go_into_the_body(self):
        part_px = MODULE.describe_part(epaper())
        self.assertEqual((part_px["usb_mark"], part_px["labels"], part_px["full_surface"]), (False, "into-body", False))
        self.assertEqual((part_px["ground"], part_px["doubtful"], part_px["covers_holes"]), (None, [], True))
        self.assertEqual([note["sentence"] for note in part_px["notes"]],
                         ["e-paper pads not verified", "e-paper header side not verified"])

    def test_the_board_keeps_its_usb_mark_and_its_labels_beside_the_pads(self):
        part_px = RECORD.describe_part(firebeetle())
        self.assertEqual((part_px["usb_mark"], part_px["labels"], part_px["full_surface"]), (True, "beside", True))

    def test_the_printed_spellings_name_the_pads_and_the_steps_pins_find_them(self):
        self.assertIn("D/C", MODULE.find_shape(epaper()).pins)
        self.assertEqual(MODULE.find_pin_names(epaper()), {
            "VCC": "VCC", "GND": "GND", "SDI": "SDI", "SCLK": "SCLK", "CS": "CS", "DC": "D/C", "RESET": "Reset",
            "BUSY": "Busy"})

    def test_two_pins_printed_alike_are_refused_with_the_label(self):
        record = epaper()
        sclk = next(need for need in record["needs"] if need["pin"] == "SCLK")
        sclk["printed"] = "CS"
        self.assertEqual(module_refusal(record), ("duplicate_pad_label", "CS"))

    def test_a_pad_with_no_pin_in_pin_order_is_refused_by_pin_order(self):
        # the contract allows a null pad (nothing on it); one null and two nulls are both named by the field
        for nulls in ([3], [3, 5]):
            record = epaper()
            for index in nulls:
                record["pin_order"][index] = None
            with self.subTest(nulls=nulls):
                self.assertEqual(module_refusal(record), ("no_header_fact", "pin_order"))

    def test_the_placer_is_given_by_injection(self):
        class EveryPadAtOnePlace(part_shape.OneRowHeaderPlacer):
            def place(self, header, size, labels):
                return [(label, 1, 1) for label in labels]

        pins = part_shape.ModuleShapeSource(EveryPadAtOnePlace()).find_shape(epaper()).pins
        self.assertEqual(set(pins.values()), {(1, 1)})


class TheGuideNamesEveryCodeTest(unittest.TestCase):
    def test_agents_md_names_every_code_and_the_kept_fields(self):
        guide = ROOT / "docs" / "guide"
        text = "".join(page.read_text() for page in [guide / "agents.md"] + sorted((guide / "agents").glob("*.md")))
        self.assertEqual([code for code in drawing.CODES if "`%s`" % code not in text], [])
        for field in ("code", "subject", "expected", "drawn_from", "fix", "record"):
            self.assertIn("`%s`" % field, text)


class TheSourcesAreAskedInOrderTest(unittest.TestCase):
    def test_the_xiao_stays_on_the_wokwi_source_and_its_px_are_the_measured_ones(self):
        part_px, name = part_shape.find_part_px(xiao())
        self.assertEqual(name, "wokwi")
        self.assertEqual(part_px, GEOMETRY["parts"]["board-xiao-esp32-c6"])
        self.assertNotIn("source", part_px)

    def test_a_board_with_no_flag_counts_as_no_stand_in(self):
        board = xiao()
        board.pop("wokwi_is_stand_in", None)
        self.assertEqual(part_shape.find_part_px(board)[1], "wokwi")

    def test_a_stand_in_with_a_wokwi_entry_loses_to_a_complete_record(self):
        board = firebeetle()
        parts = {board["wokwi_part_type"]: GEOMETRY["parts"]["board-xiao-esp32-c6"]}
        sources = (part_shape.WokwiGeometryShapeSource(parts), RECORD)
        self.assertEqual(part_shape.find_part_px(board, sources)[1], "record")
        board["wokwi_is_stand_in"] = False
        self.assertEqual(part_shape.find_part_px(board, sources)[1], "wokwi")

    def test_a_stand_in_never_shows_the_wrong_board_when_the_record_is_not_complete(self):
        board = firebeetle()
        del board["physical"]["header"]
        parts = {board["wokwi_part_type"]: GEOMETRY["parts"]["board-xiao-esp32-c6"]}
        with self.assertRaises(drawing.NotDrawnError):
            part_shape.find_part_px(board, (part_shape.WokwiGeometryShapeSource(parts), RECORD))

    def test_a_wokwi_board_names_pins_only_when_its_wokwi_pins_are_the_printed_labels(self):
        parts = {"board-x": {"size": [1, 1], "center": [0, 0], "covers_holes": True, "pins": {"D0": [0, 0], "D1": [1, 1]}}}
        source = part_shape.WokwiGeometryShapeSource(parts)
        board = {"wokwi_part_type": "board-x", "wokwi_pin_naming": "silkscreen"}
        self.assertEqual(source.find_pin_names(board), {"D0": "D0", "D1": "D1"})
        self.assertEqual(source.find_pin_names(dict(board, wokwi_pin_naming="gpio")), {})
        self.assertEqual(source.find_pin_names({"wokwi_part_type": "board-x"}), {})
        self.assertEqual(source.find_pin_names({"wokwi_part_type": "board-none", "wokwi_pin_naming": "silkscreen"}), {})

    def test_the_order_decides(self):
        board = xiao()
        board["physical"]["header"]["doubtful_pads"] = []
        self.assertEqual(part_shape.find_part_px(board, (RECORD, part_shape.WokwiGeometryShapeSource()))[1], "record")
        self.assertEqual(part_shape.find_part_px(board)[1], "wokwi")


class EveryShapeSourceKeepsTheContractTest(unittest.TestCase):
    """The contract (T3): describe_part gives None or a part_px, and find_pin_names maps only to pins of that part."""

    def test_both_sources_on_both_boards(self):
        for board in (xiao(), firebeetle()):
            for source in (part_shape.WokwiGeometryShapeSource(), RECORD):
                with self.subTest(board=board["id"], source=source.NAME):
                    try:
                        part_px = source.describe_part(copy.deepcopy(board))
                    except drawing.NotDrawnError as refused:
                        self.assertEqual(refused.code, "no_doubtful_pad_fact")  # the XIAO's record does not say yet
                        continue
                    if part_px is None:
                        continue
                    for key in ("size", "center", "pins", "covers_holes"):
                        self.assertIn(key, part_px)
                    names = source.find_pin_names(board)
                    self.assertTrue(set(names.values()) <= set(part_px["pins"]), names)


if __name__ == "__main__":
    unittest.main()
