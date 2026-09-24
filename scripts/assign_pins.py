#!/usr/bin/env python3
"""
Which pin should each signal go on, and why?

    assign_pins.py requirements.json
    assign_pins.py requirements.json --board firebeetle2-esp32s3 --json

`check_design.py` tells you a pin assignment is wrong. This works out a right one, and — the part
that matters more — says what each choice cost, so a person can disagree with it.

WHY THIS IS A SCRIPT
Because it is a constraint problem with one right family of answers, and because doing it by hand
is where the expensive mistakes live. On a real board this step took an afternoon and produced a
map that had to be redone from scratch when the microcontroller changed: the old chip could wake
from three usable pins and the new one from twenty-two, so every assignment made under the old
scarcity was the wrong shape under the new one.

THE IDEA IT ENCODES: SPEND THE SCARCE PINS LAST
A pin is not just free or taken. Some pins can do things no other pin can — wake the chip, read a
voltage — and a signal that does not need those abilities should never be given one. Assigning
greedily in the order the signals happen to be listed burns an ADC pin on an LED and then fails
on the sensor that needed it, with no explanation beyond "no pins left".

So signals are placed most-constrained-first, and each is given the LEAST capable pin that can
still do its job. That is the whole algorithm, and it is the same reasoning a careful person
applies — written down, applied consistently, and able to explain itself.

WHAT IT REFUSES TO DO
It does not silently drop a requirement it cannot meet. An impossible set comes back as a
refusal naming the signal, what it needed, and which pins could have served it and why each is
taken. A tool that half-assigns and exits zero is how a board gets built around a pin map that
was never actually satisfiable.
"""

import argparse
import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

import boards  # noqa: E402
import parts as parts_library  # noqa: E402

EXIT_OK, EXIT_IMPOSSIBLE, EXIT_COULD_NOT_RUN = 0, 1, 2

#: What a signal can ask a pin for. Anything else in `needs` is refused rather than ignored,
#: because a typo'd requirement that is silently dropped produces a board that is wrong in
#: exactly the way the requirement existed to prevent.
CAPABILITIES = ("wake", "adc")

#: Roles from the board definition that make a pin unusable for general assignment.
#:
#: `strapping` is the important one: a pin the bootloader samples at reset. Put a button on it and
#: holding that button during a reset drops the board into the bootloader instead of running.
UNAVAILABLE_ROLES = ("strapping",)

#: Roles that do not disqualify a pin but make it a worse choice, and by how much.
#:
#: Reporting a role is not enough. The first version of this only noted them, and cheerfully put
#: a motor driver input on the console UART — a pin the ROM bootloader drives push-pull on every
#: reset, so the motor would twitch every time the board booted — and an enable line on the
#: module's own button. Both were printed in the output and neither was avoided.
#:
#: So a role costs something, and a pin carrying one is taken only when nothing plainer is free.
#: The numbers are ordinal, not physical: they rank pins against each other and nothing else.
ROLE_PENALTY = {
    "console_uart": 40,               # costs you the serial console, and TX moves at every reset
    "onboard_button": 20,             # something else is already wired to it, and can press it
    "onboard_led": 10,                # it will blink whatever you put on it
    "adc2_unusable_with_wifi": 1,     # only a loss if you wanted the ADC, which `can` covers
}
DEFAULT_ROLE_PENALTY = 5

#: Roles where something ELSE is already wired to the pin, so sharing it has a consequence a
#: person needs to be told about. The rest are caveats that may not apply: a pin being on ADC2
#: matters only if you wanted to read a voltage with it, and calling that "another job" when the
#: signal is an LED is noise dressed as a warning.
CONFLICTING_ROLES = ("console_uart", "onboard_button", "onboard_led")

#: What one unused capability costs, in the same units as a role penalty.
#:
#: These have to be ONE number, not two sorts. Ranking by capability count first and penalty
#: second meant a zero-capability pin always won — so the console UART, which can do nothing
#: special, beat a plain wake-capable pin. That is backwards: this chip has twenty-two
#: wake-capable pins and one console, and losing the console costs you bring-up.
#:
#: At 8, spending a wake pin is cheaper than the onboard button (20) or the console (40), and
#: spending an ADC pin (16, two capabilities) is still cheaper than the console. Those orderings
#: are the judgement in this file; everything else is bookkeeping.
CAPABILITY_COST = 8


class Impossible(Exception):
    """A requirement no pin on this board can satisfy, with the reason."""


def capability_of(board, gpio):
    """Everything this pin can do, as a set — the basis for "least capable pin that will do"."""
    can = set()
    if gpio in board.get("wake_capable_gpio", []):
        can.add("wake")
    if gpio in board.get("adc_gpio", []):
        can.add("adc")
    return can


