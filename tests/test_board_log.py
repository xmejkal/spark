"""
P1043 (#1533): the board log, `sim/runs/board/<moment>.log`, written after a flash and read by the deploy reader. A log
gets a reason line with its cause's code. An older log with none gets the cause of its sentence's fixed start, and an
unknown start gets none. The reader takes the time, the image, the verdict and the cause, never the port or the console.

    python3 -m unittest tests.test_board_log
"""

import datetime
import hashlib
import sys
import tempfile
import unittest
from collections import namedtuple
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from spark.bench import board_connection, board_log, download_mode, ready_probe  # noqa: E402
from spark.flow import flow_codes  # noqa: E402
from fakes import FakeBoardConnection  # noqa: E402

MAIN = {"/main.py": hashlib.sha256(b"print('ready')\n").hexdigest()}
HASHES = "file %s /main.py\n" % MAIN["/main.py"]
MOMENT = datetime.datetime(2026, 11, 23, 14, 9, 49, tzinfo=datetime.timezone(datetime.timedelta(hours=1)))
#: The RESET button's place, as a board record gives it.
Places = namedtuple("Places", "reset orientation")
PLACES = Places("RESET (R)", ", top left")


def probe(*answers, expected=MAIN):
    """The sentence of `ReadyProbe.check` for the fake board's `answers`."""
    return ready_probe.ReadyProbe(FakeBoardConnection(*answers)).check(expected)


def a_log(verdict="ready unknown", sentence="mpremote could not read the board's files: x", reason=None, **kw):
    """A BoardLog in today's layout, with made-up values."""
    return board_log.BoardLog(**dict(dict(moment=MOMENT, port="/dev/cu.usbmodem101", image_sha256="ab" * 32,
                                          facts_line="facts file spark.json sha256: f", verdict=verdict, sentence=sentence,
                                          heard="what the board printed\n", simulation="passed"), **kw), reason=reason)


def a_project_with(*texts):
    """A project whose sim/runs/board/ holds each text as a log, named in order of `texts`."""
    project = Path(tempfile.mkdtemp())
    folder = project / "sim" / "runs" / "board"
    folder.mkdir(parents=True)
    for index, text in enumerate(texts):
        (folder / ("2026-11-23T14-09-%02d.log" % index)).write_bytes(text if isinstance(text, bytes) else text.encode())
    return project


class TheCauseOfASentenceTest(unittest.TestCase):
    """P1043-D2 (b): an old log with no reason line gets its cause from the start of spark's own sentence, before its first
    colon. Each fixed start is the start of the sentence the bench makes for its code (test 17)."""

    def test_each_fixed_start_is_the_start_of_the_sentence_the_bench_makes_for_its_code(self):
        made = {"files_unread": probe(board_connection.BoardCodeError("Traceback\n", 1)).sentence,
                "firmware_not_started": probe(HASHES, board_connection.BoardUnreachableError("could not enter raw repl", "")).sentence,
                "no_files_named": probe(expected={}).sentence,
                "firmware_error": probe(HASHES, board_connection.BoardCodeError("Traceback\nValueError: x\n", 1)).sentence,
                "no_ready_line": probe(HASHES, "nothing\n").sentence,
                "port_gone": download_mode.port_gone(PLACES),
                "download_mode_stayed": download_mode.no_reset(PLACES)}
        self.assertEqual({code: board_log.cause_of(sentence) for code, sentence in made.items()}, {code: code for code in made})
        self.assertEqual(sorted(board_log.CAUSES.values()), sorted(made))

    def test_the_flow_has_words_for_each_cause_the_log_can_hold(self):
        # P1043-D1: the codes and their starts are the bench's, the words the flow's; a lost board and files that differ have no start
        self.assertEqual(sorted(flow_codes.CAUSE_WORDS), sorted(set(board_log.CAUSES.values()) | {"board_lost", "files_differ"}))

    def test_a_lost_board_has_its_own_start_and_files_that_differ_have_none(self):
        # the review of #1579: the lost board's sentence holds mpremote's text before its first colon, so its start is its own
        lost = board_connection.BoardUnreachableError("OSError: [Errno 6] Device not configured", "ready\n")
        self.assertEqual(board_log.cause_of(probe(HASHES, lost).sentence), "board_lost")
        self.assertIsNone(board_log.cause_of(probe("file %s /main.py\n" % ("0" * 64), "ready\n").sentence))

    def test_an_old_log_with_a_read_again_gives_no_files_unread_and_a_reason_line_still_wins(self):
        heard = "the first read: ready unknown: mpremote could not start the firmware: x\nread again\n"
        for reason, cause in ((None, None), ("firmware_not_started", "firmware_not_started")):
            with self.subTest(reason=reason):
                log = a_log(sentence="mpremote could not read the board's files: x", heard=heard, reason=reason)
                self.assertEqual(board_log.newest_logged_deploy(a_project_with(log.text()))[1].cause, cause)
        log = a_log(sentence="mpremote could not read the board's files: x")
        self.assertEqual(board_log.newest_logged_deploy(a_project_with(log.text()))[1].cause, "files_unread")

    def test_an_unknown_start_gives_no_cause_never_the_start(self):
        for sentence in ("the board said something new (x: y)", "", "mpremote: anything", "the firmware printed 'ready'"):
            with self.subTest(sentence=sentence):
                self.assertIsNone(board_log.cause_of(sentence))


class TheReasonLineTest(unittest.TestCase):
    """Test 18: with a reason, `BoardLog` writes `reason: <code>` as line 4; with none, today's bytes."""

    def test_a_log_with_a_reason_writes_it_as_line_4(self):
        lines = a_log(reason="files_unread").text().splitlines()
        self.assertEqual(lines[:5], ["# deploy 2026-11-23T14:09:49+01:00 on /dev/cu.usbmodem101", "image sha256: " + "ab" * 32,
                                     "simulation: passed", "reason: files_unread", "facts file spark.json sha256: f"])

    def test_a_log_with_no_reason_is_today_s_text(self):
        self.assertNotIn("reason:", a_log().text())
        self.assertEqual(a_log().text().splitlines()[3], "facts file spark.json sha256: f")

    def test_the_reader_reads_the_reason_back_and_a_log_of_today_s_format(self):
        for log, cause in ((a_log(reason="board_lost"), "board_lost"), (a_log(), "files_unread")):
            with self.subTest(cause=cause):
                count, logged = board_log.newest_logged_deploy(a_project_with(log.text()))
                self.assertEqual((count, logged), (1, board_log.LoggedDeploy("2026-11-23T14:09:49+01:00", "ab" * 32, "ready unknown", cause)))

    def test_no_log_is_none(self):
        self.assertEqual(board_log.newest_logged_deploy(Path(tempfile.mkdtemp())), (0, None))


class TheUnreadableLogTest(unittest.TestCase):
    """Test 19: a log that is not UTF-8, or misses its moment, image or verdict line, cannot be read."""

    def test_a_log_that_is_not_utf_8_cannot_be_read(self):
        with self.assertRaises(board_log.BoardLogError) as raised:
            board_log.newest_logged_deploy(a_project_with(b"# deploy \xff\xfe on x\n"))
        self.assertEqual(raised.exception.code, "board_log_unreadable")
        self.assertIn("sim/runs/board/2026-11-23T14-09-00.log", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
