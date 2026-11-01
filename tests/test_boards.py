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
from unittest import mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import boards  # noqa: E402
import store  # noqa: E402
from flat_message import NASTY, assert_flat  # noqa: E402

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


BUTTONS = {"seen_from": "the shield facing you, USB-C at the top",
           "boot": {"silkscreen": "B", "place": "top right"}, "reset": {"silkscreen": "R", "place": "top left"}}


def with_buttons(buttons):
    return {"physical": {"buttons": buttons}}


class ANewlineInAValueGivesOneLineTest(unittest.TestCase):
    def test_a_newline_in_a_path_gives_one_line_in_a_board_file_that_is_no_json(self):
        folder = Path(tempfile.mkdtemp()) / NASTY
        folder.mkdir()
        (folder / "bad.json").write_text("{not json")
        with self.assertRaises(boards.BoardError) as caught:
            boards._read_json(folder / "bad.json", "board definition")
        assert_flat(self, caught.exception, folder / "bad.json")
        with self.assertRaises(boards.BoardError) as caught:
            boards._read_json(folder / "nope.json", NASTY)
        assert_flat(self, caught.exception, NASTY)

    def test_a_contract_with_problems_keeps_its_lines_and_a_path_with_a_newline_gives_one_line(self):
        root = Path(tempfile.mkdtemp()) / NASTY
        (root / "boards").mkdir(parents=True)
        (root / "boards" / "active.json").write_text(json.dumps({"schema": 1, "board": "bad"}))
        (root / "boards" / "bad.json").write_text(json.dumps({"id": "bad"}))
        with self.assertRaises(boards.BoardError) as caught:
            boards.load(root)
        assert_flat(self, caught.exception)
        self.assertGreater(len(str(caught.exception).split("\n")), 2, "the problem lines stay lines")

    def test_an_id_with_a_newline_is_shown_escaped_with_the_available_boards_on_a_line_of_their_own(self):
        with self.assertRaises(boards.BoardError) as caught:
            boards.definition_path(project(), NASTY)
        assert_flat(self, caught.exception, NASTY)
        self.assertEqual(len(str(caught.exception).split("\n")), 2)


