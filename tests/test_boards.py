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

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  P172: this process's temp folder, removed at exit

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

    def test_a_selection_holding_TWO_boards_is_refused(self):
        """
        `if not board_id` was the only guard, and a non-empty list is truthy.

        Putting both boards in the one file that chooses the board is the first thing anyone with
        two boards tries. `--id` then printed `['firebeetle2-esp32s3', 'xiao-esp32-c6']` and exited
        0 — and `boards/README.md` offers `--id` to Make and every other consumer to interpolate,
        so that repr goes straight into a path. `--validate` said `ok` twice, and `--list` silently
        dropped the `*` marking the active board: an absent character as the only signal.
        """
        root = project()
        (root / "boards" / "active.json").write_text(
            json.dumps({"schema": 1, "board": ["firebeetle2-esp32s3", "xiao-esp32-c6"]}))
        with self.assertRaises(boards.BoardError) as caught:
            boards.active_id(root)
        self.assertIn("ONE board", str(caught.exception))

    def test_the_refusal_says_what_to_do_with_two_boards(self):
        # A refusal nobody can act on is only marginally better than a wrong answer, and "two
        # boards" is a real thing to want — a car and its remote.
        root = project()
        (root / "boards" / "active.json").write_text(
            json.dumps({"schema": 1, "board": ["a", "b"]}))
        with self.assertRaises(boards.BoardError) as caught:
            boards.active_id(root)
        self.assertIn("two projects", str(caught.exception))

    def test_a_selection_holding_a_number_is_refused_too(self):
        # The check is on the TYPE, not on lists specifically.
        root = project()
        (root / "boards" / "active.json").write_text(json.dumps({"schema": 1, "board": 7}))
        with self.assertRaises(boards.BoardError):
            boards.active_id(root)

    def test_an_ordinary_string_selection_still_works(self):
        self.assertEqual(boards.active_id(project()), "firebeetle2-esp32s3")


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

    def test_a_power_pad_naming_no_rail_is_refused(self):
        # The generator skipped such a pad with `continue`, wiring the processor's pad to
        # nothing in silence. Refused here, where the board file is read.
        problems = self._problems(power_pads={"GND1": {"rail": "ground"}, "3V3": {}})
        self.assertTrue(any("power_pads.3V3" in p for p in problems), problems)
        self.assertFalse(any("power_pads" in p for p in
                             self._problems(power_pads={"GND1": {"rail": "ground"}})))

    def test_a_power_pad_rail_that_is_no_name_is_refused(self):
        # P87's attribute half: the pad's rail is the net its trace is written to, `to="net.<RAIL>"`
        problems = self._problems(power_pads={"GND1": {"rail": "ground"}, "VCC": {"rail": 'motor" pcbX={(globalThis.x = 1, 0)} y="'}})
        self.assertEqual([p for p in problems if "power_pads" in p], [
            "power_pads.VCC rail is 'motor\" pcbX={(globalThis.x = 1, 0)} y=\"', but a rail is a name — letters, digits and _ "
            "(ground, logic, motor): the board is written with it as code"])

    def test_a_label_a_pad_an_export_or_an_id_that_is_no_name_is_refused(self):
        # P87's attribute half: board.tsx is written with `.Mcu > .<label>`, `.Mcu > .<pad>`, `import { <export> }` and
        # `<export name="Mcu">`; the id names the board's file and heads the footprint generated from it
        crafted = 'D3" pcbX={(globalThis.x = 1, 0)} y="'
        for overrides, said in (
                ({"pins": {crafted: 0}}, "pins key %r is not a name — letters, digits and _ (D3, SDA, A0): the board is written "
                                         "with it as code" % crafted),
                ({"power_pads": {crafted: {"rail": "ground"}}}, "power_pads key %r is not a name — letters, digits and _ (3V3, "
                                                                "GND1, VCC): the board is written with it as code" % crafted),
                ({"physical": {"footprint_module": "X", "footprint_export": crafted}},
                 "physical.footprint_export is %r, but it is a name — letters, digits and _ (FireBeetle2Esp32S3): the board is "
                 "written with it as code" % crafted)):
            with self.subTest(said=said):
                self.assertIn(said, self._problems(**overrides))
        for board_id in ('x"y', "Bad_Board", "XIAO"):
            with self.subTest(id=board_id):
                self.assertIn("id is %r, but an id is a plain key — lower-case letters, digits and - (firebeetle2-esp32s3): "
                              "files are named by it, and it is written into the footprint generated from it" % board_id,
                              self._problems(board_id=board_id))

    def test_a_crafted_label_carried_through_the_whole_file_is_refused_by_the_name_rule_itself(self):
        # it was refused only when it sat on no pad (header_order) or had no simulator name (wokwi_power_pins); carried
        # consistently through all of them it passed, and the rule that refuses it now is the name's own
        crafted = 'D3" pcbX={(globalThis.x = 1, 0)} y="'
        path = ROOT / "boards" / "firebeetle2-esp32s3.json"
        for key, old in (("pins", "D3"), ("power_pads", "VCC")):
            with self.subTest(key=key):
                board = json.loads(path.read_text())
                board[key][crafted] = board[key].pop(old)
                if key == "power_pads":
                    board["wokwi_power_pins"][crafted] = board["wokwi_power_pins"].pop(old)
                for row, labels in board["physical"]["header_order"].items():
                    if not row.startswith("//"):
                        board["physical"]["header_order"][row] = [crafted if label == old else label for label in labels]
                self.assertEqual([p for p in boards.validate(board, path) if crafted in p],
                                 ["%s key %r is not a name — letters, digits and _ (%s): the board is written with it as code"
                                  % (key, crafted, "D3, SDA, A0" if key == "pins" else "3V3, GND1, VCC")])

    def test_a_drill_that_is_no_number_is_refused(self):
        # concern 1: the footprint's comment quotes the drawing's drill, `NOT the <drill_mm> mm`; it is a number, never text
        physical = {"footprint_module": "X", "footprint_export": "X"}
        crafted = '0.9\nexport const injected = 1 //'
        self.assertIn("physical.header.drill_mm is %r, but it is a number of millimetres (0.9): the footprint generated from "
                      "it is written with it" % crafted, self._problems(physical=dict(physical, header={"drill_mm": crafted})))
        for drill in (0.9, 1):
            with self.subTest(drill=drill):
                self.assertEqual([p for p in self._problems(physical=dict(physical, header={"drill_mm": drill})) if "drill" in p], [])

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


