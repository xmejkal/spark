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

import design  # noqa: E402
import fab  # noqa: E402
import boards  # noqa: E402
from text_guards import one_line  # noqa: E402

from outcomes import EXIT_OK, EXIT_PROBLEMS, EXIT_COULD_NOT_RUN, STATUS_FOR  # noqa: E402

#: From `data/fabrication.json` through `fab`, so a project that states a coarser process in its
#: rules file gets pads drawn for it — and so the ring this DRAWS can never drift from the ring
#: `check_footprints` demands. That relationship used to be a sentence in this comment.
HEADER_PIN_DIAGONAL_MM = fab.header_pin_diagonal_mm()
#: Kept as a module name because a test reads it; the value is the file's, not a literal.
PLATING_THICKNESS_MM = fab.process("plating_thickness_mm")


def hole_diameter_mm(rules=None):
    """The drill that admits a header pin once plating has closed in on it."""
    step = fab.process("drill_step_mm", rules)
    needed = HEADER_PIN_DIAGONAL_MM + 2 * fab.process("plating_thickness_mm", rules)
    return math.ceil(needed / step) * step


def pad_diameter_mm(hole_mm, rules=None):
    """
    The pad around that hole: the ring the board house recommends — or a project's own stricter
    minimum — plus the margin (`fab.annular_ring_to_draw_mm`). `check_footprints` fails only under
    the absolute minimum since P57; a generator drawing a new pad never aims there.

    Never a literal. This was `ANNULAR_RING_MM = 0.35` with a comment saying "check_footprints
    fails below 0.25 mm, so this carries 0.1 mm of margin" — true, and said in prose, so raising
    the checker's minimum left this drawing the old ring and emitting footprints that fail the
    check they were drawn for. The sentence is arithmetic now (backlog P46).
    """
    return round(hole_mm + 2 * fab.annular_ring_to_draw_mm(rules), 3)


def _missing(physical, header):
    """Every field this script needs and cannot derive, named individually, as (field, note) with "" for a field that needs no note."""
    gaps = []
    if not header:
        return [("physical.header", "no header geometry at all")]
    for field in ("rows", "pins", "pitch_mm", "row_spacing_mm", "first_pad_from_edge_mm"):
        if header.get(field) in (None, ""):
            gaps.append(("physical.header.%s" % field, ""))
    for field in ("width_mm", "height_mm"):
        if physical.get(field) in (None, ""):
            gaps.append(("physical.%s" % field, ""))
    if not physical.get("header_order"):
        gaps.append(("physical.header_order", "which label is on which pad — not derivable"))
    if not physical.get("footprint_export"):
        gaps.append(("physical.footprint_export", "what the module should be called"))
    return gaps


def _gaps(board):
    """`_missing` of a board; a board that is no object lacks all of it. A `physical` or a `header` that is no object is no geometry."""
    board = board if isinstance(board, dict) else {}
    physical = board.get("physical") if isinstance(board.get("physical"), dict) else {}
    header = physical.get("header")
    return _missing(physical, header if isinstance(header, dict) else None)


def footprint_gaps(board):
    """
    What a board's file lacks for its footprint to be generated (`_missing`), each as its field and its note in parentheses, or
    [] when nothing — the one rule by which this script refuses, and by which `--match`, `--audit` and `--requirements` say a
    board stops the chain at the footprint stage (C-7, P121) before anyone builds.
    """
    return ["%s (%s)" % (field, note) if note else field for field, note in _gaps(board)]


# --- MVP --- (P411) the gaps `footprint_gaps` finds are said two ways, each from the same facts: the list, for the build and
# for Claude, and the line, for a row that says where a board stops among many.
#: The line's sentence (P411): after a board's id or its row, the stage and what the board file lacks.
STOP_LINE_MESSAGE = "stops at the footprint stage (P121): its board file lacks %s"


def why_no_footprint(board):
    """The list: why no footprint can be generated for `board`, naming each gap of `footprint_gaps` with its note, or None when
    one can. The sentence of this refusal for this script, `emit_board` and the spine's footprint stage, and the `stops_why` of
    a `--match` candidate and an `--audit` row."""
    gaps = footprint_gaps(board)
    if not gaps:
        return None
    return ("%s cannot have a footprint generated — these are not recorded, and none of them can be derived from the "
            "rest:\n  %s" % (board.get("id") if isinstance(board, dict) else None, "\n  ".join(gaps)))