class ButtonPlacesTest(unittest.TestCase):
    """The words that name BOOT and RESET in a hint, from the record's physical.buttons."""

    def test_a_full_record_names_each_button_with_its_silkscreen_and_place(self):
        places = boards.ButtonPlaces.from_record(with_buttons(BUTTONS))
        self.assertEqual(places.boot, "BOOT button (B, top right)")
        self.assertEqual(places.reset, "RESET (R, top left)")
        self.assertEqual(places.orientation, ". Left and right as seen with the shield facing you, USB-C at the top")

    def test_a_record_without_buttons_gives_the_plain_words(self):
        for record in ({}, {"physical": {}}, {"physical": None}, None, [], with_buttons("x"), with_buttons(None)):
            places = boards.ButtonPlaces.from_record(record)
            self.assertEqual((places.boot, places.reset, places.orientation), ("BOOT button", "RESET", ""), record)
        self.assertEqual(boards.ButtonPlaces.EMPTY.boot, "BOOT button")

    def test_a_part_missing_or_of_the_wrong_type_gives_the_plain_words_not_half_a_hint(self):
        for broken in ({k: v for k, v in BUTTONS.items() if k != "seen_from"},
                       {k: v for k, v in BUTTONS.items() if k != "reset"},
                       dict(BUTTONS, boot={"silkscreen": "B"}),
                       dict(BUTTONS, boot={"silkscreen": "B", "place": 3}),
                       dict(BUTTONS, reset="R"),
                       dict(BUTTONS, seen_from=" "),
                       dict(BUTTONS, boot={"silkscreen": "", "place": "top right"}),
                       dict(BUTTONS, reset={"silkscreen": "R", "place": ""})):
            places = boards.ButtonPlaces.from_record(with_buttons(broken))
            self.assertEqual((places.boot, places.reset, places.orientation), ("BOOT button", "RESET", ""), broken)

    def test_of_project_reads_the_record_requirements_names(self):
        root = project(own={"mine": definition("mine", physical={"footprint_module": "X", "footprint_export": "X",
                                                                 "buttons": BUTTONS})})
        (root / "requirements.json").write_text(json.dumps({"board": "mine"}))
        self.assertEqual(boards.ButtonPlaces.of_project(root).boot, "BOOT button (B, top right)")

    def test_of_project_gives_the_plain_words_when_the_record_cannot_be_read(self):
        root = project()
        self.assertEqual(boards.ButtonPlaces.of_project(root).boot, "BOOT button")  # no requirements.json
        (root / "requirements.json").write_text("{not json")
        self.assertEqual(boards.ButtonPlaces.of_project(root).boot, "BOOT button")
        (root / "requirements.json").write_text(json.dumps({"board": "no-such-board"}))
        self.assertEqual(boards.ButtonPlaces.of_project(root).boot, "BOOT button")
        (root / "requirements.json").write_text(json.dumps({}))
        self.assertEqual(boards.ButtonPlaces.of_project(root).boot, "BOOT button")


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

    def test_a_doubtful_pad_must_be_a_pad_of_the_header_order(self):
        # P412: the drawn breadboard picks ground by this field, so a name that is no pad would leave a wrong ground
        physical = {"footprint_module": "X", "footprint_export": "X", "header_order": {"row": ["A", "GND"]}}
        for doubtful, count in ((["GND"], 0), (["NOPE"], 1), ("GND", 1), (["GND", "NOPE", "NADA"], 2), ([{}], 1), ([None, "GND"], 1)):
            with self.subTest(doubtful=doubtful):
                problems = self._problems(physical=dict(physical, header={"doubtful_pads": doubtful}), pins={"A": 0})
                self.assertEqual(len([p for p in problems if "doubtful_pads" in p]), count, problems)

    def test_the_library_boards_doubtful_pads_are_the_two_grounds_of_the_firebeetle(self):
        board = json.loads((boards.LIBRARY / (LIBRARY_BOARD + ".json")).read_text())
        self.assertEqual(board["physical"]["header"]["doubtful_pads"], ["GND1", "GND3"])

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

    def test_an_active_level_of_zero_or_one_passes(self):
        # P353: the level that lights an LED or that a pressed button reads.
        for level in (0, 1):
            with self.subTest(level=level):
                self.assertEqual(self._problems({"onboard_led": {"gpio": [15], "note": "x", "active_level": level}}), [])

    def test_an_active_level_as_a_fact_passes_and_one_without_a_source_or_with_value_2_is_refused(self):
        # P464: a level written by --fact-set carries its origin
        def led(level):
            return self._problems({"onboard_led": {"gpio": [15], "note": "x", "active_level": level}})

        self.assertEqual(led({"value": 0, "verified": True, "source": "the bench"}), [])
        self.assertEqual(led({"value": None, "verified": False, "source": "unknown"}), [])
        self.assertTrue(any("source" in p for p in led({"value": 0, "verified": True})), led({"value": 0, "verified": True}))
        self.assertTrue(any("must be 0 or 1" in p for p in led({"value": 2, "verified": True, "source": "the bench"})))

    def test_any_other_active_level_is_refused(self):
        for level in (2, True, "0"):
            with self.subTest(level=level):
                problems = self._problems({"onboard_led": {"gpio": [15], "note": "x", "active_level": level}})
                self.assertTrue(any("active_level" in p for p in problems), problems)

    def test_a_gpio_that_is_no_list_of_numbers_in_range_is_one_problem(self):
        for gpio in (["9"], 9, [True], [99], None, [1.5], [3, "x"]):
            with self.subTest(gpio=gpio):
                problems = self._problems({"onboard_led": {"gpio": gpio, "note": "x"}})
                self.assertEqual(len(problems), 1, problems)
                self.assertIn("pin_roles['onboard_led'].gpio", problems[0])

    def test_an_empty_gpio_list_and_two_numbers_in_range_hold(self):
        for gpio in ([], [0, 35]):
            with self.subTest(gpio=gpio):
                self.assertEqual(self._problems({"onboard_button": {"gpio": gpio, "note": "x"}}), [])

    def test_two_numbers_out_of_range_are_two_problems(self):
        problems = self._problems({"onboard_led": {"gpio": [64, 99, 3], "note": "x"}})
        self.assertEqual(problems, ["pin_roles['onboard_led'].gpio has GPIO64, outside 0-63",
                                    "pin_roles['onboard_led'].gpio has GPIO99, outside 0-63"])

    def test_a_note_that_is_no_string_is_a_problem_not_a_crash(self):
        problems = self._problems({"onboard_led": {"gpio": [15], "note": 5}})
        self.assertEqual(problems, ["pin_roles['onboard_led'] has an empty note; say what the caveat is"])

    def test_pin_roles_that_is_no_object_is_one_problem_not_a_crash(self):
        for roles in ([1], ["onboard_led"], "x", 5, [], True):
            with self.subTest(roles=roles):
                problems = boards.validate(dict(definition("b"), pin_roles=roles), boards.LIBRARY / "b.json")
                self.assertEqual(problems, ["pin_roles is %r; it must be an object of role -> {gpio, note}" % (roles,)])

    def test_a_role_name_with_a_line_break_reaches_the_screen_quoted_in_every_problem(self):
        for entry in ({"gpio": [0], "note": "x"}, {"gpio": [0]}, {"gpio": [0], "note": " ", "active_level": 2}):
            with self.subTest(entry=entry):
                problems = self._problems({"a\nb": entry})
                self.assertTrue(problems)
                for problem in problems:
                    self.assertNotIn("\n", problem.split("Known:")[0])
                    self.assertTrue(problem.startswith("pin_roles['a\\nb']"), problem)

    def test_a_gpio_listed_twice_is_one_problem(self):
        problems = self._problems({"onboard_led": {"gpio": [1, 1, 2], "note": "x"}})
        self.assertEqual(problems, ["pin_roles['onboard_led'].gpio has GPIO1 twice"])

    def test_a_gpio_that_is_refused_gives_one_problem_even_with_labels(self):
        problems = self._problems({"onboard_button": {"gpio": ["0", 35], "note": "x", "labels": {"S1": 0, "S2": 35}}})
        self.assertEqual(len(problems), 1, problems)
        self.assertIn("gpio is ['0', 35]", problems[0])

    def test_labels_that_name_gpios_of_the_entry_hold(self):
        self.assertEqual(self._problems({"onboard_button": {"gpio": [0, 35], "note": "x", "labels": {"S1": 0, "S2": 35}}}), [])

    def test_a_label_must_be_capitals_and_digits_not_on_and_name_a_gpio_of_the_entry(self):
        for labels, said in (({"S1": 4}, "pin_roles['onboard_button'].labels['S1'] is 4, which is not a GPIO in "),
                             ({"s1": 0}, "has the label 's1'"), ({"S-1": 0}, "has the label 'S-1'"),
                             ({"ON": 0}, "has the label 'ON'"), ({"S1": True}, "labels['S1'] is True"),
                             ({"S1": "0"}, "labels['S1'] is '0'"), (["S1"], "labels is ['S1']")):
            with self.subTest(labels=labels):
                problems = self._problems({"onboard_button": {"gpio": [0, 35], "note": "x", "labels": labels}})
                self.assertEqual(len(problems), 1, problems)
                self.assertIn(said, problems[0])

    def test_two_bad_labels_are_two_problems(self):
        problems = self._problems({"onboard_button": {"gpio": [0, 35], "note": "x", "labels": {"a": 0, "ON": 35}}})
        self.assertEqual(len(problems), 2, problems)

    FACT = {"value": 135, "verified": False, "source": "s", "why_it_matters": "sizes the sprite"}

    def test_a_fact_with_its_provenance_holds(self):
        self.assertEqual(self._problems({"onboard_led": {"gpio": [15], "note": "x", "facts": {"width": self.FACT}}}), [])

    def test_a_fact_that_breaks_the_rule_is_one_problem_that_names_it(self):
        for fact, said in (({"value": 1, "verified": True}, "has no 'source'"), ("135", "is '135', but it is an object"),
                           ({"value": 1, "verified": False, "source": "s"}, "unverified value with no why_it_matters")):
            with self.subTest(fact=fact):
                problems = self._problems({"onboard_led": {"gpio": [15], "note": "x", "facts": {"width": fact}}})
                self.assertEqual(len(problems), 1, problems)
                self.assertTrue(problems[0].startswith("pin_roles['onboard_led'].facts['width'] "), problems)
                self.assertIn(said, problems[0])

    def test_a_fact_value_that_is_a_list_a_dict_a_bool_or_not_finite_is_one_problem_and_a_number_or_word_holds(self):
        for value, holds in ((135, True), (1.14, True), ("ST7789", True), (None, True), (True, False), ([1], False),
                             ({"x": 1}, False), (float("nan"), False), (float("inf"), False), ([], False),
                             ("", False), ("  ", False), ("\t\n", False)):
            with self.subTest(value=value):
                fact = dict(self.FACT, value=value)
                problems = self._problems({"onboard_led": {"gpio": [15], "note": "x", "facts": {"width": fact}}})
                self.assertEqual(problems == [], holds, problems)
                self.assertEqual(len(problems), 0 if holds else 1)

    def test_every_fact_of_every_role_is_checked(self):
        bad = {"value": 1, "verified": True}
        problems = self._problems({"onboard_led": {"gpio": [15], "note": "x", "facts": {"width": bad, "height": bad}},
                                   "onboard_button": {"gpio": [0], "note": "x", "facts": {"a": bad, "b": bad}}})
        self.assertEqual(len(problems), 4, problems)

    def test_a_fact_name_must_be_lower_case_letters_and_underscores_and_not_on(self):
        for name in ("width-px", "Width", "on", "w2"):
            with self.subTest(name=name):
                problems = self._problems({"onboard_led": {"gpio": [15], "note": "x", "facts": {name: self.FACT}}})
                self.assertEqual(len(problems), 1, problems)
                self.assertIn("has the name %r" % name, problems[0])

    def test_a_fact_may_not_take_the_name_of_a_label(self):
        problems = self._problems({"onboard_button": {"gpio": [0], "note": "x", "labels": {"MOSI": 0}, "facts": {"mosi": self.FACT}}})
        self.assertEqual(len(problems), 1, problems)
        self.assertIn("pin_roles['onboard_button'].facts['mosi'] has the name of the label 'MOSI'", problems[0])

    def test_facts_that_are_no_object_are_one_problem(self):
        problems = self._problems({"onboard_led": {"gpio": [15], "note": "x", "facts": ["width"]}})
        self.assertEqual(len(problems), 1, problems)
        self.assertIn("facts is ['width']", problems[0])

    def test_a_name_with_a_line_break_reaches_the_screen_quoted(self):
        problems = self._problems({"onboard_led": {"gpio": [15], "note": "x", "facts": {"a\nb": self.FACT}}})
        self.assertEqual(len(problems), 1, problems)
        self.assertNotIn("\n", problems[0])
        self.assertIn("'a\\nb'", problems[0])

    def test_every_role_the_assigner_prices_is_one_a_board_may_use(self):
        # The other half of the same drift: a penalty keyed on a name no board file may carry is
        # a penalty that never fires, and it looks identical to one that does.
        sys.path.insert(0, str(ROOT / "scripts"))
        import assign_pins  # noqa: E402,PLC0415 - here so this file stays standalone
        priced = set(assign_pins.ROLE_PENALTY) | set(assign_pins.CONFLICTING_ROLES)
        self.assertEqual(priced - set(boards.PIN_ROLES), set())

    def test_every_onboard_role_is_one_a_board_may_use(self):
        self.assertEqual(set(boards.ONBOARD_ROLES) - set(boards.PIN_ROLES), set())


