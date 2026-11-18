"""P920 (#1302): a project that is not spark's registers once in spark's store, then records its deploys. bench.py register
writes the name and the launcher, bench.py record adds one deploy by the USB serial's MAC part and opens no port, and the
view and the look name the project and its tool."""

import contextlib
import datetime
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import bench  # noqa: E402
import golden_bench  # noqa: E402
from spark import bench as bench_area  # noqa: E402
from spark.bench import bench_service  # noqa: E402
from spark.bench import board_look  # noqa: E402
from spark.bench import deploy_gate  # noqa: E402
from spark.bench.record_deploy import RecordDeploy  # noqa: E402
from spark.bench.register_project import RegisterProject  # noqa: E402
from spark.core import outcomes  # noqa: E402
from spark.core.errors import SparkError  # noqa: E402
from spark.records import launcher  # noqa: E402
from spark.records import records_codes  # noqa: E402
from spark.records import store  # noqa: E402
from spark.records.deploy_record_store import DeployRecordStore, LastDeploy, outside_deploy  # noqa: E402
from spark.records.registered_project_store import RegisteredProject, RegisteredProjectStore  # noqa: E402
from fakes import FakeClock, FakeOutsideWorld, pin_time_zone  # noqa: E402
from test_bench_show import BRIDGE, C6, FIRMWARE_SERIAL, MAC_A, NO_SERIAL, S3, ShowCase, StoreCase, devs_of, entry  # noqa: E402
from test_deploy import found  # noqa: E402

ORIGIN, OTHER_ORIGIN = "https://example.org/someone/pixel-games.git", "https://example.org/another/pixel-games.git"
#: The moment of the record: in Prague's winter zone, with seconds, so neither a lost zone nor a lost second can hide.
RECORDED_AT = datetime.datetime(2026, 11, 18, 21, 40, 17, tzinfo=datetime.timezone(datetime.timedelta(hours=1)))
REGISTERED_AT = "2026-11-18T20:13:42+01:00"


class RegisteredProjectStoreTest(StoreCase):
    def test_a_name_is_written_once_and_read_back(self):
        written = RegisteredProjectStore().register("pixel-games", ORIGIN, "box.py", REGISTERED_AT)
        self.assertEqual(written, (RegisteredProject("pixel-games", ORIGIN, "box.py", REGISTERED_AT), True))
        self.assertEqual(RegisteredProjectStore().read("pixel-games"), written[0])
        self.assertIsNone(RegisteredProjectStore().read("blink"))
        self.assertEqual(json.loads(store.place("registered-projects").read_text()),
                         {"pixel-games": {"origin": ORIGIN, "tool": "box.py", "registered": REGISTERED_AT}})

    def test_the_same_name_and_origin_changes_nothing(self):
        RegisteredProjectStore().register("pixel-games", ORIGIN, "box.py", REGISTERED_AT)
        again = RegisteredProjectStore().register("pixel-games", ORIGIN, "box.py", "2026-11-19T07:05:09+01:00")
        self.assertEqual(again, (RegisteredProject("pixel-games", ORIGIN, "box.py", REGISTERED_AT), False))

    def test_the_same_name_and_origin_with_another_tool_replaces_the_tool(self):
        RegisteredProjectStore().register("pixel-games", ORIGIN, "box.py", REGISTERED_AT)
        again = RegisteredProjectStore().register("pixel-games", ORIGIN, "deploy.sh", "2026-11-19T07:05:09+01:00")
        self.assertEqual(again, (RegisteredProject("pixel-games", ORIGIN, "deploy.sh", "2026-11-19T07:05:09+01:00"), True))
        self.assertEqual(RegisteredProjectStore().read("pixel-games").tool, "deploy.sh")

    def test_a_name_with_another_origin_is_taken_and_the_file_stays(self):
        RegisteredProjectStore().register("pixel-games", ORIGIN, "box.py", REGISTERED_AT)
        before = store.place("registered-projects").read_text()
        with self.assertRaises(SparkError) as refused:
            RegisteredProjectStore().register("pixel-games", OTHER_ORIGIN, "box.py", REGISTERED_AT)
        self.assertEqual(refused.exception.code, "name_taken")
        self.assertEqual(store.place("registered-projects").read_text(), before)

    def test_a_name_on_the_projects_list_is_taken_also_when_its_folder_is_gone(self):
        store.write_json("projects", None, {"walk4": str(Path(tempfile.mkdtemp()) / "gone")})
        with self.assertRaises(SparkError) as refused:
            RegisteredProjectStore().register("walk4", ORIGIN, "box.py", REGISTERED_AT)
        self.assertEqual(refused.exception.code, "name_taken")
        self.assertFalse(store.place("registered-projects").exists())

    def test_a_name_that_is_not_plain_is_refused(self):
        for name in ("Pixel-Games", "../x", "-x", ""):
            with self.assertRaises(SparkError) as refused:
                RegisteredProjectStore().register(name, ORIGIN, "box.py", REGISTERED_AT)
            self.assertEqual(refused.exception.code, "key_not_plain", name)

    def test_a_file_that_is_no_object_of_registrations_is_a_store_error(self):
        store.place("registered-projects").parent.mkdir(parents=True, exist_ok=True)
        for text in ("{not json", '["pixel-games"]', '{"pixel-games": {"origin": 7}}'):
            store.place("registered-projects").write_text(text)
            with self.assertRaises(store.StoreError) as refused:
                RegisteredProjectStore().read("pixel-games")
            self.assertEqual(refused.exception.code, "record_file_broken", text)

    def test_the_file_is_private(self):
        RegisteredProjectStore().register("pixel-games", ORIGIN, "box.py", REGISTERED_AT)
        self.assertEqual(store.place("registered-projects").stat().st_mode & 0o777, 0o600)


