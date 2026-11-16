"""P481: a page block between an Operation's markers is what OperationHelpTable renders for it, and a broken marker is named."""

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


class TheBlockTest(unittest.TestCase):
    def test_a_block_is_written_between_its_markers_and_the_rest_stays(self):
        fresh = doc_blocks.fresh_text("a.md", block("old words"), LOOK)
        self.assertEqual(fresh, block("\n%s\n" % OperationHelpTable.render(LookAtBoard)))
        self.assertEqual(doc_blocks.fresh_text("a.md", fresh, LOOK), fresh)

    def test_a_start_without_its_end_is_named_with_the_page_and_the_name(self):
        with self.assertRaises(doc_blocks.BlockError) as said:
            doc_blocks.fresh_text("a.md", "%s\nwords\n" % START, LOOK)
        self.assertEqual(str(said.exception), "a.md: the block of look has no end marker")

    def test_a_second_start_before_the_end_is_a_start_without_its_end(self):
        with self.assertRaises(doc_blocks.BlockError) as said:
            doc_blocks.fresh_text("a.md", "%s\n%s\n%s\n" % (START, START, END), LOOK)
        self.assertEqual(str(said.exception), "a.md: the block of look has no end marker")

    def test_an_end_that_names_another_operation_is_named(self):
        with self.assertRaises(doc_blocks.BlockError) as said:
            doc_blocks.fresh_text("a.md", "%s\n<!-- /spark:operation deploy -->\n" % START, LOOK)
        self.assertEqual(str(said.exception), "a.md: the block of look ends with the marker of deploy")

    def test_a_name_no_table_holds_is_named(self):
        with self.assertRaises(doc_blocks.BlockError) as said:
            doc_blocks.fresh_text("a.md", block("words"), {})
        self.assertEqual(str(said.exception), "a.md: no Operation is named look")

    def test_a_marker_inside_a_line_is_no_marker(self):
        text = "The markers are `%s` and `%s`.\n" % (START, END)
        self.assertEqual(doc_blocks.fresh_text("a.md", text, {}), text)


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
                              "docs/guide/b.md: the block of look has no end marker"])
            self.assertEqual(changed.read_text(), block("hand-written words"))

    def test_the_writer_writes_a_stale_page_and_leaves_a_refused_one_as_it_is(self):
        with tempfile.TemporaryDirectory() as root:
            stale = self.page(root, "commands/a.md", block("hand-written words"))
            broken = self.page(root, "docs/guide/b.md", "%s\n" % START)
            self.assertEqual(doc_blocks.write_pages(Path(root), LOOK),
                             (["commands/a.md"], ["docs/guide/b.md: the block of look has no end marker"]))
            self.assertEqual(stale.read_text(), block("\n%s\n" % OperationHelpTable.render(LookAtBoard)))
            self.assertEqual(broken.read_text(), "%s\n" % START)
            self.assertEqual(doc_blocks.stale_pages(Path(root), LOOK), ["docs/guide/b.md: the block of look has no end marker"])


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