# --- MVP ---
class TheBoardsOwnPowerPartsTest(unittest.TestCase):
    """P389: the charger, the regulator and the battery input are facts of `power`, and the board offers them for a need."""

    CHARGER = {"does": "power", "what": "onboard charger"}
    REGULATOR = {"does": "power", "what": "onboard voltage regulator"}
    BATTERY_INPUT = {"does": "connect", "what": "onboard battery input"}
    BATTERY_LEVEL = {"does": "sense", "what": "onboard battery level", "role": "onboard_battery_sense"}

    @staticmethod
    def fact(value):
        return {"value": value, "verified": True, "source": "s"}

    def offered(self, power):
        return boards.onboard_functions({"power": power})

    def test_each_power_fact_with_a_value_is_one_function(self):
        for fact, function in (("charger", self.CHARGER), ("regulator", self.REGULATOR), ("battery_input", self.BATTERY_INPUT)):
            with self.subTest(fact=fact):
                self.assertEqual(self.offered({fact: self.fact("X1")}), [function])

    def test_the_functions_come_in_the_table_s_order_whatever_the_record_s_order(self):
        power = {"battery_input": self.fact("pads"), "charger": self.fact("TP4054")}
        self.assertEqual(self.offered(power), [self.CHARGER, self.BATTERY_INPUT])
        power = {"battery_input": self.fact("pads"), "regulator": self.fact("U7"), "charger": self.fact("TP4054")}
        self.assertEqual(self.offered(power), [self.CHARGER, self.REGULATOR, self.BATTERY_INPUT])

    def test_a_number_is_a_value_too(self):
        self.assertEqual(self.offered({"charger": self.fact(4054)}), [self.CHARGER])

    def test_a_power_block_that_names_no_such_fact_offers_nothing(self):
        for power in (None, [], ["charger"], "charger", 5, {}, {"charge_current_a": self.fact(0.12)},
                      {"charger": "TP4054"}, {"charger": ["TP4054"]}, {"charger": None}, {"charger": {}},
                      {"charger": self.fact(None)}, {"charger": self.fact(True)}, {"charger": self.fact("")},
                      {"charger": self.fact("  ")}, {"charger": self.fact(["x"])}, {"charger": self.fact(float("nan"))}):
            with self.subTest(power=power):
                self.assertEqual(self.offered(power), [])

    def test_the_power_functions_follow_the_pin_roles_functions(self):
        board = {"power": {"charger": self.fact("TP4054")}, "pin_roles": {"onboard_battery_sense": {"gpio": [34], "note": "x"},
                                                                              "onboard_led": {"gpio": [2], "note": "x"}}}
        self.assertEqual(boards.onboard_functions(board), [
            {"does": "indicate", "what": "onboard LED light", "role": "onboard_led"}, self.BATTERY_LEVEL, self.CHARGER])

    def test_a_board_with_no_pin_role_still_offers_its_power_facts(self):
        self.assertEqual(boards.onboard_functions({"pin_roles": 5, "power": {"charger": self.fact("TP4054")}}), [self.CHARGER])

    def test_the_battery_level_pin_is_offered_when_pins_py_names_it(self):
        for entry, offered in (({"gpio": [34], "note": "x"}, True), ({"gpio": [], "note": "x"}, False),
                               ({"gpio": [34, 35], "note": "x"}, False)):
            with self.subTest(entry=entry):
                self.assertEqual(boards.onboard_functions({"pin_roles": {"onboard_battery_sense": entry}}),
                                 [self.BATTERY_LEVEL] if offered else [])

    def test_a_blank_word_is_no_fact_value_and_a_number_or_a_word_is(self):
        for value, holds in (("", False), (" ", False), ("\n", False), ("a", True), (0, True), (0.0, True), (-1, True),
                             (True, False), (None, False), ([], False)):
            with self.subTest(value=value):
                self.assertEqual(boards.is_fact_value(value), holds)

    def test_the_shipped_boards_with_a_charger_offer_it(self):
        for name in ("xiao-esp32-c6", "firebeetle2-esp32s3"):
            with self.subTest(board=name):
                record = json.loads((boards.LIBRARY / (name + ".json")).read_text())
                self.assertIn(self.CHARGER, boards.onboard_functions(record))
                self.assertIn(self.REGULATOR, boards.onboard_functions(record))

    def test_the_firebeetle_names_its_regulator_as_its_v1_3_schematic_prints_it(self):
        firebeetle = json.loads((boards.LIBRARY / "firebeetle2-esp32s3.json").read_text())
        fact = firebeetle["power"]["regulator"]
        self.assertEqual((fact["value"], fact["verified"], fact["cites"]), ("TPS62A02DRLR", True, {
            "document": "firebeetle2-s3-schematic-v1-3", "at": "U1"}))

    def test_the_xiao_offers_its_battery_pads(self):
        xiao = json.loads((boards.LIBRARY / "xiao-esp32-c6.json").read_text())
        self.assertIn(self.BATTERY_INPUT, boards.onboard_functions(xiao))


