"""P219 step 4 (#201): deploy.py erases a board only after the look agrees, the token is this board's and this image's,
and the person types yes in their own terminal."""

import contextlib
import datetime
import getpass
import hashlib
import io
import json
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

import board_facts  # noqa: E402
import deploy  # noqa: E402
import deploy_gate  # noqa: E402
import flash_image  # noqa: E402
import store  # noqa: E402
import tools  # noqa: E402
from fakes import FakeConsent, FakeConsoleProbe  # noqa: E402
from test_board_look import FOUND, LookCase, data, done, found  # noqa: E402


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
    #: The exception mpremote raises when it copies the facts file, or None; what `fs cat` adds to the copy.
    uncopied, garbled = None, ""

    def fs(self, command):
        """mpremote fs cp and fs cat on the fake board, which keeps the copied files in self.copied."""
        if self.uncopied:
            raise self.uncopied
        if command[-3] == "cp":
            self.copied[command[-1].lstrip(":")] = Path(command[-2]).read_text()
            return done("")
        return done(self.copied[command[-1].lstrip(":")] + self.garbled)

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

    def deploy(self, *argv, consent=None, esptool="c6-flash-id.txt", text=None, devs="mpremote-devs-one.txt", devs_text=None, fails=False, probe=None, clock=None):
        """(exit code, stdout, stderr) of deploy.py with fake tools. self.ran keeps every command."""
        self.copied = getattr(self, "copied", {})

        def run(command, **kw):
            self.ran.append(command)
            if "fs" in command:
                return self.fs(command)
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
            code = deploy.main(["--project", str(self.project), *argv], run=run, consent=consent, probe=probe, clock=clock)
        return code, out.getvalue(), err.getvalue()

    def token(self, **kw):
        return self.look(**kw).token()

    def flashed(self):
        return [command[-1] for command in self.ran if "erase_flash" in command or "write_flash" in command]


