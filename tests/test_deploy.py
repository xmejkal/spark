"""P192 (#144): deploy.py puts the flash image that passed the simulation onto the board, and no other image."""

import contextlib
import io
import json
import os
import shlex
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  P172: this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import deploy  # noqa: E402
import run_scenario  # noqa: E402
import sim_project  # noqa: E402
import tools  # noqa: E402

FAKE_CLI = [sys.executable, str(ROOT / "tests" / "fake_wokwi_cli.py")]
READY_MATCHED = '[s] Expected text matched: "ready"\n'
SCENARIO = 'name: s\nversion: 1\nsteps:\n  - wait-serial: "LED on"\n'
PYTHON = "/opt/python3"
#: esptool and mpremote as tools.find returns them once /spark:setup installed them for the Python at PYTHON.
FOUND = {"flasher": tools.Tool("esptool", "flasher", {"kind": "python", "module": "esptool"}, [PYTHON]),
         "board-shell": tools.Tool("mpremote", "board-shell", {"kind": "python", "module": "mpremote"}, [PYTHON])}
PORT = "/dev/cu.usbmodem1101"


def found(name, *args, **kwargs):
    """tools.find for the two roles deploy.py asks for."""
    return FOUND[name]


class ProjectCase(unittest.TestCase):
    """A built project whose folder name has a space, with firmware, a scenario and the board in requirements.json."""

    def setUp(self):
        self.project = Path(tempfile.mkdtemp()) / "my bin"
        sim = self.project / "sim"
        (sim / "scenarios").mkdir(parents=True)
        (sim / "diagram.json").write_text("{}")
        (sim / "wokwi.toml").write_text(sim_project.wokwi_toml([]))  # as the build writes it with no --firmware
        (self.project / "firmware").mkdir()
        (self.project / "firmware" / "main.py").write_text("print('ready')\n")
        (self.project / "requirements.json").write_text(json.dumps({"board": "firebeetle2-esp32s3", "parts": []}))
        self.scenario = sim / "scenarios" / "s.scenario.yaml"
        self.scenario.write_text(SCENARIO)
        self.micropython = self.project / "micropython.bin"
        self.micropython.write_bytes(b"\xe9" + b"\x00" * 999)
        self.image = sim / "flash-with-firmware.bin"

    def run_the_scenario(self, exit_code=0, scenario=None):
        """A scenario (default: s) runs with a fake wokwi-cli: it writes the image and the log, as a person's run does."""
        told = {"FAKE_WOKWI_SERIAL": "ready\nLED on\n", "FAKE_WOKWI_EXIT": str(exit_code), "FAKE_WOKWI_OUT": READY_MATCHED,
                "FAKE_WOKWI_ERR": "" if exit_code == 0 else "Error: stuck\n"}
        with mock.patch.dict(os.environ, told):
            run_scenario.ScenarioRun(self.project, scenario or self.scenario, micropython=self.micropython).run(FAKE_CLI)

    def deploy(self, *argv, find=found, run=None):
        """(exit code, stdout, stderr, the commands run) of deploy.py in this project."""
        ran = []
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(tools, "find", side_effect=find), contextlib.redirect_stdout(out), \
                contextlib.redirect_stderr(err):
            code = deploy.main(["--project", str(self.project), *argv], run=run or (lambda argv, **kw: ran.append(argv)))
        return code, out.getvalue(), err.getvalue(), ran


