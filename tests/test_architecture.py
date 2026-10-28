"""P440 (#585), S3 of refactor plan v2: spark's code is held to the architecture rules, against a baseline that only shrinks.

`tools/measure.py` reads `scripts/` and `tests/` with `ast` and lists each breach with its measured value. This test holds
the list against `tests/architecture_baseline.json`: a breach the baseline does not list fails, a value above the baseline
fails, and so does a value below it and an entry the code no longer has, so the file shrinks with the fix. After a fix,
run `python3 tools/measure.py --rules --accept` and commit the shorter file. The rules are the table in
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
from test_measure import function_of, planted  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
HOW_TO_FIX = ("fix the code; when a value fell or an entry is gone, run `python3 tools/measure.py --rules --accept` "
              "and commit the shorter tests/architecture_baseline.json")


class ArchitectureRules(unittest.TestCase):
    """Spark's own code, against each rule and the baseline."""

    @classmethod
    def setUpClass(cls):
        cls.found = measure.breaches(ROOT)
        cls.baseline = measure.read_baseline(ROOT)

    def holds(self, rule):
        said = ["%s %s: now %s, the baseline has %s" % (d.key, d.kind, d.found, d.allowed)
                for d in measure.drift(self.found, self.baseline, rule)]
        self.assertEqual(said, [], "%s -- %s" % (rule, HOW_TO_FIX))

    def test_a_function_is_short_and_so_is_a_module_and_a_main(self):
        """R1: a function in scripts/spark/ is at most 40 lines, an old script's 60, a module 600, a `main` 15."""
        self.holds("R1")

    def test_nesting_is_at_most_three_deep(self):
        """R2."""
        self.holds("R2")

    def test_a_function_takes_at_most_five_parameters(self):
        """R3."""
        self.holds("R3")

    def test_a_class_docstring_starts_with_a_role_word(self):
        """R6."""
        self.holds("R6")

    def test_only_an_adapter_runs_a_program_reads_the_clock_or_the_environment_or_writes_a_file(self):
        """T1."""
        self.holds("T1")

    def test_no_test_file_adds_a_mock_patch(self):
        """T2."""
        self.holds("T2")

    def test_code_never_branches_on_what_is_imported(self):
        """T4."""
        self.holds("T4")

    def test_spark_holds_no_main_no_print_and_no_exit_outside_a_renderer(self):
        """X2: nothing is under scripts/spark/ yet, so the baseline holds no X2 entry."""
        self.holds("X2")

    def test_the_leaves_import_nothing_of_spark_and_no_script_reads_a_moved_guard_from_its_old_module(self):
        """U1."""
        self.holds("U1")

    def test_a_file_name_is_unique_and_an_exception_name_ends_in_error(self):
        """C1."""
        self.holds("C1")

    def test_an_exit_code_has_no_second_name(self):
        """C3."""
        self.holds("C3")

    def test_every_baseline_entry_belongs_to_a_rule_and_the_file_is_one_sorted_line_per_entry(self):
        text = (ROOT / measure.BASELINE).read_text()
        entries = measure.read_baseline(ROOT)
        self.assertEqual(list(entries), sorted(entries))
        self.assertEqual(len(text.splitlines()), len(entries) + 2)
        self.assertEqual({key.split(":")[0] for key in entries} - {"R1", "R2", "R3", "R6", "T1", "T2", "T4", "X2", "U1", "C1", "C3"},
                         set())


class TheBaselineOnlyShrinksTest(unittest.TestCase):
    """A planted tree with one breach, against baselines that are right, too high, too low and out of date."""

    KEY = "R1:scripts/spark/big.py:big"

    def drift(self, baseline):
        root = planted({"scripts/spark/big.py": function_of("big", 45)})
        return measure.drift(measure.breaches(root), baseline)

    def test_a_breach_at_its_baseline_value_passes(self):
        self.assertEqual(self.drift({self.KEY: 45}), [])

    def test_a_breach_the_baseline_does_not_list_fails(self):
        self.assertEqual(self.drift({}), [measure.Drift(self.KEY, "new-breach", 45, None)])

    def test_a_value_that_rose_fails(self):
        self.assertEqual(self.drift({self.KEY: 44}), [measure.Drift(self.KEY, "value-rose", 45, 44)])

    def test_a_value_that_fell_fails_until_the_baseline_is_lowered(self):
        self.assertEqual(self.drift({self.KEY: 50}), [measure.Drift(self.KEY, "value-fell", 45, 50)])

    def test_a_baseline_entry_the_code_no_longer_has_fails(self):
        self.assertEqual(self.drift({self.KEY: 45, "R1:scripts/spark/gone.py:old": 61}),
                         [measure.Drift("R1:scripts/spark/gone.py:old", "entry-gone", None, 61)])

    def test_the_drift_of_one_rule_leaves_the_others_out(self):
        self.assertEqual(measure.drift({"R2:a.py:f": 4}, {"R1:a.py:f": 61}, "R2"), [measure.Drift("R2:a.py:f", "new-breach", 4, None)])


