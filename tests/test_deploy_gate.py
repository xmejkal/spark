"""P219 step 4 (#201): deploy.py erases a board only after the look agrees, the token is this board's and this image's,
and the person types yes in their own terminal."""

import contextlib
import hashlib
import io
import shlex
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  P172: this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import deploy  # noqa: E402
import deploy_gate  # noqa: E402
import flash_image  # noqa: E402
import tools  # noqa: E402
from test_board_look import FOUND, LookCase, data, done, found  # noqa: E402


class Says:
    """A Consent that answers `answer` and keeps each question."""

    def __init__(self, answer):
        self.answer, self.asked = answer, []

    def ask(self, question):
        self.asked.append(question)
        return self.answer


class Stream(io.StringIO):
    """A stdin or stdout that is a terminal or not."""

    def __init__(self, text="", tty=True):
        super().__init__(text)
        self.tty = tty

    def isatty(self):
        return self.tty


class GateCase(LookCase):
    #: What the fake board prints when its firmware starts, or the exception mpremote raises then.
    prints = "ready\n"
    #: The fake board's files {path: bytes}, or None for the firmware the image holds.
    files_on_board = None
    #: The exception mpremote raises when it hashes the board's files, or None.
    unread = None

    def on_board(self, command):
        """What mpremote exec prints on the fake board: the firmware's start, or a line per file."""
        if command[-1] == "import main":
            if isinstance(self.prints, Exception):
                raise self.prints
            return done(self.prints)
        if self.unread:
            raise self.unread
        files = self.files_on_board if self.files_on_board is not None else dict(flash_image.files_under(self.project / "firmware"))
        return done("".join("file %s %s\n" % (hashlib.sha256(data).hexdigest(), path) for path, data in files.items()))

    def deploy(self, *argv, consent=None, esptool="c6-flash-id.txt", text=None, devs="mpremote-devs-one.txt", devs_text=None, fails=False):
        """(exit code, stdout, stderr) of deploy.py with fake tools. self.ran keeps every command."""
        def run(command, **kw):
            self.ran.append(command)
            if "devs" in command:
                return done(devs_text or data(devs))
            if "flash_id" in command:
                return done(text or data(esptool))
            if "exec" in command:
                return self.on_board(command)
            if fails:
                raise subprocess.CalledProcessError(2, command)
            return done("")

        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(tools, "find", side_effect=lambda name, *a, **k: FOUND["flasher"] if name == "flasher" else found(name)), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = deploy.main(["--project", str(self.project), *argv], run=run, consent=consent)
        return code, out.getvalue(), err.getvalue()

    def token(self, **kw):
        return self.look(**kw).token()

    def flashed(self):
        return [command[-1] for command in self.ran if "erase_flash" in command or "write_flash" in command]


