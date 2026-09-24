#!/usr/bin/env python3
"""
Does the built board obey physics, or only itself?

    check_physics.py dist/board/circuit.json --rules .spark/rules.json

Every other check in this plugin compares one part of a design to another part of the same
design. That catches drift and nothing else: a board can be perfectly self-consistent and still
melt. Four defects got through a fully green check suite on a real project, and all four were
arithmetic nobody did:

  * a 220 uF 4 V tantalum on a 6.4 V battery rail — a part that fails SHORT when overvolted,
    across a 4xAA pack, inside a plastic bin;
  * every trace on the board at 0.15 mm, including ~83 mm of motor supply, good for about 0.6 A;
  * a 0.33 ohm current shunt in an 0805 (0.125 W) that dissipates 0.33 W at a 1 A stall;
  * I2C pull-ups sized with the wrong rise-time constant for a bus running at 400 kHz.

Each was written down correctly in a prose comment and never evaluated. This evaluates them.

WHAT IT NEEDS FROM YOU, AND WHY
The netlist knows a resistor is 0.33 ohm. It does not know that 2 A flows through it, that the
rail is 6.4 V, or that the trace is expected to carry a motor. Those are facts about the world,
so they come from the rules file, and a rail with no stated current is REPORTED rather than
assumed safe — an unchecked rail must never look like a passing one.

WHAT IT REFUSES TO DO
It does not invent currents. Where the rules file says a value is unmeasured, every finding that
depends on it is reported as `needs-measurement`, not as a pass and not as a failure. A project
whose worst risk is an unmeasured number should be told that, not given a green tick.
"""

import argparse
import json
import math
import sys
from pathlib import Path

EXIT_OK, EXIT_PROBLEMS, EXIT_COULD_NOT_RUN = 0, 1, 2
OK, PROBLEMS, COULD_NOT_RUN = "ok", "problems", "could-not-run"

#: IPC-2221 external-layer constant: I = k * dT^0.44 * A^0.725, with A in square mils.
IPC_K_EXTERNAL = 0.048
IPC_DT_EXPONENT = 0.44
IPC_AREA_EXPONENT = 0.725

#: 1 oz/ft^2 finished copper, the default on every cheap 2-layer process.
COPPER_THICKNESS_MM = 0.035
MM_PER_MIL = 0.0254

#: A rise on an open-drain bus is specified between these fractions of the supply, NOT from zero.
#: t = R*C*ln((1-lo)/(1-hi)) = 0.8473*R*C. Using ln(1/(1-hi)) = 1.204 instead overstates the rise
#: time by 42% and is an easy mistake to make; it was made on the project this came from.
I2C_RISE_FROM, I2C_RISE_TO = 0.3, 0.7
I2C_RISE_CONSTANT = math.log((1 - I2C_RISE_FROM) / (1 - I2C_RISE_TO))

#: Maximum rise time the I2C specification allows, by bus speed.
I2C_MAX_RISE_NS = {100_000: 1000, 400_000: 300, 1_000_000: 120}

#: A capacitor should not be operated near its rating. Electrolytics and especially tantalums are
#: derated hard because a tantalum above its rating fails short rather than open.
VOLTAGE_DERATING = {"tantalum": 2.0, "electrolytic": 1.5, "ceramic": 1.5, "unknown": 2.0}

#: What a chip resistor of each size can dissipate, in watts. Conservative, standard values.
PACKAGE_POWER_W = {"0402": 0.063, "0603": 0.1, "0805": 0.125, "1206": 0.25,
                   "1210": 0.5, "2010": 0.75, "2512": 1.0}


class Finding:
    """One thing physics says about this board."""

    def __init__(self, rule, subject, detail, severity="problem", fix=None):
        self.rule, self.subject, self.detail = rule, subject, detail
        self.severity, self.fix = severity, fix

    def as_data(self):
        return {"rule": self.rule, "subject": self.subject, "detail": self.detail,
                "severity": self.severity, "fix": self.fix}


