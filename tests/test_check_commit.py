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

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

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
    OUTCOMES = (ROOT / "scripts" / "spark" / "core" / "outcomes.py").read_text()

    def test_a_tree_whose_suite_passes_is_ok(self):
        root = repo_with({"scripts/spark/core/outcomes.py": self.OUTCOMES,
                          "m.py": "def add(a, b):\n    return a + b\n",
                          "tests/test_m.py": "import sys, unittest\nsys.path.insert(0, '.')\nimport m\n"
                                             "class T(unittest.TestCase):\n    def test_add(self): self.assertEqual(m.add(1, 2), 3)\n"})
        scratch = Path(tempfile.mkdtemp())
        check_commit.archive(root, "HEAD", scratch)
        suite, ok, left, _ = check_commit.measure(scratch)
        self.assertTrue(ok, suite)
        self.assertIn("OK", suite)
        self.assertEqual(left, [], "a suite that leaves nothing behind leaves nothing to name")

    def test_a_file_left_uncommitted_makes_the_committed_tree_fail(self):
        # The C3 shape: the working tree has the module, the commit does not.
        root = repo_with({"scripts/spark/core/outcomes.py": self.OUTCOMES,
                          "m.py": "import helper\ndef add(a, b):\n    return helper.plus(a, b)\n",
                          "tests/test_m.py": "import sys, unittest\nsys.path.insert(0, '.')\nimport m\n"
                                             "class T(unittest.TestCase):\n    def test_add(self): self.assertEqual(m.add(1, 2), 3)\n"})
        (root / "helper.py").write_text("def plus(a, b):\n    return a + b\n")   # never committed
        working = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"],
                                 cwd=str(root), capture_output=True, text=True)
        self.assertEqual(working.returncode, 0, "the working tree passes — that is the trap")
        scratch = Path(tempfile.mkdtemp())
        check_commit.archive(root, "HEAD", scratch)
        suite, ok, left, _ = check_commit.measure(scratch)
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

    def test_the_size_counts_a_package_under_scripts_but_not_the_micropython_stand_in(self):
        root = repo_with({"scripts/a.py": "x = 1\n", "scripts/spark/core/b.py": "y = 2\nz = 3\n",
                          "scripts/spark/firmware/stand_in/machine.py": "q = 1\n"})
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
        root = repo_with({"scripts/spark/core/outcomes.py": TheCommittedTreeIsMeasuredTest.OUTCOMES,
                          "m.py": "def add(a, b):\n    return a + b\n",
                          "tests/test_m.py": "import sys, unittest\nsys.path.insert(0, '.')\nimport m\n"
                                             "class T(unittest.TestCase):\n    def test_add(self): self.assertEqual(m.add(1, 2), 3)\n",
                          "tests/test_env.py": "import os, unittest\nclass E(unittest.TestCase):\n"
                                               "    def test_no_git_variable(self):\n"
                                               "        self.assertEqual([k for k in os.environ if k.startswith('GIT_')], [])\n"})
        scratch = Path(tempfile.mkdtemp())
        check_commit.archive(root, "HEAD", scratch)
        with mock.patch.dict(os.environ, {"GIT_DIR": str(root / ".git"), "GIT_INDEX_FILE": str(root / ".git" / "index")}):
            suite, ok, left, _ = check_commit.measure(scratch)
        self.assertTrue(ok, suite)

    def test_a_throwaway_repository_leaves_the_hook_s_repository_alone(self):
        victim = repo_with({"kept.txt": "the branch being pushed\n"})
        before = head_and_config(victim)
        with mock.patch.dict(os.environ, {"GIT_DIR": str(victim / ".git")}):
            repo_with({"junk.txt": "a test's file\n"})
        self.assertEqual(head_and_config(victim), before)


class TheGateEnforcesTheBoardTest(unittest.TestCase):
    """P102a: a board that breaks its limits fails the gate even when the suite is green."""

    def test_a_board_problem_fails_the_gate(self):
        board = mock.Mock(main=mock.Mock(return_value=1))
        with mock.patch.object(check_commit, "archive"), \
                mock.patch.object(check_commit, "measure", return_value=("OK", True, [], [])), \
                mock.patch.object(check_commit, "size_line", return_value="size"), \
                mock.patch.dict(sys.modules, {"check_backlog": board}), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(check_commit.main(["HEAD"]), check_commit.EXIT_PROBLEMS)


