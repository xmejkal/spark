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
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from spark.bench import board_grant  # noqa: E402
from spark.bench import board_look  # noqa: E402
from spark.bench import known_board  # noqa: E402
import live  # noqa: E402
from spark.records import tool_finder  # noqa: E402
from spark.bench.board_console import Cure  # noqa: E402
from fakes import FakeClock, FakeConsoleProbe, FakeOutsideWorld, FakeProbePlatform, know_the_board  # noqa: E402
from spark.bench.run_live_code import RunLiveCode  # noqa: E402
from test_board_look import C6_PORT, data, done  # noqa: E402
from test_deploy import found  # noqa: E402

NOW = datetime.datetime(2026, 10, 17, 9, 0, tzinfo=datetime.timezone.utc)
MAC = "8c:bf:ea:xx:xx:xx"
RESTART = Cure("rst:0x15 (USB_UART_HPSYS),boot:0x1e\n", None, True, True)


class LiveCase(unittest.TestCase):
    """A scratch store with a grant for P228's bench C6, and a project whose board is the XIAO ESP32-C6: the helpers only,
    so a subclass does not run LiveScriptTest's tests again (P1057)."""

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
        know_the_board(self.project, MAC, known_board.comparable_key(MAC))  # P892: live runs on the kept board with no question

    def world(self, answers=("1\n", ""), devs="mpremote-devs-one.txt", minutes_later=0):
        """A FakeOutsideWorld whose `run` answers mpremote devs from a fixture, then the exec and the reset from `answers` in turn.
        `devs` is one fixture, or a tuple of fixtures, one for each list in turn, the last for every list after it (P1057)."""
        answers, lists = list(answers), [devs] if isinstance(devs, str) else list(devs)

        def run(command, **kw):
            if "devs" in command:
                return done(data(lists.pop(0) if len(lists) > 1 else lists[0]))
            answer = answers.pop(0)
            if isinstance(answer, Exception):
                raise answer
            return done(answer)
        return FakeOutsideWorld(run=run, find_tool=found, clock=FakeClock(NOW + datetime.timedelta(minutes=minutes_later)))

    def platform_for(self, project, find_tool, probe=None):
        """The FakeProbePlatform of a run: the probe is `probe`, or one whose cure restarts the board."""
        return FakeProbePlatform(project, probe or FakeConsoleProbe(cured=RESTART), find_tool)

    def go(self, *argv, answers=("1\n", ""), devs="mpremote-devs-one.txt", minutes_later=0, probe=None):
        """(exit code, stdout, stderr, the commands run) of live.py with fake tools."""
        outside = self.world(answers, devs, minutes_later)
        out, err = io.StringIO(), io.StringIO()
        argv = ["--project", str(self.project)] + list(argv)
        operation = RunLiveCode(platform_for=lambda project, find_tool: self.platform_for(project, find_tool, probe))
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = live.main(argv, outside=outside, operation=operation)
        return code, out.getvalue(), err.getvalue(), outside.ran


