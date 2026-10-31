"""P239 PR 5 (#238): ProjectImage is the image a project's sim/wokwi.toml names and the run logs that name it."""

import hashlib
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import project_image  # noqa: E402
import run_scenario  # noqa: E402
from project_image import DeployError, ProjectImage  # noqa: E402

IMAGE = b"image"
DIGEST = hashlib.sha256(IMAGE).hexdigest()


def project_with_image():
    project = Path(tempfile.mkdtemp())
    (project / "sim" / "runs").mkdir(parents=True)
    (project / "sim" / "wokwi.toml").write_text("")
    (project / "sim" / "flash-with-firmware.bin").write_bytes(IMAGE)
    return project


def write_log(project, name, verdict, sha256=DIGEST):
    line = "image sha256: %s\n" % sha256 if sha256 else ""
    (project / "sim" / "runs" / name).write_text("# %s\nverdict: %s\n%s\nbody\n" % (name, verdict, line))


class TheImageTest(unittest.TestCase):
    def test_the_path_is_the_image_wokwi_toml_names_and_the_sha256_is_its_hash(self):
        project = project_with_image()
        image = ProjectImage(project)
        self.assertEqual(image.path, project / "sim" / "flash-with-firmware.bin")
        self.assertEqual(image.sha256, DIGEST)

    def test_a_project_with_no_wokwi_toml_is_a_deploy_error_that_says_to_build(self):
        with self.assertRaises(DeployError) as said:
            ProjectImage(Path(tempfile.mkdtemp()))
        self.assertIn("build with /spark:build --keep . first", str(said.exception))
        self.assertEqual(said.exception.reason, "no_sim_toml")

    def test_a_toml_with_no_image_file_is_a_deploy_error_that_says_to_run_a_scenario(self):
        project = project_with_image()
        (project / "sim" / "flash-with-firmware.bin").unlink()
        with self.assertRaises(DeployError) as said:
            ProjectImage(project)
        self.assertIn("run a scenario first", str(said.exception))
        self.assertEqual(said.exception.reason, "no_image")

    def test_the_missing_image_sentence_names_the_no_simulation_way_with_the_build_command(self):
        # P463: a build writes no image, so a person with no simulation needs the build command and the look
        project = project_with_image()
        (project / "sim" / "flash-with-firmware.bin").unlink()
        with self.assertRaises(DeployError) as said:
            ProjectImage(project)
        self.assertTrue(str(said.exception).endswith(
            ", or, with no simulation, the board is the test: build it with flash_image.py --project %s --files firmware -o %s, "
            "then run look.py --no-simulation" % (project.resolve(), (project / "sim" / "flash-with-firmware.bin").resolve())),
            str(said.exception))

    def test_a_path_with_a_space_in_the_build_command_is_quoted(self):
        project = project_with_image().rename(Path(tempfile.mkdtemp()) / "my project")
        (project / "sim" / "flash-with-firmware.bin").unlink()
        with self.assertRaises(DeployError) as said:
            ProjectImage(project)
        self.assertIn("--project '%s' --files" % project.resolve(), str(said.exception))

    def test_a_firmware_line_that_is_no_string_is_a_deploy_error_with_one_sentence(self):
        # P429: `firmware = 3` raised a TypeError
        project = project_with_image()
        (project / "sim" / "wokwi.toml").write_text("[wokwi]\nfirmware = 3\n")
        with self.assertRaises(DeployError) as said:
            ProjectImage(project)
        self.assertEqual(str(said.exception), "sim/wokwi.toml line 2 names the firmware in a form spark cannot read. "
                         'To fix it, write it as firmware = "name.bin".')
        self.assertEqual(said.exception.reason, "firmware_line_bad")

    def test_an_empty_firmware_name_and_a_file_that_is_no_text_each_have_their_own_sentence(self):
        project = project_with_image()
        (project / "sim" / "wokwi.toml").write_text('[wokwi]\nfirmware = ""\n')
        with self.assertRaises(DeployError) as empty:
            ProjectImage(project)
        self.assertEqual(str(empty.exception), 'sim/wokwi.toml line 2 names no file. To fix it, write it as firmware = "name.bin".')
        (project / "sim" / "wokwi.toml").write_bytes(b"\xff\xfe\x00")
        with self.assertRaises(DeployError) as unreadable:
            ProjectImage(project)
        self.assertEqual(str(unreadable.exception), "sim/wokwi.toml cannot be read: it is not text in UTF-8.")
        self.assertEqual((empty.exception.reason, unreadable.exception.reason), ("firmware_line_bad", "firmware_line_bad"))

    def test_an_image_outside_sim_is_a_deploy_error_as_it_is_a_refused_run(self):
        # P429: the look and the deploy took "../x.bin" and "/abs/x.bin", which no run writes
        project = project_with_image()
        for named in ("../x.bin", "/abs/x.bin"):
            (project / "sim" / "wokwi.toml").write_text('firmware = "%s"\n' % named)
            with self.assertRaises(DeployError) as said:
                ProjectImage(project)
            self.assertEqual(str(said.exception), "wokwi.toml names %s, outside sim/, and a run writes its image only "
                             "inside sim/" % (project / "sim" / named))
            self.assertEqual(said.exception.reason, "firmware_line_bad")

    def test_a_new_project_image_after_the_file_changed_has_the_new_sha256(self):
        project = project_with_image()
        ProjectImage(project).sha256
        (project / "sim" / "flash-with-firmware.bin").write_bytes(b"changed")
        self.assertEqual(ProjectImage(project).sha256, hashlib.sha256(b"changed").hexdigest())

    def test_the_constructor_reads_no_log(self):
        project = project_with_image()
        write_log(project, "a.log", "passed")
        with mock.patch.object(run_scenario, "run_record", side_effect=OSError("denied")):
            ProjectImage(project)

    def test_the_error_is_an_exception_named_for_what_it_is(self):
        self.assertTrue(issubclass(DeployError, Exception))
        self.assertFalse(hasattr(project_image, "DeployProblem"))


