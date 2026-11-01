"""
Proof that pins are spent in the right order, and that an impossible request is refused.

The thing being tested is a judgement, not a calculation: which pin a signal *should* get when
several would work. Getting it wrong is not an error, it is a worse board — an ADC pin burned on
an LED, and then a sensor with nowhere to go.

Two properties carry the whole design and both are asserted below.

**Scarce last.** A signal that needs nothing special must never take a pin that can do something,
while a plainer pin is free. Otherwise the order signals happen to be listed decides the board.

**A refusal, not a partial answer.** A set of requirements that cannot be met comes back as an
explanation naming what could have served it. A tool that assigns most of them and exits zero is
how a board gets built around a pin map that was never satisfiable.

    python3 -m unittest discover -s tests
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import assign_pins  # noqa: E402


def board(**overrides):
    """
    A small board with one of each kind of pin, so a test can be read at a glance.

      P0, P1  plain          — nothing special, the cheapest thing to spend
      W0, W1  wake only
      A0      wake and adc   — the most capable, and so the last resort
      S0      strapping      — never assignable
      U0      console UART   — assignable, but it costs you the serial console
      B0      onboard button — assignable, but something is already wired to it
    """
    return dict({
        "schema": 1, "id": "test", "name": "Test Board", "chip": "esp32",
        "pins": {"P0": 0, "P1": 1, "W0": 2, "W1": 3, "A0": 4, "S0": 5, "U0": 6, "B0": 7},
        "wake_capable_gpio": [2, 3, 4],
        "adc_gpio": [4],
        "pin_roles": {
            "strapping": {"gpio": [5], "note": "sampled at reset"},
            "console_uart": {"gpio": [6], "note": "the serial console"},
            "onboard_button": {"gpio": [7], "note": "a button is already on it"},
        },
    }, **overrides)


def placed(assignments):
    return {entry["signal"]: entry["pin"] for entry in assignments}


class ScarceLastTest(unittest.TestCase):
    def test_a_plain_signal_takes_a_plain_pin(self):
        assignments, _ = assign_pins.assign(board(), [{"name": "LED", "needs": []}])
        self.assertIn(placed(assignments)["LED"], ("P0", "P1"))

    def test_a_plain_signal_does_not_burn_the_adc_pin(self):
        signals = [{"name": "L%d" % n, "needs": []} for n in range(4)]
        assignments, _ = assign_pins.assign(board(), signals)
        self.assertNotIn("A0", placed(assignments).values(),
                         "the only ADC pin was spent on a signal that did not need it")

    def test_the_order_signals_are_listed_in_does_not_decide_the_board(self):
        # Most-constrained-first, so a greedy pass cannot strand the hard requirement.
        hard_last = [{"name": "LED", "needs": []}, {"name": "SENSE", "needs": ["adc"]}]
        hard_first = list(reversed(hard_last))
        self.assertEqual(placed(assign_pins.assign(board(), hard_last)[0])["SENSE"],
                         placed(assign_pins.assign(board(), hard_first)[0])["SENSE"])

    def test_a_signal_that_needs_wake_gets_a_wake_pin(self):
        assignments, _ = assign_pins.assign(board(), [{"name": "INT", "needs": ["wake"]}])
        self.assertIn(placed(assignments)["INT"], ("W0", "W1"),
                      "a wake signal took the ADC pin while plain wake pins were free")

    def test_a_signal_that_needs_adc_gets_the_adc_pin(self):
        assignments, _ = assign_pins.assign(board(), [{"name": "SENSE", "needs": ["adc"]}])
        self.assertEqual(placed(assignments)["SENSE"], "A0")

    def test_the_reason_does_not_claim_scarcity_while_a_pin_with_the_same_ability_sits_free(self):
        # I8: the irrigation controller's three probes were each told "spent here because nothing
        # else was available" with two ADC pins still listed under "still free".
        two_adc = board(pins={"P0": 0, "A0": 4, "A1": 8}, adc_gpio=[4, 8], wake_capable_gpio=[4, 8])
        assignments, free = assign_pins.assign(two_adc, [{"name": "SENSE", "needs": ["adc"]}])
        self.assertIn("A1", free, "a second ADC pin is still free")
        self.assertNotIn("nothing else", assignments[0]["why"], assignments[0]["why"])


class PinsWithAnotherJobTest(unittest.TestCase):
    def test_a_strapping_pin_is_never_assigned(self):
        # Hold a button on a strapping pin during a reset and the board enters its bootloader.
        signals = [{"name": "S%d" % n, "needs": []} for n in range(7)]
        assignments, _ = assign_pins.assign(board(), signals)
        self.assertNotIn("S0", placed(assignments).values())

    def test_the_console_is_kept_free_for_longer_than_a_wake_pin(self):
        # This board has three wake-capable pins and one console. Losing the console costs you
        # bring-up; losing a wake pin costs you one of three.
        signals = [{"name": "S%d" % n, "needs": []} for n in range(4)]
        assignments, _ = assign_pins.assign(board(), signals)
        self.assertNotIn("U0", placed(assignments).values())

    def test_an_encumbered_pin_is_used_when_nothing_else_is_left(self):
        # It is a worse choice, not a forbidden one — and the answer has to say why.
        signals = [{"name": "S%d" % n, "needs": []} for n in range(6)]
        assignments, _ = assign_pins.assign(board(), signals)
        taken = set(placed(assignments).values())
        self.assertTrue({"U0", "B0"} & taken)
        shared = [a for a in assignments if a["pin"] in ("U0", "B0")]
        self.assertTrue(all("already wired here" in a["why"] for a in shared))

    # --- MVP --- P389
    def with_a_screen(self):
        """The test board with one more pin, D0 on GPIO 8, that the board's own display uses."""
        return board(pins=dict(board()["pins"], D0=8), pin_roles=dict(
            board()["pin_roles"], onboard_display={"gpio": [8], "labels": {"CS": 8}, "note": "the screen's chip select"}))

    def test_a_pin_of_the_boards_own_display_is_kept_free_for_longer_than_a_plain_one(self):
        signals = [{"name": "S%d" % n, "needs": []} for n in range(2)]
        assignments, _ = assign_pins.assign(self.with_a_screen(), signals)
        self.assertNotIn("D0", placed(assignments).values())

    def test_a_pin_of_the_display_is_used_when_nothing_else_is_left_and_the_answer_says_why(self):
        signals = [{"name": "S%d" % n, "needs": []} for n in range(7)]
        assignments, _ = assign_pins.assign(self.with_a_screen(), signals)
        shared = [entry for entry in assignments if entry["pin"] == "D0"]
        self.assertEqual(len(shared), 1, placed(assignments))
        self.assertEqual(shared[0]["roles"], ["onboard_display"])
        self.assertIn("something else is already wired here (onboard_display)", shared[0]["why"])

    def test_a_pin_of_the_display_costs_more_than_one_of_the_board_s_button(self):
        self.assertGreater(assign_pins.ROLE_PENALTY["onboard_display"], assign_pins.ROLE_PENALTY["onboard_button"])

    def test_a_pin_the_battery_divider_is_wired_to_costs_as_much_as_the_board_s_led_and_less_than_the_console(self):
        penalty = assign_pins.ROLE_PENALTY["onboard_battery_sense"]
        self.assertGreaterEqual(penalty, assign_pins.ROLE_PENALTY["onboard_led"])
        self.assertLess(penalty, assign_pins.ROLE_PENALTY["console_uart"])

    def with_a_battery_pin(self):
        """The test board with one more pin, D0 on GPIO 8, that a divider from the battery is wired to."""
        return board(pins=dict(board()["pins"], D0=8), pin_roles=dict(
            board()["pin_roles"], onboard_battery_sense={"gpio": [8], "note": "the battery divider"}))

    def test_the_battery_level_pin_is_kept_free_for_longer_than_a_plain_one(self):
        signals = [{"name": "S%d" % n, "needs": []} for n in range(2)]
        assignments, _ = assign_pins.assign(self.with_a_battery_pin(), signals)
        self.assertNotIn("D0", placed(assignments).values())

    def test_the_battery_level_pin_is_used_when_nothing_else_is_left_and_the_answer_says_why(self):
        signals = [{"name": "S%d" % n, "needs": []} for n in range(7)]
        assignments, _ = assign_pins.assign(self.with_a_battery_pin(), signals)
        shared = [entry for entry in assignments if entry["pin"] == "D0"]
        self.assertEqual(len(shared), 1, placed(assignments))
        self.assertEqual(shared[0]["roles"], ["onboard_battery_sense"])
        self.assertIn("something else is already wired here (onboard_battery_sense)", shared[0]["why"])
    # --- end MVP ---

    def test_every_assignment_explains_itself(self):
        assignments, _ = assign_pins.assign(
            board(), [{"name": "A", "needs": ["adc"]}, {"name": "B", "needs": []}])
        self.assertTrue(all(entry["why"] for entry in assignments))


