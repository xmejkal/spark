"""P418 (#546), OC8 of the refactor plan v2: the leaves import nothing of spark, and a moved guard is read from its leaf.

It reads `scripts/*.py` with `ast` and imports none of them. S3 folds it into the rules test later.
"""

import ast
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
SPARK = {path.stem for path in SCRIPTS.glob("*.py")}

#: The modules that import nothing of spark, so that every reader can use them without importing another reader.
LEAVES = ("outcomes", "provenance", "text_guards", "zone_time")

#: The names OC8 moved into `text_guards`, by the module that held them. No script reads them from there again.
MOVED = {"drawer": {"clean", "CONTROL", "LABEL_MAX", "TEXT_MAX", "TAGS_MAX"}, "parts": {"one_line", "COMMENT_UNSAFE"}}


def tree_of(stem):
    return ast.parse((SCRIPTS / ("%s.py" % stem)).read_text())


def imported(tree):
    """Every module the tree imports, at the top or inside a function, by its first name."""
    names = {alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
    return names | {node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module}


def old_reads(tree):
    """Each moved name the tree reaches through its old module: `drawer.clean`, `parts_library.one_line`, `from drawer import clean`."""
    bound = {alias.asname or alias.name: alias.name for node in ast.walk(tree) if isinstance(node, ast.Import)
             for alias in node.names if alias.name in MOVED}
    reads = {"%s.%s" % (bound[node.value.id], node.attr) for node in ast.walk(tree)
             if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id in bound
             and node.attr in MOVED[bound[node.value.id]]}
    return reads | {"%s.%s" % (node.module, alias.name) for node in ast.walk(tree)
                    if isinstance(node, ast.ImportFrom) and node.module in MOVED
                    for alias in node.names if alias.name in MOVED[node.module]}


class LeafImportTest(unittest.TestCase):
    def test_each_leaf_imports_nothing_of_spark(self):
        for leaf in LEAVES:
            with self.subTest(leaf=leaf):
                self.assertTrue((SCRIPTS / ("%s.py" % leaf)).is_file(), "scripts/%s.py does not exist" % leaf)
                self.assertEqual(imported(tree_of(leaf)) & SPARK, set())

    def test_matching_imports_no_drawer(self):
        self.assertNotIn("drawer", imported(tree_of("matching")))

    def test_no_script_reads_a_moved_guard_from_its_old_module(self):
        found = {stem: sorted(old_reads(tree_of(stem))) for stem in sorted(SPARK)}
        self.assertEqual({stem: reads for stem, reads in found.items() if reads}, {})

    def test_the_reading_finds_each_way_to_the_old_module(self):
        tree = ast.parse("import parts as parts_library\nimport drawer\nfrom drawer import TAGS_MAX\n"
                         "parts_library.one_line(x)\ndrawer.clean(y)\ndrawer.listing()\n")
        self.assertEqual(old_reads(tree), {"parts.one_line", "drawer.clean", "drawer.TAGS_MAX"})


if __name__ == "__main__":
    unittest.main()
