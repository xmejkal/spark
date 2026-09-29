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

    def test_a_need_with_no_pin_is_caught_even_when_the_part_has_a_pin_order(self):
        """
        The validator crashed on exactly the malformation it exists to catch.

        `needs[0] has no pin` was appended, and three lines later the pin_order block read
        `need["pin"]` on that same entry and raised KeyError. Every real part has a pin_order, so
        any part broken this way took the whole run down instead of being reported — and the run
        it took down was `--validate`, whose entire job is surviving bad records long enough to
        describe them.
        """
        problems = self._problems(needs=[{"signal": "SIG"}], pin_order=["A", "B"])
        self.assertTrue(any("has no pin" in p for p in problems), problems)

    def test_a_power_entry_with_no_pin_is_caught_rather_than_crashing(self):
        # The SECOND instance of the same crash, found by writing the test for the first. Only
        # `needs` entries were checked for a pin, and `power` was then read with `["pin"]` in
        # four places — a rule written at the use site instead of in the contract.
        problems = self._problems(power=[{"rail": "logic", "direction": "in"}], pin_order=["P"])
        self.assertTrue(any("power[0] has no pin" in p for p in problems), problems)

    def test_an_unused_pin_entry_with_no_pin_is_caught_too(self):
        problems = self._problems(unused_pins=[{"note": "left floating"}])
        self.assertTrue(any("unused_pins[0] has no pin" in p for p in problems), problems)

    def test_a_well_formed_power_entry_is_not_reported(self):
        # The rule was widened, not made noisy.
        self.assertEqual(self._problems(
            power=[{"pin": "VCC", "rail": "logic", "direction": "in"}],
            pin_order=["P", "VCC"]), [])

    def test_a_capability_no_pin_can_offer_is_caught_where_it_is_written(self):
        """
        Two halves of the plugin disagreed, and the honest record was the one punished.

        A servo declaring `needs: ["pwm"]` — which is true, a servo is a pulse-width device —
        validated as a good record here, and then made `assign_pins` refuse the ENTIRE design,
        because that file kept its own vocabulary of `("wake", "adc")`. The only way to get a
        board out was to delete a true fact about the part.

        There is now one `CAPABILITIES`, owned by this file because a capability is a claim a
        PART makes, and `assign_pins` imports it.
        """
        problems = self._problems(
            needs=[{"signal": "S", "pin": "P", "direction": "in", "needs": ["telepathy"]}])
        self.assertTrue(any("telepathy" in p for p in problems), problems)

    def test_pwm_is_a_thing_a_part_may_ask_for(self):
        self.assertEqual(self._problems(
            needs=[{"signal": "S", "pin": "P", "direction": "in", "needs": ["pwm"]}]), [])

    def test_the_assigner_reads_the_same_vocabulary_this_file_validates(self):
        # The disagreement is gone structurally, not by keeping two lists in step.
        import assign_pins
        self.assertIs(assign_pins.CAPABILITIES, parts.CAPABILITIES)

    def test_a_placeholder_footprint_must_say_what_the_real_one_is(self):
        """
        The most expensive field to get wrong was the one field with no way to say "not yet".

        `facts` and `body_mm` carry `verified`; the footprint carried nothing. An XT30 drawn as a
        JST PH — wrong pitch, wrong hole, stated as a stand-in in a comment nothing reads — looked
        identical to a footprint generated from a vendor drawing, and `check_footprints` measured
        the JST's annular rings and reported a defect about a part that is not on the board.
        """
        problems = self._problems(footprint="jst_ph_2", footprint_placeholder=True)
        self.assertTrue(any("footprint_note" in p for p in problems), problems)

    def test_a_placeholder_WITH_a_note_is_a_valid_record(self):
        self.assertEqual(self._problems(
            footprint="jst_ph_2", footprint_placeholder=True,
            footprint_note="stands in for an XT30-PW nobody has drawn"), [])

    def test_a_real_footprint_needs_no_note(self):
        # Opt-in, so the five shipped records and every honest footprint are untouched.
        self.assertEqual(self._problems(footprint="pinrow5"), [])
        self.assertFalse(parts.has_placeholder_footprint(part(footprint="pinrow5")))

    def test_a_pin_name_a_selector_cannot_parse_is_caught_where_it_is_written(self):
        """
        Measured on a probe board: `IN+`, `OUT-` and `A.B` do not resolve as tscircuit selectors;
        `V_IN`, `GND2` and `3V3` do. An MP1584's pads are silkscreened IN+ IN- OUT+ OUT-, a record
        using those names produced four "could not find port" errors, and the rename that fixed
        it LOST the silkscreen — the exact failure `pad_aliases` prevents on the board side.
        """
        for bad in ("IN+", "OUT-", "A.B", "V IN"):
            with self.subTest(pin=bad):
                problems = self._problems(needs=[{"signal": "S", "pin": bad, "direction": "in"}])
                self.assertTrue(any("cannot be a selector" in p for p in problems), problems)

    def test_the_names_that_DO_resolve_are_not_refused(self):
        for good in ("VIN", "GND2", "3V3", "V_IN", "a"):
            with self.subTest(pin=good):
                self.assertEqual(self._problems(
                    needs=[{"signal": "S", "pin": good, "direction": "in"}]), [])

    def test_the_silkscreen_may_say_anything(self):
        # `printed` is what is on the part. It never reaches a selector, so nothing constrains it.
        self.assertEqual(self._problems(
            needs=[{"signal": "S", "pin": "VIN", "printed": "IN+", "direction": "in"}]), [])

    def test_printed_names_are_collected_only_where_they_differ(self):
        record = part(needs=[{"signal": "S", "pin": "VIN", "printed": "IN+", "direction": "in"}],
                      power=[{"pin": "GND", "printed": "GND", "rail": "ground", "direction": "in"}])
        self.assertEqual(parts.printed_names(record), {"VIN": "IN+"})

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


