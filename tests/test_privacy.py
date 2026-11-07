"""P677 (S10, W5-1): a bench run shows no path under the person's home and no account token, except in a line a person
pastes. `Privacy` masks the result, the values and the Events; the pasted places keep their real paths."""

import contextlib
import io
import json
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import golden_bench  # noqa: E402
from fakes import FakeOutsideWorld, FakeReporter  # noqa: E402
from spark.bench import bench_privacy  # noqa: E402
from spark.core import outcomes  # noqa: E402
from spark.core.events import Event, TerminalReporter  # noqa: E402
from spark.core.cli import HelpText, run_cli  # noqa: E402
from spark.core.operation import COMMON_ARGUMENTS, Operation  # noqa: E402
from spark.core.privacy import MaskingReporter, Pasted, PastedLine, Privacy  # noqa: E402
from spark.core.result import Finding, NextStep, OperationResult  # noqa: E402

HOME = "/srv/person"
PROJECT = HOME + "/gadgets/lamp"
STORE = HOME + "/.local/share/spark"
REPO = HOME + "/Development/spark"
TOKEN = "wok_5ecret"
PASTED = Pasted(("no_terminal",), ("run_in_terminal",))


def privacy(project=PROJECT, store_path=STORE, secrets=(TOKEN,)):
    return Privacy.of(project, store_path, HOME, secrets, PASTED)


def finding(sentence, code="flash_differs", fix=""):
    return Finding(outcomes.PROBLEMS, None, code, sentence, fix)


class PathRulesTest(unittest.TestCase):

    def test_a_project_path_becomes_relative_and_a_store_path_gets_the_placeholder(self):
        masked = privacy().mask_text("wrote %s/sim/flash.bin and %s/boards/a.json for %s" % (PROJECT, STORE, PROJECT))
        self.assertEqual(masked, "wrote sim/flash.bin and <store>/boards/a.json for <project>")

    def test_a_repo_path_under_home_gets_a_tilde_and_a_path_outside_home_stays(self):
        masked = privacy().mask_text("%s/scripts/deploy.py and /usr/bin/python3" % REPO)
        self.assertEqual(masked, "~/Development/spark/scripts/deploy.py and /usr/bin/python3")

    def test_a_longer_name_beside_a_path_is_not_cut(self):
        self.assertEqual(privacy().mask_text(PROJECT + "-old/x"), "~/gadgets/lamp-old/x")

    def test_the_store_under_the_project_is_the_store(self):
        inner = PROJECT + "/.store"
        self.assertEqual(privacy(store_path=inner).mask_text(inner + "/boards/a.json " + PROJECT + "/sim"),
                         "<store>/boards/a.json sim")

    def test_a_relative_project_is_the_folder_it_names(self):
        here = str(Path(".").resolve())
        self.assertEqual(Privacy.of(Path("."), STORE, HOME, ()).mask_text(here + "/sim/x.bin"), "sim/x.bin")

    def test_a_path_before_a_full_stop_is_masked_and_a_longer_name_with_a_dot_is_kept_whole(self):
        self.assertEqual(privacy().mask_text("it is in %s." % HOME), "it is in ~.")
        self.assertEqual(privacy().mask_text("%s.bak/x and %s.old" % (PROJECT, STORE)), "~/gadgets/lamp.bak/x and ~/.local/share/spark.old")

    def test_the_project_folder_with_a_trailing_slash_keeps_its_slash(self):
        self.assertEqual(privacy().mask_text("copied to %s/ now, %s/.spark" % (PROJECT, PROJECT)), "copied to <project>/ now, .spark")

    def test_an_empty_secret_masks_nothing(self):
        self.assertEqual(privacy(secrets=("",)).mask_text("/usr/bin/x"), "/usr/bin/x")

    def test_no_rules_pass_everything_through(self):
        result = OperationResult({"a": PROJECT}, [finding(PROJECT)], lines=[PROJECT])
        self.assertIs(Privacy().mask_result(result), result)


