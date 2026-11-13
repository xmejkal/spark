"""
Proof that the mutation tool cannot report "all caught" for a defect no test notices.

The tool exists because the discipline it enforces lived in memory and two mutations escaped a
green suite in one sprint. So the thing to test is the tool's own honesty: that an escape is
reported as one, that a `find` matching nowhere is refused rather than scored, that the files come
back, and that it refuses to score anything if the suite was red to begin with.

Every test here builds a tiny throwaway project — one module, one test — so the assertions are
about the tool and not about this repository's real suite.

    python3 -m unittest discover -s tests
"""

import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
import unittest.mock
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit
from suite_runs import slow, planted_folder  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import ledger  # noqa: E402
import mutate  # noqa: E402
import scratch  # noqa: E402


def tiny_project(*, tested=True, green=True):
    """
    A module `m.py` with `add` and `sub`, and a test that covers `add` — and `sub` only if asked.

    `tested=False` leaves `sub` uncovered, which is the escape case. `green=False` makes the test
    fail before any mutation, which is the case the tool must refuse.
    """
    root = Path(tempfile.mkdtemp())
    (root / "m.py").write_text("def add(a, b):\n    return a + b\n\ndef sub(a, b):\n    return a - b\n")
    tests = root / "tests"
    tests.mkdir()
    body = ["import sys, unittest", "sys.path.insert(0, %r)" % str(root), "import m",
            "class T(unittest.TestCase):",
            "    def test_add(self): self.assertEqual(m.add(2, 3), %d)" % (5 if green else 6)]
    if tested:
        body.append("    def test_sub(self): self.assertEqual(m.sub(5, 3), 2)")
    (tests / "test_m.py").write_text("\n".join(body) + "\n")
    return root


def table(root, *mutations):
    path = root / "mutations.json"
    path.write_text(json.dumps(list(mutations)))
    return path


BREAK_ADD = {"file": "m.py", "name": "add subtracts", "find": "return a + b", "replace": "return a - b"}
BREAK_SUB = {"file": "m.py", "name": "sub adds", "find": "return a - b", "replace": "return a + b"}


class ACaughtMutationTest(unittest.TestCase):
    def test_a_defect_a_test_notices_is_reported_caught(self):
        root = tiny_project()
        results, restored = mutate.run(root, "tests", [BREAK_ADD])
        self.assertEqual(results[0]["status"], mutate.CAUGHT)
        self.assertTrue(restored)

    def test_the_file_is_put_back(self):
        root = tiny_project()
        before = (root / "m.py").read_text()
        mutate.run(root, "tests", [BREAK_ADD])
        self.assertEqual((root / "m.py").read_text(), before)


@slow("back-to-back mutation runs of a tiny tree, 4 tests, 3.3 s on 2026-10-26")
class StaleBytecodeTest(unittest.TestCase):
    """
    A same-size edit, mutated and restored within one second, is invisible to `.pyc` validation.

    Python checks a cached `.pyc` against the source's mtime in whole seconds and its size.
    `a + b` -> `a - b` changes neither within a second, so the first full run of this suite saw
    the tool report the mutation caught and then the RESTORED suite red — it had run the mutated
    bytecode. The single-test run passed, because a cold start does not share a second.
    """

    def test_a_same_length_mutation_restored_within_a_second_leaves_the_suite_green(self):
        root = tiny_project()
        # Prime the cache the way a real run would: one green pass writes bytecode for the
        # original source. Then mutate and restore immediately.
        self.assertTrue(mutate.suite_is_green(root, "tests"))
        results, restored = mutate.run(root, "tests", [BREAK_ADD])
        self.assertEqual(results[0]["status"], mutate.CAUGHT)
        self.assertTrue(restored, "the restored suite ran stale bytecode")

    def test_each_run_s_empty_cache_goes_with_the_run(self):
        # P172: a fresh cache prefix per run, never removed — 87 mutate-pycache-* folders from one run of this suite.
        import os
        from unittest import mock
        root, fresh = tiny_project(), tempfile.mkdtemp()
        with mock.patch.object(tempfile, "tempdir", fresh):
            self.assertTrue(mutate.suite_is_green(root, "tests"))
        self.assertEqual(os.listdir(fresh), [])

    def test_each_run_s_temp_files_go_with_the_run(self):
        # P172: the suite under mutation wrote into mutate's own temp folder — a sweep left its tests' folders behind.
        import os
        from unittest import mock
        root, fresh = tiny_project(), tempfile.mkdtemp()
        (root / "tests" / "test_leak.py").write_text(
            "import tempfile, unittest\nclass L(unittest.TestCase):\n    def test_leaves_a_folder(self):\n"
            "        with open(%r, 'a') as where: where.write(tempfile.gettempdir() + '\\n')\n"
            "        tempfile.mkdtemp(prefix='left-')\n" % str(root / "where.txt"))
        # TEMP too: a TMPDIR that does not exist falls back to it, so a run without its folder lands here, not in /tmp.
        with mock.patch.object(tempfile, "tempdir", fresh), mock.patch.dict(os.environ, {"TMPDIR": fresh, "TEMP": fresh}):
            self.assertTrue(mutate.suite_is_green(root, "tests"), "the whole suite, from the root")
            self.assertTrue(mutate.suite_is_green(root, "tests", only=("test_leak",)), "named modules, from tests/")
        self.assertEqual(os.listdir(fresh), [])
        where = [Path(line) for line in (root / "where.txt").read_text().splitlines()]
        self.assertEqual([(place.name, place.parent.parent) for place in where], [("tmp", Path(fresh))] * 2,
                         "each run's temp files went into that run's own folder, not wherever TMPDIR fell back to")

    def test_ten_back_to_back_mutations_all_score_correctly(self):
        # The realistic case: a table of many mutations run inside one second between them.
        root = tiny_project()
        results, restored = mutate.run(root, "tests", [BREAK_ADD, BREAK_SUB] * 5)
        self.assertEqual({r["status"] for r in results}, {mutate.CAUGHT})
        self.assertTrue(restored)


@slow("a mutation run no test notices, on a tiny tree, 3 tests, 2.1 s on 2026-10-26")
class AnEscapedMutationTest(unittest.TestCase):
    def test_a_defect_no_test_notices_is_reported_escaped_not_caught(self):
        # The whole product. `sub` has no test, so breaking it leaves the suite green.
        root = tiny_project(tested=False)
        results, _ = mutate.run(root, "tests", [BREAK_SUB])
        self.assertEqual(results[0]["status"], mutate.ESCAPED)
        self.assertIn("no test notices", results[0]["detail"])

    def test_an_escape_makes_the_exit_code_say_so(self):
        root = tiny_project(tested=False)
        results, restored = mutate.run(root, "tests", [BREAK_SUB])
        self.assertEqual(mutate.verdict(results, restored), mutate.EXIT_ESCAPED)

    def test_the_same_defect_is_caught_once_a_test_exists(self):
        # The control: without it the test above passes for a tool that reports everything
        # escaped.
        root = tiny_project(tested=True)
        results, _ = mutate.run(root, "tests", [BREAK_SUB])
        self.assertEqual(results[0]["status"], mutate.CAUGHT)


class ARefusedMutationTest(unittest.TestCase):
    def test_a_find_that_matches_nothing_is_refused_not_scored(self):
        # An earlier hand-rolled harness scored this "caught": the substitution did nothing and
        # the unmutated suite was red for an unrelated reason.
        root = tiny_project()
        results, _ = mutate.run(root, "tests", [dict(BREAK_ADD, find="return a * b")])
        self.assertEqual(results[0]["status"], mutate.REFUSED)
        self.assertIn("0 time(s)", results[0]["detail"])

    def test_a_find_that_matches_twice_is_refused_too(self):
        root = tiny_project()
        # A second `add` body, with the arena's other functions kept: the pre-check now runs
        # under the lock inside `run`, and an arena missing what its tests import is red before
        # any mutation — a refusal to score, which is right, and not what this test is about.
        (root / "m.py").write_text((root / "m.py").read_text() + "\n\ndef add2(a, b):\n    return a + b\n")
        results, _ = mutate.run(root, "tests", [BREAK_ADD])
        self.assertEqual(results[0]["status"], mutate.REFUSED)
        self.assertIn("2 time(s)", results[0]["detail"])

    def test_a_refusal_is_not_an_ok_verdict(self):
        root = tiny_project()
        results, restored = mutate.run(root, "tests", [dict(BREAK_ADD, find="nope")])
        self.assertNotEqual(mutate.verdict(results, restored), mutate.EXIT_OK)


