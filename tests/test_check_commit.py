"""
Proof that the numbers a commit carries are measured on the tree the commit holds.

A commit said "Ran 589 tests, OK" and ran 562 FAILED as committed: the run was on the working
tree, and the file it imported was staged one commit later (sprint-4 close audit, C3).

    python3 -m unittest discover -s tests
"""

import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import check_commit  # noqa: E402


def own_env():
    """The environment with no GIT_* variable, so a throwaway repository's git never reaches another (P105)."""
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def repo_with(files):
    """A throwaway git repository holding `files`, committed once."""
    root = Path(tempfile.mkdtemp())
    for name, text in files.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(text)
    for command in (["git", "init", "-q"], ["git", "add", "-A"],
                    ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "one"]):
        subprocess.run(command, cwd=str(root), check=True, capture_output=True, env=own_env())
    return root


class TheCommittedTreeIsMeasuredTest(unittest.TestCase):
    MUTATE = (ROOT / "tools" / "mutate.py").read_text()
    OUTCOMES = (ROOT / "scripts" / "outcomes.py").read_text()

    def test_a_tree_whose_suite_passes_is_ok(self):
        root = repo_with({"tools/mutate.py": self.MUTATE, "scripts/outcomes.py": self.OUTCOMES,
                          "m.py": "def add(a, b):\n    return a + b\n",
                          "tests/test_m.py": "import sys, unittest\nsys.path.insert(0, '.')\nimport m\n"
                                             "class T(unittest.TestCase):\n    def test_add(self): self.assertEqual(m.add(1, 2), 3)\n",
                          "tests/mutations/t.json": '[{"file": "m.py", "find": "a + b", "replace": "a - b"}]'})
        scratch = Path(tempfile.mkdtemp())
        check_commit.archive(root, "HEAD", scratch)
        suite, anchors, ok, left = check_commit.measure(scratch)
        self.assertTrue(ok, (suite, anchors))
        self.assertIn("OK", suite)
        self.assertEqual(left, [], "a suite that leaves nothing behind leaves nothing to name")
        self.assertIn("every anchor present", anchors)

    def test_a_file_left_uncommitted_makes_the_committed_tree_fail(self):
        # The C3 shape: the working tree has the module, the commit does not.
        root = repo_with({"tools/mutate.py": self.MUTATE, "scripts/outcomes.py": self.OUTCOMES,
                          "m.py": "import helper\ndef add(a, b):\n    return helper.plus(a, b)\n",
                          "tests/test_m.py": "import sys, unittest\nsys.path.insert(0, '.')\nimport m\n"
                                             "class T(unittest.TestCase):\n    def test_add(self): self.assertEqual(m.add(1, 2), 3)\n"})
        (root / "helper.py").write_text("def plus(a, b):\n    return a + b\n")   # never committed
        working = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"],
                                 cwd=str(root), capture_output=True, text=True)
        self.assertEqual(working.returncode, 0, "the working tree passes — that is the trap")
        scratch = Path(tempfile.mkdtemp())
        check_commit.archive(root, "HEAD", scratch)
        suite, anchors, ok, left = check_commit.measure(scratch)
        self.assertFalse(ok, suite)

    def test_a_commit_that_does_not_exist_is_could_not_run(self):
        self.assertEqual(check_commit.main(["no-such-commit-xyz"]), check_commit.EXIT_COULD_NOT_RUN)


class TheSizeIsSaidTest(unittest.TestCase):
    """P99: the gate says how big scripts/ is and what a push adds to it — a number at every push, not a cap."""

    def test_code_lines_counts_code_not_prose(self):
        source = '"""A module."""\n\n# a comment\ndef f():\n    """What f does,\n    on two lines."""\n    return 1\n'
        self.assertEqual(check_commit.code_lines(source), 2)

    def test_the_size_line_says_the_growth_since_a_base(self):
        root = repo_with({"scripts/a.py": "x = 1\n", "scripts/README.md": "not code, not counted\n"})
        (root / "scripts" / "a.py").write_text("x = 1\ny = 2\n# free\n")
        (root / "scripts" / "b.py").write_text('"""free"""\nz = 3\n')
        for command in (["git", "add", "-A"], ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "two"]):
            subprocess.run(command, cwd=str(root), check=True, capture_output=True, env=own_env())
        self.assertEqual(check_commit.size_line(root, "HEAD", "HEAD~1"), "scripts/: 3 code lines (+2 since HEAD~1)")
        self.assertEqual(check_commit.size_line(root, "HEAD", "no-such-base"), "scripts/: 3 code lines")



def head_and_config(root):
    """A repository's HEAD commit and its config, read with no GIT_* variable steering git elsewhere."""
    head = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True, env=own_env()).stdout
    return head, (root / ".git" / "config").read_text()