def footprint_stop_line(board):
    """The line: one sentence for a row in a list, with no id (the row puts its own first) and no notes — the field when one
    is missing, else how many and the first — or None when a footprint can be generated. `why_no_footprint` has the list."""
    fields = [field for field, _ in _gaps(board)]
    if not fields:
        return None
    return STOP_LINE_MESSAGE % (fields[0] if len(fields) == 1 else "%d fields (first: %s)" % (len(fields), fields[0]))


#: What a board whose header geometry and pad order do not fit each other is told (P411): `main` and the spine's footprint stage.
DISAGREES_MESSAGE = "the board definition disagrees with itself: %s"


def _wrong_kind(physical):
    """The first field of a complete board file that holds a value of the wrong kind, said with its name, or None. The board
    file's validation checks no header geometry, so `pads` and `render` would raise a TypeError on a pitch written as text."""
    header = physical["header"]
    numbers = [("physical.%s" % field, physical[field]) for field in ("width_mm", "height_mm")] + [
        ("physical.header.%s" % field, header[field]) for field in ("pitch_mm", "row_spacing_mm", "first_pad_from_edge_mm")]
    for name, value in numbers:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return "%s is not a number" % name
    pins, order = header["pins"], physical["header_order"]
    if not isinstance(pins, list) or not all(isinstance(count, int) and not isinstance(count, bool) for count in pins):
        return "physical.header.pins is not a list of whole numbers"
    if not isinstance(order, dict) or not all(isinstance(labels, list) for key, labels in order.items() if not key.startswith("//")):
        return "physical.header_order is not an object with a list of labels for each row"
    return None


def why_header_disagrees(board, rules=None):
    """
    Why the footprint of `board` cannot be drawn although nothing is missing, or None when it can (or when something is
    missing: `why_no_footprint` says that): a value of the wrong kind, which is named, or a pad order that does not fit the
    pin counts.
    """
    if footprint_gaps(board):
        return None
    wrong = _wrong_kind(board["physical"])
    if wrong:
        return DISAGREES_MESSAGE % wrong
    try:
        render(board, rules)
    except (ValueError, KeyError, TypeError) as exc:  # TypeError: a project's rules value of the wrong kind reaches it until P434 (#576) checks rules values
        return DISAGREES_MESSAGE % exc
    return None


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


def render(board, rules=None):
    """The footprint module, as TSX, sized for the process the project states."""
    physical = board["physical"]
    export = physical["footprint_export"]
    hole = hole_diameter_mm(rules)
    pad = pad_diameter_mm(hole, rules)
    half_w = physical["width_mm"] / 2.0
    half_h = physical["height_mm"] / 2.0

    lines = [
        "// Generated by spark's emit_footprint.py from boards/%s.json — do not hand-edit."
        % one_line(board["id"]),
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
        # P87's attribute half: a label no pin names is held to no name rule (the FireBeetle's D- and D+ are none), so it
        # is written as a string literal, escaped — a quote in it cannot end the string, and RX is written "RX" as before
        lines.append(
            '      <platedhole portHints={[%s]} pcbX="%gmm" pcbY="%gmm" '
            'outerDiameter="%gmm" holeDiameter="%gmm" shape="circle" />' % (json.dumps(label), x, y, pad, hole))
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

    # Resolving the project has to sit INSIDE the guard. It raises when there is no project
    # around, and outside the try that escaped `main` as a traceback — so a caller asking for an
    # exit code got an exception instead, and whoever called it reported the crash as a verdict.
    try:
        project = Path(args.project) if args.project else boards.project_or_library()
        board = boards.load(project, args.board)
    except Exception as exc:  # noqa: BLE001 — the message is the product
        return _report(args, EXIT_COULD_NOT_RUN, "no board to generate from: %s" % exc)

    refusal = why_no_footprint(board)
    if refusal:
        return _report(args, EXIT_COULD_NOT_RUN, refusal)

    rules = design.rules_in(project)
    disagreement = why_header_disagrees(board, rules)
    if disagreement:
        return _report(args, EXIT_PROBLEMS, disagreement)
    text = render(board, rules)

    if args.out:
        Path(args.out).write_text(text)
        return _report(args, EXIT_OK, "wrote %s (%d pads, %.2f mm holes)"
                       % (args.out, len(pads(board)), hole_diameter_mm(rules)))
    sys.stdout.write(text)
    return EXIT_OK


def _report(args, code, message):
    status = STATUS_FOR[code]
    if args.json:
        print(json.dumps({"check": "emit-footprint", "status": status, "message": message}))
    else:
        print(message if code == EXIT_OK else "%s: %s" % (status, message), file=sys.stderr)
    return code


if __name__ == "__main__":
    sys.exit(main())
