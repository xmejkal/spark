"""P130: the harness that runs a built project's scenario in Wokwi. A fake wokwi-cli stands in, so no CI minute is spent."""

import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import run_scenario  # noqa: E402
import sim_project  # noqa: E402
import flash_image  # noqa: E402
import tools  # noqa: E402
from spark.core.outcomes import COULD_NOT_RUN, EXIT_COULD_NOT_RUN, EXIT_OK, EXIT_PROBLEMS, OK, PROBLEMS  # noqa: E402

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


class TheStepCountsTest(unittest.TestCase):
    """P345: the counts of a scenario's steps by kind, read from the text as run and from a log's header only."""

    @staticmethod
    def steps(*items):
        return "name: x\nversion: 1\nsteps:\n" + "".join("  %s\n" % item for item in items)

    def counted(self, *items):
        return run_scenario.ScenarioSteps.from_text(self.steps(*items))

    def test_each_kind_is_counted_and_two_of_one_kind_are_two(self):
        steps = self.counted('- wait-serial: "ready"', "- set-control: { part-id: b, name: pressed, value: 1 }",
                             '- wait-serial: "on"', "- expect-pin: { part-id: led, pin: A, value: 1 }",
                             "- set-control: { part-id: b, name: pressed, value: 0 }")
        self.assertEqual(steps.counts, {"wait-serial": 2, "set-control": 2, "expect-pin": 1})
        self.assertEqual((steps.state, steps.why), ("recorded", None))
        self.assertEqual(steps.line(), "step counts: expect-pin 1, set-control 2, wait-serial 2")

    def test_a_kind_this_does_not_name_is_counted_and_a_log_with_only_a_delay_is_recorded(self):
        steps = self.counted("- delay: 500ms", '- wait-serial: "ready"')
        self.assertEqual((steps.count("delay"), steps.state), (1, "recorded"))
        self.assertEqual(steps.line(), "step counts: delay 1, expect-pin 0, set-control 0, wait-serial 1")

    def test_the_flow_form_and_a_quoted_key_are_counted(self):
        for item in ("- { set-control: { part-id: b, name: pressed, value: 1 } }", "- {set-control: {part-id: b}}",
                     '- "set-control":  {part-id: b}', "- 'set-control' : {part-id: b}"):
            with self.subTest(item=item):
                self.assertEqual(self.counted(item).counts, {"set-control": 1})

    def test_a_kind_in_a_comment_or_in_a_value_is_not_counted(self):
        steps = self.counted("# - set-control: { part-id: b }", '- wait-serial: "set-control: x"  # - expect-pin: y',
                             "- wait-serial: 'expect-pin: z'")
        self.assertEqual(steps.counts, {"wait-serial": 2})
        self.assertEqual(steps.count("set-control"), 0)

    def test_a_nested_list_item_is_no_step(self):
        scenario = self.steps("- set-control:", "    part-id: b", "    values:", "      - 1", "      - 2", "- wait-serial: x")
        steps = run_scenario.ScenarioSteps.from_text(scenario)
        self.assertEqual((steps.counts, steps.state), ({"set-control": 1, "wait-serial": 1}, "recorded"))

    def test_a_step_name_is_its_label_and_the_next_key_is_its_kind(self):
        # wokwi-cli lets a step carry `name:`, which it prints (TestScenario.ts, validStepKeys = ['name']).
        block = self.steps("- name: press the button", "  set-control:", "    part-id: b", '- wait-serial: "on"')
        self.assertEqual(run_scenario.ScenarioSteps.from_text(block).counts, {"set-control": 1, "wait-serial": 1})
        for item in ("- { name: press, set-control: { part-id: b } }", "- {name: press, expect-pin: {part-id: led}}"):
            with self.subTest(item=item):
                self.assertEqual(self.counted(item).count("name"), 0)
                self.assertEqual(self.counted(item).state, "recorded")

    def test_a_step_with_only_a_name_is_not_checked(self):
        steps = self.counted("- name: nothing else")
        self.assertEqual((steps.state, steps.why), ("not-checked", "a step of the scenario has no kind"))

    def test_the_steps_end_at_a_key_of_the_scenario_at_their_own_indent(self):
        scenario = "name: x\nsteps:\n  - wait-serial: a\n  - set-control: {part-id: b}\nafter: 1\n  - expect-pin: c\n"
        self.assertEqual(run_scenario.ScenarioSteps.from_text(scenario).counts, {"wait-serial": 1, "set-control": 1})

    def test_an_item_with_no_key_makes_the_counts_not_checked(self):
        for item in ("- just-a-word", "- [a, b]", '- "two words": x', "- : x", "-"):
            with self.subTest(item=item):
                steps = self.counted('- wait-serial: "ready"', item)
                self.assertEqual((steps.state, steps.why, steps.counts), ("not-checked", "a step of the scenario has no kind", {}))
                self.assertEqual(steps.line(), "step counts: not read")

    def test_a_text_with_no_steps_is_none_recorded(self):
        for text in ("", "name: x\n", "steps:\n"):
            with self.subTest(text=text):
                steps = run_scenario.ScenarioSteps.from_text(text)
                self.assertEqual((steps.state, steps.why, steps.line()), ("none-recorded", None, "step counts: not read"))

    def test_the_line_round_trips_through_a_log_header(self):
        log = Path(tempfile.mkdtemp()) / "a.log"
        for steps, state in ((self.counted("- delay: 1s", '- wait-serial: "ready"'), "recorded"),
                             (self.counted("- just-a-word"), "not-checked"), (self.counted(""), "not-checked")):
            log.write_text("# a, run 2026-10-24T10:00:00+02:00, timeout 1 ms\nverdict: passed\n%s\n\nbody\n" % steps.line())
            with self.subTest(line=steps.line(), written=steps.state):
                read = run_scenario.ScenarioSteps.from_log(log)
                self.assertEqual((read.line(), read.state), (steps.line(), state))  # the log keeps no difference between the two non-recorded states

    def test_a_log_with_no_counts_line_is_none_recorded(self):
        log = Path(tempfile.mkdtemp()) / "a.log"
        log.write_text("# a, run 2026-10-24T10:00:00, timeout 1 ms\nverdict: passed\n\nbody\n")
        steps = run_scenario.ScenarioSteps.from_log(log)
        self.assertEqual((steps.state, steps.why, steps.counts), ("none-recorded", None, {}))

    def test_a_log_that_says_not_read_is_not_checked_with_its_reason(self):
        log = Path(tempfile.mkdtemp()) / "a.log"
        log.write_text("# a, run 2026-10-24T10:00:00, timeout 1 ms\nverdict: passed\nstep counts: not read\n\nbody\n")
        steps = run_scenario.ScenarioSteps.from_log(log)
        self.assertEqual((steps.state, steps.why), ("not-checked", "the log says its steps were not counted"))

    def test_a_malformed_counts_line_or_no_file_is_not_checked_with_its_reason(self):
        log = Path(tempfile.mkdtemp()) / "a.log"
        header = "# a, run 2026-10-24T10:00:00, timeout 1 ms\nverdict: passed\n"
        for text in (header + "step counts: \n\n", header + "step counts: wait-serial\n\n",
                     header + "step counts: wait-serial x\n\n", header + "step counts: wait-serial 1; delay 2\n\n",
                     header + "step counts: set-control 1, set-control 2\n\n"):
            log.write_text(text)
            with self.subTest(text=text):
                steps = run_scenario.ScenarioSteps.from_log(log)
                self.assertEqual((steps.state, steps.why), ("not-checked", "the log's step counts line is malformed"))
        steps = run_scenario.ScenarioSteps.from_log(log.with_name("none.log"))
        self.assertEqual((steps.state, steps.why), ("not-checked", "the log cannot be read"))

    def test_merge_adds_the_counts_of_the_counted_steps(self):
        merged = run_scenario.ScenarioSteps.merge([
            run_scenario.ScenarioSteps({"set-control": 1, "wait-serial": 2}),
            run_scenario.ScenarioSteps({}, "not-checked", "why"),
            run_scenario.ScenarioSteps({"set-control": 2, "expect-pin": 1}),
            run_scenario.ScenarioSteps({}, "none-recorded")])
        self.assertEqual((merged.state, merged.counts), ("recorded", {"set-control": 3, "wait-serial": 2, "expect-pin": 1}))

    def test_merge_of_no_counted_steps_is_none_recorded(self):
        for each in ([], [run_scenario.ScenarioSteps({}, "not-checked", "why"), run_scenario.ScenarioSteps({}, "none-recorded")]):
            merged = run_scenario.ScenarioSteps.merge(each)
            with self.subTest(each=len(each)):
                self.assertEqual((merged.state, merged.why, merged.counts), ("none-recorded", None, {}))

    def test_a_counts_line_after_the_header_is_not_read(self):
        log = Path(tempfile.mkdtemp()) / "a.log"
        log.write_text("# a, run 2026-10-24T10:00:00, timeout 1 ms\nverdict: passed\n\nstep counts: set-control 3\n")
        self.assertEqual(run_scenario.ScenarioSteps.from_log(log).state, "none-recorded")


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


