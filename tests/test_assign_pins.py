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

if __name__ == "__main__":
    unittest.main()
