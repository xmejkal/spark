"""
The flow reader (P825, #1183): `flow.py show` says where a project stands, phase by phase, from the files the earlier
stages wrote, and offers the next steps as keys. On five projects (no needs, picked, built, a build that could not run,
requirements changed after the build) each test pins the nine phases' status and offers from `flow.py show --json`.
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


def statuses(envelope):
    return {phase["phase"]: phase["status"] for phase in envelope["data"]["phases"]}


def offers(envelope, phase):
    return [offer["key"] for offer in next(each for each in envelope["data"]["phases"] if each["phase"] == phase)["offers"]]


def facts(envelope, phase):
    return next(each for each in envelope["data"]["phases"] if each["phase"] == phase)["facts"]


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


def a_built_project(status="ok"):
    """A copy of the built fixture with its breadboard sheet and the record of a build that ended in `status`."""
    project = Path(tempfile.mkdtemp()) / "xiao"
    shutil.copytree(BUILT, project)
    (project / "breadboard.md").write_text("# the sheet\n")
    stages = [{"name": "board", "status": "ok"}, {"name": "build", "status": status}]
    BuildRecordStore(project, clock=FakeClock()).write({"status": status, "stages": stages, "missing_facts": [],
                                                       "requirements": "requirements.json",
                                                       "requirements_sha256": sha256_of(project / "requirements.json")})
    return project


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
        self.assertEqual(statuses(said), {"idea": None, "needs": "not-started", "parts": "not-started", "requirements": "not-started",
                                          "build": "not-started", "breadboard": "not-started", "firmware": None, "simulate": None,
                                          "deploy": "not-started"})
        self.assertEqual(said["data"]["stands_at"], "needs")
        self.assertEqual({phase: offers(said, phase) for phase in PHASES}, {phase: [] for phase in PHASES})
        self.assertEqual(facts(said, "idea"), ["Tell Claude your goal in the chat"])
        self.assertEqual(facts(said, "firmware"), ["no firmware/main.py yet"])
        self.assertIn("no sim/wokwi.toml", facts(said, "simulate")[0])
        self.assertEqual([phase["by"] for phase in said["data"]["phases"]],
                         ["you", "claude", "you", "claude", "claude", "you", "claude", "your terminal", "your terminal"])

    def test_a_project_with_one_of_two_needs_picked_offers_each_pick_with_what_it_does(self):
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [
            {"id": "soil", "does": "sense", "what": "soil-moisture", "pick": [{"part": "x-many"}]},
            {"id": "wet", "does": "sense", "what": "soil-moisture"}])
        said, code = show(project)
        self.assertEqual(code, 0)
        self.assertEqual({phase: statuses(said)[phase] for phase in ("needs", "parts", "requirements", "build")},
                         {"needs": "ok", "parts": "partial", "requirements": "not-started", "build": "not-started"})
        self.assertEqual(said["data"]["stands_at"], "parts")
        self.assertEqual(offers(said, "needs"), ["needs-drop:soil", "needs-drop:wet"])
        self.assertIn("1 of 2 needs picked", facts(said, "parts"))
        self.assertEqual(offers(said, "requirements"), ["requirements"])
        effects = {offer["key"]: offer["effect"] for offer in said["data"]["phases"][2]["offers"]}
        self.assertEqual(effects["pick:wet:x-held"], "replaces the picks of need wet in needs.json; you have 3; held by smartbin-local")
        self.assertEqual(effects["pick:wet:x-many"], "replaces the picks of need wet in needs.json; you have many")
        self.assertEqual(effects["pick:wet:x-unknown"], "replaces the picks of need wet in needs.json; how many you have is unknown")
        self.assertIn("pick:soil:x-many", effects)
        self.assertEqual(said["data"]["phases"][1]["offers"][0]["effect"], "drops need soil from needs.json and frees its holds")

    def test_every_need_picked_makes_the_parts_ok(self):
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [
            {"id": "soil", "does": "sense", "what": "soil-moisture", "pick": [{"part": "x-many"}]}])
        said, _ = show(project)
        self.assertEqual(statuses(said)["parts"], "ok")
        self.assertEqual(said["data"]["stands_at"], "requirements")

    def test_needs_with_no_pick_leave_the_parts_not_started(self):
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [{"id": "soil", "does": "sense", "what": "soil-moisture"}])
        self.assertEqual(statuses(show(project)[0])["parts"], "not-started")

    def test_a_need_with_no_what_gives_the_parts_problems_and_exit_1(self):
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [{"id": "soil", "does": "sense"}])
        said, code = show(project)
        self.assertEqual((code, said["status"], statuses(said)["parts"]), (1, "problems", "problems"))
        self.assertIn("soil: a need with no `what` cannot be matched", facts(said, "parts")[0])
        self.assertEqual([(item["subject"], item["code"]) for item in said["problems"]], [("parts", "phase_problems")])

    def test_a_built_project_with_no_needs_has_each_built_phase_ok_and_stands_at_the_needs(self):
        said, code = show(a_built_project())
        self.assertEqual(code, 0)
        self.assertEqual(statuses(said), {"idea": None, "needs": "not-started", "parts": "not-started", "requirements": "ok",
                                          "build": "ok", "breadboard": "ok", "firmware": None, "simulate": None,
                                          "deploy": "not-started"})
        self.assertEqual(said["data"]["stands_at"], "needs")
        self.assertEqual(offers(said, "build"), ["build"])
        self.assertEqual(offers(said, "requirements"), [])
        self.assertIn(zone_time.stamp(FakeClock().now()), " ".join(facts(said, "build")))

    def test_a_build_that_could_not_run_says_so_and_exits_2(self):
        said, code = show(a_built_project("could-not-run"))
        self.assertEqual((code, said["status"], statuses(said)["build"]), (2, "could-not-run", "could-not-run"))
        self.assertEqual([(item["subject"], item["code"]) for item in said["unchecked"]], [("build", "phase_could_not_run")])
        self.assertIn("build: could-not-run", facts(said, "build"))

    def test_requirements_changed_after_the_build_make_the_build_and_the_sheet_stale(self):
        project = a_built_project()
        (project / "requirements.json").write_text(json.dumps({"board": "xiao-esp32-c6-fresh", "parts": ["tactile-button"]}))
        said, code = show(project)
        self.assertEqual(code, 0)
        self.assertEqual({phase: statuses(said)[phase] for phase in ("requirements", "build", "breadboard")},
                         {"requirements": "ok", "build": "stale", "breadboard": "stale"})
        self.assertEqual(said["data"]["stands_at"], "needs")

    def test_a_sheet_built_from_other_requirements_is_stale_while_the_build_record_is_current(self):
        project = a_built_project()
        (project / "dist" / "board" / "built-from.json").write_text(json.dumps({"requirements": {"board": "x", "parts": []}}))
        said, _ = show(project)
        self.assertEqual((statuses(said)["build"], statuses(said)["breadboard"]), ("ok", "stale"))

    def test_the_same_requirements_written_again_in_other_bytes_make_the_build_and_its_sheet_stale(self):
        project = a_built_project()
        written = json.loads((project / "requirements.json").read_text())
        (project / "requirements.json").write_text(json.dumps(written, indent=4))
        said, _ = show(project)
        self.assertEqual({phase: statuses(said)[phase] for phase in ("requirements", "build", "breadboard")},
                         {"requirements": "ok", "build": "stale", "breadboard": "stale"})

    def test_requirements_that_differ_from_the_picks_are_stale(self):
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [
            {"id": "board", "does": "compute", "what": "microcontroller", "pick": [{"board": "xiao-esp32-c6"}]}])
        (project / "requirements.json").write_text(json.dumps({"board": "firebeetle2-esp32s3", "parts": []}))
        said, _ = show(project)
        self.assertEqual(statuses(said)["requirements"], "stale")
        self.assertEqual(offers(said, "requirements"), ["requirements"])

    def test_requirements_with_no_board_picked_have_problems(self):
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [
            {"id": "soil", "does": "sense", "what": "soil-moisture", "pick": [{"part": "x-many"}]}])
        (project / "requirements.json").write_text(json.dumps({"board": "xiao-esp32-c6", "parts": []}))
        said, _ = show(project)
        self.assertEqual(statuses(said)["requirements"], "problems")
        self.assertIn("board: pick one board", facts(said, "requirements")[0])

    def test_a_broken_needs_file_makes_each_phase_that_reads_it_could_not_run_and_the_rest_answer(self):
        project = Path(tempfile.mkdtemp()) / "plant-alarm"
        (project / ".spark").mkdir(parents=True)
        (project / ".spark" / "needs.json").write_text("{not json")
        said, code = show(project)
        self.assertEqual(code, 2)
        self.assertEqual({phase: statuses(said)[phase] for phase in ("needs", "parts", "requirements", "build", "deploy")},
                         {"needs": "could-not-run", "parts": "could-not-run", "requirements": "could-not-run", "build": "not-started",
                          "deploy": "not-started"})
        self.assertIn("is not JSON", facts(said, "needs")[0])
        self.assertEqual(sorted(item["subject"] for item in said["unchecked"]), ["needs", "parts", "requirements"])

    def test_the_firmware_s_time_is_said_in_the_machine_s_zone(self):
        project = a_built_project()
        (project / "firmware").mkdir()
        (project / "firmware" / "main.py").write_text("print(1)\n")
        os.utime(project / "firmware" / "main.py", (1_700_000_000, 1_700_000_000))
        said, _ = show(project)
        self.assertEqual(facts(said, "firmware"), ["firmware/main.py written %s" % zone_time.stamp(datetime.datetime.fromtimestamp(1_700_000_000))])

    def test_a_simulation_fact_says_a_passed_run_tested_the_image_or_why_not(self):
        project = a_built_project()
        (project / "sim").mkdir()
        (project / "sim" / "wokwi.toml").write_text('[wokwi]\nversion = 1\nfirmware = "image.bin"\n')
        (project / "sim" / "image.bin").write_bytes(b"an image")
        said, _ = show(project)
        self.assertIn("no run in sim/runs/ tested image.bin", facts(said, "simulate")[0])
        self.assertIn("${CLAUDE_PLUGIN_ROOT}/scripts/run_scenario.py sim/scenarios/<name>.scenario.yaml uses Wokwi CI minutes", facts(said, "simulate"))
        self.assertIsNone(statuses(said)["simulate"])


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
        for text in ("{not json", "[]"):
            (project / BUILD_RECORD_FILE).write_text(text)
            with self.assertRaises(store.StoreError) as refused:
                BuildRecordStore(project).read()
            self.assertEqual(refused.exception.code, "record_file_broken")


if __name__ == "__main__":
    unittest.main()
