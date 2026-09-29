"""
Proof that the numbers a commit carries are measured on the tree the commit holds.

A commit said "Ran 589 tests, OK" and ran 562 FAILED as committed: the run was on the working
tree, and the file it imported was staged one commit later (sprint-4 close audit, C3).

    python3 -m unittest discover -s tests
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import check_commit  # noqa: E402


def repo_with(files):
    """A throwaway git repository holding `files`, committed once."""
    root = Path(tempfile.mkdtemp())
    for name, text in files.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(text)
    for command in (["git", "init", "-q"], ["git", "add", "-A"],
                    ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "one"]):
        subprocess.run(command, cwd=str(root), check=True, capture_output=True)
    return root


class TheCommittedTreeIsMeasuredTest(unittest.TestCase):
    MUTATE = (ROOT / "scripts" / "mutate.py").read_text()
    OUTCOMES = (ROOT / "scripts" / "outcomes.py").read_text()

    def test_a_tree_whose_suite_passes_is_ok(self):
        root = repo_with({"scripts/mutate.py": self.MUTATE, "scripts/outcomes.py": self.OUTCOMES,
                          "m.py": "def add(a, b):\n    return a + b\n",
                          "tests/test_m.py": "import sys, unittest\nsys.path.insert(0, '.')\nimport m\n"
                                             "class T(unittest.TestCase):\n    def test_add(self): self.assertEqual(m.add(1, 2), 3)\n",
                          "tests/mutations/t.json": '[{"file": "m.py", "find": "a + b", "replace": "a - b"}]'})
        scratch = Path(tempfile.mkdtemp())
        check_commit.archive(root, "HEAD", scratch)
        suite, anchors, ok = check_commit.measure(scratch)
        self.assertTrue(ok, (suite, anchors))
        self.assertIn("OK", suite)
        self.assertIn("every anchor present", anchors)

    def test_a_file_left_uncommitted_makes_the_committed_tree_fail(self):
        # The C3 shape: the working tree has the module, the commit does not.
        root = repo_with({"scripts/mutate.py": self.MUTATE, "scripts/outcomes.py": self.OUTCOMES,
                          "m.py": "import helper\ndef add(a, b):\n    return helper.plus(a, b)\n",
                          "tests/test_m.py": "import sys, unittest\nsys.path.insert(0, '.')\nimport m\n"
                                             "class T(unittest.TestCase):\n    def test_add(self): self.assertEqual(m.add(1, 2), 3)\n"})
        (root / "helper.py").write_text("def plus(a, b):\n    return a + b\n")   # never committed
        working = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"],
                                 cwd=str(root), capture_output=True, text=True)
        self.assertEqual(working.returncode, 0, "the working tree passes — that is the trap")
        scratch = Path(tempfile.mkdtemp())
        check_commit.archive(root, "HEAD", scratch)
        suite, anchors, ok = check_commit.measure(scratch)
        self.assertFalse(ok, suite)

    def test_a_commit_that_does_not_exist_is_could_not_run(self):
        self.assertEqual(check_commit.main(["no-such-commit-xyz"]), check_commit.EXIT_COULD_NOT_RUN)


if __name__ == "__main__":
    unittest.main()