class PlantedBreachesTest(unittest.TestCase):
    """For each rule, a tree with its breach (and the cases that are none), and the key and value that `measure` lists."""

    def test_r1_a_long_function_a_long_module_and_a_long_main(self):
        root = planted({
            "scripts/spark/limit.py": function_of("exact", 40),
            "scripts/spark/over.py": function_of("over", 41),
            "scripts/old.py": function_of("exact", 60) + "\n\n" + function_of("over", 61),
            "scripts/door.py": function_of("main", 16),
            "scripts/module.py": "X = 1\n" * 601,
        })
        self.assertEqual(measure.breaches(root), {
            "R1:scripts/spark/over.py:over": 41, "R1:scripts/old.py:over": 61,
            "R1:scripts/door.py:main/cli": 16, "R1:scripts/module.py:<module>": 601})

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

    def test_r6_a_class_without_a_role_word_or_a_docstring(self):
        root = planted({"scripts/roles.py": (
            'class A:\n    """Value: x."""\n\n\nclass B:\n    """Does things."""\n\n\nclass C:\n    pass\n')})
        self.assertEqual(measure.breaches(root), {"R6:scripts/roles.py:B": 1, "R6:scripts/roles.py:C": 1})

    def test_t1_the_outside_touched_outside_an_adapter(self):
        root = planted({"scripts/touch.py": (
            "import os\nimport subprocess\nimport time\nfrom pathlib import Path\n\n\n"
            'class Runner:\n    """Adapter: wraps a tool."""\n\n    def go(self):\n        return subprocess.run(["x"])\n\n\n'
            'def outside():\n    subprocess.run(["y"])\n    time.monotonic()\n    open("f", "w")\n    open("g")\n'
            '    Path("p").write_text("x")\n    return os.environ["A"]\n')})
        self.assertEqual(measure.breaches(root), {
            "T1:scripts/touch.py:file-write": 2, "T1:scripts/touch.py:os.environ": 1,
            "T1:scripts/touch.py:subprocess": 1, "T1:scripts/touch.py:time": 1})

    def test_t2_the_mock_patches_of_a_test_file_but_not_those_on_the_environment(self):
        root = planted({"tests/test_a.py": (
            "import os\nimport sys\nfrom unittest import mock\n\n\n@mock.patch(\"a.b\")\ndef test_x(b):\n"
            "    with mock.patch.object(a, \"b\"):\n        pass\n"
            "    with mock.patch.dict(os.environ, {\"A\": \"1\"}):\n        pass\n"
            "    with mock.patch.dict(sys.modules, {}):\n        pass\n")})
        self.assertEqual(measure.breaches(root), {"T2:tests/test_a.py:mock.patch": 3})

    def test_t4_a_branch_on_what_is_imported(self):
        root = planted({"scripts/branch.py": (
            "import sys\n\nif \"unittest\" in sys.modules:\n    pass\nX = 1 if \"x\" in sys.modules else 2\n"
            "Y = sys.modules\nif sys.version_info:\n    pass\n")})
        self.assertEqual(measure.breaches(root), {"T4:scripts/branch.py:sys.modules": 2})

    def test_x2_output_in_spark_outside_a_renderer_and_the_terminal_consent(self):
        root = planted({
            "scripts/spark/core/out.py": (
                "import sys\n\n\ndef main():\n    pass\n\n\ndef run():\n    print(\"x\")\n    answer = input()\n"
                "    sys.stdout.write(answer)\n    sys.exit(1)\n    sys.stdin.readline()\n\n\n"
                'class Draw:\n    """Renderer: draws lines."""\n\n    def draw(self):\n        print("ok")\n\n\n'
                'class TerminalConsentStrategy:\n    """Strategy: asks on the terminal."""\n\n    def ask(self):\n        return input()\n'),
            "scripts/other.py": "def run():\n    print(\"x\")\n"})
        self.assertEqual(measure.breaches(root), {
            "X2:scripts/spark/core/out.py:input": 1, "X2:scripts/spark/core/out.py:main": 1, "X2:scripts/spark/core/out.py:print": 1,
            "X2:scripts/spark/core/out.py:readline": 1, "X2:scripts/spark/core/out.py:sys.exit": 1,
            "X2:scripts/spark/core/out.py:sys.stdin": 1, "X2:scripts/spark/core/out.py:sys.stdout": 1})

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
                                'class FineError(Exception):\n    """Error: x."""\n\n\nclass Thing:\n    """Value: x."""\n')})
        self.assertEqual(measure.breaches(root), {
            "C1:scripts/a/dup.py:basename": 1, "C1:scripts/b/dup.py:basename": 1,
            "C1:scripts/oops.py:Oops": 1, "C1:scripts/oops.py:Sub": 1})

    def test_c3_a_second_name_for_an_exit_code(self):
        root = planted({"scripts/exits.py": (
            "import outcomes\nfrom outcomes import EXIT_PROBLEMS as EXIT_BAD, EXIT_OK as EXIT_OK, EXIT_FOR\n\n"
            "EXIT_THIS = outcomes.EXIT_OK\nEXIT_LOCAL = 3\n")})
        self.assertEqual(measure.breaches(root), {"C3:scripts/exits.py:EXIT_BAD": 1, "C3:scripts/exits.py:EXIT_THIS": 1})


if __name__ == "__main__":
    unittest.main()
