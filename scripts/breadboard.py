#!/usr/bin/env python3
"""
The breadboard sheet: from the board that was built, what to put on a breadboard and how to wire it.

    breadboard.py requirements.json                 print the sheet and write breadboard.md beside the file
    breadboard.py requirements.json --out FILE      write it there instead

Example, in a project after `/spark:build` (`check_spine.py requirements.json --keep .` writes the sheet itself):

    python3 "$CLAUDE_PLUGIN_ROOT/scripts/breadboard.py" requirements.json

What it writes, each time from scratch (it reads back only the parts you moved in breadboard.json, and
wiring-record.json, which it keeps beside the sheet):
  - the parts: the board, each part with how many, each resistor a part asks for (R1, R2, …, through-hole) and what
    it is for, and whether you have each: yours (your drawer holds it for this project), in your drawer (you own it,
    not held here), to get; blank when the project is not on your list (/spark:init puts it there);
  - the wiring (P202): numbered steps, one connection each, by the board's printed label and each part's pin and leg
    (the board and each part in first, each pin in its own row, then each wire to its point's anchor: a part's pin row,
    else a resistor end's row, else a free row for a board pin's jumper, or a rail for a point with more ends than a row
    holds); a mermaid diagram whose numbered lines are those steps; and the points, one per
    line, as the check list after wiring (spark/breadboard/wiring_steps.py holds the step rule);
  - beside the sheet, breadboard.json (P267): the steps on a Wokwi half breadboard, each jumper in its step's color,
    to paste into a new project on wokwi.com; and breadboard.svg (P268), the same layout as a picture the sheet
    shows, each part as spark's own pictogram (data/pictograms/). A part, a resistor or a jumper you moved in
    breadboard.json stays where you put it at the next build (P273, P287), if it still fits: a resistor with its
    joined pin in the row it joins, a jumper between the two rows the new layout joins (it keeps its holes and bends,
    not its color). What it cannot keep is named on stderr, with why. The XIAO ESP32-C6 is drawn on a half breadboard. A board with a
    complete record (the FireBeetle) is drawn from the record on 63 columns, as breadboard.svg alone (P412). Rails are not drawn.
    Otherwise the sheet says why, and an old drawing is removed. The code is in check_spine's kept entries and in WriteResult;
  - after a rebuild (P300), "Changes since the last build" before the steps: one line for each thing to change on
    the bench, so you do not read the whole sheet again. A line says what to put in, take out, move or swap, and names
    a jumper by its two ends and the color the earlier sheet showed. It never names holes: you pick your own free rows.
    The same lines go to stderr as `change: …`. `wiring-record.json` holds what the last sheet said, and which jumpers
    spark drew itself. Spark never names a jumper it drew itself when a new circuit leaves it out. A jumper you moved
    is named when the build cannot keep it. A first build has no such section;
  - before you power it: each part's CONFLICT lines, the pins its record says must not float, and its warnings.

It reads the built circuit (dist/board/circuit.json), the same file every check reads, so the sheet is the board that
was built. A circuit from a failed build, or from another requirements file, is refused: build again.

Exit 0: the sheet was written; 2: it could not be (nothing built, a stale or failed build, a file it cannot write).
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from spark.breadboard.sheet import CHANGE_LIST, REFUSALS, SHEET, write  # noqa: E402
from spark.core.outcomes import EXIT_OK, EXIT_COULD_NOT_RUN  # noqa: E402


def main(argv=None):
    parser = argparse.ArgumentParser(prog="breadboard.py", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("requirements", help="the project's requirements.json, after a build with --keep")
    parser.add_argument("--out", help="where to write the sheet (default: breadboard.md beside the requirements file)")
    args = parser.parse_args(argv)
    requirements = Path(args.requirements)
    out = Path(args.out) if args.out else requirements.resolve().parent / SHEET
    try:
        written = write(requirements, out)
    except REFUSALS as stopped:  # each has a code (refusal_code), library-only until an Operation writes JSON
        print("breadboard.py: could not run — %s" % stopped, file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    print(written.sheet.read_text(), end="")
    print("wrote %s" % written.sheet, file=sys.stderr)
    for path, renderer in written.drawings:
        print("wrote %s — %s" % (path, renderer.PURPOSE_MESSAGE), file=sys.stderr)
    for change in written.changes:
        print("change: %s" % CHANGE_LIST.line(change), file=sys.stderr)
    for named in written.not_kept:
        print("not kept: %s" % named.line, file=sys.stderr)
    for differs in written.differs:
        print("drawing differs: %s" % differs.why, file=sys.stderr)
    for refused in written.not_written:
        print("%s not written: %s" % (refused.renderer.FILE_NAME, refused.why), file=sys.stderr)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
