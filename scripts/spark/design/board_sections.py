"""
The sections of a tscircuit board file (P708): `emit` writes the header, the parts, the signals and the power, and each
`*_lines` function gives one section. It asks `power_rails` about the nets and `board_components` about the parts.
"""

from spark.records import board_pads, provenance
from spark.design import fab
from spark.design import copper
from spark.design import loader
from spark.sourcing import part_facts, part_rules
from spark.design.board_components import (component_name, DEFAULT_BODY_MM, host_part_names,
                                           parts_without_an_outline, placeholders)
from spark.design.power_rails import (mcu_power_nets, outputs_in_contention, outputs_with_nothing_on_them,
                                      pair_sides_without_a_driver, power_connections, power_pins_with_no_rail,
                                      rail_loads, rails_not_established, rails_without_a_source, supply_net_of)


# --- MVP ---
#: The tag that opens each trace in a board file, after its indent: `check_spine` counts the traces by it, and
#: `tests/test_routes.py` holds the count to the build guide's.
TRACE_TAG = "<trace "


#: Fabrication defaults, set rather than inherited, and from `data/fabrication.json` rather than
#: from a literal here — these are the same two numbers `check_footprints` judges vias by.
VIA_HOLE_MM = fab.process("min_via_hole_mm")
VIA_PAD_MM = fab.process("min_via_pad_mm")
BOARD_THICKNESS_MM = fab.process("board_thickness_mm")


def inert(text):
    """
    Words the file keeps in a comment, with every `*/` written `* /` (F11, P87's emitter half).

    The file keeps a record's name, a signal, a passive's why, a power pin's note, a footprint note and a host
    requirement in `{/* … */}` comments and in its header's doc comment, and a `*/` in any of them ended the comment:
    `tsci build` ran what followed, with Node's `require` and `process` in reach. Every value a comment here carries
    goes through this one rule. Nothing else is touched: inside a comment a `"` is only text, and product names carry
    inch marks.
    """
    return str(text).replace("*/", "* /")


def power_trace(component, pin, net, rules, note="", unjustified=None):
    """
    One power connection, sized by what its rail carries.

    ONE function, because there are TWO places that emit power traces — the modules' pins and the
    microcontroller's own pads — and sizing only the first is how the car came out with 1.30 mm
    to the motor driver and the router's 0.15 mm default to the processor's ground. Same shape as
    the signal-prefix mapping and the pin reads before it: a rule written at the use site gets
    applied at one of them.
    """
    needed = trace_width_mm(net, rules)
    if needed is None:
        if unjustified is not None:
            unjustified.add(net)
        thickness = ""
    else:
        thickness = ' thickness="%.2fmm"' % needed
    suffix = ("  {/* %s */}" % inert(note)) if note else ""
    return '    <trace from=".%s > .%s" to="net.%s"%s />%s' % (
        component, pin, net, thickness, suffix)


def trace_width_mm(net, rules):
    """
    The width this net's current needs, or None when nobody has stated a current.

    Every generated trace was tscircuit's 0.15 mm default — good for about 0.6 A — including on
    an RC car whose traction rail carries 2.9 A. `check_physics` caught all three rails and the
    generator had never asked, even though the answer was in a file the same project holds.

    The arithmetic is IMPORTED from `check_physics` rather than repeated, so the generator cannot
    disagree with the checker that judges it. Two copies of one formula is how a board passes its
    own tool and fails a fab.

    None is a real answer: a rail with no stated current gets the default AND a comment saying
    the width is unjustified, which is the honest state rather than a silent 0.15 mm.
    """
    rails = ((rules.get("physics") or {}).get("rails") or {})
    current = (rails.get(net) or {}).get("max_current_a")
    # `copper.width_to_emit_mm` only ever widens, so a zero or negative current comes back None
    # on its own; a guard for it here was dead code, found by a mutation that changed nothing.
    if not isinstance(current, (int, float)):
        return None
    rise = ((rules.get("physics") or {}).get("trace_temperature_rise_c")
            or copper.DEFAULT_RISE_C)
    return copper.width_to_emit_mm(current, rise)