class TheHooksGitIsNotTheSuitesTest(unittest.TestCase):
    """
    P105: git hands its hooks GIT_DIR, and in a worktree it is absolute. A suite that inherits it runs every throwaway
    repository's git against the repository being pushed: on 2026-10-05 four test commits landed on the real branch, the
    first deleting every file, and `core.bare = true` was written into its config.
    """

    def test_the_measured_suite_never_sees_the_hook_s_git_variables(self):
        root = repo_with({"tools/mutate.py": TheCommittedTreeIsMeasuredTest.MUTATE,
                          "scripts/outcomes.py": TheCommittedTreeIsMeasuredTest.OUTCOMES,
                          "m.py": "def add(a, b):\n    return a + b\n",
                          "tests/test_m.py": "import sys, unittest\nsys.path.insert(0, '.')\nimport m\n"
                                             "class T(unittest.TestCase):\n    def test_add(self): self.assertEqual(m.add(1, 2), 3)\n",
                          "tests/test_env.py": "import os, unittest\nclass E(unittest.TestCase):\n"
                                               "    def test_no_git_variable(self):\n"
                                               "        self.assertEqual([k for k in os.environ if k.startswith('GIT_')], [])\n",
                          "tests/mutations/t.json": '[{"file": "m.py", "find": "a + b", "replace": "a - b"}]'})
        scratch = Path(tempfile.mkdtemp())
        check_commit.archive(root, "HEAD", scratch)
        with mock.patch.dict(os.environ, {"GIT_DIR": str(root / ".git"), "GIT_INDEX_FILE": str(root / ".git" / "index")}):
            suite, anchors, ok, left = check_commit.measure(scratch)
        self.assertTrue(ok, (suite, anchors))

    def test_a_throwaway_repository_leaves_the_hook_s_repository_alone(self):
        victim = repo_with({"kept.txt": "the branch being pushed\n"})
        before = head_and_config(victim)
        with mock.patch.dict(os.environ, {"GIT_DIR": str(victim / ".git")}):
            repo_with({"junk.txt": "a test's file\n"})
        self.assertEqual(head_and_config(victim), before)


class TheGateEnforcesTheBoardTest(unittest.TestCase):
    """P102a: a board that breaks its limits fails the gate even when the suite and the anchors are green."""

    def test_a_board_problem_fails_the_gate(self):
        board = mock.Mock(main=mock.Mock(return_value=1))
        with mock.patch.object(check_commit, "archive"), \
                mock.patch.object(check_commit, "measure", return_value=("OK", "anchors ok", True, [])), \
                mock.patch.object(check_commit, "size_line", return_value="size"), \
                mock.patch.dict(sys.modules, {"check_backlog": board}), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(check_commit.main(["HEAD"]), check_commit.EXIT_PROBLEMS)


#: A test that passes and leaves a folder in the temp folder behind it — the shape of 1,888 of the 2,291 entries.
LEAKING_TEST = ("import tempfile, unittest\nclass L(unittest.TestCase):\n"
                "    def test_leaves_a_folder(self): tempfile.mkdtemp(prefix='left-behind-')\n")


def gate(left, ok=True, board=0):
    """`main` with everything but the temp verdict stubbed: (exit code, what it printed)."""
    said = io.StringIO()
    with mock.patch.object(check_commit, "archive"), \
            mock.patch.object(check_commit, "measure", return_value=("Ran 1 test / OK", "anchors ok", ok, left)), \
            mock.patch.object(check_commit, "size_line", return_value="size"), \
            mock.patch.dict(sys.modules, {"check_backlog": mock.Mock(main=mock.Mock(return_value=board))}), \
            contextlib.redirect_stdout(said):
        code = check_commit.main(["HEAD"])
    return code, said.getvalue()


