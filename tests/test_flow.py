"""
The flow reader (P825, #1183): `flow.py show` says where a project stands, phase by phase, from the files the earlier
stages wrote, and offers the next steps as keys. On five projects (no needs, picked, built by hand with no needs, a build
that ended in could-not-run, requirements changed after the build) each test pins all nine phases' status and offer keys
from `flow.py show --json`, and `stands_at`. More tests pin one phase each.
It covers the area's modules `show_flow`, `phase_readers` and `flow_codes`, and the build record `build_record`.

    python3 -m unittest tests.test_flow
"""

import contextlib
import datetime
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import flow  # noqa: E402
from fakes import FakeClock, FakeOutsideWorld, FakeTextFileWriter  # noqa: E402
from spark.build.build_record import BUILD_RECORD_FILE, BuildRecordStore, sha256_of  # noqa: E402
from spark.core import zone_time  # noqa: E402
from spark.flow.phase_readers import SimulateReader  # noqa: E402
from spark.flow.guide import guide_of  # noqa: E402
from spark.flow.show_flow import ShowFlow, read_flow  # noqa: E402
from spark.flow.fingerprint import fingerprint_of  # noqa: E402
from spark.core.cli import run_operation  # noqa: E402
from spark.core.outcomes import OK  # noqa: E402
from spark.design.pick_parts import NO_PASSED_OVER, PickParts  # noqa: E402
from spark.design.write_requirements import WriteRequirements  # noqa: E402
from spark.flow.flow_codes import STALE  # noqa: E402
from spark.records import store  # noqa: E402

#: A built project: requirements.json, the board it names and the circuit a finished build kept with its built-from.json.
BUILT = ROOT / "tests" / "data" / "breadboard" / "button-light-xiao"
PHASES = ["idea", "needs", "parts", "requirements", "build", "breadboard", "firmware", "simulate", "deploy"]


def show(project, *argv):
    """`flow.py show --project <project> --json`: (the envelope, the exit code)."""
    with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
        code = flow.main(["show", "--project", str(project), "--json", *argv])
    return json.loads(out.getvalue()), code


def table(envelope):
    """{phase: (status, [offer keys])} for all nine phases."""
    return {phase["phase"]: (phase["status"], [offer["key"] for offer in phase["offers"]]) for phase in envelope["data"]["phases"]}


def statuses(envelope):
    return {phase["phase"]: phase["status"] for phase in envelope["data"]["phases"]}


def marks(envelope):
    return {phase["phase"]: phase["mark"] for phase in envelope["data"]["phases"]}


def offers(envelope, phase):
    return [offer["key"] for offer in next(each for each in envelope["data"]["phases"] if each["phase"] == phase)["offers"]]


def says(envelope, phase):
    return next(each for each in envelope["data"]["phases"] if each["phase"] == phase)["says"]


def a_store():
    """A scratch store: three soil probes in the catalog, each owned once in the drawer — 3 held by another project, many,
    and a count nobody gave."""
    home = Path(tempfile.mkdtemp())
    for folder in ("catalog", "drawer"):
        (home / folder).mkdir()
    for part in ("x-held", "x-many", "x-unknown"):
        (home / "catalog" / (part + ".json")).write_text(json.dumps({"schema": 1, "id": part, "name": "A soil probe", "kind": "sensor",
                                                                     "function": [{"does": "sense", "what": "soil-moisture"}]}))
    entries = {"held": {"label": "three probes", "count": 3, "is": {"part": "x-held"}, "used_in": {"smartbin-local": 3}},
               "many": {"label": "a bag of probes", "count": "many", "is": {"part": "x-many"}},
               "unknown": {"label": "some probes", "is": {"part": "x-unknown"}}}
    for key, entry in entries.items():
        (home / "drawer" / (key + ".json")).write_text(json.dumps(dict({"schema": 1}, **entry)))
    return home


def with_needs(project, needs):
    (project / ".spark").mkdir(parents=True, exist_ok=True)
    (project / ".spark" / "needs.json").write_text(json.dumps({"schema": 1, "needs": needs}))
    return project


def a_built_project(status="ok", stages=None):
    """A copy of the built fixture with its breadboard sheet and the record of a build that ended in `status`. `stages` are
    the record's {name: status}, in order (None: a board and a build that ended in `status`)."""
    project = Path(tempfile.mkdtemp()) / "xiao"
    shutil.copytree(BUILT, project)
    (project / "breadboard.md").write_text("# the sheet\n")
    stages = [{"name": name, "status": ended} for name, ended in (stages or {"board": "ok", "build": status}).items()]
    BuildRecordStore(project, clock=FakeClock()).write({"status": status, "stages": stages, "missing_facts": [],
                                                       "requirements": "requirements.json",
                                                       "requirements_sha256": sha256_of(project / "requirements.json")})
    return project


def a_board_only_project(simulation="ok"):
    """A project built on the board alone, as `build_service.board_alone` records it: four skipped stages and a simulation
    that ended in `simulation`. A board-only build keeps no sheet."""
    project = a_built_project(simulation, {"board": "ok", "parts": "skipped", "schematic": "skipped", "footprint": "skipped",
                                           "build": "skipped", "simulation": simulation})
    (project / "breadboard.md").unlink()
    return project


def lines_of(project):
    """The lines `flow.py show` prints for a person."""
    with contextlib.redirect_stdout(io.StringIO()) as out:
        flow.main(["show", "--project", str(project)])
    return out.getvalue().splitlines()


def a_built_project_with_a_sheet_from(requirements):
    """A built project whose built-from.json names `requirements`."""
    project = a_built_project()
    (project / "dist" / "board" / "built-from.json").write_text(json.dumps({"requirements": requirements}))
    return project


NS = "not-started"
#: A project built by hand: requirements.json and no needs, its build and its sheet current, no firmware yet. Spark
#: compared the requirements with nothing and does not judge the wiring, so neither has a status (P878).
BUILT_TABLE = {"idea": (None, []), "needs": (None, []), "parts": (None, []), "requirements": (None, []), "build": ("ok", ["build"]),
               "breadboard": (None, []), "firmware": (NS, []), "simulate": (NS, []), "deploy": (NS, [])}


class FlowTest(unittest.TestCase):
    def setUp(self):
        self.home = a_store()
        patcher = mock.patch.dict(os.environ, {"SPARK_HOME": str(self.home)})
        patcher.start()
        self.addCleanup(patcher.stop)


