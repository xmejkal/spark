#!/usr/bin/env python3
"""
Everything a project needs before any check can run.

    init_project.py                        # here
    init_project.py --project ../thing --board firebeetle2-esp32s3
    init_project.py --project . --answers answers.json   # the brief's answers, in the person's words

The library is `spark/build/project_setup.py` (P705).
"""

import argparse
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from spark.build import ai_files  # noqa: E402
from spark.design import footprint_emitter  # noqa: E402
from spark.records import store  # noqa: E402
from spark.build.project_setup import (NOTHING_TO_DO, PROJECT_TEMPLATE, answers_in, boards_offered, design_in,  # noqa: E402
                                       find_circuit, nets_in, package_file, rules_for, unanswered_fields,
                                       why_board_refused, why_project_refused, write, write_brief)

from spark.core.outcomes import EXIT_OK, EXIT_COULD_NOT_RUN, EXIT_PROBLEMS as EXIT_NOTHING_TO_DO  # noqa: E402
from spark.core.result import Refusal  # noqa: E402


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
    parser.add_argument("--answers", metavar="FILE",
                        help="a JSON object with the brief's answers in the person's words — goal, must, prefer, sellers, "
                             "decided — merged into project.json: what it states wins, what it leaves out is kept, and a "
                             "null un-answers nothing")
    args = parser.parse_args(argv)

    project = Path(args.project).resolve()
    if (refused := why_project_refused(project)):
        print(refused, file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    try:
        listed = "on your projects list as %r" % store.add_project(project)
    except store.StoreError as refused:
        listed = "not on your projects list: %s" % refused
    brief_path = project / ".spark" / "project.json"
    answers = answers_in(Path(args.answers), brief_path) if args.answers else None
    if isinstance(answers, Refusal):
        print(answers, file=sys.stderr)
        return EXIT_COULD_NOT_RUN

    circuit, ambiguous = (args.circuit, None) if args.circuit else find_circuit(project)

    nets = nets_in(circuit)
    part_list, notes = design_in(project)
    notes.append(listed)
    unstated = []
    if ambiguous:
        notes.append(ambiguous)
    written = []

    for path, payload, brief, merge in ((project / ".spark" / "rules.json", rules_for(nets, part_list), False, True),
                                 (brief_path, PROJECT_TEMPLATE, True, False)):
        if brief and answers is not None:
            did, note = write_brief(path, answers, Path(args.answers).name)
        else:
            did, note = write(path, payload, args.force, brief=brief, merge=merge, unstated=unstated)
        notes.append(note)
        if did:
            written.append(path)
    notes.append(write(project / "package.json", package_file(project), force=False)[1])
    notes.extend(unstated)
    unanswered, unread = unanswered_fields(project)
    notes.extend(unread)
    ai_did, ai_notes = ai_files.AiFiles(project).write()
    notes.extend(ai_notes)

    if args.board:
        if (refused := why_board_refused(args.board, project)):
            print(refused, file=sys.stderr)
            return EXIT_COULD_NOT_RUN
        did, note = write(project / "boards" / "active.json",
                          {"schema": 1, "board": args.board}, args.force)
        notes.append(note)
        stop = footprint_emitter.footprint_stop(args.board, project)  # F12: said where a board is chosen, never refused
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

    if unanswered:
        print("\n%d field(s) nobody has answered. Nothing here is guessed, and a check reading a "
              "null\nreports it as unverifiable rather than passing it:\n" % len(unanswered))
        for name, field in unanswered:
            print("  %s  %s" % (name, field))

    if not written and not args.board and not ai_did:
        print(NOTHING_TO_DO)
        return EXIT_NOTHING_TO_DO
    # Part of the job could not be done, and W1 applies to this tool as much as to a check: the
    # rails are unseeded and the exit code says so, even though everything else was written.
    return EXIT_COULD_NOT_RUN if ambiguous else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
