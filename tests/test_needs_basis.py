"""
P1027 (#1506), slice 1: the needs phase says that the goal or the must lines changed after the needs were written. A record
beside the needs, `.spark/needs-basis.json`, keeps the sha256 of the brief's goal and of its must lines as they were when
`parts.py --needs-set` wrote the needs. `flow.py show` and the page compare them with the brief now. Spark edits nothing.
It covers `design/needs_basis`, its writer in `design/set_needs` and its reader in `flow/phase_readers`.

    python3 -m unittest tests.test_needs_basis
"""

import contextlib
import hashlib
import html
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import flow  # noqa: E402
import parts  # noqa: E402
from spark.design import needs_basis  # noqa: E402
from spark.flow.write_flow_page import PageParts, write_page  # noqa: E402
from spark.records.brief import Brief  # noqa: E402

GOAL = "A clock that shows the date on a press"
#: The record, as the card names it: a literal, not the code's own.
RECORD = Path(".spark") / "needs-basis.json"
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
                (project / RECORD).write_text(text)
                self.assertEqual(needs_basis.NeedsBasisStore(project).held(), "broken")

    def test_a_record_that_is_a_folder_is_broken(self):
        project = a_project()
        (project / RECORD).mkdir()
        self.assertEqual(needs_basis.NeedsBasisStore(project).held(), "broken")


def needs_set(project, items, *argv):
    """`parts.py --needs-set <project> <file of items> --json`: (the envelope, the exit code, the text lines without --json)."""
    given = Path(tempfile.mkdtemp()) / "needs.json"
    given.write_text(json.dumps(items))
    with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
        code = parts.main(["--needs-set", str(project), str(given), *argv, "--json"])
    with contextlib.redirect_stdout(io.StringIO()) as text, contextlib.redirect_stderr(io.StringIO()):
        parts.main(["--needs-set", str(project), str(given), *argv, "--dry-run"])
    return json.loads(out.getvalue()), code, text.getvalue().splitlines()


def brief_of(goal=GOAL, must=MUST):
    return {"goal": goal, "must": list(must)}


def set_brief(project, goal=GOAL, must=MUST):
    """Edit the brief as `init_project.py --answers` leaves it: project.json with the goal and the must lines."""
    (project / ".spark" / "project.json").write_text(json.dumps(brief_of(goal, must)))


BOARD = {"id": "board", "does": "compute", "what": "microcontroller"}
SCREEN = {"id": "screen", "does": "indicate", "what": "time"}
NOTED = "  noted the goal and the must lines these needs were written from (.spark/needs-basis.json)"
WOULD_NOTE = "  would note the goal and the must lines these needs were written from (.spark/needs-basis.json)"


