"""
P1027 (#1506), slice 2: a need that goes away makes spark ask about the must lines it served. The record of slice 1,
`.spark/needs-basis.json`, also notes the ids of the needs the must lines were last gone through with. A noted need that
needs.json no longer holds is a dropped need: the idea phase of `flow.py show` is out of date, names it, and its next step
is the brief step, `init_project.py --answers`, which runs only on the person's yes. Only a review (`--needs-set []`) clears
it. Spark edits nothing from the flow.

    python3 -m unittest tests.test_needs_dropped
"""

import contextlib
import html
import io
import json
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit
from test_needs_basis import RECORD, FakeStore, WithAStore, a_project, brief_of, digest, needs_set, show  # noqa: E402
from test_project_commit import a_repository, git, isolated_env  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import flow  # noqa: E402
import init_project  # noqa: E402
import parts  # noqa: E402
from spark.design import needs_basis  # noqa: E402
from spark.flow.write_flow_page import PageParts, write_page  # noqa: E402

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


#: The idea phase's lines and the guide's sentence after a drop, as the card names them: literals, not the code's own.
GOAL_LINE = "your goal is “A clock that shows the date on a press”"
DROPPED_LINE = "needs dropped after the must lines were last gone through: %s"
MUST_ASK = ("Claude asks you about each must line a dropped need served, and on your yes changes it in the brief: git keeps "
            "each change, so it can be taken back. If the must lines still hold, Claude runs the review: parts.py --needs-set "
            "with []")
IDEA_STALE_NOW = ("A need was dropped. Claude names it and the must lines it served: tell Claude whether they still hold. "
                  "Claude can change them for you.")
BRIEF_WHY = ("On the person's yes: writes the must lines they agreed to into the brief, one commit when git holds it, so git "
             "revert --no-edit takes it back")
ANSWERS_PLACEHOLDER = "<answers.json>"


def phase_of(envelope, name):
    return next(phase for phase in envelope["data"]["phases"] if phase["phase"] == name)


def now_line(project):
    """The NOW line of `flow.py show`'s text."""
    with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
        flow.main(["show", "--project", str(project)])
    return next(line for line in out.getvalue().splitlines() if line.startswith("  NOW ("))


class WithNeedsInGit(WithNeeds):
    """A scratch repository with an empty HOME and global config, beside the scratch store."""

    def setUp(self):
        super().setUp()
        patcher = mock.patch.dict(os.environ, isolated_env())
        patcher.start()
        self.addCleanup(patcher.stop)

    def brief_step(self, project):
        return {"op": "init_project", "argv": ["--project", str(project.absolute()), "--answers", ANSWERS_PLACEHOLDER],
                "why": BRIEF_WHY, "effects": ["reads", "runs", "writes"], "needs_yes": True,
                "env": {"SPARK_HOME": str(Path(os.environ["SPARK_HOME"]).resolve())}}


