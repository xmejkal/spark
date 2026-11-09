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

import math

from spark.design import copper
from spark.design import fab
from spark.design.power_rails import GROUND_NETS
from spark.checks import check_codes
from spark.checks.build_check import package_of
from spark.core.outcomes import COULD_NOT_RUN
from spark.core.result import Refusal
from spark.checks.physics_board import Board

# `package_of` (`res0603` -> `0603`) is build_check's one copy: a table keyed on the bare size matched nothing (A7).

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

#: What a chip resistor of each size can dissipate. THE SAME table `build_check` judges by:
#: it was a second copy here, so a package added to one checker was missing from the other and
#: nothing said so.
PACKAGE_POWER_W = fab.part("package_power_w")

#: The resistor bound (P197) clears a resistor only at half its package rating: the usual derating, and room for a
#: supply above its typical voltage. VDD33 is 3.6 V at most against 3.3 V typical, which is 19% more power.
RESISTOR_POWER_DERATING = 2.0

#: The only severities a finding may carry. Free text let "problems" vanish: nothing rendered,
#: counted or filtered it (P143). `could-not-run` is the outcome word of the same name.
PROBLEM = "problem"
NEEDS_MEASUREMENT = "needs-measurement"
SEVERITIES = (PROBLEM, NEEDS_MEASUREMENT, COULD_NOT_RUN)


class Finding:
    """One thing physics says about this board; an unknown severity makes it a could-not-run."""

    def __init__(self, rule, subject, detail, severity=PROBLEM, fix=None):
        if severity not in SEVERITIES:
            detail = ("rule %s wrote severity %r, not one of %s — a bug in spark, so the rule is "
                      "unchecked (it said: %s)" % (rule, severity, " / ".join(SEVERITIES), detail))
            severity = COULD_NOT_RUN
        self.rule, self.subject, self.detail = rule, subject, detail
        self.severity, self.fix = severity, fix

    def as_data(self):
        return {"rule": self.rule, "subject": self.subject, "detail": self.detail,
                "severity": self.severity, "fix": self.fix}


#: Kept as names so existing call sites read unchanged; the arithmetic is `copper`'s.
trace_current_capacity_a = copper.current_capacity_a
width_for_current_mm = copper.width_for_current_mm


def check_trace_currents(board, rails, rise_c, loads=None):
    """
    Can the copper carry what the rail is expected to carry?

    A stated `max_current_a` comes first, because a measurement beats a sum. Where the rules leave
    it null, the part records' own figures are used when they are complete (P52): sizing was
    asking for a number the records already held.
    """
    findings = []
    narrowest = board.narrowest_by_net()
    loads = loads or {}

    # No early return when nothing is routed: a board whose returns are all poured, or one checked before routing, is
    # told what is known about each rail, not "could not run". Absence of copper is a fact about a rail.
    for rail, spec in sorted(rails.items()):
        current, summed, origin = spec.get("max_current_a"), loads.get(rail), ""
        if current is None and summed and summed["complete"]:
            current, origin = summed["amps"], " (summed from the part records)"
        if current is None:
            still_open = ("; the part records leave it open: " + ", ".join(
                gap.split(":")[0] for gap in summed["missing"]) if summed else "")
            findings.append(Finding(
                "trace-current", rail,
                "no maximum current stated, so nothing here can be verified" + still_open,
                severity="needs-measurement",
                fix="measure it, then put it in the rules file as max_current_a"))
            continue
        if spec.get("served_by_pour"):
            # A pour is not sized by trace width, so this check does not apply. It is recorded, not skipped:
            # "no finding" and "not checked" are different answers, and only one of them is reassuring.
            findings.append(Finding(
                "trace-current", rail,
                "carries up to %.2f A%s and is served by a copper pour, which this check cannot "
                "size" % (current, origin),
                severity="needs-measurement",
                fix="confirm the pour actually reaches every return on a 2-layer board with "
                    "components on top — a pour broken into islands by traces is not a plane"))
            continue
        findings += copper_findings(rail, current, origin, narrowest.get(rail), rise_c)
    return findings


def copper_findings(rail, current, origin, width, rise_c):
    """Value: the Finding of a rail's routed copper, `width` its narrowest segment or None, carrying `current`; [] when it can."""
    if width is None:
        return [Finding(
            "trace-current", rail,
            "carries up to %.2f A%s but has no routed trace of its own — if it is served by "
            "a copper pour, say so in the rules file" % (current, origin),
            severity="needs-measurement")]
    capacity = trace_current_capacity_a(width, rise_c)
    if current <= capacity:
        return []
    needed = width_for_current_mm(current, rise_c)
    return [Finding(
        "trace-current", rail,
        "carries up to %.2f A%s, but its narrowest segment is %.2f mm, good for %.2f A at a "
        "%g C rise" % (current, origin, width, capacity, rise_c),
        fix="widen this net to at least %.2f mm, or pour it" % needed)]


