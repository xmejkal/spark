"""P440 (#585), S3 of refactor plan v2: spark's code is held to the architecture rules, against a baseline that only shrinks.

`tools/measure.py` reads `scripts/` and `tests/` with `ast` and lists each breach with its measured value. This test holds
the list against `tests/architecture_baseline.json`: a breach the baseline does not list fails, a value above the baseline
fails, and so does an entry the code no longer has. A value below the baseline passes. After a fix, run
`python3 tools/measure.py --rules --accept` and commit the shorter file. The rules, in one sentence each, are `measure.RULES`;
the table with their ids is
`docs/discovery/2026-10-19-p323-target-architecture/architecture/notes.md`.

Not here yet: R4, R5, U2, X1, X3, C4, T3 and T5. Each waits for the code it measures (an Operation module, a registry, a
Fake per Strategy) and enters with the slice that first needs it.

    python3 -m unittest discover -s tests
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import measure  # noqa: E402
from planted_tree import function_of, planted  # noqa: E402

# --- MVP ---
ROOT = Path(__file__).resolve().parent.parent


def rule_test(rule):
    """A test method that holds the code to `rule` against the baseline; its docstring is the rule's sentence."""
    def test(self):
        self.holds(rule)
    test.rule = rule
    test.__doc__ = "%s: %s" % (rule, measure.RULES[rule])
    return test


class ArchitectureRules(unittest.TestCase):
    """Spark's own code, against each rule and the baseline. One method per rule in `measure.RULES`."""

    @classmethod
    def setUpClass(cls):
        cls.found = measure.breaches(ROOT)
        cls.baseline = measure.read_baseline(ROOT)

    def holds(self, rule):
        said = [measure.explain(d) for d in measure.compare(self.found, self.baseline, rule) if d.kind in measure.FAILING]
        self.assertEqual(said, [])

    test_r1_a_function_a_module_and_a_main_are_short = rule_test("R1")
    test_r2_nesting_is_at_most_three_deep = rule_test("R2")
    test_r3_a_function_takes_at_most_five_parameters = rule_test("R3")
    test_r6_a_class_docstring_starts_with_a_role_word = rule_test("R6")
    test_t1_only_an_adapter_touches_the_outside = rule_test("T1")
    test_t2_no_test_file_adds_a_mock_patch = rule_test("T2")
    test_t4_code_never_branches_on_what_is_imported = rule_test("T4")
    test_x2_spark_holds_no_main_print_or_exit_outside_a_renderer = rule_test("X2")
    test_u1_the_leaves_import_nothing_of_spark = rule_test("U1")
    test_c1_a_file_name_is_unique_and_an_exception_name_ends_in_error = rule_test("C1")
    test_c3_an_exit_code_has_no_second_name = rule_test("C3")
    test_v1_a_value_message_error_is_raised_with_a_constant_template = rule_test("V1")

    def test_every_rule_in_the_table_has_a_test_method_and_no_method_has_none(self):
        held = {method.rule for method in vars(type(self)).values() if hasattr(method, "rule")}
        self.assertEqual(held, set(measure.RULES))

    def test_every_baseline_entry_belongs_to_a_rule_and_the_file_is_one_sorted_line_per_entry(self):
        text = (ROOT / measure.BASELINE).read_text()
        entries = measure.read_baseline(ROOT)
        self.assertEqual(list(entries), sorted(entries))
        self.assertEqual(len(text.splitlines()), len(entries) + 2)
        self.assertEqual({key.split(":")[0] for key in entries} - set(measure.RULES), set())


