"""
Proof that `/spark:init` writes spark's section of a project's `.gitignore`, with or without a repository (P1150, P1156):
the link to the person's rules, the flash images and the run logs never reach git by `git add -A`; a `.gitignore` of the
person's keeps its lines; a `.gitignore` that git tracks is left alone and the lines are named; a file git already
tracks that the section covers is said, never untracked by spark.

    python3 -m unittest tests.test_ignore_list
"""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit
from test_project_commit import Isolated, a_repository, git  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from spark.build import ai_files, ignore_list  # noqa: E402

#: The markers and lines, spelled out: a person's file keeps them across spark versions.
BEGIN, END = "# spark:begin", "# spark:end"
LINES = ["CLAUDE.local.md", "sim/*.bin", "sim/runs/"]


def put(root, name, text="x"):
    (root / name).parent.mkdir(parents=True, exist_ok=True)
    (root / name).write_text(text)


class IgnoreListCase(Isolated):
    def setUp(self):
        super().setUp()
        self.project = Path(tempfile.mkdtemp())
        self.store = Path(tempfile.mkdtemp())
        (self.store / "rules.md").write_text("# my rules\n")
        patcher = mock.patch.dict(os.environ, {"SPARK_HOME": str(self.store)})
        patcher.start()
        self.addCleanup(patcher.stop)

    def write(self, project=None):
        return ignore_list.IgnoreList(project or self.project).write()

    def gitignore(self, project=None):
        return ((project or self.project) / ".gitignore").read_bytes().decode()


class TheWriteTest(IgnoreListCase):
    def test_no_repository_gives_the_section_and_a_second_run_says_already(self):
        did, notes = self.write()
        self.assertTrue(did)
        self.assertEqual(notes, ["wrote .gitignore with spark's section"])
        text = self.gitignore()
        self.assertIn(BEGIN, text)
        self.assertIn(END, text)
        for line in LINES:
            self.assertIn(line + "\n", text.splitlines(True))
        did, notes = self.write()
        self.assertFalse(did)
        self.assertEqual(notes, [".gitignore already has spark's section"])

    def test_a_persons_gitignore_keeps_its_lines_with_lf_and_crlf(self):
        for newline in ("\n", "\r\n"):
            with self.subTest(newline=newline):
                project = Path(tempfile.mkdtemp())
                mine = "node_modules/%s*.tmp%s" % (newline, newline)
                (project / ".gitignore").write_bytes(mine.encode())
                did, notes = self.write(project)
                self.assertTrue(did)
                self.assertEqual(notes, ["added spark's section to the end of your .gitignore"])
                self.assertTrue(self.gitignore(project).startswith(mine + "\n" + BEGIN), repr(self.gitignore(project)))

    def test_an_old_section_is_rewritten_and_the_persons_lines_around_it_stay(self):
        (self.project / ".gitignore").write_text("top\n%s. an old spark\nold-line\n%s\nbottom\n" % (BEGIN, END))
        did, notes = self.write()
        self.assertEqual((did, notes), (True, ["rewrote spark's section of .gitignore"]))
        text = self.gitignore()
        self.assertTrue(text.startswith("top\n" + BEGIN), text)
        self.assertTrue(text.endswith(END + "\nbottom\n"), text)
        self.assertNotIn("old-line", text)
        self.assertIn("sim/runs/", text)

    def test_a_link_a_folder_and_a_file_that_is_not_utf8_are_left_alone_and_said(self):
        link = Path(tempfile.mkdtemp())
        (link / "elsewhere").write_text("x\n")
        (link / ".gitignore").symlink_to(link / "elsewhere")
        folder = Path(tempfile.mkdtemp())
        (folder / ".gitignore").mkdir()
        binary = Path(tempfile.mkdtemp())
        (binary / ".gitignore").write_bytes(b"\xff\xfe\x00")
        for project in (link, folder, binary):
            with self.subTest(project=project):
                before = os.listdir(project), (project / ".gitignore").is_symlink()
                did, notes = self.write(project)
                self.assertFalse(did)
                self.assertEqual(len([n for n in notes if ".gitignore" in n and "left alone" in n]), 1, notes)
                self.assertEqual((os.listdir(project), (project / ".gitignore").is_symlink()), before)
        self.assertEqual((link / "elsewhere").read_text(), "x\n")
        self.assertEqual((binary / ".gitignore").read_bytes(), b"\xff\xfe\x00")

    def test_a_begin_marker_with_no_end_is_left_alone_and_said(self):
        (self.project / ".gitignore").write_text(BEGIN + "\nhalf\n")
        did, notes = self.write()
        self.assertFalse(did)
        self.assertIn("no end marker", notes[0])
        self.assertEqual(self.gitignore(), BEGIN + "\nhalf\n")


