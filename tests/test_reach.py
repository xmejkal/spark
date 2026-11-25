"""P251 (#264): reach.py, the PO's bench tool, says whether the board answered and whether a cure ran."""

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
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import reach  # noqa: E402
from spark.bench import known_board  # noqa: E402
from spark.records import tool_finder  # noqa: E402
from spark.bench.board_console import Cure  # noqa: E402
from fakes import FakeClock, FakeConsoleProbe, FakeOutsideWorld, FakeProbePlatform, know_the_board  # noqa: E402
from spark.bench.reach_board import ReachBoard  # noqa: E402
from test_board_look import C6_MAC, C6_PORT, data, done, found  # noqa: E402

MOMENT = datetime.datetime(2026, 10, 17, 9, 0, tzinfo=datetime.timezone.utc)
REFUSED = subprocess.CalledProcessError(1, [], "", "mpremote.transport.TransportError: could not enter raw repl\n")
RESTART = Cure("rst:0x15 (USB_UART_HPSYS),boot:0x1e\n", None, True, True)


class ReachCase(unittest.TestCase):
    """The helpers only, so a subclass does not run ReachScriptTest's tests again (P1057)."""

    def setUp(self):
        home = Path(tempfile.mkdtemp())  # P892: a store of its own, which keeps the C6 for the project, here
        patcher = mock.patch.dict(os.environ, {"SPARK_HOME": str(home)})
        patcher.start()
        self.addCleanup(patcher.stop)
        know_the_board(Path("."), C6_MAC, known_board.comparable_key(C6_MAC))

    def world(self, answers=("reached\n",), devs="mpremote-devs-one.txt", devs_text=None):
        """A FakeOutsideWorld whose `run` answers mpremote devs from a fixture and the exec of each of `answers` in turn.
        `devs` is one fixture, or a tuple of fixtures, one for each list in turn, the last for every list after it (P1057)."""
        answers, lists = list(answers), [devs] if isinstance(devs, str) else list(devs)

        def run(command, **kw):
            if "devs" in command:
                return done(data(lists.pop(0) if len(lists) > 1 else lists[0]) if devs_text is None else devs_text)
            answer = answers.pop(0)
            if isinstance(answer, Exception):
                raise answer
            return done(answer)
        return FakeOutsideWorld(run=run, find_tool=found, clock=FakeClock(MOMENT))

    def operation(self, probe=None):
        """The ReachBoard with a platform whose console probe is `probe` (default: one whose cure restarts the board)."""
        probe = FakeConsoleProbe(cured=RESTART) if probe is None else probe
        return ReachBoard(platform_for=lambda project, find_tool: FakeProbePlatform(project, probe, find_tool))

    def go(self, *argv, answers=("reached\n",), devs="mpremote-devs-one.txt", probe=None, devs_text=None):
        """(exit code, stdout, stderr, the commands run) of reach.py with fake tools."""
        outside = self.world(answers, devs, devs_text)
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = reach.main(list(argv), outside=outside, operation=self.operation(probe))
        return code, out.getvalue(), err.getvalue(), outside.ran


