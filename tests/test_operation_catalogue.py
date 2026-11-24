"""
P1077 (#1581, P793 piece 4): the Operation catalogue, `scripts/spark/operation_catalogue.py`, is one map of every area's
OPERATIONS table. It sits above the areas, outside the core: no module of the core or of an area imports it, and a
frontend hands it, or its slice, to the core's `DescribeOperations` through the constructor.

These tests hold that every table's Operations are in it once, that every Operation class under scripts/spark is in it,
that each entry builds with no argument and has a sentence (the construction contract), that its network list `NETWORK`
is the ops that declare `fetches`, that `--describe` over it reads `flag` and `dry_run` from each Operation's own
arguments, that the Operations with no `data_keys` (S3) only get fewer, and the import direction by full dotted path.

    SPARK_HOME=<scratch> python3 -m unittest tests.test_operation_catalogue
"""

import ast
import contextlib
import io
import re
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tools"))

import doc_blocks  # noqa: E402
import parts  # noqa: E402
from fakes import FakeOutsideWorld  # noqa: E402
from planted_tree import planted  # noqa: E402
from spark import operation_catalogue  # noqa: E402
from spark.core.describe_operations import DescribeOperations, summary_of  # noqa: E402
from spark.core.operation import Operation  # noqa: E402
from spark.flow import run_request  # noqa: E402
from spark.sourcing.research import research_part  # noqa: E402

# --- MVP ---
#: The Operation classes under scripts/spark that are no entry, each with its reason (D4): the two bases, which no frontend
#: runs, and the core's DescribeOperations, which needs a registry to be built (the one exception to the construction
#: contract) and is every CLI's.
NO_ENTRY = {"AnswerOperation", "PartOperation", "DescribeOperations"}
#: The ops with no `data_keys` today (S3, FE-3's 11). The list only shrinks: P937 #1333 (piece 7) fills them.
NO_DATA_KEYS = {"look", "deploy", "issue-grant", "check-grant", "live", "reach", "needs-drop", "build-board", "list-boards",
                "research-part", "disallow-direct-flashing"}
#: The script a frontend names a network op by, when it is not a parts.py flag (the frontend's fact, P1081 #1585).
SCRIPT_OF = {"research-part": research_part.SCRIPT}
#: The network operations off the core, which agents.md names beside the ones the Operation catalogue lists.
OFF_THE_CORE = ("--install", "--on", "check_vendor_pins.py")


def operation_classes(root):
    """The names of the classes under `root`/scripts/spark (stand_in/ aside) whose bases reach `Operation`, read by base
    name and transitively, Operation itself left out."""
    classes = [(node.name, {base.id if isinstance(base, ast.Name) else base.attr for base in node.bases
                            if isinstance(base, (ast.Name, ast.Attribute))})
               for path in sorted((root / "scripts" / "spark").rglob("*.py")) if "stand_in" not in path.parts
               for node in ast.walk(ast.parse(path.read_text())) if isinstance(node, ast.ClassDef)]
    found = {"Operation"}
    while True:
        more = {name for name, bases in classes if bases & found} - found
        if not more:
            return found - {"Operation"}
        found |= more


def imported_modules(tree):
    """The modules each import statement names, by their full dotted paths, one list per statement: `import a.b` gives a.b,
    and `from a.b import c` gives a.b and a.b.c, so `from spark import flow` holds spark.flow and `from spark.flow.guide
    import x` holds spark.flow.guide."""
    statements = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            statements.append([alias.name for alias in node.names])
        elif isinstance(node, ast.ImportFrom) and node.level:
            statements.append(["." * node.level + (node.module or "")])  # relative: the direction cannot be read, so a finding
        elif isinstance(node, ast.ImportFrom) and node.module:
            statements.append([node.module] + ["%s.%s" % (node.module, alias.name) for alias in node.names])
    return statements


def imports_against_the_direction(root):
    """Each import under `root`/scripts/spark that breaks the direction: a core module that imports an area or the
    Operation catalogue, or an area module that imports the Operation catalogue, as `<module>: <dotted path>`, once per
    import statement (its first name that breaks it). A relative import is a finding too: its direction is not read."""
    spark = root / "scripts" / "spark"
    areas = {folder.name for folder in spark.iterdir() if (folder / "__init__.py").is_file()} - {"core"}
    found = []
    for path in sorted(spark.rglob("*.py")):
        relative = path.relative_to(spark)
        if len(relative.parts) == 1:
            continue  # spark/__init__.py and the Operation catalogue itself
        forbidden = ["spark.operation_catalogue"] + (["spark." + area for area in sorted(areas)] if relative.parts[0] == "core" else [])
        for names in imported_modules(ast.parse(path.read_text())):
            found += ["%s: %s" % (relative.as_posix(), name) for name in names
                      if name.startswith(".") or any(name == one or name.startswith(one + ".") for one in forbidden)][:1]
    return found


