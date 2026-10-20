"""P337 PR A: PassedRunEvidence is the evidence that a passed run in sim/runs/ names the image."""

import os
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  P172: this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import image_evidence  # noqa: E402
from image_evidence import ImageEvidence, PassedRunEvidence  # noqa: E402
from project_image import DeployError, ProjectImage  # noqa: E402
from test_project_image import project_with_image, write_log  # noqa: E402

FAILED = "failed (wokwi-cli exit 1)"


class PassedRunEvidenceTest(unittest.TestCase):
    def setUp(self):
        self.project = project_with_image()
        self.image = ProjectImage(self.project)

    def test_it_is_an_image_evidence_that_says_passed(self):
        evidence = PassedRunEvidence()
        self.assertIsInstance(evidence, ImageEvidence)
        self.assertEqual((evidence.simulation, evidence.caveat()), ("passed", None))

    def test_a_passed_run_of_this_image_is_ready(self):
        write_log(self.project, "a.log", "passed")
        self.assertIsNone(PassedRunEvidence().why_not_ready(self.image))

    def test_a_failed_run_of_this_image_refuses_even_when_older_runs_are_ignored(self):
        write_log(self.project, "a.log", FAILED)
        for ignore in (False, True):
            self.assertIn("a.log did not pass on this image", PassedRunEvidence(ignore).why_not_ready(self.image))

    def test_no_run_naming_this_image_refuses(self):
        self.assertIn("no run in sim/runs/ tested", PassedRunEvidence().why_not_ready(self.image))

    def test_a_run_of_another_image_refuses_and_the_way_out_is_added_on_ask(self):
        write_log(self.project, "a.log", "passed")
        write_log(self.project, "old.log", "passed", "0")
        evidence = PassedRunEvidence()
        other = self.image.why_other_runs()
        self.assertEqual(evidence.why_not_ready(self.image), other)
        self.assertEqual(evidence.why_not_ready(self.image, with_way_out=True),
                         other + ". If a log's scenario is gone, delete the log after the person says yes. To flash anyway, "
                         "pass --ignore-older-runs, and deploy.py names the log in a note")

    def test_ignoring_older_runs_makes_a_run_of_another_image_a_note(self):
        write_log(self.project, "a.log", "passed")
        write_log(self.project, "old.log", "passed", "0")
        evidence = PassedRunEvidence(ignore_older_runs=True)
        self.assertIsNone(evidence.why_not_ready(self.image, with_way_out=True))
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


if __name__ == "__main__":
    unittest.main()
