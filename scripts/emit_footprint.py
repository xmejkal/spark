#!/usr/bin/env python3
"""
Turn a board definition into the footprint module its generated design imports.

WHY THIS EXISTS

`emit_board.py` writes `import { FireBeetle2Esp32S3 } from "./FireBeetle2Esp32S3"` and the plugin
ships zero such modules, so its output has never built. Everything downstream of the schematic —
the checks, the netlist, the simulation — was unreachable behind one missing file.

The facts needed to write that file were already in the board definition, precise to 0.01 mm. All
but two: which silkscreen label sits on which pad, and how far the first pad is from the edge.
Both were prose in a comment. Both are now data, which is what made this script possible.

THE ONE NUMBER THIS SCRIPT REFUSES TO COPY

The board file records `drill_mm: 0.9`. That is the vendor's finished hole for the vendor's own
obround pad, and it is the wrong number for a hole that has to *accept* their pin. A 2.54 mm
header pin is 0.64 mm square — 0.905 mm across the diagonal, which is the dimension that has to
fit — and plating grows inward, so a 0.9 mm drill finishes near 0.84 mm. Thirty-two holes that
each need reaming is a scrapped board.

So the hole is sized from the pin, never from the vendor's drawing. `check_footprints.py` in this
same plugin rejects 0.9 mm; a generator that emitted it would be producing boards its own checker
refuses.

WHAT IT REFUSES TO GUESS

A board with no header geometry, no pad order, or a pad order whose length disagrees with the pin
count gets a refusal naming the missing field. It does not invent a pinout: four different
VL6180X breakouts exist with four different pinouts, and the same is true of dev boards. A
footprint that is silently wrong is worse than none, because the board builds and the error
surfaces at assembly.

    emit_footprint.py --board firebeetle2-esp32s3 -o FireBeetle2Esp32S3.tsx
    emit_footprint.py --board firebeetle2-esp32s3            # to stdout
"""

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import boards  # noqa: E402

EXIT_OK, EXIT_PROBLEMS, EXIT_COULD_NOT_RUN = 0, 1, 2

#: A standard 0.64 mm square header pin, across the diagonal. The pin is sold by its side, so the
#: diagonal is the dimension people forget, and it is the only one that has to fit.
HEADER_PIN_SIDE_MM = 0.64
HEADER_PIN_DIAGONAL_MM = HEADER_PIN_SIDE_MM * math.sqrt(2)

#: Plating grows into the hole from every side, so a finished hole is smaller than its drill.
PLATING_THICKNESS_MM = 0.03

#: Copper left around the hole. `check_footprints` fails below 0.25 mm; sitting exactly on a
#: minimum means any tolerance in drill placement breaks out of the pad, so this carries 0.1 mm
#: of margin. It also reproduces the 1.7 mm pad on the hand-checked reference footprint.
ANNULAR_RING_MM = 0.35

#: Drills come in steps. Rounding up is the safe direction: a hole slightly too big still seats.
DRILL_STEP_MM = 0.1


def hole_diameter_mm():
    """The drill that admits a header pin once plating has closed in on it."""
    needed = HEADER_PIN_DIAGONAL_MM + 2 * PLATING_THICKNESS_MM
    return math.ceil(needed / DRILL_STEP_MM) * DRILL_STEP_MM


def pad_diameter_mm(hole_mm):
    return round(hole_mm + 2 * ANNULAR_RING_MM, 3)


def _missing(physical, header):
    """Every field this script needs and cannot derive, named individually."""
    gaps = []
    if not header:
        return ["physical.header (no header geometry at all)"]
    for field in ("rows", "pins", "pitch_mm", "row_spacing_mm", "first_pad_from_edge_mm"):
        if header.get(field) in (None, ""):
            gaps.append("physical.header.%s" % field)
    for field in ("width_mm", "height_mm"):
        if physical.get(field) in (None, ""):
            gaps.append("physical.%s" % field)
    if not physical.get("header_order"):
        gaps.append("physical.header_order (which label is on which pad — not derivable)")
    if not physical.get("footprint_export"):
        gaps.append("physical.footprint_export (what the module should be called)")
    return gaps