class TheDeployEntryTest(StoreCase):
    def test_an_outside_deploy_holds_the_keys_of_spark_s_entry_and_made_by(self):
        self.assertEqual(outside_deploy("pixel-games", "box.py", "2026-11-18T21:40:17+01:00", "ready not read"), {
            "project": "pixel-games", "made_by": "box.py", "deployed": "2026-11-18T21:40:17+01:00", "verdict": "ready not read",
            "image_sha256": None, "simulation": None, "yes": None, "micropython_banner": None})

    def test_append_deploy_with_no_board_keeps_the_record_s_board(self):
        self.deploys(MAC_A, [entry("walk4", "2026-11-17T08:04:00+01:00")], board="firebeetle2-esp32s3")
        added = outside_deploy("pixel-games", "box.py", "2026-11-18T21:40:17+01:00", "ready not read")
        path = DeployRecordStore().append_deploy(MAC_A, added)
        record = json.loads(path.read_text())
        self.assertEqual((record["board"], [each["project"] for each in record["deploys"]]),
                         ("firebeetle2-esp32s3", ["walk4", "pixel-games"]))

    def test_append_deploy_with_a_board_sets_it_and_a_new_record_has_none(self):
        added = outside_deploy("pixel-games", "box.py", "2026-11-18T21:40:17+01:00", "ready not read")
        record = json.loads(DeployRecordStore().append_deploy(MAC_A, added).read_text())
        self.assertEqual((record["mac"], "board" in record, len(record["deploys"])), (MAC_A, False, 1))
        record = json.loads(DeployRecordStore().append_deploy(MAC_A, added, "xiao-esp32-c6").read_text())
        self.assertEqual((record["board"], len(record["deploys"])), ("xiao-esp32-c6", 2))

    def test_both_readers_read_an_entry_with_nulls_as_recorded_with_its_maker(self):
        DeployRecordStore().append_deploy(MAC_A, outside_deploy("pixel-games", "box.py", "2026-11-18T21:40:17+01:00",
                                                                "ready not read"))
        last = DeployRecordStore().read_last_deploy(MAC_A)
        self.assertEqual((last.state, last.project, last.verdict, last.made_by, last.micropython_banner),
                         (outcomes.RECORDED, "pixel-games", "ready not read", "box.py", None))
        self.assertEqual(DeployRecordStore().read_deploys(MAC_A).state, outcomes.RECORDED)

    def test_a_maker_that_is_no_text_is_read_as_none(self):
        self.deploys(MAC_A, [dict(entry("walk4", "2026-11-17T08:04:00+01:00"), made_by=7)])
        self.assertIsNone(DeployRecordStore().read_last_deploy(MAC_A).made_by)


