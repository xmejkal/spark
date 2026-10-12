"""P130: the harness that runs a built project's scenario in Wokwi. A fake wokwi-cli stands in, so no CI minute is spent."""

import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  P172: this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import run_scenario  # noqa: E402
import sim_project  # noqa: E402
from outcomes import COULD_NOT_RUN, EXIT_COULD_NOT_RUN, OK, PROBLEMS  # noqa: E402

#: wokwi-cli as the tests run it: tests/fake_wokwi_cli.py, which spends nothing.
FAKE_CLI = [sys.executable, str(Path(__file__).resolve().parent / "fake_wokwi_cli.py")]

SCENARIO = """name: the button lights the LED
version: 1
steps:
  - set-control: { part-id: tactilebutton, name: pressed, value: 1 }
  - wait-serial: "LED on"
"""


#: wokwi-cli 0.27.1's own line when the ready wait matched, copied from the real run of 2026-10-12.
READY_MATCHED = '[the button lights the LED] Expected text matched: "ready"\n'


class TheReadyWaitTest(unittest.TestCase):
    def test_the_wait_goes_before_the_first_step_at_its_indent(self):
        self.assertIn('steps:\n  - wait-serial: "ready"\n  - set-control:', run_scenario.with_ready_wait(SCENARIO))
        flush = SCENARIO.replace("\n  - ", "\n- ")
        self.assertIn('steps:\n- wait-serial: "ready"\n- set-control:', run_scenario.with_ready_wait(flush))

    def test_a_scenario_that_already_waits_for_ready_text_before_its_first_input_is_left_as_it_is(self):
        # A second wait would never match: a wait sees only text that arrives after its step begins (WR1).
        for first in ('- wait-serial: "ready"', '- wait-serial: "smartbin ready"', '- wait-serial: "ready"  # boot done',
                      "- { wait-serial: ready }", '- delay: 500ms\n  - wait-serial: "ready"'):
            scenario = SCENARIO.replace("steps:\n", "steps:\n  %s\n" % first)
            with self.subTest(first=first):
                self.assertEqual(run_scenario.with_ready_wait(scenario), scenario)

    def test_a_ready_wait_after_the_first_input_still_gets_one_before(self):
        scenario = SCENARIO + '  - wait-serial: "ready"\n'
        self.assertIn('steps:\n  - wait-serial: "ready"\n  - set-control:', run_scenario.with_ready_wait(scenario))

    def test_a_scenario_with_no_steps_is_refused(self):
        for text in ("name: x\nversion: 1\n", "name: x\nsteps:\n", "steps:\nversion: 1\n"):
            with self.subTest(text=text), self.assertRaisesRegex(ValueError, "steps"):
                run_scenario.with_ready_wait(text)


class TheVerdictTest(unittest.TestCase):
    def test_the_reason_is_wokwi_cli_s_own_error_not_a_firmware_line_that_says_error(self):
        status, said = run_scenario.verdict(1, "ready\nError: I2C not found\n", "ready\nError: I2C not found\n" + READY_MATCHED,
                                            "Error: GPIO 4 expected to be 1 but was 0\n", 60000)
        self.assertEqual((status, said), (PROBLEMS, "failed (wokwi-cli exit 1): Error: GPIO 4 expected to be 1 but was 0"))

    def test_ready_with_a_prefix_counts_when_wokwi_cli_says_the_wait_matched(self):
        # RF1: the wait matches text containing ready, so "I ready" passes it, and a later failure must be named as such.
        status, said = run_scenario.verdict(1, "I ready\n", "I ready\n" + READY_MATCHED, "Error: expect-pin failed\n", 60000)
        self.assertEqual((status, said), (PROBLEMS, "failed (wokwi-cli exit 1): Error: expect-pin failed"))

    def test_the_ready_line_is_not_read_from_the_serial_file_which_joins_lines(self):
        # wokwi-cli 0.27.1 wrote "readyLED onLED off" into its serial log file; its stdout said the wait matched.
        status, _ = run_scenario.verdict(42, "readyLED on", "ready\n", "", 60000)
        self.assertEqual(status, PROBLEMS)

    def test_a_lost_simulator_could_not_run(self):
        status, said = run_scenario.verdict(1, "ready\n", "ready\n" + READY_MATCHED, "API Error: connection closed\n", 60000)
        self.assertEqual((status, said), (COULD_NOT_RUN, "wokwi-cli lost the simulator (exit 1): API Error: connection closed"))

    def test_a_board_silent_until_the_timeout_could_not_run_and_asks_about_the_serial_wires(self):
        status, said = run_scenario.verdict(42, "", "", "Timeout\n", 60000)
        self.assertEqual(status, COULD_NOT_RUN)
        self.assertIn("$serialMonitor", said)