class TheGateTest(GateCase):
    def test_no_token_says_to_run_the_look_first_and_erases_nothing(self):
        self.run_the_scenario()
        code, _, problems = self.deploy(consent=FakeConsent(True))
        self.assertEqual((code, self.flashed()), (2, []))
        self.assertIn("run look.py first, then deploy.py --token <token>.", problems)

    def test_the_yes_erases_then_writes_on_the_port_the_look_picked(self):
        self.run_the_scenario()
        consent = FakeConsent(True)
        code, said, _ = self.deploy("--token", self.token(), consent=consent)
        self.assertEqual(code, 0)
        self.assertEqual(self.flashed(), ["erase_flash", str(self.image)])
        self.assertTrue(all("/dev/cu.usbmodem101" in c for c in self.ran if "erase_flash" in c or "write_flash" in c))
        self.assertIn("erase ALL of this board's flash", consent.asked[0])
        self.assertIn("ready seen: the firmware printed 'ready' and the board's 1 files match the run that passed", said)

    def test_the_answer_no_erases_nothing(self):
        self.run_the_scenario()
        code, _, problems = self.deploy("--token", self.token(), consent=FakeConsent(False))
        self.assertEqual((code, self.flashed()), (2, []))
        self.assertIn("not flashed: you answered no.", problems)

    def test_a_token_for_another_board_names_the_board(self):
        self.run_the_scenario()
        image = self.token().split("-")[1]
        code, _, problems = self.deploy("--token", "0000-" + image, consent=FakeConsent(True))
        self.assertEqual((code, self.flashed()), (2, []))
        self.assertIn("the board changed since the look: run look.py again.", problems)

    def test_a_token_for_another_image_names_the_image(self):
        self.run_the_scenario()
        mac, _ = self.token().split("-")
        code, _, problems = self.deploy("--token", mac + "-0000", consent=FakeConsent(True))
        self.assertEqual((code, self.flashed()), (2, []))
        self.assertIn("the image changed since the look: run look.py again.", problems)

    def test_a_token_with_more_after_the_image_half_is_another_image(self):
        self.run_the_scenario()
        code, _, problems = self.deploy("--token", self.token() + "-1", consent=FakeConsent(True))
        self.assertEqual(code, 2)
        self.assertIn("the image changed", problems)

    def test_the_same_board_on_another_port_name_passes(self):
        self.run_the_scenario()
        token = self.token()
        moved = data("mpremote-devs-one.txt").replace("/dev/cu.usbmodem101", "/dev/cu.usbmodem2101")
        code, _, _ = self.deploy("--token", token, devs_text=moved, consent=FakeConsent(True))
        self.assertEqual(code, 0)
        self.assertTrue(all("/dev/cu.usbmodem2101" in c for c in self.ran if "erase_flash" in c))

    def test_another_chip_stops_before_the_question(self):
        self.run_the_scenario()
        token = self.token()
        self.board("firebeetle2-esp32s3")
        consent = FakeConsent(True)
        code, _, problems = self.deploy("--token", token, consent=consent)
        self.assertEqual((code, self.flashed(), consent.asked), (1, [], []))
        self.assertIn("this board is an esp32c6, the project is for an esp32s3. not flashed.", problems)

    def test_a_warning_is_named_in_the_question(self):
        self.run_the_scenario()
        self.board("firebeetle2-esp32s3")
        token = self.token(esptool="s3-flash-id-8mb.txt")
        consent = FakeConsent(True)
        code, _, _ = self.deploy("--token", token, esptool="s3-flash-id-8mb.txt", consent=consent)
        self.assertEqual(code, 0)
        self.assertIn("the flash differs: 8 MB, the record says 16 or 4", consent.asked[0])

    def test_an_unknown_field_is_named_in_the_question(self):
        self.run_the_scenario()
        token = self.token(esptool="c6-flash-id-garbled.txt")
        consent = FakeConsent(True)
        self.deploy("--token", token, esptool="c6-flash-id-garbled.txt", consent=consent)
        self.assertIn("flash unknown (the board did not say)", consent.asked[0])

    def test_a_look_with_no_token_refuses_whatever_token_is_given(self):
        self.run_the_scenario()
        code, _, problems = self.deploy("--token", "aaaa-bbbb", esptool="c6-flash-id-no-mac.txt", consent=FakeConsent(True))
        self.assertEqual((code, self.flashed()), (2, []))
        self.assertIn("no token: the board's MAC could not be read. not flashed.", problems)

    def test_ignore_older_runs_gives_the_look_the_same_token(self):
        self.run_the_scenario()
        (self.project / "firmware" / "main.py").write_text("print('ready')\nprint(2)\n")
        self.run_the_scenario(scenario=self.second_scenario())
        token = self.token(ignore_older_runs=True)
        code, _, _ = self.deploy("--token", token, "--ignore-older-runs", consent=FakeConsent(True))
        self.assertEqual(code, 0)

    def second_scenario(self):
        other = self.scenario.with_name("t.scenario.yaml")
        other.write_text(self.scenario.read_text().replace("name: s", "name: t"))
        return other

    def test_a_failed_erase_writes_nothing_and_says_what_to_try(self):
        self.run_the_scenario()
        code, _, problems = self.deploy("--token", self.token(), consent=FakeConsent(True), fails=True)
        self.assertEqual((code, self.flashed()), (2, ["erase_flash"]))
        self.assertIn("hold the board's BOOT button", problems)

    def test_a_flash_too_small_for_the_image_stops_before_the_question(self):
        self.run_the_scenario()
        self.board("firebeetle2-esp32s3")
        consent = FakeConsent(True)
        code, _, problems = self.deploy("--token", "aaaa-bbbb", esptool="s3-flash-id-2mb.txt", consent=consent)
        self.assertEqual((code, self.flashed(), consent.asked), (1, [], []))
        self.assertIn("the flash is 2 MB, the image needs 4 MB. not flashed.", problems)

    def test_no_board_on_usb_is_a_sentence_and_erases_nothing(self):
        self.run_the_scenario()
        code, said, problems = self.deploy("--token", "aaaa-bbbb", devs_text="\n", consent=FakeConsent(True))
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
        return self.deploy("--token", self.token(), consent=consent or FakeConsent(True))

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

    def test_a_firmware_that_stops_with_an_error_is_not_seen_and_its_traceback_is_kept(self):
        self.prints = subprocess.CalledProcessError(1, ["mpremote"], output="ready\nTraceback: OSError: 19\n", stderr="")
        code, said, _ = self.flash()
        self.assertEqual(code, 1)
        self.assertIn("ready not seen: the firmware stopped with an error: Traceback: OSError: 19", said)
        log = next((self.project / "sim" / "runs" / "board").glob("*.log"))
        self.assertIn("Traceback: OSError: 19", log.read_text())

    def test_a_passed_log_gone_after_the_flash_is_unknown_not_a_traceback(self):
        with mock.patch.object(deploy, "passed_log", side_effect=lambda *a: None):
            code, said, _ = self.flash()
        self.assertEqual(code, 2)
        self.assertIn("ready unknown: the passed run's log names no files", said)

    def test_mpremote_that_cannot_reach_the_board_is_unknown_never_seen(self):
        self.unread = subprocess.CalledProcessError(1, ["mpremote"])
        code, said, _ = self.flash()
        self.assertEqual(code, 2)
        self.assertIn("ready unknown: mpremote could not read the board's files", said)
        self.assertIn("then, to see it start", said)

    def test_a_board_that_does_not_answer_keeps_mpremote_s_words_in_the_line_and_the_board_log(self):
        self.unread = subprocess.CalledProcessError(
            1, ["mpremote"], "b''\n", "Traceback (most recent call last):\nmpremote.transport.TransportError: could not enter raw repl\n")
        code, said, _ = self.flash()
        self.assertEqual(code, 2)
        self.assertIn("ready unknown: mpremote could not read the board's files: "
                      "mpremote.transport.TransportError: could not enter raw repl", said)
        log = next((self.project / "sim" / "runs" / "board").glob("*.log")).read_text()
        self.assertIn("b''", log)
        self.assertIn("could not enter raw repl", log)

    def test_a_board_that_hangs_is_unknown(self):
        self.unread = subprocess.TimeoutExpired(["mpremote"], 20)
        code, said, _ = self.flash()
        self.assertEqual(code, 2)
        self.assertIn("ready unknown", said)

    def test_a_passed_log_from_before_the_file_lines_is_unknown(self):
        self.run_the_scenario()
        log = next((self.project / "sim" / "runs").glob("*.log"))
        log.write_text("".join(line for line in log.read_text().splitlines(True) if not line.startswith("file sha256: ")))
        code, said, _ = self.deploy("--token", self.token(), consent=FakeConsent(True))
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

        class ChangesTheImage(FakeConsent):
            def ask(self, question):
                test.image.write_bytes(rebuilt[0])
                for name, text in rebuilt[1].items():
                    (runs / name).write_text(text)
                return True

        code, _, problems = self.flash(ChangesTheImage(True))
        self.assertEqual((code, self.flashed()), (2, []))
        self.assertIn("the image changed after your yes: run look.py again. not flashed.", problems)


