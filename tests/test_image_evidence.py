"""P337: PassedRunEvidence is the evidence that a passed run in sim/runs/ names the image (A). NoSimulationEvidence is
firmware/ in place of a run (B)."""

import hashlib
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import image_evidence  # noqa: E402
import sim_project  # noqa: E402
import flash_image  # noqa: E402
import tools  # noqa: E402
from image_evidence import ImageEvidence, NoSimulationEvidence, PassedRunEvidence  # noqa: E402
from run_scenario import ScenarioSteps  # noqa: E402
from project_image import DeployError, ProjectImage  # noqa: E402
from test_project_image import project_with_image, write_log  # noqa: E402
from flat_message import NASTY, assert_flat  # noqa: E402

FAILED = "failed (wokwi-cli exit 1)"


def crashing_source():
    """A source that kills the compiler of the Python that runs the test, measured per version (P427, in a child as spark starts it)."""
    if sys.version_info[:2] == (3, 9):
        return "x=" + "1+" * 2000000 + "1\n"  # signal 11 on 3.9; a RecursionError on 3.10
    if sys.version_info[:2] == (3, 10):
        return "x = " + "not " * 200000 + "1\n"  # signal 11 on 3.10; compiles on 3.9
    raise unittest.SkipTest("no input is measured to kill the compiler of Python %d.%d" % sys.version_info[:2])