class TheRunTest(unittest.TestCase):
    def setUp(self):
        self.project = Path(tempfile.mkdtemp())
        sim = self.project / "sim"
        (sim / "scenarios").mkdir(parents=True)
        (sim / "diagram.json").write_text("{}")
        (sim / "wokwi.toml").write_text(sim_project.wokwi_toml([]))  # as the build writes it with no --firmware
        (self.project / "firmware").mkdir()
        (self.project / "firmware" / "main.py").write_text("print('ready')\n")
        self.scenario = sim / "scenarios" / "lights.v2.scenario.yaml"
        self.scenario.write_text(SCENARIO)
        self.micropython = self.project / "micropython.bin"
        self.micropython.write_bytes(b"\xe9" + b"\x00" * 999)
        self.seen = self.project / "seen.json"
        self.log = sim / "runs" / "lights.v2.log"

    def run_with(self, serial="ready\n", exit_code=0, out=READY_MATCHED, err=""):
        told = {"FAKE_WOKWI_SERIAL": serial, "FAKE_WOKWI_EXIT": str(exit_code), "FAKE_WOKWI_OUT": out,
                "FAKE_WOKWI_ERR": err, "FAKE_WOKWI_SEEN": str(self.seen)}
        with mock.patch.dict(os.environ, told):
            return run_scenario.run(self.project, self.scenario, FAKE_CLI, micropython=self.micropython)

    def test_a_pass_is_logged_with_its_date_the_scenario_as_run_and_what_wokwi_cli_printed(self):
        status, said, log = self.run_with("boot\nready\nLED on\n")
        self.assertEqual((status, said, log), (OK, "passed", self.log))
        text = log.read_text()
        self.assertRegex(text.splitlines()[0], r"run \d{4}-\d\d-\d\dT")
        for shown in ("verdict: passed", '  - wait-serial: "ready"', "LED on", "Wokwi CLI v0.0.0 (fake)"):
            self.assertIn(shown, text)

    def test_the_cli_gets_the_scenario_with_the_wait_the_timeout_and_an_image_of_the_firmware_as_it_is_now(self):
        self.run_with()
        seen = json.loads(self.seen.read_text())
        self.assertEqual(seen["scenario"], run_scenario.with_ready_wait(SCENARIO))
        self.assertEqual(seen["args"][0], str(self.project / "sim"))
        self.assertIn("--timeout 60000", " ".join(seen["args"]))
        self.assertIn(b"print('ready')", (self.project / "sim" / "flash-with-firmware.bin").read_bytes())

    def test_a_build_with_no_image_named_gets_one_named_as_firmware_would(self):
        # wokwi-cli refuses a wokwi.toml with no firmware line: "Firmware path must be a string" (0.27.1, 2026-10-12).
        self.run_with()
        self.assertEqual((self.project / "sim" / "wokwi.toml").read_text(), sim_project.wokwi_toml([], "flash-with-firmware.bin"))

    def test_the_image_is_the_one_wokwi_toml_names(self):
        (self.project / "sim" / "wokwi.toml").write_text(sim_project.wokwi_toml([], "mine.bin"))
        self.run_with()
        self.assertTrue((self.project / "sim" / "mine.bin").is_file())

    def test_an_image_named_outside_sim_is_left_alone_and_nothing_runs(self):
        # WR4: a person's own --firmware can name any path; the run must not overwrite it with MicroPython.
        theirs = self.project / "build" / "app.bin"
        theirs.parent.mkdir()
        theirs.write_bytes(b"their own firmware")
        (self.project / "sim" / "wokwi.toml").write_text(sim_project.wokwi_toml([], "../build/app.bin"))
        status, said, _ = self.run_with()
        self.assertEqual((status, theirs.read_bytes()), (COULD_NOT_RUN, b"their own firmware"))
        self.assertIn("outside sim/", said)
        self.assertFalse(self.seen.exists())

    def test_a_firmware_that_never_prints_ready_is_named_with_the_contract(self):
        status, said, _ = self.run_with("boot\nTraceback (most recent call last):\n", exit_code=42, out="")
        self.assertEqual(status, PROBLEMS)
        self.assertIn("never printed 'ready'", said)

    def test_a_timeout_after_ready_says_it_timed_out(self):
        status, said, _ = self.run_with(exit_code=42)  # wokwi-cli's --timeout-exit-code default, from its --help (0.27.1)
        self.assertEqual((status, said), (PROBLEMS, "timed out after 60000 ms: a step waited for something that never came"))

    def test_a_board_that_never_started_could_not_run_with_wokwi_cli_s_error_line(self):
        status, said, _ = self.run_with("", exit_code=1, out="",
                                        err="Error: Error in wokwi.toml: Firmware path must be a string\n    at parseConfig")
        self.assertEqual((status, said), (COULD_NOT_RUN, "wokwi-cli stopped before the board started (exit 1): "
                                                         "Error: Error in wokwi.toml: Firmware path must be a string"))

    def test_a_failed_step_is_logged_with_wokwi_cli_s_error(self):
        status, said, log = self.run_with(exit_code=1, err="Error: GPIO 4 expected to be 1 but was 0")
        self.assertEqual((status, said), (PROBLEMS, "failed (wokwi-cli exit 1): Error: GPIO 4 expected to be 1 but was 0"))
        self.assertIn("verdict: failed", log.read_text())

    def test_serial_bytes_that_are_not_utf_8_do_not_crash_the_run(self):
        with mock.patch.dict(os.environ, {"FAKE_WOKWI_NOISE": "1"}):
            status, _, log = self.run_with()
        self.assertEqual(status, OK)
        self.assertIn("\ufffd", log.read_text())

    def test_without_the_simulation_project_nothing_runs_the_build_is_named_and_an_old_log_is_gone(self):
        self.log.parent.mkdir()
        self.log.write_text("verdict: passed\n")
        (self.project / "sim" / "diagram.json").unlink()
        status, said, log = self.run_with()
        self.assertEqual((status, log), (COULD_NOT_RUN, None))
        self.assertIn("check_spine.py requirements.json --keep .", said)
        self.assertFalse(self.seen.exists())
        self.assertFalse(self.log.exists())


class TheCommandTest(unittest.TestCase):
    def test_without_a_token_nothing_runs_and_it_says_where_to_get_one(self):
        without = {name: value for name, value in os.environ.items() if name != "WOKWI_CLI_TOKEN"}
        with mock.patch.dict(os.environ, without, clear=True), redirect_stderr(io.StringIO()) as err, \
                mock.patch.object(run_scenario, "run") as runs:
            code = run_scenario.main(["sim/scenarios/lights.scenario.yaml"])
        self.assertEqual(code, EXIT_COULD_NOT_RUN)
        self.assertIn("https://wokwi.com/dashboard/ci", err.getvalue())
        runs.assert_not_called()


if __name__ == "__main__":
    unittest.main()
