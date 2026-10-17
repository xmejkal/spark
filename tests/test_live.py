"""P247 (#267): live.py runs the code on the one port it checked the grant on, and its exit code and JSON say the answer."""

import contextlib
import datetime
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  P172: this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import board_grant  # noqa: E402
import board_look  # noqa: E402
import live  # noqa: E402
import tools  # noqa: E402
from board_console import Cure  # noqa: E402
from fakes import FakeConsoleProbe  # noqa: E402
from test_board_look import C6_PORT, data, done  # noqa: E402
from test_deploy import found  # noqa: E402

NOW = datetime.datetime(2026, 10, 17, 9, 0, tzinfo=datetime.timezone.utc)
MAC = "8c:bf:ea:xx:xx:xx"
RESTART = Cure("rst:0x15 (USB_UART_HPSYS),boot:0x1e\n", None, True, True)


class LiveScriptTest(unittest.TestCase):
    """A scratch store with a grant for P228's bench C6, and a project whose board is the XIAO ESP32-C6."""

    def setUp(self):
        home = Path(tempfile.mkdtemp())
        patcher = mock.patch.dict(os.environ, {"SPARK_HOME": str(home)})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.project = Path(tempfile.mkdtemp())
        (self.project / "boards").mkdir()
        (self.project / "boards" / "active.json").write_text(json.dumps({"schema": 1, "board": "xiao-esp32-c6"}))
        board_grant.GrantStore().save(board_grant.Grant(MAC, board_look.board_token(MAC), "petr", NOW.isoformat(),
                                                        (NOW + datetime.timedelta(minutes=30)).isoformat()))

    def go(self, *argv, answers=("1\n", ""), devs="mpremote-devs-one.txt", minutes_later=0):
        """(exit code, stdout, stderr, the commands run) of live.py with fake tools."""
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
        argv = ["--project", str(self.project)] + list(argv)
        with mock.patch.object(tools, "find", side_effect=found), contextlib.redirect_stdout(out), \
                contextlib.redirect_stderr(err):
            code = live.main(argv, run=run, probe=FakeConsoleProbe(cured=RESTART),
                             now=lambda: NOW + datetime.timedelta(minutes=minutes_later))
        return code, out.getvalue(), err.getvalue(), ran

    def test_print_1_runs_on_the_checked_port_and_the_board_is_reset(self):
        code, said, _, ran = self.go("--code", "print(1)", "--json")
        line = json.loads(said)
        self.assertEqual(code, 0)
        self.assertEqual((line["answer"], line["output"], line["reset"], line["port"]), ("ran", "1\n", "done", C6_PORT))
        self.assertEqual([command[-4:] for command in ran if "devs" not in command],
                         [["connect", C6_PORT, "exec", "print(1)"], ["mpremote", "connect", C6_PORT, "reset"]])
        self.assertEqual(sorted(line), ["answer", "cure", "gpio_numbers_in_code", "grant_why", "output", "pins_checked",
                                        "port", "reset", "why"])

    def test_an_ended_grant_exits_1_with_its_code_and_runs_nothing_on_the_board(self):
        code, said, _, ran = self.go("--code", "print(1)", "--json", minutes_later=31)
        line = json.loads(said)
        self.assertEqual((code, line["answer"], line["grant_why"]), (1, "refused_no_grant", "expired"))
        self.assertEqual([command for command in ran if "devs" not in command], [])

    def test_code_that_does_not_parse_exits_1(self):
        code, said, _, ran = self.go("--code", "print(")
        self.assertEqual(code, 1)
        self.assertIn("answer  refused_no_parse", said)
        self.assertEqual([command for command in ran if "devs" not in command], [])

    def test_two_boards_without_a_port_name_live_py_and_exit_2(self):
        code, said, problems, ran = self.go("--code", "print(1)", "--json", devs="mpremote-devs-two.txt")
        self.assertEqual(code, 2)
        self.assertIn("live.py --port", problems)
        self.assertEqual(json.loads(said)["answer"], "could-not-run")
        self.assertEqual([command for command in ran if "devs" not in command], [])

    def test_a_broken_record_exits_2(self):
        (self.project / "boards" / "active.json").write_text(json.dumps({"schema": 1, "board": "no-such-board"}))
        code, _, problems, _ = self.go("--code", "print(1)")
        self.assertEqual(code, 2)
        self.assertIn("no board definition for 'no-such-board'", problems)

    def test_a_silent_board_exits_2_and_is_not_reset(self):
        refused = subprocess.CalledProcessError(1, [], "", "mpremote.transport.TransportError: could not enter raw repl\n")
        code, said, _, ran = self.go("--code", "print(1)", answers=(refused, refused))
        self.assertEqual(code, 2)
        self.assertIn("does not read its console", said)
        self.assertEqual([command for command in ran if "reset" in command], [])

    def test_the_text_lists_the_gpio_numbers_in_the_code(self):
        code, said, _, _ = self.go("--code", "from machine import Pin\nPin(15, Pin.OUT).value(1)", answers=("", ""))
        self.assertEqual(code, 0)
        self.assertIn("  gpio    the code writes 1, 15, each a GPIO of this board\n", said + "\n")


if __name__ == "__main__":
    unittest.main()
