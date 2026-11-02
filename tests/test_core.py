"""P442 (#587, W3-3): the core contract, with a toy Operation and no spark area imported: the result, the error, the codes."""

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import tools  # noqa: E402
from fakes import FakeOutsideWorld, FakeReporter  # noqa: E402
from spark.core import codes, outcomes  # noqa: E402
from spark.core.cli import HelpText, JsonEnvelope, TextReport, run_cli, run_operation  # noqa: E402
from spark.core.errors import SparkError  # noqa: E402
from spark.core.events import BEGIN, LINE, Event, TerminalReporter  # noqa: E402
from spark.core.operation import COMMON_ARGUMENTS, READS, RUNS, Argument, Operation  # noqa: E402
from spark.core.outside import ProgramRunner, build_outside_world  # noqa: E402
from spark.core.result import Finding, NextStep, OperationResult, envelope_item  # noqa: E402

PROBLEM = Finding(outcomes.PROBLEMS, "flash", "flash_differs", "the flash differs", "accept it")
UNCHECKED = Finding(outcomes.COULD_NOT_RUN, None, "field_unknown", "flash unknown", "unknown is not a pass")
STEP = NextStep("deploy", ["--project", "p", "--token", "t"], "erases the flash", ["deletes", "writes"], True)


class OperationResultTest(unittest.TestCase):
    def test_ok(self):
        result = OperationResult({"port": "/dev/x"}, lines=["  port /dev/x"])
        envelope = result.to_envelope("look", "look")
        self.assertEqual((result.status(), envelope["status"], envelope["data"], envelope["problems"], envelope["unchecked"]),
                         (outcomes.OK, outcomes.OK, {"port": "/dev/x"}, [], []))
        self.assertEqual((envelope["tool"], envelope["op"], envelope["next"]), ("look", "look", []))
        self.assertNotIn("notes", envelope)

    def test_problems(self):
        result = OperationResult(None, [PROBLEM])
        envelope = result.to_envelope("look", "look")
        self.assertEqual((result.status(), envelope["status"]), (outcomes.PROBLEMS, outcomes.PROBLEMS))
        self.assertEqual(envelope["problems"], [{"subject": "flash", "code": "flash_differs", "sentence": "the flash differs", "fix": "accept it"}])
        self.assertEqual(list(envelope["problems"][0]), ["subject", "code", "sentence", "fix"])  # the goldens compare bytes

    def test_could_not_run(self):
        result = OperationResult(None, [UNCHECKED])
        envelope = result.to_envelope("look", "look")
        self.assertEqual((result.status(), envelope["status"]), (outcomes.COULD_NOT_RUN, outcomes.COULD_NOT_RUN))
        self.assertEqual(envelope["unchecked"], [{"code": "field_unknown", "sentence": "flash unknown", "fix": "unknown is not a pass"}])
        self.assertEqual(list(envelope["unchecked"][0]), ["code", "sentence", "fix"])

    def test_an_unchecked_item_has_a_subject_only_when_one_is_set(self):
        # P464: a missing fact says what it lacks; the unchecked Findings of today pass None, so the goldens keep their bytes
        named = UNCHECKED._replace(subject="pin_roles.onboard_led.active_level")
        self.assertEqual(list(envelope_item(named)), ["subject", "code", "sentence", "fix"])
        self.assertEqual(list(envelope_item(UNCHECKED)), ["code", "sentence", "fix"])
        self.assertEqual(OperationResult(None, [named]).to_envelope("look", "look")["unchecked"], [envelope_item(named)])
        self.assertEqual(envelope_item(PROBLEM._replace(subject=None))["subject"], None)

    def test_an_unchecked_finding_never_gives_ok(self):
        self.assertEqual(OperationResult(None, [PROBLEM, UNCHECKED]).status(), outcomes.PROBLEMS)
        self.assertEqual(OperationResult({"a": 1}, [UNCHECKED], [STEP], ["a line"]).status(), outcomes.COULD_NOT_RUN)
        for severity in (outcomes.PROBLEMS, outcomes.COULD_NOT_RUN):
            self.assertNotEqual(OperationResult(None, [PROBLEM._replace(severity=severity)]).status(), outcomes.OK)

    def test_a_next_step_prints_as_outcomes_step_does_with_needs_person_only_when_given(self):
        envelope = OperationResult(None, [], [STEP, STEP._replace(needs_person=True)]).to_envelope("look", "look")
        self.assertEqual(envelope["next"][0], outcomes.step("deploy", ["--project", "p", "--token", "t"], "erases the flash", ["deletes", "writes"], True))
        self.assertNotIn("needs_person", envelope["next"][0])
        self.assertTrue(envelope["next"][1]["needs_person"])

    def test_notes_are_a_key_only_when_given(self):
        self.assertEqual(OperationResult(None, notes=["said"]).to_envelope("deploy", "deploy")["notes"], ["said"])
        self.assertNotIn("notes", OperationResult(None).to_envelope("deploy", "deploy"))


