"""
A wired board's offers say that a pin can move (P1044, #1534). Two witnesses say that the person's breadboard can be wired:
the kept wiring sheet, breadboard.md, current or stale, and the newest board log in sim/runs/board/. With one or more, the
parts phase says so in a line of its own with the day of each, and each pick and build offer's effect starts with a fixed
sentence that has no date, so a date never changes the fingerprint. `data.guide.wired` holds both times with their zones.
Every case pins its times and runs in Europe/Prague.

    python3 -m unittest tests.test_wired_board
"""

import contextlib
import datetime
import html
import io
import json
import os
import re
import shutil
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp and the flow tests' helpers
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from fakes import FakeOutsideWorld  # noqa: E402
from test_flow import (FlowTest, LOGGED_AT, SEEN_SENTENCE, a_board_log, a_built_project,  # noqa: E402
                       a_built_project_with_a_sheet_from, a_deploy_project, lines_of, offer_of, says, show, statuses, with_needs)
from test_run_request import BUTTON_LIGHT, ID, FakeStep  # noqa: E402
from spark.core import zone_time  # noqa: E402
from spark.core.cli import HelpText, run_cli  # noqa: E402
from spark.core.outside import build_bare_outside_world  # noqa: E402
from spark.flow import flow_codes, phase_readers, wired_board  # noqa: E402
from spark.flow.fingerprint import fingerprint_of  # noqa: E402
from spark.flow.flow_codes import (BOARD_ONLY_BUILD_EFFECT, WIRED_BUILD_MESSAGE, WIRED_DEPLOY_MESSAGE, WIRED_PICK_MESSAGE,  # noqa: E402
                                   WIRED_SHEET_MESSAGE, WIRED_STEP_MESSAGE)
from spark.flow.flow_page import page_words  # noqa: E402
from spark.flow.run_request import RunRequest  # noqa: E402
from spark.flow.show_flow import read_flow  # noqa: E402
from spark.flow.write_flow_page import write_page  # noqa: E402

#: The sheet's moment: noon UTC on 22 Nov 2026, 13:00 in Prague.
SHEET_AT = datetime.datetime(2026, 11, 22, 12, 0, tzinfo=datetime.timezone.utc).timestamp()
SHEET_DAY, LOG_DAY = "22 Nov 2026", "23 Nov 2026"
#: Two needs, one picked: the parts phase offers picks for the other.
NEEDS = [{"id": "soil", "does": "sense", "what": "soil-moisture", "pick": [{"part": "x-many"}]},
         {"id": "wet", "does": "sense", "what": "soil-moisture"}]
#: An ISO time with its zone, as zone_time stamps it.
ZONED = r"[+-]\d\d:\d\d$"


def sheet_text(day=SHEET_DAY):
    return WIRED_SHEET_MESSAGE % day


def log_text(day=LOG_DAY):
    return WIRED_DEPLOY_MESSAGE % day


def a_sheet_at(project, moment=SHEET_AT):
    """`project` with its breadboard.md dated `moment` (seconds since the epoch)."""
    os.utime(project / "breadboard.md", (moment, moment))
    return project


def a_wired_project():
    """A built project with two needs, one picked, and its sheet dated SHEET_AT: picks and a build are offered."""
    return a_sheet_at(with_needs(a_built_project(), NEEDS))


def effects(said, kind):
    """The effects of the offers of `kind` (pick, build) in an envelope."""
    return [offer["effect"] for phase in said["data"]["phases"] for offer in phase["offers"] if offer["key"].split(":", 1)[0] == kind]


def wired_of(said):
    return said["data"]["guide"]["wired"]


class WiredTest(FlowTest):
    """FlowTest in Europe/Prague: a day the line says is pinned."""

    def setUp(self):
        super().setUp()
        patcher = mock.patch.dict(os.environ, {"TZ": "Europe/Prague"})
        patcher.start()
        self.addCleanup(time.tzset)
        self.addCleanup(patcher.stop)
        time.tzset()


class NoWitnessTest(WiredTest):
    def test_no_sheet_and_no_log_change_nothing(self):
        project = with_needs(a_built_project(), NEEDS)
        (project / "breadboard.md").unlink()
        said, _ = show(project)
        own = {reader.PHASE: reader.answer(project) for reader in phase_readers.READERS}
        self.assertEqual(says(said, "parts"), own["parts"].says)
        self.assertEqual(effects(said, "build"), [phase_readers.build_effect(project)])
        self.assertEqual(effects(said, "pick"), [offer.effect for offer in own["parts"].offers])
        self.assertTrue(effects(said, "pick"))
        self.assertIsNone(wired_of(said))
        self.assertEqual(said["data"]["fingerprint"], fingerprint_of(project, list(own.values())))