class ThePhasesTest(FlowTest):
    def test_a_project_with_no_needs_stands_at_the_needs(self):
        project = Path(tempfile.mkdtemp()) / "plant-alarm"
        project.mkdir()
        said, code = show(project)
        self.assertEqual((code, said["status"], said["tool"], said["op"]), (0, "ok", "flow", "show-flow"))
        self.assertEqual([phase["phase"] for phase in said["data"]["phases"]], PHASES)
        self.assertEqual(table(said), {"idea": (None, []), "needs": (NS, []), "parts": (NS, []), "requirements": (NS, []),
                                       "build": (NS, []), "breadboard": (NS, []), "firmware": (NS, []), "simulate": (NS, []),
                                       "deploy": (NS, [])})
        self.assertEqual(said["data"]["stands_at"], "needs")
        self.assertEqual(says(said, "idea"), ["Tell Claude your goal in the chat"])
        self.assertEqual(says(said, "firmware"), ["no firmware/main.py yet"])
        self.assertIn("no sim/wokwi.toml", says(said, "simulate")[0])
        self.assertEqual(says(said, "deploy"), ["ask Claude to look at the board first",
                                                "then run ${CLAUDE_PLUGIN_ROOT}/scripts/deploy.py --dry-run in your terminal"])
        self.assertEqual([phase["by"] for phase in said["data"]["phases"]],
                         ["you", "claude", "you", "claude", "claude", "you", "claude", "your terminal", "your terminal"])

    def test_a_project_with_one_of_two_needs_picked_offers_each_pick_with_what_it_does(self):
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [
            {"id": "soil", "does": "sense", "what": "soil-moisture", "pick": [{"part": "x-many"}]},
            {"id": "wet", "does": "sense", "what": "soil-moisture"}])
        said, code = show(project)
        self.assertEqual(code, 0)
        picks = ["pick:%s:%s" % (need, part) for need in ("soil", "wet") for part in ("x-held", "x-many", "x-unknown", "vl6180x-breakout")]
        self.assertEqual(table(said), {"idea": (None, []), "needs": ("ok", ["needs-drop:soil", "needs-drop:wet"]), "parts": ("partial", picks),
                                       "requirements": (NS, ["requirements"]), "build": (NS, []), "breadboard": (NS, []),
                                       "firmware": (NS, []), "simulate": (NS, []), "deploy": (NS, [])})
        self.assertEqual(said["data"]["stands_at"], "parts")
        self.assertIn("1 of 2 needs picked", says(said, "parts"))
        effects = {offer["key"]: offer["effect"] for offer in said["data"]["phases"][2]["offers"]}
        self.assertEqual(effects["pick:wet:x-held"], "Too few “A soil probe” are free for this pick (3 owned, held by smartbin-local — 1 picked "
                                                     "here), so spark refuses this pick and saves nothing.")
        self.assertEqual(effects["pick:wet:x-many"], "Saves “A soil probe” as the pick for the wet need in this project. Uses 1 of your “A soil "
                                                     "probe” for the wet. Adds this project to your list of projects. May note the choice in your history.")
        self.assertEqual(effects["pick:wet:x-unknown"], "Saves “A soil probe” as the pick for the wet need in this project. Uses 1 of your “A "
                                                        "soil probe” for the wet, if you have one: spark does not know how many you have. Adds "
                                                        "this project to your list of projects. May note the choice in your history.")
        self.assertEqual(said["data"]["phases"][1]["offers"][0]["effect"], "To drop this need, tell Claude: “drop the soil need”.")
        labels = {offer["key"]: offer["label"] for offer in said["data"]["phases"][2]["offers"]}
        self.assertEqual(labels["pick:wet:x-many"], "Pick “A soil probe” for wet")

    def test_every_need_picked_makes_the_parts_ok(self):
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [
            {"id": "soil", "does": "sense", "what": "soil-moisture", "pick": [{"part": "x-many"}]}])
        said, _ = show(project)
        self.assertEqual(statuses(said)["parts"], "ok")
        self.assertEqual(said["data"]["stands_at"], "requirements")

    def test_needs_with_no_pick_leave_the_parts_not_started(self):
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [{"id": "soil", "does": "sense", "what": "soil-moisture"}])
        self.assertEqual(statuses(show(project)[0])["parts"], NS)

    def test_a_need_with_no_what_gives_the_parts_problems_and_exit_1(self):
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [{"id": "soil", "does": "sense"}])
        said, code = show(project)
        self.assertEqual((code, said["status"], statuses(said)["parts"]), (1, "problems", "problems"))
        self.assertIn("soil: a need with no `what` cannot be matched", says(said, "parts")[0])
        self.assertEqual([(item["subject"], item["code"]) for item in said["problems"]], [("parts", "phase_problems")])

    def test_problems_beside_a_phase_that_could_not_run_give_problems_and_exit_1(self):
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [{"id": "soil", "does": "sense"}])
        (project / ".spark" / "build.json").write_text("{not json")
        said, code = show(project)
        self.assertEqual((code, said["status"], statuses(said)["build"]), (1, "problems", "could-not-run"))
        self.assertEqual([item["subject"] for item in said["unchecked"]], ["build"])

    def an_unreadable_record_is_one_sentence(self, text):
        """Show a built project whose build record holds `text`; assert the build phase is could-not-run with the one sentence."""
        project = a_built_project()
        (project / BUILD_RECORD_FILE).write_text(text)
        said, code = show(project)
        self.assertEqual((code, said["status"]), (2, "could-not-run"), text)
        self.assertEqual(len(said["data"]["phases"]), 9, text)
        self.assertEqual(statuses(said)["build"], "could-not-run", text)
        self.assertEqual(len(says(said, "build")), 1, text)
        self.assertEqual(says(said, "build"), [".spark/build.json is no build record: build again with --keep"], text)
        self.assertEqual({item["code"] for item in said["unchecked"]}, {"phase_could_not_run"}, text)
        with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()) as err:
            flow.main(["show", "--project", str(project)])
        self.assertNotIn("Traceback", out.getvalue() + err.getvalue(), text)

    def test_a_record_whose_stages_is_no_list_is_could_not_run_in_one_sentence(self):
        self.an_unreadable_record_is_one_sentence('{"status": "ok", "stages": 5}')

    def test_a_stages_entry_that_is_no_object_is_the_same_sentence(self):
        for text in ('{"stages": [5]}', '{"stages": "ab"}', '{"stages": {"a": 1}}'):
            with self.subTest(text=text):
                self.an_unreadable_record_is_one_sentence(text)

    def test_a_missing_facts_that_is_no_list_is_the_same_sentence(self):
        self.an_unreadable_record_is_one_sentence('{"status": "ok", "missing_facts": 5}')

    def test_a_requirements_that_is_no_string_is_the_same_sentence(self):
        self.an_unreadable_record_is_one_sentence('{"status": "ok", "requirements": 5}')

    def test_a_record_that_is_no_object_is_the_same_sentence(self):
        # A pin: the shape was refused before P886; it is here for the same sentence at the flow's level.
        for text in ("[]", '"text"', "5"):
            with self.subTest(text=text):
                self.an_unreadable_record_is_one_sentence(text)

    def test_a_project_built_by_hand_with_no_needs_stands_at_the_firmware(self):
        said, code = show(a_built_project())
        self.assertEqual(code, 0)
        self.assertEqual(table(said), BUILT_TABLE)
        self.assertEqual(said["data"]["stands_at"], "firmware")
        self.assertEqual(says(said, "needs"), ["a hand-written project: requirements.json and no needs"])
        self.assertIn(zone_time.stamp(FakeClock().now()), " ".join(says(said, "build")))

    def test_a_build_that_could_not_run_says_so_and_exits_2(self):
        said, code = show(a_built_project("could-not-run"))
        self.assertEqual((code, said["status"]), (2, "could-not-run"))
        self.assertEqual(table(said), dict(BUILT_TABLE, build=("could-not-run", ["build"])))
        self.assertEqual(said["data"]["stands_at"], "build")
        self.assertEqual([(item["subject"], item["code"]) for item in said["unchecked"]], [("build", "phase_could_not_run")])
        self.assertIn("build: could-not-run", says(said, "build"))

    def test_requirements_changed_after_the_build_make_the_build_and_the_sheet_stale(self):
        project = a_built_project()
        (project / "requirements.json").write_text(json.dumps({"board": "xiao-esp32-c6-fresh", "parts": ["tactile-button"]}))
        said, code = show(project)
        self.assertEqual(code, 0)
        self.assertEqual(table(said), dict(BUILT_TABLE, build=("stale", ["build"]), breadboard=("stale", [])))
        self.assertEqual(said["data"]["stands_at"], "build")

    def test_a_sheet_built_from_other_requirements_is_stale_while_the_build_record_is_current(self):
        said, _ = show(a_built_project_with_a_sheet_from({"board": "x", "parts": []}))
        self.assertEqual((statuses(said)["build"], statuses(said)["breadboard"]), ("ok", "stale"))

    def test_the_same_requirements_written_again_in_other_bytes_make_the_build_and_its_sheet_stale(self):
        project = a_built_project()
        written = json.loads((project / "requirements.json").read_text())
        (project / "requirements.json").write_text(json.dumps(written, indent=4))
        said, _ = show(project)
        self.assertEqual({phase: statuses(said)[phase] for phase in ("requirements", "build", "breadboard")},
                         {"requirements": None, "build": "stale", "breadboard": "stale"})

    def test_a_board_only_build_gets_no_tick_and_the_project_stands_at_the_firmware(self):
        project = a_board_only_project()
        said, code = show(project)
        self.assertEqual(code, 0)
        self.assertEqual((table(said)["build"], table(said)["breadboard"]), ((None, []), (None, [])))
        self.assertEqual((marks(said)["build"], marks(said)["breadboard"]), ("·", "·"))
        self.assertEqual(says(said, "build"), ["board only: nothing to wire, no board was built"])
        self.assertEqual(says(said, "breadboard"), ["board only: nothing to wire"])
        self.assertEqual(said["data"]["stands_at"], "firmware")
        self.assertIn("  · build: board only: nothing to wire, no board was built (claude)", lines_of(project))

    def test_a_board_only_build_whose_requirements_changed_is_stale_and_its_sheet_not_started(self):
        project = a_board_only_project()
        (project / "requirements.json").write_text(json.dumps({"board": "xiao-esp32-c6-fresh", "parts": ["tactile-button"]}))
        said, _ = show(project)
        self.assertEqual((statuses(said)["build"], statuses(said)["breadboard"]), ("stale", NS))
        self.assertEqual(said["data"]["stands_at"], "build")

    def test_a_board_only_build_whose_simulation_could_not_run_stays_could_not_run(self):
        said, code = show(a_board_only_project("could-not-run"))
        self.assertEqual((code, statuses(said)["build"], said["data"]["stands_at"]), (2, "could-not-run", "build"))
        self.assertIn("simulation: could-not-run", says(said, "build"))
        self.assertEqual(offers(said, "build"), ["build"])
        self.assertEqual((statuses(said)["breadboard"], says(said, "breadboard")), (None, ["board only: nothing to wire"]))

    def test_a_build_whose_simulation_alone_was_skipped_gets_no_tick_and_says_why(self):
        project = a_built_project(stages={"board": "ok", "build": "ok", "simulation": "skipped"})
        said, code = show(project)
        self.assertEqual((code, statuses(said)["build"], marks(said)["build"]), (0, None, "·"))
        self.assertEqual(says(said, "build")[1:], ["simulation: skipped",
                                                   "every part is skipped from the simulation, so spark did not judge the diagram"])
        self.assertEqual(said["data"]["stands_at"], "firmware")
        self.assertFalse([line for line in lines_of(project) if "✓ build" in line])

    def test_any_other_skipped_stage_makes_the_build_partly_done(self):
        for stages in ({"board": "ok", "footprint": "skipped", "build": "ok"},
                       {"board": "ok", "footprint": "skipped", "build": "ok", "simulation": "skipped"}):
            with self.subTest(stages=stages):
                project = a_built_project(stages=stages)
                said, code = show(project)
                self.assertEqual((code, statuses(said)["build"], marks(said)["build"]), (0, "partial", "◐"))
                self.assertIn("footprint: skipped", says(said, "build"))
                self.assertEqual(said["data"]["stands_at"], "build")
                self.assertTrue([line for line in lines_of(project) if line.startswith("  ◐ build: partly done, ")])

    def test_a_current_sheet_gets_no_tick_because_spark_does_not_judge_the_wiring(self):
        said, _ = show(a_built_project())
        self.assertEqual((statuses(said)["breadboard"], marks(said)["breadboard"]), (None, "·"))
        self.assertEqual(says(said, "breadboard"), ["breadboard.md, spark does not judge the wiring"])

    def test_a_missing_sheet_beside_a_build_record_that_cannot_be_read_is_not_started(self):
        project = a_built_project()
        (project / "breadboard.md").unlink()
        (project / BUILD_RECORD_FILE).write_text("{not json")
        self.assertEqual(statuses(show(project)[0])["breadboard"], NS)

    def test_requirements_with_no_needs_get_no_tick_because_nothing_was_compared(self):
        said, _ = show(a_built_project())
        self.assertEqual((statuses(said)["requirements"], marks(said)["requirements"]), (None, "·"))
        self.assertEqual(says(said, "requirements"), ["requirements.json, with no needs to compare it with, so spark did not judge it"])

    def test_requirements_that_are_what_the_picks_give_are_ok(self):
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [
            {"id": "board", "does": "compute", "what": "microcontroller", "pick": [{"board": "xiao-esp32-c6"}]}])
        (project / "requirements.json").write_text(json.dumps({"board": "xiao-esp32-c6", "parts": [], "board_only": True}))
        said, _ = show(project)
        self.assertEqual(table(said)["requirements"], ("ok", ["requirements"]))
        self.assertEqual(said["data"]["stands_at"], "build")

    def test_requirements_that_differ_from_the_picks_are_stale(self):
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [
            {"id": "board", "does": "compute", "what": "microcontroller", "pick": [{"board": "xiao-esp32-c6"}]}])
        (project / "requirements.json").write_text(json.dumps({"board": "firebeetle2-esp32s3", "parts": []}))
        said, _ = show(project)
        self.assertEqual(table(said)["requirements"], ("stale", ["requirements"]))

    def test_requirements_with_no_board_picked_have_problems(self):
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [
            {"id": "soil", "does": "sense", "what": "soil-moisture", "pick": [{"part": "x-many"}]}])
        (project / "requirements.json").write_text(json.dumps({"board": "xiao-esp32-c6", "parts": []}))
        said, _ = show(project)
        self.assertEqual(statuses(said)["requirements"], "problems")
        self.assertIn("board: pick one board", says(said, "requirements")[0])

    def test_a_broken_needs_file_makes_each_phase_that_reads_it_could_not_run_and_the_rest_answer(self):
        project = Path(tempfile.mkdtemp()) / "plant-alarm"
        (project / ".spark").mkdir(parents=True)
        (project / ".spark" / "needs.json").write_text("{not json")
        said, code = show(project)
        self.assertEqual(code, 2)
        self.assertEqual({phase: statuses(said)[phase] for phase in ("needs", "parts", "requirements", "build", "deploy")},
                         {"needs": "could-not-run", "parts": "could-not-run", "requirements": "could-not-run", "build": NS,
                          "deploy": NS})
        self.assertIn("is not JSON", says(said, "needs")[0])
        self.assertEqual(sorted(item["subject"] for item in said["unchecked"]), ["needs", "parts", "requirements"])

    def test_a_requirements_file_that_is_no_json_is_could_not_run(self):
        project = Path(tempfile.mkdtemp()) / "plant-alarm"
        project.mkdir()
        (project / "requirements.json").write_text("{not json")
        said, _ = show(project)
        self.assertEqual(statuses(said)["requirements"], "could-not-run")
        self.assertIn("is not JSON", says(said, "requirements")[0])

    def test_the_firmware_s_time_is_said_in_the_machine_s_zone(self):
        project = a_built_project()
        (project / "firmware").mkdir()
        (project / "firmware" / "main.py").write_text("print(1)\n")
        os.utime(project / "firmware" / "main.py", (1_700_000_000, 1_700_000_000))
        said, _ = show(project)
        self.assertIsNone(statuses(said)["firmware"])
        self.assertEqual(says(said, "firmware"), ["firmware/main.py written %s" % zone_time.stamp(datetime.datetime.fromtimestamp(1_700_000_000))])
        self.assertEqual(said["data"]["stands_at"], "simulate")

    def test_a_simulation_fact_says_a_passed_run_tested_the_image_or_why_not(self):
        project = a_built_project()
        (project / "sim").mkdir()
        (project / "sim" / "wokwi.toml").write_text('[wokwi]\nversion = 1\nfirmware = "image.bin"\n')
        (project / "sim" / "image.bin").write_bytes(b"an image")
        said, _ = show(project)
        self.assertIn("no run in sim/runs/ tested image.bin", says(said, "simulate")[0])
        self.assertNotIn("older spark", says(said, "simulate")[0])  # P878: no log is there to blame
        self.assertIn("run ${CLAUDE_PLUGIN_ROOT}/scripts/run_scenario.py sim/scenarios/<name>.scenario.yaml in your terminal: "
                      "it uses Wokwi CI minutes", says(said, "simulate"))
        self.assertIsNone(statuses(said)["simulate"])

    def test_a_firmware_line_spark_cannot_read_gives_the_simulate_phase_problems(self):
        project = a_built_project()
        (project / "sim").mkdir()
        (project / "sim" / "wokwi.toml").write_text("[wokwi]\nversion = 1\nfirmware = 42\n")
        said, _ = show(project)
        self.assertEqual(statuses(said)["simulate"], "problems")

    def test_a_run_log_spark_cannot_read_gives_the_simulate_phase_could_not_run_with_its_sentence(self):
        # P853: the reader raised a SparkError with no fix, a TypeError that crashed the whole flow
        project = a_built_project()
        (project / "sim" / "runs").mkdir(parents=True)
        (project / "sim" / "wokwi.toml").write_text('[wokwi]\nversion = 1\nfirmware = "image.bin"\n')
        (project / "sim" / "image.bin").write_bytes(b"an image")
        log = project / "sim" / "runs" / "a.log"
        log.write_text("")
        log.chmod(0)
        self.addCleanup(log.chmod, 0o600)
        phase = SimulateReader().answer(project)
        self.assertEqual((phase.status, phase.says), ("could-not-run", ["cannot read %s: [Errno 13] Permission denied: '%s'" % (log, log)]))


