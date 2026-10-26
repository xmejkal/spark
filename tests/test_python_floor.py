"""P426 (#560): spark runs on the Python 3.9 its README and pyproject promise, so no script or tool uses newer syntax.

`ast.parse` with `feature_version=(3, 9)` refuses 3.10's grammar, such as a `match` statement. It is a best-effort check that the
host Python limits, so a release still runs the suite on 3.9 once (row 4 of the rows file).
An `X | Y` annotation parses there but fails when the module runs, unless the module has `from __future__ import
annotations`, so that is searched apart.
"""

import ast
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
#: The oldest Python spark promises (README.md, pyproject.toml).
FLOOR = (3, 9)


def sources():
    return sorted(ROOT.glob("scripts/**/*.py")) + sorted(ROOT.glob("tools/*.py"))


def floor_problem(text, name):
    """`name:line why` when `text` does not parse as Python FLOOR, else None."""
    try:
        ast.parse(text, name, feature_version=FLOOR)
    except SyntaxError as newer:
        return "%s:%s %s" % (name, newer.lineno, newer.msg)
    return None


def union_annotations(tree):
    """The lines of each `X | Y` annotation, in a module without `from __future__ import annotations`."""
    if any(isinstance(node, ast.ImportFrom) and node.module == "__future__" and any(a.name == "annotations" for a in node.names)
           for node in tree.body):
        return []
    annotations = [node.annotation for node in ast.walk(tree) if isinstance(node, (ast.AnnAssign, ast.arg)) and node.annotation]
    annotations += [node.returns for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.returns]
    return sorted({one.lineno for one in annotations
                   if any(isinstance(part, ast.BinOp) and isinstance(part.op, ast.BitOr) for part in ast.walk(one))})


class PythonFloorTest(unittest.TestCase):
    def test_every_script_and_tool_parses_as_python_3_9(self):
        refused = [floor_problem(source.read_text(), str(source.relative_to(ROOT))) for source in sources()]
        self.assertEqual([one for one in refused if one], [])

    def test_the_parse_refuses_a_match_statement_and_passes_3_9_code(self):
        self.assertRegex(floor_problem("match a:\n    case 1:\n        pass\n", "s") or "", r"^s:[0-9]+ ")
        self.assertIsNone(floor_problem("x = {**a, **b}\n", "s"))

    def test_no_annotation_needs_python_3_10(self):
        found = ["%s:%d" % (source.relative_to(ROOT), line) for source in sources()
                 for line in union_annotations(ast.parse(source.read_text()))]
        self.assertEqual(found, [])

    def test_the_search_finds_a_union_annotation_and_lets_a_future_import_through(self):
        self.assertEqual(union_annotations(ast.parse("x: str | None = None\ndef f(a: int | str) -> bytes | None: pass\n")), [1, 2])
        self.assertEqual(union_annotations(ast.parse("from __future__ import annotations\nx: str | None = None\n")), [])


if __name__ == "__main__":
    unittest.main()
