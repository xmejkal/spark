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
import suite_temp  # noqa: E402,F401  P172: this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import design  # noqa: E402


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
        with self.assertRaises(design.DesignError) as caught:
            design.read(Path(tempfile.mkdtemp()) / "nope.json")
        self.assertIn("no requirements at", str(caught.exception))

    def test_malformed_json_is_a_sentence_naming_the_file(self):
        # Was a JSONDecodeError traceback, exit 1, in three scripts (audit A8).
        path = Path(tempfile.mkdtemp()) / "bad.json"
        path.write_text("{not json")
        with self.assertRaises(design.DesignError) as caught:
            design.read(path)
        self.assertIn("bad.json", str(caught.exception))
        self.assertIn("not JSON", str(caught.exception))

    def test_a_list_is_not_a_requirements_file(self):
        path = Path(tempfile.mkdtemp()) / "list.json"
        path.write_text("[1, 2]")
        with self.assertRaises(design.DesignError):
            design.read(path)

    def test_an_entry_without_a_part_is_a_sentence_not_a_key_error(self):
        with self.assertRaises(design.DesignError) as caught:
            design.requested_parts({"parts": [{"name": "X"}]})
        self.assertIn("parts[0]", str(caught.exception))

    def test_an_entry_of_the_wrong_type_is_refused(self):
        with self.assertRaises(design.DesignError):
            design.requested_parts({"parts": [42]})

    def test_an_instance_whose_name_is_no_name_is_refused(self):
        # P87's attribute half: the instance's name is the component the board is written with, `<chip name="…">`
        for name in ('Btn" pcbX={(globalThis.x = 1, 0)} y="', "Btn Open", "Btn-Open"):
            with self.subTest(name=name):
                with self.assertRaises(design.DesignError) as caught:
                    design.requested_parts({"parts": [{"part": "tactile-button", "name": name}]})
                self.assertTrue(str(caught.exception).startswith("parts[0] calls its instance %r, but" % name), str(caught.exception))
                self.assertIn("the board is written with it as code", str(caught.exception))
        self.assertEqual(design.requested_parts({"parts": [{"part": "tactile-button", "name": "Btn_Open2"}]}),
                         [("tactile-button", "Btn_Open2")])

    def test_a_signal_the_requirements_name_that_is_no_name_is_refused(self):
        # P87's attribute half, as for a part's signal: the pin map and the board name it, and firmware is written against it
        path = Path(tempfile.mkdtemp()) / "r.json"
        path.write_text(json.dumps({"board": "firebeetle2-esp32s3", "parts": [], "signals": [{"name": 'LED" x="', "needs": []}]}))
        with self.assertRaises(design.DesignError) as caught:
            design.read(path)
        self.assertEqual(str(caught.exception), "%s: signals[0] is named 'LED\" x=\"', but a signal is a name — letters, digits "
                                                 "and _ (LED_STATUS): the pin map and the board name it, and firmware is written "
                                                 "against it" % path)

    def test_the_two_entry_forms_normalise_to_one(self):
        self.assertEqual(design.requested_parts(
            {"parts": ["l9110s-module", {"part": "tactile-button", "name": "BtnForward"}]}),
            [("l9110s-module", None), ("tactile-button", "BtnForward")])


class TheProjectIsTheFilesTest(unittest.TestCase):
    def test_the_flag_wins(self):
        root, path = project()
        other = Path(tempfile.mkdtemp())
        self.assertEqual(design.project_for(path, str(other)), other.resolve())

    def test_found_up_from_the_file_not_from_the_current_directory(self):
        # The spine resolved from cwd and, from /tmp, could not find a part sitting beside the
        # requirements file (audit A10). Two directories down from the project, run from
        # elsewhere: still that project.
        root, path = project(sub="designs/v2")
        with elsewhere():
            self.assertEqual(design.project_for(path), root.resolve())

    def test_a_file_in_no_project_is_built_from_the_plugins_library(self):
        # The decision changed 2026-09-29 (audit B5): this raised, and every documented step
        # refused "no project here" from a fresh directory while `check_spine` alone fell back.
        path = Path(tempfile.mkdtemp()) / "loose.json"
        path.write_text("{}")
        with elsewhere():
            project = design.project_for(path)
        self.assertTrue(design.is_library(project))
        self.assertFalse(design.is_library(tempfile.mkdtemp()))

    def test_a_design_from_nowhere_has_no_rules(self):
        path = Path(tempfile.mkdtemp()) / "loose.json"
        path.write_text(json.dumps({"board": "firebeetle2-esp32s3", "parts": ["l9110s-module"]}))
        loaded = design.load(path)
        self.assertTrue(design.is_library(loaded.project))
        self.assertEqual(loaded.rules, {})