class PinsAskedForByNameTest(unittest.TestCase):
    def test_a_named_pin_is_honoured_without_argument(self):
        # Dedicated hardware — an I2C bus — is a fact about the board, not a choice to optimise.
        assignments, _ = assign_pins.assign(board(), [{"name": "SDA", "pin": "A0"}])
        self.assertEqual(placed(assignments)["SDA"], "A0")

    def test_a_named_pin_the_board_does_not_have_is_refused(self):
        with self.assertRaises(assign_pins.Impossible) as refused:
            assign_pins.assign(board(), [{"name": "SDA", "pin": "NOPE"}])
        self.assertIn("does not bring out", str(refused.exception))

    def test_two_signals_on_one_named_pin_are_refused(self):
        with self.assertRaises(assign_pins.Impossible):
            assign_pins.assign(board(), [{"name": "A", "pin": "P0"}, {"name": "B", "pin": "P0"}])

    def test_a_named_pin_is_taken_out_of_play_for_everyone_else(self):
        assignments, free = assign_pins.assign(
            board(), [{"name": "SDA", "pin": "P0"}, {"name": "LED", "needs": []}])
        self.assertEqual(placed(assignments)["LED"], "P1")
        self.assertNotIn("P0", free)


class RefusalTest(unittest.TestCase):
    def test_more_wake_signals_than_wake_pins_is_refused_with_the_reason(self):
        signals = [{"name": "W%d" % n, "needs": ["wake"]} for n in range(4)]
        with self.assertRaises(assign_pins.Impossible) as refused:
            assign_pins.assign(board(), signals)
        message = str(refused.exception)
        self.assertIn("needs wake", message)
        self.assertIn("already taken", message)
        # It must name the pins that could have served it, or the reader has nothing to act on.
        self.assertTrue(any(pin in message for pin in ("W0", "W1", "A0")))

    def test_a_capability_no_pin_has_is_refused_plainly(self):
        flat = board(wake_capable_gpio=[], adc_gpio=[])
        with self.assertRaises(assign_pins.Impossible) as refused:
            assign_pins.assign(flat, [{"name": "INT", "needs": ["wake"]}])
        self.assertIn("no pin on this board can do that", str(refused.exception))

    def test_an_unknown_requirement_is_refused_rather_than_ignored(self):
        # A typo'd requirement that is silently dropped produces a board that is wrong in exactly
        # the way the requirement existed to prevent.
        with self.assertRaises(assign_pins.Impossible) as refused:
            assign_pins.assign(board(), [{"name": "X", "needs": ["waek"]}])
        self.assertIn("not something a pin can be asked for", str(refused.exception))

    def test_nothing_is_assigned_when_the_set_is_impossible(self):
        # Partial answers are the failure mode: a board gets built around a map that was never
        # satisfiable, and the missing signal is discovered on the bench.
        signals = [{"name": "W%d" % n, "needs": ["wake"]} for n in range(4)]
        with self.assertRaises(assign_pins.Impossible):
            assign_pins.assign(board(), signals)


