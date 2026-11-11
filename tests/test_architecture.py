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

import ast
import subprocess
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
    test_v1_a_value_message_error_is_made_with_a_constant_template = rule_test("V1")

    def test_v1_has_no_baseline_entry_so_a_new_raw_site_cannot_be_hidden_in_it(self):
        self.assertEqual([key for key in self.baseline if key.startswith("V1:")], [])

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

    def test_x2_output_in_spark_outside_a_renderer_the_terminal_adapter_and_run_cli(self):
        root = planted({
            "scripts/spark/core/cli.py": "import sys\n\n\ndef run_cli():\n    print(sys.stderr)\n\n\ndef other():\n    def run_cli():\n        print(1)\n",
            "scripts/spark/core/out.py": (
                "import sys\nimport sys as system\n\n\ndef main():\n    pass\n\n\ndef run_cli():\n    print(sys.stderr)\n\n\n"
                'class Service:\n    """Service: runs."""\n\n    def run_cli(self):\n        print(2)\n\n\n'
                "def run():\n    print(\"x\")\n    answer = input()\n"
                "    sys.stdout.write(answer)\n    system.stderr.write(answer)\n    sys.exit(1)\n    sys.stdin.readline()\n"
                "    raise SystemExit(2)\n\n\n"
                'class Draw:\n    """Renderer: draws lines."""\n\n    def draw(self):\n        print("ok")\n\n\n'
                'class Terminal:\n    """Adapter: the tty."""\n\n    def ask(self):\n        return input()\n'),
            "scripts/other.py": "def run():\n    print(\"x\")\n"})
        self.assertEqual(measure.breaches(root), {
            "X2:scripts/spark/core/cli.py:print": 1,  # the nested run_cli; the top-level one in cli.py is X2's named function
            "X2:scripts/spark/core/out.py:input": 1, "X2:scripts/spark/core/out.py:main": 1, "X2:scripts/spark/core/out.py:print": 3,
            "X2:scripts/spark/core/out.py:sys.stderr": 2,
            "X2:scripts/spark/core/out.py:readline": 1, "X2:scripts/spark/core/out.py:sys.exit": 1,
            "X2:scripts/spark/core/out.py:sys.stdin": 1, "X2:scripts/spark/core/out.py:sys.stdout": 1,
            "X2:scripts/spark/core/out.py:SystemExit": 1})

    def test_u1_a_leaf_that_imports_a_script_matching_with_drawer_a_moved_guard_and_a_missing_leaf(self):
        # the layout since wave 6 (P721): drawer and matching in a package, imported through it
        root = planted({
            "scripts/outcomes.py": "from spark.sourcing import drawer\n",
            "scripts/spark/sourcing/drawer.py": "def clean(x):\n    return x\n",
            "scripts/spark/sourcing/matching.py": "from spark.sourcing import drawer\n",
            "scripts/parts.py": "def one_line(x):\n    return x\n",
            "scripts/spark/sourcing/user.py": "import parts as library\nfrom spark.sourcing.drawer import clean\n"
                                              "from spark.sourcing import drawer\n\nlibrary.one_line(clean)\ndrawer.CONTROL\n"})
        self.assertEqual(measure.breaches(root), {
            "U1:scripts/outcomes.py:imports-drawer": 1, "U1:scripts/outcomes.py:imports-spark": 1,
            "U1:scripts/spark/sourcing/matching.py:imports-drawer": 1,
            "U1:scripts/spark/sourcing/user.py:reads-drawer.CONTROL": 1,
            "U1:scripts/spark/sourcing/user.py:reads-drawer.clean": 1,
            "U1:scripts/spark/sourcing/user.py:reads-parts.one_line": 1})
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

    def test_v1_a_call_of_a_value_message_error_or_a_subclass_with_a_template_that_is_no_constant(self):
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
                            '    if a == 8:\n        stop = OneError("%s is bad" % a)\n        raise stop\n'
                            '    if a == 9:\n        raise OneError(template="%s is bad" % a)\n'
                            '    if a == 10:\n        raise OneError(template="%s is bad", a=a)\n'
                            '    if a == 11:\n        template = "%s is bad" % a\n        raise OneError(template)\n'
                            '    if a == 12:\n        raise OneError("%s is bad", **b)\n'
                            '    raise OneError.of_lines([a])\n\n\n'
                            'def say(template, *values):\n    return OneError(template, *values)\n')})
        self.assertEqual(measure.breaches(root), {"V1:scripts/raises.py:OneError": 6, "V1:scripts/raises.py:TwoError": 3})

    def test_v1_only_text_guards_may_hand_a_bare_template_on(self):
        helper = 'def flat_line(template, *values):\n    return ValueMessageError(template, *values)\n'
        root = planted({"scripts/spark/core/text_guards.py": 'class ValueMessageError(Exception):\n    """Error: x."""\n\n\n' + helper,
                        "scripts/other.py": 'from spark.core.text_guards import ValueMessageError\n\n\n' + helper}, leaves=False)
        self.assertEqual({key: each for key, each in measure.breaches(root).items() if key.startswith("V1")},
                         {"V1:scripts/other.py:ValueMessageError": 1})

    def test_v1_a_baselined_count_that_the_code_no_longer_has_fails_as_gone(self):
        self.assertEqual(measure.compare({}, {"V1:scripts/x.py:OneError": 2}),
                         [measure.Drift("V1:scripts/x.py:OneError", "entry-gone", None, 2)])