class TheBoardInDownloadModeTest(GateCase):
    """P243 (#252): a board silent after the flash because it waits in download mode gets a press of R, then the
    ready check runs again."""

    unread = subprocess.CalledProcessError(1, ["mpremote"], "", "mpremote.transport.TransportError: could not enter raw repl\n")

    def flash(self, probe):
        self.run_the_scenario()
        return self.deploy("--token", self.token(), consent=FakeConsent(True), probe=probe)

    def answers(self):
        self.unread = self.uncopied = None
        self.ran.append("reset")

    def test_a_press_of_r_after_download_mode_runs_the_ready_check_again(self):
        self.uncopied = self.unread
        probe = FakeConsoleProbe("boot:0x4 (DOWNLOAD)\nwaiting for download\n", on_reset=self.answers)
        code, said, _ = self.flash(probe)
        self.assertEqual((code, probe.asked), (0, ["console", "reset"]))
        self.assertIn("press the board's R (reset) button once", said)
        self.assertIn("ready seen", said)
        self.assertIn("facts file spark.json sha256", said)
        log = next((self.project / "sim" / "runs" / "board").glob("*.log")).read_text()
        self.assertIn("console with DTR and RTS off: boot:0x4 (DOWNLOAD)\nwaiting for download\nreset seen", log)
        after = self.ran[self.ran.index("reset") + 1:]
        self.assertEqual([c[c.index("fs") + 1] if "fs" in c else c[-1][:6] for c in after], ["cp", "cat", "import", "import"])

    def test_no_press_in_time_is_unknown_and_says_to_press_r(self):
        code, said, _ = self.flash(FakeConsoleProbe("waiting for download\n", reset=False))
        self.assertEqual(code, 2)
        self.assertIn("ready unknown: the board waits in download mode, and its port did not go and come back in 60 s: "
                      "press its R button", said)
        self.assertIn("waiting for download\nno reset", next((self.project / "sim" / "runs" / "board").glob("*.log")).read_text())

    def test_a_silent_board_not_in_download_mode_stays_unknown_and_asks_nothing(self):
        probe = FakeConsoleProbe("")
        code, said, _ = self.flash(probe)
        self.assertEqual((code, probe.asked), (2, ["console"]))
        self.assertNotIn("press the board's R", said)
        self.assertIn("ready unknown: mpremote could not read the board's files", said)
        self.assertIn("console with DTR and RTS off: nothing\n", next((self.project / "sim" / "runs" / "board").glob("*.log")).read_text())

    def test_a_console_that_heard_ready_reads_the_board_again(self):
        # P245 (#257): on 2026-10-15 mpremote asked while the board still restarted, then the console heard ready
        self.uncopied = self.unread
        boot = "mode:DIO, clock div:2\nentry 0x4086b910\nready\n"
        probe = FakeConsoleProbe(boot, on_console=self.answers)
        code, said, _ = self.flash(probe)
        self.assertEqual((code, probe.asked), (0, ["console"]))
        self.assertNotIn("press the board's R", said)
        self.assertIn("ready seen", said)
        log = next((self.project / "sim" / "runs" / "board").glob("*.log")).read_text()
        self.assertIn("facts file spark.json sha256", said)
        self.assertIn("console with DTR and RTS off: mode:DIO, clock div:2\nentry 0x4086b910\nready\nread again\n", log)

    def test_download_mode_with_ready_after_it_still_asks_for_r_and_never_reads_again(self):
        code, said, _ = self.flash(FakeConsoleProbe("waiting for download\nready\n", reset=False))
        self.assertEqual(code, 2)
        self.assertIn("the board waits in download mode, and its port did not go and come back", said)
        self.assertNotIn("read again", next((self.project / "sim" / "runs" / "board").glob("*.log")).read_text())

    def test_a_ready_inside_another_word_is_not_a_boot(self):
        code, said, _ = self.flash(FakeConsoleProbe("not ready yet\n", on_console=self.answers))
        self.assertEqual(code, 2)
        self.assertNotIn("read again", next((self.project / "sim" / "runs" / "board").glob("*.log")).read_text())

    def test_what_a_board_not_in_download_mode_printed_stays_in_the_log(self):
        # P244 (#255): the 2026-10-15 bench lost what the check read, so nobody knew why the board was silent
        code, said, _ = self.flash(FakeConsoleProbe("rst:0x15 (USB_UART_HPSYS),boot:0x1e\n"))
        self.assertEqual(code, 2)
        self.assertIn("console with DTR and RTS off: rst:0x15 (USB_UART_HPSYS),boot:0x1e\n",
                      next((self.project / "sim" / "runs" / "board").glob("*.log")).read_text())

    def test_a_passed_log_that_names_no_files_is_never_probed(self):
        probe = FakeConsoleProbe("waiting for download\n")
        with mock.patch.object(deploy, "file_hashes", side_effect=lambda log: {}):
            code, said, _ = self.flash(probe)
        self.assertEqual((code, probe.asked), (2, []))
        self.assertIn("ready unknown: the passed run's log names no files", said)

    def test_a_board_that_answers_is_never_probed(self):
        self.unread = None
        probe = FakeConsoleProbe("waiting for download\n")
        self.assertEqual((self.flash(probe)[0], probe.asked), (0, []))

    def test_without_a_probe_the_default_reads_the_port_with_mpremote_s_python(self):
        code, said, _ = self.flash(None)
        self.assertEqual(code, 2)
        probes = [command for command in self.ran if command[1:2] == ["-c"] and "serial" in command[2]]
        self.assertEqual([command[:1] + command[3:] for command in probes],
                         [FOUND["board-shell"].command + [self.look().port, "2"]])