class TheCommandTest(FlowTest):
    def test_help_exits_0(self):
        with contextlib.redirect_stdout(io.StringIO()) as out, self.assertRaises(SystemExit) as stopped:
            flow.main(["--help"])
        self.assertEqual(stopped.exception.code, 0)
        self.assertIn("Exit codes:", out.getvalue())

    def test_each_verb_s_help_says_its_own_operation_s_sentence(self):
        # P937 (the PO, 2026-11-20): one sentence per Operation, the summary of the verb's
        from spark.flow.write_flow_page import WriteFlowPage
        for argv, own, other in ((["--help"], ShowFlow, WriteFlowPage), (["show", "--help"], ShowFlow, WriteFlowPage),
                                 (["page", "--help"], WriteFlowPage, ShowFlow)):
            with contextlib.redirect_stdout(io.StringIO()) as out, self.assertRaises(SystemExit):
                flow.main(argv)
            self.assertIn("\n" + own.summary + "\n", out.getvalue(), argv)
            self.assertNotIn(other.summary, out.getvalue(), argv)

    def test_a_word_that_is_no_verb_is_refused_with_2(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as stopped:
            flow.main(["nonsense"])
        self.assertEqual(stopped.exception.code, 2)

    def test_no_verb_shows(self):
        project = Path(tempfile.mkdtemp()) / "plant-alarm"
        project.mkdir()
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = flow.main(["--project", str(project)])
        self.assertEqual(code, 0)
        self.assertIn("needs: not started", out.getvalue())
        self.assertIn("stands at: needs", out.getvalue())

    def test_the_lines_leave_ok_to_the_mark_and_show_five_offer_keys_and_how_many_more(self):
        project = with_needs(a_built_project(), [
            {"id": "soil", "does": "sense", "what": "soil-moisture", "pick": [{"part": "x-many"}]},
            {"id": "wet", "does": "sense", "what": "soil-moisture"}])
        with contextlib.redirect_stdout(io.StringIO()) as out:
            flow.main(["show", "--project", str(project)])
        lines = out.getvalue().splitlines()
        self.assertIn("  ✓ needs: 2 need(s): soil, wet (claude)", lines)
        self.assertIn("      offers: pick:soil:x-held, pick:soil:x-many, pick:soil:x-unknown, pick:soil:vl6180x-breakout, "
                      "pick:wet:x-held, +3 more", lines)

    def test_the_data_keys_are_a_real_answer_s_keys(self):
        project = Path(tempfile.mkdtemp()) / "plant-alarm"
        project.mkdir()
        self.assertEqual(sorted(show(project)[0]["data"]), sorted(ShowFlow.data_keys))

    def test_the_answer_names_no_home_path(self):
        said, _ = show(a_built_project())
        self.assertNotIn(str(Path.home()), json.dumps(said))
        self.assertIn("<project>", json.dumps(said))


class TheBuildRecordStoreTest(unittest.TestCase):
    def test_a_write_holds_the_schema_the_record_and_the_time_in_the_machine_s_zone(self):
        writer, project = FakeTextFileWriter(), Path(tempfile.mkdtemp())
        path = BuildRecordStore(project, writer, FakeClock()).write({"status": "ok"})
        self.assertEqual(path, project / BUILD_RECORD_FILE)
        self.assertEqual(json.loads(writer.written[path]), {"schema": 1, "status": "ok", "at": zone_time.stamp(FakeClock().now())})

    def test_a_project_with_no_record_reads_none_and_a_broken_one_is_refused(self):
        project = Path(tempfile.mkdtemp())
        self.assertIsNone(BuildRecordStore(project).read())
        (project / ".spark").mkdir()
        for text in ("{not json", "[]", '{"stages": 5}', '{"stages": [5]}', '{"stages": 0}',
                     '{"missing_facts": 5}', '{"requirements": 5}',
                     '{"requirements": ["r.json"]}', '{"missing_facts": {"a": 1}}', "[" * 200000):
            (project / BUILD_RECORD_FILE).write_text(text)
            with self.assertRaises(store.StoreError) as refused:
                BuildRecordStore(project).read()
            self.assertEqual(refused.exception.code, "record_file_broken")

    def test_a_record_with_a_shape_the_readers_can_use_is_read(self):
        # Pins: the shapes that were readable before P886 stay readable.
        project = Path(tempfile.mkdtemp())
        (project / ".spark").mkdir()
        for text in ('{"status": "ok"}', '{"stages": null}', '{"stages": [{}]}', '{"stages": []}',
                     '{"missing_facts": ["x"], "requirements": "r.json"}'):
            (project / BUILD_RECORD_FILE).write_text(text)
            self.assertEqual(BuildRecordStore(project).read(), json.loads(text), text)

    def test_an_unreadable_record_holds_no_sha256(self):
        project = Path(tempfile.mkdtemp())
        (project / ".spark").mkdir()
        record = {"stages": 5, "written_sha256": {"board.tsx": "ab" * 32}}
        (project / BUILD_RECORD_FILE).write_text(json.dumps(record))
        self.assertEqual(BuildRecordStore(project).written_sha256(), {})
        (project / BUILD_RECORD_FILE).write_text(json.dumps(dict(record, stages=[])))
        self.assertEqual(BuildRecordStore(project).written_sha256(), {"board.tsx": "ab" * 32})
    def test_a_record_nested_too_deep_holds_no_sha256(self):
        project = Path(tempfile.mkdtemp())
        (project / ".spark").mkdir()
        (project / BUILD_RECORD_FILE).write_text("[" * 200000)
        self.assertEqual(BuildRecordStore(project).written_sha256(), {})

def a_project_built_with_no_simulation(code="board_not_in_wokwi", status="could-not-run"):
    """A built project whose board and build ended ok and whose simulation stage ended in `status` with `code`, as the
    p934 walk's FireBeetle 2 ESP32-C6 build records it (P977)."""
    project = a_built_project(status)
    record = BuildRecordStore(project).read()
    record["stages"] = [{"name": "board", "status": "ok"}, {"name": "build", "status": "ok"},
                        {"name": "simulation", "status": status, "code": code}]
    BuildRecordStore(project, clock=FakeClock()).write({key: value for key, value in record.items() if key not in ("schema", "at")})
    return project


def a_firmware(project):
    (project / "firmware").mkdir()
    (project / "firmware" / "main.py").write_text("print(1)\n")
    return project


# P977 review: the sentences the review asked for, and `now.by` a list (two jobs name the person and Claude)
NO_MODEL = "No simulation: Wokwi has no model of this board. You test it on the real board."


def a_run(project, verdict, image=b"an image"):
    """A run log in sim/runs/ that names `verdict` and the sha256 of `image`, as run_scenario.py writes its header."""
    (project / "sim" / "runs").mkdir(parents=True, exist_ok=True)
    (project / "sim" / "runs" / "one.log").write_text("verdict: %s\nimage sha256: %s\n\nwhat the board printed\n"
                                                       % (verdict, hashlib.sha256(image).hexdigest()))
    return project


def an_image(project, image=b"an image"):
    """sim/wokwi.toml naming sim/image.bin, which holds `image`, an hour after firmware/ was written."""
    (project / "sim").mkdir(exist_ok=True)
    (project / "sim" / "wokwi.toml").write_text('[wokwi]\nversion = 1\nfirmware = "image.bin"\n')
    (project / "sim" / "image.bin").write_bytes(image)
    for path in (project / "firmware").rglob("*"):
        os.utime(path, (1_700_000_000, 1_700_000_000))
    os.utime(project / "sim" / "image.bin", (1_700_003_600, 1_700_003_600))
    return project


class TheGuideTest(FlowTest):
    """P977: `data.guide` says what to do now, what is done, what comes later and what the person set aside."""

    def test_a_board_wokwi_has_no_model_of_passes_the_build_and_the_firmware_and_the_wiring_are_now(self):
        said, code = show(a_project_built_with_no_simulation())
        self.assertEqual((code, statuses(said)["build"], said["data"]["stands_at"]), (2, "could-not-run", "build"))
        self.assertEqual(said["data"]["guide"], {
            "now": {"phase": "firmware", "by": ["you", "claude"], "offer": None, "needs": [],
                    "says": "Two jobs, in any order: wire the breadboard (10 steps, power off), and ask Claude to write the "
                            "firmware. Spark cannot see your wiring."},
            "done": ["idea", "needs", "parts", "requirements", "build (no simulation)"],
            "later": ["simulate (no Wokwi model of this board)", "deploy"], "set_aside": [], "no_simulation": NO_MODEL})

    def test_a_sheet_whose_steps_cannot_be_counted_leaves_the_firmware_one_job_and_the_breadboard_done(self):
        project = a_project_built_with_no_simulation()
        phases, _ = read_flow(project)
        guide = guide_of(project, phases, steps=lambda _project: None)
        self.assertEqual((guide["now"]["phase"], guide["now"]["by"], guide["now"]["says"]),
                         ("firmware", ["claude"], "Ask Claude in the chat to write the firmware for this board."))
        self.assertIn("breadboard (spark cannot see it)", guide["done"])

    def test_with_the_firmware_written_the_deploy_is_now_and_the_simulate_stays_later(self):
        said, _ = show(a_firmware(a_project_built_with_no_simulation()))
        self.assertEqual(said["data"]["guide"], {
            "now": {"phase": "deploy", "by": ["your terminal"], "offer": None, "needs": [],
                    "says": "When the breadboard is wired, plug the board into USB. Ask Claude to look at it first, then "
                            "run the deploy in your terminal."},
            "done": ["idea", "needs", "parts", "requirements", "build (no simulation)", "breadboard (spark cannot see it)", "firmware"],
            "later": ["simulate (no Wokwi model of this board)"], "set_aside": [], "no_simulation": NO_MODEL})

    def test_any_other_cause_of_a_simulation_that_could_not_run_stops_at_the_build(self):
        for code in ("simulation_fact_missing", "converter_lacks_part", None):
            with self.subTest(code=code):
                guide = show(a_project_built_with_no_simulation(code))[0]["data"]["guide"]
                self.assertEqual((guide["now"]["phase"], guide["now"]["says"], guide["now"]["offer"], guide["no_simulation"]),
                                 ("build", "The build phase could not run. Ask Claude to read you why.", "build", None))
                self.assertEqual(guide["done"], ["idea", "needs", "parts", "requirements"])

    def test_a_board_only_build_of_a_board_wokwi_has_no_model_of_is_passed_and_the_firmware_is_one_job(self):
        project = a_board_only_project("could-not-run")
        record = BuildRecordStore(project).read()
        record["stages"][-1]["code"] = "board_not_in_wokwi"
        BuildRecordStore(project, clock=FakeClock()).write({key: value for key, value in record.items() if key not in ("schema", "at")})
        guide = show(project)[0]["data"]["guide"]
        self.assertEqual((guide["now"]["phase"], guide["now"]["says"]),
                         ("firmware", "Ask Claude in the chat to write the firmware for this board."))
        self.assertEqual(guide["done"], ["idea", "needs", "parts", "requirements", "build (no simulation)"])

    def test_a_build_of_a_board_wokwi_has_no_model_of_is_stale_when_the_parts_list_changed(self):
        project = a_project_built_with_no_simulation()
        (project / "requirements.json").write_text(json.dumps({"board": "xiao-esp32-c6-fresh", "parts": ["led-red-5mm"]}))
        guide = show(project)[0]["data"]["guide"]
        self.assertEqual((guide["now"]["phase"], guide["now"]["says"], guide["no_simulation"]),
                         ("build", "The parts list changed since the last build. Ask Claude to build again.", None))

    def test_a_simulation_with_problems_is_not_passed(self):
        guide = show(a_project_built_with_no_simulation("diagram_unwired", "problems"))[0]["data"]["guide"]
        self.assertEqual((guide["now"]["phase"], guide["now"]["says"]),
                         ("build", "The build phase has problems. Ask Claude to go through them with you."))

    def test_a_passed_build_with_a_simulate_that_has_problems_makes_the_simulate_now(self):
        project = a_firmware(a_project_built_with_no_simulation())
        (project / "sim").mkdir()
        (project / "sim" / "wokwi.toml").write_text('[wokwi]\nversion = 1\nfirmware = 42\n')
        guide = show(project)[0]["data"]["guide"]
        self.assertEqual((guide["now"]["phase"], guide["now"]["says"]),
                         ("simulate", "The simulate phase has problems. Ask Claude to go through them with you."))
        self.assertEqual((guide["later"], guide["no_simulation"]), (["deploy"], NO_MODEL))

    def test_an_image_no_run_tested_makes_the_simulate_now(self):
        project = a_firmware(a_built_project())
        (project / "sim").mkdir()
        (project / "sim" / "wokwi.toml").write_text('[wokwi]\nversion = 1\nfirmware = "image.bin"\n')
        (project / "sim" / "image.bin").write_bytes(b"an image")
        guide = show(project)[0]["data"]["guide"]
        self.assertEqual((guide["now"]["phase"], guide["now"]["by"], guide["now"]["says"]),
                         ("simulate", ["your terminal"], "Ask Claude for the scenario command, and run it in your terminal. "
                                                         "It uses Wokwi CI minutes."))
        self.assertEqual(guide["done"], ["idea", "needs", "parts", "requirements", "build", "breadboard (spark cannot see it)", "firmware"])

    def test_an_old_image_on_a_board_wokwi_has_no_model_of_is_counted_as_done(self):
        guide = show(an_image(a_firmware(a_project_built_with_no_simulation())))[0]["data"]["guide"]
        self.assertEqual((guide["now"]["phase"], guide["later"], guide["no_simulation"]),
                         ("deploy", ["simulate (no Wokwi model of this board)"], NO_MODEL))
        self.assertNotIn("simulate", guide["done"])

    def test_a_run_that_failed_on_the_image_has_its_own_sentence(self):
        guide = show(a_run(an_image(a_firmware(a_built_project())), "failed"))[0]["data"]["guide"]
        self.assertEqual((guide["now"]["phase"], guide["now"]["by"], guide["now"]["says"]),
                         ("simulate", ["claude"], "A run failed on this image (one.log). Ask Claude to go through its log with you."))

    def test_a_failed_run_beside_a_later_passed_run_is_named_and_keeps_the_simulate_open(self):
        project = a_run(an_image(a_firmware(a_built_project())), "failed")
        (project / "sim" / "runs" / "two.log").write_text("verdict: passed\nimage sha256: %s\n\n" % hashlib.sha256(b"an image").hexdigest())
        guide = show(project)[0]["data"]["guide"]
        self.assertEqual((guide["now"]["phase"], guide["now"]["says"]),
                         ("simulate", "A run failed on this image (one.log). Ask Claude to go through its log with you."))

    def test_firmware_changed_after_a_passed_run_leaves_the_simulate_open(self):
        project = a_run(an_image(a_firmware(a_built_project())), "passed")
        self.assertEqual(show(project)[0]["data"]["guide"]["now"]["phase"], "deploy")  # the run tested this image
        os.utime(project / "firmware" / "main.py", (1_700_007_200, 1_700_007_200))
        guide = show(project)[0]["data"]["guide"]
        self.assertEqual((guide["now"]["phase"], guide["now"]["by"], guide["now"]["says"]),
                         ("simulate", ["claude"], "Your firmware changed after the image. Ask Claude to make the image again, then run the scenario."))
        self.assertNotIn("simulate", guide["done"])

    def test_a_fresh_project_starts_at_the_idea(self):
        project = Path(tempfile.mkdtemp()) / "plant-alarm"
        project.mkdir()
        self.assertEqual(show(project)[0]["data"]["guide"], {
            "now": {"phase": "idea", "by": ["you"], "offer": None, "needs": [],
                    "says": "Tell Claude your goal in the chat, in your own words."},
            "done": [], "later": ["needs", "parts", "requirements", "build", "breadboard", "firmware", "simulate", "deploy"],
            "set_aside": [], "no_simulation": None})

    def test_needs_set_aside_do_not_count_and_a_picked_one_counts_as_picked(self):
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [
            {"id": "soil", "does": "sense", "what": "soil-moisture"},
            {"id": "wet", "does": "sense", "what": "soil-moisture", "aside": True},
            {"id": "dry", "does": "sense", "what": "soil-moisture", "aside": True, "pick": [{"part": "x-many"}]}])
        said, _ = show(project)
        self.assertEqual((statuses(said)["parts"], says(said, "parts")), ("partial", ["1 of 2 needs picked", "set aside: wet, dry"]))
        self.assertFalse([key for key in offers(said, "parts") if key.startswith("pick:wet:")])
        self.assertTrue([key for key in offers(said, "parts") if key.startswith("pick:dry:")])
        guide = said["data"]["guide"]
        self.assertEqual((guide["now"]["phase"], guide["now"]["by"], guide["now"]["needs"], guide["now"]["says"], guide["set_aside"]),
                         ("parts", ["you"], ["soil"], "1 need(s) have no part yet: soil. Tell Claude a pick for each, or to set it aside.",
                          ["wet", "dry"]))
        self.assertEqual(guide["done"], ["idea", "needs"])

    def test_every_need_picked_or_set_aside_makes_the_parts_ok_and_the_parts_list_now(self):
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [
            {"id": "soil", "does": "sense", "what": "soil-moisture", "pick": [{"part": "x-many"}]},
            {"id": "wet", "does": "sense", "what": "soil-moisture", "aside": True}])
        said, _ = show(project)
        self.assertEqual(statuses(said)["parts"], "ok")
        self.assertEqual((said["data"]["guide"]["now"]["phase"], said["data"]["guide"]["now"]["offer"], said["data"]["guide"]["now"]["says"]),
                         ("requirements", "requirements", "Ask Claude in the chat to write the parts list from your picks."))

    def test_the_build_record_keeps_the_code_of_a_stage_that_did_not_end_ok_and_no_detail(self):
        from spark.build import kept_files
        from spark.build.stages import Stage
        project = a_built_project()
        kept_files.keep_build_record(project, project / "requirements.json",
                                     [Stage("board", "ok"), Stage("simulation", "could-not-run", "/a/detail", "board_not_in_wokwi")], [])
        self.assertEqual(BuildRecordStore(project).read()["stages"], [
            {"name": "board", "status": "ok"}, {"name": "simulation", "status": "could-not-run", "code": "board_not_in_wokwi"}])


