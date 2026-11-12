"""
Library for the board's own LED and button as wired parts of a board-only build's Wokwi diagram (P484, #663): which rows
of the board record's `pin_roles` spark wires, and the sentence each wired GPIO gives the limits. The build area reads it:
`board_alone_input` makes the converter's input from these parts. `limits_of_board` is what a passed run does not test
of the board's own parts, the one answer the pick, the build and the look give (P778).
"""

from typing import NamedTuple

from spark.records import board_records
from spark.records import provenance


# --- MVP ---
class OnboardPart(NamedTuple):
    """
    Value: the part record that stands in for one onboard role in the diagram, the `active_level` its record's wiring
    gives (signal pin to the GPIO, ground pin to ground), and the limit sentence for its wired GPIO (`%(gpio)d`).
    """

    record: str
    level: int
    wired: str


#: The roles spark wires, each with its stand-in part. Only roles with a scenario verb (a test pins it): the display and
#: the battery-level pin keep their `not_in_diagram` sentence.
ONBOARD_PARTS = {
    board_records.ONBOARD_LED: OnboardPart(
        "led-red-5mm", 1,
        "the Wokwi stand-in has no LED on GPIO%(gpio)d, so spark wires Wokwi's LED to GPIO%(gpio)d in its place: a passed "
        "run shows the level a scenario read on GPIO%(gpio)d, not a PWM duty or a brightness, nor that the board's own LED "
        "lights. " + board_records.BENCH),
    board_records.ONBOARD_BUTTON: OnboardPart(
        "tactile-button", 0,
        "the Wokwi stand-in has no button on GPIO%(gpio)d, so spark wires Wokwi's pushbutton to GPIO%(gpio)d in its "
        "place: a scenario presses that part, not the board's own button. " + board_records.BENCH),
}


class OnboardPartReader:
    """
    Value: the board's own parts that spark wires into a board-only build's Wokwi diagram, from the board record alone.
    Given the record; reads no file, writes nothing, never raises. Only a stand-in board (`wokwi_is_stand_in`) gets them:
    spark's record then says the Wokwi part is another board's, so the board's own LED and button are absent from it. For
    any other board spark's records do not say the Wokwi part lacks them, so nothing is wired.
    """

    def __init__(self, board):
        self.board = board if isinstance(board, dict) else {}

    def parts(self):
        """
        One {"id", "onboard", "_instance", "gpio", "pin"} per role of ONBOARD_PARTS whose row names one GPIO, a pin
        of the record's `pins` (`pin`, the key the converter wires), at the level its part is wired for (an LED that a 1
        lights, a button that reads 0 when pressed); in table order. `id` is the part record, `onboard` the board's id,
        `_instance` the role (the diagram's part id). [] for a board that is no stand-in or names no ground pin.
        """
        if self.board.get("wokwi_is_stand_in") is not True or not self.ground():
            return []
        found = []
        for role, _, entry in board_records.onboard_entries(self.board):
            part, gpios = ONBOARD_PARTS.get(role), entry.get("gpio")
            if not part or not isinstance(gpios, list) or len(gpios) != 1:
                continue
            level, pin = provenance.read_value(entry, "active_level"), self.pin_of(gpios[0])
            if pin and type(level) is int and level == part.level:
                found.append({"id": part.record, "onboard": self.board.get("id"), "_instance": role, "gpio": gpios[0], "pin": pin})
        return found

    def pin_of(self, gpio):
        """The first key of the record's `pins` whose GPIO is `gpio`, or None."""
        pins = self.board.get("pins") if isinstance(self.board.get("pins"), dict) else {}
        return next((name for name, number in pins.items() if board_records.is_gpio(gpio) and number == gpio), None)

    def ground(self):
        """The first key of the record's `wokwi_power_pins` that names a ground pin, or None."""
        power = self.board.get("wokwi_power_pins") if isinstance(self.board.get("wokwi_power_pins"), dict) else {}
        return next((name for name in power if name.startswith(GROUND_PREFIX)), None)


#: The start of a ground pin's key in the record's `wokwi_power_pins` (the S3 devkit has no plain GND).
GROUND_PREFIX = "GND"


def say_wired_gpios(parts):
    """{gpio: sentence} for each part `OnboardPartReader.parts` gave, the `wired` of `board_records.onboard_limits`."""
    return {part["gpio"]: ONBOARD_PARTS[part["_instance"]].wired % {"gpio": part["gpio"]} for part in parts}


def limits_of_board(board, roles, wired, definitions=None, key=None):
    """
    What a passed run does not test of the board's own parts, for the pick, the build and the look alike (P778):
    `board_records.role_limits`, {role: [(component, sentence)]}, when `roles` is a list, else `board_records.onboard_limits`,
    the pairs of every role. `wired` is {gpio: sentence} for the GPIOs spark wires in the diagram (`say_wired_gpios`), or
    None for those `OnboardPartReader` gives this board. `definitions` and `key` are `role_limits`'s memo. It reads the
    board's Wokwi definition from the store and nothing else, and never raises.
    """
    if wired is None:
        wired = say_wired_gpios(OnboardPartReader(board).parts())
    if roles is not None:
        return board_records.role_limits(board, roles, definitions, key, wired)
    return board_records.onboard_limits(board, wired)


# --- end MVP ---