class TheFactsAfterTheFlashTest(GateCase):
    """P215 step 3 (D22, D23, D44): the board holds what spark put there, and the store remembers the board by its MAC."""

    def flash(self, consent=None):
        self.run_the_scenario()
        return self.deploy("--token", self.token(), consent=consent or FakeConsent(True))

    def test_the_facts_file_is_on_the_board_and_the_board_log_names_its_sha256(self):
        code, said, _ = self.flash()
        facts = json.loads(self.copied["spark.json"])
        self.assertEqual(code, 0)
        self.assertEqual((facts["project"], facts["board"], facts["image_sha256"]),
                         (self.project.name, "xiao-esp32-c6", hashlib.sha256(self.image.read_bytes()).hexdigest()))
        self.assertEqual(facts["files"], {"/main.py": hashlib.sha256((self.project / "firmware" / "main.py").read_bytes()).hexdigest()})
        self.assertEqual(facts["spark"], json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())["version"])
        line = "facts file spark.json sha256: %s" % hashlib.sha256(self.copied["spark.json"].encode()).hexdigest()
        self.assertIn(line, said)
        self.assertIn(line, next((self.project / "sim" / "runs" / "board").glob("*.log")).read_text())

    def test_the_store_keeps_one_record_per_mac_and_adds_each_deploy(self):
        _, said, _ = self.flash()
        record = Path(said.split("store record: ")[1].strip())
        before = len(json.loads(record.read_text())["deploys"])  # the suite's store is shared, so count from here
        self.flash()
        kept = json.loads(record.read_text())
        self.assertEqual(record.parent, store.place("boards"))
        self.assertEqual((kept["mac"], kept["board"], len(kept["deploys"])),
                         (json.loads(self.copied["spark.json"])["mac"], "xiao-esp32-c6", before + 1))
        self.assertEqual(kept["deploys"][-1]["verdict"], "ready seen")

    def test_the_record_keeps_whose_yes_the_consent_says(self):
        _, said, _ = self.flash(FakeConsent(True))
        record = Path(said.split("store record: ")[1].strip())
        self.assertEqual(json.loads(record.read_text())["deploys"][-1]["yes"], "a test")

    def test_a_yes_typed_in_a_terminal_is_recorded_as_typed_in_a_terminal(self):
        terminal = deploy_gate.TerminalConsentStrategy("x", stdin=Stream("yes\n"), stdout=Stream())
        with mock.patch.object(getpass, "getuser", return_value="ada"):
            _, said, _ = self.flash(terminal)
        record = Path(said.split("store record: ")[1].strip())
        self.assertEqual(json.loads(record.read_text())["deploys"][-1]["yes"], "typed in a terminal by ada")

    def test_one_moment_names_the_facts_the_log_and_its_file(self):
        moment, calls = datetime.datetime(2026, 10, 17, 9, 8, 7), []
        self.run_the_scenario()
        self.deploy("--token", self.token(), consent=FakeConsent(True), clock=lambda: calls.append(1) or moment)
        log = next((self.project / "sim" / "runs" / "board").glob("*.log"))
        self.assertEqual((len(calls), json.loads(self.copied["spark.json"])["deployed"], log.name),
                         (1, "2026-10-17T09:08:07", "2026-10-17T09-08-07.log"))
        self.assertTrue(log.read_text().startswith("# deploy 2026-10-17T09:08:07 on /dev/cu.usbmodem101\n"))

    def test_the_facts_carry_the_moment_given_and_no_clock(self):
        moment = datetime.datetime(2026, 1, 2, 3, 4, 5)
        self.run_the_scenario()
        said = board_facts.facts(self.project, "xiao-esp32-c6", "aa:bb", self.image, {}, moment)
        self.assertEqual(said["deployed"], "2026-01-02T03:04:05")

    def test_the_record_writes_the_who_it_is_given(self):
        said = {"mac": "aa:bb:test-who", "project": "p", "board": "b", "image_sha256": "0", "deployed": "d"}
        path = board_facts.record_deploy(said, "ready seen", "a test")
        self.assertEqual(json.loads(path.read_text())["deploys"][-1]["yes"], "a test")

    def test_the_facts_go_to_the_look_s_port_and_name_the_look_s_mac(self):
        self.flash()
        copy = next(command for command in self.ran if "cp" in command)
        self.assertEqual(copy[copy.index("connect"):copy.index("connect") + 2], ["connect", "/dev/cu.usbmodem101"])
        self.assertEqual(json.loads(self.copied["spark.json"])["mac"], self.look().reading.mac)

    def test_the_record_is_named_by_the_mac_private_and_keeps_the_verdict(self):
        self.files_on_board = {"/main.py": b"print('old')\n"}
        _, said, _ = self.flash()
        record = Path(said.split("store record: ")[1].strip())
        self.assertEqual(record.name, store.slug(self.look().reading.mac) + ".json")
        self.assertEqual(record.stat().st_mode & 0o777, 0o600)
        self.assertEqual(json.loads(record.read_text())["deploys"][-1]["verdict"], "ready not seen")

    def test_the_same_facts_are_the_same_bytes(self):
        self.assertEqual(board_facts.facts_text({"b": 1, "a": 2}), board_facts.facts_text({"a": 2, "b": 1}))

    def test_a_copy_that_fails_is_said_and_the_ready_check_still_runs(self):
        self.uncopied = subprocess.CalledProcessError(1, ["mpremote"])
        code, said, _ = self.flash()
        self.assertEqual(code, 0)
        self.assertIn("facts file: not written: mpremote could not copy it", said)
        self.assertIn("ready seen", said)

    def test_a_facts_file_that_reads_back_different_is_not_written(self):
        self.garbled = "x"
        _, said, _ = self.flash()
        self.assertIn("facts file: not written: it read back different from what was copied", said)

    def test_a_board_record_that_is_not_one_is_left_as_it_is_and_the_verdict_stands(self):
        _, said, _ = self.flash()
        record = Path(said.split("store record: ")[1].strip())
        good = record.read_text()
        self.addCleanup(record.write_text, good)  # the suite's store is shared
        for bad in ("", "[]", '{"mac": "x"}'):
            record.write_text(bad)
            code, said, _ = self.flash()
            self.assertEqual(code, 0)
            self.assertIn("store record: not written: %s is not a board record, so it was left as it is" % record, said)
            self.assertEqual(record.read_text(), bad)

    def test_a_store_that_cannot_be_written_is_a_sentence(self):
        with mock.patch.object(store, "write_json", side_effect=store.StoreProblem("no room")):
            code, said, _ = self.flash()
        self.assertEqual(code, 0)
        self.assertIn("store record: not written: no room", said)


