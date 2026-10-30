"""P239 PR 8: DeployService runs a deploy without a terminal, over a FirmwarePlatform, and prints nothing."""

import ast
import json
import shlex
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import board_connection  # noqa: E402
import deploy_gate  # noqa: E402
import deploy_service  # noqa: E402
import firmware_platform  # noqa: E402
import flash_image  # noqa: E402
import flasher  # noqa: E402
import project_image  # noqa: E402
import ready_check  # noqa: E402
import image_evidence  # noqa: E402
import tools  # noqa: E402
from fakes import FakeConsent  # noqa: E402
from test_board_look import FOUND, found  # noqa: E402
from test_deploy_gate import GateCase  # noqa: E402

PORT = "/dev/cu.usbmodem101"


def find(name, *args, **kwargs):
    return FOUND["flasher"] if name == "flasher" else found(name)


class ServiceCase(GateCase):
    """A project whose image passed, a look of its board, and a service whose `run` keeps every command."""

    def setUp(self):
        super().setUp()
        self.run_the_scenario()
        self.lines, self.commands = [], []
        self.slept = []
        for patch in (mock.patch.object(tools, "find", side_effect=find),
                      mock.patch.object(deploy_service.DeployService, "sleep", side_effect=self.slept.append)):
            patch.start()
            self.addCleanup(patch.stop)

    def fake_run(self, command, **kwargs):
        self.commands.append(command)
        if self.fails:
            raise subprocess.CalledProcessError(2, command)
        return subprocess.CompletedProcess(command, 0, "", "")

    fails = False

    def service(self, **kwargs):
        return deploy_service.DeployService(self.project, firmware_platform.FirmwarePlatform.micropython(self.project),
                                            image_evidence.PassedRunEvidence(), run=self.fake_run, **kwargs)


class TheFlashTest(ServiceCase):
    def test_deploy_shows_each_command_before_it_runs_and_returns_the_plan_it_ran(self):
        report = self.look()
        planned = self.service().deploy(report, report.token(), FakeConsent(True), self.lines.append)
        self.assertEqual(planned.commands, self.commands)
        self.assertEqual(self.lines, ["  running: %s" % shlex.join(command) for command in self.commands])
        self.assertEqual(len(self.commands), 2)

    def test_the_gate_question_starts_with_the_caveats_of_the_passed_run(self):
        report = self.look()
        consent = FakeConsent(True)
        self.service().deploy(report, report.token(), consent, self.lines.append)
        self.assertTrue(consent.asked[0].startswith("the passed run's scenario has no set-control step"), consent.asked[0])

    def test_the_gate_question_counts_the_unnamed_must_lines_once_after_the_look_s_caveats(self):
        (self.project / ".spark").mkdir()
        (self.project / ".spark" / "project.json").write_text('{"must": ["a", "b"]}')
        report = self.look()
        consent = FakeConsent(True)
        self.service().deploy(report, report.token(), consent, self.lines.append)
        self.assertEqual(consent.asked[0].count("2 must lines were not named by any scenario (see the look)"), 1)
        self.assertTrue(consent.asked[0].startswith("the passed run's scenario has no set-control step"), consent.asked[0])

    def test_a_failed_flash_is_a_deploy_error_with_the_sentence_and_the_hint(self):
        report = self.look()
        self.fails = True
        with self.assertRaises(project_image.DeployError) as failed:
            self.service().deploy(report, report.token(), FakeConsent(True), self.lines.append)
        self.assertTrue(str(failed.exception).startswith("`"))
        self.assertTrue(str(failed.exception).endswith(": if esptool could not connect, " + "hold the board's BOOT button (B, top right, beside the USB-C), press and release RESET (R, top left, beside the USB-C), release BOOT, and run it again. Left and right as seen with the metal shield facing you, USB-C at the top"))  # the XIAO record names the places
        self.assertEqual(len(self.lines), 2)  # the erase and its one retry were shown; the write never started
        self.assertEqual((self.lines[1].startswith("  retry in 5 s: "), self.slept, len(self.commands)), (True, [5], 2))

    def test_a_token_that_is_not_the_looks_is_refused_before_any_command(self):
        report = self.look()
        with self.assertRaises(deploy_gate.GateClosedError):
            self.service().deploy(report, "aaaa-bbbb", FakeConsent(True), self.lines.append)
        self.assertEqual((self.commands, self.lines), ([], []))

    def test_a_yes_that_ends_before_the_flash_stops_it(self):
        class Ended(FakeConsent):
            def require_ready(self):
                raise project_image.DeployError("the yes ended", reason="grant_ended")
        report = self.look()
        with self.assertRaises(project_image.DeployError):
            self.service().deploy(report, report.token(), Ended(True), self.lines.append)
        self.assertEqual(self.commands, [])