@slow("mutants that do not compile or import, run on a tiny tree, 7 tests, 2.6 s on 2026-10-26")
class AMutantThatCannotLoadIsRefusedTest(unittest.TestCase):
    """
    P186 (#135), part 1's CH-2: a replacement that breaks the file's syntax, import or format turns the suite red for a
    reason no test chose, and was scored caught. A wrongly indented `pass` in a P124 row would have, on 2026-10-11; only reading the row saw it.
    """

    def assert_refused(self, results, *words):
        self.assertEqual(results[0]["status"], mutate.REFUSED, results)
        for word in words:
            self.assertIn(word, results[0]["detail"])

    def test_a_mutant_that_does_not_compile_is_refused_naming_the_file(self):
        root = tiny_project()
        before = (root / "m.py").read_text()
        results, restored = mutate.run(root, "tests", [dict(BREAK_ADD, replace="return a +")])
        self.assert_refused(results, "m.py", "does not compile")
        self.assertEqual(((root / "m.py").read_text(), restored), (before, True))

    def test_a_mutant_that_does_not_import_is_refused_naming_the_file(self):
        root = tiny_project()
        broken = {"file": "m.py", "name": "a name the module needs is gone", "find": "def sub(a, b):",
                  "replace": "nothing_defines_this\ndef sub(a, b):"}
        results, _ = mutate.run(root, "tests", [broken])
        self.assert_refused(results, "m.py", "does not import", "NameError")

    def test_a_json_mutant_that_does_not_parse_is_refused_naming_the_file(self):
        root = tiny_project()
        (root / "facts.json").write_text('{"value": 2.5}\n')
        results, _ = mutate.run(root, "tests", [{"file": "facts.json", "name": "a brace lost", "find": "}", "replace": ""}])
        self.assert_refused(results, "facts.json", "is not JSON")

    def test_a_refused_mutant_is_not_an_ok_verdict(self):
        root = tiny_project()
        results, restored = mutate.run(root, "tests", [dict(BREAK_ADD, replace="return a +")])
        self.assertNotEqual(mutate.verdict(results, restored), mutate.EXIT_OK)

    def test_anchors_names_a_mutant_that_does_not_compile_without_running_anything(self):
        root = tiny_project()
        stale = table(root, BREAK_SUB, dict(BREAK_ADD, replace="return a +"))
        said = mutate.unloadable(root, json.loads(stale.read_text()))
        self.assertEqual([(name, file) for name, file, _ in said], [("add subtracts", "m.py")])
        self.assertTrue(said[0][2].startswith("the mutant of m.py does not compile: line 2, "), said)
        self.assertEqual(mutate.main(["--anchors", str(stale), "--root", str(root)]), mutate.EXIT_ESCAPED)

    def test_a_file_that_never_imported_alone_is_judged_by_the_suite_not_refused(self):
        # The mutation run of PR #292: with the baseline guard gone, every mutant of such a file read as refused.
        root = tiny_project()
        (root / "tests" / "cfg.py").write_text("STEP = 1\n")
        (root / "m.py").write_text("import cfg\n" + (root / "m.py").read_text())
        results, _ = mutate.run(root, "tests", [BREAK_ADD])
        self.assertEqual(results[0]["status"], mutate.CAUGHT, results)

    def test_the_import_check_finds_a_module_beside_its_own_file_in_a_folder(self):
        # The mutation run of PR #292: an import check that looked in the wrong folder judged nothing.
        root = tiny_project()
        (root / "pkg").mkdir()
        (root / "pkg" / "t.py").write_text("ONE = 1\n")
        (root / "pkg" / "s.py").write_text("from t import ONE\n\ndef one():\n    return ONE\n")
        write_test(root, "test_s.py", "sys.path.insert(0, %r)" % str(root / "pkg"), "import s",
                   "class S(unittest.TestCase):", "    def test_one(self): self.assertEqual(s.one(), 1)")
        broken = {"file": "pkg/s.py", "name": "a module that is not there", "find": "from t import ONE",
                  "replace": "import nonexistent_xyz\nfrom t import ONE"}
        results, _ = mutate.run(root, "tests", [broken])
        self.assert_refused(results, "pkg/s.py", "does not import", "nonexistent_xyz")


class TheToolIsHonestAboutItselfTest(unittest.TestCase):
    def test_a_suite_that_is_red_before_mutating_is_refused(self):
        # A red suite catches nothing, so scoring mutations against it is meaningless.
        root = tiny_project(green=False)
        self.assertEqual(
            mutate.main([str(table(root, BREAK_ADD)), "--root", str(root)]),
            mutate.EXIT_COULD_NOT_RUN)

    def test_a_red_pre_check_names_the_tests_that_are_red(self):
        # P787: a red pre-check inside a --copy was read as a bug of the copy, because the tool said only "not green".
        root = tiny_project(green=False)
        with self.assertRaises(mutate.RedBeforeMutation) as red:
            mutate.run(root, "tests", [BREAK_ADD])
        said = str(red.exception).splitlines()
        self.assertEqual(said[0], "the suite is not green BEFORE any mutation; a red suite catches nothing")
        self.assertEqual([line for line in said if "test_add" in line], ["  FAIL: test_add (test_m.T)"])
        self.assertIn("  FAILED (failures=1)", said)
        self.assertEqual(mutate.suite_is_green(tiny_project(), "tests").red_lines, (), "a green run names nothing")
        self.assertEqual(mutate.RED_LINE.findall("x\nsubprocess.CalledProcessError: exit 1\ny"), ["subprocess.CalledProcessError: exit 1"])

    def test_all_caught_is_only_reported_when_the_suite_is_green_afterwards(self):
        # `restored=False` means something is left mutated or broke; nothing can be trusted.
        results = [{"name": "x", "status": mutate.CAUGHT, "detail": ""}]
        self.assertEqual(mutate.verdict(results, restored=False), mutate.EXIT_COULD_NOT_RUN)

    def test_the_command_line_end_to_end(self):
        root = tiny_project(tested=False)
        code = mutate.main([str(table(root, BREAK_ADD, BREAK_SUB)), "--root", str(root)])
        self.assertEqual(code, mutate.EXIT_ESCAPED)

    def test_the_rendering_names_the_missing_test(self):
        results = [{"name": "sub adds", "status": mutate.ESCAPED, "detail": "no test notices"}]
        text = mutate.render(results, True, mutate.EXIT_ESCAPED)
        self.assertIn("ESCAPED", text)
        self.assertIn("sub adds", text)
        self.assertIn("missing test", text)



class AnchorsAreCheckedWithoutRunningTest(unittest.TestCase):
    """
    A table's `find` strings go stale when the code moves under them, and a refused mutation
    guards nothing. `--anchors` says so in a second, so it can run at every commit.
    """

    def test_a_stale_anchor_is_named_and_nothing_is_run(self):
        root = tiny_project()
        wrong = mutate.anchors(root, [BREAK_ADD, dict(BREAK_SUB, find="return a // b")])
        self.assertEqual([(name, count) for name, _, count in wrong], [("sub adds", 0)])

    def test_anchors_mode_exits_escaped_on_a_stale_table_and_ok_on_a_fresh_one(self):
        root = tiny_project()
        fresh = table(root, BREAK_ADD, BREAK_SUB)
        self.assertEqual(mutate.main(["--anchors", str(fresh), "--root", str(root)]), mutate.EXIT_OK)
        stale = root / "stale.json"
        stale.write_text(json.dumps([dict(BREAK_ADD, find="return a ** b")]))
        self.assertEqual(mutate.main(["--anchors", str(fresh), str(stale), "--root", str(root)]),
                         mutate.EXIT_ESCAPED)

    def test_a_missing_file_counts_as_an_anchor_matching_nowhere(self):
        root = tiny_project()
        wrong = mutate.anchors(root, [dict(BREAK_ADD, file="gone.py")])
        self.assertEqual(wrong[0][2], 0)


class OneRunAtATimeTest(unittest.TestCase):
    def test_a_second_run_is_refused_while_the_first_holds_the_lock(self):
        # Two runs overlapped in the background on 2026-09-29, rewriting and restoring the same
        # files under each other; both reported verdicts neither had earned.
        root = tiny_project()
        (root / mutate.LOCK_NAME).write_text("12345")
        self.assertEqual(mutate.main([str(table(root, BREAK_ADD)), "--root", str(root)]),
                         mutate.EXIT_COULD_NOT_RUN)
        with self.assertRaises(mutate.AnotherRunIsActive):
            mutate.run(root, "tests", [BREAK_ADD])

    def test_the_lock_is_held_while_the_suite_is_pre_checked(self):
        # Audit C8: the pre-check took six seconds before the lock existed, and two runs started
        # inside that window both took it.
        import tempfile
        from unittest import mock
        root = Path(tempfile.mkdtemp())
        seen = []
        def green_under_lock(root_seen, tests):
            seen.append((root_seen / mutate.LOCK_NAME).exists())
            return False
        with mock.patch.object(mutate, "suite_is_green", green_under_lock):
            with self.assertRaises(mutate.RedBeforeMutation):
                mutate.run(root, "tests", [])
        self.assertEqual(seen, [True], "the pre-check ran with the lock already taken")
        self.assertFalse((root / mutate.LOCK_NAME).exists())

    def test_a_table_naming_a_missing_file_is_refused_not_a_traceback(self):
        import tempfile
        root = Path(tempfile.mkdtemp())
        original, refusal = mutate.apply(root, {"file": "scripts/nope.py", "find": "x", "replace": "y", "name": "n"})
        self.assertIsNone(original)
        self.assertIn("does not exist", refusal)

    def test_the_lock_is_gone_after_a_run_whatever_happened(self):
        root = tiny_project()
        mutate.run(root, "tests", [BREAK_ADD])
        self.assertFalse((root / mutate.LOCK_NAME).exists())
        with self.assertRaises(KeyError):
            mutate.run(root, "tests", [{"file": "m.py"}])      # a malformed row raises mid-run
        self.assertFalse((root / mutate.LOCK_NAME).exists(), "the lock outlived a failed run")

