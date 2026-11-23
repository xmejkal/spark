"""
P1027 (#1506), slice 2: a need that goes away makes spark ask about the must lines it served. The record of slice 1,
`.spark/needs-basis.json`, also notes the ids of the needs the must lines were last gone through with. A noted need that
needs.json no longer holds is a dropped need: the idea phase of `flow.py show` is out of date, names it, and its next step
is the brief step, `init_project.py --answers`, which runs only on the person's yes. Only a review (`--needs-set []`) clears
it. Spark edits nothing from the flow.

    python3 -m unittest tests.test_needs_dropped
"""

import contextlib
import io
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit
from test_needs_basis import RECORD, WithAStore, a_project, brief_of, needs_set  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import parts  # noqa: E402
from spark.design import needs_basis  # noqa: E402

WIFI_MUST = "The time comes from the internet over Wi-Fi."
MUST = [WIFI_MUST, "It shows the date on a press."]
NEEDS = [{"id": "board", "does": "compute", "what": "microcontroller"}, {"id": "screen", "does": "indicate", "what": "time"},
         {"id": "button", "does": "sense", "what": "press"}, {"id": "wifi", "does": "connect", "what": "wifi"}]


def drop(project, need):
    """`parts.py --needs-drop <project> <need> --json`: its exit code."""
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return parts.main(["--needs-drop", str(project), need, "--json"])


class WithNeeds(WithAStore):
    def reviewed_project(self, items=NEEDS):
        """A project with a brief, its needs written, and a review: the record notes every need."""
        project = a_project(dict(brief_of(must=MUST)))
        needs_set(project, items)
        needs_set(project, [])
        return project

    def noted(self, project):
        return json.loads((project / RECORD).read_text()).get("needs")


class TheNotedNeedsTest(WithNeeds):
    """Test 13: a review notes the needs as they are; a defining write keeps a dropped need noted."""

    def test_a_write_notes_the_ids_of_the_needs(self):
        self.assertEqual(self.noted(self.reviewed_project()), ["board", "button", "screen", "wifi"])

    def test_a_drop_is_named_and_a_review_right_after_clears_it(self):
        project = self.reviewed_project()
        self.assertEqual(drop(project, "wifi"), 0)
        self.assertEqual(needs_basis.dropped(project, ["board", "screen", "button"]), ["wifi"])
        said, code, _ = needs_set(project, [])
        self.assertEqual((code, said["data"]["basis_noted"]), (0, True))
        self.assertEqual(self.noted(project), ["board", "button", "screen"])
        self.assertEqual(needs_basis.dropped(project, ["board", "screen", "button"]), [])

    def test_a_defining_write_after_a_drop_keeps_it_noted(self):
        project = self.reviewed_project()
        drop(project, "wifi")
        needs_set(project, [{"id": "screen", "what": "date"}])
        self.assertEqual(self.noted(project), ["board", "button", "screen", "wifi"])
        self.assertEqual(needs_basis.dropped(project, ["board", "screen", "button"]), ["wifi"])

    def test_a_drop_of_the_last_need_then_a_review_notes_no_need(self):
        project = self.reviewed_project(NEEDS[:1])
        drop(project, "board")
        self.assertEqual(needs_basis.dropped(project, []), ["board"])
        said, code, _ = needs_set(project, [])
        self.assertEqual((code, said["data"]["basis_noted"], self.noted(project)), (0, True, []))
        self.assertEqual(needs_basis.dropped(project, []), [])


class AnOlderRecordTest(WithNeeds):
    """Test 14: slice 1's record, with no `needs` key, names no drop and is not broken; a review then notes the needs."""

    def slice_one_project(self):
        project = self.reviewed_project()
        record = json.loads((project / RECORD).read_text())
        del record["needs"]
        (project / RECORD).write_text(json.dumps(record))
        return project

    def test_a_record_with_no_needs_key_is_held_and_names_no_drop(self):
        project = self.slice_one_project()
        self.assertNotEqual(needs_basis.NeedsBasisStore(project).held(), "broken")
        self.assertEqual(needs_basis.dropped(project, []), [])

    def test_a_review_then_notes_the_needs(self):
        project = self.slice_one_project()
        said, code, _ = needs_set(project, [])
        self.assertEqual((code, said["data"]["basis_noted"], self.noted(project)), (0, True, ["board", "button", "screen", "wifi"]))

    def test_a_needs_value_that_is_no_list_of_ids_is_broken(self):
        for value in ("wifi", [1], ["Wi Fi"], {"wifi": True}, None):
            with self.subTest(value=value):
                project = self.reviewed_project(NEEDS[:1])
                record = json.loads((project / RECORD).read_text())
                (project / RECORD).write_text(json.dumps(dict(record, needs=value)))
                self.assertEqual(needs_basis.NeedsBasisStore(project).held(), "broken")
                self.assertEqual(needs_basis.dropped(project, []), [])


if __name__ == "__main__":
    unittest.main()