class MaskResultTest(unittest.TestCase):

    def test_a_secret_is_masked_in_every_part_of_a_result(self):
        said = "token %s in %s/x" % (TOKEN, PROJECT)
        result = OperationResult({"deep": [{"why": said}]}, [finding(said, fix=said)], lines=[said], diagnostics=[said], notes=[said])
        masked = privacy().mask_result(result)
        for text in (masked.data["deep"][0]["why"], masked.findings[0].sentence, masked.findings[0].fix, masked.lines[0],
                     masked.diagnostics[0], masked.notes[0]):
            self.assertEqual(text, "token *** in x")

    def test_mask_values_masks_the_values_of_a_trace(self):
        values = privacy().mask_values({"project": Path(PROJECT), "code": "print('%s')" % TOKEN, "json": True})
        self.assertEqual(values, {"project": "<project>", "code": "print('***')", "json": True})

    def test_a_pasted_line_keeps_its_paths(self):
        line = "SPARK_HOME=%s %s/scripts/deploy.py --project %s" % (STORE, REPO, PROJECT)
        sentence = "no terminal to ask you in. Run this line:\n  " + line
        step = NextStep("deploy", ["--project", PROJECT], "run %s/x" % PROJECT, env={"SPARK_HOME": STORE})
        result = OperationResult({"run_in_terminal": line, "look": PROJECT + "/sim"}, [finding(sentence, "no_terminal", fix="run it in your own terminal")],
                                 [step], diagnostics=["deploy.py: " + sentence, PROJECT + "/sim"])
        masked = privacy().mask_result(result)
        self.assertEqual((masked.data["run_in_terminal"], masked.findings[0], masked.next[0].argv, masked.next[0].env),
                         (line, result.findings[0], step.argv, step.env))
        self.assertEqual(masked.diagnostics, ["deploy.py: " + sentence, "sim"])
        self.assertEqual((masked.data["look"], masked.next[0].why), ("sim", "run x"))

    def test_a_part_of_a_pasted_sentence_keeps_its_paths(self):
        reason = "build it with %s/scripts/flash_image.py --project %s" % (REPO, PROJECT)
        result = OperationResult({"no_token_reason": reason}, [finding("no token: " + reason, "no_terminal")])
        self.assertEqual(privacy().mask_result(result).data, {"no_token_reason": reason})

    def test_a_pasted_line_of_lines_keeps_its_paths(self):
        line = PastedLine("  rm %s/grants/a.json" % STORE)
        result = OperationResult(None, lines=[line, STORE + "/grants/a.json"])
        self.assertEqual(privacy().mask_result(result).lines, [line, "<store>/grants/a.json"])

    def test_a_token_is_masked_in_the_raw_places_too(self):
        line = "%s/deploy.py --token %s" % (PROJECT, TOKEN)
        step = NextStep("deploy", ["--project", PROJECT, TOKEN], "why", env={"SPARK_HOME": STORE, "T": TOKEN})
        result = OperationResult({"run_in_terminal": line}, [Finding(outcomes.PROBLEMS, TOKEN, "no_terminal", "run " + line, TOKEN)],
                                 [step], lines=[PastedLine("rm %s %s" % (STORE, TOKEN))])
        masked = privacy().mask_result(result)
        raw = "%s/deploy.py --token ***" % PROJECT
        self.assertEqual((masked.data["run_in_terminal"], masked.findings[0][1:], masked.next[0].argv, masked.next[0].env, masked.lines),
                         (raw, ("***", "no_terminal", "run " + raw, "***"), ["--project", PROJECT, "***"], {"SPARK_HOME": STORE, "T": "***"},
                          ["rm %s ***" % STORE]))
        self.assertIsInstance(masked.lines[0], PastedLine)

    def test_a_line_that_holds_a_pasted_sentence_masks_the_rest(self):
        sentence = "run %s/deploy.py" % PROJECT
        result = OperationResult(None, [finding(sentence, "no_terminal")], diagnostics=["%s/sim: %s, then %s" % (PROJECT, sentence, STORE)])
        self.assertEqual(privacy().mask_result(result).diagnostics, ["sim: %s, then <store>" % sentence])

    def test_a_short_string_inside_a_pasted_sentence_is_masked(self):
        result = OperationResult({"home": HOME, "word": "ok"}, [finding("ok, run %s/x" % HOME, "no_terminal")])
        self.assertEqual(privacy().mask_result(result).data, {"home": "~", "word": "ok"})

    def test_an_empty_pasted_sentence_keeps_nothing_else_raw(self):
        result = OperationResult(None, [finding("", "no_terminal")], lines=[PROJECT + "/sim"])
        self.assertEqual(privacy().mask_result(result).lines, ["sim"])


