"""P251 (#264): spark cures a board whose USB output died at power-on, and says so."""

import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  P172: this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import board_reach  # noqa: E402
from board_connection import BoardCodeError, BoardUnreachableError, RetryingBoardConnection  # noqa: E402
from board_console import Cure  # noqa: E402
from board_console import ConsoleProbe  # noqa: E402
from fakes import FakeBoardConnection, FakeClock, FakeConsoleProbe  # noqa: E402
import subprocess  # noqa: E402

#: mpremote 1.29's last line when the board's output is dead (docs/observations/2026-10-15-p235-reach-test.md).
REFUSED = BoardUnreachableError("mpremote.transport.TransportError: could not enter raw repl")
#: What the XIAO C6 printed on the cure's open (AT187).
RESTART = Cure("ESP-ROM:esp32c6-20220919\nrst:0x15 (USB_UART_HPSYS),boot:0x1e\nready\n", None, True, True)


class TheRetryTest(unittest.TestCase):
    def test_a_board_that_answers_is_reached_at_once_and_never_cured(self):
        probe = FakeConsoleProbe(cured=RESTART)
        result = board_reach.reach(FakeBoardConnection("reached\n"), probe)
        self.assertEqual(result, board_reach.ReachResult(True, "reached\n", False, None, None, True))
        self.assertEqual(probe.asked, [])

    def test_a_refused_raw_repl_is_cured_once_and_reached(self):
        board, probe = FakeBoardConnection(REFUSED, "reached\n"), FakeConsoleProbe(cured=RESTART)
        result = board_reach.reach(board, probe)
        self.assertEqual(result, board_reach.ReachResult(True, "reached\n", True, RESTART, None, True))
        self.assertEqual(probe.asked, ["cure"])
        self.assertEqual(len(board.ran), 2)

    def test_a_cure_whose_read_failed_still_retries_and_keeps_the_read_error(self):
        unread = Cure("", "could not open port", False, True)
        result = board_reach.reach(FakeBoardConnection(REFUSED, "reached\n"), FakeConsoleProbe(cured=unread))
        self.assertTrue(result.reached)
        self.assertEqual(result.cure, unread)

    def test_silent_twice_is_not_reached_and_names_both_causes(self):
        result = board_reach.reach(FakeBoardConnection(REFUSED, REFUSED), FakeConsoleProbe(cured=RESTART))
        self.assertFalse(result.reached)
        self.assertTrue(result.first_try_failed)
        self.assertEqual(result.cure, RESTART)
        self.assertIn("USB output", result.why)
        self.assertIn("does not read its console", result.why)

    def test_a_retry_that_fails_another_way_names_both_errors(self):
        late = BoardUnreachableError("no answer in 20 s")
        result = board_reach.reach(FakeBoardConnection(REFUSED, late), FakeConsoleProbe(cured=RESTART))
        self.assertFalse(result.reached)
        self.assertIn("could not enter raw repl", result.why)
        self.assertIn("no answer in 20 s", result.why)

    def test_other_first_failures_are_not_retried(self):
        for error in (BoardUnreachableError("no answer in 20 s"),
                      BoardUnreachableError("failed to access /dev/cu.usbmodem101 (it may be in use by another program)"),
                      BoardUnreachableError("[Errno 2] No such file or directory: 'mpremote'")):
            probe = FakeConsoleProbe(cured=RESTART)
            result = board_reach.reach(FakeBoardConnection(error), probe)
            self.assertEqual(result, board_reach.ReachResult(False, "", True, None, str(error), False))
            self.assertEqual(probe.asked, [])

    def test_code_with_no_answer_in_time_entered_the_board_and_is_not_retried(self):
        from board_connection import BoardTimeoutError
        probe = FakeConsoleProbe(cured=RESTART)
        result = board_reach.reach(FakeBoardConnection(BoardTimeoutError("no answer in 20 s")), probe, code="while True: pass")
        self.assertEqual((result.reached, result.entered, result.why), (False, True, "no answer in 20 s"))
        self.assertEqual(probe.asked, [])

    def test_code_that_raised_on_the_board_is_reached_and_not_retried(self):
        raised = BoardCodeError("Traceback\nNameError: name 'x' isn't defined\n", 1)
        probe = FakeConsoleProbe(cured=RESTART)
        result = board_reach.reach(FakeBoardConnection(raised), probe)
        self.assertTrue(result.reached)
        self.assertIn("NameError", result.why)
        self.assertEqual(probe.asked, [])

    def test_code_that_raised_on_the_retry_keeps_the_cure(self):
        raised = BoardCodeError("Traceback\nNameError: name 'x' isn't defined\n", 1)
        result = board_reach.reach(FakeBoardConnection(REFUSED, raised), FakeConsoleProbe(cured=RESTART))
        self.assertTrue(result.reached)
        self.assertEqual(result.cure, RESTART)

    def test_no_probe_means_no_retry_and_the_reason_is_named(self):
        result = board_reach.reach(FakeBoardConnection(REFUSED), None)
        self.assertFalse(result.reached)
        self.assertIsNone(result.cure)
        self.assertIn("no cure: mpremote is not a Python package", result.why)

    def test_cure_first_cures_then_runs_once(self):
        board, probe = FakeBoardConnection("reached\n"), FakeConsoleProbe(cured=RESTART)
        result = board_reach.reach(board, probe, cure_first=True)
        self.assertEqual(result, board_reach.ReachResult(True, "reached\n", None, RESTART, None, True))
        self.assertEqual(probe.asked, ["cure"])
        self.assertEqual(len(board.ran), 1)


    def test_cure_first_that_does_not_reach_is_not_retried_and_names_both_causes(self):
        board = FakeBoardConnection(REFUSED)
        result = board_reach.reach(board, FakeConsoleProbe(cured=RESTART), cure_first=True)
        self.assertEqual((result.reached, result.first_try_failed, result.cure), (False, None, RESTART))
        self.assertTrue(result.why.startswith("after the cure: "))
        self.assertIn("does not read its console", result.why)
        self.assertEqual(len(board.ran), 1)

    def test_an_answer_without_reached_is_not_a_reach(self):
        result = board_reach.reach(FakeBoardConnection("\n"), FakeConsoleProbe(cured=RESTART))
        self.assertFalse(result.reached)
        self.assertIn("without printing reached", result.why)

    def test_a_retry_that_fails_another_way_does_not_blame_the_board(self):
        late = BoardUnreachableError("failed to access /dev/cu.usbmodem101")
        result = board_reach.reach(FakeBoardConnection(REFUSED, late), FakeConsoleProbe(cured=RESTART))
        self.assertIn("failed to access", result.why)
        self.assertNotIn("does not read its console", result.why)

    def test_a_failed_cure_read_and_a_port_not_back_are_named_in_why(self):
        bad = Cure("", "device disconnected", False, False)
        result = board_reach.reach(FakeBoardConnection(REFUSED, REFUSED), FakeConsoleProbe(cured=bad))
        self.assertIn("the port was not back in 10 s", result.why)
        self.assertIn("its read failed: device disconnected", result.why)