class WithAStore(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch.dict(os.environ, {"SPARK_HOME": tempfile.mkdtemp()})
        patcher.start()
        self.addCleanup(patcher.stop)

    def held(self, project):
        return needs_basis.NeedsBasisStore(project).held()

    def basis_bytes(self, project):
        path = project / RECORD
        return path.read_bytes() if path.is_file() else None


class TheWriterTest(WithAStore):
    """`parts.py --needs-set` notes the stamp of the brief on a write that defines a need or is a review (`[]`)."""

    def test_a_write_notes_the_brief_says_so_and_answers_basis_noted(self):
        project = a_project(brief_of())
        said, code, _ = needs_set(project, [BOARD, SCREEN])
        self.assertEqual((code, said["data"]["basis_noted"]), (0, True))
        self.assertEqual(self.held(project), stamp())

    def test_the_text_answer_holds_the_noted_line(self):
        project = a_project(brief_of())
        given = Path(tempfile.mkdtemp()) / "needs.json"
        given.write_text(json.dumps([BOARD]))
        with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
            parts.main(["--needs-set", str(project), str(given)])
        self.assertIn(NOTED, out.getvalue().splitlines())

    def test_a_dry_run_writes_no_record_and_says_would_note(self):
        project = a_project(brief_of())
        said, code, text = needs_set(project, [BOARD], "--dry-run")
        self.assertEqual((code, said["data"]["basis_noted"], self.basis_bytes(project)), (0, False, None))
        self.assertIn(WOULD_NOTE, text)

    def test_a_run_with_a_problem_writes_no_record_and_no_line(self):
        project = a_project(brief_of())
        said, code, text = needs_set(project, [BOARD, {"id": "Bad Id", "does": "x", "what": "y"}])
        self.assertEqual((code, said["data"]["basis_noted"], self.basis_bytes(project)), (1, False, None))
        self.assertNotIn(WOULD_NOTE, text)

    def test_a_brief_with_no_goal_gives_no_record_and_no_line(self):
        for brief in (None, {"must": MUST}, {"goal": None}):
            with self.subTest(brief=brief):
                project = a_project(brief)
                said, code, text = needs_set(project, [BOARD])
                self.assertEqual((code, said["data"]["basis_noted"], self.basis_bytes(project)), (0, False, None))
                self.assertNotIn(WOULD_NOTE, text)

    def test_a_blank_goal_gives_no_record_and_no_line(self):
        project = a_project({"goal": "  ", "must": MUST})
        said, code, text = needs_set(project, [BOARD])
        self.assertEqual((code, said["data"]["basis_noted"], self.basis_bytes(project)), (0, False, None))
        self.assertNotIn(WOULD_NOTE, text)

    @unittest.skipIf(os.geteuid() == 0, "root reads any file")
    def test_a_brief_that_cannot_be_read_never_fails_the_write(self):
        project = a_project(brief_of())
        brief = project / ".spark" / "project.json"
        brief.chmod(0)
        self.addCleanup(brief.chmod, 0o644)
        said, code, _ = needs_set(project, [BOARD])
        self.assertEqual((code, said["data"]["written"], said["data"]["basis_noted"], self.basis_bytes(project)), (0, True, False, None))

    def test_a_deeply_nested_brief_never_fails_the_write(self):
        project = a_project("[" * 100000 + "]" * 100000)
        said, code, _ = needs_set(project, [BOARD])
        self.assertEqual((code, said["data"]["written"], said["data"]["basis_noted"], self.basis_bytes(project)), (0, True, False, None))

    def test_a_review_notes_a_changed_brief_and_leaves_the_needs_byte_for_byte(self):
        project = a_project(brief_of())
        needs_set(project, [BOARD, SCREEN])
        set_brief(project, goal=GOAL + " on a battery")
        before = (project / ".spark" / "needs.json").read_bytes()
        said, code, _ = needs_set(project, [])
        self.assertEqual((code, said["data"]["basis_noted"], said["data"]["changes"]), (0, True, []))
        self.assertEqual(self.held(project), stamp(goal=GOAL + " on a battery"))
        self.assertEqual((project / ".spark" / "needs.json").read_bytes(), before)

    def test_a_review_with_a_record_that_fits_writes_nothing(self):
        project = a_project(brief_of())
        needs_set(project, [BOARD])
        record = project / RECORD
        record.write_text(record.read_text() + "\n")  # a mark of the bytes: a write would take it away
        said, code, text = needs_set(project, [])
        self.assertEqual((code, said["data"]["basis_noted"]), (0, False))
        self.assertTrue(record.read_text().endswith("\n\n"))
        self.assertNotIn(WOULD_NOTE, text)

    def test_a_review_with_no_needs_notes_nothing(self):
        project = a_project(brief_of())
        said, code, _ = needs_set(project, [])
        self.assertEqual((code, said["data"]["basis_noted"], self.basis_bytes(project)), (0, False, None))

    def test_a_mark_only_or_aside_only_write_leaves_the_record(self):
        for item in ({"id": "board", "mark": "have"}, {"id": "board", "aside": True}):
            with self.subTest(item=item):
                project = a_project(brief_of())
                needs_set(project, [BOARD])
                set_brief(project, goal="another goal")
                before = self.basis_bytes(project)
                said, code, _ = needs_set(project, [item])
                self.assertEqual((code, said["data"]["basis_noted"], self.basis_bytes(project)), (0, False, before))

    def test_a_condition_only_write_defines_the_need_and_notes(self):
        project = a_project(brief_of())
        needs_set(project, [BOARD])
        set_brief(project, goal="another goal")
        said, code, _ = needs_set(project, [{"id": "board", "condition": "when the button is pressed"}])
        self.assertEqual((code, said["data"]["basis_noted"], self.held(project)), (0, True, stamp(goal="another goal")))

    def test_a_pick_and_a_drop_leave_the_record(self):
        project = a_project(brief_of())
        needs_set(project, [BOARD, SCREEN])
        set_brief(project, goal="another goal")
        before = self.basis_bytes(project)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            picked = parts.main(["--pick", str(project), "board=xiao-esp32-c6", "--json"])
            dropped = parts.main(["--needs-drop", str(project), "screen", "--json"])
        self.assertEqual((picked, dropped, self.basis_bytes(project)), (0, 0, before))


def show(project):
    """`flow.py show --project <project> --json`: (the envelope, the exit code)."""
    with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
        code = flow.main(["show", "--project", str(project), "--json"])
    return json.loads(out.getvalue()), code


def needs_phase(envelope):
    return next(phase for phase in envelope["data"]["phases"] if phase["phase"] == "needs")


class FakeStore:
    """Fake: stands in for FlowPageStore and keeps the page it was asked to write."""

    def __init__(self):
        self.written = []

    def write(self, project, file_name, text):
        self.written.append(text)
        return Path(project) / file_name


def digest(*folders):
    """{path: sha256} of every file under `folders`: the same before and after a read says that nothing was written."""
    return {str(path): hashlib.sha256(path.read_bytes()).hexdigest()
            for folder in folders for path in sorted(Path(folder).rglob("*")) if path.is_file()}


NEEDS_LINE = "2 need(s): board, screen"
REVIEW = ("Claude goes through the needs and the must lines with you, and when they still fit, runs parts.py --needs-set with []: "
          "spark changes none of them itself")
STALE_NOW = "Your goal or must lines changed after the needs were written. Ask Claude to go through the needs and the must lines with you."
CANNOT_TELL = "spark cannot tell whether the needs fit the goal: %s"


class TheReaderTest(WithAStore):
    """`flow.py show` and the page: the needs phase is out of date when the brief changed after the needs were written."""

    def written_project(self):
        project = a_project(brief_of())
        needs_set(project, [BOARD, SCREEN])
        return project

    def test_a_goal_edited_after_the_needs_makes_them_out_of_date_and_asks_for_a_review(self):
        project = self.written_project()
        set_brief(project, goal=GOAL + " that runs on a battery")
        said, code = show(project)
        phase = needs_phase(said)
        self.assertEqual((code, phase["status"], phase["mark"], phase["by"]), (0, "stale", "↻", "claude"))
        self.assertEqual(phase["says"], [NEEDS_LINE, "the goal changed after the needs were written", REVIEW])
        self.assertEqual([offer["key"] for offer in phase["offers"]], ["needs-drop:board", "needs-drop:screen"])
        self.assertEqual(said["data"]["stands_at"], "needs")
        self.assertEqual(said["data"]["guide"]["now"], {"phase": "needs", "by": ["claude"], "says": STALE_NOW, "offer": None,
                                                        "chat_offer": None, "needs": [], "steps": None, "with_wiring": False})

    def test_the_text_line_says_out_of_date_and_what_changed(self):
        project = self.written_project()
        set_brief(project, goal="another goal")
        with contextlib.redirect_stdout(io.StringIO()) as out:
            flow.main(["show", "--project", str(project)])
        self.assertIn("  ↻ needs: out of date, %s, the goal changed after the needs were written, %s (claude)" % (NEEDS_LINE, REVIEW),
                      out.getvalue().splitlines())

    def test_a_dropped_must_line_alone_names_the_must_lines(self):
        project = self.written_project()
        set_brief(project, must=MUST[1:])
        self.assertEqual(needs_phase(show(project)[0])["says"], [NEEDS_LINE, "the must lines changed after the needs were written", REVIEW])

    def test_both_changes_name_both(self):
        project = self.written_project()
        set_brief(project, goal="another goal", must=[])
        self.assertEqual(needs_phase(show(project)[0])["says"],
                         [NEEDS_LINE, "the goal and the must lines changed after the needs were written", REVIEW])

    def test_the_must_lines_in_another_order_change_nothing(self):
        project = self.written_project()
        set_brief(project, must=MUST[::-1])
        phase = needs_phase(show(project)[0])
        self.assertEqual((phase["status"], phase["says"]), ("ok", [NEEDS_LINE]))

    def test_a_review_with_an_empty_list_makes_the_needs_current_again(self):
        project = self.written_project()
        set_brief(project, goal="another goal")
        needs_set(project, [])
        phase = needs_phase(show(project)[0])
        self.assertEqual((phase["status"], phase["says"]), ("ok", [NEEDS_LINE]))

    def test_a_mark_after_a_goal_change_leaves_the_needs_out_of_date(self):
        project = self.written_project()
        set_brief(project, goal="another goal")
        needs_set(project, [{"id": "board", "mark": "have"}])
        self.assertEqual(needs_phase(show(project)[0])["status"], "stale")

    def test_a_project_written_before_the_card_says_what_it_said_before(self):
        project = a_project(brief_of())
        (project / ".spark" / "needs.json").write_text(json.dumps({"schema": 1, "needs": [BOARD, SCREEN]}))
        said, code = show(project)
        phase = needs_phase(said)
        self.assertEqual((code, phase["status"], phase["says"]), (0, "ok", [NEEDS_LINE]))
        self.assertNotEqual(said["data"]["stands_at"], "needs")

    def test_a_broken_record_says_spark_cannot_tell(self):
        project = self.written_project()
        (project / RECORD).write_text("{not json")
        phase = needs_phase(show(project)[0])
        self.assertEqual((phase["status"], phase["says"]),
                         ("ok", [NEEDS_LINE, CANNOT_TELL % ".spark/needs-basis.json cannot be read"]))

    @unittest.skipIf(os.geteuid() == 0, "root reads any file")
    def test_a_record_that_cannot_be_read_says_spark_cannot_tell(self):
        project = self.written_project()
        (project / RECORD).chmod(0)
        self.addCleanup((project / RECORD).chmod, 0o644)
        said, code = show(project)
        phase = needs_phase(said)
        self.assertEqual((code, phase["status"], phase["says"]),
                         (0, "ok", [NEEDS_LINE, CANNOT_TELL % ".spark/needs-basis.json cannot be read"]))

    def test_a_brief_with_no_goal_now_gives_no_line(self):
        project = self.written_project()
        (project / ".spark" / "project.json").write_text(json.dumps({"goal": None, "must": MUST}))
        phase = needs_phase(show(project)[0])
        self.assertEqual((phase["status"], phase["says"]), ("ok", [NEEDS_LINE]))

    def test_a_brief_that_is_no_json_now_says_spark_cannot_tell(self):
        project = self.written_project()
        (project / ".spark" / "project.json").write_text("{not json")
        phase = needs_phase(show(project)[0])
        self.assertEqual((phase["status"], phase["says"]), ("ok", [NEEDS_LINE, CANNOT_TELL % "the brief cannot be read (bad-json)"]))

    @unittest.skipIf(os.geteuid() == 0, "root reads any file")
    def test_a_brief_that_cannot_be_read_says_spark_cannot_tell_with_the_error(self):
        project = self.written_project()
        brief = project / ".spark" / "project.json"
        brief.chmod(0)
        self.addCleanup(brief.chmod, 0o644)
        said, code = show(project)
        phase = needs_phase(said)
        self.assertEqual((code, phase["status"], len(phase["says"])), (0, "ok", 2))
        self.assertTrue(phase["says"][1].startswith(CANNOT_TELL % "the brief cannot be read ("))
        self.assertIn("Permission denied", phase["says"][1])

    def test_a_deeply_nested_brief_says_spark_cannot_tell_with_the_error(self):
        project = self.written_project()
        (project / ".spark" / "project.json").write_text("[" * 100000 + "]" * 100000)
        said, code = show(project)
        phase = needs_phase(said)
        self.assertEqual((code, phase["status"], len(phase["says"])), (0, "ok", 2))
        self.assertIn("recursion", phase["says"][1])

    def test_the_read_and_the_page_write_nothing_in_the_project_or_the_store(self):
        project = self.written_project()
        set_brief(project, goal="another goal")
        before = digest(project, os.environ["SPARK_HOME"])
        show(project)
        write_page(project, parts=lambda _project: PageParts([], None), store=FakeStore())
        self.assertEqual(digest(project, os.environ["SPARK_HOME"]), before)

    def test_the_page_shows_the_needs_out_of_date_with_both_lines_and_the_guide_s_sentence(self):
        project = self.written_project()
        set_brief(project, goal="another goal")
        store = FakeStore()
        written = write_page(project, parts=lambda _project: PageParts([], None), store=store)
        self.assertEqual(next(phase for phase in written.phases if phase["phase"] == "needs")["status"], "stale")
        text = html.unescape(store.written[0])
        for said in ("the goal changed after the needs were written", REVIEW, STALE_NOW):
            self.assertIn(said, text)


if __name__ == "__main__":
    unittest.main()