class TheRoleVocabularyIsClosedTest(unittest.TestCase):
    """
    A role name nothing reads looks exactly like a role name that is working.

    The two shipped boards described the same hazard — the serial console — under two names,
    `boot_log_tx` and `console_uart`. `check_design.py` knew only the first and `assign_pins.py`
    only the second, so a serial-parsing part on the console UART was caught on one board and
    passed without a word on the other. `--validate` said "ok" for both, because nothing checked
    that a role was one anybody consumes.
    """

    def _problems(self, roles):
        return boards.validate(dict(definition("b"), pin_roles=roles),
                               boards.LIBRARY / "b.json")

    def test_a_role_no_script_reads_is_refused(self):
        problems = self._problems({"boot_log_tx": {"gpio": [0], "note": "the old name"}})
        self.assertTrue(any("not a role any script reads" in p for p in problems), problems)

    def test_the_refusal_lists_the_names_that_would_have_worked(self):
        # Refusing without saying what to write instead is how a vocabulary becomes folklore.
        problems = self._problems({"typo_uart": {"gpio": [0], "note": "x"}})
        self.assertTrue(any(boards.CONSOLE_UART in p for p in problems), problems)

    def test_a_known_role_passes(self):
        self.assertEqual(
            self._problems({boards.CONSOLE_UART: {"gpio": [0], "note": "prints the boot log"}}),
            [])

    def test_every_role_the_assigner_prices_is_one_a_board_may_use(self):
        # The other half of the same drift: a penalty keyed on a name no board file may carry is
        # a penalty that never fires, and it looks identical to one that does.
        sys.path.insert(0, str(ROOT / "scripts"))
        import assign_pins  # noqa: E402,PLC0415 - here so this file stays standalone
        priced = set(assign_pins.ROLE_PENALTY) | set(assign_pins.CONFLICTING_ROLES)
        self.assertEqual(priced - set(boards.PIN_ROLES), set())