class ADroppedNeedTest(WithNeedsInGit):
    """Test 11, the card's value test: a dropped need makes the idea phase out of date, names it, and offers the brief step."""

    def test_a_dropped_need_asks_about_the_must_lines_and_names_the_brief_step(self):
        project = self.reviewed_project()
        drop(project, "wifi")
        said, code = show(project)
        idea = phase_of(said, "idea")
        self.assertEqual((code, idea["status"], idea["mark"], idea["by"]), (0, "stale", "↻", "you"))
        self.assertEqual(idea["says"], [DROPPED_LINE % "wifi", MUST_ASK])
        self.assertEqual(phase_of(said, "needs")["status"], "ok")
        self.assertEqual(said["data"]["guide"]["now"], {"phase": "idea", "by": ["you"], "says": IDEA_STALE_NOW, "offer": None,
                                                        "chat_offer": None, "needs": [], "steps": None, "with_wiring": False, "command": None, "no_command": None})
        self.assertEqual(said["next"], [self.brief_step(project)])
        self.assertTrue(now_line(project).endswith(" [next: init_project, needs you]"), now_line(project))  # P1035 review: needs_yes too

    def test_a_stale_idea_with_a_goal_and_no_need_left_is_still_now(self):
        project = self.reviewed_project(NEEDS[:1])  # P1142: only an ok idea gives way to the needs
        drop(project, "board")
        said, _ = show(project)
        self.assertEqual((phase_of(said, "idea")["status"], phase_of(said, "needs")["status"]), ("stale", "not-started"))
        self.assertEqual((said["data"]["guide"]["now"]["phase"], said["data"]["guide"]["now"]["says"]), ("idea", IDEA_STALE_NOW))

    def test_an_out_of_date_idea_does_not_ask_for_the_goal_that_is_set(self):
        project = self.reviewed_project()
        drop(project, "wifi")
        self.assertFalse([said for said in phase_of(show(project)[0], "idea")["says"] if "Tell Claude your goal" in said])

    def test_two_dropped_needs_are_named_in_order(self):
        project = self.reviewed_project()
        drop(project, "wifi")
        drop(project, "button")
        self.assertEqual(phase_of(show(project)[0], "idea")["says"][0], DROPPED_LINE % "button, wifi")

    def test_a_review_right_after_the_drop_clears_the_idea_and_a_defining_write_does_not(self):
        project = self.reviewed_project()
        drop(project, "wifi")
        needs_set(project, [{"id": "screen", "what": "date"}])
        self.assertEqual(phase_of(show(project)[0], "idea")["status"], "stale")
        needs_set(project, [])
        said = show(project)[0]
        self.assertEqual((phase_of(said, "idea")["status"], phase_of(said, "idea")["says"]), ("ok", [GOAL_LINE]))
        # the brief step goes; the now is the parts phase, which names its own pick for the open needs (P1141)
        self.assertEqual((said["data"]["guide"]["now"]["phase"], [step["op"] for step in said["next"]]), ("parts", ["pick"]))

    def test_a_needs_file_that_cannot_be_read_leaves_the_idea_as_it_was(self):
        project = self.reviewed_project()
        drop(project, "wifi")
        (project / ".spark" / "needs.json").write_text("{not json")
        said, code = show(project)
        self.assertEqual((phase_of(said, "idea")["status"], phase_of(said, "idea")["says"]), ("ok", [GOAL_LINE]))
        self.assertEqual(phase_of(said, "needs")["status"], "could-not-run")

    def test_the_read_and_the_page_write_nothing_after_a_drop(self):
        project = self.reviewed_project()
        drop(project, "wifi")
        before = digest(project, os.environ["SPARK_HOME"])
        show(project)
        write_page(project, parts=lambda _project: PageParts([], None), store=FakeStore())
        self.assertEqual(digest(project, os.environ["SPARK_HOME"]), before)

    def test_the_page_shows_the_idea_out_of_date_with_both_lines_and_the_guide_s_sentence(self):
        project = self.reviewed_project()
        drop(project, "wifi")
        store = FakeStore()
        written = write_page(project, parts=lambda _project: PageParts([], None), store=store)
        self.assertEqual(next(phase for phase in written.phases if phase["phase"] == "idea")["mark"], "↻")
        text = html.unescape(store.written[0])
        for said in (DROPPED_LINE % "wifi", MUST_ASK, IDEA_STALE_NOW):
            self.assertIn(said, text)


class TheBriefStepTest(WithNeedsInGit):
    """Test 12: the brief step's argv runs init_project.py, which commits the agreed must lines; the review clears both
    marks; `git revert --no-edit <sha>` brings the old brief back, and the needs phase then says the must lines changed."""

    def test_the_brief_step_commits_the_review_clears_and_git_revert_goes_back(self):
        root, _ = a_repository()
        project = root
        (project / ".spark").mkdir()
        (project / ".spark" / "project.json").write_text(json.dumps(brief_of(must=MUST)))
        git(root, "add", ".spark/project.json")
        git(root, "commit", "-q", "-m", "the brief")
        needs_set(project, NEEDS)
        needs_set(project, [])
        drop(project, "wifi")
        step = show(project)[0]["next"][0]
        answers = Path(tempfile.mkdtemp()) / "answers.json"
        answers.write_text(json.dumps({"must": MUST[1:]}))
        argv = [str(answers) if each == ANSWERS_PLACEHOLDER else each for each in step["argv"]]
        with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(init_project.main(argv), 0)
        sha = re.search(r"committed as ([0-9a-f]+)\. To go back, run in this project: git revert --no-edit \1 \(the newest change first\)", out.getvalue())
        self.assertIsNotNone(sha, out.getvalue())
        self.assertEqual(phase_of(show(project)[0], "needs")["status"], "stale")  # slice 1: the must lines changed
        needs_set(project, [])
        said = show(project)[0]
        self.assertEqual((phase_of(said, "idea")["status"], phase_of(said, "needs")["status"]), ("ok", "ok"))
        git(root, "revert", "--no-edit", sha.group(1))
        self.assertEqual(json.loads((project / ".spark" / "project.json").read_text())["must"], MUST)
        needs = phase_of(show(project)[0], "needs")
        self.assertEqual((needs["status"], needs["says"][1]), ("stale", "the must lines changed after the needs were written"))


if __name__ == "__main__":
    unittest.main()