def trace_current_capacity_a(width_mm, rise_c):
    """IPC-2221 external-layer current for a given trace width and temperature rise."""
    area_mils2 = (width_mm / MM_PER_MIL) * (COPPER_THICKNESS_MM / MM_PER_MIL)
    return IPC_K_EXTERNAL * (rise_c ** IPC_DT_EXPONENT) * (area_mils2 ** IPC_AREA_EXPONENT)


def width_for_current_mm(current_a, rise_c):
    """The inverse: the narrowest trace that carries this current within a temperature rise."""
    area_mils2 = (current_a / (IPC_K_EXTERNAL * rise_c ** IPC_DT_EXPONENT)) ** (1 / IPC_AREA_EXPONENT)
    return area_mils2 * MM_PER_MIL * MM_PER_MIL / COPPER_THICKNESS_MM


class Board:
    """Just enough of the built netlist to do arithmetic on."""

    def __init__(self, circuit):
        self.elements = circuit
        self.components = {e["source_component_id"]: e
                           for e in circuit if e["type"] == "source_component"}
        self.ports = {e["source_port_id"]: e for e in circuit if e["type"] == "source_port"}
        self.nets = {e["source_net_id"]: e for e in circuit if e["type"] == "source_net"}
        self.pcb_components = {e["pcb_component_id"]: e
                               for e in circuit if e["type"] == "pcb_component"}

        #: net name -> [(component name, port name)]
        self.members = {}
        for element in circuit:
            if element["type"] != "source_trace":
                continue
            for net_id in element.get("connected_source_net_ids", []):
                net = self.nets.get(net_id)
                if not net:
                    continue
                name = net.get("name")
                for port_id in element.get("connected_source_port_ids", []):
                    port = self.ports.get(port_id)
                    if not port:
                        continue
                    owner = self.components.get(port["source_component_id"], {})
                    self.members.setdefault(name, []).append(
                        (owner.get("name", "?"), port.get("name", "?")))

    def named(self, component_name):
        for element in self.components.values():
            if element.get("name") == component_name:
                return element
        return None

    def components_on(self, net_name):
        return sorted({name for name, _ in self.members.get(net_name, [])})

    def footprint_of(self, component_name):
        """The package string, e.g. '0805'. Taken from the PCB side, which is what is built."""
        source = self.named(component_name)
        if not source:
            return None
        for pcb in self.pcb_components.values():
            if pcb.get("source_component_id") == source["source_component_id"]:
                return (pcb.get("footprinter_string") or "").strip() or None
        return None

    def narrowest_by_net(self):
        """
        The narrowest routed segment ON EACH NET.

        Per net, not per board. The first version of this compared every rail against the
        board's globally narrowest trace, which answers a question nobody asked: once the motor
        loop is widened and the signals are not, the global minimum says the motor rail is thin
        when it is not. A rail is only as good as its own narrowest segment.
        """
        nets_of_trace = {}
        for element in self.elements:
            if element["type"] != "source_trace":
                continue
            names = [self.nets[n].get("name") for n in element.get("connected_source_net_ids", [])
                     if n in self.nets]
            nets_of_trace[element["source_trace_id"]] = names

        narrowest = {}
        for element in self.elements:
            if element["type"] != "pcb_trace":
                continue
            widths = [step["width"] for step in element.get("route", []) if "width" in step]
            if not widths:
                continue
            for net_name in nets_of_trace.get(element.get("source_trace_id"), []):
                narrowest[net_name] = min(narrowest.get(net_name, float("inf")), min(widths))
        return narrowest