class TheGateNeedsNodeForThePageScriptTest(unittest.TestCase):
    """P829 PR 3: test_flow_script skips without node, and a skip is no pass, so a story run that holds it stops."""

    @staticmethod
    def story(*modules):
        return check_commit.story_tests.StoryTests(modules, check_commit.story_tests.CHOSEN, None, 10)

    def test_without_node_a_story_run_that_holds_the_page_script_could_not_run(self):
        self.assertEqual(check_commit.node_refusal(self.story("test_flow_page", "test_flow_script"), lambda _name: None),
                         "could not run: the story run holds test_flow_script, which runs the page script with node, "
                         "and node is not installed")

    def test_with_node_or_without_the_page_script_the_story_runs(self):
        self.assertIsNone(check_commit.node_refusal(self.story("test_flow_script"), lambda _name: "/usr/bin/node"))
        self.assertIsNone(check_commit.node_refusal(self.story("test_flow_page"), lambda _name: None))
        self.assertIsNone(check_commit.node_refusal(None, lambda _name: None), "the full run")


#: The page script's four files (P1061), each from the root, and what a tree holds of them in the tests below.
FLOW = "scripts/spark/flow/"
PAGE_TS = {FLOW + "page_script.ts": "const a: number = 1;\n", FLOW + "page_script.js": "const a = 1;\n"}


def tsc_7_0(writes="const a = 1;\n", exit_code=0, said=""):
    """A swapped `subprocess.run` for tsc 7.0.2: `--version` says so, and a compile writes `writes` into its --outDir."""
    def run(argv, **_kwargs):
        if "--version" in argv:
            return subprocess.CompletedProcess(argv, 0, "Version 7.0.2\n", "")
        if writes is not None:
            (Path(argv[argv.index("--outDir") + 1]) / "page_script.js").write_text(writes)
        return subprocess.CompletedProcess(argv, exit_code, said, "")
    return run


def tsc_on_path(_name):
    return "/usr/local/bin/tsc"


class TheGateCompilesThePageScriptTest(unittest.TestCase):
    """
    P1061: page_script.ts is the source, and the committed page_script.js must be tsc 7.0's compiled output of it. A
    missing tsc, or another version, is a refusal (could not run); a compiled output that differs, or a tsc that says
    errors, is a drift (problems). Every tool is swapped: no real tsc runs.
    """

    @staticmethod
    def tree(files):
        tree = Path(tempfile.mkdtemp())
        for name, text in files.items():
            (tree / name).parent.mkdir(parents=True, exist_ok=True)
            (tree / name).write_text(text)
        return tree

    def test_a_missing_tsc_refuses_and_names_the_install(self):
        self.assertEqual(check_commit.tsc_refusal(lambda _name: None, tsc_7_0()),
                         "could not run: the gate compiles the page script's TypeScript with tsc 7.0 (P1061), and no tsc "
                         "is on this PATH; install it for the node this PATH finds: npm install -g typescript@7.0")

    def test_another_version_refuses_and_names_the_one_found(self):
        for found in ("Version 6.0.3", "Version 7.1.0", ""):
            def run(argv, **_kwargs):
                return subprocess.CompletedProcess(argv, 0, found + "\n", "")
            self.assertEqual(check_commit.tsc_refusal(tsc_on_path, run),
                             "could not run: the gate compiles the page script's TypeScript with tsc 7.0 (P1061), and the "
                             "tsc on this PATH says %r; install 7.0 for the node this PATH finds: npm install -g "
                             "typescript@7.0" % found, found)

    def test_tsc_7_0_with_any_patch_is_no_refusal(self):
        self.assertIsNone(check_commit.tsc_refusal(tsc_on_path, tsc_7_0()))

        def run(argv, **_kwargs):
            return subprocess.CompletedProcess(argv, 0, "Version 7.0.9\n", "")
        self.assertIsNone(check_commit.tsc_refusal(tsc_on_path, run))

    def test_the_same_bytes_are_no_drift(self):
        self.assertIsNone(check_commit.script_drift(self.tree(PAGE_TS), tsc_7_0()))

    def test_other_bytes_are_a_drift_that_names_the_fix(self):
        self.assertEqual(check_commit.script_drift(self.tree(PAGE_TS), tsc_7_0(writes="const a = 2;\n")),
                         "page script: the committed scripts/spark/flow/page_script.js is not tsc's compiled output of "
                         "page_script.ts (P1061); fix it with tsc -p scripts/spark/flow, then commit both files")

    def test_a_tsc_that_says_errors_is_a_drift_with_its_first_error_line(self):
        for exit_code in (1, 2):  # tsc's own exit 1 or 2 is a drift, never a refusal (C14)
            said = "page_script.ts(3,5): error TS2339: Property 'x' does not exist on type 'Y'.\nmore\n"
            self.assertEqual(check_commit.script_drift(self.tree(PAGE_TS), tsc_7_0(writes=None, exit_code=exit_code, said=said)),
                             "page script: tsc -p scripts/spark/flow says page_script.ts(3,5): error TS2339: Property 'x' "
                             "does not exist on type 'Y'. (P1061); fix the .ts, then run it again and commit both files",
                             exit_code)

    def test_a_change_of_one_of_the_four_files_a_doubt_or_the_full_run_needs_tsc(self):
        tree = self.tree(PAGE_TS)
        self.assertTrue(check_commit.needs_tsc(tree, ["scripts/spark/flow/tsconfig.json"]))
        self.assertTrue(check_commit.needs_tsc(tree, ["docs/x.md", "scripts/spark/flow/artifact_runtime.d.ts"]))
        self.assertTrue(check_commit.needs_tsc(tree, None), "git could not tell what changed: a doubt runs more")
        self.assertTrue(check_commit.needs_tsc(tree, [], full=True))
        self.assertFalse(check_commit.needs_tsc(tree, ["scripts/spark/flow/flow_page.py"]))
        self.assertFalse(check_commit.needs_tsc(tree, []))

    def test_a_tree_without_the_page_script_s_source_needs_no_tsc(self):
        # a commit before P1061, or a test's tree: there is nothing to compile
        tree = self.tree({FLOW + "page_script.js": "const a = 1;\n"})
        self.assertFalse(check_commit.needs_tsc(tree, None))
        self.assertFalse(check_commit.needs_tsc(tree, [], full=True))

    def full_gate(self, which, run):
        said = io.StringIO()
        with contextlib.redirect_stdout(said):
            code = check_commit.gate(repo_with(PAGE_TS), "HEAD", Path(tempfile.mkdtemp()), full=True, which=which, run=run)
        return code, said.getvalue()

    def test_the_full_run_refuses_without_tsc_and_runs_no_suite(self):
        code, said = self.full_gate(lambda _name: None, tsc_7_0())
        self.assertEqual(code, check_commit.EXIT_COULD_NOT_RUN, said)
        self.assertIn("and no tsc is on this PATH", said)
        self.assertNotIn("as committed", said, "a refusal runs no suite")

    def test_the_full_run_compiles_the_script_and_a_drift_runs_no_suite(self):
        code, said = self.full_gate(tsc_on_path, tsc_7_0(writes="const a = 2;\n"))
        self.assertEqual(code, check_commit.EXIT_PROBLEMS, said)
        self.assertIn("page script: the committed scripts/spark/flow/page_script.js is not tsc's compiled output", said)
        self.assertNotIn("as committed", said, "a drift runs no suite")


