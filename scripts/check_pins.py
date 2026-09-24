#!/usr/bin/env python3
"""
Two checks on a design made of modules plugged into a dev board.

    check_pins.py design.json

Exit 0 if the design is sound, 1 if it is not. Every problem names the part, the pin and the
reason, because "the design is invalid" is not something you can act on at a bench.

Why these two and not others: they are the two mistakes that no EDA tool catches, because no EDA
format models them. KiCad will happily route a wake source to a pin that cannot wake the chip,
and no netlist format in existence has a field for an I2C address. Everything else worth checking
— ERC, DRC, footprint sanity — is already somebody else's solved problem.

The board's own facts come from a board definition file (see boards/README.md in the smart-bin
project for the schema). Nothing here is specific to one board or one project.
"""

import json
import sys
from pathlib import Path

EXIT_OK = 0
EXIT_PROBLEMS = 1


class Problem:
    """One thing that is wrong, in terms a person can act on."""

    def __init__(self, part, detail, fix=None):
        self.part = part
        self.detail = detail
        self.fix = fix

    def __str__(self):
        line = "  %s: %s" % (self.part, self.detail)
        if self.fix:
            line += "\n      %s" % self.fix
        return line


def load_json(path, what):
    try:
        return json.loads(Path(path).read_text())
    except FileNotFoundError:
        raise SystemExit("no %s at %s" % (what, path))
    except ValueError as error:
        raise SystemExit("%s at %s is not valid JSON: %s" % (what, path, error))


def usable_pins(board):
    """
    What each pin on this board can actually do.

    The distinction that matters, and the one an earlier version of this got wrong: a chip's
    capability and a board's are not the same thing. An ESP32-C6 can wake on GPIO0-7, but the XIAO
    brings only three of those out to the header. Checking against the chip alone would cheerfully
    approve a wake source on a pin that is not on the board at all, so the two are intersected.
    """
    exposed = board.get("pins", {})
    wake_capable = set(board.get("wake_capable_gpio", []))
    adc_capable = set(board.get("adc_gpio", []))

    roles_by_gpio = {}
    for role_name, role in board.get("pin_roles", {}).items():
        for gpio in role.get("gpio", []):
            roles_by_gpio.setdefault(gpio, []).append((role_name, role.get("note", "")))

    pins = {}
    for label, gpio in exposed.items():
        capabilities = set()
        if gpio in wake_capable:
            capabilities.add("wake")
        if gpio in adc_capable:
            capabilities.add("adc")
        pins[label] = {
            "gpio": gpio,
            "capabilities": capabilities,
            "roles": roles_by_gpio.get(gpio, []),
        }
    return pins


def check_pin_capability(design, board):
    """
    Every pin a part asks for exists, can do what is asked of it, and is asked only once.

    `needs` is the part's claim about a pin: "wake" for anything that must bring the board out of
    deep sleep, "adc" for anything analogue. A claim the board cannot honour is the failure this
    check exists for.
    """
    pins = usable_pins(board)
    board_name = board.get("name", "this board")
    problems = []
    claimed = {}

    for part in design.get("parts", []):
        ref = part.get("ref", "<unnamed part>")

        for assignment in part.get("pins", []):
            label = assignment.get("pin")
            signal = assignment.get("signal", "?")

            if label not in pins:
                problems.append(Problem(
                    ref, "%s is assigned to %s, which %s does not bring out" % (signal, label, board_name),
                    "available: %s" % ", ".join(sorted(pins))))
                continue

            pin = pins[label]

            previous = claimed.get(label)
            if previous:
                problems.append(Problem(
                    ref, "%s wants %s, already taken by %s.%s" % (signal, label, previous[0], previous[1])))
            else:
                claimed[label] = (ref, signal)

            for needed in assignment.get("needs", []):
                if needed not in pin["capabilities"]:
                    problems.append(Problem(
                        ref,
                        "%s needs a %s pin, but %s (GPIO%d) cannot do that"
                        % (signal, needed, label, pin["gpio"]),
                        "pins that can: %s" % (", ".join(
                            sorted(name for name, p in pins.items() if needed in p["capabilities"]))
                            or "none on this board")))

            # A role is a caveat, not a ban — except for the one combination that always bites.
            for role_name, note in pin["roles"]:
                if role_name == "boot_log_tx" and part.get("reads_serial"):
                    problems.append(Problem(
                        ref,
                        "%s is on %s, which is the boot-log UART, and this part reads serial"
                        % (signal, label),
                        note))

    return problems


def check_i2c_addresses(design):
    """
    No two devices on one bus answer to the same address.

    Worth its own check because no schematic or PCB format carries an I2C address at all, so no
    EDA tool can possibly catch it. It surfaces as a device that intermittently isn't there.
    """
    problems = []
    seen = {}

    for part in design.get("parts", []):
        i2c = part.get("i2c")
        if not i2c:
            continue
        ref = part.get("ref", "<unnamed part>")
        bus = i2c.get("bus", "i2c0")
        address = str(i2c.get("address", "")).lower()
        if not address:
            continue

        key = (bus, address)
        if key in seen:
            problems.append(Problem(
                ref, "answers to %s on %s, and so does %s" % (address, bus, seen[key]),
                "one of them needs its address strap changed, or its own bus"))
        else:
            seen[key] = ref

    return problems


def run(design, board):
    """Both checks. Returns the problems; printing and exit codes are the caller's business."""
    return check_pin_capability(design, board) + check_i2c_addresses(design)


def main(argv):
    if len(argv) != 2:
        raise SystemExit(__doc__.strip().split("\n\n")[1].strip())

    design_path = Path(argv[1])
    design = load_json(design_path, "design")

    board_path = Path(design["board"])
    if not board_path.is_absolute():
        board_path = (design_path.parent / board_path).resolve()
    board = load_json(board_path, "board definition")

    problems = run(design, board)
    parts = len(design.get("parts", []))
    print("%s: %d parts against %s" % (design_path.name, parts, board.get("name", board_path.name)))

    if not problems:
        print("\nnothing to fix.")
        return EXIT_OK

    print("\n%d problem(s):\n" % len(problems))
    for problem in problems:
        print(problem)
    return EXIT_PROBLEMS


if __name__ == "__main__":
    sys.exit(main(sys.argv))