def offer_of(envelope, key):
    """The offer dict whose key is `key`, from any phase."""
    return next(offer for phase in envelope["data"]["phases"] for offer in phase["offers"] if offer["key"] == key)


SOIL = [{"id": "soil", "does": "sense", "what": "soil-moisture"}]
#: The three files a click changes, named here and not read from the module, so a file dropped there fails.
THREE_FILES = (Path(".spark") / "needs.json", Path("requirements.json"), Path(".spark") / "build.json")


class MakesStaleTest(FlowTest):
    """P829: an offer names only the phases it may make out of date that hold something now."""

    def test_with_no_requirements_json_a_pick_names_nothing(self):
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", SOIL)
        said, _ = show(project)
        self.assertEqual(offer_of(said, "pick:soil:x-many")["makes_stale"], [])
        self.assertEqual(offer_of(said, "requirements")["makes_stale"], [])

    def test_with_requirements_json_a_pick_names_the_requirements(self):
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", SOIL)
        (project / "requirements.json").write_text(json.dumps({"board": "xiao-esp32-c6", "parts": []}))
        said, _ = show(project)
        self.assertEqual(offer_of(said, "pick:soil:x-many")["makes_stale"], ["requirements"])
        self.assertEqual(offer_of(said, "build")["makes_stale"], [])

    def test_with_a_build_a_requirements_write_names_the_build_and_the_breadboard(self):
        said, _ = show(with_needs(a_built_project(), SOIL))
        self.assertEqual(offer_of(said, "requirements")["makes_stale"], ["build", "breadboard"])
        self.assertEqual(offer_of(said, "build")["makes_stale"], [])

    def test_a_refused_pick_and_a_drop_name_nothing(self):
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", SOIL)
        (project / "requirements.json").write_text(json.dumps({"board": "xiao-esp32-c6", "parts": []}))
        said, _ = show(project)
        self.assertEqual(offer_of(said, "pick:soil:x-held")["makes_stale"], [])
        self.assertEqual(offer_of(said, "needs-drop:soil")["makes_stale"], [])


