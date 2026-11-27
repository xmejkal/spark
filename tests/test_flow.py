"""
The flow reader (P825, #1183): `flow.py show` says where a project stands, phase by phase, from the files the earlier
stages wrote, and offers the next steps as keys. On five projects (no needs, picked, built by hand with no needs, a build
that ended in could-not-run, requirements changed after the build) each test pins all nine phases' status and offer keys
from `flow.py show --json`, and `stands_at`. More tests pin one phase each.
It covers the area's modules `show_flow`, `phase_readers`, `deploy_reading` (P1043, the deploy phase) and `flow_codes`, and the
build record `build_record`.

    python3 -m unittest tests.test_flow
"""

import contextlib
import datetime
import hashlib
import io
import json
import os
import re
import shlex
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import flow  # noqa: E402
from fakes import FakeClock, FakeOutsideWorld, FakeTextFileWriter  # noqa: E402
from spark.build.build_record import BUILD_RECORD_FILE, EARLIER_DIST, BuildRecordStore, sha256_of  # noqa: E402
from spark.core import zone_time  # noqa: E402
from spark.flow.phase_readers import Offer, Phase, SimulateReader  # noqa: E402
from spark.flow import flow_codes  # noqa: E402
from spark.flow import flow_page, run_request  # noqa: E402
from spark.flow import deploy_reading  # noqa: E402
from spark.bench import board_log  # noqa: E402
from spark.flow.deploy_reading import DeployState  # noqa: E402
from spark.flow.guide import NO_IMAGE_FACT, ImageFact, chat_offer_of, guide_of, job_offer, names_at, requirements_now  # noqa: E402
from spark.flow.guide import stations_of, who_and_sentence  # noqa: E402
from spark.flow.show_flow import ShowFlow, flow_and_guide, read_flow  # noqa: E402
from spark.flow.fingerprint import fingerprint_of  # noqa: E402
from spark.core.cli import run_operation  # noqa: E402
from spark.core.outcomes import OK, PROBLEMS  # noqa: E402
from spark.design import needs  # noqa: E402
from spark.design.entry_origin import EntryOriginStore  # noqa: E402
from spark.design.pick_parts import NO_PASSED_OVER, PickParts  # noqa: E402
from spark.design.write_requirements import WriteRequirements  # noqa: E402
from spark.flow.flow_codes import LOOK_WHY, SCENARIO_FIRST_WHY, SCENARIO_WHY, SIM_FILES_NOW, STALE  # noqa: E402
from spark.flow.flow_codes import WIRED_BUILD_MESSAGE, WIRED_SHEET_MESSAGE, WIRED_STEP_MESSAGE  # noqa: E402
from spark.flow.wired_board import day_of  # noqa: E402
from spark.flow.phase_steps import SCENARIO_PLACEHOLDER  # noqa: E402
from spark.records import store  # noqa: E402
from spark.core.result import NextStep  # noqa: E402

#: A built project: requirements.json, the board it names and the circuit a finished build kept with its built-from.json.
BUILT = ROOT / "tests" / "data" / "breadboard" / "button-light-xiao"
PHASES = ["idea", "needs", "parts", "requirements", "build", "breadboard", "firmware", "simulate", "deploy"]
#: A value of a project's secrets file (P1060), MIN_SECRET characters or more, and a value whose file does not parse (D5).
SECRET, HALF_TYPED = "wifipass1234", "half-typed-value-31337"


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


def a_built_project(status="ok", stages=None, where=None):
    """A copy of the built fixture with its breadboard sheet and the record of a build that ended in `status`. `stages` are
    the record's {name: status}, in order (None: a board and a build that ended in `status`). `where` is the folder it is
    made in (None: the temp folder)."""
    project = Path(tempfile.mkdtemp(dir=where)) / "xiao"
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


def sheet_at(project):
    """The time of the project's breadboard.md, with its zone, as `data.guide.wired.sheet_at` holds it (P1044)."""
    return zone_time.stamp(datetime.datetime.fromtimestamp((project / "breadboard.md").stat().st_mtime))


def wired_line(project):
    """The parts phase's first line on a project whose only witness is its sheet (P1044)."""
    return " ".join((WIRED_SHEET_MESSAGE % day_of(sheet_at(project)), WIRED_STEP_MESSAGE))


def a_built_project_with_a_sheet_from(requirements):
    """A built project whose built-from.json names `requirements`."""
    project = a_built_project()
    (project / "dist" / "board" / "built-from.json").write_text(json.dumps({"requirements": requirements}))
    return project


NS = "not-started"
#: The says lines' close, and the a_store probe that smartbin-local holds, as a refused pick names it (P991 review).
LIST = " Claude can list them with parts.py --match."
HELD = "“A soil probe” (none free, held by smartbin-local)"
#: A project built by hand: requirements.json and no needs, its build and its sheet current, no firmware yet. Spark
#: compared the requirements with nothing and does not judge the wiring, so neither has a status (P878).
BUILT_TABLE = {"idea": (None, []), "needs": (None, []), "parts": (None, []), "requirements": (None, []), "build": ("ok", ["build"]),
               "breadboard": (None, []), "firmware": (NS, []), "simulate": (NS, []), "deploy": (NS, [])}


class FlowTest(unittest.TestCase):
    def setUp(self):
        # P1034: HOME is a folder of the test's own, so a test can put a project under the home folder (Path.home reads it)
        self.home, self.user_home = a_store(), Path(tempfile.mkdtemp())
        patcher = mock.patch.dict(os.environ, {"SPARK_HOME": str(self.home), "HOME": str(self.user_home)})
        patcher.start()
        self.addCleanup(patcher.stop)


class ThePhasesTest(FlowTest):
    def test_a_project_with_no_needs_stands_at_the_idea(self):
        project = Path(tempfile.mkdtemp()) / "plant-alarm"
        project.mkdir()
        said, code = show(project)
        self.assertEqual((code, said["status"], said["tool"], said["op"]), (0, "ok", "flow", "show-flow"))
        self.assertEqual([phase["phase"] for phase in said["data"]["phases"]], PHASES)
        self.assertEqual(table(said), {"idea": (None, []), "needs": (NS, []), "parts": (NS, []), "requirements": (NS, []),
                                       "build": (NS, []), "breadboard": (NS, []), "firmware": (NS, []), "simulate": (NS, []),
                                       "deploy": (NS, [])})
        self.assertEqual(said["data"]["stands_at"], "idea")  # P1030: the guide's now, the one rule
        self.assertEqual(says(said, "idea"), ["the brief holds no goal"])
        # P979: the hints name the command and who acts, with no placeholder and no path
        self.assertEqual(says(said, "firmware"), ["No firmware/main.py yet. Ask Claude to write it in the chat. Keep main.py "
                                                   "thin, with the code in modules it calls, so the free checks can import them."])
        self.assertEqual(says(said, "simulate"), ["No simulation files yet (sim/wokwi.toml). Ask Claude to build the board."])
        self.assertEqual(says(said, "deploy"), ["Ask Claude to look at the board first (/spark:deploy).",
                                                "Claude then gives you the deploy line. Run it in your terminal and type yes, unless you gave Claude a standing yes for this board."])
        self.assertEqual([phase["by"] for phase in said["data"]["phases"]],
                         ["you", "claude", "you", "claude", "claude", "you", "claude", "your terminal", "your terminal"])

    def test_a_project_with_one_of_two_needs_picked_offers_each_pick_with_what_it_does(self):
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [
            {"id": "soil", "does": "sense", "what": "soil-moisture", "pick": [{"part": "x-many"}]},
            {"id": "wet", "does": "sense", "what": "soil-moisture"}])
        said, code = show(project)
        self.assertEqual(code, 0)
        # P976 (the PO, 2026-11-21): no refused pick (x-held), not the current pick (x-many for soil), and nothing with
        # none of the need's words (the rangefinder) is offered.
        picks = ["pick:soil:x-unknown", "pick:wet:x-many", "pick:wet:x-unknown"]
        self.assertEqual(table(said), {"idea": (None, []), "needs": ("ok", ["needs-drop:soil", "needs-drop:wet"]), "parts": ("partial", picks),
                                       "requirements": (NS, []), "build": (NS, []), "breadboard": (NS, []),
                                       "firmware": (NS, []), "simulate": (NS, []), "deploy": (NS, [])})  # P993: no board is picked, so no parts list
        self.assertEqual(said["data"]["stands_at"], "parts")
        # P976: the refused pick is no offer; the says line counts it for each need. P991: the pick is named first, and the
        # review: a refused pick is named, with who holds it.
        self.assertEqual(says(said, "parts"), ["1 of 2 needs picked", "Picked for soil: “A soil probe”.",
                                               "Not shown for soil, refused: %s.%s" % (HELD, LIST),
                                               "Not shown for wet, refused: %s.%s" % (HELD, LIST)])
        effects = {offer["key"]: offer["effect"] for offer in said["data"]["phases"][2]["offers"]}
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

    def test_a_project_whose_last_need_was_dropped_says_so_and_is_no_hand_written_project(self):
        # P984: needs.json holds no need and requirements.json was written from picks: nothing was written by hand.
        project = with_needs(a_built_project(), [])
        said, code = show(project)
        self.assertEqual(code, 0)
        self.assertEqual(says(said, "needs"), ["no need is left: the last one was dropped"])
        # P1044: the fixture keeps a sheet, so the parts phase's first line is the wired line
        self.assertEqual(says(said, "parts"), [wired_line(project), "no need or pick is behind the parts list"])
        self.assertEqual(table(said), BUILT_TABLE)

    def test_a_build_that_could_not_run_says_so_and_exits_2(self):
        said, code = show(a_built_project("could-not-run"))
        self.assertEqual((code, said["status"]), (2, "could-not-run"))
        self.assertEqual(table(said), dict(BUILT_TABLE, build=("could-not-run", ["build"])))
        self.assertEqual(said["data"]["stands_at"], "build")
        self.assertEqual([(item["subject"], item["code"]) for item in said["unchecked"]], [("build", "phase_could_not_run")])
        self.assertIn("build: could-not-run", says(said, "build"))

    def test_a_build_that_did_not_write_dist_says_so_in_the_build_phase(self):
        # P1088: the record's dist_written false (P816) over a dist/ that is there names it as an earlier build's
        project = a_built_project("could-not-run")
        BuildRecordStore(project, clock=FakeClock()).write({"status": "could-not-run", "stages": [{"name": "board", "status": "ok"}, {"name": "build", "status": "could-not-run"}],
                                                           "missing_facts": [], "requirements": "requirements.json",
                                                           "requirements_sha256": sha256_of(project / "requirements.json"), "dist_written": False})
        self.assertTrue((project / "dist").is_dir())
        said, _ = show(project)
        self.assertIn(EARLIER_DIST % BuildRecordStore(project).read()["at"], says(said, "build"))
        said, _ = show(a_built_project())
        self.assertEqual([line for line in says(said, "build") if "did not write dist/" in line], [])

    def test_a_reference_build_says_so_in_the_build_phase(self):
        # P1095: a record with requirements null is the reference design's build, not one of requirements.json
        project = a_built_project()
        BuildRecordStore(project, clock=FakeClock()).write({"status": "ok", "stages": [{"name": "board", "status": "ok"}, {"name": "build", "status": "ok"}],
                                                           "missing_facts": [], "requirements": None, "requirements_sha256": None})
        said, _ = show(project)
        self.assertEqual(statuses(said)["build"], STALE)
        self.assertEqual(says(said, "build")[0], "the last build was spark's reference design, not requirements.json")

    def test_a_record_without_the_requirements_key_is_read_as_built_from_requirements_json(self):
        # P1095: only a record that holds requirements null is the reference design's; one that lacks the key keeps the old reading
        project = a_built_project()
        BuildRecordStore(project, clock=FakeClock()).write({"status": "ok", "stages": [{"name": "board", "status": "ok"}, {"name": "build", "status": "ok"}],
                                                           "missing_facts": []})
        said, _ = show(project)
        self.assertEqual(says(said, "build")[0], "requirements.json changed after the build")

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
        # P979: the untested sentence is the flow's own, keyed on the fact, and the scenario hint has no placeholder
        self.assertEqual(says(said, "simulate"), [
            "No run tested this image yet. To skip the simulation, ask Claude to deploy firmware/ untested.",
            "Ask Claude for the scenario command, and run it in your terminal. It uses Wokwi CI minutes."])
        self.assertIsNone(statuses(said)["simulate"])

    def test_a_run_that_failed_on_the_image_keeps_the_library_s_sentence(self):
        # P979: only an image no run named gets the flow's own untested sentence
        project = a_built_project()
        (project / "sim" / "runs").mkdir(parents=True)
        (project / "sim" / "wokwi.toml").write_text('[wokwi]\nversion = 1\nfirmware = "image.bin"\n')
        (project / "sim" / "image.bin").write_bytes(b"an image")
        (project / "sim" / "runs" / "a.log").write_text(
            "# a.log\nverdict: failed (wokwi-cli exit 1)\nimage sha256: %s\nbody\n" % hashlib.sha256(b"an image").hexdigest())
        said, _ = show(project)
        self.assertIn("did not pass on this image", says(said, "simulate")[0])

    def test_an_image_that_is_not_there_says_two_sentences_and_the_page_holds_no_placeholder(self):
        # P979: str(missing) was the library's sentence, with <store>, <project> and a script path
        from spark.flow.write_flow_page import FlowPageStore, write_page
        project = a_built_project()
        (project / "sim").mkdir()
        (project / "sim" / "wokwi.toml").write_text('[wokwi]\nversion = 1\nfirmware = "image.bin"\n')
        said, _ = show(project)
        self.assertEqual(statuses(said)["simulate"], NS)
        self.assertEqual(says(said, "simulate"), [
            "No firmware image yet. The scenario run makes one. To skip the simulation, ask Claude to deploy firmware/ untested.",
            "Ask Claude for the scenario command, and run it in your terminal. It uses Wokwi CI minutes."])
        with mock.patch.dict(os.environ, {"SPARK_HOME": tempfile.mkdtemp()}):
            write_page(project, store=FlowPageStore())
        text = (project / "page.html").read_text(encoding="utf-8")
        for placeholder in ("${", "&lt;store&gt;", "&lt;project&gt;", "&lt;name&gt;", "SPARK_HOME"):
            self.assertNotIn(placeholder, text)

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
        self.assertIn("NOW (idea)", out.getvalue())  # P1030: the guide's lines, in place of the stands-at line

    def test_the_lines_leave_ok_to_the_mark_and_show_five_offer_keys_and_how_many_more(self):
        project = with_needs(a_built_project(), [
            {"id": "soil", "does": "sense", "what": "soil-moisture", "pick": [{"part": "x-many"}]},
            {"id": "wet", "does": "sense", "what": "soil-moisture"}, {"id": "damp", "does": "sense", "what": "soil-moisture"},
            {"id": "dry", "does": "sense", "what": "soil-moisture"}])
        with contextlib.redirect_stdout(io.StringIO()) as out:
            flow.main(["show", "--project", str(project)])
        lines = out.getvalue().splitlines()
        self.assertIn("  ✓ needs: 4 need(s): soil, wet, damp, dry (claude)", lines)
        # P976: no refused pick (x-held) and not the current one (x-many for soil), so four needs make seven offers
        self.assertIn("      offers: pick:soil:x-unknown, pick:wet:x-many, pick:wet:x-unknown, pick:damp:x-many, pick:damp:x-unknown, "
                      "+2 more", lines)

    def test_the_data_keys_are_a_real_answer_s_keys(self):
        project = Path(tempfile.mkdtemp()) / "plant-alarm"
        project.mkdir()
        self.assertEqual(sorted(show(project)[0]["data"]), sorted(ShowFlow.data_keys))

    def test_the_answer_names_no_home_path(self):
        # P979: the no-sim sentence no longer holds the project's path, so an unreadable log (its sentence names the path) keeps this test on a masked one
        project = a_built_project()
        (project / "sim" / "runs").mkdir(parents=True)
        (project / "sim" / "wokwi.toml").write_text('[wokwi]\nversion = 1\nfirmware = "image.bin"\n')
        (project / "sim" / "image.bin").write_bytes(b"an image")
        log = project / "sim" / "runs" / "a.log"
        log.write_text("")
        log.chmod(0)
        self.addCleanup(log.chmod, 0o600)
        said, _ = show(project)
        self.assertNotIn(str(Path.home()), json.dumps(said))
        self.assertNotIn(str(project), json.dumps(said))
        self.assertIn("cannot read sim/runs/a.log: [Errno 13]", json.dumps(said))  # the project's path is cut off the front (P979: `<project>` no longer appears)


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


def a_project_built_with_no_simulation_now():
    """The same build as a_project_built_with_no_simulation's, recorded as the build ends it since P1207 (D11): the
    simulation stage skipped with board_not_in_wokwi, and the record ok."""
    project = a_built_project()
    record = BuildRecordStore(project).read()
    record["stages"] = [{"name": "board", "status": "ok"}, {"name": "build", "status": "ok"},
                        {"name": "simulation", "status": "skipped", "code": "board_not_in_wokwi"}]
    BuildRecordStore(project, clock=FakeClock()).write({key: value for key, value in record.items() if key not in ("schema", "at")})
    return project


def a_firmware(project):
    (project / "firmware").mkdir()
    (project / "firmware" / "main.py").write_text("print(1)\n")
    return project


# P980: a project with no needs behind its requirements.json lists no needs or parts as done: the five tests below that
# build a hand-written project say `requirements (no needs or picks behind it)` in `done`, on purpose.
# P977 review: the sentences the review asked for, and `now.by` a list (two jobs name the person and Claude)
NO_MODEL = "No simulation: Wokwi has no model of this board. You test it on the real board."
#: P1209: the guide's `check` of a project with no check record, and the line of firmware with no record.
NO_CHECK = {"name": "check-firmware", "state": "none-recorded", "why": None, "at": None, "current": None, "status": None,
            "data": None, "lines": None, "inputs": None}
NOT_RUN_YET = "Free checks: not run yet. Ask Claude to run them, for free."


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


def stations(*rows):
    """The guide's `stations` (P1119) from (phase, place, note) rows."""
    return [{"phase": phase, "place": place, "note": note} for phase, place, note in rows]


