"""P442 (#587, W3-3): the core contract, with a toy Operation and no spark area imported: the result, the error, the codes."""

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from spark.records import deploy_record_store, tool_finder  # noqa: E402
from fakes import FakeDeployRecordStore, FakeOutsideWorld, FakeReporter, FakeToolFinder  # noqa: E402
from spark.core import codes, outcomes  # noqa: E402
from spark.core.cli import DEFAULT_RUN, HelpText, RunOptions, TextReport, run_cli, run_operation  # noqa: E402
from spark.core.renderers import FlatJsonLine, FullEnvelope, JsonEnvelope  # noqa: E402
from spark.core.errors import SparkError  # noqa: E402
from spark.core.events import BEGIN, LINE, Event, TerminalReporter  # noqa: E402
from spark.core.operation import ASKS, COMMON_ARGUMENTS, JSON_DEST, READS, RUNS, Argument, Operation  # noqa: E402
from spark.core.privacy import Privacy  # noqa: E402
from spark.core.outside import OutsideWorld, ProgramRunner, build_bare_outside_world, build_outside_world, refuse_replies  # noqa: E402
from spark.core.replies import AGENT, VALUE, GivenReplyStrategy, Question, Reply  # noqa: E402
from spark.core.result import Finding, NextStep, OperationResult, envelope_item, output_schema  # noqa: E402

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

    def test_a_next_step_prints_env_only_when_given(self):
        env = {"SPARK_HOME": "/my store"}
        envelope = OperationResult(None, [], [STEP, STEP._replace(env=env)]).to_envelope("look", "look")
        self.assertNotIn("env", envelope["next"][0])
        self.assertEqual(envelope["next"][1]["env"], env)
        self.assertEqual(list(envelope["next"][1])[-1], "env")

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

    def test_the_core_codes_are_its_own_crash_bad_argument_undeclared_effect_and_the_reply_codes(self):
        self.assertEqual(sorted(codes.CODES), ["bad_argument", "bad_reply", "crash", "input_unreadable", "needs_reply", "undeclared_effect", "unknown_reply"])


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


