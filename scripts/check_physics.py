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

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

import copper  # noqa: E402


#: `res0603` -> `0603`. check_footprints already works this out, and the package table here was
#: keyed on the bare size while the engine emits the prefixed form — so even with the footprint
#: resolved, nothing matched. One copy, imported — plainly, under the `sys.path` line that already
#: made that possible; the file-path loader it replaced made a second copy of the module every
#: time (audit A7).
from check_footprints import package_of  # noqa: E402

from outcomes import EXIT_OK, EXIT_PROBLEMS, EXIT_COULD_NOT_RUN, EXIT_FOR  # noqa: E402
from outcomes import OK, PROBLEMS, COULD_NOT_RUN  # noqa: E402

#: The copper arithmetic lives in its own module, because `emit_board` sizes traces by exactly
#: the formula this file judges them with. Two copies is how a board passes its own tool and
#: fails a fab; `emit_board` reaching in here by importlib is how that becomes untestable.
COPPER_THICKNESS_MM = copper.COPPER_THICKNESS_MM
MM_PER_MIL = copper.MM_PER_MIL

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


#: Kept as names so existing call sites read unchanged; the arithmetic is `copper`'s.
trace_current_capacity_a = copper.current_capacity_a
width_for_current_mm = copper.width_for_current_mm


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

    def net_names(self):
        """Every net's name, for rules that ask whether a thing exists before asking about it."""
        return [net.get("name") for net in self.nets.values() if net.get("name")]

    def footprint_of(self, component_name):
        """
        The package string, e.g. `res0603`.

        Read from `cad_component` first, falling back to `pcb_component` for older netlists. This
        looked only at `pcb_component`, where the engine no longer puts it: measured against the
        reference board it resolved 0 of 28 components, so every rule downstream of it examined
        nothing. Exactly the defect fixed in check_footprints, in a second file, which is why
        that fix needed to be an audit rather than a patch.
        """
        source = self.named(component_name)
        if not source:
            return None
        wanted = source["source_component_id"]
        for element in self.elements:
            if element.get("type") not in ("cad_component", "pcb_component"):
                continue
            if element.get("source_component_id") != wanted:
                continue
            footprint = (element.get("footprinter_string") or "").strip()
            if footprint:
                return footprint
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

        segments = {}
        for element in self.elements:
            if element["type"] != "pcb_trace":
                continue
            route = element.get("route", [])
            measured = []
            for index, step in enumerate(route):
                if "width" not in step:
                    continue
                length = None
                if index + 1 < len(route):
                    nxt = route[index + 1]
                    if None not in (step.get("x"), step.get("y"), nxt.get("x"), nxt.get("y")):
                        length = math.dist((step["x"], step["y"]), (nxt["x"], nxt["y"]))
                measured.append((step["width"], length))
            for net_name in nets_of_trace.get(element.get("source_trace_id"), []):
                segments.setdefault(net_name, []).extend(measured)

        # The width a net SUSTAINS, not the narrowest copper anywhere on it.
        #
        # Measured on a generated board: asking the router for 1.50 mm produced 86 segments at
        # 1.50 and six between 0.12 and 0.85 mm LONG at 1.20 mm wide — every one the last step
        # into a 1.2 mm pad. Judging those by a formula for long uniform traces called a
        # correctly sized 2.9 A rail unbuildable, and the remedy it printed — "widen this net" —
        # was for a trace that was already wide enough.
        #
        # A neck that short cannot reach a steady temperature: it is bonded to a pad and a plated
        # barrel, both heatsinks. The constriction is real and it belongs to the PAD, which is
        # `check_footprints`' subject. Falling back to the absolute minimum when a net is ALL
        # necks keeps a genuinely tiny net from passing by having no long segment to judge.
        narrowest = {}
        for net_name, measured in segments.items():
            sustained = copper.sustained_width_mm(measured)
            if sustained is None:
                widths = [width for width, _ in measured if width]
                if not widths:
                    continue
                sustained = min(widths)
            narrowest[net_name] = sustained
        return narrowest