class TheGateTest(GateCase):
    def test_no_token_says_to_run_the_look_first_and_erases_nothing(self):
        self.run_the_scenario()
        code, _, problems = self.deploy(consent=Says(True))
        self.assertEqual((code, self.flashed()), (2, []))
        self.assertIn("run look.py first, then deploy.py --token <token>.", problems)

    def test_the_yes_erases_then_writes_on_the_port_the_look_picked(self):
        self.run_the_scenario()
        consent = Says(True)
        code, said, _ = self.deploy("--token", self.token(), consent=consent)
        self.assertEqual(code, 0)
        self.assertEqual(self.flashed(), ["erase_flash", str(self.image)])
        self.assertTrue(all("/dev/cu.usbmodem101" in c for c in self.ran if "erase_flash" in c or "write_flash" in c))
        self.assertIn("erase ALL of this board's flash", consent.asked[0])
        self.assertIn("ready seen: the firmware printed 'ready' and the board's 1 files match the run that passed", said)

    def test_the_answer_no_erases_nothing(self):
        self.run_the_scenario()
        code, _, problems = self.deploy("--token", self.token(), consent=Says(False))
        self.assertEqual((code, self.flashed()), (2, []))
        self.assertIn("not flashed: you answered no.", problems)

    def test_a_token_for_another_board_names_the_board(self):
        self.run_the_scenario()
        image = self.token().split("-")[1]
        code, _, problems = self.deploy("--token", "0000-" + image, consent=Says(True))
        self.assertEqual((code, self.flashed()), (2, []))
        self.assertIn("the board changed since the look: run look.py again.", problems)

    def test_a_token_for_another_image_names_the_image(self):
        self.run_the_scenario()
        mac, _ = self.token().split("-")
        code, _, problems = self.deploy("--token", mac + "-0000", consent=Says(True))
        self.assertEqual((code, self.flashed()), (2, []))
        self.assertIn("the image changed since the look: run look.py again.", problems)

    def test_a_token_with_more_after_the_image_half_is_another_image(self):
        self.run_the_scenario()
        code, _, problems = self.deploy("--token", self.token() + "-1", consent=Says(True))
        self.assertEqual(code, 2)
        self.assertIn("the image changed", problems)

    def test_the_same_board_on_another_port_name_passes(self):
        self.run_the_scenario()
        token = self.token()
        moved = data("mpremote-devs-one.txt").replace("/dev/cu.usbmodem101", "/dev/cu.usbmodem2101")
        code, _, _ = self.deploy("--token", token, devs_text=moved, consent=Says(True))
        self.assertEqual(code, 0)
        self.assertTrue(all("/dev/cu.usbmodem2101" in c for c in self.ran if "erase_flash" in c))

    def test_another_chip_stops_before_the_question(self):
        self.run_the_scenario()
        token = self.token()
        self.board("firebeetle2-esp32s3")
        consent = Says(True)
        code, _, problems = self.deploy("--token", token, consent=consent)
        self.assertEqual((code, self.flashed(), consent.asked), (1, [], []))
        self.assertIn("this board is an esp32c6, the project is for an esp32s3. not flashed.", problems)

    def test_a_warning_is_named_in_the_question(self):
        self.run_the_scenario()
        self.board("firebeetle2-esp32s3")
        token = self.token(esptool="s3-flash-id-8mb.txt")
        consent = Says(True)
        code, _, _ = self.deploy("--token", token, esptool="s3-flash-id-8mb.txt", consent=consent)
        self.assertEqual(code, 0)
        self.assertIn("the flash differs: 8 MB, the record says 16 or 4", consent.asked[0])

    def test_an_unknown_field_is_named_in_the_question(self):
        self.run_the_scenario()
        token = self.token(esptool="c6-flash-id-garbled.txt")
        consent = Says(True)
        self.deploy("--token", token, esptool="c6-flash-id-garbled.txt", consent=consent)
        self.assertIn("flash unknown (the board did not say)", consent.asked[0])

    def test_a_look_with_no_token_refuses_whatever_token_is_given(self):
        self.run_the_scenario()
        code, _, problems = self.deploy("--token", "aaaa-bbbb", esptool="c6-flash-id-no-mac.txt", consent=Says(True))
        self.assertEqual((code, self.flashed()), (2, []))
        self.assertIn("no token: the board's MAC could not be read. not flashed.", problems)

    def test_ignore_older_runs_gives_the_look_the_same_token(self):
        self.run_the_scenario()
        (self.project / "firmware" / "main.py").write_text("print('ready')\nprint(2)\n")
        self.run_the_scenario(scenario=self.second_scenario())
        token = self.token(ignore_older_runs=True)
        code, _, _ = self.deploy("--token", token, "--ignore-older-runs", consent=Says(True))
        self.assertEqual(code, 0)

    def second_scenario(self):
        other = self.scenario.with_name("t.scenario.yaml")
        other.write_text(self.scenario.read_text().replace("name: s", "name: t"))
        return other

    def test_a_failed_erase_writes_nothing_and_says_what_to_try(self):
        self.run_the_scenario()
        code, _, problems = self.deploy("--token", self.token(), consent=Says(True), fails=True)
        self.assertEqual((code, self.flashed()), (2, ["erase_flash"]))
        self.assertIn("hold the board's BOOT button", problems)

    def test_a_flash_too_small_for_the_image_stops_before_the_question(self):
        self.run_the_scenario()
        self.board("firebeetle2-esp32s3")
        consent = Says(True)
        code, _, problems = self.deploy("--token", "aaaa-bbbb", esptool="s3-flash-id-2mb.txt", consent=consent)
        self.assertEqual((code, self.flashed(), consent.asked), (1, [], []))
        self.assertIn("the flash is 2 MB, the image needs 4 MB. not flashed.", problems)

    def test_no_board_on_usb_is_a_sentence_and_erases_nothing(self):
        self.run_the_scenario()
        code, said, problems = self.deploy("--token", "aaaa-bbbb", devs_text="\n", consent=Says(True))
        self.assertEqual((code, said, self.flashed()), (2, "", []))
        self.assertIn("deploy.py: no board found.", problems)

    def test_the_dry_run_never_touches_usb(self):
        self.run_the_scenario()
        code, said, _ = self.deploy("--dry-run")
        self.assertEqual((code, self.ran), (0, []))
        self.assertIn("  board: not looked at: run look.py", said.splitlines())