class AgainstARealBoardTest(unittest.TestCase):
    """The board this was written against, with the signals it actually carries."""

    SIGNALS = [
        {"name": "TOF_INT", "needs": ["wake"]}, {"name": "BTN_OPEN", "needs": ["wake"]},
        {"name": "MOTOR_SENSE", "needs": ["adc"]},
        {"name": "SDA", "pin": "SDA"}, {"name": "SCL", "pin": "SCL"},
        {"name": "MOTOR_IA"}, {"name": "MOTOR_IB"}, {"name": "MP3_TX"},
        {"name": "MP3_ENABLE"}, {"name": "BTN_MODE"}, {"name": "LED_RED"},
        {"name": "LED_GREEN"},
    ]

    def setUp(self):
        import json
        self.board = json.loads(
            (ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())

    def test_it_places_every_signal(self):
        assignments, _ = assign_pins.assign(self.board, self.SIGNALS)
        self.assertEqual(len(assignments), len(self.SIGNALS))

    def test_it_keeps_the_console_and_the_onboard_button_free(self):
        _, free = assign_pins.assign(self.board, self.SIGNALS)
        self.assertIn("TX", free)
        self.assertIn("RX", free)
        self.assertIn("D14", free)

    def test_it_spends_exactly_one_adc1_pin(self):
        # Only MOTOR_SENSE asked for one, and ADC1 is the scarce resource on this chip.
        assignments, _ = assign_pins.assign(self.board, self.SIGNALS)
        adc1 = set(self.board["adc_gpio"])
        spent = [a for a in assignments if a["gpio"] in adc1 and a["signal"] not in ("SDA", "SCL")]
        self.assertEqual([a["signal"] for a in spent], ["MOTOR_SENSE"])

    def test_no_signal_lands_on_a_strapping_pin(self):
        assignments, _ = assign_pins.assign(self.board, self.SIGNALS)
        strapping = set(self.board["pin_roles"]["strapping"]["gpio"])
        self.assertEqual([a for a in assignments if a["gpio"] in strapping], [])



class TheDocumentedInvocationTest(unittest.TestCase):
    """
    `assign_pins.py requirements.json` is the first step every document names, and until
    2026-09-29 nothing called `main`: it crashed with `TypeError` on the `{part, name}` entry
    form the same documents show, and on `rails` (audit B1). These run it the documented way.
    """

    @staticmethod
    def _main(argv, cwd):
        import contextlib
        import io
        import os
        out = io.StringIO()
        was = os.getcwd()
        os.chdir(cwd)
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                code = assign_pins.main(argv)
        finally:
            os.chdir(was)
        return code, out.getvalue()

    @staticmethod
    def _project(requirements):
        import json
        import tempfile
        root = Path(tempfile.mkdtemp())
        (root / ".spark").mkdir()
        (root / "requirements.json").write_text(json.dumps(requirements))
        return root

    def test_the_build_commands_own_example_gets_a_pin_per_signal(self):
        import json
        import re
        text = (ROOT / "commands" / "build.md").read_text()
        example = json.loads(re.search(r"```json\n(.*?)```", text, re.S).group(1))
        code, out = self._main(["requirements.json"], self._project(example))
        self.assertEqual(code, assign_pins.EXIT_OK, out)
        self.assertIn("MOTOR_IA", out)
        self.assertIn("BTNOPEN_", out)
        self.assertIn("BTNMODE_", out)

    def test_a_rails_entry_is_accepted(self):
        code, out = self._main(["requirements.json"], self._project(
            {"board": "firebeetle2-esp32s3",
             "parts": [{"part": "l9110s-module", "rails": {"VCC": "traction"}}]}))
        self.assertEqual(code, assign_pins.EXIT_OK, out)
        self.assertIn("MOTOR_IA", out)

    def test_a_shipped_part_with_a_guessed_outline_is_unverified_by_its_body_mm(self):
        # P373: the outline is a fact nobody checked, so the pin map's `unverified` lists it, in --json and in the text.
        root = self._project({"board": "firebeetle2-esp32s3", "parts": ["speaker-terminal"]})
        code, out = self._main(["requirements.json", "--json"], root)
        self.assertEqual(code, assign_pins.EXIT_OK, out)
        import json
        rows = json.loads(out)["unverified"]
        (outline,) = [row for row in rows if row["fact"] == "body_mm"]
        self.assertEqual((outline["part"], outline["write"], outline["assumed"]),
                         ("speaker-terminal", "body_mm", {"width": 7.9, "height": 5.8}))
        self.assertIn("    speaker-terminal.body_mm", self._main(["requirements.json"], root)[1])

    def test_malformed_requirements_are_could_not_run_not_a_traceback(self):
        root = self._project({})
        (root / "requirements.json").write_text("{not json")
        code, out = self._main(["requirements.json"], root)
        self.assertEqual(code, assign_pins.EXIT_COULD_NOT_RUN)
        self.assertIn("not JSON", out)

    def test_a_malformed_part_record_is_could_not_run_naming_the_part(self):
        root = self._project({"board": "firebeetle2-esp32s3", "parts": ["l9110s-module"]})
        (root / "parts").mkdir()
        (root / "parts" / "l9110s-module.json").write_text("{half a record")
        code, out = self._main(["requirements.json"], root)
        self.assertEqual(code, assign_pins.EXIT_COULD_NOT_RUN)
        self.assertIn("l9110s-module", out)


class ABusIsSharedTest(unittest.TestCase):
    """
    P21, from audit B2 and B3. The bus path found a signal's pin by the signal's NAME matching a
    board label, so an instance name (`RANGEFINDER_SDA`) took a part off its bus with exit 0, two
    I2C parts were refused as "already taken" when a bus is exactly what they share, and a bus
    line named the vendor's way (`CLK`, `DIN`) was placed on any pin with no word — against the
    docstring's promise that nothing is silently dropped.
    """

    def setUp(self):
        import json
        self.board = json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())

    @staticmethod
    def on(signal, assignments):
        return next(a["pin"] for a in assignments if a["signal"] == signal)

    def test_an_instance_name_does_not_take_a_part_off_its_bus(self):
        signals = [{"name": "RANGEFINDER_SDA", "line": "SDA", "bus": "i2c", "needs": []},
                   {"name": "RANGEFINDER_SCL", "line": "SCL", "bus": "i2c", "needs": []}]
        placed, _ = assign_pins.assign(self.board, signals)
        self.assertEqual(self.on("RANGEFINDER_SDA", placed), "SDA")
        self.assertEqual(self.on("RANGEFINDER_SCL", placed), "SCL")

    def test_two_parts_on_one_bus_share_its_pins(self):
        signals = [{"name": "A_SDA", "line": "SDA", "bus": "i2c", "needs": []},
                   {"name": "A_SCL", "line": "SCL", "bus": "i2c", "needs": []},
                   {"name": "B_SDA", "line": "SDA", "bus": "i2c", "needs": []},
                   {"name": "B_SCL", "line": "SCL", "bus": "i2c", "needs": []}]
        placed, _ = assign_pins.assign(self.board, signals)
        self.assertEqual({self.on("A_SDA", placed), self.on("B_SDA", placed)}, {"SDA"})
        self.assertEqual({self.on("A_SCL", placed), self.on("B_SCL", placed)}, {"SCL"})

    def test_a_bus_line_named_the_vendors_way_lands_on_the_boards_pin(self):
        # An e-paper or SPI display record written from its vendor's pinout says DIN and CLK.
        signals = [{"name": "CLK", "bus": "spi", "needs": []}, {"name": "DIN", "bus": "spi", "needs": []},
                   {"name": "DOUT", "bus": "spi", "needs": []}]
        placed, _ = assign_pins.assign(self.board, signals)
        self.assertEqual(self.on("CLK", placed), "SCK")
        self.assertEqual(self.on("DIN", placed), "MOSI")
        self.assertEqual(self.on("DOUT", placed), "MISO")

    def test_a_bus_line_the_vocabulary_does_not_know_is_refused_not_placed_anywhere(self):
        with self.assertRaises(assign_pins.Impossible) as refused:
            assign_pins.assign(self.board, [{"name": "XYZ", "bus": "spi", "needs": []}])
        self.assertIn("XYZ", str(refused.exception))
        self.assertIn("SCK", str(refused.exception), "the refusal names the lines a bus has")

    def test_a_bus_the_board_does_not_label_is_refused(self):
        board = dict(self.board, pins={k: v for k, v in self.board["pins"].items() if k not in ("SDA", "SCL")})
        with self.assertRaises(assign_pins.Impossible) as refused:
            assign_pins.assign(board, [{"name": "SDA", "bus": "i2c", "needs": []}])
        self.assertIn("SDA", str(refused.exception))

    def test_a_chip_select_is_not_shared(self):
        # Every SPI device has its own select: the first takes SS, the second any free pin.
        signals = [{"name": "A_CS", "line": "CS", "bus": "spi", "needs": []},
                   {"name": "B_CS", "line": "CS", "bus": "spi", "needs": []}]
        placed, _ = assign_pins.assign(self.board, signals)
        pins = {self.on("A_CS", placed), self.on("B_CS", placed)}
        self.assertIn("SS", pins)
        self.assertEqual(len(pins), 2)

    def test_a_bus_pin_taken_by_a_plain_signal_is_still_a_conflict(self):
        with self.assertRaises(assign_pins.Impossible):
            assign_pins.assign(self.board, [{"name": "LED", "pin": "SDA", "needs": []},
                                            {"name": "SDA", "bus": "i2c", "needs": []}])


