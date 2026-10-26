"""P337: PassedRunEvidence is the evidence that a passed run in sim/runs/ names the image (A). NoSimulationEvidence is
firmware/ in place of a run (B)."""

import hashlib
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import image_evidence  # noqa: E402
import flash_image  # noqa: E402
import tools  # noqa: E402
from image_evidence import ImageEvidence, NoSimulationEvidence, PassedRunEvidence  # noqa: E402
from project_image import DeployError, ProjectImage  # noqa: E402
from test_project_image import project_with_image, write_log  # noqa: E402

FAILED = "failed (wokwi-cli exit 1)"


class PassedRunEvidenceTest(unittest.TestCase):
    def setUp(self):
        self.project = project_with_image()
        self.image = ProjectImage(self.project)

    def test_it_is_an_image_evidence(self):
        self.assertIsInstance(PassedRunEvidence(), ImageEvidence)

    def test_a_passed_run_of_this_image_is_ready(self):
        write_log(self.project, "a.log", "passed")
        self.assertIsNone(PassedRunEvidence().why_not_ready(self.image))

    def test_a_failed_run_of_this_image_refuses_even_when_older_runs_are_ignored(self):
        write_log(self.project, "a.log", FAILED)
        for ignore in (False, True):
            self.assertIn("a.log did not pass on this image", PassedRunEvidence(ignore).why_not_ready(self.image))

    def test_no_run_naming_this_image_refuses(self):
        self.assertIn("no run in sim/runs/ tested", PassedRunEvidence().why_not_ready(self.image))

    def test_a_run_of_another_image_refuses_with_its_way_out(self):
        write_log(self.project, "a.log", "passed")
        write_log(self.project, "old.log", "passed", "0")
        evidence = PassedRunEvidence()
        other = self.image.why_other_runs()
        self.assertEqual(evidence.why_not_ready(self.image), other)
        self.assertEqual(evidence.way_out(self.image), ". If a log's scenario is gone, delete the log after the person says yes. To flash anyway, "
                         "pass --ignore-older-runs, and deploy.py names the log in a note")

    def test_ignoring_older_runs_makes_a_run_of_another_image_a_note(self):
        write_log(self.project, "a.log", "passed")
        write_log(self.project, "old.log", "passed", "0")
        evidence = PassedRunEvidence(ignore_older_runs=True)
        self.assertIsNone(evidence.why_not_ready(self.image))
        self.assertEqual(evidence.way_out(self.image), "")
        self.assertEqual(evidence.notes(self.image), [self.image.why_other_runs()])

    def test_a_file_newer_than_the_image_is_a_note(self):
        write_log(self.project, "a.log", "passed")
        firmware = self.project / "firmware"
        firmware.mkdir()
        (firmware / "main.py").write_text("x = 1\n")
        later = self.image.path.stat().st_mtime + 10
        os.utime(firmware / "main.py", (later, later))
        notes = PassedRunEvidence().notes(self.image)
        self.assertEqual(len(notes), 1)
        self.assertTrue(notes[0].startswith("firmware/main.py changed after this image was made"))

    def test_a_file_as_old_as_the_image_is_no_note(self):
        write_log(self.project, "a.log", "passed")
        firmware = self.project / "firmware"
        firmware.mkdir()
        (firmware / "main.py").write_text("x = 1\n")
        made = self.image.path.stat().st_mtime
        os.utime(firmware / "main.py", (made, made))
        self.assertEqual(PassedRunEvidence().notes(self.image), [])

    def test_notes_are_empty_when_nothing_is_newer_and_every_log_names_the_image(self):
        write_log(self.project, "a.log", "passed")
        self.assertEqual(PassedRunEvidence().notes(self.image), [])

    def test_expected_files_are_the_passed_logs_file_lines_or_nothing(self):
        self.assertEqual(PassedRunEvidence().expected_files(self.image), {})
        write_log(self.project, "a.log", "passed")
        with mock.patch.object(image_evidence, "file_hashes", side_effect=lambda log: {"/main.py": log.name}):
            self.assertEqual(PassedRunEvidence().expected_files(self.image), {"/main.py": "a.log"})

    def test_argv_names_ignore_older_runs_only_when_it_holds(self):
        self.assertEqual(PassedRunEvidence().argv(), [])
        self.assertEqual(PassedRunEvidence(True).argv(), ["--ignore-older-runs"])

    def test_only_ignoring_older_runs_refuses_a_deploy_grant(self):
        self.assertIsNone(PassedRunEvidence().grant_refusal)
        self.assertEqual(PassedRunEvidence(True).grant_refusal, "ignore older runs")

    def test_a_log_that_cannot_be_read_is_a_deploy_error(self):
        write_log(self.project, "a.log", "passed")
        with mock.patch.object(ProjectImage, "read_run_logs", side_effect=DeployError("cannot read a.log")), \
                self.assertRaises(DeployError):
            PassedRunEvidence().why_not_ready(self.image)

    def test_a_passed_run_is_simulation_passed(self):
        self.assertEqual(PassedRunEvidence().simulation, "passed")

    def counted(self, line, name="a.log"):
        """A passed run whose header holds this step-counts line, or none when the line is None."""
        write_log(self.project, name, "passed")
        if line is not None:
            log = self.project / "sim" / "runs" / name
            log.write_text(log.read_text().replace("\n\n", "\n%s\n\n" % line, 1))

    def test_a_scenario_with_a_control_and_a_pin_has_no_caveat(self):
        self.counted("step counts: expect-pin 1, set-control 1, wait-serial 2")
        self.assertEqual(PassedRunEvidence().caveats(self.image), [])

    def test_a_scenario_with_a_control_and_no_pin_has_no_caveat(self):
        self.counted("step counts: expect-pin 0, set-control 2, wait-serial 1")
        self.assertEqual(PassedRunEvidence().caveats(self.image), [])

    def test_a_scenario_with_a_pin_and_no_control_says_so(self):
        self.counted("step counts: expect-pin 1, set-control 0, wait-serial 1")
        self.assertEqual(PassedRunEvidence().caveats(self.image), [
            "the passed run's scenario has no set-control step (the step that presses a button or sets a sensor)"])

    def test_a_scenario_with_no_control_and_no_pin_says_both(self):
        for line in ("step counts: expect-pin 0, set-control 0, wait-serial 1", "step counts: delay 3, wait-serial 1"):
            self.counted(line)
            with self.subTest(line=line):
                self.assertEqual(PassedRunEvidence().caveats(self.image), [
                    "the passed run's scenario has no set-control step (the step that presses a button or sets a "
                    "sensor) and no expect-pin step (the step that reads a pin)"])

    def test_a_log_that_does_not_count_its_steps_is_not_checked_with_its_reason_and_never_lacks_a_step(self):
        for line, why in ((None, "the passed run's log does not count its steps"),
                          ("step counts: not read", "the log says its steps were not counted"),
                          ("step counts: nonsense", "the log's step counts line is malformed")):
            self.counted(line)
            with self.subTest(line=line):
                self.assertEqual(PassedRunEvidence().caveats(self.image), [
                    "not checked: %s: run its scenario again to count them" % why])

    def test_only_the_log_that_passed_on_this_image_is_counted(self):
        write_log(self.project, "a.log", "passed", "0")  # another image: not this run
        self.counted("step counts: expect-pin 1, set-control 1, wait-serial 1", "b.log")
        self.assertEqual(PassedRunEvidence(ignore_older_runs=True).caveats(self.image), [])

    def test_a_log_that_cannot_be_read_is_not_checked_with_its_reason(self):
        self.counted("step counts: expect-pin 1, set-control 1, wait-serial 1")
        with mock.patch.object(ProjectImage, "find_passed_log", return_value=self.project / "gone.log"):
            self.assertEqual(PassedRunEvidence().caveats(self.image), [
                "not checked: the log cannot be read: run its scenario again to count them"])

    def test_no_passed_run_gives_no_caveat(self):
        self.assertEqual(PassedRunEvidence().caveats(self.image), [])