class TheOperationCatalogueTest(unittest.TestCase):
    def test_every_table_s_operations_are_in_the_catalogue_once(self):
        tables = operation_catalogue.TABLES
        self.assertEqual([package for package, _ in tables],
                         ["idea", "sourcing", "sourcing.research", "design", "build", "checks", "bench", "flow"])
        for package, table in tables:
            for op, cls in table.items():
                self.assertIs(operation_catalogue.CATALOGUE.get(op), cls, (package, op))
                self.assertTrue(cls.__module__.startswith("spark.%s." % package), (package, op, cls.__module__))
        self.assertEqual(sum(len(table) for _, table in tables), len(operation_catalogue.CATALOGUE), "an op is in two tables")

    def test_every_operation_class_under_scripts_spark_is_in_the_catalogue(self):
        self.assertEqual(sorted(operation_classes(ROOT) - NO_ENTRY),
                         sorted(cls.__name__ for cls in operation_catalogue.CATALOGUE.values()))
        root = planted({"scripts/spark/core/operation.py": "class Operation:\n    pass\n",
                        "scripts/spark/x/stray.py": "from spark.core import operation\n\n\nclass Base(operation.Operation):\n    pass\n\n\n"
                                                    "class Stray(Base):\n    pass\n\n\nclass Other:\n    pass\n"}, leaves=False)
        self.assertEqual(operation_classes(root), {"Base", "Stray"})

    def test_each_entry_is_an_operation_named_by_its_op_with_a_sentence_that_builds_with_no_argument(self):
        for op, cls in operation_catalogue.CATALOGUE.items():
            with self.subTest(op=op):
                self.assertTrue(issubclass(cls, Operation))
                self.assertEqual(cls.name, op)
                self.assertEqual(cls().input_schema()["type"], "object")
                sentence = summary_of(cls)
                self.assertIsInstance(sentence, str)
                self.assertTrue(sentence.strip())

    def test_the_network_operations_are_the_ones_that_declare_fetches(self):
        self.assertEqual(operation_catalogue.NETWORK, ("sources", "fetch", "find-documents", "research-part"))

    def test_the_agents_page_names_each_network_operation(self):
        paragraphs = [one for one in (ROOT / "docs" / "guide" / "agents.md").read_text().split("\n\n") if "reach the network" in one]
        self.assertEqual(len(paragraphs), 1, "one paragraph of agents.md says which operations reach the network")
        names = [SCRIPT_OF.get(op, "--" + op) for op in operation_catalogue.NETWORK] + list(OFF_THE_CORE)
        self.assertEqual([name for name in names if not re.search(r"(?<![\w-])%s(?![\w-])" % re.escape(name), paragraphs[0])], [])

    def test_describe_over_the_whole_catalogue_reads_flag_and_dry_run_from_the_arguments(self):
        result = DescribeOperations(operation_catalogue.CATALOGUE).run(outside=FakeOutsideWorld())
        rows = result.data["operations"]
        self.assertEqual([row["op"] for row in rows], list(operation_catalogue.CATALOGUE))
        by_op = {row["op"]: row for row in rows}
        self.assertEqual((by_op["look"]["flag"], by_op["look"]["dry_run"]), (None, False))
        self.assertEqual(by_op["fetch"]["flag"], "--fetch")
        self.assertEqual([by_op[op]["dry_run"] for op in ("build-board", "research-part", "deploy", "pick")], [False, False, True, True])

    def test_the_operations_with_no_data_keys_only_get_fewer(self):
        empty = {op for op, cls in operation_catalogue.CATALOGUE.items() if not cls.data_keys}
        self.assertEqual(sorted(empty), sorted(NO_DATA_KEYS), "give the op its keys, with a test that compares them with a real "
                                                              "answer. Then take the op off this list")

    def test_the_page_s_steps_and_the_doc_blocks_read_the_catalogue(self):
        for op, cls in run_request.STEP_OPERATIONS.items():
            self.assertIs(operation_catalogue.CATALOGUE.get(op), cls, op)
        self.assertIs(doc_blocks.block_operations(), operation_catalogue.CATALOGUE)

    def test_the_catalogue_imports_alone_and_no_core_or_area_module_imports_it_by_any_path(self):
        for module in ("spark.operation_catalogue", "spark.sourcing.research.research_operations"):
            run = subprocess.run([sys.executable, "-c", "import %s" % module], cwd=ROOT / "scripts", capture_output=True, text=True,
                                 timeout=60, stdin=subprocess.DEVNULL)
            self.assertEqual((module, run.returncode, run.stderr), (module, 0, ""))
        self.assertEqual(imports_against_the_direction(ROOT), [])
        root = planted({"scripts/spark/__init__.py": "", "scripts/spark/core/__init__.py": "",
                        "scripts/spark/core/deep.py": "from spark.flow.guide import guide_of\nfrom spark.core import outcomes\n",
                        "scripts/spark/flow/__init__.py": "", "scripts/spark/bench/__init__.py": "",
                        "scripts/spark/bench/reader.py": "from spark import operation_catalogue\nimport spark.flow.guide\n",
                        "scripts/spark/bench/near.py": "from . import reader\n"}, leaves=False)
        self.assertEqual(imports_against_the_direction(root), ["bench/near.py: .", "bench/reader.py: spark.operation_catalogue",
                                                               "core/deep.py: spark.flow.guide"])

    def test_parts_help_holds_describe_s_lines_in_order(self):
        lines = DescribeOperations(parts.OPERATIONS).run(outside=None).lines
        self.assertEqual(len(lines), len(parts.OPERATIONS))
        out = io.StringIO()
        with contextlib.redirect_stdout(out), self.assertRaises(SystemExit):
            parts.main(["--help"])
        text = out.getvalue()
        self.assertEqual([line for line in lines if line not in text], [])
        places = [text.index(line) for line in lines]
        self.assertEqual(places, sorted(places))
# --- end MVP ---


if __name__ == "__main__":
    unittest.main()
