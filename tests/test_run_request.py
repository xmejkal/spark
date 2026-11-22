"""
RunRequest (P829 PR 2, #1187): `flow.py run-request` reads the page's request, `.spark/page-request.json`, deletes it at
once, and runs the step it names only when spark offers that key now and the page was read at the project's fingerprint
now. Fake Operations stand in for the pick, the parts list and the build, so no test writes a store or runs tsci; each
test checks the values spark gives the step, from its own offer. A refusal runs nothing and still answers.

    python3 -m unittest tests.test_run_request
"""

import contextlib
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
from fakes import FakeOutsideWorld  # noqa: E402
from spark.core.cli import HelpText, run_cli  # noqa: E402
from spark.core.operation import Operation  # noqa: E402
from spark.core.outside import build_bare_outside_world  # noqa: E402
from spark.core.result import Finding, OperationResult  # noqa: E402
from spark.design.pick_parts import NO_PASSED_OVER  # noqa: E402
from spark.flow.fingerprint import fingerprint_of  # noqa: E402
from spark.flow.phase_readers import Offer, Phase  # noqa: E402
from spark.flow.run_request import RunRequest  # noqa: E402
from spark.flow.show_flow import read_flow  # noqa: E402

#: A hand-written project: requirements.json and no needs, never built.
BUTTON_LIGHT = ROOT / "tests" / "data" / "breadboard" / "button-light"
ID = "0b5e2f3a-1c4d-4e6f-8a9b-0c1d2e3f4a5b"
#: The keys the fake phase offers: a drop, a pick, the parts list and the build.
OFFERED = ("needs-drop:light", "pick:light:led-red-5mm", "requirements", "build")


#: The one Finding of a build whose simulation stage could not run because the board's record names no Wokwi part (P1008).
NO_MODEL = Finding("could-not-run", "simulation", "board_not_in_wokwi", "the board record names no wokwi_part_type", "test it on the board")


class FakeStep(Operation):
    """Fake Operation: keeps the values of each run and answers `result`; `then` is called after each run (a build that
    writes its record)."""

    def __init__(self, name, result=None, then=None):
        self.name, self.ran, self.then = name, [], then
        self.result = result or OperationResult({"done": True}, lines=["the step said this"])

    def run(self, *, outside, **values):
        self.ran.append(values)
        if self.then:
            self.then()
        return self.result


class FakeReader:
    """Fake PhaseReader: one phase that offers `keys`."""

    def __init__(self, keys):
        self.keys = keys

    def answer(self, project):
        return Phase("parts", None, "·", "you", [], [Offer(key, "label of " + key, "effect of " + key, ()) for key in self.keys])


class RunRequestTest(unittest.TestCase):
    def setUp(self):
        home = Path(tempfile.mkdtemp())
        patcher = mock.patch.dict(os.environ, {"SPARK_HOME": str(home)})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.project = Path(tempfile.mkdtemp()) / "bl"
        shutil.copytree(BUTTON_LIGHT, self.project)
        self.readers = [FakeReader(OFFERED)]
        self.steps = {"pick": FakeStep("pick"), "requirements": FakeStep("requirements"), "build": FakeStep("build-board")}

    def seen(self):
        """The first 12 hex digits of the project's fingerprint now, as the page carries them."""
        return self.fingerprint()[:12]

    def fingerprint(self):
        return fingerprint_of(self.project, read_flow(self.project, self.readers)[0])

    def ask(self, key, seen=None, request_id=ID, **more):
        """Write the request file as the page's channel would."""
        (self.project / ".spark").mkdir(exist_ok=True)
        request = dict({"id": request_id, "key": key, "seen": self.seen() if seen is None else seen, "at": "2026-11-21T15:40:00+01:00"}, **more)
        (self.project / ".spark" / "page-request.json").write_text(json.dumps(request), encoding="utf-8")

    def run_request(self):
        """`flow.py run-request --project <project> --json` with the fake readers and steps: (the envelope, the exit code)."""
        operation = RunRequest(readers=self.readers, operations=self.steps)
        with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
            code = run_cli(HelpText("flow.py", tool="flow"), operation, ["--project", str(self.project), "--json"],
                           outside_builder=build_bare_outside_world, outside=FakeOutsideWorld())
        return json.loads(out.getvalue()), code

    def ran(self):
        return {kind: step.ran for kind, step in self.steps.items() if step.ran}

    def refused(self, key, code, **asked):
        """Ask for `key`, run, and check that nothing ran and the answer refused with `code`; the envelope."""
        self.ask(key, **asked)
        envelope, exit_code = self.run_request()
        self.assertEqual((exit_code, envelope["status"], [item["code"] for item in envelope["unchecked"]], self.ran()),
                         (2, "could-not-run", [code], {}), key)
        self.assertEqual((envelope["data"]["ran"], envelope["data"]["status"]), (False, "could-not-run"))
        return envelope


