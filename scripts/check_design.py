#!/usr/bin/env python3
"""
Two checks on a design made of modules plugged into a dev board.

    check_design.py design.json

Exit 0 if the design is sound, 1 if it is not. Every problem names the part, the pin and the
reason, because "the design is invalid" is not something you can act on at a bench.

Why these two and not others: they are the two mistakes that no EDA tool catches, because no EDA
format models them. KiCad will happily route a wake source to a pin that cannot wake the chip,
and no netlist format in existence has a field for an I2C address. Everything else worth checking
— ERC, DRC, footprint sanity — is already somebody else's solved problem.

The board's own facts come from a board definition. A design names one by id — "xiao-esp32-c6",
one of the definitions in boards/ — or by path for a board nobody has written down yet. Nothing
here is specific to one board or one project; see boards/README.md for the schema.
"""

import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

import boards  # noqa: E402  - for the role vocabulary, which must have one spelling

BOARDS = SCRIPTS.parent / "boards"

from outcomes import EXIT_OK, EXIT_PROBLEMS, EXIT_COULD_NOT_RUN, OK, PROBLEMS, COULD_NOT_RUN  # noqa: E402


class CannotCheck(Exception):
    """The design or its board could not be read: a could-not-run, never a usage message."""


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
        raise CannotCheck("no %s at %s" % (what, path))
    except ValueError as error:
        raise CannotCheck("%s at %s is not valid JSON: %s" % (what, path, error))


def resolve_board(reference, design_path):
    """
    Find a board definition, by id or by path.

    `"board": "xiao-esp32-c6"` names one of the definitions this tool ships, so a design works on
    someone else's machine without knowing where anything lives. A path still works and wins, for
    a board nobody has written down yet.
    """
    as_path = Path(reference)
    if not as_path.is_absolute():
        beside_design = (design_path.parent / as_path).resolve()
        if beside_design.is_file():
            return beside_design
    elif as_path.is_file():
        return as_path

    # Only a bare id looks in the shipped set; a path that did not resolve is a path, and saying
    # so beats silently treating it as the name of a board we ship.
    if "/" not in reference and not as_path.is_absolute():
        shipped = BOARDS / ("%s.json" % reference.removesuffix(".json"))
        if shipped.is_file():
            return shipped

    known = sorted(p.stem for p in BOARDS.glob("*.json")) if BOARDS.exists() else []
    raise CannotCheck(
        "no board definition for %r.\n  shipped: %s\n  or give a path to one."
        % (reference, ", ".join(known) or "none"))


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


def bus_of(part):
    """
    The bus this part shares, if it says it is on one.

    A bus is the one place several parts legitimately sit on the same pins. The design file
    already carries it — `{"i2c": {"bus": "i2c0"}}` — and nothing read it, so every second device
    on a bus was reported as a collision.
    """
    for key in ("i2c", "spi"):
        bus = (part.get(key) or {}).get("bus")
        if bus:
            return "%s:%s" % (key, bus)
    return None


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

            # Keyed on the GPIO, not the silkscreen label, and aware of buses. Both halves were
            # wrong, in opposite directions:
            #
            #   * One board brings GPIO10 out twice, as `SS` and as `A4`. Two parts on those two
            #     labels are on ONE pin and short each other, and a label-keyed check called that
            #     clean. `assign_pins.py` already does this correctly and says why.
            #   * Two I2C devices share SDA and SCL. That is not a collision, it is how a bus
            #     works, and it is the most common wiring pattern in the domain — reported as two
            #     errors on a stranger's first design.
            gpio, bus = pin["gpio"], bus_of(part)
            previous = claimed.get(gpio)

            if previous and bus and previous["bus"] == bus:
                pass  # shared on purpose, and both parts say so
            elif previous:
                also_known_as = ("" if previous["label"] == label
                                 else " — %s and %s are the same pin"
                                      % (label, previous["label"]))
                problems.append(Problem(
                    ref, "%s wants %s (GPIO%d), already taken by %s.%s%s"
                    % (signal, label, gpio, previous["ref"], previous["signal"], also_known_as),
                    "two parts driving one pin short each other" if not also_known_as else
                    "this board brings GPIO%d out under both names, so they are one net" % gpio))
            else:
                claimed[gpio] = {"ref": ref, "signal": signal, "label": label, "bus": bus}

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
            # The name comes from boards.PIN_ROLES rather than being spelled here: this line read
            # `"boot_log_tx"`, which is what one shipped board called the console and the other
            # did not, so the check passed a serial part on the console UART of the other board
            # without a word.
            for role_name, note in pin["roles"]:
                if role_name == boards.CONSOLE_UART and part.get("reads_serial"):
                    problems.append(Problem(
                        ref,
                        "%s is on %s, which carries the serial console, and this part reads serial"
                        % (signal, label),
                        note))

    return problems


def as_address(value):
    """
    One address, however it was written.

    `"0x29"`, `"0X29"`, `" 0x29"` and `41` are the same seven bits on the wire. Comparing them as
    strings — which this did — let a real clash through: two devices at 0x29 and 41 on one bus
    were reported as fine. That is the exact failure this check exists to catch.
    """
    try:
        return int(str(value).strip(), 0)
    except (TypeError, ValueError):
        return None


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
        raw = i2c.get("address")
        if raw in (None, ""):
            continue
        address = as_address(raw)
        if address is None:
            problems.append(Problem(
                ref, "has an I2C address of %r, which is not a number" % raw,
                "write it as 0x29 or 41"))
            continue

        key = (bus, address)
        if key in seen:
            problems.append(Problem(
                ref, "answers to 0x%02x on %s, and so does %s" % (address, bus, seen[key]),
                "one of them needs its address strap changed, or its own bus"))
        else:
            seen[key] = ref

    return problems


def run(design, board):
    """Both checks. Returns the problems; printing and exit codes are the caller's business."""
    return check_pin_capability(design, board) + check_i2c_addresses(design)


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(
        prog="check_design.py",
        description="The mistakes no EDA tool catches: pins, capabilities, shared buses, I2C addresses.")
    parser.add_argument("design", help="a design.json: the board, the parts, their pins and what each pin must do")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    # Until 2026-09-29 this read `argv[1]` and nothing else: `--help` printed "no design at
    # --help" and exited 1 — a problem code for a question (intake O4c, backlog P24).

    design_path = Path(args.design)
    try:
        design = load_json(design_path, "design")
        if not isinstance(design, dict) or not design.get("board"):
            raise CannotCheck("%s names no board" % design_path)
        board_path = resolve_board(design["board"], design_path)
        board = load_json(board_path, "board definition")
    except CannotCheck as why:
        if args.json:
            print(json.dumps({"check": "design", "status": COULD_NOT_RUN, "reason": str(why)}))
        else:
            print("check_design.py: %s" % why, file=sys.stderr)
        return EXIT_COULD_NOT_RUN

    problems = run(design, board)
    parts = len(design.get("parts", []))
    if args.json:
        print(json.dumps({"check": "design", "status": PROBLEMS if problems else OK,
                          "design": design_path.name, "board": board.get("name", board_path.name),
                          "parts": parts, "problems": [str(problem) for problem in problems]}, indent=2))
        return EXIT_PROBLEMS if problems else EXIT_OK

    print("%s: %d parts against %s" % (design_path.name, parts, board.get("name", board_path.name)))
    if not problems:
        print("\nnothing to fix.")
        return EXIT_OK
    print("\n%d problem(s):\n" % len(problems))
    for problem in problems:
        print(problem)
    return EXIT_PROBLEMS


if __name__ == "__main__":
    sys.exit(main())