TOOL = tool_finder.Tool("esptool", "flasher", {}, ["esptool"])
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

    def test_a_required_argument_and_a_choice_are_argparse_s_own(self):
        class Minutes(Toy):
            arguments = (Argument(("--minutes",), "minutes", int, "how long", required=True),
                         Argument(("--scope",), "scope", str, "what for", "live", choices=("live", "deploy")), COMMON_ARGUMENTS["json"])

            def run(self, minutes, scope, *, outside):
                return OperationResult({"minutes": minutes, "scope": scope}, lines=["%s %s" % (minutes, scope)])
        import contextlib
        import io
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = run_cli(TEXT, Minutes(), ["--minutes", "5", "--scope", "deploy"], outside_builder=None, outside=FakeOutsideWorld())
        self.assertEqual((code, out.getvalue()), (0, "5 deploy\n"))
        for argv, said in ((["--scope", "live"], "the following arguments are required: --minutes"), (["--minutes", "5", "--scope", "x"], "invalid choice: 'x' (choose from")):
            err = io.StringIO()
            with self.assertRaises(SystemExit) as raised, contextlib.redirect_stderr(err):
                run_cli(TEXT, Minutes(), argv, outside_builder=None, outside=FakeOutsideWorld())
            self.assertEqual(raised.exception.code, 2)
            self.assertIn(said, err.getvalue())

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

        def builder(project, effects, reporter, values):
            asked.append((project, effects, type(reporter), values["what"], values["json"]))
            return FakeOutsideWorld(find_tool={"flasher": TOOL}.get)
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()):
            code = run_cli(TEXT, Toy(), ["--project", "here", "--what", "ok"], outside_builder=builder)
            again = run_cli(TEXT, Toy(), ["--project", "here", "--what", "ok", "--json"], outside_builder=builder)
        # P737: the parsed values reach the builder, with the json flag the Operation never sees, so a frontend keeps a terminal out of an envelope run
        self.assertEqual((code, again, asked), (0, 0, [(Path("here"), (READS,), TerminalReporter, "ok", False), (Path("here"), (READS,), TerminalReporter, "ok", True)]))

    def test_the_builder_gets_the_effects_the_operation_narrows_to_for_these_values(self):
        asked = []

        class Narrow(Toy):
            """Operation: the toy that declares RUNS and READS, and narrows to RUNS alone when `--left` is given."""

            effects = (READS, RUNS)

            def effects_of(self, values):
                return (RUNS,) if values["left"] else self.effects
        run_operation(Narrow(), toy_values("ok") | {"left": True}, None, lambda effects: asked.append(effects) or FakeOutsideWorld(find_tool={"flasher": TOOL}.get))
        self.assertEqual(asked, [(RUNS,)])


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
        def builder(project, effects, reporter, values):
            raise OSError("no tools file")
        import contextlib
        import io
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            code = run_cli(TEXT, Toy(), ["--json"], outside_builder=builder)
        self.assertEqual((code, json.loads(out.getvalue())["unchecked"][0]["code"]), (2, "crash"))
        self.assertIn("OSError", json.loads(out.getvalue())["unchecked"][0]["sentence"])

    def test_an_undeclared_run_is_refused(self):
        outside = build_outside_world((READS,), FakeReporter(), find_tool={"flasher": TOOL}.get)
        with self.assertRaises(SparkError) as refused:
            outside.run(["ls"])
        self.assertEqual((refused.exception.code, refused.exception.status), ("undeclared_effect", outcomes.COULD_NOT_RUN))
        code, out, err = cli("--what", "run", "--json", outside=outside)
        self.assertEqual((code, json.loads(out)["unchecked"][0]["code"], err), (2, "undeclared_effect", ""))
        self.assertIn("cannot run ['ls']", json.loads(out)["unchecked"][0]["sentence"])

    def test_replies_are_refused_without_asks_and_are_the_given_strategy_s_reply_with_it(self):
        # P737: the fifth field keeps its place, so the two positional builders stand; `replies` is a keyword with a refusing default
        question = Question("revision", "Which revision?", VALUE, AGENT)
        given = GivenReplyStrategy({"revision": Reply("revision", "V2.0", "a test")})
        self.assertIs(OutsideWorld(None, None, None, None, None).replies, refuse_replies)
        with self.assertRaises(SparkError) as refused:
            build_outside_world((READS,), FakeReporter(), replies=given).replies(question)
        self.assertEqual((refused.exception.code, refused.exception.status), ("undeclared_effect", outcomes.COULD_NOT_RUN))
        self.assertIn("cannot ask 'revision'", str(refused.exception))
        with self.assertRaises(SparkError):
            build_outside_world((READS, ASKS), FakeReporter()).replies(question)  # ASKS with no strategy given
        self.assertEqual(build_outside_world((READS, ASKS), FakeReporter(), replies=given).replies(question).value, "V2.0")
        with self.assertRaises(AssertionError):
            FakeOutsideWorld().replies(question)
        self.assertEqual(FakeOutsideWorld(replies=given).replies(question).value, "V2.0")
        self.assertEqual(FakeOutsideWorld(replies=given)._replace(clock=None).replies(question).value, "V2.0")

    def test_fetch_is_refused_without_fetches_and_is_the_given_callable_with_it(self):
        # P737 step 5: the seventh field has a refusing default too, so the positional builders stand; the core imports no store
        from spark.core.operation import FETCHES
        from spark.core.outside import refuse_fetch
        self.assertIs(OutsideWorld(None, None, None, None, None).fetch, refuse_fetch)
        pages = {"https://x.example/p": b"<html>"}
        with self.assertRaises(SparkError) as refused:
            build_outside_world((READS,), FakeReporter(), fetch=pages.__getitem__).fetch("https://x.example/p")
        self.assertEqual((refused.exception.code, refused.exception.status), ("undeclared_effect", outcomes.COULD_NOT_RUN))
        self.assertIn("cannot fetch 'https://x.example/p'", str(refused.exception))
        with self.assertRaises(SparkError):
            build_outside_world((READS, FETCHES), FakeReporter()).fetch("https://x.example/p")  # FETCHES with nothing given
        self.assertEqual(build_outside_world((READS, FETCHES), FakeReporter(), fetch=pages.__getitem__).fetch("https://x.example/p"), b"<html>")
        with self.assertRaises(AssertionError):
            FakeOutsideWorld().fetch("https://x.example/p")
        fake = FakeOutsideWorld(fetch=pages.__getitem__)
        self.assertEqual((fake.fetch("https://x.example/p"), fake.fetched, fake._replace().fetch), (b"<html>", ["https://x.example/p"], fake.fetch))

    def test_a_declared_run_is_a_program_runner_and_the_finder_is_the_given_one(self):
        outside = build_outside_world((READS, RUNS), FakeReporter(), find_tool={"flasher": TOOL}.get)
        self.assertEqual((outside.run.__func__, outside.run.__self__.echo_fd), (ProgramRunner.run, None))
        self.assertEqual((outside.find_tool("flasher"), outside.find_tool("x")), (TOOL, None))

    def test_a_runner_echoes_an_uncaptured_child_where_the_reporter_says_and_a_captured_one_never(self):
        import io
        import sys
        import tempfile
        echo = [sys.executable, "-c", "print('echoed')"]
        with tempfile.TemporaryFile() as held:
            captured = ProgramRunner(held.fileno()).run(echo, capture_output=True, text=True)
            ProgramRunner(held.fileno()).run(echo)
            held.seek(0)
            self.assertEqual((captured.stdout, held.read()), ("echoed\n", b"echoed\n"))
        self.assertEqual((TerminalReporter(sys.stdout).echo_fd(), TerminalReporter(io.StringIO()).echo_fd(), FakeReporter().echo_fd()), (None, 2, None))

    def test_a_runner_keeps_the_stdout_the_caller_gives(self):
        import subprocess
        import sys
        import tempfile
        with tempfile.TemporaryFile() as held:
            piped = ProgramRunner(held.fileno()).run([sys.executable, "-c", "print('piped')"], stdout=subprocess.PIPE, text=True)
            held.seek(0)
            self.assertEqual((piped.stdout, held.read()), ("piped\n", b""))

    def test_an_undeclared_consent_is_refused_and_a_declared_one_is_the_given_builder(self):
        from spark.core.operation import DELETES
        outside = build_outside_world((READS,), FakeReporter(), make_consent=lambda line: line)
        with self.assertRaises(SparkError) as refused:
            outside.make_consent("deploy.py --token t")
        self.assertEqual(refused.exception.code, "undeclared_effect")
        self.assertIn("declares no `asks` effect", str(refused.exception))
        self.assertEqual(build_outside_world((READS, ASKS), FakeReporter(), make_consent=lambda line: line).make_consent("x"), "x")
        with self.assertRaises(SparkError, msg="an erase alone is no yes to ask for"):
            build_outside_world((READS, DELETES), FakeReporter(), make_consent=lambda line: line).make_consent("x")

    def test_a_flat_operation_prints_its_data_as_one_line_and_a_bad_argument_as_the_usage(self):
        class Flat(Toy):
            json_renderer = FlatJsonLine

            def run(self, project, what, left, right, *, outside):
                return OperationResult(None if what == "crash" else {"what": what, "näme": 1}, [] if what == "ok" else [PROBLEM])
        import contextlib
        import io
        for what, code, said in (("ok", 0, '{"what": "ok", "n\\u00e4me": 1}\n'), ("problems", 1, '{"what": "problems", "n\\u00e4me": 1}\n')):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                self.assertEqual(run_cli(TEXT, Flat(), ["--what", what, "--json"], outside_builder=None, outside=FakeOutsideWorld()), code)
            self.assertEqual(out.getvalue(), said)
        err = io.StringIO()
        with self.assertRaises(SystemExit) as raised, contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()) as out:
            run_cli(TEXT, Flat(), ["--left", "--right", "--json"], outside_builder=None)
        self.assertEqual((raised.exception.code, out.getvalue()), (2, ""))
        self.assertTrue(err.getvalue().startswith("usage: toy.py "), err.getvalue())

    def test_a_crash_under_a_flat_json_prints_no_stdout_line(self):
        class Flat(Toy):
            json_renderer = FlatJsonLine
        import contextlib
        import io
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = run_cli(TEXT, Flat(), ["--what", "crash", "--json"], outside_builder=None, outside=FakeOutsideWorld())
        self.assertEqual((code, out.getvalue()), (2, ""))
        self.assertIn("Traceback (most recent call last):", err.getvalue())

    def test_an_operation_with_no_json_argument_runs_and_prints_its_lines(self):
        class NoJson(Toy):
            arguments = (COMMON_ARGUMENTS["project"],)

            def run(self, project, *, outside):
                return OperationResult({"a": 1}, lines=["a line"])
        import contextlib
        import io
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = run_cli(TEXT, NoJson(), [], outside_builder=None, outside=FakeOutsideWorld())
        self.assertEqual((code, out.getvalue()), (0, "a line\n"))

    def test_the_renderers_decide_nothing_again(self):
        result = OperationResult({"a": 1}, [PROBLEM], lines=["one", "two"])
        self.assertEqual(TextReport.render(result), "one\ntwo")
        self.assertEqual(JsonEnvelope.render(result, "t", "o"), outcomes.dumps(result.to_envelope("t", "o")))
        self.assertEqual(TextReport.render(OperationResult(None)), "")
        self.assertEqual(FlatJsonLine.render(result, "t", "o"), '{"a": 1}')
        self.assertEqual(FlatJsonLine.render(OperationResult(None, [PROBLEM]), "t", "o"), "")
        self.assertIsNone(FlatJsonLine.render_bad_argument(result, "t", "o"))
        self.assertEqual(JsonEnvelope.render_bad_argument(result, "t", "o"), JsonEnvelope.render(result, "t", "o"))