class TheGuideTest(FlowTest):
    """P977: `data.guide` says what to do now, what is done, what comes later and what the person set aside."""

    def test_a_board_wokwi_has_no_model_of_passes_the_build_and_the_firmware_and_the_wiring_are_now(self):
        project = a_project_built_with_no_simulation()
        said, code = show(project)
        self.assertEqual((code, statuses(said)["build"], said["data"]["stands_at"]), (2, "could-not-run", "firmware"))  # P1030: the guide's now
        # P977 PR 2: now holds `steps`, the wiring's step count while the wiring is part of now, else None.
        self.assertEqual(said["data"]["guide"], {
            "now": {"phase": "firmware", "by": ["you", "claude"], "offer": None, "chat_offer": "write-firmware", "needs": [], "steps": 10,
                    "with_wiring": True,
                    "says": "Two jobs, in any order: wire the breadboard (10 steps, power off), and ask Claude to write the "
                            "firmware. Spark cannot see your wiring."},
            "done": ["idea", "requirements (no needs or picks behind it)", "build (no simulation)"],
            "later": ["simulate (no Wokwi model of this board)", "deploy"], "set_aside": [], "no_simulation": NO_MODEL,
            "simulation": {"line": NO_MODEL, "grey": True, "check": NO_CHECK},  # P1209: no firmware and no check record
            "no_open_phase": None, "wired": {"sheet_at": sheet_at(project), "deploy_at": None},  # P1044: the fixture keeps a sheet
            "gate_a": None,  # P1220: no board log yet
            # P1119: the two jobs: the breadboard is now beside the firmware, so it is in no list
            "stations": stations(("idea", "done", None), ("needs", "done", "not-done"), ("parts", "done", "not-done"),
                                 ("requirements", "done", "no-picks"), ("build", "done", "no-model"), ("breadboard", "now", None),
                                 ("firmware", "now", None), ("simulate", "later", "no-model"), ("deploy", "later", None))})

    def test_a_new_record_of_a_board_wokwi_has_no_model_of_gives_the_same_guide_and_exits_0(self):
        """P1207 (D11): the build now ends the simulation stage skipped with board_not_in_wokwi and the record ok. The guide
        is the old record's, `flow.py show` exits 0, and the build phase says why there is no simulation."""
        old, new = a_project_built_with_no_simulation(), a_project_built_with_no_simulation_now()
        (said, code), old_guide = show(new), show(old)[0]["data"]["guide"]
        guide = said["data"]["guide"]
        self.assertEqual(guide.pop("wired"), {"sheet_at": sheet_at(new), "deploy_at": None})  # each fixture keeps its own sheet
        old_guide.pop("wired")
        self.assertEqual(guide, old_guide)
        self.assertEqual((code, statuses(said)["build"], said["data"]["stands_at"]), (0, None, "firmware"))
        self.assertEqual(says(said, "build")[-1], "No simulation: Wokwi has no model of this board. You test it on the real board.")

    def test_a_new_board_only_record_of_a_board_wokwi_has_no_model_of_is_done_once_with_the_board_only_sentence(self):
        project = a_built_project(OK, {"board": "ok", "parts": "skipped", "schematic": "skipped", "footprint": "skipped",
                                       "build": "skipped", "simulation": "skipped"})
        (project / "breadboard.md").unlink()
        record = BuildRecordStore(project).read()
        record["stages"][-1]["code"] = "board_not_in_wokwi"
        BuildRecordStore(project, clock=FakeClock()).write({key: value for key, value in record.items() if key not in ("schema", "at")})
        said, code = show(project)
        guide = said["data"]["guide"]
        self.assertEqual((code, guide["now"]["phase"], guide["no_simulation"]), (0, "firmware", NO_MODEL))
        self.assertEqual(guide["done"], ["idea", "requirements (no needs or picks behind it)", "build (no simulation)"])
        self.assertEqual(says(said, "build"), ["board only: nothing to wire, no board was built"])

    def test_the_project_stands_where_the_guide_says_now(self):
        """P1030: one rule says where a project stands, the guide's now phase, in data.stands_at too."""
        empty = Path(tempfile.mkdtemp()) / "plant-alarm"
        empty.mkdir()
        for project in (empty, with_needs(Path(tempfile.mkdtemp()) / "soil", SOIL), a_built_project(), a_project_built_with_no_simulation(),
                        a_firmware(a_project_built_with_no_simulation())):
            with self.subTest(project=project.name):
                said = show(project)[0]
                self.assertEqual(said["data"]["stands_at"], said["data"]["guide"]["now"]["phase"])

    def test_a_sheet_whose_steps_cannot_be_counted_leaves_the_firmware_one_job_and_the_breadboard_done(self):
        project = a_project_built_with_no_simulation()
        phases, _ = read_flow(project)
        guide = guide_of(project, phases, steps=lambda _project: None)
        self.assertEqual((guide["now"]["phase"], guide["now"]["by"], guide["now"]["says"]),
                         ("firmware", ["claude"], "Ask Claude in the chat to write the firmware for this board. Keep main.py thin, "
                          "with the code in modules it calls, so the free checks can import them."))
        self.assertIn("breadboard (spark cannot see it)", guide["done"])

    def test_with_the_firmware_written_the_deploy_is_now_and_the_simulate_stays_later(self):
        project = a_firmware(a_project_built_with_no_simulation())
        said, _ = show(project)
        self.assertEqual(said["data"]["guide"], {
            "now": {"phase": "deploy", "by": ["your terminal"], "offer": None, "chat_offer": "look-at-board", "needs": [], "steps": None,
                    "with_wiring": True,
                    "says": "When the breadboard is wired, plug the board into USB. Ask Claude to look at it first, then "
                            "run the deploy in your terminal."},
            "done": ["idea", "requirements (no needs or picks behind it)", "build (no simulation)", "breadboard (spark cannot see it)", "firmware"],
            "later": ["simulate (no Wokwi model of this board)"], "set_aside": [], "no_simulation": NO_MODEL, "no_open_phase": None,
            "simulation": {"line": NOT_RUN_YET + " " + NO_MODEL, "grey": False, "check": NO_CHECK},  # P1209: firmware, no record
            "wired": {"sheet_at": sheet_at(project), "deploy_at": None},  # P1044: the fixture keeps a sheet
            "gate_a": {"shut_by": [], "fact": "no-model", "says": "No simulator run: none covers this board."},  # P1220: the deploy is now
            # P1119: a simulate with no model is later, though it stands before the deploy now
            "stations": stations(("idea", "done", None), ("needs", "done", "not-done"), ("parts", "done", "not-done"),
                                 ("requirements", "done", "no-picks"), ("build", "done", "no-model"), ("breadboard", "done", "unseen"),
                                 ("firmware", "done", None), ("simulate", "later", "no-model"), ("deploy", "now", None))})

    def test_any_other_cause_of_a_simulation_that_could_not_run_stops_at_the_build(self):
        for code in ("simulation_fact_missing", "converter_lacks_part", None):
            with self.subTest(code=code):
                guide = show(a_project_built_with_no_simulation(code))[0]["data"]["guide"]
                self.assertEqual((guide["now"]["phase"], guide["now"]["says"], guide["now"]["offer"], guide["no_simulation"]),
                                 ("build", "The build phase could not run. Ask Claude to read you why.", "build", None))
                self.assertEqual(guide["done"], ["idea", "requirements (no needs or picks behind it)"])

    def test_a_board_only_build_of_a_board_wokwi_has_no_model_of_is_passed_and_the_firmware_is_one_job(self):
        project = a_board_only_project("could-not-run")
        record = BuildRecordStore(project).read()
        record["stages"][-1]["code"] = "board_not_in_wokwi"
        BuildRecordStore(project, clock=FakeClock()).write({key: value for key, value in record.items() if key not in ("schema", "at")})
        guide = show(project)[0]["data"]["guide"]
        self.assertEqual((guide["now"]["phase"], guide["now"]["says"]),
                         ("firmware", "Ask Claude in the chat to write the firmware for this board. Keep main.py thin, with the "
                          "code in modules it calls, so the free checks can import them."))
        self.assertEqual(guide["done"], ["idea", "requirements (no needs or picks behind it)", "build (no simulation)"])

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
        (project / "sim" / "scenarios").mkdir(parents=True)
        (project / "sim" / "scenarios" / "a.scenario.yaml").write_text("name: a\n")  # P1034: with none, Claude writes one first
        (project / "sim" / "wokwi.toml").write_text('[wokwi]\nversion = 1\nfirmware = "image.bin"\n')
        (project / "sim" / "image.bin").write_bytes(b"an image")
        guide = show(project)[0]["data"]["guide"]
        self.assertEqual((guide["now"]["phase"], guide["now"]["by"], guide["now"]["says"]),
                         ("simulate", ["your terminal"], "Ask Claude for the scenario command, and run it in your terminal. "
                                                         "It uses Wokwi CI minutes."))
        self.assertEqual(guide["done"], ["idea", "requirements (no needs or picks behind it)", "build", "breadboard (spark cannot see it)", "firmware"])

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
            "now": {"phase": "idea", "by": ["you"], "offer": None, "chat_offer": None, "needs": [], "steps": None, "with_wiring": False,
                    "says": "Tell Claude your goal in the chat, in your own words."},
            "done": [], "later": ["needs", "parts", "requirements", "build", "breadboard", "firmware", "simulate", "deploy"],
            "set_aside": [], "no_simulation": None, "no_open_phase": None, "wired": None,  # P1044: no sheet and no board log
            "simulation": {"line": None, "grey": False, "check": NO_CHECK},  # P1209: nothing to say
            "gate_a": None,  # P1220
            "stations": stations(("idea", "now", None), *[(phase, "later", None) for phase in PHASES[1:]])})  # P1119

    def test_needs_set_aside_do_not_count_and_a_picked_one_counts_as_picked(self):
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [
            {"id": "soil", "does": "sense", "what": "soil-moisture"},
            {"id": "wet", "does": "sense", "what": "soil-moisture", "aside": True},
            {"id": "dry", "does": "sense", "what": "soil-moisture", "aside": True, "pick": [{"part": "x-many"}]}])
        said, _ = show(project)
        # P976: the refused pick (x-held) of each need with offers is counted in its own line. P991: a pick is named first.
        self.assertEqual((statuses(said)["parts"], says(said, "parts")), ("partial", [
            "1 of 2 needs picked", "set aside: wet, dry", "Not shown for soil, refused: %s.%s" % (HELD, LIST),  # P991 review: named
            "Picked for dry: “A soil probe”.", "Not shown for dry, refused: %s.%s" % (HELD, LIST)]))
        self.assertFalse([key for key in offers(said, "parts") if key.startswith("pick:wet:")])
        self.assertTrue([key for key in offers(said, "parts") if key.startswith("pick:dry:")])
        guide = said["data"]["guide"]
        self.assertEqual((guide["now"]["phase"], guide["now"]["by"], guide["now"]["needs"], guide["now"]["says"], guide["set_aside"]),
                         ("parts", ["you"], ["soil"], "1 need has no part yet: soil. Tell Claude a pick for each, or to set it aside.",
                          ["wet", "dry"]))
        self.assertEqual(guide["done"], ["idea", "needs"])

    def test_several_needs_with_no_pick_are_a_counted_plural(self):
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [
            {"id": "soil", "does": "sense", "what": "soil-moisture"}, {"id": "pump", "does": "move", "what": "water"},
            {"id": "led", "does": "indicate", "what": "light"}])
        self.assertEqual(show(project)[0]["data"]["guide"]["now"]["says"],
                         "3 needs have no part yet: soil, pump, led. Tell Claude a pick for each, or to set it aside.")

    def test_every_need_picked_or_set_aside_makes_the_parts_ok_and_the_parts_list_now(self):
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [
            {"id": "board", "does": "compute", "what": "microcontroller", "pick": [{"board": "xiao-esp32-c6"}]},
            {"id": "wet", "does": "sense", "what": "soil-moisture", "aside": True}])  # P993: a pick the parts list takes
        said, _ = show(project)
        self.assertEqual(statuses(said)["parts"], "ok")
        self.assertEqual((said["data"]["guide"]["now"]["phase"], said["data"]["guide"]["now"]["offer"], said["data"]["guide"]["now"]["says"]),
                         ("requirements", "requirements", "Ask Claude in the chat to write the parts list from your picks."))

    def test_a_hand_written_project_lists_no_needs_or_parts_as_done(self):
        project = a_built_project()
        phases, _ = read_flow(project)
        guide = guide_of(project, phases, steps=lambda _project: None)
        self.assertEqual((guide["now"]["phase"], guide["done"]),
                         ("firmware", ["idea", "requirements (no needs or picks behind it)", "build", "breadboard (spark cannot see it)"]))

    def test_a_project_whose_last_need_was_dropped_lists_no_needs_or_parts_as_done(self):
        project = with_needs(a_built_project(), [])
        phases, _ = read_flow(project)
        guide = guide_of(project, phases, steps=lambda _project: None)
        self.assertEqual((guide["now"]["phase"], guide["done"]),
                         ("firmware", ["idea", "requirements (no needs or picks behind it)", "build", "breadboard (spark cannot see it)"]))

    def test_every_need_set_aside_with_a_requirements_file_that_cannot_be_read_keeps_the_requirements_now(self):
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [
            {"id": "soil", "does": "sense", "what": "soil-moisture", "aside": True}])
        (project / "requirements.json").write_text("{not json")
        said, _ = show(project)
        self.assertEqual((statuses(said)["requirements"], said["data"]["guide"]["now"]["phase"]), ("could-not-run", "requirements"))

    def test_every_need_set_aside_makes_the_parts_now_and_not_the_parts_list(self):
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [
            {"id": "soil", "does": "sense", "what": "soil-moisture", "aside": True},
            {"id": "wet", "does": "sense", "what": "soil-moisture", "aside": True}])
        guide = show(project)[0]["data"]["guide"]
        self.assertEqual(guide["now"], {
            "phase": "parts", "by": ["you"], "offer": None, "chat_offer": None, "needs": [], "steps": None, "with_wiring": False,
            "says": "Every need is set aside, so no pick can make the parts list. Tell Claude which need to bring back, "
                    "then pick a part."})
        self.assertEqual((guide["done"], guide["later"], guide["set_aside"]), (
            ["idea", "needs"], ["requirements", "build", "breadboard", "firmware", "simulate", "deploy"], ["soil", "wet"]))

    def test_the_build_record_keeps_the_code_of_a_stage_that_did_not_end_ok_and_no_detail(self):
        from spark.build import kept_files
        from spark.build.stages import Stage
        project = a_built_project()
        kept_files.keep_build_record(project, project / "requirements.json",
                                     [Stage("board", "ok"), Stage("simulation", "could-not-run", "/a/detail", "board_not_in_wokwi")], [])
        self.assertEqual(BuildRecordStore(project).read()["stages"], [
            {"name": "board", "status": "ok"}, {"name": "simulation", "status": "could-not-run", "code": "board_not_in_wokwi"}])


def phases_of(*rows):
    """Phases from (phase, status) rows, with no offers."""
    return [Phase(phase, status, None, "you", [], []) for phase, status in rows]


#: Nine phases whose every status is ok, which a guide with no now gives (P1119).
ALL_OK = phases_of(*[(phase, OK) for phase in PHASES])


class TheStationsTest(unittest.TestCase):
    """P1119: `stations` places each phase the guide is given beside the now, with at most one note, and DONE and LATER are
    built from it: a phase with a note of `LEFT_OUT_NOTES` is in no list."""

    def lists(self, rows):
        return names_at(rows, "done"), names_at(rows, "later")

    def test_with_no_now_every_phase_is_done_but_a_simulate_with_no_model(self):
        rows = stations_of(ALL_OK, len(ALL_OK), {"simulate"}, None)
        self.assertEqual([(row["place"], row["note"]) for row in rows],
                         [("done", None)] * 5 + [("done", "no-sheet"), ("done", None), ("later", "no-model"), ("done", None)])
        self.assertEqual(self.lists(rows), (["idea", "needs", "parts", "requirements", "build", "firmware", "deploy"],
                                            ["simulate (no Wokwi model of this board)"]))

    def test_a_simulate_with_no_model_before_a_deploy_now_is_later(self):
        rows = stations_of(ALL_OK, PHASES.index("deploy"), {"build", "simulate"}, "done")
        self.assertEqual(rows[4:], stations(("build", "done", "no-model"), ("breadboard", "done", "unseen"), ("firmware", "done", None),
                                            ("simulate", "later", "no-model"), ("deploy", "now", None)))
        self.assertEqual(self.lists(rows), (["idea", "needs", "parts", "requirements", "build (no simulation)",
                                             "breadboard (spark cannot see it)", "firmware"],
                                            ["simulate (no Wokwi model of this board)"]))

    def test_the_two_jobs_make_the_breadboard_now_beside_the_firmware_with_no_note(self):
        rows = stations_of(ALL_OK, PHASES.index("firmware"), set(), "now")
        self.assertEqual(rows[5:7], stations(("breadboard", "now", None), ("firmware", "now", None)))
        done, later = self.lists(rows)
        self.assertEqual(done, ["idea", "needs", "parts", "requirements", "build"])
        self.assertNotIn("breadboard", " ".join(done + later))

    def test_a_breadboard_before_now_with_no_current_sheet_is_in_no_list(self):
        rows = stations_of(ALL_OK, PHASES.index("firmware"), set(), None)
        self.assertEqual(rows[5], {"phase": "breadboard", "place": "done", "note": "no-sheet"})
        self.assertNotIn("breadboard", self.lists(rows)[0])

    def test_no_picks_is_given_only_before_now(self):
        before = stations_of(ALL_OK, PHASES.index("build"), set(), None, no_picks=True)
        self.assertEqual(before[1:4], stations(("needs", "done", "not-done"), ("parts", "done", "not-done"),
                                               ("requirements", "done", "no-picks")))
        self.assertEqual(self.lists(before)[0], ["idea", "requirements (no needs or picks behind it)"])
        after = stations_of(phases_of(*[(phase, None) for phase in PHASES]), 0, set(), None, no_picks=True)
        self.assertEqual({row["note"] for row in after}, {None})
        self.assertEqual(self.lists(after)[1], PHASES[1:])

    def test_a_later_phase_that_is_ok_may_change_and_one_not_ok_has_no_note(self):
        rows = stations_of(phases_of(("one", "not-started"), ("two", OK), ("three", "not-started")), 0, set(), None)
        self.assertEqual(rows, stations(("one", "now", None), ("two", "later", "may-change"), ("three", "later", None)))
        self.assertEqual(self.lists(rows), ([], ["two (done, may change)", "three"]))

    def test_the_stations_follow_the_phases_the_guide_is_given_in_their_order(self):
        rows = stations_of(phases_of(("b", OK), ("a", None)), 2, set(), None)
        self.assertEqual(rows, stations(("b", "done", None), ("a", "done", None)))


def offer_of(envelope, key):
    """The offer dict whose key is `key`, from any phase."""
    return next(offer for phase in envelope["data"]["phases"] for offer in phase["offers"] if offer["key"] == key)


SOIL = [{"id": "soil", "does": "sense", "what": "soil-moisture"}]
#: A board need with a board of spark's library picked: with it the parts list's own rule refuses nothing (P993).
BOARD = [{"id": "board", "does": "compute", "what": "microcontroller", "pick": [{"board": "xiao-esp32-c6"}]}]
#: The three files a click changes, named here and not read from the module, so a file dropped there fails.
THREE_FILES = (Path(".spark") / "needs.json", Path("requirements.json"), Path(".spark") / "build.json")


class MakesStaleTest(FlowTest):
    """P829: an offer names only the phases it may make out of date that hold something now."""

    def test_with_no_requirements_json_a_pick_names_nothing(self):
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", SOIL + BOARD)  # P993: the parts list is offered
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
        said, _ = show(with_needs(a_built_project(), SOIL + BOARD))  # P993: the parts list is offered
        self.assertEqual(offer_of(said, "requirements")["makes_stale"], ["build", "breadboard"])
        self.assertEqual(offer_of(said, "build")["makes_stale"], [])

    def test_a_refused_pick_and_a_drop_name_nothing(self):
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", SOIL)
        (project / "requirements.json").write_text(json.dumps({"board": "xiao-esp32-c6", "parts": []}))
        said, _ = show(project)
        # P976: a refused pick is no longer an offer, so it names nothing; the says line counts it
        self.assertNotIn("pick:soil:x-held", offers(said, "parts"))
        self.assertEqual(offer_of(said, "needs-drop:soil")["makes_stale"], [])


class TheOfferKindsTest(FlowTest):
    """P1115's done-when: every offer the readers give is of a kind of the one table, here a literal set."""

    def test_every_offer_of_the_fixture_projects_is_of_a_known_kind(self):
        idea = Path(tempfile.mkdtemp()) / "plant-alarm"
        idea.mkdir()
        picked = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [
            {"id": "soil", "does": "sense", "what": "soil-moisture", "pick": [{"part": "x-many"}]},
            {"id": "wet", "does": "sense", "what": "soil-moisture"}])
        listed = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [
            {"id": "board", "does": "compute", "what": "microcontroller", "pick": [{"board": "xiao-esp32-c6"}]}])
        (listed / "requirements.json").write_text(json.dumps({"board": "firebeetle2-esp32s3", "parts": []}))
        kinds = {offer["key"].split(":", 1)[0] for project in (idea, picked, listed, a_built_project(), a_built_project("could-not-run"))
                 for phase in show(project)[0]["data"]["phases"] for offer in phase["offers"]}
        self.assertEqual(kinds, {"pick", "needs-drop", "requirements", "build"})


class TheBuildOfferTest(FlowTest):
    """P829: the build offer names what the build writes, from the real run on a copy of button-light."""

    def test_a_build_names_its_files_and_that_it_runs_no_simulation(self):
        said, _ = show(a_built_project())
        build = offer_of(said, "build")
        self.assertEqual(build["label"], "Build the board")
        # P1044: the fixture keeps a sheet, so the wired sentence comes first
        self.assertTrue(build["effect"].startswith(WIRED_BUILD_MESSAGE + " Saves its files in this project: the board file"))
        self.assertIn("the Wokwi drawing breadboard.json when Wokwi has a part for each part drawn", build["effect"])
        self.assertIn("If the board tool is not installed, the board is not built, the old wiring sheet and drawings stay as an "
                      "earlier build's, and this page is deleted.", build["effect"])
        self.assertIn("If spark refuses the parts list, the old wiring sheet, drawings and pin map stay as an earlier build's, and "
                      "this page is deleted.", build["effect"])
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

    def test_a_board_only_parts_list_says_what_a_refused_file_leaves(self):
        # P1109's council, decision 4: a board-only build removes the old sheet and dist/, a refused file removes neither
        project = a_built_project()
        (project / "requirements.json").write_text(json.dumps({"board": "xiao-esp32-c6", "board_only": True, "parts": []}))
        effect = offer_of(show(project)[0], "build")["effect"]
        self.assertIn("If spark refuses the parts list, the old dist folder, wiring sheet, drawings and pin map stay as an "
                      "earlier build's, and this page is deleted.", effect)
        self.assertNotIn("the old wiring sheet, drawings and pin map stay", effect)


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
        # P976: the refused pick is no offer; the says line counts it (x-held is refused too)
        self.assertNotIn("pick:wet:x-one", offers(said, "parts"))
        # P991 review: each refused pick is named; x-one is held by this project's own pick only, so no other holder
        self.assertIn("Not shown for wet, refused: %s; “A soil probe” (too few free).%s" % (HELD, LIST), says(said, "parts"))
        self.assertNotIn("pick:soil:x-one", offers(said, "parts"))  # P976: the current pick is no offer

    def test_a_pick_is_refused_when_another_need_s_pick_cannot_get_its_part(self):
        self.a_part("x-one", {"count": 1, "used_in": {"other": 1}})
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [
            {"id": "soil", "does": "sense", "what": "soil-moisture", "pick": [{"part": "x-one"}]},
            {"id": "wet", "does": "sense", "what": "soil-moisture"}])
        said, _ = show(project)
        # P976: the refusal is said once, in the need's says line, and the need gets no offers
        self.assertEqual([line for line in says(said, "parts") if "cannot get" in line],
                         ["Spark can save no new pick for wet: the pick for soil cannot get “A soil probe” (1 owned, held by other — "
                          "1 picked here)."])  # P993
        self.assertEqual([key for key in offers(said, "parts") if key.startswith("pick:wet:")], [])
        self.assertNotIn("refuses", offer_of(said, "pick:soil:x-many")["effect"])

    def test_the_refusal_names_a_part_by_its_record_s_name_else_its_drawer_label_else_its_key(self):
        # P829 row 26 (the PO, 2026-11-21): the person reads the part's name, never the key spark files it under
        self.a_part("x-one", {"count": 1})
        (self.home / "drawer" / "y-old.json").write_text(json.dumps({"schema": 1, "label": "Old probe from the shed", "count": 1}))
        plan = needs.PickPlan(with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", SOIL))
        self.assertEqual([plan.name_of(key) for key in ("x-one", "y-old", "z-none")], ["A soil probe", "Old probe from the shed", "z-none"])

    def test_a_part_held_by_another_project_and_by_this_one_is_counted_as_refused(self):
        self.a_part("x-two", {"count": 2, "used_in": {"other": 1, "plant-alarm": 1}})
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [
            {"id": "soil", "does": "sense", "what": "soil-moisture", "pick": [{"part": "x-two"}]},
            {"id": "wet", "does": "sense", "what": "soil-moisture"}])
        said, _ = show(project)
        # P976: the refused pick is no offer; the says line counts it (x-held is refused too)
        self.assertNotIn("pick:wet:x-two", offers(said, "parts"))
        # P991 review: each refused pick is named with who else holds it
        self.assertIn("Not shown for wet, refused: %s; “A soil probe” (too few free, held by other).%s" % (HELD, LIST), says(said, "parts"))

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
        self.assertNotIn("pick:soil:x-many", offers(said, "parts"))  # P976: the current pick is no offer