class TheOnboardRoleTableTest(unittest.TestCase):
    def test_a_row_has_a_scenario_verb_or_a_sentence_and_not_both_nor_neither(self):
        self.assertEqual(boards.OnboardRole("X", "read", "indicate", "x").not_in_diagram, None)
        self.assertEqual(boards.OnboardRole("X", None, "indicate", "x", "s").scenario_verb, None)
        for args in (("X", None, "indicate", "x", None), ("X", "read", "indicate", "x", "s"), ("X", "", "indicate", "x"),
                     ("X", None, "indicate", "x", "")):
            with self.subTest(args=args):
                with self.assertRaises(ValueError) as caught:
                    boards.OnboardRole(*args)
                self.assertIn("X needs a scenario verb or a sentence", str(caught.exception))

    def test_the_table_holds_the_battery_level_pin_beside_the_display(self):
        self.assertEqual(list(boards.ONBOARD_ROLES), ["onboard_led", "onboard_button", "onboard_display", "onboard_battery_sense"])
        spec = boards.ONBOARD_ROLES["onboard_battery_sense"]
        self.assertEqual((spec.constant, spec.scenario_verb, spec.does, spec.what),
                         ("ONBOARD_BATTERY_SENSE", None, "sense", "onboard battery level"))


class TheBoardsPowerFactsAreCheckedTest(unittest.TestCase):
    FACT = {"value": "TP4054", "verified": True, "source": "s"}

    def problems(self, power):
        return boards.validate(dict(definition("b"), power=power), boards.LIBRARY / "b.json")

    def test_a_power_fact_with_its_provenance_holds(self):
        self.assertEqual(self.problems({"charger": self.FACT, "regulator": self.FACT, "battery_input": self.FACT}), [])

    def test_a_fact_with_no_source_is_one_problem_that_names_it(self):
        problems = self.problems({"charger": {"value": "TP4054", "verified": True}})
        self.assertEqual(problems, ["power['charger'] has no 'source' \u2014 a number with no provenance is an opinion"])

    def test_an_unverified_value_with_no_why_it_matters_is_a_problem(self):
        problems = self.problems({"regulator": {"value": "AXP313A", "verified": False, "source": "s"}})
        self.assertEqual(len(problems), 1, problems)
        self.assertIn("power['regulator'] is an unverified value with no why_it_matters", problems[0])

    def test_a_value_that_pins_py_would_not_write_is_a_problem_and_not_a_silent_drop(self):
        for value in (["x"], {"x": 1}, True, "", "  ", float("inf")):
            with self.subTest(value=value):
                problems = self.problems({"charger": dict(self.FACT, value=value)})
                self.assertEqual(problems, ["power['charger'].value is %r; it must be a finite number, a word or null" % (value,)])

    def test_a_fact_that_is_a_word_or_a_list_is_a_problem(self):
        for fact in ("TP4054", ["TP4054"], 5):
            with self.subTest(fact=fact):
                problems = self.problems({"charger": fact})
                self.assertEqual(problems, ["power['charger'] is %r, but it is an object" % (fact,)])

    def test_a_power_that_is_no_object_is_one_problem(self):
        for power in (["charger"], "charger", 5, True):
            with self.subTest(power=power):
                problems = self.problems(power)
                self.assertEqual(problems, ["power is %r; it must be an object of name -> {value, verified, source}" % (power,)])

    def test_every_power_fact_of_the_table_is_checked(self):
        problems = self.problems({"charger": "a", "regulator": "b", "battery_input": "c"})
        self.assertEqual(len(problems), 3, problems)

    def test_a_board_with_no_power_has_no_power_problem(self):
        self.assertEqual(self.problems(None), [])
        self.assertEqual(boards.validate(definition("b"), boards.LIBRARY / "b.json"), [])

    def test_a_power_fact_the_table_does_not_name_is_left_to_its_reader(self):
        self.assertEqual(self.problems({"charge_current_a": {"value": 0.12}}), [])