class TheDryRunTest(ProjectCase):
    def test_the_dry_run_prints_the_two_flash_lines_and_how_to_see_it_start(self):
        self.run_the_scenario()
        code, said, problems, ran = self.deploy("--port", PORT, "--dry-run")
        self.assertEqual((code, problems, ran), (deploy.EXIT_OK, "", []))
        self.assertEqual(said.splitlines(), [
            "  would run: /opt/python3 -m esptool --chip esp32s3 --port %s erase_flash" % PORT,
            "  would run: /opt/python3 -m esptool --chip esp32s3 --port %s write_flash 0x0 %s" % (PORT, shlex.quote(str(self.image))),
            "  then, to see it start: /opt/python3 -m mpremote connect %s repl, press Ctrl-C, then Ctrl-D: "
            "the firmware prints `ready`" % PORT])

    def test_without_a_port_esptool_and_mpremote_find_the_board(self):
        self.run_the_scenario()
        code, said, _, _ = self.deploy("--dry-run")
        self.assertEqual(code, deploy.EXIT_OK)
        self.assertNotIn("--port", said)
        self.assertIn("/opt/python3 -m mpremote repl, press", said)


    def test_an_image_in_a_subfolder_of_sim_is_tested_by_the_logs_in_sim_runs(self):
        sim = self.project / "sim"
        (sim / "wokwi.toml").write_text(sim_project.wokwi_toml([], "images/flash.bin"))
        (sim / "images").mkdir()
        self.run_the_scenario()
        code, said, problems, _ = self.deploy("--dry-run")
        self.assertEqual((code, problems), (deploy.EXIT_OK, ""))
        self.assertIn(shlex.quote(str(sim / "images" / "flash.bin")), said)
        self.assertTrue((sim / "images" / "flash.bin").is_file())


class OnlyAnImageThatPassedTest(ProjectCase):
    def test_no_image_yet_says_to_run_a_scenario(self):
        code, _, problems, ran = self.deploy("--dry-run")
        self.assertEqual((code, ran), (deploy.EXIT_COULD_NOT_RUN, []))
        self.assertIn("run a scenario first", problems)

    def test_an_image_whose_run_failed_is_refused(self):
        self.run_the_scenario(exit_code=1)
        code, _, problems, _ = self.deploy("--dry-run")
        self.assertEqual(code, deploy.EXIT_COULD_NOT_RUN)
        self.assertIn("s.log did not pass on this image", problems)

    def test_an_image_changed_after_its_run_passed_is_refused(self):
        self.run_the_scenario()
        self.image.write_bytes(self.image.read_bytes() + b"\x00")
        code, _, problems, _ = self.deploy("--dry-run")
        self.assertEqual(code, deploy.EXIT_COULD_NOT_RUN)
        self.assertIn("no run in sim/runs/ tested flash-with-firmware.bin as it is now", problems)

    def test_one_failed_scenario_on_the_same_image_refuses_it_though_another_passed(self):
        self.run_the_scenario()
        passed = self.project / "sim" / "runs" / "s.log"
        passed.with_name("other.log").write_text(
            passed.read_text().replace("verdict: passed", "verdict: failed (wokwi-cli exit 1): Error: stuck"))
        code, _, problems, _ = self.deploy("--dry-run")
        self.assertEqual(code, deploy.EXIT_COULD_NOT_RUN)
        self.assertIn("other.log did not pass on this image", problems)

    def test_a_log_from_an_older_spark_names_no_image_and_is_refused(self):
        self.run_the_scenario()
        log = self.project / "sim" / "runs" / "s.log"
        log.write_text("\n".join(line for line in log.read_text().splitlines()
                                 if not line.startswith("image sha256: ")) + "\n")
        code, _, problems, _ = self.deploy("--dry-run")
        self.assertEqual(code, deploy.EXIT_COULD_NOT_RUN)
        self.assertIn("names no image", problems)