class TheGroupsTest(unittest.TestCase):
    def test_a_folder_name_and_a_registered_name_never_merge(self):
        entries = [entry("pixel-games", "2026-11-02T10:00:00+01:00"),
                   dict(entry("pixel-games", "2026-11-17T08:04:00+01:00"), made_by="box.py"),
                   dict(entry("pixel-games", "2026-11-18T21:40:17+01:00"), made_by="box.py")]
        self.assertEqual(bench_service.deploys_from(entries), [
            {"project": "pixel-games", "made_by": "box.py", "deploys": 2, "last": "2026-11-18T21:40:17+01:00"},
            {"project": "pixel-games", "made_by": None, "deploys": 1, "last": "2026-11-02T10:00:00+01:00"}])


class TheLinesTest(unittest.TestCase):
    def setUp(self):
        pin_time_zone(self)

    def test_the_look_and_the_deploy_question_say_who_made_the_deploy(self):
        last = LastDeploy(outcomes.RECORDED, "pixel-games", "ready not read", "2026-11-18T21:40:17+01:00", made_by="box.py")
        self.assertEqual(board_look.say_last_deploy(last), "spark's last deploy here: pixel-games, made by box.py and not by "
                                                           "spark, 2026-11-18T21:40:17+01:00 (its store record, not read from the board)")
        self.assertEqual(deploy_gate.say_last_deploy_in_question(last), "spark's store record names pixel-games as its last "
                                                                        "deploy here, 2026-11-18T21:40:17+01:00, made by box.py and not by spark")

    def test_spark_s_own_deploy_keeps_its_line(self):
        last = LastDeploy(outcomes.RECORDED, "walk4", "ready seen", "2026-11-17T08:04:00+01:00")
        self.assertEqual(board_look.say_last_deploy(last), "spark's last deploy here: walk4, ready seen, 2026-11-17T08:04:00+01:00 "
                                                           "(its store record, not read from the board)")

    def test_the_dict_carries_made_by_last(self):
        self.assertEqual(list(LastDeploy(outcomes.NONE_RECORDED).to_dict())[-1], "made_by")


class TheCodesTest(unittest.TestCase):
    def test_each_new_code_has_its_sentence(self):
        for code in ("name_taken", "not_registered"):
            self.assertTrue(records_codes.CODES[code].strip(), code)

    def test_the_frontends_list_the_two_operations(self):
        self.assertIs(bench_area.OPERATIONS["register-project"], RegisterProject)
        self.assertIs(bench_area.OPERATIONS["record-deploy"], RecordDeploy)


class RecordCase(ShowCase):
    """bench.py's verbs on a fake mpremote, with the moment of the record as the clock."""

    def bench(self, *argv, find_tool=found, clock=None):
        """(exit code, stdout, stderr) of bench.py with `argv`, the clock at RECORDED_AT unless given."""
        def run(command, **kwargs):
            self.ran.append(command)
            return subprocess.CompletedProcess(command, 0, self.devs, "")
        out, err = io.StringIO(), io.StringIO()
        outside = FakeOutsideWorld(run=run, find_tool=find_tool, clock=clock or FakeClock(RECORDED_AT))
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = bench.main(list(argv), outside=outside)
        return code, out.getvalue(), err.getvalue()

    def register(self, name="pixel-games", origin=ORIGIN, tool="box.py"):
        return self.envelope("register", name, "--origin", origin, "--tool", tool)

    def no_record(self):
        self.assertFalse(store.place("boards").exists())


