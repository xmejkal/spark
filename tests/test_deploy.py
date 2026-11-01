"""P192 (#144): deploy.py puts the flash image that passed the simulation onto the board, and no other image."""

import contextlib
import io
import json
import os
import shlex
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit
from suite_runs import needs_littlefs  # noqa: E402
from micropython_fakes import fake_interpreter  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import board_envelope  # noqa: E402
import deploy  # noqa: E402
import deploy_service  # noqa: E402
import flash_image  # noqa: E402
import firmware_platform  # noqa: E402
from project_image import DeployError  # noqa: E402
import run_scenario  # noqa: E402
import sim_project  # noqa: E402
import image_evidence  # noqa: E402
import tools  # noqa: E402

FAKE_CLI = [sys.executable, str(ROOT / "tests" / "fake_wokwi_cli.py")]
READY_MATCHED = '[s] Expected text matched: "ready"\n'
SCENARIO = 'name: s\nversion: 1\nsteps:\n  - wait-serial: "LED on"\n'
PYTHON = "/opt/python3"
#: esptool, mpremote and littlefs as tools.find returns them once /spark:setup installed them for the Python at PYTHON.
FOUND = {"flasher": tools.Tool("esptool", "flasher", {"kind": "python", "module": "esptool", "silent_step": "hold_boot"},
                                [PYTHON]),
         "board-shell": tools.Tool("mpremote", "board-shell",
                                   {"kind": "python", "module": "mpremote", "silent_step": "press_reset"}, [PYTHON]),
         "littlefs": tools.Tool("littlefs", "littlefs", {"kind": "python", "module": "littlefs"}, [PYTHON])}  # P436: the image check asks for it
PORT = "/dev/cu.usbmodem1101"


def found(name, *args, **kwargs):
    """tools.find for the roles and tools deploy.py and the image check ask for."""
    if name not in FOUND:  # P436: as tools.find does for a tool nothing installed, so a test can meet a missing tool with no patch
        raise tools.ToolProblem("%s is not installed — install: /spark:setup add %s" % (name, name))
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
        self.micropython.write_bytes(fake_interpreter())
        self.image = sim / "flash-with-firmware.bin"

    def run_the_scenario(self, exit_code=0, scenario=None):
        """A scenario (default: s) runs with a fake wokwi-cli: it writes the image and the log, as a person's run does."""
        told = {"FAKE_WOKWI_SERIAL": "ready\nLED on\n", "FAKE_WOKWI_EXIT": str(exit_code), "FAKE_WOKWI_OUT": READY_MATCHED,
                "FAKE_WOKWI_ERR": "" if exit_code == 0 else "Error: stuck\n"}
        with mock.patch.dict(os.environ, told):
            run_scenario.ScenarioRun(self.project, scenario or self.scenario, micropython=self.micropython).run(FAKE_CLI)

    def plan(self, port=None, ignore_older_runs=False):
        """The DeployPlan of a DeployService over this project's MicroPython platform. tools.find must be patched."""
        evidence = image_evidence.PassedRunEvidence(ignore_older_runs)  # the default is the refusal
        return deploy_service.DeployService(
            self.project, firmware_platform.FirmwarePlatform.micropython(self.project), evidence).plan(port)

    def deploy(self, *argv, find=found, run=None):
        """(exit code, stdout, stderr, the commands run) of deploy.py in this project."""
        ran = []
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(tools, "find", side_effect=find), contextlib.redirect_stdout(out), \
                contextlib.redirect_stderr(err):
            code = deploy.main(["--project", str(self.project), *argv], run=run or (lambda argv, **kw: ran.append(argv)))
        return code, out.getvalue(), err.getvalue(), ran


@needs_littlefs
class TheDryRunTest(ProjectCase):
    def test_the_dry_run_prints_the_two_flash_lines_and_how_to_see_it_start(self):
        self.run_the_scenario()
        code, said, problems, ran = self.deploy("--port", PORT, "--dry-run")
        self.assertEqual((code, problems, ran), (deploy.EXIT_OK, "", []))
        self.assertEqual(said.splitlines(), [
            "  would run: /opt/python3 -m esptool --chip esp32s3 --port %s erase-flash" % PORT,
            "  would run: /opt/python3 -m esptool --chip esp32s3 --port %s --after watchdog-reset write-flash 0x0 %s" % (PORT, shlex.quote(str(self.image))),
            "  board: not looked at: run look.py",
            "  then, to see it start: /opt/python3 -m mpremote connect %s repl, press Ctrl-C, then Ctrl-D: "
            "the firmware prints `ready`. Then leave mpremote's console with Ctrl-X: an open console holds the port, "
            "and the next deploy cannot open it" % PORT])

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


