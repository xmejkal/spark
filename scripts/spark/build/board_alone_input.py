"""
The converter's input for a board-only build (P484, P708): what `build_service.board_alone` writes into `sim/` before any
converter runs. It reads the wired parts of `onboard_parts` and their records, and writes nothing.
"""

from typing import NamedTuple, Optional

from spark.breadboard import sheet
from spark.design import loader
from spark.firmware import sim_project
from spark.records.onboard_parts import OnboardPartReader

# --- MVP ---
#: The netlist's file name in the simulation project. The board's component name is `sheet.BOARD_COMPONENT`, the
#: name the converter's `lib/mapping.ts` matches (a test reads both).
NETLIST = "netlist.json"


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
# --- end MVP ---
