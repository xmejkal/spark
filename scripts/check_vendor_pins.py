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

WHERE IT KEEPS THE HEADER
A live run writes the header it fetched into `.spark/cache/` of the project that owns the board
file, and its line names the file. For a board spark ships, that project is spark itself, so a
live run refreshes the shipped header. `--offline` reads the project's copy first, then spark's,
and says whose answered. A live run on a board file no project owns is refused before any fetch,
and nothing is written.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import boards  # the one project walk the scripts share (boards.project_root), and spark's root

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


#: spark's own folder, defined once in boards.py: the boards it ships come with their vendor headers
#: in its `.spark/cache/`. The tests patch this name to a stand-in.
PLUGIN_ROOT = boards.PLUGIN_ROOT


def header_name(variant: str) -> str:
    return "%s.pins_arduino.h" % variant


def project_header(path: Path, variant: str) -> Path:
    """
    The header's file in the cache of the project that owns the board file: the nearest folder up
    from it holding `boards/active.json` or `.spark/` (`boards.project_root`, the walk the scripts
    share). A live check writes here and only here, and an offline check reads here first. For a
    board spark ships, the owning project is spark itself.

    Raises `boards.BoardError` when no project owns the file. Counting two folders up from the path
    as typed, as the first version of P179's fix did, put a header checked from inside `boards/`
    into `boards/.spark/cache/`, and a loose board file's into whatever folder held it.
    """
    project = boards.project_root(path.resolve().parent)
    return project / CACHE_DIR / header_name(variant)


def header_to_read(path: Path, variant: str) -> Path:
    """
    The cached header an `--offline` check reads: the owning project's copy when there is one,
    else spark's. A project's copy of a shipped board — the documented way to record what you
    verified about it — looked only beside itself, found nothing, and the one check that reads
    the vendor's own header answered "could not run" for exactly the boards it was written to
    check (backlog P10, intake R12).

    Only a read falls back to spark's copy. When the live write followed this fallback, the first
    live check of any new board wrote into spark's own folder (P179).
    """
    try:
        own = project_header(path, variant)
    except boards.BoardError:
        own = None  # a board file in no project: only spark's own copy can answer
    name = header_name(variant)
    return own if own and own.is_file() else PLUGIN_ROOT / CACHE_DIR / name


def whose(header: Path) -> str:
    """Whose cache a header file is in, in the words `source` uses."""
    return "spark's" if header.parent.resolve() == (PLUGIN_ROOT / CACHE_DIR).resolve() else "the project's"


def no_cached_header(path: Path, variant: str) -> str:
    """Why `--offline` found no header, naming both places it looked: the owning project's, then spark's."""
    sparks = PLUGIN_ROOT / CACHE_DIR
    try:
        return "--offline but no cached header at %s, nor in spark's own %s" % (project_header(path, variant), sparks)
    except boards.BoardError:
        return ("--offline but no project owns %s, and spark's own %s has no cached header %s"
                % (path.resolve(), sparks, header_name(variant)))


def no_project_for_live(path: Path, variant: str) -> str:
    """Why a live check refused a board file no project owns, and whether `--offline` would help."""
    name = header_name(variant)
    offline = ("or use --offline, which reads spark's own %s" % name if (PLUGIN_ROOT / CACHE_DIR / name).is_file()
               else "--offline would not help: spark keeps no %s" % name)
    return ("no project owns %s: nothing up from it holds boards/active.json or .spark/, and a live check "
            "keeps the header it fetches in the board's project. Put the board file in a project's boards/ "
            "(init_project.py makes one); %s" % (path.resolve(), offline))


class CouldNotKeep(Exception):
    """A live check could not fetch the vendor's header or keep it; the message names the place and the cause."""


def keep_live_header(path: Path, variant: str, repo: str):
    """
    Fetch the vendor's header and keep it in the owning project's cache. Returns `(header text,
    the file written)`. Raises `CouldNotKeep` when no project owns the board file, the fetch fails,
    or the file cannot be written. The project is found first, so a refusal costs no network call.
    """
    try:
        target = project_header(path, variant)
    except boards.BoardError:
        raise CouldNotKeep(no_project_for_live(path, variant)) from None
    try:
        header = fetch_variant_header(variant, repo)
    except RuntimeError as broken:
        raise CouldNotKeep(str(broken)) from None
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(header)
    except OSError as refused:
        raise CouldNotKeep("fetched the header but could not keep it at %s: %s"
                           % (target, refused.strerror or refused)) from None
    return header, target


def check_board(path: Path, offline: bool, repo: str):
    board = json.loads(path.read_text())
    variant = (board.get("vendor") or {}).get("arduino_variant")
    if not variant:
        return {
            "board": path.stem, "status": "could-not-run",
            "reason": "no vendor.arduino_variant in %s, so there is nothing to check it against. "
                      "Add it, or say in the file why this board has no vendor header." % path.name,
        }

    wrote = None  # the file this run wrote, said in the answer so nobody has to guess (P179)
    if offline:
        header_file = header_to_read(path, variant)
        if not header_file.is_file():
            return {"board": path.stem, "status": "could-not-run", "reason": no_cached_header(path, variant)}
        header, source = header_file.read_text(), "%s cache (%s)" % (whose(header_file), header_file.name)
    else:
        try:
            header, wrote = keep_live_header(path, variant, repo)
        except CouldNotKeep as refused:
            return {"board": path.stem, "status": "could-not-run", "reason": str(refused)}
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
    if wrote:
        result["wrote"] = str(wrote)
    return result


def wrote_note(result: dict) -> str:
    """The end of a human line: the file this run wrote, when it wrote one (P179)."""
    return "; wrote %s" % result["wrote"] if "wrote" in result else ""


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