# --- end MVP ---


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
        from board_library import board_missing
        with board_missing("physical.header"):
            code, lines = self.listed(project())
        self.assertEqual(code, 0)
        self.assertIn("    xiao-esp32-c6 (library) stops at the footprint stage (P121): its board file lacks physical.header", lines)
        self.assertIn("  * firebeetle2-esp32s3 (library)", lines)

    def test_a_board_file_that_cannot_be_read_is_still_listed(self):
        root = project()
        (root / "boards" / "half-board.json").write_text("{not json")
        code, lines = self.listed(root)
        self.assertEqual((code, "    half-board (project)" in lines), (0, True), lines)

    def test_the_line_comes_from_the_footprint_module_and_asks_nothing_of_parts(self):
        # P411: footprint_stop imported `parts` for a sentence that now lives in emit_footprint; the edge to parts that remains is validate's.
        # emit_footprint loads parts itself, through design (design.py:41), so it is loaded first: the test asks only whether footprint_stop imports parts
        import emit_footprint  # noqa: F401
        from board_library import board_missing
        with board_missing("physical.header_order"), mock.patch.dict(sys.modules, {"parts": None}):
            self.assertEqual(boards.footprint_stop("xiao-esp32-c6", project()),
                             "stops at the footprint stage (P121): its board file lacks physical.header_order")
            self.assertEqual(boards.footprint_stop("firebeetle2-esp32s3", project()), "")


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


# --- MVP ---
#: A hand-made Wokwi definition (P396), not Wokwi's file: a comment, as Wokwi's own files have, and one virtual pin.
DEFINITION = """{
  "pins": {
    "D0": { "x": 1, "y": 1, "target": "GPIO0" },
    "GND": { "x": 2, "y": 1, "target": "GND" },
    /* Virtual pins */
    "$gpio15": { "target": "GPIO15" }
  }
}
"""


DEFINITION_CHANGED = DEFINITION + "\n"


def kept_definition_board(text=DEFINITION):
    """The XIAO record, with its Wokwi definition kept in this process's scratch store (`store.py:40-42`)."""
    digest = store.keep(text.encode(), "wokwi-test.board.json")
    board = boards.load(ROOT, "xiao-esp32-c6")
    board["documents"][boards.WOKWI_DEFINITION] = dict(board["documents"][boards.WOKWI_DEFINITION],
                                                        sha256=digest, file="wokwi-test.board.json")
    return board


def kept_path(board):
    entry = board["documents"][boards.WOKWI_DEFINITION]
    return store.place("sources") / entry["sha256"] / entry["file"]