def check_trace_currents(board, rails, rise_c):
    """Can the copper carry what the rail is expected to carry?"""
    findings = []
    narrowest = board.narrowest_by_net()

    # Deliberately no early return when nothing is routed. An earlier version bailed out here,
    # which preempted every per-rail rule below — so a board whose returns are all poured, or
    # one checked before routing, reported "could not run" instead of what is actually known
    # about each rail. Absence of copper is a fact about a rail, not a reason to stop.
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
    """
    Whether a resistor's package survives what it dissipates — which a netlist cannot answer.

    This computed `I^2 * R` using the RAIL's maximum current for every resistor on that rail. That
    is only true of a resistor in series with the whole rail. For a 100k pull-up on a 1.5 A rail
    it claims 225 kW. The mirror error is just as bad: `V^2 / R` over the rail voltage is a valid
    upper bound for a pull-up and absurd for a 0.1 ohm shunt, which never sees the full rail.

    **A netlist records neither the current through a resistor nor the voltage across it.** Both
    depend on topology the design does not state. So this rule cannot decide, and the honest
    answer is to say how many it could not assess rather than to compute a number that is wrong
    in one direction or the other.

    It never fired, in either direction, because `footprint_of` returned None for every component
    and the package table was keyed `0603` while the engine emits `res0603`. Three independent
    faults, and being broken is the only reason nobody noticed the arithmetic was wrong.

    To make this a real check, a design has to state the current through a resistor — which is a
    thing a person knows and a netlist does not.
    """
    findings = []
    unassessable = []
    for rail, spec in sorted(rails.items()):
        for component_name in board.components_on(rail):
            component = board.named(component_name)
            if not component or component.get("ftype") != "simple_resistor":
                continue
            if not component.get("resistance"):
                continue
            stated = (spec.get("resistor_currents") or {}).get(component_name)
            package = package_of(board.footprint_of(component_name))
            rated = PACKAGE_POWER_W.get(package)

            if stated is None or rated is None:
                unassessable.append(component_name)
                continue

            watts = stated * stated * float(component["resistance"])
            if watts > rated:
                findings.append(Finding(
                    "resistor-power", component_name,
                    "dissipates %.3f W at the %.2f A this design states for it, through %g ohm, "
                    "but a %s is rated %.3f W"
                    % (watts, stated, float(component["resistance"]), package, rated),
                    fix="use a package rated above %.3f W, or lower the resistance" % watts))

    if unassessable:
        findings.append(Finding(
            "resistor-power", "%d resistor(s)" % len(unassessable),
            "could not be assessed: %s. A netlist records neither the current through a resistor "
            "nor the voltage across it, and both depend on topology the design does not state"
            % ", ".join(sorted(unassessable)),
            fix="state the current in the rules file under the rail's `resistor_currents`, for "
                "any resistor whose dissipation actually matters — a shunt, an LED series "
                "resistor, a bleeder. A pull-up almost never does.",
            severity="could-not-run"))
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
    """
    Every physics rule, and an honest answer about the ones that could not run.

    This returned nothing at all when the rules file was empty, and an empty rules file is
    exactly what `spark init` writes. So a freshly-initialised project asked about a real
    415-element board and was told "nothing to answer for" — which `check_all` rendered as
    `[ok  ] physics   the board obeys physics, not just itself`.

    `commands/init.md` promises the opposite in as many words: "a check reading a null reports it
    as unverifiable rather than passing it". It did not, and the default state of every new
    project was the state where it did not.

    Each rule below says what it needs. Missing inputs are `could-not-run` findings naming the
    field to fill, because a rule that never ran must not be indistinguishable from one that ran
    and found nothing.
    """
    board = Board(circuit)
    physics = rules.get("physics") or {}
    rails = physics.get("rails") or {}
    rise_c = physics.get("trace_temperature_rise_c", 10)

    findings = []
    if rails:
        findings += check_trace_currents(board, rails, rise_c)
        findings += check_capacitor_voltages(board, rails)
        findings += check_resistor_power(board, rails)
    else:
        findings.append(Finding(
            "rails-not-stated", "physics.rails",
            "no rail is described, so trace current, capacitor derating and resistor power were "
            "not checked at all — three of this tool's four rules",
            fix="fill physics.rails in the rules file: each net's nominal_volts and "
                "max_current_a. `spark init` writes the names from the built design and leaves "
                "the numbers null, which is where they have stayed.",
            severity="could-not-run"))

    buses, hertz = rules.get("i2c_buses"), physics.get("i2c_hz")
    # Only ask about I2C when there is evidence of some. Nagging a board that has no bus is how
    # a check earns a reputation for noise — and the first version of this fix did exactly that,
    # while its own remedy text said an empty list should stop it asking.
    looks_like_a_bus = {name.upper() for name in board.net_names()} & {"SDA", "SCL"}
    if buses and hertz:
        findings += check_i2c_rise_time(
            board, buses, hertz, physics.get("i2c_bus_capacitance_pf", 50))
    elif buses or looks_like_a_bus:
        missing = " and ".join(
            [name for name, value in (("i2c_buses", buses), ("physics.i2c_hz", hertz))
             if not value])
        findings.append(Finding(
            "i2c-rise-time", "the I2C bus",
            "this board has %s, but %s is not stated, so the rise time was not checked. A "
            "pull-up that is fine at 100 kHz is too weak at 400 kHz, and nothing here can tell "
            "which you are running"
            % (" and ".join(sorted(looks_like_a_bus)) or "a bus named in the rules", missing),
            fix="name the bus nets in i2c_buses and put the clock in physics.i2c_hz",
            severity="could-not-run"))
    return findings


def render(result):
    # Two different could-not-runs reach here: one before any rule ran, which carries a `reason`
    # and nothing else, and one from a run whose findings were all could-not-run, which carries
    # findings. Reading `reason` unconditionally made the second a KeyError the moment the status
    # started telling the truth (P34).
    if result["status"] == COULD_NOT_RUN and "reason" in result:
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
    # A rule that could not look has approved nothing. This built both the status and the exit
    # code from `problems` alone, so every `could-not-run` this file emits — an unstated rail, a
    # resistor whose current no netlist records — was invisible to a caller, and the script whose
    # own docstring says an unchecked rail must never look like a passing one answered
    # `status: ok`, exit 0, over findings that were every one of them could-not-run. `check_all`'s
    # wrapper splits the severities itself, which is why this survived: it was wrong only where
    # the script is run directly, which is exactly how the smart bin's `make check` runs it.
    unchecked = [f for f in findings if f.severity == COULD_NOT_RUN]
    status = PROBLEMS if problems else (COULD_NOT_RUN if unchecked else OK)
    result = {
        "tool": "check_physics",
        "status": status,
        "design": circuit_path.name,
        "findings": [f.as_data() for f in findings],
    }
    print(json.dumps(result, indent=2) if args.json else render(result))
    return EXIT_FOR[status]


if __name__ == "__main__":
    sys.exit(main())