def unmeasured_lines(part_list):
    """The header's lines for the parts whose size was invented, or none."""
    # A warning on stderr is gone the moment the shell scrolls; the file is what someone opens in
    # six weeks. If a size was invented, the artifact says so where it cannot be missed.
    unsized = parts_without_an_outline(part_list)
    if unsized:
        return [
            " *",
            " * NOBODY HAS MEASURED: %s." % inert(", ".join(unsized)),
            " * Each is drawn as a placeholder %g x %g mm and everything else is arranged around"
            % DEFAULT_BODY_MM,
            " * that, so 'nothing overlaps' here is evidence of nothing at all. Measure them, put",
            " * width and height in the part file with a source, and regenerate.",
        ]
    return []


def header_lines(board, part_list, placements, width, height):
    """The import, the file's account of itself, and the board with the microcontroller on it."""
    lines = [
        "import { %s } from \"./%s\"" % ((board["physical"]["footprint_export"],) * 2),
        "",
        "/**",
        " * %s — generated from a module list." % inert(board["name"]),
        " *",
        " * The CONNECTIONS are derived and checked: every trace comes from a pin assignment",
        " * validated against this board's own wake, ADC and strapping constraints, and every",
        " * module pin comes from a part definition whose facts carry sources.",
        " *",
        " * The PLACEMENT is a first draft and nothing more. Modules sit in a column because that",
        " * does not overlap, not because it is right. Nothing here knows which cable should exit",
        " * where, what a person has to reach with a soldering iron once the tall parts are in, or",
        " * what a slamming lid does to a hand-made lead. Lay it out properly before ordering.",
        " *",
        " * Not decided here, and it must be: mounting holes, connector keying, and trace widths for",
        " * anything carrying real current.",
    ]

    lines += unmeasured_lines(part_list)

    lines += [
        " */",
        "export default () => (",
        '  <board width="%gmm" height="%gmm" autorouter="auto"' % (width, height),
        '      thickness="%gmm"' % BOARD_THICKNESS_MM,
        '      minViaHoleDiameter="%gmm" minViaPadDiameter="%gmm"' % (VIA_HOLE_MM, VIA_PAD_MM),
        '      automaticPoursEnabled>',
        "    <%s name=\"Mcu\" pcbX={%g} pcbY={%g} />"
        % (board["physical"]["footprint_export"], *placements["Mcu"]),
        "",
    ]
    return lines


def ohms_label(ohms):
    """tscircuit's resistance string: 10000 -> 10k, 4700 -> 4.7k, 330 -> 330."""
    if ohms >= 1e6:
        return "%gM" % (ohms / 1e6)
    if ohms >= 1e3:
        return "%gk" % (ohms / 1e3)
    return "%g" % ohms


#: The E12 series: the resistor values sold everywhere, one decade.
E12 = (1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2)


def series_ohms(part, host_part, board):
    """
    A series resistor's value, and the arithmetic when it was computed (P78). Given `ohms`, that.
    Given `for_current_ma`: (the board's I/O voltage - the part's forward voltage) / the current,
    rounded UP to the next E12 value, so the current never exceeds what was asked.
    """
    if host_part.get("ohms"):
        return host_part["ohms"], None
    supply = provenance.read_value(board, "power", "io_volts")
    forward = provenance.read_value(part, "facts", "forward_voltage_v")
    if not isinstance(supply, (int, float)) or not isinstance(forward, (int, float)):
        raise ValueError("%s asks for %g mA through a series resistor, but %s — nothing to compute it from"
                         % (part.get("id"), host_part["for_current_ma"],
                            "the record states no facts.forward_voltage_v" if not isinstance(forward, (int, float))
                            else "the board states no power.io_volts"))
    if forward >= supply:
        raise ValueError("%s needs %g V forward, and a %g V pin cannot push current through it — drive it "
                         "from a higher rail through a transistor" % (part.get("id"), forward, supply))
    exact = (supply - forward) / (host_part["for_current_ma"] / 1000.0)
    decade = 10 ** max(0, len(str(int(exact))) - 1)
    chosen = next((step * decade for step in E12 + (10.0,) if step * decade >= exact - 1e-9), exact)
    chosen = int(round(chosen)) if abs(chosen - round(chosen)) < 1e-6 else round(chosen, 6)
    return chosen, ("(%g V - %g V) / %g mA = %g ohm; next E12 value up: %g ohm, about %.1f mA"
                    % (supply, forward, host_part["for_current_ma"], round(exact, 1), chosen,
                       (supply - forward) / chosen * 1000))