#: The tools list's simulator, pointed at the fake: the same entry words as data/tools.json's wokwi-cli.
FAKE_SIMULATOR = tools.Tool("wokwi-cli", "simulator", {
    "account_env": "WOKWI_CLI_TOKEN",
    "needs_account": "a Wokwi token in WOKWI_CLI_TOKEN — create one at wokwi.com/dashboard/ci"}, FAKE_CLI)


class ProjectCase(unittest.TestCase):
    """A built project with firmware and a scenario, and wokwi-cli faked: the set-up every run test shares."""

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
            return run_scenario.ScenarioRun(self.project, self.scenario, micropython=self.micropython).run(FAKE_CLI)

    def command(self, *argv, token="t", tool=FAKE_SIMULATOR, exit_code=0, **fake):
        real_find = tools.find

        def find(name, *args, **kwargs):
            if name != "simulator":
                return real_find(name, *args, **kwargs)
            if isinstance(tool, Exception):
                raise tool
            return tool

        told = {"FAKE_WOKWI_SERIAL": "ready\n", "FAKE_WOKWI_OUT": READY_MATCHED, "FAKE_WOKWI_EXIT": str(exit_code),
                "FAKE_WOKWI_SEEN": str(self.seen), **fake}
        env = {name: value for name, value in os.environ.items() if name != "WOKWI_CLI_TOKEN"}
        env.update(told, **({"WOKWI_CLI_TOKEN": token} if token else {}))
        argv = list(argv) or [str(self.scenario.relative_to(self.project)), "--project", str(self.project),
                              "--micropython", str(self.micropython)]
        with mock.patch.dict(os.environ, env, clear=True), mock.patch.object(tools, "find", side_effect=find), \
                redirect_stdout(io.StringIO()) as out, redirect_stderr(io.StringIO()) as err:
            code = run_scenario.main(argv)
        return code, out.getvalue() + err.getvalue()