class OffersPerNeedTest(FlowTest):
    """P976 (the PO, 2026-11-21: "so many unrelated things"): at most three plausible picks per need, in the matcher's
    order, never the current pick or a refused one; the rest is one says line per need. The store's three soil probes are
    owned, so they rank first, and none holds the need's word."""

    def probe(self, part, what="zorbleflux", tags=(), entry=None, does="sense"):
        """Put the probe `part` in the scratch catalog, doing (`does`) `what` with `tags`, and `entry` (a drawer entry's fields)
        in the drawer."""
        record = {"schema": 1, "id": part, "name": "Probe " + part, "kind": "sensor", "function": [{"does": does, "what": what}]}
        (self.home / "catalog" / (part + ".json")).write_text(json.dumps(dict(record, tags=list(tags)) if tags else record))
        if entry is not None:
            (self.home / "drawer" / (part + ".json")).write_text(json.dumps(dict({"schema": 1, "label": part, "is": {"part": part}}, **entry)))

    def setUp(self):
        super().setUp()
        self.probe("a-refused", entry={"count": 1, "used_in": {"other": 1}})  # owned, so it ranks first, and none is free
        self.probe("b-pick", entry={"count": "many"})  # owned, so it ranks second: the need's pick
        for part in ("c-1", "c-2", "c-3"):
            self.probe(part)
        self.project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm",
                                  [{"id": "probe", "does": "sense", "what": "zorbleflux", "pick": [{"part": "b-pick"}]}])

    def gone(self, part):
        """Take `part` out of the scratch catalog and drawer."""
        for folder in ("catalog", "drawer"):
            (self.home / folder / (part + ".json")).unlink(missing_ok=True)

    def test_three_plausible_picks_are_offered_and_the_refused_one_is_counted(self):
        said, _ = show(self.project)
        self.assertEqual(offers(said, "parts"), ["pick:probe:c-1", "pick:probe:c-2", "pick:probe:c-3"])
        # P991: the pick is named first
        self.assertEqual(says(said, "parts"), ["1 of 1 needs picked", "Picked for probe: “Probe b-pick”.",  # P991 review: named
                                               "Not shown for probe, refused: “Probe a-refused” (none free, held by other).%s" % LIST])

    def test_a_fourth_plausible_pick_is_counted_and_not_offered(self):
        self.probe("c-4")
        said, _ = show(self.project)
        self.assertEqual(offers(said, "parts"), ["pick:probe:c-1", "pick:probe:c-2", "pick:probe:c-3"])
        # P991: the full list, with the pick named first
        self.assertEqual(says(said, "parts"),
                         ["1 of 1 needs picked", "Picked for probe: “Probe b-pick”.",
                          "Not shown for probe: 1 more pick; refused: “Probe a-refused” (none free, held by other).%s" % LIST])  # P991 review

    def test_with_none_refused_the_line_says_only_how_many_more(self):
        self.gone("a-refused")
        self.probe("c-4")
        self.probe("c-5")
        said, _ = show(self.project)
        # P991: the full list, with the pick named first
        self.assertEqual(says(said, "parts"), ["1 of 1 needs picked", "Picked for probe: “Probe b-pick”.",
                                               "Not shown for probe: 2 more picks. Claude can list them with parts.py --match."])

    def test_a_part_with_the_need_s_word_only_in_its_tags_is_offered_by_the_default_matcher(self):
        # word-overlap is the default (the PO's yes, 2026-11-21): same-words would not offer c-0
        self.gone("c-2")
        self.gone("c-3")
        self.probe("c-0", what="other-things", tags=["zorbleflux"])
        said, _ = show(self.project)
        self.assertEqual(offers(said, "parts"), ["pick:probe:c-1", "pick:probe:c-0"])

    def test_a_need_with_candidates_and_no_plausible_pick_says_so(self):
        # the review of PR #1416: a need with no offer is never silent
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [{"id": "odd", "does": "sense", "what": "quuxwobble"}])
        said, _ = show(project)
        self.assertEqual((offers(said, "parts"), says(said, "parts")),
                         ([], ["0 of 1 needs picked", "No pick fits odd by its words. Ask Claude to run parts.py --match."]))

    def test_a_need_with_no_candidate_at_all_has_no_line(self):
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [{"id": "odd", "does": "keep-time", "what": "quuxwobble"}])
        said, _ = show(project)
        self.assertEqual((offers(said, "parts"), says(said, "parts")), ([], ["0 of 1 needs picked"]))

    def test_a_board_is_plausible_for_a_compute_need_whatever_its_words(self):
        # the review of PR #1416: "control", "brain" or "mcu" names no board's words, and a board is what a compute need wants
        self.probe("c-cpu", what="coprocessor", does="compute")  # a part, not a board, with none of the need's words
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [{"id": "brain", "does": "compute", "what": "control"}])
        said, _ = show(project)
        self.assertIn("pick:brain:xiao-esp32-c6", offers(said, "parts"))
        self.assertNotIn("pick:brain:c-cpu", offers(said, "parts"))

    def test_a_current_pick_stored_as_its_drawer_entry_is_not_offered_again(self):
        # the review of PR #1416: the drawer entry "many" is the record x-many, so a pick of either is the same pick
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm",
                             [{"id": "soil", "does": "sense", "what": "soil-moisture", "pick": [{"entry": "many"}]}])
        said, _ = show(project)
        self.assertNotIn("pick:soil:x-many", offers(said, "parts"))
        self.assertIn("pick:soil:x-unknown", offers(said, "parts"))


class RecordFirstOffersTest(FlowTest):
    """P991 (the PO at the p934-display page, 2026-11-22: "the beetle 2 c6 that we created is not even there"): what the
    person owns with a record is offered first, each need's pick is named, and an offer says when spark cannot build from
    its pick."""

    #: The start of the sentence an offer says when spark cannot build from its pick.
    CANNOT = "Spark cannot build from this pick"

    def entry(self, key, fields):
        (self.home / "drawer" / (key + ".json")).write_text(json.dumps(dict({"schema": 1, "label": key, "count": 1}, **fields)))

    def a_drawer_board(self):
        """A board the person owns with no board file, plausible by its words, as the walk's DFR0575 was."""
        self.entry("beetle", {"label": "Beetle ESP32 Microcontroller", "function": [{"does": "compute", "what": "microcontroller"}]})

    def board_effects(self, other_needs):
        """{key: effect} of the board need's pick offers, in a project with `other_needs` beside the board need."""
        self.a_drawer_board()
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm",
                             [{"id": "board", "does": "compute", "what": "microcontroller"}] + other_needs)
        return {offer["key"]: offer["effect"] for offer in next(phase for phase in show(project)[0]["data"]["phases"]
                                                                if phase["phase"] == "parts")["offers"] if offer["key"].startswith("pick:board:")}

    def test_an_owned_record_is_offered_before_owned_entries_with_no_record(self):
        for key in ("e-1", "e-2", "e-3"):
            self.entry(key, {"function": [{"does": "sense", "what": "zorbleflux"}]})
        (self.home / "catalog" / "r-tag.json").write_text(json.dumps({"schema": 1, "id": "r-tag", "name": "Probe r-tag", "kind": "sensor",
                                                                      "tags": ["zorbleflux"], "function": [{"does": "sense", "what": "other-things"}]}))
        self.entry("r-tag", {"is": {"part": "r-tag"}})
        said, _ = show(with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [{"id": "probe", "does": "sense", "what": "zorbleflux"}]))
        self.assertEqual(offers(said, "parts"), ["pick:probe:r-tag", "pick:probe:e-1", "pick:probe:e-2"])

    def test_a_drawer_board_with_no_board_file_says_its_pick_cannot_be_built_from(self):
        effects = self.board_effects([])
        # P991 review: in plain words, with the part's name, before the history sentence
        self.assertIn("Spark cannot build from this pick: it has no board file for “Beetle ESP32 Microcontroller”.", effects["pick:board:beetle"])
        self.assertTrue(effects["pick:board:beetle"].endswith(". May note the choice in your history."))
        self.assertEqual([key for key, effect in effects.items() if self.CANNOT in effect], ["pick:board:beetle"],
                         "a board spark has a file for says nothing of one")

    def test_a_drawer_board_says_nothing_when_another_need_picks_the_board(self):
        # the walk's state: the button need picks the C6, so the parts list places the C6 as the board (one board pick)
        effects = self.board_effects([{"id": "button", "does": "input", "what": "button", "pick": [{"board": "xiao-esp32-c6"}]}])
        self.assertIn("pick:board:beetle", effects)
        self.assertNotIn(self.CANNOT, effects["pick:board:beetle"])

    def test_a_drawer_board_says_nothing_when_two_boards_are_picked_elsewhere(self):
        # the refusal is then "pick one board", whose subject is no drawer entry
        effects = self.board_effects([{"id": "button", "does": "input", "what": "button", "pick": [{"board": "xiao-esp32-c6"}]},
                                      {"id": "led", "does": "indicate", "what": "light", "pick": [{"board": "firebeetle2-esp32s3"}]}])
        self.assertIn("pick:board:beetle", effects)
        self.assertNotIn(self.CANNOT, effects["pick:board:beetle"])

    def test_an_entry_with_no_record_for_a_need_that_does_not_compute_says_nothing_of_a_board_file(self):
        self.entry("e-1", {"function": [{"does": "sense", "what": "zorbleflux"}]})
        said, _ = show(with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [{"id": "probe", "does": "sense", "what": "zorbleflux"}]))
        self.assertNotIn(self.CANNOT, offer_of(said, "pick:probe:e-1")["effect"])

    def test_a_drawer_board_offered_for_a_need_that_does_not_compute_says_nothing_of_a_board_file(self):
        # the review of PR #1448: the board need picks the drawer board; the button offer of it is no board pick
        self.entry("beetle", {"label": "Beetle ESP32 Microcontroller", "count": 2, "function": [
            {"does": "compute", "what": "microcontroller"}, {"does": "input", "what": "button"}]})
        said, _ = show(with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [
            {"id": "board", "does": "compute", "what": "microcontroller", "pick": [{"entry": "beetle"}]},
            {"id": "button", "does": "input", "what": "button"}]))
        self.assertNotIn(self.CANNOT, offer_of(said, "pick:button:beetle")["effect"])

    def test_a_refused_owned_record_is_named_with_who_holds_it(self):
        # the review of PR #1448 (the PO: "even if taken"): the owned C6 held by two other projects is named, not only counted
        self.entry("c6", {"label": "my C6", "count": 2, "is": {"board": "xiao-esp32-c6"}, "used_in": {"p-a": 1, "p-b": 1}})
        said, _ = show(with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [{"id": "board", "does": "compute", "what": "microcontroller"}]))
        line = next(line for line in says(said, "parts") if line.startswith("Not shown for board"))
        self.assertIn("refused: “Seeed XIAO ESP32-C6” (none free, held by p-a, p-b).", line)

    def test_the_parts_phase_names_each_need_s_pick_by_its_name(self):
        # the drawer entry "many" carries `is` x-many, so its pick is named as the record; "spare" has no record: its label
        self.entry("spare", {"label": "Spare probe from the shed", "function": [{"does": "sense", "what": "soil-moisture"}]})
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [
            {"id": "soil", "does": "sense", "what": "soil-moisture", "pick": [{"part": "x-many"}]},
            {"id": "wet", "does": "sense", "what": "soil-moisture", "pick": [{"entry": "many"}]},
            {"id": "dry", "does": "sense", "what": "soil-moisture"},
            {"id": "two", "does": "sense", "what": "soil-moisture", "pick": [{"part": "x-many"}, {"entry": "spare"}]}])
        lines = says(show(project)[0], "parts")
        self.assertEqual(lines[0], "3 of 4 needs picked")
        self.assertEqual([line for line in lines if line.startswith("Picked for")],
                         ["Picked for soil: “A soil probe”.", "Picked for wet: “A soil probe”.",
                          "Picked for two: “A soil probe”, “Spare probe from the shed”."])
        self.assertLess(lines.index("Picked for soil: “A soil probe”."),
                        min(number for number, line in enumerate(lines) if " for soil " in line or line.startswith("Not shown for soil")))


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


class TheBlockersTest(FlowTest):
    """P993: the parts list is offered only when its own rule refuses nothing, and its refusal is said before the click."""

    def test_no_pick_offers_no_parts_list(self):
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", SOIL + [{"id": "board", "does": "compute", "what": "microcontroller"}])
        said, code = show(project)
        self.assertEqual((code, table(said)["requirements"]), (0, (NS, [])))
        self.assertEqual(says(said, "requirements"), ["no requirements.json yet", "board: pick one board — none is picked"])

    def test_a_pick_that_owes_only_its_simulation_stance_offers_the_parts_list_with_a_warning(self):
        # P996 (the PO, 2026-11-22): "The simulation step should not stop us if we want and can deploy directly."
        led = json.loads((ROOT / "parts" / "led-red-5mm.json").read_text())
        (self.home / "catalog" / "x-sim.json").write_text(json.dumps(dict({k: v for k, v in led.items() if k != "simulation"}, id="x-sim")))
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", BOARD + [
            {"id": "light", "does": "indicate", "what": "light", "pick": [{"part": "x-sim"}]}])
        said, code = show(project)
        self.assertEqual((code, table(said)["requirements"]), (0, (NS, ["requirements"])))
        self.assertEqual(says(said, "requirements"), [
            "no requirements.json yet",
            "Spark cannot simulate “Kingbright L-7113ID 5 mm red LED” for light yet. The parts list and the build go on, "
            "and a deploy asks your yes for firmware that no simulation tested."])

    def test_a_pick_with_a_broken_footprint_and_no_simulation_says_the_footprint(self):
        # P996 review (refuter): the owed simulation blocks nothing, so the page says the fault that does
        led = json.loads((ROOT / "parts" / "led-red-5mm.json").read_text())
        record = dict({k: v for k, v in led.items() if k != "simulation"}, id="x-sim", footprint=5)
        (self.home / "catalog" / "x-sim.json").write_text(json.dumps(record))
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", BOARD + [
            {"id": "light", "does": "indicate", "what": "light", "pick": [{"part": "x-sim"}]}])
        said, _ = show(project)
        self.assertEqual(table(said)["requirements"], ("problems", []))
        self.assertEqual(says(said, "requirements")[1][:44], "x-sim: footprint is 5, but a footprint is th")

    def test_a_pick_that_owes_a_fact_says_which_and_offers_no_parts_list(self):
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", BOARD + [
            {"id": "soil", "does": "sense", "what": "soil-moisture", "pick": [{"part": "x-many"}]}])
        said, code = show(project)
        self.assertEqual((code, table(said)["requirements"]), (1, ("problems", [])))
        self.assertEqual(says(said, "requirements"), [
            "no requirements.json yet",
            "“A soil probe” for soil still lacks what spark needs: needs, footprint, pin_order, pin_order_proof. "
            "Ask Claude how to fill it in."])
        now = said["data"]["guide"]["now"]
        self.assertEqual((now["phase"], now["offer"], now["says"]),
                         ("requirements", None, "The requirements phase has problems. Ask Claude to go through them with you."))

    def test_a_pick_stored_as_its_drawer_entry_is_named_with_its_need(self):
        # P993 review (refuter): the pick names the entry, the owed problem names its record
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", BOARD + [
            {"id": "soil", "does": "sense", "what": "soil-moisture", "pick": [{"entry": "many"}]}])
        self.assertEqual(says(show(project)[0], "requirements")[1],
                         "“A soil probe” for soil still lacks what spark needs: needs, footprint, pin_order, pin_order_proof. "
                         "Ask Claude how to fill it in.")

    def test_every_need_set_aside_offers_no_parts_list_and_is_not_started(self):
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [
            {"id": "soil", "does": "sense", "what": "soil-moisture", "aside": True},
            {"id": "wet", "does": "sense", "what": "soil-moisture", "aside": True}])
        said, code = show(project)
        self.assertEqual((code, table(said)["requirements"], said["data"]["guide"]["now"]["phase"]), (0, (NS, []), "parts"))

    def test_a_requirements_file_the_picks_cannot_give_has_no_offer(self):
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [
            {"id": "soil", "does": "sense", "what": "soil-moisture", "pick": [{"part": "x-many"}]}])
        (project / "requirements.json").write_text(json.dumps({"board": "xiao-esp32-c6", "parts": []}))
        said, _ = show(project)
        self.assertEqual(table(said)["requirements"], ("problems", []))
        self.assertEqual(says(said, "requirements"), [
            "board: pick one board — none is picked",
            "“A soil probe” for soil still lacks what spark needs: needs, footprint, pin_order, pin_order_proof. "
            "Ask Claude how to fill it in."])


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


class TheHandEditTest(unittest.TestCase):
    """P1140: after a hand edit of requirements.json, the phase and the guide's now say the file changed by hand, not that the
    picks changed. A file as spark wrote it says the picks changed; a file with no record, or one that cannot be read, names no cause."""

    PICKS = "requirements.json differs from what the picks give"
    EDITED = "requirements.json was changed by hand after spark last wrote it, and differs from what the picks give"
    PICKS_NOW = "Your picks changed. Ask Claude to write the parts list again."
    EDITED_NOW = ("The parts list was changed by hand. Writing it again keeps its parts and puts back what your picks give. "
                  "Ask Claude to write it again, or to change your picks first.")
    DIFFERS_NOW = "The parts list differs from what your picks give. Ask Claude to write it from your picks."

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
        self.pick("brain=xiao-esp32-c6", "button=tactile-button", "light=led-red-5mm")
        self.write()
        self.assertEqual(statuses(show(self.project)[0])["requirements"], "ok")

    def pick(self, *picks):
        result = run_operation(PickParts(), {"project_and_picks": [str(self.project), *picks], "passed_over": NO_PASSED_OVER, "dry_run": False},
                               FakeOutsideWorld(clock=FakeClock()))
        self.assertEqual(result.status(), OK, result.lines)

    def write(self):
        result = run_operation(WriteRequirements(), {"project": str(self.project), "dry_run": False, "replies": None}, FakeOutsideWorld(clock=FakeClock()))
        self.assertEqual(result.status(), OK, result.lines)

    def edit(self, **changes):
        file = self.project / "requirements.json"
        file.write_text(json.dumps(dict(json.loads(file.read_text()), **changes), indent=2))

    def said(self):
        envelope = show(self.project)[0]
        return says(envelope, "requirements")[0], statuses(envelope)["requirements"], envelope["data"]["guide"]["now"]

    def test_a_part_taken_out_by_hand_says_the_file_was_changed_by_hand(self):
        self.edit(parts=["tactile-button"])
        said = show(self.project)[0]
        self.assertEqual((table(said)["requirements"], marks(said)["requirements"], says(said, "requirements")[0]), (("stale", ["requirements"]), "↻", self.EDITED))

    def test_a_board_changed_by_hand_says_so_too(self):
        self.edit(board="firebeetle2-esp32s3")
        self.assertEqual(self.said()[:2], (self.EDITED, "stale"))

    def test_a_new_pick_after_the_parts_list_keeps_the_picks_line(self):
        self.pick("brain=firebeetle2-esp32s3")
        self.assertEqual(self.said()[:2], (self.PICKS, "stale"))

    def test_with_no_record_the_line_names_no_cause(self):
        self.edit(parts=["tactile-button"])
        (self.project / ".spark" / "requirements-origin.json").unlink()
        self.assertEqual(self.said()[:2], (self.PICKS, "stale"))

    def test_the_walk_s_hand_edit_says_so_in_now_and_never_that_the_picks_changed(self):
        self.edit(parts=["tactile-button"])
        envelope = show(self.project)[0]
        now = envelope["data"]["guide"]["now"]
        self.assertEqual((now["phase"], now["by"], now["says"], now["offer"]), ("requirements", ["claude"], self.EDITED_NOW, "requirements"))
        with contextlib.redirect_stdout(io.StringIO()) as out:
            flow.main(["show", "--project", str(self.project)])
        self.assertIn("The parts list was changed by hand", out.getvalue())
        self.assertNotIn("Your picks changed", out.getvalue())

    def test_writing_again_after_the_hand_edit_puts_back_the_pick_and_is_ok(self):
        self.edit(parts=["tactile-button"])
        self.write()
        self.assertEqual(self.said()[1], "ok")
        self.assertEqual(json.loads((self.project / "requirements.json").read_text())["parts"], ["tactile-button", "led-red-5mm"])
        self.assertIs(EntryOriginStore(self.project).is_as_written(json.loads((self.project / "requirements.json").read_text())), True)

    def test_a_new_pick_says_the_picks_changed(self):
        self.pick("brain=firebeetle2-esp32s3")
        said = self.said()
        self.assertEqual((said[1], said[2]["says"]), ("stale", self.PICKS_NOW))

    def test_no_record_or_one_that_cannot_be_read_says_no_cause(self):
        self.edit(parts=["tactile-button"])
        record = self.project / ".spark" / "requirements-origin.json"
        before = show(self.project)[1]
        record.unlink()
        for text in (None, "{not json"):
            with self.subTest(record=text):
                if text:
                    record.write_text(text)
                envelope, code = show(self.project)
                self.assertEqual((envelope["data"]["guide"]["now"]["says"], code), (self.DIFFERS_NOW, before))