class RegisterTest(RecordCase):
    def test_register_writes_the_name_and_the_launcher(self):
        code, said = self.register()
        self.assertEqual((code, said["tool"], said["op"], said["status"]), (0, "bench", "register-project", "ok"))
        self.assertEqual(said["data"]["registered"], {"name": "pixel-games", "origin": ORIGIN, "tool": "box.py",
                                                      "registered": RECORDED_AT.isoformat()})
        self.assertEqual((said["data"]["changed"], said["data"]["launcher"]), (True, "<store>/launcher/bench.py"))
        path = store.place("launcher")
        self.assertEqual((path.stat().st_mode & 0o777, path.parent.stat().st_mode & 0o777), (0o600, 0o700))
        self.assertEqual(self.ran, [])

    def test_the_same_registration_again_changes_nothing_and_writes_the_launcher_again(self):
        self.register()
        store.place("launcher").unlink()
        code, said = self.register()
        self.assertEqual((code, said["data"]["changed"]), (0, False))
        self.assertTrue(store.place("launcher").is_file())

    def test_a_taken_name_exits_2_with_its_code_and_says_not_registered(self):
        self.register()
        code, said = self.register(origin=OTHER_ORIGIN)
        self.assertEqual((code, said["status"], said["data"]), (2, "could-not-run", None))
        self.assertEqual([item["code"] for item in said["unchecked"]], ["name_taken"])
        self.assertIn("Not registered.", said["unchecked"][0]["sentence"])
        self.assertIn("bench.py register", said["unchecked"][0]["fix"])

    def test_a_broken_projects_list_or_registrations_file_is_a_store_problem_and_no_crash(self):
        store.write_json("projects", None, {})
        store.place("projects").write_text("{not json")
        code, said = self.register()
        self.assertEqual((code, [item["code"] for item in said["unchecked"]]), (2, ["store_problem"]))
        store.place("projects").unlink()
        store.place("registered-projects").write_text("{not json")
        code, said = self.register()
        self.assertEqual((code, [item["code"] for item in said["unchecked"]]), (2, ["store_problem"]))

    def test_the_text_says_what_was_registered_and_where_the_launcher_is(self):
        code, out, _ = self.bench("register", "pixel-games", "--origin", ORIGIN, "--tool", "box.py")
        self.assertEqual(code, 0)
        self.assertEqual(out.splitlines(), ["registered: pixel-games, made by box.py, from %s" % ORIGIN,
                                            "launcher: <store>/launcher/bench.py"])


class TheHelpTest(RecordCase):
    def help_of(self, *argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), self.assertRaises(SystemExit):
            bench.main(list(argv) + ["--help"])
        return out.getvalue()

    def test_each_verb_prints_its_own_help_and_every_help_lists_the_verbs(self):
        shown, register, record = self.help_of(), self.help_of("register"), self.help_of("record")
        self.assertIn("writes nothing", shown)
        for said, verb in ((register, "register"), (record, "record")):
            self.assertNotIn("writes nothing", said, verb)
            self.assertIn("usage: bench.py %s" % verb, said, verb)
        for said in (shown, register, record):
            self.assertIn("The verbs: bench.py {show,register,record}, show the default.", said)
        self.assertIn("--origin", register)
        self.assertNotIn("--origin", record)


