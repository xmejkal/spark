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

import contextlib
import hashlib
import io
import json
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import assign_pins  # noqa: E402
import outcomes  # noqa: E402
import parts  # noqa: E402
import store  # noqa: E402


def in_store(home):
    """Point the store at a scratch folder for one block (P88): SPARK_HOME, read on every call."""
    return mock.patch.dict(os.environ, {"SPARK_HOME": str(home)})


def part(part_id="thing", **overrides):
    definition = dict({
        "schema": 1, "id": part_id, "name": "A Thing", "kind": "test",
        "needs": [{"signal": "SIG", "pin": "P", "direction": "in"}],
    }, **overrides)
    if definition.get("pin_order") and "pin_order_proof" not in definition:
        definition["pin_order_proof"] = {"verified": False, "source": "a test fixture"}  # P81
    return definition


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


class ABusIsSpentLastTest(unittest.TestCase):
    """
    Nothing marked SCK, MI and MO as a bus, so the assigner spent all three on two LEDs and a
    button — the cheapest pins left, by its lights — and a later SPI part had nowhere to go.
    Found by a cold rebuild of the bin and left open as backlog P3 until 2026-09-29.

    A bus signal still lands on its own named pin: that path runs first and ignores penalties.
    This is only about PLAIN signals preferring any other pin while one is free.
    """

    def setUp(self):
        self.board = json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())
        self.spi = set(self.board["pin_roles"]["spi"]["gpio"])
        self.i2c = set(self.board["pin_roles"]["i2c"]["gpio"])

    def test_the_board_records_which_pins_are_a_bus(self):
        # The data, since the assigner can only avoid what the board file names.
        self.assertEqual(self.spi, {self.board["pins"][k] for k in ("MOSI", "MISO", "SCK", "SS")})
        self.assertEqual(self.i2c, {self.board["pins"]["SDA"], self.board["pins"]["SCL"]})

    def test_six_plain_signals_fill_every_plain_pin_before_touching_the_spi_bus(self):
        """
        Six, because the FireBeetle has exactly six pins that are neither scarce nor a bus —
        D3, A5, D10, D11, D12, D6 — and the bus pins MOSI/MISO/SCK are ADC2 pins exactly like
        D6. Without the penalty the six-way tie is broken by GPIO number, which spends MOSI (15)
        and MISO (16) before D6 (18): that is the whole defect, measured. My first version placed
        three LEDs, never reached the tie, and passed with the penalty at zero.
        """
        signals = [{"name": "S%d" % i, "needs": []} for i in range(6)]
        placed, _ = assign_pins.assign(self.board, signals)
        landed = {a["gpio"] for a in placed}
        self.assertEqual(len(placed), 6)
        self.assertEqual(landed & self.spi, set(), "a plain signal took a bus pin: %s" % placed)
        self.assertEqual(landed & self.i2c, set())

    def test_a_plain_signal_takes_an_unlabelled_adc1_pin_before_the_i2c_pair(self):
        """
        On this board SDA and SCL are ADC1 pins (GPIO 1 and 2), equal in every ability to A0-A3
        and lower-numbered, so the tie-break alone would spend them first. Ten plain signals:
        nine fill every pin cheaper than an ADC1 pin (six plain, then the three SPI pins — a bus
        is cheaper than a scarce pin, by design), and the tenth must choose among the ADC1 pins.
        """
        ten = [{"name": "S%d" % i, "needs": []} for i in range(10)]
        placed, _ = assign_pins.assign(self.board, ten)
        landed = {a["gpio"] for a in placed}
        self.assertEqual(len(placed), 10)
        self.assertTrue(landed & set(self.board["adc_gpio"]),
                        "ten signals never reached an ADC1 pin; the pin count this test assumes is wrong")
        self.assertEqual(landed & self.i2c, set(), "the I2C pair was spent: %s" % placed)

    def test_the_bus_penalty_is_a_tie_breaker_smaller_than_one_ability(self):
        # 0 < penalty < CAPABILITY_COST: it orders pins that waste the same abilities and can
        # never make a plain signal waste an ability to avoid a bus. 15 broke this — two plain
        # signals sent onto ADC1 — and the ordering test below caught it; this pins the reason.
        for bus in ("spi", "i2c"):
            self.assertGreater(assign_pins.ROLE_PENALTY[bus], 0, bus)
            self.assertLess(assign_pins.ROLE_PENALTY[bus], assign_pins.CAPABILITY_COST, bus)

    def test_a_bus_signal_still_lands_on_its_own_pin(self):
        # The penalty must not push a real SPI signal off the pin it exists for.
        placed, _ = assign_pins.assign(self.board, [{"name": "SCK", "bus": "spi", "needs": []}])
        self.assertEqual(placed[0]["pin"], "SCK")

    def test_a_bus_pin_is_still_available_when_nothing_else_is(self):
        # Worse, not forbidden. A design with no SPI and many signals may use the bus; refusing
        # would fail boards that are perfectly buildable. Twenty signals: more than the pins
        # that are NOT a bus, so the bus must be drawn on, and fewer than the board has, so the
        # request is satisfiable. (My first version asked for 24 of a 23-pin board and blamed
        # the penalty for the refusal.)
        many = [{"name": "S%d" % i, "needs": []} for i in range(20)]
        placed, _ = assign_pins.assign(self.board, many)
        self.assertEqual(len(placed), 20)
        self.assertTrue({a["gpio"] for a in placed} & (self.spi | self.i2c),
                        "twenty plain signals were placed without touching a bus pin, which "
                        "means there are more non-bus pins than this test assumes")

    def test_for_a_plain_signal_a_bus_pin_costs_more_than_a_plain_pin_and_less_than_a_scarce_one(self):
        """
        The ordering, through `_cost` on real pins — not the penalty number, which is an
        implementation detail that the cost constant could move under.

        plain pin < bus pin < ADC1 pin. My first penalty was 15, which put the bus ABOVE the ADC1
        pins and sent three LEDs onto the board's scarcest inputs; a test pinning the number
        against other roles passed throughout. This one would not have.
        """
        pins = assign_pins.candidates(self.board)
        plain, bus, scarce = pins["D3"], pins["SCK"], pins["A1"]
        cost = lambda pin: assign_pins._cost(pin, frozenset())
        self.assertLess(cost(plain), cost(bus))
        self.assertLess(cost(bus), cost(scarce))

    def test_the_bin_still_spends_no_adc1_pin_on_a_plain_signal(self):
        """
        The regression the wrong penalty caused, stated beside the ordering that prevents it:
        the bin's LEDs and buttons must not be pushed onto ADC1 by the bus being expensive.

        A plain signal has no `bus` and no `needs`. SDA and SCL are excluded on purpose: on this
        board the I2C pins ARE GPIO 1 and 2, which are ADC1 — a bus signal goes where its bus is,
        and the first version of this test counted them and failed for the right placement.
        """
        signals = parts.signals_for(["l9110s-module", "vl6180x-breakout"]) + [
            {"name": "LED_%d" % i, "needs": []} for i in range(3)]
        placed, _ = assign_pins.assign(self.board, signals)
        adc1 = set(self.board["adc_gpio"])
        plain = {s["name"] for s in signals if not s.get("bus") and not s.get("needs")}
        self.assertEqual({"MOTOR_IA", "MOTOR_IB", "LED_0", "LED_1", "LED_2"}, plain)
        on_adc1 = [a["signal"] for a in placed if a["gpio"] in adc1 and a["signal"] in plain]
        self.assertEqual(on_adc1, [], "plain signals landed on ADC1 pins: %s" % on_adc1)


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



class AMissingPinIsReportedOnceTest(unittest.TestCase):
    """
    `3b5f38f` moved the missing-pin rule to the contract and left the older use-site copy in
    the `power` walk, so one malformation produced two problems — the patch-not-audit pattern
    inside the commit that named it. Found by the sprint audit (A3), reproduced, copy removed.
    """

    def test_a_power_entry_without_a_pin_is_one_problem_not_two(self):
        path = ROOT / "parts" / "l9110s-module.json"
        record = json.loads(path.read_text())
        record["power"] = [{"rail": "v33", "direction": "in"}]
        problems = [p for p in parts.validate(record, path) if "no pin" in p]
        self.assertEqual(len(problems), 1, problems)
        self.assertIn("power[0]", problems[0])


class ABusIsCheckedWhereTheRecordIsWrittenTest(unittest.TestCase):
    """The contract refuses an unknown bus or a line the bus lacks, so the chain never has to."""

    def _problems(self, **need):
        path = ROOT / "parts" / "vl6180x-breakout.json"
        record = json.loads(path.read_text())
        record["needs"] = [dict(record["needs"][0], **need)]
        return [p for p in parts.validate(record, path) if "bus" in p]

    def test_an_unknown_bus_is_refused_by_name(self):
        problems = self._problems(signal="X", bus="can")
        self.assertTrue(problems and "not a bus this knows" in problems[0], problems)

    def test_a_line_the_bus_does_not_have_is_refused_naming_the_lines(self):
        problems = self._problems(signal="XYZ", bus="spi")
        self.assertTrue(problems and "not one of its lines" in problems[0] and "SCK" in problems[0], problems)

    def test_a_bus_prefixed_signal_names_its_line(self):
        self.assertEqual(parts.bus_line_of("i2s", "I2S_BCLK"), "BCLK")
        self.assertEqual(parts.bus_line_of("spi", "CS"), "SS")
        self.assertIsNone(parts.bus_line_of("spi", "XYZ"))
        self.assertEqual(self._problems(signal="I2S_LRC", bus="i2s"), [])

    def test_every_shipped_record_is_still_within_the_vocabulary(self):
        for path in sorted((ROOT / "parts").glob("*.json")):
            record = json.loads(path.read_text())
            self.assertEqual([p for p in parts.validate(record, path) if "bus" in p], [], path.name)