class TheBoardAfterTheFlashTest(GateCase):
    """P215 step 2 (D33): after the flash, ready is seen only when the board's files match and the firmware says it."""

    def flash(self, consent=None):
        self.run_the_scenario()
        return self.deploy("--token", self.token(), consent=consent or Says(True))

    def test_ready_seen_is_kept_in_a_board_log_beside_the_run_logs_and_the_next_look_ignores_it(self):
        code, said, _ = self.flash()
        logs = list((self.project / "sim" / "runs" / "board").glob("*.log"))
        self.assertEqual((code, len(logs)), (0, 1))
        self.assertIn("board log: %s" % logs[0], said)
        self.assertIn("ready seen: ", logs[0].read_text())
        self.assertIn("image sha256: %s" % hashlib.sha256(self.image.read_bytes()).hexdigest(), logs[0].read_text())
        self.assertIsNotNone(self.look().token())

    def test_a_file_that_differs_on_the_board_is_named_and_ready_is_not_seen(self):
        self.files_on_board = {"/main.py": b"print('old')\n"}
        code, said, _ = self.flash()
        self.assertEqual(code, 1)
        self.assertIn("ready not seen: the board's /main.py is not the files that passed", said)

    def test_a_file_missing_on_the_board_is_named(self):
        self.files_on_board = {}
        code, said, _ = self.flash()
        self.assertEqual(code, 1)
        self.assertIn("/main.py is not the files that passed", said)

    def test_a_firmware_that_prints_no_ready_is_not_seen(self):
        self.prints = "booting\n"
        code, said, _ = self.flash()
        self.assertEqual(code, 1)
        self.assertIn("ready not seen: the firmware printed no 'ready' in 20 s", said)

    def test_ready_printed_before_the_wait_ends_is_seen(self):
        self.prints = subprocess.TimeoutExpired(["mpremote"], 20, output=b"ready\nLED on\n")
        code, said, _ = self.flash()
        self.assertEqual(code, 0)
        self.assertIn("ready seen", said)

    def test_mpremote_that_cannot_reach_the_board_is_unknown_never_seen(self):
        self.unread = subprocess.CalledProcessError(1, ["mpremote"])
        code, said, _ = self.flash()
        self.assertEqual(code, 2)
        self.assertIn("ready unknown: mpremote could not read the board's files", said)
        self.assertIn("then, to see it start", said)

    def test_a_board_that_hangs_is_unknown(self):
        self.unread = subprocess.TimeoutExpired(["mpremote"], 20)
        code, said, _ = self.flash()
        self.assertEqual(code, 2)
        self.assertIn("ready unknown", said)

    def test_a_passed_log_from_before_the_file_lines_is_unknown(self):
        self.run_the_scenario()
        log = next((self.project / "sim" / "runs").glob("*.log"))
        log.write_text("".join(line for line in log.read_text().splitlines(True) if not line.startswith("file sha256: ")))
        code, said, _ = self.deploy("--token", self.token(), consent=Says(True))
        self.assertEqual(code, 2)
        self.assertIn("ready unknown: the passed run's log names no files", said)

    def test_an_image_rebuilt_and_passed_while_the_person_answered_is_not_flashed(self):
        main, runs = self.project / "firmware" / "main.py", self.project / "sim" / "runs"
        first = main.read_text()
        main.write_text("print('ready')\nprint('new')\n")
        self.run_the_scenario()  # a new firmware, built and passed, swapped in while the question waits
        rebuilt = self.image.read_bytes(), {log.name: log.read_text() for log in runs.glob("*.log")}
        main.write_text(first)
        test = self

        class ChangesTheImage(Says):
            def ask(self, question):
                test.image.write_bytes(rebuilt[0])
                for name, text in rebuilt[1].items():
                    (runs / name).write_text(text)
                return True

        code, _, problems = self.flash(ChangesTheImage(True))
        self.assertEqual((code, self.flashed()), (2, []))
        self.assertIn("the image changed after your yes: run look.py again. not flashed.", problems)


