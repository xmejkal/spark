"""P1078 (#1582): run-scenario, the scenario run as an Operation on the core. No test spends a Wokwi minute: the token is
dropped in setUp, a paid run gets the test token "t" and a fake `run` that starts no program, and a dry run's world
refuses any program."""

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
from suite_runs import needs_littlefs  # noqa: E402
from micropython_fakes import fake_interpreter  # noqa: E402
from fakes import FakeReporter, FakeToolFinder  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from spark.core.cli import HelpText, run_cli, run_operation  # noqa: E402
from spark.core.errors import SparkError  # noqa: E402
from spark.core.outside import build_outside_world  # noqa: E402
from spark.firmware import sim_project  # noqa: E402
from spark.firmware.firmware_scenario import RunScenario  # noqa: E402
from spark.operation_catalogue import CATALOGUE  # noqa: E402
from spark.records import tool_finder  # noqa: E402

#: The simulator a paid run finds: a name only, because the fake `run` starts nothing.
SIMULATOR = tool_finder.Tool("wokwi-cli", "simulator", {"account_env": "WOKWI_CLI_TOKEN",
                                                       "needs_account": "a Wokwi token in WOKWI_CLI_TOKEN"}, ["wokwi-cli"])
READY_MATCHED = '[s] Expected text matched: "ready"\n'


def fake_run(code, serial, out):
    """A `run` that answers wokwi-cli as it would have run: it writes `serial` to the --serial-log-file and returns `code`
    with `out`, and starts no program. It keeps each argv in `ran`."""
    def run(argv, **options):
        run.ran.append(argv)
        Path(argv[argv.index("--serial-log-file") + 1]).write_text(serial)
        return subprocess.CompletedProcess(argv, code, out, "")
    run.ran = []
    return run


class RunScenarioCase(unittest.TestCase):
    """A built project with firmware and a scenario with no set-control step, and no WOKWI_CLI_TOKEN in the environment."""

    def setUp(self):
        patcher = mock.patch.dict(os.environ)
        patcher.start()
        self.addCleanup(patcher.stop)
        os.environ.pop("WOKWI_CLI_TOKEN", None)
        self.project = Path(tempfile.mkdtemp())
        sim = self.project / "sim"
        (sim / "scenarios").mkdir(parents=True)
        (sim / "diagram.json").write_text(json.dumps({"parts": [{"id": "mcu"}]}))
        (sim / "wokwi.toml").write_text(sim_project.wokwi_toml([]))
        (self.project / "firmware").mkdir()
        (self.project / "firmware" / "main.py").write_text("print('ready')\n")
        (sim / "scenarios" / "s.scenario.yaml").write_text('name: s\nversion: 1\nsteps:\n  - wait-serial: "LED on"\n')
        self.micropython = self.project / "micropython.bin"
        self.micropython.write_bytes(fake_interpreter())
        self.worlds = []

    def build(self, run):
        """The outside builder of a test: the core's world for the effects, the project's real finder but for the
        simulator, and `run` in place of a ProgramRunner when the effects hold RUNS. It keeps each world in `worlds`."""
        real = tool_finder.ToolFinder(self.project).find
        finder = FakeToolFinder({"simulator": SIMULATOR}, fall_back=lambda name, project: real(name))

        def builder(project, effects, reporter, values=None):
            world = build_outside_world(effects, reporter, find_tool=finder.find)
            world = world._replace(run=run) if "runs" in effects else world
            self.worlds.append(world)
            return world
        return builder

    def argv(self, *more):
        return ["sim/scenarios/s.scenario.yaml", "--project", str(self.project), "--micropython", str(self.micropython)] + list(more)

    def cli(self, *more, run=None, token=None):
        """(exit code, stdout, stderr) of run_scenario's run through run_cli, with the test token when `token` is given."""
        if token:
            os.environ["WOKWI_CLI_TOKEN"] = token
        with redirect_stdout(io.StringIO()) as out, redirect_stderr(io.StringIO()) as err:
            code = run_cli(HelpText("run_scenario.py"), RunScenario(), self.argv(*more),
                           outside_builder=self.build(run or fake_run(0, "ready\n", READY_MATCHED)))
        return code, out.getvalue(), err.getvalue()


class TheOperationTest(unittest.TestCase):
    def test_the_catalogue_lists_it_and_its_input_schema_builds(self):
        self.assertIs(CATALOGUE["run-scenario"], RunScenario)
        schema = RunScenario().input_schema()
        self.assertEqual(sorted(schema["properties"]), ["dry_run", "micropython", "project", "scenario", "timeout_ms"])
        self.assertEqual(schema["required"], ["scenario"])
        self.assertEqual(schema["properties"]["timeout_ms"], {"type": "integer", "description": "simulated time the run may take",
                                                               "default": 60000})

    def test_a_dry_run_only_reads_and_a_run_reads_runs_and_writes(self):
        self.assertEqual(RunScenario().effects_of({"dry_run": True}), ("reads",))
        self.assertEqual(RunScenario().effects_of({"dry_run": False}), ("reads", "runs", "writes"))