class TheOfferStepTest(FlowTest):
    """P1030: each offer carries the core's NextStep that runs it: its op, an argv with the whole project path, and the
    store's env. A pick is the person's choice, so its step needs the person."""

    def steps_of(self, project):
        return {offer.key: offer.step for phase in read_flow(project)[0] for offer in phase.offers}

    def test_each_offer_of_a_real_project_carries_its_step(self):
        project = with_needs(a_built_project(), SOIL)
        steps, whole, env = self.steps_of(project), str(project.absolute()), {"SPARK_HOME": str(self.home.resolve())}
        self.assertEqual(steps["pick:soil:x-many"], NextStep("pick", ["--pick", whole, "soil=x-many"],
                                                             "The person's choice: “A soil probe” for the soil need", ("reads", "writes"),
                                                             False, True, env))
        self.assertEqual(steps["build"], NextStep("build-board", [str(project.absolute() / "requirements.json"), "--keep", whole],
                                                  "Build the board", ("reads", "runs", "writes"), False, None, env))
        self.assertEqual(steps["needs-drop:soil"], NextStep("needs-drop", ["--needs-drop", whole, "soil"], "Drop the soil need",
                                                            ("reads", "writes"), False, None, env))

    def test_a_relative_project_s_step_names_it_whole_so_no_name_reads_as_a_flag(self):
        project = with_needs(a_built_project(), SOIL)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(project.parent)
        steps = self.steps_of(project.name)
        self.assertEqual(steps["build"].argv[2], str(Path.cwd() / project.name))  # the folder as the process sees it, whole

    def test_each_step_parses_with_its_own_operation_to_the_values_the_page_ran_before(self):
        from spark.core.cli import values_of
        from spark.flow.run_request import STEP_OPERATIONS
        import parts
        project = with_needs(a_built_project(), SOIL)
        whole, steps = project.absolute(), self.steps_of(project)
        operations = dict(STEP_OPERATIONS, **{"needs-drop": parts.DropNeedFlag})
        self.assertEqual({key: values_of(operations[step.op](), step.argv) for key, step in steps.items() if key in
                          ("pick:soil:x-many", "build", "needs-drop:soil")},
                         {"pick:soil:x-many": ({"project_and_picks": [str(whole), "soil=x-many"], "passed_over": NO_PASSED_OVER, "dry_run": False}, False),
                          "build": ({"requirements": str(whole / "requirements.json"), "keep": whole, "sim_dir": None, "firmware": None}, False),
                          "needs-drop:soil": ({"project_and_need": [str(whole), "soil"], "dry_run": False}, False)})
        self.assertIs(values_of(PickParts(), steps["pick:soil:x-many"].argv)[0]["passed_over"], NO_PASSED_OVER)
        self.assertEqual({step.op: step.effects for step in steps.values()},
                         {op: tuple(operation.effects) for op, operation in operations.items() if op in ("pick", "build-board", "needs-drop")})

    def test_the_joined_step_of_three_picks_is_the_pick_of_their_pairs_with_pick_parts_s_op_and_effects(self):
        """P1067: the page's Send of several picks runs one step, built through `picks_step` from the offers' own steps."""
        from spark.core.cli import values_of
        from spark.flow import offer_steps
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", SOIL)
        steps = [offer_steps.pick_step(project, need, pick_id, name) for need, pick_id, name in
                 (("soil", "x-many", "A soil probe"), ("light", "led-red-5mm", "Red LED"), ("board", "xiao-esp32-c6", "XIAO"))]
        joined = offer_steps.joined_picks(steps)
        self.assertEqual(joined, offer_steps.picks_step(project, ["soil=x-many", "light=led-red-5mm", "board=xiao-esp32-c6"],
                                                        "; ".join(step.why for step in steps)))
        self.assertEqual((joined.op, joined.effects), (PickParts.name, tuple(PickParts.effects)))
        self.assertEqual(values_of(PickParts(), joined.argv)[0]["project_and_picks"],
                         [str(project.absolute()), "soil=x-many", "light=led-red-5mm", "board=xiao-esp32-c6"])

    def test_the_parts_list_step_parses_with_its_own_operation(self):
        from spark.core.cli import values_of
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", BOARD)
        step = self.steps_of(project)["requirements"]
        self.assertEqual((step.op, step.effects, values_of(WriteRequirements(), step.argv)),
                         ("requirements", tuple(WriteRequirements.effects), ({"project": str(project.absolute()), "dry_run": False, "replies": None}, False)))

    def test_a_parts_phase_with_one_pick_offer_names_it_as_the_now_offer_and_with_two_none(self):
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", SOIL)
        self.assertEqual((show(project)[0]["data"]["guide"]["now"]["phase"], show(project)[0]["data"]["guide"]["now"]["offer"]), ("parts", None))
        for kind, name in (("catalog", "x-unknown"), ("drawer", "unknown")):
            (self.home / kind / (name + ".json")).unlink()
        said = show(project)[0]
        self.assertEqual((offers(said, "parts"), said["data"]["guide"]["now"]["offer"]), (["pick:soil:x-many"], "pick:soil:x-many"))

    def test_a_breadboard_now_names_no_offer_and_its_page_line_carries_no_key(self):
        from spark.flow.write_flow_page import FlowPageStore, write_page
        project = a_built_project()
        (project / "breadboard.md").unlink()
        said = show(project)[0]
        self.assertEqual((said["data"]["guide"]["now"]["phase"], said["data"]["guide"]["now"]["offer"], offers(said, "build")),
                         ("breadboard", None, ["build"]))
        write_page(project, store=FlowPageStore())
        page = (project / "page.html").read_text(encoding="utf-8")  # P1062: the NOW box, its NEXT line with no key
        self.assertIn("<p><strong>NOW (breadboard), by ", page)
        self.assertIn('<p class="next"><strong>NEXT</strong> ', page)

    def a_hand_written_project(self):
        project = Path(tempfile.mkdtemp()) / "bl"
        shutil.copytree(ROOT / "tests" / "data" / "breadboard" / "button-light", project)
        return project

    def test_show_s_next_holds_the_now_offer_s_step_raw_while_data_is_masked(self):
        project = self.a_hand_written_project()
        said, _ = show(project)
        self.assertEqual((said["data"]["stands_at"], said["data"]["guide"]["now"]["offer"]), ("build", "build"))
        self.assertEqual(said["next"], [{"op": "build-board", "argv": [str(project.absolute() / "requirements.json"), "--keep", str(project.absolute())],
                                         "why": "Build the board", "effects": ["reads", "runs", "writes"], "needs_yes": False,
                                         "env": {"SPARK_HOME": str(self.home.resolve())}}])
        self.assertNotIn(str(project), json.dumps(said["data"]))

    def test_show_s_next_is_empty_at_the_idea_which_names_no_step(self):
        empty = Path(tempfile.mkdtemp()) / "plant-alarm"
        empty.mkdir()
        said, _ = show(empty)
        self.assertEqual((said["data"]["guide"]["now"]["phase"], said["next"]), ("idea", []))

    def test_show_s_text_starts_with_the_guide_s_lines_and_no_stands_at_line(self):
        lines = lines_of(self.a_hand_written_project())
        self.assertEqual(lines[:3], ["  NOW (build): Ask Claude in the chat to build the board. It takes seconds and costs nothing. [build]",
                                      "  DONE: idea, requirements (no needs or picks behind it)",
                                      "  LATER: breadboard, firmware, simulate, deploy"])
        self.assertFalse([line for line in lines if "stands at" in line])

    def test_show_s_text_says_why_there_is_no_simulation_and_what_is_set_aside(self):
        project = a_project_built_with_no_simulation()
        with_needs(project, [{"id": "soil", "does": "sense", "what": "soil-moisture", "aside": True}])
        lines = lines_of(project)
        at = lines.index("  " + NO_MODEL)  # the page's order, then the first phase line
        self.assertEqual(lines[at:at + 3][:2], ["  " + NO_MODEL, "  SET ASIDE: soil"])
        self.assertIn("idea:", lines[at + 2])

    def test_show_prints_the_same_simulation_line_as_the_page(self):
        """P1209 (D5): show's text line is "  " + data.guide.simulation.line, and the page's guide section holds the same text."""
        from spark.firmware.firmware_check import INPUTS
        from spark.firmware.project_secrets import is_secret_path
        from spark.flow.write_flow_page import FlowPageStore, write_page
        from spark.records.check_record import CheckRecordStore
        project = a_firmware(a_project_built_with_no_simulation())
        CheckRecordStore(project, "check-firmware", leave_out=is_secret_path).save(
            INPUTS, "2026-11-27T02:10:00+01:00", {"status": "ok", "data": {}, "lines": ["imports: 0 of 0 imported", "tests: none (no tests/ folder)"]})
        line = show(project)[0]["data"]["guide"]["simulation"]["line"]
        self.assertTrue(line.startswith("Free checks, ") and line.endswith(NO_MODEL), line)
        self.assertIn("  " + line, lines_of(project))
        self.assertNotIn("  " + NO_MODEL, lines_of(project))  # one line, not two
        write_page(project, store=FlowPageStore())
        section = (project / "page.html").read_text(encoding="utf-8").split('<section id="guide">')[1].split("</section>")[0]
        self.assertIn('<p class="muted">%s</p>' % line, section)

    def test_show_of_a_record_with_a_line_that_is_no_text_exits_0_and_says_not_checked(self):
        """The review (A1, R12): a record's reader never raises, so `"lines": [1]` never crashes show or the page."""
        from spark.firmware.firmware_check import INPUTS
        from spark.records.check_record import CheckRecordStore
        project = a_firmware(a_project_built_with_no_simulation_now())  # a build recorded ok: show exits 0
        records = CheckRecordStore(project, "check-firmware")
        records.save(INPUTS, "2026-11-27T02:10:00+01:00", {"status": "ok", "data": {}, "lines": ["imports: 1 of 1 imported"]})
        records.path.write_text(json.dumps(dict(json.loads(records.path.read_text()), lines=[1])))
        said, code = show(project)
        simulation = said["data"]["guide"]["simulation"]
        self.assertEqual((code, simulation["check"]["state"], simulation["grey"]), (0, "not-checked", False))
        self.assertTrue(simulation["line"].startswith("Free checks: the check record is of another shape"), simulation["line"])
        self.assertIn("  " + simulation["line"], lines_of(project))

    def test_the_offers_in_data_keep_their_five_keys_and_no_step(self):
        said, _ = show(with_needs(a_built_project(), SOIL))
        self.assertEqual({tuple(offer) for phase in said["data"]["phases"] for offer in phase["offers"]},
                         {("key", "label", "effect", "makes_stale", "part")})

    def test_a_pick_offer_in_data_names_its_part_and_every_other_offer_null(self):
        """P1067 (D22: each fact on the page is in show): the page labels a pick's radio by its part."""
        said, _ = show(with_needs(a_built_project(), SOIL))
        parts = {offer["key"]: offer["part"] for phase in said["data"]["phases"] for offer in phase["offers"]}
        self.assertEqual(parts["pick:soil:x-many"], "A soil probe")
        self.assertEqual({key: part for key, part in parts.items() if not key.startswith("pick:")},
                         {key: None for key in parts if not key.startswith("pick:")})
        self.assertIn("build", parts)


def a_simulate_now(project, *scenarios):
    """`project` with firmware/, sim/wokwi.toml and an image no run tested, and the scenario files `scenarios` by name."""
    project = an_image(a_firmware(project))
    for name in scenarios:
        (project / "sim" / "scenarios").mkdir(exist_ok=True)
        (project / "sim" / "scenarios" / name).write_text("name: %s\n" % name)
    return project


def now_line(project):
    """The NOW line of `flow.py show`'s text."""
    return next(line for line in lines_of(project) if line.startswith("  NOW ("))


class TheNextOnlyStepTest(FlowTest):
    """P1034: a now phase with no offer names its step in `next`: the simulate its scenario runs (or the build while
    sim/wokwi.toml is missing), the deploy its look. The firmware names none. Each step is next-only: no page button
    runs it, and the NOW line ends with `[next: <op>]`, with `, needs you` for a step that needs the person."""

    def env(self):
        return {"SPARK_HOME": str(self.home.resolve())}

    def scenario_step(self, project, scenario, why=SCENARIO_WHY):
        return {"op": "run_scenario", "argv": [scenario, "--project", str(project.absolute())], "why": why,
                "effects": ["reads", "runs", "writes"], "needs_yes": False, "needs_person": True, "env": self.env()}

    def test_a_firmware_now_names_no_step_because_main_py_is_not_written_yet(self):
        for project in (a_project_built_with_no_simulation(), a_built_project()):
            with self.subTest(project=project):
                said, _ = show(project)
                self.assertEqual((said["data"]["guide"]["now"]["phase"], said["next"]), ("firmware", []))
                self.assertNotIn("[next:", now_line(project))

    def test_a_simulate_now_names_each_scenario_run_and_needs_the_person(self):
        import argparse
        import run_scenario
        project = a_simulate_now(a_built_project(), "b.scenario.yaml", "a.scenario.yaml")
        said, _ = show(project)
        self.assertEqual(said["data"]["guide"]["now"]["phase"], "simulate")
        self.assertEqual(said["next"], [self.scenario_step(project, "sim/scenarios/%s.scenario.yaml" % name) for name in "ab"])
        parser = argparse.ArgumentParser()
        for flags, options in run_scenario.ARGUMENTS:
            parser.add_argument(*flags, **options)
        self.assertEqual([(values.scenario, values.project) for values in (parser.parse_args(step["argv"]) for step in said["next"])],
                         [(Path("sim/scenarios/%s.scenario.yaml" % name), project.absolute()) for name in "ab"])
        self.assertTrue(now_line(project).endswith(" [next: run_scenario, needs you]"), now_line(project))

    def test_with_no_scenario_the_step_names_the_placeholder_and_claude_writes_it_first(self):
        project = a_simulate_now(a_built_project())
        said = show(project)[0]
        self.assertEqual(said["next"], [self.scenario_step(project, SCENARIO_PLACEHOLDER, SCENARIO_FIRST_WHY)])
        self.assertEqual((said["data"]["guide"]["now"]["by"], said["data"]["guide"]["now"]["says"]), (["your terminal"],
                         "No scenario is written yet, so ask Claude to write one first. Then ask for the scenario command, and "
                         "run it in your terminal. It uses Wokwi CI minutes."))

    def test_with_a_scenario_the_now_sentence_asks_for_the_scenario_command(self):
        said = show(a_simulate_now(a_built_project(), "a.scenario.yaml"))[0]
        self.assertEqual(said["data"]["guide"]["now"]["says"],
                         "Ask Claude for the scenario command, and run it in your terminal. It uses Wokwi CI minutes.")

    def test_a_simulate_with_its_toml_and_no_image_names_the_scenario_run_which_makes_the_image(self):
        project = a_firmware(a_built_project())
        (project / "sim").mkdir()
        (project / "sim" / "wokwi.toml").write_text('[wokwi]\nversion = 1\nfirmware = "image.bin"\n')
        said, _ = show(project)
        self.assertEqual((statuses(said)["simulate"], said["data"]["guide"]["now"]["phase"]), ("not-started", "simulate"))
        self.assertEqual(said["next"], [self.scenario_step(project, SCENARIO_PLACEHOLDER, SCENARIO_FIRST_WHY)])

    def test_firmware_changed_after_a_passed_run_names_the_scenario_run_again(self):
        project = a_run(an_image(a_firmware(a_built_project())), "passed")
        os.utime(project / "firmware" / "main.py", (1_700_007_200, 1_700_007_200))
        said, _ = show(project)
        self.assertEqual((said["data"]["guide"]["now"]["phase"], said["next"][0]["op"]), ("simulate", "run_scenario"))

    def test_a_failed_run_and_a_simulate_with_problems_name_no_step(self):
        failed = a_run(an_image(a_firmware(a_built_project())), "failed")
        problems = a_firmware(a_project_built_with_no_simulation())
        (problems / "sim").mkdir()
        (problems / "sim" / "wokwi.toml").write_text('[wokwi]\nversion = 1\nfirmware = 42\n')
        for project in (failed, problems):
            with self.subTest(project=project):
                said, _ = show(project)
                self.assertEqual((said["data"]["guide"]["now"]["phase"], said["next"]), ("simulate", []))
                self.assertNotIn("[next:", now_line(project))

    def test_a_simulate_with_no_sim_files_names_the_build_in_its_sentence_and_its_step(self):
        project = a_firmware(a_built_project())
        said, _ = show(project)
        whole = str(project.absolute())
        self.assertEqual(said["data"]["guide"]["now"], {"phase": "simulate", "by": ["claude"], "says": SIM_FILES_NOW, "offer": None,
                                                        "chat_offer": None, "needs": [], "steps": None, "with_wiring": False})
        self.assertEqual(said["next"], [{"op": "build-board", "argv": [str(project.absolute() / "requirements.json"), "--keep", whole],
                                         "why": "Build the board", "effects": ["reads", "runs", "writes"], "needs_yes": False,
                                         "env": self.env()}])
        self.assertTrue(now_line(project).endswith(" [next: build-board]"), now_line(project))

    def test_a_deploy_now_names_the_look_for_the_person(self):
        from spark.bench.look_at_board import LookAtBoard
        from spark.core.cli import values_of
        project = a_run(an_image(a_firmware(a_built_project())), "passed")
        said, _ = show(project)
        self.assertEqual(said["data"]["guide"]["now"]["phase"], "deploy")
        self.assertEqual(said["next"], [{"op": "look", "argv": ["--project", str(project.absolute())], "why": LOOK_WHY, "effects": [],
                                         "needs_yes": False, "needs_person": True, "env": self.env()}])
        values = values_of(LookAtBoard(), said["next"][0]["argv"])[0]
        self.assertEqual((str(values["project"]), values["no_simulation"]), (str(project.absolute()), False))
        self.assertTrue(now_line(project).endswith(" [next: look, needs you]"), now_line(project))

    def test_a_deploy_with_no_simulation_names_the_look_with_no_simulation(self):
        for project in (a_firmware(a_project_built_with_no_simulation()), an_image(a_firmware(a_project_built_with_no_simulation()))):
            with self.subTest(project=project):
                said, _ = show(project)
                self.assertEqual((said["data"]["guide"]["now"]["phase"], [step["argv"] for step in said["next"]]),
                                 ("deploy", [["--project", str(project.absolute()), "--no-simulation"]]))

    def open_needs(self, *ids):
        return with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [{"id": one, "does": "sense", "what": "soil-moisture"} for one in ids])

    def test_a_parts_now_with_open_needs_and_no_one_offer_names_one_pick_with_a_part_per_need(self):
        # P1141: two open needs give two pick offers, so the now names no offer (`job_offer`) and the parts phase its own step
        from spark.core.cli import values_of
        from spark.design.pick_parts import PickParts
        from spark.flow.flow_codes import PICK_OPEN_WHY
        from spark.flow.phase_steps import PART_PLACEHOLDER
        project = self.open_needs("soil", "wet")
        said, _ = show(project)
        self.assertEqual((said["data"]["guide"]["now"]["phase"], said["data"]["guide"]["now"]["offer"]), ("parts", None))
        self.assertEqual(said["next"], [{"op": "pick", "argv": ["--pick", str(project.absolute()), "soil=<part>", "wet=<part>"],
                                         "why": PICK_OPEN_WHY, "effects": ["reads", "writes"], "needs_yes": False, "needs_person": True,
                                         "env": self.env()}])
        self.assertEqual(PART_PLACEHOLDER, "<part>")
        self.assertEqual(values_of(PickParts(), said["next"][0]["argv"])[0]["project_and_picks"][1:], ["soil=<part>", "wet=<part>"])
        self.assertTrue(now_line(project).endswith(" [next: pick, needs you]"), now_line(project))

    def test_a_parts_now_names_only_the_open_needs_and_none_when_every_need_is_aside_or_the_phase_has_problems(self):
        partial = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [
            {"id": "soil", "does": "sense", "what": "soil-moisture"}, {"id": "wet", "does": "sense", "what": "soil-moisture"},
            {"id": "dry", "does": "sense", "what": "soil-moisture", "aside": True},
            {"id": "pump", "does": "sense", "what": "soil-moisture", "pick": [{"part": "x-many"}]}])
        self.assertEqual([step["argv"][2:] for step in show(partial)[0]["next"]], [["soil=<part>", "wet=<part>"]])
        aside = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [{"id": "dry", "does": "sense", "what": "soil-moisture", "aside": True}])
        said = show(aside)[0]
        self.assertEqual((statuses(said)["parts"], said["data"]["guide"]["now"]["phase"], said["next"]), ("ok", "parts", []))
        problems = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [{"id": "soil", "does": "sense", "what": "soil-moisture"},
                                                                        {"id": "wet", "what": "soil-moisture"}])
        said = show(problems)[0]
        self.assertEqual((statuses(said)["parts"], said["data"]["guide"]["now"]["phase"], said["next"]), ("problems", "parts", []))

    def test_the_idea_names_its_brief_step_only_when_it_is_stale(self):
        from spark.flow import phase_steps
        project = self.open_needs("soil")
        guide = {"now": {"phase": "idea"}, "no_simulation": None}
        stale, fresh = Phase("idea", STALE, None, [], [], []), Phase("idea", "ok", None, [], [], [])
        self.assertEqual([step.op for step in phase_steps.steps_of(project, [stale], guide)], ["init_project"])
        self.assertEqual(phase_steps.steps_of(project, [fresh], guide), [])
        self.assertEqual(phase_steps.steps_of(project, [fresh], {"now": None, "no_simulation": None}), [])

    def test_no_next_only_op_is_one_the_page_runs(self):
        from spark.flow.run_request import STEP_OPERATIONS
        from spark.flow.write_flow_page import FlowPageStore, write_page
        simulate, deploy = a_simulate_now(a_built_project(), "a.scenario.yaml"), a_run(an_image(a_firmware(a_built_project())), "passed")
        ops = {step["op"] for project in (simulate, deploy) for step in show(project)[0]["next"]}
        self.assertEqual(ops, {"run_scenario", "look"})
        self.assertFalse(ops & set(STEP_OPERATIONS))
        said = show(deploy)[0]
        self.assertIsNone(said["data"]["guide"]["now"]["offer"])
        self.assertFalse([offer for phase in said["data"]["phases"] for offer in phase["offers"] if offer["key"].startswith("look")])
        write_page(deploy, store=FlowPageStore())
        page = (deploy / "page.html").read_text(encoding="utf-8")  # P1062: the NOW box, its NEXT line with no key
        self.assertIn("<p><strong>NOW (deploy), by ", page)
        self.assertIn('<p class="next"><strong>NEXT</strong> ', page)

    def test_no_step_names_a_home_path_and_only_argv_and_env_name_the_project(self):
        # the projects are under HOME (FlowTest), so a raw argv names the home folder: only argv and env may
        for project in (a_simulate_now(a_built_project(where=self.user_home), "a.scenario.yaml"),
                        a_firmware(a_built_project(where=self.user_home)),
                        a_run(an_image(a_firmware(a_built_project(where=self.user_home))), "passed")):
            with self.subTest(project=project):
                said, _ = show(project)
                self.assertTrue(said["next"])
                self.assertTrue(str(project).startswith(str(Path.home())))
                self.assertTrue(all(str(project.absolute()) in step["argv"] for step in said["next"]))  # raw, as P1030's build step
                outside = dict(said, next=[{key: value for key, value in step.items() if key not in ("argv", "env")} for step in said["next"]])
                self.assertNotIn(str(Path.home()), json.dumps(outside))
                self.assertNotIn(str(project), json.dumps(outside))


def run_main(main, argv):
    """(the stdout lines, the exit code) of a CLI's `main(argv)`, stderr kept away."""
    with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
        code = main(argv)
    return out.getvalue().splitlines(), code


def a_kept_build(project, stages, keep=True, as_json=True):
    """(the stdout lines, the exit code) of check_spine.py's HELP run through the core on `project`'s requirements.json with a
    FakeRequirementsBuild of `stages`, whose work folder holds the project's own circuit, kept into `project` with `keep`."""
    import check_spine
    from fakes import FakeRequirementsBuild
    from spark.build.build_board import BuildBoard
    from spark.core.cli import run_cli
    from spark.core.outside import build_bare_outside_world
    work = Path(tempfile.mkdtemp())
    (work / "board.tsx").write_text("// the board")
    (work / "dist" / "board").mkdir(parents=True)
    shutil.copy(project / "dist" / "board" / "circuit.json", work / "dist" / "board" / "circuit.json")
    argv = [str(project / "requirements.json")] + (["--keep", str(project)] if keep else []) + (["--json"] if as_json else [])
    return run_main(lambda given: run_cli(check_spine.HELP, BuildBoard(FakeRequirementsBuild(stages, work)), given,
                                          outside_builder=build_bare_outside_world), argv)


