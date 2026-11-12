"""
The mutation ledger's own logic (P787): a row's key holds its file, the blob hash is git's, a merge lets the newer date win
and adds the catches at one blob, and the store reads an empty or missing file as empty and writes sorted lines.

    python3 -m unittest tests.test_ledger
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import ledger  # noqa: E402

ROW = {"file": "m.py", "name": "add subtracts", "find": "return a + b", "replace": "return a - b"}
FIELDS = ["key", "file", "blob", "date", "status", "by", "caught", "s"]


def a_line(key="k", blob="b1", date="2026-11-12T10:00:00+01:00", status=ledger.CAUGHT, by="test_m", caught=1, s=5):
    return {"key": key, "file": "m.py", "blob": blob, "date": date, "status": status, "by": by, "caught": caught, "s": s}


class TheRowKeyTest(unittest.TestCase):
    def test_the_key_holds_the_file_so_one_defect_on_two_files_is_two_rows(self):
        # PR 0, row 2: 12 rows share a `find` and `replace` across files, and each guards another file.
        self.assertNotEqual(ledger.row_key(ROW), ledger.row_key(dict(ROW, file="n.py")))
        self.assertEqual(ledger.row_key(ROW), ledger.row_key(dict(ROW, name="another name")), "the name is not the identity")
        self.assertNotEqual(ledger.row_key(ROW), ledger.row_key(dict(ROW, replace="return a * b")))
        self.assertNotEqual(ledger.row_key({"file": "ab", "find": "c", "replace": ""}),
                            ledger.row_key({"file": "a", "find": "bc", "replace": ""}), "the parts are kept apart")
        self.assertRegex(ledger.row_key(ROW), r"^[0-9a-f]{12}$")

    def test_the_blob_is_git_s_hash_of_the_content(self):
        # `git hash-object` of "hello\n" and of nothing, so a copy without .git hashes as the tree does.
        self.assertEqual(ledger.blob_of(b"hello\n"), "ce013625030ba8dba906f756967f9e9ca394464a")
        self.assertEqual(ledger.blob_of(b""), "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391")

    def test_a_line_keeps_the_plan_s_order_and_counts_this_run_s_catch(self):
        line = ledger.line(ROW, "b1", "2026-11-12T10:00:00+01:00", ledger.CAUGHT, "test_m", 7)
        self.assertEqual(list(line), FIELDS)
        self.assertEqual((line["key"], line["caught"], line["s"]), (ledger.row_key(ROW), 1, 7))
        self.assertEqual(ledger.line(ROW, "b1", "d", ledger.ESCAPED, ledger.ESCAPE, 1)["caught"], 0)


class TheMergeTest(unittest.TestCase):
    def test_the_newer_date_wins_a_merge_and_on_the_same_date_the_fresh_line(self):
        older, newer = a_line(date="2026-11-12T10:00:00+01:00", by="old"), a_line(date="2026-11-12T11:00:00+01:00", by="new")
        self.assertEqual([entry["by"] for entry in ledger.merged([older], [newer])], ["new"])
        self.assertEqual([entry["by"] for entry in ledger.merged([newer], [older])], ["new"], "an older line never replaces a newer")
        self.assertEqual([entry["by"] for entry in ledger.merged([older], [dict(older, by="fresh")])], ["fresh"])
        # The dates carry their zone: 09:30 UTC is 10:30 in Prague, newer than 10:00+01:00.
        self.assertEqual([entry["by"] for entry in ledger.merged([older], [a_line(date="2026-11-12T09:30:00+00:00", by="utc")])], ["utc"])

    def test_catches_at_the_same_blob_add_up_and_a_changed_blob_starts_again(self):
        kept = a_line(blob="b1", caught=2, date="2026-11-12T10:00:00+01:00")
        same = a_line(blob="b1", caught=1, date="2026-11-12T11:00:00+01:00")
        self.assertEqual(ledger.merged([kept], [same])[0]["caught"], 3)
        self.assertEqual(ledger.merged([kept], [dict(same, blob="b2")])[0]["caught"], 1, "the file changed: the count starts again")
        self.assertEqual(ledger.merged([kept], [dict(same, status=ledger.ESCAPED, by=ledger.ESCAPE, caught=0)])[0]["caught"], 2,
                         "an escape adds no catch, and the line says escaped")

    def test_the_merge_is_sorted_by_key_and_keeps_lines_the_run_did_not_touch(self):
        self.assertEqual([entry["key"] for entry in ledger.merged([a_line(key="c"), a_line(key="a")], [a_line(key="b")])], ["a", "b", "c"])


class TheLedgerStoreTest(unittest.TestCase):
    def test_a_missing_or_empty_file_is_no_lines_and_the_store_writes_sorted_lines(self):
        path = Path(tempfile.mkdtemp()) / "mutations" / ledger.LEDGER_NAME
        store = ledger.LedgerStore(path)
        self.assertEqual((store.read(), store.counts()), ([], {}), "an empty ledger is empty, not seeded")
        path.parent.mkdir()
        path.write_text("")
        self.assertEqual(store.read(), [])
        written = store.record([a_line(key="b", status=ledger.ESCAPED), a_line(key="a")])
        self.assertEqual([entry["key"] for entry in written], ["a", "b"])
        self.assertEqual(path.read_text(), "".join(json.dumps(entry) + "\n" for entry in written))
        self.assertEqual(store.counts(), {ledger.CAUGHT: 1, ledger.ESCAPED: 1})
        store.record([a_line(key="a", date="2026-11-13T10:00:00+01:00", status=ledger.REFUSED, by=None, caught=0)])
        self.assertEqual([(entry["key"], entry["status"]) for entry in store.read()], [("a", ledger.REFUSED), ("b", ledger.ESCAPED)])

    def test_the_repository_s_ledger_is_sorted_json_lines_with_the_eight_fields(self):
        path = ROOT / "tests" / "mutations" / ledger.LEDGER_NAME
        self.assertTrue(path.is_file(), "%s is in git, empty until the first run" % path)
        lines = ledger.LedgerStore(path).read()
        self.assertEqual([list(entry) for entry in lines], [FIELDS] * len(lines))
        self.assertEqual([entry["key"] for entry in lines], sorted(entry["key"] for entry in lines))


if __name__ == "__main__":
    unittest.main()
