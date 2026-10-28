"""P440 (#585): `tools/measure.py` prints the P322 figures and each breach of an architecture rule, and writes the baseline.

Every test reads a tree that it plants in a temp folder, so no figure of the real code is an expectation here.
`tests/test_architecture.py` holds the real code against the baseline.

    python3 -m unittest discover -s tests
"""

import ast
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import measure  # noqa: E402

#: The modules that import nothing of spark. A planted tree holds them, or rule U1 reports each one as missing.
LEAF_NAMES = ("board_codes", "outcomes", "provenance", "text_guards", "zone_time")


def planted(files, leaves=True):
    """A temp root holding `files` ({path under the root: source}) and, unless `leaves` is False, the five leaf modules."""
    root = Path(tempfile.mkdtemp())
    if leaves:
        files = dict({"scripts/%s.py" % name: '"""A leaf."""\n' for name in LEAF_NAMES}, **files)
    for name, source in files.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(source)
    return root


def function_of(name, lines):
    """A function `name` that is exactly `lines` lines long."""
    return "def %s():\n%s" % (name, "    pass\n" * (lines - 1))


def run_main(argv, root):
    """(exit code, stdout, stderr) of measure.main(argv) on `root`."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = measure.main(argv, root)
    return code, out.getvalue(), err.getvalue()


class FiguresTest(unittest.TestCase):
    def test_the_score_line_prints(self):
        root = planted({"scripts/a.py": 'class A:\n    """Value: a thing."""\n\n\ndef main():\n    return 0\n'}, leaves=False)
        code, out, _ = run_main([], root)
        self.assertEqual(code, 0)
        self.assertEqual(out.splitlines()[-1], "SCORE classes 50% | fat CLIs 0 | thin CLIs 1 | private imports 0 | "
                                               "outcome literals 0 | roles stated 1/1")

    def test_the_figures_read_a_folder_under_scripts_and_not_the_stand_in(self):
        root = planted({"scripts/a.py": "X = 1\n", "scripts/spark/core/b.py": "Y = 1\n", "scripts/stand_in/c.py": "Z = 1\n"},
                       leaves=False)
        _, out, _ = run_main([], root)
        self.assertIn("Total: 2 modules, 2 code lines", out)
        self.assertIn("\nb ", out)
        self.assertNotIn("\nc ", out)


class RulesPrintTest(unittest.TestCase):
    def test_the_rules_print_each_breach_once(self):
        root = planted({"scripts/spark/big.py": function_of("big", 45), "scripts/ok.py": function_of("small", 3)})
        code, out, err = run_main(["--rules"], root)
        self.assertEqual((code, out, err), (0, "R1:scripts/spark/big.py:big:45\n", ""))
        self.assertFalse((root / "tests" / "architecture_baseline.json").exists())

    def test_accept_writes_the_baseline_sorted_one_line_per_entry(self):
        root = planted({"scripts/spark/b.py": function_of("big", 45), "scripts/spark/a.py": function_of("big", 46)})
        code, out, err = run_main(["--rules", "--accept"], root)
        self.assertEqual(code, 0)
        self.assertEqual((root / "tests" / "architecture_baseline.json").read_text(),
                         '{\n"R1:scripts/spark/a.py:big": 46,\n"R1:scripts/spark/b.py:big": 45\n}\n')
        self.assertEqual(out, "R1:scripts/spark/a.py:big:46\nR1:scripts/spark/b.py:big:45\n")
        self.assertEqual(err, "wrote tests/architecture_baseline.json: 2 entries\n")

    def test_accept_without_a_breach_writes_an_empty_baseline_that_reads_back(self):
        root = planted({"scripts/ok.py": function_of("small", 3)})
        run_main(["--rules", "--accept"], root)
        self.assertEqual(json.loads((root / "tests" / "architecture_baseline.json").read_text()), {})
        self.assertEqual(measure.read_baseline(root), {})

    def test_accept_goes_with_rules(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as stopped:
            measure.main(["--accept"], planted({}))
        self.assertEqual(stopped.exception.code, 2)

    def test_a_missing_baseline_reads_as_empty(self):
        self.assertEqual(measure.read_baseline(planted({})), {})


class ReadersTest(unittest.TestCase):
    def test_the_old_reads_find_each_way_to_the_old_module(self):
        tree = ast.parse("import parts as parts_library\nimport drawer\nfrom drawer import TAGS_MAX\n"
                                 "parts_library.one_line(x)\ndrawer.clean(y)\ndrawer.listing()\n")
        self.assertEqual(measure.old_reads(tree), {"parts.one_line", "drawer.clean", "drawer.TAGS_MAX"})

    def test_functions_come_with_their_class_and_their_outer_function(self):
        tree = ast.parse("class A:\n    def m(self):\n        def inner():\n            pass\n\n\ndef f():\n    pass\n")
        self.assertEqual([name for name, _ in measure.functions_of(tree)], ["A.m", "A.m.inner", "f"])

    def test_the_role_word_drops_its_colon_and_its_full_stop(self):
        for doc, word in (('"""Value: x."""', "Value"), ('"""Store. x."""', "Store"), ("", "")):
            with self.subTest(doc=doc):
                self.assertEqual(measure.role_word_of(ast.parse("class A:\n    %s\n    pass\n" % doc).body[0]), word)


if __name__ == "__main__":
    unittest.main()