class TheFollowUpTest(FlowTest):
    """P1035: after an ok run that writes to a project, `parts.py --pick` and `check_spine.py --keep` end `next` with the
    step `flow.py show` names now, after their own steps, and their text with its line. The store holds two probes: x-held,
    which another project holds, and x-many (test_run_request's two-probe store)."""

    def setUp(self):
        super().setUp()
        (self.home / "catalog" / "x-unknown.json").unlink()
        (self.home / "drawer" / "unknown.json").unlink()

    def open_needs(self, *ids):
        return with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [{"id": one, "does": "sense", "what": "soil-moisture"} for one in ids])

    def test_a_pick_ends_with_the_flow_s_next_pick_in_its_json_and_its_text(self):
        import parts
        from spark.flow.now_follow_up import FlowFollowUp
        from spark.flow.show_flow import NEEDS_YOU, flow_and_guide, now_steps
        project = self.open_needs("soil", "wet")
        lines, code = run_main(parts.main, ["--pick", str(project), "soil=x-many", "--json"])
        said = json.loads(lines[0])
        self.assertEqual((code, said["status"]), (0, "ok"))
        self.assertEqual(said["next"], show(project)[0]["next"])
        self.assertEqual([(step["op"], step["argv"]) for step in said["next"]], [("pick", ["--pick", str(project.absolute()), "wet=x-many"])])
        other = self.open_needs("soil", "wet")
        lines, code = run_main(parts.main, ["--pick", str(other), "soil=x-many"])
        step = now_steps(other, *flow_and_guide(other))[0]
        self.assertEqual((code, lines[-1]), (0, FlowFollowUp().line(step)))
        self.assertTrue(lines[-1].startswith("  next: "), lines[-1])
        self.assertIn("/parts.py --pick %s wet=x-many%s — " % (other.absolute(), NEEDS_YOU), lines[-1])  # the review: the mark before the why

    def test_a_first_pick_that_leaves_several_open_needs_ends_with_the_parts_step(self):
        # P1141, the PO's P829 walk: the first pick (board) left two needs open and printed no next: line
        import parts
        from spark.flow.now_follow_up import FlowFollowUp
        from spark.flow.show_flow import NEEDS_YOU, flow_and_guide, now_steps
        project = self.open_needs("board", "button", "light")
        lines, code = run_main(parts.main, ["--pick", str(project), "board=x-many", "--json"])
        said = json.loads(lines[0])
        self.assertEqual((code, said["status"]), (0, "ok"))
        self.assertEqual([(step["op"], step["argv"][2:], step["needs_person"]) for step in said["next"]],
                         [("pick", ["button=<part>", "light=<part>"], True)])
        other = self.open_needs("board", "button", "light")
        lines, code = run_main(parts.main, ["--pick", str(other), "board=x-many"])
        step = now_steps(other, *flow_and_guide(other))[0]
        self.assertEqual((code, lines[-1]), (0, FlowFollowUp().line(step)))
        self.assertIn("/parts.py --pick %s 'button=<part>' 'light=<part>'%s — " % (other.absolute(), NEEDS_YOU), lines[-1])

    def test_a_dry_run_pick_names_no_flow_step(self):
        import parts
        project = self.open_needs("soil")
        self.assertEqual([(step["op"], step["argv"][-1]) for step in show(project)[0]["next"]], [("pick", "soil=x-many")])
        lines, code = run_main(parts.main, ["--pick", str(project), "soil=x-many", "--dry-run", "--json"])
        self.assertEqual((code, json.loads(lines[0])["next"]), (0, []))

    def test_a_refused_pick_names_no_flow_step(self):
        import parts
        project = self.open_needs("soil")  # one open need: the flow names its pick, so the test sees the difference
        lines, code = run_main(parts.main, ["--pick", str(project), "soil=x-held", "--json"])
        said = json.loads(lines[0])
        self.assertEqual((code, said["status"], said["next"]), (1, "problems", []))
        self.assertTrue(show(project)[0]["next"])

    def test_a_kept_build_ends_with_its_own_steps_then_the_flow_s(self):
        from spark.build.stages import Stage
        project = an_image(a_firmware(a_built_project()))
        lines, code = a_kept_build(project, [Stage("build", OK, "fine")])
        steps = json.loads(lines[0])["next"]
        flow_steps = show(project)[0]["next"]
        self.assertEqual(code, 0)
        self.assertTrue(flow_steps)
        self.assertEqual(steps[-len(flow_steps):], flow_steps)
        self.assertEqual(steps[0]["op"], "look")  # the build's own step comes first
        self.assertEqual(list(json.loads(lines[0]))[-1], "next")
        text, _ = a_kept_build(project, [Stage("build", OK, "fine")], as_json=False)
        self.assertEqual(len([line for line in text if line.startswith("  next: ")]), len(steps))
        self.assertTrue(text[-1].startswith("  next: ") and "/run_scenario.py " in text[-1], text[-1])

    def test_a_kept_rebuild_at_the_deploy_names_the_flow_s_step_after_it(self):
        from spark.build.stages import Stage
        project = a_run(an_image(a_firmware(a_built_project())), "passed")
        self.assertEqual(show(project)[0]["data"]["guide"]["now"]["phase"], "deploy")
        lines, code = a_kept_build(project, [Stage("build", OK, "fine")])
        steps, flow_steps = json.loads(lines[0])["next"], show(project)[0]["next"]
        self.assertEqual((code, [step["op"] for step in flow_steps]), (0, ["run_scenario"]))
        self.assertEqual(steps[-len(flow_steps):], flow_steps)

    def test_a_build_that_could_not_run_names_no_flow_step(self):
        import check_spine
        project = a_firmware(a_built_project())
        lines, code = run_main(check_spine.main, [str(project / "none.json"), "--keep", str(project), "--json"])
        said = json.loads(lines[0])
        self.assertEqual((code, said["status"], said.get("next", [])), (2, "could-not-run", []))
        self.assertTrue(show(project)[0]["next"])

    def test_a_build_with_problems_names_no_flow_step(self):
        from spark.build import build_codes
        from spark.build.stages import Stage
        project = an_image(a_firmware(a_built_project()))
        lines, code = a_kept_build(project, [Stage("build", PROBLEMS, "broken", build_codes.DESIGN_NOT_BUILT)])
        said = json.loads(lines[0])
        self.assertEqual((code, said["status"], said.get("next", [])), (1, "problems", []))
        self.assertEqual([step["op"] for step in show(project)[0]["next"]], ["build-board"])

    def test_a_kept_build_that_kept_no_simulation_never_names_itself_again(self):
        # the review, refuter 1: with no sim/wokwi.toml kept, the flow names the build again with the run's own argv
        from spark.build.stages import Stage
        project = a_firmware(a_built_project())
        lines, code = a_kept_build(project, [Stage("build", OK, "fine")])
        flow_steps = show(project)[0]["next"]
        self.assertEqual([(step["op"], step["argv"]) for step in flow_steps],
                         [("build-board", [str(project / "requirements.json"), "--keep", str(project)])])
        self.assertEqual((code, [step["op"] for step in json.loads(lines[0])["next"]]), (0, ["look"]))

    def test_a_build_without_keep_names_no_flow_step(self):
        from spark.build.stages import Stage
        project = an_image(a_firmware(a_built_project()))
        lines, code = a_kept_build(project, [Stage("build", OK, "fine")], keep=False)
        self.assertEqual((code, [step["op"] for step in json.loads(lines[0])["next"]]), (0, ["look"]))
        self.assertEqual([step["op"] for step in show(project)[0]["next"]], ["run_scenario"])

    def test_the_line_marks_a_step_that_needs_the_person_s_yes_and_names_its_script(self):
        # round 2, amendment D: the brief step has needs_yes and no needs_person, and its op is its script's name
        from spark.flow.now_follow_up import FlowFollowUp
        from spark.flow.phase_steps import ANSWERS_PLACEHOLDER, brief_step
        from spark.flow.show_flow import NEEDS_YOU
        project = Path(tempfile.mkdtemp()) / "plant-alarm"
        step = brief_step(project)
        self.assertEqual((step.needs_yes, step.needs_person), (True, None))
        line = FlowFollowUp().line(step)
        self.assertIn("/init_project.py --project %s --answers %s%s — " % (project.absolute(), shlex.quote(ANSWERS_PLACEHOLDER), NEEDS_YOU), line)
        self.assertNotIn(NEEDS_YOU, FlowFollowUp().line(step._replace(needs_yes=False)))

    def test_every_op_a_flow_step_names_has_its_script(self):
        import inspect
        import types
        from spark.flow import offer_steps, phase_steps
        from spark.flow.now_follow_up import STEP_SCRIPTS
        project = a_firmware(a_built_project())
        given = {"project": project, "need": "soil", "pick_id": "x-many", "name": "A soil probe", "no_simulation": False,
                 "phase": types.SimpleNamespace(status=NS), "pairs": ["soil=x-many"], "why": "the why",
                 "guide": {"now": {"needs": ["soil"]}, "no_simulation": False}}
        ops = set()
        for module in (offer_steps, phase_steps):
            for name, builder in inspect.getmembers(module, inspect.isfunction):
                if builder.__module__ == module.__name__ and name.endswith(("_step", "_steps")):
                    made = builder(*[given[parameter] for parameter in inspect.signature(builder).parameters])
                    ops |= {step.op for step in (made if isinstance(made, list) else [made])}
        self.assertTrue({"pick", "requirements", "build-board", "needs-drop", "init_project", "run_scenario", "look"} <= ops, ops)
        for op in sorted(ops):
            with self.subTest(op=op):
                self.assertTrue((ROOT / "scripts" / STEP_SCRIPTS.get(op, op + ".py")).is_file())


def wrote_nothing():
    """Operation: a run that writes to `project` and changes nothing there, so two runs read the same flow (P1035 PR 2)."""
    from spark.core.operation import COMMON_ARGUMENTS, READS, WRITES, Operation
    from spark.core.result import OperationResult

    class WroteNothing(Operation):
        """Operation: a run that wrote to its project and changed nothing there."""

        name, arguments, effects = "wrote-nothing", (COMMON_ARGUMENTS["project"],), (READS, WRITES)

        def written_project(self, values):
            return Path(values["project"])

        def run(self, project, *, outside):
            return OperationResult({"wrote": "nothing"}, lines=["  wrote nothing"])
    return WroteNothing()


def refreshed_and_alone(project, follow_up):
    """(the result of a run in `project` with `follow_up`, and the same run first with a follow-up that refreshes nothing)."""
    from spark.core.cli import DEFAULT_RUN
    from spark.flow.now_follow_up import FlowFollowUp

    class NoRefresh(FlowFollowUp):
        """Strategy: the flow's follow-up without its refresh."""

        def refresh(self, project, result):
            return None

    def run(chosen):
        return run_operation(wrote_nothing(), {"project": project}, FakeOutsideWorld(), options=DEFAULT_RUN._replace(follow_up=chosen))
    alone = run(NoRefresh())
    return run(follow_up), alone


class ThePageRefreshTest(FlowTest):
    """P1035 PR 2 (the PO's D16): after an ok run that writes to a project that has a page.html, the flow's follow-up
    writes the page again on disk and never publishes it. Every failure of that write adds one diagnostics line, and the
    run's status, findings, next, data and lines stand. The store is TheFollowUpTest's two-probe store."""

    def setUp(self):
        super().setUp()
        (self.home / "catalog" / "x-unknown.json").unlink()
        (self.home / "drawer" / "unknown.json").unlink()

    def open_needs(self, *ids):
        return with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [{"id": one, "does": "sense", "what": "soil-moisture"} for one in ids])

    def with_page(self, needs=("soil", "wet")):
        project = self.open_needs(*needs)
        (project / "page.html").write_text("an old page", encoding="utf-8")
        return project

    def test_a_pick_writes_the_page_again_and_says_so_in_its_text_and_its_note(self):
        import parts
        from spark.flow.now_follow_up import REFRESHED
        from spark.flow.write_flow_page import FlowPageStore, write_page
        project = self.with_page()
        lines, code = run_main(parts.main, ["--pick", str(project), "soil=x-many", "--json"])
        said = json.loads(lines[0])
        page = (project / "page.html").read_text(encoding="utf-8")
        self.assertEqual((code, said["status"]), (0, "ok"))
        self.assertIn({"subject": "page.html", "sentence": REFRESHED}, said["notes"])
        self.assertNotEqual(page, "an old page")
        write_page(project, store=FlowPageStore())  # the flow's page of the project as it stands now
        self.assertEqual((project / "page.html").read_text(encoding="utf-8"), page)
        self.assertFalse((project / ".spark" / "page.json").exists())  # never published (D16)
        self.assertFalse((project / "page.html.part").exists())
        other = self.with_page()
        lines, code = run_main(parts.main, ["--pick", str(other), "soil=x-many"])
        self.assertEqual((code, lines[-1]), (0, "  " + REFRESHED))
        self.assertEqual(REFRESHED, "wrote page.html again: /spark:page publishes it")

    def test_a_project_with_no_page_gets_none(self):
        import parts
        project = self.open_needs("soil", "wet")
        with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()) as err:
            code = parts.main(["--pick", str(project), "soil=x-many", "--json"])
        self.assertEqual((code, json.loads(out.getvalue()).get("notes", [])), (0, []))
        self.assertNotIn("refresh:", err.getvalue())  # no page is no failure
        self.assertFalse((project / "page.html").exists())

    def test_a_dry_run_leaves_the_page_and_a_refused_pick_writes_it_again(self):
        # P1069 (D1): a run that writes is refreshed at any status but a crash, so the refused pick writes the page as the
        # project stands, with its note; the dry run writes nothing
        import parts
        from spark.flow.now_follow_up import REFRESHED
        from spark.flow.write_flow_page import FlowPageStore, write_page
        project = self.with_page()
        lines, code = run_main(parts.main, ["--pick", str(project), "soil=x-many", "--dry-run", "--json"])
        self.assertEqual((project / "page.html").read_text(encoding="utf-8"), "an old page")
        self.assertNotIn("page.html", json.dumps(json.loads(lines[0]).get("notes", [])))
        project = self.with_page()
        lines, code = run_main(parts.main, ["--pick", str(project), "soil=x-held", "--json"])
        said = json.loads(lines[0])
        self.assertNotEqual((code, said["status"]), (0, "ok"))
        self.assertIn({"subject": "page.html", "sentence": REFRESHED}, said.get("notes", []))
        page = (project / "page.html").read_text(encoding="utf-8")
        self.assertNotEqual(page, "an old page")
        write_page(project, store=FlowPageStore())  # the flow's page of the project as it stands now
        self.assertEqual((project / "page.html").read_text(encoding="utf-8"), page)

    def test_a_kept_build_that_failed_before_it_kept_anything_writes_the_page_again(self):
        # P1069 (B5, B9): the build could not run, so it kept nothing, and the page is the flow's page of the project as it
        # stands. The build's --json is a flat line with no notes, so its text run holds the refresh's line
        import check_spine
        from spark.flow.now_follow_up import REFRESHED
        from spark.flow.write_flow_page import FlowPageStore, write_page
        for as_json in (["--json"], []):
            with self.subTest(as_json=as_json):
                project = a_firmware(a_built_project())
                (project / "page.html").write_text("an old page", encoding="utf-8")
                lines, code = run_main(check_spine.main, [str(project / "none.json"), "--keep", str(project)] + as_json)
                self.assertEqual(code, 2)
                if as_json:
                    self.assertEqual(json.loads(lines[0])["status"], "could-not-run")
                else:
                    self.assertEqual(lines[-1], "  " + REFRESHED)
                page = (project / "page.html").read_text(encoding="utf-8")
                self.assertNotEqual(page, "an old page")
                write_page(project, store=FlowPageStore())
                self.assertEqual((project / "page.html").read_text(encoding="utf-8"), page)

    def test_a_kept_build_keeps_its_own_page_and_is_not_written_again(self):
        # round 2, amendment A (decision H, measured): write_page after the kept build would call the drawn pictures
        # "Not drawn here", so the page the build wrote with its pictures stands
        from spark.build.stages import Stage
        from spark.flow import flow_codes
        from spark.flow.now_follow_up import REFRESHED
        project = an_image(a_firmware(a_built_project()))
        a_kept_build(project, [Stage("build", OK, "fine")])
        kept = (project / "page.html").read_text(encoding="utf-8")
        self.assertNotIn(flow_codes.NOT_DRAWN_HERE, kept)
        lines, code = a_kept_build(project, [Stage("build", OK, "fine")], as_json=False)
        self.assertEqual(code, 0)
        self.assertNotIn("  " + REFRESHED, lines)
        self.assertNotIn(flow_codes.NOT_DRAWN_HERE, (project / "page.html").read_text(encoding="utf-8"))

    def test_the_run_that_kept_its_page_is_read_from_its_kept_entries(self):
        from spark.core.result import OperationResult
        from spark.flow.now_follow_up import kept_its_page
        entry = {"file": "/opt/someone/p/page.html", "did": "wrote"}
        self.assertEqual([kept_its_page(OperationResult(data)) for data in (None, [1], {}, {"kept": [{"file": "/p/board.tsx"}]},
                                                                            {"kept": [entry]}, {"kept": [dict(entry, did="removed")]})],
                         [False, False, False, False, True, True])

    def assert_one_line_and_the_result_stands(self, project, follow_up, raised):
        from spark.core.cli import REFRESH_FAILED_MESSAGE
        result, alone = refreshed_and_alone(project, follow_up)
        self.assertEqual(result._replace(diagnostics=()), alone._replace(diagnostics=()))
        self.assertEqual(list(result.diagnostics), list(alone.diagnostics) + [REFRESH_FAILED_MESSAGE % (raised, "page.html")])
        self.assertTrue(result.next)  # the flow's step is there, so the comparison holds something
        self.assertFalse((project / "page.html.part").exists())

    def test_a_page_html_that_is_a_folder_a_fifo_or_a_link_is_not_written(self):
        import stat
        from spark.flow.now_follow_up import FlowFollowUp
        person = Path(tempfile.mkdtemp()) / "a-file-of-the-person.html"
        person.write_text("the person's own", encoding="utf-8")
        for name, make, kind in (("folder", Path.mkdir, stat.S_ISDIR), ("fifo", os.mkfifo, stat.S_ISFIFO),
                                 ("link", lambda page: page.symlink_to(person), stat.S_ISLNK)):
            with self.subTest(name):
                project = self.open_needs("soil")  # one open need: the flow names its pick
                make(project / "page.html")
                self.assert_one_line_and_the_result_stands(project, FlowFollowUp(), "PageNotRegularError")
                self.assertTrue(kind((project / "page.html").lstat().st_mode))
        self.assertEqual(person.read_text(encoding="utf-8"), "the person's own")

    def test_a_link_at_page_html_part_is_refused_and_the_persons_file_is_untouched(self):
        # P1054 (#1551): the store's .part is made new, so a link planted there is refused, never written through
        from spark.flow.write_flow_page import PART_FIX
        person = Path(tempfile.mkdtemp()) / "a-file-of-the-person.html"
        person.write_text("the person's own", encoding="utf-8")
        project = self.open_needs("soil")
        (project / "page.html.part").symlink_to(person)
        said, code = run_main(flow.main, ["page", "--project", str(project), "--json"])
        envelope = json.loads(said[0])
        self.assertEqual((code, envelope["status"]), (2, "could-not-run"))
        [item] = envelope["unchecked"]
        self.assertEqual((item["code"], item["fix"]), ("page_not_written", PART_FIX % "page.html"))
        self.assertIn("page.html.part is in the way", item["sentence"])  # the answer masks the project's path
        self.assertEqual(person.read_text(encoding="utf-8"), "the person's own")
        self.assertFalse((project / "page.html").is_symlink())
        self.assertTrue((project / "page.html.part").is_symlink())

    def test_a_link_at_page_html_part_is_one_line_after_a_pick_and_the_result_stands(self):
        # P1054 (#1551): assert_one_line_and_the_result_stands, but the planted link stays where it was
        from spark.core.cli import REFRESH_FAILED_MESSAGE
        from spark.flow.now_follow_up import FlowFollowUp
        person = Path(tempfile.mkdtemp()) / "a-file-of-the-person.html"
        person.write_text("the person's own", encoding="utf-8")
        project = self.with_page(("soil",))  # one open need: the flow names its pick; the refresh writes an old page only
        (project / "page.html.part").symlink_to(person)
        result, alone = refreshed_and_alone(project, FlowFollowUp())
        self.assertEqual(result._replace(diagnostics=()), alone._replace(diagnostics=()))
        self.assertEqual(list(result.diagnostics), list(alone.diagnostics) + [REFRESH_FAILED_MESSAGE % ("PartTakenError", "page.html")])
        self.assertTrue(result.next)
        self.assertEqual(person.read_text(encoding="utf-8"), "the person's own")
        self.assertEqual(((project / "page.html").read_text(encoding="utf-8"), (project / "page.html").is_symlink()), ("an old page", False))
        self.assertTrue((project / "page.html.part").is_symlink())

    def test_a_read_only_folder_a_full_disk_or_a_renderer_that_raises_leaves_the_old_page(self):
        from fakes import FakeFullDiskPageStore, FakePageRenderer
        from spark.flow.now_follow_up import FlowFollowUp
        for name, follow_up, raised in (("full disk", FlowFollowUp(store=FakeFullDiskPageStore()), "OSError"),
                                        ("renderer", FlowFollowUp(renderer=FakePageRenderer(raises=RuntimeError)), "RuntimeError"),
                                        ("half written", FlowFollowUp(renderer=FakePageRenderer("a page \ud800")), "UnicodeEncodeError"),
                                        ("read-only", FlowFollowUp(), "PermissionError")):
            with self.subTest(name):
                project = self.with_page(("soil",))  # one open need: the flow names its pick
                if name == "read-only":
                    project.chmod(0o555)
                    self.addCleanup(project.chmod, 0o755)
                self.assert_one_line_and_the_result_stands(project, follow_up, raised)
                self.assertEqual((project / "page.html").read_text(encoding="utf-8"), "an old page")

    def test_a_secrets_file_that_does_not_parse_leaves_the_old_page_and_shows_none_of_its_text(self):
        # P1060 D5: write_page refuses, and the core says so in one diagnostics line that names the refusal's class only
        from spark.flow.now_follow_up import FlowFollowUp
        project = self.with_page(("soil",))  # one open need: the flow names its pick
        (project / "firmware").mkdir()
        (project / "firmware" / "wifi_secrets.py").write_text('WIFI_PASSWORD = "%s\n' % HALF_TYPED, encoding="utf-8")
        self.assert_one_line_and_the_result_stands(project, FlowFollowUp(), "SecretsUnreadableError")
        self.assertEqual((project / "page.html").read_text(encoding="utf-8"), "an old page")
        self.assertNotIn(HALF_TYPED, repr(refreshed_and_alone(project, FlowFollowUp())[0]))

    def test_a_page_that_is_not_utf_8_is_written_over_by_flow_page_and_by_the_refresh(self):
        # the review, refuter must-fix: main wrote over such a page, so the whole-file write must not compare it first
        import parts
        from spark.flow.now_follow_up import REFRESHED
        project = self.open_needs("soil", "wet")
        (project / "page.html").write_bytes(b"\xff\xfeOLD")
        said, code = run_main(flow.main, ["page", "--project", str(project), "--json"])
        self.assertEqual((code, json.loads(said[0])["status"]), (0, "ok"))
        self.assertIn("<html", (project / "page.html").read_text(encoding="utf-8").lower())
        (project / "page.html").write_bytes(b"\xff\xfeOLD")
        lines, code = run_main(parts.main, ["--pick", str(project), "soil=x-many", "--json"])
        self.assertEqual(code, 0)
        self.assertIn({"subject": "page.html", "sentence": REFRESHED}, json.loads(lines[0])["notes"])
        self.assertIn("<html", (project / "page.html").read_text(encoding="utf-8").lower())

    def test_the_page_store_writes_a_whole_page_or_none(self):
        # round 2, amendment B: a write that fails halfway leaves the old page whole, as store.write_file does
        from spark.flow.write_flow_page import FlowPageStore
        project = self.with_page()
        with self.assertRaises(UnicodeEncodeError):
            FlowPageStore().write(project, "page.html", "a page \ud800")
        self.assertEqual(((project / "page.html").read_text(encoding="utf-8"), (project / "page.html.part").exists()), ("an old page", False))
        self.assertEqual(FlowPageStore().write(project, "page.html", "a new page"), project / "page.html")
        self.assertEqual((project / "page.html").read_text(encoding="utf-8"), "a new page")