class APwmPinTest(unittest.TestCase):
    """A steering servo is the part that made `pwm` necessary."""

    def setUp(self):
        self.board = json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())

    def test_a_pwm_signal_is_placed_on_this_board(self):
        placed, _ = assign_pins.assign(self.board, [{"name": "STEER", "needs": ["pwm"]}])
        self.assertEqual(len(placed), 1)

    def test_every_pin_offers_pwm_when_the_board_does_not_say_otherwise(self):
        # Deliberate: an ESP32 routes LEDC through a GPIO matrix, so any output pin can do it.
        # The default is a statement about the chips this tool targets, not an omission.
        self.assertIn("pwm", assign_pins.capability_of(self.board, self.board["pins"]["D3"]))

    def test_a_board_that_LISTS_its_pwm_pins_is_believed_instead(self):
        # Most STM32 parts have a fixed timer map, and a servo must not land off it.
        limited = dict(self.board, pwm_gpio=[self.board["pins"]["D3"]])
        self.assertIn("pwm", assign_pins.capability_of(limited, limited["pins"]["D3"]))
        self.assertNotIn("pwm", assign_pins.capability_of(limited, limited["pins"]["D5"]))


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

    def test_a_signal_on_two_pads_is_caught(self):
        # Two pads carrying one signal is two pads shorted together.
        problems = self._problems(pin_order=["P", "P"])
        self.assertTrue(any("more than one pad" in p for p in problems), problems)

    def test_a_supply_on_two_pads_is_allowed(self):
        """
        Real modules bring VCC and GND out on both rows so either side can be fed — the DFR0954
        I2S amplifier does exactly that with all twelve of its pads. Refusing it would have made
        the contract reject a part the library needs to describe.
        """
        self.assertEqual(self._problems(
            pin_order=["VCC", "P", "GND", "VCC", "GND"],
            power=[{"pin": "VCC", "rail": "logic", "direction": "in"},
                   {"pin": "GND", "rail": "ground", "direction": "in"}]), [])

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


