"""
Proof of the suite's two runs (P425): the quick run on the push hook skips the tests marked `@slow`, and the full run
(`tools/check_commit.py --full`) runs every test.

The suite took 109 to 127 s on the push hook; six classes and modules cost 54 to 70 s of it. A mark needs more than about 2 s
and a checkable reason. The quick run's line must not be quotable as the suite's count: it says how many tests it skipped,
and it counts only the slow skips, never a real one (a missing tool).

    python3 -m unittest discover -s tests
"""

import ast
import contextlib
import io
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit
import suite_runs  # noqa: E402
from test_check_commit import own_env, repo_with  # noqa: E402

TESTS = Path(__file__).resolve().parent
ROOT = TESTS.parent
sys.path.insert(0, str(ROOT / "tools"))

import check_commit  # noqa: E402
import mutate  # noqa: E402

#: A tiny tree's test module: three plain tests, one slow, one real skip.
TINY_TESTS = (
    "import unittest\nfrom suite_runs import slow\n\n\n"
    "class T(unittest.TestCase):\n"
    "    def test_a(self): pass\n"
    "    def test_b(self): pass\n"
    "    @slow('a pretend build, 9 s on 2026-10-26')\n"
    "    def test_slow_one(self): pass\n"
    "    @unittest.skip('no tool here')\n"
    "    def test_real_skip(self): pass\n")


def tiny_tree(extra=None):
    """A committed tree whose suite is TINY_TESTS, with the real suite_runs.py and outcomes.py, archived to a folder."""
    files = {"scripts/outcomes.py": (ROOT / "scripts" / "outcomes.py").read_text(),
             "tests/suite_runs.py": (TESTS / "suite_runs.py").read_text(),
             "tests/test_t.py": TINY_TESTS}
    files.update(extra or {})
    scratch = Path(tempfile.mkdtemp())
    check_commit.archive(repo_with(files), "HEAD", scratch)
    return scratch


def child(tree, suite=None, verbose=False):
    """The tree's suite run as a child, with SPARK_SUITE `suite` or unset: (its stderr, its exit code)."""
    env = {name: value for name, value in own_env().items() if name != "SPARK_SUITE"}
    if suite is not None:
        env["SPARK_SUITE"] = suite
    done = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"] + (["-v"] if verbose else []),
                          cwd=str(tree), capture_output=True, text=True, env=env, timeout=120)
    return done.stderr, done.returncode


def seconds_hidden(line):
    return re.sub(r"in [\d.]+ s", "in S s", line)


