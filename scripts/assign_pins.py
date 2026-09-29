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

import design as design_library  # noqa: E402
import parts as parts_library  # noqa: E402

from outcomes import EXIT_OK, EXIT_COULD_NOT_RUN, EXIT_PROBLEMS as EXIT_IMPOSSIBLE  # noqa: E402

#: What a signal can ask a pin for, from the contract that validates parts. Anything else in
#: `needs` is refused rather than ignored, because a typo'd requirement silently dropped produces
#: a board wrong in exactly the way the requirement existed to prevent.
#:
#: Imported rather than restated. This file kept its own copy, `("wake", "adc")`, while
#: `parts.py` validated any string at all — so a servo declaring `needs: ["pwm"]` was a good
#: record here and an impossible design there.
CAPABILITIES = parts_library.CAPABILITIES

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
    "spi": 5,                         # a bus, spent after plain pins and before scarce ones
    "i2c": 5,
    "adc2_unusable_with_wifi": 1,     # only a loss if you wanted the ADC, which `can` covers
}
#: THE BUS PENALTY IS A TIE-BREAKER, SMALLER THAN ONE ABILITY ON PURPOSE. Nothing marked SCK,
#: MI and MO as a bus, so the assigner spent all three on two LEDs and a button — the cheapest
#: pins left, by its lights — and a later SPI part had nowhere to go. The cost function already
#: ranks a pin by the abilities it WASTES (`CAPABILITY_COST` each), and a bus pin wastes nothing
#: scarce by itself; what spent the bus was the tie-break among equal pins, which goes by GPIO
#: number and on the FireBeetle puts MOSI (15) and MISO (16) before D6 (18). A penalty below
#: `CAPABILITY_COST` settles that tie and nothing more: a plain signal still takes a bus pin
#: before it wastes an ADC1 pin. Measured on the bin's 11 signals: at 0, LED_RED lands on MOSI;
#: at 5, on D6; at 15 — my first value — the bus ranked above the ADC1 pins and two plain
#: signals were sent onto the board's scarcest inputs instead. Five is also `DEFAULT_ROLE_PENALTY`,
#: what an unnamed role costs; these entries exist so the reason is written down. A bus signal
#: still lands on its own named pin regardless: that path runs first and ignores penalties.
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
    """
    Everything this pin can do, as a set — the basis for "least capable pin that will do".

    `pwm` is read from the board definition if it says anything, and otherwise assumed of every
    pin. That default is deliberate and it is a statement about the chips this tool targets, not
    laziness: an ESP32 routes its LEDC timers through a GPIO matrix, so any output pin can carry
    a PWM. A board where that is NOT true — most STM32 parts, where PWM comes from a fixed timer
    map — says so by listing `pwm_gpio`, and then a servo signal will not land on a pin that
    cannot drive it.
    """
    can = set()
    if gpio in board.get("wake_capable_gpio", []):
        can.add("wake")
    if gpio in board.get("adc_gpio", []):
        can.add("adc")
    if "pwm_gpio" not in board or gpio in board.get("pwm_gpio", []):
        can.add("pwm")
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


#: The lines a bus has, with the names vendors print for them — the parts library's definition,
#: imported, so a record `parts.py --validate` calls fine is one this can place (close audit C6).
BUS_LINES = parts_library.BUSES

#: Lines every device on the bus shares — which is what a bus IS. A chip select is per device:
#: the first takes the board's SS pin and the rest are ordinary signals on any free pin.
SHARED_LINES = frozenset({"SDA", "SCL", "SCK", "MOSI", "MISO"})


def bus_line(signal):
    """
    Which line of its bus a signal is, by the board's label for it — or Impossible, by name.

    The line comes from the part's own name for it (`line`, kept through the instance rename),
    else from the signal's name. Until 2026-09-29 the bus path matched the signal's NAME against
    the board's labels, so `RANGEFINDER_SDA` — a named instance — silently left the bus for D3,
    and `CLK` on `bus: spi` was placed on any pin with no word (audit B2, B3).
    """
    lines = BUS_LINES.get(signal["bus"])
    if lines is None:
        raise Impossible("%s is on bus %r, which is not a bus this knows: %s"
                         % (signal["name"], signal["bus"], ", ".join(BUS_LINES)))
    line = parts_library.bus_line_of(signal["bus"], signal.get("line") or signal["name"])
    if line is None:
        raise Impossible("%s is on the %s bus but %r is not one of its lines: %s"
                         % (signal["name"], signal["bus"].upper(), signal.get("line") or signal["name"],
                            ", ".join("%s (%s)" % (l, "/".join(names)) for l, names in lines.items())))
    return line