class TheShippedLibraryTest(unittest.TestCase):
    def test_every_board_in_the_library_satisfies_its_own_contract(self):
        for path in sorted(boards.LIBRARY.glob("*.json")):
            with self.subTest(board=path.stem):
                problems = boards.validate(json.loads(path.read_text()), path)
                self.assertEqual(problems, [], "%s: %s" % (path.stem, problems))

    def test_every_shipped_board_names_the_console_uart(self):
        # Not decoration: it is the role the pin-capability check singles out, so a board that
        # omits it is a board where that check silently does nothing.
        for path in sorted(boards.LIBRARY.glob("*.json")):
            if path.name == "active.json":
                continue
            with self.subTest(board=path.stem):
                roles = json.loads(path.read_text()).get("pin_roles") or {}
                self.assertIn(boards.CONSOLE_UART, roles)



class TheCommandLineTheSmartBinDependsOnTest(unittest.TestCase):
    """
    P41: every invocation `~/Development/smartbin-local/Makefile` makes of this script, and its
    exact output shape. That Makefile's own comment records this contract breaking once already —
    "it imported a `tools/boards.py` that moved into the plugin, and nothing noticed for weeks" —
    and until now not one of the eight was exercised by any test. These are characterisation
    tests: they pin what the caller reads today, so a refactor cannot change it in silence.
    """

    BOARD = "firebeetle2-esp32s3"

    def setUp(self):
        self.project = Path(tempfile.mkdtemp())
        (self.project / ".spark").mkdir()
        (self.project / "boards").mkdir()
        (self.project / "boards" / "active.json").write_text(
            json.dumps({"schema": 1, "board": self.BOARD}))

    def _run(self, *argv):
        import contextlib
        import io
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = boards.main([*argv, "--project", str(self.project)])
        return code, out.getvalue().strip(), err.getvalue().strip()

    def test_path_prints_one_readable_board_file(self):
        code, said, err = self._run("--path")
        self.assertEqual(code, 0, err)
        self.assertTrue(Path(said).is_file(), said)
        self.assertEqual(json.loads(Path(said).read_text())["id"], self.BOARD)

    def test_id_prints_the_board_id_alone(self):
        self.assertEqual(self._run("--id")[:2], (0, self.BOARD))

    def test_paths_prints_every_definition_space_separated(self):
        code, said, err = self._run("--paths")
        self.assertEqual(code, 0, err)
        paths = said.split(" ")
        self.assertTrue(all(Path(p).is_file() for p in paths), said)
        self.assertNotIn("active.json", said, "a selection is not a board definition")

    def test_get_chip_prints_one_bare_value(self):
        # `BOARD_CHIP := $(shell … --get chip)` is used to name a file; it must be one token.
        code, said, err = self._run("--get", "chip")
        self.assertEqual((code, said.split()), (0, [said]), err)
        self.assertEqual(said, json.loads((ROOT / "boards" / (self.BOARD + ".json")).read_text())["chip"])

    def test_get_micropython_port_prints_one_bare_value(self):
        code, said, err = self._run("--get", "micropython_port")
        self.assertEqual((code, said.split()), (0, [said]), err)

    def test_get_a_field_that_does_not_exist_fails_loudly(self):
        code, said, err = self._run("--get", "no_such_field")
        self.assertEqual(code, 1, said)
        self.assertIn("no_such_field", err)

    def test_resolve_writes_the_board_where_the_converter_reads_it(self):
        code, said, err = self._run("--resolve")
        self.assertEqual(code, 0, err)
        written = self.project / ".spark" / "board.json"
        self.assertTrue(written.is_file(), said)
        self.assertEqual(json.loads(written.read_text())["id"], self.BOARD)

    def test_validate_and_validate_for_fab_both_answer(self):
        for argv in (("--validate",), ("--validate", "--for-fab")):
            with self.subTest(argv=argv):
                code, said, err = self._run(*argv)
                self.assertIn(code, (0, 1), err)
                self.assertTrue(said or err, "it must say something either way")

