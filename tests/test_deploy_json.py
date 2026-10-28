"""P213 PR a (#192): look.py --json and deploy.py --json print one outcomes.envelope, and change no text and no exit code."""

import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import board_doctor  # noqa: E402
import board_envelope  # noqa: E402
import boards  # noqa: E402
import deploy_service  # noqa: E402
import firmware_platform  # noqa: E402
import image_evidence  # noqa: E402
import tools  # noqa: E402
import outcomes  # noqa: E402
import store  # noqa: E402
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
        self.assertEqual((said["problems"][0]["subject"], said["problems"][0]["code"]), ("stop", "chip_differs"))
        self.assertIn("this board is an esp32c6", said["problems"][0]["sentence"])

    def test_a_flash_that_differs_but_fits_is_a_problem_and_keeps_its_token_and_step(self):
        self.run_the_scenario()
        self.board("firebeetle2-esp32s3")
        code, said, _ = self.go("--json", esptool="s3-flash-id-8mb.txt")
        said = self.one(code, said, "look", "look")
        self.assertEqual((code, said["status"], said["problems"][0]["subject"], said["problems"][0]["code"]),
                         (1, "problems", "flash", "flash_differs"))
        self.assertIsNotNone(said["data"]["token"])
        self.assertEqual(said["next"][0]["op"], "deploy")

    def test_an_unknown_field_is_unchecked_not_a_pass_and_still_has_its_step(self):
        self.run_the_scenario()
        code, said, _ = self.go("--json", esptool="c6-flash-id-garbled.txt")
        said = self.one(code, said, "look", "look")
        self.assertEqual((code, said["status"], said["problems"]), (2, "could-not-run", []))
        self.assertIn("flash", said["unchecked"][0]["sentence"])
        self.assertEqual(said["unchecked"][0]["code"], "field_unknown")
        self.assertEqual(said["next"][0]["op"], "deploy")

    def test_a_last_deploy_that_cannot_be_read_is_unchecked_not_ok_and_keeps_its_token_and_step(self):
        self.run_the_scenario()
        record = store.place("boards") / (store.slug("8c:bf:ea:xx:xx:xx") + ".json")
        record.parent.mkdir(parents=True, exist_ok=True)
        record.write_text("{not json")
        code, said, _ = self.go("--json")
        said = self.one(code, said, "look", "look")
        self.assertEqual((code, said["status"], said["problems"]), (2, "could-not-run", []))
        self.assertEqual(said["unchecked"], [{"code": "last_deploy_not_checked",
                                              "sentence": "last deploy not checked: spark's record of it cannot be read",
                                              "fix": "repair or remove %s, then run look.py again" % record}])
        self.assertTrue(said["data"]["token"])
        self.assertEqual(said["next"][0]["op"], "deploy")

    def test_a_board_whose_mac_was_not_read_has_two_unchecked_items_the_token_and_the_last_deploy(self):
        self.run_the_scenario()
        code, said, _ = self.go("--json", esptool="c6-flash-id-no-mac.txt")
        said = self.one(code, said, "look", "look")
        self.assertEqual((code, said["status"]), (2, "could-not-run"))
        self.assertEqual(said["unchecked"][-1], {"code": "last_deploy_not_checked",
                                                 "sentence": "last deploy not checked: the board's MAC was not read",
                                                 "fix": "reconnect the board so that its MAC can be read, then run look.py again"})
        self.assertTrue(said["unchecked"][-2]["sentence"].startswith("no token: "))
        self.assertEqual(said["unchecked"][-2]["code"], "no_mac")

    def test_no_token_is_unchecked_and_has_no_deploy_step(self):
        code, said, _ = self.go("--json")
        said = self.one(code, said, "look", "look")
        self.assertEqual((code, said["status"], said["data"]["token"]), (2, "could-not-run", None))
        self.assertRegex(said["unchecked"][-1]["sentence"], "run a scenario first")
        self.assertEqual(said["unchecked"][-1]["code"], "no_image")
        self.assertEqual(said["next"], [])

    def test_a_look_that_stopped_has_no_data_and_says_why(self):
        code, said, err = self.go("--json", devs="mpremote-devs-none.txt")
        said = self.one(code, said, "look", "look")
        self.assertEqual((code, said["status"], said["data"]), (2, "could-not-run", None))
        self.assertIn("no board found", said["unchecked"][0]["sentence"])
        self.assertEqual(said["unchecked"][0]["code"], "no_port")
        self.assertIn("no board found", err)  # the text still goes to stderr

    def test_a_failed_read_gives_the_doctor_s_result_and_its_step_as_the_fix(self):
        result = board_doctor.BoardDoctorResult((), "boom", "hold_boot", None)
        with mock.patch.object(board_doctor, "after_esptool", return_value=result):
            code, said, err = self.go("--json", text="x", esptool="c6-flash-id.txt", fail=True)
        said = self.one(code, said, "look", "look")
        self.assertEqual((code, said["data"]["doctor"]["next_step"]), (2, "hold_boot"))
        self.assertEqual(said["unchecked"][0]["code"], "board_not_read")
        self.assertEqual(said["unchecked"][0]["fix"], "hold the board's BOOT button (B, top right, beside the USB-C), press and release RESET (R, top left, beside the USB-C), release BOOT, and run it again. After it, press RESET once so the firmware starts. Left and right as seen with the metal shield facing you, USB-C at the top")

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
        self.assertEqual(data["image_sha256"], hashlib.sha256(self.image.read_bytes()).hexdigest())  # P213
        self.assertIn("ready seen", err)  # the lines a person reads went to stderr

    def test_the_text_run_still_prints_the_same_lines_on_stdout(self):
        self.run_the_scenario()
        code, said, err = self.deploy("--token", self.token(), consent=FakeConsent(True))
        self.assertIn("ready seen", said)
        self.assertEqual((code, err), (0, ""))

    def test_the_look_report_of_the_text_run_shows_a_port_with_a_newline_and_an_override_as_one_line(self):
        # P423: the port is the person's own --port; the report's items are guarded one by one
        self.run_the_scenario()
        port = "/dev/cu.usb\u202emodem\n  FAKE"
        code, said, err = self.deploy("--token", self.token(), "--port", port, consent=FakeConsent(True))
        self.assertEqual((code, err), (0, ""))
        self.assertIn("  port   /dev/cu.usb?modem?  FAKE", said.splitlines())
        self.assertNotIn("\u202e", said)

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
        self.assertEqual(said["unchecked"][0]["code"], "no_terminal")
        self.assertIsNone(said["data"]["yes"])  # no yes was given
        self.assertIsNone(said["data"]["image_sha256"])  # nothing was flashed (P213)
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
        self.assertEqual(said["unchecked"][0]["fix"], "run look.py again")  # no doctor: the fix of the next op
        self.assertEqual(said["unchecked"][0]["code"], "token_missing")

    def test_a_token_that_is_not_this_board_s_and_this_image_s_is_stale(self):
        self.run_the_scenario()
        code, said, _ = self.go("--token", "aaaa-bbbb", consent=FakeConsent(True))
        said = self.one(code, said, "deploy", "deploy")
        self.assertEqual((code, said["unchecked"][0]["code"], [s["op"] for s in said["next"]]), (2, "token_stale", ["look"]))

    def test_the_doctor_s_fix_names_the_project_s_own_buttons(self):
        self.run_the_scenario()
        hold = test_deploy_gate.TheBusyPortTest.BUSY._replace(next_step="hold_boot")
        with mock.patch.object(board_doctor, "after_esptool", return_value=hold):
            code, said, _ = self.go("--token", "aaaa-bbbb", consent=FakeConsent(True), look_fails=True)
        fix = self.one(code, said, "deploy", "deploy")["unchecked"][0]["fix"]
        self.assertEqual(fix, board_doctor.step_sentence("hold_boot", boards.ButtonPlaces.of_project(self.project)))
        self.assertNotEqual(fix, board_doctor.step_sentence("hold_boot"))

    def test_a_stop_is_a_problem_named_gate(self):
        self.run_the_scenario()
        self.board("firebeetle2-esp32s3")
        code, said, _ = self.go("--token", "aaaa-bbbb", consent=FakeConsent(True))
        said = self.one(code, said, "deploy", "deploy")
        self.assertEqual((code, said["status"], said["problems"][0]["subject"], said["next"]), (1, "problems", "gate", []))
        self.assertEqual(said["problems"][0]["code"], "chip_differs")

    def test_a_busy_port_gives_the_doctor_s_result_and_its_step_as_the_fix(self):
        self.run_the_scenario()
        with mock.patch.object(board_doctor, "after_esptool", return_value=test_deploy_gate.TheBusyPortTest.BUSY):
            code, said, _ = self.go("--token", "aaaa-bbbb", consent=FakeConsent(True), look_fails=True)
        said = self.one(code, said, "deploy", "deploy")
        self.assertEqual((code, said["data"]["doctor"]["next_step"]), (2, "close_other"))
        self.assertEqual(said["unchecked"][0]["fix"], board_doctor.step_sentence("close_other"))

    def test_a_stop_with_no_doctor_result_has_no_doctor_and_no_fix(self):
        self.run_the_scenario()
        code, said, _ = self.go("--token", "aaaa-bbbb", consent=FakeConsent(True), devs="mpremote-devs-none.txt")
        said = self.one(code, said, "deploy", "deploy")
        self.assertEqual((code, "doctor" in said["data"], said["unchecked"][0]["fix"]), (2, False, ""))
        self.assertEqual(said["unchecked"][0]["code"], "no_port")

    def test_doctor_fix_is_the_step_s_sentence_or_nothing(self):
        busy = test_deploy_gate.TheBusyPortTest.BUSY
        self.assertEqual(board_envelope.doctor_fix(busy, boards.ButtonPlaces.EMPTY), board_doctor.step_sentence("close_other"))
        self.assertEqual((board_envelope.doctor_fix(None, boards.ButtonPlaces.EMPTY),
                          board_envelope.doctor_fix(busy._replace(next_step=None), boards.ButtonPlaces.EMPTY)), ("", ""))

    def test_the_answer_no_is_unchecked_with_no_next_step(self):
        self.run_the_scenario()
        code, said, _ = self.go("--token", self.token(), consent=FakeConsent(False))
        said = self.one(code, said, "deploy", "deploy")
        self.assertEqual((code, said["next"], self.flashed()), (2, [], []))
        self.assertEqual(said["unchecked"][0]["code"], "answered_no")

    def test_a_failed_flash_says_the_board_may_be_erased(self):
        self.run_the_scenario()
        code, said, _ = self.go("--token", self.token(), consent=FakeConsent(True), fails=2)
        said = self.one(code, said, "deploy", "deploy")
        self.assertEqual((said["data"]["stage"], said["data"]["board_state"]), ("flash", "may_be_erased"))
        self.assertEqual(said["unchecked"][0]["code"], "flash_failed")

    def test_an_erase_retried_once_gives_the_usual_envelope_and_the_retry_line_on_stderr(self):
        code, said, err = self.ready(fails=1)
        said = self.one(code, said, "deploy", "deploy")
        self.assertEqual((code, said["data"]["stage"]), (0, "verify"))
        self.assertIn("  retry in 5 s: ", err)

    def test_a_yes_that_ends_during_the_retry_wait_says_the_board_may_be_erased(self):
        self.run_the_scenario()
        code, said, _ = self.go("--token", self.token(), consent=self.ends_during_the_wait(), fails=1)
        said = self.one(code, said, "deploy", "deploy")
        self.assertEqual((said["data"]["stage"], said["data"]["board_state"]), ("flash", "may_be_erased"))
        self.assertEqual(said["unchecked"][0]["code"], "grant_ended")  # the cause the agent acts on, not the flash

    def test_a_tool_that_cannot_be_used_is_tool_missing(self):
        self.run_the_scenario()
        with mock.patch.object(deploy_service.DeployService, "plan", side_effect=tools.ToolProblem("esptool is not installed")):
            code, said, _ = self.go("--token", "aaaa-bbbb")
        said = self.one(code, said, "deploy", "deploy")
        self.assertEqual((code, said["data"]["stage"], said["unchecked"][0]["code"]), (2, "plan", "tool_missing"))
        self.assertEqual(said["unchecked"][0]["sentence"], "esptool is not installed")

    def test_a_missing_image_tool_with_no_simulation_is_tool_missing_at_the_plan(self):
        self.run_the_scenario()  # P436: the image check needs the interpreter; --no-simulation reaches it
        code, said, _ = self.go("--no-simulation", "--token", "aaaa-bbbb")  # the real check: found() has no MicroPython build to give
        said = self.one(code, said, "deploy", "deploy")
        self.assertEqual((code, said["data"]["stage"], said["unchecked"][0]["code"]), (2, "plan", "tool_missing"))
        self.assertTrue(said["unchecked"][0]["sentence"].startswith("cannot check flash-with-firmware.bin against firmware/: "))

    def test_a_board_record_that_cannot_be_read_is_chip_unknown(self):
        self.run_the_scenario()
        (self.project / "requirements.json").write_text("{}")
        code, said, _ = self.go("--token", "aaaa-bbbb")
        said = self.one(code, said, "deploy", "deploy")
        self.assertEqual((code, said["data"]["stage"], said["unchecked"][0]["code"]), (2, "plan", "chip_unknown"))

    def test_an_image_changed_while_the_person_answered_is_image_changed(self):
        main, runs = self.project / "firmware" / "main.py", self.project / "sim" / "runs"
        first = main.read_text()
        main.write_text("print('ready')\nprint('new')\n")
        self.run_the_scenario()
        rebuilt = self.image.read_bytes(), {log.name: log.read_text() for log in runs.glob("*.log")}
        main.write_text(first)
        test = self

        class ChangesTheImage(FakeConsent):
            def ask(self, question):
                test.image.write_bytes(rebuilt[0])
                for name, text in rebuilt[1].items():
                    (runs / name).write_text(text)
                return True

        self.run_the_scenario()  # the firmware as it was, built and passed; the token is of this image
        code, said, _ = self.go("--token", self.token(), consent=ChangesTheImage(True))
        said = self.one(code, said, "deploy", "deploy")
        self.assertEqual((code, said["unchecked"][0]["code"]), (2, "image_changed"))

    def test_a_log_that_tested_another_image_is_evidence_refuses(self):
        self.run_the_scenario()
        (self.project / "sim" / "runs" / "old.log").write_text("# old.scenario.yaml, run 2026-10-01\nverdict: passed\nimage sha256: 0\n\nbody\n")
        code, said, _ = self.go("--token", "aaaa-bbbb")
        said = self.one(code, said, "deploy", "deploy")
        self.assertEqual((code, said["data"]["stage"], said["unchecked"][0]["code"]), (2, "plan", "evidence_refuses"))
        self.assertIn("old.log tested another image", said["unchecked"][0]["sentence"])

    def test_a_plan_that_cannot_be_made_has_no_look(self):
        code, said, _ = self.go()
        said = self.one(code, said, "deploy", "deploy")
        self.assertEqual((code, said["data"]["stage"], said["data"]["look"]), (2, "plan", None))
        self.assertIn("run a scenario", said["unchecked"][0]["sentence"])
        self.assertEqual(said["unchecked"][0]["code"], "no_image")

    def test_the_dry_run_lists_the_commands_and_points_to_the_look(self):
        self.run_the_scenario()
        code, said, _ = self.go("--dry-run", "--port", PORT)
        said = self.one(code, said, "deploy", "deploy")
        self.assertEqual((code, said["status"], said["data"]["dry_run"], self.ran), (0, "ok", True, []))
        self.assertEqual(len(said["data"]["commands"]), 2)
        self.assertEqual([s["op"] for s in said["next"]], ["look"])
        self.assertIsNone(said["data"]["image_sha256"])  # nothing was flashed
        self.assertEqual(said["next"][0]["argv"], ["--project", str(self.project.resolve()), "--port", PORT])

    def test_ready_not_seen_is_a_problem(self):
        self.prints = "no luck\n"
        code, said, _ = self.ready()
        said = self.one(code, said, "deploy", "deploy")
        self.assertEqual((code, said["problems"][0]["subject"], said["data"]["ready"]["verdict"]), (1, "ready", "ready not seen"))
        self.assertEqual(said["problems"][0]["code"], "ready_not_seen")

    def test_ready_unknown_gives_a_watch_step_and_never_a_second_erase(self):
        self.unread = subprocess.CalledProcessError(1, "mpremote")
        code, said, _ = self.ready(probe=FakeConsoleProbe(""))
        said = self.one(code, said, "deploy", "deploy")
        self.assertEqual((code, said["status"], said["data"]["person_action"]), (2, "could-not-run", None))
        self.assertEqual([s["op"] for s in said["next"]], ["watch"])
        self.assertEqual(said["unchecked"][0]["code"], "ready_unknown")
        self.assertNotIn("needs_person", said["next"][0])  # nobody must press anything first
        self.assertTrue(said["data"]["repl_command"])
        self.assertEqual(said["next"][0]["argv"], said["data"]["repl_command"])

    def test_an_r_press_that_did_not_come_names_the_person_action(self):
        self.unread = self.uncopied = subprocess.CalledProcessError(1, "mpremote")
        code, said, _ = self.ready(probe=FakeConsoleProbe("waiting for download\n", reset=False))
        said = self.one(code, said, "deploy", "deploy")
        self.assertEqual(code, 2)
        self.assertIn("press the board's RESET (R, top left, beside the USB-C) once", said["data"]["person_action"])
        self.assertEqual(said["next"][0]["op"], "watch")
        self.assertIs(said["next"][0]["needs_person"], True)
        self.assertIn("First the person presses the board's RESET (R, top left, beside the USB-C)", said["next"][0]["why"])

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
            service = deploy_service.DeployService(self.project, platform, image_evidence.PassedRunEvidence(), echo_to=echo_to,
                                                   run=lambda command, **kw: seen.append(kw) or done(""))
            with mock.patch.object(tools, "find", side_effect=lambda name, *a, **k: FOUND["flasher"] if name == "flasher" else found(name)):
                service.deploy(self.look(), self.token(), FakeConsent(True), lambda line: None)
            self.assertEqual(seen, [dict(check=True, **expected)] * 2)


if __name__ == "__main__":
    unittest.main()