class TheSheetTest(WiredTest):
    def test_a_current_sheet_opens_the_parts_and_each_pick_and_build_offer(self):
        project = a_wired_project()
        said, _ = show(project)
        self.assertIsNone(statuses(said)["breadboard"])  # a current sheet
        self.assertEqual(says(said, "parts")[0], " ".join((sheet_text(), WIRED_STEP_MESSAGE)))
        self.assertEqual(says(said, "parts")[1], "1 of 2 needs picked")
        self.assertTrue(offer_of(said, "build")["effect"].startswith(WIRED_BUILD_MESSAGE + " Saves its files in this project"))
        self.assertTrue(effects(said, "pick"))
        for effect in effects(said, "pick"):
            self.assertTrue(effect.startswith(WIRED_PICK_MESSAGE + " Saves "), effect)
        self.assertRegex(wired_of(said)["sheet_at"], ZONED)
        self.assertEqual(wired_of(said), {"sheet_at": zone_time.stamp(datetime.datetime.fromtimestamp(SHEET_AT)), "deploy_at": None})

    def test_a_stale_sheet_is_a_witness_too(self):
        project = a_sheet_at(a_built_project_with_a_sheet_from({"board": "another"}))
        said, _ = show(project)
        self.assertEqual(statuses(said)["breadboard"], "stale")
        self.assertTrue(says(said, "parts")[0].startswith(sheet_text()))
        self.assertTrue(offer_of(said, "build")["effect"].startswith(WIRED_BUILD_MESSAGE))


class TheBoardLogTest(WiredTest):
    def test_a_board_log_alone_is_a_witness_with_the_deploy_s_time(self):
        project = a_board_log(a_deploy_project(), "ready seen", SEEN_SENTENCE)
        (project / "breadboard.md").unlink()
        said, _ = show(project)
        self.assertEqual(says(said, "parts")[0], " ".join((log_text(), WIRED_STEP_MESSAGE)))
        self.assertEqual(wired_of(said), {"sheet_at": None, "deploy_at": said["data"]["deploy"]["at"]})
        self.assertEqual(wired_of(said)["deploy_at"], LOGGED_AT.isoformat())
        self.assertTrue(offer_of(said, "build")["effect"].startswith(WIRED_BUILD_MESSAGE))

    def test_a_log_that_cannot_be_read_is_no_witness(self):
        project = a_board_log(a_deploy_project(), "a word", "x")
        (project / "breadboard.md").unlink()
        said, _ = show(project)
        self.assertEqual(statuses(said)["deploy"], "could-not-run")
        self.assertIsNone(wired_of(said))
        self.assertNotIn(WIRED_STEP_MESSAGE, " ".join(says(said, "parts")))
        self.assertNotIn(WIRED_BUILD_MESSAGE, offer_of(said, "build")["effect"])

    def test_both_witnesses_give_one_line_the_sheet_then_the_log_then_the_step(self):
        project = a_sheet_at(a_board_log(a_deploy_project(), "ready seen", SEEN_SENTENCE))
        said, _ = show(project)
        self.assertEqual(says(said, "parts")[0], " ".join((sheet_text(), log_text(), WIRED_STEP_MESSAGE)))
        self.assertEqual(sum(WIRED_STEP_MESSAGE in line for line in says(said, "parts")), 1)
        self.assertEqual(set(wired_of(said)), {"sheet_at", "deploy_at"})
        self.assertTrue(all(wired_of(said).values()))


class TheFingerprintTest(WiredTest):
    def test_a_newer_sheet_changes_the_line_and_never_the_fingerprint(self):
        project = a_wired_project()
        before, _ = show(project)
        a_sheet_at(project, SHEET_AT + 3 * 86400)
        after, _ = show(project)
        self.assertEqual(after["data"]["fingerprint"], before["data"]["fingerprint"])
        self.assertNotEqual(says(after, "parts")[0], says(before, "parts")[0])
        self.assertIn("25 Nov 2026", says(after, "parts")[0])

    def test_a_newer_log_changes_the_line_and_never_the_fingerprint(self):
        project = a_sheet_at(a_board_log(a_deploy_project(), "ready seen", SEEN_SENTENCE))
        before, _ = show(project)
        a_board_log(project, "ready seen", SEEN_SENTENCE, name="2026-11-26T09-00-00",
                    moment=datetime.datetime(2026, 11, 26, 9, 0, 0, tzinfo=datetime.timezone(datetime.timedelta(hours=1))))
        after, _ = show(project)
        self.assertEqual(after["data"]["fingerprint"], before["data"]["fingerprint"])
        self.assertNotEqual(says(after, "parts")[0], says(before, "parts")[0])
        self.assertIn(log_text("26 Nov 2026"), says(after, "parts")[0])

    def test_no_effect_holds_a_year(self):
        for project in (a_wired_project(), a_sheet_at(a_board_log(a_deploy_project(), "ready seen", SEEN_SENTENCE))):
            said, _ = show(project)
            every = [offer["effect"] for phase in said["data"]["phases"] for offer in phase["offers"]]
            self.assertTrue(every)
            for effect in every:
                self.assertNotRegex(effect, r"20\d\d")


