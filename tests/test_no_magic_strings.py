"""P260 (#282): code in scripts/ decides on a named constant, never on a sentence written into the comparison."""

import ast
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
#: The str methods and `re` functions whose first argument is a text to look for.
#: `re.compile` is not one: its pattern is a named constant once it is kept.
SEARCHES = {"startswith", "endswith", "removeprefix", "removesuffix", "find", "rfind", "index", "count", "search", "match",
            "fullmatch", "findall"}


def _sentences(node):
    """The string literals with a space in them that this operand is, or holds in a tuple, a list or a set."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str) and " " in node.value:
        return [node]
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        return [one for element in node.elts for one in _sentences(element)]
    return []


def magic_strings(source, name):
    """Each `file:line text` where code compares, or looks for, a literal sentence."""
    found = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Compare):
            operands = [node.left] + node.comparators
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in SEARCHES:
            operands = node.args[:1]
        elif hasattr(ast, "MatchValue") and isinstance(node, ast.MatchValue):  # 3.10's match; a 3.9 script has none
            operands = [node.value]
        else:
            continue
        found += ["%s:%d %r" % (name, one.lineno, one.value) for operand in operands for one in _sentences(operand)]
    return found


class NoMagicStringsTest(unittest.TestCase):
    def test_no_script_decides_on_a_literal_sentence(self):
        found = [one for script in sorted(SCRIPTS.rglob("*.py"))
                 for one in magic_strings(script.read_text(), script.relative_to(SCRIPTS).as_posix())]
        self.assertEqual(found, [], "name each as a constant beside its source (patterns-and-names.md, P260)")

    def test_the_guard_sees_each_shape(self):
        source = ('a == "x y"\n"x y" in a\na in ("b", "x y")\na.startswith("x y")\nre.search("x y", a)\n'
                  'a.startswith(("x y", "b"))\na in ["x y"]\na.find("x y")\n')
        seen = ["s:1", "s:2", "s:3", "s:4", "s:5", "s:6", "s:7", "s:8"]
        if hasattr(ast, "MatchValue"):  # Python 3.10 or newer: a match statement parses
            source, seen = source + 'match a:\n    case "x y":\n        pass\n', seen + ["s:10"]
        self.assertEqual([one.split(" ")[0] for one in magic_strings(source, "s")], seen)

    def test_the_guard_passes_a_name_and_a_word(self):
        self.assertEqual(magic_strings('a == X_Y\na == "xy"\na.startswith(X + " ")\nb = "x y"\n', "s"), [])


if __name__ == "__main__":
    unittest.main()
