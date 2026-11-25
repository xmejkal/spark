"""
P877 (#1245): the rows spark keeps of the entries it wrote in requirements.json, `spark.design.entry_origin`: which entries are
named as written for a pick that is gone (the count rule), the reply key, and the record read as it is found.

    python3 -m unittest tests.test_entry_origin
"""

import json
import sys
import tempfile
import unittest
from collections import namedtuple
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from spark.core.errors import SparkError  # noqa: E402
from spark.design.entry_origin import EntryOriginStore, EntryRemoval, UnexplainedEntries, WrittenEntry, rows_present  # noqa: E402

#: What `need_requirements._merge_parts` gives `find`: the indexes a pick explains, `kept` for the rest, the rows it adds.
Merged = namedtuple("Merged", "explained kept written")
LED = "led"


def shown(entry):
    return {"part": entry if isinstance(entry, str) else entry["part"], "name": None if isinstance(entry, str) else entry.get("name")}


def found(existing, explained, rows, note=None, written=()):
    """The value for `existing` (a list of entries), the indexes a pick `explained` and the `rows` the record holds."""
    kept = [shown(entry) for number, entry in enumerate(existing) if number not in explained]
    return UnexplainedEntries.find(existing, Merged(set(explained), kept, list(written)), rows, note)


def indexes(value):
    return [each.index for each in value.removable]


class TheCountRuleTest(unittest.TestCase):
    def test_an_entry_a_row_holds_that_no_pick_explains_is_removable_with_its_need(self):
        value = found([LED], [], [WrittenEntry("light", LED)])
        self.assertEqual((indexes(value), value.removable[0].row.need, value.persons), ([0], "light", []))

    def test_an_entry_with_no_row_is_the_person_s(self):
        value = found([LED], [], [])
        self.assertEqual((indexes(value), value.persons), ([], [{"part": LED, "name": None}]))

    def test_an_entry_a_pick_explains_is_never_removable(self):
        self.assertEqual(indexes(found([LED], [0], [WrittenEntry("light", LED)])), [])

    def test_an_entry_the_person_changed_is_not_the_row_s(self):
        named = {"part": LED, "name": "Lamp"}
        self.assertEqual(indexes(found([named], [], [WrittenEntry("light", LED)])), [])

    def test_a_second_copy_by_hand_stays_when_a_pick_explains_the_first(self):
        # r = 1 row, k = 1 explained, u = 1 not: r - k = 0
        self.assertEqual(indexes(found([LED, LED], [0], [WrittenEntry("a", LED)])), [])

    def test_of_two_equal_entries_one_row_removes_the_last_and_two_rows_both(self):
        self.assertEqual(indexes(found([LED, LED], [], [WrittenEntry("a", LED)])), [1])
        self.assertEqual(indexes(found([LED, LED], [], [WrittenEntry("a", LED), WrittenEntry("b", LED)])), [0, 1])

    def test_the_persons_are_the_unexplained_entries_that_are_not_removable(self):
        value = found(["gone", "mine", "led"], [2], [WrittenEntry("light", "gone")])
        self.assertEqual((indexes(value), value.persons), ([0], [{"part": "mine", "name": None}]))

    def test_a_no_leaves_the_rows_of_the_removable_entries_out(self):
        rows = [WrittenEntry("light", "gone"), WrittenEntry("alarm", "kept")]
        value = found(["gone", "kept"], [1], rows)
        self.assertEqual(value.rows_left(), [WrittenEntry("alarm", "kept")])

    def test_a_yes_settles_the_file_and_the_rows_without_the_entries(self):
        value = found(["gone", "kept"], [1], [WrittenEntry("light", "gone"), WrittenEntry("alarm", "kept")])
        self.assertEqual(value.without_removable(["gone", "kept"]), (["kept"], [WrittenEntry("alarm", "kept")]))

    def test_the_data_names_the_part_the_name_the_need_and_the_code(self):
        value = found([{"part": "tactile-button", "name": "OpenLid"}], [], [WrittenEntry("open-lid", {"part": "tactile-button", "name": "OpenLid"})])
        self.assertEqual(value.to_dicts(), [{"part": "tactile-button", "name": "OpenLid", "need": "open-lid", "code": "entry_pick_gone"}])