class TheFootprintAndThePinoutDescribeOnePartTest(unittest.TestCase):
    """
    Two fields, one physical object, and nothing compared them.

    `vl6180x-breakout` shipped saying `pinrow5` while its `pin_order` named seven pads — five of
    the seven carry a signal and two are unwired, so somebody counted the pins instead of the
    pads. The file's own prose note said seven all along, which is the recurring shape here: the
    truth written for a human, the contradiction written for the program.

    What it cost: the generator labelled a pad that did not exist, that port was given no
    position, and tscircuit's autorouter died reading its `x`. That failure is silent — the board
    comes back with zero traces rather than an error naming the part.
    """

    def _problems(self, **overrides):
        definition = part(**overrides)
        return parts.validate(definition, written(definition))

    def test_a_footprint_with_fewer_pads_than_the_pinout_is_caught(self):
        problems = self._problems(footprint="pinrow5", pin_order=[None, "P", None, None, None,
                                                                 None, None])
        self.assertTrue(any("7" in p and "5" in p for p in problems), problems)

    def test_a_footprint_with_more_pads_than_the_pinout_is_caught(self):
        # The other direction is just as wrong and reads as "finished" just as easily.
        problems = self._problems(footprint="pinrow8", pin_order=["P", None])
        self.assertTrue(any("8" in p for p in problems), problems)

    def test_they_agree_and_nothing_is_reported(self):
        self.assertEqual(self._problems(footprint="pinrow2", pin_order=["P", None]), [])

    def test_a_footprint_whose_pad_count_cannot_be_read_asserts_nothing(self):
        # Most footprints do not encode a count. Guessing one would report every honest part
        # file as a disagreement, and a checker that cries wolf gets switched off.
        self.assertEqual(self._problems(footprint="jlcpcb:C2040", pin_order=["P", None]), [])


class CountingPadsFromAFootprintNameTest(unittest.TestCase):
    def test_a_pin_row_says_how_many(self):
        self.assertEqual(parts.footprint_pad_count("pinrow7"), 7)

    def test_a_module_header_says_how_many(self):
        self.assertEqual(parts.footprint_pad_count("headermodule6"), 6)

    def test_a_package_named_after_its_body_is_not_a_pad_count(self):
        # The trap that makes this a whitelist. `sot23` is three pads, `0603` is a size in
        # hundredths of an inch, `sod123` is neither — and the obvious implementation, "take the
        # first integer", reads them as 23, 603 and 123.
        for footprint in ("sot23", "0603", "0805", "sod123", "sot23_3"):
            with self.subTest(footprint=footprint):
                self.assertIsNone(parts.footprint_pad_count(footprint))

    def test_a_footprint_from_a_supplier_or_a_file_says_nothing(self):
        self.assertIsNone(parts.footprint_pad_count("jlcpcb:C12345"))
        self.assertIsNone(parts.footprint_pad_count(None))


class TheShippedLibraryTest(unittest.TestCase):
    def test_every_part_shipped_satisfies_the_contract(self):
        for part_id in parts.available():
            with self.subTest(part=part_id):
                path = parts.definition_path(part_id)
                problems = parts.validate(json.loads(path.read_text()), path)
                self.assertEqual(problems, [], "%s: %s" % (part_id, problems))

    def test_every_shipped_part_does_something_for_the_board(self):
        """
        This asserted that every part produces SIGNALS, which was true only for as long as the
        library held nothing but modules with GPIO.

        A power inlet asks the host for no pin at all — that is the entire point of it, and it is
        the part that stops a generated board having a rail with one member. Requiring a signal
        would have made the contract reject the category the library most needed.

        The real rule underneath is that a part must do SOMETHING: ask for a pin, or carry a
        rail. One that does neither is inert, and would be emitted as a component nothing can
        ever connect to.
        """
        for part_id in parts.available():
            with self.subTest(part=part_id):
                definition = parts.load(part_id)
                self.assertTrue(
                    parts.signals_for([part_id]) or definition.get("power"),
                    "%s asks the host for no pin and carries no rail, so placing it on a board "
                    "does nothing at all" % part_id)


if __name__ == "__main__":
    unittest.main()