#: A test that passes and leaves a folder in the temp folder behind it — the shape of 1,888 of the 2,291 entries.
LEAKING_TEST = ("import tempfile, unittest\nclass L(unittest.TestCase):\n"
                "    def test_leaves_a_folder(self): tempfile.mkdtemp(prefix='left-behind-')\n")


def a_good_board():
    """The gate's board check, stubbed to say the board is fine."""
    return mock.patch.dict(sys.modules, {"check_backlog": mock.Mock(main=mock.Mock(return_value=0))})


def gate(left, ok=True, board=0):
    """`main` with everything but the temp verdict stubbed: (exit code, what it printed)."""
    said = io.StringIO()
    with mock.patch.object(check_commit, "archive"), \
            mock.patch.object(check_commit, "measure", return_value=("Ran 1 test / OK", ok, left, [])), \
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
        files = {"scripts/spark/core/outcomes.py": TheCommittedTreeIsMeasuredTest.OUTCOMES,
                 "m.py": "def add(a, b):\n    return a + b\n",
                 "tests/test_m.py": "import sys, unittest\nsys.path.insert(0, '.')\nimport m\n"
                                    "class T(unittest.TestCase):\n    def test_add(self): self.assertEqual(m.add(1, 2), 3)\n"}
        files.update(tests)
        scratch = Path(tempfile.mkdtemp())
        check_commit.archive(repo_with(files), "HEAD", scratch)
        return scratch

    def test_what_a_passing_suite_leaves_is_counted_and_named(self):
        suite, ok, left, _ = check_commit.measure(self.tree(("tests/test_l.py", LEAKING_TEST)))
        self.assertTrue(ok, suite)
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

        def measured(tree, full=False, story=None):
            check_commit.lend_node_modules(tree)
            self.assertTrue((tree / "tools" / "circuit-to-wokwi" / "node_modules").is_symlink())
            return "OK", True, [], []

        with mock.patch.object(check_commit, "ROOT", checkout), \
                mock.patch.object(check_commit, "archive", side_effect=archived), \
                mock.patch.object(check_commit, "measure", side_effect=measured), \
                mock.patch.object(check_commit, "size_line", return_value="size"), \
                a_good_board(), \
                contextlib.redirect_stdout(io.StringIO()):
            check_commit.main(["HEAD"])
        self.assertEqual((installed / "kept").read_text(), "the checkout's own\n")


