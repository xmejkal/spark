"""
P1027 (#1506), slice 2: `records/project_commit.ProjectCommit`, the one code in `scripts/spark/` that runs git. It makes one
commit of one file spark changed in a person's project, so `git revert --no-edit <sha>` takes that change back, and it says
why not when git does not hold the file as it is, on a branch. Every repository here is a scratch one in the suite's temp
folder, with an empty HOME and an empty global config, so no test reads the machine's git identity.

    python3 -m unittest tests.test_project_commit
"""

import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from spark.records.project_commit import NOT_ON_BRANCH, UNCOMMITTED, UNFINISHED, UNHELD, ProjectCommit  # noqa: E402

BRIEF = ".spark/project.json"
OLD, NEW = '{"must": ["a", "b"]}\n', '{"must": ["a"]}\n'


def isolated_env():
    """The environment every test runs in: an empty HOME and XDG_CONFIG_HOME, an empty global config and no system config.
    ProjectCommit drops every GIT_* variable but GIT_CONFIG_GLOBAL and GIT_CONFIG_NOSYSTEM, which only say where git reads
    its config, so these two reach its git too: no machine's identity answers for a test."""
    empty = Path(tempfile.mkdtemp())
    (empty / "gitconfig").write_text("")
    return {"HOME": str(empty), "XDG_CONFIG_HOME": str(empty / "xdg"), "GIT_CONFIG_GLOBAL": str(empty / "gitconfig"),
            "GIT_CONFIG_NOSYSTEM": "1"}


def git(root, *args, check=True, env=None):
    """Run the test's own git in `root`, with no GIT_* variable of the caller's but the isolated config: its stdout."""
    own = {name: value for name, value in os.environ.items() if not name.startswith("GIT_")}
    own.update({"GIT_CONFIG_GLOBAL": os.environ["GIT_CONFIG_GLOBAL"], "GIT_CONFIG_NOSYSTEM": "1"}, **(env or {}))
    done = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, env=own, check=False)
    if check and done.returncode:
        raise AssertionError("git %s: %s" % (" ".join(args), done.stderr))
    return done.stdout.strip()


def a_repository(identity=True):
    """A scratch repository with its own identity, no signing and an empty hooks folder of its own: (root, hooks)."""
    root = Path(tempfile.mkdtemp()) / "project"
    root.mkdir()
    hooks = root.parent / "hooks"
    hooks.mkdir()
    git(root, "init", "-q", "-b", "main")
    for key, value in ((("user.email", "t@t"), ("user.name", "t")) if identity else ()) + (
            ("commit.gpgsign", "false"), ("core.hooksPath", str(hooks))):
        git(root, "config", key, value)
    return root, hooks


def with_brief(root, text=OLD, commit=True):
    """Write the brief in `root` and, with `commit`, commit it on the branch."""
    (root / ".spark").mkdir(exist_ok=True)
    (root / BRIEF).write_text(text)
    if commit:
        git(root, "add", BRIEF)
        git(root, "commit", "-q", "-m", "the brief")
    return root


def a_hook(hooks, body):
    hook = hooks / "pre-commit"
    hook.write_text("#!/bin/sh\n%s\n" % body)
    hook.chmod(0o755)


