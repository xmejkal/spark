"""
Proof that the BOM check bites.

The BOM is the one artifact that stops being a design and becomes an order. Every other check in
this plugin reads the design; nothing read what the design was about to buy — and on a real board
the exported package assigned one supplier part number to two different capacitances. The part in
question is 100 nF, the schematic wanted 1 uF for a filter whose corner the design's own comment
depends on, and at 100 nF that corner moves by a factor of ten.

The checks here are deliberately the ones that need no supplier lookup, so they run offline and
cannot rot when a catalogue changes. What this refuses to do is claim a part number is CORRECT:
proving that needs the catalogue, and a check that silently stops verifying when a network call
fails is worse than no check.

    python3 -m unittest discover -s tests
"""

import csv
import io
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import check_bom  # noqa: E402

COLUMNS = ["Designator", "Comment", "Value", "Footprint", "JLCPCB Part #"]


def rows(*lines):
    """`("C1", "100n", "C14663")` -> a BOM row dict."""
    return [dict(zip(COLUMNS, [designator, value, value, "cap0603", part]))
            for designator, value, part in lines]


def package(bom_rows, name="bom.csv"):
    """A fab package on disk, so the reader is exercised rather than bypassed."""
    text = io.StringIO()
    writer = csv.DictWriter(text, fieldnames=COLUMNS)
    writer.writeheader()
    writer.writerows(bom_rows)

    path = Path(tempfile.mkdtemp()) / "fab.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(name, text.getvalue())
        archive.writestr("Edge_Cuts.gbr", "G04 not a real gerber*")
    return path


class DuplicateSupplierPartTest(unittest.TestCase):
    """One part number standing for two values is a contradiction on its face."""

    def test_the_same_part_for_two_values_is_caught(self):
        problems = check_bom.check_duplicate_parts(rows(
            ("C1", "100n", "C14663"), ("C2", "100n", "C14663"), ("C3", "1u", "C14663")))
        self.assertEqual(len(problems), 1)
        self.assertIn("C14663", problems[0])
        self.assertIn("2 different values", problems[0])
        # It has to name the odd one out, or nobody knows which line to fix.
        self.assertIn("C3", problems[0])

    def test_the_same_part_for_the_same_value_many_times_is_normal(self):
        self.assertEqual(check_bom.check_duplicate_parts(rows(
            ("C1", "100n", "C14663"), ("C2", "100n", "C14663"))), [])

    def test_different_parts_for_different_values_are_fine(self):
        self.assertEqual(check_bom.check_duplicate_parts(rows(
            ("C1", "100n", "C14663"), ("C2", "1u", "C5199872"))), [])

    def test_lines_with_no_supplier_part_are_not_compared(self):
        # A hand-fitted module has neither, and must not collide with another hand-fitted module.
        self.assertEqual(check_bom.check_duplicate_parts(rows(
            ("U1", "", ""), ("U2", "", ""))), [])


class UnbuildableLineTest(unittest.TestCase):
    """
    A value nobody can source.

    Keyed on having a value, not on a list of component names — the version of this that shipped
    with one project's designators in a regex was dead code, because every name it listed was
    already skipped for having no value.
    """

    def test_a_value_with_no_supplier_part_is_caught(self):
        problems = check_bom.check_missing_parts(rows(("R1", "10k", "")))
        self.assertEqual(len(problems), 1)
        self.assertIn("cannot be ordered", problems[0])

    def test_a_hand_fitted_part_with_no_value_is_not_a_problem(self):
        # Modules, connectors and headers carry no value and are fitted by a person.
        self.assertEqual(check_bom.check_missing_parts(rows(("U1", "", ""))), [])

    def test_a_part_the_designer_excluded_is_simply_absent(self):
        # `doNotPlace` removes the line from the BOM entirely, so there is nothing to report and
        # no project-specific list to maintain.
        self.assertEqual(check_bom.check_missing_parts([]), [])