class TheStoryRunTest(unittest.TestCase):
    """P714: the gate runs the tests of what the branch changed, and says so; a doubt is the quick run, and says why."""

    MAIN = {"a.py": "def one(): return 1\n", "b.py": "def two(): return 2\n",
            "tests/test_a.py": "import unittest\nimport a\nclass T(unittest.TestCase):\n    def test_one(self): self.assertEqual(a.one(), 1)\n",
            "tests/test_b.py": "import unittest\nimport b\nclass T(unittest.TestCase):\n    def test_two(self): self.assertEqual(b.two(), 22)\n"}

    def branch_changes(self, files, *, origin=True):
        root = repo_with(self.MAIN)
        if origin:
            subprocess.run(["git", "update-ref", "refs/remotes/origin/main", "HEAD"], cwd=str(root), check=True, env=own_env())
        for name, text in files.items():
            (root / name).parent.mkdir(parents=True, exist_ok=True)
            (root / name).write_text(text)
        for command in (["git", "add", "-A"], ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "two"]):
            subprocess.run(command, cwd=str(root), check=True, capture_output=True, env=own_env())
        said = io.StringIO()
        with a_good_board(), contextlib.redirect_stdout(said):
            code = check_commit.gate(root, "HEAD", Path(tempfile.mkdtemp()))
        return code, said.getvalue()

    def test_a_failing_test_of_a_file_the_branch_left_alone_does_not_run(self):
        code, said = self.branch_changes({"a.py": "def one(): return 1  # a comment\n"})
        self.assertEqual(code, check_commit.EXIT_OK, said)
        self.assertRegex(said, r"story run: Ran 1 tests in [\d.]+ s \(0 slow tests skipped; 1 of 2 test files; "
                               r"the full run is check_commit.py --full\) / OK\n")
        self.assertRegex(said, r"story run: the seconds above")
        self.assertNotIn("FAIL:", said, "a green push names no red test")

    def test_a_failing_test_of_the_changed_file_fails_the_gate_and_the_line_says_so(self):
        code, said = self.branch_changes({"a.py": "def one(): return 11\n"})
        self.assertEqual(code, check_commit.EXIT_PROBLEMS, said)
        self.assertRegex(said, r"story run: Ran 1 tests .* / FAILED \(failures=1\)\n")
        self.assertRegex(said, r"/ FAILED \(failures=1\)\n    FAIL: test_one \([\w.]+\)\n    AssertionError: 11 != 1\n")

    def test_no_origin_main_is_the_quick_run_and_says_why(self):
        code, said = self.branch_changes({"a.py": "def one(): return 1  # a comment\n"}, origin=False)
        self.assertEqual(code, check_commit.EXIT_PROBLEMS, said)  # the quick run reaches tests/test_b.py and its failure
        self.assertIn("quick run: Ran 2 of 2 tests", said)
        self.assertIn("  no story run: the changes since origin/main could not be read\n", said)

    def test_a_file_no_test_names_is_the_quick_run_and_the_line_names_it(self):
        code, said = self.branch_changes({"tools/new_thing.py": "x = 1\n"})
        self.assertEqual(code, check_commit.EXIT_PROBLEMS, said)
        self.assertIn("  no story run: no test names tools/new_thing.py\n", said)

    def test_a_selected_test_that_cannot_compile_fails_the_gate_and_the_line_says_why(self):
        code, said = self.branch_changes({"tests/test_a.py": "def broken(:\n"})
        self.assertEqual(code, check_commit.EXIT_PROBLEMS, said)
        self.assertIn("SyntaxError", said)

    def test_a_deleted_file_and_both_names_of_a_renamed_file_count_as_changed(self):
        root = repo_with(self.MAIN)
        subprocess.run(["git", "update-ref", "refs/remotes/origin/main", "HEAD"], cwd=str(root), check=True, env=own_env())
        for command in (["git", "rm", "-q", "b.py"], ["git", "mv", "a.py", "c.py"],
                        ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "two"]):
            subprocess.run(command, cwd=str(root), check=True, capture_output=True, env=own_env())
        self.assertEqual(check_commit.changed_files(root, "HEAD"), ["a.py", "b.py", "c.py"])

    def test_the_story_reads_the_imports_of_the_archived_scripts(self):
        # P1017: test_x imports top, top imports low, and only test_names_it names low
        tree = Path(tempfile.mkdtemp())
        for name, text in {"tests/test_x.py": "import spark.a.top\n", "scripts/spark/a/top.py": "from spark.a import low as below\n",
                           "scripts/spark/a/low.py": "", "tests/test_apart.py": "import json\n",
                           "tests/test_names_it.py": "# low\n"}.items():
            (tree / name).parent.mkdir(parents=True, exist_ok=True)
            (tree / name).write_text(text)
        story = check_commit.story_tests_in(tree, ["scripts/spark/a/low.py"])
        self.assertEqual((story.state, story.modules), ("chosen", ("test_names_it", "test_x")), story.why)


if __name__ == "__main__":
    unittest.main()