class TheSuiteLeavesNoTempBehindTest(unittest.TestCase):
    """
    P172: one run of the suite on main c49a17e left 2,291 entries (26 MB) in an empty temp folder, and the
    pre-push hook runs it at every push. The gate gives the suite a temp folder of its own, and anything left
    in it fails the push — the leak could only grow while nothing counted it.
    """

    def tree(self, *tests):
        files = {"tools/mutate.py": TheCommittedTreeIsMeasuredTest.MUTATE,
                 "scripts/outcomes.py": TheCommittedTreeIsMeasuredTest.OUTCOMES,
                 "m.py": "def add(a, b):\n    return a + b\n",
                 "tests/test_m.py": "import sys, unittest\nsys.path.insert(0, '.')\nimport m\n"
                                    "class T(unittest.TestCase):\n    def test_add(self): self.assertEqual(m.add(1, 2), 3)\n",
                 "tests/mutations/t.json": '[{"file": "m.py", "find": "a + b", "replace": "a - b"}]'}
        files.update(tests)
        scratch = Path(tempfile.mkdtemp())
        check_commit.archive(repo_with(files), "HEAD", scratch)
        return scratch

    def test_what_a_passing_suite_leaves_is_counted_and_named(self):
        suite, anchors, ok, left = check_commit.measure(self.tree(("tests/test_l.py", LEAKING_TEST)))
        self.assertTrue(ok, (suite, anchors))
        self.assertEqual(len(left), 1, left)
        self.assertTrue(left[0].startswith("left-behind-"), left)

    def test_the_gate_s_temp_folder_for_the_suite_goes_when_it_is_counted(self):
        scratch, fresh = self.tree(("tests/test_l.py", LEAKING_TEST)), tempfile.mkdtemp()
        with mock.patch.object(tempfile, "tempdir", fresh):
            check_commit.measure(scratch)
        self.assertEqual(os.listdir(fresh), [])

    def test_a_folder_that_is_gone_cannot_be_counted(self):
        self.assertIsNone(check_commit.leftovers(Path(tempfile.mkdtemp()) / "gone"))
        folder = Path(tempfile.mkdtemp())
        (folder / "b").write_text("")
        (folder / ".a").mkdir()
        self.assertEqual(check_commit.leftovers(folder), [".a", "b"])

    def test_anything_left_fails_the_gate_with_one_line_naming_it(self):
        code, said = gate(["spark-suite-x", "tmpab12", "tmpcd34", "tmpef56"])
        self.assertEqual(code, check_commit.EXIT_PROBLEMS)
        self.assertIn("  temp: the suite left 4 entries behind (spark-suite-x, tmpab12, tmpcd34, …) — P172\n", said)
        self.assertIn("1,234 entries", check_commit.temp_line(["x"] * 1234))
        self.assertIn("left 1 entry behind (tmpab12) — P172", check_commit.temp_line(["tmpab12"]))

    def test_nothing_left_passes_and_says_nothing(self):
        code, said = gate([])
        self.assertEqual(code, check_commit.EXIT_OK)
        self.assertNotIn("temp:", said)

    def test_a_count_that_could_not_be_taken_is_could_not_run_never_ok(self):
        code, said = gate(None)
        self.assertEqual(code, check_commit.EXIT_COULD_NOT_RUN)
        self.assertIn("temp: what the suite left behind could not be counted", said)
        self.assertEqual(gate(None, ok=False)[0], check_commit.EXIT_PROBLEMS, "a problem found outranks a look not taken")


class TheGateRemovesItsOwnArchiveTest(unittest.TestCase):
    """P172: the gate's archive of the commit, 6.2 MB, stayed in the temp folder after every push."""

    def test_the_archive_goes_when_the_gate_ends(self):
        fresh = tempfile.mkdtemp()
        with mock.patch.object(tempfile, "tempdir", fresh):
            gate([])
        self.assertEqual(os.listdir(fresh), [])

    def test_the_archive_goes_when_the_commit_could_not_be_archived(self):
        fresh = tempfile.mkdtemp()
        with mock.patch.object(tempfile, "tempdir", fresh):
            self.assertEqual(check_commit.main(["no-such-commit-xyz"]), check_commit.EXIT_COULD_NOT_RUN)
        self.assertEqual(os.listdir(fresh), [])

    def test_the_cleanup_never_reaches_the_node_modules_it_lent(self):
        # The archive holds a link to this checkout's installed dependencies; removing the archive removes the link only.
        checkout = Path(tempfile.mkdtemp())
        installed = checkout / "tools" / "circuit-to-wokwi" / "node_modules"
        installed.mkdir(parents=True)
        (installed / "kept").write_text("the checkout's own\n")

        def archived(root, commit, into):
            (into / "tools" / "circuit-to-wokwi").mkdir(parents=True)

        def measured(tree):
            check_commit.lend_node_modules(tree)
            self.assertTrue((tree / "tools" / "circuit-to-wokwi" / "node_modules").is_symlink())
            return "OK", "anchors ok", True, []

        with mock.patch.object(check_commit, "ROOT", checkout), \
                mock.patch.object(check_commit, "archive", side_effect=archived), \
                mock.patch.object(check_commit, "measure", side_effect=measured), \
                mock.patch.object(check_commit, "size_line", return_value="size"), \
                mock.patch.dict(sys.modules, {"check_backlog": mock.Mock(main=mock.Mock(return_value=0))}), \
                contextlib.redirect_stdout(io.StringIO()):
            check_commit.main(["HEAD"])
        self.assertEqual((installed / "kept").read_text(), "the checkout's own\n")


if __name__ == "__main__":
    unittest.main()
