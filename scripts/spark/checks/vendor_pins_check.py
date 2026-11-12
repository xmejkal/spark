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

import json
import re
import subprocess
from pathlib import Path

from spark.records import board_records  # the one project walk the scripts share (project_root), and spark's root
from spark.checks import check_codes
from spark.core.result import Refusal

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


#: spark's own folder, defined once in board_records.py: the boards it ships come with their vendor headers
#: in its `.spark/cache/`. The tests patch this name to a stand-in.
PLUGIN_ROOT = board_records.PLUGIN_ROOT


def header_name(variant: str) -> str:
    return "%s.pins_arduino.h" % variant


def project_header(path: Path, variant: str) -> Path:
    """
    The header's file in the cache of the project that owns the board file: the nearest folder up
    from it holding `boards/active.json` or `.spark/` (`board_records.project_root`, the walk the scripts
    share). A live check writes here and only here, and an offline check reads here first. For a
    board spark ships, the owning project is spark itself.

    Raises `board_records.BoardError` when no project owns the file. Counting two folders up from the path
    as typed, as the first version of P179's fix did, put a header checked from inside `boards/`
    into `boards/.spark/cache/`, and a loose board file's into whatever folder held it.
    """
    project = board_records.project_root(path.resolve().parent)
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
    except board_records.BoardError:
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
    except board_records.BoardError:
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


class CouldNotKeepError(Exception):
    """A live check could not fetch the vendor's header or keep it; the message names the place and the cause, and
    `code` (check_codes) says which."""

    def __init__(self, message, code):  # --- MVP --- (P693)
        super().__init__(message)
        self.code = code


def keep_live_header(path: Path, variant: str, repo: str):
    """
    Fetch the vendor's header and keep it in the owning project's cache. Returns `(header text,
    the file written)`. Raises `CouldNotKeepError` when no project owns the board file, the fetch fails,
    or the file cannot be written. The project is found first, so a refusal costs no network call.
    """
    try:
        target = project_header(path, variant)
    except board_records.BoardError:
        raise CouldNotKeepError(no_project_for_live(path, variant), check_codes.BOARD_HAS_NO_PROJECT) from None
    try:
        header = fetch_variant_header(variant, repo)
    except RuntimeError as broken:
        raise CouldNotKeepError(str(broken), check_codes.HEADER_NOT_FETCHED) from None
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(header)
    except OSError as refused:
        raise CouldNotKeepError("fetched the header but could not keep it at %s: %s"
                           % (target, refused.strerror or refused), check_codes.HEADER_NOT_KEPT) from None
    return header, target


def could_not_run(path, refusal):
    """One board's could-not-run result: the board, the Refusal as `reason`, and its `code` beside it for `--json` (P688)."""
    return {"board": path.stem, "status": "could-not-run", "reason": refusal, "code": refusal.code}


def check_board(path: Path, offline: bool, repo: str):
    if not path.is_file():  # P688: a traceback said less than a sentence
        return could_not_run(path, Refusal("no board file at %s" % path, check_codes.NO_BOARD_FILE))
    board = json.loads(path.read_text())
    variant = (board.get("vendor") or {}).get("arduino_variant")
    if not variant:
        return could_not_run(path, Refusal("no vendor.arduino_variant in %s, so there is nothing to check it against. "
                                           "Add it, or say in the file why this board has no vendor header." % path.name,
                                           check_codes.NO_VENDOR_VARIANT))

    wrote = None  # the file this run wrote, said in the answer so nobody has to guess (P179)
    if offline:
        header_file = header_to_read(path, variant)
        if not header_file.is_file():
            return could_not_run(path, Refusal(no_cached_header(path, variant), check_codes.NO_CACHED_HEADER))
        header, source = header_file.read_text(), "%s cache (%s)" % (whose(header_file), header_file.name)
    else:
        try:
            header, wrote = keep_live_header(path, variant, repo)
        except CouldNotKeepError as refused:
            return could_not_run(path, Refusal(str(refused), refused.code))
        source = "%s %s" % (repo, VARIANT_PATH % variant)

    vendor_pins = parse_pins(header)
    if not vendor_pins:
        result = could_not_run(path, Refusal("parsed no pin definitions out of %s" % source, check_codes.HEADER_HAS_NO_PINS))
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
