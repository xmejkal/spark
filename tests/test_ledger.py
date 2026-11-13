"""
The mutation ledger's own logic (P787): a row's key holds its file, the blob hash is git's, a merge lets the newer date win
and adds the catches and the refusals at one blob, the store reads an empty or missing file as empty and writes sorted
lines, and a row's tier is read from its line and its file's blob (PR 2); the repository's critical marks stay under the
PO's cap and name files that exist (PR 4); a row refused twice at its file's current blob is retired, listed and never
new again (PR 5).

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
FIELDS = ["key", "file", "blob", "date", "status", "by", "caught", "refused", "s"]
#: At most this many rows carry `"tier": "critical"`: the PO's number (P787's plan, approved 2026-11-12), so the rows that
#: run every sweep stay few, and a mark is a choice, never a default.
CRITICAL_CAP = 40
TABLES = sorted((ROOT / "tests" / "mutations").glob("*.json"))


def a_line(key="k", blob="b1", date="2026-11-12T10:00:00+01:00", status=ledger.CAUGHT, by="test_m", caught=1, refused=0, s=5):
    return {"key": key, "file": "m.py", "blob": blob, "date": date, "status": status, "by": by, "caught": caught, "refused": refused, "s": s}


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
        self.assertEqual((line["key"], line["caught"], line["refused"], line["s"]), (ledger.row_key(ROW), 1, 0, 7))
        self.assertEqual(ledger.line(ROW, "b1", "d", ledger.ESCAPED, ledger.ESCAPE, 1)["caught"], 0)
        refused = ledger.line(ROW, "b1", "d", ledger.REFUSED, None, 0)
        self.assertEqual((refused["caught"], refused["refused"]), (0, 1), "a refusal counts as one, as a catch does")


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

    def test_refusals_at_the_same_blob_add_up_as_catches_do_and_a_changed_blob_starts_again(self):
        # PR 5: "refused in two sweeps" is a count across runs, kept by the ledger as `caught` is.
        kept = a_line(blob="b1", status=ledger.REFUSED, by=None, caught=1, refused=1, date="2026-11-12T10:00:00+01:00")
        same = a_line(blob="b1", status=ledger.REFUSED, by=None, caught=0, refused=1, date="2026-11-12T11:00:00+01:00")
        merged = ledger.merged([kept], [same])[0]
        self.assertEqual((merged["status"], merged["caught"], merged["refused"]), (ledger.REFUSED, 1, 2), "the catch count is kept too (row 49)")
        self.assertEqual(ledger.merged([kept], [dict(same, blob="b2")])[0]["refused"], 1, "the file changed: the count starts again")

    def test_an_eight_field_line_from_before_the_refused_count_merges_and_tiers_without_a_crash(self):
        # The refuter of PR 5: a sweep on main writes eight-field lines until this merges; they read as no refusal.
        old = a_line(blob="b1", status=ledger.REFUSED, by=None, caught=0)
        del old["refused"]
        fresh = a_line(blob="b1", status=ledger.REFUSED, by=None, caught=0, refused=1, date="2026-11-12T11:00:00+01:00")
        self.assertEqual(ledger.merged([old], [fresh])[0]["refused"], 1, "the old line counts no refusal")
        self.assertFalse(ledger.is_retired(old, "b1"))
        self.assertEqual(ledger.tier_of(ROW, old, "b1"), ledger.NEW)

    def test_the_merge_is_sorted_by_key_and_keeps_lines_the_run_did_not_touch(self):
        self.assertEqual([entry["key"] for entry in ledger.merged([a_line(key="c"), a_line(key="a")], [a_line(key="b")])], ["a", "b", "c"])


class TheTiersTest(unittest.TestCase):
    """P787 PR 2: a tier is a fact read from the row, its ledger line and its file's current blob; nothing is guessed."""

    def test_the_four_tiers_are_read_from_the_row_the_line_and_the_blob(self):
        self.assertEqual(ledger.tier_of(ROW, None, "b1"), ledger.NEW, "no line: never run")
        self.assertEqual(ledger.tier_of(ROW, a_line(blob="b0", caught=5), "b1"), ledger.NEW, "the file changed since: the blob rule alone")
        self.assertEqual(ledger.tier_of(ROW, a_line(blob="b1", caught=1), "b1"), ledger.PROVING)
        self.assertEqual(ledger.tier_of(ROW, a_line(blob="b1", caught=2), "b1"), ledger.PROVEN)
        self.assertEqual(ledger.tier_of(ROW, a_line(blob="b1", caught=3), "b1"), ledger.PROVEN)
        self.assertEqual(ledger.tier_of(dict(ROW, tier="critical"), a_line(blob="b1", caught=3), "b1"), ledger.CRITICAL,
                         "the row's own key, whatever the ledger says")
        self.assertEqual(ledger.tier_of(ROW, a_line(blob="b1", caught=5), None), ledger.NEW, "a file that is not there has no blob")
        self.assertEqual(ledger.tier_of(ROW, a_line(blob=None, caught=2), None), ledger.NEW,
                         "a hand-written line with no blob meets a gone file: still new, never proven (the refuter of PR 2)")
        self.assertEqual(ledger.TIERS, ("critical", "new", "proving", "proven"), "the tiers a sweep runs, in its order")
        self.assertEqual(ledger.TIER_WORDS, ("critical", "new", "proving", "proven", "retired"))

    def test_an_escaped_or_once_refused_line_at_the_current_blob_is_new_again(self):
        # Row 49: a refused line keeps its count from the same blob (`merged` adds 0), so status and count are read together.
        self.assertEqual(ledger.tier_of(ROW, a_line(blob="b1", status=ledger.ESCAPED, by=ledger.ESCAPE, caught=2), "b1"), ledger.NEW)
        self.assertEqual(ledger.tier_of(ROW, a_line(blob="b1", status=ledger.REFUSED, by=None, caught=2, refused=1), "b1"), ledger.NEW)

    def test_the_selection_runs_critical_then_new_in_the_tables_order_then_proving_then_proven_oldest_first(self):
        root = Path(tempfile.mkdtemp())
        (root / "m.py").write_text("x\n")
        blob = ledger.blob_of(b"x\n")
        rows = [dict(ROW, name=name, find=name) for name in ("proven-late", "new-1", "proving", "proven-early", "new-2")]
        critical = dict(ROW, name="critical", find="critical", tier="critical")
        rows.insert(3, critical)
        lines = [a_line(key=ledger.row_key(rows[0]), blob=blob, caught=2, date="2026-11-12T10:00:00+01:00"),
                 a_line(key=ledger.row_key(rows[2]), blob=blob, caught=1),
                 a_line(key=ledger.row_key(rows[4]), blob=blob, caught=4, date="2026-11-01T10:00:00+01:00"),
                 a_line(key=ledger.row_key(critical), blob=blob, caught=2)]
        tiers = ledger.tiers_of(root, rows, lines)
        self.assertEqual(tiers.counts(), {"critical": 1, "new": 2, "proving": 1, "proven": 2, "retired": 0})
        self.assertEqual([row["name"] for row in tiers.selected(ledger.TIERS)],
                         ["critical", "new-1", "new-2", "proving", "proven-early", "proven-late"])
        self.assertEqual([row["name"] for row in tiers.selected(["proven", "new"])], ["new-1", "new-2", "proven-early", "proven-late"],
                         "the sweep's order, not the caller's")
        self.assertEqual(tiers.selected([]), [])
        self.assertEqual(ledger.tiers_of(root, rows, []).counts(), {"critical": 1, "new": 5, "proving": 0, "proven": 0, "retired": 0},
                         "an empty ledger makes every row new but the critical one")