class TheBaselineOnlyShrinksTest(unittest.TestCase):
    """A planted tree with one breach, against baselines that are right, too high, too low and out of date."""

    KEY = "R1:scripts/spark/big.py:big"

    def compare(self, baseline):
        root = planted({"scripts/spark/big.py": function_of("big", 45)})
        return measure.compare(measure.breaches(root), baseline)

    def test_a_breach_at_its_baseline_value_passes(self):
        self.assertEqual(self.compare({self.KEY: 45}), [])

    def test_a_breach_the_baseline_does_not_list_fails(self):
        self.assertEqual(self.compare({}), [measure.Drift(self.KEY, "new-breach", 45, None)])

    def test_a_value_that_rose_fails(self):
        self.assertEqual(self.compare({self.KEY: 44}), [measure.Drift(self.KEY, "value-rose", 45, 44)])

    def test_a_value_that_fell_passes_and_may_be_written_back(self):
        found = self.compare({self.KEY: 50})
        self.assertEqual(found, [measure.Drift(self.KEY, "value-fell", 45, 50)])
        self.assertEqual([d for d in found if d.kind in measure.FAILING], [])

    def test_a_baseline_entry_the_code_no_longer_has_fails(self):
        found = self.compare({self.KEY: 45, "R1:scripts/spark/gone.py:old": 61})
        self.assertEqual(found, [measure.Drift("R1:scripts/spark/gone.py:old", "entry-gone", None, 61)])
        self.assertEqual(found, [d for d in found if d.kind in measure.FAILING])

    def test_the_drift_of_one_rule_leaves_the_others_out(self):
        self.assertEqual(measure.compare({"R2:a.py:f": 4}, {"R1:a.py:f": 61}, "R2"), [measure.Drift("R2:a.py:f", "new-breach", 4, None)])

    def test_each_kind_is_told_with_its_rule_its_limit_the_file_the_name_and_the_values(self):
        said = {kind: measure.explain(measure.Drift(self.KEY, kind, 45, 44)) for kind in ("new-breach", "value-rose", "entry-gone", "value-fell")}
        for kind, sentence in said.items():
            with self.subTest(kind=kind):
                self.assertIn("R1: a function, a module and a main are short (a function 40 lines in scripts/spark/ and 60 elsewhere, "
                              "a module 600, a main 15)", sentence)
                self.assertIn("big in scripts/spark/big.py", sentence)
        self.assertIn("is 45 and the baseline does not list it", said["new-breach"])
        self.assertIn("python3 tools/measure.py --rules` lists every breach", said["new-breach"])
        self.assertIn("rose from 44 to 45", said["value-rose"])
        self.assertIn("lists big in scripts/spark/big.py at 44 and the code no longer has it", said["entry-gone"])
        self.assertIn("--rules --accept", said["entry-gone"])
        self.assertIn("fell from 44 to 45", said["value-fell"])


