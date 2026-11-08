#!/usr/bin/env python3
"""
Everything a project needs before any check can run.

    init_project.py                        # here
    init_project.py --project ../thing --board firebeetle2-esp32s3

The library is `spark/build/project_setup.py` (P705).
"""

import argparse
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from spark.build import ai_files  # noqa: E402
import boards  # noqa: E402
from spark.records import store  # noqa: E402
from spark.build.project_setup import (NOTHING_TO_DO, PROJECT_TEMPLATE, boards_offered, design_in, find_circuit,  # noqa: E402
                                       nets_in, nulls_in, package_file, rules_for, why_board_refused,
                                       why_project_refused, write)

from spark.core.outcomes import EXIT_OK, EXIT_COULD_NOT_RUN, EXIT_PROBLEMS as EXIT_NOTHING_TO_DO  # noqa: E402


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="init_project.py",
        description="Create the files every check and reviewer needs, with nothing guessed.")
    parser.add_argument("--project", default=".", help="the project to set up (default: here)")
    parser.add_argument("--board", help="board id to make active; omit to see what is available")
    parser.add_argument("--circuit", help="a built netlist to name the rails from")
    parser.add_argument("--force", action="store_true",
                        help="work on files that exist too: merge what is derived into rules.json (answers stay), "
                             "rewrite project.json only if it has no answers, set boards/active.json when --board "
                             "names one; package.json is never rewritten")
    args = parser.parse_args(argv)

    project = Path(args.project).resolve()
    if (refused := why_project_refused(project)):
        print(refused, file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    try:
        listed = "on your projects list as %r" % store.add_project(project)
    except store.StoreProblem as refused:
        listed = "not on your projects list: %s" % refused

    circuit, ambiguous = (args.circuit, None) if args.circuit else find_circuit(project)

    nets = nets_in(circuit)
    part_list, notes = design_in(project)
    notes.append(listed)
    unstated = []
    if ambiguous:
        notes.append(ambiguous)
    written = []

    for path, payload, brief, merge in ((project / ".spark" / "rules.json", rules_for(nets, part_list), False, True),
                                 (project / ".spark" / "project.json", PROJECT_TEMPLATE, True, False)):
        did, note = write(path, payload, args.force, brief=brief, merge=merge,
                          unstated=unstated)
        notes.append(note)
        if did:
            written.append((path, payload))
    notes.append(write(project / "package.json", package_file(project), force=False)[1])
    notes.extend(unstated)
    ai_did, ai_notes = ai_files.AiFiles(project).write()
    notes.extend(ai_notes)

    if args.board:
        if (refused := why_board_refused(args.board, project)):
            print(refused, file=sys.stderr)
            return EXIT_COULD_NOT_RUN
        did, note = write(project / "boards" / "active.json",
                          {"schema": 1, "board": args.board}, args.force)
        notes.append(note)
        stop = boards.footprint_stop(args.board, project)  # F12: said where the board is chosen, never refused
        notes += ["board %s: %s" % (args.board, stop)] if stop else []

    print("spark init in %s" % project)
    for note in notes:
        print("  %s" % note)
    if circuit:
        print("  named %d rail(s) from %s" % (len(nets), Path(circuit).name))
    else:
        print("  no built design found, so the rails are empty — build, then re-run with --force")
    if not args.board:
        print("  no board chosen. Available: %s" % boards_offered(project))

    unanswered = [(path, nulls_in(payload)) for path, payload in written]
    total = sum(len(fields) for _, fields in unanswered)
    if total:
        print("\n%d field(s) nobody has answered. Nothing here is guessed, and a check reading a "
              "null\nreports it as unverifiable rather than passing it:\n" % total)
        for path, fields in unanswered:
            for field in fields:
                print("  %s  %s" % (path.name, field))

    if not written and not args.board and not ai_did:
        print(NOTHING_TO_DO)
        return EXIT_NOTHING_TO_DO
    # Part of the job could not be done, and W1 applies to this tool as much as to a check: the
    # rails are unseeded and the exit code says so, even though everything else was written.
    return EXIT_COULD_NOT_RUN if ambiguous else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