class SparkErrorTest(unittest.TestCase):
    def test_it_carries_its_code_its_fix_and_a_status_that_is_could_not_run_unless_given(self):
        error = SparkError("no %s here", "tool", code="tool_missing", fix="install it")
        self.assertEqual((str(error), error.code, error.fix, error.status), ("no tool here", "tool_missing", "install it", outcomes.COULD_NOT_RUN))
        self.assertEqual(SparkError("x", code="c", fix="f", status=outcomes.PROBLEMS).status, outcomes.PROBLEMS)

    def test_a_value_in_its_sentence_stays_on_one_line(self):
        self.assertEqual(str(SparkError("%s is missing", "a\nb", code="c", fix="f")), "a?b is missing")


class CodesTest(unittest.TestCase):
    def test_the_table_holds_each_constant_of_the_module_once_with_a_sentence(self):
        constants = {name: value for name, value in vars(codes).items() if name.isupper() and isinstance(value, str)}
        self.assertEqual(sorted(constants.values()), sorted(codes.CODES))
        sentences = list(codes.CODES.values())
        self.assertTrue(all(sentence.strip() for sentence in sentences))
        self.assertEqual(len(set(sentences)), len(sentences))

    def test_the_core_codes_are_its_own_crash_bad_argument_and_undeclared_effect(self):
        self.assertEqual(sorted(codes.CODES), ["bad_argument", "crash", "undeclared_effect"])


class Toy(Operation):
    """Operation: the toy of these tests. `--what` picks the path: ok, problems, unchecked, error, run (a program), crash."""

    name = "toy"
    arguments = (COMMON_ARGUMENTS["project"], Argument(("--what",), "what", str, "the path", "ok"),
                 Argument(("--left",), "left", bool, "one side", group="side"), Argument(("--right",), "right", bool, "the other", group="side"),
                 COMMON_ARGUMENTS["json"])
    effects = (READS,)

    def run(self, project, what, left, right, *, outside):
        if what == "error":
            raise SparkError("no %s in %s", "tool", project, code="tool_missing", fix="install it")
        if what == "crash":
            raise RuntimeError("boom at /opt/someone/project")
        if what == "run":
            outside.run(["ls"])
        findings = {"ok": [], "problems": [PROBLEM], "unchecked": [UNCHECKED]}[what]
        return OperationResult({"what": what, "tool": outside.find_tool("flasher").name}, findings, [STEP] if what == "ok" else [],
                               ["  what   %s" % what, "  left   %s" % left], ["an aside"] if what == "problems" else [])


TOOL = tools.Tool("esptool", "flasher", {}, ["esptool"])
TEXT = HelpText("toy.py", "The toy.", "Exit codes: 0, 1, 2.")


def cli(*argv, outside=None):
    """(exit code, stdout, stderr) of the toy run as a CLI with a FakeOutsideWorld, so no builder runs."""
    import contextlib
    import io
    out, err = io.StringIO(), io.StringIO()
    outside = outside or FakeOutsideWorld(find_tool={"flasher": TOOL}.get)
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = run_cli(TEXT, Toy(), list(argv), outside_builder=None, outside=outside)
    return code, out.getvalue(), err.getvalue()


