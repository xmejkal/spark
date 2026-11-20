"""P481: a page block between an Operation's markers is what OperationHelpTable renders for it, and a broken marker is named.
P936: a stages block is what StageMarkdownTable renders for the Operation's stages."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tools"))

import doc_blocks  # noqa: E402
from spark.bench.look_at_board import LookAtBoard  # noqa: E402
from spark.build.build_board import BuildBoard  # noqa: E402
from spark.build.stage_help_table import StageMarkdownTable  # noqa: E402
from spark.build.stages import NO_PARTS_ENDING, StageDefinition  # noqa: E402
from spark.core.operation import COMMON_ARGUMENTS, Argument, Operation  # noqa: E402
from spark.core.operation_help_table import OperationHelpTable  # noqa: E402

LOOK = {"look": LookAtBoard}
START, END = "<!-- spark:operation look -->", "<!-- /spark:operation look -->"


def block(body):
    return "# A page\n\n%s\n%s\n%s\n\nThe rest.\n" % (START, body, END)


class Piped(Operation):
    name = "pipe"
    summary = "Joins two words."
    arguments = (Argument(("--word",), "word", str, "one word | another word"), COMMON_ARGUMENTS["json"])


class TheTreeTest(unittest.TestCase):
    def test_no_page_of_the_tree_holds_a_stale_or_broken_block(self):
        self.assertEqual(doc_blocks.stale_pages(), [])

    def test_the_deploy_command_holds_the_looks_block(self):
        self.assertIn("commands/deploy.md", [page for page, _ in doc_blocks.pages_with_blocks()])

    def test_importing_the_tool_for_its_markers_loads_no_spark_module(self):
        # P855 review: tools/check_docs.py imports END from here, and the docs checker must not depend on the bench area
        code = "import sys; import doc_blocks; print(sorted(name for name in sys.modules if name.split('.')[0] == 'spark'))"
        run = subprocess.run([sys.executable, "-c", code], cwd=ROOT / "tools", capture_output=True, text=True, timeout=60,
                             stdin=subprocess.DEVNULL)
        self.assertEqual(run.stdout, "[]\n", run.stderr)

    def test_the_how_it_works_page_holds_the_build_stages_block(self):
        # P936: the stage table is generated, kept current by the first test
        self.assertIn("docs/guide/how-it-works.md", [page for page, _ in doc_blocks.pages_with_blocks()])
        self.assertIn("<!-- spark:stages build-board -->\n", (ROOT / "docs/guide/how-it-works.md").read_text())

    def test_a_block_may_name_the_build_operation(self):
        self.assertIs(doc_blocks.block_operations()["build-board"], BuildBoard)

    def test_the_scripts_page_holds_lives_block(self):
        # P855: the first block on a guide page, kept current by the test above
        self.assertIn("<!-- spark:operation live -->\n", (ROOT / "docs/guide/agents/scripts.md").read_text())


class TheBlockTest(unittest.TestCase):
    def test_a_block_is_written_between_its_markers_and_the_rest_stays(self):
        fresh = doc_blocks.fresh_text("a.md", block("old words"), LOOK)
        self.assertEqual(fresh, block("\n%s\n" % OperationHelpTable.render(LookAtBoard)))
        self.assertEqual(doc_blocks.fresh_text("a.md", fresh, LOOK), fresh)

    def refused(self, text, operations=LOOK):
        """The sentence of the BlockError that `text` raises."""
        with self.assertRaises(doc_blocks.BlockError) as said:
            doc_blocks.fresh_text("a.md", text, operations)
        return str(said.exception)

    def test_a_start_without_its_end_is_named_with_the_page_the_line_and_the_name(self):
        self.assertEqual(self.refused("# A page\n%s\nwords\n" % START), "a.md line 2: the block of look has no end marker")

    def test_a_second_start_before_the_end_is_a_start_without_its_end(self):
        self.assertEqual(self.refused("%s\n%s\n%s\n" % (START, START, END)), "a.md line 1: the block of look has no end marker")

    def test_an_end_that_names_another_operation_is_named(self):
        self.assertEqual(self.refused("%s\n<!-- /spark:operation deploy -->\n" % START),
                         "a.md line 2: the block of look ends with the marker of deploy")

    def test_an_end_without_its_start_is_named(self):
        # P481 review: a stray end marker after a good block, or alone, is refused, never left to rot
        self.assertEqual(self.refused(block("words") + END + "\n"), "a.md line 8: the end marker of look has no start marker")

    def test_a_name_no_table_holds_is_named(self):
        self.assertEqual(self.refused(block("words"), {}), "a.md line 3: no Operation is named look")

    def test_an_operation_with_no_summary_is_named_and_not_a_crash(self):
        # P481 review: five of the six bench Operations have no summary yet
        self.assertEqual(self.refused(block("words"), {"look": Operation}), "a.md line 3: the Operation look has no summary to show")

    def test_a_comment_line_that_names_the_marker_word_but_is_no_marker_is_named(self):
        for line in ("<!--spark:operation look-->", START + " ", START + "\r", "<!-- spark:operation: look -->", "  " + START):
            self.assertEqual(self.refused("# A page\n%s\n" % line), "a.md line 2: this line names spark:operation but is no marker")

    def test_a_marker_inside_a_line_is_no_marker(self):
        text = "The markers are `%s` and `%s`.\n" % (START, END)
        self.assertEqual(doc_blocks.fresh_text("a.md", text, {}), text)

    def test_a_marker_in_a_code_fence_is_an_example_and_stays(self):
        # P481 review: a page that shows the markers in a fence keeps its example as written
        text = "# A page\n\n```\n%s\nan example\n%s\n```\n\n```md\n%s\n```\n" % (START, END, END)
        self.assertEqual(doc_blocks.fresh_text("a.md", text, LOOK), text)
        self.assertEqual(doc_blocks.fresh_text("a.md", text + block("old"), LOOK),
                         text + block("\n%s\n" % OperationHelpTable.render(LookAtBoard)))


class Staged(Operation):
    name = "staged"
    stages = (StageDefinition("one", "the first", (NO_PARTS_ENDING,)),)


STAGED = {"staged": Staged}
STAGES_START, STAGES_END = "<!-- spark:stages staged -->", "<!-- /spark:stages staged -->"


class TheStagesBlockTest(unittest.TestCase):
    """P936: a stages block is StageMarkdownTable's text for the stages of the Operation it names."""

    def refused(self, text, operations=STAGED):
        with self.assertRaises(doc_blocks.BlockError) as said:
            doc_blocks.fresh_text("a.md", text, operations)
        return str(said.exception)

    def test_a_stages_block_is_written_from_the_operation_s_stages(self):
        text = "# A page\n\n%s\nold words\n%s\n" % (STAGES_START, STAGES_END)
        self.assertEqual(doc_blocks.fresh_text("a.md", text, STAGED),
                         "# A page\n\n%s\n\n%s\n\n%s\n" % (STAGES_START, StageMarkdownTable.render(Staged.stages), STAGES_END))

    def test_an_operation_with_no_stages_is_named(self):
        self.assertEqual(self.refused("%s\n%s\n" % (STAGES_START, STAGES_END), {"staged": Operation}),
                         "a.md line 1: the Operation staged has no stages to show")

    def test_an_end_of_the_other_kind_is_named(self):
        self.assertEqual(self.refused("%s\n<!-- /spark:operation staged -->\n" % STAGES_START),
                         "a.md line 2: the stages block of staged ends with a marker of the kind operation")

    def test_a_comment_line_that_names_spark_stages_but_is_no_marker_is_named(self):
        self.assertEqual(self.refused("# A page\n%s \n" % STAGES_START), "a.md line 2: this line names spark:stages but is no marker")

    def test_a_page_with_only_a_stages_block_is_found(self):
        with tempfile.TemporaryDirectory() as root:
            (Path(root) / "a.md").write_text("%s\nold\n%s\n" % (STAGES_START, STAGES_END))
            self.assertEqual([page for page, _ in doc_blocks.pages_with_blocks(Path(root))], ["a.md"])