class TheBoardLogTextTest(unittest.TestCase):
    """The board log's text is a Value's: the same facts are the same text."""

    MOMENT = datetime.datetime(2026, 10, 17, 9, 8, 7)

    def log(self, **kw):
        return deploy.BoardLog(**dict(dict(moment=self.MOMENT, port="/dev/x", image_sha256="abc",
                                           facts_line="facts file spark.json sha256: f", verdict="ready seen",
                                           sentence="it is up", heard="the board said\n"), **kw))

    def test_a_ready_seen_log_reads_as_it_always_did(self):
        self.assertEqual(self.log().text(), "# deploy 2026-10-17T09:08:07 on /dev/x\nimage sha256: abc\n"
                         "facts file spark.json sha256: f\nready seen: it is up\n\nthe board said\n\n")

    def test_a_log_with_no_reset_keeps_the_console_text_before_the_board_s(self):
        text = self.log(verdict="ready unknown", sentence="no reset came",
                        heard="console with DTR and RTS off: waiting for download\nno reset\nOSError\n").text()
        self.assertEqual(text, "# deploy 2026-10-17T09:08:07 on /dev/x\nimage sha256: abc\n"
                         "facts file spark.json sha256: f\nready unknown: no reset came\n\n"
                         "console with DTR and RTS off: waiting for download\nno reset\nOSError\n\n")