class RunCliTest(unittest.TestCase):
    def test_ok_prints_the_lines_without_json_and_the_envelope_with_it_and_exits_0(self):
        self.assertEqual(cli("--what", "ok", "--left"), (0, "  what   ok\n  left   True\n", ""))
        code, out, err = cli("--what", "ok", "--json")
        envelope = json.loads(out)
        self.assertEqual((code, err, envelope["status"], envelope["data"], envelope["next"][0]["op"]), (0, "", "ok", {"what": "ok", "tool": "esptool"}, "deploy"))
        self.assertEqual(sorted(envelope), sorted(["envelope", "tool", "op", "status", "data", "problems", "unchecked", "next", "truncated"]))

    def test_problems_exits_1_and_the_diagnostics_go_to_stderr_in_both_modes(self):
        self.assertEqual(cli("--what", "problems"), (1, "  what   problems\n  left   False\n", "an aside\n"))
        code, out, err = cli("--what", "problems", "--json")
        self.assertEqual((code, json.loads(out)["problems"][0]["code"], err), (1, "flash_differs", "an aside\n"))

    def test_could_not_run_exits_2(self):
        code, out, _ = cli("--what", "unchecked", "--json")
        self.assertEqual((code, json.loads(out)["status"], json.loads(out)["unchecked"][0]["code"]), (2, "could-not-run", "field_unknown"))

    def test_a_bad_flag_is_an_envelope_with_json_and_the_usage_without(self):
        code, out, err = cli("--left", "--right", "--json")
        envelope = json.loads(out)
        self.assertEqual((code, err, envelope["status"], envelope["data"], envelope["problems"]), (2, "", "could-not-run", None, []))
        self.assertEqual([(item["code"], item["fix"]) for item in envelope["unchecked"]], [("bad_argument", "toy.py --help lists the arguments")])
        self.assertIn("not allowed with argument", envelope["unchecked"][0]["sentence"])
        import contextlib
        import io
        err = io.StringIO()
        with self.assertRaises(SystemExit) as raised, contextlib.redirect_stderr(err):
            run_cli(TEXT, Toy(), ["--left", "--right"], outside_builder=None)
        self.assertEqual(raised.exception.code, 2)
        self.assertTrue(err.getvalue().startswith("usage: toy.py "), err.getvalue())

    def test_the_usage_and_the_diagnostics_are_guarded(self):
        import contextlib
        import io
        err = io.StringIO()
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(err):
            run_cli(TEXT, Toy(), ["--bad\x1b[2J"], outside_builder=None)
        self.assertIn("toy.py: error: unrecognized arguments: --bad?[2J\n", err.getvalue())

        class Aside(Toy):
            """Operation: the toy with a control character in its diagnostics."""

            def run(self, project, what, left, right, *, outside):
                return OperationResult(None, diagnostics=["a\x1bb\u202ec"])
        err = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            run_cli(TEXT, Aside(), [], outside_builder=None, outside=FakeOutsideWorld())
        self.assertEqual(err.getvalue(), "a?b?c\n")

    def test_the_builder_gets_the_project_and_the_effects_when_no_outside_is_given(self):
        asked = []

        def builder(project, effects):
            asked.append((project, effects))
            return FakeOutsideWorld(find_tool={"flasher": TOOL}.get)
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()):
            code = run_cli(TEXT, Toy(), ["--project", "here", "--what", "ok"], outside_builder=builder)
        self.assertEqual((code, asked), (0, [(Path("here"), (READS,))]))


