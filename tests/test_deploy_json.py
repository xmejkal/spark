"""P213 PR a (#192): look.py --json and deploy.py --json print one outcomes.envelope, and change no text and no exit code."""

import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  P172: this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import board_doctor  # noqa: E402
import deploy_service  # noqa: E402
import firmware_platform  # noqa: E402
import tools  # noqa: E402
import outcomes  # noqa: E402
from fakes import FakeConsent, FakeConsoleProbe  # noqa: E402
from test_board_look import FOUND, done, found  # noqa: E402
import test_deploy_gate  # noqa: E402
from test_deploy_gate import GateCase  # noqa: E402
from test_look import LookScriptCase  # noqa: E402

PORT = "/dev/cu.usbmodem101"
KEYS = {"envelope", "tool", "op", "status", "data", "problems", "unchecked", "next", "truncated"}


class JsonCase:
    """Mixin: one envelope on stdout, and its status is the exit code's."""

    def one(self, code, said, tool, op):
        self.assertEqual(len(said), 1, said)
        envelope = json.loads(said[0])
        self.assertEqual(set(envelope) - {"notes"}, KEYS)
        self.assertEqual((envelope["envelope"], envelope["tool"], envelope["op"]), (1, tool, op))
        self.assertEqual(outcomes.EXIT_FOR[envelope["status"]], code)
        return envelope


class LookJsonTest(JsonCase, LookScriptCase):
    def test_a_matching_board_gives_the_token_and_the_deploy_step_that_needs_a_yes(self):
        self.run_the_scenario()
        code, said, err = self.go("--json")
        said = self.one(code, said, "look", "look")
        self.assertEqual((code, said["status"], said["problems"], said["unchecked"]), (0, "ok", [], []))
        self.assertEqual(said["data"]["token"], self.token())
        self.assertEqual((said["data"]["verdict"], said["data"]["port"], said["data"]["board"]), ("match", PORT, "xiao-esp32-c6"))
        step, = said["next"]
        self.assertEqual((step["op"], step["needs_yes"], step["effects"]), ("deploy", True, ["deletes", "writes"]))
        self.assertEqual(step["argv"], ["--project", str(self.project.resolve()), "--token", self.token(), "--port", PORT])
        self.assertIn("not the yes", step["why"])

    def test_the_text_run_is_the_same_with_or_without_the_flag(self):
        self.run_the_scenario()
        _, text, _ = self.go()
        self.assertTrue(text[-1].startswith("  token  "))

    def test_a_stop_is_a_problem_with_no_token_and_no_deploy_step(self):
        self.run_the_scenario()
        self.board("firebeetle2-esp32s3")
        code, said, _ = self.go("--json")
        said = self.one(code, said, "look", "look")
        self.assertEqual((code, said["status"], said["data"]["token"], said["next"]), (1, "problems", None, []))
        self.assertEqual(said["problems"][0]["subject"], "stop")
        self.assertIn("this board is an esp32c6", said["problems"][0]["sentence"])

    def test_a_flash_that_differs_but_fits_is_a_problem_and_keeps_its_token_and_step(self):
        self.run_the_scenario()
        self.board("firebeetle2-esp32s3")
        code, said, _ = self.go("--json", esptool="s3-flash-id-8mb.txt")
        said = self.one(code, said, "look", "look")
        self.assertEqual((code, said["status"], said["problems"][0]["subject"]), (1, "problems", "flash"))
        self.assertIsNotNone(said["data"]["token"])
        self.assertEqual(said["next"][0]["op"], "deploy")

    def test_an_unknown_field_is_unchecked_not_a_pass_and_still_has_its_step(self):
        self.run_the_scenario()
        code, said, _ = self.go("--json", esptool="c6-flash-id-garbled.txt")
        said = self.one(code, said, "look", "look")
        self.assertEqual((code, said["status"], said["problems"]), (2, "could-not-run", []))
        self.assertIn("flash", said["unchecked"][0]["sentence"])
        self.assertEqual(said["next"][0]["op"], "deploy")

    def test_no_token_is_unchecked_and_has_no_deploy_step(self):
        code, said, _ = self.go("--json")
        said = self.one(code, said, "look", "look")
        self.assertEqual((code, said["status"], said["data"]["token"]), (2, "could-not-run", None))
        self.assertRegex(said["unchecked"][-1]["sentence"], "run a scenario first")
        self.assertEqual(said["next"], [])

    def test_a_look_that_stopped_has_no_data_and_says_why(self):
        code, said, err = self.go("--json", devs="mpremote-devs-none.txt")
        said = self.one(code, said, "look", "look")
        self.assertEqual((code, said["status"], said["data"]), (2, "could-not-run", None))
        self.assertIn("no board found", said["unchecked"][0]["sentence"])
        self.assertIn("no board found", err)  # the text still goes to stderr

    def test_a_failed_read_gives_the_doctor_s_result_and_its_step_as_the_fix(self):
        result = board_doctor.BoardDoctorResult((), "boom", "hold_boot", None)
        with mock.patch.object(board_doctor, "after_esptool", return_value=result):
            code, said, err = self.go("--json", text="x", esptool="c6-flash-id.txt", fail=True)
        said = self.one(code, said, "look", "look")
        self.assertEqual((code, said["data"]["doctor"]["next_step"]), (2, "hold_boot"))
        self.assertEqual(said["unchecked"][0]["fix"], "hold the board's BOOT (B) button, press and release R, release BOOT, and run it again. After it, press R once so the firmware starts")

    def test_status_is_the_exit_code_for_every_fixture(self):
        self.run_the_scenario()
        for esptool in ("c6-flash-id.txt", "c6-flash-id-garbled.txt", "c6-flash-id-no-mac.txt", "wrong-chip.txt"):
            code, said, _ = self.go("--json", esptool=esptool)
            self.one(code, said, "look", "look")