class TheSlowMarkTest(unittest.TestCase):
    def test_a_marked_test_runs_in_a_plain_run(self):
        said, code = child(tiny_tree())
        self.assertEqual(code, 0, said)
        self.assertIn("Ran 4 tests", said)
        self.assertIn("OK (skipped=1)", said, "only the real skip is skipped")

    def test_a_marked_test_is_skipped_when_the_suite_is_quick_with_a_reason_that_starts_slow(self):
        said, code = child(tiny_tree(), suite="quick", verbose=True)
        self.assertEqual(code, 0, said)
        self.assertIn("Ran 4 tests", said)
        self.assertIn("test_slow_one (test_t.T) ... skipped 'slow: a pretend build, 9 s on 2026-10-26'", said)
        self.assertIn("test_real_skip (test_t.T) ... skipped 'no tool here'", said)
        self.assertIn("OK (skipped=2)", said)

    def test_any_other_value_of_the_variable_is_a_plain_run(self):
        said, code = child(tiny_tree(), suite="full")
        self.assertEqual(code, 0, said)
        self.assertIn("OK (skipped=1)", said)

    def test_a_marked_class_skips_its_set_up_class_too(self):
        tree = tiny_tree({"tests/test_c.py": (
            "import unittest\nfrom suite_runs import slow\n\n\n"
            "@slow('a pretend class, 9 s on 2026-10-26')\n"
            "class C(unittest.TestCase):\n"
            "    @classmethod\n    def setUpClass(cls): raise RuntimeError('built')\n"
            "    def test_x(self): pass\n")})
        said, code = child(tree, suite="quick")
        self.assertEqual(code, 0, said)
        self.assertIn("Ran 5 tests", said)
        self.assertIn("OK (skipped=3)", said)

    def test_a_mark_with_no_reason_is_refused(self):
        for empty in ("", "   "):
            with self.assertRaises(ValueError):
                suite_runs.slow(empty)

    def test_every_mark_in_the_suite_names_its_seconds_and_its_date(self):
        marks = []
        for path in sorted(TESTS.glob("test_*.py")):
            for node in ast.walk(ast.parse(path.read_text())):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    marks += [(path.name, node.name, ast.literal_eval(mark.args[0]))
                              for mark in node.decorator_list
                              if isinstance(mark, ast.Call) and getattr(mark.func, "id", "") == "slow"]
        self.assertEqual(sorted((file, name) for file, name, _ in marks), [
            ("test_journey_basic.py", "TheBasicJourneyTest"),
            ("test_json_contracts.py", "test_every_reason_raised_is_in_the_table"),
            ("test_mutate.py", "AMutantThatCannotLoadIsRefusedTest"),
            ("test_mutate.py", "AnEscapedMutationTest"),
            ("test_mutate.py", "NearTestsFirstTest"),
            ("test_mutate.py", "StaleBytecodeTest"),
            ("test_needs.py", "test_a_catalog_pick_whose_name_would_end_the_board_s_comment_is_built_with_it_inert"),
            ("test_tabbed_page.py", "test_the_real_tsci_exports_a_circuit"),
            ("test_xiao_record.py", "TheLibraryXiaoBuildsAButtonAndAnLedTest"),
        ])
        for file, name, reason in marks:
            self.assertRegex(reason, r"\d+(\.\d+)?( to \d+)? s on \d{4}-\d{2}-\d{2}$", "%s %s" % (file, name))


class TheQuickRunAndTheFullRunSayWhatTheyRanTest(unittest.TestCase):
    def test_the_quick_line_counts_the_slow_skip_and_not_the_real_one(self):
        line, ok, left = check_commit.measure(tiny_tree())
        self.assertTrue(ok, line)
        self.assertEqual(left, [])
        self.assertEqual(seconds_hidden(line), "quick run: Ran 3 of 4 tests in S s "
                         "(1 slow test skipped; the full run is check_commit.py --full) / OK (skipped=2)")

    def test_the_full_line_names_every_test_it_ran(self):
        line, ok, left = check_commit.measure(tiny_tree(), full=True)
        self.assertTrue(ok, line)
        self.assertEqual(seconds_hidden(line), "full run: Ran 4 tests in S s / OK (skipped=1)")

    def test_the_full_run_runs_the_slow_tests_even_when_the_gate_s_own_environment_says_quick(self):
        with mock.patch.dict(os.environ, {"SPARK_SUITE": "quick"}):
            line, ok, left = check_commit.measure(tiny_tree(), full=True)
        self.assertEqual(seconds_hidden(line), "full run: Ran 4 tests in S s / OK (skipped=1)")

    def test_two_slow_tests_are_said_in_the_plural(self):
        tree = tiny_tree({"tests/test_u.py": (
            "import unittest\nfrom suite_runs import slow\n\n\n"
            "class U(unittest.TestCase):\n"
            "    @slow('another pretend build, 3 s on 2026-10-26')\n"
            "    def test_slow_two(self): pass\n")})
        line, ok, left = check_commit.measure(tree)
        self.assertEqual(seconds_hidden(line), "quick run: Ran 3 of 5 tests in S s "
                         "(2 slow tests skipped; the full run is check_commit.py --full) / OK (skipped=3)")

    def test_a_failure_is_said_after_the_counts(self):
        tree = tiny_tree({"tests/test_f.py": "import unittest\n\n\nclass F(unittest.TestCase):\n    def test_f(self): self.fail('x')\n"})
        line, ok, left = check_commit.measure(tree)
        self.assertFalse(ok)
        self.assertTrue(line.startswith("quick run: Ran 4 of 5 tests in "), line)
        self.assertTrue(line.endswith("/ FAILED (failures=1, skipped=2)"), line)

    def test_a_failure_that_quotes_a_slow_skip_does_not_raise_the_count(self):
        # A traceback can hold a child run's -v lines. The verdict's own skipped=N says there was no skip at all.
        tree = tiny_tree({"tests/test_t.py": (
            "import unittest\n\n\nclass T(unittest.TestCase):\n"
            "    def test_a(self): pass\n"
            "    def test_quotes(self): self.fail(\"a child said ... skipped 'slow: a pretend build\")\n")})
        line, ok, left = check_commit.measure(tree)
        self.assertFalse(ok)
        self.assertEqual(seconds_hidden(line), "quick run: Ran 2 of 2 tests in S s "
                         "(0 slow tests skipped; the full run is check_commit.py --full) / FAILED (failures=1)")