class TickingClock:
    """A clock whose `monotonic` gives 10.0 and then 12.5, and raises StopIteration on a third read (FakeClock stands still)."""

    def __init__(self):
        self.monotonic = iter([10.0, 12.5]).__next__


class MarkingPrivacy(Privacy):
    """Privacy: marks what it masked, so a test sees that the trace and the frontend get the masked result and values."""

    def mask_result(self, result):
        return result._replace(notes=["masked"])

    def mask_values(self, values):
        return dict(values, project="<project>")


def toy_values(what):
    return {"project": Path("/opt/someone/p"), "what": what, "left": False, "right": False}


class RunOptionsTest(unittest.TestCase):
    """P605: run_operation masks the result with the Privacy step, then calls the one trace hook once per run."""

    def run_traced(self, what, privacy=Privacy(), trace=None):
        calls = []
        options = RunOptions(privacy, trace or (lambda *call: calls.append(call)), TickingClock())
        outside = FakeOutsideWorld(find_tool={"flasher": TOOL}.get)
        return run_operation(Toy(), toy_values(what), outside, options=options), calls

    def test_a_recording_trace_sees_one_call_per_run(self):
        for what in ("ok", "error", "crash"):
            with self.subTest(what=what):
                result, calls = self.run_traced(what)
                self.assertEqual(calls, [("toy", toy_values(what), result, 2.5)])
        calls = []
        result = run_operation(Toy(), toy_values("ok"), None, lambda effects: 1 / 0, RunOptions(Privacy(), lambda *call: calls.append(call), TickingClock()))
        self.assertEqual((result.findings[0].code, calls), ("crash", [("toy", toy_values("ok"), result, 2.5)]), "a builder that crashes")

    def test_a_tracer_that_raises_leaves_the_result_standing(self):
        def broken(*call):
            raise ValueError("the tracer at /opt/someone is down")
        untraced = run_operation(Toy(), toy_values("problems"), FakeOutsideWorld(find_tool={"flasher": TOOL}.get))
        result, _ = self.run_traced("problems", trace=broken)
        self.assertEqual(result.to_envelope("toy", "toy"), untraced.to_envelope("toy", "toy"))
        self.assertEqual(list(result.diagnostics), list(untraced.diagnostics) + ["trace: ValueError raised, the result stands"])

    def test_privacy_runs_before_the_trace_and_the_result(self):
        result, calls = self.run_traced("ok", privacy=MarkingPrivacy())
        self.assertEqual(result.notes, ["masked"])
        self.assertEqual(calls, [("toy", dict(toy_values("ok"), project="<project>"), result, 2.5)])
        untraced = run_operation(Toy(), toy_values("ok"), FakeOutsideWorld(find_tool={"flasher": TOOL}.get),
                                 options=RunOptions(MarkingPrivacy(), None, TickingClock()))
        self.assertEqual(untraced.notes, ["masked"], "a run with no trace is masked too")

    def test_the_default_run_masks_nothing_and_traces_nothing(self):
        self.assertIsNone(DEFAULT_RUN.trace)
        result = OperationResult({"a": 1}, [PROBLEM], lines=["one"])
        self.assertIs(DEFAULT_RUN.privacy.mask_result(result), result)
        self.assertEqual(DEFAULT_RUN.privacy.mask_values({"a": 1}), {"a": 1})
        outside = FakeOutsideWorld(find_tool={"flasher": TOOL}.get)
        self.assertEqual(run_operation(Toy(), toy_values("problems"), outside), Toy().run(**toy_values("problems"), outside=outside))


