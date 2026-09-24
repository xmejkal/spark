#!/usr/bin/env python3
"""
A pretend bench, so the measurement loop can be demonstrated and tested without one.

    bench_sim.py mp3-idle-current
    bench_sim.py motor-stall-current --seed 7        reproducible, for tests
    bench_sim.py --list                              what it can pretend to measure

It prints the command that would record the reading. It never writes to a store itself — you can
see what it produced, and decide, which is the same shape as a real bench where a number arrives
via a person.

**Everything it produces is marked `simulated`.** That is the whole design constraint. A
fabricated value once walked out of this project's own documentation into a live findings store
and sat there with an instrument and a date, looking exactly like a reading, while the handover
note still said the number had never been taken. A simulator that produced convincing readings
would be that same failure shipped as a feature. So a simulated number is a distinct source, it
prints with a warning attached, and nothing that costs money may rest on it.

The models below are honest about what they are: plausible ranges and textbook relationships, not
claims about any particular part on anybody's desk.
"""

import argparse
import json
import random
import sys

#: What this can pretend to measure, and why the number looks like that.
#:
#: A model is either a `range` — two plausible bounds for a part of this class — or a `formula`
#: that derives the value from other quantities, which is the more useful kind because it lets a
#: demo show one reading moving another.
BENCH = {
    "mp3-idle-current": {
        "unit": "mA",
        "range": (12.0, 26.0),
        "why": "A UART audio module with an onboard regulator and a biased amplifier. The spread "
               "is wide because it depends on the module's own firmware state.",
    },
    "motor-winding-resistance": {
        "unit": "ohm",
        "range": (3.0, 20.0),
        "why": "A small brushed gearmotor. The range spans the difference between a motor that is "
               "comfortable on this driver and one that is not, which is exactly why it is worth "
               "measuring rather than assuming.",
    },
    "motor-stall-current": {
        "unit": "A",
        "formula": "supply / (winding + source + shunt)",
        "needs": {"motor-winding-resistance": "ohm"},
        "why": "Locked rotor is set by resistance, not by wishful thinking: (V_oc - V_sat) over "
               "the winding plus the pack's internal resistance plus the sense shunt.",
        "constants": {"supply": 6.0, "saturation_drop": 0.9, "pack": 0.8, "shunt": 0.33},
    },
    "sensor-idle-current": {
        "unit": "mA",
        "range": (0.2, 3.0),
        "why": "A rangefinder breakout free-running. The top of the range is what a power LED on "
               "a cheap board costs you, which is why the breakout has to be identified.",
    },
}


def simulate(name, seed=None, given=None):
    """
    Produce one plausible reading, and say how it was produced.

    `given` supplies values a formula depends on, so a demo can show a measurement that follows
    from another — take the winding resistance, and the stall current falls out.
    """
    model = BENCH.get(name)
    if model is None:
        raise SystemExit(
            "no bench model for %r.\n  can pretend to measure: %s"
            % (name, ", ".join(sorted(BENCH))))

    generator = random.Random(seed)

    if "range" in model:
        low, high = model["range"]
        value = round(generator.uniform(low, high), 2)
        working = "drawn from %s-%s %s" % (low, high, model["unit"])
    else:
        supplied = dict(given or {})
        missing = [need for need in model["needs"] if need not in supplied]
        if missing:
            # Rather than invent the input, measure it first — which is the point the formula is
            # here to make.
            supplied.update({need: simulate(need, seed)["value"] for need in missing})
        constants = model["constants"]
        winding = float(supplied["motor-winding-resistance"])
        value = round(
            (constants["supply"] - constants["saturation_drop"])
            / (winding + constants["pack"] + constants["shunt"]), 2)
        working = "(%.1f - %.1f) / (%.2f + %.2f + %.2f)" % (
            constants["supply"], constants["saturation_drop"],
            winding, constants["pack"], constants["shunt"])

    return {"name": name, "value": value, "unit": model["unit"],
            "working": working, "why": model["why"]}


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="bench_sim.py",
        description="Pretend to take a reading, so the loop can be shown without a bench.")
    parser.add_argument("name", nargs="?", help="what to pretend to measure")
    parser.add_argument("--seed", type=int, help="reproducible, for tests")
    parser.add_argument("--list", action="store_true", help="what it can pretend to measure")
    parser.add_argument("--json", action="store_true", help="machine-readable, for a caller")
    args = parser.parse_args(argv)

    if args.list or not args.name:
        for name, model in sorted(BENCH.items()):
            print("  %-26s %s" % (name, model["why"].split(".")[0] + "."))
        return 0

    reading = simulate(args.name, args.seed)

    if args.json:
        # The human path printed "NOT A READING" and this one printed a bare number with a unit,
        # indistinguishable from something somebody measured — in the one output format a machine
        # consumes, in a tool whose stated single design constraint is that everything it produces
        # is marked simulated. That is the failure this module exists to prevent, shipped as a
        # feature, on the path least able to notice.
        print(json.dumps(dict(reading, source="simulated", measured=False,
                              warning="NOT A READING. Nobody measured anything. This number came "
                                      "from a model of the part, and recording it with any source "
                                      "but 'simulated' would make a guess look like a reading."),
                         indent=2))
        return 0

    print("%s = %s %s" % (reading["name"], reading["value"], reading["unit"]))
    print("  how: %s" % reading["working"])
    print("  why: %s" % reading["why"])
    print()
    print("  NOT A READING. Nobody measured anything. To record it as what it is:")
    print("    findings.py measure %s --value %s --unit %s --source simulated"
          % (reading["name"], reading["value"], reading["unit"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