class TheDecoratorTest(unittest.TestCase):
    def test_keep_running_for_reaches_the_wrapped_connection_on_both_tries(self):
        board = FakeBoardConnection(REFUSED, "ok")
        RetryingBoardConnection(board, FakeConsoleProbe(cured=RESTART)).run_code("x = 1", keep_running_for=3)
        self.assertEqual(board.ran, [("x = 1", 3), ("x = 1", 3)])

    def test_the_other_three_methods_pass_through(self):
        board = mock.Mock()
        retrying = RetryingBoardConnection(board, None)
        retrying.copy_to_board("main.py", "main.py")
        retrying.read_file("spark.json")
        retrying.repl_command()
        board.copy_to_board.assert_called_once_with("main.py", "main.py")
        board.read_file.assert_called_once_with("spark.json")
        board.repl_command.assert_called_once_with()

    def test_last_cure_is_reset_on_each_run(self):
        retrying = RetryingBoardConnection(FakeBoardConnection(REFUSED, "a", "b"), FakeConsoleProbe(cured=RESTART))
        retrying.run_code("one")
        self.assertEqual(retrying.last_cure, RESTART)
        retrying.run_code("two")
        self.assertIsNone(retrying.last_cure)



class TheRealProbeTest(unittest.TestCase):
    """A real ConsoleProbe through reach(): its read prints the restart and then fails as the port drops, and the port
    is gone for 3 looks."""

    def test_a_restart_heard_before_the_port_dropped_is_kept_and_the_retry_comes_after_the_port(self):
        events, looks = [], [False, False, False]

        def run(command, **kw):
            events.append("read")
            raise subprocess.CalledProcessError(1, command, "rst:0x15 (USB_UART_HPSYS),boot:0x1e\n",
                                                "serial.serialutil.SerialException: device reports readiness")

        def port_exists(port):
            events.append("look")
            return looks.pop(0) if looks else True

        clock = FakeClock()
        probe = ConsoleProbe(["/opt/python3"], "/dev/cu.usbmodem101", run, clock=clock, port_exists=port_exists)
        board = FakeBoardConnection(REFUSED, "reached\n")
        result = board_reach.reach(board, probe)
        self.assertTrue(result.reached)
        self.assertTrue(result.cure.restart_heard)
        self.assertTrue(result.cure.port_back)
        self.assertIn("device reports readiness", result.cure.why)
        self.assertEqual(events[0], "read")
        self.assertEqual(events.count("look"), 5)
        self.assertEqual(clock.slept[-1], 2)


if __name__ == "__main__":
    unittest.main()