class DeployJsonTest(JsonCase, GateCase):
    def go(self, *argv, **kw):
        code, said, err = self.deploy("--json", *argv, **kw)
        return code, said.splitlines(), err

    def ready(self, **kw):
        self.run_the_scenario()
        return self.go("--token", self.token(), consent=FakeConsent(True), **kw)

    def test_a_flash_that_is_ready_gives_every_fact_and_no_text_on_stdout(self):
        code, said, err = self.ready()
        said = self.one(code, said, "deploy", "deploy")
        data = said["data"]
        self.assertEqual((code, said["status"], said["problems"], said["unchecked"], said["next"]), (0, "ok", [], [], []))
        self.assertEqual((data["stage"], data["dry_run"], data["token"]), ("verify", False, self.token()))
        self.assertEqual(data["yes"]["kind"], "typed")
        self.assertEqual(data["ready"]["verdict"], "ready seen")
        self.assertEqual(data["look"]["verdict"], "match")
        self.assertEqual(data["commands"][0][-1], "erase_flash")
        self.assertTrue(Path(data["board_log"]).is_file())
        self.assertTrue(data["facts_line"].startswith("facts file spark.json sha256: "))
        self.assertIn("ready seen", err)  # the lines a person reads went to stderr

    def test_the_text_run_still_prints_the_same_lines_on_stdout(self):
        self.run_the_scenario()
        code, said, err = self.deploy("--token", self.token(), consent=FakeConsent(True))
        self.assertIn("ready seen", said)
        self.assertEqual((code, err), (0, ""))

    def test_a_standing_grant_is_the_yes_of_kind_grant(self):
        case = test_deploy_gate.TheStandingYesTest("test_a_deploy_grant_erases_with_no_terminal_and_the_record_names_the_standing_yes")
        case.setUp()
        try:
            case.give()
            code, said, _ = case.deploy("--json", "--token", case.token(), grant_service=case.grants)
        finally:
            case.doCleanups()
        said = self.one(code, said.splitlines(), "deploy", "deploy")
        self.assertEqual((said["data"]["yes"]["kind"], said["data"]["yes"]["who"][:18]), ("grant", "standing yes typed"))

    def test_no_terminal_is_unchecked_and_hands_the_person_the_line(self):
        self.run_the_scenario()
        token = self.token()
        code, said, _ = self.go("--token", token)
        said = self.one(code, said, "deploy", "deploy")
        self.assertEqual((code, said["status"], said["data"]["stage"], self.flashed()), (2, "could-not-run", "gate", []))
        self.assertIn("no terminal", said["unchecked"][0]["sentence"])
        self.assertIsNone(said["data"]["yes"])  # no yes was given
        self.assertIn("--token %s" % token, said["data"]["run_in_terminal"])
        ops = [step["op"] for step in said["next"]]
        self.assertEqual(ops, ["deploy", "grant"])
        self.assertTrue(said["next"][0]["needs_yes"])
        self.assertIn("own terminal", said["next"][0]["why"])
        self.assertEqual(said["next"][1]["effects"], ["writes"])

    def test_no_token_points_to_the_look(self):
        self.run_the_scenario()
        code, said, _ = self.go(consent=FakeConsent(True))
        said = self.one(code, said, "deploy", "deploy")
        self.assertEqual((code, said["status"], [s["op"] for s in said["next"]]), (2, "could-not-run", ["look"]))

    def test_a_stop_is_a_problem_named_gate(self):
        self.run_the_scenario()
        self.board("firebeetle2-esp32s3")
        code, said, _ = self.go("--token", "aaaa-bbbb", consent=FakeConsent(True))
        said = self.one(code, said, "deploy", "deploy")
        self.assertEqual((code, said["status"], said["problems"][0]["subject"], said["next"]), (1, "problems", "gate", []))

    def test_the_answer_no_is_unchecked_with_no_next_step(self):
        self.run_the_scenario()
        code, said, _ = self.go("--token", self.token(), consent=FakeConsent(False))
        said = self.one(code, said, "deploy", "deploy")
        self.assertEqual((code, said["next"], self.flashed()), (2, [], []))

    def test_a_failed_flash_says_the_board_may_be_erased(self):
        self.run_the_scenario()
        code, said, _ = self.go("--token", self.token(), consent=FakeConsent(True), fails=True)
        said = self.one(code, said, "deploy", "deploy")
        self.assertEqual((said["data"]["stage"], said["data"]["board_state"]), ("flash", "may_be_erased"))

    def test_a_plan_that_cannot_be_made_has_no_look(self):
        code, said, _ = self.go()
        said = self.one(code, said, "deploy", "deploy")
        self.assertEqual((code, said["data"]["stage"], said["data"]["look"]), (2, "plan", None))
        self.assertIn("run a scenario", said["unchecked"][0]["sentence"])

    def test_the_dry_run_lists_the_commands_and_points_to_the_look(self):
        self.run_the_scenario()
        code, said, _ = self.go("--dry-run", "--port", PORT)
        said = self.one(code, said, "deploy", "deploy")
        self.assertEqual((code, said["status"], said["data"]["dry_run"], self.ran), (0, "ok", True, []))
        self.assertEqual(len(said["data"]["commands"]), 2)
        self.assertEqual([s["op"] for s in said["next"]], ["look"])
        self.assertEqual(said["next"][0]["argv"], ["--project", str(self.project.resolve()), "--port", PORT])

    def test_ready_not_seen_is_a_problem(self):
        self.prints = "no luck\n"
        code, said, _ = self.ready()
        said = self.one(code, said, "deploy", "deploy")
        self.assertEqual((code, said["problems"][0]["subject"], said["data"]["ready"]["verdict"]), (1, "ready", "ready not seen"))

    def test_ready_unknown_gives_a_watch_step_and_never_a_second_erase(self):
        self.unread = subprocess.CalledProcessError(1, "mpremote")
        code, said, _ = self.ready(probe=FakeConsoleProbe(""))
        said = self.one(code, said, "deploy", "deploy")
        self.assertEqual((code, said["status"], said["data"]["person_action"]), (2, "could-not-run", None))
        self.assertEqual([s["op"] for s in said["next"]], ["watch"])
        self.assertTrue(said["data"]["repl_command"])
        self.assertEqual(said["next"][0]["argv"], said["data"]["repl_command"])

    def test_an_r_press_that_did_not_come_names_the_person_action(self):
        self.unread = self.uncopied = subprocess.CalledProcessError(1, "mpremote")
        code, said, _ = self.ready(probe=FakeConsoleProbe("waiting for download\n", reset=False))
        said = self.one(code, said, "deploy", "deploy")
        self.assertEqual(code, 2)
        self.assertIn("R (reset) button", said["data"]["person_action"])
        self.assertEqual(said["next"][0]["op"], "watch")
        self.assertIn("R", said["next"][0]["why"])

    def test_a_store_record_that_was_not_written_is_said_beside_the_null(self):
        import store
        with mock.patch.object(deploy_service.DeployService, "record", side_effect=store.StoreProblem("no")):
            code, said, _ = self.ready()
        said = self.one(code, said, "deploy", "deploy")
        self.assertEqual((code, said["data"]["store_record"], said["data"]["store_record_error"]), (0, None, "no"))

    def test_the_flash_tool_writes_to_the_descriptor_it_is_given(self):
        self.run_the_scenario()
        seen = []
        platform = firmware_platform.FirmwarePlatform.micropython(self.project)
        for echo_to, expected in ((2, {"stdout": 2}), (None, {})):
            seen.clear()
            service = deploy_service.DeployService(self.project, platform, echo_to=echo_to,
                                                   run=lambda command, **kw: seen.append(kw) or done(""))
            with mock.patch.object(tools, "find", side_effect=lambda name, *a, **k: FOUND["flasher"] if name == "flasher" else found(name)):
                service.deploy(self.look(), self.token(), FakeConsent(True), lambda line: None)
            self.assertEqual(seen, [dict(check=True, **expected)] * 2)


if __name__ == "__main__":
    unittest.main()