class LiveScriptTest(LiveCase):
    def test_print_1_runs_on_the_checked_port_and_the_board_is_reset(self):
        code, said, _, ran = self.go("--code", "print(1)", "--json")
        line = json.loads(said)
        self.assertEqual(code, 0)
        self.assertEqual((line["answer"], line["output"], line["reset"], line["port"]), ("ran", "1\n", "done", C6_PORT))
        self.assertEqual([command[command.index("connect"):] for command in ran if "devs" not in command],
                         [["connect", C6_PORT, "exec", "print(1)"], ["connect", C6_PORT, "reset"]])
        self.assertEqual(sorted(line), ["answer", "cure", "doctor", "gpio_numbers_in_code", "grant_why", "output", "pins_checked",
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

    def test_an_unreadable_grant_file_is_no_grant_and_runs_nothing(self):
        grant = Path(os.environ["SPARK_HOME"]) / "grants" / "8c-bf-ea-xx-xx-xx.json"
        grant.chmod(0)
        self.addCleanup(grant.chmod, 0o600)
        code, said, _, ran = self.go("--code", "print(1)", "--json")
        self.assertEqual((code, json.loads(said)["grant_why"]), (1, "not a grant"))
        self.assertEqual([command for command in ran if "devs" not in command], [])

    def test_a_given_port_reaches_the_grant_check_the_run_and_the_reset(self):
        code, said, _, ran = self.go("--code", "print(1)", "--port", C6_PORT)
        self.assertEqual(code, 0)
        self.assertEqual([command[-1] for command in ran if C6_PORT in command], ["print(1)", "reset"])

    def test_could_not_run_json_holds_every_field(self):
        code, said, _, _ = self.go("--code", "print(1)", "--json", devs="mpremote-devs-two.txt")
        self.assertEqual(sorted(json.loads(said)), ["answer", "cure", "doctor", "gpio_numbers_in_code", "grant_why", "output",
                                                    "pins_checked", "port", "reset", "why"])

    def test_a_broken_record_exits_2(self):
        (self.project / "boards" / "active.json").write_text(json.dumps({"schema": 1, "board": "no-such-board"}))
        code, _, problems, _ = self.go("--code", "print(1)")
        self.assertEqual(code, 2)
        self.assertIn("no board definition for 'no-such-board'", problems)

    def test_the_board_requirements_json_names_is_the_one_checked_not_the_selection(self):
        # P988 (D35): the walk's selection named one board and its requirements another; live.py checks the requirements'
        (self.project / "boards" / "active.json").write_text(json.dumps({"schema": 1, "board": "no-such-board"}))
        (self.project / "requirements.json").write_text(json.dumps({"board": "xiao-esp32-c6"}))
        code, _, problems, _ = self.go("--code", "print(1)")
        self.assertEqual(code, 0, problems)

    def test_a_board_requirements_json_names_that_no_record_holds_exits_2_over_a_good_selection(self):
        (self.project / "requirements.json").write_text(json.dumps({"board": "no-such-board"}))
        code, _, problems, _ = self.go("--code", "print(1)")
        self.assertEqual(code, 2)
        self.assertIn("no board definition for 'no-such-board'", problems)

    def test_a_silent_board_exits_2_and_is_not_reset(self):
        refused = subprocess.CalledProcessError(1, [], "", "mpremote.transport.TransportError: could not enter raw repl\n")
        code, said, _, ran = self.go("--code", "print(1)", answers=(refused, refused))
        self.assertEqual(code, 2)
        self.assertIn("does not read its console", said)
        self.assertEqual([command for command in ran if "reset" in command], [])
        self.assertIn("  check   console: the console was silent for 2 s (a firmware that prints nothing and a board that does "
                      "not answer sound the same here)\n", said)
        self.assertTrue(said.rstrip().endswith("if not  unplug the board, plug it in again, and run it again"))

    def test_a_silent_board_s_json_carries_the_doctor_s_codes(self):
        refused = subprocess.CalledProcessError(1, [], "", "mpremote.transport.TransportError: could not enter raw repl\n")
        code, said, _, _ = self.go("--code", "print(1)", "--json", answers=(refused, refused))
        doctor = json.loads(said)["doctor"]
        self.assertEqual((code, doctor["next_step"], doctor["if_not_helped"]), (2, "press_reset", "replug"))
        self.assertEqual([check["name"] for check in doctor["checks"]], ["port-listed", "console"])

    def test_a_port_mpremote_could_not_open_gets_the_doctor_and_no_reset(self):
        busy = subprocess.CalledProcessError(1, [], "", "failed to access %s (it may be in use by another program)\n" % C6_PORT)
        code, said, _, ran = self.go("--code", "print(1)", "--json", answers=(busy,))
        line = json.loads(said)
        self.assertEqual((code, line["reset"]), (2, None))
        self.assertEqual(line["doctor"]["checks"][0]["name"], "port-listed")
        self.assertEqual([command for command in ran if "reset" in command], [])

    def test_an_unknown_silent_step_keeps_the_try_s_answer_and_says_no_doctor(self):
        refused = subprocess.CalledProcessError(1, [], "", "mpremote.transport.TransportError: could not enter raw repl\n")
        shell = tool_finder.Tool("mpremote", "board-shell",
                                 {"kind": "python", "module": "mpremote", "silent_step": "erase"},
                                 ["/opt/python3"])
        with mock.patch.dict(found.__globals__["FOUND"], {"board-shell": shell}):
            code, said, _, _ = self.go("--code", "print(1)", "--json", answers=(refused, refused))
        line = json.loads(said)
        self.assertEqual((code, line["answer"], line["doctor"]), (2, "not_reached", None))
        self.assertIn("No doctor:", line["why"])

    def test_the_text_lists_the_gpio_numbers_in_the_code(self):
        code, said, _, _ = self.go("--code", "from machine import Pin\nPin(15, Pin.OUT).value(1)", answers=("", ""))
        self.assertEqual(code, 0)
        self.assertIn("  gpio    the code writes 1, 15, each a GPIO of this board\n", said + "\n")

    # --- MVP --- (P430, #569) the printed lines are guarded, the --json values stay raw; the message of a stop is flat in both (P444)
    def test_a_board_reply_with_control_characters_shows_guarded_and_json_keeps_it_raw(self):
        reply = "a\x1b[31m\u202eb\n"
        _, said, _, _ = self.go("--code", "print(1)", answers=(reply, ""))
        self.assertIn("  output  a?[31m?b\n", said + "\n")
        _, said, _, _ = self.go("--code", "print(1)", "--json", answers=(reply, ""))
        self.assertEqual(json.loads(said)["output"], reply)

    def test_a_port_that_is_not_listed_is_told_guarded_and_json_keeps_it_raw(self):
        port = "/dev/x\u202ey"
        code, said, problems, _ = self.go("--code", "print(1)", "--port", port)
        self.assertEqual((code, problems), (2, "live.py: no board on /dev/x?y: mpremote devs does not list it.\n"))
        code, said, _, _ = self.go("--code", "print(1)", "--port", port, "--json")
        line = json.loads(said)
        self.assertEqual(line["port"], port)
        self.assertIn("/dev/x?y", line["why"])  # P444: the message is flat

    def test_a_newline_in_the_port_cannot_fake_a_line_of_the_stop(self):
        code, _, problems, _ = self.go("--code", "print(1)", "--port", "/dev/x\nGRANTED")
        self.assertEqual((code, problems), (2, "live.py: no board on /dev/x?GRANTED: mpremote devs does not list it.\n"))

    def test_the_doctor_s_console_line_shows_guarded_and_json_keeps_it_raw(self):
        refused = subprocess.CalledProcessError(1, [], "", "mpremote.transport.TransportError: could not enter raw repl\n")
        printed = "boot\u202e x"
        _, said, _, _ = self.go("--code", "print(1)", answers=(refused, refused), probe=FakeConsoleProbe(printed=printed))
        self.assertIn("  check   console: ", said)
        self.assertNotIn("\u202e", said)
        self.assertIn("boot? x", said)
        _, said, _, _ = self.go("--code", "print(1)", "--json", answers=(refused, refused),
                                probe=FakeConsoleProbe(printed=printed))
        self.assertIn("boot\u202e x", json.dumps(json.loads(said)["doctor"], ensure_ascii=False))

    def test_a_newline_in_the_project_path_cannot_fake_a_line_of_a_tool_problem(self):
        project = Path(tempfile.mkdtemp()) / "a\nGRANTED: board ok"
        (project / ".spark").mkdir(parents=True)
        (project / ".spark" / "tools.json").write_text("not json")
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = live.main(["--code", "print(1)", "--project", str(project), "--json"])
        self.assertEqual(code, 2)
        self.assertEqual(len(err.getvalue().splitlines()), 1, err.getvalue())
        self.assertIn("a?GRANTED: board ok", err.getvalue())
        self.assertIn("a?GRANTED: board ok", json.loads(out.getvalue())["why"])  # P444: --json carries the flat message

    def test_a_failed_reset_is_exit_2_and_one_unchecked_item_whatever_the_answer(self):
        failed = subprocess.CalledProcessError(1, [], "", "the reset died")
        code, said, _, _ = self.go("--code", "print(1)", "--json", answers=("1\n", failed))
        line = json.loads(said)
        self.assertEqual((code, line["answer"], line["reset"]), (2, "ran", "failed"))
        self.assertIn("the reset failed", line["why"])
        result = RunLiveCode(platform_for=self.platform_for).run(code="print(1)", project=self.project, port=C6_PORT, outside=self.world(("1\n", failed)))
        self.assertEqual([(found.severity, found.code) for found in result.findings], [("could-not-run", "reset_failed")])

    def test_each_answer_is_one_finding_of_its_status_with_the_answer_for_its_code(self):
        def finding_of(code, **world):
            result = RunLiveCode(platform_for=self.platform_for).run(code=code, project=self.project, port=C6_PORT, outside=self.world(**world))
            return result.status(), [found.code for found in result.findings]
        self.assertEqual(finding_of("print(1)", answers=("1\n", "")), ("ok", []))
        self.assertEqual(finding_of("print(", answers=()), ("problems", ["refused_no_parse"]))
        self.assertEqual(finding_of("print(1)", answers=(), minutes_later=31), ("problems", ["refused_no_grant"]))
        self.assertEqual(finding_of("time.sleep(12)", answers=()), ("problems", ["refused_pin"]))
        refused = subprocess.CalledProcessError(1, [], "", "mpremote.transport.TransportError: could not enter raw repl\n")
        self.assertEqual(finding_of("print(1)", answers=(refused, refused)), ("could-not-run", ["not_reached"]))

    def test_every_answer_but_ran_is_a_code_of_the_table(self):
        from spark.bench import board_codes
        from spark.bench import board_live
        for answer in set(board_live.EXIT_FOR_ANSWER) - {board_live.RAN}:
            self.assertIn(answer, board_codes.CODES)

    def test_a_stop_has_the_empty_fields_a_finding_and_the_stderr_line(self):
        result = RunLiveCode(platform_for=self.platform_for).run(code="print(1)", project=self.project, port=None,
                                                                 outside=self.world(devs="mpremote-devs-two.txt"))
        self.assertEqual((result.status(), [found.code for found in result.findings]), ("could-not-run", ["two_boards"]))
        self.assertEqual((result.data["answer"], result.data["port"], result.data["output"]), ("could-not-run", None, None))
        self.assertTrue(result.diagnostics[0].startswith("live.py: "), result.diagnostics)

    def test_a_bad_argument_with_json_is_the_usage_and_a_missing_code_is_refused(self):
        for argv, said in ((["--code", "print(1)", "--json", "--bogus"], "unrecognized arguments: --bogus"),
                           (["--json"], "the following arguments are required: --code")):
            out, err = io.StringIO(), io.StringIO()
            with self.assertRaises(SystemExit) as raised, contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                live.main(argv, outside=FakeOutsideWorld())
            self.assertEqual((raised.exception.code, out.getvalue()), (2, ""))
            self.assertIn(said, err.getvalue())

    def test_a_crash_with_json_prints_no_line_and_the_traceback_on_stderr(self):
        code, said, problems, _ = self.go("--code", "print(1)", "--json", answers=(RuntimeError("boom"),))
        self.assertEqual((code, said), (2, ""))
        self.assertIn("Traceback (most recent call last):", problems)


class ASleepingBoardTest(LiveCase):
    """P1057: with no board on USB, or a port the person named that is not, and a firmware/ that calls deepsleep, live.py
    says the asleep fix on stderr, as look.py and grant.py do, and not the cable advice. A port that spark found and that
    left USB before the grant check gets the fix with its own opening (P1057 PR 2): it never says "the port you named"."""

    def setUp(self):
        super().setUp()
        (self.project / "firmware").mkdir()
        (self.project / "firmware" / "main.py").write_text("import machine\nmachine.deepsleep(1)\n")

    def test_no_board_gives_no_board_found_and_the_asleep_fix(self):
        code, _, problems, ran = self.go("--code", "print(1)", devs="mpremote-devs-none.txt")
        lines = problems.splitlines()
        self.assertEqual((code, lines[0], len(lines)), (2, "live.py: no board found.", 2))
        self.assertTrue(lines[1].startswith("What spark knows: no board is on USB, and the project's firmware calls "
                                            "deepsleep (firmware/main.py:2)."), lines[1])
        self.assertEqual([command for command in ran if "devs" not in command], [])

    def test_a_named_port_not_on_usb_opens_the_fix_with_that_port(self):
        code, _, problems, _ = self.go("--code", "print(1)", "--port", "/dev/cu.usbmodem9")
        lines = problems.splitlines()
        self.assertEqual((code, lines[0]), (2, "live.py: no board on /dev/cu.usbmodem9: mpremote devs does not list it."))
        self.assertTrue(lines[1].startswith("What spark knows: the port you named is not on USB, and the project's firmware"), lines[1])

    def test_a_named_port_that_leaves_usb_before_the_grant_check_opens_the_fix_with_that_port(self):
        # the review of #1596: the grant check lists the boards a second time, and the port the person named is gone
        code, _, problems, _ = self.go("--code", "print(1)", "--port", C6_PORT, devs=("mpremote-devs-one.txt", "mpremote-devs-none.txt"))
        lines = problems.splitlines()
        self.assertEqual((code, lines[0], len(lines)), (2, "live.py: no board on %s: mpremote devs does not list it." % C6_PORT, 2))
        self.assertTrue(lines[1].startswith("What spark knows: the port you named is not on USB, and the project's firmware"), lines[1])

    def test_an_unnamed_port_that_left_usb_gets_the_fix_with_its_own_opening(self):
        # the grant check lists the boards a second time, and the board spark found is gone (D2 of the plan: PR 2)
        code, _, problems, _ = self.go("--code", "print(1)", devs=("mpremote-devs-one.txt", "mpremote-devs-none.txt"))
        lines = problems.splitlines()
        self.assertEqual((code, lines[0], len(lines)), (2, "live.py: no board on %s: mpremote devs does not list it." % C6_PORT, 2))
        self.assertTrue(lines[1].startswith("What spark knows: the port that spark found on USB is not on USB any more, and the "
                                            "project's firmware calls deepsleep (firmware/main.py:2)."), lines[1])
        self.assertNotIn("the port you named", problems)

    #: The lists of a board that leaves USB at the exec: the first list and the grant check's hold it, the doctor's does not.
    GONE_AT_THE_EXEC = ("mpremote-devs-one.txt", "mpremote-devs-one.txt", "mpremote-devs-none.txt")
    REFUSED = subprocess.CalledProcessError(1, [], "", "mpremote.transport.TransportError: could not enter raw repl\n")

    def doctor_road(self, *argv):
        """(exit code, stdout, stderr) of live.py whose exec is refused twice, the board gone from USB from the exec on."""
        code, said, problems, _ = self.go("--code", "print(1)", *argv, answers=(self.REFUSED, self.REFUSED), devs=self.GONE_AT_THE_EXEC)
        return code, said, problems

    def test_after_the_doctor_an_unnamed_port_gets_the_fix_with_its_own_opening_in_place_of_the_cable_step(self):
        # P1057 PR 2 (D3, R3): the doctor said plug_in; the asleep fix takes the next line's place, as in look.py
        code, said, _ = self.doctor_road()
        nexts = [line for line in said.splitlines() if line.lstrip().startswith("next    ")]
        self.assertEqual(code, 2)
        self.assertEqual(len(nexts), 1)
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
        self.assertEqual((code, line["answer"], line["doctor"]["next_step"]), (2, "not_reached", "plug_in"))
        self.assertEqual((line["next"][0]["op"], line["next"][0]["needs_person"]), ("look", True))
        self.assertIsNone(line["reset"], "mpremote never got in, so live.py read no board and reset none")

    def test_after_the_doctor_a_firmware_with_no_deepsleep_call_keeps_the_cable_step(self):
        (self.project / "firmware" / "main.py").write_text("import machine\nmachine.lightsleep(1)\n")
        code, said, _ = self.doctor_road()
        self.assertEqual(code, 2)
        self.assertIn("next    plug the board straight into the computer", said)
        self.assertNotIn("What spark knows", said)
        code, said, _ = self.doctor_road("--json")
        self.assertNotIn("next", json.loads(said))

    def test_the_json_line_says_the_finding_s_sentence_and_ends_with_the_look_that_needs_the_person(self):
        code, said, _, _ = self.go("--code", "print(1)", "--json", devs="mpremote-devs-none.txt")
        line = json.loads(said)
        (step,) = line["next"]
        self.assertEqual((code, line["answer"], line["why"]), (2, "could-not-run", "no board found."))
        self.assertEqual((step["op"], step["argv"], step["needs_person"]), ("look", ["--project", str(self.project.resolve())], True))

    def test_without_a_deepsleep_call_the_stop_is_as_before(self):
        for main in ("import machine\nmachine.lightsleep(1)\n", "import machine\nmachine.deepsleep(\n"):
            with self.subTest(main=main):
                (self.project / "firmware" / "main.py").write_text(main)
                code, said, problems, _ = self.go("--code", "print(1)", devs="mpremote-devs-none.txt")
                self.assertEqual((code, problems.splitlines()), (2, ["live.py: no board found. Plug it straight into the computer "
                                                                     "with a data cable, not a hub that gives power only. If the "
                                                                     "plug is USB-C, turn it around, or use a USB-A to USB-C cable."]))

    def test_the_help_says_a_board_in_download_mode_runs_no_firmware(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), self.assertRaises(SystemExit):
            live.main(["--help"], outside=FakeOutsideWorld())
        said = " ".join(out.getvalue().split())
        self.assertIn("download mode", said)
        self.assertIn("runs no firmware", said)


class TheHelpTest(unittest.TestCase):
    """P937 (the PO, 2026-11-20): each paragraph of live.py --help in its place: the board doctor's is RunLiveCode's, so
    it comes before the CLI's own --json and exit codes."""

    def test_the_board_doctor_paragraph_is_the_operations_and_comes_before_the_json(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), self.assertRaises(SystemExit):
            live.main(["--help"], outside=FakeOutsideWorld())
        said, doctor = out.getvalue(), "the board doctor (P282) runs two checks"
        self.assertIn(doctor, RunLiveCode.details)
        self.assertEqual(said.count(doctor), 1)
        self.assertLess(said.index(doctor), said.index("--json prints one line"))
        self.assertLess(said.index("--json prints one line"), said.index("Exit codes:"))


if __name__ == "__main__":
    unittest.main()