def answered(stdout, returncode=0):
    """What subprocess.run gives back, with a child's stdout."""
    return subprocess.CompletedProcess([], returncode, stdout=stdout, stderr="")


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
        with mock.patch.object(ProjectImage, "read_run_logs", side_effect=DeployError("cannot read a.log", reason="log_unreadable")), \
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

    def test_a_log_with_no_counts_line_is_older_than_step_counting_and_is_not_said_to_be_not_checked(self):
        self.counted(None)
        self.assertEqual(PassedRunEvidence().caveats(self.image), [
            "the passed run's log is older than step counting: run its scenario again to count its steps"])

    def test_a_log_that_does_not_count_its_steps_is_not_checked_with_its_reason_and_never_lacks_a_step(self):
        for line, why in (("step counts: not read", "the log says its steps were not counted"),
                          ("step counts: nonsense", "the log's step counts line is malformed")):
            self.counted(line)
            with self.subTest(line=line):
                self.assertEqual(PassedRunEvidence().caveats(self.image), [
                    "not checked: %s; run its scenario again to count them" % why])

    def test_only_the_log_that_passed_on_this_image_is_counted(self):
        write_log(self.project, "a.log", "passed", "0")  # another image: not this run
        self.counted("step counts: expect-pin 1, set-control 1, wait-serial 1", "b.log")
        self.assertEqual(PassedRunEvidence(ignore_older_runs=True).caveats(self.image), [])

    def test_a_log_that_cannot_be_read_is_not_checked_with_its_reason(self):
        self.counted("step counts: expect-pin 1, set-control 1, wait-serial 1")
        with mock.patch.object(ProjectImage, "find_passed_logs", return_value=[self.project / "gone.log"]):
            self.assertEqual(PassedRunEvidence().caveats(self.image), [
                "not checked: the log cannot be read; run its scenario again to count them"])

    def named(self, names, name="a.log", marker=None, counts=None):
        """A passed run whose header holds a counts line (when `counts`), a names marker (the count of `names` unless `marker`) and a name line for each, or no marker when `names` is None."""
        write_log(self.project, name, "passed")
        lines = [] if counts is None else [counts]
        if names is not None:
            lines += ["step names: %s" % (len(names) if marker is None else marker)] + ["step name: %s" % each for each in names]
        log = self.project / "sim" / "runs" / name
        log.write_text(log.read_text().replace("\n\n", "\n%s\n\n" % "\n".join(lines), 1)) if lines else None

    OLDER = "not checked: the passed run's log is older than step names; run its scenario again to name its steps"
    NOT_ADDING_UP = "not checked: the log's step names do not match its step names count; run its scenario again to name its steps"

    def test_a_must_line_is_unnamed_when_no_passed_log_names_it(self):
        self.named(["A", "B"], "a.log")
        self.named(["B", "C"], "b.log")
        found = PassedRunEvidence().find_unnamed_must(self.image, ["A", "C", "D", "B"])
        self.assertEqual((found.lines, found.caveats), (["D"], ()))

    def test_case_and_spacing_do_not_matter_but_the_words_do(self):
        self.named(["The  LED Lights", "the led goes off"])
        found = PassedRunEvidence().find_unnamed_must(self.image, ["the led   lights", "The LED goes out"])
        self.assertEqual((found.lines, found.caveats), (["The LED goes out"], ()))

    def test_a_quoted_hash_is_in_the_name_and_an_unquoted_one_starts_a_comment(self):
        steps = ScenarioSteps.from_text("steps:\n  - name: \"fix issue #3\"\n    wait-serial: x\n  - name: fix issue #4\n    wait-serial: y\n")
        self.named(list(steps.names))
        found = PassedRunEvidence().find_unnamed_must(self.image, ["fix issue #3", "fix issue #4"])
        self.assertEqual(found.lines, ["fix issue #4"])

    def test_an_older_log_beside_a_new_one_leaves_the_new_one_to_decide_and_says_nothing(self):
        self.named(None, "a.log")
        self.named(["A"], "b.log")
        found = PassedRunEvidence().find_unnamed_must(self.image, ["A", "B"])
        self.assertEqual((found.lines, found.caveats), (["B"], ()))

    def test_only_older_logs_give_a_caveat_and_no_line(self):
        self.named(None, counts=self.CONTROL)
        found = PassedRunEvidence().find_unnamed_must(self.image, ["A"])
        self.assertEqual((found.lines, found.caveats), ([], (self.OLDER,)))

    def test_a_log_whose_names_do_not_add_up_gives_its_caveat(self):
        self.named(["A"], marker=2, counts=self.CONTROL)
        found = PassedRunEvidence().find_unnamed_must(self.image, ["A"])
        self.assertEqual((found.lines, found.caveats), ([], (self.NOT_ADDING_UP,)))

    def test_a_log_with_a_broken_marker_beside_a_good_one_still_gets_a_caveat_named_by_its_file_and_the_good_one_lists_lines(self):
        self.named(["A"], "a.log", marker=2, counts=self.CONTROL)
        self.named(["A"], "b.log", counts=self.CONTROL)
        found = PassedRunEvidence().find_unnamed_must(self.image, ["A", "B"])
        self.assertEqual((found.lines, found.caveats), (["B"], ("a.log: " + self.NOT_ADDING_UP,)))

    def test_a_log_whose_control_caveat_already_says_to_run_it_again_gets_no_second_caveat(self):
        self.named(None)
        found = PassedRunEvidence().find_unnamed_must(self.image, ["A"])  # no counts either: no set-control anywhere
        self.assertEqual((found.lines, found.caveats), ([], ()))
        self.assertEqual(len(PassedRunEvidence().caveats(self.image)), 1)

    def test_names_not_read_in_the_log_are_a_caveat(self):
        self.named(None, counts=self.CONTROL)
        log = self.project / "sim" / "runs" / "a.log"
        log.write_text(log.read_text().replace("\n\n", "\nstep names: not read\n\n", 1))
        found = PassedRunEvidence().find_unnamed_must(self.image, ["A"])
        self.assertEqual((found.lines, found.caveats), ([], ("not checked: the log says its step names were not read; run its scenario again to name its steps",)))

    def test_a_log_with_a_marker_and_no_name_leaves_every_line_unnamed(self):
        self.named([])
        found = PassedRunEvidence().find_unnamed_must(self.image, ["A", "B"])
        self.assertEqual((found.lines, found.caveats), (["A", "B"], ()))

    def test_no_must_line_gives_no_line_and_no_caveat_even_for_an_older_log(self):
        self.named(None)
        found = PassedRunEvidence().find_unnamed_must(self.image, [])
        self.assertEqual((found.lines, found.caveats), ([], ()))

    def test_the_base_evidence_and_no_simulation_name_nothing(self):
        found = NoSimulationEvidence(self.project).find_unnamed_must(self.image, ["A"])
        self.assertEqual((found.lines, found.caveats), ([], ()))

    def with_section(self, name, note_text):
        """The log `name` with this text as its limits section, where write_log puts it (right after the header)."""
        log = self.project / "sim" / "runs" / name
        header, _, body = log.read_text().partition("\n\n")
        log.write_text("%s\n\n--- what this simulation cannot show ---\n%s\n--- the scenario as run ---\n%s" % (header, note_text, body))

    DISPLAY = ("ONBOARD_DISPLAY", "no part for the display. Test it on the board.")
    BUTTON = ("ONBOARD_BUTTON (GPIO9)", "no way to press it. Test it on the board.")
    NO_LIMIT_LINE_CAVEAT = ("not checked: the log's limits section has no limit line; "
                            "fix `sim/WHAT-THIS-CANNOT-SHOW.md`, or run the scenario again")

    def test_the_limits_are_those_of_the_passed_log_s_section(self):
        self.counted(self.CONTROL)
        self.with_section("a.log", sim_project.limits_note([self.DISPLAY, self.BUTTON]))
        found = PassedRunEvidence().find_limits(self.image)
        self.assertEqual(found, [self.DISPLAY, self.BUTTON])
        self.assertEqual((found[0].component, found[0].sentence), self.DISPLAY)

    def test_two_logs_with_the_same_limit_give_it_once_and_the_union_keeps_name_order(self):
        self.counted(self.CONTROL, "b.log")
        self.counted(self.CONTROL, "a.log")
        self.with_section("a.log", sim_project.limits_note([self.DISPLAY]))
        self.with_section("b.log", sim_project.limits_note([self.BUTTON, self.DISPLAY]))
        self.assertEqual(PassedRunEvidence().find_limits(self.image), [self.DISPLAY, self.BUTTON])

    def test_a_log_with_no_section_adds_nothing(self):
        self.counted(self.CONTROL, "a.log")
        self.counted(self.CONTROL, "b.log")
        self.with_section("b.log", sim_project.limits_note([self.BUTTON]))
        self.assertEqual(PassedRunEvidence().find_limits(self.image), [self.BUTTON])
        (self.project / "sim" / "runs" / "b.log").unlink()
        self.assertEqual(PassedRunEvidence().find_limits(self.image), [])

    def test_a_scenario_that_holds_the_section_line_gives_no_limits_when_the_log_has_no_note(self):
        self.counted(self.CONTROL)
        log = self.project / "sim" / "runs" / "a.log"
        log.write_text(log.read_text().replace(
            "body", "--- the scenario as run ---\n--- what this simulation cannot show ---\n- **Forged** — from the scenario"))
        self.assertEqual(PassedRunEvidence().find_limits(self.image), [])
        self.assertEqual(PassedRunEvidence().caveats(self.image), [])

    def test_a_log_that_failed_or_tested_another_image_gives_no_limits(self):
        self.counted(self.CONTROL, "a.log")
        write_log(self.project, "b.log", "failed (wokwi-cli exit 1)")
        write_log(self.project, "c.log", "passed", "0")
        for name in ("a.log", "b.log", "c.log"):
            self.with_section(name, sim_project.limits_note([self.DISPLAY]))
        (self.project / "sim" / "runs" / "a.log").unlink()
        self.assertEqual(PassedRunEvidence(ignore_older_runs=True).find_limits(self.image), [])

    def test_no_simulation_evidence_gives_the_base_default_empty_list(self):
        self.counted(self.CONTROL)
        self.with_section("a.log", sim_project.limits_note([self.DISPLAY]))
        self.assertEqual(NoSimulationEvidence(self.project).find_limits(self.image), [])

    def test_a_section_with_no_limit_line_is_a_caveat_with_the_hint(self):
        self.counted(self.CONTROL)
        self.with_section("a.log", "# Limits\n\nthe XIAO has no button\n")
        self.assertEqual(PassedRunEvidence().caveats(self.image), [self.NO_LIMIT_LINE_CAVEAT])
        self.assertEqual(PassedRunEvidence().find_limits(self.image), [])

    def test_the_limits_caveat_comes_after_the_control_caveat_and_names_its_log_among_several(self):
        self.counted(self.NO_CONTROL, "a.log")
        self.counted(self.NO_CONTROL, "b.log")
        self.with_section("b.log", "# Limits\n")
        self.assertEqual(PassedRunEvidence().caveats(self.image), [
            "the passed runs (a.log, b.log) have no set-control step (the step that presses a button or sets a sensor) "
            "and no expect-pin step (the step that reads a pin)",
            "b.log: " + self.NO_LIMIT_LINE_CAVEAT])

    def test_an_unreadable_log_beside_a_run_with_a_control_still_gets_the_limits_sentence(self):
        self.counted(self.CONTROL, "a.log")
        gone = self.project / "sim" / "runs" / "gone.log"
        logs = [self.project / "sim" / "runs" / "a.log", gone]
        with mock.patch.object(ProjectImage, "find_passed_logs", return_value=logs):
            self.assertEqual(PassedRunEvidence().caveats(self.image), [
                "gone.log: not checked: the log cannot be read; fix `sim/WHAT-THIS-CANNOT-SHOW.md`, or run the scenario again"])

    def test_a_good_section_adds_no_caveat(self):
        self.counted(self.NO_CONTROL)
        self.with_section("a.log", sim_project.limits_note([self.DISPLAY]))
        self.assertEqual(len(PassedRunEvidence().caveats(self.image)), 1)

    def test_an_unreadable_log_gets_one_sentence_not_two(self):
        with mock.patch.object(ProjectImage, "find_passed_logs", return_value=[self.project / "gone.log"]):
            self.assertEqual(PassedRunEvidence().caveats(self.image), [
                "not checked: the log cannot be read; run its scenario again to count them"])
            self.assertEqual(PassedRunEvidence().find_limits(self.image), [])

    CONTROL = "step counts: expect-pin 0, set-control 1, wait-serial 2"
    NO_CONTROL = "step counts: expect-pin 0, set-control 0, wait-serial 1"
    PIN_NO_CONTROL = "step counts: expect-pin 1, set-control 0, wait-serial 1"

    def test_a_second_passed_run_that_sets_a_control_clears_the_no_control_caveat(self):
        self.counted(self.NO_CONTROL, "a.log")
        self.counted(self.CONTROL, "b.log")
        self.assertEqual(PassedRunEvidence().caveats(self.image), [])

    def test_two_passed_runs_with_no_control_say_it_once_and_name_both_logs(self):
        self.counted(self.NO_CONTROL, "a.log")
        self.counted(self.NO_CONTROL, "b.log")
        self.assertEqual(PassedRunEvidence().caveats(self.image), [
            "the passed runs (a.log, b.log) have no set-control step (the step that presses a button or sets a sensor) "
            "and no expect-pin step (the step that reads a pin)"])

    def test_a_pin_read_by_the_other_run_gives_the_short_sentence(self):
        self.counted(self.NO_CONTROL, "a.log")
        self.counted(self.PIN_NO_CONTROL, "b.log")
        self.assertEqual(PassedRunEvidence().caveats(self.image), [
            "the passed runs (a.log, b.log) have no set-control step (the step that presses a button or sets a sensor)"])

    def test_an_uncounted_run_beside_a_run_with_no_control_makes_no_no_control_claim_and_names_its_log(self):
        self.counted(self.NO_CONTROL, "a.log")
        self.counted(None, "b.log")
        self.assertEqual(PassedRunEvidence().caveats(self.image), [
            "b.log: the passed run's log is older than step counting: run its scenario again to count its steps"])
        self.counted("step counts: nonsense", "b.log")
        self.assertEqual(PassedRunEvidence().caveats(self.image), [
            "b.log: not checked: the log's step counts line is malformed; run its scenario again to count them"])

    def test_a_counted_run_with_a_control_beside_an_uncounted_run_has_no_caveat(self):
        self.counted(None, "a.log")
        self.counted(self.CONTROL, "b.log")
        self.assertEqual(PassedRunEvidence().caveats(self.image), [])

    def test_the_same_pair_the_other_way_round_has_no_caveat_either(self):
        self.counted(self.CONTROL, "a.log")
        self.counted(None, "b.log")
        self.assertEqual(PassedRunEvidence().caveats(self.image), [])

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

    raising = None  # P436: a test sets what the interpreter's lookup raises, so it needs no patch of its own

    def find_interpreter(self, given, project=None, find_tool=None):
        if self.raising:
            raise self.raising
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

    def test_the_four_old_compile_sentences_are_pinned_word_for_word(self):
        (self.firmware / "lib").mkdir()
        bad = self.firmware / "lib" / "bad.py"
        bad.write_text("x = 1\ny = = 2\n")
        self.assertEqual(self.why(), "firmware/lib/bad.py, line 2 does not compile: invalid syntax")
        bad.write_bytes(b"x = 1\x00\n")
        self.assertEqual(self.why(), "firmware/lib/bad.py does not compile: source code string cannot contain null bytes")
        bad.unlink()
        bad.mkdir()  # a folder named like a source file: it cannot be read
        self.assertEqual(self.why(), "cannot read firmware/lib/bad.py: [Errno 21] Is a directory: '%s'" % bad)

    def test_no_main_py_refuses_with_the_run_scenario_sentence(self):
        (self.firmware / "main.py").unlink()
        self.assertIn("no firmware/main.py in %s: the board would boot to a bare prompt" % self.project, self.why())

    def test_no_firmware_folder_refuses_like_no_main_py(self):
        (self.firmware / "main.py").unlink()
        self.firmware.rmdir()
        self.assertIn("no firmware/main.py", self.why())

    def test_a_missing_interpreter_raises_its_tool_problem_with_the_check_words(self):
        self.raising = tools.ToolProblem("no tool holds it")
        with self.assertRaises(tools.ToolProblem) as raised:
            self.why()
        self.assertEqual(str(raised.exception), "cannot check flash-with-firmware.bin against firmware/: no tool holds it")

    def test_a_newline_in_the_image_name_gives_one_line_in_the_check_words_of_a_missing_tool_and_of_an_unreadable_file(self):
        named = mock.Mock(path=Path(NASTY))
        self.raising = tools.ToolProblem("no tool holds it")
        with self.assertRaises(tools.ToolProblem) as raised:
            NoSimulationEvidence(self.project)._why_image_differs(named)
        assert_flat(self, raised.exception)
        self.raising = OSError("gone")
        said = NoSimulationEvidence(self.project)._why_image_differs(named)
        self.assertIn("a?GRANTED: board ok", said)
        self.assertNotIn("\n", said)

    def test_a_missing_littlefs_raises_its_tool_problem_with_the_install_line(self):
        def find(name, *args, **kwargs):
            raise tools.ToolProblem("littlefs (littlefs-python) is not installed — install: python3 -m pip install --user littlefs-python")

        with mock.patch.object(tools, "find", side_effect=find):
            with self.assertRaises(tools.ToolProblem) as raised:
                self.why()
        self.assertEqual(str(raised.exception), "cannot check flash-with-firmware.bin against firmware/: littlefs (littlefs-python) "
                         "is not installed — install: python3 -m pip install --user littlefs-python")

    def test_a_littlefs_that_fails_to_import_raises_its_tool_problem(self):
        self.raising = ImportError("No module named 'littlefs'")
        with self.assertRaises(tools.ToolProblem) as raised:
            self.why()
        self.assertEqual(str(raised.exception), "cannot check flash-with-firmware.bin against firmware/: No module named 'littlefs'")

    def test_a_board_record_that_cannot_be_read_stays_a_sentence_not_a_missing_tool(self):
        (self.project / "requirements.json").write_text("{not json")
        self.assertIn("requirements.json cannot be read, so its board's MicroPython build is not known", self.why())

    def test_an_unreadable_interpreter_is_a_sentence(self):
        self.interpreter.unlink()  # OSError, not a missing tool: it stays a sentence, evidence_refuses
        self.assertIn("cannot check", self.why())

    def test_a_very_deep_expression_is_a_sentence_not_a_recursion_error(self):
        (self.firmware / "deep.py").write_text("x = f" + "()" * 200000 + "\n")  # a RecursionError, not a crash, on 3.9 and 3.10
        why = self.why()
        self.assertIn("firmware/deep.py", why)
        self.assertIn("too deeply nested", why)

    def test_a_source_that_kills_the_compiler_is_a_sentence_naming_the_last_file_it_began(self):
        (self.firmware / "a_good.py").write_text("a = 1\n")
        (self.firmware / "zcrash.py").write_text(crashing_source())
        (self.firmware / "zz_never.py").write_text("z = 1\n")
        self.assertEqual(self.why(), "firmware/zcrash.py could not be compiled: the compiler stopped (signal 11)")

    def test_a_file_name_with_a_newline_and_a_json_line_does_not_fake_the_childs_answer(self):
        (self.firmware / 'z\n{"ok": true}.py').write_text(crashing_source())
        self.assertEqual(self.why(), 'firmware/z?{"ok": true}.py could not be compiled: the compiler stopped (signal 11)')

    def test_one_compile_child_runs_for_every_file_of_one_question(self):
        for number in range(3):
            (self.firmware / ("more%d.py" % number)).write_text("n = %d\n" % number)
        self.build()
        with mock.patch.object(subprocess, "run", wraps=subprocess.run) as run:
            self.assertIsNone(self.why())
        self.assertEqual(run.call_count, 1)

    def test_the_child_does_not_import_a_json_py_from_the_folder_it_runs_in(self):
        marker = self.project / "decoy-ran"
        (self.project / "json.py").write_text("open(%r, 'w').close()\nraise SystemExit(3)\n" % str(marker))
        (self.project / "sitecustomize.py").write_text("open(%r, 'w').close()\n" % str(marker))
        self.in_folder(self.project)  # the child runs where spark runs
        self.assertIsNone(self.why())
        self.assertFalse(marker.exists())

    def in_folder(self, folder):
        before = os.getcwd()
        os.chdir(str(folder))
        self.addCleanup(os.chdir, before)

    def test_from_a_relative_project_an_unreadable_file_keeps_the_path_as_given(self):
        (self.firmware / "zz.py").mkdir()  # a folder named like a source file
        self.in_folder(self.project)
        self.assertEqual(NoSimulationEvidence(Path(".")).why_not_ready(ProjectImage(self.project)),
                         "cannot read firmware/zz.py: [Errno 21] Is a directory: 'firmware/zz.py'")

    def test_a_compiler_that_does_not_finish_in_time_is_a_sentence_naming_the_file(self):
        slow = ("import json, time\nprint(json.dumps({'checking': 'firmware/slow.py'}), flush=True)\ntime.sleep(60)\n")
        with mock.patch.object(image_evidence, "COMPILE_CHILD", slow), mock.patch.object(image_evidence, "COMPILE_TIMEOUT_S", 1):
            self.assertEqual(self.why(), "firmware/slow.py did not compile in 1 s")

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