class EachKindRunsItsStepTest(RunRequestTest):
    def test_a_pick_runs_the_pick_with_the_need_and_the_part_of_its_key(self):
        self.ask("pick:light:led-red-5mm")
        envelope, code = self.run_request()
        self.assertEqual((code, envelope["tool"], envelope["op"]), (0, "flow", "run-request"))
        self.assertEqual(self.ran(), {"pick": [{"project_and_picks": [str(self.project), "light=led-red-5mm"],
                                                "passed_over": (), "dry_run": False}]})
        self.assertIs(self.steps["pick"].ran[0]["passed_over"], NO_PASSED_OVER)  # the flag left out, never a payload
        self.assertEqual(envelope["data"], {"for": ID, "key": "pick:light:led-red-5mm", "label": "label of pick:light:led-red-5mm", "ran": True,
                                            "status": "ok", "mark": "✓", "line": "ran label of pick:light:led-red-5mm: ok",
                                            "note": None, "fingerprint": self.fingerprint()})

    def test_the_parts_list_runs_the_requirements_write_with_no_dry_run_and_no_replies(self):
        self.ask("requirements")
        envelope, code = self.run_request()
        self.assertEqual((code, self.ran()), (0, {"requirements": [{"project": str(self.project), "dry_run": False, "replies": None}]}))

    def test_the_build_runs_the_build_of_the_project_s_requirements_kept_in_the_project(self):
        self.ask("build")
        envelope, code = self.run_request()
        self.assertEqual((code, self.ran()), (0, {"build": [{"requirements": str(self.project / "requirements.json"), "keep": self.project,
                                                             "sim_dir": None, "firmware": None}]}))

    def test_a_step_with_problems_answers_its_first_problem_and_exits_1(self):
        self.steps["build"] = FakeStep("build-board", OperationResult({}, [Finding("problems", "board", "a_code", "the board has no pins", "fix it")]))
        self.ask("build")
        envelope, code = self.run_request()
        self.assertEqual((code, envelope["status"], [item["code"] for item in envelope["problems"]]), (1, "problems", ["a_code"]))
        self.assertEqual({key: envelope["data"][key] for key in ("ran", "status", "mark", "line")},
                         {"ran": True, "status": "problems", "mark": "✗", "line": "the board has no pins"})

    def test_a_step_that_could_not_run_answers_its_reason_and_exits_2(self):
        self.steps["build"] = FakeStep("build-board", OperationResult({}, [Finding("could-not-run", None, "a_code", "tsci is not installed", "install it")]))
        self.ask("build")
        envelope, code = self.run_request()
        self.assertEqual((code, envelope["data"]["ran"], envelope["data"]["status"], envelope["data"]["line"]),
                         (2, True, "could-not-run", "tsci is not installed"))

    def test_a_build_that_stopped_only_at_the_simulation_for_no_wokwi_part_answers_built_with_a_note(self):
        """P1008: the board, the sheet and the pin map were written; only Wokwi has no model of the board."""
        self.steps["build"] = FakeStep("build-board", OperationResult({}, [NO_MODEL]))
        self.ask("build")
        envelope, code = self.run_request()
        self.assertEqual((code, envelope["status"], [item["code"] for item in envelope["unchecked"]]), (2, "could-not-run", ["board_not_in_wokwi"]))
        self.assertEqual({key: envelope["data"][key] for key in ("ran", "status", "mark", "line", "note")},
                         {"ran": True, "status": "ok", "mark": "✓", "line": "ran label of build: ok",
                          "note": "the board record names no wokwi_part_type"})

    def test_a_build_that_also_stopped_before_the_simulation_still_could_not_run(self):
        """A crash writes no build record, so an older one that stopped only at the simulation never makes it ok."""
        (self.project / ".spark").mkdir(exist_ok=True)
        (self.project / ".spark" / "build.json").write_text(json.dumps(
            {"stages": [{"name": "simulation", "status": "could-not-run", "code": "board_not_in_wokwi"}]}))
        for findings in ([Finding("could-not-run", "build", "a_code", "tsci is not installed", "install it"), NO_MODEL],
                         [Finding("could-not-run", None, "crash", "the build crashed", "report it")]):
            with self.subTest(codes=[finding.code for finding in findings]):
                self.steps["build"] = FakeStep("build-board", OperationResult({}, findings))
                self.ask("build")
                envelope, code = self.run_request()
                self.assertEqual((code, envelope["data"]["status"], envelope["data"]["note"]), (2, "could-not-run", None))

    def test_a_pick_that_could_not_run_for_the_same_code_keeps_could_not_run(self):
        self.steps["pick"] = FakeStep("pick", OperationResult({}, [NO_MODEL]))
        self.ask("pick:light:led-red-5mm")
        envelope, code = self.run_request()
        self.assertEqual((code, envelope["data"]["status"], envelope["data"]["note"]), (2, "could-not-run", None))

    def test_the_text_says_which_step_ran_by_its_label_and_how_it_ended(self):
        for result, code, first in ((OperationResult({}, [Finding("problems", "board", "a_code", "the board has no pins", "fix it")]), 1,
                                     "ran label of build: problems"),
                                    (OperationResult({}, [Finding("could-not-run", None, "a_code", "tsci is not installed", "install it")]), 2,
                                     "ran label of build: could not run"),
                                    (OperationResult({}, lines=["", "built"]), 0, "ran label of build: ok")):
            with self.subTest(first=first):
                self.steps["build"] = FakeStep("build-board", result)
                self.ask("build")
                with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
                    exit_code = run_cli(HelpText("flow.py", tool="flow"), RunRequest(readers=self.readers, operations=self.steps),
                                        ["--project", str(self.project)], outside_builder=build_bare_outside_world, outside=FakeOutsideWorld())
                self.assertEqual((exit_code, out.getvalue().splitlines()[0]), (code, first))

    def test_the_answer_holds_no_path_of_the_project_or_the_home_folder(self):
        self.steps["build"] = FakeStep("build-board", OperationResult({"at": str(self.project)}, lines=["wrote %s and %s" % (self.project, Path.home())]))
        self.ask("build")
        with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
            run_cli(HelpText("flow.py", tool="flow"), RunRequest(readers=self.readers, operations=self.steps),
                    ["--project", str(self.project)], outside_builder=build_bare_outside_world, outside=FakeOutsideWorld())
        said = out.getvalue()
        self.assertNotIn(str(self.project), said)
        self.assertNotIn(str(Path.home()), said)
        self.assertIn("<project>", said)

    def test_the_fingerprint_of_the_answer_is_the_one_after_the_run(self):
        record = self.project / ".spark" / "build.json"
        self.steps["build"] = FakeStep("build-board", then=lambda: record.write_text("{}"))
        self.ask("build")
        before = self.fingerprint()
        envelope, _ = self.run_request()
        self.assertNotEqual(envelope["data"]["fingerprint"], before)
        self.assertEqual(envelope["data"]["fingerprint"], self.fingerprint())


