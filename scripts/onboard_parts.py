"""
Library for the board's own LED and button as wired parts of a board-only build's Wokwi diagram (P484, #663): which rows
of the board record's `pin_roles` spark wires, the netlist and mapping the converter reads for them (`--netlist`), and
the sentence each wired GPIO gives the limits. `check_spine.board_alone` calls it.
"""

from typing import NamedTuple, Optional

import boards
import breadboard
import design
import provenance
import sim_project


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
    boards.ONBOARD_LED: OnboardPart(
        "led-red-5mm", 1,
        "the Wokwi stand-in has no LED on GPIO%(gpio)d, so spark wires Wokwi's LED to GPIO%(gpio)d in its place: a passed "
        "run shows the level a scenario read on GPIO%(gpio)d, not a PWM duty or a brightness, nor that the board's own LED "
        "lights. " + boards.BENCH),
    boards.ONBOARD_BUTTON: OnboardPart(
        "tactile-button", 0,
        "the Wokwi stand-in has no button on GPIO%(gpio)d, so spark wires Wokwi's pushbutton to GPIO%(gpio)d in its "
        "place: a scenario presses that part, not the board's own button. " + boards.BENCH),
}

#: The netlist's file name in the simulation project. The board's component name is `breadboard.BOARD_COMPONENT`, the
#: name the converter's `lib/mapping.ts` matches (a test reads both).
NETLIST = "netlist.json"


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
        for role, _, entry in boards.onboard_entries(self.board):
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
        return next((name for name, number in pins.items() if boards.is_gpio(gpio) and number == gpio), None)

    def ground(self):
        """The first key of the record's `wokwi_power_pins` that names a ground pin, or None."""
        power = self.board.get("wokwi_power_pins") if isinstance(self.board.get("wokwi_power_pins"), dict) else {}
        return next((name for name in power if name.startswith(GROUND_PREFIX)), None)


#: The start of a ground pin's key in the record's `wokwi_power_pins` (the S3 devkit has no plain GND).
GROUND_PREFIX = "GND"


class BoardAloneResult(NamedTuple):
    """
    Result: what a board-only build writes into `sim/` before any converter runs. `wired` is `OnboardPartReader.parts`,
    `files` is {file name: JSON value} (the netlist and mapping when something is wired, else the diagram of the board
    alone), `why` says why a wired part cannot be given to the converter (then `files` is None), and `lead` starts the
    simulation stage's detail.
    """

    wired: list
    files: Optional[dict]
    why: Optional[str]
    lead: str


def read_board_alone(board, project):
    """
    The BoardAloneResult for a board-only build of `board`, reading the wired parts' records from `project`. Writes
    nothing and runs nothing: `check_spine.board_alone` writes the files and runs the converter on the netlist.
    """
    reader = OnboardPartReader(board)
    wired = reader.parts()
    if not wired:
        alone = {"version": 1, "author": "spark", "editor": "wokwi", "connections": [],
                 "parts": [{"type": board["wokwi_part_type"], "id": "mcu", "top": 0, "left": 0, "attrs": {}}]}
        return BoardAloneResult(wired, {"diagram.json": alone}, None, "the board alone, ")
    files, why = make_converter_input(wired, reader.ground(), project)
    return BoardAloneResult(wired, files, why, "the board and its own %s, " % " and ".join(part["_instance"] for part in wired))


def say_wired_gpios(parts):
    """{gpio: sentence} for each part `OnboardPartReader.parts` gave, the `wired` of `boards.onboard_limits`."""
    return {part["gpio"]: ONBOARD_PARTS[part["_instance"]].wired % {"gpio": part["gpio"]} for part in parts}


def make_converter_input(parts, ground, project):
    """
    The converter's input for `parts` (`OnboardPartReader.parts`) and `ground`, the board's ground pin (the reader's
    `ground`), as ({file name: JSON value}, None), or (None, why) when a part record cannot be read or lacks a fact below;
    writes nothing. NETLIST holds the board as `breadboard.BOARD_COMPONENT` and each part by its role, a net from the
    GPIO's board pin to the part's signal pin (its record's first need), and one ground net from `ground` to each part's
    ground pin (its `power` entry on the ground rail). `sim_project.MAPPING_FILE` holds each part's Wokwi type, pins and
    attrs from its record's `simulation.wokwi`.
    """
    board = breadboard.BOARD_COMPONENT
    components = [{"id": board, "name": board, "type": "board", "pins": []}]
    nets, mapping, grounds = [], {}, [{"componentId": board, "pinName": ground}]
    for part in parts:
        role = part["_instance"]
        try:
            record = design.record(part["id"], project)
        except design.DesignError as broken:
            return None, str(broken)
        signal = next((need.get("pin") for need in record.get("needs") or [] if isinstance(need, dict)), None)
        returns = next((rail.get("pin") for rail in record.get("power") or [] if isinstance(rail, dict) and rail.get("rail") == "ground"), None)
        wokwi = (record.get("simulation") or {}).get("wokwi") or {}
        if not (signal and returns and wokwi.get("part")):
            return None, "the record for %r names no signal pin, ground pin or Wokwi part, so spark cannot wire %s" % (part["id"], role)
        components.append({"id": role, "name": role, "type": part["id"], "pins": [{"name": signal, "portId": role + "." + signal},
                                                                                  {"name": returns, "portId": role + "." + returns}]})
        nets.append({"id": role, "members": [{"componentId": board, "pinName": part["pin"]}, {"componentId": role, "pinName": signal}]})
        grounds.append({"componentId": role, "pinName": returns})
        mapping[role] = {"wokwiType": wokwi["part"], "pins": wokwi.get("pins") or {}, "attrs": wokwi.get("attrs") or {}}
    netlist = {"components": components, "nets": nets + [{"id": "ground", "name": "GND", "members": grounds}]}
    return {sim_project.MAPPING_FILE: mapping, NETLIST: netlist}, None
# --- end MVP ---