class Isolated(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch.dict(os.environ, isolated_env())
        patcher.start()
        self.addCleanup(patcher.stop)


class TheCommitTest(Isolated):
    def test_a_clean_tracked_brief_is_committed_alone_and_git_revert_gives_the_old_bytes_back(self):
        root, _ = a_repository()
        with_brief(root)
        (root / "other.txt").write_text("staged before\n")
        git(root, "add", "other.txt")
        committer = ProjectCommit(root)
        self.assertIsNone(committer.held_as_is(BRIEF))
        (root / BRIEF).write_text(NEW)
        sha, said = committer.commit(BRIEF, "spark: must in .spark/project.json")
        self.assertIsNone(said)
        self.assertEqual(git(root, "rev-parse", "--short", "HEAD"), sha)
        self.assertEqual(git(root, "show", "--name-only", "--format=", sha), BRIEF)
        self.assertEqual(git(root, "log", "-1", "--format=%s"), "spark: must in .spark/project.json")
        self.assertEqual(git(root, "diff", "--cached", "--name-only"), "other.txt", "a file staged before stays staged")
        git(root, "commit", "-q", "-m", "the other file")  # a clean index: the way back needs one
        git(root, "revert", "--no-edit", sha)
        self.assertEqual((root / BRIEF).read_text(), OLD)

    def test_a_project_in_a_subfolder_of_the_repository_is_held_and_committed(self):
        root, _ = a_repository()
        project = root / "boards" / "clock"
        project.mkdir(parents=True)
        with_brief(project)
        committer = ProjectCommit(project)
        self.assertIsNone(committer.held_as_is(BRIEF))
        (project / BRIEF).write_text(NEW)
        sha, said = committer.commit(BRIEF, "spark: must in .spark/project.json")
        self.assertEqual((said, git(root, "show", "--name-only", "--format=", sha)), (None, "boards/clock/" + BRIEF))


class WhyNotTest(Isolated):
    def test_no_repository_an_untracked_brief_and_no_commit_are_unheld(self):
        bare = with_brief(Path(tempfile.mkdtemp()), commit=False)
        untracked, _ = a_repository()
        with_brief(untracked, commit=False)
        git(untracked, "commit", "-q", "--allow-empty", "-m", "first")
        unborn, _ = a_repository()
        with_brief(unborn, commit=False)
        git(unborn, "add", BRIEF)
        for root in (bare, untracked, unborn):
            with self.subTest(root=root):
                self.assertEqual(ProjectCommit(root).held_as_is(BRIEF), UNHELD)

    def test_a_detached_head_is_not_on_a_branch(self):
        root, _ = a_repository()
        with_brief(root)
        git(root, "checkout", "-q", "--detach")
        self.assertEqual(ProjectCommit(root).held_as_is(BRIEF), NOT_ON_BRANCH)

    def test_a_stopped_rebase_is_not_on_a_branch(self):
        root, _ = a_repository()
        with_brief(root)
        (root / BRIEF).write_text(NEW)
        git(root, "commit", "-q", "-am", "second")
        git(root, "rebase", "-q", "-i", "HEAD~1", env={"GIT_SEQUENCE_EDITOR": "sed -i.bak -e s/^pick/edit/"})
        self.assertTrue((root / ".git" / "rebase-merge").is_dir(), "the rebase stopped")
        self.assertEqual(ProjectCommit(root).held_as_is(BRIEF), NOT_ON_BRANCH)

    def test_unheld_comes_before_not_on_a_branch_and_not_on_a_branch_before_uncommitted(self):
        root, _ = a_repository()
        with_brief(root)
        git(root, "checkout", "-q", "--detach")
        (root / BRIEF).write_text(NEW)
        self.assertEqual(ProjectCommit(root).held_as_is(BRIEF), NOT_ON_BRANCH)
        git(root, "rm", "-q", "--cached", BRIEF)
        git(root, "commit", "-q", "-m", "untrack the brief")
        self.assertEqual(ProjectCommit(root).held_as_is(BRIEF), UNHELD)

    def test_an_edit_git_does_not_hold_is_uncommitted_staged_or_not_or_hidden(self):
        for how in ("unstaged", "staged", "assume-unchanged", "staged-then-restored"):
            with self.subTest(how=how):
                root, _ = a_repository()
                with_brief(root)
                if how == "assume-unchanged":
                    git(root, "update-index", "--assume-unchanged", BRIEF)
                (root / BRIEF).write_text(NEW)
                if how.startswith("staged"):
                    git(root, "add", BRIEF)
                if how == "staged-then-restored":
                    (root / BRIEF).write_text(OLD)
                self.assertEqual(ProjectCommit(root).held_as_is(BRIEF), UNCOMMITTED)

    def test_with_no_git_on_the_path_it_is_unheld_and_never_raises(self):
        root, _ = a_repository()
        with_brief(root)
        with mock.patch.dict(os.environ, {"PATH": tempfile.mkdtemp()}):
            committer = ProjectCommit(root)
            self.assertEqual(committer.held_as_is(BRIEF), UNHELD)
            sha, said = committer.commit(BRIEF, "spark: must in .spark/project.json")
        self.assertIsNone(sha)
        self.assertTrue(said)


class ARefusedCommitTest(Isolated):
    def test_a_hook_that_refuses_gives_its_output_and_the_file_stays_written(self):
        root, hooks = a_repository()
        with_brief(root)
        a_hook(hooks, "echo 'the hook says no' >&2\nexit 1")
        head = git(root, "rev-parse", "HEAD")
        (root / BRIEF).write_text(NEW)
        self.assertEqual(ProjectCommit(root).commit(BRIEF, "spark: must"), (None, "the hook says no"))
        self.assertEqual((git(root, "rev-parse", "HEAD"), (root / BRIEF).read_text()), (head, NEW))

    def test_a_hook_that_refuses_silently_gives_the_exit_code(self):
        root, hooks = a_repository()
        with_brief(root)
        a_hook(hooks, "exit 3")
        (root / BRIEF).write_text(NEW)
        self.assertEqual(ProjectCommit(root).commit(BRIEF, "spark: must"), (None, "git exited with 1"))

    def test_a_hook_that_does_not_finish_is_stopped_and_leaves_no_lock(self):
        root, hooks = a_repository()
        with_brief(root)
        a_hook(hooks, "sleep 10")
        (root / BRIEF).write_text(NEW)
        began = time.monotonic()
        said = ProjectCommit(root, timeout=1).commit(BRIEF, "spark: must")
        self.assertEqual(said, (None, UNFINISHED))
        self.assertLess(time.monotonic() - began, 5)
        self.assertFalse((root / ".git" / "index.lock").exists(), "a killed git leaves index.lock behind")

    def test_a_hook_that_ignores_sigterm_ends_in_bounded_time_and_leaves_no_lock(self):
        root, hooks = a_repository()
        with_brief(root)
        a_hook(hooks, "trap '' TERM\nsleep 30")
        (root / BRIEF).write_text(NEW)
        began = time.monotonic()
        said = ProjectCommit(root, timeout=1).commit(BRIEF, "spark: must")
        self.assertEqual(said, (None, UNFINISHED))
        self.assertLess(time.monotonic() - began, 10)
        self.assertFalse((root / ".git" / "index.lock").exists(), "a killed git leaves index.lock behind")

    def test_a_slow_post_commit_hook_still_reports_the_commit_it_made(self):
        root, hooks = a_repository()
        with_brief(root)
        hook = hooks / "post-commit"
        hook.write_text("#!/bin/sh\nsleep 10\n")
        hook.chmod(0o755)
        (root / BRIEF).write_text(NEW)
        began = time.monotonic()
        sha, said = ProjectCommit(root, timeout=1).commit(BRIEF, "spark: must")
        self.assertLess(time.monotonic() - began, 10)
        self.assertEqual((sha, said), (git(root, "rev-parse", "--short", "HEAD"), None))
        self.assertEqual(git(root, "show", "--name-only", "--format=", sha), BRIEF)

    def test_a_refusal_with_no_new_commit_is_no_commit_even_when_the_last_commit_holds_the_brief_alone(self):
        root, hooks = a_repository()
        with_brief(root)
        (root / BRIEF).write_text(NEW)
        git(root, "commit", "-q", "-am", "the brief again")  # HEAD holds the brief alone, but it was there before
        (root / BRIEF).write_text(OLD)
        a_hook(hooks, "exit 1")
        self.assertEqual(ProjectCommit(root).commit(BRIEF, "spark: must"), (None, "git exited with 1"))

    def test_no_identity_is_refused_and_never_guessed(self):
        root, _ = a_repository(identity=False)
        with_brief(root, commit=False)
        git(root, "add", BRIEF)
        git(root, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "the brief")
        (root / BRIEF).write_text(NEW)
        head = git(root, "rev-parse", "HEAD")
        with mock.patch.dict(os.environ, {"EMAIL": "t@t"}):  # git would take it as the address without useConfigOnly
            sha, said = ProjectCommit(root).commit(BRIEF, "spark: must")
        self.assertEqual((sha, said), (None, "Author identity unknown"))
        self.assertEqual(git(root, "rev-parse", "HEAD"), head)


class TheConfigItReadsTest(Isolated):
    def test_the_global_config_the_caller_names_reaches_git(self):
        root, _ = a_repository(identity=False)
        with_brief(root, commit=False)
        git(root, "add", BRIEF)
        git(root, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "the brief")
        Path(os.environ["GIT_CONFIG_GLOBAL"]).write_text("[user]\n\temail = t@t\n\tname = t\n")
        (root / BRIEF).write_text(NEW)
        sha, said = ProjectCommit(root).commit(BRIEF, "spark: must")
        self.assertEqual((said, git(root, "log", "-1", "--format=%ae")), (None, "t@t"))


class TheHooksGitDirTest(Isolated):
    def test_a_git_dir_from_a_hook_never_steers_the_commit_to_another_repository(self):
        root, _ = a_repository()
        with_brief(root)
        other, _ = a_repository()
        with_brief(other)
        before = git(other, "rev-parse", "HEAD")
        with mock.patch.dict(os.environ, {"GIT_DIR": str(other / ".git")}):
            committer = ProjectCommit(root)
            self.assertIsNone(committer.held_as_is(BRIEF))
            (root / BRIEF).write_text(NEW)
            sha, _ = committer.commit(BRIEF, "spark: must")
        self.assertEqual(git(root, "rev-parse", "--short", "HEAD"), sha)
        self.assertEqual(git(other, "rev-parse", "HEAD"), before)


if __name__ == "__main__":
    unittest.main()