class TheBuildOfferTest(FlowTest):
    """P829: the build offer names what the build writes, from the real run on a copy of button-light."""

    def test_a_build_names_its_files_and_that_it_runs_no_simulation(self):
        said, _ = show(a_built_project())
        build = offer_of(said, "build")
        self.assertEqual(build["label"], "Build the board")
        self.assertTrue(build["effect"].startswith("Saves its files in this project: the board file"))
        self.assertIn("the Wokwi drawing breadboard.json when Wokwi has a part for each part drawn", build["effect"])
        self.assertIn("If the board tool is not installed, the board is not built, and the old wiring sheet, drawings and this page "
                      "are deleted.", build["effect"])
        self.assertIn("If the parts list has a problem, the old wiring sheet, drawings, this page and the pin map are deleted.", build["effect"])
        self.assertTrue(build["effect"].endswith("Runs no simulation and costs nothing."))
        self.assertNotIn("history", build["effect"])

    def test_a_listed_project_notes_the_build_in_the_history(self):
        project = a_built_project()
        store.add_project(project)
        self.assertIn("Notes the build in your history.", offer_of(show(project)[0], "build")["effect"])

    def test_a_board_only_parts_list_says_dist_is_deleted_and_names_no_board_file(self):
        project = a_built_project()
        (project / "requirements.json").write_text(json.dumps({"board": "xiao-esp32-c6", "board_only": True, "parts": []}))
        effect = offer_of(show(project)[0], "build")["effect"]
        self.assertIn("This board needs no wiring, so the old dist folder is deleted.", effect)
        self.assertTrue(effect.startswith("This board needs no parts, so nothing is built or wired."))
        self.assertNotIn("board file", effect)