def signal_target(part, need):
    """
    Where the host's trace for a signal ends: the module's pad, or — when the record demands a
    divider on that pad — the divider's midpoint, so the host's pin sees the divided level.
    """
    for host_part in part.get("host_parts") or []:
        if host_part["kind"] == "divider" and host_part["pin"] == need["pin"]:
            return (host_part_names(part, host_part)[0], "pin2")
        if host_part["kind"] == "series" and host_part["pin"] == need["pin"]:
            return (host_part_names(part, host_part)[0], "pin1")
    return (component_name(part), need["pin"])


def host_part_lines(part_list, placements, board=None):
    """
    The passives the records demand of this board, as components and traces (backlog P6). This
    was prose in a comment block — "10 k pulldowns on both inputs" printed under a board whose
    inputs floated, on the reference design and the car alike.
    """
    lines = []
    for part in part_list:
        for host_part in part.get("host_parts") or []:
            module, pad, kind = component_name(part), host_part["pin"], host_part["kind"]
            names = host_part_names(part, host_part)
            if kind == "divider":
                top, bottom = names
                lines.append("    {/* %s */}" % inert("%s.%s through a divider: %s" % (module, pad, host_part["why"])))
                for name, ohms in ((top, host_part["top_ohms"]), (bottom, host_part["bottom_ohms"])):
                    lines.append('    <resistor name="%s" resistance="%s" footprint="0603" pcbX={%g} pcbY={%g} />'
                                 % (name, ohms_label(ohms), *placements[name]))
                lines.append('    <trace from=".%s > .%s" to=".%s > .pin1" />' % (module, pad, top))
                lines.append('    <trace from=".%s > .pin2" to=".%s > .pin1" />  {/* the midpoint the host\'s pin reads */}' % (top, bottom))
                lines.append('    <trace from=".%s > .pin2" to="net.GND" />' % bottom)
                continue
            name, = names
            if kind == "series":
                ohms, arithmetic = series_ohms(part, host_part, board)
                lines.append("    {/* %s */}" % inert("in series with %s.%s: %s%s" % (
                    module, pad, host_part["why"], " — %s" % arithmetic if arithmetic else "")))
                lines.append('    <resistor name="%s" resistance="%s" footprint="0603" pcbX={%g} pcbY={%g} />'
                             % (name, ohms_label(ohms), *placements[name]))
                lines.append('    <trace from=".%s > .pin2" to=".%s > .%s" />' % (name, module, pad))
                continue
            net = "GND" if kind == "pulldown" else supply_net_of(part)
            lines.append("    {/* %s */}" % inert("%s on %s.%s: %s" % (kind, module, pad, host_part["why"])))
            lines.append('    <resistor name="%s" resistance="%s" footprint="0603" pcbX={%g} pcbY={%g} />'
                         % (name, ohms_label(host_part["ohms"]), *placements[name]))
            lines.append('    <trace from=".%s > .pin1" to=".%s > .%s" />' % (name, module, pad))
            lines.append('    <trace from=".%s > .pin2" to="net.%s" />' % (name, net))
    if lines:
        lines = ["    {/* What the parts demand of this board as components, from their records' host_parts — done here. */}"] + lines + [""]
    return lines