class TheDefaultConsentTest(GateCase):
    """deploy.main with no consent given asks in this terminal. Under the tests stdout is no terminal, as in Claude's shell."""

    def test_no_token_says_to_run_the_look_first(self):
        self.run_the_scenario()
        code, _, problems = self.deploy()
        self.assertEqual((code, self.flashed()), (2, []))
        self.assertIn("run look.py first, then deploy.py --token <token>.", problems)

    def test_no_terminal_prints_the_line_to_run_and_erases_nothing(self):
        self.run_the_scenario()
        token = self.token()
        code, said, problems = self.deploy("--token", token)
        self.assertEqual((code, self.flashed()), (2, []))
        self.assertIn("  chip   same      esp32c6", said.splitlines())
        line = shlex.join([str(Path(deploy.__file__).resolve()), "--project", str(self.project.resolve()), "--token", token,
                           "--port", "/dev/cu.usbmodem101"])
        self.assertIn("no terminal to ask you in", problems)
        self.assertIn("\n  %s\n" % line, problems)


class TerminalConsentTest(unittest.TestCase):
    LINE = "/spark/scripts/deploy.py --project /p --token aaaa-bbbb --port /dev/cu.usbmodem101"

    def ask(self, typed, stdin_tty=True, stdout_tty=True):
        stdout = Stream(tty=stdout_tty)
        consent = deploy_gate.TerminalConsent(self.LINE, Stream(typed, stdin_tty), stdout)
        return consent.ask("erase ALL of this board's flash?"), stdout.getvalue()

    def test_yes_in_a_terminal_is_the_yes(self):
        self.assertEqual(self.ask("yes\n"), (True, "erase ALL of this board's flash? type yes to go on: "))

    def test_anything_else_is_no(self):
        for typed in ("y\n", "YES please\n", "\n", ""):
            self.assertFalse(self.ask(typed)[0], typed)

    def test_a_pipe_is_no_terminal_and_gives_the_line_to_run(self):
        for stdin_tty, stdout_tty in ((False, True), (True, False), (False, False)):
            with self.assertRaises(deploy_gate.Closed) as shut:
                self.ask("yes\n", stdin_tty, stdout_tty)
            self.assertIn("no terminal to ask you in", str(shut.exception))
            self.assertIn(self.LINE, str(shut.exception))
            self.assertEqual(shut.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
