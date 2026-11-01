"""P104: the docs name only what is there (docs/2026-10-05-readme-design.md §5)."""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import check_docs  # noqa: E402

#: The most lines the journey guide's index may hold: its short version, the flow, the status words and a line a page.
INDEX_LINES = 45


def page(root, name, text):
    path = Path(root) / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


class TheChecksTest(unittest.TestCase):
    def test_a_command_or_script_that_does_not_exist_is_named(self):
        said = check_docs.missing_names("run `/spark:build`, then `/spark:frobnicate`, check_all.py and frob.py")
        self.assertEqual(said, ["/spark:frobnicate names no command", "frob.py names no script"])

    def test_a_script_in_a_package_under_scripts_may_be_named_by_its_file_name(self):
        self.assertEqual(check_docs.missing_names("the exit codes live in `outcomes.py`"), [])

    def test_a_file_of_the_micropython_stand_in_is_no_script(self):
        self.assertEqual(check_docs.missing_names("the stand-in `machine.py`"), ["machine.py names no script"])

    def test_a_file_spark_writes_into_a_project_may_be_named(self):
        self.assertEqual(check_docs.missing_names("the project gets `pins.py`"), [])

    def test_the_boot_file_a_project_holds_may_be_named(self):
        # P59: import_firmware.py leaves the project's own main.py unrun, and the guides say so.
        self.assertEqual(check_docs.missing_names("the command leaves `main.py` and `boot.py` unrun"), [])

    def test_every_command_skill_and_agent_must_be_listed(self):
        with tempfile.TemporaryDirectory() as root:
            for name in ("commands/build.md", "skills/spark-review/SKILL.md", "agents/part-finder.md"):
                page(root, name, "")
            page(root, "README.md", "/spark:build, spark-review, part-finder")
            page(root, "docs/guide/commands.md", "/spark:build, spark-review")
            self.assertEqual(check_docs.unlisted(Path(root)), ["docs/guide/commands.md does not name part-finder"])

    def test_a_table_row_naming_no_skill_or_agent_is_named(self):
        text = ("## Skills\n\n| skill | what |\n| --- | --- |\n| **spark-review** | x |\n| **spark-dream** | y |\n\n"
                "## Agents\n\n| agent | what |\n| --- | --- |\n| `part-finder` | z |\n")
        self.assertEqual(check_docs.unknown_in_tables(text), ["## Skills names spark-dream, which is no skill"])

    def test_a_flag_its_script_does_not_have_is_named(self):
        text = "```sh\npython3 scripts/check_all.py --project . --json --frob\n```\nand `board.py status --when-in DIR`"
        self.assertEqual(check_docs.missing_flags(text), ["check_all.py shows --frob, which its --help does not list"])

    def test_a_script_whose_help_fails_is_said_so(self):
        with tempfile.TemporaryDirectory() as root:
            page(root, "scripts/broken.py", "import no_such_module_anywhere\n")
            self.assertEqual(check_docs.missing_flags("`broken.py --x --y`", Path(root)),
                             ["broken.py --help exits 1, so the flags shown with it cannot be checked"])

    def test_a_broken_link_or_anchor_is_named(self):
        with tempfile.TemporaryDirectory() as root:
            guide = page(root, "docs/guide/a.md", "# A\n\n## The flow — an item's stages\n")
            text = "[ok](a.md#the-flow--an-items-stages) [gone](b.md) [bad](a.md#nowhere) [web](https://x.org/y)"
            self.assertEqual(check_docs.broken_links(guide, text, Path(root)),
                             ["docs/guide/a.md links b.md, which does not exist",
                              "docs/guide/a.md links a.md#nowhere, which has no such heading"])

    def test_a_broken_anchor_in_a_sub_folder_is_named_by_its_path_from_the_root(self):
        with tempfile.TemporaryDirectory() as root:
            deep = page(root, "docs/guide/sub/b.md", "# B\n")
            self.assertEqual(check_docs.broken_links(deep, "[x](b.md#nowhere)", Path(root)),
                             ["docs/guide/sub/b.md links b.md#nowhere, which has no such heading"])

    def test_a_page_in_a_sub_folder_of_the_guide_is_read(self):
        with tempfile.TemporaryDirectory() as root:
            page(root, ".claude-plugin/plugin.json", '{"version": "0"}')
            page(root, "docs/guide/sub/b.md", "[gone](c.md)\n")
            self.assertIn("docs/guide/sub/b.md links c.md, which does not exist", check_docs.problems(Path(root)))

    def test_a_page_over_its_budget_names_itself_and_its_budget(self):
        with tempfile.TemporaryDirectory() as root:
            page(root, "docs/guide/a.md", "x\n" * 401)
            self.assertEqual(check_docs.over_budget(Path(root), cell_limits={})[:1],
                             ["docs/guide/a.md has 401 lines, over its budget of 400. "
                              "Move text out or split the page, never raise the budget."])

    def test_a_page_with_its_own_budget_fails_over_it_and_passes_at_it(self):
        with tempfile.TemporaryDirectory() as root:
            budgets = {"docs/guide/a.md": 3}
            page(root, "docs/guide/a.md", "x\n" * 3)
            self.assertEqual(check_docs.over_budget(Path(root), budgets, {}), [])
            page(root, "docs/guide/a.md", "x\n" * 4)
            self.assertEqual(check_docs.over_budget(Path(root), budgets, {}),
                             ["docs/guide/a.md has 4 lines, over its budget of 3. "
                              "Move text out or split the page, never raise the budget."])

    def test_a_budget_for_a_page_that_is_gone_fails_and_a_smaller_page_passes(self):
        with tempfile.TemporaryDirectory() as root:
            page(root, "docs/guide/a.md", "x\n" * 2)
            self.assertEqual(check_docs.over_budget(Path(root), {"docs/guide/a.md": 50, "docs/guide/gone.md": 9}, {}),
                             ["docs/guide/gone.md has a budget but is not there. Remove its entry from BUDGETS."])

    def test_the_journey_guide_keeps_the_budget_of_an_index(self):
        # P501 made journey.md an index of one page per step. A budget over the index's size lets the long page grow back.
        self.assertLessEqual(check_docs.BUDGETS["docs/guide/journey.md"], INDEX_LINES)

    def test_every_journey_page_links_back_to_the_index(self):
        # P501: a reader who lands on a step's page or a shared page finds the whole journey from it.
        pages = sorted((ROOT / "docs" / "guide" / "journey").glob("*.md"))
        self.assertTrue(pages)
        self.assertEqual([page.name for page in pages if "](../journey.md)" not in page.read_text()], [])

    def test_a_table_cell_of_301_characters_fails_and_300_passes(self):
        with tempfile.TemporaryDirectory() as root:
            guide = page(root, "docs/guide/a.md", "")
            self.assertEqual(check_docs.long_cells(guide, "| a | %s |\n" % ("x" * 300), Path(root)), [])
            self.assertEqual(check_docs.long_cells(guide, "| a | %s |\n" % ("x" * 301), Path(root)),
                             ["docs/guide/a.md line 1 has a table cell of 301 characters, over 300. Shorten it or move the text below the table."])

    def test_a_long_cell_is_named_by_its_line_after_a_fenced_block(self):
        text = "x\n```text\n| %s |\n```\n| a | %s |\n" % ("y" * 400, "x" * 301)
        self.assertEqual(check_docs.long_cells(Path("a.md"), text),
                         ["a.md line 5 has a table cell of 301 characters, over 300. Shorten it or move the text below the table."])

    def test_an_escaped_pipe_stays_inside_its_cell(self):
        text = "| %s \\| %s |\n" % ("a" * 200, "b" * 200)
        self.assertEqual(len(check_docs.long_cells(Path("a.md"), text)), 1)

    def test_an_indented_table_row_is_counted(self):
        self.assertEqual(len(check_docs.long_cells(Path("a.md"), "  | %s |\n" % ("x" * 301))), 1)

    def test_a_cell_limit_for_a_page_that_is_gone_fails(self):
        with tempfile.TemporaryDirectory() as root:
            page(root, "docs/guide/a.md", "x\n")
            self.assertEqual(check_docs.over_budget(Path(root), {"docs/guide/a.md": 50}, {"docs/guide/gone.md": 900}),
                             ["docs/guide/gone.md has a cell limit but is not there. Remove its entry from CELL_LIMITS."])

    def test_a_table_cell_in_a_fenced_block_is_not_counted(self):
        text = "```text\n| %s |\n```\n" % ("x" * 400)
        self.assertEqual(check_docs.long_cells(Path("a.md"), text), [])

    def test_a_page_with_its_own_cell_limit_gets_that_limit(self):
        with tempfile.TemporaryDirectory() as root:
            guide = page(root, "docs/guide/a.md", "")
            limits = {"docs/guide/a.md": 400}
            self.assertEqual(check_docs.long_cells(guide, "| %s |\n" % ("x" * 400), Path(root), limits), [])
            self.assertEqual(check_docs.long_cells(guide, "| %s |\n" % ("x" * 401), Path(root), limits),
                             ["docs/guide/a.md line 1 has a table cell of 401 characters, over 400. Shorten it or move the text below the table."])

    def test_an_anchor_follows_github_s_slug(self):
        self.assertEqual(check_docs.slug("`/spark:build` — one command"), "sparkbuild--one-command")
        self.assertEqual(check_docs.slug("The flow — an item's stages"), "the-flow--an-items-stages")

    def test_a_link_to_a_folder_is_fine(self):
        with tempfile.TemporaryDirectory() as root:
            (Path(root) / "parts").mkdir()
            guide = page(root, "docs/guide/a.md", "# A\n")
            self.assertEqual(check_docs.broken_links(guide, "[parts](../../parts/)"), [])

    def test_an_output_with_no_date_and_version_is_named(self):
        text = "<!-- output: run 2026-10-06, spark 0.6.0 -->\n```text\nok\n```\n\n```text\nundated\n```\n"
        self.assertEqual(check_docs.undated_outputs(text),
                         ["the output at line 6 has no `<!-- output: run DATE, spark VERSION -->` above it"])

    def test_a_runnable_example_must_end_as_marked(self):
        text = "<!-- runs: exit 0 -->\n```sh\ntrue\n```\n<!-- runs: exit 0 -->\n```sh\nexit 3\n```\n```sh\nexit 5\n```\n"
        self.assertEqual(check_docs.failed_examples(text), ["the example `exit 3` exits 3, not 0"])

    def test_a_runnable_example_that_hangs_is_named(self):
        with mock.patch.object(check_docs, "RUN_TIMEOUT", 1):
            said = check_docs.failed_examples("<!-- runs: exit 0 -->\n```sh\nsleep 5\n```\n")
        self.assertEqual(said, ["the example `sleep 5` takes longer than 1 s — not a light example"])

    def test_a_runnable_example_gets_a_store_of_its_own(self):
        outer = os.environ.get("SPARK_HOME", "")
        text = '<!-- runs: exit 0 -->\n```sh\ntest -n "$SPARK_HOME" && test "$SPARK_HOME" != "%s"\n```\n' % outer
        self.assertEqual(check_docs.failed_examples(text), [])

    def test_the_readme_must_say_the_plugin_s_version(self):
        with tempfile.TemporaryDirectory() as root:
            page(root, ".claude-plugin/plugin.json", '{"version": "9.9.9"}')
            self.assertEqual(check_docs.version_mismatch("v9.9.9 · MIT", Path(root)), [])
            self.assertEqual(check_docs.version_mismatch("v1.0.0 · MIT", Path(root)),
                             ["README.md does not say v9.9.9, the version plugin.json ships"])

    def test_a_personal_path_is_named(self):
        # A temp directory, not a home: test_orphans refuses a home path in any shipped file, tests included (P44).
        self.assertEqual(check_docs.personal_paths(Path("README.md"), "fine\nsee /private/var/folders/x\n"),
                         ["README.md line 2 names a personal path or checkout: /private/"])

    def test_a_docs_path_that_is_not_a_file_is_named(self):
        # The stale path is joined from parts, so that no check reads this line as a real citation.
        stale = "/".join(["docs", "gone"]) + ".md"
        with tempfile.TemporaryDirectory() as root:
            (Path(root) / "docs").mkdir()
            (Path(root) / "docs" / "here.md").write_text("x")
            (Path(root) / "scripts").mkdir()
            (Path(root) / "scripts" / "a.py").write_text("# docs/here.md#top, docs/<name>.md and %s." % stale)
            self.assertEqual(check_docs.stale_doc_paths(Path(root)),
                             ["scripts/a.py names %s, which is not there" % stale])

    def test_every_citing_folder_is_read_deep_and_each_stale_path_is_named_once(self):
        # P386 R1's mutation run: each line below catches one defect the test above let through.
        stale = "/".join(["docs", "guide", "gone.v2"]) + ".md"
        folders = ("agents", "commands", "data", "scripts", "skills")
        with tempfile.TemporaryDirectory() as root:
            for folder in folders:
                (Path(root) / folder / "sub").mkdir(parents=True)
                (Path(root) / folder / "sub" / "a.txt").write_text("%s, %s, docs/*.md and docs/{x}.md" % (stale, stale))
            (Path(root) / "scripts" / "b.bin").write_bytes(b"\x80")
            (Path(root) / ".claude-plugin").mkdir()
            (Path(root) / ".claude-plugin" / "plugin.json").write_text('{"version": "0"}')
            self.assertEqual(check_docs.stale_doc_paths(Path(root)),
                             ["%s/sub/a.txt names %s, which is not there" % (folder, stale)
                              for folder in ("scripts", "data", "commands", "skills", "agents")])
            self.assertIn("scripts/sub/a.txt names %s, which is not there" % stale, check_docs.problems(Path(root)))

    def test_the_code_names_no_docs_page_that_is_gone(self):
        self.assertEqual(check_docs.stale_doc_paths(), [])


class TheDocsTest(unittest.TestCase):
    def test_the_docs_name_only_what_is_there(self):
        self.assertEqual(check_docs.problems(), [])


if __name__ == "__main__":
    unittest.main()