def component_lines(part_list, placements):
    """One chip per part instance, its pads numbered from the module's own pin_order."""
    lines = []
    for part in part_list:
        name = component_name(part)
        # Numbered from the part's own pin_order, which is pad 1..N of the real module. This read
        # the order the pins happened to appear in the JSON file, so an L9110S whose header reads
        # BIA BIB GND VCC AIA AIB came out as pin1: "AIA" and every trace landed on the wrong pad.
        pin_labels = ", ".join('pin%d: "%s"' % (position, pad)
                               for position, pad in enumerate(part.get("pin_order") or [], 1)
                               if pad is not None)
        lines.append("    {/* %s */}" % inert(part["name"]))
        printed = part_facts.printed_names(part)
        if printed:
            # The silkscreen, kept where a person wiring the module will read it. `pin` is what
            # a selector can parse; `printed` is what is actually on the part, and losing the
            # second to satisfy the first is how an MP1584's IN+ became VIN with no record of it.
            lines.append("    {/* silkscreen: %s */}" % inert(", ".join(
                "%s is printed %s" % (wiring, label) for wiring, label in sorted(printed.items()))))
        lines.append('    <chip name="%s" footprint="%s" pcbX={%g} pcbY={%g}'
                     % (name, part["footprint"], *placements[name]))
        lines.append("      pinLabels={{ %s }} />" % pin_labels)
    lines.append("")
    return lines


def signal_lines(part_list, assignments, pads):  # --- MVP --- (P512, #708) `pads` turns MOSI into the pad MO
    """
    Every signal the assigner placed, and an account of each one.

    This iterated over PARTS and their needs, so a signal placed for something with no part
    record — a button, an LED, a limit switch, a connector — was never looked up at all. On a
    twelve-signal design six vanished, with no trace and no warning, under this very banner.
    The assignments are the authority on what has to be connected; the parts only say where.
    """
    wants = {}
    for part in part_list:
        for need in part.get("needs") or []:
            wants[loader.signal_name(part, need)] = signal_target(part, need)

    lines = ["    {/* Signals, each on the pin assign_pins.py chose and for the reason it gave. */}"]
    unclaimed = []
    for entry in assignments:
        target = wants.get(entry["signal"])
        if not target:
            unclaimed.append(entry)
            continue
        # The signal's own name, not just the module pin it lands on. Without it the file says `.Mcu > .D3 ->
        # .L9110sModule > .AIA` and nothing connects that back to MOTOR_IA or to the reason the assigner chose D3.
        lines.append('    <trace from=".Mcu > .%s" to=".%s > .%s" />  {/* %s */}'
                     % (pads.pad_of(entry["pin"]), target[0], target[1], inert("%s: %s" % (entry["signal"], entry["why"]))))

    if unclaimed:
        lines += ["",
                  "    {/* ASSIGNED, AND CONNECTED TO NOTHING. The pin assigner placed these, and",
                  "        no part in the module list claims them, so this file cannot say what",
                  "        they reach. They are not optional — the design asked for them:"]
        for entry in unclaimed:
            lines.append("          - %s" % inert("%s on %s (GPIO%s): %s"
                                                  % (entry["signal"], entry["pin"], entry["gpio"], entry["why"])))
        lines += ["        Add a part record for whatever each one drives, or wire it by hand.",
                  "        A schematic missing half its signals builds and routes cleanly. */}"]
    lines.append("")
    return lines


def mcu_power_lines(board, part_list, rules, unjustified):
    """
    The microcontroller's OWN supply pins.

    Omitted entirely until 2026-09-25, so a generated board's processor shared a net with none
    of its pins — no ground, no 3.3 V — while the modules around it were correctly wired to
    rails the MCU was not on. It built, it routed, and nothing reported it, because "is this
    component connected to anything" was a question no check asked.
    """
    lines = []
    for pad, net, wired in mcu_power_nets(board, part_list):
        if not net:
            # Said, not skipped. This was `continue` — the silent drop G2 removed for module
            # pins, kept for the processor's own pads. The board contract now refuses a pad
            # with no rail; this is the generator refusing to hide one that reaches it anyway.
            lines.append("    {/* Mcu.%s NAMES NO RAIL in the board file's power_pads, so it is" % inert(pad))
            lines.append("        wired to nothing. Add a rail to that entry. */}")
            continue
        if not wired:
            # Also said, not skipped, and for the same reason: an absent trace reads the same
            # whether it was reasoned about or forgotten, and one of those two is a fault.
            lines.append("    {/* Mcu.%s receives net.%s and NOTHING ON THIS BOARD DRIVES that" % (inert(pad), inert(net)))
            lines.append("        rail, so it is left open — on this module that pad is then a")
            lines.append("        source, carrying USB power out. Add a regulator or an inlet")
            lines.append("        whose record declares an output on that rail to feed it. */}")
            continue
        lines.append(power_trace("Mcu", pad, net, rules, unjustified=unjustified))
    if not board.get("power_pads"):
        lines.append("    {/* THIS BOARD FILE DOES NOT SAY WHICH OF ITS PADS ARE POWER, so the")
        lines.append("        microcontroller is wired to no rail at all. Every module below may")
        lines.append("        be correctly connected to a ground the processor is not on. Add")
        lines.append("        `power_pads` to the board definition. */}")
    return lines