class OnlyWhatSparkOffersRunsTest(RunRequestTest):
    def test_a_key_the_page_never_offers_runs_nothing(self):
        for key in ("deploy", "simulate", "look", "grant", "pick:light:x --keep /", "pick:light:x=y", "pick:light:led-red-5mm:2", "build "):
            with self.subTest(key=key):
                envelope = self.refused(key, "request_not_offered")
                self.assertEqual((envelope["data"]["key"], envelope["data"]["label"]), (None, None))

    def test_a_refusal_never_copies_a_key_that_is_no_offer(self):
        key = "pick:light:" + "\x1b[2J" + "x" * 185
        self.assertEqual(len(key), 200)
        envelope = self.refused(key, "request_not_offered")
        self.assertIsNone(envelope["data"]["key"])
        self.assertNotIn("x" * 185, json.dumps(envelope))

    def test_a_kind_spark_offers_now_that_is_not_offered_in_this_project_runs_nothing(self):
        self.readers = [FakeReader(("pick:light:led-red-5mm",))]
        self.refused("build", "request_not_offered")

    def test_an_offered_key_of_a_kind_the_page_never_runs_runs_nothing(self):
        """A later phase may offer a deploy or a simulation; the page runs only a pick, the parts list and the build (D9)."""
        self.readers = [FakeReader(OFFERED + ("deploy", "simulate:main"))]
        for key in ("deploy", "simulate:main"):
            with self.subTest(key=key):
                self.refused(key, "request_not_offered")

    def test_a_drop_is_asked_in_the_chat_and_runs_nothing(self):
        envelope = self.refused("needs-drop:light", "request_in_chat")
        self.assertEqual(envelope["data"]["line"], "the request names a step that is asked in the chat, never from the page, so nothing ran")

    def test_a_page_read_before_the_project_changed_is_stale_and_runs_nothing(self):
        self.refused("build", "request_stale", seen="0123456789ab")

    def test_a_second_build_from_the_same_page_is_stale_once_the_first_ran(self):
        record = self.project / ".spark" / "build.json"
        self.steps["build"] = FakeStep("build-board", then=lambda: record.write_text("{}"))
        seen = self.seen()
        self.ask("build", seen=seen)
        self.assertEqual(self.run_request()[1], 0)
        self.ask("build", seen=seen)
        envelope, code = self.run_request()
        self.assertEqual((code, [item["code"] for item in envelope["unchecked"]], len(self.steps["build"].ran)), (2, ["request_stale"], 1))

    def test_a_double_click_on_a_pick_is_stale_though_the_pick_is_no_offer_any_more(self):
        """After the pick, the need's pick is the current one, so spark no longer offers it (P976); the second click is stale."""
        reader = FakeReader(OFFERED)
        self.readers = [reader]
        needs_file = self.project / ".spark" / "needs.json"

        def picked():
            needs_file.write_text("{}")
            reader.keys = ("needs-drop:light", "requirements", "build")
        self.steps["pick"] = FakeStep("pick", then=picked)
        seen = self.seen()
        self.ask("pick:light:led-red-5mm", seen=seen)
        self.assertEqual(self.run_request()[1], 0)
        self.ask("pick:light:led-red-5mm", seen=seen)
        envelope, code = self.run_request()
        self.assertEqual((code, [item["code"] for item in envelope["unchecked"]], len(self.steps["pick"].ran)), (2, ["request_stale"], 1))
        self.assertEqual((envelope["data"]["key"], envelope["data"]["label"]), (None, None))

    def test_a_refusal_answers_whom_it_is_for_and_says_nothing_ran(self):
        envelope = self.refused("deploy", "request_not_offered")
        self.assertEqual(envelope["data"], {"for": ID, "key": None, "label": None, "ran": False, "status": "could-not-run", "mark": "?",
                                            "line": "the request names a step that spark does not offer now, so nothing ran",
                                            "note": None, "fingerprint": self.fingerprint()})

    def test_a_refusal_of_an_offered_key_names_its_offer(self):
        envelope = self.refused("build", "request_stale", seen="0123456789ab")
        self.assertEqual((envelope["data"]["key"], envelope["data"]["label"]), ("build", "label of build"))

    def test_each_refusal_tells_claude_how_to_get_a_new_page_first(self):
        fixes = {}
        for key, code, seen in (("deploy", "request_not_offered", None), ("build", "request_stale", "0123456789ab")):
            fixes[code] = self.refused(key, code, seen=seen)["unchecked"][0]["fix"]
        self.assertEqual(fixes, {"request_not_offered": "write the page again with flow.py page, then click again: the page shows the steps "
                                                        "spark offers now",
                                 "request_stale": "write the page again with flow.py page, then click again"})

    def test_a_stale_refusal_says_the_project_changed(self):
        envelope = self.refused("build", "request_stale", seen="0123456789ab")
        self.assertEqual(envelope["data"]["line"], "the project changed after the page was read, so nothing ran")