class ThePagesTest(unittest.TestCase):
    def page(self, root, name, text):
        path = Path(root) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def test_a_changed_block_and_a_broken_one_are_each_named_and_nothing_is_written(self):
        with tempfile.TemporaryDirectory() as root:
            changed = self.page(root, "commands/a.md", block("hand-written words"))
            self.page(root, "docs/guide/b.md", "%s\n" % START)
            self.assertEqual(doc_blocks.stale_pages(Path(root), LOOK),
                             ["commands/a.md: a block differs from its Operation, so run python3 tools/doc_blocks.py",
                              "docs/guide/b.md line 1: the block of look has no end marker"])
            self.assertEqual(changed.read_text(), block("hand-written words"))

    def test_the_writer_writes_a_stale_page_and_leaves_a_refused_one_as_it_is(self):
        with tempfile.TemporaryDirectory() as root:
            stale = self.page(root, "commands/a.md", block("hand-written words"))
            broken = self.page(root, "docs/guide/b.md", "%s\n" % START)
            self.assertEqual(doc_blocks.write_pages(Path(root), LOOK),
                             (["commands/a.md"], ["docs/guide/b.md line 1: the block of look has no end marker"]))
            self.assertEqual(stale.read_text(), block("\n%s\n" % OperationHelpTable.render(LookAtBoard)))
            self.assertEqual(broken.read_text(), "%s\n" % START)
            self.assertEqual(doc_blocks.stale_pages(Path(root), LOOK), ["docs/guide/b.md line 1: the block of look has no end marker"])


class TheHelpTableTest(unittest.TestCase):
    def test_the_summary_comes_first_then_a_row_per_argument_but_json(self):
        self.assertEqual(OperationHelpTable.render(Piped).splitlines(),
                         ["Joins two words.", "", "| flag | value | what it does |", "|---|---|---|",
                          "| `--word` | `WORD` | one word \\| another word |"])

    def test_a_flag_has_no_value_and_a_metavar_or_the_choices_name_one(self):
        class Shown(Operation):
            summary = "Shows values."
            arguments = (Argument(("--on",), "on", bool, "turns it on"),
                         Argument(("--as",), "kind", str, "the kind", choices=("a", "b")),
                         Argument(("--project",), "project", Path, "the folder", metavar="PROJECT_DIR"))
        rows = OperationHelpTable.render(Shown).splitlines()[4:]
        self.assertEqual(rows, ["| `--on` |  | turns it on |", "| `--as` | `{a,b}` | the kind |",
                                "| `--project` | `PROJECT_DIR` | the folder |"])


if __name__ == "__main__":
    unittest.main()