class TheReviewRoundTest(FlowTest):
    """P829's review: a broken list of projects keeps the build offer, and each pick sentence holds only when it is true."""

    def a_part(self, part, entry=None):
        """Put the soil probe `part` in the scratch catalog, and `entry` (a drawer entry's fields) in the drawer."""
        (self.home / "catalog" / (part + ".json")).write_text(json.dumps({"schema": 1, "id": part, "name": "A soil probe", "kind": "sensor",
                                                                         "function": [{"does": "sense", "what": "soil-moisture"}]}))
        if entry is not None:
            (self.home / "drawer" / (part + ".json")).write_text(json.dumps(dict({"schema": 1, "label": part, "is": {"part": part}}, **entry)))

    def test_a_broken_list_of_projects_keeps_the_build_offer_without_the_history(self):
        project = Path(tempfile.mkdtemp()) / "plant-alarm"
        project.mkdir()
        (project / "requirements.json").write_text(json.dumps({"board": "xiao-esp32-c6", "parts": []}))
        (self.home / "projects.json").write_text("{broken")
        said, _ = show(project)
        self.assertEqual(table(said)["build"], (NS, ["build"]))
        self.assertNotIn("history", offer_of(said, "build")["effect"])

    def test_a_part_you_own_none_of_goes_on_the_list_to_get(self):
        self.a_part("x-none")
        said, _ = show(with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", SOIL))
        effect = offer_of(said, "pick:soil:x-none")["effect"]
        self.assertIn("You have none, so it goes on the list to get.", effect)
        self.assertNotIn("Uses 1", effect)

    def test_a_pick_on_a_listed_project_does_not_list_it_again(self):
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", SOIL)
        self.assertIn("Adds this project to your list of projects.", offer_of(show(project)[0], "pick:soil:x-many")["effect"])
        store.add_project(project)
        self.assertNotIn("Adds this project", offer_of(show(project)[0], "pick:soil:x-many")["effect"])

    def test_a_pick_the_project_s_other_picks_leave_no_piece_for_is_refused(self):
        self.a_part("x-one", {"count": 1})
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [
            {"id": "soil", "does": "sense", "what": "soil-moisture", "pick": [{"part": "x-one"}]},
            {"id": "wet", "does": "sense", "what": "soil-moisture"}])
        said, _ = show(project)
        self.assertEqual(offer_of(said, "pick:wet:x-one")["effect"],
                         "Too few “A soil probe” are free for this pick (1 owned — 2 picked here), so spark refuses this pick and saves nothing.")
        self.assertEqual(offer_of(said, "pick:wet:x-one")["makes_stale"], [])
        self.assertIn("Uses 1 of your 1 “A soil probe” for the soil.", offer_of(said, "pick:soil:x-one")["effect"])

    def test_a_pick_is_refused_when_another_need_s_pick_cannot_get_its_part(self):
        self.a_part("x-one", {"count": 1, "used_in": {"other": 1}})
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [
            {"id": "soil", "does": "sense", "what": "soil-moisture", "pick": [{"part": "x-one"}]},
            {"id": "wet", "does": "sense", "what": "soil-moisture"}])
        said, _ = show(project)
        self.assertEqual(offer_of(said, "pick:wet:x-many")["effect"], "The pick for soil cannot get “x-one” (1 owned, held by other — 1 "
                                                                       "picked here), so spark refuses this pick and saves nothing.")
        self.assertNotIn("refuses", offer_of(said, "pick:soil:x-many")["effect"])

    def test_a_part_held_by_another_project_and_by_this_one_names_both_in_the_refusal(self):
        self.a_part("x-two", {"count": 2, "used_in": {"other": 1, "plant-alarm": 1}})
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [
            {"id": "soil", "does": "sense", "what": "soil-moisture", "pick": [{"part": "x-two"}]},
            {"id": "wet", "does": "sense", "what": "soil-moisture"}])
        said, _ = show(project)
        self.assertEqual(offer_of(said, "pick:wet:x-two")["effect"], "Too few “A soil probe” are free for this pick (2 owned, held by other — "
                                                                      "2 picked here), so spark refuses this pick and saves nothing.")

    def test_a_first_pick_frees_a_hold_given_by_hand_and_names_no_old_pick(self):
        (self.home / "drawer" / "many.json").write_text(json.dumps({"schema": 1, "label": "a bag of probes", "count": "many",
                                                                    "is": {"part": "x-many"}, "used_in": {"plant-alarm": 2}}))
        said, _ = show(with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", SOIL))
        effect = offer_of(said, "pick:soil:x-unknown")["effect"]
        self.assertIn("Frees a part this project held without a pick.", effect)
        self.assertNotIn("old pick", effect)

    def test_a_re_pick_frees_what_the_old_pick_held(self):
        (self.home / "drawer" / "many.json").write_text(json.dumps({"schema": 1, "label": "a bag of probes", "count": "many",
                                                                    "is": {"part": "x-many"}, "used_in": {"plant-alarm": 1}}))
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [
            {"id": "soil", "does": "sense", "what": "soil-moisture", "pick": [{"part": "x-many"}]}])
        said, _ = show(project)
        self.assertIn("Frees what the old pick held.", offer_of(said, "pick:soil:x-unknown")["effect"])
        self.assertNotIn("without a pick", offer_of(said, "pick:soil:x-unknown")["effect"])
        self.assertNotIn("Frees", offer_of(said, "pick:soil:x-many")["effect"])


