"""P678: docs/guide/map.md, the page that says where the code is, follows the code."""

import ast
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import map as area_map  # noqa: E402  (not `map`: that is a built-in)

MODULE_WITH_AN_OPERATION = '''"""
Does a thing, over
two lines. And then more.
"""


class Operation:
    pass


class Thing(Operation):
    name = "thing"


class Other:
    name = "other"
'''


def tree(root, documented=True):
    """A small tree: one area `demo` with a documented module and a bare one, a test for the first, a CLI, a registry."""
    (root / "tests").mkdir()
    (root / "tests" / "test_one.py").write_text("from spark.demo.one import Thing\n")
    (root / "tests" / "test_aaa.py").write_text("import spark.demo.two as two\n")
    (root / "tests" / "test_two.py").write_text("import spark.demo.two\n")  # named for the module: listed first
    area = root / "scripts" / "spark" / "demo"
    area.mkdir(parents=True)
    (area / "__init__.py").write_text('"""The demo area."""\n')
    (area / "one.py").write_text(MODULE_WITH_AN_OPERATION)
    (area / "two.py").write_text("X = 1\n")
    (area / "three.py").write_text("Y = 1\n")
    (root / "scripts" / "demo_cli.py").write_text("from spark.demo.one import Thing, Other\n")
    (root / "scripts" / "ghost_cli.py").write_text("from spark.demo.ghost import Thing\n")  # no such module: no crash
    (root / "scripts" / "p678_registry.py").write_text('ONLY = (("lonely", 1),)\n')


class TheMapTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        tree(self.root)
        registries = (area_map.Registry("ONLY", "p678_registry", "ONLY", lambda row: row[0]),)
        self.text = area_map.AreaMap.of(self.root, registries).markdown()

    def test_a_module_shows_its_first_docstring_line_and_its_test_file(self):
        self.assertIn("| `one.py` | Does a thing, over two lines. | `tests/test_one.py` |", self.text)

    def test_a_module_without_a_docstring_or_an_importing_test_says_so(self):
        self.assertIn("| `three.py` | (no docstring) | none |", self.text)

    def test_the_test_named_for_the_module_comes_first_and_an_import_as_counts(self):
        self.assertIn("| `two.py` | (no docstring) | `tests/test_two.py`, `tests/test_aaa.py` |", self.text)

    def test_a_long_first_sentence_is_cut_at_a_word_with_an_ellipsis(self):
        about = area_map.first_line(ast.parse('"""%s."""' % " ".join(["word"] * 40)))
        self.assertEqual(about, " ".join(["word"] * 20)[:99].rsplit(" ", 1)[0] + "…")

    def test_a_sentence_does_not_end_at_the_dot_of_a_heading_line(self):
        self.assertEqual(area_map.first_line(ast.parse('"""A heading (P442,\nW3-3): it does a thing. More."""')),
                         "A heading (P442, W3-3): it does a thing.")

    def test_an_area_shows_its_own_first_docstring_line(self):
        self.assertIn("## spark/demo: The demo area.", self.text)

    def test_a_class_that_is_no_operation_is_not_listed(self):
        self.assertNotIn("other", self.text)

    def test_a_cli_lists_the_operations_it_imports(self):
        self.assertIn("| `demo_cli.py` | `thing` (`spark.demo.one.Thing`) |", self.text)

    def test_a_registry_with_one_key_renders_one_row(self):
        self.assertIn("- `ONLY`: lonely\n", self.text)

    def test_the_page_says_that_it_is_generated_and_by_which_command(self):
        self.assertIn("python3 tools/map.py --write", self.text.splitlines()[2])


class TheCommittedMapTest(unittest.TestCase):
    def test_the_committed_page_is_the_one_the_code_gives(self):
        self.assertEqual((ROOT / area_map.PAGE).read_text(), area_map.AreaMap.of(ROOT).markdown(),
                         "docs/guide/map.md is stale: run python3 tools/map.py --write")

    def test_each_registry_of_the_code_is_on_the_page(self):
        text = (ROOT / area_map.PAGE).read_text()
        for registry in area_map.REGISTRIES:
            self.assertIn("`%s`" % registry.label, text)

    def test_each_module_of_each_area_is_on_the_page(self):
        text = (ROOT / area_map.PAGE).read_text()
        for path in (ROOT / "scripts" / "spark").glob("*/*.py"):
            if path.name != "__init__.py":
                section = text.partition("## spark/%s:" % path.parent.name)[2].partition("\n## ")[0]
                self.assertIn("| `%s` |" % path.name, section)


if __name__ == "__main__":
    unittest.main()