class TheRetiredRowsTest(unittest.TestCase):
    """P787 PR 5: a row refused in two sweeps at its file's current blob is retired: listed for a deleting PR, never new again."""

    def refused(self, blob="b1", refused=2, **more):
        return a_line(blob=blob, status=ledger.REFUSED, by=None, caught=0, refused=refused, **more)

    def test_a_row_refused_twice_at_the_current_blob_is_retired_and_once_is_not(self):
        self.assertTrue(ledger.is_retired(self.refused(refused=2), "b1"))
        self.assertTrue(ledger.is_retired(self.refused(refused=3), "b1"))
        self.assertFalse(ledger.is_retired(self.refused(refused=1), "b1"), "one refusal: --anchors' business, the row is new")
        self.assertFalse(ledger.is_retired(None, "b1"), "no line: never run")
        self.assertEqual(ledger.RETIRED_AT, 2, "the plan: refused in two sweeps")

    def test_a_row_refused_twice_at_an_older_blob_is_not_retired(self):
        # The blob rule: the file changed since, and the anchor may be back; the next sweep refuses it again, or not.
        self.assertFalse(ledger.is_retired(self.refused(blob="b0", refused=2), "b1"))
        self.assertFalse(ledger.is_retired(self.refused(blob="b1", refused=5), None), "the file is gone since the refusals")
        self.assertTrue(ledger.is_retired(self.refused(blob=None, refused=2), None), "gone then and gone now: the same content, none")

    def test_an_escape_or_a_catch_never_retires_whatever_the_refusal_count_says(self):
        # W3: an escape is a missing test. A catch at this blob says the row works now: the last word decides.
        self.assertFalse(ledger.is_retired(a_line(blob="b1", status=ledger.ESCAPED, by=ledger.ESCAPE, caught=0, refused=2), "b1"))
        self.assertFalse(ledger.is_retired(a_line(blob="b1", status=ledger.CAUGHT, caught=1, refused=2), "b1"))

    def test_a_retired_row_is_in_the_retired_tier_and_no_sweep_selects_it(self):
        self.assertEqual(ledger.tier_of(ROW, self.refused(), "b1"), ledger.RETIRED)
        self.assertEqual(ledger.tier_of(dict(ROW, tier="critical"), self.refused(), "b1"), ledger.CRITICAL,
                         "the row's own key first: a critical row runs every sweep until the PR deletes or re-anchors it")
        root = Path(tempfile.mkdtemp())
        (root / "m.py").write_text("x\n")
        blob = ledger.blob_of(b"x\n")
        retired, fresh = dict(ROW, name="retired", find="gone"), dict(ROW, name="fresh", find="x")
        tiers = ledger.tiers_of(root, [retired, fresh], [self.refused(key=ledger.row_key(retired), blob=blob)])
        self.assertEqual(tiers.counts(), {"critical": 0, "new": 1, "proving": 0, "proven": 0, "retired": 1})
        self.assertEqual([row["name"] for row in tiers.selected(ledger.TIERS)], ["fresh"], "a retired row is not new: not planted again")
        self.assertEqual(tiers.selected([ledger.RETIRED]), [], "and naming the word selects nothing: --retire lists, a PR deletes")
        self.assertEqual([row["name"] for row in tiers.rows[ledger.RETIRED]], ["retired"])


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

    def test_the_repository_s_ledger_is_sorted_json_lines_with_the_nine_fields(self):
        path = ROOT / "tests" / "mutations" / ledger.LEDGER_NAME
        self.assertTrue(path.is_file(), "%s is in git, empty until the first run" % path)
        lines = ledger.LedgerStore(path).read()
        self.assertEqual([list(entry) for entry in lines], [FIELDS] * len(lines))
        self.assertEqual([entry["key"] for entry in lines], sorted(entry["key"] for entry in lines))