class TheRunTest(ProjectCase):
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

    def test_a_project_named_relative_to_here_hands_the_cli_an_absolute_scenario(self):
        # P236: wokwi-cli reads --scenario from inside sim/, so `sim/scenarios/x` became `sim/sim/scenarios/x`.
        told = {"FAKE_WOKWI_SERIAL": "ready\n", "FAKE_WOKWI_EXIT": "0", "FAKE_WOKWI_OUT": READY_MATCHED,
                "FAKE_WOKWI_ERR": "", "FAKE_WOKWI_SEEN": str(self.seen)}
        here = os.getcwd()
        try:
            os.chdir(self.project)
            with mock.patch.dict(os.environ, told):
                run_scenario.ScenarioRun(".", self.scenario.relative_to(self.project), micropython=self.micropython).run(FAKE_CLI)
        finally:
            os.chdir(here)
        args = json.loads(self.seen.read_text())["args"]
        self.assertTrue(Path(args[args.index("--scenario") + 1]).is_absolute())

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
        self.assertIn("/spark:build --keep .", said)
        self.assertFalse(self.seen.exists())
        self.assertFalse(self.log.exists())


class TheLogNamesTheImageTest(ProjectCase):
    """P192: each log names the image its run tested by its sha256, so deploy.py flashes only an image that passed."""

    def test_a_passed_run_names_the_image_it_tested(self):
        _, _, log = self.run_with("ready\n")
        image = self.project / "sim" / "flash-with-firmware.bin"
        self.assertEqual(run_scenario.run_record(log), ("passed", hashlib.sha256(image.read_bytes()).hexdigest()))

    def test_only_the_header_is_read_not_what_the_board_printed(self):
        _, _, log = self.run_with("ready\n", exit_code=1, out=READY_MATCHED + "verdict: passed\nimage sha256: 00\n",
                                  err="Error: stuck\n")
        verdict, sha256 = run_scenario.run_record(log)
        self.assertEqual(verdict, "failed (wokwi-cli exit 1): Error: stuck")
        self.assertRegex(sha256, "^[0-9a-f]{64}$")

    def test_with_no_build_given_the_image_starts_with_the_build_the_board_names(self):
        (self.project / "requirements.json").write_text(json.dumps({"board": "xiao-esp32-c6"}))
        c6 = self.project / "c6.bin"
        c6.write_bytes(b"\xe9C6" + b"\x00" * 997)
        real_find = tools.find
        found = tools.Tool("micropython-xiao-esp32c6", None, {}, [str(c6)])
        told = {"FAKE_WOKWI_SERIAL": "ready\n", "FAKE_WOKWI_EXIT": "0", "FAKE_WOKWI_OUT": READY_MATCHED,
                "FAKE_WOKWI_ERR": "", "FAKE_WOKWI_SEEN": str(self.seen)}
        with mock.patch.dict(os.environ, told), mock.patch.object(
                tools, "find", side_effect=lambda name, *rest, **kw: found if name == "micropython-xiao-esp32c6" else real_find(name, *rest, **kw)):
            run_scenario.ScenarioRun(self.project, self.scenario).run(FAKE_CLI)
        self.assertEqual((self.project / "sim" / "flash-with-firmware.bin").read_bytes()[:3], b"\xe9C6")

    def test_a_log_from_an_older_spark_names_no_image(self):
        self.log.parent.mkdir(parents=True)
        self.log.write_text("# lights.v2.scenario.yaml, run 2026-10-11T10:00:00, timeout 60000 ms\nverdict: passed\n\n"
                            "--- the scenario as run ---\n")
        self.assertEqual(run_scenario.run_record(self.log), ("passed", None))