def current_text(amps):
    """Under an amp in milliamps: "0.01 A" was a 15 mA flow meter on the irrigation board."""
    return "%.2f A" % amps if amps >= 1 else "%.0f mA" % (amps * 1000)


def check_rail_supply(loads):
    """
    Can each rail's source deliver what its members draw? (P52)

    P29 answered *does a trace reach a supply*; nothing asked *can that supply carry what is on
    it*. `loads` is `power_rails.rail_loads`: the figures each power pin's record names, summed. A
    load nobody stated is named rather than taken as zero; a sum that fits on figures nobody
    verified says what it rests on. A rail with no single source is the generator's to report.
    """
    findings = []
    for rail, load in sorted(loads.items()):
        supply = load["supply"]
        if supply is None:
            continue
        drawn, rated = load["amps"], supply["amps"]
        if rated is not None and drawn > rated:
            findings.append(Finding(
                "rail-supply", rail,
                "draws at least %s, more than %s is rated for (%s)"
                % (current_text(drawn), supply["who"], current_text(rated)),
                fix="a bigger supply, or a second rail for the heaviest load"))
        elif load["missing"] or rated is None:
            gaps = load["missing"] + ([] if rated is not None else
                                      ["%s: %s" % (supply["who"], supply["why"])])
            findings.append(Finding(
                "rail-supply", rail,
                "draws at least %s; not stated: %s" % (current_text(drawn), "; ".join(gaps)),
                severity="could-not-run",
                fix="state each figure in its part record and name it from the pin's `draws` "
                    "or `can_supply`"))
        elif load["unverified"] or not supply["verified"]:
            resting = load["unverified"] + ([] if supply["verified"] else
                                            ["%s: %s" % (supply["who"], supply["why"])])
            findings.append(Finding(
                "rail-supply", rail,
                "draws %s of %s, resting on figures nobody has verified: %s"
                % (current_text(drawn), current_text(rated), "; ".join(resting)),
                severity="needs-measurement",
                fix="verify each at its source, or measure the rail"))
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