def check_trace_currents(board, rails, rise_c):
    """Can the copper carry what the rail is expected to carry?"""
    findings = []
    narrowest = board.narrowest_by_net()
    if not narrowest:
        return [Finding("trace-current", "the board", "no routed traces to check",
                        severity="could-not-run")]

    for rail, spec in sorted(rails.items()):
        current = spec.get("max_current_a")
        if current is None:
            findings.append(Finding(
                "trace-current", rail,
                "no maximum current stated, so nothing here can be verified",
                severity="needs-measurement",
                fix="measure it, then put it in the rules file as max_current_a"))
            continue
        if spec.get("served_by_pour"):
            # A pour is not sized by trace width, so this check does not apply. It is recorded
            # rather than silently skipped, because "no finding" and "not checked" are different
            # answers and only one of them is reassuring.
            findings.append(Finding(
                "trace-current", rail,
                "carries up to %.2f A and is served by a copper pour, which this check cannot "
                "size" % current,
                severity="needs-measurement",
                fix="confirm the pour actually reaches every return on a 2-layer board with "
                    "components on top — a pour broken into islands by traces is not a plane"))
            continue

        width = narrowest.get(rail)
        if width is None:
            findings.append(Finding(
                "trace-current", rail,
                "carries up to %.2f A but has no routed trace of its own — if it is served by "
                "a copper pour, say so in the rules file" % current,
                severity="needs-measurement"))
            continue
        capacity = trace_current_capacity_a(width, rise_c)
        if current <= capacity:
            continue
        needed = width_for_current_mm(current, rise_c)
        findings.append(Finding(
            "trace-current", rail,
            "carries up to %.2f A, but its narrowest segment is %.2f mm, good for %.2f A at a "
            "%g C rise" % (current, width, capacity, rise_c),
            fix="widen this net to at least %.2f mm, or pour it" % needed))
    return findings


def check_capacitor_voltages(board, rails):
    """A capacitor on a rail must be rated well above it — a tantalum fails SHORT if it is not."""
    findings = []
    for rail, spec in sorted(rails.items()):
        volts = spec.get("nominal_volts")
        if volts is None:
            continue
        for component_name in board.components_on(rail):
            component = board.named(component_name)
            if not component or component.get("ftype") != "simple_capacitor":
                continue
            rating = component.get("max_voltage_rating")
            kind = (spec.get("capacitor_chemistry") or "unknown").lower()
            margin = VOLTAGE_DERATING.get(kind, VOLTAGE_DERATING["unknown"])
            required = volts * margin
            if rating is None:
                findings.append(Finding(
                    "capacitor-voltage", component_name,
                    "sits on %s (%.1f V) with no stated voltage rating" % (rail, volts),
                    fix="give it maxVoltageRating; at %gx derating this rail needs >= %.0f V. "
                        "A part with no stated rating is chosen by whatever the supplier matches, "
                        "which is how a 4 V tantalum lands on a 6 V rail"
                        % (margin, required)))
            elif float(rating) < required:
                findings.append(Finding(
                    "capacitor-voltage", component_name,
                    "is rated %.1f V on a %.1f V rail (%s)" % (float(rating), volts, rail),
                    fix="use >= %.0f V (%gx derating)" % (required, margin)))
    return findings


def check_resistor_power(board, rails):
    """Does a resistor's package survive what it dissipates?"""
    findings = []
    for rail, spec in sorted(rails.items()):
        current = spec.get("max_current_a")
        if current is None:
            continue
        for component_name in board.components_on(rail):
            component = board.named(component_name)
            if not component or component.get("ftype") != "simple_resistor":
                continue
            ohms = component.get("resistance")
            if not ohms:
                continue
            watts = current * current * float(ohms)
            footprint = board.footprint_of(component_name) or ""
            rated = next((w for size, w in PACKAGE_POWER_W.items() if footprint.startswith(size)),
                         None)
            if rated is None:
                continue
            if watts > rated:
                findings.append(Finding(
                    "resistor-power", component_name,
                    "dissipates %.2f W at %.2f A through %g ohm, but a %s is rated %.3f W"
                    % (watts, current, float(ohms), footprint, rated),
                    fix="use a package rated above %.2f W, or lower the resistance" % watts))
    return findings