class SchemaTest(unittest.TestCase):
    """P605: an Operation's input and output as JSON Schemas, for an MCP tool or a LangGraph node (P417)."""

    def test_every_argument_but_json_is_a_property_of_the_input_schema(self):
        schema = Toy().input_schema()
        dests = [argument.dest for argument in Toy.arguments if argument.dest != JSON_DEST]
        self.assertEqual(list(schema["properties"]), dests)
        self.assertEqual((schema["type"], schema["additionalProperties"]), ("object", False))
        self.assertEqual(schema["properties"]["project"], {"type": "string", "description": COMMON_ARGUMENTS["project"].help, "default": "."})
        self.assertEqual(schema["properties"]["left"], {"type": "boolean", "description": "one side", "default": False})
        self.assertEqual(schema["properties"]["what"]["default"], "ok")

    def test_an_argument_with_no_default_has_no_default_key(self):
        class Port(Toy):
            arguments = (COMMON_ARGUMENTS["port"],)
        self.assertEqual(Port().input_schema()["properties"]["port"], {"type": "string", "description": COMMON_ARGUMENTS["port"].help})

    def test_a_kind_outside_the_table_is_refused(self):
        class Counting(Toy):
            arguments = (Argument(("--times",), "times", float, "how often"),)
        with self.assertRaises(KeyError):
            Counting().input_schema()

    def test_a_required_integer_with_choices_in_the_input_schema(self):
        class Minutes(Toy):
            arguments = (Argument(("--minutes",), "minutes", int, "how long", required=True),
                         Argument(("--scope",), "scope", str, "what for", "live", choices=("live", "deploy")))
        schema = Minutes().input_schema()
        self.assertEqual(schema["required"], ["minutes"])
        self.assertEqual(schema["properties"]["minutes"], {"type": "integer", "description": "how long"})
        self.assertEqual(schema["properties"]["scope"], {"type": "string", "description": "what for", "enum": ["live", "deploy"], "default": "live"})
        self.assertNotIn("required", Toy().input_schema(), "[] is invalid in JSON Schema draft 4")

    def test_an_argument_with_several_values_is_an_array_and_shows_its_word(self):
        # P726: `parts.py --need WORD [WORD ...]`, the first Operation with a list value
        class Words(Toy):
            arguments = (Argument(("--need",), "words", str, "the words", nargs="+", metavar="WORD"), COMMON_ARGUMENTS["json"])
        self.assertEqual(Words().input_schema()["properties"]["words"], {"type": "array", "items": {"type": "string"}, "description": "the words"})
        from spark.core.cli import parser_for
        parser = parser_for(TEXT, Words())
        self.assertEqual(vars(parser.parse_args(["--need", "a", "b"]))["words"], ["a", "b"])
        self.assertIn("--need WORD [WORD ...]", parser.format_usage())

    def test_an_argument_that_repeats_keeps_every_value_and_is_an_array(self):
        # P726 PR 2: `parts.py --read --label a=x --label b=y`, argparse's append; nargs="+" would keep the last flag alone
        class Labels(Toy):
            arguments = (Argument(("--label",), "labels", str, "extra words", repeats=True), COMMON_ARGUMENTS["json"])
        self.assertEqual(Labels().input_schema()["properties"]["labels"], {"type": "array", "items": {"type": "string"}, "description": "extra words"})
        from spark.core.cli import parser_for
        parsed = vars(parser_for(TEXT, Labels()).parse_args(["--label", "a=x", "--label", "b=y"]))
        self.assertEqual(parsed["labels"], ["a=x", "b=y"])
        self.assertIsNone(vars(parser_for(TEXT, Labels()).parse_args([]))["labels"])

    def test_a_payload_token_is_read_by_the_cli_and_handed_to_the_operation_as_a_value(self):
        # P726 PR 3: reading a file or stdin is the adapter's job (rule X2); the Operation takes the parsed JSON
        import io
        import tempfile
        from pathlib import Path
        from spark.core.cli import load_payloads
        from spark.core.errors import CodedMessageError
        from spark.core import codes
        class Writes(Toy):
            arguments = (Argument(("--set",), "items", str, "a JSON list", metavar="FILE", payload=0),
                         Argument(("--fact-set",), "part_and_facts", str, "a part and a JSON object", nargs=2, metavar=("PART", "FILE"), payload=1),
                         COMMON_ARGUMENTS["json"])
        given = Path(tempfile.mkdtemp()) / "in.json"
        given.write_text('{"a": 1}')
        values = load_payloads(Writes(), {"items": str(given), "part_and_facts": ["x", "-"]}, io.StringIO("[1, 2]"))
        self.assertEqual(values, {"items": {"a": 1}, "part_and_facts": ["x", [1, 2]]})
        self.assertEqual(load_payloads(Writes(), {"items": None, "part_and_facts": None}, io.StringIO()), {"items": None, "part_and_facts": None})
        given.write_text("{")
        with self.assertRaises(CodedMessageError) as refused:
            load_payloads(Writes(), {"items": str(given), "part_and_facts": None}, io.StringIO())
        self.assertEqual(refused.exception.code, codes.INPUT_UNREADABLE)
        self.assertIn("is not readable JSON", str(refused.exception))
        schema = Writes().input_schema()["properties"]
        self.assertEqual(schema["items"]["type"], ["object", "array"])
        self.assertEqual(schema["part_and_facts"]["prefixItems"], [{"type": "string"}, {"type": ["object", "array"]}])

    def test_a_required_flag_refuses_an_empty_argv_with_the_cli_s_own_fix(self):
        # P726 PR 3: parts.py's --describe is required, so `parts.py` alone exits 2 and the fix names --describe
        import io
        import json
        import contextlib
        from spark.core.cli import HelpText, run_cli
        from spark.core.outside import build_bare_outside_world
        class Describe(Toy):
            arguments = (Argument(("--describe",), "describe", bool, "the list", required=True), COMMON_ARGUMENTS["json"])
        text = HelpText("x.py", "", "", bad_argument_fix="x.py --describe lists the operations")
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = run_cli(text, Describe(), ["--json"], outside_builder=build_bare_outside_world)
        said = json.loads(out.getvalue())
        self.assertEqual((code, said["unchecked"][0]["code"], said["unchecked"][0]["fix"]), (2, "bad_argument", "x.py --describe lists the operations"))

    def test_describe_operations_reflects_over_a_registry(self):
        # P726 PR 3: the rows come from the classes (flag, summary, effect words in a fixed order, the schema), not a table
        from spark.core.describe_operations import DescribeOperations
        from spark.core.operation import FETCHES, READS, WRITES
        class Fetch(Toy):
            name = "fetch"
            effects = (READS, WRITES, FETCHES)
            arguments = (Argument(("--fetch",), "part_id", str, "download what a record cites", metavar="PART"), COMMON_ARGUMENTS["json"])
        class Quiet(Toy):
            name = "quiet"
            summary = "says nothing"
            arguments = (Argument(("--project",), "project", str, "a project"), COMMON_ARGUMENTS["json"])
        result = DescribeOperations({"fetch": Fetch, "quiet": Quiet}).run(outside=None)
        rows = result.data["operations"]
        self.assertEqual([(r["flag"], r["summary"], r["effects"], r["dry_run"]) for r in rows],
                         [("--fetch", "download what a record cites", ["network", "writes"], True), ("--quiet", "says nothing", [], False)])
        self.assertEqual(rows[0]["arguments"]["part_id"]["metavar"], "PART")
        self.assertEqual([o["flag"] for o in result.data["options"]], ["--json", "--project"])
        self.assertEqual(result.lines[0], "  --fetch            download what a record cites  [network, writes]")
        self.assertEqual(result.data["exits"], {"0": "ok", "1": "problems", "2": "could-not-run"})

    def test_the_output_schema_requires_the_keys_of_a_real_envelope(self):
        schema = Toy().output_schema()
        self.assertEqual(schema, output_schema())
        envelope = json.loads(cli("--json")[1])
        self.assertEqual(schema["required"], list(envelope))
        self.assertEqual(schema["properties"]["status"], {"enum": [outcomes.OK, outcomes.PROBLEMS, outcomes.COULD_NOT_RUN]})
        self.assertEqual(schema["properties"]["envelope"], {"const": 1})


