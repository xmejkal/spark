"""
The suite cannot pass by asking the code to confirm itself (P54).

Two ways it could, both found by an outside reading rather than by any test:

* **A test that builds its expected value from the module under test.** `test_flash_image` read
  the filesystem back at `flash_image.FILESYSTEM_OFFSET` — the very number the module wrote it at.
  Move the offset and the test moves with it; the one figure that must match MicroPython's own
  partition table was guarded by nothing. Mutation testing is blind to this by construction: a
  mutation on the constant moves both sides of the assertion.
* **A file no mutation ever touched.** Every table names the files it mutates; a script named by
  none has never been shown to have a test that bites. `flash_image.py` and `check_bom.py` were
  two such, under a green suite.

Both are mechanical, so both are tests: a reading that needs an agent is not run, and one that runs
in a second is.
"""

import ast
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = {path.stem for path in (ROOT / "scripts").glob("*.py")}

#: Names that are vocabulary, not values: the outcomes every tool shares, which a test MUST name
#: rather than restate — `outcomes.py` is where they are decided, and every script re-exports them.
VOCABULARY = {"OK", "PROBLEMS", "COULD_NOT_RUN", "SKIPPED", "EXIT_OK", "EXIT_PROBLEMS",
              "EXIT_COULD_NOT_RUN", "EXIT_FOR", "STATUS_FOR", "EXIT_IMPOSSIBLE", "EXIT_MISMATCH",
              "EXIT_INVALID"}

#: A module constant a test may read, and why that is not the test confirming the code by itself.
#: Every entry is a reason someone can argue with; an unlisted one fails, naming file and line.
SAMENESS = "the claim is that two modules share ONE object (assertIs) — sameness, not a value"
AGREEMENT = ("compared with a second source that has to say the same — the data file, a document, "
             "another module — so a wrong value fails as disagreement")
STRUCTURE = "a path, a fixture or a registry the test walks — where to look, not what to expect"
RELATION = ("a relation between tuning numbers (this costs less than that), which is the design "
            "decision itself; the numbers' values are not the expectation")
MAY_READ = {
    "assign_pins.BUS_LINES": SAMENESS, "parts.BUSES": SAMENESS,
    "assign_pins.CAPABILITIES": SAMENESS, "parts.CAPABILITIES": SAMENESS,
    "check_footprints.PACKAGE_POWER_W": SAMENESS, "check_physics.PACKAGE_POWER_W": SAMENESS,
    "init_project.CIRCUIT_PATHS": SAMENESS, "design.CIRCUIT_PATHS": SAMENESS,
    "check_all.CONVENTIONS": AGREEMENT, "emit_board.VIA_HOLE_MM": AGREEMENT,
    "emit_board.VIA_PAD_MM": AGREEMENT, "copper.COPPER_THICKNESS_MM": AGREEMENT,
    "init_project.PINNED_TSCI": AGREEMENT + "; that the version EXISTS is P51's cold run, not this",
    "init_project.PINNED_CORE": AGREEMENT + "; that the version EXISTS is P51's cold run, not this",
    "check_physics.I2C_RISE_CONSTANT": "asserted against ln(0.7/0.3), computed in the test from the I2C specification",
    "check_physics.VOLTAGE_DERATING": "an ordering the engineering requires (a tantalum is derated harder than a ceramic)",
    "copper.MIN_TRACE_WIDTH_MM": "a floor the result must exceed — the property, not the value",
    "copper.DEFAULT_RISE_C": "an input to the arithmetic under test, whose expected result (2.9 A) is a literal",
    "emit_footprint.PLATING_THICKNESS_MM": "the plated-hole rule's own inputs, which test_fab pins to the data file",
    "emit_footprint.HEADER_PIN_DIAGONAL_MM": "the plated-hole rule's own inputs, which test_fab pins to the data file",
    "parts.DEFAULT_VENDOR_ORDER": "the claim is the FALLBACK: with nothing configured, the default is what is used",
    "assign_pins.ROLE_PENALTY": RELATION, "assign_pins.CAPABILITY_COST": RELATION,
    "assign_pins.CONFLICTING_ROLES": RELATION + "; and every priced role must be a role boards may declare",
    "boards.PIN_ROLES": "the vocabulary of roles a board may declare, checked against what assign_pins prices",
    "boards.CONSOLE_UART": "a role's NAME, used to build a fixture — vocabulary, not a value",
    "check_all.CHECKS": STRUCTURE, "boards.LIBRARY": STRUCTURE, "fab.FILE": STRUCTURE,
    "fab.DATA": STRUCTURE, "check_spine.REFERENCE": STRUCTURE,
    "check_spine.CONVERTER_PATHS": STRUCTURE,
    "init_project.PROJECT_TEMPLATE": STRUCTURE,
    "tools.DOWNLOADS": STRUCTURE + " — the test points it at a scratch folder and looks for the download there",
}