class TheBenchAreaTest(unittest.TestCase):
    """W5-3a (P679, S11): the bench's modules live in `scripts/spark/bench/`, and each one imports alone."""
    BENCH = ROOT / "scripts" / "spark" / "bench"

    def test_no_bench_module_stays_in_scripts(self):
        # W6-R3a (P718): board_codes, read by bench modules alone, is the bench's leaf; board_pads and
        # deploy_record_store are the records area's
        left = sorted(path.name for pattern in ("board_*.py", "deploy_*.py") for path in (ROOT / "scripts").glob(pattern))
        self.assertEqual(left, [])
        self.assertTrue((self.BENCH / "board_codes.py").is_file())

    def test_no_bench_module_has_a_second_copy_in_scripts(self):
        # the review of #915: flasher.py or image_evidence.py back in scripts/ would pass the glob above
        twins = sorted(path.name for path in self.BENCH.glob("*.py")
                       if path.name != "__init__.py" and (ROOT / "scripts" / path.name).exists())
        self.assertEqual(twins, [])

    def test_the_next_lines_name_the_cli_in_scripts(self):
        # the refuter of #915: next_text builds the CLI's path from its own file, two folders up since the move
        code = "from spark.bench import board_envelope; print(board_envelope.next_text([{'op': 'look', 'argv': [], 'why': 'w'}]))"
        run = subprocess.run([sys.executable, "-c", code], cwd=ROOT / "scripts", capture_output=True, text=True,
                             timeout=60, stdin=subprocess.DEVNULL)
        self.assertIn(str(ROOT / "scripts" / "look.py"), run.stdout, run.stderr)

    def test_each_bench_module_imports_alone(self):
        each_module_imports_alone(self, "bench")


def each_module_imports_alone(test, area):
    """A child Python per module of `scripts/spark/<area>/`: an import cycle shows as "partially initialized module", which
    a warm process hides."""
    for module in sorted(path.stem for path in (ROOT / "scripts" / "spark" / area).glob("*.py") if path.name != "__init__.py"):
        with test.subTest(module=module):
            run = subprocess.run([sys.executable, "-c", "import spark.%s.%s" % (area, module)], cwd=ROOT / "scripts",
                                 capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
            test.assertEqual(run.returncode, 0, run.stderr)


# --- MVP ---
class TheFirmwareAreaTest(unittest.TestCase):
    """W6-F3 (P685): the firmware's modules live in `scripts/spark/firmware/`, its `__init__.py` imports nothing, and each
    module imports alone. `scripts/` keeps the three CLIs only."""
    FIRMWARE = ROOT / "scripts" / "spark" / "firmware"

    #: Each CLI's own top-level functions: `main` and what only it uses to parse and print. A library function back in a
    #: CLI, under any name, fails the check.
    CLIS = {"flash_image.py": ["main", "project_here"], "import_firmware.py": ["main", "render"], "run_scenario.py": ["main"]}

    def test_scripts_holds_the_three_clis_and_no_firmware_library_module(self):
        names = {path.stem for path in self.FIRMWARE.glob("*.py") if path.name != "__init__.py"}
        self.assertEqual(sorted(names & {path.stem for path in (ROOT / "scripts").glob("*.py")}), [])
        self.assertFalse((ROOT / "scripts" / "stand_in").exists())
        for cli, own in self.CLIS.items():
            with self.subTest(cli=cli):
                tree = ast.parse((ROOT / "scripts" / cli).read_text())
                self.assertEqual(sorted(node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))), own)

    def test_the_area_s_init_imports_nothing(self):
        # an __init__ that imports its modules made the cycles of wave 5 (P676 rows 4 and 10)
        tree = ast.parse((self.FIRMWARE / "__init__.py").read_text())
        self.assertEqual([node.lineno for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))], [])

    def test_each_firmware_module_imports_alone(self):
        each_module_imports_alone(self, "firmware")