class AnI2cBusIsPulledUpBySomebodyTest(unittest.TestCase):
    """
    P55. I2C only ever pulls down, and the FireBeetle V1.2+ has no pull-ups of its own, so every
    record on the bus must say where its pull-ups come from: the module (a fact) or the host
    (`host_parts`). The fact sat in four catalog records that no test read, and flipping it, or
    setting a 1 MOhm pull-up, passed a green suite — while the RTC the PO owns said the same thing
    under a second name the catalog does not use.
    """

    I2C = [{"signal": "SDA", "pin": "SDA", "bus": "i2c"}, {"signal": "SCL", "pin": "SCL", "bus": "i2c"}]

    def _problems(self, facts=None, host_parts=None):
        definition = part(needs=self.I2C, facts=facts or {})
        if host_parts is not None:
            definition["host_parts"] = host_parts
        return [p for p in parts.validate(definition, written(definition)) if "pull" in p]

    @staticmethod
    def fact(value):
        return {"value": value, "verified": True, "source": "test"}

    def test_a_module_that_carries_its_pull_ups_says_so_and_passes(self):
        self.assertEqual(self._problems({"module_has_i2c_pullups": self.fact(True)}), [])

    def test_a_host_that_adds_them_passes(self):
        pullups = [{"kind": "pullup", "pin": line, "ohms": 2200, "why": "the bus"} for line in ("SDA", "SCL")]
        self.assertEqual(self._problems(host_parts=pullups), [])

    def test_a_host_pull_up_on_one_line_does_not_cover_the_other(self):
        half = [{"kind": "pullup", "pin": "SDA", "ohms": 2200, "why": "the data line"}]
        self.assertEqual(len(self._problems(host_parts=half)), 1, "SCL still floats")

    def test_a_bus_nobody_pulls_up_is_refused(self):
        refused = self._problems({"module_has_i2c_pullups": self.fact(False)})
        self.assertEqual(len(refused), 1, refused)
        self.assertIn("module_has_i2c_pullups", refused[0])

    def test_silence_is_refused_too(self):
        self.assertEqual(len(self._problems()), 1, "saying nothing is how a bus floats")

    def test_a_module_pull_up_that_cannot_hold_a_bus_is_refused(self):
        refused = self._problems({"module_has_i2c_pullups": self.fact(True),
                                  "i2c_pullup_ohms": self.fact(1_000_000)})
        self.assertTrue(any("i2c_pullup_ohms" in p for p in refused), refused)

    def test_every_shipped_record_holds_the_contract(self):
        # The real files — not a temporary directory standing in for them. The catalog was walked
        # here too until P83 moved it into the person's store, where `--promote` demands the
        # contract of a record before anything builds with it.
        paths = sorted((ROOT / "parts").glob("*.json"))
        self.assertGreaterEqual(len(paths), 7)
        for path in paths:
            with self.subTest(record=path.name):
                self.assertEqual(parts.validate(json.loads(path.read_text()), path), [])


class ResearchStartsFromWhatExistsTest(unittest.TestCase):
    """
    Backlog R11, pulled by the PO for the third cold test: research parts vendor by vendor and
    keep what was found. The deterministic half lives here — what exists, a skeleton to fill, the
    vendor order, and sources that must answer. The reading is the agent's.
    """

    def test_need_matches_id_name_kind_and_alias(self):
        self.assertIn("l9110s-module", [p["id"] for p in parts.need(["motor"])[0]])
        self.assertIn("vl6180x-breakout", [p["id"] for p in parts.need(["rangefinder"])[0]])
        self.assertEqual(parts.need(["unobtainium"]), ([], []))
        self.assertEqual([p["id"] for p in parts.need(["motor", "driver"])[0]], ["l9110s-module"])
        self.assertIn("l9110s-module", [p["id"] for p in parts.need(["motor-driver"])[0]],
                      "the kind alone matches — the name says 'motor driver' without the hyphen")
        self.assertIn("l9110s-module", [p["id"] for p in parts.need(["hg7881"])[0]],
                      "an alias alone matches — HG7881 appears nowhere but also_known_as")

    def test_a_draft_still_being_filled_in_is_named_and_does_not_stop_the_search(self):
        # I3: `--need` died on a researcher's skeleton while five researchers were running.
        import tempfile
        root = Path(tempfile.mkdtemp())
        parts.main(["--skeleton", "dfr0457-mosfet-driver", "--kind", "mosfet-driver", "--project", str(root)])
        found, drafts = parts.need(["mosfet"], root)
        self.assertEqual(found, [])
        self.assertEqual(drafts, ["dfr0457-mosfet-driver"])
        self.assertIn("l9110s-module", [p["id"] for p in parts.need(["motor"], root)[0]],
                      "the library is still searched past the draft")

    def test_no_match_names_the_research_command_and_the_vendor_order(self):
        import contextlib
        import io
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            parts.main(["--need", "unobtainium"])
        self.assertIn("/spark:research", out.getvalue())
        self.assertIn("dfrobot, seeed", out.getvalue())

    def test_the_vendor_order_is_the_briefs_when_it_says_and_the_default_when_not(self):
        import tempfile
        root = Path(tempfile.mkdtemp())
        self.assertEqual(parts.vendor_order(root), parts.DEFAULT_VENDOR_ORDER)
        (root / ".spark").mkdir()
        (root / ".spark" / "project.json").write_text(json.dumps({"prefer": ["Seeed", "adafruit"]}))
        self.assertEqual(parts.vendor_order(root), ("seeed", "adafruit"))
        (root / ".spark" / "project.json").write_text(json.dumps({"prefer": None}))
        self.assertEqual(parts.vendor_order(root), parts.DEFAULT_VENDOR_ORDER)

    def test_sellers_come_from_the_brief_or_are_none_named(self):
        # Local first is the person's rule, so it lives in their brief; the tool never picks a shop.
        import tempfile
        root = Path(tempfile.mkdtemp())
        self.assertEqual(parts.sellers(root), ())
        (root / ".spark").mkdir()
        (root / ".spark" / "project.json").write_text(json.dumps({"sellers": ["LaskaKit", "gme"]}))
        self.assertEqual(parts.sellers(root), ("laskakit", "gme"))
        self.assertIn("sourcing", parts.skeleton("x", "connector"))

    def test_a_skeleton_has_every_field_and_no_guess_and_the_contract_refuses_it_until_filled(self):
        import tempfile
        root = Path(tempfile.mkdtemp())
        code = parts.main(["--skeleton", "sg90-servo", "--kind", "actuator", "--vendor", "dfrobot",
                           "--project", str(root)])
        self.assertEqual(code, parts.EXIT_OK)
        written = json.loads((root / "parts" / "sg90-servo.json").read_text())
        self.assertEqual(written["id"], "sg90-servo")
        self.assertIsNone(written["name"])
        self.assertIsNone(written["footprint"])
        self.assertFalse(written["body_mm"]["verified"])
        problems = parts.validate(written, root / "parts" / "sg90-servo.json")
        self.assertTrue(problems, "a skeleton full of nulls must not pass the contract")
        self.assertEqual(parts.main(["--skeleton", "sg90-servo", "--kind", "actuator", "--project", str(root)]),
                         parts.EXIT_INVALID, "an existing record is never overwritten")

    def test_sources_are_fetched_and_a_dead_one_is_named(self):
        record = {"sources": ["https://wiki.example/a", "not a url"],
                  "facts": {"x": {"value": 1, "verified": True, "source": "https://wiki.example/b"},
                            "y": {"value": 2, "verified": False, "source": "the datasheet, page 3"}}}
        self.assertEqual(parts.cited_urls(record), ["https://wiki.example/a", "https://wiki.example/b"])
        answers = parts.sources_resolve(record, fetch=lambda url: url.endswith("/a"))
        self.assertEqual(answers, [("https://wiki.example/a", True), ("https://wiki.example/b", False)])


