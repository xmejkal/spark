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

from outcomes import EXIT_OK, EXIT_COULD_NOT_RUN, EXIT_FOR, EXIT_PROBLEMS as EXIT_MISMATCH, status_of  # noqa: E402

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


#: The plugin's own cache: the boards it ships come with their vendor headers fetched.
PLUGIN_ROOT = Path(__file__).resolve().parent.parent


def own_cache(path: Path, variant: str) -> Path:
    """
    Where the board file's own project keeps its vendor header: `.spark/cache/` beside the
    `boards/` folder the file is in. A live check writes here and nowhere else; for a board the
    plugin ships, that project is the plugin itself (P179).
    """
    return path.parent.parent / CACHE_DIR / ("%s.pins_arduino.h" % variant)


def cached_header(path: Path, variant: str) -> Path:
    """
    The vendor header to READ for a board file: the board's own project's when it has one, else
    the plugin's. A project's copy of a shipped board — the documented way to record what you
    verified about it — looked only beside itself, found nothing, and the one check that reads
    the vendor's own header answered "could not run" for exactly the boards it was written to
    check (backlog P10, intake R12).

    Never the place to WRITE a fetched header: that is `own_cache`, always. When the write
    followed this fallback, the first live check of any new board wrote into the plugin's folder
    (P179).
    """
    own = own_cache(path, variant)
    name = own.name
    return own if own.is_file() else PLUGIN_ROOT / CACHE_DIR / name


def check_board(path: Path, offline: bool, repo: str):
    board = json.loads(path.read_text())
    variant = (board.get("vendor") or {}).get("arduino_variant")
    if not variant:
        return {
            "board": path.stem, "status": "could-not-run",
            "reason": "no vendor.arduino_variant in %s, so there is nothing to check it against. "
                      "Add it, or say in the file why this board has no vendor header." % path.name,
        }

    written = None  # the file this run wrote, said in the answer so nobody has to guess (P179)
    if offline:
        cache = cached_header(path, variant)
        if not cache.is_file():
            return {"board": path.stem, "status": "could-not-run",
                    "reason": "--offline but no cached header at %s, nor in the plugin's own %s"
                              % (own_cache(path, variant), PLUGIN_ROOT / CACHE_DIR)}
        # The whole path: whether the project's copy or the plugin's answered is the point.
        header, source = cache.read_text(), "cache (%s)" % cache
    else:
        try:
            header = fetch_variant_header(variant, repo)
        except RuntimeError as broken:
            return {"board": path.stem, "status": "could-not-run", "reason": str(broken)}
        written = own_cache(path, variant)
        written.parent.mkdir(parents=True, exist_ok=True)
        written.write_text(header)
        source = "%s %s" % (repo, VARIANT_PATH % variant)

    vendor_pins = parse_pins(header)
    if not vendor_pins:
        result = {"board": path.stem, "status": "could-not-run",
                  "reason": "parsed no pin definitions out of %s" % source}
    else:
        problems, compared, missing = compare(board, vendor_pins)
        result = {"board": path.stem, "status": "mismatch" if problems else "ok",
                  "source": source, "compared": compared,
                  "problems": problems, "not_recorded": missing}
    if written:
        result["cached"] = str(written)
    return result


def where_kept(result: dict) -> str:
    """The end of a human line: the file this run wrote, when it wrote one (P179)."""
    return "; cached at %s" % result["cached"] if "cached" in result else ""


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
                print("  %-24s could not run: %s%s" % (result["board"], result["reason"], where_kept(result)))
                continue
            print("  %-24s %s  (%d pins against %s%s)"
                  % (result["board"],
                     "ok" if result["status"] == "ok" else "MISMATCH",
                     result["compared"], result["source"], where_kept(result)))
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