#: Files no mutation table names, and why that is not a hole.
UNMUTATED = {
    "agents/*.md": "instructions to a model, judged by reading; W15 checks each is named where a user looks",
    "skills/*/SKILL.md": "instructions to a model, judged by reading; W15 checks each is named where a user looks",
    "skills/*/references/*.md": "reference prose a skill loads; judged by reading, not by a test",
    "boards/README.md": "prose for a person",
    "boards/xiao-esp32-c6.json": "a board no current design uses (W14); the board contract test validates it, "
                                 "and its first design's item writes its mutations",
}


def constant_reads(path):
    """(module, NAME, line) for every UPPER_CASE attribute of a `scripts/` module a test reads."""
    tree = ast.parse(path.read_text())
    imported = {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import)
                for alias in node.names if alias.name in SCRIPTS}
    return [(node.value.id, node.attr, node.lineno) for node in ast.walk(tree)
            if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name)
            and node.value.id in imported and re.fullmatch(r"[A-Z][A-Z0-9_]+", node.attr)]


def mutated_files():
    return {entry["file"] for table in (ROOT / "tests" / "mutations").glob("*.json")
            for entry in json.loads(table.read_text())}


def shipped_files():
    for folder in ("scripts", "agents", "skills", "boards", "catalog"):
        for path in sorted((ROOT / folder).rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                yield path.relative_to(ROOT).as_posix()


class NoTestConfirmsTheCodeWithItsOwnNumbers(unittest.TestCase):
    def test_every_module_constant_a_test_reads_is_vocabulary_or_has_a_reason(self):
        unexplained = ["%s:%d %s.%s" % (path.name, line, module, name)
                       for path in sorted((ROOT / "tests").glob("test_*.py"))
                       for module, name, line in constant_reads(path)
                       if name not in VOCABULARY and "%s.%s" % (module, name) not in MAY_READ]
        self.assertEqual(unexplained, [], "a test reads the code's own number as its expectation")

    def test_every_reason_is_still_needed(self):
        read = {"%s.%s" % (module, name) for path in (ROOT / "tests").glob("test_*.py")
                for module, name, _ in constant_reads(path)}
        self.assertEqual(sorted(set(MAY_READ) - read), [], "an exception nothing needs any more")


class EveryShippedFileHasBeenShownToHaveATestThatBites(unittest.TestCase):
    def test_every_file_is_named_by_a_mutation_table_or_excepted_with_a_reason(self):
        mutated = mutated_files()
        holes = [name for name in shipped_files() if name not in mutated
                 and not any(Path(name).match(pattern) for pattern in UNMUTATED)]
        self.assertEqual(holes, [], "files no mutation has ever touched")

    def test_every_exception_still_excuses_something(self):
        names = list(shipped_files())
        unused = [pattern for pattern in UNMUTATED
                  if not any(Path(name).match(pattern) for name in names)]
        self.assertEqual(unused, [], "an exception that matches no file any more")


if __name__ == "__main__":
    unittest.main()