def check_resistor_power(board, rails, loads=None, bus_nets=()):
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

    To make this a real check, a design has to state the current through a resistor — which is a
    thing a person knows and a netlist does not.

    One upper bound needs no topology (P197): no resistor sees more than the span between the
    highest and the lowest voltage on the board's named nets. So a package that survives `V^2 / R`
    at that span, at half its rating, is safe. A 10k pull-up at 3.3 V is 1.1 mW, so a fresh
    button-and-LED board clears. The bound only clears: above it the resistor stays unassessed,
    because for a shunt the bound is absurd, not a finding.

    It assumes every voltage source reaches the board through a named net, which is how spark's
    generator wires every supply (`net.X`). So the bound runs only when the part records were read
    (`loads`, which `check_all --project` passes): the board is then spark's own design. Without
    them, nothing clears by it. A supply that a hand-edited `board.tsx` joins by a bare trace is a
    voltage neither this file nor the records can see, and it breaks the assumption.

    Every resistor on the board, not only one with an end on a rail (P197, the PO's choice of
    2026-10-12): an LED's series resistor sits between a GPIO and the LED, on no rail, and was
    never looked at while physics answered `ok`. Its stated current goes under any rail's
    `resistor_currents`.
    """
    findings = []
    stated_currents = {}
    for spec in rails.values():
        for name, amps in (spec.get("resistor_currents") or {}).items():
            stated_currents.setdefault(name, amps)
    resistors = {component["name"]: stated_currents.get(component["name"])
                 for component in board.components.values()
                 if component.get("ftype") == "simple_resistor" and component.get("resistance")
                 and component.get("name")}

    span, unverified, unvoltaged = (None, [], []) if loads is None else \
        rail_span_volts(rails, loads, set(board.net_names()), bus_nets)
    unassessable, resting = [], []
    for component_name, stated in sorted(resistors.items()):
        ohms = float(board.named(component_name)["resistance"])
        package = package_of(board.footprint_of(component_name))
        rated = PACKAGE_POWER_W.get(package)

        if stated is None and rated is not None and span is not None \
                and span * span / ohms <= rated / RESISTOR_POWER_DERATING:
            if unverified:
                resting.append(component_name)
            continue
        if stated is None or rated is None:
            unassessable.append(component_name)
            continue

        watts = stated * stated * ohms
        if watts > rated:
            findings.append(Finding(
                "resistor-power", component_name,
                "dissipates %.3f W at the %.2f A this design states for it, through %g ohm, "
                "but a %s is rated %.3f W"
                % (watts, stated, ohms, package, rated),
                fix="use a package rated above %.3f W, or lower the resistance" % watts))

    if unassessable:
        findings.append(Finding(
            "resistor-power", "%d resistor(s)" % len(unassessable),
            "could not be assessed: %s. A netlist records neither the current through a resistor "
            "nor the voltage across it, and both depend on topology the design does not state%s"
            % (", ".join(unassessable),
               "; no voltage is stated for %s, so no bound could clear them" % ", ".join(unvoltaged)
               if unvoltaged else ""),
            fix=("state nominal_volts for %s in the rules file, and every resistor whose package "
                 "survives the board's whole voltage span clears. For one that still does not, "
                 % ", ".join(unvoltaged) if unvoltaged else "")
                + "state the current in the rules file under any rail's `resistor_currents`, for "
                "any resistor whose dissipation actually matters — a shunt, an LED series "
                "resistor, a bleeder. A pull-up almost never does.",
            severity="could-not-run"))
    if resting:
        findings.append(Finding(
            "resistor-power", "%d resistor(s)" % len(resting),
            "%s: within half its package rating with the board's whole %g V span across it, "
            "resting on figures nobody has verified: %s"
            % (", ".join(resting), span, "; ".join(unverified)),
            fix="verify each at its source, or state the rail's nominal_volts in the rules file",
            severity=NEEDS_MEASUREMENT))
    return findings


def rail_span_volts(rails, loads=None, nets=None, bus_nets=()):
    """
    The most voltage two nets of this board can put across a resistor, the unverified figures
    that rests on, and the nets with no voltage at all (P197).

    Every named net needs a voltage, because the one left out could be the highest or the lowest.
    A voltage the rules state beats the record's, as a measurement beats a datasheet; ground is
    zero. An I2C line sits between ground and the rail its pull-up goes to, so it needs none. A
    rail only the records know, such as a module's 5 V pad that nothing wires, is not one of
    `nets` and so reaches no resistor. The span is None when a net has no voltage, or when no net
    but ground has one, so the caller assesses nothing on a guess.
    """
    loads = loads or {}
    wired = {net for net in loads if nets is None or net in nets}
    highest = lowest = 0.0
    unverified, unvoltaged = [], []
    for net in sorted((set(rails) | wired | set(nets or ())) - set(bus_nets)):
        if net.upper() in GROUND_NETS:
            continue
        volts = volts_in((rails.get(net) or {}).get("nominal_volts"))
        if volts is None:
            supply = (loads.get(net) or {}).get("supply") or {}
            held = supply.get("volts") or {}
            volts = volts_in(held.get("value"))
            if volts is not None and not held.get("verified"):
                unverified.append("%s: %s" % (supply.get("who"), held.get("why")))
        if volts is None:
            unvoltaged.append(net)
            continue
        highest, lowest = max(highest, volts), min(lowest, volts)
    if unvoltaged or highest == lowest:
        return None, [], unvoltaged
    return highest - lowest, unverified, []


def volts_in(value):
    """A stated voltage as a number, or None for null or anything that is not one ("3V3")."""
    if isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


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


def run(circuit, rules, loads=None):
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
    # `loads` is None when the caller had no part records to offer — this file's own CLI, which
    # is handed a netlist and a rules file only. `check_all --project` passes them, or says why not.
    if loads is not None:
        findings += check_rail_supply(loads)
    if rails:
        findings += check_trace_currents(board, rails, rise_c, loads)
        findings += check_capacitor_voltages(board, rails)
        findings += check_resistor_power(board, rails, loads, rules.get("i2c_buses") or ())
    else:
        findings.append(Finding(
            "rails-not-stated", "physics.rails",
            "no rail is described, so trace current, capacitor derating and resistor power were "
            "not checked at all — three of this tool's five rules",
            fix="fill physics.rails in the rules file: each net's nominal_volts and "
                "max_current_a. `/spark:init` writes the names from the built design and leaves "
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
    for severity in SEVERITIES:
        group = by_severity.get(severity) or []
        if not group:
            continue
        lines.append("\n%d %s:" % (len(group), severity))
        for finding in group:
            lines.append("  [%s] %s: %s" % (finding["rule"], finding["subject"], finding["detail"]))
            if finding.get("fix"):
                lines.append("      %s" % finding["fix"])
    return "\n".join(lines)


# --- MVP --- (P455, #616) the rules go through `fab.read_rules`, so a refusal is a sentence and exit 2, not a traceback
def rules_or_reason(circuit_path, rules_path):
    """`(rules, None)`, or `(None, the Refusal that says why nothing can run)`: a file that is missing, or rules that
    fab.read_rules refuses."""
    for path, what, code in ((circuit_path, "built design", check_codes.NO_CIRCUIT),
                             (rules_path, "rules", check_codes.NO_RULES_FILE)):
        if not path.is_file():
            return None, Refusal("no %s at %s" % (what, path), code)
    try:
        return fab.read_rules(rules_path), None
    except fab.RulesError as refused:
        return None, Refusal(str(refused), check_codes.RULES_REFUSED)