class DesignWarningsBecomeFatalAtFabTest(unittest.TestCase):
    def _circuit(self, *elements):
        path = Path(tempfile.mkdtemp()) / "circuit.json"
        path.write_text(json.dumps(list(elements)))
        return path

    def test_a_supplier_footprint_mismatch_is_fatal_once_it_is_an_order(self):
        # tscircuit emits this as a warning: it matched a real part whose land does not fit the
        # footprint drawn. That is a warning while designing and a scrapped part once ordered.
        path = self._circuit({"type": "supplier_footprint_mismatch_warning",
                              "message": "0805 does not match supplier footprint"})
        problems = check_bom.check_design_warnings(path)
        self.assertEqual(len(problems), 1)
        self.assertIn("supplier footprint", problems[0])

    def test_other_warnings_are_left_alone(self):
        path = self._circuit({"type": "source_refdes_convention_warning", "message": "meh"})
        self.assertEqual(check_bom.check_design_warnings(path), [])

    def test_a_missing_circuit_is_not_treated_as_clean(self):
        # Asked for a file that is not there, it must not report zero problems as if it looked.
        # This asserted `== []` — that exact failure — under this exact comment. The name and the
        # comment were both right and only the assertion disagreed with them, so it stayed green.
        with self.assertRaises(FileNotFoundError):
            check_bom.check_design_warnings(Path("/nonexistent/circuit.json"))


class EndToEndTest(unittest.TestCase):
    def test_a_real_package_is_read_and_a_contradiction_reported(self):
        path = package(rows(("C1", "100n", "C14663"), ("C2", "1u", "C14663")))
        self.assertEqual(check_bom.main([str(path)]), check_bom.EXIT_PROBLEMS)

    def test_a_clean_package_passes(self):
        path = package(rows(("C1", "100n", "C14663"), ("C2", "1u", "C5199872")))
        self.assertEqual(check_bom.main([str(path)]), check_bom.EXIT_OK)

    def test_a_missing_package_is_could_not_run_not_ok(self):
        self.assertEqual(check_bom.main(["/nonexistent/fab.zip"]), check_bom.EXIT_COULD_NOT_RUN)
        self.assertNotEqual(check_bom.EXIT_COULD_NOT_RUN, check_bom.EXIT_OK)


class APartWhoseFootprintCannotSayWhichPadIsWhichTest(unittest.TestCase):
    """
    The value rule exempts anything without a value, because headers, connectors and plug-in
    modules legitimately have none and their footprint says everything about them.

    A semiconductor is the opposite. `sot23` does not say which pad is the gate — a real SOT-23
    P-FET is gate, source, drain, and the tool that drew this project's high-side switch bound
    pad 1 to the drain. Fitting any actual part would put the load on the gate and a GPIO on the
    drain, shorting a 2 A rail through it. The line had no value, so it was exempt, and nothing
    in the whole suite looked at it.
    """

    def test_a_semiconductor_with_no_part_number_is_caught(self):
        problems = check_bom.check_missing_parts(
            [{"Designator": "Q1", "Value": "", "Footprint": "sot23", "JLCPCB Part #": ""}])
        self.assertEqual(len(problems), 1)
        self.assertIn("does not say which pad", problems[0])

    def test_a_semiconductor_with_a_part_number_is_fine(self):
        self.assertEqual(check_bom.check_missing_parts(
            [{"Designator": "Q1", "Value": "", "Footprint": "sot23",
              "JLCPCB Part #": "C15127"}]), [])

    def test_a_header_with_no_value_and_no_part_is_still_exempt(self):
        # The exemption has to survive, or every hand-fitted module and connector cries wolf.
        for footprint in ("headermodule6", "jst_ph_2", "pinrow5"):
            with self.subTest(footprint=footprint):
                self.assertEqual(check_bom.check_missing_parts(
                    [{"Designator": "J1", "Value": "", "Footprint": footprint,
                      "JLCPCB Part #": ""}]), [])

    def test_a_passive_with_a_value_is_still_caught_by_the_original_rule(self):
        problems = check_bom.check_missing_parts(
            [{"Designator": "C1", "Value": "100nF", "Footprint": "0603", "JLCPCB Part #": ""}])
        self.assertIn("has a value", problems[0])


if __name__ == "__main__":
    unittest.main()