class TheReplyKeyTest(unittest.TestCase):
    def setUp(self):
        self.value = found([LED], [], [WrittenEntry("light", LED)])

    def test_the_key_is_eight_hex_digits_after_the_prefix(self):
        self.assertRegex(self.value.key(b"bytes"), r"^requirements\.remove_entries\.[0-9a-f]{8}$")

    def test_other_bytes_or_other_entries_make_another_key(self):
        other = found(["x-led"], [], [WrittenEntry("light", "x-led")])
        self.assertEqual(self.value.key(b"bytes"), self.value.key(b"bytes"))
        self.assertNotEqual(self.value.key(b"bytes"), self.value.key(b"other bytes"))
        self.assertNotEqual(self.value.key(b"bytes"), other.key(b"bytes"))

    def test_no_removable_entry_holds_no_key(self):
        self.assertIsNone(found([LED], [0], [WrittenEntry("light", LED)]).key(b"bytes"))


class TheRecordTest(unittest.TestCase):
    def setUp(self):
        self.project = Path(tempfile.mkdtemp())
        self.record = EntryOriginStore(self.project)

    def write(self, text):
        self.record.path.parent.mkdir(parents=True)
        self.record.path.write_text(text)

    def test_what_is_saved_is_read_back_when_the_parts_are_the_same(self):
        self.record.save([LED], [WrittenEntry("light", LED)])
        self.assertEqual(self.record.rows_of([LED]), ([WrittenEntry("light", LED)], None))

    def test_other_parts_read_no_rows_and_say_so_when_there_were_rows(self):
        self.record.save([LED], [WrittenEntry("light", LED)])
        rows, note = self.record.rows_of([LED, "extra"])
        self.assertEqual((rows, note is not None), ([], True))

    def test_other_parts_with_no_rows_say_nothing(self):
        self.record.save([LED], [WrittenEntry("light", LED)])
        self.record.save([LED], [])
        self.assertEqual(self.record.rows_of(["extra"]), ([], None))

    def test_no_record_reads_no_rows_and_no_note(self):
        self.assertEqual((self.record.rows_of([LED]), self.record.path.exists()), (([], None), False))

    def test_a_save_with_no_rows_writes_a_record_that_reads_no_rows(self):
        # P1139: the record says "spark wrote no entry of these parts", so a later run can tell a hand edit (P1140)
        self.record.save([LED], [])
        self.assertEqual((self.record.path.exists(), self.record.rows_of([LED]), self.record.rows_of(["extra"])),
                         (True, ([], None), ([], None)))

    def test_a_record_of_any_other_shape_reads_no_rows_with_a_note_and_never_raises(self):
        for text in ("{not json", "[]", '{"written": 5}', '{"written": ["x"], "parts_sha256": "y"}', '{"written": [{"need": "a"}]}', ""):
            with self.subTest(text=text):
                self.record.path.unlink(missing_ok=True)
                self.write(text)
                rows, note = self.record.rows_of([LED])
                self.assertEqual((rows, note is not None), ([], True))
                self.record.path.unlink()
                self.record.path.parent.rmdir()

    def test_a_row_of_an_entry_the_file_no_longer_holds_is_dropped_one_row_for_each_equal_entry(self):
        rows = [WrittenEntry("a", LED), WrittenEntry("b", LED), WrittenEntry("c", "gone")]
        self.assertEqual(rows_present(rows, [LED, "other"]), [WrittenEntry("a", LED)])

    def test_the_record_holds_the_schema_the_hash_and_the_rows(self):
        self.record.save([LED], [WrittenEntry("light", LED)])
        held = json.loads(self.record.path.read_text())
        self.assertEqual((held["schema"], held["written"], len(held["parts_sha256"])), (1, [{"need": "light", "entry": LED}], 64))


class TheRepliesFileThatCannotBeReadTest(unittest.TestCase):
    """P935 PR 3: `EntryRemoval._load` says what it said when its fix was a constant of this file."""

    def test_an_unreadable_replies_file_is_a_bad_argument_with_this_operation_s_fix(self):
        with self.assertRaises(SparkError) as raised:
            EntryRemoval._load(Path(tempfile.mkdtemp()) / "no-such-replies.json")
        self.assertEqual((raised.exception.code, raised.exception.fix, raised.exception.status),
                         ("bad_argument", 'write the replies file as {"replies": {"<key>": true}} with the key of the run before, or leave out --replies', "could-not-run"))


if __name__ == "__main__":
    unittest.main()