def counting(case):
    """Record every suite run as the near set it ran, or None for the whole suite — and still run it."""
    from unittest import mock
    calls, real = [], mutate.suite_is_green

    def counted(root, tests, only=(), failfast=False):
        calls.append(tuple(only) or None)
        return real(root, tests, only=only, failfast=failfast)
    patcher = mock.patch.object(mutate, "suite_is_green", counted)
    patcher.start()
    case.addCleanup(patcher.stop)
    return calls


def write_test(root, name, *lines):
    (root / "tests" / name).write_text("\n".join(["import sys, unittest", "sys.path.insert(0, %r)" % str(root)] + list(lines)) + "\n")


@slow("mutation runs of a tiny tree, near tests then the whole suite, 7 tests, 3.7 s on 2026-10-26")
class NearTestsFirstTest(unittest.TestCase):
    """P98: a mutation meets the tests near its file first; the whole suite decides only what they miss."""

    def test_a_python_file_is_near_the_tests_that_import_it_and_any_other_file_near_those_naming_it(self):
        root = tiny_project()
        write_test(root, "test_alias.py", "import m as other")
        write_test(root, "test_words.py", "SAID = 'm is mentioned, not imported'")
        write_test(root, "test_data.py", "NAME = 'd.json'")
        self.assertEqual(mutate.near_tests(root, "tests", "m.py"), ["test_alias", "test_m"])
        self.assertEqual(mutate.near_tests(root, "tests", "data/d.json"), ["test_data"])
        self.assertEqual(mutate.near_tests(root, "tests", "x.md"), [])

    def test_a_defect_a_near_test_notices_is_caught_without_the_whole_suite(self):
        root = tiny_project()
        calls = counting(self)
        results, restored = mutate.run(root, "tests", [BREAK_ADD])
        self.assertEqual((results[0]["status"], results[0]["by"], restored), (mutate.CAUGHT, "near", True))
        self.assertEqual(calls.count(None), 2, "the whole suite runs only before and after: %s" % calls)

    def test_a_defect_the_near_tests_miss_is_caught_by_the_whole_suite(self):
        root = tiny_project(tested=False)
        write_test(root, "test_other.py", "import importlib", "class T(unittest.TestCase):",
                   "    def test_sub(self): self.assertEqual(importlib.import_module('m').sub(5, 3), 2)")
        results, _ = mutate.run(root, "tests", [BREAK_SUB])
        self.assertEqual((results[0]["status"], results[0]["by"]), (mutate.CAUGHT, "full"))

    def test_an_escape_is_reported_only_after_the_whole_suite(self):
        root = tiny_project(tested=False)
        calls = counting(self)
        results, _ = mutate.run(root, "tests", [BREAK_SUB])
        self.assertEqual(results[0]["status"], mutate.ESCAPED)
        self.assertEqual(calls.count(None), 3, "before, for the mutation, after: %s" % calls)

    def test_a_file_nothing_names_goes_straight_to_the_whole_suite(self):
        root = tiny_project()
        (root / "d.txt").write_text("5\n")
        write_test(root, "test_d.py", "from pathlib import Path", "class T(unittest.TestCase):",
                   "    def test_d(self): self.assertEqual(Path(%r, 'd' + '.txt').read_text(), '5\\n')" % str(root))
        calls = counting(self)
        results, _ = mutate.run(root, "tests", [{"file": "d.txt", "name": "five is six", "find": "5", "replace": "6"}])
        self.assertEqual((results[0]["status"], results[0]["by"]), (mutate.CAUGHT, "full"))
        self.assertEqual([call for call in calls if call], [], "nothing near d.txt was run: %s" % calls)

    def test_near_tests_that_fail_alone_on_clean_code_fall_back_to_the_whole_suite(self):
        root = tiny_project()
        write_test(root, "test_a.py", "import os", "os.environ['SET_BY_TEST_A'] = '1'")
        write_test(root, "test_m.py", "import os", "import m", "class T(unittest.TestCase):",
                   "    def test_add(self): self.assertEqual(m.add(2, 3), 5)",
                   "    def test_needs_a(self): self.assertEqual(os.environ.get('SET_BY_TEST_A'), '1')")
        self.assertEqual(mutate.near_tests(root, "tests", "m.py"), ["test_m"], "test_m is near m.py, so the fallback is what is tested")
        results, restored = mutate.run(root, "tests", [BREAK_ADD])
        self.assertEqual((results[0]["status"], results[0]["by"], restored), (mutate.CAUGHT, "full", True))

    def test_the_rendering_says_which_run_caught_it_and_the_command_line_how_long_it_took(self):
        text = mutate.render([{"name": "add subtracts", "status": mutate.CAUGHT, "by": "near", "detail": ""}],
                             True, mutate.EXIT_OK)
        self.assertIn("[caught near] add subtracts", text)
        import contextlib
        import io
        root = tiny_project()
        with contextlib.redirect_stdout(io.StringIO()) as out:
            mutate.main([str(table(root, BREAK_ADD)), "--root", str(root)])
        self.assertRegex(out.getvalue(), r"1 mutation\(s\) in \d+ s")



class RetargetTest(unittest.TestCase):
    """P440: --retarget moves the rows of a file that moved, by editing the table's text."""

    def test_retarget_moves_every_row_of_the_old_file_and_no_other(self):
        text = ('[{"file": "scripts/a.py", "name": "one", "find": "x", "replace": "y"},\n'
                ' {"file": "scripts/ab.py", "name": "two", "find": "x", "replace": "y"},\n'
                ' {"file": "scripts/a.py", "name": "three", "find": "scripts/a.py", "replace": "\\"file\\": \\"scripts/a.py\\""}]\n')
        changed, count = mutate.retarget(text, "scripts/a.py", "scripts/spark/a.py")
        self.assertEqual(count, 2)
        self.assertEqual([(row["file"], row["find"]) for row in json.loads(changed)],
                         [("scripts/spark/a.py", "x"), ("scripts/ab.py", "x"), ("scripts/spark/a.py", "scripts/a.py")])

    def test_retarget_keeps_the_table_s_own_alignment(self):
        text = '[{"file":"scripts/a.py", "find": "x"},\n {"file" :  "scripts/a.py", "find": "y"},\n {"file": "scripts/a.py", "find": "z"}]'
        changed, count = mutate.retarget(text, "scripts/a.py", "scripts/b.py")
        self.assertEqual((changed, count), ('[{"file":"scripts/b.py", "find": "x"},\n {"file" :  "scripts/b.py", "find": "y"},\n'
                                            ' {"file": "scripts/b.py", "find": "z"}]', 3))

    def test_retarget_refuses_a_table_that_is_not_json_and_a_text_that_does_not_match_the_rows(self):
        with self.assertRaises(ValueError):
            mutate.retarget('[{"file": "a.py",}]', "a.py", "b.py")
        with self.assertRaises(ValueError):
            mutate.retarget('[{"file": "a.py", "find": "x"}, {"note": {"file": "a.py"}}]', "a.py", "b.py")

    def test_the_command_that_moves_no_row_is_could_not_run_and_runs_alone(self):
        import contextlib
        import io
        root = Path(tempfile.mkdtemp())
        table_file = root / "t.json"
        table_file.write_text('[{"file": "c.py", "find": "x"}]')
        with contextlib.redirect_stderr(io.StringIO()) as err:
            self.assertEqual(mutate.main([str(table_file), "--retarget", "a.py", "b.py"]), mutate.EXIT_COULD_NOT_RUN)
        self.assertIn("nothing moved", err.getvalue())
        for flag in ("--anchors", "--copy"):
            with self.subTest(flag=flag), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                mutate.main([str(table_file), "--retarget", "c.py", "d.py", flag])
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            mutate.main([str(table_file), "--retarget", "c.py", "d.py", "--for", "c.py"])
        self.assertEqual(table_file.read_text(), '[{"file": "c.py", "find": "x"}]')

    def test_the_command_moves_the_rows_of_every_table_or_none(self):
        import contextlib
        import io
        root = Path(tempfile.mkdtemp())
        good, other, bad = root / "good.json", root / "other.json", root / "bad.json"
        good.write_text('[{"file": "a.py", "find": "x"}]')
        other.write_text('[{"file": "c.py", "find": "x"}]')
        bad.write_text("[{")
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(mutate.main([str(good), str(other), "--retarget", "a.py", "b.py"]), mutate.EXIT_OK)
        self.assertEqual(out.getvalue(), "  moved 1 row(s) from a.py to b.py in 1 of 2 table(s); run --anchors to prove them\n")
        self.assertEqual((good.read_text(), other.read_text()), ('[{"file": "b.py", "find": "x"}]', '[{"file": "c.py", "find": "x"}]'))
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(mutate.main([str(good), str(bad), "--retarget", "b.py", "c.py"]), mutate.EXIT_COULD_NOT_RUN)
        self.assertEqual(good.read_text(), '[{"file": "b.py", "find": "x"}]')