class TheClickTest(WiredTest):
    """A page read on a wired project sends a build, and run-request runs it: the real readers, a fake build."""

    def test_a_build_asked_from_a_wired_page_runs(self):
        project = Path(tempfile.mkdtemp()) / "bl"
        shutil.copytree(BUTTON_LIGHT, project)
        (project / "breadboard.md").write_text("# the sheet\n")
        shown, _ = show(project)
        self.assertTrue(offer_of(shown, "build")["effect"].startswith(WIRED_BUILD_MESSAGE))
        (project / ".spark").mkdir(exist_ok=True)
        (project / ".spark" / "page-request.json").write_text(json.dumps(
            {"id": ID, "key": "build", "seen": shown["data"]["fingerprint"][:12], "at": "2026-11-24T10:00:00+01:00"}), encoding="utf-8")
        build = FakeStep("build-board")
        operation = RunRequest(operations={"pick": FakeStep("pick"), "requirements": FakeStep("requirements"), "build-board": build})
        with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
            code = run_cli(HelpText("flow.py", tool="flow"), operation, ["--project", str(project), "--json"],
                           outside_builder=build_bare_outside_world, outside=FakeOutsideWorld())
        answer = json.loads(out.getvalue())
        self.assertEqual((code, answer["data"]["ran"]), (0, True), answer)
        self.assertEqual(len(build.ran), 1)


class TheProblemsTest(WiredTest):
    def test_a_parts_phase_with_problems_keeps_its_sentence_first_and_the_wired_line_last(self):
        project = a_sheet_at(with_needs(a_built_project(), [{"id": "soil", "does": "sense"}]))
        said, code = show(project)
        self.assertEqual((code, statuses(said)["parts"]), (1, "problems"))
        self.assertIn("soil: a need with no `what` cannot be matched", says(said, "parts")[0])
        self.assertEqual(says(said, "parts")[-1], " ".join((sheet_text(), WIRED_STEP_MESSAGE)))
        self.assertEqual([item["sentence"] for item in said["problems"] if item["subject"] == "parts"], ["parts: " + says(said, "parts")[0]])


class TheDayTest(WiredTest):
    def test_a_day_is_the_local_day(self):
        self.assertEqual(wired_board.day_of("2026-11-22T23:30:00+00:00"), "23 Nov 2026")
        self.assertEqual(wired_board.day_of("2026-11-02T10:00:00+01:00"), "2 Nov 2026")

    def test_a_moment_that_does_not_parse_shows_as_written(self):
        self.assertEqual(wired_board.day_of("not a moment"), "not a moment")


class ThePageTest(WiredTest):
    def test_the_page_shows_the_line_first_in_the_parts_and_the_sentence_in_the_build_and_its_confirm(self):
        project = a_wired_project()
        write_page(project)
        text = (project / "page.html").read_text(encoding="utf-8")
        parts = text[text.index('<div id="phase-parts">'):]
        self.assertTrue(parts.startswith('<div id="phase-parts">\n<p>Done by: you</p>\n<p>%s' % html.escape(sheet_text())), parts[:300])
        build = re.search(r'<li data-key="build"[^>]*>(.*?)</li>', text).group(1)
        self.assertIn(html.escape(WIRED_BUILD_MESSAGE), build)
        words = page_words([phase.to_dict() for phase in read_flow(project)[0]])
        self.assertTrue(words["offers"]["build"]["says"][0].startswith(WIRED_BUILD_MESSAGE))


class TheTextViewTest(WiredTest):
    def test_the_parts_line_holds_the_wired_text_and_no_full_stop_meets_a_comma(self):
        for project in (a_wired_project(), a_sheet_at(a_board_log(a_deploy_project(), "ready seen", SEEN_SENTENCE))):
            lines = lines_of(project)
            parts = [line for line in lines if line.startswith("  ") and " parts: " in line]
            self.assertEqual(len(parts), 1, lines)
            self.assertIn(WIRED_STEP_MESSAGE, parts[0])
            self.assertFalse([line for line in lines if ".," in line], "no sentence ends before a comma")


class TheBoardOnlyBuildTest(WiredTest):
    def test_a_board_only_build_gets_no_wired_sentence(self):
        project = a_sheet_at(a_built_project())
        (project / "requirements.json").write_text(json.dumps({"board": "xiao-esp32-c6", "board_only": True, "parts": []}))
        effect = offer_of(show(project)[0], "build")["effect"]
        self.assertTrue(effect.startswith(BOARD_ONLY_BUILD_EFFECT), effect)
        self.assertNotIn(WIRED_BUILD_MESSAGE, effect)


class TheValueTest(WiredTest):
    def test_not_wired_has_no_data_and_changes_no_phase(self):
        self.assertIsNone(wired_board.wired_data(wired_board.NOT_WIRED))
        phases = [phase_readers.Phase(flow_codes.PARTS, None, "·", "you", [], [])]
        self.assertIs(wired_board.with_wired(Path("nowhere"), phases, wired_board.NOT_WIRED), phases)

    def test_an_empty_parts_says_gets_the_line_alone(self):
        phases = [phase_readers.Phase(flow_codes.PARTS, None, "·", "you", [], [])]
        board = wired_board.WiredBoard(None, "2026-11-23T14:09:49+01:00")
        self.assertEqual(wired_board.with_wired(Path("nowhere"), phases, board)[0].says, [" ".join((log_text(), WIRED_STEP_MESSAGE))])


if __name__ == "__main__":
    unittest.main()