class TheCriticalMarksTest(unittest.TestCase):
    """The hand-written `"tier": "critical"` marks in the repository's tables (P787 PR 4): few, spelled right, on files that exist."""

    def rows(self):
        return [(table.name, row) for table in TABLES for row in json.loads(table.read_text())]

    def test_the_critical_rows_stay_under_the_po_s_cap_and_the_tier_key_says_critical_or_nothing(self):
        rows = self.rows()
        self.assertTrue(rows, "the tables are read from the repository")
        misspelt = [(table, row.get("name", "?")) for table, row in rows if row.get(ledger.TIER_KEY, ledger.CRITICAL) != ledger.CRITICAL]
        self.assertEqual(misspelt, [], "a tier key spells %r or is absent: any other word is a mark the tool never reads" % ledger.CRITICAL)
        marked = [(table, row.get("name", "?")) for table, row in rows if ledger.TIER_KEY in row]
        self.assertLessEqual(len(marked), CRITICAL_CAP, "more than the PO's %d critical rows: drop one before adding one" % CRITICAL_CAP)

    def test_every_critical_row_names_a_file_that_exists(self):
        gone = [(table, row.get("name", "?"), row["file"]) for table, row in self.rows()
                if row.get(ledger.TIER_KEY) == ledger.CRITICAL and not (ROOT / row["file"]).is_file()]
        self.assertEqual(gone, [], "a critical row on a gone file is a stale mark: retarget or unmark it")


if __name__ == "__main__":
    unittest.main()