class FingerprintTest(FlowTest):
    """P829: the fingerprint is the sha256 of the offers and the three files a click changes, and of nothing else."""

    def test_show_prints_the_fingerprint_of_the_flow(self):
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", SOIL)
        said, _ = show(project)
        self.assertEqual(said["data"]["fingerprint"], fingerprint_of(project, read_flow(project)[0]))
        self.assertRegex(said["data"]["fingerprint"], "^[0-9a-f]{64}$")

    def test_it_changes_when_any_one_of_the_three_files_changes(self):
        for name in THREE_FILES:
            with self.subTest(name=str(name)):
                project = Path(tempfile.mkdtemp())
                for each in THREE_FILES:
                    (project / each).parent.mkdir(parents=True, exist_ok=True)
                    (project / each).write_text("{}")
                before = fingerprint_of(project, [])
                (project / name).write_text('{"a": 1}')
                self.assertNotEqual(fingerprint_of(project, []), before)

    def test_a_missing_file_that_becomes_empty_changes_it(self):
        for name in THREE_FILES:
            with self.subTest(name=str(name)):
                project = Path(tempfile.mkdtemp())
                before = fingerprint_of(project, [])
                (project / name).parent.mkdir(parents=True, exist_ok=True)
                (project / name).write_text("")
                self.assertNotEqual(fingerprint_of(project, []), before)

    def test_it_changes_when_the_drawer_count_in_an_offer_changes(self):
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", SOIL)
        before = show(project)[0]["data"]["fingerprint"]
        (self.home / "drawer" / "many.json").write_text(json.dumps({"schema": 1, "label": "a bag of probes", "count": 3, "is": {"part": "x-many"}}))
        after = show(project)[0]
        self.assertIn("Uses 1 of your 3 “A soil probe” for the soil.", offer_of(after, "pick:soil:x-many")["effect"])
        self.assertNotEqual(after["data"]["fingerprint"], before)

    def test_no_other_file_changes_it(self):
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", SOIL)
        before = show(project)[0]["data"]["fingerprint"]
        (project / "firmware").mkdir()
        (project / "firmware" / "main.py").write_text("print('ready')\n")
        (project / "README.md").write_text("notes\n")
        (project / ".spark" / "page-request.json").write_text("{}")
        self.assertEqual(show(project)[0]["data"]["fingerprint"], before)


