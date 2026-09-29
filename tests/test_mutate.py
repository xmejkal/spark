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

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

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
        (root / "m.py").write_text("def add(a, b):\n    return a + b\n\ndef add2(a, b):\n    return a + b\n")
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


if __name__ == "__main__":
    unittest.main()