class TheNoSimulationServiceTest(ServiceCase):
    def service(self, **kwargs):
        return deploy_service.DeployService(self.project, firmware_platform.FirmwarePlatform.micropython(self.project),
                                            image_evidence.NoSimulationEvidence(self.project), run=self.fake_run, **kwargs)

    def build(self):
        patcher = mock.patch.object(flash_image, "interpreter_for",
                                    side_effect=lambda given, project=None, find_tool=None: flash_image.Interpreter(self.micropython, 0))
        patcher.start()
        self.addCleanup(patcher.stop)
        for log in (self.project / "sim" / "runs").glob("*.log"):
            log.unlink()
        self.image.write_bytes(flash_image.image(self.micropython.read_bytes(), flash_image.files_under(self.project / "firmware")))

    def test_the_gate_question_starts_with_the_caveat_and_the_plan_has_no_notes(self):
        self.build()
        report = self.look(evidence=image_evidence.NoSimulationEvidence(self.project))
        consent = FakeConsent(True)
        planned = self.service().deploy(report, report.token(), consent, self.lines.append)
        self.assertTrue(consent.asked[0].startswith("no simulation tested this image. erase ALL"))
        self.assertEqual((planned.notes, len(self.commands)), ([], 2))

    def test_the_gate_question_names_the_last_deploy_the_store_holds(self):
        self.build()
        self.record_a_deploy()
        report = self.look(evidence=image_evidence.NoSimulationEvidence(self.project))
        consent = FakeConsent(True)
        self.service().deploy(report, report.token(), consent, self.lines.append)
        self.assertIn("erase ALL of this board's flash (spark's store record names blink-c6 as its last deploy here, "
                      "2026-10-19T09:24:50+02:00, ready seen) and write ", consent.asked[0])

    def test_a_refusal_is_a_deploy_error_before_any_command(self):
        self.build()
        (self.project / "firmware" / "main.py").write_text("print('changed')\n")
        with self.assertRaises(project_image.DeployError) as refused:
            self.service().plan()
        self.assertIn("flash_image.py --project", str(refused.exception))
        self.assertEqual(self.commands, [])


class TheVerifyTest(ServiceCase):
    def test_a_fault_reading_the_passed_log_after_the_flash_is_not_turned_into_a_sentence(self):
        report = self.look()
        service = self.service()
        planned = service.deploy(report, report.token(), FakeConsent(True), self.lines.append)
        with mock.patch.object(project_image.ProjectImage, "find_passed_log", side_effect=project_image.DeployError("x", reason="log_unreadable")):
            with self.assertRaises(project_image.DeployError):
                service.verify(report, planned, self.lines.append)

    def test_main_lets_a_fault_after_the_flash_through_as_a_traceback(self):
        token = self.token()
        real = project_image.ProjectImage.find_passed_log

        def find_passed_log(image):
            if self.flashed():  # only after the flash
                raise project_image.DeployError("the log is gone", reason="log_unreadable")
            return real(image)
        with mock.patch.object(project_image.ProjectImage, "find_passed_log", find_passed_log):
            with self.assertRaises(project_image.DeployError):
                self.deploy("--token", token, consent=FakeConsent(True))


    def test_a_who_that_cannot_be_read_is_a_store_record_not_written_after_the_board_log_line(self):
        class Nobody(FakeConsent):
            @property
            def who(self):
                raise OSError("no user")
        code, said, _ = self.deploy("--token", self.token(), consent=Nobody(True))
        lines = said.splitlines()
        self.assertEqual(code, 0)
        self.assertTrue(lines[-1].startswith("  store record: not written: no user"), lines[-1])
        self.assertTrue(lines[-2].startswith("  board log: "), lines[-2])

    def test_a_who_that_cannot_be_read_still_gives_the_envelope_after_the_flash(self):
        class Nobody(FakeConsent):
            @property
            def who(self):
                raise KeyError("getpwuid(): uid not found: 501")  # what getpass raises before Python 3.13
        code, said, _ = self.deploy("--json", "--token", self.token(), consent=Nobody(True))
        envelope = json.loads(said)
        self.assertEqual((code, envelope["data"]["yes"]["who"]), (0, "not known ('getpwuid(): uid not found: 501')"))
        self.assertIsNone(envelope["data"]["store_record"])  # the record cannot say whose yes, so it is not written
        self.assertIn("uid not found", envelope["data"]["store_record_error"])