class ReachScriptTest(ReachCase):
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
        self.assertEqual(sorted(line), ["at", "cure", "cure_first", "doctor", "entered", "first_try_failed", "fix", "output", "port", "reached",
                                        "why"])
        self.assertEqual(line["at"], "2026-10-17T09:00:00+0000", "the time is the outside's clock")
        self.assertEqual(line["cure"], {"heard": RESTART.heard, "why": None, "restart_heard": True, "port_back": True, "boot_heard": False})
        self.assertFalse(line["cure_first"])
        self.assertTrue(line["first_try_failed"])

    def test_two_boards_without_a_port_list_them_and_run_nothing_on_a_board(self):
        code, _, problems, ran = self.go(devs="mpremote-devs-two.txt")
        self.assertEqual(code, 2)
        self.assertIn("reach.py --port", problems)
        self.assertEqual([command for command in ran if "exec" in command], [])

    def test_a_given_port_is_listed_once_and_then_used(self):
        code, _, _, ran = self.go("--port", "/dev/cu.usbmodem2101", devs_text=data("mpremote-devs-one.txt").replace(C6_PORT, "/dev/cu.usbmodem2101"))
        self.assertEqual(code, 0)
        self.assertEqual(len([command for command in ran if "devs" in command]), 1)
        self.assertIn("/dev/cu.usbmodem2101", ran[1])

    def test_cure_first_cures_before_the_only_try(self):
        probe = FakeConsoleProbe(cured=RESTART)
        code, _, _, ran = self.go("--cure-first", probe=probe)
        self.assertEqual((code, probe.asked), (0, ["cure"]))
        self.assertEqual(len([command for command in ran if "exec" in command]), 1)


    def test_cure_first_says_there_was_no_first_try(self):
        code, said, _, _ = self.go("--cure-first")
        self.assertIn("  first   none: the cure came first\n", said)

    def test_cure_first_with_mpremote_not_a_python_package_runs_nothing(self):
        command = tool_finder.Tool("mpremote", "board-shell", {"kind": "command"}, ["/usr/local/bin/mpremote"])
        outside = FakeOutsideWorld(run=lambda c, **kw: done(data("mpremote-devs-one.txt")), find_tool=lambda name, **where: command)
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = reach.main(["--cure-first", "--port", C6_PORT], outside=outside)
        self.assertEqual((code, out.getvalue()), (2, ""))
        self.assertIn("reach.py: no cure: mpremote is not a Python package", err.getvalue())
        self.assertEqual([ran[-1] for ran in outside.ran], ["devs"])
        result = ReachBoard().run(project=Path("."), port=C6_PORT, cure_first=True, outside=outside)
        self.assertEqual([(found.severity, found.code) for found in result.findings], [("could-not-run", "no_probe")])
        self.assertIsNone(result.data)

    def test_a_cure_whose_read_failed_says_why(self):
        unread = Cure("", "could not open port", False, True)
        _, said, _, _ = self.go(answers=(REFUSED, "reached\n"), probe=FakeConsoleProbe(cured=unread))
        self.assertIn("        its read failed: could not open port\n", said)
        self.assertIn("        nothing heard\n", said)

    def test_a_boot_tail_is_said_apart_from_a_restart(self):
        tail = Cure("entry 0x4086b910\nready\n", None, False, True, True)
        _, said, _, _ = self.go(answers=(REFUSED, "reached\n"), probe=FakeConsoleProbe(cured=tail))
        self.assertIn("  cure    boot tail heard, no rst: line, the port was back\n", said)

    # --- MVP --- (P430, #569) the printed lines are guarded, the --json values stay raw
    def test_a_port_with_a_bidi_character_shows_guarded_and_json_keeps_it_raw(self):
        port = "/dev/x\u202ey"
        listed = data("mpremote-devs-one.txt").replace(C6_PORT, port)
        _, said, _, _ = self.go("--port", port, devs_text=listed)
        self.assertIn("  port    /dev/x?y\n", said)
        _, said, _, _ = self.go("--port", port, "--json", devs_text=listed)
        self.assertEqual(json.loads(said)["port"], port)

    def test_what_the_cure_heard_and_why_it_failed_show_guarded_and_json_keeps_them_raw(self):
        heard = Cure("boot\x1b[31m\u202e x\n", "no\u202eread", False, True)
        _, said, _, _ = self.go(answers=(REFUSED, "reached\n"), probe=FakeConsoleProbe(cured=heard))
        self.assertIn("        its read failed: no?read\n", said)
        self.assertIn("        boot?[31m? x\n", said)
        _, said, _, _ = self.go("--json", answers=(REFUSED, "reached\n"), probe=FakeConsoleProbe(cured=heard))
        self.assertEqual(json.loads(said)["cure"]["heard"], heard.heard)

    def test_a_device_name_in_the_two_boards_stop_shows_guarded(self):
        devs = data("mpremote-devs-two.txt").replace("usbserial-1410", "usbser\u202eial")
        code, _, problems, _ = self.go(devs_text=devs)
        self.assertEqual(code, 2)
        self.assertIn("/dev/cu.usbser?ial", problems)
        self.assertNotIn("\u202e", problems)

    def test_a_tools_list_word_in_the_no_doctor_line_shows_guarded(self):
        shell = tool_finder.Tool("mpremote\u202e", "board-shell",
                                 {"kind": "python", "module": "mpremote", "silent_step": "erase"},
                                 ["/opt/python3"])
        with mock.patch.dict(found.__globals__["FOUND"], {"board-shell": shell}):
            code, _, problems, _ = self.go(answers=(REFUSED, REFUSED))
        self.assertEqual(code, 2)
        self.assertTrue(problems.startswith("reach.py: no doctor: the tools list gives mpremote? the silent_step"), problems)
        self.assertNotIn("\u202e", problems)

    def test_a_newline_in_the_project_path_cannot_fake_a_line_of_a_tool_problem(self):
        project = Path(tempfile.mkdtemp()) / "a\nGRANTED: board ok"
        (project / ".spark").mkdir(parents=True)
        (project / ".spark" / "tools.json").write_text("not json")
        err = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            code = reach.main(["--project", str(project)])
        self.assertEqual(code, 2)
        self.assertEqual(len(err.getvalue().splitlines()), 1, err.getvalue())
        self.assertIn("a?GRANTED: board ok", err.getvalue())

    def test_a_newline_in_a_tool_s_name_in_the_tools_file_cannot_fake_a_line(self):
        project = Path(tempfile.mkdtemp())
        (project / ".spark").mkdir()
        name = "mpre\nGRANTED: board ok"
        (project / ".spark" / "tools.json").write_text(json.dumps(
            {name: {"kind": "command", "command": "mpremote", "meets": ["board-shell"]}, "roles": {"board-shell": name}}))
        err = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            code = reach.main(["--project", str(project)])
        self.assertEqual(code, 2)
        self.assertEqual([line for line in err.getvalue().splitlines() if line.startswith("GRANTED")], [])
        self.assertIn("'mpre\\nGRANTED: board ok'", err.getvalue())

    def test_a_newline_in_a_needs_name_in_the_tools_file_cannot_fake_a_line(self):
        project = Path(tempfile.mkdtemp())
        (project / ".spark").mkdir()
        (project / ".spark" / "tools.json").write_text(json.dumps({"mpremote": {"needs": ["py\nGRANTED: board ok"]}}))
        err = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            code = reach.main(["--project", str(project)])
        self.assertEqual(code, 2)
        self.assertEqual([line for line in err.getvalue().splitlines() if line.startswith("GRANTED")], [])

    def test_a_bad_argument_with_json_is_the_usage_on_stderr_and_no_line(self):
        out, err = io.StringIO(), io.StringIO()
        with self.assertRaises(SystemExit) as raised, contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            reach.main(["--bogus", "--json"], outside=self.world(), operation=self.operation())
        self.assertEqual((raised.exception.code, out.getvalue()), (2, ""))
        self.assertTrue(err.getvalue().startswith("usage: reach.py "), err.getvalue())

    def test_a_crash_with_json_prints_no_line_and_the_traceback_on_stderr(self):
        code, said, problems, _ = self.go("--json", answers=(RuntimeError("boom"),))
        self.assertEqual((code, said), (2, ""))
        self.assertIn("Traceback (most recent call last):", problems)
        self.assertIn("reach: crashed, RuntimeError", problems)

    def test_a_board_that_answers_is_no_finding_and_a_silent_one_is_one_unchecked_item(self):
        answered = self.operation().run(project=Path("."), port=None, cure_first=False, outside=self.world())
        self.assertEqual((answered.status(), answered.findings), ("ok", []))
        silent = self.operation().run(project=Path("."), port=None, cure_first=False, outside=self.world(answers=(REFUSED, REFUSED)))
        self.assertEqual([(found.severity, found.code, found.subject) for found in silent.findings], [("could-not-run", "not_reached", None)])
        self.assertIn("does not read its console", silent.findings[0].sentence)
        self.assertTrue(silent.findings[0].fix.startswith("press the board's RESET once"), silent.findings[0].fix)
        self.assertEqual(silent.status(), "could-not-run")

    def test_a_stop_before_the_try_has_no_data_and_the_code_of_the_stop(self):
        stopped = self.operation().run(project=Path("."), port=None, cure_first=False, outside=self.world(devs="mpremote-devs-two.txt"))
        self.assertEqual((stopped.data, [found.code for found in stopped.findings]), (None, ["two_boards"]))
        self.assertTrue(stopped.diagnostics[0].startswith("reach.py: "), stopped.diagnostics)