def roles_of(board, gpio):
    return sorted(role for role, spec in (board.get("pin_roles") or {}).items()
                  if gpio in spec.get("gpio", []))


def candidates(board):
    """
    Every header pin that may be assigned, with what it can do and what else it is.

    Keyed by silkscreen label, because that is what is printed on the board and what a person
    wiring it reads. Two labels may share a GPIO — on one real board both A4 and SS are GPIO10 —
    so assigning one has to take the other out of play, which `assign` handles by GPIO.
    """
    found = {}
    for label, gpio in sorted(board["pins"].items(), key=lambda pin: (pin[1], pin[0])):
        roles = roles_of(board, gpio)
        if any(role in UNAVAILABLE_ROLES for role in roles):
            continue
        found[label] = {"gpio": gpio, "can": capability_of(board, gpio), "roles": roles}
    return found


def assign(board, signals):
    """
    Place every signal, most-constrained first, on the least capable pin that will do.

    Returns (assignments, leftover). Raises `Impossible` rather than returning a partial map.
    """
    available = candidates(board)
    for signal in signals:
        unknown = set(signal.get("needs", [])) - set(CAPABILITIES)
        if unknown:
            raise Impossible(
                "%s asks for %s, which is not something a pin can be asked for. Known: %s"
                % (signal["name"], ", ".join(sorted(unknown)), ", ".join(CAPABILITIES)))

    # A signal on a named bus is dedicated hardware. If the board brings that peripheral out on
    # a pin of the same name — SDA, SCL, SCK — that is the pin, and no optimisation applies.
    #
    # Without this the assigner put I2C on two arbitrary GPIOs and then gave the pin actually
    # labelled SDA to an analogue input, which is wrong twice: the bus loses its hardware
    # peripheral, and the board's silkscreen now lies about what is connected to it.
    signals = [dict(signal, pin=signal["name"])
               if signal.get("bus") and not signal.get("pin")
               and signal["name"] in board["pins"] else signal
               for signal in signals]

    # A signal that names its own pin is honoured first and without argument.
    assignments, taken_gpio = [], set()
    for signal in [s for s in signals if s.get("pin")]:
        label = signal["pin"]
        if label not in board["pins"]:
            raise Impossible("%s asks for pin %r, which this board does not bring out"
                             % (signal["name"], label))
        gpio = board["pins"][label]
        if gpio in taken_gpio:
            raise Impossible("%s asks for %s (GPIO%d), which is already taken"
                             % (signal["name"], label, gpio))
        taken_gpio.add(gpio)
        assignments.append({
            "signal": signal["name"], "pin": label, "gpio": gpio,
            "why": ("on the board's own %s pin — dedicated hardware, not a choice"
                    % signal["bus"].upper()) if signal.get("bus")
                   else "asked for by name — dedicated hardware, not a choice",
            "roles": roles_of(board, gpio)})

    # Then the rest: hardest to place first, so a scarce pin is never spent on a signal that
    # could have used any pin at all.
    def difficulty(signal):
        return -len(set(signal.get("needs", [])))

    for signal in sorted([s for s in signals if not s.get("pin")], key=difficulty):
        needs = set(signal.get("needs", []))
        usable = {label: pin for label, pin in available.items()
                  if pin["gpio"] not in taken_gpio and needs <= pin["can"]}
        if not usable:
            raise Impossible(_why_not(board, signal, needs, available, taken_gpio))

        # The least capable, least encumbered pin that still does the job — so abilities stay
        # available for the signals that need them, and pins with another job stay free for as
        # long as possible. Ties break on GPIO number, for a stable answer.
        label = min(usable,
                    key=lambda name: (_cost(usable[name], needs), usable[name]["gpio"]))
        pin = usable[label]
        taken_gpio.add(pin["gpio"])
        assignments.append({
            "signal": signal["name"], "pin": label, "gpio": pin["gpio"],
            "why": _why(needs, pin), "roles": pin["roles"]})

    leftover = {label: pin for label, pin in available.items()
                if pin["gpio"] not in taken_gpio}
    return assignments, leftover


def _penalty(roles):
    """How reluctant we should be to spend this pin, from its roles."""
    return sum(ROLE_PENALTY.get(role, DEFAULT_ROLE_PENALTY) for role in roles
               if role != "not_wake_capable")


def _cost(pin, needs=frozenset()):
    """
    What spending this pin costs: the abilities it wastes, plus the job it already has.

    One number, so the two can be traded against each other. `needs` are not wasted — a signal
    that asked for `wake` is not squandering the wake pin it gets.
    """
    wasted = len(pin["can"] - set(needs))
    return wasted * CAPABILITY_COST + _penalty(pin["roles"])


