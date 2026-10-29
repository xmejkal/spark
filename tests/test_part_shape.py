"""
Proof that a part's shape is read from its record into mm, projected to the px the drawn breadboard plans with, and
that a board whose record lacks a fact or disagrees with itself is refused with a code (P412, epic P446).

    python3 -m unittest tests.test_part_shape
"""

import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import breadboard_drawing  # noqa: E402
import part_shape  # noqa: E402
import provenance  # noqa: E402

GEOMETRY = json.loads((ROOT / "data" / "wokwi-geometry.json").read_text())
RECORD = part_shape.RecordShapeSource()


def firebeetle():
    return json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())


def xiao():
    return json.loads((ROOT / "boards" / "xiao-esp32-c6.json").read_text())


def refusal(board):
    """(code, subject) of the refusal that RecordShapeSource gives the board."""
    with unittest.TestCase().assertRaises(breadboard_drawing.NotDrawn) as caught:
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
        self.assertEqual(part_px["source"], "record")
        self.assertEqual(part_px["doubtful"], ["GND1", "GND3"])

    def test_ground_is_the_one_pad_the_record_does_not_doubt(self):
        shape = RECORD.find_shape(firebeetle())
        self.assertEqual(shape.ground, "GND2")
        self.assertEqual(RECORD.pin_names(firebeetle())["GND"], "GND2")

    def test_a_pad_the_steps_print_under_an_alias_is_a_pad_of_the_shape(self):
        # the steps print MISO as MI (breadboard.printed_label), the label the shape's pad has
        self.assertEqual(RECORD.pin_names(firebeetle())["MI"], "MI")

    def test_each_fact_group_holds_under_the_provenance_rule(self):
        groups = RECORD.find_shape(firebeetle()).groups
        self.assertEqual(sorted(groups), ["doubtful_pads", "pads", "row_side"])
        for name, group in groups.items():
            with self.subTest(group=name):
                self.assertEqual(provenance.fact_problems(name, group), [])
        self.assertEqual([group["verified"] for group in groups.values()], [True, False, False])

    def test_the_unverified_groups_become_notes_in_order(self):
        notes = part_shape.project_to_px(RECORD.find_shape(firebeetle()))["notes"]
        self.assertEqual([note["group"] for note in notes], ["row_side", "doubtful_pads"])
        self.assertTrue(all(note["sentence"] and note["why"] for note in notes))


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
        self.assertEqual(refusal(board), ("header_disagrees", None))

    def test_a_pad_order_that_does_not_fit_the_pin_counts_disagrees(self):
        board = firebeetle()
        board["physical"]["header"]["pins"] = [18, 13]
        self.assertEqual(refusal(board), ("header_disagrees", None))

    def test_two_pads_with_one_label_are_refused_with_the_label(self):
        board = firebeetle()
        board["physical"]["header_order"]["row_14"][0] = "RX"
        self.assertEqual(refusal(board), ("duplicate_pad_label", "RX"))

    def test_a_record_without_doubtful_pads_is_refused(self):
        board = firebeetle()
        del board["physical"]["header"]["doubtful_pads"]
        self.assertEqual(refusal(board), ("no_doubtful_pad_fact", None))

    def test_two_grounds_left_is_not_one(self):
        board = firebeetle()
        board["physical"]["header"]["doubtful_pads"] = ["GND1"]
        self.assertEqual(refusal(board), ("ground_not_one", "GND2, GND3"))

    def test_no_ground_left_is_not_one(self):
        board = firebeetle()
        board["physical"]["header"]["doubtful_pads"] = ["GND1", "GND2", "GND3"]
        self.assertEqual(refusal(board), ("ground_not_one", None))

    def test_the_t_display_fixture_lacks_its_header(self):
        board = json.loads((ROOT / "tests" / "data" / "boards" / "lilygo-t-display.json").read_text())
        self.assertEqual(refusal(board)[0], "no_header_fact")

    def test_every_code_has_one_sentence(self):
        self.assertEqual(sorted(breadboard_drawing.CODES), sorted([
            "no_header_fact", "header_disagrees", "no_doubtful_pad_fact", "ground_not_one", "duplicate_pad_label",
            "no_hole_left", "no_wokwi_part"]))
        self.assertTrue(all(sentence and "\n" not in sentence for sentence in breadboard_drawing.CODES.values()))


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
        with self.assertRaises(breadboard_drawing.NotDrawn):
            part_shape.find_part_px(board, (part_shape.WokwiGeometryShapeSource(parts), RECORD))

    def test_the_order_decides(self):
        board = xiao()
        board["physical"]["header"]["doubtful_pads"] = []
        self.assertEqual(part_shape.find_part_px(board, (RECORD, part_shape.WokwiGeometryShapeSource()))[1], "record")
        self.assertEqual(part_shape.find_part_px(board)[1], "wokwi")


class EveryShapeSourceKeepsTheContractTest(unittest.TestCase):
    """The contract (T3): place_part gives None or a part_px, and pin_names maps only to pins of that part."""

    def test_both_sources_on_both_boards(self):
        for board in (xiao(), firebeetle()):
            for source in (part_shape.WokwiGeometryShapeSource(), RECORD):
                with self.subTest(board=board["id"], source=source.NAME):
                    try:
                        part_px = source.place_part(copy.deepcopy(board))
                    except breadboard_drawing.NotDrawn as refused:
                        self.assertEqual(refused.code, "no_doubtful_pad_fact")  # the XIAO's record does not say yet
                        continue
                    if part_px is None:
                        continue
                    for key in ("size", "center", "pins", "covers_holes"):
                        self.assertIn(key, part_px)
                    names = source.pin_names(board)
                    self.assertTrue(set(names.values()) <= set(part_px["pins"]), names)


if __name__ == "__main__":
    unittest.main()