class TheLogCountsTheStepsTest(ProjectCase):
    """P345: a log's header counts the steps that ran, and the time carries its zone."""

    def test_the_header_counts_the_steps_as_run_after_the_verdict(self):
        _, _, log = self.run_with("ready\nLED on\n")
        lines = log.read_text().split("\n\n", 1)[0].splitlines()
        self.assertEqual(lines[1:3], ["verdict: passed", "step counts: expect-pin 0, set-control 1, wait-serial 2"])

    def test_the_log_reads_back_as_the_counts_it_wrote(self):
        _, _, log = self.run_with("ready\n")
        steps = run_scenario.ScenarioSteps.from_log(log)
        self.assertEqual((steps.counts, steps.state), ({"expect-pin": 0, "set-control": 1, "wait-serial": 2}, "recorded"))

    def test_a_limits_note_that_cannot_be_read_leaves_the_verdict_written(self):
        note = self.project / "sim" / "WHAT-THIS-CANNOT-SHOW.md"
        note.write_text("- a limit\n")
        read = Path.read_text

        def unreadable(self, *args, **kwargs):
            if self.name == note.name:
                raise PermissionError("denied")
            return read(self, *args, **kwargs)

        with mock.patch.object(Path, "read_text", unreadable):
            _, _, log = self.run_with("ready\n")
        self.assertEqual(run_scenario.run_record(log)[0], "passed")
        self.assertNotIn("--- what this simulation cannot show ---", log.read_text())

    def test_the_time_has_its_zone(self):
        _, _, log = self.run_with("ready\n")
        self.assertRegex(log.read_text().splitlines()[0], r", run \d{4}-\d\d-\d\dT\d\d:\d\d:\d\d[+-]\d\d:\d\d, timeout 60000 ms$")

    def test_what_the_board_printed_cannot_set_the_counts(self):
        _, _, log = self.run_with("ready\n", out=READY_MATCHED + "step counts: set-control 9\n")
        self.assertEqual(run_scenario.ScenarioSteps.from_log(log).count("set-control"), 1)

    def test_the_limits_note_goes_after_the_header_and_leaves_the_records_as_they_read(self):
        (self.project / "sim" / "WHAT-THIS-CANNOT-SHOW.md").write_text("# Limits\n\nthe XIAO has no button\n\nsecond\n")
        _, _, log = self.run_with("ready\n")
        text = log.read_text()
        self.assertIn("\n\n--- what this simulation cannot show ---\n# Limits\n\nthe XIAO has no button\n\nsecond\n"
                      "\n--- the scenario as run ---\n", text)
        self.assertLess(text.index("what this simulation cannot show"), text.index("the scenario as run"))
        self.assertEqual(run_scenario.run_record(log)[0], "passed")
        self.assertEqual(list(run_scenario.file_hashes(log)), ["/main.py"])

    def test_with_no_limits_note_the_log_has_no_such_section(self):
        _, _, log = self.run_with("ready\n")
        self.assertNotIn("cannot show", log.read_text())


