"""
Proof that a part says what it needs, and admits what nobody has checked.

A part library is easy to build in a way that is worse than not having one. The temptation is one
schema for everything a part might have — and since a motor driver's facts have nothing in common
with a rangefinder's, that schema collapses into `{name, notes}`: documentation pretending to be
configuration. So the split is the design, and both halves are tested here.

`needs` is a real schema because it is genuinely uniform: every part asks its host for pins. It
is what makes this data rather than prose, and what `assign_pins.py` consumes.

`facts` is open, but every entry must carry a value, a source, and whether anyone actually
checked. The contract's sharpest rule is about the unverified ones: a number nobody has confirmed
must say what depends on it, or not be carried at all. That is how an assumption becomes a fact
without anyone deciding to promote it.

    python3 -m unittest discover -s tests
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import assign_pins  # noqa: E402
import parts  # noqa: E402


def part(part_id="thing", **overrides):
    return dict({
        "schema": 1, "id": part_id, "name": "A Thing", "kind": "test",
        "needs": [{"signal": "SIG", "pin": "P", "direction": "in"}],
    }, **overrides)


def written(definition):
    path = Path(tempfile.mkdtemp()) / (definition["id"] + ".json")
    path.write_text(json.dumps(definition))
    return path


class TheContractTest(unittest.TestCase):
    def _problems(self, **overrides):
        definition = part(**overrides)
        return parts.validate(definition, written(definition))

    def test_a_good_definition_passes(self):
        self.assertEqual(self._problems(), [])

    def test_a_need_with_no_pin_is_caught(self):
        problems = self._problems(needs=[{"signal": "SIG"}])
        self.assertTrue(any("has no pin" in p for p in problems))

    def test_a_nonsense_direction_is_caught(self):
        problems = self._problems(needs=[{"signal": "S", "pin": "P", "direction": "sideways"}])
        self.assertTrue(any("direction" in p for p in problems))

    def test_a_fact_without_provenance_is_caught(self):
        # A number with no source is an opinion, and this library's whole value is telling the
        # two apart.
        problems = self._problems(facts={"current_ma": {"value": 20, "verified": True}})
        self.assertTrue(any("source" in p for p in problems))

    def test_a_fact_claiming_to_be_verified_with_no_value_is_caught(self):
        problems = self._problems(
            facts={"x": {"value": None, "verified": True, "source": "somewhere"}})
        self.assertTrue(any("verified but has no value" in p for p in problems))

    def test_an_unverified_number_must_say_what_depends_on_it(self):
        # The sharpest rule in the contract. An unexplained guess with a number attached is how
        # an assumption gets treated as a fact — nobody promotes it, it just stops being
        # questioned.
        problems = self._problems(
            facts={"idle_ma": {"value": 20, "verified": False, "source": "a guess"}})
        self.assertTrue(any("why_it_matters" in p for p in problems))

    def test_an_unverified_number_WITH_a_reason_is_fine(self):
        self.assertEqual(self._problems(facts={"idle_ma": {
            "value": 20, "verified": False, "source": "a guess",
            "why_it_matters": "decides whether the battery lasts a day or a month"}}), [])

    def test_an_unknown_with_no_value_needs_no_justification(self):
        # "Nobody knows" is an honest state and must not be made tedious to record.
        self.assertEqual(self._problems(facts={"idle_ma": {
            "value": None, "verified": False, "source": "not measured"}}), [])


class WhatAPartAsksForTest(unittest.TestCase):
    def test_signals_come_out_ready_for_the_assigner(self):
        signals = parts.signals_for(["l9110s-module"])
        self.assertEqual([s["name"] for s in signals], ["MOTOR_IA", "MOTOR_IB"])
        self.assertTrue(all(s["from"] == "l9110s-module" for s in signals))

    def test_a_capability_a_part_needs_survives_into_the_signal(self):
        signals = parts.signals_for(["vl6180x-breakout"])
        interrupt = next(s for s in signals if s["name"] == "TOF_INT")
        self.assertIn("wake", interrupt["needs"])

    def test_a_bus_signal_is_marked_as_one(self):
        signals = parts.signals_for(["vl6180x-breakout"])
        self.assertEqual({s["name"] for s in signals if s.get("bus") == "i2c"}, {"SDA", "SCL"})

    def test_an_optional_signal_is_still_offered(self):
        # Dropping it silently would hide a requirement. A caller that does not want the sensor
        # to wake the host can remove it; it must not vanish on its own.
        self.assertIn("TOF_INT", [s["name"] for s in parts.signals_for(["vl6180x-breakout"])])


class WhatNobodyHasCheckedTest(unittest.TestCase):
    def test_unverified_facts_are_collected_across_parts(self):
        questions = parts.unverified(["dfr0534-module", "vl6180x-breakout"])
        self.assertTrue(questions)
        self.assertTrue(all("why_it_matters" in q for q in questions))

    def test_a_verified_fact_is_not_reported_as_open(self):
        names = {q["fact"] for q in parts.unverified(["l9110s-module"])}
        self.assertNotIn("input_high_threshold_v", names)

    def test_the_audio_module_declares_its_unmeasured_idle_current(self):
        # The single most consequential unknown on the project this came from. If the library
        # cannot surface that, it is not doing its job.
        questions = parts.unverified(["dfr0534-module"])
        self.assertIn("idle_current_ma", {q["fact"] for q in questions})


class FromPartsToAPinMapTest(unittest.TestCase):
    """The whole point: a list of modules in, a defensible pin map out."""

    def setUp(self):
        self.board = json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())
        self.signals = parts.signals_for(
            ["l9110s-module", "vl6180x-breakout", "dfr0534-module"])

    def test_every_signal_the_parts_ask_for_is_placed(self):
        assignments, _ = assign_pins.assign(self.board, self.signals)
        self.assertEqual({a["signal"] for a in assignments},
                         {s["name"] for s in self.signals})

    def test_i2c_lands_on_the_boards_own_i2c_pins(self):
        # It went to two arbitrary GPIOs once, while the pin actually labelled SDA was given to
        # an analogue input. That is wrong twice: the bus loses its hardware peripheral, and the
        # silkscreen now lies about what is connected to it.
        assignments, _ = assign_pins.assign(self.board, self.signals)
        placed = {a["signal"]: a["pin"] for a in assignments}
        self.assertEqual(placed["SDA"], "SDA")
        self.assertEqual(placed["SCL"], "SCL")

    def test_the_sensor_interrupt_lands_somewhere_that_can_wake_the_chip(self):
        assignments, _ = assign_pins.assign(self.board, self.signals)
        interrupt = next(a for a in assignments if a["signal"] == "TOF_INT")
        self.assertIn(interrupt["gpio"], self.board["wake_capable_gpio"])

    def test_nothing_lands_on_a_strapping_pin(self):
        assignments, _ = assign_pins.assign(self.board, self.signals)
        strapping = set(self.board["pin_roles"]["strapping"]["gpio"])
        self.assertEqual([a for a in assignments if a["gpio"] in strapping], [])


class WhichPadIsPinOneTest(unittest.TestCase):
    """
    The generator numbered pads from the order the pins happened to appear in the file, which is
    not a fact about any module. `pin_order` is that fact; these are the ways it can be wrong and
    still look fine.
    """

    def _problems(self, **overrides):
        definition = part(**overrides)
        return parts.validate(definition, written(definition))

    def test_a_pad_naming_something_the_part_never_mentions_is_caught(self):
        # It would silently wire nothing — the worst shape of wrong, because the file looks
        # complete and the board builds.
        problems = self._problems(pin_order=["P", "TYPO"])
        self.assertTrue(any("never mentions" in p for p in problems), problems)

    def test_a_pin_with_no_pad_is_caught(self):
        problems = self._problems(pin_order=[None, None])
        self.assertTrue(any("does not say where" in p for p in problems), problems)

    def test_the_same_pad_named_twice_is_caught(self):
        problems = self._problems(pin_order=["P", "P"])
        self.assertTrue(any("twice" in p for p in problems), problems)

    def test_an_unwired_pad_is_allowed_to_be_empty(self):
        # A module with ten pads of which you use five is the normal case; the gaps must stay
        # gaps, or everything after one shifts by a pad.
        self.assertEqual(self._problems(pin_order=[None, "P", None]), [])

    def test_a_part_that_records_no_pinout_at_all_still_validates(self):
        # Absent is honest — four different VL6180X breakouts exist with different pinouts. The
        # generator refuses such a part; the contract does not force a guess into the file.
        self.assertEqual(self._problems(), [])


class AProjectCanExtendTheLibraryTest(unittest.TestCase):
    """
    Every function here took `project`, the docstring promised "a project's own wins", and
    `main()` never passed one. So the override was unreachable from every entry point and the
    library was closed at whatever ships with the plugin — a stranger's first part could not be
    added, which makes the library a private data file with a read-only API.
    """

    def setUp(self):
        self.project = Path(tempfile.mkdtemp())
        (self.project / "parts").mkdir()
        self.own = part("ssd1306-oled", name="SSD1306 OLED", kind="display")
        (self.project / "parts" / "ssd1306-oled.json").write_text(json.dumps(self.own))

    def test_a_projects_own_part_is_listed(self):
        self.assertIn("ssd1306-oled", parts.available(self.project))
        self.assertNotIn("ssd1306-oled", parts.available())

    def test_a_projects_own_part_can_be_loaded_and_asked_for_signals(self):
        self.assertEqual(parts.load("ssd1306-oled", self.project)["name"], "SSD1306 OLED")
        self.assertTrue(parts.signals_for(["ssd1306-oled"], self.project))

    def test_a_project_definition_beats_the_shipped_one_of_the_same_name(self):
        # The reason the override exists: what you verified yourself must not be replaced by a
        # plugin update.
        shadowed = part("l9110s-module", name="My own measured L9110S")
        (self.project / "parts" / "l9110s-module.json").write_text(json.dumps(shadowed))
        self.assertEqual(parts.load("l9110s-module", self.project)["name"],
                         "My own measured L9110S")

    def test_the_cli_reaches_it(self):
        # The defect was exactly here: the library functions worked and no flag could get to them.
        self.assertEqual(parts.main(["--show", "ssd1306-oled", "--project", str(self.project)]),
                         parts.EXIT_OK)

    def test_the_cli_without_a_project_still_cannot_see_it(self):
        self.assertEqual(parts.main(["--show", "ssd1306-oled"]), parts.EXIT_INVALID)


class TheShippedLibraryTest(unittest.TestCase):
    def test_every_part_shipped_satisfies_the_contract(self):
        for part_id in parts.available():
            with self.subTest(part=part_id):
                path = parts.definition_path(part_id)
                problems = parts.validate(json.loads(path.read_text()), path)
                self.assertEqual(problems, [], "%s: %s" % (part_id, problems))

    def test_every_shipped_part_can_produce_signals(self):
        for part_id in parts.available():
            with self.subTest(part=part_id):
                self.assertTrue(parts.signals_for([part_id]),
                                "%s asks its host for nothing at all" % part_id)


if __name__ == "__main__":
    unittest.main()
