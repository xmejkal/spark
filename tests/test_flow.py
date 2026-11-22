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
from spark.design import needs  # noqa: E402
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
#: The says lines' close, and the a_store probe that smartbin-local holds, as a refused pick names it (P991 review).
LIST = " Claude can list them with parts.py --match."
HELD = "“A soil probe” (none free, held by smartbin-local)"
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
        # P979: the hints name the command and who acts, with no placeholder and no path
        self.assertEqual(says(said, "firmware"), ["No firmware/main.py yet. Ask Claude to write it in the chat."])
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
        said, code = show(with_needs(a_built_project(), []))
        self.assertEqual(code, 0)
        self.assertEqual(says(said, "needs"), ["no need is left: the last one was dropped"])
        self.assertEqual(says(said, "parts"), ["no need or pick is behind the parts list"])
        self.assertEqual(table(said), BUILT_TABLE)

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
        self.assertIn("stands at: needs", out.getvalue())

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


def a_firmware(project):
    (project / "firmware").mkdir()
    (project / "firmware" / "main.py").write_text("print(1)\n")
    return project


# P980: a project with no needs behind its requirements.json lists no needs or parts as done: the five tests below that
# build a hand-written project say `requirements (no needs or picks behind it)` in `done`, on purpose.
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
        # P977 PR 2: now holds `steps`, the wiring's step count while the wiring is part of now, else None.
        self.assertEqual(said["data"]["guide"], {
            "now": {"phase": "firmware", "by": ["you", "claude"], "offer": None, "needs": [], "steps": 10,
                    "says": "Two jobs, in any order: wire the breadboard (10 steps, power off), and ask Claude to write the "
                            "firmware. Spark cannot see your wiring."},
            "done": ["idea", "requirements (no needs or picks behind it)", "build (no simulation)"],
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
            "now": {"phase": "deploy", "by": ["your terminal"], "offer": None, "needs": [], "steps": None,
                    "says": "When the breadboard is wired, plug the board into USB. Ask Claude to look at it first, then "
                            "run the deploy in your terminal."},
            "done": ["idea", "requirements (no needs or picks behind it)", "build (no simulation)", "breadboard (spark cannot see it)", "firmware"],
            "later": ["simulate (no Wokwi model of this board)"], "set_aside": [], "no_simulation": NO_MODEL})

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
                         ("firmware", "Ask Claude in the chat to write the firmware for this board."))
        self.assertEqual(guide["done"], ["idea", "requirements (no needs or picks behind it)", "build (no simulation)"])

    def test_a_build_of_a_board_wokwi_has_no_model_of_is_stale_when_the_parts_list_changed(self):
        project = a_project_built_with_no_simulation()
        (project / "requirements.json").write_text(json.dumps({"board": "xiao-esp32-c6-fresh", "parts": ["led-red-5mm"]}))
        guide = show(project)[0]["data"]["guide"]
        self.assertEqual((guide["now"]["phase"], guide["now"]["says"], guide["no_simulation"]),
                         ("build", "The parts list changed since the last build. Build the board again.", None))  # P993

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
            "now": {"phase": "idea", "by": ["you"], "offer": None, "needs": [], "steps": None,
                    "says": "Tell Claude your goal in the chat, in your own words."},
            "done": [], "later": ["needs", "parts", "requirements", "build", "breadboard", "firmware", "simulate", "deploy"],
            "set_aside": [], "no_simulation": None})

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
                         ("requirements", "requirements", "Write the parts list from your picks."))  # P993

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
            "phase": "parts", "by": ["you"], "offer": None, "needs": [], "steps": None,
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

    def test_a_pick_that_owes_a_fact_says_which_and_offers_no_parts_list(self):
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", BOARD + [
            {"id": "soil", "does": "sense", "what": "soil-moisture", "pick": [{"part": "x-many"}]}])
        said, code = show(project)
        self.assertEqual((code, table(said)["requirements"]), (1, ("problems", [])))
        self.assertEqual(says(said, "requirements"), [
            "no requirements.json yet",
            "“A soil probe” for soil still lacks what spark needs: needs, footprint, pin_order, pin_order_proof, simulation. "
            "Ask Claude how to fill it in."])
        now = said["data"]["guide"]["now"]
        self.assertEqual((now["phase"], now["offer"], now["says"]),
                         ("requirements", None, "The requirements phase has problems. Ask Claude to go through them with you."))

    def test_a_pick_stored_as_its_drawer_entry_is_named_with_its_need(self):
        # P993 review (refuter): the pick names the entry, the owed problem names its record
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", BOARD + [
            {"id": "soil", "does": "sense", "what": "soil-moisture", "pick": [{"entry": "many"}]}])
        self.assertEqual(says(show(project)[0], "requirements")[1],
                         "“A soil probe” for soil still lacks what spark needs: needs, footprint, pin_order, pin_order_proof, "
                         "simulation. Ask Claude how to fill it in.")

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
            "“A soil probe” for soil still lacks what spark needs: needs, footprint, pin_order, pin_order_proof, simulation. "
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


if __name__ == "__main__":
    unittest.main()
