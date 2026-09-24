#!/usr/bin/env python3
"""
Does the firmware drive the board that was actually designed?

    check_firmware.py config.py --board firebeetle2-esp32s3
    check_firmware.py config.py --assignment pinmap.json

The firmware and the board are written in different languages, by different tools, at different
times, and nothing compiles them together. So they drift, and the drift is silent: the code runs,
the board builds, and the lid does not move.

WHAT IT COMPARES
Two things, and the second only if you have it.

  * Always — every pin the firmware names against what the BOARD can do. A pin that is not on the
    header, or is a strapping pin, is wrong whatever the design intended.
  * With an assignment — every pin against the pin map that was agreed. This is the real check:
    the firmware must drive the pins the design wired, and the design must wire every pin the
    firmware drives.

MATCHED BY GPIO, NOT BY NAME
A tool that did this before decided which firmware constants needed a wake-capable pin by running
a regex over their NAMES — `/INTERRUPT|BUTTON_OPEN/`. That is a naming convention pretending to
be a requirement: rename a constant and the check silently stops applying, and a project whose
constants are called something else gets no checking at all.

Here the requirement comes from the assignment, which came from the part that asked for it. Names
are used only to make the output readable. What is compared is the GPIO number, which is the thing
that is actually physically true.
"""

import argparse
import json
import re
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

import boards  # noqa: E402

EXIT_OK, EXIT_PROBLEMS, EXIT_COULD_NOT_RUN = 0, 1, 2

#: `PIN_MOTOR_IA = 14` at the start of a line. Deliberately narrow: an expression, a computed
#: value or a conditional assignment is not something to guess at, and a check that guesses is
#: worse than one that says it could not tell.
PIN_CONSTANT = re.compile(r"^(PIN_[A-Z0-9_]+)\s*=\s*(\d+)\s*(?:#.*)?$", re.M)

#: Roles that make a pin wrong for firmware to drive at all, whatever it is for.
FORBIDDEN_ROLES = ("strapping",)


def read_pin_constants(source: str) -> dict:
    """`PIN_MOTOR_IA = 14` -> {"PIN_MOTOR_IA": 14}."""
    return {name: int(number) for name, number in PIN_CONSTANT.findall(source)}


def check_against_board(firmware: dict, board: dict) -> list:
    """What is wrong with these pins on this board, regardless of what they are for."""
    problems = []
    on_header = {gpio: label for label, gpio in board["pins"].items()}
    roles = board.get("pin_roles") or {}

    for name, gpio in sorted(firmware.items(), key=lambda pin: pin[1]):
        if gpio not in on_header:
            problems.append(
                "%s = GPIO%d, which %s does not bring out — the firmware drives a pin that is "
                "not on the header" % (name, gpio, board["name"]))
            continue
        for role in FORBIDDEN_ROLES:
            if gpio in (roles.get(role) or {}).get("gpio", []):
                problems.append(
                    "%s = GPIO%d (%s), a %s pin: %s"
                    % (name, gpio, on_header[gpio], role, roles[role]["note"]))
    return problems


def check_against_assignment(firmware: dict, assignment: list, board: dict) -> list:
    """
    The firmware must drive the pins the design wired, and the design must wire every pin it
    drives. Both directions, because each failure is silent in its own way.
    """
    problems = []
    on_header = {gpio: label for label, gpio in board["pins"].items()}
    assigned = {entry["gpio"]: entry for entry in assignment}
    driven = {gpio: name for name, gpio in firmware.items()}

    for gpio, entry in sorted(assigned.items()):
        if gpio not in driven:
            problems.append(
                "the design wires %s to %s (GPIO%d), but no firmware constant uses that pin"
                % (entry["signal"], entry["pin"], gpio))

    for gpio, name in sorted(driven.items()):
        if gpio not in assigned:
            problems.append(
                "%s drives GPIO%d (%s), which the design does not connect to anything"
                % (name, gpio, on_header.get(gpio, "not on the header")))

    # A capability the assignment asked for has to still hold. It normally will — the assigner
    # honoured it — but a hand-edited pin map is exactly where this goes wrong.
    for entry in assignment:
        for needed in entry.get("needs", []):
            capable = {"wake": board.get("wake_capable_gpio", []),
                       "adc": board.get("adc_gpio", [])}.get(needed, [])
            if entry["gpio"] not in capable:
                problems.append(
                    "%s is on %s (GPIO%d) and needs %s, which that pin cannot do"
                    % (entry["signal"], entry["pin"], entry["gpio"], needed))
    return problems


def render(firmware, problems, compared):
    lines = ["%d pin constant(s) read" % len(firmware)]
    if compared:
        lines.append("  %d compared against the agreed pin map" % compared)
    if not problems:
        lines.append("\n  the firmware drives the board that was designed.")
        return "\n".join(lines)
    lines.append("\n%d disagreement(s):\n" % len(problems))
    for problem in problems:
        lines.append("  - %s" % problem)
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="check_firmware.py",
        description="Check that the firmware's pins match the board and the agreed pin map.")
    parser.add_argument("config", help="the firmware file holding PIN_* constants")
    parser.add_argument("--board", help="board id (default: the project's active board)")
    parser.add_argument("--project")
    parser.add_argument("--assignment",
                        help="JSON from assign_pins.py --json, the pin map that was agreed")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    path = Path(args.config)
    if not path.is_file():
        print("no firmware config at %s" % path)
        return EXIT_COULD_NOT_RUN

    firmware = read_pin_constants(path.read_text())
    if not firmware:
        # Silence here would read as "the firmware agrees", which is the one thing it must never
        # be mistaken for.
        print("no PIN_* constants in %s — nothing to compare, which is not the same as agreeing"
              % path.name)
        return EXIT_COULD_NOT_RUN

    try:
        project = Path(args.project).resolve() if args.project else boards.project_root()
        board = boards.load(project, args.board)
    except boards.BoardError as broken:
        print("could not load the board: %s" % broken)
        return EXIT_COULD_NOT_RUN

    problems = check_against_board(firmware, board)
    compared = 0
    if args.assignment:
        assignment_path = Path(args.assignment)
        if not assignment_path.is_file():
            print("no assignment at %s" % assignment_path)
            return EXIT_COULD_NOT_RUN
        assignment = json.loads(assignment_path.read_text()).get("assignments", [])
        problems += check_against_assignment(firmware, assignment, board)
        compared = len(assignment)

    if args.json:
        print(json.dumps({"tool": "check_firmware",
                          "status": "problems" if problems else "ok",
                          "constants": firmware, "problems": problems}, indent=2))
    else:
        print(render(firmware, problems, compared))
    return EXIT_PROBLEMS if problems else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
