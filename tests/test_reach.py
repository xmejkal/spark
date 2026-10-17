"""P251 (#264): reach.py, the PO's bench tool, says whether the board answered and whether a cure ran."""

import contextlib
import io
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  P172: this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import reach  # noqa: E402
import tools  # noqa: E402
from board_console import Cure  # noqa: E402
from fakes import FakeConsoleProbe  # noqa: E402
from test_board_look import C6_PORT, data, done, found  # noqa: E402

REFUSED = subprocess.CalledProcessError(1, [], "", "mpremote.transport.TransportError: could not enter raw repl\n")
RESTART = Cure("rst:0x15 (USB_UART_HPSYS),boot:0x1e\n", None, True, True)


class ReachScriptTest(unittest.TestCase):
    def go(self, *argv, answers=("reached\n",), devs="mpremote-devs-one.txt", probe=None):
        """(exit code, stdout, stderr, the commands run) of reach.py with fake tools."""
        answers, ran = list(answers), []

        def run(command, **kw):
            ran.append(command)
            if "devs" in command:
                return done(data(devs))
            answer = answers.pop(0)
            if isinstance(answer, Exception):
                raise answer
            return done(answer)

        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(tools, "find", side_effect=found), contextlib.redirect_stdout(out), \
                contextlib.redirect_stderr(err):
            code = reach.main(list(argv), run=run, probe=FakeConsoleProbe(cured=RESTART) if probe is None else probe)
        return code, out.getvalue(), err.getvalue(), ran

    def test_a_board_that_answers_exits_0_and_says_the_firmware_is_stopped(self):
        code, said, _, ran = self.go()
        self.assertEqual(code, 0)
        self.assertIn("reached", said)
        self.assertIn("the firmware is stopped: press R or replug to run it", said)
        self.assertIn(["connect", C6_PORT, "exec", 'print("reached")'], [command[-4:] for command in ran])

    def test_a_cured_board_says_the_cure_and_what_it_heard(self):
        code, said, _, _ = self.go(answers=(REFUSED, "reached\n"))
        self.assertEqual(code, 0)
        self.assertIn("  cure    restart heard, the port was back\n", said)
        self.assertIn("        rst:0x15", said)

    def test_a_board_that_stays_silent_exits_2(self):
        code, said, _, _ = self.go(answers=(REFUSED, REFUSED))
        self.assertEqual(code, 2)
        self.assertIn("does not read its console", said)
        self.assertNotIn("the firmware is stopped", said)
        self.assertTrue(said.rstrip().endswith("if not  unplug the board, plug it in again, and run it again"))

    def test_json_is_one_line_with_the_cure_as_an_object_and_the_time(self):
        code, said, _, _ = self.go("--json", answers=(REFUSED, "reached\n"))
        line = json.loads(said)
        self.assertEqual(code, 0)
        self.assertEqual(sorted(line), ["at", "cure", "cure_first", "doctor", "entered", "first_try_failed", "output", "port", "reached", "why"])
        self.assertEqual(line["cure"], {"heard": RESTART.heard, "why": None, "restart_heard": True, "port_back": True, "boot_heard": False})
        self.assertFalse(line["cure_first"])
        self.assertTrue(line["first_try_failed"])

    def test_two_boards_without_a_port_list_them_and_run_nothing_on_a_board(self):
        code, _, problems, ran = self.go(devs="mpremote-devs-two.txt")
        self.assertEqual(code, 2)
        self.assertIn("reach.py --port", problems)
        self.assertEqual([command for command in ran if "exec" in command], [])

    def test_a_given_port_is_used_without_listing(self):
        code, _, _, ran = self.go("--port", "/dev/cu.usbmodem2101")
        self.assertEqual(code, 0)
        self.assertEqual([command for command in ran if "devs" in command], [])
        self.assertIn("/dev/cu.usbmodem2101", ran[0])

    def test_cure_first_cures_before_the_only_try(self):
        probe = FakeConsoleProbe(cured=RESTART)
        code, _, _, ran = self.go("--cure-first", probe=probe)
        self.assertEqual((code, probe.asked), (0, ["cure"]))
        self.assertEqual(len([command for command in ran if "exec" in command]), 1)


    def test_cure_first_says_there_was_no_first_try(self):
        code, said, _, _ = self.go("--cure-first")
        self.assertIn("  first   none: the cure came first\n", said)

    def test_cure_first_with_mpremote_not_a_python_package_runs_nothing(self):
        command = tools.Tool("mpremote", "board-shell", {"kind": "command"}, ["/usr/local/bin/mpremote"])
        ran, err = [], io.StringIO()
        with mock.patch.object(tools, "find", return_value=command), contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(err):
            code = reach.main(["--cure-first", "--port", C6_PORT], run=lambda c, **kw: ran.append(c))
        self.assertEqual(code, 2)
        self.assertIn("no cure: mpremote is not a Python package", err.getvalue())
        self.assertEqual(ran, [])

    def test_a_cure_whose_read_failed_says_why(self):
        unread = Cure("", "could not open port", False, True)
        _, said, _, _ = self.go(answers=(REFUSED, "reached\n"), probe=FakeConsoleProbe(cured=unread))
        self.assertIn("        its read failed: could not open port\n", said)
        self.assertIn("        nothing heard\n", said)

    def test_a_boot_tail_is_said_apart_from_a_restart(self):
        tail = Cure("entry 0x4086b910\nready\n", None, False, True, True)
        _, said, _, _ = self.go(answers=(REFUSED, "reached\n"), probe=FakeConsoleProbe(cured=tail))
        self.assertIn("  cure    boot tail heard, no rst: line, the port was back\n", said)


if __name__ == "__main__":
    unittest.main()
