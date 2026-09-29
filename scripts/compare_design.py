#!/usr/bin/env python3
"""
Compare a written rule against the design that was actually built.

    compare_design.py dist/board/circuit.json

Exit 0 if every rule holds, 1 if one does not. Each failure names the net, the parts on it, and
what to add.

This exists because of a pattern that showed up three times in one project, always the same shape:
a rule written down, an artifact that did not implement it, and nothing comparing the two. A
design-rules document required I2C pull-ups; the board carried six resistors and not one was a
pull-up; the two disagreed from the day the rule was written and no check could see it, because
the rule lived in prose and the truth lived in a netlist.

The other checks in this plugin read a design description. This one reads `circuit.json` — the
compiled output of the thing that will actually be fabricated — so what it reports is a property
of the board rather than of somebody's description of the board.
"""

import json
import sys
from pathlib import Path

from outcomes import EXIT_OK, EXIT_PROBLEMS, EXIT_COULD_NOT_RUN  # noqa: E402

#: A pull-up weaker than this cannot hold a bus high against its own capacitance; stronger than
#: this and the driving pin cannot pull it down. Wide on purpose — this is a sanity band, not a
#: design calculation, and saying which is which matters.
PULLUP_MIN_OHM = 1000
PULLUP_MAX_OHM = 10000


#: The three answers a caller must be able to tell apart.
#:
#: An autonomous caller cannot act on prose, and it especially cannot act on an exit code that
#: conflates "I looked and everything is fine" with "I could not look". That conflation already
#: cost this project once: an eval scored zero on every run because the files were outside the
#: sandbox, and a zero that means "found nothing" is indistinguishable from a zero that means
#: "could not read the board" — so the obvious reading was that the reviewer did not work.
OK, PROBLEMS, COULD_NOT_RUN = "ok", "problems", "could-not-run"


class Failure:
    """One rule that the built design does not satisfy."""

    def __init__(self, rule, subject, detail, fix=None):
        self.rule = rule
        self.subject = subject
        self.detail = detail
        self.fix = fix

    def as_data(self):
        return {"rule": self.rule, "subject": self.subject,
                "detail": self.detail, "fix": self.fix}

    def __str__(self):
        text = "  [%s] %s: %s" % (self.rule, self.subject, self.detail)
        if self.fix:
            text += "\n      %s" % self.fix
        return text


def could_not_run(reason, **detail):
    """A refusal a caller can act on, rather than a message a caller has to read."""
    return dict({"tool": "compare_design", "status": COULD_NOT_RUN, "reason": reason}, **detail)


def render(result):
    """
    The human view, built from the result rather than beside it.

    Two code paths would drift, the same way a rule in prose drifts from the board it describes —
    which is the failure this whole script exists to catch.
    """
    if result["status"] == COULD_NOT_RUN:
        return "could not run: %s" % result["reason"]

    lines = ["%s: %d rule(s) checked against the built design"
             % (result["design"], result["checked"])]
    if result["status"] == OK:
        lines.append("\nevery rule holds.")
        return "\n".join(lines)

    lines.append("\n%d rule(s) the board does not satisfy:\n" % len(result["problems"]))
    for problem in result["problems"]:
        line = "  [%s] %s: %s" % (problem["rule"], problem["subject"], problem["detail"])
        if problem.get("fix"):
            line += "\n      %s" % problem["fix"]
        lines.append(line)
    return "\n".join(lines)


class Netlist:
    """
    The built design, as connectivity.

    Connectivity comes from `source_trace`, which states its ports and nets explicitly. It is
    tempting to group ports by `subcircuit_connectivity_map_key` instead — but in a real export
    16 of 92 ports carry no key at all, and grouping on that joins every one of them into a
    single phantom net, wiring a 5 V pin to an H-bridge input. Unconnected is a state, not a
    grouping.
    """

    def __init__(self, circuit):
        self.components = {
            e["source_component_id"]: e for e in circuit if e["type"] == "source_component"}
        self.ports = {e["source_port_id"]: e for e in circuit if e["type"] == "source_port"}
        self.nets = {e["source_net_id"]: e for e in circuit if e["type"] == "source_net"}

        #: net id -> [(component name, port name)]
        self.members = {net_id: [] for net_id in self.nets}
        for element in circuit:
            if element["type"] != "source_trace":
                continue
            net_ids = [net_id for net_id in element.get("connected_source_net_ids", []) if net_id in self.members]
            if not net_ids:
                # A pin-to-pin trace names no net, and it is still a connection: spark's generator
                # wires every signal this way, and this loop skipped them, so every such pin read
                # as floating on three projects (backlog P8). Its connectivity key groups the
                # traces of one wire; the trace's own id stands in when there is none.
                net_ids = ["trace:" + (element.get("subcircuit_connectivity_map_key") or element["source_trace_id"])]
                self.members.setdefault(net_ids[0], [])
            for net_id in net_ids:
                for port_id in element.get("connected_source_port_ids", []):
                    port = self.ports.get(port_id)
                    if not port:
                        continue
                    owner = self.components.get(port["source_component_id"], {})
                    self.members[net_id].append((owner.get("name", "?"), port.get("name", "?")))

    def net_named(self, name):
        for net_id, net in self.nets.items():
            if net.get("name") == name:
                return net_id
        return None

    def power_nets(self):
        return {net_id for net_id, net in self.nets.items() if net.get("is_power")}

    def nets_of(self, component_name, port_name):
        """Which nets a given pin sits on."""
        return {
            net_id for net_id, members in self.members.items()
            if (component_name, port_name) in members
        }

    def component(self, name):
        for element in self.components.values():
            if element.get("name") == name:
                return element
        return None