class CompileCheckTest(unittest.TestCase):
    """What the parent makes of the child's answer, with the child's stdout and exit code given (P427)."""

    def why(self, stdout="", returncode=0, **raised):
        with mock.patch.object(subprocess, "run", return_value=answered(stdout, returncode), **raised) as run:
            why = image_evidence.CompileCheck([("firmware/a.py", "/p/firmware/a.py"), ("firmware/b.py", "/p/firmware/b.py")]).why_not()
        self.run = run
        return why

    def lines(self, *entries):
        return "".join(json.dumps(entry) + "\n" for entry in entries)

    def test_the_child_gets_the_names_and_paths_as_json_on_stdin_and_runs_isolated_for_30_s(self):
        self.why(self.lines({"ok": True}))
        command = self.run.call_args[0][0]
        self.assertEqual((command[0], command[1:3]), (sys.executable, ["-I", "-B"]))
        self.assertEqual(self.run.call_args[1]["input"], '[["firmware/a.py", "/p/firmware/a.py"], ["firmware/b.py", "/p/firmware/b.py"]]')
        self.assertEqual(self.run.call_args[1]["timeout"], 30)

    def test_an_ok_answer_is_none(self):
        self.assertIsNone(self.why(self.lines({"checking": "firmware/a.py"}, {"checking": "firmware/b.py"}, {"ok": True})))

    def test_a_child_killed_by_a_signal_names_the_last_file_it_began(self):
        said = self.lines({"checking": "firmware/a.py"}, {"checking": "firmware/b.py"})
        self.assertEqual(self.why(said, -9), "firmware/b.py could not be compiled: the compiler stopped (signal 9)")

    def test_a_line_cut_in_the_middle_is_not_read(self):
        said = self.lines({"checking": "firmware/a.py"}) + '{"checking": "firmware/b.p'
        self.assertEqual(self.why(said, -11), "firmware/a.py could not be compiled: the compiler stopped (signal 11)")

    def test_a_child_that_died_before_its_first_file_names_the_folder(self):
        self.assertEqual(self.why("", -11), "firmware/ could not be compiled: the compiler stopped (signal 11)")

    def test_a_child_that_exited_with_no_answer_says_its_exit_code(self):
        said = self.lines({"checking": "firmware/a.py"})
        self.assertEqual(self.why(said, 1), "firmware/a.py could not be compiled: the compiler stopped (exit code 1)")

    def test_a_timeout_names_the_last_file_the_child_began_from_bytes_or_text(self):
        said = self.lines({"checking": "firmware/a.py"}, {"checking": "firmware/b.py"})
        for output in (said.encode(), said):
            why = self.why(side_effect=subprocess.TimeoutExpired([], 30, output=output))
            self.assertEqual(why, "firmware/b.py did not compile in 30 s")

    def test_a_timeout_before_any_file_names_the_folder(self):
        self.assertEqual(self.why(side_effect=subprocess.TimeoutExpired([], 30, output=None)), "firmware/ did not compile in 30 s")

    def test_each_failure_kind_has_its_own_sentence(self):
        for entry, sentence in (
                ({"name": "firmware/a.py", "kind": "syntax", "line": 3, "msg": "invalid syntax"},
                 "firmware/a.py, line 3 does not compile: invalid syntax"),
                ({"name": "firmware/a.py", "kind": "too_deep"}, "firmware/a.py is too deeply nested or too big to compile"),
                ({"name": "firmware/a.py", "kind": "bytes", "msg": "a null byte"}, "firmware/a.py does not compile: a null byte"),
                ({"name": "firmware/a.py", "kind": "unreadable", "msg": "gone"}, "cannot read firmware/a.py: gone")):
            self.assertEqual(self.why(self.lines({"checking": "firmware/a.py"}, entry)), sentence)

    def test_a_child_that_exited_0_with_no_answer_says_it_gave_none(self):
        said = self.lines({"checking": "firmware/a.py"})
        self.assertEqual(self.why(said, 0), "firmware/a.py could not be compiled: the compiler gave no answer")
        self.assertEqual(self.why("", 0), "firmware/ could not be compiled: the compiler gave no answer")

    def test_an_answer_with_no_name_names_the_last_file_the_child_began_or_a_firmware_file(self):
        said = self.lines({"checking": "firmware/a.py"}, {"kind": "too_deep"})
        self.assertEqual(self.why(said), "firmware/a.py is too deeply nested or too big to compile")
        self.assertEqual(self.why(self.lines({"kind": "too_deep"})), "a firmware file is too deeply nested or too big to compile")

    def test_a_name_with_a_control_character_is_printed_with_a_question_mark(self):
        said = self.lines({"checking": "firmware/a\x07b.py"})
        self.assertEqual(self.why(said, -11), "firmware/a?b.py could not be compiled: the compiler stopped (signal 11)")
        entry = {"name": "firmware/a\x07b.py", "kind": "too_deep"}
        self.assertEqual(self.why(self.lines(entry)), "firmware/a?b.py is too deeply nested or too big to compile")


if __name__ == "__main__":
    unittest.main()