class MaskEventTest(unittest.TestCase):

    def test_an_event_is_masked_and_a_raw_event_is_not(self):
        reporter = FakeReporter()
        masking = MaskingReporter(reporter, privacy())
        for event in (Event.line("look", "token %s" % TOKEN), Event.line("gate", "run %s/x" % REPO, raw=True), Event.begin("look")):
            masking.report(event)
        self.assertEqual(reporter.events, [Event.line("look", "token ***"), Event.line("gate", "run %s/x" % REPO, raw=True),
                                           Event.begin("look")])

    def test_a_raw_event_still_masks_a_token(self):
        self.assertEqual(privacy().mask_event(Event.line("gate", "run %s/x %s" % (REPO, TOKEN), raw=True)),
                         Event.line("gate", "run %s/x ***" % REPO, raw=True))

    def test_the_masking_reporter_keeps_the_terminal_stream_and_its_fd(self):
        stream = io.StringIO()
        masking = MaskingReporter(TerminalReporter(stream), privacy())
        self.assertEqual((masking.stream, masking.echo_fd()), (stream, 2))

    def test_an_event_needs_no_raw_field(self):
        self.assertFalse(Event("begin", "toy", None).raw)


class Pasting(Operation):
    """Operation: answers with a pasted line and a plain line, each naming the project, as deploy.py's no-terminal refusal does."""

    name = "pasting"
    arguments = (COMMON_ARGUMENTS["project"],)
    privacy_for = staticmethod(lambda project: Privacy.of(project, STORE, HOME, (), PASTED))

    def run(self, *, outside, project):
        sentence = "no terminal: run %s/deploy.py" % project
        return OperationResult(None, [Finding(outcomes.COULD_NOT_RUN, None, "no_terminal", sentence, "")],
                               diagnostics=["deploy.py: " + sentence, "looked in %s/sim" % project])


class GuardedRawLineTest(unittest.TestCase):
    """P430 holds on a raw place too: the pasted line keeps its path, and the terminal still shows an override as `?`."""

    def test_a_pasted_path_stays_raw_and_guarded_and_a_masked_one_goes(self):
        bad = "/nowhere/a\u202eb"
        err = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            run_cli(HelpText("pasting.py", "", ""), Pasting(), ["--project", bad], outside_builder=None, outside=FakeOutsideWorld())
        self.assertEqual(err.getvalue(), "deploy.py: no terminal: run /nowhere/a?b/deploy.py\nlooked in sim\n")


class BenchPrivacyTest(unittest.TestCase):

    def test_the_bench_masks_the_token_of_a_tool_with_an_account(self):
        with mock.patch.dict(os.environ, {"WOKWI_CLI_TOKEN": TOKEN}):
            masked = bench_privacy.privacy_for(Path(".")).mask_text("token " + TOKEN)
        self.assertEqual(masked, "token ***")

    def test_the_bench_ignores_a_token_too_short_to_mask_safely(self):
        with mock.patch.dict(os.environ, {"WOKWI_CLI_TOKEN": "abc1234"}):
            masked = bench_privacy.privacy_for(Path(".")).mask_text("abc1234 or 1")
        self.assertEqual(masked, "abc1234 or 1")

    def test_the_bench_keeps_the_codes_and_keys_of_a_line_a_person_acts_on(self):
        pasted = bench_privacy.privacy_for(Path(".")).pasted
        self.assertLessEqual({"no_terminal", "no_grant", "refused_no_grant", "no_image", "last_deploy_not_checked"}, set(pasted.codes))
        self.assertLessEqual({"run_in_terminal", "board_log", "commands", "repl_command"}, set(pasted.keys))