@needs_littlefs
class TheDryRunTest(RunScenarioCase):
    def test_a_dry_run_s_world_refuses_any_program(self):
        code, out, _ = self.cli("--dry-run")
        self.assertEqual(code, 0, out)
        with self.assertRaises(SparkError) as refused:
            self.worlds[0].run(["wokwi-cli"])
        self.assertEqual(refused.exception.code, "undeclared_effect")

    def test_an_ok_dry_run_names_the_paid_run_with_the_run_s_values(self):
        code, out, _ = self.cli("--dry-run", "--timeout-ms", "5000", "--json")
        said = json.loads(out)
        self.assertEqual((code, said["status"], said["data"]["ran"], said["data"]["log"]), (0, "ok", False, None))
        step = said["next"][0]
        self.assertEqual((step["op"], step["argv"], step["needs_yes"], step["needs_person"], step["effects"]),
                         ("run-scenario", ["sim/scenarios/s.scenario.yaml", "--project", str(self.project.absolute()),
                                           "--micropython", str(self.micropython.absolute()), "--timeout-ms", "5000"],
                          False, True, ["reads", "runs", "writes"]))
        self.assertIn("SPARK_HOME", step["env"])

    def test_a_dry_run_with_no_sim_could_not_run_with_its_code(self):
        (self.project / "sim" / "diagram.json").unlink()
        code, out, _ = self.cli("--dry-run", "--json")
        said = json.loads(out)
        self.assertEqual((code, said["status"], said["unchecked"][0]["code"], said["next"], said["data"]["ran"]),
                         (2, "could-not-run", "no_sim_project", [], False))


@needs_littlefs
class ThePaidRunTest(RunScenarioCase):
    def test_no_token_could_not_run_with_its_code_and_starts_nothing(self):
        run = fake_run(0, "ready\n", READY_MATCHED)
        code, out, _ = self.cli("--json", run=run)
        said = json.loads(out)
        self.assertEqual((code, said["unchecked"][0]["code"], said["data"]["ran"], said["data"]["log"], run.ran),
                         (2, "no_token", False, None, []))

    def test_never_ready_is_a_problem_with_its_code_and_the_log(self):
        code, out, _ = self.cli("--json", run=fake_run(42, "booting\n", ""), token="t")
        said = json.loads(out)
        self.assertEqual((code, said["status"], said["problems"][0]["code"], said["data"]["ran"]),
                         (1, "problems", "never_ready", True))
        self.assertEqual(said["data"]["log"], str(self.project / "sim" / "runs" / "s.log"))

    def test_the_run_starts_wokwi_cli_through_the_world_s_run(self):
        run = fake_run(0, "ready\n", READY_MATCHED)
        self.assertEqual(self.cli(run=run, token="t")[0], 0)
        self.assertEqual(run.ran[0][:3], ["wokwi-cli", str(self.project / "sim"), "--scenario"])

    def test_the_caveat_of_a_pass_is_in_the_text_once_and_a_note_in_json(self):
        caveat = "passed, but it has no set-control step"
        code, out, _ = self.cli(token="t")
        self.assertEqual((code, out.count(caveat)), (0, 1), out)
        said = json.loads(self.cli("--json", token="t")[1])
        self.assertEqual(said["status"], "ok")
        self.assertEqual(len(said["notes"]), 1)
        self.assertTrue(said["notes"][0].startswith(caveat), said["notes"])

    def test_a_not_checked_line_leaves_a_pass_ok_and_reaches_the_text(self):
        (self.project / "sim" / "diagram.json").write_text("{")
        code, out, _ = self.cli(token="t")
        self.assertEqual(code, 0, out)
        self.assertIn("not checked: the scenario's component ids, because", out)
        said = json.loads(self.cli("--json", token="t")[1])
        self.assertEqual(said["status"], "ok")
        self.assertTrue(said["assumptions"][0].startswith("not checked: the scenario's component ids, because"), said)
        self.assertEqual(said["problems"] + said["unchecked"], [])

    def test_a_refusal_is_not_ran_and_a_pass_is(self):
        self.assertFalse(json.loads(self.cli("--json")[1])["data"]["ran"])
        self.assertTrue(json.loads(self.cli("--json", token="t")[1])["data"]["ran"])

    def test_run_operation_answers_a_code_caller_as_the_cli_does(self):
        # the later MCP server's door: the catalogue's class, its values and a world
        values = {"scenario": Path("sim/scenarios/s.scenario.yaml"), "project": self.project, "timeout_ms": 60000,
                  "micropython": self.micropython, "dry_run": True}
        result = run_operation(CATALOGUE["run-scenario"](), values, build_outside=lambda effects: self.build(None)(
            self.project, effects, FakeReporter()))
        self.assertEqual((result.status(), result.next[0].op), ("ok", "run-scenario"))


if __name__ == "__main__":
    unittest.main()
