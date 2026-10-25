"""P389: provenance.fact_problems, the one rule a part record and a board record check a fact by."""

import ast
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import provenance  # noqa: E402


class FactProblemsTest(unittest.TestCase):
    def test_a_fact_with_its_value_verified_flag_and_source_holds(self):
        self.assertEqual(provenance.fact_problems("facts.a", {"value": 3, "verified": True, "source": "page 4"}), [])

    def test_each_missing_key_is_one_problem(self):
        self.assertEqual(
            provenance.fact_problems("facts.a", {}),
            ["facts.a has no 'value' — a number with no provenance is an opinion",
             "facts.a has no 'verified' — a number with no provenance is an opinion",
             "facts.a has no 'source' — a number with no provenance is an opinion"])

    def test_a_verified_fact_with_no_value_is_one_problem(self):
        self.assertEqual(provenance.fact_problems("facts.a", {"value": None, "verified": True, "source": "s"}),
                         ["facts.a is marked verified but has no value"])

    def test_an_unverified_value_with_no_reason_is_one_problem(self):
        self.assertEqual(
            provenance.fact_problems("facts.a", {"value": 3, "verified": False, "source": "s"}),
            ["facts.a is an unverified value with no why_it_matters; say what depends on it or do not carry the number"])

    def test_an_unverified_value_with_a_reason_holds(self):
        self.assertEqual(provenance.fact_problems(
            "facts.a", {"value": 3, "verified": False, "source": "s", "why_it_matters": "sizes the sprite"}), [])

    def test_an_unverified_fact_with_no_value_needs_no_reason(self):
        self.assertEqual(provenance.fact_problems("facts.a", {"value": None, "verified": False, "source": "s"}), [])

    def test_a_fact_that_is_no_object_is_one_problem(self):
        for fact in ("s", 3, None, ["value"], True):
            with self.subTest(fact=fact):
                self.assertEqual(provenance.fact_problems("facts.a", fact),
                                 ["facts.a is %r, but it is an object" % (fact,)])

    def test_provenance_imports_no_spark_module(self):
        tree = ast.parse((ROOT / "scripts" / "provenance.py").read_text())
        imported = {name.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import) for name in node.names}
        imported |= {node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module}
        spark = {path.stem for path in (ROOT / "scripts").glob("*.py")}
        self.assertEqual(imported & spark, set())


if __name__ == "__main__":
    unittest.main()