class AWokwiDefinitionSaysWhichGpiosItSimulatesTest(unittest.TestCase):
    """P396, P397: the Wokwi definition that spark keeps names the GPIOs a scenario can reach, so the build says which it cannot."""

    NOT_KEPT = ("not-checked", "spark's store lacks the Wokwi definition that the board record names, its sha256 differs, "
                               "or it does not parse")

    def state_of(self, board):
        part = boards.read_simulated_part(board)
        return part.state, part.why

    def test_the_targets_of_its_pins_are_its_gpios_with_the_comment_cut(self):
        part = boards.read_simulated_part(kept_definition_board())
        self.assertEqual((part.state, part.why, part.board_id, part.gpios), ("recorded", None, "xiao-esp32-c6", frozenset({0, 15})))

    def test_a_gpio_with_no_pin_has_a_reason_and_one_with_a_pin_has_none(self):
        part = boards.read_simulated_part(kept_definition_board())
        self.assertEqual(part.why_not_simulated(9), "the Wokwi definition of xiao-esp32-c6 has no pin on GPIO9")
        self.assertIsNone(part.why_not_simulated(15))

    def test_a_file_the_store_lacks_is_not_checked(self):
        board = kept_definition_board()
        board["documents"][boards.WOKWI_DEFINITION]["file"] = "absent.board.json"
        self.assertEqual(self.state_of(board), self.NOT_KEPT)

    def test_a_file_whose_bytes_changed_is_not_checked(self):
        board = kept_definition_board(DEFINITION + "\n")
        kept_path(board).write_text(DEFINITION + "  ")
        self.assertEqual(self.state_of(board), self.NOT_KEPT)

    def test_strict_json_with_a_comment_mark_inside_a_string_parses(self):
        text = '{"pins": {"D1": {"target": "GPIO1", "note": "a /* b"}, "D2": {"target": "GPIO2", "note": "*/"}}}'
        self.assertEqual(boards.read_simulated_part(kept_definition_board(text)).gpios, frozenset({1, 2}))

    def test_a_definition_that_does_not_parse_is_not_checked(self):
        self.assertEqual(self.state_of(kept_definition_board('{"pins": ')), self.NOT_KEPT)

    def test_a_definition_whose_pins_are_not_a_table_is_not_checked_never_no_pins(self):
        for text in ('{"pins": [1]}', '[1]', '{"name": "no pins"}'):
            with self.subTest(text=text):
                self.assertEqual(self.state_of(kept_definition_board(text)), self.NOT_KEPT)

    def test_a_target_that_is_not_ascii_digits_is_no_gpio(self):
        text = '{"pins": {"D1": {"target": "GPIO\uff19"}, "D2": {"target": 9}, "D3": {"target": "GPIO3"}}}'
        self.assertEqual(boards.read_simulated_part(kept_definition_board(text)).gpios, frozenset({3}))

    def test_only_a_whole_gpio_name_is_a_gpio(self):
        text = '{"pins": {"A": {"target": "GPIO9x"}, "B": {"target": "XGPIO9"}, "C": {"target": "GPIO9/ADC"}, ' \
               '"D": {"target": "GPIO5"}}}'
        self.assertEqual(boards.read_simulated_part(kept_definition_board(text)).gpios, frozenset({5}))

    def test_a_definition_nested_too_deep_is_not_checked(self):
        self.assertEqual(self.state_of(kept_definition_board("[" * 100000 + "]" * 100000)), self.NOT_KEPT)

    def test_documents_that_are_not_a_table_name_no_definition(self):
        self.assertEqual(self.state_of({"id": "x", "documents": ["wokwi-board"]}), ("none-recorded", None))

    def test_a_record_with_no_documents_names_no_definition(self):
        self.assertEqual(self.state_of({"id": "x"}), ("none-recorded", None))

    def test_a_definition_entry_that_is_present_but_null_or_no_table_is_not_checked(self):
        # Only a missing key is "names none": a key that is there and holds nothing usable is a record spark could not read.
        for entry in (None, "wokwi-board", ["x"], 5, {}):
            with self.subTest(entry=entry):
                self.assertEqual(self.state_of({"id": "x", "documents": {boards.WOKWI_DEFINITION: entry}}), self.NOT_KEPT)

    def test_a_file_name_with_a_null_byte_is_not_checked_never_raised(self):
        board = kept_definition_board()
        board["documents"][boards.WOKWI_DEFINITION]["file"] = "a\0b.board.json"
        self.assertEqual(self.state_of(board), self.NOT_KEPT)

    def test_a_pin_target_whose_digits_int_refuses_is_not_checked_never_raised(self):
        # int() refuses a very long digit run on Python 3.9.14+, 3.10.7+ and 3.11+, and not on older ones, so it is made to here.
        board = kept_definition_board('{"pins": {"D1": {"target": "GPIO9"}}}')
        with mock.patch.object(boards, "int", side_effect=ValueError("too many digits"), create=True):
            self.assertEqual(self.state_of(board), self.NOT_KEPT)

    def test_a_record_that_is_no_table_names_no_definition(self):
        for record in ([], "x", None, 5, ["id"]):
            with self.subTest(record=record):
                self.assertEqual(self.state_of(record), ("none-recorded", None))

    def test_an_entry_that_would_leave_the_store_is_not_checked_and_never_opened(self):
        # A sha256 that is no 64 lowercase hex, or a file that is no plain name, is joined into a path: it could be an
        # absolute one, a "../" one, or a FIFO that hangs the read. The outside file below holds a good definition.
        outside = Path(tempfile.mkdtemp()) / "outside.board.json"
        outside.write_text(DEFINITION)
        good = kept_definition_board()["documents"][boards.WOKWI_DEFINITION]
        hostile = {"an absolute sha256": dict(good, sha256=str(outside.parent), file=outside.name),
                   "a ../ sha256": dict(good, sha256="../" * 3 + str(outside.parent).lstrip("/"), file=outside.name),
                   "an uppercase sha256": dict(good, sha256=good["sha256"].upper()),
                   "a short sha256": dict(good, sha256=good["sha256"][:63]),
                   "a file with a slash": dict(good, file="sub/" + good["file"]),
                   "an absolute file": dict(good, file=str(outside)),
                   "a file with a backslash": dict(good, file="sub\\" + good["file"]),
                   "a file with two dots": dict(good, file=".." + good["file"]),
                   "a file of ..": dict(good, file=".."),
                   "a file that is no string": dict(good, file=5)}
        for case, entry in hostile.items():
            with self.subTest(case=case), mock.patch.object(Path, "read_bytes", side_effect=AssertionError("opened " + case)):
                board = {"id": "x", "documents": {boards.WOKWI_DEFINITION: entry}}
                self.assertEqual(self.state_of(board), self.NOT_KEPT)

    def test_why_not_simulated_says_what_stopped_the_reader_never_that_a_pin_is_missing(self):
        # A definition that spark could not look at has no GPIOs, which is not the same as having no pin on GPIO9.
        lacking = kept_definition_board()
        lacking["documents"][boards.WOKWI_DEFINITION]["file"] = "absent.board.json"
        self.assertEqual(boards.read_simulated_part(lacking).why_not_simulated(9),
                         "not checked: spark's store lacks the Wokwi definition that the board record names, its sha256 "
                         "differs, or it does not parse")
        self.assertEqual(boards.read_simulated_part({"id": "x"}).why_not_simulated(9),
                         "not checked: the board record names no Wokwi definition")

    def test_the_value_is_built_by_state_why_and_gpios(self):
        part = boards.SimulatedPart("recorded", "x", frozenset({1}))
        self.assertEqual((part.state, part.board_id, part.gpios, part.why), ("recorded", "x", frozenset({1}), None))
        self.assertEqual(boards.SimulatedPart("none-recorded", "x").gpios, frozenset())