class EverythingFoundIsKeptTest(unittest.TestCase):
    """The catalog: what research has read, chosen or not, with its datasheets kept beside it."""

    def _catalog_record(self, catalog, part_id, **extra):
        record = dict(schema=1, id=part_id, name="A candidate", kind="sensor", sources=[], facts={})
        record.update(extra)
        (catalog / (part_id + ".json")).write_text(json.dumps(record))
        return record

    def test_the_catalog_is_searched_like_the_library_and_a_broken_record_is_named(self):
        import tempfile
        from unittest import mock
        home = self._home(); catalog = home / "catalog"
        self._catalog_record(catalog, "sen0193-soil-moisture", name="Gravity capacitive soil moisture sensor")
        self._catalog_record(catalog, "dfr0831-buck-5v", name="Buck converter", kind="power")
        (catalog / "broken.json").write_text("{not json")
        (catalog / "nameless.json").write_text(json.dumps({"schema": 1, "id": "nameless", "kind": "sensor"}))
        with in_store(home):
            known = parts.catalog_matches(["Soil", "moisture"])
            records, broken = parts.catalog_records()
        self.assertEqual([p["id"] for p in known], ["sen0193-soil-moisture"])
        self.assertEqual((sorted(records), broken), (["dfr0831-buck-5v", "sen0193-soil-moisture"], ["broken.json", "nameless.json"]),
                         "a record that parses but does not say what it is, is broken too")

    @staticmethod
    def _home():
        """A scratch store for one test (P88): its catalog folder made, its sources folder not yet."""
        home = Path(tempfile.mkdtemp())
        (home / "catalog").mkdir()
        return home

    def test_fetch_keeps_datasheets_and_images_in_the_store_under_their_checksum(self):
        """P62a: a published plugin cannot carry vendor files, so nothing lands beside the record."""
        import datetime
        import hashlib
        import tempfile
        from unittest import mock
        home = self._home(); catalog, store = home / "catalog", home / "sources"
        self._catalog_record(catalog, "x-part", sources=["https://v.example/x.pdf?v=2", "https://v.example/page.html"],
                             facts={"w": {"value": 1, "verified": True, "source": "https://v.example/photo.jpg"}})
        fetched = []
        def fetch(url):
            fetched.append(url)
            return b"payload" if ".pdf" in url or url.endswith(".jpg") else None
        with in_store(home):
            kept = parts.fetch_documents("x-part", fetch=fetch)
        self.assertEqual(sorted(fetched), ["https://v.example/photo.jpg", "https://v.example/x.pdf?v=2"],
                         "only datasheets and images are fetched; a page is not")
        digest = hashlib.sha256(b"payload").hexdigest()
        self.assertEqual(kept["x"], {"url": "https://v.example/x.pdf?v=2", "sha256": digest, "file": "x.pdf",
                                     "retrieved": datetime.date.today().isoformat(), "title": None, "version": None})
        self.assertEqual(kept["photo"]["file"], "photo.jpg")
        self.assertEqual((store / digest / "x.pdf").read_bytes(), b"payload")
        self.assertFalse((catalog / "x-part").exists(), "nothing is kept beside the record any more")
        written = json.loads((catalog / "x-part.json").read_text())
        self.assertEqual((written["documents"], "attachments" in written), (kept, False))

    def test_a_document_already_kept_is_not_fetched_again(self):
        import tempfile
        from unittest import mock
        home = self._home(); catalog, store = home / "catalog", home / "sources"
        self._catalog_record(catalog, "x-part", sources=["https://v.example/x.pdf"])
        with in_store(home):
            parts.fetch_documents("x-part", fetch=lambda url: b"pdf")
            again = []
            parts.fetch_documents("x-part", fetch=lambda url: again.append(url))
        self.assertEqual(again, [])

    def test_a_catalog_draft_answers_sources_show_and_unverified_like_any_record(self):
        import tempfile
        from unittest import mock
        home = self._home(); catalog = home / "catalog"
        self._catalog_record(catalog, "x-part", sources=["https://v.example/x.pdf"],
                             facts={"pitch_mm": {"value": 2.0, "verified": False, "why_it_matters": "the socket", "source": None}})
        answered = lambda record: [(url, True) for url in parts.cited_urls(record)]  # noqa: E731 — no network
        with in_store(home), mock.patch.object(parts, "sources_resolve", answered):
            self.assertEqual(parts.any_record("x-part")["id"], "x-part")
            self.assertEqual([q["fact"] for q in parts.unverified(["x-part"])], ["pitch_mm"])
            with contextlib.redirect_stdout(io.StringIO()) as out:
                code = parts.main(["--sources", "x-part"])
        self.assertEqual((code, "ok" in out.getvalue()), (0, True), out.getvalue())

    def test_fetch_keeps_the_text_as_written_and_decodes_the_saved_name(self):
        import tempfile
        from unittest import mock
        home = self._home(); catalog, store = home / "catalog", home / "sources"
        self._catalog_record(catalog, "x-part", sources=["https://v.example/DFR%20(1).pdf"],
                             **{"//": "98 Kč — 帝江"})
        with in_store(home):
            kept = parts.fetch_documents("x-part", fetch=lambda url: b"pdf")
        (key, entry), = kept.items()
        self.assertEqual(entry["file"], "DFR (1).pdf")
        self.assertTrue((store / entry["sha256"] / "DFR (1).pdf").is_file())
        self.assertIn("98 Kč — 帝江", (catalog / "x-part.json").read_text(), "a rewrite must not turn text into escapes")

    def test_two_sources_with_one_basename_are_both_kept(self):
        import tempfile
        from unittest import mock
        home = self._home(); catalog, store = home / "catalog", home / "sources"
        self._catalog_record(catalog, "x-part", sources=["https://a.example/DS3231.pdf", "https://b.example/DS3231.pdf"])
        with in_store(home):
            kept = parts.fetch_documents("x-part", fetch=lambda url: url.encode())
        self.assertEqual(sorted(entry["url"] for entry in kept.values()),
                         ["https://a.example/DS3231.pdf", "https://b.example/DS3231.pdf"])
        self.assertEqual(len({entry["sha256"] for entry in kept.values()}), 2, "two documents, two checksums")
        for entry in kept.values():
            self.assertEqual((store / entry["sha256"] / "DS3231.pdf").read_bytes(), entry["url"].encode())

    def test_promote_moves_a_record_with_its_documents_and_its_folder_and_never_overwrites(self):
        import tempfile
        from unittest import mock
        home = self._home(); catalog = home / "catalog"; project, library = (Path(tempfile.mkdtemp()) for _ in range(2))
        (project / ".spark").mkdir()
        documents = {"x": {"url": "https://v.example/x.pdf", "sha256": "a" * 64, "file": "x.pdf",
                           "retrieved": "2026-10-02", "title": None, "version": None}}
        self._catalog_record(catalog, "x-part", documents=documents)
        (catalog / "x-part" / "chip").mkdir(parents=True)
        (catalog / "x-part" / "chip" / "x.chip.json").write_text("{}")
        with in_store(home):
            self.assertEqual(parts.promote("x-part", project), project / "parts" / "x-part.json")
            self.assertEqual(json.loads((project / "parts" / "x-part.json").read_text())["documents"], documents)
            self.assertTrue((project / "parts" / "x-part" / "chip" / "x.chip.json").is_file(), "a chip travels with it")
            with self.assertRaises(parts.PartError):
                parts.promote("x-part", project, to=project / "parts")
            self.assertEqual(parts.promote("x-part", project, to=library), library / "x-part.json")
            self.assertTrue((library / "x-part" / "chip" / "x.chip.json").is_file())

    def test_cited_urls_reads_a_dict_of_sources_and_a_url_inside_prose(self):
        # Both P62 lenses: four library records keep `sources` as a dict, and `--sources` saw none.
        record = {"sources": {"pins": "the vendor header, https://a.example/pins.h, read 09-24",
                              "wiki": "https://b.example/wiki"},
                  "facts": {"w": {"source": "Table 3 of https://c.example/ds.pdf (rev 7)"},
                            "v": {"source": "the drawing (see https://d.example/dim.pdf)."},
                            "u": {"source": "https://e.example/DFR%20(1).pdf"}}}
        self.assertEqual(sorted(parts.cited_urls(record)),
                         ["https://a.example/pins.h", "https://b.example/wiki", "https://c.example/ds.pdf",
                          "https://d.example/dim.pdf", "https://e.example/DFR%20(1).pdf"],
                         "a parenthesis the URL opened is its own; one it never opened is the prose's")

    def test_a_record_still_carrying_attachments_is_refused(self):
        definition = part(attachments={"https://v.example/x.pdf": "thing/x.pdf"})
        self.assertTrue(any("attachments" in p for p in parts.validate(definition, written(definition))))

    # --- P62b: a source is found before it is fetched again ---

    def test_keep_puts_a_local_file_in_the_store_and_says_what_to_record(self):
        import datetime
        import hashlib
        import tempfile
        from unittest import mock
        home = self._home(); store = home / "sources"
        local = Path(tempfile.mkdtemp()) / "ds_v1.1.pdf"
        local.write_bytes(b"the v1.1 pdf")
        with in_store(home):
            entry = parts.keep_local(local, url="https://v.example/ds.pdf")
        digest = hashlib.sha256(b"the v1.1 pdf").hexdigest()
        self.assertEqual(entry, {"url": "https://v.example/ds.pdf", "sha256": digest, "file": "ds_v1.1.pdf",
                                 "retrieved": datetime.date.today().isoformat(), "title": None, "version": None})
        self.assertEqual((store / digest / "ds_v1.1.pdf").read_bytes(), b"the v1.1 pdf")

    def test_a_document_with_no_url_is_allowed_a_photo_of_your_own_module_has_none(self):
        definition = part(documents={"photo": {"url": None, "sha256": "a" * 64, "file": "top.jpg",
                                               "retrieved": "2026-10-03", "title": None, "version": None}})
        self.assertEqual([p for p in parts.validate(definition, written(definition)) if "documents" in p], [])

    def _kept_world(self, stored=True):
        """A catalog record and a project board that both point at one datasheet, the board citing a page."""
        import tempfile
        home = self._home(); catalog, project, store = home / "catalog", Path(tempfile.mkdtemp()), home / "sources"
        (project / ".spark").mkdir()
        digest = "b" * 64
        document = {"url": "https://v.example/wroom.pdf", "sha256": digest, "file": "wroom_v1.1.pdf",
                    "retrieved": "2026-09-24", "title": "ESP32-S3-WROOM-1 Datasheet", "version": "v1.1"}
        self._catalog_record(catalog, "x-rtc", documents={"wroom": document},
                             facts={"idle_ua": {"value": 8, "verified": True, "source": "https://v.example/wroom.pdf"}})
        # A record with a document of its own and nothing resting on the WROOM: it must not be named.
        self._catalog_record(catalog, "x-jack", body_mm={"value": [9, 14], "verified": True, "source": "drawing"},
                             documents={"drawing": dict(document, url="https://v.example/jack.pdf",
                                                        sha256="c" * 64, file="jack.pdf", title="Jack")},
                             facts={"rating_a": {"value": 2, "verified": True, "source": "the drawing",
                                                 "cites": {"document": "drawing", "at": "page 2"}}})
        (project / "boards").mkdir()
        (project / "boards" / "x-board.json").write_text(json.dumps({
            "id": "x-board", "documents": {"wroom": document},
            "power": {"deep_sleep_ua": {"value": None, "verified": False, "source": "Table 12",
                                        "cites": {"document": "wroom", "at": "Table 12, page 15"}}}}))
        if stored:
            (store / digest).mkdir(parents=True)
            (store / digest / "wroom_v1.1.pdf").write_bytes(b"pdf")
        return home, project, store

    def _kept(self, words, stored=True):
        from unittest import mock
        home, project, store = self._kept_world(stored)
        def no_network(url):
            raise AssertionError("--kept must never reach the network, asked for %s" % url)
        import boards
        with in_store(home), \
                mock.patch.object(boards, "LIBRARY", home / "no-library"), \
                mock.patch.object(parts, "_download", no_network), \
                contextlib.redirect_stdout(io.StringIO()) as out:
            code = parts.main(["--kept"] + words + ["--project", str(project)])
        return code, out.getvalue(), store

    def test_kept_finds_a_document_by_every_word_and_says_where_it_is(self):
        code, said, store = self._kept(["wroom", "v1.1"])
        self.assertEqual(code, 0, said)
        self.assertIn(str(store / ("b" * 64) / "wroom_v1.1.pdf"), said)
        self.assertIn("present", said)

    def test_kept_names_every_fact_that_rests_on_it_with_its_page_and_nothing_else(self):
        _, said, _ = self._kept(["wroom"])
        cited = sorted(set(line.strip() for line in said.splitlines() if "cited by" in line))
        self.assertEqual(cited, ["cited by x-board power.deep_sleep_ua — Table 12, page 15",
                                 "cited by x-rtc facts.idle_ua — cites its URL"])

    def test_kept_says_missing_when_the_store_does_not_hold_it(self):
        _, said, _ = self._kept(["wroom"], stored=False)
        self.assertIn("MISSING", said)

    def test_kept_finds_a_stored_file_no_record_here_cites(self):
        """P80: the L-7113ID kept by the quickstart was invisible to every other project, so the next
        one would have fetched it again."""
        from unittest import mock
        home, project, store = self._kept_world()
        (store / ("d" * 64)).mkdir(parents=True)
        (store / ("d" * 64) / "L-7113ID(Ver.29A).pdf").write_bytes(b"pdf")
        with in_store(home), \
                contextlib.redirect_stdout(io.StringIO()) as out:
            code = parts.main(["--kept", "l-7113id"])
        self.assertEqual(code, 0, out.getvalue())
        self.assertIn(str(store / ("d" * 64) / "L-7113ID(Ver.29A).pdf"), out.getvalue())
        self.assertIn("no record here cites it", out.getvalue())

    def test_kept_needs_every_word(self):
        code, said, _ = self._kept(["wroom", "nothing-like-this"])
        self.assertNotIn("present", said)
        self.assertIn("nothing kept matches", said)
        self.assertEqual(code, 0, "finding nothing is an answer, said in words (§6.4.1: a gap is an answer)")

    def test_a_fact_citing_a_document_the_record_does_not_hold_is_refused(self):
        definition = part(facts={"idle_ua": {"value": 8, "verified": True, "source": "the datasheet",
                                             "cites": {"document": "ds", "at": "page 3"}}})
        self.assertTrue(any("facts.idle_ua" in p and "'ds'" in p for p in parts.validate(definition, written(definition))))

    @staticmethod
    def _photo_with_location():
        """A minimal JPEG whose EXIF carries a GPS block: latitude N 50° 5' 12.34" — as a phone writes it."""
        import struct
        latitude = struct.pack("<6I", 50, 1, 5, 1, 1234, 100)
        tiff = (b"II*\x00" + struct.pack("<I", 8)
                + struct.pack("<H", 1) + struct.pack("<HHII", 0x8825, 4, 1, 26) + struct.pack("<I", 0)
                + struct.pack("<H", 2) + struct.pack("<HHI4s", 1, 2, 2, b"N\x00\x00\x00")
                + struct.pack("<HHII", 2, 5, 3, 56) + struct.pack("<I", 0) + latitude)
        exif = b"Exif\x00\x00" + tiff
        return b"\xff\xd8\xff\xe1" + struct.pack(">H", len(exif) + 2) + exif + b"\xff\xd9", latitude

    def _keep_photo(self, payload, name="module.jpg"):
        import tempfile
        from unittest import mock
        home = self._home(); store, local = home / "sources", Path(tempfile.mkdtemp()) / name
        local.write_bytes(payload)
        with in_store(home), contextlib.redirect_stdout(io.StringIO()) as out, \
                contextlib.redirect_stderr(io.StringIO()) as err:
            parts.main(["--keep", str(local)])
        json.loads(out.getvalue())  # what is pasted into a record stays JSON
        kept = next(store.rglob(name)).read_bytes()
        return kept, err.getvalue()

    def test_a_kept_photo_does_not_say_where_it_was_taken(self):
        """P75: all five of irrigation's phone photos carried latitude, longitude and altitude."""
        import struct
        photo, latitude = self._photo_with_location()
        kept, said = self._keep_photo(photo)
        self.assertNotIn(latitude, kept, "the coordinates are still in the file")
        self.assertNotIn(b"N\x00\x00\x00", kept[kept.index(b"Exif"):], "the hemisphere is still in the file")
        gps_entries = struct.unpack_from("<H", kept, kept.index(b"II*\x00") + 26)[0]
        self.assertEqual(gps_entries, 0, "the GPS block still lists entries")
        self.assertEqual(len(kept), len(photo), "nothing else in the file may move")
        self.assertIn("location", said.lower())

    def test_a_photo_with_no_location_and_any_other_file_are_kept_unchanged(self):
        photo, _ = self._photo_with_location()
        plain = photo.replace(b"\x25\x88", b"\x0f\x01", 1)  # the GPS pointer becomes the camera maker's tag
        for payload, name in ((plain, "plain.jpg"), (b"%PDF-1.4 whatever", "ds.pdf")):
            kept, said = self._keep_photo(payload, name)
            self.assertEqual(kept, payload, name)
            self.assertNotIn("location", said.lower(), name)

    def test_a_document_whose_checksum_is_not_one_is_refused(self):
        definition = part(documents={"x": {"url": "https://v.example/x.pdf", "sha256": "abc", "file": "x.pdf",
                                           "retrieved": "2026-10-02", "title": None, "version": None}})
        self.assertTrue(any("sha256" in p for p in parts.validate(definition, written(definition))))


