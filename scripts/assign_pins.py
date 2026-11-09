#!/usr/bin/env python3
"""
Which pin should each signal go on, and why?

    assign_pins.py requirements.json
    assign_pins.py requirements.json --board firebeetle2-esp32s3 --json

The pin assignment is `spark/design/pin_assigner.py`, which says why it spends the scarce pins last. This CLI parses
the arguments and prints.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from spark.sourcing import part_facts  # noqa: E402
from spark.core.outcomes import EXIT_OK, EXIT_COULD_NOT_RUN, EXIT_PROBLEMS as EXIT_IMPOSSIBLE  # noqa: E402
from spark.design import loader  # noqa: E402
from spark.design.pin_assigner import ImpossibleError, assign, pin_module, pulled_up, render  # noqa: E402


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="assign_pins.py",
        description="Work out which pin each signal should go on, and say why.")
    parser.add_argument("requirements", help="the requirements file (a board and a list of parts)")
    parser.add_argument("--board", help="board id (default: the project's active board)")
    parser.add_argument("--project", help="the project to resolve the board from")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--emit-pins", metavar="FILE",
                        help="also write the map as a module the firmware imports (P36), with ONBOARD_LED, ONBOARD_BUTTON and ONBOARD_BATTERY_SENSE for a part on one pin, ONBOARD_<PART>_<LABEL> per label (ONBOARD_BUTTON_S1), ONBOARD_<PART>_<FACT> per fact (ONBOARD_DISPLAY_WIDTH) and the _ON levels, when the board record names them")
    args = parser.parse_args(argv)

    # One loader for the whole chain (`spark/design/loader.py`): the project is the requirements FILE's, the
    # parts are instances, and the signals are derived once and named per instance — the same
    # list `emit_board` traces. This used to read the JSON outside any try, resolve the project
    # from the current directory, and hand the raw `parts` entries to the library, so the first
    # step every document names crashed on the `{part, name}` form every document shows (B1).
    try:
        loaded = loader.load(args.requirements, args.project, args.board)
    except loader.DesignError as broken:
        print("could not load the design: %s" % broken)
        return EXIT_COULD_NOT_RUN
    board = loaded.board
    if not args.project and loader.is_library(loaded.project):
        print(loader.LIBRARY_NOTE)

    try:
        assignments, leftover = assign(board, loaded.signals)
    except ImpossibleError as refused:
        print("cannot place every signal on this board:\n\n  %s" % refused)
        return EXIT_IMPOSSIBLE

    if args.emit_pins:
        try:
            module = pin_module(board, assignments, Path(args.requirements).name, pulled_up(loaded.parts))
        except ImpossibleError as refused:
            print("cannot write the pin map:\n\n  %s" % refused)
            return EXIT_IMPOSSIBLE
        target = Path(args.emit_pins)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(module)

    # Whatever the parts do not know about themselves travels with the answer. A pin map that
    # looks complete while resting on unmeasured numbers is the thing this plugin exists to stop.
    open_questions = part_facts.unverified(
        list(dict.fromkeys(part["id"] for part in loaded.parts)), loaded.project)

    if args.json:
        print(json.dumps({"tool": "assign_pins", "board": board["id"],
                          "unverified": open_questions,
                          "assignments": assignments,
                          "free": [{"pin": label, **pin} | {"can": sorted(pin["can"])}
                                   for label, pin in leftover.items()]}, indent=2))
    else:
        print(render(board, assignments, leftover))
        if open_questions:
            print("\n  still unverified about these parts:")
            for question in open_questions:
                print("    %s.%s" % (question["part"], question["fact"]))
                if question["why_it_matters"]:
                    print("      %s" % question["why_it_matters"])
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