class TheConsentTest(unittest.TestCase):
    def test_a_consent_that_does_not_say_who_cannot_be_built(self):
        class Silent(deploy_gate.ConsentStrategy):
            def ask(self, question):
                return True
        with self.assertRaises(TypeError):
            Silent()

    def test_the_terminal_says_who_typed_the_yes(self):
        terminal = deploy_gate.TerminalConsentStrategy("x")
        with mock.patch.object(getpass, "getuser", return_value="ada"):
            self.assertEqual(terminal.who, "typed in a terminal by ada")


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


class TheRerunLineTest(unittest.TestCase):
    """P283: the line a person runs in their own terminal names the script by its whole path, from any folder."""

    def test_a_relative_script_becomes_its_absolute_path(self):
        line = deploy_gate.format_rerun_line("scripts/grant.py", ["--minutes", 30])
        self.assertEqual(line, shlex.join([str(Path("scripts/grant.py").resolve()), "--minutes", "30"]))

    def test_deploy_keeps_ignore_older_runs_in_its_line(self):
        import argparse
        args = argparse.Namespace(project=Path("."), token="aaaa-bbbb", ignore_older_runs=True)
        self.assertTrue(deploy.rerun_line(args, "/dev/cu.usbmodem101").endswith(" --ignore-older-runs"))

    def test_a_path_with_a_space_is_quoted(self):
        self.assertEqual(deploy_gate.format_rerun_line("/my spark/grant.py", []), "'/my spark/grant.py'")


