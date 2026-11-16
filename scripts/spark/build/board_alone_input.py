"""
The converter's input for the board's own LED and button on a stand-in board (P484, P708): what `build_service.board_alone`
writes into `sim/` before any converter runs, and what the full build adds to its circuit with `--add-netlist` (P792). It
reads the wired parts of `onboard_parts` and their records, and writes nothing.
"""

from typing import NamedTuple, Optional

from spark.breadboard import sheet
from spark.design import loader
from spark.firmware import sim_project
from spark.records import onboard_parts
from spark.records.onboard_parts import OnboardPartReader

# --- MVP ---
#: The netlist's file name in the simulation project. The board's component name is `sheet.BOARD_COMPONENT`, the
#: name the converter's `lib/mapping.ts` matches (a test reads both).
NETLIST = "netlist.json"

#: The line a full build adds when a stand-in it gave the converter is not in the diagram (`%s`: their roles): a project's
#: own converter older than P792 ignores `--add-netlist`, and its limits then say those parts are not wired.
NOT_WIRED_BY_OLDER_CONVERTER = ("the diagram holds no stand-in for %s: a project's own converter older than P792 does "
                                "not wire the board's own LED and button")


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
    nothing and runs nothing: `build_service.board_alone` writes the files and runs the converter on the netlist.
    """
    reader = OnboardPartReader(board)
    wired = reader.parts()
    if not wired:
        alone = {"version": 1, "author": "spark", "editor": "wokwi", "connections": [],
                 "parts": [{"type": board["wokwi_part_type"], "id": "mcu", "top": 0, "left": 0, "attrs": {}}]}
        return BoardAloneResult(wired, {"diagram.json": alone}, None, "the board alone, ")
    files, why = make_converter_input(wired, reader.ground(), project)
    return BoardAloneResult(wired, files, why, "the board and its own %s, " % " and ".join(part["_instance"] for part in wired))


def make_converter_input(parts, ground, project):
    """
    The converter's input for `parts` (`OnboardPartReader.parts`) and `ground`, the board's ground pin (the reader's
    `ground`), as ({file name: JSON value}, None), or (None, why) when a part record cannot be read or lacks a fact below;
    writes nothing. NETLIST holds the board as `sheet.BOARD_COMPONENT` and each part by its role, a net from the
    GPIO's board pin to the part's signal pin (its record's first need), and one ground net from `ground` to each part's
    ground pin (its `power` entry on the ground rail). `sim_project.MAPPING_FILE` holds each part's Wokwi type, pins and
    attrs from its record's `simulation.wokwi`.
    """
    board = sheet.BOARD_COMPONENT
    components = [{"id": board, "name": board, "type": "board", "pins": []}]
    nets, mapping, grounds = [], {}, [{"componentId": board, "pinName": ground}]
    for part in parts:
        role = part["_instance"]
        try:
            record = loader.record(part["id"], project)
        except loader.DesignError as broken:
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


def wired_in(diagram, parts):
    """The `parts` (`OnboardPartReader.parts`) whose role is a part id in `diagram`: the stand-ins a converter wired."""
    ids = {part.get("id") for part in (diagram or {}).get("parts") or [] if isinstance(part, dict)}
    return [part for part in parts if part["_instance"] in ids]


class StandInsFound(NamedTuple):
    """
    Value: what a full build's diagram holds of the stand-ins it gave the converter. `ids` are their part ids, which the
    unwired check leaves out; `gpios` is `onboard_parts.say_wired_gpios`'s {gpio: sentence} for the limits; `note` is ""
    or the line NOT_WIRED_BY_OLDER_CONVERTER, for the stage's detail.
    """

    ids: set
    gpios: dict
    note: str


class OnboardStandIns:
    """
    Value: the board's own LED and button that a full build adds to its circuit (P792), as the board-only build wires
    them. Given the board record and the project; reads the parts' records once, writes nothing, runs nothing.
    """

    def __init__(self, board, project):
        self.given = read_board_alone(board, project)
        self.why = self.given.why

    def files(self, mapping):
        """{file name: JSON value} for `sim/`: `mapping` with the stand-ins' entries, and NETLIST when one is wired."""
        if not self.given.wired:
            return {sim_project.MAPPING_FILE: mapping}
        return {sim_project.MAPPING_FILE: dict(mapping, **self.given.files[sim_project.MAPPING_FILE]), NETLIST: self.given.files[NETLIST]}

    def source(self, sim_dir):
        """The converter's arguments that add the stand-ins' netlist in `sim_dir`, or [] when none is wired."""
        return ["--add-netlist", str(sim_dir / NETLIST)] if self.given.wired else []

    def found_in(self, diagram):
        """The StandInsFound of the diagram the converter wrote."""
        found = wired_in(diagram, self.given.wired)
        missing = [part["_instance"] for part in self.given.wired if part not in found]
        note = "\n           " + NOT_WIRED_BY_OLDER_CONVERTER % " and ".join(missing) if missing else ""
        return StandInsFound({part["_instance"] for part in found}, onboard_parts.say_wired_gpios(found), note)
# --- end MVP ---