#: The moment of a made-up board log, as `BoardLog` writes it (P1043), and a newer one.
LOGGED_AT = datetime.datetime(2026, 11, 23, 14, 9, 49, tzinfo=datetime.timezone(datetime.timedelta(hours=1)))
LOG_NAME = "2026-11-23T14-09-49"
#: The sentences the bench made in real board logs (the refuter's quotes, P1043's plan), with made-up tool text.
FILES_UNREAD_SENTENCE = "mpremote could not read the board's files: mpremote.transport.TransportError: could not enter raw repl"
NOT_STARTED_SENTENCE = "mpremote could not start the firmware: OSError: [Errno 6] Device not configured"
LOST_SENTENCE = ("the firmware printed 'ready', then mpremote lost the board (OSError: [Errno 6] Device not configured), "
                 "and spark found no deepsleep call in firmware/")
SEEN_SENTENCE = "the firmware printed 'ready' and the board's 1 files match the image"
#: The words of the deploy's says line (P1043): brief D10's for a run with no read-back, exactly.
NO_READ_BACK = "written by the flasher, nothing read back, start not seen"


def a_deploy_project():
    """A built project whose firmware a passed run tested on the image it holds now, so the deploy is the phase now and
    every other phase is ok or has no status: the exit says the deploy's status alone."""
    return a_run(an_image(a_firmware(a_built_project())), "passed")


def a_board_log(project, verdict, sentence, image=b"an image", reason=None, name=LOG_NAME, **kw):
    """A board log in sim/runs/board/<name>.log in the real layout (`BoardLog`), with made-up values."""
    from spark.bench.board_log import BoardLog
    folder = project / "sim" / "runs" / "board"
    folder.mkdir(parents=True, exist_ok=True)
    log = BoardLog(LOGGED_AT, "/dev/cu.usbmodem101", hashlib.sha256(image).hexdigest(), "facts file spark.json sha256: f",
                   verdict, sentence, "what the board printed\n", "passed", reason)._replace(**kw)
    (folder / (name + ".log")).write_text(log.text())
    return project


def deploy_of(said):
    """The deploy phase's dict in an envelope."""
    return next(phase for phase in said["data"]["phases"] if phase["phase"] == "deploy")


def logged(words, *more, count=1, image=b"an image"):
    """The deploy's says line for a log of LOGGED_AT on `image`: the verdict's words, more sentences, then the count."""
    return " ".join(["Last deploy 2026-11-23T14:09:49+01:00, image %s: %s." % (hashlib.sha256(image).hexdigest()[:12], words),
                     *more, "%d deploy%s logged." % (count, "" if count == 1 else "s")])


class TheDeployReaderTest(FlowTest):
    """P1043 (#1533): the deploy phase reads the newest board log in sim/runs/board/: its time, image, verdict and cause.
    Only ready seen on the image the project holds now is ok, with a tick. Ready unknown is partial, ready not seen is
    problems, and an image that changed since is stale. A flash that did not finish is problems (P1092). A tool's text, the port and the console never reach an answer."""

    def test_no_board_log_keeps_today_s_phase_and_no_deploy_data(self):
        said, code = show(a_deploy_project())
        self.assertEqual((code, deploy_of(said)["status"], deploy_of(said)["says"]), (0, "not-started", [
            "Ask Claude to look at the board first (/spark:deploy).", "Claude then gives you the deploy line. Run it in your "
            "terminal and type yes, unless you gave Claude a standing yes for this board."]))
        self.assertIsNone(said["data"]["deploy"])
        self.assertEqual(said["data"]["guide"]["now"]["phase"], "deploy")

    def test_ready_seen_on_the_image_now_is_ok_with_a_tick_and_nothing_is_now(self):
        said, code = show(a_board_log(a_deploy_project(), "ready seen", SEEN_SENTENCE))
        self.assertEqual((code, deploy_of(said)["status"], deploy_of(said)["mark"]), (0, "ok", "✓"))
        self.assertEqual(deploy_of(said)["says"], [logged("written by the flasher, files read back, ready seen")])
        self.assertEqual((said["data"]["guide"]["now"], said["data"]["stands_at"], said["next"]), (None, None, []))
        self.assertEqual(said["data"]["guide"]["done"][-1], "deploy")

    def test_ready_unknown_with_no_read_back_says_brief_d10_s_words_and_is_partial(self):
        said, code = show(a_board_log(a_deploy_project(), "ready unknown", FILES_UNREAD_SENTENCE))
        self.assertEqual((code, deploy_of(said)["status"], deploy_of(said)["mark"]), (0, "partial", "◐"))
        self.assertEqual(deploy_of(said)["says"], [logged(NO_READ_BACK, "Cause in the log: spark did not reach the board to read its files.")])
        self.assertEqual((said["problems"], said["unchecked"]), ([], []))
        self.assertEqual([step["op"] for step in said["next"]], ["look"])
        self.assertIs(said["data"]["deploy"]["read_back"], False)

    def test_ready_unknown_after_the_files_were_read_says_start_not_seen_once(self):
        said, _ = show(a_board_log(a_deploy_project(), "ready unknown", NOT_STARTED_SENTENCE))
        says = deploy_of(said)["says"]
        self.assertEqual(says, [logged("written by the flasher, files read back, start not seen",
                                       "Cause in the log: the command that starts the firmware failed.")])
        self.assertEqual([line.count("start not seen") for line in lines_of(a_board_log(a_deploy_project(), "ready unknown",
                                                                                         NOT_STARTED_SENTENCE))
                          if "start not seen" in line], [1])
        self.assertIs(said["data"]["deploy"]["read_back"], True)

    def test_a_board_lost_after_ready_says_ready_was_printed_and_never_that_the_start_was_not_seen(self):
        said, _ = show(a_board_log(a_deploy_project(), "ready unknown", LOST_SENTENCE, reason="board_lost"))
        self.assertEqual(deploy_of(said)["says"], [logged(
            "written by the flasher, files read back, ready printed, then the board was lost",
            "Cause in the log: spark found no deepsleep call in firmware/, so it does not count the ready.")])
        self.assertNotIn("start not seen", " ".join(deploy_of(said)["says"]))
        self.assertEqual((deploy_of(said)["status"], said["data"]["deploy"]["read_back"]), ("partial", True))

    def test_a_port_gone_or_download_mode_says_start_not_confirmed_and_never_nothing_read_back(self):
        for reason, sentence, words in (("port_gone", "the board's port is gone: press its RESET once", "the board's port was gone"),
                                        ("download_mode_stayed", "the board still waits in download mode after 60 s: press its RESET",
                                         "the board stayed in download mode")):
            with self.subTest(reason=reason):
                said, _ = show(a_board_log(a_deploy_project(), "ready unknown", sentence, reason=reason))
                self.assertEqual(deploy_of(said)["says"], [logged("written by the flasher, start not confirmed", "Cause in the log: %s." % words)])
                self.assertIsNone(said["data"]["deploy"]["read_back"])
                self.assertNotIn("nothing read back", json.dumps(said))

    def test_an_unknown_start_is_cause_not_recorded_and_its_cause_is_null(self):
        said, _ = show(a_board_log(a_deploy_project(), "ready unknown", "the board said something new: x"))
        self.assertEqual(deploy_of(said)["says"], [logged("written by the flasher, start not confirmed", "Cause not recorded.")])
        self.assertEqual((said["data"]["deploy"]["cause"], said["data"]["deploy"]["read_back"]), (None, None))

    def test_the_reason_line_wins_over_the_start_and_is_read_from_line_4_only(self):
        project = a_board_log(a_deploy_project(), "ready unknown", FILES_UNREAD_SENTENCE, reason="board_lost")
        self.assertEqual(show(project)[0]["data"]["deploy"]["cause"], "board_lost")
        for heard, reason in (("reason: board_lost\n", None), ("", "a_code_spark_never_wrote")):
            with self.subTest(heard=heard, reason=reason):
                project = a_board_log(a_deploy_project(), "ready unknown", FILES_UNREAD_SENTENCE, reason=reason, heard=heard)
                self.assertEqual(show(project)[0]["data"]["deploy"]["cause"], "files_unread")
        project = a_board_log(a_deploy_project(), "ready unknown", "an unknown start: x", reason="a_code_spark_never_wrote")
        self.assertIsNone(show(project)[0]["data"]["deploy"]["cause"])

    def test_the_newest_log_by_name_wins_and_the_count_says_how_many(self):
        older, newer = "2026-11-23T14-00-00", "2026-11-23T15-00-00"
        project = a_board_log(a_board_log(a_deploy_project(), "ready seen", SEEN_SENTENCE, name=older),
                              "ready unknown", FILES_UNREAD_SENTENCE, name=newer)
        said, _ = show(project)
        self.assertEqual(deploy_of(said)["status"], "partial")
        self.assertTrue(deploy_of(said)["says"][-1].endswith("2 deploys logged."), deploy_of(said)["says"])
        project = a_board_log(a_board_log(a_deploy_project(), "ready unknown", FILES_UNREAD_SENTENCE, name=older),
                              "ready seen", SEEN_SENTENCE, name=newer)
        self.assertEqual(deploy_of(show(project)[0])["status"], "ok")

    def test_a_log_of_another_image_is_stale_and_says_so_first(self):
        said, code = show(a_board_log(a_deploy_project(), "ready seen", SEEN_SENTENCE, image=b"another image"))
        self.assertEqual((code, deploy_of(said)["status"], deploy_of(said)["mark"]), (0, "stale", "↻"))
        self.assertEqual(deploy_of(said)["says"], [  # one line: the opener, then the log (the review of #1579)
            "The last deploy wrote a different image from the one this project has now. "
            + logged("written by the flasher, files read back, ready seen", image=b"another image")])
        self.assertFalse([line for line in lines_of(a_board_log(a_deploy_project(), "ready seen", SEEN_SENTENCE, image=b"another image"))
                          if ".," in line], "no sentence ends before a comma")
        self.assertEqual(said["data"]["deploy"]["fact"], "image-differs")

    def test_no_image_now_is_stale_and_a_firmware_line_spark_cannot_use_could_not_run(self):
        project = a_board_log(a_deploy_project(), "ready seen", SEEN_SENTENCE)
        (project / "sim" / "image.bin").unlink()
        said, _ = show(project)
        self.assertEqual((deploy_of(said)["status"], deploy_of(said)["says"][0].split(" Last deploy")[0], said["data"]["deploy"]["fact"]),
                         ("stale", "This project has no image now.", "no-image"))
        project = a_board_log(a_deploy_project(), "ready seen", SEEN_SENTENCE)
        (project / "sim" / "wokwi.toml").write_text('[wokwi]\nversion = 1\nfirmware = 42\n')
        said, _ = show(project)  # the simulate has problems for the same line, so the exit is 1
        self.assertEqual((statuses(said)["simulate"], deploy_of(said)["status"]), ("problems", "could-not-run"))
        self.assertTrue(deploy_of(said)["says"][0].startswith("sim/wokwi.toml"), deploy_of(said)["says"])
        self.assertIsNone(said["data"]["deploy"])

    def test_ready_not_seen_is_problems_with_one_finding_and_stale_wins_over_it(self):
        project = a_board_log(a_deploy_project(), "ready not seen", "the firmware stopped with an error: Traceback ...")
        said, code = show(project)
        self.assertEqual((code, deploy_of(said)["status"], deploy_of(said)["mark"]), (1, "problems", "✗"))
        self.assertEqual([(problem["subject"], problem["code"]) for problem in said["problems"]], [("deploy", "phase_problems")])
        self.assertEqual(deploy_of(said)["says"], [logged("written by the flasher, files read back, ready not seen",
                                                          "Cause in the log: the firmware stopped with an error.")])
        os.utime(project / "firmware" / "main.py", (1_700_007_200, 1_700_007_200))
        said, _ = show(project)
        self.assertEqual((deploy_of(said)["status"], said["data"]["deploy"]["fact"]), ("stale", "firmware-newer"))
        self.assertIn("ready not seen", deploy_of(said)["says"][-1])  # the says line keeps the verdict

    def test_a_log_with_no_verdict_line_or_a_verdict_spark_never_writes_could_not_run(self):
        for case, verdict in (("no verdict line", "a word"), ("ready not read", "ready not read")):
            with self.subTest(case=case):
                said, code = show(a_board_log(a_deploy_project(), verdict, "x"))
                self.assertEqual((code, deploy_of(said)["status"]), (2, "could-not-run"))
                self.assertEqual([item["subject"] for item in said["unchecked"]], ["deploy"])
                self.assertIn("sim/runs/board/%s.log cannot be read" % LOG_NAME, said["unchecked"][0]["sentence"])

    def test_nothing_private_or_foreign_reaches_the_answer(self):
        project = a_deploy_project()
        (project / "sim" / "runs" / "board").mkdir(parents=True)
        shutil.copy(ROOT / "tests" / "data" / "board_log" / ("%s.log" % LOG_NAME), project / "sim" / "runs" / "board")
        a_board_log(project, "ready unknown", "mpremote could not start the firmware: MARK-TOOL TransportError /dev/cu.x",
                    name="2026-11-23T15-00-00", port="MARK-PORT", facts_line="facts file: not written: MARK-FACTS",
                    heard="MARK-HEARD what the console printed\n")
        said, _ = show(project)
        shown = json.dumps([said["data"]["phases"], said["data"]["guide"], said["data"]["deploy"]]) + "\n".join(lines_of(project))
        for mark in ("MARK-PORT", "MARK-FACTS", "MARK-HEARD", "MARK-TOOL", "TransportError", "/dev/", str(project)):
            with self.subTest(mark=mark):
                self.assertNotIn(mark, shown)

    def test_an_old_log_of_the_c6_sequence_says_nothing_false(self):
        # the review of #1579: a log from before the reason line. A read again may follow a first read that read the files,
        # so its "could not read the board's files" gives no cause; a lost board after ready keeps its own words
        project = a_board_log(a_deploy_project(), "ready unknown", FILES_UNREAD_SENTENCE,
                              heard="the first read: ready unknown: mpremote could not start the firmware: x\nread again\n")
        said, _ = show(project)
        self.assertEqual(deploy_of(said)["says"], [logged("written by the flasher, start not confirmed", "Cause not recorded.")])
        self.assertEqual((said["data"]["deploy"]["cause"], said["data"]["deploy"]["read_back"]), (None, None))
        said, _ = show(a_board_log(a_deploy_project(), "ready unknown", LOST_SENTENCE))
        self.assertEqual((said["data"]["deploy"]["cause"], said["data"]["deploy"]["read_back"]), ("board_lost", True))
        self.assertNotIn("start not", deploy_of(said)["says"][0])

    def test_ready_not_seen_read_the_files_back_whatever_its_cause(self):
        # the review of #1579: only a read of the files gives ready not seen, so read_back agrees with the says line
        said, _ = show(a_board_log(a_deploy_project(), "ready not seen", "the board's /main.py is not the files of the image"))
        self.assertEqual((said["data"]["deploy"]["cause"], said["data"]["deploy"]["read_back"]), (None, True))
        self.assertIn("files read back", deploy_of(said)["says"][0])

    def test_a_log_that_lands_between_the_reads_of_one_run_changes_nothing_of_it(self):
        # the review of #1579: the phase, the guide and data.deploy take one DeployState, read once per run
        from spark.flow.phase_readers import READERS, IdeaReader

        class Lander(IdeaReader):
            PHASE = "lander"

            def read(self, project):
                (project / "sim" / "runs" / "board" / "2026-11-23T23-00-00.log").write_text("not a board log\n")
                return self.phase(None, ["landed"])
        project = a_board_log(a_deploy_project(), "ready seen", SEEN_SENTENCE, image=b"another image")
        result = ShowFlow(readers=READERS + (Lander(),)).run(project, outside=None)
        self.assertEqual((deploy_of({"data": result.data})["status"], result.data["deploy"]["fact"]), ("stale", "image-differs"))
        self.assertTrue(result.data["guide"]["now"]["says"].startswith("The last deploy wrote a different image"))

    def test_the_deploy_data_holds_the_six_fields_of_the_newest_log(self):
        said, _ = show(a_board_log(a_deploy_project(), "ready unknown", NOT_STARTED_SENTENCE))
        self.assertEqual(said["data"]["deploy"], {"at": "2026-11-23T14:09:49+01:00", "image": hashlib.sha256(b"an image").hexdigest(),
                                                  "verdict": "ready unknown", "cause": "firmware_not_started",
                                                  "fact": "current", "read_back": True})


#: The guide's line when no phase is open (P1043).
NOTHING_WAITS = ("Nothing is waiting on you: the last deploy started the image this project holds now. Tell Claude what to "
                 "change next.")
NO_START_NOW = ("Spark could not confirm that the firmware started after the last deploy. Ask Claude to look at the board with "
                "you. If the look asks for it, run the deploy again in your terminal.")


class TheDeployNowTest(FlowTest):
    """P1043: who acts on an open deploy, and the one sentence when nothing is open. Each NOW says the job in words, never
    what the board does now; a lost board after ready says what spark saw and never that the start was not seen."""

    def now(self, said):
        return said["data"]["guide"]["now"]

    def test_a_deploy_that_saw_ready_leaves_nothing_open_and_one_sentence_says_so(self):
        project = a_board_log(a_deploy_project(), "ready seen", SEEN_SENTENCE)
        said, _ = show(project)
        self.assertEqual((self.now(said), said["data"]["guide"]["no_open_phase"]), (None, NOTHING_WAITS))
        self.assertEqual(lines_of(project)[0], "  " + NOTHING_WAITS)

    def test_each_open_deploy_has_its_own_now(self):
        lost = "Spark saw ready after the last deploy, then lost the board, and cannot tell from here whether the firmware still runs. "
        # P1122: a partial deploy's sentence asks Claude to look at the board; a deploy with problems asks for the log
        look, log = "look-at-board", None
        for name, verdict, sentence, reason, now, chat in (
                ("no read-back", "ready unknown", FILES_UNREAD_SENTENCE, None, NO_START_NOW, look),
                ("not started", "ready unknown", NOT_STARTED_SENTENCE, None, NO_START_NOW, look),
                ("lost", "ready unknown", LOST_SENTENCE, "board_lost",
                 lost + "If your gadget works, nothing is wrong. Else ask Claude to look at the board with you.", look),
                ("port gone", "ready unknown", "the board's port is gone: x", "port_gone",
                 "After the last deploy, the board's port was gone. Ask Claude to look at the board with you.", look),
                ("download mode", "ready unknown", "x", "download_mode_stayed",
                 "After the last deploy, the board stayed in download mode. Ask Claude to look at the board with you.", look),
                ("not recorded", "ready unknown", "the board said something new: x", None,
                 "The log does not say whether the firmware started after the last deploy. Ask Claude to look at the board with you.", look),
                ("firmware error", "ready not seen", "the firmware stopped with an error: Traceback ...", None,
                 "After the last deploy, the firmware stopped with an error. Ask Claude to go through the board log with you.", log),
                ("old files differ", "ready not seen", "the board's /main.py is not the files of the image", None,
                 "After the last deploy, spark did not see ready. Ask Claude to go through the board log with you.", log)):
            with self.subTest(name=name):
                said, _ = show(a_board_log(a_deploy_project(), verdict, sentence, reason=reason))
                self.assertEqual(self.now(said), {"phase": "deploy", "by": ["your terminal"], "says": now, "offer": None,
                                                  "chat_offer": chat, "needs": [], "steps": None, "with_wiring": True})
                self.assertEqual([step["op"] for step in said["next"]], ["look"])
                self.assertIsNone(said["data"]["guide"]["no_open_phase"])

    def test_a_lost_board_never_says_spark_did_not_see_the_firmware_start(self):
        project = a_board_log(a_deploy_project(), "ready unknown", LOST_SENTENCE, reason="board_lost")
        self.assertNotIn("did not see the firmware start", json.dumps(show(project)[0]) + "\n".join(lines_of(project)))

    def test_a_stale_deploy_names_who_acts_by_its_fact(self):
        project = a_board_log(a_deploy_project(), "ready seen", SEEN_SENTENCE, image=b"another image")
        self.assertEqual((self.now(show(project)[0])["by"], self.now(show(project)[0])["says"]), (["your terminal"],
                         "The last deploy wrote a different image from the one this project has now. Ask Claude to look at "
                         "the board, then run the deploy line in your terminal."))
        # with no image, a project with a Wokwi model has the simulate first: a board with none reaches the deploy
        project = a_board_log(an_image(a_firmware(a_project_built_with_no_simulation())), "ready seen", SEEN_SENTENCE)
        (project / "sim" / "image.bin").unlink()
        self.assertEqual((self.now(show(project)[0])["by"], self.now(show(project)[0])["says"]), (["claude"],
                         "This project has no image now. Ask Claude to make the image and to look at the board. Then run "
                         "the deploy line in your terminal."))

    def test_firmware_newer_than_the_deployed_image_is_claude_s_first_with_no_tick(self):
        # test 8, P1043-D4: on a board Wokwi has no model of, the simulate is counted as done, so the deploy is now
        for verdict, sentence in (("ready seen", SEEN_SENTENCE), ("ready unknown", FILES_UNREAD_SENTENCE)):
            with self.subTest(verdict=verdict):
                project = a_board_log(an_image(a_firmware(a_project_built_with_no_simulation())), verdict, sentence)
                os.utime(project / "firmware" / "main.py", (1_700_007_200, 1_700_007_200))
                said, _ = show(project)
                self.assertEqual((deploy_of(said)["status"], deploy_of(said)["mark"]), ("stale", "↻"))
                self.assertEqual((self.now(said)["phase"], self.now(said)["by"], self.now(said)["says"]), ("deploy", ["claude"],
                                 "Your firmware changed after the image that the last deploy wrote. Ask Claude to make the "
                                 "image again and to look at the board. Then run the deploy line in your terminal."))
                self.assertNotIn("deploy", said["data"]["guide"]["done"])

    def test_with_a_model_the_simulate_s_image_older_comes_first(self):
        project = a_board_log(a_deploy_project(), "ready seen", SEEN_SENTENCE)
        os.utime(project / "firmware" / "main.py", (1_700_007_200, 1_700_007_200))
        said, _ = show(project)
        self.assertEqual((self.now(said)["phase"], deploy_of(said)["status"]), ("simulate", "stale"))
        self.assertEqual(self.now(said)["says"], "Your firmware changed after the image. Ask Claude to make the image again, then run the scenario.")

    def test_no_open_phase_is_null_whenever_now_is_set_and_with_other_readers(self):
        # test 14: a phase list a test swaps in, whose now is None, gets no sentence: only an ok deploy says nothing waits
        from spark.flow.phase_readers import IdeaReader
        project = Path(tempfile.mkdtemp())

        class Done(IdeaReader):
            def read(self, project):
                return self.phase(OK, ["done"])
        phases, guide = flow_and_guide(project, (Done(),))
        self.assertEqual((guide["now"], guide["no_open_phase"]), (None, None))
        for each in (a_deploy_project(), a_board_log(a_deploy_project(), "ready unknown", FILES_UNREAD_SENTENCE)):
            with self.subTest(project=each):
                self.assertIsNone(show(each)[0]["data"]["guide"]["no_open_phase"])