class ATrackedGitignoreTest(IgnoreListCase):
    def test_a_tracked_gitignore_stays_byte_identical_and_the_lines_are_named(self):
        root, _ = a_repository()
        (root / ".gitignore").write_bytes(b"mine\r\nlines\r\n")
        git(root, "add", ".gitignore")
        put(root, "AGENTS.md")  # an untracked file does not matter
        did, notes = self.write(root)
        self.assertFalse(did)
        self.assertEqual((root / ".gitignore").read_bytes(), b"mine\r\nlines\r\n")
        self.assertEqual(notes, ["git tracks your .gitignore, so spark leaves it alone: add spark's section, or these "
                                 "lines: CLAUDE.local.md, sim/*.bin, sim/runs/"])

    def test_the_exclude_file_still_keeps_the_link_out_when_the_gitignore_is_left_alone(self):
        root, _ = a_repository()
        (root / ".gitignore").write_text("mine\n")
        git(root, "add", ".gitignore")
        ai_files.AiFiles(root, self.store).write()
        self.write(root)
        self.assertIn("CLAUDE.local.md", (root / ".git" / "info" / "exclude").read_text().splitlines())
        self.assertEqual((root / ".gitignore").read_text(), "mine\n")

    def test_an_untracked_gitignore_in_a_repository_is_written(self):
        root, _ = a_repository()
        (root / ".gitignore").write_text("mine\n")
        did, notes = self.write(root)
        self.assertTrue(did)
        self.assertIn(BEGIN, self.gitignore(root))

    def test_no_git_on_the_path_counts_as_untracked_and_the_file_is_written(self):
        with mock.patch.dict(os.environ, {"PATH": str(Path(tempfile.mkdtemp()))}):
            did, _ = self.write()
        self.assertTrue(did)


class AlreadyTrackedTest(IgnoreListCase):
    def test_the_files_git_tracks_that_the_section_covers_are_named_and_never_untracked(self):
        root, _ = a_repository()
        for name in ("CLAUDE.local.md", "sim/runs/a.log", "sim/x/y.bin", "keep.txt"):
            put(root, name)
        git(root, "add", "-A")
        did, notes = self.write(root)
        self.assertTrue(did)
        said = [note for note in notes if "already tracks" in note]
        self.assertEqual(len(said), 1, notes)
        self.assertIn("git already tracks 2 file(s) that spark's section covers: CLAUDE.local.md, sim/runs/a.log.", said[0])
        self.assertIn("`git rm --cached <file>` stops git tracking a file and keeps your copy", said[0])
        self.assertIn("Earlier commits still hold it, so change a password that was in one", said[0])
        self.assertNotIn("y.bin", said[0])
        self.assertEqual(git(root, "ls-files").splitlines(), ["CLAUDE.local.md", "keep.txt", "sim/runs/a.log", "sim/x/y.bin"])
        self.assertEqual(git(root, "diff", "--cached", "--name-only").splitlines(), git(root, "ls-files").splitlines())

    def test_a_file_that_is_tracked_byte_identical_is_still_named(self):
        root, _ = a_repository()
        put(root, "sim/runs/a.log", "same")
        git(root, "add", "-A")
        git(root, "commit", "-q", "-m", "x")
        self.assertEqual(ignore_list.IgnoreList(root).already_tracked(), ["sim/runs/a.log"])

    def test_already_tracked_is_empty_outside_a_repository(self):
        self.assertEqual(ignore_list.IgnoreList(self.project).already_tracked(), [])

    def test_the_note_comes_after_a_left_alone_gitignore_too(self):
        root, _ = a_repository()
        put(root, ".gitignore", "mine\n")
        put(root, "sim/runs/a.log")
        git(root, "add", "-A")
        _, notes = self.write(root)
        self.assertEqual(len(notes), 2, notes)
        self.assertIn("git tracks your .gitignore", notes[0])
        self.assertIn("already tracks 1 file(s)", notes[1])

    def test_the_git_it_asks_is_handed_in(self):
        class Fake:
            def tracks(self, name):
                return None

            def tracked_files(self, patterns):
                return ["sim/runs/z.log"]
        did, notes = ignore_list.IgnoreList(self.project, Fake()).write()
        self.assertTrue(did)
        self.assertIn("already tracks 1 file(s)", notes[-1])


class WhereGitLooksTest(IgnoreListCase):
    def test_a_project_in_a_subfolder_of_a_repository_ignores_its_own_files(self):
        root, _ = a_repository()
        project = root / "boards" / "clock"
        project.mkdir(parents=True)
        self.write(project)
        for name in ("sim/runs/x.log", "sim/micropython-esp32s3.bin", "sim/flash-with-firmware.bin"):
            put(project, name)
        put(project, "sim/x/y.bin")
        named = git(project, "check-ignore", "sim/runs/x.log", "sim/micropython-esp32s3.bin").splitlines()
        self.assertEqual(named, ["sim/runs/x.log", "sim/micropython-esp32s3.bin"])
        self.assertEqual(git(project, "check-ignore", "sim/x/y.bin", check=False), "")

    def test_the_cards_proof_init_then_git_add_keeps_the_three_kinds_out(self):
        import contextlib
        import io
        import init_project
        root = Path(tempfile.mkdtemp())
        with contextlib.redirect_stdout(io.StringIO()):
            init_project.main(["--project", str(root)])
        for name in ("sim/flash-with-firmware.bin", "sim/runs/a.log"):
            put(root, name)
        git(root, "init", "-q")
        git(root, "add", "-A")
        named = git(root, "check-ignore", "CLAUDE.local.md", "sim/flash-with-firmware.bin", "sim/runs/a.log").splitlines()
        self.assertEqual(named, ["CLAUDE.local.md", "sim/flash-with-firmware.bin", "sim/runs/a.log"])
        tracked = git(root, "ls-files").splitlines()
        for name in named:
            self.assertNotIn(name, tracked)
        self.assertIn(".gitignore", tracked)


if __name__ == "__main__":
    unittest.main()