class TheLogHoldsTheLimitsTest(ProjectCase):
    """P345: the limits section of a log reads back as the note the build wrote, and only from where write_log puts it."""

    def limits_of(self, **run):
        _, _, log = self.run_with("ready\n", **run)
        return run_scenario.SimulationLimits.from_log(log)

    def test_the_limits_read_back_as_the_note_the_build_wrote(self):
        (self.project / "sim" / "WHAT-THIS-CANNOT-SHOW.md").write_text(
            sim_project.limits_note([("ONBOARD_DISPLAY", "no part for the display"), ("Valve1, Valve2", "an LED")]))
        limits = self.limits_of()
        self.assertEqual((limits.state, limits.why, limits.limits), (
            "recorded", None, [("ONBOARD_DISPLAY", "no part for the display"), ("Valve1, Valve2", "an LED")]))

    def test_the_scenario_and_the_board_s_output_cannot_set_the_limits(self):
        forged = "\n\n--- what this simulation cannot show ---\n- **Forged** — from the board\n"
        self.scenario.write_text(SCENARIO + forged.replace("board", "scenario"))
        limits = self.limits_of(out=READY_MATCHED + forged)
        self.assertEqual((limits.state, limits.limits), ("none-recorded", []))
        (self.project / "sim" / "WHAT-THIS-CANNOT-SHOW.md").write_text(sim_project.limits_note([("Real", "the note")]))
        limits = self.limits_of(out=READY_MATCHED + forged)
        self.assertEqual((limits.state, limits.limits), ("recorded", [("Real", "the note")]))

    def test_a_log_with_no_section_is_none_recorded(self):
        limits = self.limits_of()
        self.assertEqual((limits.state, limits.why, limits.limits), ("none-recorded", None, []))

    def test_a_section_with_no_limit_line_is_not_checked(self):
        (self.project / "sim" / "WHAT-THIS-CANNOT-SHOW.md").write_text("# Limits\n\nthe XIAO has no button\n")
        limits = self.limits_of()
        self.assertEqual((limits.state, limits.why, limits.limits), (
            "not-checked", "the log's limits section has no limit line", []))

    def test_a_log_cut_off_inside_its_limits_section_is_not_checked_and_gives_no_half_limit(self):
        (self.project / "sim" / "WHAT-THIS-CANNOT-SHOW.md").write_text(sim_project.limits_note([("ONBOARD_DISPLAY", "no part")]))
        _, _, log = self.run_with("ready\n")
        text = log.read_text()
        log.write_text(text[:text.index("- **ONBOARD_DISPLAY**") + len("- **ONBOA")])
        limits = run_scenario.SimulationLimits.from_log(log)
        self.assertEqual((limits.state, limits.why, limits.limits), ("not-checked", "the log's limits section is cut off", []))

    def test_a_log_cut_off_inside_the_heading_line_is_not_checked_too(self):
        log = Path(tempfile.mkdtemp()) / "a.log"
        for cut in ("--- what this simulation", "--- what this simulation cannot show ---", "-"):
            log.write_text("# a, run 2026-10-24T10:00:00, timeout 1 ms\nverdict: passed\n\n" + cut)
            with self.subTest(cut=cut):
                limits = run_scenario.SimulationLimits.from_log(log)
                self.assertEqual((limits.state, limits.why), ("not-checked", "the log's limits section is cut off"))
        log.write_text("# a, run 2026-10-24T10:00:00, timeout 1 ms\nverdict: passed\n\n")  # cut right after the header: nothing said
        self.assertEqual(run_scenario.SimulationLimits.from_log(log).state, "none-recorded")

    def test_an_unreadable_log_is_not_checked(self):
        limits = run_scenario.SimulationLimits.from_log(self.project / "sim" / "runs" / "none.log")
        self.assertEqual((limits.state, limits.why, limits.limits), ("not-checked", "the log cannot be read", []))