#: The bench's sentence in a board log of a flash that did not finish (P1092), and the flow's words for it.
NOT_FINISHED_SENTENCE = "a flash command failed, so the board may be erased and not written"
FLASH_NOT_FINISHED_WORDS = "flash not finished, nothing read back, the board may be erased"
NOT_FINISHED_NOW = ("The last flash did not finish, so the board may be erased. The board log says what failed. Ask Claude "
                    "to look at the board with you, then run the deploy again in your terminal.")


def a_not_finished_log(project, reason="flash_failed", **kw):
    """A board log of a flash that did not finish after the yes (P1092), in the layout the bench writes."""
    return a_board_log(project, "flash not finished", NOT_FINISHED_SENTENCE, reason=reason,
                       facts_line="facts file: not written: the flash did not finish", **kw)


class TheFlashNotFinishedTest(FlowTest):
    """P1092 tests 6 to 8: a board log of a flash that did not finish after the yes is problems: the board may be erased.
    It wins over a stale image, because each stale opener speaks of the image that the last deploy wrote, and nothing was
    read back. The newest log wins, either way."""

    def test_a_flash_not_finished_is_problems_and_says_the_board_may_be_erased(self):
        for reason, words in (("flash_failed", "a flash command failed"), ("grant_ended", "your yes ended before the erase's retry")):
            with self.subTest(reason=reason):
                said, code = show(a_not_finished_log(a_deploy_project(), reason))
                self.assertEqual((code, deploy_of(said)["status"], deploy_of(said)["mark"]), (1, "problems", "✗"))
                self.assertEqual(deploy_of(said)["says"], [logged(FLASH_NOT_FINISHED_WORDS, "Cause in the log: %s." % words)])
                self.assertEqual(said["data"]["deploy"], {"at": "2026-11-23T14:09:49+01:00", "image": hashlib.sha256(b"an image").hexdigest(),
                                                          "verdict": "flash not finished", "cause": reason, "fact": "current",
                                                          "read_back": False})
                self.assertEqual((said["data"]["guide"]["now"]["by"], said["data"]["guide"]["now"]["says"]),
                                 (["your terminal"], NOT_FINISHED_NOW))

    def test_a_crash_and_a_ctrl_c_in_the_flash_have_their_own_words(self):
        # P1096 test 6: the two new causes of a flash that did not finish
        for reason, words in (("crash", "spark crashed during the deploy"), ("interrupted", "a Ctrl-C interrupted the deploy")):
            with self.subTest(reason=reason):
                said, _ = show(a_not_finished_log(a_deploy_project(), reason))
                self.assertEqual(deploy_of(said)["says"], [logged(FLASH_NOT_FINISHED_WORDS, "Cause in the log: %s." % words)])
                self.assertIs(said["data"]["deploy"]["read_back"], False)

    def test_a_verify_that_did_not_finish_is_partial_and_says_the_start_was_not_confirmed(self):
        # P1110 test 5: the flash finished, so the board log says ready unknown, and nothing claims a read-back either way
        from spark.flow.flow_codes import DEPLOY_NO_START_NOW, UNSURE_WORDS
        for reason, words in (("crash", "spark crashed during the deploy"), ("interrupted", "a Ctrl-C interrupted the deploy")):
            with self.subTest(reason=reason):
                said, _ = show(a_board_log(a_deploy_project(), "ready unknown", "spark crashed while it read the board after the flash",
                                           reason=reason, facts_line="facts file: not known: the read after the flash did not finish"))
                self.assertEqual((deploy_of(said)["status"], said["data"]["deploy"]["read_back"]), ("partial", None))
                self.assertEqual(deploy_of(said)["says"], [logged(UNSURE_WORDS, "Cause in the log: %s." % words)])
                self.assertEqual(said["data"]["guide"]["now"]["says"], DEPLOY_NO_START_NOW)

    def test_it_wins_over_a_stale_image_and_the_fact_is_still_said_in_the_data(self):
        other = a_not_finished_log(a_deploy_project(), image=b"another image")
        # on a board Wokwi has no model of, the simulate is counted as done, so the deploy's NOW is the guide's
        newer = a_not_finished_log(an_image(a_firmware(a_project_built_with_no_simulation())))
        os.utime(newer / "firmware" / "main.py", (1_700_007_200, 1_700_007_200))
        none = a_not_finished_log(an_image(a_firmware(a_project_built_with_no_simulation())))
        (none / "sim" / "image.bin").unlink()
        for project, fact, image in ((other, "image-differs", b"another image"), (newer, "firmware-newer", b"an image"),
                                     (none, "no-image", b"an image")):
            with self.subTest(fact=fact):
                said, _ = show(project)
                self.assertEqual((deploy_of(said)["status"], said["data"]["deploy"]["fact"]), ("problems", fact))
                self.assertEqual(deploy_of(said)["says"], [logged(FLASH_NOT_FINISHED_WORDS, "Cause in the log: a flash command failed.", image=image)])
                self.assertEqual(said["data"]["guide"]["now"]["says"], NOT_FINISHED_NOW)

    def test_the_newest_log_wins_both_ways(self):
        older, newer = "2026-11-23T14-00-00", "2026-11-23T15-00-00"
        said, _ = show(a_not_finished_log(a_board_log(a_deploy_project(), "ready seen", SEEN_SENTENCE, name=older), name=newer))
        self.assertEqual(deploy_of(said)["status"], "problems")
        self.assertTrue(deploy_of(said)["says"][-1].endswith("2 deploys logged."), deploy_of(said)["says"])
        said, _ = show(a_board_log(a_not_finished_log(a_deploy_project(), name=older), "ready seen", SEEN_SENTENCE, name=newer))
        self.assertEqual(deploy_of(said)["status"], "ok")


def with_secrets(project, text):
    """`project` with firmware/wifi_secrets.py holding `text`."""
    (project / "firmware").mkdir(parents=True, exist_ok=True)
    (project / "firmware" / "wifi_secrets.py").write_text(text, encoding="utf-8")
    return project


def chat_offer(project):
    """The guide's `now.chat_offer` of `project` (P1122)."""
    return show(project)[0]["data"]["guide"]["now"]["chat_offer"]


class TheChatOfferTest(FlowTest):
    """P1122, D3: the guide's now names the chat offer whose job its NOW sentence asks Claude for, one row of the plan's
    table per test, and None beside any sentence that asks for something else. The keys are literals here."""

    def test_a_firmware_not_started_asks_claude_to_write_the_firmware_with_two_jobs_or_one(self):
        for project in (a_project_built_with_no_simulation(), a_built_project()):
            with self.subTest(project=project):
                self.assertEqual(chat_offer(project), "write-firmware")

    def test_a_simulate_with_no_sim_files_asks_for_the_build_so_it_names_none(self):
        project = a_firmware(a_built_project())
        self.assertEqual((show(project)[0]["data"]["guide"]["now"]["phase"], chat_offer(project)), ("simulate", None))

    def test_a_simulate_not_started_asks_to_run_the_simulation_with_a_scenario_or_none(self):
        for scenario in ((), ("a.scenario.yaml",)):
            with self.subTest(scenario=scenario):
                project = a_firmware(a_built_project())
                (project / "sim").mkdir()
                (project / "sim" / "wokwi.toml").write_text('[wokwi]\nversion = 1\nfirmware = "image.bin"\n')
                for name in scenario:
                    (project / "sim" / "scenarios").mkdir()
                    (project / "sim" / "scenarios" / name).write_text("name: a\n")
                self.assertEqual((statuses(show(project)[0])["simulate"], chat_offer(project)), ("not-started", "run-simulation"))

    def test_an_image_no_run_tested_asks_to_run_the_simulation_with_a_scenario_or_none(self):
        for scenario in ((), ("a.scenario.yaml",)):
            with self.subTest(scenario=scenario):
                project = a_simulate_now(a_built_project(), *scenario)
                self.assertEqual((statuses(show(project)[0])["simulate"], chat_offer(project)), (None, "run-simulation"))

    def test_a_failed_run_or_an_image_older_than_the_firmware_names_none(self):
        failed = a_run(an_image(a_firmware(a_built_project())), "failed")
        older = a_run(an_image(a_firmware(a_built_project())), "passed")
        os.utime(older / "firmware" / "main.py", (1_700_007_200, 1_700_007_200))
        for project in (failed, older):
            with self.subTest(project=project):
                self.assertEqual((show(project)[0]["data"]["guide"]["now"]["phase"], chat_offer(project)), ("simulate", None))

    def test_a_firmware_with_problems_or_that_could_not_run_names_none(self):
        # FirmwareReader gives only not-started or no status, so D3's last firmware row is reached with a Phase value
        for status in ("problems", "could-not-run"):
            with self.subTest(status=status):
                self.assertIsNone(chat_offer_of(who_and_sentence(Phase("firmware", status, "?", "Claude", ["said"], []), [], NO_IMAGE_FACT)))

    def test_a_simulate_with_problems_names_none(self):
        project = a_firmware(a_project_built_with_no_simulation())
        (project / "sim").mkdir()
        (project / "sim" / "wokwi.toml").write_text('[wokwi]\nversion = 1\nfirmware = 42\n')
        self.assertEqual((statuses(show(project)[0])["simulate"], chat_offer(project)), ("problems", None))

    def test_a_deploy_not_started_asks_claude_to_look_at_the_board_and_next_is_still_the_look(self):
        said = show(a_deploy_project())[0]
        self.assertEqual((said["data"]["guide"]["now"]["chat_offer"], said["data"]["guide"]["now"]["offer"]), ("look-at-board", None))
        self.assertEqual([step["op"] for step in said["next"]], ["look"])

    def test_a_flash_that_did_not_finish_asks_to_look_at_the_board_even_on_another_image(self):
        for image in (b"an image", b"another image"):
            with self.subTest(image=image):
                project = a_not_finished_log(a_deploy_project(), image=image)
                self.assertEqual((deploy_of(show(project)[0])["status"], chat_offer(project)), ("problems", "look-at-board"))

    def test_a_deploy_of_another_image_asks_to_look_at_the_board(self):
        project = a_board_log(a_deploy_project(), "ready seen", SEEN_SENTENCE, image=b"another image")
        self.assertEqual((deploy_of(show(project)[0])["status"], chat_offer(project)), ("stale", "look-at-board"))

    def test_a_stale_deploy_that_needs_the_image_made_first_names_none(self):
        # making the image is no chat offer yet (the plan's Q2), so no block shows beside "make the image again"
        newer = a_board_log(an_image(a_firmware(a_project_built_with_no_simulation())), "ready seen", SEEN_SENTENCE)
        os.utime(newer / "firmware" / "main.py", (1_700_007_200, 1_700_007_200))
        none = a_board_log(an_image(a_firmware(a_project_built_with_no_simulation())), "ready seen", SEEN_SENTENCE)
        (none / "sim" / "image.bin").unlink()
        for project, fact in ((newer, "firmware-newer"), (none, "no-image")):
            with self.subTest(fact=fact):
                said = show(project)[0]
                self.assertEqual((said["data"]["deploy"]["fact"], said["data"]["guide"]["now"]["chat_offer"]), (fact, None))

    def test_a_deploy_log_that_cannot_be_read_names_none(self):
        project = a_board_log(a_deploy_project(), "ready not read", "x")
        self.assertEqual((deploy_of(show(project)[0])["status"], chat_offer(project)), ("could-not-run", None))

    def test_a_deploy_phase_that_is_partial_with_no_board_log_says_could_not_run_and_names_none(self):
        # P1133: a phase list the guide's own deploy read does not match (a swapped list) used to name the look's tell
        # beside "could not run"; the sentence's value, could-not-run, has no chat offer
        project = Path(tempfile.mkdtemp())
        now = guide_of(project, [Phase("deploy", "partial", "?", "you", ["said"], [])], steps=lambda _project: None)["now"]
        self.assertEqual((now["says"], now["chat_offer"]), ("The deploy phase could not run. Ask Claude to read you why.", None))

    def test_any_other_phase_names_none_and_a_build_now_keeps_its_offer(self):
        idea = Path(tempfile.mkdtemp()) / "plant-alarm"
        idea.mkdir()
        build = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [
            {"id": "board", "does": "compute", "what": "microcontroller", "pick": [{"board": "xiao-esp32-c6"}]}])
        (build / "requirements.json").write_text(json.dumps({"board": "xiao-esp32-c6", "parts": [], "board_only": True}))
        self.assertIsNone(chat_offer(idea))
        now = show(build)[0]["data"]["guide"]["now"]
        self.assertEqual((now["phase"], now["offer"], now["chat_offer"]), ("build", "build", None))


class TheNowSentenceTest(unittest.TestCase):
    """P1133: each NOW sentence picker returns a NowSentence, whose `chosen_by` is the (phase, value) it chose the sentence by,
    and `chat_offer_of` is the one lookup of that pair in CHAT_NOW. The pairs and the words are literals here."""

    def test_each_guide_sentence_carries_the_value_it_was_chosen_by(self):
        for phase, fact, written, chosen_by, starts in (
                (Phase("simulate", "not-started", "?", "you", ["said"], []), ImageFact("no-sim-files", None), True,
                 ("simulate", "no-sim-files"), "No simulation files yet"),
                (Phase("simulate", "not-started", "?", "you", ["said"], []), NO_IMAGE_FACT, False,
                 ("simulate", "no-scenario"), "No scenario is written yet"),
                (Phase("simulate", None, "?", "you", ["said"], []), ImageFact("run-failed", "a.log"), True,
                 ("simulate", "run-failed"), "A run failed on this image (a.log)"),
                (Phase("firmware", "not-started", "?", "Claude", ["said"], []), NO_IMAGE_FACT, True,
                 ("firmware", "not-started"), "Ask Claude in the chat to write the firmware"),
                (Phase("firmware", "problems", "?", "Claude", ["said"], []), NO_IMAGE_FACT, True,
                 ("firmware", "problems"), "The firmware phase has problems"),
                (Phase("deploy", "partial", "?", "you", ["said"], []), NO_IMAGE_FACT, True,
                 ("deploy", "could-not-run"), "The deploy phase could not run")):
            with self.subTest(chosen_by=chosen_by):
                told = who_and_sentence(phase, [], fact, written)
                self.assertEqual(told.chosen_by, chosen_by)
                self.assertTrue(told.says.startswith(starts), told.says)

    def test_each_open_deploy_sentence_carries_the_value_it_was_chosen_by(self):
        logged = board_log.LoggedDeploy("2026-11-26T10:00:00+01:00", "abc", "ready unknown", "board_lost")
        not_finished = board_log.LoggedDeploy("2026-11-26T10:00:00+01:00", "abc", "flash not finished", None)
        for state, chosen_by in (
                (DeployState(1, logged, "image-differs", "stale", None), ("deploy", "image-differs")),
                (DeployState(1, not_finished, "current", "problems", None), ("deploy", "flash not finished")),
                (DeployState(1, logged._replace(verdict="ready not seen"), "current", "problems", None), ("deploy", "problems")),
                (DeployState(1, logged, "current", "partial", None), ("deploy", "partial"))):
            with self.subTest(chosen_by=chosen_by):
                self.assertEqual(deploy_reading.deploy_now(state).chosen_by, chosen_by)

    def test_the_chat_offer_is_one_lookup_of_that_value(self):
        for chosen_by, offer in ((("deploy", "flash not finished"), "look-at-board"), (("simulate", "no-scenario"), "run-simulation"),
                                 (("deploy", "problems"), None), (("deploy", "could-not-run"), None)):
            with self.subTest(chosen_by=chosen_by):
                self.assertEqual(chat_offer_of(flow_codes.NowSentence(["claude"], "x", chosen_by)), offer)

    def test_a_stale_parts_list_is_a_picker_too_and_names_no_chat_offer(self):
        for written in (True, False, None):
            with self.subTest(written=written):
                told = requirements_now(["Claude"], written)
                self.assertEqual((told.chosen_by, chat_offer_of(told)), (("requirements", "stale"), None))

    def test_every_key_of_the_chat_offer_table_is_a_value_some_picker_returns(self):
        # the pairs the pickers return for the phases that have a chat offer, and the stale parts list (the plan's table)
        returned = {("simulate", "no-sim-files"), ("simulate", "no-scenario"), ("simulate", "run-failed"),
                    ("simulate", "image-older"), ("simulate", "image-untested"), ("simulate", "not-started"),
                    ("firmware", "not-started"), ("firmware", "problems"), ("firmware", "could-not-run"),
                    ("simulate", "problems"), ("simulate", "could-not-run"),
                    ("deploy", "not-started"), ("deploy", "problems"), ("deploy", "could-not-run"), ("deploy", "partial"),
                    ("deploy", "firmware-newer"), ("deploy", "no-image"), ("deploy", "image-differs"),
                    ("deploy", "flash not finished"), ("requirements", "stale")}
        self.assertLessEqual(set(flow_codes.CHAT_NOW), returned)
        for key, offer in flow_codes.CHAT_NOW.items():
            with self.subTest(key=key):
                self.assertTrue(flow_codes.OFFER_KINDS[offer].tell)


class TheOfferKindsTableTest(unittest.TestCase):
    """P1115, P1122: the rules of the one table of offer kinds. The kinds, the keys and the words are literals here."""

    def test_the_table_holds_the_seven_kinds_in_order(self):
        self.assertEqual(list(flow_codes.OFFER_KINDS),
                         ["pick", "requirements", "build", "needs-drop", "write-firmware", "run-simulation", "look-at-board"])

    def test_a_kind_with_a_tell_is_never_sent_from_the_page_and_a_sent_kind_has_no_tell(self):
        for kind, row in flow_codes.OFFER_KINDS.items():
            with self.subTest(kind=kind):
                self.assertFalse(row.tell and row.from_page)

    def test_a_tell_names_the_job_never_the_how(self):
        tells = [row.tell for row in flow_codes.OFFER_KINDS.values() if row.tell]
        self.assertEqual(len(tells), 3)
        for tell in tells:
            with self.subTest(tell=tell):
                self.assertFalse([part for part in ("/spark:", ".py", "--", "/") if part in tell])
                self.assertTrue(tell.endswith("."))

    def test_every_chat_offer_the_guide_names_has_a_tell(self):
        named = set(flow_codes.CHAT_NOW.values())
        self.assertEqual(named, {"write-firmware", "run-simulation", "look-at-board"})
        self.assertEqual([kind for kind in named if not flow_codes.OFFER_KINDS[kind].tell], [])

    def test_kind_of_is_the_word_before_the_first_colon(self):
        self.assertEqual(flow_codes.kind_of("pick:light:led-red-5mm"), "pick")
        self.assertEqual(flow_codes.kind_of("needs-drop:light"), "needs-drop")
        self.assertEqual(flow_codes.kind_of("build"), "build")

    def test_only_a_pick_the_parts_list_and_the_build_are_sendable(self):
        for key in ("pick:light:led-red-5mm", "pick", "requirements", "build"):
            with self.subTest(key=key):
                self.assertTrue(flow_codes.is_sendable(key))
                self.assertFalse(flow_codes.in_chat(key))
        for key in ("needs-drop:light", "write-firmware", "run-simulation", "look-at-board"):
            with self.subTest(key=key):
                self.assertFalse(flow_codes.is_sendable(key))
                self.assertTrue(flow_codes.in_chat(key))
        for key in ("deploy", "simulate:main", ""):
            with self.subTest(key=key):
                self.assertFalse(flow_codes.is_sendable(key))
                self.assertFalse(flow_codes.in_chat(key))  # a kind spark does not know is in no chat either
        self.assertEqual(flow_codes.SENDABLE, ("pick", "requirements", "build"))

    def test_one_row_s_from_page_turns_the_button_off_for_the_guide_the_page_and_the_run(self):
        build_offer = {"key": "build", "label": "Build the board", "effect": "e", "makes_stale": []}
        now = SimpleNamespace(offers=[Offer("build", "Build the board", "e", [], NextStep("build-board", [], "w"))])
        offered = {"build": now.offers[0]}
        request = run_request.PageRequest("00000000-0000-0000-0000-000000000000", "build", "0" * 12)
        self.assertEqual(job_offer(now), "build")
        self.assertEqual(list(flow_page.page_words([{"offers": [build_offer]}])["offers"]), ["build"])
        self.assertIsNone(run_request.refusal_of(request, offered, "0" * 64))
        on = flow_codes.OFFER_KINDS
        off = dict(flow_codes.OFFER_KINDS, build=flow_codes.OFFER_KINDS["build"]._replace(from_page=False))
        flow_codes.OFFER_KINDS = off  # no mock.patch (T2): put back below, whatever the asserts say
        try:
            self.assertIsNone(job_offer(now))
            self.assertEqual(flow_page.page_words([{"offers": [build_offer]}])["offers"], {})
            self.assertEqual(str(run_request.refusal_of(request, offered, "0" * 64)), "request_in_chat")
        finally:
            flow_codes.OFFER_KINDS = on

    def test_the_words_of_a_request_whose_offer_left_the_page_are_those_of_the_sendable_kinds(self):
        self.assertEqual(set(flow_codes.LAST_REQUEST_KINDS), set(flow_codes.SENDABLE))
        self.assertEqual(set(flow_codes.RAN_OK_SAYS), set(flow_codes.SENDABLE))