class ASimulationIsDeclaredTest(unittest.TestCase):
    """P31: a record says how it is simulated, and the contract refuses a half-said one."""

    def _record(self, **extra):
        record = {"schema": 1, "id": "x-part", "name": "X", "kind": "sensor",
                  "needs": [{"signal": "OUT", "pin": "OUT", "needs": []}],
                  "power": [{"pin": "VCC", "rail": "logic", "direction": "in"}, {"pin": "GND", "rail": "ground", "direction": "in"}],
                  "unused_pins": [{"pin": "NC", "note": "no connection"}]}
        record.update(extra)
        return record

    def _problems(self, simulation, root=None):
        import tempfile
        root = root or Path(tempfile.mkdtemp())
        path = root / "x-part.json"
        return parts.simulation_problems(self._record(simulation=simulation), path), root

    def test_a_skip_needs_its_reason_and_nothing_else(self):
        self.assertEqual(self._problems({"skip": "wiring, not a part"})[0], [])
        self.assertTrue(self._problems({"skip": ""})[0])
        self.assertTrue(self._problems({"skip": "x", "wokwi": {}})[0])

    def test_a_stand_in_names_its_part_its_pins_and_what_differs(self):
        good = {"wokwi": {"part": "wokwi-led", "pins": {"OUT": "A", "GND": "C", "VCC": None}, "stand_in": "an LED shows the level"}}
        self.assertEqual(self._problems(good)[0], [])
        no_note = {"wokwi": {"part": "wokwi-led", "pins": {"OUT": "A", "GND": "C", "VCC": None}}}
        self.assertTrue(any("stand_in" in p for p in self._problems(no_note)[0]))
        both = {"wokwi": {"part": "wokwi-led", "chip": "x", "pins": {"OUT": "A", "GND": "C", "VCC": None}, "stand_in": "s"}}
        self.assertTrue(any("exactly one" in p for p in self._problems(both)[0]))

    def test_every_wired_pad_is_placed_and_no_unknown_pad_is_named(self):
        missing = {"wokwi": {"part": "wokwi-led", "pins": {"OUT": "A"}, "stand_in": "s"}}
        said = " ".join(self._problems(missing)[0])
        self.assertIn("'GND'", said); self.assertIn("'VCC'", said)
        unknown = {"wokwi": {"part": "wokwi-led", "pins": {"OUT": "A", "GND": "C", "VCC": None, "BOGUS": "B"}, "stand_in": "s"}}
        self.assertTrue(any("never mentions" in p for p in self._problems(unknown)[0]))
        unused_may_be_absent = {"wokwi": {"part": "wokwi-led", "pins": {"OUT": "A", "GND": "C", "VCC": None}, "stand_in": "s"}}
        self.assertEqual(self._problems(unused_may_be_absent)[0], [], "NC is unused and need not be placed")

    def test_a_control_id_is_what_a_scenario_can_name(self):
        # wokwi-cli's own check: /controls/0/id must match ^[a-zA-Z][a-zA-Z0-9]*$ — `flow_lpm` was refused.
        import tempfile
        root = Path(tempfile.mkdtemp())
        folder = root / "x-part" / "chip"; folder.mkdir(parents=True)
        (folder / "probe.chip.c").write_text("// c")
        (folder / "probe.chip.json").write_text(json.dumps({"pins": ["SIG", "GND", "VCC"], "controls": [{"id": "flow_lpm"}, {"id": "flowLpm"}]}))
        chip = {"wokwi": {"chip": "probe", "pins": {"OUT": "SIG", "GND": "GND", "VCC": "VCC"}}}
        problems = self._problems(chip, root)[0]
        self.assertEqual(len(problems), 1, problems)
        self.assertIn("'flow_lpm'", problems[0])

    def test_a_chip_pin_map_names_only_pins_the_chip_has(self):
        # Audit D18: `AIA: "NOPE"` validated clean and was refused only by the converter.
        import tempfile
        root = Path(tempfile.mkdtemp())
        folder = root / "x-part" / "chip"; folder.mkdir(parents=True)
        (folder / "probe.chip.c").write_text("// c")
        (folder / "probe.chip.json").write_text(json.dumps({"pins": ["SIG", "GND", "VCC"]}))
        good = {"wokwi": {"chip": "probe", "pins": {"OUT": "SIG", "GND": "GND", "VCC": None}}}
        self.assertEqual(self._problems(good, root)[0], [])
        bad = {"wokwi": {"chip": "probe", "pins": {"OUT": "NOPE", "GND": "GND", "VCC": "VCC"}}}
        self.assertTrue(any("does not have" in p and "'NOPE'" in p for p in self._problems(bad, root)[0]))

    def test_a_chip_must_exist_beside_the_record(self):
        import tempfile
        root = Path(tempfile.mkdtemp())
        chip = {"wokwi": {"chip": "probe", "pins": {"OUT": "SIG", "GND": "GND", "VCC": "VCC"}}}
        self.assertTrue(any("needs" in p and "probe.chip.c" in p for p in self._problems(chip, root)[0]))
        folder = root / "x-part" / "chip"; folder.mkdir(parents=True)
        (folder / "probe.chip.c").write_text("// c"); (folder / "probe.chip.json").write_text("{}")
        self.assertEqual(self._problems(chip, root)[0], [])

    def test_the_validator_refuses_a_record_whose_simulation_is_half_said(self):
        import tempfile
        root = Path(tempfile.mkdtemp())
        record = self._record(simulation={"skip": ""}, pin_order=["OUT", "VCC", "GND", "NC"], footprint="pinrow4",
                              body_mm={"width": 10, "height": 10, "verified": True, "source": "x"})
        self.assertTrue(any("simulation.skip" in p for p in parts.validate(record, root / "x-part.json")),
                        "validate must carry the simulation problems, or --validate passes a record the converter cannot use")

    def test_every_shipped_record_says_how_it_is_simulated(self):
        for part_id in parts.available():
            record = parts.load(part_id)
            self.assertIn("simulation", record, "%s: the converter has nothing to read" % part_id)