def gate_said(argv, left=()):
    """`main` with everything but the measure stubbed: (what measure was asked, what the gate printed)."""
    said, asked = io.StringIO(), []

    def measured(tree, full=False):
        asked.append(full)
        return "quick run: Ran 1 of 2 tests in 1.0 s (1 slow test skipped) / OK", True, list(left)

    archived = []
    with mock.patch.object(check_commit, "archive", side_effect=lambda root, commit, into: archived.append(commit)), \
            mock.patch.object(check_commit, "measure", side_effect=measured), \
            mock.patch.object(check_commit, "size_line", return_value="size"), \
            mock.patch.dict(sys.modules, {"check_backlog": mock.Mock(main=mock.Mock(return_value=0))}), \
            contextlib.redirect_stdout(said):
        code = check_commit.main(argv)
    return code, asked, archived, said.getvalue()


class TheFullRunIsAskedForTest(unittest.TestCase):
    def test_no_flag_is_the_quick_run_of_head(self):
        code, asked, archived, said = gate_said([])
        self.assertEqual((code, asked, archived), (check_commit.EXIT_OK, [False], ["HEAD"]))

    def test_full_after_a_commit_or_before_it_is_the_full_run_of_that_commit(self):
        for argv in (["abc1234", "--full"], ["--full", "abc1234"]):
            code, asked, archived, said = gate_said(argv)
            self.assertEqual((code, asked, archived), (check_commit.EXIT_OK, [True], ["abc1234"]), argv)

    def test_full_alone_is_the_full_run_of_head(self):
        self.assertEqual(gate_said(["--full"])[1:3], ([True], ["HEAD"]))

    def test_the_quick_gate_says_the_board_check_and_the_size_line_come_on_top_and_the_full_gate_does_not(self):
        quick = gate_said([])[3]
        self.assertRegex(quick, r"\n  quick run: the seconds above are the tests alone; the board check and the size line come on top, \d+ s for the whole gate\n")
        self.assertIn(" as committed, quick run: Ran 1 of 2 tests in 1.0 s (1 slow test skipped) / OK\n", quick)
        self.assertNotIn("the seconds above", gate_said(["--full"])[3])

    def test_an_unknown_flag_is_refused_by_the_parser(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as stopped:
            check_commit.main(["--every-test"])
        self.assertEqual(stopped.exception.code, 2)


class AMutationRunNeverRunsTheQuickRunTest(unittest.TestCase):
    def test_the_environment_of_a_mutation_run_has_no_suite_variable(self):
        with mock.patch.dict(os.environ, {"SPARK_SUITE": "quick", "SPARK_KEPT": "kept"}):
            with mutate._from_source("mutate-test-") as environment:
                self.assertNotIn("SPARK_SUITE", environment)
                self.assertEqual(environment["SPARK_KEPT"], "kept", "only the one variable goes")
                self.assertEqual(environment["PYTHONDONTWRITEBYTECODE"], "1")


if __name__ == "__main__":
    unittest.main()