# --- end MVP ---


# --- MVP ---
class TheBreadboardAreaTest(unittest.TestCase):
    """W6-B3 (P694): the breadboard's modules live in `scripts/spark/breadboard/`, its `__init__.py` imports nothing, and
    each module imports alone. `scripts/` keeps the CLI `breadboard.py`, which defines `main` only."""
    BREADBOARD = ROOT / "scripts" / "spark" / "breadboard"
    #: The eleven modules of the area, by the names of its page (`areas/breadboard.md`); `part_shape` came in W6-D3b.
    MODULES = ["bench_changes", "breadboard_codes", "drawing", "drawing_catalog", "drawing_match", "kept_moves",
               "part_pictures", "part_shape", "sheet", "tabbed_page", "wiring_steps"]

    def test_scripts_holds_the_cli_and_no_breadboard_library_module(self):
        self.assertEqual(sorted(path.stem for path in self.BREADBOARD.glob("*.py") if path.name != "__init__.py"), self.MODULES)
        old = ["part_pictures.py", "part_shape.py", "tabbed_page.py"] + [path.name for path in (ROOT / "scripts").glob("breadboard*.py")]
        self.assertEqual(sorted(name for name in old if (ROOT / "scripts" / name).exists()), ["breadboard.py"])
        self.assertEqual(sorted(set(self.MODULES) & {path.stem for path in (ROOT / "scripts").glob("*.py")}), [])
        tree = ast.parse((ROOT / "scripts" / "breadboard.py").read_text())
        self.assertEqual([node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))], ["main"])

    def test_the_area_s_init_imports_nothing(self):
        # an __init__ that imports its modules made the cycles of wave 5 (P676 rows 4 and 10)
        tree = ast.parse((self.BREADBOARD / "__init__.py").read_text())
        self.assertEqual([node.lineno for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))], [])

    def test_each_breadboard_module_imports_alone(self):
        each_module_imports_alone(self, "breadboard")
# --- end MVP ---


# --- MVP ---
class TheChecksAreaTest(unittest.TestCase):
    """W6-C3 (P695): the checks' modules live in `scripts/spark/checks/`, its `__init__.py` imports nothing, and each
    module imports alone. `scripts/` keeps the six CLIs and `check_spine.py`, and each CLI defines `main` only."""
    CHECKS = ROOT / "scripts" / "spark" / "checks"
    #: The modules of the area, by the names of its page (`areas/checks.md`).
    MODULES = ["build_check", "check", "check_codes", "order_check", "physics_board", "physics_check", "rules_check", "vendor_pins_check"]
    CLIS = ["check_all.py", "check_bom.py", "check_footprints.py", "check_physics.py", "check_vendor_pins.py",
            "compare_design.py"]

    def test_scripts_holds_the_six_clis_and_no_checks_library_module(self):
        self.assertEqual(sorted(path.stem for path in self.CHECKS.glob("*.py") if path.name != "__init__.py"), self.MODULES)
        scripts = ROOT / "scripts"
        self.assertEqual(sorted(path.name for path in [*scripts.glob("check_*.py"), *scripts.glob("compare_design.py")]),
                         sorted(self.CLIS + ["check_spine.py"]))
        self.assertEqual(sorted(set(self.MODULES) & {path.stem for path in scripts.glob("*.py")}), [])
        for cli in self.CLIS:
            with self.subTest(cli=cli):
                tree = ast.parse((scripts / cli).read_text())
                self.assertEqual([node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))],
                                 ["main"])

    def test_the_area_s_init_imports_nothing(self):
        # an __init__ that imports its modules made the cycles of wave 5 (P676 rows 4 and 10)
        tree = ast.parse((self.CHECKS / "__init__.py").read_text())
        self.assertEqual([node.lineno for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))], [])

    def test_each_checks_module_imports_alone(self):
        each_module_imports_alone(self, "checks")
# --- end MVP ---