@needs_littlefs
class TheNoSimulationDryRunTest(ProjectCase):
    """P337 B: --no-simulation plans an image of firmware/ that no run tested."""

    def setUp(self):
        super().setUp()
        patcher = mock.patch.object(flash_image, "interpreter_for",
                                    side_effect=lambda given, project=None, find_tool=None: flash_image.Interpreter(self.micropython, 0))
        patcher.start()
        self.addCleanup(patcher.stop)
        self.image.write_bytes(flash_image.image(self.micropython.read_bytes(), flash_image.files_under(self.project / "firmware")))

    def test_the_flag_plans_the_flash_lines_with_no_run_log(self):
        code, said, problems, ran = self.deploy("--port", PORT, "--dry-run", "--no-simulation")
        self.assertEqual((code, problems, ran), (deploy.EXIT_OK, "", []))
        self.assertIn("would run: /opt/python3 -m esptool --chip esp32s3 --port %s erase-flash" % PORT, said)
        self.assertNotIn("changed after this image was made", said)

    def test_without_the_flag_it_is_refused_as_today(self):
        code, _, problems, _ = self.deploy("--dry-run")
        self.assertEqual(code, deploy.EXIT_COULD_NOT_RUN)
        self.assertIn("no run in sim/runs/ tested flash-with-firmware.bin as it is now", problems)

    def test_the_flag_refuses_firmware_that_does_not_compile(self):
        (self.project / "firmware" / "main.py").write_text("print(\n")
        code, _, problems, ran = self.deploy("--dry-run", "--no-simulation")
        self.assertEqual((code, ran), (deploy.EXIT_COULD_NOT_RUN, []))
        self.assertIn("firmware/main.py, line", problems)

    def test_the_image_check_asks_for_littlefs_without_the_project_as_flash_image_does(self):
        # P442: with no finder given, the evidence asks tools.find as main did, so a project's tools file changes nothing here
        asked = []

        def find(name, *args, **kwargs):
            asked.append((name, args, kwargs))
            return found(name)
        code, _, problems, _ = self.deploy("--dry-run", "--no-simulation", find=find)
        self.assertEqual((code, problems), (deploy.EXIT_OK, ""))
        self.assertIn(("littlefs", (), {"project": None}), asked)

    def test_the_dry_run_json_names_the_look_step_with_the_flag(self):
        code, said, _, _ = self.deploy("--dry-run", "--no-simulation", "--json")
        envelope = json.loads(said)
        # a dry run reads no board, so no look states what tested the image (P345)
        self.assertEqual((code, envelope["data"]["simulation"]), (deploy.EXIT_OK, None))
        self.assertIn("--no-simulation", envelope["next"][0]["argv"])

    def test_both_flags_are_an_argument_error(self):
        err = io.StringIO()
        with self.assertRaises(SystemExit) as raised, contextlib.redirect_stderr(err):
            deploy.main(["--project", str(self.project), "--dry-run", "--no-simulation", "--ignore-older-runs"])
        self.assertEqual(raised.exception.code, 2)
        self.assertTrue(err.getvalue().startswith("usage: deploy.py "), err.getvalue())
        self.assertIn("deploy.py: error: argument --ignore-older-runs: not allowed with argument --no-simulation", err.getvalue())

    def test_the_error_text_shows_a_control_character_as_a_question_mark(self):
        err = io.StringIO()
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(err):
            deploy.main(["--project", str(self.project), "--bad\x1b[2J"])
        self.assertIn("deploy.py: error: unrecognized arguments: --bad?[2J\n", err.getvalue())
        self.assertNotIn("\x1b", err.getvalue())

    def test_a_bad_flag_with_json_is_an_envelope_and_no_usage(self):
        code, said, err, ran = self.deploy("--dry-run", "--no-simulation", "--ignore-older-runs", "--json")
        self.assertEqual((code, err, ran), (deploy.EXIT_COULD_NOT_RUN, "", []))
        envelope = json.loads(said)
        self.assertEqual((envelope["tool"], envelope["op"], envelope["status"], envelope["data"], envelope["problems"], envelope["next"]),
                         ("deploy", "deploy", "could-not-run", None, [], []))
        self.assertEqual([item["code"] for item in envelope["unchecked"]], ["bad_argument"])
        self.assertIn("not allowed with argument --no-simulation", envelope["unchecked"][0]["sentence"])