class TheHelpersEachHaveANameTest(unittest.TestCase):
    """
    Audit B16: `roles_of`, `_penalty`, `_why` and `_why_not` were reached only through `assign`.
    Each is a sentence a person can disagree with, so each gets a test that says what it claims.
    """

    def setUp(self):
        import json
        self.board = json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())

    def test_roles_of_lists_every_role_a_gpio_carries(self):
        self.assertEqual(assign_pins.roles_of(self.board, 17), ["adc2_unusable_with_wifi", "spi"])
        self.assertEqual(assign_pins.roles_of(self.board, 47), ["not_wake_capable", "onboard_button"])
        # GPIO 38 is not an RTC pin on the S3, so it rightly carries `not_wake_capable`; GPIO 4
        # (A0) carries nothing — the first version of this test had that the wrong way round.
        self.assertEqual(assign_pins.roles_of(self.board, 38), ["not_wake_capable"])
        self.assertEqual(assign_pins.roles_of(self.board, 4), [])

    def test_penalty_sums_the_roles_and_not_being_wake_capable_costs_nothing(self):
        # Not waking is not a cost of spending the pin: nothing is lost that a plain signal had.
        self.assertEqual(assign_pins._penalty(["not_wake_capable"]), 0)
        self.assertEqual(assign_pins._penalty(["onboard_button"]), assign_pins.ROLE_PENALTY["onboard_button"])
        self.assertEqual(assign_pins._penalty(["spi", "onboard_led"]),
                         assign_pins.ROLE_PENALTY["spi"] + assign_pins.ROLE_PENALTY["onboard_led"])

    def test_why_says_what_the_pin_does_beyond_what_was_asked(self):
        exact = {"can": {"adc"}, "roles": []}
        self.assertIn("exactly that and no more", assign_pins._why({"adc"}, exact))
        spare = {"can": {"adc", "wake"}, "roles": []}
        self.assertIn("also does wake", assign_pins._why({"adc"}, spare))
        plain = {"can": set(), "roles": []}
        self.assertIn("can do nothing special", assign_pins._why(set(), plain))
        shared = {"can": set(), "roles": ["onboard_led"]}
        self.assertIn("already wired here", assign_pins._why(set(), shared))

    def test_why_not_names_who_has_the_pins_or_says_no_pin_could(self):
        available = assign_pins.candidates(self.board)
        adc = {label for label, pin in available.items() if "adc" in pin["can"]}
        taken = {available[label]["gpio"] for label in adc}
        said = assign_pins._why_not(self.board, {"name": "SENSE"}, {"adc"}, available, taken)
        self.assertIn("could have served it", said)
        self.assertIn(sorted(adc)[0], said)
        no_adc = {label: pin for label, pin in available.items() if "adc" not in pin["can"]}
        said = assign_pins._why_not(self.board, {"name": "SENSE"}, {"adc"}, no_adc, set())
        self.assertIn("no pin on this board can do that at all", said)


class ABusWithNoDedicatedPinsGoesAnywhereTest(unittest.TestCase):
    """
    Close audit C6: P21's rule refused every bus line the board did not label, and the ESP32
    routes I2S through its GPIO matrix — no board labels BCLK — so the shipped MAX98357A could
    not be placed by the chain while `parts.py --validate` called it fine. A bus the board
    states no `pin_roles` for is placed like any signal, and the reason says so.
    """

    def setUp(self):
        import json
        self.board = json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())

    def test_the_shipped_i2s_amplifier_is_placed_and_the_reason_names_the_matrix(self):
        import parts
        placed, _ = assign_pins.assign(self.board, parts.signals_for(["max98357a-dfr0954"]))
        names = {a["signal"] for a in placed}
        self.assertTrue({"I2S_BCLK", "I2S_LRC", "I2S_DIN"} <= names, names)
        why = next(a["why"] for a in placed if a["signal"] == "I2S_BCLK")
        self.assertIn("GPIO matrix", why)
        self.assertIn("I2S", why)

    def test_a_bus_the_board_dedicates_pins_to_is_still_refused_when_a_line_is_missing(self):
        board = dict(self.board, pins={k: v for k, v in self.board["pins"].items() if k != "SDA"})
        with self.assertRaises(assign_pins.Impossible):
            assign_pins.assign(board, [{"name": "SDA", "bus": "i2c", "needs": []}])

    def test_the_vocabulary_is_the_parts_librarys(self):
        import parts
        self.assertIs(assign_pins.BUS_LINES, parts.BUSES)