class FakeOutsideWorldTest(unittest.TestCase):
    def test_it_keeps_each_command_and_refuses_what_the_test_gave_it_no_answer_for(self):
        world = FakeOutsideWorld(run=lambda command, **options: (command, options))
        self.assertEqual(world.run(["ls"], check=True), (["ls"], {"check": True}))
        self.assertEqual(world.ran, [["ls"]])
        with self.assertRaises(AssertionError):
            world.find_tool("flasher")
        with self.assertRaises(AssertionError):
            FakeOutsideWorld().run(["ls"])

    def test_it_reports_to_its_own_fake_reporter_or_the_one_given(self):
        world = FakeOutsideWorld()
        world.report(Event.begin("toy"))
        self.assertEqual(world.reporter.events, [Event.begin("toy")])
        given = FakeReporter()
        self.assertIs(FakeOutsideWorld(reporter=given).reporter, given)


class FakeToolFinderTest(unittest.TestCase):
    TOOL = tool_finder.Tool("esptool", "flasher", {}, ["/opt/esptool"])

    def test_it_answers_from_its_dict_and_keeps_each_name_and_project_asked(self):
        finder = FakeToolFinder({"flasher": self.TOOL})
        self.assertIs(finder.find("flasher", "a-project"), self.TOOL)
        self.assertIs(finder.find("flasher"), self.TOOL)
        self.assertEqual(finder.asked, [("flasher", "a-project"), ("flasher", None)])

    def test_an_entry_that_is_an_exception_is_raised(self):
        with self.assertRaises(KeyError):
            FakeToolFinder({"flasher": KeyError("the test's own")}).find("flasher")

    def test_a_name_it_lacks_is_a_missing_tool_in_its_own_words_or_the_fall_back_s_answer(self):
        with self.assertRaises(tool_finder.ToolMissingError) as missing:
            FakeToolFinder({}).find("littlefs", "p")
        self.assertEqual((str(missing.exception), missing.exception.code),
                         ("littlefs is not installed — the test gave no entry for it", tool_finder.records_codes.TOOL_MISSING))
        finder = FakeToolFinder({}, fall_back=lambda name, project: (name, project))
        self.assertEqual(finder.find("littlefs", "p"), ("littlefs", "p"))