class WhatAPartDemandsOfItsHostTest(unittest.TestCase):
    """P6: `host_parts` is a component list the generator can act on, so it is checked like one."""

    def _problems(self, host_parts):
        part = {"schema": 1, "id": "x", "name": "X", "kind": "sensor",
                "needs": [{"signal": "OUT", "pin": "OUT", "needs": []}],
                "power": [{"pin": "VCC", "rail": "logic", "direction": "in"}]}
        part["host_parts"] = host_parts
        return parts.host_part_problems(part)

    def test_a_well_said_pulldown_passes_and_each_omission_is_named(self):
        self.assertEqual(self._problems([{"kind": "pulldown", "pin": "OUT", "ohms": 10000, "why": "floats at reset"}]), [])
        self.assertTrue(any("not one the generator can place" in p for p in self._problems([{"kind": "flyback", "pin": "OUT", "ohms": 1, "why": "w"}])))
        self.assertTrue(any("not a signal pad" in p for p in self._problems([{"kind": "pulldown", "pin": "VCC", "ohms": 10000, "why": "w"}])))
        self.assertTrue(any("positive ohms" in p for p in self._problems([{"kind": "pulldown", "pin": "OUT", "ohms": 0, "why": "w"}])))
        self.assertTrue(any("no why" in p for p in self._problems([{"kind": "pulldown", "pin": "OUT", "ohms": 10000}])))

    def test_a_series_resistor_states_its_ohms_or_the_current_it_is_for(self):
        self.assertEqual(self._problems([{"kind": "series", "pin": "OUT", "ohms": 1000, "why": "limits the LED"}]), [])
        self.assertEqual(self._problems([{"kind": "series", "pin": "OUT", "for_current_ma": 5, "why": "an indicator"}]), [])
        said = " ".join(self._problems([{"kind": "series", "pin": "OUT", "why": "w"}]))
        self.assertIn("for_current_ma", said, "neither a value nor a current: nothing to place")

    def test_the_validator_carries_the_host_parts_problems(self):
        import tempfile
        record = {"schema": 1, "id": "x-part", "name": "X", "kind": "sensor",
                  "needs": [{"signal": "OUT", "pin": "OUT", "needs": []}], "power": [{"pin": "GND", "rail": "ground", "direction": "in"}],
                  "pin_order": ["OUT", "GND"], "footprint": "pinrow2", "body_mm": {"width": 5, "height": 5, "verified": True, "source": "x"},
                  "host_parts": [{"kind": "pulldown", "pin": "GND", "ohms": 100, "why": "w"}]}
        self.assertTrue(any("not a signal pad" in p for p in parts.validate(record, Path(tempfile.mkdtemp()) / "x-part.json")))

    def test_a_divider_needs_both_values(self):
        said = " ".join(self._problems([{"kind": "divider", "pin": "OUT", "top_ohms": 10000, "why": "w"}]))
        self.assertIn("bottom_ohms", said)
        self.assertEqual(self._problems([{"kind": "divider", "pin": "OUT", "top_ohms": 10000, "bottom_ohms": 18000, "why": "w"}]), [])

class APinOrderSaysHowItWasReadTest(unittest.TestCase):
    """
    P81. Every fact must say where it came from, except the one where a mistake reverses a supply:
    `pin_order` carried its proof only in a prose note nothing checked — and the irrigation DS3231's
    note described the 4-pad edge while its typed order was the 6-pin header, SCL against 32K.
    """

    def record(self, **extra):
        definition = {"schema": 1, "id": "x-part", "name": "X", "kind": "sensor",
                      "needs": [{"signal": "OUT", "pin": "OUT", "needs": []}],
                      "power": [{"pin": "GND", "rail": "ground", "direction": "in"}],
                      "pin_order": ["OUT", "GND"], "footprint": "pinrow2",
                      "body_mm": {"width": 5, "height": 5, "verified": True, "source": "x"}}
        definition.update(extra)
        return definition

    def problems(self, definition):
        import tempfile
        return [p for p in parts.validate(definition, Path(tempfile.mkdtemp()) / "x-part.json") if "pin_order" in p]

    def test_a_pin_order_without_proof_is_refused(self):
        self.assertTrue(any("pin_order_proof" in p for p in self.problems(self.record())))

    def test_a_proof_says_whether_it_was_verified_and_where_it_was_read(self):
        good = self.record(pin_order_proof={"verified": False, "source": "read off the module's silkscreen in a photo"})
        self.assertEqual(self.problems(good), [])
        self.assertTrue(self.problems(self.record(pin_order_proof={"verified": False, "source": ""})))
        self.assertTrue(self.problems(self.record(pin_order_proof={"verified": "yes", "source": "x"})))

    def test_an_unverified_pin_order_is_listed_with_the_unverified_facts(self):
        definition = self.record(pin_order_proof={"verified": False, "source": "read off a photo"})
        listed = [q for q in parts.open_questions_of(definition) if q["fact"] == "pin_order"]
        self.assertEqual(len(listed), 1)
        self.assertEqual(listed[0]["source"], "read off a photo")