class TheSecretMaskTest(FlowTest):
    """P1060 (#1558): `show` masks the values of the project's secrets file as `***`. A file that cannot be read or parsed
    does not stop `show` (D5: `show` fails open): it masks what it can and says in a note that the mask is off for it."""

    def test_a_secret_value_in_a_phase_sentence_is_masked(self):
        project = with_secrets(with_needs(Path(tempfile.mkdtemp()) / "plant", [{"id": SECRET, "does": "sense", "what": "soil-moisture"}]),
                               'WIFI_PASSWORD = "%s"\n' % SECRET)
        with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
            flow.main(["show", "--project", str(project), "--json"])
        self.assertNotIn(SECRET, out.getvalue())
        self.assertIn("1 need(s): ***", says(json.loads(out.getvalue()), "needs"))
        self.assertNotIn(SECRET, "\n".join(lines_of(project)))

    def test_a_secret_in_the_project_s_path_is_masked_in_next_s_argv_too_the_known_risk(self):
        # A11: a raw place keeps its paths and loses its tokens, so a project whose path holds a secret gets a `next`
        # argv that no longer runs. The plan names this risk and takes it: the mask comes first.
        project = self.user_home / SECRET / "xiao"
        shutil.copytree(BUILT, project)  # never built: `next` is the build, whose argv holds the project's path
        with_secrets(project, 'WIFI_PASSWORD = "%s"\n' % SECRET)
        envelope, _code = show(project)
        argv = [part for step in envelope["next"] for part in step["argv"]]
        self.assertTrue(argv)
        self.assertNotIn(SECRET, json.dumps(envelope))
        self.assertTrue(any("/***/" in part for part in argv), argv)

    def test_a_secrets_file_that_does_not_parse_adds_a_note_and_shows_none_of_its_text(self):
        from spark.flow.show_flow import MASK_OFF
        project = with_secrets(with_needs(Path(tempfile.mkdtemp()) / "plant", [{"id": "soil", "does": "sense", "what": "soil-moisture"}]),
                               'WIFI_PASSWORD = "%s\n' % HALF_TYPED)
        with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()) as err:
            code = flow.main(["show", "--project", str(project), "--json"])
        envelope = json.loads(out.getvalue())
        self.assertEqual((code, envelope["status"]), (0, OK))
        self.assertEqual(envelope["notes"], [{"subject": "firmware/wifi_secrets.py", "sentence": MASK_OFF % "firmware/wifi_secrets.py"}])
        self.assertEqual(MASK_OFF % "firmware/", "the mask is off for firmware/: it cannot be read or parsed, so spark cannot mask "
                                                 "its values. Repair or remove it")  # the lens of #1610: no firmware/firmware
        self.assertNotIn(HALF_TYPED, out.getvalue() + err.getvalue())
        text = "\n".join(lines_of(project))
        self.assertIn(MASK_OFF % "firmware/wifi_secrets.py", text)
        self.assertNotIn(HALF_TYPED, text)


def in_prague(test):
    """Pin the zone of `test` to Europe/Prague for its run, so a time said in words is known."""
    import time
    patcher = mock.patch.dict(os.environ, {"TZ": "Europe/Prague"})
    patcher.start()
    test.addCleanup(time.tzset)
    test.addCleanup(patcher.stop)
    time.tzset()


class TheDeployedLineTest(unittest.TestCase):
    """P1062 (test 9): ON THE BOARD's sentence on the page, from `data.deploy`: a readable time in the machine's zone, the
    verdict's words, the cause unless ready was seen, and a stale fact's opener first, by the one rule of deployed_says."""

    AT = "2026-11-23T13:09:41+00:00"

    def setUp(self):
        in_prague(self)

    def line(self, verdict, cause=None, fact="current"):
        from spark.flow.deploy_reading import deployed_line
        return deployed_line({"at": self.AT, "image": "ab" * 32, "verdict": verdict, "cause": cause, "fact": fact, "read_back": None})

    def test_ready_unknown_with_a_known_cause_says_the_verdict_and_the_cause(self):
        self.assertEqual(self.line("ready unknown", "files_unread"),
                         "Last deploy 23 Nov 2026, 14:09. Written by the flasher, nothing read back, start not seen. "
                         "Cause in the log: spark did not reach the board to read its files.")

    def test_ready_unknown_with_no_cause_says_the_cause_is_not_recorded(self):
        self.assertEqual(self.line("ready unknown"),
                         "Last deploy 23 Nov 2026, 14:09. Written by the flasher, start not confirmed. Cause not recorded.")

    def test_ready_seen_has_no_cause_sentence(self):
        self.assertEqual(self.line("ready seen"), "Last deploy 23 Nov 2026, 14:09. Written by the flasher, files read back, ready seen.")

    def test_a_stale_fact_with_ready_seen_opens_with_its_sentence_so_it_never_reads_as_a_pass(self):
        self.assertEqual(self.line("ready seen", fact="firmware-newer"),
                         "Your firmware changed after the image that the last deploy wrote. Last deploy 23 Nov 2026, 14:09. "
                         "Written by the flasher, files read back, ready seen.")

    def test_a_flash_not_finished_has_no_stale_opener(self):
        # P1092 test 11: each opener speaks of the image the last deploy wrote, and this one wrote none
        self.assertEqual(self.line("flash not finished", "flash_failed", fact="image-differs"),
                         "Last deploy 23 Nov 2026, 14:09. Flash not finished, nothing read back, the board may be erased. "
                         "Cause in the log: a flash command failed.")

    def test_no_deploy_gives_none_and_a_line_holds_no_iso_time_and_no_image(self):
        from spark.flow.deploy_reading import deployed_line
        self.assertIsNone(deployed_line(None))
        said = self.line("ready not seen", "no_ready_line")
        self.assertNotIn(self.AT, said)
        self.assertNotIn("abab", said)
        self.assertIn("Cause in the log: the firmware printed no ready line.", said)

    def test_the_day_and_time_of_a_stored_time_is_the_machine_s_and_one_that_does_not_parse_stays(self):
        self.assertEqual(zone_time.day_and_time("2026-11-02T23:30:05+00:00"), "3 Nov 2026, 00:30")
        self.assertEqual(zone_time.day_and_time("not a time"), "not a time")
        self.assertEqual(zone_time.day_and_time("2026-01-15T12:00:00+00:00"), "15 Jan 2026, 13:00")


class TheWiringWithNowTest(unittest.TestCase):
    """The review of #1619 (E16 as a fact): `now.with_wiring` says whether the job now holds the wiring: the two jobs beside a
    current sheet, or the deploy beside a current sheet. The page opens its wiring fold by it and decides nothing."""

    def now(self, phases, sheet=True):
        from spark.flow.phase_readers import Phase
        project = Path(tempfile.mkdtemp())
        if sheet:
            (project / "breadboard.md").write_text("# a sheet\n")
        return guide_of(project, [Phase(*each, "you", ["said"], []) for each in phases], steps=lambda _project: 3)["now"]

    def test_the_deploy_beside_a_current_sheet_holds_the_wiring(self):
        self.assertIs(self.now([("breadboard", None, "·"), ("deploy", "not-started", "○")])["with_wiring"], True)

    def test_the_deploy_with_no_kept_sheet_or_a_sheet_not_current_does_not(self):
        self.assertIs(self.now([("breadboard", None, "·"), ("deploy", "not-started", "○")], sheet=False)["with_wiring"], False)
        self.assertIs(self.now([("breadboard", "stale", "↻"), ("deploy", "not-started", "○")])["with_wiring"], False)

    def test_the_two_jobs_hold_it_and_another_now_does_not(self):
        two = self.now([("breadboard", None, "·"), ("firmware", "not-started", "○")])
        self.assertEqual((two["steps"], two["with_wiring"]), (3, True))
        self.assertIs(self.now([("build", "not-started", "○"), ("breadboard", None, "·")])["with_wiring"], False)


GOAL = "a button switches a light on and off"
GOAL_LINE = "your goal is “%s”" % GOAL
NO_GOAL_LINE = "the brief holds no goal"


def with_brief(project, text):
    """`project` with `.spark/project.json` holding `text` as it is."""
    (project / ".spark").mkdir(parents=True, exist_ok=True)
    (project / ".spark" / "project.json").write_text(text)
    return project


def a_project_with_a_brief(text):
    project = Path(tempfile.mkdtemp()) / "plant-alarm"
    project.mkdir()
    return with_brief(project, text)


def idea_of(said):
    idea = next(each for each in said["data"]["phases"] if each["phase"] == "idea")
    return idea["status"], idea["mark"], idea["says"]


class TheIdeaGoalTest(FlowTest):
    """P1142: the idea phase reads the brief's goal, and show's first line is the guide's NOW."""

    def test_a_brief_with_a_goal_makes_the_idea_ok_and_says_the_goal(self):
        said, _ = show(a_project_with_a_brief(json.dumps({"goal": GOAL})))
        self.assertEqual(idea_of(said), ("ok", "✓", [GOAL_LINE]))

    def test_a_goal_is_said_whatever_must_holds(self):
        said, code = show(a_project_with_a_brief(json.dumps({"goal": "a lamp", "must": "x"})))
        self.assertEqual((idea_of(said), code), (("ok", "✓", ["your goal is “a lamp”"]), 0))

    def test_no_goal_a_null_goal_or_a_blank_goal_says_so_with_no_status(self):
        empty = Path(tempfile.mkdtemp()) / "plant-alarm"
        empty.mkdir()
        for project in (empty, a_project_with_a_brief('{"goal": null}'), a_project_with_a_brief('{"goal": "  "}'),
                        a_project_with_a_brief('{"goal": 7}')):
            with self.subTest(project=project.name, brief=(project / ".spark").exists()):
                self.assertEqual(idea_of(show(project)[0]), (None, "·", [NO_GOAL_LINE]))

    def test_a_brief_that_cannot_be_read_says_why_with_no_status(self):
        said, code = show(a_project_with_a_brief("{not json"))
        self.assertEqual((idea_of(said), code), ((None, "·", ["the brief cannot be read (bad-json)"]), 0))
        status, _, lines = idea_of(show(a_project_with_a_brief("[" * 100000))[0])
        self.assertEqual((status, len(lines), lines[0].startswith("the brief cannot be read (")), (None, 1, True))

    def test_a_goal_with_no_needs_stands_at_the_needs(self):
        said, _ = show(a_project_with_a_brief(json.dumps({"goal": GOAL})))
        guide = said["data"]["guide"]
        self.assertEqual(guide["now"], {"phase": "needs", "by": ["claude"], "says": "Ask Claude in the chat to write the needs from your goal.",
                                        "offer": None, "chat_offer": None, "needs": [], "steps": None, "with_wiring": False})
        self.assertEqual(([each["place"] for each in guide["stations"] if each["phase"] == "idea"], said["next"], said["data"]["stands_at"]),
                         (["done"], [], "needs"))

    def test_the_walk_s_project_starts_with_now_and_its_done_idea_says_the_goal(self):
        project = with_needs(a_project_with_a_brief(json.dumps({"goal": GOAL, "must": ["one line"]})), [
            {"id": "soil", "does": "sense", "what": "soil-moisture", "pick": [{"part": "x-many"}]}])
        lines = lines_of(project)
        self.assertTrue(lines[0].startswith("  NOW ("), lines[0])
        self.assertIn("  ✓ idea: %s (you)" % GOAL_LINE, lines)
        self.assertFalse([line for line in lines if "Tell Claude your goal" in line])

    def test_a_goal_with_no_needs_starts_with_the_needs_and_not_the_goal_question(self):
        lines = lines_of(a_project_with_a_brief(json.dumps({"goal": "a lamp", "must": "x"})))
        self.assertEqual(lines[0], "  NOW (needs): Ask Claude in the chat to write the needs from your goal.")
        self.assertFalse([line for line in lines if "Tell Claude your goal" in line])

    def test_an_idea_with_a_goal_is_no_finding_and_keeps_the_exit(self):
        said, code = show(a_project_with_a_brief(json.dumps({"goal": GOAL})))
        self.assertEqual((code, said["status"], said["problems"]), (0, "ok", []))


FAILED_NOW = "A run failed on this image (one.log)."
CANNOT_TELL = "Spark cannot tell. The simulation phase says why."


def runs_folder_state(project):
    """{file: mtime_ns} of every file under sim/runs/: a reader that wrote or ran something changes it."""
    return {path.as_posix(): path.stat().st_mtime_ns for path in sorted((project / "sim" / "runs").rglob("*")) if path.is_file()}


def a_project_at_the_board(verdict="failed"):
    """An image, a run of it that ended in `verdict`, and a board log of it that saw ready: the deploy is ok (P1220)."""
    project = a_run(an_image(a_firmware(a_built_project())), verdict)
    return a_board_log(project, "ready seen", SEEN_SENTENCE)


def gate_a_of_project(project):
    return show(project)[0]["data"]["guide"]["gate_a"]


class TheGateATest(FlowTest):
    """P1220 (#1769): gate A's one free condition, no failed run on the current image (D10), and its row "Tested before the board"."""

    def test_a_failed_run_on_the_image_shuts_gate_a_and_the_row_says_which_log(self):
        self.assertEqual(gate_a_of_project(a_project_at_the_board()),
                         {"shut_by": ["run-failed"], "fact": "run-failed", "says": FAILED_NOW})

    def test_reading_gate_a_costs_no_minutes_through_show_and_the_page(self):
        """The fake run raises, and the files under sim/runs/ keep their mtimes: nothing ran and nothing was written there."""
        from spark.flow.write_flow_page import WriteFlowPage
        project = a_project_at_the_board()
        before = runs_folder_state(project)
        self.assertEqual(sorted(path.name for path in (project / "sim" / "runs").glob("*.log")), ["one.log"])
        for operation, values in ((ShowFlow(), {"project": str(project)}), (WriteFlowPage(), {"project": str(project), "artifact": None})):
            with self.subTest(operation=operation.name):
                outside = FakeOutsideWorld(run=mock.Mock(side_effect=AssertionError("a program ran")))
                result = run_operation(operation, values, outside)
                self.assertEqual((outside.ran, result.data["guide"]["gate_a"]["shut_by"]), ([], ["run-failed"]))
                self.assertEqual(runs_folder_state(project), before)

    def test_show_prints_the_row_after_the_now_line_and_prints_none_before_the_station(self):
        lines = lines_of(a_project_at_the_board())
        self.assertEqual(lines[1], "  TESTED BEFORE THE BOARD: A run failed on this image (one.log).")
        self.assertTrue(lines[0].startswith("  NOW (simulate)"), lines[0])
        self.assertFalse([line for line in lines_of(a_run(an_image(a_firmware(a_built_project())), "failed")) if "TESTED BEFORE" in line])
        self.assertFalse([line for line in lines_of(Path(tempfile.mkdtemp())) if "TESTED BEFORE" in line])

    def test_show_prints_a_null_shut_by_row(self):
        """A null `shut_by` is not a null `gate_a`: the deploy has a board log and a log cannot be read."""
        project = a_board_log(a_deploy_project(), "ready seen", SEEN_SENTENCE)
        log = project / "sim" / "runs" / "one.log"
        self.addCleanup(log.chmod, 0o644)
        log.chmod(0)
        self.assertIn("  TESTED BEFORE THE BOARD: " + CANNOT_TELL, lines_of(project))

    def test_show_prints_the_row_after_the_line_that_says_nothing_is_open(self):
        lines = lines_of(a_project_at_the_board("passed"))
        self.assertEqual(lines[0], "  " + NOTHING_WAITS)
        self.assertEqual(lines[1], "  TESTED BEFORE THE BOARD: A run passed on this image.")

    def test_a_passed_run_and_a_board_log_leave_nothing_shutting_gate_a(self):
        self.assertEqual(gate_a_of_project(a_project_at_the_board("passed")),
                         {"shut_by": [], "fact": "image-tested", "says": "A run passed on this image."})

    def test_a_failed_run_beside_a_later_passed_run_still_shuts_gate_a(self):
        project = a_project_at_the_board()
        (project / "sim" / "runs" / "two.log").write_text("verdict: passed\nimage sha256: %s\n\nx\n" % hashlib.sha256(b"an image").hexdigest())
        self.assertEqual(gate_a_of_project(project)["shut_by"], ["run-failed"])

    def test_a_failed_run_on_another_image_shuts_nothing(self):
        project = a_board_log(a_run(an_image(a_firmware(a_built_project())), "failed", image=b"older"), "ready seen", SEEN_SENTENCE)
        self.assertEqual(gate_a_of_project(project),
                         {"shut_by": [], "fact": "image-untested", "says": "No run tested this image."})

    def test_a_rebuild_after_an_older_board_log_and_a_failed_run_on_the_new_image_shuts_gate_a(self):
        project = a_board_log(a_firmware(a_built_project()), "ready seen", SEEN_SENTENCE, image=b"the older image")
        a_run(an_image(project, b"the new image"), "failed", image=b"the new image")
        self.assertEqual(gate_a_of_project(project)["shut_by"], ["run-failed"])

    def test_firmware_changed_after_the_image_is_said_in_the_row(self):
        project = a_project_at_the_board("passed")
        os.utime(project / "firmware" / "main.py", (1_700_007_200, 1_700_007_200))
        self.assertEqual(gate_a_of_project(project), {
            "shut_by": [], "fact": "image-older", "says": "Your firmware changed after the image, so no run tested it as it is now."})

    def test_before_the_on_the_board_station_gate_a_is_null(self):
        for name, project in (("a fresh project", Path(tempfile.mkdtemp())), ("the simulate now", a_run(an_image(a_firmware(a_built_project())), "failed"))):
            with self.subTest(name):
                self.assertIsNone(gate_a_of_project(project))

    def test_the_deploy_now_reaches_the_station_and_a_log_that_cannot_be_read_gives_null(self):
        project = a_deploy_project()
        self.assertEqual(gate_a_of_project(project)["fact"], "image-tested")  # the deploy is now, with no board log
        a_board_log(project, "ready seen", SEEN_SENTENCE)
        self.assertEqual(gate_a_of_project(project), {"shut_by": [], "fact": "image-tested", "says": "A run passed on this image."})
        log = project / "sim" / "runs" / "one.log"
        self.addCleanup(log.chmod, 0o644)
        log.chmod(0)
        self.assertEqual(gate_a_of_project(project), {"shut_by": None, "fact": None, "says": CANNOT_TELL})

    def test_a_board_with_no_wokwi_model_says_no_model_and_a_failed_run_still_shuts_it(self):
        project = a_board_log(a_firmware(a_project_built_with_no_simulation()), "ready seen", SEEN_SENTENCE)
        self.assertEqual(gate_a_of_project(project),
                         {"shut_by": [], "fact": "no-model", "says": "No simulator run: none covers this board."})
        project = a_board_log(a_run(an_image(a_firmware(a_project_built_with_no_simulation())), "failed"), "ready seen", SEEN_SENTENCE)
        self.assertEqual(gate_a_of_project(project)["shut_by"], ["run-failed"])

    def a_no_model_board_with_the_default_image(self):
        """A real no-model board (P1001): no sim/wokwi.toml, and the image sim/flash-with-firmware.bin."""
        project = a_firmware(a_project_built_with_no_simulation())
        (project / "sim").mkdir(exist_ok=True)
        (project / "sim" / "flash-with-firmware.bin").write_bytes(b"an image")
        return project

    def test_a_no_model_board_with_no_toml_reads_the_default_image_as_the_deploy_does(self):
        project = a_run(self.a_no_model_board_with_the_default_image(), "failed")
        a_board_log(project, "ready seen", SEEN_SENTENCE)
        self.assertEqual(gate_a_of_project(project), {"shut_by": ["run-failed"], "fact": "run-failed", "says": FAILED_NOW})
        log = project / "sim" / "runs" / "one.log"
        self.addCleanup(log.chmod, 0o644)
        log.chmod(0)
        self.assertEqual(gate_a_of_project(project), {"shut_by": None, "fact": None, "says": CANNOT_TELL})

    def test_a_no_model_board_with_the_default_image_and_no_failed_run_says_no_model(self):
        project = a_board_log(self.a_no_model_board_with_the_default_image(), "ready seen", SEEN_SENTENCE)
        self.assertEqual(gate_a_of_project(project)["fact"], "no-model")

    def test_a_failed_log_with_no_sim_wokwi_toml_is_not_seen_and_the_row_says_no_simulation_files(self):
        """The risk the plan names: image_fact reads no image without sim/wokwi.toml, though the deploy refuses a failed log
        on sim/flash-with-firmware.bin. Pinned so a change shows."""
        project = a_board_log(a_run(a_firmware(a_built_project()), "failed"), "ready seen", SEEN_SENTENCE)
        self.assertEqual(gate_a_of_project(project), {
            "shut_by": [], "fact": "no-sim-files", "says": "No run tested this image: the project has no simulation files."})

    def test_no_row_with_an_empty_shut_by_says_a_word_of_permission(self):
        from spark.flow import flow_codes as codes
        projects = (a_project_at_the_board("passed"), a_board_log(a_firmware(a_project_built_with_no_simulation()), "ready seen", SEEN_SENTENCE),
                    a_board_log(a_run(an_image(a_firmware(a_built_project())), "failed", image=b"older"), "ready seen", SEEN_SENTENCE),
                    a_board_log(a_run(a_firmware(a_built_project()), "failed"), "ready seen", SEEN_SENTENCE))
        said = [gate_a_of_project(project) for project in projects] + [{"says": text} for text in codes.GATE_A_SAYS.values()]
        for row in said:
            with self.subTest(row["says"]):
                self.assertFalse(re.search(r"\b(open|ok|allowed|ready|permitted)\b", row["says"], re.IGNORECASE), row["says"])
        self.assertEqual(len(said), 4 + len(codes.GATE_A_SAYS))


if __name__ == "__main__":
    unittest.main()