class RecordTest(RecordCase):
    def test_a_recorded_deploy_names_the_project_in_the_view_and_the_look(self):
        self.register()
        code, said = self.envelope("record", "pixel-games")
        self.assertEqual((code, said["op"], said["status"]), (0, "record-deploy", "ok"))
        self.assertEqual(said["data"], {"entry": outside_deploy("pixel-games", "box.py", RECORDED_AT.isoformat(), "ready not read"),
                                        "mac": MAC_A, "device": S3.device})
        code, out, _ = self.bench("show")
        self.assertEqual(code, 0)
        self.assertIn("  deploys from  pixel-games, by box.py (1, last 2026-11-18)", out.splitlines())
        self.assertIn("  spark's last deploy here: pixel-games, made by box.py and not by spark, 2026-11-18T21:40:17+01:00 "
                      "(its store record, not read from the board)", out.splitlines())
        board = self.envelope("show")[1]["data"]["boards"][0]
        self.assertEqual((board["last_deploy"]["made_by"], board["deploys_from"][0]["made_by"]), ("box.py", "box.py"))
        self.assertEqual([argv[-1] for argv in self.ran], ["devs"] * 3)

    def test_the_text_of_a_record(self):
        self.register()
        code, out, _ = self.bench("record", "pixel-games")
        self.assertEqual((code, out.splitlines()), (0, [
            "recorded: pixel-games, made by box.py, 2026-11-18T21:40:17+01:00, on /dev/cu.usbmodem1101, MAC ends ee:ff. "
            "No port was opened."]))

    def test_each_call_adds_one_entry(self):
        self.register()
        self.bench("record", "pixel-games")
        self.bench("record", "pixel-games", clock=FakeClock(RECORDED_AT + datetime.timedelta(minutes=7, seconds=3)))
        deploys = DeployRecordStore().read_deploys(MAC_A)
        self.assertEqual([each["deployed"] for each in deploys.entries], ["2026-11-18T21:40:17+01:00", "2026-11-18T21:47:20+01:00"])

    def test_a_name_that_is_not_registered_writes_nothing(self):
        self.register()
        code, said = self.envelope("record", "pixel-game")
        self.assertEqual((code, said["data"], [item["code"] for item in said["unchecked"]]), (2, None, ["not_registered"]))
        self.assertIn("Nothing was written.", said["unchecked"][0]["sentence"])
        self.assertIn("bench.py register pixel-game", said["unchecked"][0]["fix"])
        self.assertEqual(self.ran, [])
        self.no_record()

    def test_no_board_two_boards_and_an_unlisted_port_write_nothing(self):
        self.register()
        for devs, argv, code in (("", [], "no_port"), (devs_of(S3, C6), [], "two_boards"),
                                 (devs_of(S3), ["--port", "/dev/cu.usbmodem9"], "port_not_listed")):
            self.devs = devs
            exit_code, said = self.envelope("record", "pixel-games", *argv)
            self.assertEqual((exit_code, [item["code"] for item in said["unchecked"]]), (2, [code]), code)
            self.assertIn("bench.py record pixel-games", said["unchecked"][0]["fix"], code)
            _, _, err = self.bench("record", "pixel-games", *argv)
            self.assertIn("Nothing was written.", err, code)
        self.no_record()

    def test_a_board_whose_serial_is_no_mac_writes_nothing_even_when_a_project_keeps_it(self):
        self.register()
        self.keep("/tmp/one", "aa:bb:cc:dd:12:34", "01a2b3c4")  # a kept bridge board: the record reads no kept board
        for row in (BRIDGE, NO_SERIAL, FIRMWARE_SERIAL):
            self.devs = devs_of(row)
            code, said = self.envelope("record", "pixel-games")
            self.assertEqual((code, [item["code"] for item in said["unchecked"]]), (2, ["cannot_tell_board"]), row)
            self.assertIn("Nothing was written.", said["unchecked"][0]["sentence"], row)
        self.no_record()

    def test_the_port_picks_one_of_two_boards(self):
        self.register()
        self.devs = devs_of(C6, S3)
        code, said = self.envelope("record", "pixel-games", "--port", S3.device)
        self.assertEqual((code, said["data"]["mac"], said["data"]["device"]), (0, MAC_A, S3.device))

    def test_a_record_keeps_the_board_of_the_record(self):
        self.register()
        self.deploys(MAC_A, [entry("walk4", "2026-11-17T08:04:00+01:00")], board="firebeetle2-esp32s3")
        self.bench("record", "pixel-games")
        self.assertEqual(json.loads(DeployRecordStore().find_path(MAC_A).read_text())["board"], "firebeetle2-esp32s3")

    def test_a_folder_deploy_and_a_recorded_deploy_of_one_name_stay_two_groups(self):
        self.deploys(MAC_A, [entry("pixel-games", "2026-11-02T10:00:00+01:00")])
        self.register()
        self.bench("record", "pixel-games")
        code, out, _ = self.bench("show")
        self.assertIn("  deploys from  pixel-games, by box.py (1, last 2026-11-18), pixel-games (1, last 2026-11-02)", out.splitlines())

    def test_a_broken_registrations_file_is_a_store_problem_and_no_crash(self):
        store.place("registered-projects").parent.mkdir(parents=True, exist_ok=True)
        store.place("registered-projects").write_text("[1]")
        code, said = self.envelope("record", "pixel-games")
        self.assertEqual((code, [item["code"] for item in said["unchecked"]]), (2, ["store_problem"]))
        self.no_record()

    def test_a_broken_board_record_is_left_as_it_is(self):
        self.register()
        store.place("boards").mkdir(parents=True)
        DeployRecordStore().find_path(MAC_A).write_text("[1, 2]")
        code, said = self.envelope("record", "pixel-games")
        self.assertEqual((code, [item["code"] for item in said["unchecked"]]), (2, ["store_problem"]))
        self.assertEqual(DeployRecordStore().find_path(MAC_A).read_text(), "[1, 2]")


