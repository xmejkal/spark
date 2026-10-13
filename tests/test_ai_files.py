"""
Proof that `/spark:init` gives a project the files each AI tool reads (P216 step 6), and leaves the person's own
files alone.

Three files: spark's section of `AGENTS.md`, between two marker lines; a `CLAUDE.md` that imports `@AGENTS.md`,
because a `CLAUDE.local.md` stops Claude Code from reading `AGENTS.md` on its own; and `CLAUDE.local.md`, a link to the
person's rules in their store, kept out of git.

    python3 -m unittest discover -s tests -t tests
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  P172: this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import ai_files  # noqa: E402


class AiFilesTest(unittest.TestCase):
    def setUp(self):
        self.project = Path(tempfile.mkdtemp())
        (self.project / ".git" / "info").mkdir(parents=True)
        self.store = Path(tempfile.mkdtemp())
        self.rules = self.store / "rules.md"
        self.rules.write_text("# my rules\n")

    def run_it(self):
        return ai_files.AiFiles(self.project, self.store).write()

    def text(self, name):
        return (self.project / name).read_text()

    def test_a_new_project_gets_all_three(self):
        did, notes = self.run_it()
        self.assertTrue(did)
        self.assertIn(ai_files.BEGIN, self.text("AGENTS.md"))
        self.assertIn(ai_files.END, self.text("AGENTS.md"))
        self.assertEqual(self.text("CLAUDE.md"), "@AGENTS.md\n")
        link = self.project / "CLAUDE.local.md"
        self.assertTrue(link.is_symlink())
        self.assertEqual(link.resolve(), self.rules.resolve())
        self.assertIn("CLAUDE.local.md", (self.project / ".git" / "info" / "exclude").read_text().splitlines())
        self.assertEqual(len(notes), 3)

    def test_a_second_run_changes_nothing(self):
        self.run_it()
        exclude = (self.project / ".git" / "info" / "exclude").read_text()
        did, notes = self.run_it()
        self.assertFalse(did)
        self.assertEqual((self.project / ".git" / "info" / "exclude").read_text(), exclude)
        self.assertTrue(all("already" in note for note in notes), notes)

    def test_the_person_s_agents_md_keeps_its_text(self):
        (self.project / "AGENTS.md").write_text("# my project\n\nmine\n")
        self.run_it()
        text = self.text("AGENTS.md")
        self.assertTrue(text.startswith("# my project\n\nmine\n"))
        self.assertEqual(text.count(ai_files.BEGIN), 1)

    def test_an_old_section_is_replaced_between_the_markers_only(self):
        (self.project / "AGENTS.md").write_text(
            "before\n%s\nold words\n%s\nafter\n" % (ai_files.BEGIN, ai_files.END))
        self.run_it()
        text = self.text("AGENTS.md")
        self.assertNotIn("old words", text)
        self.assertTrue(text.startswith("before\n") and text.endswith("after\n"))
        self.assertIn(ai_files.SECTION.strip(), text)

    def test_a_begin_marker_without_an_end_is_left_alone_and_said(self):
        broken = "%s\nhalf\n" % ai_files.BEGIN
        (self.project / "AGENTS.md").write_text(broken)
        did, notes = self.run_it()
        self.assertEqual(self.text("AGENTS.md"), broken)
        self.assertTrue(any("AGENTS.md" in note and "left alone" in note for note in notes), notes)

    def test_the_person_s_claude_md_is_left_alone_and_the_line_named(self):
        (self.project / "CLAUDE.md").write_text("# mine\n")
        did, notes = self.run_it()
        self.assertEqual(self.text("CLAUDE.md"), "# mine\n")
        self.assertTrue(any("@AGENTS.md" in note and "CLAUDE.md" in note for note in notes), notes)

    def test_a_claude_md_that_imports_agents_md_is_already_here(self):
        (self.project / "CLAUDE.md").write_text("# mine\n@AGENTS.md\n")
        did, notes = self.run_it()
        self.assertEqual(self.text("CLAUDE.md"), "# mine\n@AGENTS.md\n")
        self.assertTrue(any(note.startswith("CLAUDE.md already") for note in notes), notes)

    def test_the_person_s_own_claude_local_md_is_left_alone(self):
        (self.project / "CLAUDE.local.md").write_text("private\n")
        did, notes = self.run_it()
        self.assertFalse((self.project / "CLAUDE.local.md").is_symlink())
        self.assertEqual(self.text("CLAUDE.local.md"), "private\n")
        self.assertTrue(any("CLAUDE.local.md" in note and "left alone" in note for note in notes), notes)

    def test_no_rules_file_means_no_link_and_says_where_to_start_one(self):
        self.rules.unlink()
        did, notes = self.run_it()
        self.assertFalse(os.path.lexists(self.project / "CLAUDE.local.md"))
        self.assertTrue(any(str(self.rules) in note for note in notes), notes)

    def test_outside_git_the_link_is_made_and_nothing_is_excluded(self):
        project = Path(tempfile.mkdtemp())
        did, notes = ai_files.AiFiles(project, self.store).write()
        self.assertTrue((project / "CLAUDE.local.md").is_symlink())
        self.assertFalse((project / ".git").exists())


class InitWritesThemTest(unittest.TestCase):
    def test_init_writes_the_ai_files_and_a_run_that_only_wrote_them_is_not_nothing_to_do(self):
        import contextlib
        import io
        import init_project
        project = Path(tempfile.mkdtemp())
        with contextlib.redirect_stdout(io.StringIO()):
            init_project.main(["--project", str(project)])
        (project / "AGENTS.md").unlink()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = init_project.main(["--project", str(project)])
        self.assertIn("wrote AGENTS.md", out.getvalue())
        self.assertNotIn("nothing to do", out.getvalue())
        self.assertEqual(code, init_project.EXIT_OK)


if __name__ == "__main__":
    unittest.main()