# --- MVP ---
class TheDesignAreaTest(unittest.TestCase):
    """W6-D3a (P702), W6-D3b (P703), W6-D3c (P704) and W6-S3b (P721): the design values, the emitters, the needs and the
    goal handlers live in `scripts/spark/design/`, its `__init__.py` imports nothing, and each module imports alone.
    `scripts/` keeps the three CLIs."""
    DESIGN = ROOT / "scripts" / "spark" / "design"
    #: The modules of the area so far, by the names of its page (`areas/design.md`).
    MODULES = ["audit_records", "board_components", "board_emitter", "board_sections", "copper", "design_codes", "design_operations", "fab",
               "find_offers", "footprint_emitter", "goal_handlers", "list_boards", "list_needs", "loader", "match_needs", "need_requirements",
               "needs", "netlist", "pin_assigner", "power_rails", "restricted_pins", "show_offer", "tally_cost", "write_requirements"]
    #: Each CLI's own top-level functions: `main` and what only it uses to print. A library function back in a CLI, under
    #: any name, fails the check.
    CLIS = {"assign_pins.py": ["main"], "emit_board.py": ["main"], "emit_footprint.py": ["_report", "main"]}

    def test_scripts_holds_the_cli_and_no_design_library_module(self):
        self.assertEqual(sorted(path.stem for path in self.DESIGN.glob("*.py") if path.name != "__init__.py"), self.MODULES)
        scripts = ROOT / "scripts"
        old = ["assign_pins.py", "copper.py", "design.py", "design_codes.py", "emit_board.py", "emit_footprint.py", "fab.py",
               "needs.py", "netlist.py", "restricted_pins.py"]
        self.assertEqual([name for name in old if (scripts / name).exists()], sorted(self.CLIS))
        self.assertEqual(sorted(set(self.MODULES) & {path.stem for path in scripts.glob("*.py")}), [])
        for cli, own in self.CLIS.items():
            with self.subTest(cli=cli):
                tree = ast.parse((scripts / cli).read_text())
                self.assertEqual(sorted(node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))),
                                 own)

    def test_the_area_s_init_imports_nothing(self):
        # an __init__ that imports its modules made the cycles of wave 5 (P676 rows 4 and 10)
        tree = ast.parse((self.DESIGN / "__init__.py").read_text())
        self.assertEqual([node.lineno for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))], [])

    def test_each_design_module_imports_alone(self):
        each_module_imports_alone(self, "design")

    def test_the_operations_table_maps_each_op_to_its_operation_class(self):
        # P707 (N19): the table is a module, because the area's __init__ imports nothing; a frontend reads it as bench.OPERATIONS
        code = ("from spark.core.operation import Operation; from spark.design import design_operations as d; "
                "print(sorted(d.OPERATIONS)); print([op for op, cls in d.OPERATIONS.items() if cls.name != op or not issubclass(cls, Operation)])")
        run = subprocess.run([sys.executable, "-c", code], cwd=ROOT / "scripts", capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
        self.assertEqual(run.stdout.split("\n")[:2], ["['audit', 'list-boards', 'match', 'need', 'needs', 'offer', 'requirements', 'tally']", "[]"], run.stderr)
# --- end MVP ---


# --- MVP ---
class TheBuildAreaTest(unittest.TestCase):
    """W6-U3 (P705): the build's modules live in `scripts/spark/build/`, its `__init__.py` imports nothing, and each module
    imports alone. `scripts/` keeps the two CLIs."""
    BUILD = ROOT / "scripts" / "spark" / "build"
    #: The modules of the area, by the names of its page (`areas/build.md`).
    MODULES = ["ai_files", "board_alone_input", "board_engine", "build_codes", "build_service", "kept_files", "project_setup", "stages"]
    #: Each CLI's own top-level functions: `main` and what only it uses to parse and print (`report` prints). A library
    #: function back in a CLI, under any name, fails the check.
    CLIS = {"check_spine.py": ["main", "render", "report", "timed_out_sentence"], "init_project.py": ["main"]}

    def test_scripts_holds_the_two_clis_and_no_build_library_module(self):
        self.assertEqual(sorted(path.stem for path in self.BUILD.glob("*.py") if path.name != "__init__.py"), self.MODULES)
        scripts = ROOT / "scripts"
        old = ["ai_files.py", "build_codes.py", "check_spine.py", "init_project.py"]
        self.assertEqual([name for name in old if (scripts / name).exists()], sorted(self.CLIS))
        self.assertEqual(sorted(set(self.MODULES) & {path.stem for path in scripts.glob("*.py")}), [])
        for cli, own in self.CLIS.items():
            with self.subTest(cli=cli):
                tree = ast.parse((scripts / cli).read_text())
                self.assertEqual(sorted(node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))),
                                 own)

    def test_the_area_s_init_imports_nothing(self):
        # an __init__ that imports its modules made the cycles of wave 5 (P676 rows 4 and 10)
        tree = ast.parse((self.BUILD / "__init__.py").read_text())
        self.assertEqual([node.lineno for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))], [])

    def test_each_build_module_imports_alone(self):
        each_module_imports_alone(self, "build")

    def test_the_build_runs_the_emit_board_cli_in_scripts(self):
        # run's child is the CLI two folders up from build_service, and the plugin's own library is the plugin folder
        code = ("from spark.records import board_records; from spark.build import build_service; "
                "print(build_service.EMIT_BOARD_SCRIPT); print(board_records.PLUGIN_ROOT)")
        run = subprocess.run([sys.executable, "-c", code], cwd=ROOT / "scripts", capture_output=True, text=True,
                             timeout=60, stdin=subprocess.DEVNULL)
        self.assertEqual(run.stdout.split("\n")[:2], [str(ROOT / "scripts" / "emit_board.py"), str(ROOT)], run.stderr)