class ASleepingBoardTest(ReachCase):
    """P1057: with no board on USB, or a named port that is not, and a firmware/ that calls deepsleep, reach.py says the
    asleep fix on stderr, as look.py does, and not the cable advice. Its --json prints nothing on such a stop (P1057's D4)."""

    def setUp(self):
        super().setUp()
        self.project = Path(tempfile.mkdtemp())
        (self.project / "firmware").mkdir()
        (self.project / "firmware" / "main.py").write_text("import machine\nmachine.deepsleep(1)\n")

    def test_no_board_gives_no_board_found_and_the_asleep_fix_and_no_json_line(self):
        for argv in ((), ("--json",)):
            with self.subTest(argv=argv):
                code, said, problems, ran = self.go("--project", str(self.project), *argv, devs="mpremote-devs-none.txt")
                lines = problems.splitlines()
                self.assertEqual((code, said, lines[0], len(lines)), (2, "", "reach.py: no board found.", 2))
                self.assertTrue(lines[1].startswith("What spark knows: no board is on USB, and the project's firmware calls "
                                                    "deepsleep (firmware/main.py:2)."), lines[1])
                self.assertEqual([command for command in ran if "devs" not in command], [])

    def test_a_named_port_not_on_usb_opens_the_fix_with_that_port(self):
        code, _, problems, _ = self.go("--project", str(self.project), "--port", "/dev/cu.usbmodem9")
        lines = problems.splitlines()
        self.assertEqual((code, lines[0]), (2, "reach.py: no board on /dev/cu.usbmodem9: mpremote devs does not list it."))
        self.assertTrue(lines[1].startswith("What spark knows: the port you named is not on USB, and the project's firmware"), lines[1])

    def doctor_road(self, *argv):
        """(exit code, stdout, stderr) of reach.py whose exec is refused twice, the board gone from USB from the exec on."""
        know_the_board(self.project, C6_MAC, known_board.comparable_key(C6_MAC))  # P892: no question on the kept board
        code, said, problems, _ = self.go("--project", str(self.project), *argv, answers=(REFUSED, REFUSED),
                                          devs=("mpremote-devs-one.txt", "mpremote-devs-none.txt"))
        return code, said, problems

    def test_after_the_doctor_an_unnamed_port_gets_the_fix_with_its_own_opening_in_place_of_the_cable_step(self):
        # P1057 PR 2 (D3, R3): the doctor said plug_in; the asleep fix takes the next line's place, as in look.py
        code, said, _ = self.doctor_road()
        nexts = [line for line in said.splitlines() if line.lstrip().startswith("next    ")]
        self.assertEqual((code, len(nexts)), (2, 1))
        self.assertIn("next    What spark knows: the port that spark found on USB is not on USB any more, and the project's", nexts[0])
        self.assertNotIn("plug the board straight", said)

    def test_after_the_doctor_a_named_port_gets_the_fix_with_the_named_opening(self):
        code, said, _ = self.doctor_road("--port", C6_PORT)
        self.assertEqual(code, 2)
        self.assertIn("next    What spark knows: the port you named is not on USB, and the project's firmware", said)
        self.assertNotIn("plug the board straight", said)

    def test_after_the_doctor_the_json_line_ends_with_the_look_and_keeps_what_the_doctor_saw(self):
        # R3: the look that needs the person; L4: mpremote never got in; L2: doctor.next_step stays the doctor's own
        code, said, _ = self.doctor_road("--json")
        line = json.loads(said)
        self.assertEqual((code, line["reached"], line["entered"], line["doctor"]["next_step"]), (2, False, False, "plug_in"))
        self.assertEqual((line["next"][0]["op"], line["next"][0]["needs_person"]), ("look", True))

    def test_after_the_doctor_the_json_line_s_fix_is_the_text_s_next_line(self):
        # P1055 on the doctor road: the asleep fix, before `next`, where doctor.next_step still says plug_in
        _, said, _ = self.doctor_road()
        (step,) = [line for line in said.splitlines() if line.lstrip().startswith("next    ")]
        line = json.loads(self.doctor_road("--json")[1])
        self.assertEqual((line["fix"], list(line)[-2:]), (step.lstrip()[len("next    "):], ["fix", "next"]))

    def test_after_the_doctor_a_firmware_with_no_deepsleep_call_keeps_the_cable_step(self):
        (self.project / "firmware" / "main.py").write_text("import machine\nmachine.lightsleep(1)\n")
        code, said, _ = self.doctor_road()
        self.assertEqual(code, 2)
        self.assertIn("next    plug the board straight into the computer", said)
        self.assertNotIn("What spark knows", said)
        (step,) = [line for line in said.splitlines() if line.lstrip().startswith("next    ")]
        line = json.loads(self.doctor_road("--json")[1])
        self.assertNotIn("next", line)
        self.assertEqual(line["fix"], step.lstrip()[len("next    "):])  # P1055: the doctor's plug_in sentence, the text's next line

    def test_without_a_deepsleep_call_the_stop_is_as_before(self):
        (self.project / "firmware" / "main.py").write_text("import machine\nmachine.lightsleep(1)\n")
        code, _, problems, _ = self.go("--project", str(self.project), devs="mpremote-devs-none.txt")
        self.assertEqual((code, problems.splitlines()), (2, ["reach.py: no board found. Plug it straight into the computer with a "
                                                             "data cable, not a hub that gives power only. If the plug is USB-C, "
                                                             "turn it around, or use a USB-A to USB-C cable."]))

    def test_the_help_says_a_board_in_download_mode_runs_no_firmware(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), self.assertRaises(SystemExit):
            reach.main(["--help"], outside=FakeOutsideWorld())
        said = " ".join(out.getvalue().split())
        self.assertIn("download mode", said)
        self.assertIn("runs no firmware", said)


if __name__ == "__main__":
    unittest.main()