class TheBoardsOwnLimitsTest(unittest.TestCase):
    """P396, P397: an onboard GPIO with no pin in the board's Wokwi definition is a limit, in the build and in the note."""

    BUTTON = ("ONBOARD_BUTTON (GPIO9)", "the Wokwi definition of xiao-esp32-c6 has no pin on GPIO9, so spark knows no "
                                        "way for a scenario to press it. Test it on the board.")

    def test_the_button_with_no_pin_is_a_limit_and_the_led_with_one_is_not(self):
        self.assertEqual(boards.onboard_limits(kept_definition_board()), [self.BUTTON])

    def test_an_led_with_no_pin_is_one_no_scenario_can_read(self):
        board = kept_definition_board()
        board["pin_roles"][boards.ONBOARD_LED]["gpio"] = [3]
        self.assertIn(("ONBOARD_LED (GPIO3)", "the Wokwi definition of xiao-esp32-c6 has no pin on GPIO3, so spark "
                                              "knows no way for a scenario to read it. Test it on the board."),
                      boards.onboard_limits(board))

    def test_a_record_that_names_no_definition_says_not_checked(self):
        board = kept_definition_board()
        del board["documents"][boards.WOKWI_DEFINITION]
        self.assertEqual(boards.onboard_limits(board),
                         [("onboard GPIOs", "not checked: the board record names no Wokwi definition")])

    def test_a_definition_the_store_lacks_says_not_checked(self):
        board = kept_definition_board()
        board["documents"][boards.WOKWI_DEFINITION]["file"] = "absent.board.json"
        self.assertEqual(boards.onboard_limits(board),
                         [("onboard GPIOs", "not checked: spark's store lacks the Wokwi definition that the board "
                                            "record names, its sha256 differs, or it does not parse")])

    def test_a_definition_whose_bytes_changed_says_not_checked(self):
        board = kept_definition_board(DEFINITION_CHANGED)
        kept_path(board).write_text(DEFINITION_CHANGED + " ")
        self.assertEqual([component for component, _ in boards.onboard_limits(board)], ["onboard GPIOs"])

    def test_each_gpio_of_a_role_with_no_pin_is_its_own_limit(self):
        board = kept_definition_board()
        board["pin_roles"][boards.ONBOARD_BUTTON]["gpio"] = [9, 3]
        self.assertEqual([component for component, _ in boards.onboard_limits(board)],
                         ["ONBOARD_BUTTON (GPIO9)", "ONBOARD_BUTTON (GPIO3)"])

    def test_a_gpio_that_is_not_a_number_is_skipped_never_raised(self):
        board = kept_definition_board()
        board["pin_roles"][boards.ONBOARD_BUTTON]["gpio"] = ["9", None, True]
        self.assertEqual(boards.onboard_limits(board), [])

    def test_a_board_with_no_onboard_role_says_nothing(self):
        board = kept_definition_board()
        for role in (boards.ONBOARD_LED, boards.ONBOARD_BUTTON):
            del board["pin_roles"][role]
        del board["documents"][boards.WOKWI_DEFINITION]
        self.assertEqual(boards.onboard_limits(board), [])

    DISPLAY = ("ONBOARD_DISPLAY", "spark adds no part to the diagram for the board's own display, so a passed run does not "
                                  "test what it shows. Test it on the board.")
    BATTERY = ("ONBOARD_BATTERY_SENSE", "spark adds no battery to the diagram, so a passed run does not test what the board "
                                        "reads on this pin. Test it on the board.")
    TDISPLAY = ROOT / "tests" / "data" / "boards" / "lilygo-t-display.json"

    def test_the_display_is_one_limit_after_the_gpio_lines_whatever_its_gpios_are(self):
        for gpio in ([3], [15], [], "x"):
            with self.subTest(gpio=gpio):
                board = kept_definition_board()
                board["pin_roles"][boards.ONBOARD_DISPLAY] = {"gpio": gpio, "note": "the screen"}
                self.assertEqual(boards.onboard_limits(board), [self.BUTTON, self.DISPLAY])

    def test_the_t_displays_record_names_no_definition_a_screen_and_a_battery_pin(self):
        self.assertEqual(boards.onboard_limits(json.loads(self.TDISPLAY.read_text())),
                         [("onboard GPIOs", "not checked: the board record names no Wokwi definition"), self.DISPLAY, self.BATTERY])

    def test_the_battery_level_pin_is_one_limit_after_the_gpio_lines_whatever_its_gpio_is(self):
        for gpio in ([34], [], "x"):
            with self.subTest(gpio=gpio):
                board = kept_definition_board()
                board["pin_roles"][boards.ONBOARD_BATTERY_SENSE] = {"gpio": gpio, "note": "the divider"}
                self.assertEqual(boards.onboard_limits(board), [self.BUTTON, self.BATTERY])

    def test_a_board_with_only_a_display_gets_that_line_and_no_not_checked_line(self):
        board = json.loads(self.TDISPLAY.read_text())
        del board["pin_roles"][boards.ONBOARD_BUTTON]
        del board["pin_roles"][boards.ONBOARD_BATTERY_SENSE]
        self.assertEqual(boards.onboard_limits(board), [self.DISPLAY])

    def test_a_definition_the_store_lacks_still_leaves_the_display_line_after_the_not_checked_one(self):
        board = kept_definition_board()
        board["documents"][boards.WOKWI_DEFINITION]["file"] = "absent.board.json"
        board["pin_roles"][boards.ONBOARD_DISPLAY] = {"gpio": [3], "note": "the screen"}
        self.assertEqual([component for component, _ in boards.onboard_limits(board)], ["onboard GPIOs", "ONBOARD_DISPLAY"])

    def test_a_board_that_names_every_onboard_part_has_a_sentence_for_each_part_no_scenario_reaches(self):
        board = kept_definition_board()
        for role in boards.ONBOARD_ROLES:
            board["pin_roles"].setdefault(role, {"gpio": [3], "note": "x"})
        self.assertEqual([component for component, _ in boards.onboard_limits(board)],
                         ["ONBOARD_BUTTON (GPIO9)", "ONBOARD_DISPLAY", "ONBOARD_BATTERY_SENSE"])

    def test_a_role_with_no_gpio_list_says_nothing(self):
        board = kept_definition_board()
        board["pin_roles"][boards.ONBOARD_BUTTON] = {"note": "somewhere"}
        self.assertEqual(boards.onboard_limits(board), [])

    def test_documents_that_are_not_a_table_name_no_definition(self):
        board = kept_definition_board()
        board["documents"] = ["wokwi-board"]
        self.assertEqual(boards.onboard_limits(board),
                         [("onboard GPIOs", "not checked: the board record names no Wokwi definition")])

    # --- P397: the limits of one role, for the note of a pick
    NOT_KEPT = ("onboard GPIOs", "not checked: spark's store lacks the Wokwi definition that the board record names, its sha256 "
                                 "differs, or it does not parse")

    def test_a_role_has_the_pairs_that_onboard_limits_gives_for_it_alone(self):
        board = kept_definition_board()
        self.assertEqual(boards.role_limits(board, {boards.ONBOARD_BUTTON}), {boards.ONBOARD_BUTTON: [self.BUTTON]})
        self.assertEqual(boards.role_limits(board, {boards.ONBOARD_LED}), {boards.ONBOARD_LED: []})
        self.assertEqual(boards.role_limits(board, {boards.ONBOARD_LED, boards.ONBOARD_BUTTON}),
                         {boards.ONBOARD_LED: [], boards.ONBOARD_BUTTON: [self.BUTTON]})

    def test_a_role_the_board_does_not_name_or_the_caller_did_not_ask_for_is_not_in_the_answer(self):
        board = kept_definition_board()
        self.assertEqual(boards.role_limits(board, {boards.ONBOARD_DISPLAY, boards.ONBOARD_BATTERY_SENSE}), {})
        self.assertEqual(boards.role_limits(board, set()), {})

    def test_a_part_no_scenario_reaches_has_its_sentence_and_the_definition_is_not_read_for_it(self):
        board = json.loads(self.TDISPLAY.read_text())
        with mock.patch.object(boards, "read_simulated_part", side_effect=AssertionError("read")):
            self.assertEqual(boards.role_limits(board, {boards.ONBOARD_DISPLAY, boards.ONBOARD_BATTERY_SENSE}),
                             {boards.ONBOARD_DISPLAY: [self.DISPLAY], boards.ONBOARD_BATTERY_SENSE: [self.BATTERY]})

    def test_a_definition_spark_cannot_compare_gives_each_verb_role_its_not_checked_pair(self):
        board = kept_definition_board()
        board["documents"][boards.WOKWI_DEFINITION]["file"] = "absent.board.json"
        self.assertEqual(boards.role_limits(board, {boards.ONBOARD_LED, boards.ONBOARD_BUTTON}),
                         {boards.ONBOARD_LED: [self.NOT_KEPT], boards.ONBOARD_BUTTON: [self.NOT_KEPT]})

    def test_the_definition_is_read_once_for_every_role_and_once_over_calls_that_share_a_dict(self):
        board = kept_definition_board()
        with mock.patch.object(boards, "read_simulated_part", wraps=boards.read_simulated_part) as read:
            boards.role_limits(board, {boards.ONBOARD_LED, boards.ONBOARD_BUTTON})
        self.assertEqual(read.call_count, 1)
        with mock.patch.object(boards, "read_simulated_part", wraps=boards.read_simulated_part) as read:
            shared = {}
            boards.role_limits(board, {boards.ONBOARD_LED}, shared)
            boards.role_limits(board, {boards.ONBOARD_BUTTON}, shared)
        self.assertEqual((read.call_count, list(shared)), (1, ["xiao-esp32-c6"]))

    def test_two_records_that_share_an_id_or_have_none_do_not_share_a_cached_definition(self):
        board, other = kept_definition_board(), kept_definition_board(DEFINITION_CHANGED)
        other["documents"][boards.WOKWI_DEFINITION]["file"] = "absent.board.json"
        shared = {}
        self.assertEqual(boards.role_limits(board, {boards.ONBOARD_BUTTON}, shared, "kept"), {boards.ONBOARD_BUTTON: [self.BUTTON]})
        self.assertEqual(boards.role_limits(other, {boards.ONBOARD_BUTTON}, shared, "absent"), {boards.ONBOARD_BUTTON: [self.NOT_KEPT]})
        del board["id"]
        self.assertEqual(boards.role_limits(board, {boards.ONBOARD_BUTTON}, shared, "kept")[boards.ONBOARD_BUTTON][0][0], "ONBOARD_BUTTON (GPIO9)")
        self.assertEqual(sorted(shared), ["absent", "kept"])


