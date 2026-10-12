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
from outcomes import COULD_NOT_RUN, EXIT_COULD_NOT_RUN, OK, PROBLEMS  # noqa: E402

#: wokwi-cli as the tests run it: tests/fake_wokwi_cli.py, which spends nothing.
FAKE_CLI = [sys.executable, str(Path(__file__).resolve().parent / "fake_wokwi_cli.py")]

SCENARIO = """name: the button lights the LED
version: 1
steps:
  - set-control: { part-id: tactilebutton, name: pressed, value: 1 }
  - wait-serial: "LED on"
"""


class TheReadyWaitTest(unittest.TestCase):
    def test_the_wait_goes_before_the_first_step_at_its_indent(self):
        self.assertIn('steps:\n  - wait-serial: "ready"\n  - set-control:', run_scenario.with_ready_wait(SCENARIO))

    def test_a_scenario_that_already_waits_for_ready_is_left_as_it_is(self):
        once = run_scenario.with_ready_wait(SCENARIO)
        self.assertEqual(run_scenario.with_ready_wait(once), once)

    def test_a_scenario_with_no_steps_is_refused(self):
        for text in ("name: x\nversion: 1\n", "name: x\nsteps:\n"):
            with self.subTest(text=text), self.assertRaisesRegex(ValueError, "steps"):
                run_scenario.with_ready_wait(text)


class TheRunTest(unittest.TestCase):
    def setUp(self):
        self.project = Path(tempfile.mkdtemp())
        sim = self.project / "sim"
        (sim / "scenarios").mkdir(parents=True)
        (sim / "diagram.json").write_text("{}")
        (sim / "wokwi.toml").write_text('[wokwi]\nversion = 1\n# firmware = "flash-with-firmware.bin"\n')
        (self.project / "firmware").mkdir()
        (self.project / "firmware" / "main.py").write_text("print('ready')\n")
        self.scenario = sim / "scenarios" / "lights.scenario.yaml"
        self.scenario.write_text(SCENARIO)
        self.micropython = self.project / "micropython.bin"
        self.micropython.write_bytes(b"\xe9" + b"\x00" * 999)
        self.seen = self.project / "seen.json"

    def run_with(self, serial="ready\n", exit_code=0, said=""):
        told = {"FAKE_WOKWI_SERIAL": serial, "FAKE_WOKWI_EXIT": str(exit_code), "FAKE_WOKWI_SAID": said,
                "FAKE_WOKWI_SEEN": str(self.seen)}
        with mock.patch.dict(os.environ, told):
            return run_scenario.run(self.project, self.scenario, FAKE_CLI, micropython=self.micropython)

    def test_a_pass_is_logged_with_its_date_the_scenario_as_run_and_the_serial(self):
        status, said, log = self.run_with("boot\nready\nLED on\n")
        self.assertEqual((status, said, log), (OK, "passed", self.project / "sim" / "runs" / "lights.log"))
        text = log.read_text()
        self.assertRegex(text.splitlines()[0], r"run \d{4}-\d\d-\d\dT")
        for shown in ("verdict: passed", '  - wait-serial: "ready"', "LED on", "Wokwi CLI v0.0.0 (fake)"):
            self.assertIn(shown, text)

    def test_the_cli_gets_the_scenario_with_the_wait_and_an_image_of_the_firmware_as_it_is_now(self):
        self.run_with()
        seen = json.loads(self.seen.read_text())
        self.assertEqual(seen["scenario"], run_scenario.with_ready_wait(SCENARIO))
        image = Path(seen["args"][seen["args"].index("--elf") + 1])
        self.assertEqual(image, self.project / "sim" / "flash-with-firmware.bin")
        self.assertIn(b"print('ready')", image.read_bytes())

    def test_the_image_is_the_one_wokwi_toml_names(self):
        (self.project / "sim" / "wokwi.toml").write_text('[wokwi]\nversion = 1\nfirmware = "mine.bin"\nelf = "mine.bin"\n')
        self.run_with()
        self.assertTrue((self.project / "sim" / "mine.bin").is_file())

    def test_a_firmware_that_never_prints_ready_is_named_with_the_contract(self):
        status, said, _ = self.run_with("boot\nTraceback (most recent call last):\n", exit_code=42)
        self.assertEqual(status, PROBLEMS)
        self.assertIn("never printed 'ready'", said)

    def test_a_timeout_after_ready_says_it_timed_out(self):
        status, said, _ = self.run_with("ready\n", exit_code=run_scenario.TIMEOUT_EXIT)
        self.assertEqual(status, PROBLEMS)
        self.assertIn("timed out after 60000 ms", said)

    def test_a_failed_step_is_a_problem_in_wokwi_cli_s_last_words(self):
        status, said, log = self.run_with("ready\n", exit_code=1, said="expect-pin ledred5mm:A: expected 1, got 0")
        self.assertEqual((status, said), (PROBLEMS, "failed (wokwi-cli exit 1): expect-pin ledred5mm:A: expected 1, got 0"))
        self.assertIn("verdict: failed", log.read_text())

    def test_without_the_simulation_project_nothing_runs_and_the_build_is_named(self):
        (self.project / "sim" / "diagram.json").unlink()
        status, said, log = self.run_with()
        self.assertEqual((status, log), (COULD_NOT_RUN, None))
        self.assertIn("check_spine.py requirements.json --keep .", said)
        self.assertFalse(self.seen.exists())


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