def board_dedicates_pins_to(board, bus):
    """
    Whether this board brings the bus out on labelled pins, which is a fact the board file
    states in `pin_roles`. A bus it does not — I2S on an ESP32, which reaches any pin through
    the GPIO matrix — has no pin to refuse for, and is placed like any signal, saying so.
    """
    return bus in (board.get("pin_roles") or {})


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

    # A signal on a named bus is dedicated hardware: the board's pin for that line of that bus,
    # shared with every other device on the bus, and no optimisation applies. Without this the
    # assigner put I2C on two arbitrary GPIOs and then gave the pin actually labelled SDA to an
    # analogue input — the bus lost its hardware peripheral and the silkscreen lied. A bus line
    # the board does not label is refused, not placed somewhere quiet.
    placed_by_name, to_place = [], []
    for signal in signals:
        if not signal.get("bus") or signal.get("pin"):
            (placed_by_name if signal.get("pin") else to_place).append(signal)
            continue
        line = bus_line(signal)
        if line in board["pins"]:
            placed_by_name.append(dict(signal, pin=line, line=line))
        elif line == "SS" or not board_dedicates_pins_to(board, signal["bus"]):
            # A select can go anywhere (see below); so can every line of a bus this board routes
            # through its matrix rather than to labelled pins — I2S on the ESP32. Refusing those
            # made the shipped MAX98357A unplaceable for an evening (close audit C6).
            to_place.append(dict(signal, line=line))
        else:
            raise Impossible("%s needs the %s bus's %s line and this board labels no %s pin — "
                             "add it to the board file's pins, or use another board"
                             % (signal["name"], signal["bus"].upper(), line, line))

    # A signal that names its own pin is honoured first and without argument.
    assignments, taken_gpio, bus_holders = [], set(), {}
    for signal in placed_by_name:
        label = signal["pin"]
        if label not in board["pins"]:
            raise Impossible("%s asks for pin %r, which this board does not bring out"
                             % (signal["name"], label))
        gpio = board["pins"][label]
        line = signal.get("line") if signal.get("bus") else None
        if gpio in taken_gpio:
            if line in SHARED_LINES and bus_holders.get(gpio) == (signal["bus"], line):
                assignments.append({
                    "signal": signal["name"], "pin": label, "gpio": gpio,
                    "why": "on the board's own %s pin, shared with everything else on the %s bus"
                           % (line, signal["bus"].upper()),
                    "roles": roles_of(board, gpio)})
                continue
            if line == "SS":
                # Every SPI device has its own select; the first took SS, this one goes anywhere.
                to_place.append(dict(signal, pin=None))
                continue
            raise Impossible("%s asks for %s (GPIO%d), which is already taken"
                             % (signal["name"], label, gpio))
        taken_gpio.add(gpio)
        if line in SHARED_LINES:
            bus_holders[gpio] = (signal["bus"], line)
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

    for signal in sorted([s for s in to_place if not s.get("pin")], key=difficulty):
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
        why = _why(needs, pin)
        if signal.get("line") == "SS" and board_dedicates_pins_to(board, signal.get("bus", "")):
            why = "a chip select — every SPI device has its own, and the board's SS pin is " \
                  "taken, so any pin serves; " + why
        elif signal.get("bus") and signal.get("line"):
            why = ("on the %s bus, which this board routes through its GPIO matrix rather than "
                   "to labelled pins, so any pin serves; " % signal["bus"].upper()) + why
        assignments.append({
            "signal": signal["name"], "pin": label, "gpio": pin["gpio"],
            "why": why, "roles": pin["roles"]})

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

    # One loader for the whole chain (`design.py`): the project is the requirements FILE's, the
    # parts are instances, and the signals are derived once and named per instance — the same
    # list `emit_board` traces. This used to read the JSON outside any try, resolve the project
    # from the current directory, and hand the raw `parts` entries to the library, so the first
    # step every document names crashed on the `{part, name}` form every document shows (B1).
    try:
        loaded = design_library.load(args.requirements, args.project, args.board)
    except design_library.DesignError as broken:
        print("could not load the design: %s" % broken)
        return EXIT_COULD_NOT_RUN
    board = loaded.board
    if not args.project and design_library.is_library(loaded.project):
        print(design_library.LIBRARY_NOTE)

    try:
        assignments, leftover = assign(board, loaded.signals)
    except Impossible as refused:
        print("cannot place every signal on this board:\n\n  %s" % refused)
        return EXIT_IMPOSSIBLE

    # Whatever the parts do not know about themselves travels with the answer. A pin map that
    # looks complete while resting on unmeasured numbers is the thing this plugin exists to stop.
    open_questions = parts_library.unverified(
        list(dict.fromkeys(part["id"] for part in loaded.parts)), loaded.project)

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