class RunOperationTest(unittest.TestCase):
    def test_a_spark_error_is_one_finding_with_its_status(self):
        result = run_operation(Toy(), {"project": Path("p"), "what": "error", "left": False, "right": False}, FakeOutsideWorld())
        self.assertEqual(result.findings, [Finding(outcomes.COULD_NOT_RUN, None, "tool_missing", "no tool in p", "install it")])
        self.assertEqual((result.status(), result.data, result.diagnostics), (outcomes.COULD_NOT_RUN, None, ()))

    def test_a_crash_is_the_whole_envelope_in_key_order_exit_2_and_the_traceback_in_diagnostics(self):
        code, out, err = cli("--what", "crash", "--json")
        self.assertEqual(code, 2)
        expected = {"envelope": 1, "tool": "toy", "op": "toy", "status": "could-not-run", "data": None, "problems": [],
                    "unchecked": [{"code": "crash", "sentence": "RuntimeError: the traceback is on stderr",
                                   "fix": "report this to the spark maintainers with the stderr traceback"}], "next": [], "truncated": None}
        self.assertEqual(json.loads(out), expected)
        self.assertEqual(out, json.dumps(expected, separators=(",", ":")) + "\n")  # the key order, as the goldens compare it
        self.assertTrue(err.startswith("toy: crashed, RuntimeError\nreport this to the spark maintainers with the stderr traceback\n"
                                       "Traceback (most recent call last):\n"), err)
        self.assertIn("RuntimeError: boom at /opt/someone/project", err)
        self.assertNotIn("/opt/someone", out)

    def test_a_message_with_a_newline_cannot_fake_a_line_on_stderr_and_a_class_with_one_stays_one_line(self):
        class Faking(Toy):
            """Operation: the toy that crashes with a message holding a fake report line."""

            def run(self, project, what, left, right, *, outside):
                raise RuntimeError("boom\ntoy: ok, token abcd")
        import contextlib
        import io
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            run_cli(TEXT, Faking(), ["--json"], outside_builder=None, outside=FakeOutsideWorld())
        self.assertEqual([line for line in err.getvalue().splitlines() if line.startswith("toy: ok")], [])
        self.assertIn("RuntimeError: boom?toy: ok, token abcd", err.getvalue())
        Odd = type("Bad\nName", (RuntimeError,), {})

        class OddlyNamed(Toy):
            """Operation: the toy that crashes with a class whose name holds a newline."""

            def run(self, project, what, left, right, *, outside):
                raise Odd("x")
        result = run_operation(OddlyNamed(), {"project": None, "what": "ok", "left": False, "right": False}, FakeOutsideWorld())
        self.assertEqual(result.findings[0].sentence, "Bad?Name: the traceback is on stderr")
        self.assertEqual(result.diagnostics[0], "toy: crashed, Bad?Name")
        self.assertFalse([line for line in result.diagnostics if "\n" in line])

    def test_a_chained_cause_and_a_context_stay_on_stderr(self):
        class Chained(Toy):
            """Operation: the toy that crashes with a cause, and with a context."""

            def run(self, project, what, left, right, *, outside):
                if what == "cause":
                    raise RuntimeError("outer") from KeyError("root cause")
                try:
                    1 / 0
                finally:
                    raise RuntimeError("while handling")
        import contextlib
        import io
        for what, said in (("cause", ["KeyError: 'root cause'", "The above exception was the direct cause of the following exception:"]),
                           ("context", ["ZeroDivisionError: division by zero", "During handling of the above exception, another exception occurred:"])):
            with self.subTest(what=what):
                err = io.StringIO()
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                    run_cli(TEXT, Chained(), ["--what", what], outside_builder=None, outside=FakeOutsideWorld())
                lines = err.getvalue().splitlines()
                for line in said:
                    self.assertIn(line, lines)
                self.assertEqual(lines.count("Traceback (most recent call last):"), 2 if what == "context" else 1)  # a cause raised by `from` has no frames

    def test_a_builder_that_crashes_is_a_crash_envelope_too(self):
        def builder(project, effects):
            raise OSError("no tools file")
        import contextlib
        import io
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            code = run_cli(TEXT, Toy(), ["--json"], outside_builder=builder)
        self.assertEqual((code, json.loads(out.getvalue())["unchecked"][0]["code"]), (2, "crash"))
        self.assertIn("OSError", json.loads(out.getvalue())["unchecked"][0]["sentence"])

    def test_an_undeclared_run_is_refused(self):
        outside = build_outside_world((READS,), find_tool={"flasher": TOOL}.get)
        with self.assertRaises(SparkError) as refused:
            outside.run(["ls"])
        self.assertEqual((refused.exception.code, refused.exception.status), ("undeclared_effect", outcomes.COULD_NOT_RUN))
        code, out, err = cli("--what", "run", "--json", outside=outside)
        self.assertEqual((code, json.loads(out)["unchecked"][0]["code"], err), (2, "undeclared_effect", ""))
        self.assertIn("cannot run ['ls']", json.loads(out)["unchecked"][0]["sentence"])

    def test_a_declared_run_is_subprocess_run_and_the_finder_is_the_given_one(self):
        import subprocess
        outside = build_outside_world((READS, RUNS), find_tool={"flasher": TOOL}.get)
        self.assertIs(outside.run, subprocess.run)
        self.assertIs(ProgramRunner.run, subprocess.run)
        self.assertEqual((outside.find_tool("flasher"), outside.find_tool("x")), (TOOL, None))

    def test_the_renderers_decide_nothing_again(self):
        result = OperationResult({"a": 1}, [PROBLEM], lines=["one", "two"])
        self.assertEqual(TextReport.render(result), "one\ntwo")
        self.assertEqual(JsonEnvelope.render(result, "t", "o"), outcomes.dumps(result.to_envelope("t", "o")))
        self.assertEqual(TextReport.render(OperationResult(None)), "")