def _why(needs, pin):
    """One sentence a person can disagree with."""
    if needs:
        spare = sorted(pin["can"] - needs)
        if spare:
            return ("needs %s; this pin also does %s, which is spent here because nothing else "
                    "was available" % (", ".join(sorted(needs)), ", ".join(spare)))
        return "needs %s, and this pin does exactly that and no more" % ", ".join(sorted(needs))
    shared = [role for role in pin["roles"] if role in CONFLICTING_ROLES]
    if shared:
        return ("needs nothing special, but something else is already wired here (%s) — taken "
                "only because nothing free was left" % ", ".join(shared))
    if pin["can"]:
        return ("needs nothing special; the cheapest pin left could still %s, which is spent here"
                % " and ".join(sorted(pin["can"])))
    return "needs nothing special, and this pin can do nothing special — the right trade"


def _why_not(board, signal, needs, available, taken_gpio):
    """An impossibility, explained by naming who has the pins it wanted."""
    could_have = {label: pin for label, pin in available.items() if needs <= pin["can"]}
    if not could_have:
        return ("%s needs %s, and no pin on this board can do that at all"
                % (signal["name"], ", ".join(sorted(needs)) or "a pin"))
    return ("%s needs %s. %d pin(s) could have served it — %s — and every one is already taken. "
            "Free a pin, or move this signal to a board with more of them."
            % (signal["name"], ", ".join(sorted(needs)) or "a pin",
               len(could_have), ", ".join(sorted(could_have))))


def render(board, assignments, leftover):
    lines = ["%s — %d signal(s) placed\n" % (board["name"], len(assignments))]
    width = max((len(a["signal"]) for a in assignments), default=0)
    for entry in assignments:
        note = ("  [%s]" % ", ".join(entry["roles"])) if entry["roles"] else ""
        lines.append("  %s  %-5s GPIO%-3d %s%s"
                     % (entry["signal"].ljust(width), entry["pin"], entry["gpio"],
                        entry["why"], note))

    lines.append("\n  still free:")
    if not leftover:
        lines.append("    nothing — every assignable pin is spent")
    for label, pin in sorted(leftover.items(), key=lambda item: item[1]["gpio"]):
        can = ", ".join(sorted(pin["can"])) or "plain"
        lines.append("    %-5s GPIO%-3d %s" % (label, pin["gpio"], can))
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="assign_pins.py",
        description="Work out which pin each signal should go on, and say why.")
    parser.add_argument("requirements", help="JSON naming the signals and what each pin must do")
    parser.add_argument("--board", help="board id (default: the project's active board)")
    parser.add_argument("--project", help="the project to resolve the board from")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    path = Path(args.requirements)
    if not path.is_file():
        print("no requirements at %s" % path)
        return EXIT_COULD_NOT_RUN

    wanted = json.loads(path.read_text())

    # The project is resolved first because BOTH libraries need it: a project's own board file
    # beats the shipped one, and so does its own part file. Reading the parts before this was
    # settled is how the parts library ended up being consulted without a project at all.
    try:
        project = Path(args.project).resolve() if args.project else boards.project_root()
        board = boards.load(project, args.board or wanted.get("board"))
    except boards.BoardError as broken:
        print("could not load the board: %s" % broken)
        return EXIT_COULD_NOT_RUN

    # A requirements file may name PARTS instead of listing every signal by hand. The signals a
    # part asks for are a property of the part, not of this design, so they belong in the part
    # library where they can be verified once and reused.
    signals = list(wanted.get("signals") or [])
    if wanted.get("parts"):
        try:
            signals = parts_library.signals_for(wanted["parts"], project) + signals
        except parts_library.PartError as broken:
            print("could not read a part: %s" % broken)
            return EXIT_COULD_NOT_RUN

    try:
        assignments, leftover = assign(board, signals)
    except Impossible as refused:
        print("cannot place every signal on this board:\n\n  %s" % refused)
        return EXIT_IMPOSSIBLE

    # Whatever the parts do not know about themselves travels with the answer. A pin map that
    # looks complete while resting on unmeasured numbers is the thing this plugin exists to stop.
    open_questions = (parts_library.unverified(wanted["parts"], project)
                      if wanted.get("parts") else [])

    if args.json:
        print(json.dumps({"tool": "assign_pins", "board": board["id"],
                          "unverified": open_questions,
                          "assignments": assignments,
                          "free": [{"pin": label, **pin} | {"can": sorted(pin["can"])}
                                   for label, pin in leftover.items()]}, indent=2))
    else:
        print(render(board, assignments, leftover))
        if open_questions:
            print("\n  still unverified about these parts:")
            for question in open_questions:
                print("    %s.%s" % (question["part"], question["fact"]))
                if question["why_it_matters"]:
                    print("      %s" % question["why_it_matters"])
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