class TheRunLogsTest(unittest.TestCase):
    def setUp(self):
        self.project = project_with_image()
        self.image = ProjectImage(self.project)

    def test_the_logs_are_listed_by_name_with_verdict_and_sha256_and_a_folder_named_log_is_skipped(self):
        write_log(self.project, "b.log", "failed (wokwi-cli exit 1)", None)
        write_log(self.project, "a.log", "passed")
        (self.project / "sim" / "runs" / "dir.log").mkdir()
        self.assertEqual(self.image.read_run_logs(),
                         [(self.project / "sim" / "runs" / "a.log", "passed", DIGEST),
                          (self.project / "sim" / "runs" / "b.log", "failed (wokwi-cli exit 1)", None)])

    def test_a_log_that_cannot_be_read_is_a_deploy_error(self):
        write_log(self.project, "a.log", "passed")
        with mock.patch.object(run_scenario, "run_record", side_effect=OSError("denied")), \
                self.assertRaises(DeployError) as said:
            self.image.read_run_logs()
        self.assertIn("cannot read", str(said.exception))
        self.assertEqual(said.exception.reason, "log_unreadable")

    def test_why_untested_is_none_for_a_passed_run_of_this_image(self):
        write_log(self.project, "a.log", "passed")
        self.assertIsNone(self.image.why_untested())

    def test_why_untested_names_a_failed_run_of_this_image_even_beside_a_passed_one(self):
        write_log(self.project, "a.log", "passed")
        write_log(self.project, "b.log", "failed (wokwi-cli exit 1)")
        self.assertIn("b.log did not pass on this image (verdict: failed (wokwi-cli exit 1))", self.image.why_untested())

    def test_why_untested_says_so_when_no_run_names_this_image(self):
        write_log(self.project, "a.log", "passed", "0")
        self.assertIn("no run in sim/runs/ tested %s as it is now" % self.image.path.name, self.image.why_untested())

    def test_the_untested_sentence_names_the_no_simulation_way(self):
        self.assertTrue(self.image.why_untested().endswith(
            "run its scenario again with run_scenario.py, or, with no simulation, the board is the test: run look.py --no-simulation"))

    def test_why_other_runs_is_none_when_every_log_names_this_image(self):
        write_log(self.project, "a.log", "passed")
        self.assertIsNone(self.image.why_other_runs())

    def test_why_other_runs_names_a_log_of_another_image_and_a_log_of_an_older_spark(self):
        write_log(self.project, "a.log", "passed")
        write_log(self.project, "old.log", "passed", "0")
        write_log(self.project, "older.log", "passed", None)
        self.assertEqual(self.image.why_other_runs(),
                         "old.log tested another image, not this one, and older.log names no image (an older spark): "
                         "run those scenarios again to test this one")

    def test_why_other_runs_for_one_older_log_speaks_in_the_singular(self):
        write_log(self.project, "older.log", "passed", None)
        self.assertEqual(self.image.why_other_runs(),
                         "older.log names no image (an older spark): run that scenario again to test this one")

    def test_why_other_runs_for_two_older_logs_speaks_in_the_plural(self):
        write_log(self.project, "a.log", "passed", None)
        write_log(self.project, "b.log", "passed", None)
        self.assertEqual(self.image.why_other_runs(),
                         "a.log, b.log name no image (an older spark): run those scenarios again to test this one")

    def test_a_failed_run_on_the_same_image_is_never_the_passed_log(self):
        write_log(self.project, "a.log", "failed (wokwi-cli exit 1)")
        write_log(self.project, "b.log", "passed")
        self.assertEqual(self.image.find_passed_log(), self.project / "sim" / "runs" / "b.log")

    def test_no_passed_run_of_this_image_means_no_passed_log(self):
        write_log(self.project, "a.log", "passed", "0")
        self.assertIsNone(self.image.find_passed_log())

    def test_find_passed_logs_lists_every_passed_log_of_this_image_in_name_order(self):
        write_log(self.project, "c.log", "passed")
        write_log(self.project, "a.log", "passed")
        write_log(self.project, "b.log", "failed (wokwi-cli exit 1)")
        write_log(self.project, "d.log", "passed", "0")  # another image
        runs = self.project / "sim" / "runs"
        self.assertEqual(self.image.find_passed_logs(), [runs / "a.log", runs / "c.log"])
        self.assertEqual(self.image.find_passed_log(), runs / "a.log")

    def test_find_passed_logs_is_empty_when_no_run_passed(self):
        self.assertEqual(self.image.find_passed_logs(), [])


if __name__ == "__main__":
    unittest.main()