class FakeOutsideWorldTest(unittest.TestCase):
    def test_it_keeps_each_command_and_refuses_what_the_test_gave_it_no_answer_for(self):
        world = FakeOutsideWorld(run=lambda command, **options: (command, options))
        self.assertEqual(world.run(["ls"], check=True), (["ls"], {"check": True}))
        self.assertEqual(world.ran, [["ls"]])
        with self.assertRaises(AssertionError):
            world.find_tool("flasher")
        with self.assertRaises(AssertionError):
            FakeOutsideWorld().run(["ls"])


class EventTest(unittest.TestCase):
    """P507: an Event is a Value of three facts, and a LINE alone holds a sentence."""

    def test_each_kind_holds_its_fields(self):
        said, begun = Event.line("toy", "said"), Event.begin("toy")
        self.assertEqual((said.kind, said.code, said.text), (LINE, "toy", "said"))
        self.assertEqual((begun.kind, begun.code, begun.text), (BEGIN, "toy", None))
        self.assertEqual((LINE, BEGIN), ("line", "begin"))


class ReporterContract:
    """P507: what every Reporter owes: it takes a LINE, a BEGIN and a kind it does not know, and raises on none."""

    def reporter(self):
        raise NotImplementedError

    def test_it_takes_each_kind_and_an_unknown_one(self):
        reporter = self.reporter()
        for event in (Event.line("toy", "said"), Event.begin("toy"), Event("other", "toy", None)):
            self.assertIsNone(reporter.report(event))


class TerminalReporterTest(ReporterContract, unittest.TestCase):
    def reporter(self):
        import io
        return TerminalReporter(io.StringIO())

    def test_a_line_is_printed_with_its_indent_and_a_begin_prints_nothing(self):
        import io
        stream = io.StringIO()
        reporter = TerminalReporter(stream)
        reporter.report(Event.begin("toy"))
        self.assertEqual(stream.getvalue(), "")
        reporter.report(Event.line("toy", "said \x1b[2J now"))
        self.assertEqual(stream.getvalue(), "  said ?[2J now\n")

    def test_for_json_picks_stderr_and_stdout_without(self):
        import contextlib
        import io
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            self.assertEqual((TerminalReporter.for_json(True).stream, TerminalReporter.for_json(False).stream), (err, out))


class FakeReporterTest(ReporterContract, unittest.TestCase):
    def reporter(self):
        return FakeReporter()

    def test_it_keeps_each_event(self):
        reporter = FakeReporter()
        reporter.report(Event.begin("toy"))
        self.assertEqual(reporter.events, [Event("begin", "toy", None)])


if __name__ == "__main__":
    unittest.main()