def check_i2c_rise_time(board, buses, bus_hz, capacitance_pf):
    """Can the pull-up actually pull the bus up in the time the bus speed allows?"""
    findings = []
    limit_ns = I2C_MAX_RISE_NS.get(bus_hz)
    if limit_ns is None:
        return [Finding("i2c-rise-time", "the bus",
                        "no rise-time limit known for %g Hz" % bus_hz, severity="could-not-run")]

    for line in buses:
        pullups = []
        for component_name in board.components_on(line):
            component = board.named(component_name)
            if component and component.get("ftype") == "simple_resistor":
                pullups.append((component_name, float(component.get("resistance") or 0)))
        if not pullups:
            continue
        # Parallel pull-ups pull harder, so the effective resistance is what matters.
        conductance = sum(1 / ohms for _, ohms in pullups if ohms)
        effective = 1 / conductance if conductance else 0
        rise_ns = I2C_RISE_CONSTANT * effective * capacitance_pf * 1e-12 * 1e9
        if rise_ns > limit_ns:
            largest = limit_ns * 1e-9 / (I2C_RISE_CONSTANT * capacitance_pf * 1e-12)
            findings.append(Finding(
                "i2c-rise-time", line,
                "%.0f ohm against %g pF rises in %.0f ns, but %g kHz allows %d ns"
                % (effective, capacitance_pf, rise_ns, bus_hz / 1000, limit_ns),
                fix="use <= %.0f ohm, or drop the bus to a slower mode — changing the bus "
                    "speed is free, changing a resistor costs a board revision"
                    % largest))
    return findings


def run(circuit, rules):
    board = Board(circuit)
    physics = rules.get("physics") or {}
    rails = physics.get("rails") or {}
    rise_c = physics.get("trace_temperature_rise_c", 10)

    findings = []
    findings += check_trace_currents(board, rails, rise_c)
    findings += check_capacitor_voltages(board, rails)
    findings += check_resistor_power(board, rails)
    if rules.get("i2c_buses") and physics.get("i2c_hz"):
        findings += check_i2c_rise_time(
            board, rules["i2c_buses"], physics["i2c_hz"],
            physics.get("i2c_bus_capacitance_pf", 50))
    return findings


def render(result):
    if result["status"] == COULD_NOT_RUN:
        return "could not run: %s" % result["reason"]
    lines = ["%s: checked against physics, not against itself" % result["design"]]
    if not result["findings"]:
        lines.append("\nnothing to answer for.")
        return "\n".join(lines)

    by_severity = {}
    for finding in result["findings"]:
        by_severity.setdefault(finding["severity"], []).append(finding)
    for severity in ("problem", "needs-measurement", "could-not-run"):
        group = by_severity.get(severity) or []
        if not group:
            continue
        lines.append("\n%d %s:" % (len(group), severity))
        for finding in group:
            lines.append("  [%s] %s: %s" % (finding["rule"], finding["subject"], finding["detail"]))
            if finding.get("fix"):
                lines.append("      %s" % finding["fix"])
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="check_physics.py",
        description="Check a built board against physics rather than against itself.")
    parser.add_argument("circuit", help="the built netlist, usually dist/board/circuit.json")
    parser.add_argument("--rules", help="JSON naming rails, currents and voltages")
    parser.add_argument("--json", action="store_true", help="the result as data")
    args = parser.parse_args(argv)

    circuit_path = Path(args.circuit)
    rules_path = Path(args.rules or circuit_path.parent.parent.parent / ".spark/rules.json")
    for path, what in ((circuit_path, "built design"), (rules_path, "rules")):
        if not path.is_file():
            result = {"tool": "check_physics", "status": COULD_NOT_RUN,
                      "reason": "no %s at %s" % (what, path)}
            print(json.dumps(result, indent=2) if args.json else render(result))
            return EXIT_COULD_NOT_RUN

    findings = run(json.loads(circuit_path.read_text()), json.loads(rules_path.read_text()))
    problems = [f for f in findings if f.severity == "problem"]
    result = {
        "tool": "check_physics",
        "status": PROBLEMS if problems else OK,
        "design": circuit_path.name,
        "findings": [f.as_data() for f in findings],
    }
    print(json.dumps(result, indent=2) if args.json else render(result))
    return EXIT_PROBLEMS if problems else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