class AMalformedRequestRunsNothingTest(RunRequestTest):
    def test_an_id_that_is_no_uuid_is_malformed(self):
        for request_id in ("0b5e2f3a-1c4d-4e6f-8a9b-0c1d2e3f4a5b;rm", " %s " % ID, ID + "\n", "x", "", 7, None):
            with self.subTest(request_id=request_id):
                envelope = self.refused("build", "request_malformed", request_id=request_id)
                self.assertIsNone(envelope["data"]["for"])

    def test_a_seen_that_is_not_12_hex_digits_is_malformed(self):
        for seen in ("0123456789abc", "0123456789a", "0123456789AB", "0123456789a;"):
            with self.subTest(seen=seen):
                envelope = self.refused("build", "request_malformed", seen=seen)
                self.assertEqual(envelope["data"]["for"], ID)

    def test_a_key_that_is_no_text_is_malformed(self):
        for key in (["build"], 3, None, ""):
            with self.subTest(key=key):
                envelope = self.refused(key, "request_malformed")
                self.assertIsNone(envelope["data"]["key"])

    def test_a_file_that_is_no_json_object_or_no_file_is_malformed(self):
        for text in ("not json", "[]", '"build"'):
            with self.subTest(text=text):
                (self.project / ".spark").mkdir(exist_ok=True)
                (self.project / ".spark" / "page-request.json").write_text(text)
                envelope, code = self.run_request()
                self.assertEqual((code, [item["code"] for item in envelope["unchecked"]], self.ran()), (2, ["request_malformed"], {}))
        envelope, code = self.run_request()
        self.assertEqual((code, [item["code"] for item in envelope["unchecked"]], envelope["data"]["for"]), (2, ["request_malformed"], None))
        self.assertEqual(envelope["data"]["line"], "the request file is missing, is no regular file or no JSON object, holds an id, key or seen that cannot be read, or could not be deleted, so nothing ran")
        self.assertEqual(envelope["unchecked"][0]["fix"], "write the page's request to .spark/page-request.json as the page sent it. If it was "
                                                          "written that way, ask the person to click again")

    def test_a_request_file_that_is_a_folder_is_malformed_and_left_alone_every_time(self):
        folder = self.project / ".spark" / "page-request.json"
        folder.mkdir(parents=True)
        for _ in range(2):
            with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()) as err:
                code = run_cli(HelpText("flow.py", tool="flow"), RunRequest(readers=self.readers, operations=self.steps),
                               ["--project", str(self.project), "--json"], outside_builder=build_bare_outside_world, outside=FakeOutsideWorld())
            self.assertEqual((code, [item["code"] for item in json.loads(out.getvalue())["unchecked"]], err.getvalue()), (2, ["request_malformed"], ""))
        self.assertTrue(folder.is_dir())
        self.assertNotIn(str(self.project), out.getvalue())

    def test_a_request_the_folder_will_not_let_go_runs_nothing(self):
        """A file that cannot be deleted could run again, so it runs nothing now."""
        self.ask("build")
        spark = self.project / ".spark"
        spark.chmod(0o500)
        self.addCleanup(spark.chmod, 0o700)
        if os.access(spark, os.W_OK):
            self.skipTest("this user may write a read-only folder (root), so the delete cannot be refused")
        envelope, code = self.run_request()
        self.assertEqual((code, [item["code"] for item in envelope["unchecked"]], self.ran()), (2, ["request_malformed"], {}))


