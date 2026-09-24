"""
Proof that a board is found, validated, and resolved to one place.

A board definition is the file every other check compares things TO, so the rules about where it
comes from matter as much as what is in it. Two are load-bearing and are asserted here.

**A project's own definition always wins over the shipped library.** A definition you verified
yourself must never be silently replaced by a shared one, and a project must never change
behaviour because the plugin was updated.

**The resolved board lands at one known path.** Before that, the search and the schema check
existed twice — once in Python and once, partially, in TypeScript — and the library would have
forced a third copy to learn about a second directory. Resolving once means every consumer reads
a file instead of re-implementing a lookup.

    python3 -m unittest discover -s tests
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import boards  # noqa: E402

LIBRARY_BOARD = "firebeetle2-esp32s3"


def project(active=LIBRARY_BOARD, own=None):
    """A project directory: a selection, and optionally its own definitions."""
    root = Path(tempfile.mkdtemp())
    (root / "boards").mkdir()
    (root / "boards" / "active.json").write_text(json.dumps({"schema": 1, "board": active}))
    for board_id, definition in (own or {}).items():
        (root / "boards" / (board_id + ".json")).write_text(json.dumps(definition))
    return root


def definition(board_id, **overrides):
    """A definition that satisfies the contract, so tests can break one thing at a time."""
    return dict({
        "schema": 1, "id": board_id, "name": "Test Board", "chip": "esp32",
        "micropython_port": "ESP32_GENERIC", "wokwi_part_type": "board-test",
        "wokwi_pin_naming": "gpio",
        "pins": {"D0": 0, "D1": 1},
        "wake_capable_gpio": [0, 1], "adc_gpio": [0],
        "physical": {"footprint_module": "X", "footprint_export": "X"},
    }, **overrides)


class WhereABoardComesFromTest(unittest.TestCase):
    def test_a_project_with_only_a_selection_gets_the_library(self):
        # The whole point of shipping a library: adopt a verified board without copying a file
        # you would then have to maintain.
        root = project()
        self.assertEqual(boards.load(root)["id"], LIBRARY_BOARD)
        self.assertEqual(boards.definition_path(root).parent, boards.LIBRARY)

    def test_the_library_is_listed_as_available(self):
        self.assertIn(LIBRARY_BOARD, boards.available(project()))

    def test_a_projects_own_definition_wins_over_the_library(self):
        # A definition you verified yourself must never be replaced by a shared one, and a
        # project must not change behaviour because the plugin was updated.
        root = project(own={LIBRARY_BOARD: definition(LIBRARY_BOARD, name="Mine")})
        self.assertEqual(boards.load(root)["name"], "Mine")
        self.assertEqual(boards.definition_path(root).parent, root / "boards")

    def test_a_board_nobody_has_is_refused_with_the_alternatives(self):
        with self.assertRaises(boards.BoardError) as refused:
            boards.load(project(active="no-such-board"))
        self.assertIn("no board definition", str(refused.exception))
        self.assertIn(LIBRARY_BOARD, str(refused.exception))

    def test_a_selection_naming_nothing_is_refused(self):
        root = project()
        (root / "boards" / "active.json").write_text(json.dumps({"schema": 1}))
        with self.assertRaises(boards.BoardError):
            boards.active_id(root)


class ResolvingTest(unittest.TestCase):
    def test_resolve_writes_the_board_to_one_known_path(self):
        root = project()
        written = boards.resolve(root)
        self.assertEqual(written, root / ".spark" / "board.json")
        self.assertEqual(json.loads(written.read_text())["id"], LIBRARY_BOARD)

    def test_the_resolved_file_says_it_is_generated(self):
        # It is derived. A file that looks hand-written invites being hand-edited.
        root = project()
        resolved = json.loads(boards.resolve(root).read_text())
        self.assertIn("GENERATED", resolved["//generated"])
        # And it must not have clobbered the definition's own comment.
        self.assertIn("//", resolved)

    def test_resolving_an_invalid_board_writes_nothing(self):
        root = project(active="broken", own={"broken": {"schema": 1, "id": "broken"}})
        with self.assertRaises(boards.BoardError):
            boards.resolve(root)
        self.assertFalse((root / ".spark" / "board.json").exists(),
                         "a board that fails the contract must not reach consumers")


class TheContractTest(unittest.TestCase):
    """Rules a definition must satisfy before anything downstream is allowed to read it."""

    def _problems(self, board_id="b", **overrides):
        root = project(active=board_id, own={board_id: definition(board_id, **overrides)})
        return boards.validate(json.loads((root / "boards" / (board_id + ".json")).read_text()),
                               root / "boards" / (board_id + ".json"))

    def test_a_good_definition_passes(self):
        self.assertEqual(self._problems(), [])

    def test_a_wrong_schema_version_is_refused_rather_than_read_hopefully(self):
        problems = self._problems(schema=99)
        self.assertTrue(any("schema" in p for p in problems))

    def test_an_id_that_disagrees_with_the_filename_is_caught(self):
        problems = self._problems(id="something-else")
        self.assertTrue(any("filename" in p for p in problems))

    def test_a_pin_that_is_not_a_number_is_caught(self):
        problems = self._problems(pins={"D0": "zero"})
        self.assertTrue(any("not a GPIO number" in p for p in problems))

    def test_two_labels_on_one_gpio_are_allowed(self):
        # Real and common: on the FireBeetle both A4 and SS are GPIO10.
        self.assertEqual(self._problems(pins={"A4": 10, "SS": 10}), [])

    def test_a_decision_in_a_facts_file_is_caught(self):
        # The rule the README states, mechanised. `wake_on_high` follows from how the buttons are
        # wired, not from the board — it was removed from one board file and left in the other,
        # and validation said ok for a day.
        problems = self._problems(deep_sleep={"wake_on_high": False})
        self.assertTrue(any("DECISION" in p for p in problems),
                        "a decision must not be allowed to live in a facts file")

    def test_fab_readiness_is_separate_from_being_valid(self):
        # Firmware work must not be blocked by an unverified footprint, and an unverified
        # footprint must not reach a gerber.
        board = definition("b", physical={"footprint_module": None, "footprint_export": None})
        path = Path(tempfile.mkdtemp()) / "b.json"
        path.write_text(json.dumps(board))
        self.assertEqual(boards.validate(board, path), [])
        self.assertTrue(boards.validate(board, path, for_fab=True))


class TheShippedLibraryTest(unittest.TestCase):
    def test_every_board_in_the_library_satisfies_its_own_contract(self):
        for path in sorted(boards.LIBRARY.glob("*.json")):
            with self.subTest(board=path.stem):
                problems = boards.validate(json.loads(path.read_text()), path)
                self.assertEqual(problems, [], "%s: %s" % (path.stem, problems))


if __name__ == "__main__":
    unittest.main()