class OnlyAnImageThatPassedTest(ProjectCase):
    def test_no_image_yet_says_to_run_a_scenario(self):
        code, _, problems, ran = self.deploy("--dry-run")
        self.assertEqual((code, ran), (deploy.EXIT_COULD_NOT_RUN, []))
        self.assertIn("run a scenario first", problems)

    @needs_littlefs
    def test_an_image_whose_run_failed_is_refused(self):
        self.run_the_scenario(exit_code=1)
        code, _, problems, _ = self.deploy("--dry-run")
        self.assertEqual(code, deploy.EXIT_COULD_NOT_RUN)
        self.assertIn("s.log did not pass on this image", problems)

    @needs_littlefs
    def test_an_image_changed_after_its_run_passed_is_refused(self):
        self.run_the_scenario()
        self.image.write_bytes(self.image.read_bytes() + b"\x00")
        code, _, problems, _ = self.deploy("--dry-run")
        self.assertEqual(code, deploy.EXIT_COULD_NOT_RUN)
        self.assertIn("no run in sim/runs/ tested flash-with-firmware.bin as it is now", problems)

    @needs_littlefs
    def test_one_failed_scenario_on_the_same_image_refuses_it_though_another_passed(self):
        self.run_the_scenario()
        passed = self.project / "sim" / "runs" / "s.log"
        passed.with_name("other.log").write_text(
            passed.read_text().replace("verdict: passed", "verdict: failed (wokwi-cli exit 1): Error: stuck"))
        code, _, problems, _ = self.deploy("--dry-run")
        self.assertEqual(code, deploy.EXIT_COULD_NOT_RUN)
        self.assertIn("other.log did not pass on this image", problems)

    @needs_littlefs
    def test_a_log_from_an_older_spark_names_no_image_and_is_refused(self):
        self.run_the_scenario()
        log = self.project / "sim" / "runs" / "s.log"
        log.write_text("\n".join(line for line in log.read_text().splitlines()
                                 if not line.startswith("image sha256: ")) + "\n")
        code, _, problems, _ = self.deploy("--dry-run")
        self.assertEqual(code, deploy.EXIT_COULD_NOT_RUN)
        self.assertIn("names no image", problems)


@needs_littlefs
class ALogThatTestedAnotherImageTest(ProjectCase):
    """A scenario that last ran on another image never tested this one, so it refuses the flash by default (the PO,
    2026-10-12). --ignore-older-runs flashes anyway and names it in a note."""

    def run_two_scenarios(self):
        """Scenario s fails, the firmware changes, and only scenario t runs again and passes."""
        self.run_the_scenario(exit_code=1)
        (self.project / "firmware" / "main.py").write_text("print('ready')\nprint('changed')\n")
        other = self.project / "sim" / "scenarios" / "t.scenario.yaml"
        other.write_text(SCENARIO.replace("name: s", "name: t"))
        self.run_the_scenario(scenario=other)

    def test_a_scenario_that_failed_on_an_older_image_refuses_the_flash(self):
        self.run_two_scenarios()
        code, said, problems, ran = self.deploy("--dry-run")
        self.assertEqual((code, said, ran), (deploy.EXIT_COULD_NOT_RUN, "", []))
        self.assertIn("s.log tested another image, not this one: run that scenario again to test this one", problems)
        self.assertIn("pass --ignore-older-runs", problems)

    def test_ignore_older_runs_flashes_and_names_them_in_a_note(self):
        self.run_two_scenarios()
        code, said, problems, _ = self.deploy("--dry-run", "--ignore-older-runs")
        self.assertEqual((code, problems), (deploy.EXIT_OK, ""))
        self.assertIn("  note: s.log tested another image, not this one: run that scenario again to test this one",
                      said.splitlines())

    def test_ignore_older_runs_never_flashes_an_image_whose_own_run_failed(self):
        self.run_the_scenario(exit_code=1)
        code, _, problems, ran = self.deploy("--ignore-older-runs")
        self.assertEqual((code, ran), (deploy.EXIT_COULD_NOT_RUN, []))
        self.assertIn("s.log did not pass on this image", problems)

    def test_a_real_run_refuses_before_any_command(self):
        self.run_two_scenarios()
        code, _, problems, ran = self.deploy()
        self.assertEqual((code, ran), (deploy.EXIT_COULD_NOT_RUN, []))
        self.assertIn("pass --ignore-older-runs", problems)

    def test_plan_refuses_by_default(self):
        self.run_two_scenarios()
        with mock.patch.object(tools, "find", side_effect=found), self.assertRaises(DeployError) as said:
            self.plan()
        self.assertIn("--ignore-older-runs", str(said.exception))

    def test_plan_returns_a_deploy_plan_read_by_name(self):
        self.run_the_scenario()
        with mock.patch.object(tools, "find", side_effect=found):
            plan = self.plan(PORT)
        self.assertIsInstance(plan, deploy_service.DeployPlan)
        self.assertEqual((len(plan.commands), plan.mpremote, plan.notes), (2, [PYTHON, "-m", "mpremote"], []))
        self.assertEqual(plan.commands, plan.flasher.build_commands(self.image, PORT))
        self.assertIn("hold the board's BOOT button", plan.flasher.boot_hint)

    def test_the_log_refusal_comes_before_the_tools(self):
        self.run_two_scenarios()

        def missing(name, *args, **kwargs):
            raise tools.ToolProblem("flasher (esptool) is not installed")
        code, _, problems, _ = self.deploy("--dry-run", find=missing)
        self.assertEqual(code, deploy.EXIT_COULD_NOT_RUN)
        self.assertIn("tested another image", problems)
        self.assertNotIn("not installed", problems)

    def test_several_logs_go_in_one_sentence_and_a_log_from_an_older_spark_is_one_of_them(self):
        self.run_the_scenario()
        runs = self.project / "sim" / "runs"
        (runs / "a.log").write_text("# a.scenario.yaml, run 2026-10-01\nverdict: passed\n\nbody\n")
        (runs / "b.log").write_text("# b.scenario.yaml, run 2026-10-01\nverdict: failed\nimage sha256: 0\n\nbody\n")
        code, _, problems, _ = self.deploy("--dry-run")
        self.assertEqual(code, deploy.EXIT_COULD_NOT_RUN)
        self.assertIn("b.log tested another image, not this one, and a.log names no image (an older spark): run those "
                      "scenarios again", problems)
        code, said, _, _ = self.deploy("--dry-run", "--ignore-older-runs")
        self.assertEqual((code, said.count("note:")), (deploy.EXIT_OK, 1))