class LoadingTest(unittest.TestCase):
    RULES = {"physics": {"rails": {"MOTOR6V": {"max_current_a": 2.0}}}}

    def test_the_rules_are_the_resolved_projects_from_anywhere(self):
        # The cause of the unsized car (audit A2): rules looked up by the raw flag, None
        # without it. Loaded from elsewhere, with no flag, the rules are still the project's.
        root, path = project(rules=self.RULES)
        with elsewhere():
            loaded = design.load(path)
        self.assertEqual(loaded.project, root.resolve())
        self.assertEqual(loaded.rules, self.RULES)

    def test_no_rules_file_is_no_rules_not_an_error(self):
        root, path = project()
        self.assertEqual(design.load(path).rules, {})

    def test_an_unreadable_rules_file_is_an_error_not_no_rules(self):
        # Silently "no rules" would size nothing and call every width unjustified while the
        # file that justifies them sits right there.
        root, path = project()
        (root / ".spark" / "rules.json").write_text("{broken")
        with self.assertRaises(design.DesignError) as caught:
            design.load(path)
        self.assertIn("rules.json", str(caught.exception))

    def test_parts_come_back_as_instances(self):
        root, path = project(requirements={
            "board": "firebeetle2-esp32s3",
            "parts": [{"part": "vl6180x-breakout", "name": "Rangefinder"}, "l9110s-module"]})
        loaded = design.load(path)
        self.assertEqual([p.get("_instance") for p in loaded.parts], ["Rangefinder", None])
        self.assertEqual([p["id"] for p in loaded.parts], ["vl6180x-breakout", "l9110s-module"])

    def test_an_unknown_part_is_a_sentence(self):
        root, path = project(requirements={"board": "firebeetle2-esp32s3", "parts": ["unobtainium"]})
        with self.assertRaises(design.DesignError) as caught:
            design.load(path)
        self.assertIn("unobtainium", str(caught.exception))

    def test_an_unknown_board_is_a_sentence(self):
        root, path = project(requirements={"board": "no-such-board", "parts": []})
        with self.assertRaises(design.DesignError):
            design.load(path)

    def test_the_board_can_be_overridden(self):
        root, path = project()
        self.assertEqual(design.load(path, board_id="xiao-esp32-c6").board["id"], "xiao-esp32-c6")



class ARailBelongsToTheDesignTest(unittest.TestCase):
    """
    The RC car copied the whole shipped L9110S record to change `motor` to `traction` (G5).
    A requirements entry says it instead, and the library's record is never touched.
    """

    ENTRY = {"part": "l9110s-module", "name": "Drive", "rails": {"VCC": "traction"}}

    def test_a_pins_rail_can_be_re_pointed_from_the_requirements(self):
        root, path = project(requirements={"board": "firebeetle2-esp32s3", "parts": [self.ENTRY]})
        [drive] = design.load(path).parts
        rails = {supply["pin"]: supply["rail"] for supply in drive["power"]}
        self.assertEqual(rails["VCC"], "traction")
        self.assertEqual(rails["GND"], "ground", "only the named pin moves")
        self.assertEqual(drive["_instance"], "Drive")

    def test_on_rails_returns_a_copy_and_leaves_its_argument_as_loaded(self):
        # The first version of this test re-loaded the record from disk afterwards, which
        # `parts.load` does fresh every time — so an in-place edit was invisible and the mutation
        # escaped (W12). The contract is on the function: its argument is untouched.
        import parts
        record = parts.load("l9110s-module")
        moved = design.on_rails(record, {"VCC": "traction"})
        self.assertEqual([s["rail"] for s in moved["power"] if s["pin"] == "VCC"], ["traction"])
        self.assertEqual([s["rail"] for s in record["power"] if s["pin"] == "VCC"], ["motor"])
        self.assertIsNot(moved["power"], record["power"])

    def test_a_pin_the_part_does_not_have_is_a_sentence(self):
        entry = dict(self.ENTRY, rails={"VIN": "traction"})
        root, path = project(requirements={"board": "firebeetle2-esp32s3", "parts": [entry]})
        with self.assertRaises(design.DesignError) as caught:
            design.load(path)
        self.assertIn("VIN", str(caught.exception))
        self.assertIn("VCC", str(caught.exception), "the message names the pins it does have")

    def test_rails_must_be_a_pin_to_rail_map(self):
        with self.assertRaises(design.DesignError):
            design.rails_requested({"parts": [dict(self.ENTRY, rails=["traction"])]})

    def test_a_rail_the_requirements_give_that_is_no_name_is_refused(self):
        # P87's attribute half: the rail becomes the net the pin's trace is written to
        with self.assertRaises(design.DesignError) as caught:
            design.rails_requested({"parts": [dict(self.ENTRY, rails={"VCC": 'traction" x="'})]})
        self.assertEqual(str(caught.exception), "parts[0].rails puts VCC on 'traction\" x=\"', but a rail is a name — letters, "
                                                 "digits and _ (traction, motor): the board is written with it as code")

    def test_an_unnamed_entry_can_carry_rails_too(self):
        entry = {"part": "l9110s-module", "rails": {"VCC": "traction"}}
        root, path = project(requirements={"board": "firebeetle2-esp32s3", "parts": [entry]})
        [drive] = design.load(path).parts
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
        names = [signal["name"] for signal in design.load(path).signals]
        self.assertEqual(len(names), len(set(names)), names)
        self.assertTrue(any(name.startswith("BTNOPEN_") for name in names), names)
        self.assertTrue(any(name.startswith("BTNMODE_") for name in names), names)
        self.assertIn("MOTOR_IA", names)

    def test_the_requirements_own_signals_come_last(self):
        root, path = project(requirements={
            "board": "firebeetle2-esp32s3", "parts": ["l9110s-module"],
            "signals": [{"name": "LED_STATUS", "needs": []}]})
        self.assertEqual(design.load(path).signals[-1]["name"], "LED_STATUS")

    def test_a_malformed_project_part_is_a_sentence_naming_the_part(self):
        root, path = project()
        (root / "parts").mkdir()
        (root / "parts" / "l9110s-module.json").write_text("{half a record")
        with self.assertRaises(design.DesignError) as caught:
            design.load(path)
        self.assertIn("l9110s-module", str(caught.exception))