def tiny_package(root):
    """Under `scripts/spark/core/`: `sibling.py` and `leaf.py`, which reads `sibling` from its package, as every module of the core does."""
    core = root / "scripts" / "spark" / "core"
    core.mkdir(parents=True)
    for folder in (root / "scripts" / "spark", core):
        (folder / "__init__.py").write_text('"""A package."""\n')
    (core / "sibling.py").write_text("ONE = 1\n")
    (core / "leaf.py").write_text("from spark.core import sibling\n\n\ndef one():\n    return sibling.ONE\n")
    write_test(root, "test_leaf.py", "sys.path.insert(0, %r)" % str(root / "scripts"), "from spark.core import leaf",
               "class T(unittest.TestCase):", "    def test_one(self): self.assertEqual(leaf.one(), 1)")


class APackageModuleTest(unittest.TestCase):
    """P440: a module of a package is found, near and imported, by its dotted name."""

    def test_a_package_module_s_near_tests_are_the_ones_that_import_its_dotted_name(self):
        root = tiny_project()
        (root / "scripts" / "spark" / "core").mkdir(parents=True)
        for folder in (root / "scripts" / "spark", root / "scripts" / "spark" / "core"):
            (folder / "__init__.py").write_text("")
        for name, line in (("test_from_package.py", "from spark.core import outcomes"),
                           ("test_dotted.py", "import spark.core.outcomes"),
                           ("test_from_module.py", "from spark.core.outcomes import ONE"),
                           ("test_among_names.py", "from spark.core import other, outcomes as o"),
                           ("test_flat.py", "import outcomes"),
                           ("test_look_alike.py", "from spark.core import outcomes_extra\nimport spark.core.outcomes_extra"),
                           ("test_other_package.py", "from spark.edge import outcomes")):
            write_test(root, name, line)
        self.assertEqual(mutate.near_tests(root, "tests", "scripts/spark/core/outcomes.py"),
                         ["test_among_names", "test_dotted", "test_from_module", "test_from_package"])
        self.assertEqual(mutate.near_tests(root, "tests", "scripts/outcomes.py"), ["test_flat"])
        self.assertEqual(mutate.near_tests(root, "tests", "scripts/spark/core/__init__.py"),
                         ["test_among_names", "test_dotted", "test_from_module", "test_from_package", "test_look_alike"])

    def test_a_script_in_a_folder_without_an_init_is_near_the_tests_that_import_its_stem(self):
        # a stand_in/ folder (spark's is scripts/spark/firmware/stand_in/) is no package: tests/test_journey_basic.py does `import machine`.
        root = tiny_project()
        (root / "scripts" / "stand_in").mkdir(parents=True)
        (root / "scripts" / "stand_in" / "machine.py").write_text("ONE = 1\n")
        write_test(root, "test_flat.py", "import machine")
        write_test(root, "test_dotted.py", "import stand_in.machine")
        self.assertEqual(mutate.near_tests(root, "tests", "scripts/stand_in/machine.py"), ["test_flat"])
        self.assertIsNone(mutate._import_error(root, "scripts/stand_in/machine.py"))

    def test_a_folder_below_a_folder_without_an_init_falls_back_to_the_stem(self):
        root = tiny_project()
        inner = root / "scripts" / "fallback" / "inner"
        inner.mkdir(parents=True)
        (inner / "__init__.py").write_text("")
        (inner / "x.py").write_text("ONE = 1\n")
        write_test(root, "test_stem.py", "import x")
        write_test(root, "test_path.py", "from fallback.inner import x")
        self.assertEqual(mutate.import_spec(root, "scripts/fallback/inner/x.py"), (inner, "x"))
        self.assertEqual(mutate.near_tests(root, "tests", "scripts/fallback/inner/x.py"), ["test_stem"])

    def test_a_package_module_s_import_is_checked_by_its_dotted_name(self):
        root = tiny_project()
        tiny_package(root)
        self.assertEqual([mutate._import_error(root, file) for file in ("scripts/spark/core/leaf.py", "scripts/spark/__init__.py")],
                         [None, None])
        broken = {"file": "scripts/spark/core/leaf.py", "name": "the package has no such module",
                  "find": "from spark.core import sibling", "replace": "from spark.core import sibling_xyz"}
        results, restored = mutate.run(root, "tests", [broken])
        self.assertEqual((results[0]["status"], restored), (mutate.REFUSED, True))
        self.assertIn("does not import", results[0]["detail"])
        self.assertIn("sibling_xyz", results[0]["detail"])


class OnlyTheMutationsOfAPathTest(unittest.TestCase):
    """P208: --for keeps the rows of a file, or of a folder and everything in it, from any number of tables."""

    ROWS = [{"file": "scripts/a.py", "find": "x"}, {"file": "scripts/ab.py", "find": "y"}, {"file": "tools/b.py", "find": "z"}]

    def test_a_file_keeps_its_own_rows(self):
        self.assertEqual(mutate.related(self.ROWS, ["scripts/a.py"]), self.ROWS[:1])

    def test_several_names_in_one_argument_are_each_kept(self):
        # zsh does not split a variable: `--for $changed` arrives as one argument, a name per line (FR5).
        self.assertEqual(mutate.related(self.ROWS, ["scripts/a.py\ntools/b.py"]), [self.ROWS[0], self.ROWS[2]])

    def test_a_folder_keeps_everything_under_it_and_no_look_alike(self):
        self.assertEqual(mutate.related(self.ROWS, ["./scripts/"]), self.ROWS[:2])
        self.assertEqual(mutate.related(self.ROWS, ["scripts/a"]), [])

    def test_the_command_runs_only_the_related_rows(self):
        root = tiny_project(tested=False)
        (root / "other.py").write_text("x = 1\n")
        rows = table(root, BREAK_SUB, {"file": "other.py", "name": "x moves", "find": "x = 1", "replace": "x = 2"})
        self.assertEqual(mutate.main([str(rows), "--root", str(root), "--for", "other.py"]), mutate.EXIT_ESCAPED)
        self.assertEqual(mutate.main([str(rows), "--root", str(root), "--for", "nothing.py"]), mutate.EXIT_OK)


def tiny_project_that_finds_itself():
    """tiny_project, but its test finds `m` beside its own file, as this repository's tests do: a copy tests the copy."""
    root = tiny_project()
    test = root / "tests" / "test_m.py"
    test.write_text(test.read_text().replace("sys.path.insert(0, %r)" % str(root),
                                             "sys.path.insert(0, __import__('os').path.dirname(__file__) + '/..')"))
    return root