@needs_littlefs
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


class TheGuardedPrintTest(ProjectCase):
    """P423 (#556): every text print of deploy.py shows a character a terminal does not print as `?`; --json keeps it raw."""

    def test_shown_guards_each_line_and_keeps_the_newlines_on_the_stream_it_is_given(self):
        out = io.StringIO()
        deploy.shown("a\u202eb\nc\x1bd\te", out, flush=True)
        self.assertEqual(out.getvalue(), "a?b\nc?d?e\n")

    def test_shown_flushes_when_asked_to_and_only_then_and_a_service_line_always_does(self):
        class Recording(io.StringIO):
            flushed = 0

            def flush(self):
                self.flushed += 1

        stream = Recording()
        deploy.shown("a", stream)
        self.assertEqual(stream.flushed, 0)
        deploy.shown("b", stream, flush=True)
        self.assertEqual(stream.flushed, 1)
        deploy.show_line("c", stream)
        self.assertEqual((stream.flushed, stream.getvalue()), (2, "a\nb\nc\n"))

    @needs_littlefs
    def test_the_dry_run_on_stdout_shows_a_right_to_left_override_in_the_port_as_a_question_mark(self):
        self.run_the_scenario()
        code, said, problems, _ = self.deploy("--port", "/dev/cu.usb\u202emodem", "--dry-run")
        self.assertEqual((code, problems), (deploy.EXIT_OK, ""))
        self.assertIn("--port '/dev/cu.usb?modem' erase-flash", said)

    def test_a_refusal_on_stderr_shows_it_and_the_json_keeps_it_raw(self):
        bad = str(self.project.with_name("a\u202eb"))
        code, _, problems, _ = self.deploy("--project", bad, "--dry-run")
        self.assertEqual(code, deploy.EXIT_COULD_NOT_RUN)
        self.assertIn("no sim/wokwi.toml in %s/a?b: build" % self.project.parent, problems)
        _, said, _, _ = self.deploy("--project", bad, "--dry-run", "--json")
        self.assertIn("/a\u202eb: build", json.loads(said)["unchecked"][0]["sentence"])


class TheDeployEnvelopeYesRuleTest(unittest.TestCase):
    """P337 B: the NEXT_DEPLOY step names a deploy grant only where a grant may answer."""

    def step_why(self, evidence):
        reached = {"project": Path("p"), "evidence": evidence, "stage": "gate", "next_op": "deploy",
                   "token": "t", "port": "/dev/x", "refusal": "no yes"}
        return board_envelope.deploy_envelope(reached, 2)["next"][0]["why"]

    def test_no_simulation_drops_the_grant_clause_and_a_passed_run_keeps_it(self):
        self.assertNotIn("grant", self.step_why(image_evidence.NoSimulationEvidence("p")))
        self.assertNotIn("grant", self.step_why(image_evidence.PassedRunEvidence(True)))
        self.assertIn("or a deploy grant stands", self.step_why(image_evidence.PassedRunEvidence()))


if __name__ == "__main__":
    unittest.main()