class FakeDeployRecordStoreTest(unittest.TestCase):
    def test_its_read_keeps_each_mac_asked_and_gives_the_last_deploy_given_or_none_recorded(self):
        # P458: the store the look reads comes through LookAtBoard(records=)
        records = FakeDeployRecordStore()
        self.assertEqual((records.read_last_deploy("aa:bb").state, records.asked), (outcomes.NONE_RECORDED, ["aa:bb"]))
        last = deploy_record_store.LastDeploy(outcomes.RECORDED, "p", "ready", "2026-10-17T09:00:00+02:00")
        records = FakeDeployRecordStore(path=Path("kept.json"), last=last)
        self.assertIs(records.read_last_deploy(None), last)
        self.assertEqual((records.asked, records.find_path("aa:bb")), ([None], Path("kept.json")))


class Reporting(Toy):
    """Operation: the toy that reports a BEGIN and a LINE while it runs, then answers as the toy does."""

    def run(self, project, what, left, right, *, outside):
        outside.report(Event.begin("toy"))
        outside.report(Event.line("toy", "said now"))
        return super().run(project, what, left, right, outside=outside)


class TheWorldReportsTest(unittest.TestCase):
    """P507: an event goes from the Operation through the world's `report` to the Reporter run_cli picked (rules 2 and 5)."""

    @staticmethod
    def through_a_builder(*argv):
        """(exit code, stdout, stderr) of the reporting toy, its world built by build_outside_world with run_cli's reporter."""
        import contextlib
        import io
        out, err = io.StringIO(), io.StringIO()

        def builder(project, effects, reporter, values):
            return build_outside_world(effects, reporter, find_tool={"flasher": TOOL}.get)
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = run_cli(TEXT, Reporting(), list(argv), outside_builder=builder)
        return code, out.getvalue(), err.getvalue()

    def test_a_line_is_on_stdout_before_the_report_and_a_begin_prints_nothing(self):
        self.assertEqual(self.through_a_builder(), (0, "  said now\n  what   ok\n  left   False\n", ""))

    def test_with_json_the_line_is_on_stderr_and_stdout_holds_the_envelope_alone(self):
        code, out, err = self.through_a_builder("--json")
        result = Toy().run(None, "ok", False, False, outside=FakeOutsideWorld(find_tool={"flasher": TOOL}.get))
        self.assertEqual((code, out, err), (0, JsonEnvelope.render(result, "toy", "toy") + "\n", "  said now\n"))

    def test_a_bare_world_reports_to_the_reporter_it_was_built_with(self):
        reporter = FakeReporter()
        build_outside_world((READS,), reporter).report(Event.begin("toy"))
        self.assertEqual(reporter.events, [Event.begin("toy")])


