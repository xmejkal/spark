#!/usr/bin/env python3
"""
Which board this project is built around — resolved in one place, and checked against a contract.

    python3 scripts/boards.py --path        the active board's definition file
    python3 scripts/boards.py --id          the active board's id
    python3 scripts/boards.py --list        every board available to switch to
    python3 scripts/boards.py --paths       their file paths, for tools that take a list
    python3 scripts/boards.py --get chip    one field, by dotted path
    python3 scripts/boards.py --validate    check every board file against the contract
    python3 scripts/boards.py --validate --for-fab
                                            also require what the PCB needs, not just the firmware

The command `/spark:init`, `/spark:build` and the review skill call. The library is `spark/records/board_records.py`
(P718), and `--list` says each board that stops at the footprint by `footprint_emitter.footprint_stop`, read lazily.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from spark.core.outcomes import EXIT_OK, EXIT_PROBLEMS as EXIT_INVALID  # noqa: E402
from spark.records import board_records  # noqa: E402
from spark.records.board_records import (BoardError, _read_json, active_id, available, definition_path,  # noqa: E402
                                         get, project_or_library, project_root, resolve, validate)


def _footprint_stop(board_id: str, project: Path) -> str:
    """`footprint_emitter.footprint_stop`, imported here as before the move: only `--list` needs the design area, which
    loads the parts library and the fabrication data, so `--id`, `--path` and `--get` do not."""
    from spark.design import footprint_emitter
    return footprint_emitter.footprint_stop(board_id, project)


def _validate_all(project: Path, for_fab: bool) -> int:
    """Check every board file, not just the active one, and say what is wrong with each."""
    failed = False
    for board_id in available(project):
        path = definition_path(project, board_id)
        try:
            board = _read_json(path, "board definition")
        except BoardError as broken:
            print(f"  {board_id}: {broken}")
            failed = True
            continue
        problems = validate(board, path, for_fab=for_fab)
        marker = "active" if board_id == active_id(project) else "     "
        where = "library" if path.parent == board_records.LIBRARY else "project"
        if problems:
            print(f"  {marker}  {board_id} ({where}): {len(problems)} problem(s)")
            for problem in problems:
                print(f"           - {problem}")
            failed = True
        else:
            print(f"  {marker}  {board_id} ({where}): ok")
    return EXIT_INVALID if failed else EXIT_OK


def main(argv=None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        prog="boards.py", description="Resolve and check the project's board definitions.")
    what = parser.add_mutually_exclusive_group(required=True)
    what.add_argument("--path", action="store_true", help="the active board's definition file")
    what.add_argument("--id", action="store_true", help="the active board's id")
    what.add_argument("--list", action="store_true", help="every board available to switch to")
    what.add_argument("--paths", action="store_true",
                      help="every board definition file, for tools that take a list")
    what.add_argument("--validate", action="store_true", help="check every board file")
    what.add_argument("--get", metavar="KEY.PATH",
                      help="one field from the active board, e.g. chip or physical.width_mm")
    what.add_argument("--resolve", action="store_true",
                      help="write the validated active board to .spark/board.json")
    parser.add_argument("--for-fab", action="store_true",
                        help="with --validate, also require what the PCB needs")
    parser.add_argument("--project", help="the project to act on (default: found upwards)")
    args = parser.parse_args(argv)

    try:
        # Reading modes may fall back to the plugin's library; the one writing mode may not.
        project = (Path(args.project).resolve() if args.project
                   else project_root() if args.resolve else project_or_library())
        if args.path:
            print(definition_path(project))
        elif args.resolve:
            print(resolve(project))
        elif args.id:
            print(active_id(project))
        elif args.paths:
            # Deliberately not `boards/*.json`: that glob also matches active.json, which is a
            # selection rather than a board. Everything that needs the list should ask here.
            print(" ".join(str(definition_path(project, b)) for b in available(project)))
        elif args.get:
            print(get(project, args.get))
        elif args.list:
            try:
                current = active_id(project)
            except BoardError:
                current = None          # nothing chosen — the library, or a project before init
            for board_id in available(project):
                where = "library" if definition_path(project, board_id).parent == board_records.LIBRARY \
                    else "project"
                stop = _footprint_stop(board_id, project)
                print(f"  {'*' if board_id == current else ' '} {board_id} ({where}){' ' + stop if stop else ''}")
        else:
            return _validate_all(project, for_fab=args.for_fab)
    except BoardError as broken:
        print(f"boards.py: {broken}", file=sys.stderr)
        return EXIT_INVALID
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