class TheLauncherTest(StoreCase):
    def run_launcher(self, *argv, cwd="/"):
        env = golden_bench.child_env(self.home, "s3-flash-id-16mb.txt", "mpremote-devs-one.txt")
        return subprocess.run([sys.executable, str(store.place("launcher")), *argv], cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                              capture_output=True, text=True, timeout=golden_bench.RUN_TIMEOUT_S)

    def test_a_child_in_another_folder_runs_show_through_the_launcher(self):
        golden_bench.plant_known_board(self.home, tempfile.mkdtemp(), "mpremote-devs-one.txt")  # so the canned board is named
        launcher.write_launcher()
        done = self.run_launcher("show", "--json")
        said = json.loads(done.stdout)
        self.assertEqual((done.returncode, said["op"], len(said["data"]["boards"])), (0, "show-bench", 1), done.stderr)

    def test_a_launcher_whose_script_or_python_is_gone_prints_launcher_stale_and_exits_2(self):
        gone = Path(tempfile.mkdtemp()) / "gone"
        for python, script in ((sys.executable, gone / "bench.py"), (str(gone / "python3"), ROOT / "scripts" / "bench.py")):
            launcher.write_launcher(python, script)
            done = self.run_launcher("record", "pixel-games", "--json")
            said = json.loads(done.stdout)
            self.assertEqual((done.returncode, len(done.stdout.splitlines())), (2, 1), script)
            self.assertEqual((said["envelope"], said["tool"], said["op"], said["status"], said["data"]),
                             (1, "bench", None, "could-not-run", None))
            self.assertEqual([item["code"] for item in said["unchecked"]], ["launcher_stale"])
            self.assertIn("bench.py register", said["unchecked"][0]["fix"])
            self.assertEqual((said["problems"], said["next"], said["truncated"]), ([], [], None))

    def test_the_launcher_is_private_and_returns_the_exit_code(self):
        path = launcher.write_launcher()
        self.assertEqual((path, path.stat().st_mode & 0o777, path.parent.stat().st_mode & 0o777),
                         (store.place("launcher"), 0o600, 0o700))
        done = self.run_launcher("record", "pixel-games", "--json")
        self.assertEqual((done.returncode, [item["code"] for item in json.loads(done.stdout)["unchecked"]]), (2, ["not_registered"]))