class EventTest(unittest.TestCase):
    """P507: an Event is a Value of three facts, and a LINE alone holds a sentence."""

    def test_each_kind_holds_its_fields(self):
        said, begun = Event.line("toy", "said"), Event.begin("toy")
        self.assertEqual((said.kind, said.code, said.text), (LINE, "toy", "said"))
        self.assertEqual((begun.kind, begun.code, begun.text), (BEGIN, "toy", None))
        self.assertEqual((LINE, BEGIN), ("line", "begin"))

    def test_a_line_without_a_string_is_refused(self):
        with self.assertRaises(TypeError):
            Event.line("toy", None)


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

    def test_each_line_of_a_text_with_a_newline_keeps_its_indent(self):
        import io
        stream = io.StringIO()
        TerminalReporter(stream).report(Event.line("toy", "one\ntwo"))
        self.assertEqual(stream.getvalue(), "  one\n  two\n")

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


class DumpsTest(unittest.TestCase):
    """P726 (P445): the one JSON writer of every envelope writes a lone surrogate as an escape, so `print` never fails."""

    def test_a_lone_surrogate_is_written_as_a_json_escape(self):
        line = outcomes.dumps({"data": {"name": "x\ud800y"}})
        line.encode("utf-8")  # a raw surrogate cannot be encoded, so this is what `print` does
        self.assertIn("\\ud800", line)
        self.assertEqual(json.loads(line), {"data": {"name": "x\ud800y"}})