def check_i2c_pullups(netlist, buses):
    """
    Every I2C line has a pull-up to a power rail, of a plausible value.

    I2C has no push-pull high side: every device only ever pulls down, so without a pull-up the
    bus never leaves logic 0 and nothing answers. Breakout boards often carry their own, which is
    exactly why this gets left off a board — it works on the bench with one module and fails when
    that module is swapped for one without them.

    `buses` names the nets to check, because no netlist format records that a net is an I2C line.
    """
    failures = []

    for line in buses:
        net_id = netlist.net_named(line)
        if net_id is None:
            failures.append(Failure(
                "i2c-pullups", line, "no net of that name in the built design",
                "nets present: %s" % ", ".join(
                    sorted(n.get("name", "?") for n in netlist.nets.values()))))
            continue

        pulled_up = []
        for component_name, _ in netlist.members[net_id]:
            component = netlist.component(component_name)
            if not component or component.get("ftype") != "simple_resistor":
                continue
            # A resistor is a pull-up only if its other end is on a power rail. One sitting
            # between two signals is a series resistor and does not hold anything high.
            other_ends = set()
            for port_name in ("pin1", "pin2"):
                other_ends |= netlist.nets_of(component_name, port_name)
            if other_ends & netlist.power_nets():
                pulled_up.append((component_name, component.get("resistance")))

        if not pulled_up:
            on_the_net = sorted({name for name, _ in netlist.members[net_id]})
            failures.append(Failure(
                "i2c-pullups", line,
                "nothing pulls it up: no resistor on it reaches a power net",
                "on this net: %s. Add a resistor from %s to a supply."
                % (", ".join(on_the_net) or "nothing", line)))
            continue

        for name, ohms in pulled_up:
            if ohms is None:
                continue
            if not PULLUP_MIN_OHM <= ohms <= PULLUP_MAX_OHM:
                failures.append(Failure(
                    "i2c-pullups", line,
                    "%s is %g ohm, outside the %g-%g band a pull-up usually wants"
                    % (name, ohms, PULLUP_MIN_OHM, PULLUP_MAX_OHM),
                    "too weak and the bus never rises; too strong and a device cannot pull it "
                    "down. Worth checking against the bus capacitance rather than taking this "
                    "band as the answer."))

    return failures


def check_floating_inputs(netlist, watch):
    """
    A named pin that nothing connects to, on a part that is powered.

    A floating CMOS input does not sit at a defined level; it drifts, and on a motor driver that
    means both halves of a bridge can conduct. `watch` names the pins worth caring about, because
    plenty of pins are deliberately left open and reporting all of them is noise.
    """
    failures = []
    for component_name, port_name in watch:
        if netlist.component(component_name) is None:
            continue
        if not netlist.nets_of(component_name, port_name):
            failures.append(Failure(
                "floating-input", "%s.%s" % (component_name, port_name),
                "connects to nothing",
                "an input left floating has no defined level; tie it, or say in the design why "
                "it is deliberately open"))
    return failures


def run(circuit, rules):
    netlist = Netlist(circuit)
    failures = []
    if rules.get("i2c_buses"):
        failures += check_i2c_pullups(netlist, rules["i2c_buses"])
    if rules.get("must_not_float"):
        failures += check_floating_inputs(
            netlist, [tuple(pair) for pair in rules["must_not_float"]])
    return failures


def compare(circuit_path, rules_path):
    """Everything main() does except deciding how to say it."""
    circuit_path = Path(circuit_path)
    if not circuit_path.is_file():
        return could_not_run("no built design at %s" % circuit_path,
                             fix="build it first: `make`, or `tsci build`")

    rules_path = Path(rules_path)
    if not rules_path.is_file():
        return could_not_run(
            "no rules at %s" % rules_path,
            fix="a rules file says which nets are an I2C bus and which pins must not float — "
                "things no netlist format records")

    try:
        circuit = json.loads(circuit_path.read_text())
        rules = json.loads(rules_path.read_text())
    except ValueError as broken:
        return could_not_run("not valid JSON: %s" % broken)

    failures = run(circuit, rules)
    checked = len(rules.get("i2c_buses", [])) + len(rules.get("must_not_float", []))
    return {
        "tool": "compare_design",
        "status": PROBLEMS if failures else OK,
        "design": circuit_path.name,
        "checked": checked,
        "problems": [f.as_data() for f in failures],
    }


def main(argv=None):
    import argparse

    parser = argparse.ArgumentParser(
        prog="compare_design.py",
        description="Compare written rules against the design that was built.")
    parser.add_argument("circuit", help="the built netlist, usually dist/board/circuit.json")
    parser.add_argument("--rules", help="JSON naming what to check (default: .spark/rules.json)")
    parser.add_argument("--json", action="store_true",
                        help="the result as data, for a caller that is not a person")
    args = parser.parse_args(argv)

    default_rules = Path(args.circuit).parent.parent.parent / ".spark/rules.json"
    result = compare(args.circuit, args.rules or default_rules)

    print(json.dumps(result, indent=2) if args.json else render(result))
    return {OK: EXIT_OK, PROBLEMS: EXIT_PROBLEMS, COULD_NOT_RUN: EXIT_COULD_NOT_RUN}[
        result["status"]]


if __name__ == "__main__":
    sys.exit(main())