class ALogThatTestedAnotherImageTest(ProjectCase):
    """A scenario that last ran on another image is not a refusal, but it is not forgotten either."""

    def test_a_scenario_that_failed_on_an_older_image_is_named_in_a_note(self):
        self.run_the_scenario(exit_code=1)
        (self.project / "firmware" / "main.py").write_text("print('ready')\nprint('changed')\n")
        other = self.project / "sim" / "scenarios" / "t.scenario.yaml"
        other.write_text(SCENARIO.replace("name: s", "name: t"))
        self.run_the_scenario(scenario=other)
        code, said, problems, _ = self.deploy("--dry-run")
        self.assertEqual((code, problems), (deploy.EXIT_OK, ""))
        self.assertIn("  note: s.log tested another image, not this one: run that scenario again to test this one",
                      said.splitlines())

    def test_several_logs_go_in_one_note_and_a_log_from_an_older_spark_is_one_of_them(self):
        self.run_the_scenario()
        runs = self.project / "sim" / "runs"
        (runs / "a.log").write_text("# a.scenario.yaml, run 2026-10-01\nverdict: passed\n\nbody\n")
        (runs / "b.log").write_text("# b.scenario.yaml, run 2026-10-01\nverdict: failed\nimage sha256: 0\n\nbody\n")
        code, said, _, _ = self.deploy("--dry-run")
        self.assertEqual(code, deploy.EXIT_OK)
        self.assertIn("  note: a.log, b.log tested another image, not this one: run those scenarios again", said.splitlines()[0])
        self.assertEqual(said.count("note:"), 1)


class WhatDeployNeedsTest(ProjectCase):
    def test_a_missing_flasher_names_what_installs_it_and_runs_nothing(self):
        self.run_the_scenario()

        def missing(name, *args, **kwargs):
            raise tools.ToolProblem("flasher (esptool) is not installed — install: python3 -m pip install --user esptool==5.5.0")
        code, _, problems, ran = self.deploy("--dry-run", find=missing)
        self.assertEqual((code, ran), (deploy.EXIT_COULD_NOT_RUN, []))
        self.assertIn("pip install --user esptool==5.5.0", problems)

    def test_no_requirements_json_names_where_the_chip_comes_from(self):
        self.run_the_scenario()
        (self.project / "requirements.json").unlink()
        code, _, problems, _ = self.deploy("--dry-run")
        self.assertEqual(code, deploy.EXIT_COULD_NOT_RUN)
        self.assertIn("requirements.json", problems)

    def test_a_folder_named_like_a_log_is_skipped(self):
        self.run_the_scenario()
        (self.project / "sim" / "runs" / "x.log").mkdir()
        code, said, problems, _ = self.deploy("--dry-run")
        self.assertEqual((code, problems), (deploy.EXIT_OK, ""))
        self.assertNotIn("note:", said)

    def test_a_log_that_cannot_be_read_is_a_sentence_not_a_traceback(self):
        self.run_the_scenario()
        with mock.patch.object(run_scenario, "run_record", side_effect=PermissionError("denied")):
            code, _, problems, ran = self.deploy("--dry-run")
        self.assertEqual((code, ran), (deploy.EXIT_COULD_NOT_RUN, []))
        self.assertIn("cannot read ", problems)
        self.assertIn("s.log: denied", problems)

    def test_a_firmware_file_changed_after_the_image_is_named_but_the_image_still_goes(self):
        self.run_the_scenario()
        later = self.image.stat().st_mtime + 10
        os.utime(self.project / "firmware" / "main.py", (later, later))
        code, said, _, _ = self.deploy("--dry-run")
        self.assertEqual(code, deploy.EXIT_OK)
        self.assertIn("note: firmware/main.py changed after this image was made", said)


class TheFlashTest(ProjectCase):
    def test_a_flash_erases_then_writes_the_image_and_says_how_to_see_it_start(self):
        self.run_the_scenario()
        code, said, _, ran = self.deploy("--port", PORT)
        self.assertEqual(code, deploy.EXIT_OK)
        self.assertEqual([argv[-1] for argv in ran], ["erase_flash", str(self.image)])
        self.assertIn("then, to see it start", said)

    def test_a_failed_erase_writes_nothing_and_says_what_to_try(self):
        self.run_the_scenario()
        ran = []

        def fails(argv, **kw):
            ran.append(argv)
            raise subprocess.CalledProcessError(2, argv)
        code, _, problems, _ = self.deploy("--port", "/dev/nothing", run=fails)
        self.assertEqual((code, len(ran)), (deploy.EXIT_COULD_NOT_RUN, 1))
        self.assertIn("hold the board's BOOT button", problems)


if __name__ == "__main__":
    unittest.main()