class AMultiOperationCliTest(unittest.TestCase):
    """P707: what a CLI with several Operations (parts.py) needs of the core: its own `tool` in the envelope, the `truncated`
    and `assumptions` keys, a Renderer that keeps every key on a refusal, and a builder with `run_cli`'s signature."""

    class Full(Toy):
        json_renderer = FullEnvelope

    def run_cli(self, text, operation, *argv):
        import contextlib
        import io
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            code = run_cli(text, operation, list(argv), outside_builder=None, outside=FakeOutsideWorld(find_tool={"flasher": TOOL}.get))
        return code, json.loads(out.getvalue())

    def test_the_tool_is_the_help_text_s_when_given_and_the_operation_s_name_without(self):
        _, said = self.run_cli(TEXT, Toy(), "--what", "ok", "--json")
        self.assertEqual((said["tool"], said["op"]), ("toy", "toy"))
        _, said = self.run_cli(TEXT._replace(tool="toys"), Toy(), "--what", "ok", "--json")
        self.assertEqual((said["tool"], said["op"]), ("toys", "toy"))
        _, said = self.run_cli(TEXT._replace(tool="toys"), Toy(), "--left", "--right", "--json")
        self.assertEqual((said["tool"], said["unchecked"][0]["code"]), ("toys", "bad_argument"))

    def test_truncated_and_assumptions_reach_the_envelope_and_assumptions_is_a_key_only_when_given(self):
        cut = {"shown": 1, "total": 2, "next": outcomes.step("toy", ["--from", "1"], "the rest")}
        said = OperationResult({"a": 1}, truncated=cut, assumptions=[{"fact": "x"}]).to_envelope("toys", "toy")
        self.assertEqual((said["truncated"], said["assumptions"]), (cut, [{"fact": "x"}]))
        said = OperationResult({"a": 1}).to_envelope("toys", "toy")
        self.assertEqual((said["truncated"], "assumptions" in said, "notes" in said), (None, False, False))

    def test_the_full_envelope_has_every_key_on_an_answer_a_refusal_a_crash_and_a_bad_argument(self):
        keys = ["assumptions", "data", "envelope", "next", "notes", "op", "problems", "status", "tool", "truncated", "unchecked"]
        for argv in (("--what", "ok"), ("--what", "error"), ("--what", "crash"), ("--left", "--right")):
            with self.subTest(argv=argv):
                _, said = self.run_cli(TEXT, self.Full(), *argv, "--json")
                self.assertEqual(sorted(said), keys)
                self.assertEqual((said["notes"], said["assumptions"]), ([], []))
        _, said = self.run_cli(TEXT, Toy(), "--what", "error", "--json")
        self.assertNotIn("notes", said, "JsonEnvelope keeps today's keys")

    def test_the_bare_builder_takes_run_cli_s_four_arguments_and_refuses_a_program(self):
        outside = build_bare_outside_world(Path("."), (READS,), FakeReporter(), {"json": False})
        with self.assertRaises(SparkError) as refused:
            outside.run(["true"])
        self.assertEqual(refused.exception.code, "undeclared_effect")
        self.assertEqual(build_bare_outside_world(None, (RUNS,), FakeReporter()).run.__name__, "run")


if __name__ == "__main__":
    unittest.main()