def power_note_lines(part_list):
    """Everything the power section has to say before its traces, each from its own rule."""
    lines = []
    for net, part_name, pin in outputs_with_nothing_on_them(part_list):
        lines.append("    {/* net.%s is driven by %s.%s and NOTHING ON THIS BOARD RECEIVES IT."
                     % (inert(net), inert(part_name), inert(pin)))
        lines.append("        A speaker, a motor or a connector is not a module, so nobody lists")
        lines.append("        one — whatever this drives has to be added, or the net has one")
        lines.append("        member and will not route. */}")
    for net, who in outputs_in_contention(part_list):
        lines.append("    {/* net.%s IS DRIVEN BY MORE THAN ONE SUPPLY: %s." % (inert(net), inert(", ".join(who))))
        lines.append("        Two supplies on one rail short into each other unless one is designed")
        lines.append("        to back-feed, which a part record cannot say. Move one to its own")
        lines.append("        rail, or state the arrangement in the design. */}")
    for pin in power_pins_with_no_rail(part_list):
        lines.append("    {/* %s NAMES NO RAIL, so nothing can place it. A power pin with no" % inert(pin))
        lines.append("        rail is not a pin on some default rail — it is a connection the part")
        lines.append("        file never stated. Add a `rail` to that entry. */}")
    invented = rails_not_established(part_list)
    if invented:
        lines.append("    {/* Rails this design INVENTED. Listed because a typo creates a net just")
        lines.append("        as easily as a new rail does — GROUDN is a fine net name and a")
        lines.append("        terrible ground. Check each one is intended:")
        for invented_net, pins in invented.items():
            lines.append("          net.%-12s from %s" % (inert(invented_net), inert(", ".join(pins))))
        lines.append("     */}")
    pair_sides = pair_sides_without_a_driver(part_list)  # F15: an amplifier drives these, never a supply
    for net in rails_without_a_source(part_list):
        if net in pair_sides:
            lines.append("    {/* NOTHING ON THIS BOARD DRIVES net.%s, one side of a driven pair. Add what" % inert(net))
            lines.append("        drives the pair (the amplifier this terminal hangs off), never a supply,")
            lines.append("        or the net has one member and will not route. */}")
            continue
        lines.append("    {/* NOTHING ON THIS BOARD SOURCES net.%s. A module list is a list of" % inert(net))
        lines.append("        consumers — whatever supplies this rail (a connector, a regulator,")
        lines.append("        a battery) has to be added, or the net has one member and will not")
        lines.append("        route. */}" )
    return lines


def module_power_lines(part_list, rules, unjustified):
    """Each module power pin on its rail's net, through the one walk of the power lists."""
    return [power_trace(component_name(part), supply["pin"], net, rules,
                        supply.get("note") or "", unjustified)
            for part, supply, net in power_connections(part_list)]


def unjustified_lines(unjustified):
    """The admission that goes under any power trace nobody could size."""
    if not unjustified:
        return []
    return ["    {/* THE WIDTH OF THE TRACES ABOVE ON %s IS UNJUSTIFIED."
            % inert(", ".join("net." + net for net in sorted(unjustified))),
            "        They take the router's default, which is about 0.15 mm and good",
            "        for roughly 0.6 A. Nobody has stated what these rails carry, so",
            "        nothing here could size them. Name each load's figure in its part",
            "        record (`draws` or `can_supply` on the power pin), or state",
            "        `max_current_a` in .spark/rules.json, and regenerate; `check_physics`",
            "        judges the result by the same arithmetic that would have set it. */}"]


