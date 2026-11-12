#!/usr/bin/env python3
"""
A pin map and a module list, as a board file you can build.

    emit_board.py requirements.json > board.tsx
    emit_board.py requirements.json --project ~/my-project --board xiao-esp32-c6

The project — its parts, its rules — is the one found up from the requirements file's own
directory unless `--project` says otherwise. Where the command is typed does not matter.

The board file is `spark/design/board_emitter.py`, which says what it is honest about: this CLI parses the arguments and
prints what its `BoardEmitter` reads, emits and notes, as the build does in process (P706).
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from spark.core.outcomes import EXIT_OK, EXIT_COULD_NOT_RUN  # noqa: E402
from spark.design import loader  # noqa: E402
from spark.design.board_emitter import BoardEmitter, RefusedInputError  # noqa: E402


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
    emitter = BoardEmitter(args.assume_missing_sizes)

    try:
        inputs = emitter.read(args.requirements, args.project, args.board)
    except RefusedInputError as refused:
        print(refused, file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    # Said only when the library was fallen into, not asked for: `check_spine` passes
    # `--project` to build the reference design from it on purpose, and it reads every
    # line here as a note about the design.
    if not args.project and loader.is_library(inputs.design.project):
        print(loader.LIBRARY_NOTE, file=sys.stderr)

    text, refused = emitter.emit(inputs)
    if refused:
        print(refused, file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    sys.stdout.write(text)
    # To stderr, so the notes are visible even when stdout is being redirected into a file.
    for note in emitter.notes(inputs):
        print(note, file=sys.stderr)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