class NoSimulationEvidenceTest(unittest.TestCase):
    INTERPRETER = b"\xe9" + b"\x00" * 99

    def setUp(self):
        self.project = project_with_image()
        self.firmware = self.project / "firmware"
        self.firmware.mkdir()
        (self.firmware / "main.py").write_text("import machine\nmachine.PWM(machine.Pin(1))\nprint('ready')\n")
        patcher = mock.patch.object(flash_image, "interpreter_for", side_effect=self.find_interpreter)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.offset = 0
        self.interpreter = self.project / "micropython.bin"
        self.interpreter.write_bytes(self.INTERPRETER)
        self.build()

    def find_interpreter(self, given, project=None):
        return flash_image.Interpreter(self.interpreter, self.offset)

    def build(self, offset=None):
        (self.project / "sim" / "flash-with-firmware.bin").write_bytes(
            flash_image.image(self.INTERPRETER, flash_image.files_under(self.firmware),
                              offset=self.offset if offset is None else offset))
        self.image = ProjectImage(self.project)

    def why(self):
        return NoSimulationEvidence(self.project).why_not_ready(ProjectImage(self.project))

    def test_it_is_an_image_evidence(self):
        self.assertIsInstance(NoSimulationEvidence(self.project), ImageEvidence)

    def test_firmware_that_uses_pwm_and_an_image_of_it_are_ready_with_no_run_log(self):
        self.assertIsNone(self.why())

    def test_an_image_with_the_esp32_s_offset_is_ready_and_one_built_at_0_is_not(self):
        self.offset = 0x1000  # the original ESP32's build starts there (P335)
        self.build()
        self.assertIsNone(self.why())
        self.build(offset=0)
        self.assertIn("does not hold firmware/ as it is now", self.why())

    def test_a_file_changed_after_the_image_refuses_and_names_the_build_command(self):
        (self.firmware / "main.py").write_text("print('ready')\nprint(2)\n")
        self.assertEqual(self.why(), "flash-with-firmware.bin does not hold firmware/ as it is now: build it with "
                         "flash_image.py --project %s --files firmware -o %s" % (self.project.resolve(), self.image.path))

    def test_a_file_that_does_not_compile_refuses_with_its_file_and_line(self):
        (self.firmware / "lib").mkdir()
        (self.firmware / "lib" / "bad.py").write_text("x = 1\ny = (\n")
        why = self.why()
        self.assertTrue(why.startswith("firmware/lib/bad.py, line "), why)
        self.assertIn("does not compile", why)

    def test_no_main_py_refuses_with_the_run_scenario_sentence(self):
        (self.firmware / "main.py").unlink()
        self.assertIn("no firmware/main.py in %s: the board would boot to a bare prompt" % self.project, self.why())

    def test_no_firmware_folder_refuses_like_no_main_py(self):
        (self.firmware / "main.py").unlink()
        self.firmware.rmdir()
        self.assertIn("no firmware/main.py", self.why())

    def test_no_interpreter_is_a_sentence_not_a_traceback(self):
        with mock.patch.object(flash_image, "interpreter_for", side_effect=tools.ToolProblem("no tool holds it")):
            self.assertEqual(self.why(), "cannot check flash-with-firmware.bin against firmware/: no tool holds it")

    def test_a_missing_littlefs_is_a_sentence_too(self):
        with mock.patch.object(flash_image, "image", side_effect=ImportError("No module named 'littlefs'")):
            self.assertIn("No module named 'littlefs'", self.why())

    def test_an_unreadable_interpreter_is_a_sentence(self):
        self.interpreter.unlink()
        self.assertIn("cannot check", self.why())

    def test_a_very_deep_expression_is_a_sentence_not_a_recursion_error(self):
        (self.firmware / "deep.py").write_text("x = f" + "()" * 200000 + "\n")  # too deep on 3.9 to 3.13 alike
        why = self.why()
        self.assertIn("firmware/deep.py", why)
        self.assertIn("too deeply nested", why)

    def test_a_file_too_big_for_the_image_is_a_sentence_not_a_littlefs_error(self):
        (self.firmware / "big.bin").write_bytes(os.urandom(2200 * 1024))
        self.assertIn("firmware/ does not fit the image's file system", self.why())

    def test_a_failed_run_of_this_image_refuses_and_names_the_log_and_its_verdict(self):
        write_log(self.project, "bad.log", FAILED, ProjectImage(self.project).sha256)
        why = self.why()
        self.assertIn("bad.log did not pass on this image", why)
        self.assertIn(FAILED, why)

    def test_a_passed_run_of_this_image_does_not_matter(self):
        write_log(self.project, "a.log", "passed", ProjectImage(self.project).sha256)
        self.assertIsNone(self.why())

    def test_the_expected_files_are_the_sha256_of_each_file_under_firmware(self):
        (self.firmware / "lib").mkdir()
        (self.firmware / "lib" / "a.py").write_text("a = 1\n")
        expected = NoSimulationEvidence(self.project).expected_files(self.image)
        self.assertEqual(expected, {"/lib/a.py": hashlib.sha256(b"a = 1\n").hexdigest(),
                                    "/main.py": hashlib.sha256((self.firmware / "main.py").read_bytes()).hexdigest()})

    def test_it_says_none_with_its_caveat_flag_and_no_notes_and_never_answers_for_a_grant(self):
        evidence = NoSimulationEvidence(self.project)
        self.assertEqual((evidence.simulation, evidence.caveats(self.image), evidence.argv(), evidence.notes(self.image)),
                         ("none", ["no simulation tested this image"], ["--no-simulation"], []))
        self.assertEqual(evidence.grant_refusal, "no simulation")
        self.assertEqual(evidence.way_out(self.image), "")


if __name__ == "__main__":
    unittest.main()