class APullTheBoardAddsAgainstTheModulesOwnIsShownWithItsArithmeticTest(unittest.TestCase):
    """
    P81 increment 2, B11. The L9110S record states, verified, 10 k pull-ups to VCC on its inputs, and
    demands 10 k pull-downs of the board "so both are held low" — together a divider at half the
    supply, above the 2.5 V input threshold on the 6 V pack. The record's own note said so; no
    output did. A pull the board adds against the module's own is now shown, with the arithmetic.
    """

    def record(self, pulldown_ohms=10000):
        return part(facts={"onboard_input_pullups_ohms": {"value": 10000, "verified": True, "source": "schematic"},
                           "input_high_threshold_v": {"value": 2.5, "verified": True, "source": "datasheet"},
                           "supply_range_v": {"value": [2.5, 12.0], "verified": True, "source": "datasheet"}},
                    needs=[{"signal": "MOTOR_IA", "pin": "AIA"}],
                    host_parts=[{"kind": "pulldown", "pin": "AIA", "ohms": pulldown_ohms, "why": "held low"}])

    def test_the_divider_and_where_it_crosses_the_threshold_are_said(self):
        said = " ".join(parts.pull_conflicts(self.record()))
        self.assertIn("AIA", said)
        self.assertIn("0.5 of the supply", said)
        self.assertIn("5 V", said, "2.5 V x (10k + 10k) / 10k: the supply above which the pin idles HIGH")
        self.assertIn("input-low threshold is not recorded", said, "what is missing to decide, named")

    def test_a_pulldown_strong_enough_for_the_whole_supply_range_is_quiet(self):
        # 1 k against 10 k: at 12 V the pin idles at 1.09 V, under the 2.5 V threshold everywhere.
        self.assertEqual(parts.pull_conflicts(self.record(pulldown_ohms=1000)), [])

    def test_show_prints_it_where_a_person_reads_the_part(self):
        self.assertIn("5 V", parts.describe(self.record()))

class ReadingADatasheetStopsWhenItHasWhatItNeedsTest(unittest.TestCase):
    """
    P80. A research run printed a whole datasheet early and paid for it on every later turn; the
    facts a record needs sit on one or two pages (13 % of the LED's text, 2 % of the WROOM's). So
    `--read` streams page by page and stops on the page where every wanted fact has a table row.
    The fixture is written in a datasheet's shape; no vendor's text is copied.
    """

    PAGE_1 = """
    FEATURES
      * Low forward voltage, typically 1.9 V
      * Viewing angle 30 deg
    """
    PAGE_2 = """
    ELECTRICAL / OPTICAL CHARACTERISTICS at TA=25 C
      Parameter              Symbol      Typ.      Max.      Unit      Test Condition
      Forward Voltage        VF          1.9       2.3       V         IF=10mA
      Peak Wavelength        lambda      627                 nm        IF=10mA
    ABSOLUTE MAXIMUM RATINGS
      DC Forward Current     IF                    30        mA
    Viewing angle (2 theta)
      Lamp
           30
    """

    def pages(self, *texts):
        for number, text in enumerate(texts, 1):
            yield number, text
        raise AssertionError("read past the last page the facts are on")

    def test_a_fact_on_a_table_row_is_found_and_the_reading_stops_there(self):
        found = parts.scan_datasheet(self.pages(self.PAGE_1, self.PAGE_2), ["forward_voltage_v", "max_continuous_current_ma"])
        self.assertEqual(found["forward_voltage_v"]["status"], "FOUND")
        self.assertEqual(found["forward_voltage_v"]["hits"][0][:2], (2, 4), "page 2, line 4")
        self.assertIn("1.9", found["forward_voltage_v"]["hits"][0][3])
        self.assertEqual(found["max_continuous_current_ma"]["status"], "FOUND")

    def test_a_prose_bullet_is_never_taken_for_the_table(self):
        # The S3 overview's "7 uA" bullet was taken before the table — the P63 misreading in miniature.
        found = parts.scan_datasheet(iter([(1, self.PAGE_1)]), ["forward_voltage_v"])
        self.assertNotEqual(found["forward_voltage_v"]["status"], "FOUND")

    def test_a_unit_stated_in_a_column_header_counts(self):
        page = """
        Table 12: Current Consumption
          Work mode                 Description                     Current (uA)
          Deep-sleep                RTC memory and peripherals on   8
        """
        found = parts.scan_datasheet(iter([(1, page)]), ["deep_sleep_current_ua"])
        self.assertEqual(found["deep_sleep_current_ua"]["status"], "FOUND")
        self.assertIn("Table 12", found["deep_sleep_current_ua"]["hits"][0][2], "the locator a citation needs")

    def test_a_label_whose_value_sits_below_shows_the_next_lines(self):
        found = parts.scan_datasheet(iter([(1, self.PAGE_2)]), ["viewing_angle_deg"])
        self.assertEqual(found["viewing_angle_deg"]["status"], "LABEL ONLY")
        self.assertIn("30", found["viewing_angle_deg"]["hits"][0][3])

    def test_a_fact_nowhere_says_so_and_names_the_words_tried(self):
        found = parts.scan_datasheet(iter([(1, self.PAGE_2)]), ["reverse_current_ua"], labels={"reverse_current_ua": ["leakage"]})
        self.assertEqual(found["reverse_current_ua"]["status"], "NOT FOUND")
        self.assertIn("leakage", found["reverse_current_ua"]["tried"])

    def test_a_value_on_the_line_above_its_label_is_shown(self):
        # The WROOM-1's Table 12: "Deep-sleep" sits between its two rows, 8 uA above and 7 uA below
        # — showing only what follows the label is how 8 uA could be missed again (P63).
        page = """
        Table 12: Current Consumption Depending on Work Modes
          Work mode      Description                                       Typ      Unit
                         RTC memory and RTC peripherals are powered on.    8        uA
          Deep-sleep
                         RTC memory is powered on. RTC peripherals off.    7        uA
        """
        hit = parts.scan_datasheet(iter([(1, page)]), ["deep_sleep_current_ua"])["deep_sleep_current_ua"]["hits"][0][3]
        self.assertIn("8", hit)
        self.assertIn("7", hit)

    def test_a_table_row_is_never_taken_for_the_heading_it_sits_under(self):
        page = """
        Table 9: Recommended Operating Conditions
          VDD33        Power supply voltage        3.0     3.3     3.6     V
        """
        hit = parts.scan_datasheet(iter([(1, page)]), ["supply_voltage_v"])["supply_voltage_v"]["hits"][0]
        self.assertEqual(hit[2], "Table 9: Recommended Operating Conditions")

    def test_a_stray_capital_letter_is_not_a_heading(self):
        # The L-7113ID's ratings table has a line reading "K      Symbol" under its real heading.
        page = """
        ABSOLUTE MAXIMUM RATINGS
        K                           Symbol
          DC Forward Current        IF        30        mA
        """
        hit = parts.scan_datasheet(iter([(1, page)]), ["max_continuous_current_ma"])["max_continuous_current_ma"]["hits"][0]
        self.assertEqual(hit[2], "ABSOLUTE MAXIMUM RATINGS")

    def test_a_maker_naming_the_fact_its_own_way_is_still_read(self):
        page = """
          Parameter                           Symbol     Typ.     Unit
          Wavelength at Peak Emission         lpeak      627      nm
        """
        found = parts.scan_datasheet(iter([(1, page)]), ["peak_wavelength_nm"])["peak_wavelength_nm"]
        self.assertEqual(found["status"], "FOUND")
        self.assertEqual(len(found["tried"]), len(set(found["tried"])), "each word tried once")

    def test_the_command_reads_a_real_pdf_and_exits_by_what_it_found(self):
        import shutil, tempfile
        if not shutil.which("pdftotext"):
            self.skipTest("pdftotext is not installed")
        pdf = Path(tempfile.mkdtemp()) / "ds.pdf"
        pdf.write_bytes(_tiny_pdf([["FEATURES", "Small and bright"],
                                   ["Parameter      Symbol      Max.      Unit", "DC Forward Current      IF      30      mA"],
                                   ["this page must not be read"]]))
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = parts.main(["--read", str(pdf), "--want", "max_continuous_current_ma"])
        self.assertEqual(code, parts.EXIT_OK, out.getvalue())
        self.assertIn("p2:", out.getvalue())
        self.assertIn("read 2 of", out.getvalue(), "it stopped at the page with the fact")
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = parts.main(["--read", str(pdf), "--want", "peak_wavelength_nm"])
        self.assertNotEqual(code, parts.EXIT_OK, "a fact not found is not a pass")


