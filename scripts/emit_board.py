#!/usr/bin/env python3
"""
A pin map and a module list, as a board file you can build.

    emit_board.py requirements.json > board.tsx
    emit_board.py requirements.json --project ~/my-project --board xiao-esp32-c6

The project — its parts, its rules — is the one found up from the requirements file's own
directory unless `--project` says otherwise. Where the command is typed does not matter.

The board file is `spark/design/board_emitter.py`, which says what it is honest about. This CLI parses the arguments
and prints.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from spark.core.outcomes import EXIT_OK, EXIT_COULD_NOT_RUN  # noqa: E402
from spark.design import loader  # noqa: E402
from spark.design.board_emitter import (RefusedInputError, board_file, outputs_in_contention,  # noqa: E402
                                        outputs_with_nothing_on_them, pair_sides_without_a_driver,
                                        rails_without_a_source, read_inputs)


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="emit_board.py", description="Turn a module list and a pin map into a board file.")
    parser.add_argument("requirements")
    parser.add_argument("--project")
    parser.add_argument("--board")
    parser.add_argument("--assume-missing-sizes", action="store_true",
                        help="lay out around a guessed size for any part whose outline "
                             "nobody recorded, saying so in the generated file")
    args = parser.parse_args(argv)

    try:
        inputs = read_inputs(args.requirements, args.project, args.board)
    except RefusedInputError as refused:
        print(refused, file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    design, assignments = inputs.design, inputs.assignments
    part_list = design.parts
    # Said only when the library was fallen into, not asked for: `check_spine` passes
    # `--project` to build the reference design from it on purpose, and it reads every
    # line here as a note about the design.
    if not args.project and loader.is_library(design.project):
        print(loader.LIBRARY_NOTE, file=sys.stderr)

    text, refused = board_file(inputs, args.assume_missing_sizes)
    if refused:
        print(refused, file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    sys.stdout.write(text)

    # To stderr, so it is visible even when stdout is being redirected into a file.
    placed = {entry["signal"] for entry in assignments}
    claimed = {loader.signal_name(part, need)
               for part in part_list for need in part.get("needs") or []}
    for signal in sorted(placed - claimed):
        print("note: %s was assigned a pin and no part claims it, so nothing in the emitted "
              "board connects to it" % signal, file=sys.stderr)
    for net, part_name, pin in outputs_with_nothing_on_them(part_list):
        print("note: %s.%s drives net.%s and nothing on this board receives it — add whatever it "
              "drives, or that net has one member and will not route" % (part_name, pin, net),
              file=sys.stderr)
    pair_sides = pair_sides_without_a_driver(part_list)
    for net in rails_without_a_source(part_list):
        if net in pair_sides:  # F15: what drives a side of a pair is an amplifier, and a supply into it destroys it
            print("note: nothing drives net.%s, one side of a driven pair — add what drives the pair (the amplifier this "
                  "terminal hangs off), never a supply, or that net has one member and the board will not route" % net,
                  file=sys.stderr)
            continue
        print("note: nothing sources net.%s — add whatever supplies it, or that net has one "
              "member and the board will not route" % net, file=sys.stderr)
    for net, who in outputs_in_contention(part_list):
        print("note: net.%s is driven by more than one supply (%s) — two supplies on one rail "
              "short into each other; move one to its own rail or state the arrangement"
              % (net, ", ".join(who)), file=sys.stderr)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