class ANamedPinIsStillCheckedTest(unittest.TestCase):
    """
    Close audit C4: a signal naming its own pin was honoured without a look at its `needs` or
    the pin's roles. Named is dedicated, not exempt.
    """

    def setUp(self):
        import json
        self.board = json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())

    def test_a_named_pin_that_cannot_do_what_is_asked_is_refused_saying_what(self):
        with self.assertRaises(assign_pins.Impossible) as refused:
            assign_pins.assign(self.board, [{"name": "BTN_WAKE", "pin": "D14", "needs": ["wake"]}])
        self.assertIn("D14", str(refused.exception))
        self.assertIn("wake", str(refused.exception))
        with self.assertRaises(assign_pins.Impossible) as refused:
            assign_pins.assign(self.board, [{"name": "SENSE", "pin": "D3", "needs": ["adc"]}])
        self.assertIn("adc", str(refused.exception))

    def test_a_named_strap_is_refused_even_with_nothing_asked(self):
        with self.assertRaises(assign_pins.Impossible) as refused:
            assign_pins.assign(self.board, [{"name": "BTN_BOOT", "pin": "D9", "needs": []}])
        self.assertIn("strapping", str(refused.exception))

    def test_a_named_pin_that_can_do_it_is_honoured(self):
        placed, _ = assign_pins.assign(self.board, [{"name": "BTN_WAKE", "pin": "D12", "needs": ["wake"]}])
        self.assertEqual(placed[0]["pin"], "D12")
        self.assertIn("by name", placed[0]["why"])