def pads(board):
    """
    Every header pad, as (label, x, y), in the order the board file lists them.

    Both rows are flush at one edge and run away from it, which is the only alignment this
    handles; a board whose rows are centred or staggered differently is a refusal, not a guess.
    """
    physical = board.get("physical") or {}
    header = physical.get("header") or {}
    order = physical.get("header_order") or {}

    pitch = header["pitch_mm"]
    half_spacing = header["row_spacing_mm"] / 2.0
    first_y = physical["height_mm"] / 2.0 - header["first_pad_from_edge_mm"]

    counts = header["pins"]
    row_keys = [key for key in order if not key.startswith("//")]
    if len(row_keys) != len(counts):
        raise ValueError(
            "physical.header.pins lists %d rows and header_order has %d (%s)"
            % (len(counts), len(row_keys), ", ".join(row_keys)))

    placed = []
    for index, (key, expected) in enumerate(zip(row_keys, counts)):
        labels = order[key]
        if len(labels) != expected:
            raise ValueError(
                "header_order.%s has %d labels but physical.header.pins says %d — one of the two "
                "is wrong, and guessing which would shift every pad after the disagreement"
                % (key, len(labels), expected))
        # Row 0 is the -x side. Rows run away from the flush edge, so y decreases.
        x = -half_spacing if index == 0 else half_spacing
        for position, label in enumerate(labels):
            placed.append((label, x, round(first_y - position * pitch, 4)))
    return placed


def render(board):
    """The footprint module, as TSX."""
    physical = board["physical"]
    export = physical["footprint_export"]
    hole = hole_diameter_mm()
    pad = pad_diameter_mm(hole)
    half_w = physical["width_mm"] / 2.0
    half_h = physical["height_mm"] / 2.0

    lines = [
        "// Generated by spark's emit_footprint.py from boards/%s.json — do not hand-edit."
        % board["id"],
        "//",
        "// The holes are %.2f mm, NOT the %s mm on the vendor drawing. That figure is their"
        % (hole, physical["header"].get("drill_mm", "?")),
        "// finished hole for their own pad; this one has to admit a 0.64 mm square header pin,",
        "// which is %.3f mm across the diagonal before plating closes in on it."
        % HEADER_PIN_DIAGONAL_MM,
        "",
        'import { type ChipProps } from "tscircuit"',
        "",
        "export const %s = (props: ChipProps) => (" % export,
        "  <chip",
        "    footprint={<footprint>",
    ]
    for label, x, y in pads(board):
        lines.append(
            '      <platedhole portHints={["%s"]} pcbX="%gmm" pcbY="%gmm" '
            'outerDiameter="%gmm" holeDiameter="%gmm" shape="circle" />' % (label, x, y, pad, hole))
    for (x1, y1), (x2, y2) in zip(
            [(-half_w, half_h), (half_w, half_h), (half_w, -half_h), (-half_w, -half_h)],
            [(half_w, half_h), (half_w, -half_h), (-half_w, -half_h), (-half_w, half_h)]):
        lines.append('      <silkscreenpath route={[{"x":%g,"y":%g},{"x":%g,"y":%g}]} />'
                     % (x1, y1, x2, y2))
    lines += [
        "    </footprint>}",
        "    {...props}",
        "  />",
        ")",
        "",
    ]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--board", required=True, help="board id, as in boards/<id>.json")
    parser.add_argument("-o", "--out", help="write here instead of stdout")
    parser.add_argument("--project", help="a project directory whose boards/ is searched first")
    parser.add_argument("--json", action="store_true", help="machine-readable result")
    args = parser.parse_args(argv)

    project = Path(args.project) if args.project else boards.project_root()
    try:
        board = boards.load(project, args.board)
    except Exception as exc:  # noqa: BLE001 — the message is the product
        return _report(args, EXIT_COULD_NOT_RUN, "no such board: %s" % exc)

    physical = board.get("physical") or {}
    gaps = _missing(physical, physical.get("header"))
    if gaps:
        return _report(
            args, EXIT_COULD_NOT_RUN,
            "%s cannot have a footprint generated — these are not recorded, and none of them "
            "can be derived from the rest:\n  %s" % (args.board, "\n  ".join(gaps)))

    try:
        text = render(board)
    except (ValueError, KeyError) as exc:
        return _report(args, EXIT_PROBLEMS, "the board definition disagrees with itself: %s" % exc)

    if args.out:
        Path(args.out).write_text(text)
        return _report(args, EXIT_OK, "wrote %s (%d pads, %.2f mm holes)"
                       % (args.out, len(pads(board)), hole_diameter_mm()))
    sys.stdout.write(text)
    return EXIT_OK


def _report(args, code, message):
    status = {EXIT_OK: "ok", EXIT_PROBLEMS: "problems", EXIT_COULD_NOT_RUN: "could-not-run"}[code]
    if args.json:
        print(json.dumps({"check": "emit-footprint", "status": status, "message": message}))
    else:
        print(message if code == EXIT_OK else "%s: %s" % (status, message), file=sys.stderr)
    return code


if __name__ == "__main__":
    sys.exit(main())