# --- end MVP ---


# --- MVP ---
class TheRecordsAreaTest(unittest.TestCase):
    """W6-R3a (P718), W6-R3b (P719) and W6-S3a (P720, `record_kind`): the records' modules live in
    `scripts/spark/records/`, its `__init__.py` imports nothing, and each module imports alone. `scripts/` keeps the CLIs
    `boards.py` and `tools.py`."""
    RECORDS = ROOT / "scripts" / "spark" / "records"
    #: The modules of the area so far, by the names of its page (`areas/records.md`).
    MODULES = ["answer_operation", "board_pads", "board_records", "board_rules", "brief", "deploy_record_store", "fact_needs", "missing_facts",
               "onboard_parts", "provenance", "record_kind", "records_codes", "store", "tool_finder", "versions"]
    #: Each CLI's own top-level functions: `main` and what only it uses to print (`_validate_all` and `print_status`).
    #: `boards.py --list` runs design's `ListBoards`, imported inside `main` (P707). A library function back in a CLI,
    #: under any name, fails the check.
    CLIS = {"boards.py": ["_validate_all", "main"], "tools.py": ["main", "print_status"]}

    def test_scripts_holds_the_cli_and_no_records_library_module(self):
        modules = sorted(path.stem for path in self.RECORDS.glob("*.py") if path.name != "__init__.py")
        self.assertEqual(modules, self.MODULES)
        scripts = ROOT / "scripts"
        old = ["board_codes.py", "board_pads.py", "boards.py", "brief.py", "deploy_record_store.py", "missing_facts.py",
               "onboard_parts.py", "provenance.py", "records_codes.py", "store.py", "tools.py", "versions.py"]
        self.assertEqual([name for name in old if (scripts / name).exists()], sorted(self.CLIS))
        self.assertEqual(sorted(set(self.MODULES) & {path.stem for path in scripts.glob("*.py")}), [])
        for cli, own in self.CLIS.items():
            with self.subTest(cli=cli):
                tree = ast.parse((scripts / cli).read_text())
                defined = [node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))]
                self.assertEqual(sorted(defined), own)

    def test_the_area_s_init_imports_nothing(self):
        # an __init__ that imports its modules made the cycles of wave 5 (P676 rows 4 and 10)
        tree = ast.parse((self.RECORDS / "__init__.py").read_text())
        self.assertEqual([node.lineno for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))], [])

    def test_each_records_module_imports_alone(self):
        each_module_imports_alone(self, "records")

    def test_onboard_parts_imports_only_records_and_core(self):
        # P708: `onboard_parts` imported `sheet`, `loader` and `sim_project` from above; that half is the build's now
        tree = ast.parse((self.RECORDS / "onboard_parts.py").read_text())
        found = {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module.startswith("spark")}
        self.assertTrue(found)
        self.assertEqual([name for name in sorted(found) if name.split(".")[1] not in ("records", "core")], [])
        self.assertEqual([alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names
                          if alias.name.startswith("spark")], [])

    def test_the_plugin_folder_is_three_folders_up(self):
        # store.PLUGIN, board_records.LIBRARY and PLUGIN_ROOT read the plugin by parents[3] since the move, and
        # tool_finder.PLUGIN reads PLUGIN_ROOT (P719)
        code = ("from spark.records import board_records, store, tool_finder; print(store.PLUGIN); "
                "print(board_records.PLUGIN_ROOT); print(board_records.LIBRARY); print(tool_finder.PLUGIN)")
        run = subprocess.run([sys.executable, "-c", code], cwd=ROOT / "scripts", capture_output=True, text=True,
                             timeout=60, stdin=subprocess.DEVNULL)
        self.assertEqual(run.stdout.split("\n")[:4], [str(ROOT), str(ROOT), str(ROOT / "boards"), str(ROOT)],
                         run.stderr)