class ThePinMapIsAFileTheFirmwareImportsTest(unittest.TestCase):
    """
    P36. The irrigation firmware typed twelve GPIO numbers by hand and its scenario a thirteenth,
    and nothing compared any of them with this file's answer: they agreed by luck. Now the answer
    is written as a module the firmware imports — plain integers, so CPython and MicroPython read
    it alike (P60), each with what the board record says about that pin.
    """

    SIGNALS = [{"name": "LED", "needs": []}, {"name": "SENSE", "needs": ["adc"]},
               {"name": "WAKE_BTN", "needs": ["wake"]}, {"name": "TX_LINE", "needs": []},
               {"name": "SPARE", "needs": []}, {"name": "LAST", "needs": []}]

    def _module(self):
        assignments, _ = assign_pins.assign(board(), self.SIGNALS)
        return assignments, assign_pins.pin_module(board(), assignments, "garden.requirements.json")

    def test_every_signal_appears_exactly_once_as_its_gpio(self):
        assignments, text = self._module()
        names = {}
        exec(text, names)       # plain Python: no `const`, no import of `micropython`
        own = {"ONBOARD_LED", "ONBOARD_BUTTON"}  # the board's own parts are lines of their own (P353)
        self.assertEqual({k: v for k, v in names.items() if not k.startswith("__") and k not in own},
                         {entry["signal"]: entry["gpio"] for entry in assignments})
        for entry in assignments:
            self.assertEqual(text.count("\n%s = " % entry["signal"]), 1, entry["signal"])

    def test_each_line_says_its_pad_and_why(self):
        assignments, text = self._module()
        sense = next(e for e in assignments if e["signal"] == "SENSE")
        line = next(text_line for text_line in text.splitlines() if text_line.startswith("SENSE = "))
        self.assertIn("pad %s" % sense["pin"], line)
        self.assertIn(sense["why"], line)

    def test_the_pad_named_is_the_one_silkscreened_on_the_board(self):
        # The FireBeetle's key is MOSI and its silkscreen reads MO (physical.pad_aliases): a
        # firmware author holding the board looks for MO.
        assignments, _ = assign_pins.assign(board(), [{"name": "LED", "needs": []}])
        aliased = board(physical={"pad_aliases": {assignments[0]["pin"]: "SILK"}})
        self.assertIn("# pad SILK;", assign_pins.pin_module(aliased, assignments, "r.json"))

    def test_the_board_s_own_led_is_named_even_with_no_parts(self):
        # P236: a board-only project blinks the LED the board record names; the number is the record's, not a guess.
        lit = board(pin_roles={"onboard_led": {"gpio": [15], "note": "the on-board user LED (not on the header)"}})
        names = {}
        exec(assign_pins.pin_module(lit, [], "r.json"), names)
        self.assertEqual(names["ONBOARD_LED"], 15)

    def test_a_signal_named_like_the_board_s_led_is_refused_not_shadowed(self):
        lit = board(pin_roles={"onboard_led": {"gpio": [15], "note": "the LED"}})
        assignments, _ = assign_pins.assign(lit, [{"name": "ONBOARD_LED", "needs": []}])
        with self.assertRaises(assign_pins.Impossible):
            assign_pins.pin_module(lit, assignments, "r.json")

    def test_the_level_that_lights_the_board_s_led_is_named_with_its_source(self):
        # P353: walk 1's firmware guessed the XIAO's LED level. The record holds it now, and the line says where from.
        lit = board(pin_roles={"onboard_led": {"gpio": [15], "note": "lit by a 0 (the bench)", "active_level": 0}})
        text = assign_pins.pin_module(lit, [], "r.json")
        names = {}
        exec(text, names)
        self.assertEqual(names["ONBOARD_LED_ON"], 0)
        self.assertIn("the bench", next(text_line for text_line in text.splitlines() if text_line.startswith("ONBOARD_LED = ")))
        self.assertNotIn("polarity is not in the board record", text)

    def test_a_led_with_no_level_in_the_record_keeps_today_s_note(self):
        lit = board(pin_roles={"onboard_led": {"gpio": [15], "note": "the LED"}})
        text = assign_pins.pin_module(lit, [], "r.json")
        self.assertIn("Its active level is not in the board record", text)
        self.assertNotIn("ONBOARD_LED_ON", text)

    def test_the_active_level_as_a_fact_is_named_with_its_source_and_whether_it_is_verified(self):
        # P464: a level written by --fact-set is {value, verified, source}; the line says where it came from
        bench = {"value": 0, "verified": True, "source": "the PO's bench, 2026-11-01"}
        guess = {"value": 1, "verified": False, "source": "the seller's page", "why_it_matters": "the LED may stay dark"}
        text = assign_pins.pin_module(board(pin_roles={
            "onboard_led": {"gpio": [15], "note": "the LED", "active_level": bench},
            "onboard_button": {"gpio": [9], "note": "the button", "active_level": guess}}), [], "r.json")
        names = {}
        exec(text, names)
        self.assertEqual((names["ONBOARD_LED_ON"], names["ONBOARD_BUTTON_ON"]), (0, 1))
        lines = text.splitlines()
        self.assertIn("ONBOARD_LED_ON = 0  # the active level in the board record, source: the PO's bench, 2026-11-01", lines)
        self.assertIn("ONBOARD_BUTTON_ON = 1  # the active level in the board record, source: the seller's page; not verified", lines)

    def test_a_button_with_no_level_says_so_in_its_comment(self):
        pressed = board(pin_roles={"onboard_button": {"gpio": [9], "note": "the BOOT button"}})
        self.assertIn("Its active level is not in the board record", assign_pins.pin_module(pressed, [], "r.json"))

    def test_the_board_s_own_button_is_named_with_its_source(self):
        pressed = board(pin_roles={"onboard_button": {"gpio": [9], "note": "the BOOT button (wiki)"}})
        text = assign_pins.pin_module(pressed, [], "r.json")
        names = {}
        exec(text, names)
        self.assertEqual(names["ONBOARD_BUTTON"], 9)
        self.assertIn("wiki", next(text_line for text_line in text.splitlines() if text_line.startswith("ONBOARD_BUTTON = ")))

    def test_a_signal_named_like_the_board_s_button_is_refused_not_shadowed(self):
        pressed = board(pin_roles={"onboard_button": {"gpio": [9], "note": "the button"}})
        assignments, _ = assign_pins.assign(pressed, [{"name": "ONBOARD_BUTTON", "needs": []}])
        with self.assertRaises(assign_pins.Impossible):
            assign_pins.pin_module(pressed, assignments, "r.json")

    def test_a_button_line_without_a_level_is_its_number_and_its_note(self):
        pressed = board(pin_roles={"onboard_button": {"gpio": [9], "note": "the BOOT button"}})
        lines = assign_pins.pin_module(pressed, [], "r.json").splitlines()
        self.assertIn("ONBOARD_BUTTON = 9  # onboard_button: the BOOT button. Its active level is not in the board record", lines)
        self.assertFalse(any(text_line.startswith("ONBOARD_BUTTON_ON") for text_line in lines))

    def test_a_role_on_two_gpios_names_no_single_pin(self):
        two = board(pin_roles={"onboard_led": {"gpio": [2, 3], "note": "two LEDs", "active_level": 0},
                               "onboard_button": {"gpio": [4, 5], "note": "two buttons"}})
        self.assertNotIn("ONBOARD_", assign_pins.pin_module(two, [], "r.json"))

    def test_a_signal_named_like_the_led_s_level_is_refused_not_shadowed(self):
        # The refuter's repro: a signal ONBOARD_LED_ON on GPIO17, then the level line, and the firmware read 0.
        lit = board(pin_roles={"onboard_led": {"gpio": [15], "note": "the LED", "active_level": 0}})
        assignments, _ = assign_pins.assign(lit, [{"name": "ONBOARD_LED_ON", "needs": []}])
        with self.assertRaises(assign_pins.Impossible):
            assign_pins.pin_module(lit, assignments, "r.json")

    def test_the_board_s_whole_note_reaches_its_own_line(self):
        # The XIAO's BOOT warning is the second sentence of its note, and the firmware writer needs it.
        pressed = board(pin_roles={"onboard_button": {"gpio": [9], "note": "the BOOT button. Held at reset it boots."}})
        self.assertIn("Held at reset it boots", assign_pins.pin_module(pressed, [], "r.json"))

    def test_the_xiao_s_pins_file_names_the_level_a_pressed_button_reads(self):
        # P388: walk 2 predicted the firmware must guess it. The record holds it, from the Seeed schematic.
        import json
        xiao = json.loads((ROOT / "boards" / "xiao-esp32-c6.json").read_text())
        names = {}
        exec(assign_pins.pin_module(xiao, [], "r.json"), names)
        self.assertEqual((names["ONBOARD_BUTTON"], names["ONBOARD_BUTTON_ON"]), (9, 0))
        self.assertEqual((names["ONBOARD_LED"], names["ONBOARD_LED_ON"]), (15, 0))

    def test_a_board_with_no_led_of_its_own_names_none(self):
        names = {}
        exec(assign_pins.pin_module(board(), [], "r.json"), names)
        self.assertNotIn("ONBOARD_LED", names)

    def test_a_pin_with_a_role_carries_the_board_records_own_words(self):
        # The probe models were told nothing and got ADC2-with-WiFi wrong; a note in the file
        # the firmware imports is where the next one reads it (P60: notes fixed 7 of 7).
        assignments, text = self._module()
        with_role = [e for e in assignments if e["roles"]]
        self.assertTrue(with_role, "the fixture must spend a pin that carries a role")
        role = with_role[0]["roles"][0]
        line = next(text_line for text_line in text.splitlines() if text_line.startswith(with_role[0]["signal"] + " = "))
        self.assertIn("%s: %s" % (role, board()["pin_roles"][role]["note"]), line)

    def test_the_file_names_its_source_and_says_not_to_edit_it(self):
        _, text = self._module()
        self.assertIn("garden.requirements.json", text.splitlines()[0] + text.splitlines()[1])
        self.assertIn("Test Board", text)
        self.assertIn("do not edit", text.lower())

    def test_a_line_break_in_the_board_s_words_never_leaves_the_comment(self):
        # concern 1 (P87's line-comment half): the board's name, a role's note, a pad's alias and the source file's name are
        # written into `#` comments, and a line break in one ended the comment — and the firmware imports this file
        import contextlib
        import io
        probe = '\nprint("PINMAP-INJECTED") #'
        assignments, _ = assign_pins.assign(board(), self.SIGNALS)
        role = next(e for e in assignments if e["roles"])["roles"][0]
        roles = dict(board()["pin_roles"], **{role: dict(board()["pin_roles"][role], note="its note" + probe)})
        places = {"the board's name": (board(name="Test Board" + probe), "r.json"),
                  "a role's note": (board(pin_roles=roles), "r.json"),
                  "a pad's alias": (board(physical={"pad_aliases": {assignments[0]["pin"]: "SILK" + probe}}), "r.json"),
                  "the source's name": (board(), "r" + probe + ".json")}
        for where, (crafted, source) in places.items():
            with self.subTest(where=where):
                text, out = assign_pins.pin_module(crafted, assignments, source), io.StringIO()
                with contextlib.redirect_stdout(out):
                    exec(text, {})
                self.assertEqual(out.getvalue(), "", "a comment's words were run")
                self.assertIn('print("PINMAP-INJECTED")', text, "kept, on the comment's own line")

    def test_a_signal_name_python_cannot_spell_is_refused_not_mangled(self):
        assignments, _ = assign_pins.assign(board(), [{"name": "2ND-LED", "needs": []}])
        with self.assertRaises(assign_pins.Impossible):
            assign_pins.pin_module(board(), assignments, "r.json")

    def test_the_command_writes_the_file(self):
        import json
        import tempfile
        root = Path(tempfile.mkdtemp())
        (root / ".spark").mkdir()
        (root / "requirements.json").write_text(json.dumps(
            {"board": "firebeetle2-esp32s3", "parts": ["l9110s-module"]}))
        code, out = TheDocumentedInvocationTest._main(
            ["requirements.json", "--emit-pins", "firmware/pins.py"], root)
        self.assertEqual(code, assign_pins.EXIT_OK, out)
        names = {}
        exec((root / "firmware" / "pins.py").read_text(), names)
        self.assertIn("MOTOR_IA", names)