class TheFireBeetleCitesItsStandInsDefinitionTest(unittest.TestCase):
    """P483: the FireBeetle's record cites the S3 devkit's Wokwi file as a stand-in, so its LED and button pins are header pins."""

    STAND_IN = "the Wokwi part of firebeetle2-esp32s3 is a stand-in, where GPIO%d is a bare header pin with no onboard LED or button"
    TAIL = ", so spark knows no way for a scenario to %s it. Test it on the board."
    DEVKIT = '{"pins": {"21": {"target": "GPIO21"}, "47": {"target": "GPIO47"}, "GND": {"target": "GND"}}}'

    def firebeetle(self, text=DEVKIT):
        """The shipped FireBeetle record, with a hand-made definition kept in the scratch store under its entry."""
        board = boards.load(ROOT, "firebeetle2-esp32s3")
        entry = board["documents"]["wokwi-board"]
        board["documents"]["wokwi-board"] = dict(entry, sha256=store.keep(text.encode(), entry["file"]))
        return board

    def test_the_record_cites_the_devkits_file_with_a_64_hex_sha256(self):
        entry = boards.load(ROOT, "firebeetle2-esp32s3")["documents"]["wokwi-board"]
        self.assertRegex(entry["sha256"], "^[0-9a-f]{64}$")
        self.assertEqual(entry["file"], "wokwi-esp32-s3-devkitc-1.board.json")

    def test_a_kept_definition_is_read_with_both_pins_and_the_stand_in_mark(self):
        part = boards.read_simulated_part(self.firebeetle())
        self.assertEqual((part.state, part.gpios, part.is_stand_in), ("recorded", frozenset({21, 47}), True))

    def test_each_onboard_gpio_the_stand_in_reaches_still_gets_one_limit_with_the_stand_in_sentence(self):
        self.assertEqual(boards.onboard_limits(self.firebeetle()),
                         [("ONBOARD_LED (GPIO21)", self.STAND_IN % 21 + self.TAIL % "read"),
                          ("ONBOARD_BUTTON (GPIO47)", self.STAND_IN % 47 + self.TAIL % "press")])

    def test_an_empty_store_says_spark_lacks_it_and_never_that_no_definition_is_named(self):
        board = boards.load(ROOT, "firebeetle2-esp32s3")
        board["documents"]["wokwi-board"]["sha256"] = "0" * 64
        self.assertEqual(boards.onboard_limits(board),
                         [("onboard GPIOs", "not checked: spark's store lacks the Wokwi definition that the board "
                                            "record names, its sha256 differs, or it does not parse")])

    def test_a_definition_without_gpio47_says_it_has_no_pin_there(self):
        said = dict(boards.onboard_limits(self.firebeetle('{"pins": {"21": {"target": "GPIO21"}}}')))
        self.assertTrue(said["ONBOARD_BUTTON (GPIO47)"].startswith("the Wokwi definition of firebeetle2-esp32s3 has no pin on GPIO47"))

    def test_a_board_that_is_no_stand_in_gets_no_stand_in_sentence(self):
        board = kept_definition_board()
        self.assertFalse(boards.read_simulated_part(board).is_stand_in)
        self.assertIsNone(boards.read_simulated_part(board).why_not_simulated(15))

    def test_a_part_that_is_no_stand_in_keeps_its_old_texts(self):
        part = boards.read_simulated_part(kept_definition_board())
        self.assertEqual(part.why_not_simulated(21), "the Wokwi definition of xiao-esp32-c6 has no pin on GPIO21")
        self.assertIsNone(part.why_not_simulated(0))

    def test_only_true_marks_a_stand_in(self):
        board = self.firebeetle()
        board["wokwi_is_stand_in"] = "yes"
        self.assertFalse(boards.read_simulated_part(board).is_stand_in)


# --- end MVP ---


if __name__ == "__main__":
    unittest.main()