def rules_with_record_currents(rules, loads):
    """
    The rules, with each rail they leave unstated sized from its records' complete sum (P52).

    A stated `max_current_a` is kept, because a measurement beats a sum; an open sum is not used,
    because a partial one sizes a trace too thin. `check_physics` makes the same choice from the
    same `rail_loads`, so the generator and the checker read one number.
    """
    physics = dict((rules or {}).get("physics") or {})
    rails = {net: dict(spec) for net, spec in (physics.get("rails") or {}).items()}
    for net, load in loads.items():
        stated = rails.get(net, {}).get("max_current_a")
        if load["complete"] and not isinstance(stated, (int, float)):
            rails.setdefault(net, {})["max_current_a"] = load["amps"]
    return dict(rules or {}, physics=dict(physics, rails=rails))


def power_lines(board, part_list, rules):
    """The power section. `unjustified` collects, across both trace loops, what could not be sized."""
    rules = rules_with_record_currents(rules, rail_loads(part_list, board))
    unjustified = set()
    lines = ["    {/* Power. Which rail each module pin belongs to comes from its part file. */}"]
    lines += mcu_power_lines(board, part_list, rules, unjustified)
    lines += power_note_lines(part_list)
    lines += module_power_lines(part_list, rules, unjustified)
    lines += unjustified_lines(unjustified)
    return lines


def stand_in_lines(part_list):
    """The footprints that are placeholders, named as the netlist names them."""
    stand_ins = placeholders(part_list)
    if not stand_ins:
        return []
    lines = ["", "    {/* FOOTPRINTS THAT ARE PLACEHOLDERS. The netlist is right and the geometry",
             "        is not; every check that measures copper is told to skip these:"]
    for part in stand_ins:
        lines.append("          %s" % inert("%s drawn as %s — %s"
                                            % (component_name(part), part.get("footprint"), part.get("footprint_note"))))
    lines.append("     */}")
    return lines


def host_requirement_lines(part_list):
    """
    Requirements a part states about its host, carried into the file rather than left in a
    library nobody opens. These are the things a generated board CANNOT do for you.
    """
    requirements = [(part["name"], text)
                    for part in part_list for text in part.get("host_requirements") or []]
    if not requirements:
        return []
    done = sum(len(part.get("host_parts") or []) for part in part_list)
    lines = ["", "    {/* What these parts require of this board, from their part files.",
             ("        Beyond the %d passive(s) placed above, none of it is done here — each one is a design decision:" % done)
             if done else "        None of it is done here — each one is a design decision:"]
    for part_name, text in requirements:
        lines.append("          - %s" % inert("%s: %s" % (part_name, text)))
    for part in part_list:  # P81: a pull this board adds that the part's own defeats, with the arithmetic
        for conflict in part_rules.pull_conflicts(part):
            lines.append("          - CONFLICT %s" % inert("%s: %s" % (part["name"], conflict)))
    lines.append("     */}")
    return lines


def emit(board, part_list, assignments, placements, width, height, rules=None):
    """
    The board file: one section per function above, in the order a reader meets them.

    This was one 186-line function with ten sections and 39 branches (sprint audit A5), where a
    rule fixed in one section stayed wrong in the next. Each section now takes what it needs and
    returns its lines, so it can be tested alone and the whole is the sum, byte for byte.
    """
    rules = rules or {}
    lines = (header_lines(board, part_list, placements, width, height)
             + component_lines(part_list, placements)
             + host_part_lines(part_list, placements, board)
             + signal_lines(part_list, assignments, board_pads.BoardPads.from_record(board))
             + power_lines(board, part_list, rules)
             + stand_in_lines(part_list)
             + host_requirement_lines(part_list)
             + ["  </board>", ")"])
    return "\n".join(lines) + "\n"
# --- end MVP ---
