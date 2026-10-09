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
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  P172: this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import mutate  # noqa: E402


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


class TheToolIsHonestAboutItselfTest(unittest.TestCase):
    def test_a_suite_that_is_red_before_mutating_is_refused(self):
        # A red suite catches nothing, so scoring mutations against it is meaningless.
        root = tiny_project(green=False)
        self.assertEqual(
            mutate.main([str(table(root, BREAK_ADD)), "--root", str(root)]),
            mutate.EXIT_COULD_NOT_RUN)

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


if __name__ == "__main__":
    unittest.main()