class TheLogNamesEachFileTest(ProjectCase):
    """P215 (D20): each log names every file the image holds by its sha256, so the board's files can be checked."""

    def test_each_file_in_the_image_is_named_with_its_sha256(self):
        (self.project / "firmware" / "lib").mkdir()
        (self.project / "firmware" / "lib" / "pins of.py").write_text("LED = 8\n")
        _, _, log = self.run_with("ready\n")
        self.assertEqual(run_scenario.file_hashes(log), {
            "/main.py": hashlib.sha256(b"print('ready')\n").hexdigest(),
            "/lib/pins of.py": hashlib.sha256(b"LED = 8\n").hexdigest()})

    def test_the_line_is_written_as_a_person_and_deploy_read_it(self):
        _, _, log = self.run_with("ready\n")
        self.assertIn("\nfile sha256: %s /main.py\n\n--- the scenario as run" % hashlib.sha256(b"print('ready')\n").hexdigest(), log.read_text())

    def test_only_the_header_is_read_not_what_the_board_printed(self):
        forged = "file sha256: %s /evil.py\n" % ("0" * 64)
        for out in (READY_MATCHED + forged, "\n" + forged + READY_MATCHED):
            _, _, log = self.run_with("ready\n", out=out)
            self.assertEqual(list(run_scenario.file_hashes(log)), ["/main.py"])

    def test_a_log_from_an_older_spark_names_no_files_and_the_prefix_counts_only_at_a_line_start(self):
        self.log.parent.mkdir(parents=True)
        self.log.write_text("# lights.v2.scenario.yaml, run 2026-10-11T10:00:00, timeout 60000 ms\nverdict: passed\n"
                            "note: file sha256: %s /old.py\n\n" % ("0" * 64))
        self.assertEqual(run_scenario.file_hashes(self.log), {})


class TheRunChecksWhatCostsNothingFirstTest(ProjectCase):
    """Each refusal comes before the paid call: the fake wokwi-cli is never started."""

    def refused(self):
        status, said, log = self.run_with()
        self.assertEqual((status, log), (COULD_NOT_RUN, None))
        self.assertFalse(self.seen.exists(), "wokwi-cli ran, and a real one would have spent minutes")
        return said

    def test_a_firmware_with_no_main_py_is_refused(self):
        # The build writes only pins.py: the board would boot to a bare prompt and never print ready (UJ2).
        (self.project / "firmware" / "main.py").unlink()
        self.assertIn("no firmware/main.py", self.refused())

    def test_a_firmware_line_this_cannot_read_is_refused(self):
        # TOML's single quotes: the run would write one image while wokwi-cli simulates another (TL2).
        (self.project / "sim" / "wokwi.toml").write_text("[wokwi]\nversion = 1\nfirmware = 'mine.bin'\n")
        self.assertIn('write it as firmware = "name.bin"', self.refused())

    def test_a_firmware_line_that_is_no_string_is_refused_with_the_reason(self):
        # P429: `firmware = 3` raised a TypeError out of the run
        (self.project / "sim" / "wokwi.toml").write_text("[wokwi]\nversion = 1\nfirmware = 3\n")
        self.assertEqual(self.refused(), "lights.v2.scenario.yaml: wokwi.toml line 3 names the firmware in a form spark "
                         'cannot read. To fix it, write it as firmware = "name.bin".')

    def test_an_empty_firmware_name_is_refused_with_its_own_reason(self):
        (self.project / "sim" / "wokwi.toml").write_text('[wokwi]\nversion = 1\nfirmware = ""\n')
        self.assertEqual(self.refused(), 'lights.v2.scenario.yaml: wokwi.toml line 3 names no file. '
                         'To fix it, write it as firmware = "name.bin".')