class TheRunOnButtonLightTest(unittest.TestCase):
    """P829: on a copy of button-light with a scratch store, a real pick and a real parts list turn out of date only the
    phases their offers named."""

    def setUp(self):
        home = Path(tempfile.mkdtemp())
        patcher = mock.patch.dict(os.environ, {"SPARK_HOME": str(home)})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.project = Path(tempfile.mkdtemp()) / "bl"
        shutil.copytree(ROOT / "tests" / "data" / "breadboard" / "button-light", self.project)
        with_needs(self.project, [{"id": "brain", "does": "compute", "what": "control"},
                                  {"id": "button", "does": "input", "what": "button"},
                                  {"id": "light", "does": "indicate", "what": "light"}])

    def turned_stale(self, operation, values, key):
        """(the phases that turned stale when `operation` ran with `values`, the makes_stale of the offer `key` before)."""
        before = show(self.project)[0]
        result = run_operation(operation, values, FakeOutsideWorld(clock=FakeClock()))
        self.assertEqual(result.status(), OK, result.lines)
        after = show(self.project)[0]
        turned = {phase for phase, status in statuses(after).items() if status == STALE and statuses(before)[phase] != STALE}
        return turned, set(offer_of(before, key)["makes_stale"])

    def test_a_pick_and_a_parts_list_make_stale_only_what_their_offers_name(self):
        picks = [str(self.project), "brain=xiao-esp32-c6", "button=tactile-button", "light=led-red-5mm"]  # another board than the file names
        turned, named = self.turned_stale(PickParts(), {"project_and_picks": picks, "passed_over": NO_PASSED_OVER, "dry_run": False},
                                          "pick:brain:xiao-esp32-c6")
        self.assertEqual(turned, {"requirements"})
        self.assertLessEqual(turned, named)
        (self.project / "breadboard.md").write_text("# the sheet\n")
        (self.project / "dist" / "board" / "built-from.json").write_text(json.dumps({"requirements": json.loads((self.project / "requirements.json").read_text())}))
        BuildRecordStore(self.project, clock=FakeClock()).write({"status": OK, "stages": [{"name": "build", "status": OK}], "missing_facts": [],
                                                                "requirements": "requirements.json",
                                                                "requirements_sha256": sha256_of(self.project / "requirements.json")})
        turned, named = self.turned_stale(WriteRequirements(), {"project": str(self.project), "dry_run": False, "replies": None}, "requirements")
        self.assertEqual(turned, {"build", "breadboard"})
        self.assertLessEqual(turned, named)


if __name__ == "__main__":
    unittest.main()