class TheListSaysWhichBoardStopsAtTheFootprintTest(unittest.TestCase):
    """
    F12 (C-7): /spark:init shows this list and asks the person to choose, and the XIAO — whose file records no header
    geometry, so the chain stops at its footprint stage — was offered unmarked. It is marked, in the words --audit uses,
    and never hidden: it is still a choice for pin-map work. The `  * id (layer)` start of each line is unchanged.
    """

    def listed(self, root):
        import contextlib
        import io
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = boards.main(["--list", "--project", str(root)])
        return code, out.getvalue().splitlines()

    def test_a_board_that_stops_is_listed_saying_so_and_one_that_builds_is_not(self):
        code, lines = self.listed(project())
        self.assertEqual(code, 0)
        self.assertIn("    xiao-esp32-c6 (library) stops at the footprint stage (P121) — no header geometry in its board file", lines)
        self.assertIn("  * firebeetle2-esp32s3 (library)", lines)

    def test_a_board_file_that_cannot_be_read_is_still_listed(self):
        root = project()
        (root / "boards" / "half-board.json").write_text("{not json")
        code, lines = self.listed(root)
        self.assertEqual((code, "    half-board (project)" in lines), (0, True), lines)


class APadTheBoardCanWireMustHaveASimulatorNameTest(unittest.TestCase):
    """
    Found by P32a, caused by P29: a pad became wirable and nothing checked Wokwi knew it.

    P29 made the FireBeetle's VCC wired whenever something on the board drives its 5 V rail. The
    irrigation controller then stopped at `"VCC" is not a pin of board-esp32-s3-devkitc-1` — the
    stand-in devkit calls that pin `5V`. Two lists in one file disagreed and the only thing that
    compared them was a person running the chain on one project.
    """

    def board(self):
        return json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())

    def test_the_shipped_board_holds(self):
        problems = boards.validate(self.board(), ROOT / "boards" / "firebeetle2-esp32s3.json")
        self.assertEqual([p for p in problems if "wokwi_power_pins" in p], [])

    def test_a_pad_with_no_simulator_name_is_reported(self):
        board = self.board()
        board["wokwi_power_pins"].pop("VCC")
        problems = boards.validate(board, ROOT / "boards" / "firebeetle2-esp32s3.json")
        self.assertTrue(any("VCC" in p and "wokwi_power_pins" in p for p in problems),
                        "a pad that can be wired and cannot be simulated passed: %s" % problems)

    def test_a_board_with_no_wokwi_part_is_not_asked(self):
        # A board nothing simulates has no simulator names to be missing, and demanding them
        # would fail a definition that is complete.
        board = self.board()
        board.pop("wokwi_part_type")
        problems = boards.validate(board, ROOT / "boards" / "firebeetle2-esp32s3.json")
        self.assertEqual([p for p in problems if "wokwi_power_pins" in p], [])


class ABoardPointsAtItsDatasheetsLikeAPartTest(unittest.TestCase):
    """P62b put `documents` on a board record, and nothing read them: a wrong checksum or a
    citation of a document the board does not hold was a pointer to nothing, under a green suite."""

    def board(self):
        return json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())

    def problems(self, board):
        return boards.validate(board, ROOT / "boards" / "firebeetle2-esp32s3.json")

    def test_a_citation_of_a_document_the_board_does_not_hold_is_reported(self):
        board = self.board()
        board["power"]["deep_sleep_ua"]["cites"]["document"] = "wroom1-v1-8"
        self.assertTrue(any("power.deep_sleep_ua" in p and "wroom1-v1-8" in p for p in self.problems(board)))

    def test_a_board_document_whose_checksum_is_not_one_is_reported(self):
        board = self.board()
        board["documents"]["wroom1-v1-1"]["sha256"] = "bc430d66"
        self.assertTrue(any("documents.wroom1-v1-1" in p for p in self.problems(board)))


if __name__ == "__main__":
    unittest.main()