class TheFixRoundTest(RecordCase):
    """The review of PR #1306: the cases that no test held."""

    def test_a_blank_or_unprintable_tool_or_origin_is_refused_before_anything_is_written(self):
        for origin, tool in ((ORIGIN, ""), (ORIGIN, "  "), (ORIGIN, "box\x1b[2Jpy"), ("", "box.py"), (" \t", "box.py"),
                             ("https://example.org/a\nb", "box.py")):
            code, said = self.register(origin=origin, tool=tool)
            self.assertEqual((code, [item["code"] for item in said["unchecked"]]), (2, ["blank_value"]), (origin, tool))
            self.assertIn("bench.py register", said["unchecked"][0]["fix"])
        self.assertEqual((store.place("registered-projects").exists(), store.place("launcher").exists()), (False, False))

    def test_a_launcher_that_cannot_be_written_says_the_name_is_registered(self):
        store.place("launcher").parent.parent.mkdir(parents=True, exist_ok=True)
        store.place("launcher").parent.write_text("a file where the launcher's folder goes")
        code, said = self.register()
        self.assertEqual((code, [item["code"] for item in said["unchecked"]]), (2, ["store_problem"]))
        self.assertEqual((said["data"]["registered"]["name"], said["data"]["changed"], said["data"]["launcher"]),
                         ("pixel-games", True, None))
        self.assertIn("bench.py register pixel-games", said["unchecked"][0]["fix"])
        self.assertEqual(RegisteredProjectStore().read("pixel-games").tool, "box.py")
        _, _, err = self.bench("register", "pixel-games", "--origin", ORIGIN, "--tool", "box.py")
        self.assertIn("pixel-games is registered, but the launcher was not written.", err)
        self.assertNotIn("Not registered.", err)

    def test_every_stop_of_register_names_the_next_command(self):
        store.write_json("projects", None, {})
        store.place("projects").write_text("{not json")
        code, said = self.register()
        self.assertIn("bench.py register pixel-games", said["unchecked"][0]["fix"])
        _, _, err = self.bench("register", "pixel-games", "--origin", ORIGIN, "--tool", "box.py")
        self.assertIn("Not registered.", err)

    def test_a_taken_name_writes_no_launcher(self):
        store.write_json("projects", None, {"pixel-games": "/tmp/somewhere"})
        self.assertEqual(self.register()[0], 2)
        self.assertFalse(store.place("launcher").exists())

    def test_a_maker_that_is_no_text_shows_as_spark_s_own_and_no_crash(self):
        self.deploys(MAC_A, [dict(entry("walk4", "2026-11-17T08:04:00+01:00"), made_by=[1]),
                             dict(entry("walk4", "2026-11-18T08:04:00+01:00"), made_by={"a": 1})])
        code, said = self.envelope("show")
        self.assertEqual((code, said["data"]["boards"][0]["deploys_from"]),
                         (0, [{"project": "walk4", "made_by": None, "deploys": 2, "last": "2026-11-18T08:04:00+01:00"}]))

    def test_a_board_record_that_is_a_folder_is_refused_and_no_crash(self):
        self.register()
        DeployRecordStore().find_path(MAC_A).mkdir(parents=True)
        code, said = self.envelope("record", "pixel-games")
        self.assertEqual((code, [item["code"] for item in said["unchecked"]]), (2, ["store_problem"]))
        self.assertIn("is not a board record", said["unchecked"][0]["sentence"])
        self.assertTrue(DeployRecordStore().find_path(MAC_A).is_dir())

    def test_spark_s_own_deploy_with_no_board_writes_none_as_on_main(self):
        self.deploys(MAC_A, [entry("walk4", "2026-11-17T08:04:00+01:00")], board="firebeetle2-esp32s3")
        facts = {"mac": MAC_A, "project": "blink", "image_sha256": "1" * 64, "deployed": "2026-11-18T09:15:42+01:00",
                 "simulation": "passed", "board": None}
        record = json.loads(DeployRecordStore().write_deploy(facts, "ready seen", "typed by a test").read_text())
        self.assertEqual((record["board"], len(record["deploys"])), (None, 2))

    def test_the_maker_lines_say_the_time_in_the_machine_s_zone(self):
        last = LastDeploy(outcomes.RECORDED, "pixel-games", "ready not read", "2026-11-18T20:40:17+00:00", made_by="box.py")
        self.assertIn("box.py and not by spark, 2026-11-18T21:40:17+01:00 (its store", board_look.say_last_deploy(last))
        self.assertIn("here, 2026-11-18T21:40:17+01:00, made by", deploy_gate.say_last_deploy_in_question(last))


class TheStoreFixRoundTest(StoreCase):
    def test_a_registration_keeps_the_other_names(self):
        RegisteredProjectStore().register("pixel-games", ORIGIN, "box.py", REGISTERED_AT)
        RegisteredProjectStore().register("rc-car", OTHER_ORIGIN, "flash.sh", REGISTERED_AT)
        self.assertEqual([RegisteredProjectStore().read(name).tool for name in ("pixel-games", "rc-car")], ["box.py", "flash.sh"])

    def test_a_registrations_file_that_cannot_be_read_or_is_a_folder_is_a_store_error(self):
        path = store.place("registered-projects")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}")
        path.chmod(0)
        self.addCleanup(path.chmod, 0o600)
        with self.assertRaises(store.StoreError) as refused:
            RegisteredProjectStore().read("pixel-games")
        self.assertEqual(refused.exception.code, "file_refused")
        path.chmod(0o600)
        path.unlink()
        path.mkdir()
        with self.assertRaises(store.StoreError):
            RegisteredProjectStore().read("pixel-games")

    def test_a_projects_list_that_cannot_be_read_is_a_store_error(self):
        store.write_json("projects", None, {})
        store.place("projects").chmod(0)
        self.addCleanup(store.place("projects").chmod, 0o600)
        with self.assertRaises(store.StoreError) as refused:
            store.projects()
        self.assertEqual(refused.exception.code, "file_refused")

    def test_register_holds_the_store_s_lock_while_it_reads_and_writes(self):
        import threading
        held, release = threading.Event(), threading.Event()

        def hold():
            with store.locked():
                held.set()
                release.wait(10)
        holder = threading.Thread(target=hold)
        holder.start()
        held.wait(10)
        writer = threading.Thread(target=RegisteredProjectStore().register, args=("pixel-games", ORIGIN, "box.py", REGISTERED_AT))
        writer.start()
        writer.join(0.5)
        written_while_held = store.place("registered-projects").exists()
        release.set()
        holder.join(10)
        writer.join(10)
        self.assertEqual((written_while_held, store.place("registered-projects").exists()), (False, True))