def _tiny_pdf(pages):
    """A PDF with one text line per entry, columns kept by spaces — enough for pdftotext -layout."""
    objects, kids = [], []
    font = "<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>"
    objects.append(font)
    for lines in pages:
        stream = "BT /F1 10 Tf 40 760 Td 12 TL " + " ".join("(%s) '" % line for line in lines) + " ET"
        objects.append("<< /Length %d >>\nstream\n%s\nendstream" % (len(stream), stream))
        kids.append(len(objects) + 1)
        objects.append("<< /Type /Page /Parent PAGESREF /MediaBox [0 0 612 792] /Contents %d 0 R "
                       "/Resources << /Font << /F1 1 0 R >> >> >>" % len(objects))
    pages_index = len(objects) + 1
    objects.append("<< /Type /Pages /Kids [%s] /Count %d >>" % (" ".join("%d 0 R" % k for k in kids), len(kids)))
    objects.append("<< /Type /Catalog /Pages %d 0 R >>" % pages_index)
    out, offsets = "%PDF-1.4\n", []
    for number, body in enumerate(objects, 1):
        offsets.append(len(out))
        out += "%d 0 obj\n%s\nendobj\n" % (number, body.replace("PAGESREF", "%d 0 R" % pages_index))
    xref = len(out)
    out += "xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1) + "".join("%010d 00000 n \n" % o for o in offsets)
    out += "trailer\n<< /Size %d /Root %d 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objects) + 1, len(objects), xref)
    return out.encode("latin-1")



class TheCatalogIsThePersonSTest(unittest.TestCase):
    """P83: candidates nobody chose live in the person's store, keep their part facts, and no seller listings."""

    def test_the_catalog_lives_in_the_person_s_store_not_the_plugin(self):
        home = Path(tempfile.mkdtemp())
        (home / "catalog").mkdir()
        (home / "catalog" / "rtc-a.json").write_text(json.dumps({"schema": 1, "id": "rtc-a", "name": "An RTC", "kind": "rtc"}))
        with in_store(home):
            self.assertEqual(sorted(parts.catalog_records()[0]), ["rtc-a"], "read from the store's catalog")
        self.assertEqual(sorted((ROOT / "catalog").glob("*.json")), [], "the plugin ships no catalog records")

    def test_a_catalog_record_with_seller_listings_is_refused_by_name(self):
        import tempfile
        from unittest import mock
        home = Path(tempfile.mkdtemp()); catalog = home / "catalog"; catalog.mkdir()
        record = {"schema": 1, "id": "rtc-a", "name": "An RTC", "kind": "rtc",
                  "pin_order": ["VCC", "GND", "SCL", "SDA"],
                  "sourcing": [{"seller": "a shop", "url": "https://example.org", "price_czk": 99}]}
        (catalog / "rtc-a.json").write_text(json.dumps(record))
        kept = dict(record, id="rtc-b"); kept.pop("sourcing")
        (catalog / "rtc-b.json").write_text(json.dumps(kept))
        with in_store(home):
            records, broken = parts.catalog_records()
        self.assertEqual(sorted(records), ["rtc-b"], "a candidate keeps its part facts — its pinout too")
        self.assertEqual(records["rtc-b"]["pin_order"], ["VCC", "GND", "SCL", "SDA"])
        self.assertEqual(len(broken), 1)
        self.assertIn("rtc-a.json", broken[0])
        self.assertIn("seller listings", broken[0])


ENVELOPE_KEYS = ["data", "envelope", "next", "op", "problems", "status", "tool", "truncated", "unchecked"]


def run_json(argv):
    """parts.py with --json: (the one envelope it printed, its exit code). Anything else on stdout fails to parse."""
    with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
        code = parts.main(argv + ["--json"])
    return json.loads(out.getvalue()), code


class EveryAnswerIsOneEnvelopeTest(unittest.TestCase):
    """P95, §6.4.1–6.4.5: an agent reads one shape from every parts.py --json run, errors and bad arguments included."""

    def test_every_operation_answers_in_one_envelope_whose_status_is_its_exit(self):
        project = Path(tempfile.mkdtemp())
        for argv in (["--list"], ["--show", "no-such-part"], ["--validate"], ["--signals", "tactile-button"],
                     ["--unverified", "tactile-button"], ["--need", "unobtainium"], ["--skeleton", "x-part"],
                     ["--kept", "nothing-like-this"], ["--catalog"], ["--describe"], ["--promote", "x-part"],
                     ["--keep", str(project / "absent.pdf")], ["--bogus"], [], ["--list", "--show", "x"]):
            with self.subTest(argv=argv):
                said, code = run_json(argv)
                self.assertEqual(sorted(said), ENVELOPE_KEYS)
                self.assertEqual((said["envelope"], said["tool"]), (1, "parts"))
                self.assertEqual(code, outcomes.EXIT_FOR[said["status"]])

    def test_a_named_id_that_does_not_exist_is_problems(self):
        said, code = run_json(["--show", "no-such-part"])
        self.assertEqual((said["status"], code), ("problems", 1))
        self.assertEqual(said["problems"][0]["subject"], "no-such-part")

    def test_a_bad_argument_is_could_not_run_and_says_where_the_operations_are(self):
        said, code = run_json(["--bogus"])
        self.assertEqual((said["status"], code), ("could-not-run", 2))
        self.assertIn("--describe", said["unchecked"][0]["fix"])

    def test_an_operation_missing_its_project_is_could_not_run(self):
        said, code = run_json(["--skeleton", "x-part", "--kind", "sensor"])
        self.assertEqual((said["status"], code), ("could-not-run", 2))

    def test_finding_nothing_is_an_answer(self):
        said, code = run_json(["--need", "unobtainium"])
        self.assertEqual((said["status"], code, said["data"]["found"]), ("ok", 0, []))

    def test_describe_lists_exactly_what_the_parser_accepts(self):
        said, _ = run_json(["--describe"])
        described = {entry["flag"] for entry in said["data"]["operations"] + said["data"]["options"]}
        accepted = {action.option_strings[-1] for action in parts._parser()._actions
                    if action.option_strings and action.dest != "help"}
        self.assertEqual(described, accepted)
        self.assertEqual(said["data"]["exits"], {"0": "ok", "1": "problems", "2": "could-not-run"})
        self.assertEqual([op["op"] for op in said["data"]["operations"] if op["effects"] and not op["dry_run"]], [],
                         "every operation with an effect takes --dry-run")

    def test_a_dry_run_writes_nothing(self):
        project = Path(tempfile.mkdtemp())
        said, code = run_json(["--skeleton", "x-part", "--kind", "sensor", "--project", str(project), "--dry-run"])
        self.assertEqual((code, said["data"]["written"]), (0, False))
        self.assertFalse((project / "parts").exists())

    def test_a_dry_run_of_a_network_operation_reaches_nothing(self):
        # `sources_resolve` binds `reachable` as a default argument, so it is the function patched here.
        def no_network(*_):
            raise AssertionError("a dry run asked the network")
        with mock.patch.object(parts, "sources_resolve", no_network), mock.patch.object(parts, "_download", no_network):
            said, code = run_json(["--sources", "l9110s-module", "--dry-run"])
        self.assertEqual((code, bool(said["data"]["sources"])), (0, True))

    def test_a_record_that_is_not_json_is_could_not_run_not_a_traceback(self):
        project = Path(tempfile.mkdtemp())
        (project / "parts").mkdir()
        (project / "parts" / "broken.json").write_text("{")
        said, code = run_json(["--validate", "--project", str(project)])
        self.assertEqual(sorted(said), ENVELOPE_KEYS)
        self.assertEqual((said["status"], code), ("could-not-run", 2))
        self.assertIn("broken.json", said["unchecked"][0]["sentence"])

    def test_an_unreadable_store_is_could_not_run_not_a_traceback(self):
        with mock.patch.object(parts.store, "records", side_effect=PermissionError("the store is unreadable")):
            said, code = run_json(["--list"])
        self.assertEqual((sorted(said), said["status"], code), (ENVELOPE_KEYS, "could-not-run", 2))
        self.assertIn("the store is unreadable", said["unchecked"][0]["sentence"])

    def test_a_listing_is_paged_and_says_how_to_get_the_rest(self):
        home = Path(tempfile.mkdtemp())
        (home / "catalog").mkdir()
        for number in range(30):
            (home / "catalog" / ("x-%02d.json" % number)).write_text(json.dumps(
                {"schema": 1, "id": "x-%02d" % number, "name": "A candidate", "kind": "sensor"}))
        with in_store(home):
            first, _ = run_json(["--catalog"])
            rest, _ = run_json(first["truncated"]["next"]["argv"])
        self.assertEqual((first["truncated"]["shown"], first["truncated"]["total"]), (20, 30))
        self.assertEqual([r["id"] for r in first["data"]["records"] + rest["data"]["records"]],
                         ["x-%02d" % number for number in range(30)])
        self.assertIsNone(rest["truncated"]["next"])


class TheShelfIsALayerTest(unittest.TestCase):
    """P91, §5.5: a record on the shelf is found from every project — no project needed — and says where it is."""

    def test_a_record_on_the_shelf_is_listed_and_loaded_without_a_project(self):
        home = Path(tempfile.mkdtemp())
        record = json.loads((ROOT / "parts" / "tactile-button.json").read_text())
        record["id"] = "x-shelved"
        (home / "shelf").mkdir()
        (home / "shelf" / "x-shelved.json").write_text(json.dumps(record))
        with in_store(home):
            self.assertIn("x-shelved", parts.available())
            self.assertEqual(parts.load("x-shelved")["id"], "x-shelved")
            said, _ = run_json(["--list"])
        self.assertIn({"id": "x-shelved", "layer": "shelf"},
                      [{"id": p["id"], "layer": p["layer"]} for p in said["data"]["parts"]])