class ABusSignalKeepsItsLineTest(unittest.TestCase):
    def test_a_named_instances_bus_signal_still_says_which_line_it_is(self):
        # The instance prefix renames the signal; the bus line it is has to survive the rename,
        # or the assigner cannot find the board's pin for it (P21).
        root, path = project(requirements={"board": "firebeetle2-esp32s3",
                                           "parts": [{"part": "vl6180x-breakout", "name": "Rangefinder"}]})
        signals = {s["name"]: s for s in design.load(path).signals}
        self.assertEqual(signals["RANGEFINDER_SDA"]["line"], "SDA")
        self.assertEqual(signals["RANGEFINDER_SDA"]["bus"], "i2c")


class RulesInTest(unittest.TestCase):
    def test_rules_in_reads_the_projects_rules_or_none(self):
        root = Path(tempfile.mkdtemp())
        self.assertEqual(design.rules_in(root), {})
        (root / ".spark").mkdir()
        (root / ".spark" / "rules.json").write_text(json.dumps({"physics": {"i2c_hz": 400000}}))
        self.assertEqual(design.rules_in(root)["physics"]["i2c_hz"], 400000)


class TheInputIsCheckedWhereItIsReadTest(unittest.TestCase):
    def test_a_project_that_does_not_exist_is_a_sentence_naming_it(self):
        # Close audit C5: a typo'd --project resolved to a path nobody checked, and a project's
        # rules were dropped with exit 0.
        root, path = project(rules={"physics": {"rails": {"MOTOR6V": {"max_current_a": 2.0}}}})
        with self.assertRaises(design.DesignError) as caught:
            design.load(path, project=str(root / "typo"))
        self.assertIn("typo", str(caught.exception))

    def test_a_signal_without_a_name_is_a_sentence_naming_the_entry(self):
        # Close audit C7: a KeyError through both mains and "the chain is broken" in the spine.
        root, path = project(requirements={"board": "firebeetle2-esp32s3", "parts": [],
                                           "signals": [{"needs": []}]})
        with self.assertRaises(design.DesignError) as caught:
            design.read(path)
        self.assertIn("signals[0]", str(caught.exception))
        path.write_text(json.dumps({"board": "firebeetle2-esp32s3", "parts": [],
                                    "signals": [{"name": "X", "needs": "wake"}]}))
        with self.assertRaises(design.DesignError):
            design.read(path)


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
        self.assertEqual(design.one_name("OpenLid"), design.one_name("Openlid"))
        self.assertEqual(design.one_name("OpenLid"), design.signal_name({"_instance": "OpenLid"}, {"signal": "X"})[:-2])
        self.assertNotEqual(design.one_name("Btn_Open"), design.one_name("BtnOpen"))

    def test_needs_tells_names_apart_the_same_way(self):
        # W16: `needs._one_name` was a second copy of the rule for the picks it writes; now it is a pointer.
        import needs
        self.assertIs(needs._one_name, design.one_name)

    def test_two_entries_whose_names_differ_only_in_capitals_are_refused_where_the_file_is_read(self):
        path = self.entries("OpenLid", "Openlid")
        with self.assertRaises(design.DesignError) as caught:
            design.read(path)
        self.assertEqual(str(caught.exception), "%s: parts[0] is called OpenLid and parts[1] Openlid — the build refuses two "
                                                 "components of one name, and capitals do not make two names; give one of them a "
                                                 'name of its own, {"part": "tactile-button", "name": …}' % path)

    def test_a_name_given_by_hand_beside_one_a_need_wrote_in_other_capitals_is_refused_too(self):
        # MODE by hand, Mode written by `needs --requirements` after its need: one name, the same refusal.
        with self.assertRaises(design.DesignError) as caught:
            design.read(self.entries("MODE", "Mode"))
        self.assertIn("parts[0] is called MODE and parts[1] Mode", str(caught.exception))

    def test_one_name_written_twice_is_refused_by_the_same_rule_without_the_capitals_rider(self):
        # The rule is the same; the sentence about capitals is for two spellings, and BtnLeft twice has one.
        with self.assertRaises(design.DesignError) as caught:
            design.read(self.entries("BtnLeft", "BtnLeft"))
        self.assertIn("parts[0] is called BtnLeft and parts[1] BtnLeft — the build refuses two components of one name; "
                      "give one of them", str(caught.exception))
        self.assertNotIn("capitals", str(caught.exception))

    def test_names_that_differ_by_more_than_capitals_pass(self):
        self.assertEqual([entry["name"] for entry in design.read(self.entries("BtnOpen", "BtnMode", "Btn_Open"))["parts"]],
                         ["BtnOpen", "BtnMode", "Btn_Open"])

    def test_a_signal_written_by_hand_under_an_instances_signal_name_is_refused_where_the_signals_are_derived(self):
        # The route the names compare does not see: `signals` holds OPENLID_BUTTON beside an instance called OpenLid. One
        # signal to the assigner and the generator — placed twice, both pins traced to one pad, "the chain runs end to end".
        root, path = project(requirements={"board": "firebeetle2-esp32s3",
                                           "parts": [{"part": "tactile-button", "name": "OpenLid"}],
                                           "signals": [{"name": "OPENLID_BUTTON", "needs": []}]})
        with self.assertRaises(design.DesignError) as caught:
            design.load(path)
        self.assertEqual(str(caught.exception), "OpenLid's BUTTON and signals[0] are both OPENLID_BUTTON — one signal, which "
                                                 "the pin assigner would place twice and the generator trace to one pad from two "
                                                 "pins; give one of them a name of its own")

    def test_two_unnamed_parts_asking_for_one_signal_are_refused_by_the_same_compare(self):
        # Not the component-name rule (that is `read`'s and the generator's): two parts, named or not, whose signals land on
        # one name. Here the same part twice, unnamed, so both ask for BUTTON.
        root, path = project(requirements={"board": "firebeetle2-esp32s3", "parts": ["tactile-button", "tactile-button"]})
        with self.assertRaises(design.DesignError) as caught:
            design.load(path)
        self.assertIn("tactile-button's BUTTON and tactile-button's BUTTON are both BUTTON", str(caught.exception))

    def test_two_hand_written_signals_of_one_name_are_refused_naming_both_entries(self):
        root, path = project(requirements={"board": "firebeetle2-esp32s3", "parts": [],
                                           "signals": [{"name": "LED", "needs": []}, {"name": "LED", "needs": []}]})
        with self.assertRaises(design.DesignError) as caught:
            design.load(path)
        self.assertIn("signals[0] and signals[1] are both LED", str(caught.exception))

    def test_a_hand_written_signal_of_its_own_name_passes_beside_an_instance(self):
        root, path = project(requirements={"board": "firebeetle2-esp32s3",
                                           "parts": [{"part": "tactile-button", "name": "OpenLid"}],
                                           "signals": [{"name": "LED_STATUS", "needs": []}]})
        self.assertEqual([signal["name"] for signal in design.load(path).signals], ["OPENLID_BUTTON", "LED_STATUS"])

    def test_an_entry_with_no_name_or_no_shape_is_left_to_the_parts_reader(self):
        # The compare is on the names the file gives; what is wrong with an entry's shape is `requested_parts`' sentence.
        path = Path(tempfile.mkdtemp()) / "r.json"
        path.write_text(json.dumps({"board": "firebeetle2-esp32s3",
                                    "parts": ["tactile-button", {"part": "tactile-button"}, {"name": 7}, 42]}))
        self.assertEqual(len(design.read(path)["parts"]), 4)


if __name__ == "__main__":
    unittest.main()