class TerminalConsentTest(unittest.TestCase):
    LINE = "/spark/scripts/deploy.py --project /p --token aaaa-bbbb --port /dev/cu.usbmodem101"

    def ask(self, typed, stdin_tty=True, stdout_tty=True):
        stdout = Stream(tty=stdout_tty)
        consent = deploy_gate.TerminalConsentStrategy(self.LINE, Stream(typed, stdin_tty), stdout)
        return consent.ask("erase ALL of this board's flash?"), stdout.getvalue()

    def test_yes_in_a_terminal_is_the_yes(self):
        self.assertEqual(self.ask("yes\n"), (True, "erase ALL of this board's flash? type yes to go on: "))

    def test_anything_else_is_no(self):
        for typed in ("y\n", "YES please\n", "\n", ""):
            self.assertFalse(self.ask(typed)[0], typed)

    def test_a_pipe_is_no_terminal_and_gives_the_line_to_run(self):
        for stdin_tty, stdout_tty in ((False, True), (True, False), (False, False)):
            with self.assertRaises(deploy_gate.GateClosedError) as shut:
                self.ask("yes\n", stdin_tty, stdout_tty)
            self.assertIn("no terminal to ask you in", str(shut.exception))
            self.assertIn(self.LINE, str(shut.exception))
            self.assertEqual(shut.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