class TheShelfTest(unittest.TestCase):
    """P91, §5.5, §5.7: a record from one project goes onto the shelf as the part, not as that project's story of it."""

    def test_a_digest_moves_only_with_the_facts_a_build_reads(self):
        record = {"id": "x", "name": "X", "needs": [{"signal": "SIG"}], "pin_order": ["SIG", "GND"]}
        self.assertEqual(parts.digest(record),
                         hashlib.sha256(b'{"needs":[{"signal":"SIG"}],"pin_order":["SIG","GND"]}').hexdigest())
        self.assertEqual(parts.digest(dict(record, name="renamed", sources=["https://x.example"])), parts.digest(record))
        self.assertNotEqual(parts.digest(dict(record, pin_order=["GND", "SIG"])), parts.digest(record))

    def test_a_shelved_record_leaves_the_project_s_story_behind_and_says_where_it_came_from(self):
        home, source = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp()) / "x-module.json"
        record = json.loads((ROOT / "parts" / "tactile-button.json").read_text())
        record.update(id="x-module", owned=True, photo="photos/x.jpg", photos=["photos/x.jpg"],
                      sourcing=[{"seller": "a shop"}], alternatives=["y-module"])
        source.write_text(json.dumps(record))
        (source.parent / "x-module" / "chip").mkdir(parents=True)
        (source.parent / "x-module" / "chip" / "x.chip.json").write_text("{}")
        with in_store(home):
            self.assertTrue(parts.shelve(source, "irrigation"))
            self.assertFalse(parts.shelve(source, "irrigation"), "a retried shelving changes nothing")
            shelved = json.loads((home / "shelf" / "x-module.json").read_text())
            self.assertEqual(parts.load("x-module")["id"], "x-module", "the shelf copy still meets the contract")
        self.assertEqual(sorted(set(record) - set(shelved)), ["alternatives", "owned", "photo", "photos", "sourcing"])
        self.assertEqual(shelved["based_on"]["project"], "irrigation")
        self.assertEqual(len(shelved["based_on"]["digest"]), 64)
        self.assertTrue((home / "shelf" / "x-module" / "chip" / "x.chip.json").is_file(), "its folder travels with it")

    def test_a_shelved_folder_is_private_though_its_source_was_not(self):
        home, source = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp()) / "y-module.json"
        record = json.loads((ROOT / "parts" / "tactile-button.json").read_text())
        record["id"] = "y-module"
        source.write_text(json.dumps(record))
        chip = source.parent / "y-module" / "chip"
        chip.mkdir(parents=True)
        (chip / "y.chip.json").write_text("{}")
        os.chmod(chip / "y.chip.json", 0o644)
        os.chmod(chip, 0o755)
        with in_store(home):
            parts.shelve(source, "irrigation")
        shelved = home / "shelf" / "y-module" / "chip"
        self.assertEqual(stat.S_IMODE((shelved / "y.chip.json").stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(shelved.stat().st_mode), 0o700)


class OwningIsTheDrawersTest(unittest.TestCase):
    """P95 (W16): a record no longer says the person owns one — the drawer does."""

    def test_owned_photo_and_an_owned_seller_are_refused_naming_where_they_go(self):
        for extra, where in (({"owned": True}, "drawer"), ({"photo": "photos/x.jpg"}, "photos"),
                             ({"sourcing": [{"seller": "owned"}]}, "drawer")):
            with self.subTest(extra=extra):
                definition = part(**extra)
                said = [problem for problem in parts.validate(definition, written(definition)) if "retired" in problem]
                self.assertEqual(len(said), 1, said)
                self.assertIn(where, said[0])


class WhatAPartDoesTest(unittest.TestCase):
    """P96, §5.6: a record says what it does, or its kind says it; a sensor's is written once, through parts.py."""

    def test_a_kind_that_says_it_and_a_function_that_says_it(self):
        self.assertEqual(parts.function_of({"kind": "rtc"}), [{"does": "keep-time", "what": "rtc"}])
        self.assertEqual(parts.function_of({"kind": "rtc", "function": [{"does": "store", "what": "eeprom"}]}),
                         [{"does": "store", "what": "eeprom"}], "a record's own function wins")
        self.assertEqual(parts.function_of({"kind": "sensor"}), [], "a sensor says nothing until it is written")
        self.assertEqual(parts.function_of({"pins": {}}, board=True), [{"does": "compute", "what": "microcontroller"}])

    def test_a_function_outside_the_thirteen_verbs_is_refused(self):
        definition = part(function=[{"does": "measure", "what": "soil-moisture"}])
        self.assertTrue(any("function" in p and "keep-time" in p for p in parts.validate(definition, written(definition))))
        definition = part(function=[{"does": "sense", "what": "soil-moisture"}])
        self.assertEqual([p for p in parts.validate(definition, written(definition)) if "function" in p], [])

    def test_function_set_writes_into_the_record_s_own_home_after_a_dry_run(self):
        home = Path(tempfile.mkdtemp())
        (home / "catalog").mkdir()
        (home / "catalog" / "x-soil.json").write_text(json.dumps({"schema": 1, "id": "x-soil", "name": "A probe", "kind": "sensor"}))
        given = Path(tempfile.mkdtemp()) / "function.json"
        given.write_text(json.dumps([{"does": "sense", "what": "soil-moisture"}]))
        with in_store(home):
            dry, code = run_json(["--function-set", "x-soil", str(given), "--dry-run"])
            self.assertEqual((code, dry["data"]["written"]), (0, False))
            self.assertNotIn("function", json.loads((home / "catalog" / "x-soil.json").read_text()))
            done, code = run_json(["--function-set", "x-soil", str(given)])
        self.assertEqual((code, done["data"]["now"]), (0, [{"does": "sense", "what": "soil-moisture"}]))
        self.assertEqual(json.loads((home / "catalog" / "x-soil.json").read_text())["function"],
                         [{"does": "sense", "what": "soil-moisture"}])

    def test_function_set_refuses_a_wrong_function_and_a_part_nobody_has(self):
        given = Path(tempfile.mkdtemp()) / "function.json"
        given.write_text(json.dumps([{"does": "measure", "what": "x"}]))
        self.assertEqual(run_json(["--function-set", "tactile-button", str(given)])[1], 1)
        given.write_text(json.dumps([{"does": "sense", "what": "x"}]))
        self.assertEqual(run_json(["--function-set", "no-such-part", str(given), "--dry-run"])[1], 1)


class OwedIsNotBrokenTest(unittest.TestCase):
    """§5.4: an absent fact is owed — the record waits for it; a present, wrong value is broken."""

    def test_a_record_missing_what_the_chain_reads_owes_it_and_is_not_broken(self):
        definition = part(body_mm={"width": None, "height": None, "verified": False, "source": None})
        self.assertEqual(sorted(parts.owes(definition)), ["body_mm", "footprint", "pin_order", "pin_order_proof", "simulation"])
        self.assertEqual(parts.broken_problems(definition, written(definition)), [])

    def test_a_present_wrong_value_is_broken(self):
        definition = part(needs=[{"signal": "SIG", "pin": "S", "direction": "sideways"}])
        self.assertTrue(any("sideways" in p for p in parts.broken_problems(definition, written(definition))))

    def test_a_problem_that_merely_names_an_owed_key_is_still_broken(self):
        placeholder = part(footprint=None, footprint_placeholder=True)
        self.assertIn("footprint", parts.owes(placeholder))
        self.assertTrue(any(p.startswith("footprint_placeholder is set") for p in parts.broken_problems(placeholder, written(placeholder))))
        no_needs = part(simulation={"wokwi": "x"})
        del no_needs["needs"]
        self.assertIn("needs", parts.owes(no_needs))
        self.assertTrue(any(p.startswith("simulation needs wokwi") for p in parts.broken_problems(no_needs, written(no_needs))))

    def test_audit_walks_every_layer_names_what_says_nothing_and_exits_1_only_on_broken(self):
        home = Path(tempfile.mkdtemp())
        (home / "catalog").mkdir()
        (home / "catalog" / "x-draft.json").write_text(json.dumps({"schema": 1, "id": "x-draft", "name": "A probe", "kind": "sensor"}))
        with in_store(home):
            said, code = run_json(["--audit"])
        self.assertEqual((said["status"], code), ("ok", 0), "a draft that owes facts is not a problem")
        self.assertEqual(said["data"]["layers"]["catalog"], {"current": 0, "owed": 1, "broken": 0})
        self.assertIn("x-draft", said["data"]["no_function"])
        (home / "catalog" / "x-bad.json").write_text(json.dumps({"schema": 2, "id": "x-bad", "name": "B", "kind": "rtc"}))
        with in_store(home):
            said, code = run_json(["--audit"])
        self.assertEqual((said["status"], code), ("problems", 1))
        self.assertEqual([b["id"] for b in said["data"]["broken"]], ["x-bad"])

    def test_audit_names_a_drawer_link_to_a_record_nobody_has(self):
        home = Path(tempfile.mkdtemp())
        (home / "drawer").mkdir()
        (home / "drawer" / "x.json").write_text(json.dumps({"schema": 1, "label": "x", "count": 1, "is": {"part": "gone-part"}}))
        with in_store(home):
            said, code = run_json(["--audit"])
        self.assertEqual((code, said["data"]["dangling"]), (1, ["x"]))


if __name__ == "__main__":
    unittest.main()