class AMutationRunInACopyTest(unittest.TestCase):
    """P208: --copy mutates a copy of the tree, so no file a person or another agent has open is ever rewritten."""

    def test_the_run_never_touches_the_tree_it_was_given_and_the_copy_goes(self):
        root = tiny_project_that_finds_itself()
        seen = []
        real_run = mutate.run

        def watched(where, tests, mutations, **kept):
            seen.append(where)
            self.assertEqual((root / "m.py").read_text().count("return a + b"), 1)
            return real_run(where, tests, mutations, **kept)

        with unittest.mock.patch.object(mutate, "run", side_effect=watched):
            code = mutate.main([str(table(root, BREAK_ADD)), "--root", str(root), "--copy"])
        self.assertEqual(code, mutate.EXIT_OK)
        self.assertNotEqual(seen[0], root.resolve())
        self.assertFalse(seen[0].parent.exists(), "the copy, or the folder it was made in, stays behind")
    def test_a_copy_skips_the_after_suite_and_reports_restored(self):
        # P424: a copy is deleted after the run, so running the whole suite again to prove it restored proves nothing.
        root = tiny_project()
        calls = counting(self)
        results, restored = mutate.run(root, "tests", [BREAK_ADD], copied=True)
        self.assertEqual((results[0]["status"], restored, calls.count(None)), (mutate.CAUGHT, True, 1))
        calls.clear()
        mutate.run(root, "tests", [BREAK_ADD])
        self.assertEqual(calls.count(None), 2, "outside a copy the suite runs before and after: %s" % calls)

    def test_the_copy_leaves_out_git_worktrees_caches_and_the_lock_and_borrows_node_modules(self):
        root = Path(tempfile.mkdtemp()) / "tree"
        for name in (".git/HEAD", ".worktrees/x/f.py", "__pycache__/c.pyc", mutate.LOCK_NAME, "kept.py",
                     "node_modules/p/i.js", "tools/circuit-to-wokwi/node_modules/q/i.js", "tools/circuit-to-wokwi/cli.ts"):
            (root / name).parent.mkdir(parents=True, exist_ok=True)
            (root / name).write_text("x")
        (root / "link.py").symlink_to("kept.py")
        copy = mutate.copy_of(root)
        try:
            for left_out in (".git", ".worktrees", "__pycache__", mutate.LOCK_NAME):
                self.assertFalse((copy / left_out).exists(), left_out)
            self.assertTrue((copy / "kept.py").is_file())
            self.assertTrue((copy / "link.py").is_symlink(), "a symlink is copied as a symlink")
            for folder in (Path("."), Path("tools") / "circuit-to-wokwi"):
                borrowed = copy / folder / "node_modules"
                self.assertTrue(borrowed.is_symlink(), folder)
                self.assertEqual(borrowed.resolve(), (root / folder / "node_modules").resolve())
        finally:
            __import__("shutil").rmtree(copy.parent)


def ledger_of(root):
    """The ledger a run on `root` writes, where `main` puts it: tests/mutations/ledger.jsonl under the root."""
    return ledger.LedgerStore(root / "tests" / "mutations" / ledger.LEDGER_NAME)


