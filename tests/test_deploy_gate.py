"""P219 step 4 (#201): deploy.py erases a board only after the look agrees, the token is this board's and this image's,
and the person types yes in their own terminal."""

import contextlib
import io
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
    def deploy(self, *argv, consent=None, esptool="c6-flash-id.txt", text=None, devs="mpremote-devs-one.txt", devs_text=None, fails=False):
        """(exit code, stdout, stderr) of deploy.py with fake tools. self.ran keeps every command."""
        def run(command, **kw):
            self.ran.append(command)
            if "devs" in command:
                return done(devs_text or data(devs))
            if "flash_id" in command:
                return done(text or data(esptool))
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
        self.assertIn("then, to see it start", said)

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

    def test_the_dry_run_never_touches_usb(self):
        self.run_the_scenario()
        code, said, _ = self.deploy("--dry-run")
        self.assertEqual((code, self.ran), (0, []))
        self.assertIn("  board: not looked at: run look.py", said.splitlines())


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