# --- MVP ---
class TheBoardsOwnDisplayAndLabelledButtonsTest(unittest.TestCase):
    """P389: labels, facts and a display, named in pins.py from the record alone."""

    FIXTURE = ROOT / "tests" / "data" / "boards" / "lilygo-t-display.json"

    def record(self):
        import json
        return json.loads(self.FIXTURE.read_text())

    def lines(self, record, assignments=()):
        return assign_pins.pin_module(record, list(assignments), "r.json").splitlines()

    def named(self, record):
        """Each ONBOARD_ line cut before its comment."""
        return [line.split("  #")[0] for line in self.lines(record) if line.startswith("ONBOARD_")]

    def test_the_t_display_s_screen_buttons_and_driver_are_named(self):
        names = {}
        exec("\n".join(self.lines(self.record())), names)
        onboard = {key: value for key, value in names.items() if key.startswith("ONBOARD_")}
        self.assertEqual(onboard, {
            "ONBOARD_BUTTON_S1": 0, "ONBOARD_BUTTON_S2": 35, "ONBOARD_BUTTON_ON": 0,
            "ONBOARD_DISPLAY_MOSI": 19, "ONBOARD_DISPLAY_SCLK": 18, "ONBOARD_DISPLAY_CS": 5, "ONBOARD_DISPLAY_DC": 16,
            "ONBOARD_DISPLAY_RST": 23, "ONBOARD_DISPLAY_BL": 4, "ONBOARD_DISPLAY_DRIVER": "ST7789",
            "ONBOARD_DISPLAY_WIDTH": 135, "ONBOARD_DISPLAY_HEIGHT": 240,
            "ONBOARD_BATTERY_SENSE": 34, "ONBOARD_BATTERY_SENSE_DIVIDER": 2})

    def test_the_battery_level_pin_and_its_divider_are_named_with_their_source(self):
        lines = {line.split(" = ")[0]: line for line in self.lines(self.record())}
        self.assertTrue(lines["ONBOARD_BATTERY_SENSE"].startswith("ONBOARD_BATTERY_SENSE = 34  # onboard_battery_sense: GPIO34 reads the battery "), lines)
        self.assertIn("BAT_ADC", lines["ONBOARD_BATTERY_SENSE"])
        self.assertIn("source: documents.lilygo-t-display-schematic-2019-06-26, R6 and R7, 100K each", lines["ONBOARD_BATTERY_SENSE_DIVIDER"])
        self.assertFalse(lines["ONBOARD_BATTERY_SENSE_DIVIDER"].endswith("not verified"), lines["ONBOARD_BATTERY_SENSE_DIVIDER"])

    def test_a_power_fact_writes_no_line_of_its_own(self):
        lines = "\n".join(self.lines(self.record()))
        for word in ("TP4054", "AP2112K", "CHARGER", "REGULATOR", "BATTERY_INPUT"):
            self.assertNotIn(word, lines)

    def test_a_blank_fact_value_writes_no_line_and_a_word_does(self):
        facts = {"a_empty": "", "b_blank": "  ", "c_word": "x"}
        entry = {"gpio": [], "note": "x", "facts": {name: {"value": value, "verified": True, "source": "s"}
                                                     for name, value in facts.items()}}
        self.assertEqual(self.named(board(pin_roles={"onboard_display": entry})), ["ONBOARD_DISPLAY_C_WORD = 'x'"])

    def test_the_labels_come_in_the_records_order_and_the_note_is_on_the_first(self):
        lines = [line for line in self.lines(self.record()) if line.startswith("ONBOARD_DISPLAY_")]
        self.assertEqual([line.split(" = ")[0] for line in lines],
                         ["ONBOARD_DISPLAY_MOSI", "ONBOARD_DISPLAY_SCLK", "ONBOARD_DISPLAY_CS", "ONBOARD_DISPLAY_DC",
                          "ONBOARD_DISPLAY_RST", "ONBOARD_DISPLAY_BL", "ONBOARD_DISPLAY_DRIVER", "ONBOARD_DISPLAY_WIDTH",
                          "ONBOARD_DISPLAY_HEIGHT"])
        self.assertIn("The TFT on SPI with no MISO", lines[0])
        self.assertIn("the note is on the first line of this part", lines[1])
        self.assertNotIn("The TFT on SPI", lines[1])

    def test_a_fact_nobody_verified_says_so_and_a_verified_one_says_where_from(self):
        lines = {line.split(" = ")[0]: line for line in self.lines(self.record())}
        self.assertTrue(lines["ONBOARD_DISPLAY_WIDTH"].endswith("; not verified"), lines["ONBOARD_DISPLAY_WIDTH"])
        self.assertIn("source: none, no kept source states it", lines["ONBOARD_DISPLAY_WIDTH"])
        self.assertEqual(lines["ONBOARD_DISPLAY_DRIVER"],
                         "ONBOARD_DISPLAY_DRIVER = 'ST7789'  # onboard_display: driver, source: documents.lilygo-t-display-readme, "
                         "Pinout table, row TFT Driver")

    def test_each_button_label_is_a_line_and_the_level_is_one_line(self):
        lines = [line.split("  #")[0] for line in self.lines(self.record()) if line.startswith("ONBOARD_BUTTON")]
        self.assertEqual(lines, ["ONBOARD_BUTTON_S1 = 0", "ONBOARD_BUTTON_S2 = 35", "ONBOARD_BUTTON_ON = 0"])

    def test_a_fact_is_a_line_only_when_its_value_is_a_finite_number_or_a_word(self):
        facts = {"a_int": 3, "b_word": "it's", "c_bool": True, "d_none": None, "e_float": 1.14, "f_list": [1], "g_object": {"x": 1},
                 "h_nan": float("nan"), "i_inf": float("inf")}
        entry = {"gpio": [], "note": "x", "facts": {name: {"value": value, "verified": True, "source": "s"}
                                                     for name, value in facts.items()}}
        self.assertEqual(self.named(board(pin_roles={"onboard_display": entry})),
                         ["ONBOARD_DISPLAY_A_INT = 3", 'ONBOARD_DISPLAY_B_WORD = "it\'s"', "ONBOARD_DISPLAY_E_FLOAT = 1.14"])

    def test_a_fact_that_is_no_object_names_nothing(self):
        lit = board(pin_roles={"onboard_display": {"gpio": [], "note": "x", "facts": {"width": 135, "height": ["x"]}}})
        self.assertEqual(self.named(lit), [])

    def test_a_role_on_two_gpios_with_no_labels_names_no_pin_but_still_names_its_facts(self):
        two = board(pin_roles={"onboard_display": {"gpio": [2, 3], "note": "x", "active_level": 1, "facts": {
            "driver": {"value": "ST7789", "verified": True, "source": "s"}}}})
        self.assertEqual(self.named(two), ["ONBOARD_DISPLAY_DRIVER = 'ST7789'"])

    def test_a_role_with_one_gpio_and_a_label_names_the_label_not_the_bare_role(self):
        one = board(pin_roles={"onboard_button": {"gpio": [9], "note": "x", "labels": {"BOOT": 9}}})
        self.assertEqual(self.named(one), ["ONBOARD_BUTTON_BOOT = 9"])

    def test_a_control_character_or_a_lone_surrogate_in_a_comment_never_breaks_the_module(self):
        # the refuter's repro: a NUL stopped pins.py from compiling, and a lone surrogate stopped it from being written
        record = self.record()
        record["name"] = "T\x00Display"
        entry = record["pin_roles"]["onboard_display"]
        entry["note"] = "the screen\x00\x0b\x0c\ud800 on SPI"
        entry["facts"]["driver"]["source"] = "page\x00 4\ud800\x1b"
        text = assign_pins.pin_module(record, [], "r\x00.json")
        compile(text, "pins.py", "exec")
        text.encode("utf-8")
        self.assertIn("ONBOARD_DISPLAY_DRIVER = 'ST7789'  # onboard_display: driver, source: page  4  ", text)
        self.assertIn("the screen     on SPI", text)
        self.assertIn("# The pin map: written by spark's assign_pins.py from r .json\n# for the T Display. Regenerate it", text)

    def test_a_label_whose_gpio_is_no_number_is_skipped_and_the_note_goes_on_the_next(self):
        entry = {"gpio": [1, 2], "note": "the pads", "labels": {"A": "1", "B": 2, "C": True, "D": None, "E": 1}}
        lines = [line for line in self.lines(board(pin_roles={"onboard_display": entry})) if line.startswith("ONBOARD_")]
        self.assertEqual([line.split("  #")[0] for line in lines], ["ONBOARD_DISPLAY_B = 2", "ONBOARD_DISPLAY_E = 1"])
        self.assertIn("the pads", lines[0])

    def test_a_gpio_that_is_no_list_names_nothing(self):
        for gpio in (9, "9", None, {"x": 9}):
            with self.subTest(gpio=gpio):
                self.assertEqual(self.named(board(pin_roles={"onboard_led": {"gpio": gpio, "note": "x", "labels": {"A": 9}}})), [])

    def test_pin_roles_of_the_wrong_shape_name_nothing(self):
        for pin_roles in (["onboard_led"], "x", {"onboard_led": "x"}, {"onboard_led": ["gpio"]}):
            with self.subTest(pin_roles=pin_roles):
                self.assertEqual(self.named(board(pin_roles=pin_roles)), [])

    def test_a_signal_with_the_name_of_any_line_of_a_role_is_refused(self):
        for taken in ("ONBOARD_DISPLAY_CS", "ONBOARD_DISPLAY_WIDTH", "ONBOARD_BUTTON_ON", "ONBOARD_BUTTON_S2"):
            with self.subTest(taken=taken):
                assignments, _ = assign_pins.assign(board(), [{"name": taken, "needs": []}])
                with self.assertRaises(assign_pins.Impossible) as caught:
                    assign_pins.pin_module(self.record(), assignments, "r.json")
                self.assertEqual(str(caught.exception), "%s is a name pins.py gives a signal and the board's own %s: rename the signal"
                                 % (taken, "display" if "DISPLAY" in taken else "button"))

    def test_a_fact_may_not_take_the_name_of_the_pull_up_line_of_a_signal(self):
        # the refuter's repro: a signal ONBOARD_DISPLAY with a pull-up writes ONBOARD_DISPLAY_PULL, and so does a fact `pull`
        record = self.record()
        record["pin_roles"]["onboard_display"]["facts"]["pull"] = {"value": "down", "verified": True, "source": "s"}
        assignments = [{"signal": "ONBOARD_DISPLAY", "gpio": 25, "pin": "IO25", "why": "w", "roles": []}]
        with self.assertRaises(assign_pins.Impossible) as caught:
            assign_pins.pin_module(record, assignments, "r.json", pulled_up=("ONBOARD_DISPLAY",))
        self.assertIn("ONBOARD_DISPLAY_PULL is a name pins.py gives a signal", str(caught.exception))
        self.assertIn("ONBOARD_DISPLAY_PULL = 'down'", "\n".join(assign_pins.pin_module(record, assignments, "r.json").splitlines()),
                      "with no pull-up on the signal the name is free")

    def test_a_signal_with_a_name_the_record_does_not_make_is_kept(self):
        assignments, _ = assign_pins.assign(board(), [{"name": "ONBOARD_DISPLAY_MISO", "needs": []}])
        self.assertIn("ONBOARD_DISPLAY_MISO = ", "\n".join(self.lines(self.record(), assignments)))

    def test_a_record_with_bad_labels_never_reaches_the_pin_map(self):
        import json
        import tempfile
        import design
        root = Path(tempfile.mkdtemp())
        (root / ".spark").mkdir()
        (root / "boards").mkdir()
        record = self.record()
        record["pin_roles"]["onboard_display"]["labels"]["mosi"] = 19
        (root / "boards" / "lilygo-t-display.json").write_text(json.dumps(record))
        (root / "requirements.json").write_text(json.dumps({"board": "lilygo-t-display", "parts": []}))
        with self.assertRaises(design.DesignError) as caught:
            assign_pins.pin_module_for(root / "requirements.json")
        self.assertIn("has the label 'mosi'", str(caught.exception))
# --- end MVP ---


if __name__ == "__main__":
    unittest.main()
