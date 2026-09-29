#!/usr/bin/env python3
"""
Does the board definition match what the vendor says, or only what somebody typed?

    check_vendor_pins.py boards/firebeetle2-esp32s3.json
    check_vendor_pins.py boards/*.json --offline      # use the cache, never the network

A board definition is a transcription. Someone read a pinout, or a header file, or a picture,
and typed numbers into JSON. Every check downstream then compares other things TO that file, so
a transcription error is invisible: the firmware, the PCB and the simulator all agree, and all
three are wrong together.

This is the only check that looks outside the project. It re-derives the silkscreen-to-GPIO map
from the vendor's own Arduino variant header and compares it to the board file.

WHY THE ARDUINO HEADER, AND NOT THE PINOUT DIAGRAM
Because it is machine-readable and it is what a toolchain compiles against. Pinout diagrams are
drawn for marketing and are rasterised; on the project this came from, two header pads were read
off a vendor's board render as "NC" and were in fact GROUND — a mistake that survived every
other check, because those checks all read the same wrong file.

WHAT IT DOES WHEN IT CANNOT REACH THE VENDOR
It fails. A verification tool that silently degrades to "no news is good news" the moment a
network call fails is worse than no tool, because it still prints a tick. `--offline` uses a
cached copy and says so, and an absent cache is an error, not a pass.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from outcomes import EXIT_OK, EXIT_COULD_NOT_RUN, EXIT_PROBLEMS as EXIT_MISMATCH  # noqa: E402

#: Where the vendor's own header lives. Only Espressif's Arduino core is understood today; a
#: board from another vendor would need its own fetcher, which is why this is a named constant
#: and not a formatted string buried in a function.
ARDUINO_ESP32_REPO = "espressif/arduino-esp32"
VARIANT_PATH = "variants/%s/pins_arduino.h"

#: `static const uint8_t D9 = 0;` — the form the variant headers use for pin aliases.
PIN_DEFINITION = re.compile(
    r"^\s*static\s+const\s+uint8_t\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(\d+)\s*;", re.M)

#: Names in the header that are not silkscreen labels: touch-sensor aliases, bus roles that the
#: board may or may not print, and build-system leftovers. Compared only if the board file also
#: lists them.
NOT_A_SILKSCREEN_LABEL = re.compile(r"^(T\d+|LED_BUILTIN|BUILTIN_LED|RGB_BUILTIN|.*_PIN)$")

CACHE_DIR = ".spark/cache"


def fetch_variant_header(variant: str, repo: str) -> str:
    """The vendor's header, via `gh` so it works with the user's existing auth."""
    path = VARIANT_PATH % variant
    result = subprocess.run(
        ["gh", "api", "repos/%s/contents/%s" % (repo, path), "--jq", ".content"],
        capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError("could not fetch %s from %s: %s"
                           % (path, repo, result.stderr.strip()[:200]))
    import base64
    return base64.b64decode(result.stdout).decode("utf-8", "replace")


def parse_pins(header: str) -> dict:
    return {name: int(number) for name, number in PIN_DEFINITION.findall(header)}


def compare(board: dict, vendor_pins: dict):
    """Every way the board file and the vendor's header disagree."""
    problems, compared = [], 0
    ours = board.get("pins") or {}

    for label, gpio in sorted(ours.items(), key=lambda pin: pin[1]):
        theirs = vendor_pins.get(label)
        if theirs is None:
            problems.append(
                "%s = GPIO%d in the board file, but the vendor's header defines no pin called "
                "%r. Either the label is invented or it is printed on the board under another "
                "name — say which in a comment." % (label, gpio, label))
            continue
        compared += 1
        if theirs != gpio:
            problems.append(
                "%s is GPIO%d in the board file but GPIO%d in the vendor's header. "
                "This is the error class the board file exists to prevent." % (label, gpio, theirs))

    # A pin the vendor brings out that we never recorded is worth knowing about: it is either a
    # pin nobody can use because it is undocumented here, or a transcription that stopped early.
    missing = [name for name, gpio in sorted(vendor_pins.items(), key=lambda pin: pin[1])
               if name not in ours and not NOT_A_SILKSCREEN_LABEL.match(name)]
    return problems, compared, missing


def check_board(path: Path, offline: bool, repo: str):
    board = json.loads(path.read_text())
    variant = (board.get("vendor") or {}).get("arduino_variant")
    if not variant:
        return {
            "board": path.stem, "status": "could-not-run",
            "reason": "no vendor.arduino_variant in %s, so there is nothing to check it against. "
                      "Add it, or say in the file why this board has no vendor header." % path.name,
        }

    cache = path.parent.parent / CACHE_DIR / ("%s.pins_arduino.h" % variant)
    if offline:
        if not cache.is_file():
            return {"board": path.stem, "status": "could-not-run",
                    "reason": "--offline but no cached header at %s" % cache}
        header, source = cache.read_text(), "cache (%s)" % cache.name
    else:
        try:
            header = fetch_variant_header(variant, repo)
        except RuntimeError as broken:
            return {"board": path.stem, "status": "could-not-run", "reason": str(broken)}
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(header)
        source = "%s %s" % (repo, VARIANT_PATH % variant)

    vendor_pins = parse_pins(header)
    if not vendor_pins:
        return {"board": path.stem, "status": "could-not-run",
                "reason": "parsed no pin definitions out of %s" % source}

    problems, compared, missing = compare(board, vendor_pins)
    return {"board": path.stem, "status": "mismatch" if problems else "ok",
            "source": source, "compared": compared,
            "problems": problems, "not_recorded": missing}


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="check_vendor_pins.py",
        description="Compare a board definition against the vendor's own pin header.")
    parser.add_argument("boards", nargs="+", help="board definition files")
    parser.add_argument("--offline", action="store_true",
                        help="use the cached header; fail if there is none")
    parser.add_argument("--repo", default=ARDUINO_ESP32_REPO)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    results = [check_board(Path(p), args.offline, args.repo) for p in args.boards]
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for result in results:
            if result["status"] == "could-not-run":
                print("  %-24s could not run: %s" % (result["board"], result["reason"]))
                continue
            print("  %-24s %s  (%d pins against %s)"
                  % (result["board"],
                     "ok" if result["status"] == "ok" else "MISMATCH",
                     result["compared"], result["source"]))
            for problem in result.get("problems", []):
                print("      - %s" % problem)
            if result.get("not_recorded"):
                print("      note: the vendor also defines %s, which this board file does not "
                      "record" % ", ".join(result["not_recorded"]))

    if any(r["status"] == "mismatch" for r in results):
        return EXIT_MISMATCH
    if any(r["status"] == "could-not-run" for r in results):
        return EXIT_COULD_NOT_RUN
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
