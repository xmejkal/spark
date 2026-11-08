#!/usr/bin/env python3
"""
Turn a board definition into the footprint module its generated design imports.

    emit_footprint.py --board firebeetle2-esp32s3 -o FireBeetle2Esp32S3.tsx
    emit_footprint.py --board firebeetle2-esp32s3            # to stdout

The footprint is `spark/design/footprint_emitter.py`, which says why it sizes the hole from the pin and what it refuses
to guess. This CLI parses the arguments and prints.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from spark.core.outcomes import EXIT_OK, EXIT_PROBLEMS, EXIT_COULD_NOT_RUN, STATUS_FOR  # noqa: E402
from spark.design.footprint_emitter import (board_to_draw, hole_diameter_mm, pads, render,  # noqa: E402
                                            why_header_disagrees, why_no_footprint)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--board", required=True, help="board id, as in boards/<id>.json")
    parser.add_argument("-o", "--out", help="write here instead of stdout")
    parser.add_argument("--project", help="a project directory whose boards/ is searched first; its rules.json must hold finite numbers, none below its lowest (else exit 2)")
    parser.add_argument("--json", action="store_true", help="machine-readable result")
    args = parser.parse_args(argv)

    board, rules, refused = board_to_draw(args.project, args.board)
    if refused:
        return _report(args, EXIT_COULD_NOT_RUN, refused)

    refusal = why_no_footprint(board)
    if refusal:
        return _report(args, EXIT_COULD_NOT_RUN, refusal)

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
