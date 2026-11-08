#!/usr/bin/env python3
"""
Does the board definition match what the vendor says, or only what somebody typed?

    check_vendor_pins.py boards/firebeetle2-esp32s3.json
    check_vendor_pins.py boards/*.json --offline      # use the cache, never the network

The check is `spark/checks/vendor_pins_check.py`, which says why it exists. This CLI parses the arguments and prints.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from spark.checks.vendor_pins_check import ARDUINO_ESP32_REPO, check_board, wrote_note  # noqa: E402
from spark.core.outcomes import EXIT_OK as EXIT_OK, EXIT_COULD_NOT_RUN as EXIT_COULD_NOT_RUN, EXIT_FOR, EXIT_PROBLEMS as EXIT_MISMATCH, status_of  # noqa: E402, F401


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="check_vendor_pins.py",
        description="Compare a board definition against the vendor's own pin header: the Arduino core's "
                    "pins_arduino.h for the variant its vendor.arduino_variant names. Without --offline it "
                    "fetches the header with the GitHub CLI gh and keeps it in .spark/cache/ of the project that "
                    "owns the board file (the nearest folder up from it holding boards/active.json or .spark/), and "
                    "a line that kept a header ends with the file it wrote. "
                    "A board spark ships is owned by spark, so a live run refreshes spark's own copy: check those "
                    "with --offline unless asked to refresh them. "
                    "A live run on a board file no project owns is refused before anything is fetched.")
    parser.add_argument("boards", nargs="+", help="board definition files")
    parser.add_argument("--offline", action="store_true",
                        help="never fetch: read the header a live run kept, the project's first, then spark's own; "
                             "could-not-run if neither has it")
    parser.add_argument("--repo", default=ARDUINO_ESP32_REPO,
                        help="the GitHub repository holding the variant headers (default: %(default)s)")
    parser.add_argument("--json", action="store_true",
                        help="a JSON list, one entry per board, for a caller that is not a person; a live run "
                             "that kept a header adds wrote, the path of that file")
    args = parser.parse_args(argv)

    results = [check_board(Path(p), args.offline, args.repo) for p in args.boards]
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for result in results:
            if result["status"] == "could-not-run":
                print("  %-24s could not run: %s%s" % (result["board"], result["reason"], wrote_note(result)))
                continue
            print("  %-24s %s  (%d pins against %s%s)"
                  % (result["board"],
                     "ok" if result["status"] == "ok" else "MISMATCH",
                     result["compared"], result["source"], wrote_note(result)))
            for problem in result.get("problems", []):
                print("      - %s" % problem)
            if result.get("not_recorded"):
                print("      note: the vendor also defines %s, which this board file does not "
                      "record" % ", ".join(result["not_recorded"]))

    # Its own word for "ran, and the answer is no" is `mismatch`; the exit code is the shared
    # rule all the same (P42). Giving every payload one shape is P43's.
    return EXIT_FOR[status_of(
        problems=[r for r in results if r["status"] == "mismatch"],
        unchecked=[r for r in results if r["status"] == "could-not-run"])]


if __name__ == "__main__":
    sys.exit(main())