# --- end MVP ---


# --- MVP ---
class TheSourcingAreaTest(unittest.TestCase):
    """W6-S2 (P717), W6-S3a (P720) and W6-S3b (P721): the sourcing area holds the pull-up band and the part rules in
    `scripts/spark/sourcing/part_rules.py`, the part records, the part facts, the datasheets, the drawer, the part
    handlers, the matchers, the cost of a run and the leaf `sourcing_codes`. Its `__init__.py` imports nothing, and each
    module imports alone. Checks read the band from there, so no module imports the checks area for it. `scripts/` keeps
    the CLIs `cost.py`, `main` alone, and `parts.py`, its parser, its printers and the handlers that read a payload."""
    SOURCING = ROOT / "scripts" / "spark" / "sourcing"
    #: The modules of the area, by the names of its page (`areas/sourcing.md`).
    MODULES = ["datasheets", "drawer", "matching", "offers", "part_facts", "part_handlers", "part_records", "part_rules", "run_cost",
               "sourcing_codes"]
    #: `parts.py`'s own top-level functions: its parser and printer, `_op_describe`, `_op_needs_drop` on the core, the route
    #: to the Operations on the core (P707, P726), and the handlers that read a JSON payload, because reading stdin is the
    #: interface's job (P721 row 6). The text printer's rule is `record_kind.Answer.text_lines` since P726.
    PARTS_CLI = ["_not_negative", "_op_describe", "_op_drawer_import", "_op_drawer_set", "_op_fact_set", "_op_function_set",
                 "_op_needs_drop", "_op_needs_set", "_op_pick", "_parser", "_part_problem", "_read_json_input", "_say", "asked_on_the_core", "main",
                 "on_the_core"]

    def test_the_area_holds_its_modules_and_the_band_is_bound_there_alone(self):
        modules = sorted(path.stem for path in self.SOURCING.glob("*.py") if path.name != "__init__.py")
        self.assertEqual(modules, self.MODULES)
        # any binding of a name, a tuple's element too (the refuter's `PULLUP_MIN_OHM, PULLUP_MAX_OHM = 1000, 10000`)
        bound = {str(path.relative_to(ROOT)) for path in (ROOT / "scripts").rglob("*.py")
                 for node in ast.walk(ast.parse(path.read_text())) if isinstance(node, ast.Name)
                 and isinstance(node.ctx, ast.Store) and node.id in ("PULLUP_MIN_OHM", "PULLUP_MAX_OHM")}
        self.assertEqual(sorted(bound), ["scripts/spark/sourcing/part_rules.py"])
        scripts = ROOT / "scripts"
        self.assertEqual([name for name in ("cost.py", "drawer.py", "matching.py", "sourcing_codes.py")
                          if (scripts / name).exists()], ["cost.py"])
        tree = ast.parse((scripts / "cost.py").read_text())
        self.assertEqual([node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))], ["main"])

    def test_parts_py_defines_only_its_cli_and_no_module_imports_it(self):
        tree = ast.parse((ROOT / "scripts" / "parts.py").read_text())
        self.assertEqual(sorted(node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))),
                         self.PARTS_CLI)
        # `import parts`, and `from parts import x` too, at the top or lazily: the flat modules are no library any more
        importers = sorted(str(path.relative_to(ROOT)) for path in (ROOT / "scripts").rglob("*.py")
                           for node in ast.walk(ast.parse(path.read_text()))
                           if isinstance(node, ast.Import) and any(alias.name in ("parts", "drawer") for alias in node.names)
                           or isinstance(node, ast.ImportFrom) and node.level == 0 and node.module in ("parts", "drawer"))
        self.assertEqual(importers, [])

    def test_the_area_s_init_imports_nothing(self):
        # an __init__ that imports its modules made the cycles of wave 5 (P676 rows 4 and 10)
        tree = ast.parse((self.SOURCING / "__init__.py").read_text())
        self.assertEqual([node.lineno for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))], [])

    def test_each_sourcing_module_imports_alone(self):
        each_module_imports_alone(self, "sourcing")
# --- end MVP ---


if __name__ == "__main__":
    unittest.main()
