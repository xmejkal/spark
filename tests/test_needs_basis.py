"""
P1027 (#1506), slice 1: the needs phase says that the goal or the must lines changed after the needs were written. A record
beside the needs, `.spark/needs-basis.json`, keeps the sha256 of the brief's goal and of its must lines as they were when
`parts.py --needs-set` wrote the needs. `flow.py show` and the page compare them with the brief now. Spark edits nothing.
It covers `design/needs_basis`, its writer in `design/set_needs` and its reader in `flow/phase_readers`.

    python3 -m unittest tests.test_needs_basis
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from spark.design import needs_basis  # noqa: E402
from spark.records.brief import Brief  # noqa: E402

GOAL = "A clock that shows the date on a press"
MUST = ["The time comes from the internet over Wi-Fi.", "It runs a week on a battery."]


def a_project(brief=None):
    """A project folder with `.spark/project.json` holding `brief` (a dict, or text written as it is), or no brief."""
    project = Path(tempfile.mkdtemp()) / "clock"
    (project / ".spark").mkdir(parents=True)
    if brief is not None:
        (project / ".spark" / "project.json").write_text(brief if isinstance(brief, str) else json.dumps(brief))
    return project


def stamp(goal=GOAL, must=MUST):
    return needs_basis.stamp_of(Brief(goal=goal, must=tuple(must)))


class TheStampTest(unittest.TestCase):
    def test_a_brief_with_a_goal_gives_both_hashes(self):
        given = stamp()
        self.assertEqual(sorted(given), ["goal_sha256", "must_sha256"])
        self.assertTrue(all(len(value) == 64 and int(value, 16) >= 0 for value in given.values()))

    def test_no_goal_a_null_goal_bad_json_and_a_must_that_is_no_list_give_none(self):
        for brief in ({"must": MUST}, {"goal": None, "must": MUST}, "{not json", {"goal": GOAL, "must": "one line"}):
            with self.subTest(brief=brief):
                self.assertIsNone(needs_basis.stamp_of(Brief.from_project(a_project(brief))))


class TheChangeTest(unittest.TestCase):
    def test_the_same_stamp_is_no_change(self):
        self.assertEqual(needs_basis.changed(stamp(), stamp()), [])

    def test_another_goal_is_the_goal(self):
        self.assertEqual(needs_basis.changed(stamp(), stamp(goal=GOAL + " and a battery")), ["goal"])

    def test_a_dropped_must_line_is_the_must_lines(self):
        self.assertEqual(needs_basis.changed(stamp(), stamp(must=MUST[1:])), ["must"])

    def test_the_same_must_lines_in_another_order_are_no_change(self):
        self.assertEqual(needs_basis.changed(stamp(), stamp(must=MUST[::-1])), [])

    def test_a_trailing_space_in_the_goal_is_a_change(self):
        self.assertEqual(needs_basis.changed(stamp(), stamp(goal=GOAL + " ")), ["goal"])

    def test_both_changes_are_both_in_order(self):
        self.assertEqual(needs_basis.changed(stamp(), stamp(goal="other", must=[])), ["goal", "must"])


class TheStoreTest(unittest.TestCase):
    def test_a_saved_stamp_is_held(self):
        project = a_project()
        needs_basis.NeedsBasisStore(project).save(stamp())
        self.assertEqual(needs_basis.NeedsBasisStore(project).held(), stamp())

    def test_no_record_is_none(self):
        self.assertIsNone(needs_basis.NeedsBasisStore(a_project()).held())

    def test_a_record_that_is_no_json_of_its_shape_is_broken(self):
        good = dict(stamp(), schema=1)
        for text in ("{not json", json.dumps({"schema": 1, "goal_sha256": good["goal_sha256"]}), json.dumps(dict(good, schema=2)),
                     json.dumps(dict(good, must_sha256="not hex")), json.dumps([good])):
            with self.subTest(text=text):
                project = a_project()
                (project / needs_basis.BASIS_FILE).write_text(text)
                self.assertIs(needs_basis.NeedsBasisStore(project).held(), needs_basis.BROKEN)

    def test_a_record_that_is_a_folder_is_broken(self):
        project = a_project()
        (project / needs_basis.BASIS_FILE).mkdir()
        self.assertIs(needs_basis.NeedsBasisStore(project).held(), needs_basis.BROKEN)


if __name__ == "__main__":
    unittest.main()
