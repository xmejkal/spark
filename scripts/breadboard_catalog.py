"""
What the drawn breadboard draws each component as: the catalog of a build, from the records, as `DrawnPart`s keyed by the
name the steps use, and what a planned layout says of its board. It writes no file. `breadboard.py` plans with it (P267).
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import breadboard_drawing  # noqa: E402
import breadboard_steps  # noqa: E402
import emit_board  # noqa: E402
import part_shape  # noqa: E402

#: Ohms by a resistance's suffix, for the value Wokwi's resistor takes.
OHMS = {"": 1, "k": 1000, "M": 1000000}


def to_ohms(resistance):
    """'330Ω' or '10kΩ' as Wokwi's resistor value, in ohms."""
    found = re.fullmatch(r"(\d+(?:\.\d+)?)\s*([kM]?)\s*Ω?", resistance or "")
    if not found:
        return ""
    ohms = float(found.group(1)) * OHMS[found.group(2)]
    return str(int(ohms)) if ohms == int(ohms) else str(ohms)


def describe_parts(read, geometry):
    """{component as the steps name it: how Wokwi draws it}, from the records. The board's pins come from the first
    shape source that places it (`part_shape`), or NotDrawn with a code says why none does. A board whose Wokwi pins are
    not its printed labels names no pins, so the drawing says which pin it cannot find. `geometry` must be Wokwi's own."""
    board = read.built.board
    source, _ = part_shape.find_source(board, part_shape.sources_for(geometry.data["parts"]))
    catalog = {breadboard_steps.THE_BOARD: breadboard_drawing.DrawnPart(
        board.get("wokwi_part_type") or board.get("id"), {}, source.pin_names(board))}
    for part in read.built.parts:
        wokwi = (part.get("simulation") or {}).get("wokwi") or {}
        if wokwi.get("part"):
            catalog[emit_board.component_name(part)] = breadboard_drawing.DrawnPart(
                wokwi["part"], wokwi.get("attrs") or {}, wokwi.get("pins") or {})
    for tag, value, _ in read.resistors.values():
        catalog[tag] = breadboard_drawing.DrawnPart("wokwi-resistor", {"value": to_ohms(value)}, {"1": "1", "2": "2"})
    return catalog


def board_px(layout):
    """The part_px the layout drew its board from, {} when it drew none."""
    return next((layout.geometry.part(part.type) for part in layout.parts if part.id == breadboard_steps.THE_BOARD), {})


def ground_line(layout):
    """For a board drawn from its own record, which pad every GND on this sheet is; None for any other board."""
    part_px = board_px(layout)
    if part_px.get("source") != breadboard_drawing.RECORD_SOURCE:
        return None
    return "On the board, GND is the pad %s.%s" % (
        part_px["ground"], " The pads %s are doubtful and are not used." % " and ".join(part_px["doubtful"])
        if part_px["doubtful"] else "")