class BenchGoldenPathsTest(unittest.TestCase):
    """What the goldens of tests/golden show of a path, after `golden_bench.scrub`: `<project-dir>`, `<spark-home>`, `<repo>`
    and `<python>` are the run's own paths, printed raw; `<project>`, `sim/...` and `<store>` are what Privacy printed."""

    def golden(self, name):
        return json.loads((golden_bench.GOLDEN_DIR / name).read_text())

    def test_the_pasted_lines_keep_their_paths(self):
        ran = self.golden("deploy-could-not-run-no-terminal.json")
        self.assertTrue(ran["data"]["run_in_terminal"].startswith("SPARK_HOME=<spark-home> <repo>/scripts/deploy.py --project <project-dir> "))
        self.assertIn("<repo>/scripts/grant.py --scope deploy --minutes N --project <project-dir> ", ran["unchecked"][0]["sentence"])
        self.assertEqual((ran["next"][0]["argv"][1], ran["next"][0]["env"]), ("<project-dir>", {"SPARK_HOME": "<spark-home>"}))
        stderr = (golden_bench.GOLDEN_DIR / "deploy-could-not-run-no-terminal.json.stderr").read_text()
        self.assertIn("SPARK_HOME=<spark-home> <repo>/scripts/deploy.py --project <project-dir>", stderr)
        self.assertIn("<repo>/scripts/grant.py --minutes N", self.golden("live-problems-refused-no-grant.json")["why"])

    def test_the_other_paths_are_masked(self):
        self.assertEqual(self.golden("deploy-ok-ready-seen.json")["data"]["store_record"], "<store>/boards/dc-da-0c-xx-xx-xx.json")
        stderr = (golden_bench.GOLDEN_DIR / "deploy-ok-ready-seen.json.stderr").read_text()
        self.assertIn("  store record: <store>/boards/dc-da-0c-xx-xx-xx.json\n", stderr)

    def test_a_command_a_person_runs_keeps_its_paths(self):
        data = self.golden("deploy-ok-ready-seen.json")["data"]
        self.assertEqual(data["commands"][1][-1], "<project-dir>/sim/flash-with-firmware.bin")
        stderr = (golden_bench.GOLDEN_DIR / "deploy-ok-ready-seen.json.stderr").read_text()
        self.assertIn("write-flash 0x0 <project-dir>/sim/flash-with-firmware.bin\n", stderr)
        self.assertIn("  board log: <project-dir>/sim/runs/board/<time>.log\n", stderr)
        dry = (golden_bench.GOLDEN_DIR / "deploy-ok-dry-run.txt").read_text()
        self.assertIn("  would run: <python> -m esptool --chip esp32s3 --after watchdog-reset write-flash 0x0 <project-dir>/sim/flash-with-firmware.bin\n", dry)

    def test_a_file_a_person_or_an_agent_opens_keeps_its_path(self):
        self.assertEqual(self.golden("deploy-ok-ready-seen.json")["data"]["board_log"], "<project-dir>/sim/runs/board/<time>.log")
        fix = self.golden("look-could-not-run-last-deploy-not-checked.json")["unchecked"][0]["fix"]
        self.assertEqual(fix, "repair or remove <spark-home>/boards/dc-da-0c-xx-xx-xx.json, then run look.py again")

    def test_the_scrub_knows_the_tilde_form_of_the_repo_and_the_python(self):
        places = golden_bench.replacements_of(Path("/nowhere/p"), Path("/nowhere/s"))
        home = Path.home()
        if golden_bench.ROOT.is_relative_to(home):
            self.assertEqual(places["~/" + str(golden_bench.ROOT.relative_to(home))], "<repo>")
        self.assertEqual((places["/nowhere/s"], places["/nowhere/p"]), ("<spark-home>", "<project-dir>"))


if __name__ == "__main__":
    unittest.main()