class TheLauncherFixRoundTest(StoreCase):
    def run_launcher(self, *argv, env=None):
        env = env or golden_bench.child_env(self.home, "s3-flash-id-16mb.txt", "mpremote-devs-made-up-mac.txt")
        return subprocess.run([sys.executable, str(store.place("launcher")), *argv], cwd="/", env=env, stdin=subprocess.DEVNULL,
                              capture_output=True, text=True, timeout=golden_bench.RUN_TIMEOUT_S)

    def test_a_caller_whose_environment_names_another_store_still_records_in_the_launcher_s(self):
        RegisteredProjectStore().register("pixel-games", ORIGIN, "box.py", REGISTERED_AT)
        launcher.write_launcher()
        other = Path(tempfile.mkdtemp())
        env = golden_bench.child_env(other, "s3-flash-id-16mb.txt", "mpremote-devs-made-up-mac.txt")
        env["XDG_DATA_HOME"] = str(other)
        done = self.run_launcher("record", "pixel-games", "--json", env=env)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(len(DeployRecordStore().read_deploys(MAC_A).entries), 1)
        self.assertEqual(list(other.iterdir()), [])

    def test_the_launcher_runs_the_python_it_was_given_and_returns_its_exit_code(self):
        wrapper = Path(tempfile.mkdtemp()) / "python"
        wrapper.write_text("#!/bin/sh\necho ran by the wrapper: \"$2\"\nexit 7\n")
        wrapper.chmod(0o700)
        launcher.write_launcher(wrapper)
        done = self.run_launcher("show", "--json")
        self.assertEqual((done.returncode, done.stdout), (7, "ran by the wrapper: show\n"))

    def test_the_default_launcher_runs_this_python(self):
        launcher.write_launcher()
        site = Path(tempfile.mkdtemp())
        (site / "sitecustomize.py").write_text("import sys\nsys.stderr.write('python: %s\\n' % sys.executable)\n")
        env = golden_bench.child_env(self.home, "s3-flash-id-16mb.txt", "mpremote-devs-made-up-mac.txt")
        env["PYTHONPATH"] = str(site) + ":" + env["PYTHONPATH"]
        done = self.run_launcher("show", "--json", env=env)
        said = [line for line in done.stderr.splitlines() if line.startswith("python: ")]
        self.assertEqual(said, ["python: %s" % sys.executable] * 2, done.stderr)

    def test_a_store_path_with_a_space_and_a_quote_runs(self):
        home = Path(tempfile.mkdtemp()) / "a store's \"place\""
        with mock.patch.dict(os.environ, {"SPARK_HOME": str(home)}):
            RegisteredProjectStore().register("pixel-games", ORIGIN, "box.py", REGISTERED_AT)
            path = launcher.write_launcher()
        env = golden_bench.child_env(Path(tempfile.mkdtemp()), "s3-flash-id-16mb.txt", "mpremote-devs-made-up-mac.txt")
        done = subprocess.run([sys.executable, str(path), "record", "pixel-games", "--json"], cwd="/", env=env,
                              stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=golden_bench.RUN_TIMEOUT_S)
        self.assertEqual((done.returncode, json.loads(done.stdout)["data"]["mac"]), (0, MAC_A), done.stderr)
        self.assertTrue((home / "boards").is_dir())


if __name__ == "__main__":
    unittest.main()
