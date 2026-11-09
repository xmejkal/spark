"""
Proof that a design is loaded from its file, once, and that bad input is a sentence rather than a
traceback.

Three scripts used to load a design each in their own way, and the sprint audit of 2026-09-29
found them disagreeing: the generator looked its rules up by the raw `--project` flag after
resolving the project properly two screens earlier, the spine resolved the project from the
current directory, and all three read the JSON outside any `try`. Everything here is about the
one loader they now share.

    python3 -m unittest discover -s tests
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from spark.design import pin_assigner  # noqa: E402
from spark.design import loader  # noqa: E402
from flat_message import NASTY, assert_flat  # noqa: E402


def project(rules=None, requirements=None, sub=None):
    """A temp project: `.spark/` (which is what makes it a project), rules, one requirements file."""
    root = Path(tempfile.mkdtemp())
    (root / ".spark").mkdir()
    if rules is not None:
        (root / ".spark" / "rules.json").write_text(json.dumps(rules))
    where = root / sub if sub else root
    where.mkdir(parents=True, exist_ok=True)
    path = where / "car.requirements.json"
    path.write_text(json.dumps(requirements if requirements is not None else
                               {"board": "firebeetle2-esp32s3", "parts": ["l9110s-module"]}))
    return root, path


class elsewhere:
    """Run the body from a directory that is not the project — the case every copy got wrong."""

    def __enter__(self):
        self.was = os.getcwd()
        os.chdir(tempfile.mkdtemp())
        return self

    def __exit__(self, *_):
        os.chdir(self.was)


class ReadingTheRequirementsTest(unittest.TestCase):
    def test_a_missing_file_is_a_sentence(self):
        with self.assertRaises(loader.DesignError) as caught:
            loader.read(Path(tempfile.mkdtemp()) / "nope.json")
        self.assertIn("no requirements at", str(caught.exception))

    def test_malformed_json_is_a_sentence_naming_the_file(self):
        # Was a JSONDecodeError traceback, exit 1, in three scripts (audit A8).
        path = Path(tempfile.mkdtemp()) / "bad.json"
        path.write_text("{not json")
        with self.assertRaises(loader.DesignError) as caught:
            loader.read(path)
        self.assertIn("bad.json", str(caught.exception))
        self.assertIn("not JSON", str(caught.exception))

    def test_a_newline_in_the_requirements_path_gives_one_line_in_read(self):
        path = Path(tempfile.mkdtemp()) / NASTY
        with self.assertRaises(loader.DesignError) as caught:
            loader.read(path)
        assert_flat(self, caught.exception, path)

    def test_a_part_error_keeps_its_two_lines_and_a_path_with_a_newline_gives_one_line_in_record(self):
        root = Path(tempfile.mkdtemp())
        (root / ".spark").mkdir()
        with self.assertRaises(loader.DesignError) as caught:
            loader.record("no-such-part", root)
        self.assertEqual(len(str(caught.exception).split("\n")), 2, str(caught.exception))
        home = Path(tempfile.mkdtemp()) / NASTY
        (home / ".spark").mkdir(parents=True)
        (home / "parts").mkdir()
        (home / "parts" / "bad.json").write_text("{}")
        with self.assertRaises(loader.DesignError) as caught:
            loader.record("bad", home)
        assert_flat(self, caught.exception)
        self.assertGreater(len(str(caught.exception).split("\n")), 2, "the problem lines stay lines")
        (home / "boards").mkdir()
        (home / "boards" / "worse.json").write_text(json.dumps({"id": "worse"}))
        (home / "car.requirements.json").write_text(json.dumps({"board": "worse", "parts": []}))
        with self.assertRaises(loader.DesignError) as caught:
            loader.load(home / "car.requirements.json")
        assert_flat(self, caught.exception)
        self.assertGreater(len(str(caught.exception).split("\n")), 2, "the problem lines stay lines")
        with self.assertRaises(loader.DesignError) as caught:
            loader.signals_of([{"id": "bad"}], {}, home)
        assert_flat(self, caught.exception)
        self.assertGreater(len(str(caught.exception).split("\n")), 2, "the problem lines stay lines")

    def test_a_list_is_not_a_requirements_file(self):
        path = Path(tempfile.mkdtemp()) / "list.json"
        path.write_text("[1, 2]")
        with self.assertRaises(loader.DesignError):
            loader.read(path)

    def test_an_entry_without_a_part_is_a_sentence_not_a_key_error(self):
        with self.assertRaises(loader.DesignError) as caught:
            loader.requested_parts({"parts": [{"name": "X"}]})
        self.assertIn("parts[0]", str(caught.exception))

    def test_an_entry_of_the_wrong_type_is_refused(self):
        with self.assertRaises(loader.DesignError):
            loader.requested_parts({"parts": [42]})

    def test_an_instance_whose_name_is_no_name_is_refused(self):
        # P87's attribute half: the instance's name is the component the board is written with, `<chip name="…">`
        for name in ('Btn" pcbX={(globalThis.x = 1, 0)} y="', "Btn Open", "Btn-Open"):
            with self.subTest(name=name):
                with self.assertRaises(loader.DesignError) as caught:
                    loader.requested_parts({"parts": [{"part": "tactile-button", "name": name}]})
                self.assertTrue(str(caught.exception).startswith("parts[0] calls its instance %r, but" % name), str(caught.exception))
                self.assertIn("the board is written with it as code", str(caught.exception))
        self.assertEqual(loader.requested_parts({"parts": [{"part": "tactile-button", "name": "Btn_Open2"}]}),
                         [("tactile-button", "Btn_Open2")])

    def test_a_signal_the_requirements_name_that_is_no_name_is_refused(self):
        # P87's attribute half, as for a part's signal: the pin map and the board name it, and firmware is written against it
        path = Path(tempfile.mkdtemp()) / "r.json"
        path.write_text(json.dumps({"board": "firebeetle2-esp32s3", "parts": [], "signals": [{"name": 'LED" x="', "needs": []}]}))
        with self.assertRaises(loader.DesignError) as caught:
            loader.read(path)
        self.assertEqual(str(caught.exception), "%s: signals[0] is named 'LED\" x=\"', but a signal is a name — letters, digits "
                                                 "and _ (LED_STATUS): the pin map and the board name it, and firmware is written "
                                                 "against it" % path)

    def test_the_two_entry_forms_normalise_to_one(self):
        self.assertEqual(loader.requested_parts(
            {"parts": ["l9110s-module", {"part": "tactile-button", "name": "BtnForward"}]}),
            [("l9110s-module", None), ("tactile-button", "BtnForward")])


# --- MVP --- (P438, #583)
class ARequirementsFileOfTheWrongKindIsRefusedTest(unittest.TestCase):
    """`signals` that is no list and a `pin` that is no pin name were a traceback, or a wrong sentence, or silently no pin."""

    def refused(self, signals, parts=()):
        path = Path(tempfile.mkdtemp()) / "car.requirements.json"
        path.write_text(json.dumps({"board": "xiao-esp32-c6", "parts": list(parts) if isinstance(parts, tuple) else parts,
                                    "signals": signals}))
        with self.assertRaises(loader.DesignError) as caught:
            loader.read(path)
        self.assertIn(str(path), str(caught.exception))
        return str(caught.exception)

    def test_signals_that_is_no_list_is_refused_naming_its_kind(self):
        for value, kind in ((5, "a number"), ("abc", "text"), ({}, "an object"), (0, "a number"), (False, "true or false")):
            with self.subTest(value=value):
                said = self.refused(value)
                self.assertIn("signals is %s; write a list of signals" % kind, said)

    def test_a_pin_that_is_no_name_is_refused_naming_its_kind(self):
        for value, kind in ((["D0"], "a list"), ({"a": 1}, "an object"), (4, "a number"), (0, "a number"), (True, "true or false"),
                            (False, "true or false")):
            with self.subTest(value=value):
                said = self.refused([{"name": "X", "needs": [], "pin": value}])
                self.assertIn("signals[0].pin is %s; write a pin name from the board" % kind, said)

    def test_parts_that_is_no_list_is_refused_naming_its_kind(self):
        for value, kind in ((5, "a number"), ("led-red-5mm", "text"), ({}, "an object"), (True, "true or false")):
            with self.subTest(value=value):
                said = self.refused(None, parts=value)
                self.assertIn('parts is %s; write a list of part ids or {"part", "name"}' % kind, said)

    def test_an_empty_pin_is_refused(self):
        self.assertIn("signals[0].pin is an empty name", self.refused([{"name": "X", "pin": ""}]))

    def test_the_kinds_that_were_fine_still_read(self):
        for signals in (None, [], [{"name": "X", "pin": "D0"}], [{"name": "X", "pin": None}], [{"name": "X"}]):
            with self.subTest(signals=signals):
                path = Path(tempfile.mkdtemp()) / "car.requirements.json"
                path.write_text(json.dumps({"board": "xiao-esp32-c6", "parts": [], "signals": signals}))
                self.assertEqual(loader.read(path)["signals"], signals)


class TheProjectIsTheFilesTest(unittest.TestCase):
    def test_the_flag_wins(self):
        root, path = project()
        other = Path(tempfile.mkdtemp())
        self.assertEqual(loader.project_for(path, str(other)), other.resolve())

    def test_found_up_from_the_file_not_from_the_current_directory(self):
        # The spine resolved from cwd and, from /tmp, could not find a part sitting beside the
        # requirements file (audit A10). Two directories down from the project, run from
        # elsewhere: still that project.
        root, path = project(sub="designs/v2")
        with elsewhere():
            self.assertEqual(loader.project_for(path), root.resolve())

    def test_a_file_in_no_project_is_built_from_the_plugins_library(self):
        # The decision changed 2026-09-29 (audit B5): this raised, and every documented step
        # refused "no project here" from a fresh directory while `check_spine` alone fell back.
        path = Path(tempfile.mkdtemp()) / "loose.json"
        path.write_text("{}")
        with elsewhere():
            project = loader.project_for(path)
        self.assertTrue(loader.is_library(project))
        self.assertFalse(loader.is_library(tempfile.mkdtemp()))

    def test_a_design_from_nowhere_has_no_rules(self):
        path = Path(tempfile.mkdtemp()) / "loose.json"
        path.write_text(json.dumps({"board": "firebeetle2-esp32s3", "parts": ["l9110s-module"]}))
        loaded = loader.load(path)
        self.assertTrue(loader.is_library(loaded.project))
        self.assertEqual(loaded.rules, {})


class LoadingTest(unittest.TestCase):
    RULES = {"physics": {"rails": {"MOTOR6V": {"max_current_a": 2.0}}}}

    def test_the_rules_are_the_resolved_projects_from_anywhere(self):
        # The cause of the unsized car (audit A2): rules looked up by the raw flag, None
        # without it. Loaded from elsewhere, with no flag, the rules are still the project's.
        root, path = project(rules=self.RULES)
        with elsewhere():
            loaded = loader.load(path)
        self.assertEqual(loaded.project, root.resolve())
        self.assertEqual(loaded.rules, self.RULES)

    def test_no_rules_file_is_no_rules_not_an_error(self):
        root, path = project()
        self.assertEqual(loader.load(path).rules, {})

    def test_an_unreadable_rules_file_is_an_error_not_no_rules(self):
        # Silently "no rules" would size nothing and call every width unjustified while the
        # file that justifies them sits right there.
        root, path = project()
        (root / ".spark" / "rules.json").write_text("{broken")
        with self.assertRaises(loader.DesignError) as caught:
            loader.load(path)
        self.assertIn("rules.json", str(caught.exception))

    # --- MVP ---
    def test_a_rule_of_the_wrong_kind_is_an_error_naming_the_file_and_the_field(self):
        root, path = project(rules={"fabrication": {"drill_step_mm": "0.1"}})
        with self.assertRaises(loader.DesignError) as caught:
            loader.rules_in(root)
        self.assertIn(".spark/rules.json: fabrication.drill_step_mm is not a finite number", str(caught.exception))
        self.assertIsInstance(caught.exception.__cause__, loader.fab.RulesError)

    def test_a_rule_below_its_lowest_is_an_error_naming_the_file_and_the_field(self):
        # P454: a drill step of 0 was a ZeroDivisionError in the footprint generator
        root, path = project(rules={"fabrication": {"drill_step_mm": 0}})
        with self.assertRaises(loader.DesignError) as caught:
            loader.rules_in(root)
        self.assertIn(".spark/rules.json: fabrication.drill_step_mm must be above 0", str(caught.exception))

    # --- MVP --- (P438)
    def test_a_rules_path_that_is_a_folder_is_an_error_not_no_rules(self):
        root, path = project()
        (root / ".spark" / "rules.json").mkdir()
        with self.assertRaises(loader.DesignError) as caught:
            loader.rules_in(root)
        self.assertTrue(str(caught.exception).startswith(str(root / ".spark" / "rules.json")), str(caught.exception))
        self.assertIn("could not be read", str(caught.exception))

    def test_a_rules_file_that_is_fine_is_read(self):
        root, path = project(rules={"fabrication": {"drill_step_mm": 0.3}})
        self.assertEqual(loader.rules_in(root), {"fabrication": {"drill_step_mm": 0.3}})

    def test_parts_come_back_as_instances(self):
        root, path = project(requirements={
            "board": "firebeetle2-esp32s3",
            "parts": [{"part": "vl6180x-breakout", "name": "Rangefinder"}, "l9110s-module"]})
        loaded = loader.load(path)
        self.assertEqual([p.get("_instance") for p in loaded.parts], ["Rangefinder", None])
        self.assertEqual([p["id"] for p in loaded.parts], ["vl6180x-breakout", "l9110s-module"])

    def test_an_unknown_part_is_a_sentence(self):
        root, path = project(requirements={"board": "firebeetle2-esp32s3", "parts": ["unobtainium"]})
        with self.assertRaises(loader.DesignError) as caught:
            loader.load(path)
        self.assertIn("unobtainium", str(caught.exception))

    def test_an_unknown_board_is_a_sentence(self):
        root, path = project(requirements={"board": "no-such-board", "parts": []})
        with self.assertRaises(loader.DesignError):
            loader.load(path)

    def test_the_board_can_be_overridden(self):
        root, path = project()
        self.assertEqual(loader.load(path, board_id="xiao-esp32-c6").board["id"], "xiao-esp32-c6")



class ARailBelongsToTheDesignTest(unittest.TestCase):
    """
    The RC car copied the whole shipped L9110S record to change `motor` to `traction` (G5).
    A requirements entry says it instead, and the library's record is never touched.
    """

    ENTRY = {"part": "l9110s-module", "name": "Drive", "rails": {"VCC": "traction"}}

    def test_a_pins_rail_can_be_re_pointed_from_the_requirements(self):
        root, path = project(requirements={"board": "firebeetle2-esp32s3", "parts": [self.ENTRY]})
        [drive] = loader.load(path).parts
        rails = {supply["pin"]: supply["rail"] for supply in drive["power"]}
        self.assertEqual(rails["VCC"], "traction")
        self.assertEqual(rails["GND"], "ground", "only the named pin moves")
        self.assertEqual(drive["_instance"], "Drive")

    def test_on_rails_returns_a_copy_and_leaves_its_argument_as_loaded(self):
        # The first version of this test re-loaded the record from disk afterwards, which
        # `part_records.load` does fresh every time — so an in-place edit was invisible and the mutation
        # escaped (W12). The contract is on the function: its argument is untouched.
        from spark.sourcing import part_records
        record = part_records.load("l9110s-module")
        moved = loader.on_rails(record, {"VCC": "traction"})
        self.assertEqual([s["rail"] for s in moved["power"] if s["pin"] == "VCC"], ["traction"])
        self.assertEqual([s["rail"] for s in record["power"] if s["pin"] == "VCC"], ["motor"])
        self.assertIsNot(moved["power"], record["power"])

    def test_a_pin_the_part_does_not_have_is_a_sentence(self):
        entry = dict(self.ENTRY, rails={"VIN": "traction"})
        root, path = project(requirements={"board": "firebeetle2-esp32s3", "parts": [entry]})
        with self.assertRaises(loader.DesignError) as caught:
            loader.load(path)
        self.assertIn("VIN", str(caught.exception))
        self.assertIn("VCC", str(caught.exception), "the message names the pins it does have")

    def test_rails_must_be_a_pin_to_rail_map(self):
        with self.assertRaises(loader.DesignError):
            loader.rails_requested({"parts": [dict(self.ENTRY, rails=["traction"])]})

    def test_a_rail_the_requirements_give_that_is_no_name_is_refused(self):
        # P87's attribute half: the rail becomes the net the pin's trace is written to
        with self.assertRaises(loader.DesignError) as caught:
            loader.rails_requested({"parts": [dict(self.ENTRY, rails={"VCC": 'traction" x="'})]})
        self.assertEqual(str(caught.exception), "parts[0].rails puts VCC on 'traction\" x=\"', but a rail is a name — letters, "
                                                 "digits and _ (traction, motor): the board is written with it as code")

    def test_an_unnamed_entry_can_carry_rails_too(self):
        entry = {"part": "l9110s-module", "rails": {"VCC": "traction"}}
        root, path = project(requirements={"board": "firebeetle2-esp32s3", "parts": [entry]})
        [drive] = loader.load(path).parts
        self.assertEqual([s["rail"] for s in drive["power"] if s["pin"] == "VCC"], ["traction"])


class TheSignalsAreDerivedOnceTest(unittest.TestCase):
    """
    P20: `emit_board.main` derived a design's signals and `assign_pins.main` handed the raw parts
    entries to the library instead, so the first documented step crashed on the documented input
    (audit B1). The loader derives them, named per instance, and both mains read `design.signals`.
    """

    def test_each_instance_gets_its_own_signal_names(self):
        root, path = project(requirements={
            "board": "firebeetle2-esp32s3",
            "parts": [{"part": "tactile-button", "name": "BtnOpen"},
                      {"part": "tactile-button", "name": "BtnMode"}, "l9110s-module"]})
        names = [signal["name"] for signal in loader.load(path).signals]
        self.assertEqual(len(names), len(set(names)), names)
        self.assertTrue(any(name.startswith("BTNOPEN_") for name in names), names)
        self.assertTrue(any(name.startswith("BTNMODE_") for name in names), names)
        self.assertIn("MOTOR_IA", names)

    def test_the_requirements_own_signals_come_last(self):
        root, path = project(requirements={
            "board": "firebeetle2-esp32s3", "parts": ["l9110s-module"],
            "signals": [{"name": "LED_STATUS", "needs": []}]})
        self.assertEqual(loader.load(path).signals[-1]["name"], "LED_STATUS")

    def test_a_malformed_project_part_is_a_sentence_naming_the_part(self):
        root, path = project()
        (root / "parts").mkdir()
        (root / "parts" / "l9110s-module.json").write_text("{half a record")
        with self.assertRaises(loader.DesignError) as caught:
            loader.load(path)
        self.assertIn("l9110s-module", str(caught.exception))


class ABusSignalKeepsItsLineTest(unittest.TestCase):
    def test_a_named_instances_bus_signal_still_says_which_line_it_is(self):
        # The instance prefix renames the signal; the bus line it is has to survive the rename,
        # or the assigner cannot find the board's pin for it (P21).
        root, path = project(requirements={"board": "firebeetle2-esp32s3",
                                           "parts": [{"part": "vl6180x-breakout", "name": "Rangefinder"}]})
        signals = {s["name"]: s for s in loader.load(path).signals}
        self.assertEqual(signals["RANGEFINDER_SDA"]["line"], "SDA")
        self.assertEqual(signals["RANGEFINDER_SDA"]["bus"], "i2c")


class RulesInTest(unittest.TestCase):
    def test_rules_in_reads_the_projects_rules_or_none(self):
        root = Path(tempfile.mkdtemp())
        self.assertEqual(loader.rules_in(root), {})
        (root / ".spark").mkdir()
        (root / ".spark" / "rules.json").write_text(json.dumps({"physics": {"i2c_hz": 400000}}))
        self.assertEqual(loader.rules_in(root)["physics"]["i2c_hz"], 400000)


class TheInputIsCheckedWhereItIsReadTest(unittest.TestCase):
    def test_a_project_that_does_not_exist_is_a_sentence_naming_it(self):
        # Close audit C5: a typo'd --project resolved to a path nobody checked, and a project's
        # rules were dropped with exit 0.
        root, path = project(rules={"physics": {"rails": {"MOTOR6V": {"max_current_a": 2.0}}}})
        with self.assertRaises(loader.DesignError) as caught:
            loader.load(path, project=str(root / "typo"))
        self.assertIn("typo", str(caught.exception))

    def test_a_signal_without_a_name_is_a_sentence_naming_the_entry(self):
        # Close audit C7: a KeyError through both mains and "the chain is broken" in the spine.
        root, path = project(requirements={"board": "firebeetle2-esp32s3", "parts": [],
                                           "signals": [{"needs": []}]})
        with self.assertRaises(loader.DesignError) as caught:
            loader.read(path)
        self.assertIn("signals[0]", str(caught.exception))
        path.write_text(json.dumps({"board": "firebeetle2-esp32s3", "parts": [],
                                    "signals": [{"name": "X", "needs": "wake"}]}))
        with self.assertRaises(loader.DesignError):
            loader.read(path)


class CapitalsDoNotMakeTwoNamesTest(unittest.TestCase):
    """
    P163 (#100): `OpenLid` and `Openlid` passed the generator's exact compare, `signal_name` put both in capitals as
    OPENLID_BUTTON, and two GPIOs were traced to one pad, exit 0. The build's view of a name is ONE function, and the
    requirements file is refused where it is read — before any stage runs.
    """

    def entries(self, *names):
        path = Path(tempfile.mkdtemp()) / "r.json"
        path.write_text(json.dumps({"board": "firebeetle2-esp32s3",
                                    "parts": [{"part": "tactile-button", "name": name} for name in names]}))
        return path

    def test_one_name_is_the_builds_view_of_a_name(self):
        # `signal_name` prefixes an instance's signals with its name in capitals, so that is what tells names apart.
        self.assertEqual(loader.one_name("OpenLid"), loader.one_name("Openlid"))
        self.assertEqual(loader.one_name("OpenLid"), loader.signal_name({"_instance": "OpenLid"}, {"signal": "X"})[:-2])
        self.assertNotEqual(loader.one_name("Btn_Open"), loader.one_name("BtnOpen"))

    def test_needs_tells_names_apart_the_same_way(self):
        # W16: `needs._one_name` was a second copy of the rule for the picks it writes; now it is a pointer.
        from spark.design import needs
        self.assertIs(needs._one_name, loader.one_name)

    def test_two_entries_whose_names_differ_only_in_capitals_are_refused_where_the_file_is_read(self):
        path = self.entries("OpenLid", "Openlid")
        with self.assertRaises(loader.DesignError) as caught:
            loader.read(path)
        self.assertEqual(str(caught.exception), "%s: parts[0] is called OpenLid and parts[1] Openlid — the build refuses two "
                                                 "components of one name, and capitals do not make two names; give one of them a "
                                                 'name of its own, {"part": "tactile-button", "name": …}' % path)

    def test_a_name_given_by_hand_beside_one_a_need_wrote_in_other_capitals_is_refused_too(self):
        # MODE by hand, Mode written by `needs --requirements` after its need: one name, the same refusal.
        with self.assertRaises(loader.DesignError) as caught:
            loader.read(self.entries("MODE", "Mode"))
        self.assertIn("parts[0] is called MODE and parts[1] Mode", str(caught.exception))

    def test_one_name_written_twice_is_refused_by_the_same_rule_without_the_capitals_rider(self):
        # The rule is the same; the sentence about capitals is for two spellings, and BtnLeft twice has one.
        with self.assertRaises(loader.DesignError) as caught:
            loader.read(self.entries("BtnLeft", "BtnLeft"))
        self.assertIn("parts[0] is called BtnLeft and parts[1] BtnLeft — the build refuses two components of one name; "
                      "give one of them", str(caught.exception))
        self.assertNotIn("capitals", str(caught.exception))

    def test_names_that_differ_by_more_than_capitals_pass(self):
        self.assertEqual([entry["name"] for entry in loader.read(self.entries("BtnOpen", "BtnMode", "Btn_Open"))["parts"]],
                         ["BtnOpen", "BtnMode", "Btn_Open"])

    def test_a_signal_written_by_hand_under_an_instances_signal_name_is_refused_where_the_signals_are_derived(self):
        # The route the names compare does not see: `signals` holds OPENLID_BUTTON beside an instance called OpenLid. One
        # signal to the assigner and the generator — placed twice, both pins traced to one pad, "the chain runs end to end".
        root, path = project(requirements={"board": "firebeetle2-esp32s3",
                                           "parts": [{"part": "tactile-button", "name": "OpenLid"}],
                                           "signals": [{"name": "OPENLID_BUTTON", "needs": []}]})
        with self.assertRaises(loader.DesignError) as caught:
            loader.load(path)
        self.assertEqual(str(caught.exception), "OpenLid's BUTTON and signals[0] are both OPENLID_BUTTON — one signal, which "
                                                 "the pin assigner would place twice and the generator trace to one pad from two "
                                                 "pins; give one of them a name of its own")

    def test_two_unnamed_parts_asking_for_one_signal_are_refused_by_the_same_compare(self):
        # Not the component-name rule (that is `read`'s and the generator's): two parts, named or not, whose signals land on
        # one name. Here the same part twice, unnamed, so both ask for BUTTON.
        root, path = project(requirements={"board": "firebeetle2-esp32s3", "parts": ["tactile-button", "tactile-button"]})
        with self.assertRaises(loader.DesignError) as caught:
            loader.load(path)
        self.assertIn("tactile-button's BUTTON and tactile-button's BUTTON are both BUTTON", str(caught.exception))

    def test_two_hand_written_signals_of_one_name_are_refused_naming_both_entries(self):
        root, path = project(requirements={"board": "firebeetle2-esp32s3", "parts": [],
                                           "signals": [{"name": "LED", "needs": []}, {"name": "LED", "needs": []}]})
        with self.assertRaises(loader.DesignError) as caught:
            loader.load(path)
        self.assertIn("signals[0] and signals[1] are both LED", str(caught.exception))

    def test_a_hand_written_signal_of_its_own_name_passes_beside_an_instance(self):
        root, path = project(requirements={"board": "firebeetle2-esp32s3",
                                           "parts": [{"part": "tactile-button", "name": "OpenLid"}],
                                           "signals": [{"name": "LED_STATUS", "needs": []}]})
        self.assertEqual([signal["name"] for signal in loader.load(path).signals], ["OPENLID_BUTTON", "LED_STATUS"])

    def test_an_entry_with_no_name_or_no_shape_is_left_to_the_parts_reader(self):
        # The compare is on the names the file gives; what is wrong with an entry's shape is `requested_parts`' sentence.
        path = Path(tempfile.mkdtemp()) / "r.json"
        path.write_text(json.dumps({"board": "firebeetle2-esp32s3",
                                    "parts": ["tactile-button", {"part": "tactile-button"}, {"name": 7}, 42]}))
        self.assertEqual(len(loader.read(path)["parts"]), 4)


# --- MVP --- (P513, #709) a requirements signal with a part's signal name and a `pin` sets that signal's pin
class APartSignalIsPinnedByNameTest(unittest.TestCase):
    """
    Walk 4 (G27): the GDI cable fixes the display's pins, and `signals: [{"name": "TFT_BL", "pin": "D13"}]` beside the
    display was refused as "both TFT_BL". Now the entry is the part signal's pin, and P163's refusal stays for an entry
    with no `pin`. The display's record is the fixture P512 added; the store is never read.
    """

    GDI_PINS = {"TFT_BL": "D13", "TFT_CS": "D6", "TFT_RST": "D3", "SD_CS": "D7"}  # the cable's labels, no bus line

    @staticmethod
    def load(parts, signals):
        root, path = project(requirements={"board": "firebeetle2-esp32s3", "parts": parts, "signals": signals})
        (root / "parts").mkdir()
        (root / "parts" / "dfr0664-tft-2in.json").write_bytes((ROOT / "tests" / "data" / "parts" /
                                                                "dfr0664-tft-2in.json").read_bytes())
        return path

    def named(self, path, name):
        found = [signal for signal in loader.load(path).signals if signal["name"] == name]
        self.assertEqual(len(found), 1, found)
        return found[0]

    def test_the_entry_sets_the_part_signals_pin_and_adds_no_second_signal(self):
        bl = self.named(self.load(["dfr0664-tft-2in"], [{"name": "TFT_BL", "pin": "D13"}]), "TFT_BL")
        self.assertEqual((bl["pin"], bl["from"], bl["needs"]), ("D13", "dfr0664-tft-2in", ["pwm"]))

    def test_an_instances_signal_is_pinned_by_its_instance_name(self):
        path = self.load([{"part": "dfr0664-tft-2in", "name": "Screen"}], [{"name": "SCREEN_TFT_BL", "pin": "D13"}])
        self.assertEqual(self.named(path, "SCREEN_TFT_BL")["pin"], "D13")

    def test_an_entry_with_no_pin_is_still_refused_as_one_signal_twice(self):
        with self.assertRaises(loader.DesignError) as caught:
            loader.load(self.load(["dfr0664-tft-2in"], [{"name": "TFT_BL", "needs": []}]))
        self.assertIn("dfr0664-tft-2in's TFT_BL and signals[0] are both TFT_BL", str(caught.exception))

    def test_a_second_pin_for_one_signal_is_refused_naming_its_own_entry(self):
        with self.assertRaises(loader.DesignError) as caught:
            loader.load(self.load(["dfr0664-tft-2in"], [{"name": "TFT_BL", "pin": "D13"}, {"name": "TFT_BL", "pin": "D6"}]))
        self.assertIn("dfr0664-tft-2in's TFT_BL and signals[1] are both TFT_BL", str(caught.exception))

    def test_a_pinning_entry_with_another_key_is_refused_by_name(self):
        with self.assertRaises(loader.DesignError) as caught:
            loader.load(self.load(["dfr0664-tft-2in"], [{"name": "TFT_BL", "pin": "D13", "needs": []}]))
        self.assertEqual(str(caught.exception), "signals[0] pins dfr0664-tft-2in's TFT_BL and also gives needs; an entry "
                                                 "that pins a part's signal holds only `name` and `pin`, and the part's "
                                                 "record says the rest")

    def test_a_pinning_entry_that_gives_a_bus_is_refused_too(self):
        with self.assertRaises(loader.DesignError) as caught:
            loader.load(self.load(["dfr0664-tft-2in"], [{"name": "TFT_BL", "pin": "D13", "bus": "spi"}]))
        self.assertIn("signals[0] pins dfr0664-tft-2in's TFT_BL and also gives bus;", str(caught.exception))

    def test_a_pin_on_a_bus_line_is_refused_by_name(self):
        # Review of #727: MOSI pinned to D13 landed on GPIO21, and a second SPI part then took GPIO15 — a split bus, exit 0.
        for parts in (["dfr0664-tft-2in"], ["dfr0664-tft-2in", {"part": "dfr0664-tft-2in", "name": "Two"}]):
            with self.subTest(parts=len(parts)), self.assertRaises(loader.DesignError) as caught:
                loader.load(self.load(parts, [{"name": "MOSI", "pin": "D13"}]))
            self.assertEqual(str(caught.exception), "signals[0] pins dfr0664-tft-2in's MOSI, an SPI bus line: the "
                                                     "assigner places the bus, so drop `pin`")

    def test_a_pinning_entry_that_differs_from_a_part_signal_only_in_capitals_is_refused(self):
        # Review of #727: `tft_bl` added a stray signal on GPIO21 and left TFT_BL unpinned; the names compare is exact.
        with self.assertRaises(loader.DesignError) as caught:
            loader.load(self.load(["dfr0664-tft-2in"], [{"name": "tft_bl", "pin": "D13"}]))
        self.assertEqual(str(caught.exception), "signals[0] pins tft_bl, and no part has a signal of that name; did you "
                                                 "mean TFT_BL, dfr0664-tft-2in's TFT_BL? A signal's name is exact")

    def test_a_pin_the_board_lacks_is_refused_by_name(self):
        loaded = loader.load(self.load(["dfr0664-tft-2in"], [{"name": "TFT_BL", "pin": "D99"}]))
        with self.assertRaises(pin_assigner.ImpossibleError) as caught:
            pin_assigner.assign(loaded.board, loaded.signals)
        self.assertEqual(str(caught.exception), "TFT_BL asks for pin 'D99', which this board does not bring out")

    def test_the_four_gdi_pins_place_and_the_pin_map_names_them(self):
        # Done when (P513): the 4 GDI signals that are no bus line on the cable's labels. The SPI lines need no pin and
        # land on the cable's GPIO 17, 15 and 16. DC is not pinned, so it lands on A5 (GPIO11), NOT the cable's GPIO3:
        # the GDI display does not work through spark until P527 (#726).
        path = self.load(["dfr0664-tft-2in"], [{"name": name, "pin": pin} for name, pin in self.GDI_PINS.items()])
        module = pin_assigner.pin_module_for(path).module
        for name, gpio in (("TFT_BL", 21), ("TFT_CS", 18), ("TFT_RST", 38), ("SD_CS", 9), ("SCLK", 17), ("MOSI", 15),
                           ("MISO", 16), ("TFT_DC", 11)):
            with self.subTest(signal=name):
                self.assertRegex(module, r"(?m)^%s = %d\b" % (name, gpio))

    def test_dc_on_the_cables_strap_pin_is_refused_with_the_way_out(self):
        # Close audit C4 stays (the PO, 2026-11-02): D2 is GPIO3, read at reset. The refusal says what to do.
        signals = [{"name": name, "pin": pin} for name, pin in dict(self.GDI_PINS, TFT_DC="D2").items()]
        with self.assertRaises(pin_assigner.ImpossibleError) as caught:
            pin_assigner.pin_module_for(self.load(["dfr0664-tft-2in"], signals))
        self.assertEqual(str(caught.exception),
                         "TFT_DC asks for D2 by name, and GPIO3 is strapping — a pin this never offers, because the chip "
                         "reads it at reset; drop `pin` and spark picks another, or see P527 (#726) for a pin a connector "
                         "fixes")


if __name__ == "__main__":
    unittest.main()


class TheBoardsOwnPullUpTest(unittest.TestCase):
    """P204, the PO's rule of 2026-10-12: prefer what the board offers. A button's pull-up is the board's internal one."""

    BOARD = {"power": {"internal_pull_up_ohms": {"value": 45000, "verified": True, "source": "test"}}}

    @staticmethod
    def button(wakes=False):
        need = {"signal": "BUTTON", "pin": "A", "direction": "in", "needs": ["wake"] if wakes else []}
        return {"id": "tactile-button", "needs": [need],
                "host_parts": [{"kind": "pullup", "pin": "A", "ohms": 10000, "internal_will_do": True, "why": "t"},
                               {"kind": "series", "pin": "A", "ohms": 330, "why": "t"}]}

    def test_on_a_board_with_an_internal_pull_up_the_firmware_holds_the_pin(self):
        part = loader.firmware_pulls(self.button(), self.BOARD)
        self.assertEqual([host["kind"] for host in part["host_parts"]], ["series"])
        self.assertEqual(part["_firmware_pulls"], ["A"])

    def test_a_pin_that_wakes_the_chip_keeps_its_resistor(self):
        part = loader.firmware_pulls(self.button(wakes=True), self.BOARD)
        self.assertEqual(len(part["host_parts"]), 2)
        self.assertNotIn("_firmware_pulls", part)

    def test_a_bare_pull_up_number_leaves_the_pull_to_the_firmware(self):
        # P431: a number where a fact belongs reads as the pull, as a bare `io_volts` does. On main it raised AttributeError.
        part = loader.firmware_pulls(self.button(), {"power": {"internal_pull_up_ohms": 10000}})
        self.assertEqual(part["_firmware_pulls"], ["A"])

    def test_a_bare_value_that_is_no_positive_number_keeps_the_resistor(self):
        # P431: a bare value is read as the pull only when it is a number above zero, never "unknown", true, a list or NaN.
        for bare in ("unknown", "null", True, [0], 0, -5, float("nan"), float("inf"), None):
            with self.subTest(bare=bare):
                part = loader.firmware_pulls(self.button(), {"power": {"internal_pull_up_ohms": bare}})
                self.assertEqual([host["kind"] for host in part["host_parts"]], ["pullup", "series"])
                self.assertNotIn("_firmware_pulls", part)

    def test_a_fact_whose_value_is_no_positive_number_keeps_the_resistor(self):
        for value in ("unknown", True, 0, None):
            with self.subTest(value=value):
                board = {"power": {"internal_pull_up_ohms": {"value": value, "verified": False, "source": "test"}}}
                self.assertEqual(len(loader.firmware_pulls(self.button(), board)["host_parts"]), 2)

    def test_a_400_digit_pull_up_number_does_not_crash_the_design(self):
        # P431 refuter: json.loads gives a Python int of any size, and math.isfinite raised OverflowError on it.
        huge = 10 ** 400
        for stated in (huge, {"value": huge, "verified": False, "source": "test"}):
            with self.subTest(stated=type(stated).__name__):
                part = loader.firmware_pulls(self.button(), {"power": {"internal_pull_up_ohms": stated}})
                self.assertEqual(part["_firmware_pulls"], ["A"])

    def test_a_board_that_states_no_internal_pull_up_keeps_every_resistor(self):
        self.assertEqual(loader.firmware_pulls(self.button(), {"power": {}}), self.button())
        self.assertEqual(loader.firmware_pulls(self.button(), None), self.button())


# --- MVP --- (P700)
class EachDesignRefusalCarriesItsCodeTest(unittest.TestCase):
    """P700: every DesignError carries its code (design_codes) beside its sentence, and an agent decides on the code."""

    def code_of(self, call, *args):
        with self.assertRaises(loader.DesignError) as caught:
            call(*args)
        return caught.exception.code

    def read_code(self, text):
        path = Path(tempfile.mkdtemp()) / "car.requirements.json"
        path.write_text(text if isinstance(text, str) else json.dumps(text))
        return self.code_of(loader.read, path)

    def record_folder(self, body):
        """A project whose parts/x.json holds `body`, or is a folder when `body` is None."""
        root = Path(tempfile.mkdtemp())
        (root / ".spark").mkdir()
        (root / "parts").mkdir()
        if body is None:
            (root / "parts" / "x.json").mkdir()
        else:
            (root / "parts" / "x.json").write_text(body)
        return root

    def test_the_requirements_file_itself(self):
        self.assertEqual(self.code_of(loader.read, Path(tempfile.mkdtemp()) / "nope.json"), "no_requirements")
        self.assertEqual(self.read_code("{not json"), "requirements_unreadable")
        self.assertEqual(self.read_code([1, 2]), "requirements_field_wrong")

    @unittest.skipIf(os.geteuid() == 0, "root reads a file whatever its mode")
    def test_a_requirements_file_nobody_may_read(self):
        path = Path(tempfile.mkdtemp()) / "car.requirements.json"
        path.write_text("{}")
        path.chmod(0)
        self.addCleanup(path.chmod, 0o600)
        self.assertEqual(self.code_of(loader.read, path), "requirements_unreadable")

    def test_each_field_of_the_wrong_kind(self):
        for wanted in ({"signals": 5}, {"parts": 5}, {"signals": [{}]}, {"signals": [{"name": "X", "needs": 5}]},
                       {"signals": [{"name": "X", "pin": 4}]}, {"signals": [{"name": "X", "pin": ""}]},
                       {"signals": [{"name": "X-1"}]}):
            with self.subTest(wanted=wanted):
                self.assertEqual(self.read_code(wanted), "requirements_field_wrong")
        for wanted in ({"parts": [{"name": "X"}]}, {"parts": [{"part": "p", "name": "X-1"}]}, {"parts": [42]}):
            with self.subTest(wanted=wanted):
                self.assertEqual(self.code_of(loader.requested_parts, wanted), "requirements_field_wrong")
        for rails in ({"VCC": 5}, {"VCC": "a-b"}):
            with self.subTest(rails=rails):
                self.assertEqual(self.code_of(loader.rails_requested, {"parts": [{"part": "p", "rails": rails}]}),
                                 "requirements_field_wrong")
        self.assertEqual(self.code_of(loader.on_rails, {"id": "p", "power": []}, {"VCC": "motor"}), "requirements_field_wrong")

    def test_a_pin_entry_for_a_part_signal(self):
        signals, sources = [{"name": "SDA", "bus": "i2c"}, {"name": "LED"}], ["a's SDA", "b's LED"]
        for entry in ({"name": "led", "pin": "D0"}, {"name": "SDA", "pin": "D0"}, {"name": "LED", "pin": "D0", "needs": []}):
            with self.subTest(entry=entry):
                self.assertEqual(self.code_of(loader.pin_part_signals, signals, sources, [entry]), "requirements_field_wrong")

    def test_one_name_twice(self):
        self.assertEqual(self.read_code({"parts": [{"part": "p", "name": "Btn"}, {"part": "p", "name": "btn"}]}),
                         "name_used_twice")
        self.assertEqual(self.code_of(loader.refuse_one_signal_twice, ["a", "b"], [{"name": "X"}, {"name": "X"}]),
                         "name_used_twice")

    def test_the_project_and_its_records(self):
        self.assertEqual(self.code_of(loader.project_for, "r.json", Path(tempfile.mkdtemp()) / "nope"), "no_project_folder")
        root = self.record_folder("{not json")
        self.assertEqual(self.code_of(loader.record, "no-such-part", root), "part_unusable")
        self.assertEqual(self.code_of(loader.record, "x", root), "part_unusable")
        self.assertEqual(self.code_of(loader.record, "x", self.record_folder(None)), "part_unusable")
        self.assertEqual(self.code_of(loader.signals_of, [{"id": "no-such-part"}], {}, root), "part_unusable")
        self.assertEqual(self.code_of(loader.signals_of, [{"id": "x"}], {}, root), "part_unusable")
        self.assertEqual(self.code_of(loader.signals_of, [{"id": "x"}], {}, self.record_folder(None)), "part_unusable")

    def test_the_rules_and_the_board(self):
        root, path = project(requirements={"board": "no-such-board", "parts": []})
        self.assertEqual(self.code_of(loader.load, path), "board_unusable")
        (root / ".spark" / "rules.json").write_text("{not json")
        self.assertEqual(self.code_of(loader.rules_in, root), "rules_refused")
# --- end MVP ---