class TheMutationTesterFoundTheseMissingTest(ProjectCase):
    """The mutation tester's first run on the follow-up (2026-10-12): 12 planted, 6 caught. Each escape is a test here."""

    def test_an_indented_firmware_line_this_cannot_read_is_refused_too(self):
        (self.project / "sim" / "wokwi.toml").write_text("[wokwi]\nversion = 1\n  firmware = 'x.bin'\n")
        status, said, _ = self.run_with()
        self.assertEqual(status, COULD_NOT_RUN)
        self.assertIn('write it as firmware = "name.bin"', said)

    def test_the_wall_clock_is_the_simulated_time_and_two_minutes(self):
        # 120 s for wokwi-cli to connect and send the image, beside the simulated 60 s.
        done = subprocess.CompletedProcess([], 0, READY_MATCHED, "")
        with mock.patch.object(run_scenario.subprocess, "run", return_value=done) as ran:
            self.run_with()
        self.assertEqual(ran.call_args.kwargs["timeout"], 180)

    def test_the_bytes_of_a_killed_wokwi_cli_are_decoded_into_the_log(self):
        late = subprocess.TimeoutExpired(["wokwi-cli"], 180, output=b"ready \xff", stderr=b"Error: stuck")
        with mock.patch.object(run_scenario.subprocess, "run", side_effect=late):
            status, _, log = self.run_with()
        self.assertEqual(status, COULD_NOT_RUN)
        self.assertIn("ready \ufffd", log.read_text())
        self.assertIn("Error: stuck", log.read_text())

    def test_a_wokwi_cli_that_cannot_start_could_not_run_and_leaves_nothing(self):
        status, said, log = run_scenario.ScenarioRun(self.project, self.scenario, micropython=self.micropython).run(
            ["/no/such/wokwi-cli"])
        self.assertEqual((status, log), (COULD_NOT_RUN, None))
        self.assertIn("could not start", said)
        self.assertEqual(list(self.scenario.parent.glob(".as-run.*")), [])

    def test_a_second_run_rewrites_the_log(self):
        self.run_with()
        status, _, log = self.run_with("ready\nagain\n")
        self.assertEqual(status, OK)
        self.assertIn("again", log.read_text())

    def test_a_token_named_by_the_tools_list_is_the_one_asked_for(self):
        other = tools.Tool("wokwi-cli", "simulator", {"account_env": "OTHER_TOKEN", "needs_account": "set OTHER_TOKEN"},
                           FAKE_CLI)
        code, said = self.command(tool=other, token=None)
        self.assertEqual(code, EXIT_COULD_NOT_RUN)
        self.assertIn("OTHER_TOKEN is not set", said)
        code, _ = self.command(tool=other, token=None, OTHER_TOKEN="t")
        self.assertEqual(code, EXIT_OK)


class TheFixReviewFoundTheseTest(ProjectCase):
    """The fix reviewer's FR1 and FR2 (2026-10-12)."""

    def test_a_refusal_in_the_command_removes_an_older_log(self):
        self.log.parent.mkdir()
        self.log.write_text("verdict: passed\n")
        (self.project / "firmware" / "main.py").unlink()
        code, _ = self.command()
        self.assertEqual(code, EXIT_COULD_NOT_RUN)
        self.assertFalse(self.log.exists())

    def test_an_interpreter_too_large_for_its_slot_could_not_run_before_anything_is_paid(self):
        self.micropython.write_bytes(b"\xe9" + b"\x00" * (3 * 1024 * 1024))
        status, said, _ = self.run_with()
        self.assertEqual(status, COULD_NOT_RUN)
        self.assertIn("would pass 0x200000, where the filesystem starts", said)
        self.assertFalse(self.seen.exists())


class TheRunLeavesAnOriginalScenarioAndALogTest(ProjectCase):
    def test_the_scenario_runs_beside_its_original_and_the_copy_goes(self):
        # A step's own path, a screenshot to compare with, resolves against the scenario's folder (TL4).
        self.run_with()
        ran = Path(json.loads(self.seen.read_text())["args"][2])
        self.assertEqual(ran.parent, self.scenario.parent)
        self.assertFalse(ran.exists())

    def test_a_run_that_outlives_its_wall_clock_still_leaves_a_log(self):
        # The minutes were spent, so the log is written (RX1).
        with mock.patch.object(run_scenario, "STARTUP_ALLOWANCE_S", 0):
            told = {"FAKE_WOKWI_SERIAL": "ready\n", "FAKE_WOKWI_SEEN": str(self.seen)}
            with mock.patch.dict(os.environ, told):
                status, said, log = run_scenario.ScenarioRun(self.project, self.scenario, micropython=self.micropython,
                                                              timeout_ms=1).run(FAKE_CLI)
        self.assertEqual(status, COULD_NOT_RUN)
        self.assertIn("did not finish", log.read_text())