class ThePlanTest(ServiceCase):
    def test_plan_checks_the_image_before_the_tools(self):
        (self.project / "sim" / "runs" / "s.log").unlink()
        with mock.patch.object(tools, "find", side_effect=AssertionError("tools asked first")):
            with self.assertRaises(project_image.DeployError):
                self.service().plan()

    def test_a_chip_problem_shows_before_a_missing_tool(self):
        (self.project / "requirements.json").unlink()
        with mock.patch.object(tools, "find", side_effect=tools.ToolProblem("flasher is not installed")):
            with self.assertRaises(project_image.DeployError):
                self.service().plan()

    def test_plan_asks_for_the_flasher_before_the_shell(self):
        asked = []
        with mock.patch.object(tools, "find", side_effect=lambda name, *a, **k: asked.append(name) or find(name)):
            self.service().plan()
        self.assertEqual(asked, ["flasher", "board-shell"])


class TheFirmwarePlatformTest(ServiceCase):
    def test_the_micropython_platform_makes_esptool_and_mpremote_parts(self):
        platform = firmware_platform.FirmwarePlatform.micropython(self.project)
        self.assertIsInstance(platform.make_flasher(), flasher.EsptoolFlasher)
        self.assertEqual(platform.make_flasher().chip, "esp32c6")
        command = platform.make_shell_command()
        connection = platform.make_connection(command, PORT)
        self.assertIsInstance(connection, board_connection.BoardConnection)
        self.assertEqual(connection.repl_command(), command + ["connect", PORT, "repl"])
        self.assertIsInstance(platform.make_ready_check(connection), ready_check.ReadyCheck)
        self.assertIsNone(platform.make_console_probe(None))
        self.assertEqual(platform.board_of(), "xiao-esp32-c6")

    def test_the_flasher_carries_the_places_of_the_projects_record(self):
        hint = firmware_platform.FirmwarePlatform.micropython(self.project).make_flasher().boot_hint
        self.assertIn("BOOT button (B, top right, beside the USB-C)", hint)
        self.assertIn("RESET (R, top left, beside the USB-C)", hint)
        self.assertEqual(firmware_platform.record_of(self.project)["chip"], "esp32c6")

    def test_an_unknown_board_is_a_deploy_error_before_a_missing_tool(self):
        (self.project / "requirements.json").write_text(json.dumps({"board": "no-such-board"}))
        asked = []
        with mock.patch.object(tools, "find", side_effect=lambda name, *a, **k: asked.append(name) or find(name)):
            with self.assertRaises(project_image.DeployError):
                firmware_platform.FirmwarePlatform.micropython(self.project).make_flasher()
        self.assertEqual(asked, [])


class TheServiceHoldsNoPrintTest(unittest.TestCase):
    MODULES = ("deploy_service.py", "firmware_platform.py")

    def test_no_print_and_no_exit(self):
        for name in self.MODULES:
            tree = ast.parse((ROOT / "scripts" / name).read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    function = node.func
                    called = function.id if isinstance(function, ast.Name) else (
                        function.attr if isinstance(function, ast.Attribute) else "")
                    self.assertNotIn(called, ("print", "exit"), "%s:%d" % (name, node.lineno))

    def test_the_platform_does_not_import_the_service(self):
        tree = ast.parse((ROOT / "scripts" / "firmware_platform.py").read_text())
        imported = {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
        imported |= {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
        self.assertNotIn("deploy_service", imported)


if __name__ == "__main__":
    unittest.main()
