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
from fakes import FakeClock, FakeTextFileWriter  # noqa: E402
from spark.build.build_record import BUILD_RECORD_FILE, BuildRecordStore, sha256_of  # noqa: E402
from spark.core import zone_time  # noqa: E402
from spark.flow.show_flow import ShowFlow  # noqa: E402
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
        self.assertEqual(effects["pick:wet:x-held"], "replaces the picks of need wet in needs.json; you have 3; held by smartbin-local")
        self.assertEqual(effects["pick:wet:x-many"], "replaces the picks of need wet in needs.json; you have many")
        self.assertEqual(effects["pick:wet:x-unknown"], "replaces the picks of need wet in needs.json; how many you have is unknown")
        self.assertEqual(said["data"]["phases"][1]["offers"][0]["effect"], "drops need soil from needs.json and frees its holds")

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


class TheCommandTest(FlowTest):
    def test_help_exits_0(self):
        with contextlib.redirect_stdout(io.StringIO()) as out, self.assertRaises(SystemExit) as stopped:
            flow.main(["--help"])
        self.assertEqual(stopped.exception.code, 0)
        self.assertIn("Exit codes:", out.getvalue())

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

if __name__ == "__main__":
    unittest.main()