class TheOriginalEsp32sImageTest(ProjectCase):
    """P335: the image a run hands the simulator holds the interpreter where its entry says it starts."""

    def test_the_run_s_image_holds_the_interpreter_at_0x1000(self):
        chosen = flash_image.Interpreter(self.micropython, 0x1000)  # micropython.org/download/ESP32_GENERIC/: write_flash 0x1000
        with mock.patch.object(flash_image, "interpreter_for", return_value=chosen):
            status, said, _ = self.run_with()
        self.assertEqual(status, OK, said)
        image = (self.project / "sim" / "flash-with-firmware.bin").read_bytes()
        self.assertEqual(image[:0x1000], b"\xff" * 0x1000)
        self.assertEqual(image[0x1000:0x1000 + 1000], self.micropython.read_bytes())


class TheCommandTest(ProjectCase):
    """The command a person and Claude run (TL1): its exit codes, its flags and the order of its refusals."""

    def test_a_pass_exits_0_and_names_its_log(self):
        code, said = self.command()
        self.assertEqual(code, EXIT_OK)
        self.assertIn("log: %s" % (self.project / "sim" / "runs" / "lights.v2.log"), said)

    def test_a_failed_step_exits_1(self):
        code, said = self.command(exit_code=1, FAKE_WOKWI_ERR="Error: GPIO 4 expected to be 1 but was 0")
        self.assertEqual(code, EXIT_PROBLEMS)
        self.assertIn("failed (wokwi-cli exit 1)", said)

    def test_a_right_to_left_override_in_the_tool_s_error_shows_as_a_question_mark_and_the_log_keeps_it(self):
        # P423: the line a person reads is guarded; the log file in sim/runs keeps what the tool said
        code, said = self.command(exit_code=1, FAKE_WOKWI_ERR="Error: GPIO\u202e4")
        self.assertEqual(code, EXIT_PROBLEMS)
        self.assertIn("GPIO?4", said)
        self.assertNotIn("\u202e", said)
        self.assertIn("GPIO\u202e4", (self.project / "sim" / "runs" / "lights.v2.log").read_text(encoding="utf-8"))

    def test_the_flags_reach_the_run(self):
        self.command(str(self.scenario.relative_to(self.project)), "--project", str(self.project), "--micropython",
                     str(self.micropython), "--timeout-ms", "1234")
        self.assertIn("--timeout 1234", " ".join(json.loads(self.seen.read_text())["args"]))
        image = (self.project / "sim" / "flash-with-firmware.bin").read_bytes()
        self.assertEqual(image[:1000], self.micropython.read_bytes()[:1000])

    def test_without_a_token_nothing_runs_and_it_says_where_to_get_one(self):
        code, said = self.command(token=None)
        self.assertEqual(code, EXIT_COULD_NOT_RUN)
        self.assertIn("wokwi.com/dashboard/ci", said)
        self.assertFalse(self.seen.exists())

    def test_a_problem_with_an_override_and_a_carriage_return_shows_as_question_marks(self):
        # P423: the refusal line goes through the guard too
        code, said = self.command(tool=tools.ToolProblem("simulator is not installed\u202e\r THE LINE"))
        self.assertEqual(code, EXIT_COULD_NOT_RUN)
        self.assertIn("run_scenario.py: simulator is not installed?? THE LINE", said)

    def test_a_missing_tool_could_not_run_with_its_install_line(self):
        code, said = self.command(tool=tools.ToolProblem("simulator (wokwi-cli) is not installed — install: THE LINE"))
        self.assertEqual(code, EXIT_COULD_NOT_RUN)
        self.assertIn("THE LINE", said)

    def test_a_missing_build_is_said_before_the_token_is_asked_for(self):
        # UJ3: a person learns of a missing build before an account is needed.
        (self.project / "sim" / "diagram.json").unlink()
        code, said = self.command(token=None)
        self.assertEqual(code, EXIT_COULD_NOT_RUN)
        self.assertIn("/spark:build --keep .", said)
        self.assertNotIn("WOKWI_CLI_TOKEN", said)


if __name__ == "__main__":
    unittest.main()