@slow("mutation runs of a tiny tree that write the ledger, 6 tests, 6.1 s on 2026-11-12")
class TheLedgerTest(unittest.TestCase):
    """P787: a run that plants rows writes one ledger line per row, in the tree it was given, also under --copy."""

    def test_a_run_records_each_row_in_the_ledger_it_was_given(self):
        root = tiny_project(tested=False)  # add is tested, sub is not
        content = (root / "m.py").read_bytes()
        refused = dict(BREAK_ADD, name="nowhere", find="return a * b")
        results, restored = mutate.run(root, "tests", [BREAK_ADD, BREAK_SUB, refused], ledger_store=ledger_of(root))
        ended = datetime.now().astimezone()
        self.assertEqual(([r["status"] for r in results], restored), ([mutate.CAUGHT, mutate.ESCAPED, mutate.REFUSED], True))
        lines = {entry["key"]: entry for entry in ledger_of(root).read()}
        self.assertEqual(set(lines), {ledger.row_key(row) for row in (BREAK_ADD, BREAK_SUB, refused)})
        add, sub, nowhere = (lines[ledger.row_key(row)] for row in (BREAK_ADD, BREAK_SUB, refused))
        self.assertEqual((add["status"], add["by"], add["caught"]), (ledger.CAUGHT, "test_m", 1), "the near test that caught it")
        self.assertEqual((sub["status"], sub["by"], sub["caught"]), (ledger.ESCAPED, ledger.ESCAPE, 0))
        self.assertEqual((nowhere["status"], nowhere["by"], nowhere["caught"]), (ledger.REFUSED, None, 0))
        self.assertEqual({entry["blob"] for entry in lines.values()}, {ledger.blob_of(content)}, "the file as the run read it")
        self.assertEqual({entry["date"] for entry in lines.values()}, {add["date"]}, "one date per run")
        self.assertRegex(add["date"], r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d[+-]\d\d:\d\d$")
        # The run's END, not its start (the review of PR 1): a long night run that ends after a shorter later one must
        # win the merge. Three rows take seconds, and the stamp is in whole seconds, so it sits within a second of the end.
        self.assertGreaterEqual(datetime.fromisoformat(add["date"]), ended - timedelta(seconds=1), add["date"])
        self.assertLessEqual(datetime.fromisoformat(add["date"]), ended)
        self.assertTrue(all(isinstance(entry["s"], int) for entry in lines.values()), lines)
        self.assertEqual([r.get("by") for r in results], [mutate.NEAR, None, None], "the report's own `by` is unchanged")

    def test_a_second_run_at_the_same_content_adds_the_catch(self):
        root = tiny_project()
        for _ in range(2):
            mutate.run(root, "tests", [BREAK_ADD], ledger_store=ledger_of(root))
        self.assertEqual([entry["caught"] for entry in ledger_of(root).read()], [2])

    def test_main_writes_the_ledger_in_the_tree_it_was_given_also_with_copy(self):
        import contextlib
        import io
        for flags in ((), ("--copy",)):
            with self.subTest(flags=flags):
                root = tiny_project_that_finds_itself()
                with contextlib.redirect_stdout(io.StringIO()) as out:
                    code = mutate.main([str(table(root, BREAK_ADD)), "--root", str(root), *flags])
                self.assertEqual(code, mutate.EXIT_OK)
                self.assertEqual([(entry["status"], entry["by"]) for entry in ledger_of(root).read()], [(ledger.CAUGHT, "test_m")])
                self.assertIn("\n  1 row(s) recorded in tests/mutations/ledger.jsonl (1 in all)\n", out.getvalue())
        root = tiny_project_that_finds_itself()
        with contextlib.redirect_stdout(io.StringIO()) as out:
            mutate.main([str(table(root, BREAK_ADD)), "--root", str(root), "--copy", "--json"])
        self.assertEqual(json.loads(out.getvalue())["ledger"], {"path": "tests/mutations/ledger.jsonl", "recorded": 1, "rows": 1})

    def test_a_run_whose_files_are_not_restored_records_nothing(self):
        # The after-suite goes red on its own: the project's test fails at its second run, which is the restore check.
        root = tiny_project()
        count = root / "count"
        write_test(root, "test_m.py", "import m", "from pathlib import Path", "class T(unittest.TestCase):",
                   "    def test_add(self):",
                   "        runs = Path(%r); runs.write_text(runs.read_text() + 'x' if runs.exists() else 'x')" % str(count),
                   "        self.assertEqual((m.add(2, 3), len(runs.read_text()) < 2), (5, True))")
        results, restored = mutate._run(root, "tests", [BREAK_ADD], {}, False, ledger_store=ledger_of(root))
        self.assertEqual((results[0]["status"], restored), (mutate.CAUGHT, False))
        self.assertEqual(ledger_of(root).read(), [], "a verdict nothing can trust recorded a line")

    def test_the_ledger_command_counts_by_status_and_anchors_writes_none(self):
        import contextlib
        import io
        root = tiny_project()
        self.assertEqual(mutate.main(["--anchors", str(table(root, BREAK_ADD)), "--root", str(root)]), mutate.EXIT_OK)
        self.assertFalse(ledger_of(root).path.exists(), "--anchors wrote the ledger")
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(mutate.main(["--ledger", "--root", str(root)]), mutate.EXIT_OK)
        self.assertEqual(out.getvalue(), "  ledger tests/mutations/ledger.jsonl: 0 row(s)\n")
        mutate.run(tiny_project(), "tests", [BREAK_ADD], ledger_store=ledger_of(root))
        mutate.run(tiny_project(tested=False), "tests", [BREAK_SUB], ledger_store=ledger_of(root))
        with contextlib.redirect_stdout(io.StringIO()) as out:
            mutate.main(["--ledger", "--root", str(root)])
        self.assertEqual(out.getvalue(), "  ledger tests/mutations/ledger.jsonl: 2 row(s): 1 caught, 1 escaped\n")
        with contextlib.redirect_stdout(io.StringIO()) as out:
            mutate.main(["--ledger", "--root", str(root), "--json"])
        self.assertEqual(json.loads(out.getvalue()), {"tool": "mutate", "ledger": "tests/mutations/ledger.jsonl", "rows": 2,
                                                      "statuses": {"caught": 1, "escaped": 1}})
        for extra in ([str(table(root, BREAK_ADD))], ["--anchors"], ["--copy"]):
            with self.subTest(extra=extra), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                mutate.main(["--ledger", "--root", str(root)] + extra)
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            mutate.main(["--root", str(root)])  # no table and no --ledger: the usage, as before

    def test_caught_by_names_the_module_of_the_first_red_test(self):
        self.assertEqual(mutate.caught_by(mutate.SuiteResult(False, ("FAIL: test_add (test_m.T)", "FAILED (failures=1)"))), "test_m")
        self.assertEqual(mutate.caught_by(mutate.SuiteResult(False, ("ERROR: test_x (test_other.T.test_x)",))), "test_other", "3.11's id")
        self.assertEqual(mutate.caught_by(mutate.SuiteResult(False, ("ValueError: boom",))), ledger.SUITE, "no test named")
        self.assertEqual(mutate.caught_by(False), ledger.SUITE, "a plain bool from a stand-in")


@slow("mutation runs of a tiny tree under --tier and --tier-count, 3 tests, 1.4 s on 2026-11-12")
class TheTiersTest(unittest.TestCase):
    """P787 PR 2: --tier runs only the rows the ledger puts in the named tiers, and --tier-count runs nothing."""

    def proven_ledger(self, root, row, caught=2):
        """A ledger under `root` whose one line says `row` was caught `caught` times at its file's current content."""
        blob = ledger.blob_of((root / row["file"]).read_bytes())
        ledger_of(root).write([ledger.line(row, blob, "2026-11-12T10:00:00+01:00", ledger.CAUGHT, "test_m", 1) | {"caught": caught}])

    def test_tier_count_says_how_many_rows_each_tier_holds_and_runs_nothing(self):
        import contextlib
        import io
        root = tiny_project()
        rows = table(root, BREAK_ADD, BREAK_SUB, dict(BREAK_ADD, name="critical", find="def add", replace="def add_", tier="critical"))
        self.proven_ledger(root, BREAK_ADD)
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(mutate.main([str(rows), "--root", str(root), "--tier-count"]), mutate.EXIT_OK)
        self.assertEqual(out.getvalue(), "  tiers of 3 row(s) in 1 table(s): critical 1, new 1, proving 0, proven 1, retired 0\n")
        with contextlib.redirect_stdout(io.StringIO()) as out:
            mutate.main([str(rows), "--root", str(root), "--tier-count", "--json"])
        self.assertEqual(json.loads(out.getvalue()), {"tool": "mutate", "tables": 1, "rows": 3,
                                                      "tiers": {"critical": 1, "new": 1, "proving": 0, "proven": 1, "retired": 0}})
        self.assertEqual([entry["caught"] for entry in ledger_of(root).read()], [2], "nothing ran: the ledger is as it was")
        (root / "m.py").write_text((root / "m.py").read_text() + "# an edit\n")
        with contextlib.redirect_stdout(io.StringIO()) as out:
            mutate.main([str(rows), "--root", str(root), "--tier-count", "--for", "m.py"])
        self.assertEqual(out.getvalue(), "  tiers of 3 row(s) in 1 table(s): critical 1, new 2, proving 0, proven 0, retired 0\n",
                         "an edit of the file makes its proven row new again, by the blob rule alone")

    def test_a_tier_run_plants_only_the_selected_rows_and_says_so_in_its_header(self):
        import contextlib
        import io
        root = tiny_project()
        rows = table(root, BREAK_ADD, BREAK_SUB)
        self.proven_ledger(root, BREAK_ADD)
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(mutate.main([str(rows), "--root", str(root), "--tier", "new"]), mutate.EXIT_OK)
        said = out.getvalue().splitlines()
        self.assertEqual(said[0], "  tiers new: 1 row(s) selected (critical 0, new 1, proving 0, proven 1, retired 0)")
        self.assertEqual([line for line in said if line.startswith("  [")], ["  [caught near] sub adds"], "add's proven row did not run")
        self.assertIn("  1 mutation(s) in ", "\n".join(said))
        lines = {entry["key"]: entry for entry in ledger_of(root).read()}
        self.assertEqual((lines[ledger.row_key(BREAK_ADD)]["caught"], lines[ledger.row_key(BREAK_SUB)]["caught"]), (2, 1))
        with contextlib.redirect_stdout(io.StringIO()) as out:
            mutate.main([str(rows), "--root", str(root), "--tier", "proven,proving", "--json"])
        report = json.loads(out.getvalue())
        self.assertEqual(report["tiers"], {"selected": ["proven", "proving"], "rows": 2, "counts": {"critical": 0, "new": 0, "proving": 1, "proven": 1, "retired": 0}})
        self.assertEqual([r["name"] for r in report["mutations"]], ["sub adds", "add subtracts"], "proving before proven, whatever --tier's order")
        with contextlib.redirect_stderr(io.StringIO()) as err:
            self.assertEqual(mutate.main([str(rows), "--root", str(root), "--tier", "critical"]), mutate.EXIT_OK)
        self.assertEqual(err.getvalue(), "  no row is in the tier(s) critical: nothing to run\n")
        (root / "other.py").write_text("x = 1\n")
        more = table(root, BREAK_ADD, BREAK_SUB, {"file": "other.py", "name": "x moves", "find": "x = 1", "replace": "x = 2"})
        with contextlib.redirect_stdout(io.StringIO()) as out:
            mutate.main([str(more), "--root", str(root), "--tier", "new,new", "--for", "other.py", "--json"])
        self.assertEqual(json.loads(out.getvalue())["tiers"], {"selected": ["new"], "rows": 1, "counts": {"critical": 0, "new": 1, "proving": 0, "proven": 0, "retired": 0}},
                         "--for narrows the rows before the tiers count them, and a tier named twice is named once")

    def test_tier_count_runs_alone_and_tier_takes_the_four_words_only(self):
        import contextlib
        import io
        root = tiny_project()
        rows = table(root, BREAK_ADD)
        for extra in (["--anchors"], ["--copy"], ["--tier", "new"], ["--ledger"], ["--retarget", "m.py", "n.py"]):
            with self.subTest(extra=extra), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                mutate.main([str(rows), "--root", str(root), "--tier-count"] + extra)
        for bad in ("bogus", "new,bogus", "", "retired"):  # retired is a tier word, not one a sweep runs: --retire lists it
            with self.subTest(tier=bad), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                mutate.main([str(rows), "--root", str(root), "--tier", bad])
        self.assertFalse(ledger_of(root).path.exists(), "something ran")


class TheRetireTest(unittest.TestCase):
    """P787 PR 5: --retire lists the rows the ledger shows refused in two sweeps at their file's current blob, and runs nothing."""

    RETIRE_LINE = "  %d row(s) to retire: refused by --anchors in two sweeps; delete each with its reason in a PR, or re-anchor it\n"

    def project(self, *rows):
        """A tiny project whose one table sits beside the ledger, as the repository's do, with no `name` on the last row."""
        root = tiny_project()
        (root / "tests" / "mutations").mkdir()
        (root / "tests" / "mutations" / "p1-topic.json").write_text(json.dumps(list(rows)))
        return root

    def refused_line(self, root, row, refused, blob=None):
        return ledger.line(row, blob or ledger.blob_of((root / row["file"]).read_bytes()), "2026-11-12T10:00:00+01:00",
                           ledger.REFUSED, None, 0) | {"refused": refused}

    def retire(self, root, *flags):
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = mutate.main(["--retire", "--root", str(root), *flags])
        return code, out.getvalue()

    def test_a_row_refused_twice_at_the_current_blob_is_listed_by_table_index_and_name(self):
        gone = dict(BREAK_ADD, name="nowhere", find="return a * b")
        nameless = {"file": "m.py", "find": "return a / b", "replace": "return a // b"}
        root = self.project(BREAK_ADD, gone, nameless)
        ledger_of(root).write([self.refused_line(root, gone, 2), self.refused_line(root, nameless, 3)])
        self.assertEqual(self.retire(root), (mutate.EXIT_OK, "  p1-topic.json:1 nowhere\n  p1-topic.json:2 return a / b\n" + self.RETIRE_LINE % 2))
        code, said = self.retire(root, "--json")
        self.assertEqual(json.loads(said), {"tool": "mutate", "rows": 2, "retired": [
            {"table": "p1-topic.json", "index": 1, "name": "nowhere", "key": ledger.row_key(gone), "file": "m.py"},
            {"table": "p1-topic.json", "index": 2, "name": "return a / b", "key": ledger.row_key(nameless), "file": "m.py"}]})
        self.assertEqual(json.loads((root / "tests" / "mutations" / "p1-topic.json").read_text()), [BREAK_ADD, gone, nameless], "the tool deleted a row")

    def test_a_row_refused_once_or_at_an_older_blob_is_not_listed(self):
        gone = dict(BREAK_ADD, name="nowhere", find="return a * b")
        root = self.project(gone)
        ledger_of(root).write([self.refused_line(root, gone, 1)])
        self.assertEqual(self.retire(root), (mutate.EXIT_OK, self.RETIRE_LINE % 0), "one refusal is --anchors' business")
        ledger_of(root).write([self.refused_line(root, gone, 2, blob=ledger.blob_of(b"an older content\n"))])
        self.assertEqual(self.retire(root), (mutate.EXIT_OK, self.RETIRE_LINE % 0), "the file changed since: the blob rule")
        self.assertEqual(self.retire(tiny_project()), (mutate.EXIT_OK, self.RETIRE_LINE % 0), "no table and no ledger: nothing to retire")

    def test_retire_runs_alone(self):
        import contextlib
        import io
        root = tiny_project()
        for extra in ([str(table(root, BREAK_ADD))], ["--ledger"], ["--anchors"], ["--copy"], ["--tier-count"], ["--tier", "new"],
                      ["--budget", "1"], ["--for", "m.py"], ["--retarget", "m.py", "n.py"]):
            with self.subTest(extra=extra), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                mutate.main(["--retire", "--root", str(root)] + extra)
        self.assertFalse(ledger_of(root).path.exists(), "something ran")


class TheBudgetValueTest(unittest.TestCase):
    """P787 PR 3: the budget's arithmetic and the duration facts it reads, with plain numbers and no run."""

    def test_a_row_that_ends_at_the_budget_s_end_fits_and_one_second_more_crosses_it(self):
        budget = mutate.Budget(20, started=100.0)
        self.assertEqual(budget.left(100.0 + 1190), 10)
        self.assertTrue(budget.allows(100.0 + 1190, 10), "it ends exactly at the end: within")
        self.assertFalse(budget.allows(100.0 + 1190, 11), "it would cross by a second")
        self.assertFalse(budget.allows(100.0 + 1201, 0), "the budget is crossed already: nothing more runs")
        self.assertTrue(mutate.Budget(1, started=0).allows(0, 60))

    def test_the_expected_seconds_are_the_ledger_s_then_this_run_s_median_then_the_suite_s(self):
        known = {ledger.row_key(BREAK_ADD): 42}
        ran = [ledger.line(BREAK_ADD, "b", "d", ledger.CAUGHT, "test_m", 1), ledger.line(BREAK_ADD, "b", "d", ledger.ESCAPED, ledger.ESCAPE, 9),
               ledger.line(BREAK_ADD, "b", "d", ledger.CAUGHT, "test_m", 2)]
        refused = [ledger.line(BREAK_ADD, "b", "d", ledger.REFUSED, None, 0)] * 2
        self.assertEqual(mutate.expected_seconds(BREAK_ADD, known, ran, 180), 42, "its ledger line, whatever ran")
        self.assertEqual(mutate.expected_seconds(BREAK_SUB, known, ran, 180), 2, "no line: the median of this run's caught and escaped rows")
        self.assertEqual(mutate.expected_seconds(BREAK_SUB, known, refused + ran, 180), 2, "a refused row ran nothing: not in the median")
        self.assertEqual(mutate.expected_seconds(BREAK_SUB, known, refused, 180), 180, "two refused rows, nothing ran: the suite's seconds, not 0")
        self.assertEqual(mutate.expected_seconds(BREAK_SUB, known, [], 180), 180, "nothing ran yet: the pre-check suite's seconds")


def budget_ledger(root, *rows_and_seconds):
    """A ledger under `root` with one caught line per (row, seconds) at the row's file's current content: a faked last duration."""
    ledger_of(root).write([ledger.line(row, ledger.blob_of((root / row["file"]).read_bytes()), "2026-11-12T10:00:00+01:00",
                                       ledger.CAUGHT, "test_m", seconds) for row, seconds in rows_and_seconds])


@slow("mutation runs of a tiny tree under --budget, 7 tests, 5.6 s on 2026-11-13")
class TheBudgetTest(unittest.TestCase):
    """P787 PR 3: --budget stops before the row whose expected seconds would cross it, counted from the run's start."""

    def test_a_run_stops_before_the_row_whose_last_duration_would_cross_the_budget(self):
        root = tiny_project()
        budget_ledger(root, (BREAK_ADD, 50), (BREAK_SUB, 60))  # a tiny row takes a second; its ledger line says 50 or 60
        results, restored = mutate.run(root, "tests", [BREAK_ADD, BREAK_SUB], ledger_store=ledger_of(root),
                                       budget=mutate.Budget(1, time.monotonic()))
        self.assertEqual(([r["name"] for r in results], restored), (["add subtracts"], True), "sub's 60 s would cross the minute")
        lines = {entry["key"]: entry for entry in ledger_of(root).read()}
        self.assertEqual((lines[ledger.row_key(BREAK_ADD)]["caught"], lines[ledger.row_key(BREAK_SUB)]["caught"]), (2, 1),
                         "the row that ran is recorded; the left row's line is as it was")
        self.assertEqual((root / "m.py").read_text().count("return a + b"), 1)

    def test_the_budget_counts_from_the_run_s_start_so_the_overhead_is_inside_it(self):
        root = tiny_project()
        budget_ledger(root, (BREAK_ADD, 40))
        results, _ = mutate.run(root, "tests", [BREAK_ADD], ledger_store=ledger_of(root), budget=mutate.Budget(1, time.monotonic() - 30))
        self.assertEqual(results, [], "started 30 s ago: 30 + 40 crosses the minute, so nothing ran")
        results, _ = mutate.run(root, "tests", [BREAK_ADD], ledger_store=ledger_of(root), budget=mutate.Budget(1, time.monotonic()))
        self.assertEqual([r["status"] for r in results], [mutate.CAUGHT], "the same row with the whole minute runs")

    def test_the_closing_line_and_the_json_count_the_left_rows_per_tier(self):
        import contextlib
        import io
        root = tiny_project()
        rows = table(root, BREAK_ADD, BREAK_SUB)  # add, first in the table, is proven at 60 s; sub has no line (new; the suite's seconds)
        ledger_of(root).write([ledger.line(BREAK_ADD, ledger.blob_of((root / "m.py").read_bytes()), "2026-11-12T10:00:00+01:00",
                                           ledger.CAUGHT, "test_m", 60) | {"caught": 2}])
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(mutate.main([str(rows), "--root", str(root), "--budget", "1"]), mutate.EXIT_OK)
        said = out.getvalue().splitlines()
        self.assertEqual(said[-1], "  budget 1 min: ran 1 of 2 selected (critical 0/0, new 1/1, proving 0/0, proven 0/1); 1 left for the next sweep")
        self.assertEqual([line for line in said if line.startswith("  [")], ["  [caught near] sub adds"],
                         "under a budget the new row runs before the proven one that the table lists first (the tiers' order, no --tier)")
        with contextlib.redirect_stdout(io.StringIO()) as out:
            mutate.main([str(rows), "--root", str(root), "--budget", "1", "--tier", "proving", "--json"])  # sub, caught once above
        report = json.loads(out.getvalue())
        self.assertEqual(report["budget"], {"minutes": 1, "ran": 1, "selected": 1, "left": 0,
                                            "by_tier": {"critical": {"ran": 0, "selected": 0}, "new": {"ran": 0, "selected": 0},
                                                        "proving": {"ran": 1, "selected": 1}, "proven": {"ran": 0, "selected": 0}}},
                         "a tier not selected selected nothing, so the denominators add up to the selected count")
        self.assertEqual(report["tiers"]["rows"], 1)
        with contextlib.redirect_stdout(io.StringIO()) as out:
            mutate.main([str(rows), "--root", str(root), "--json"])
        self.assertNotIn("budget", json.loads(out.getvalue()), "without --budget no budget key")

    def test_a_budget_run_that_ran_no_row_is_could_not_run(self):
        import contextlib
        import io
        root = tiny_project()
        budget_ledger(root, (BREAK_ADD, 60))
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = mutate.main([str(table(root, BREAK_ADD)), "--root", str(root), "--budget", "1", "--json"])
        report = json.loads(out.getvalue())
        self.assertEqual((code, report["status"], report["budget"]["ran"], report["budget"]["left"]), (mutate.EXIT_COULD_NOT_RUN, "could-not-run", 0, 1),
                         "a 0 would say a pass about a run that tested nothing")

    def test_a_copy_writes_each_row_s_line_as_soon_as_it_is_done_and_the_real_tree_waits_for_the_after_suite(self):
        root = tiny_project()
        with self.assertRaises(KeyError):  # the second row is malformed: the run crashes after the first
            mutate.run(root, "tests", [BREAK_ADD, {"file": "m.py"}], copied=True, ledger_store=ledger_of(root))
        self.assertEqual([entry["status"] for entry in ledger_of(root).read()], [ledger.CAUGHT], "the copy's first row was kept")
        root = tiny_project()
        with self.assertRaises(KeyError):
            mutate.run(root, "tests", [BREAK_ADD, {"file": "m.py"}], ledger_store=ledger_of(root))
        self.assertEqual(ledger_of(root).read(), [], "in the real tree the lines wait for the after-suite, which never ran")

    def test_a_sigterm_in_a_copy_run_keeps_the_lines_recorded_before_it(self):
        # The file's existing way: the project's test blocks while the second row is planted, and the parent sends SIGTERM once
        # the first row's line is on disk. `subprocess.run` kills the blocked suite when the SystemExit passes through it.
        root = tiny_project_that_finds_itself()
        test = root / "tests" / "test_m.py"
        test.write_text(test.read_text() + "    def test_sub_blocks(self):\n"
                        "        while m.sub(5, 3) != 2: __import__('time').sleep(0.01)\n")
        mine = Path(tempfile.mkdtemp())
        child = subprocess.Popen([sys.executable, str(ROOT / "tools" / "mutate.py"), str(table(root, BREAK_ADD, BREAK_SUB)), "--root",
                                  str(root), "--copy"], env=dict(os.environ, TMPDIR=str(mine)),
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            for _ in range(6000):
                if ledger_of(root).path.exists() or child.poll() is not None:
                    break
                time.sleep(0.01)
            ended_first = child.poll()
            if ended_first is None:
                child.send_signal(signal.SIGTERM)
            code = child.wait(timeout=60)
        finally:
            if child.poll() is None:
                child.kill()
                child.wait()
        self.assertIsNone(ended_first, "the child ended with code %s before its first line" % ended_first)
        self.assertEqual(code, 128 + signal.SIGTERM)
        self.assertEqual([(entry["key"], entry["status"]) for entry in ledger_of(root).read()], [(ledger.row_key(BREAK_ADD), ledger.CAUGHT)],
                         "the row done before the signal is recorded, the one it stopped is not")
        self.assertEqual(os.listdir(mine), [])
        shutil.rmtree(mine, ignore_errors=True)

    def test_budget_takes_a_whole_number_of_minutes_above_zero_and_runs_rows(self):
        import contextlib
        import io
        root = tiny_project()
        rows = table(root, BREAK_ADD)
        for bad in (["--budget", "0"], ["--budget", "-5"], ["--budget", "1.5"], ["--budget", "20", "--anchors"],
                    ["--budget", "20", "--tier-count"], ["--budget", "20", "--retarget", "m.py", "n.py"]):
            with self.subTest(bad=bad), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                mutate.main([str(rows), "--root", str(root)] + bad)
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            mutate.main(["--ledger", "--root", str(root), "--budget", "20"])
        self.assertFalse(ledger_of(root).path.exists(), "something ran")


DAY = scratch.OLD_AFTER_SECONDS


def planted_scratch(name, age):
    """A folder `name` in this process's temp folder, last touched `age` seconds ago."""
    return planted_folder(tempfile.gettempdir(), name, age)


class TheScratchOfAStoppedRunTest(unittest.TestCase):
    """P435: a run that was killed leaves folders in the temp folder; the next start removes the old ones."""

    def test_each_prefix_loses_its_old_folder_and_keeps_its_young_one(self):
        for prefix in (mutate.RUN_PREFIX, mutate.IMPORT_PREFIX, mutate.COPY_PREFIX):
            old, young = planted_scratch(prefix + "old", 2 * DAY), planted_scratch(prefix + "young", 60)
            mutate.remove_old_scratch()
            self.assertEqual([old.exists(), young.exists()], [False, True], prefix)

    def test_the_prefixes_are_the_ones_the_run_makes(self):
        self.assertEqual((mutate.RUN_PREFIX, mutate.IMPORT_PREFIX, mutate.COPY_PREFIX),
                         ("mutate-run-", "mutate-import-", "mutate-copy-"))

    def test_main_sweeps_at_its_start(self):
        root = tiny_project_that_finds_itself()
        old = planted_scratch(mutate.COPY_PREFIX + "left-by-a-kill", 2 * DAY)
        self.assertEqual(mutate.main([str(table(root, BREAK_ADD)), "--root", str(root), "--copy"]), mutate.EXIT_OK)
        self.assertFalse(old.exists())

    def in_own_temp_folder(self):
        """A fresh temp folder that `tempfile` uses until the test ends."""
        mine, kept = tempfile.mkdtemp(), tempfile.tempdir
        tempfile.tempdir = mine
        self.addCleanup(setattr, tempfile, "tempdir", kept)
        return mine

    @unittest.skipIf(os.geteuid() == 0, "root reads every file")
    def test_a_copy_that_cannot_be_read_leaves_no_half_made_folder(self):
        root = Path(tempfile.mkdtemp()) / "tree"
        root.mkdir()
        (root / "ok.py").write_text("x")
        (root / "locked.py").write_text("x")
        (root / "locked.py").chmod(0)
        self.addCleanup((root / "locked.py").chmod, 0o644)
        mine = self.in_own_temp_folder()
        with self.assertRaises(shutil.Error):
            mutate.copy_of(root)
        self.assertEqual(os.listdir(mine), [])

    @unittest.skipIf(os.geteuid() == 0, "root writes into a read-only folder")
    def test_a_read_only_root_with_node_modules_leaves_no_copy(self):
        root = Path(tempfile.mkdtemp()) / "tree"
        (root / "node_modules").mkdir(parents=True)
        (root / "kept.py").write_text("x")
        root.chmod(0o555)
        self.addCleanup(root.chmod, 0o755)
        mine = self.in_own_temp_folder()
        with self.assertRaises(PermissionError):
            mutate.copy_of(root)
        self.assertEqual(os.listdir(mine), [])

    def test_a_read_only_folder_in_the_tree_is_gone_after_a_copy_run(self):
        root = tiny_project_that_finds_itself()
        (root / "ro").mkdir()
        (root / "ro" / "f").write_text("x")
        (root / "ro").chmod(0o555)
        self.addCleanup((root / "ro").chmod, 0o755)
        mine = self.in_own_temp_folder()
        self.assertEqual(mutate.main([str(table(root, BREAK_ADD)), "--root", str(root), "--copy"]), mutate.EXIT_OK)
        self.assertEqual(os.listdir(mine), [])

    def test_a_stop_by_sigterm_leaves_nothing_in_the_temp_folder(self):
        root = tiny_project_that_finds_itself()
        # The project's test waits for a file that never comes, so the child is inside its run, copy made, until the signal.
        gate = root / "never"
        test = root / "tests" / "test_m.py"
        test.write_text(test.read_text().replace("    def test_add(self): ", "    def test_add(self):\n"
                        "        while not __import__('os').path.exists(%r): __import__('time').sleep(0.01)\n"
                        "        " % str(gate), 1))
        mine = Path(tempfile.mkdtemp())
        child = subprocess.Popen([sys.executable, str(ROOT / "tools" / "mutate.py"), str(table(root, BREAK_ADD)), "--root", str(root),
                                  "--copy"], env=dict(os.environ, TMPDIR=str(mine)),
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            for _ in range(3000):
                if list(mine.glob(mutate.COPY_PREFIX + "*")) or child.poll() is not None:
                    break
                time.sleep(0.01)
            seen = bool(list(mine.glob(mutate.COPY_PREFIX + "*")))
            ended_first = child.poll()
            if ended_first is None:
                child.send_signal(signal.SIGTERM)
            code = child.wait(timeout=60)
        finally:
            if child.poll() is None:
                child.kill()
                child.wait()
        self.assertTrue(seen, "the child ended with code %s before a copy showed" % ended_first)
        self.assertEqual(code, 128 + signal.SIGTERM)
        self.assertEqual(os.listdir(mine), [])
        shutil.rmtree(mine, ignore_errors=True)

    def test_a_sigterm_during_the_removal_of_the_copy_waits_for_it_and_exits_143(self):
        root = tiny_project_that_finds_itself()
        mine = Path(tempfile.mkdtemp())
        # The child sends SIGTERM to itself from inside the removal of its copy, which only main's `finally` starts.
        wrapper = ("import os, signal, sys\nsys.path.insert(0, %r)\nimport mutate, scratch\nreal = scratch.remove_tree\n"
                   "def hit(folder):\n    os.kill(os.getpid(), signal.SIGTERM)\n    return real(folder)\n"
                   "scratch.remove_tree = hit\nsys.exit(mutate.main(sys.argv[1:]))\n" % str(ROOT / "tools"))
        done = subprocess.run([sys.executable, "-c", wrapper, str(table(root, BREAK_ADD)), "--root", str(root), "--copy"],
                              env=dict(os.environ, TMPDIR=str(mine)), capture_output=True, text=True, timeout=120)
        self.assertEqual(done.returncode, 128 + signal.SIGTERM, done.stderr[-300:])
        self.assertEqual(os.listdir(mine), [])
        shutil.rmtree(mine, ignore_errors=True)

    @unittest.skipIf(signal.getsignal(signal.SIGTERM) != signal.SIG_DFL, "the runner set its own SIGTERM handler")
    def test_the_handler_is_put_back(self):
        with mutate.sigterm_as_exit():
            self.assertNotEqual(signal.getsignal(signal.SIGTERM), signal.SIG_DFL)
        self.assertEqual(signal.getsignal(signal.SIGTERM), signal.SIG_DFL)


if __name__ == "__main__":
    unittest.main()