class TheRequestFileIsGoneTest(RunRequestTest):
    def test_the_request_file_is_deleted_after_every_run(self):
        for key, seen, request_id in (("build", None, ID), ("deploy", None, ID), ("build", "0123456789ab", ID), ("build", None, "x")):
            with self.subTest(key=key, seen=seen, request_id=request_id):
                self.ask(key, seen=seen, request_id=request_id)
                self.run_request()
                self.assertFalse((self.project / ".spark" / "page-request.json").exists())


class TheVerbTest(unittest.TestCase):
    def test_flow_py_run_request_reads_the_real_offers_and_refuses_a_step_that_is_not_offered(self):
        """button-light is written by hand: no needs, so the parts list is not offered, and a request for it runs nothing."""
        with tempfile.TemporaryDirectory() as home, tempfile.TemporaryDirectory() as folder:
            project = Path(folder) / "bl"
            shutil.copytree(BUTTON_LIGHT, project)
            (project / ".spark").mkdir()
            seen = fingerprint_of(project, read_flow(project)[0])[:12]
            (project / ".spark" / "page-request.json").write_text(json.dumps({"id": ID, "key": "requirements", "seen": seen}))
            with mock.patch.dict(os.environ, {"SPARK_HOME": home}), contextlib.redirect_stdout(io.StringIO()) as out, \
                    contextlib.redirect_stderr(io.StringIO()):
                code = flow.main(["run-request", "--project", str(project), "--json"])
            envelope = json.loads(out.getvalue())
            self.assertEqual((code, envelope["op"], [item["code"] for item in envelope["unchecked"]]), (2, "run-request", ["request_not_offered"]))
            self.assertFalse((project / ".spark" / "page-request.json").exists())

    def test_a_refused_pick_and_the_current_pick_are_no_offers_so_a_request_for_either_runs_nothing(self):
        """P976 (#1416): a pick spark would refuse (none free) and the need's current pick are not offered; another is."""
        with tempfile.TemporaryDirectory() as home, tempfile.TemporaryDirectory() as folder:
            for part, entry in (("x-held", {"count": 3, "used_in": {"smartbin-local": 3}}), ("x-many", {"count": "many"})):
                for kind, held in (("catalog", {"id": part, "name": "A soil probe", "kind": "sensor",
                                                "function": [{"does": "sense", "what": "soil-moisture"}]}),
                                   ("drawer", dict({"label": part, "is": {"part": part}}, **entry))):
                    (Path(home) / kind).mkdir(exist_ok=True)
                    (Path(home) / kind / (part + ".json")).write_text(json.dumps(dict({"schema": 1}, **held)))
            project = Path(folder) / "plant-alarm"
            (project / ".spark").mkdir(parents=True)
            (project / ".spark" / "needs.json").write_text(json.dumps({"schema": 1, "needs": [
                {"id": "soil", "does": "sense", "what": "soil-moisture", "pick": [{"part": "x-many"}]},
                {"id": "wet", "does": "sense", "what": "soil-moisture"}]}))
            pick = FakeStep("pick")
            with mock.patch.dict(os.environ, {"SPARK_HOME": home}):
                for key, code in (("pick:soil:x-held", "request_not_offered"), ("pick:soil:x-many", "request_not_offered"),
                                  ("pick:wet:x-held", "request_not_offered"), ("pick:wet:x-many", None)):
                    seen = fingerprint_of(project, read_flow(project)[0])[:12]
                    (project / ".spark" / "page-request.json").write_text(json.dumps({"id": ID, "key": key, "seen": seen}))
                    with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
                        run_cli(HelpText("flow.py", tool="flow"), RunRequest(operations={"pick": pick}),
                                ["--project", str(project), "--json"], outside_builder=build_bare_outside_world, outside=FakeOutsideWorld())
                    self.assertEqual([item["code"] for item in json.loads(out.getvalue())["unchecked"]], [code] if code else [], key)
            self.assertEqual([values["project_and_picks"][1] for values in pick.ran], ["wet=x-many"])

    def test_the_real_build_offer_of_a_hand_written_project_runs_the_build(self):
        with tempfile.TemporaryDirectory() as home, tempfile.TemporaryDirectory() as folder:
            project = Path(folder) / "bl"
            shutil.copytree(BUTTON_LIGHT, project)
            (project / ".spark").mkdir()
            with mock.patch.dict(os.environ, {"SPARK_HOME": home}):
                seen = fingerprint_of(project, read_flow(project)[0])[:12]
                (project / ".spark" / "page-request.json").write_text(json.dumps({"id": ID, "key": "build", "seen": seen}))
                build = FakeStep("build-board")
                with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
                    code = run_cli(HelpText("flow.py", tool="flow"), RunRequest(operations={"build": build}),
                                   ["--project", str(project), "--json"], outside_builder=build_bare_outside_world, outside=FakeOutsideWorld())
            self.assertEqual((code, json.loads(out.getvalue())["data"]["ran"]), (0, True))
            self.assertEqual(build.ran, [{"requirements": str(project / "requirements.json"), "keep": project, "sim_dir": None, "firmware": None}])


if __name__ == "__main__":
    unittest.main()