class PlantedBreachesTest(unittest.TestCase):
    """For each rule, a tree with its breach (and the cases that are none), and the key and value that `measure` lists."""

    def test_r1_a_long_function_a_long_module_and_a_long_main_each_once(self):
        root = planted({
            "scripts/spark/limit.py": function_of("exact", 40),
            "scripts/spark/over.py": function_of("over", 41),
            "scripts/old.py": function_of("exact", 60) + "\n\n" + function_of("over", 61),
            "scripts/door.py": function_of("main", 16),
            "scripts/fat.py": function_of("main", 70),
            "scripts/thin.py": function_of("main", 15),
            "scripts/module.py": "X = 1\n" * 601,
        })
        self.assertEqual(measure.breaches(root), {
            "R1:scripts/spark/over.py:over": 41, "R1:scripts/old.py:over": 61,
            "R1:scripts/door.py:main": 16, "R1:scripts/fat.py:main": 70, "R1:scripts/module.py:<module>": 601})

    def test_r2_a_nest_of_four_and_an_elif_chain_that_is_one_level(self):
        root = planted({"scripts/nest.py": (
            "def deep(a):\n    for x in a:\n        if x:\n            while x:\n                with x:\n                    pass\n\n\n"
            "def chain(a):\n    if a == 1:\n        pass\n    elif a == 2:\n        pass\n    elif a == 3:\n"
            "        if a:\n            if a:\n                pass\n")})
        self.assertEqual(measure.breaches(root), {"R2:scripts/nest.py:deep": 4})

    def test_r3_six_parameters_without_self_and_five_that_are_none(self):
        root = planted({"scripts/many.py": (
            'class Many:\n    """Value: x."""\n\n    def six(self, a, b, c, d, e, f):\n        pass\n\n'
            "    def five(self, a, b, c, d, e):\n        pass\n")})
        self.assertEqual(measure.breaches(root), {"R3:scripts/many.py:Many.six": 6})

    def test_r6_a_class_without_a_role_word_or_a_docstring_by_its_qualified_name(self):
        root = planted({"scripts/roles.py": (
            'class A:\n    """Value: x."""\n\n    class Inner:\n        pass\n\n\nclass B:\n    """Does things."""\n\n    class Inner:\n        pass\n\n\n'
            'class C:\n    pass\n\n\nif True:\n    class C:\n        pass\n')})
        self.assertEqual(measure.breaches(root), {
            "R6:scripts/roles.py:A.Inner": 1, "R6:scripts/roles.py:B": 1, "R6:scripts/roles.py:B.Inner": 1, "R6:scripts/roles.py:C": 2})

    def test_t1_the_outside_touched_outside_an_adapter(self):
        root = planted({"scripts/touch.py": (
            "import os\nimport subprocess\nimport subprocess as sp\nimport time\nimport urllib.parse\nimport urllib.request\n"
            "from datetime import date, datetime as clock\nfrom pathlib import Path\n\n\n"
            'class Runner:\n    """Adapter: wraps a tool."""\n\n    def go(self):\n        return subprocess.run(["x"]), time.sleep(1), clock.now()\n\n\n'
            'def outside():\n    subprocess.run(["y"])\n    sp.run(["z"])\n    time.monotonic()\n    time.strftime("%Y")\n    time.strftime("%Y", when)\n    time.ctime(when)\n    time.asctime()\n'
            '    urllib.parse.quote("a")\n    urllib.request.urlopen("u")\n    clock.now()\n    date.today()\n'
            '    open("f", "w")\n    open("g")\n    Path("p").write_text("x")\n    os.getenv("B")\n    return os.environ["A"]\n')})
        self.assertEqual(measure.breaches(root), {
            "T1:scripts/touch.py:datetime": 2, "T1:scripts/touch.py:file-write": 2, "T1:scripts/touch.py:os.environ": 1,
            "T1:scripts/touch.py:os.getenv": 1, "T1:scripts/touch.py:subprocess": 2, "T1:scripts/touch.py:time": 3,
            "T1:scripts/touch.py:urllib": 1})

    def test_t2_the_mock_patches_of_a_test_file_but_not_those_on_the_environment(self):
        root = planted({"tests/test_a.py": (
            "import os\nimport sys\nfrom unittest import mock\n\n\n@mock.patch(\"a.b\")\ndef test_x(b):\n"
            "    with mock.patch.object(a, \"b\"):\n        pass\n"
            "    with mock.patch.dict(os.environ, {\"A\": \"1\"}):\n        pass\n"
            "    with mock.patch.dict(sys.modules, {}):\n        pass\n")})
        self.assertEqual(measure.breaches(root), {"T2:tests/test_a.py:mock.patch": 3})

    def test_t4_a_branch_on_what_is_imported_counts_each_read_once(self):
        root = planted({"scripts/branch.py": (
            "import sys\n\nif \"unittest\" in sys.modules:\n    pass\nX = 1 if \"x\" in sys.modules else 2\n"
            "Y = sys.modules\nif sys.version_info:\n    pass\n"
            "if \"a\" in (1 if \"b\" in sys.modules else 2):\n    pass\n")})
        self.assertEqual(measure.breaches(root), {"T4:scripts/branch.py:sys.modules": 3})

    def test_x2_output_in_spark_outside_a_renderer_and_the_terminal_consent(self):
        root = planted({
            "scripts/spark/core/out.py": (
                "import sys\nimport sys as system\n\n\ndef main():\n    pass\n\n\ndef run():\n    print(\"x\")\n    answer = input()\n"
                "    sys.stdout.write(answer)\n    system.stderr.write(answer)\n    sys.exit(1)\n    sys.stdin.readline()\n"
                "    raise SystemExit(2)\n\n\n"
                'class Draw:\n    """Renderer: draws lines."""\n\n    def draw(self):\n        print("ok")\n\n\n'
                'class TerminalConsentStrategy:\n    """Strategy: asks on the terminal."""\n\n    def ask(self):\n        return input()\n'),
            "scripts/other.py": "def run():\n    print(\"x\")\n"})
        self.assertEqual(measure.breaches(root), {
            "X2:scripts/spark/core/out.py:input": 1, "X2:scripts/spark/core/out.py:main": 1, "X2:scripts/spark/core/out.py:print": 1,
            "X2:scripts/spark/core/out.py:readline": 1, "X2:scripts/spark/core/out.py:sys.exit": 1,
            "X2:scripts/spark/core/out.py:sys.stdin": 1, "X2:scripts/spark/core/out.py:sys.stdout": 1,
            "X2:scripts/spark/core/out.py:sys.stderr": 1, "X2:scripts/spark/core/out.py:SystemExit": 1})

    def test_u1_a_leaf_that_imports_a_script_matching_with_drawer_a_moved_guard_and_a_missing_leaf(self):
        root = planted({
            "scripts/outcomes.py": "import drawer\n", "scripts/drawer.py": "def clean(x):\n    return x\n",
            "scripts/matching.py": "import drawer\n", "scripts/parts.py": "def one_line(x):\n    return x\n",
            "scripts/user.py": "import parts as library\nfrom drawer import clean\n\nlibrary.one_line(clean)\n"})
        self.assertEqual(measure.breaches(root), {
            "U1:scripts/outcomes.py:imports-drawer": 1, "U1:scripts/matching.py:imports-drawer": 1,
            "U1:scripts/user.py:reads-drawer.clean": 1, "U1:scripts/user.py:reads-parts.one_line": 1})
        self.assertEqual(measure.breaches(planted({}, leaves=False))["U1:scripts:no-leaf-outcomes"], 1)

    def test_c1_a_basename_in_two_folders_and_an_exception_not_ending_in_error(self):
        root = planted({
            "scripts/a/dup.py": '"""x"""\n', "scripts/b/dup.py": '"""x"""\n', "scripts/a/__init__.py": '"""x"""\n',
            "scripts/b/__init__.py": '"""x"""\n',
            "scripts/oops.py": ('class Oops(Exception):\n    """Error: x."""\n\n\nclass Sub(Oops):\n    """Error: x."""\n\n\n'
                                'class FineError(Exception):\n    """Error: x."""\n\n\nclass Thing:\n    """Value: x."""\n\n    class Oops(Exception):\n        """Error: x."""\n')})
        self.assertEqual(measure.breaches(root), {
            "C1:scripts/a/dup.py:basename": 1, "C1:scripts/b/dup.py:basename": 1,
            "C1:scripts/oops.py:Oops": 1, "C1:scripts/oops.py:Sub": 1, "C1:scripts/oops.py:Thing.Oops": 1})

    def test_c3_a_second_name_for_an_exit_code(self):
        root = planted({"scripts/exits.py": (
            "import outcomes\nfrom outcomes import EXIT_PROBLEMS as EXIT_BAD, EXIT_OK as EXIT_OK, EXIT_FOR\n\n"
            "EXIT_THIS = outcomes.EXIT_OK\nEXIT_LOCAL = 3\n")})
        self.assertEqual(measure.breaches(root), {"C3:scripts/exits.py:EXIT_BAD": 1, "C3:scripts/exits.py:EXIT_THIS": 1})

    def test_v1_a_raise_of_a_value_message_error_or_a_subclass_with_a_template_that_is_no_constant(self):
        root = planted({"scripts/raises.py": (
                            'class ValueMessageError(Exception):\n    """Error: x."""\n\n\n'
                            'class OneError(ValueMessageError):\n    """Error: x."""\n\n\n'
                            'class TwoError(OneError):\n    """Error: x."""\n\n\n'
                            'class OtherError(Exception):\n    """Error: x."""\n\n\n'
                            "def f(a, b):\n"
                            '    if a == 1:\n        raise OneError("%s is bad", a)\n'
                            '    if a == 2:\n        raise OneError("%s is bad" % a)\n'
                            '    if a == 3:\n        raise TwoError(f"{a} is bad")\n'
                            '    if a == 4:\n        raise TwoError(b, a)\n'
                            '    if a == 5:\n        raise TwoError("%s is " "bad" % a)\n'
                            '    if a == 6:\n        raise OtherError("%s is bad" % a)\n'
                            '    if a == 7:\n        raise OneError()\n'
                            '    raise OneError.of_lines([a])\n')})
        self.assertEqual(measure.breaches(root), {"V1:scripts/raises.py:OneError": 1, "V1:scripts/raises.py:TwoError": 3})

    def test_v1_a_baselined_count_that_the_code_no_longer_has_fails_as_gone(self):
        self.assertEqual(measure.compare({}, {"V1:scripts/x.py:OneError": 2}),
                         [measure.Drift("V1:scripts/x.py:OneError", "entry-gone", None, 2)])


if __name__ == "__main__":
    unittest.main()
