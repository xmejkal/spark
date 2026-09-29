#!/usr/bin/env python3
"""
A pin map and a module list, as a board file you can build.

    emit_board.py requirements.json > board.tsx
    emit_board.py requirements.json --project ~/my-project --board xiao-esp32-c6

The project — its parts, its rules — is the one found up from the requirements file's own
directory unless `--project` says otherwise. Where the command is typed does not matter.

This is the last step of "I have these modules, wire them up". Everything before it — which board,
what each module asks for, which pin each signal goes on — is settled by `boards.py`,
`parts.py` and `assign_pins.py`. This turns that into tscircuit.

WHAT IT IS HONEST ABOUT
The connections are derived and trustworthy: every trace comes from a pin assignment that was
checked against the board's own capabilities, and every module pin comes from a part definition
whose facts carry sources. Nothing here is guessed.

**The placement is not.** It is a first draft: modules in a column, connectors on an edge,
passives near what they serve. It has no opinion about which cable should exit where, what a
person has to reach, or what a lid slamming does to a hand-made lead. A real layout is a design
activity, and the generated file says so at the top rather than pretending otherwise.

So the output is a starting point that BUILDS and can be checked, not a finished board. That is
the useful thing: `tsci build` and the whole deterministic check suite can run on it immediately,
which is the difference between a draft you can iterate and a blank file.
"""

import argparse
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

import assign_pins  # noqa: E402
import boards  # noqa: E402
import copper  # noqa: E402
import design as design_library  # noqa: E402
import parts as parts_library  # noqa: E402

EXIT_OK, EXIT_COULD_NOT_RUN = 0, 2

#: Layout constants. Ordinal, not designed — they exist to produce something that does not
#: overlap, so the checks have a board to run on.
MARGIN_MM = 6
GAP_MM = 4
DEFAULT_BODY_MM = (16, 12)

#: Rails with an ESTABLISHED net name. Deliberately not the whole vocabulary — see
#: `net_name_for_rail`. `MOTOR6V` carries a voltage belonging to one project's battery and is kept
#: only because designs already reference that net by name; a new design should say `motor` and
#: state the voltage in its rules file.
KNOWN_RAIL_NETS = {"logic": "V33", "ground": "GND", "motor": "MOTOR6V", "speaker": "SPEAKER"}


def net_name_for_rail(rail):
    """
    The net a rail's name means. ANY rail name is allowed.

    This was a closed dictionary of four, and a rail outside it returned None — which the power
    loops turned into `continue`, so the connection was silently not emitted. An RC car with a 5 V
    servo rail and a 7.4 V traction pack came out with a servo that had a ground and no supply,
    and a regulator joined to the board by its two ground pins and nothing else. Exit 0, one
    unrelated note. That is the third instance of one defect — `244feb1` (signals with no part
    record) and `21156b4` (the processor on no ground) were the first two: the generator emitting
    less than it was asked for without saying so.

    The four above keep their names so existing designs are unchanged. Anything else becomes its
    own name upper-cased, and `rails_not_established` reports it — because an open vocabulary
    means a typo creates a net, and the answer is to show the reader what was created rather than
    to refuse every rail nobody thought of in advance.
    """
    if not rail:
        return None
    return KNOWN_RAIL_NETS.get(rail, str(rail).upper())


def rails_not_established(part_list):
    """
    Rails this design invented, so a typo is visible rather than silently a new net.

    `GROUDN` is a perfectly good net name and a terrible ground. Reported, not refused: the
    alternative is the closed vocabulary that silently dropped three connections.
    """
    invented = {}
    for part, supply, _ in power_connections(part_list):
        rail = supply["rail"]
        if rail not in KNOWN_RAIL_NETS:
            invented.setdefault(net_name_for_rail(rail), []).append(
                "%s.%s" % (part["name"], supply["pin"]))
    return {net: sorted(pins) for net, pins in sorted(invented.items())}


def power_pins_with_no_rail(part_list):
    """Power pins whose record names no rail at all — a connection nobody can place."""
    return ["%s.%s" % (part["name"], supply["pin"])
            for part in part_list for supply in part.get("power") or []
            if not supply.get("rail")]

#: What a `polarity` becomes in a net name, so a differential pair reads as one.
POLARITY_SUFFIX = {"+": "_P", "-": "_N"}


#: Fabrication defaults, set rather than inherited.
#:
#: A tool's floor is what you get when nothing is stated, and on a real board that produced
#: 0.2 mm vias with a 0.05 mm annular ring — below every cheap process's minimum, and an
#: upcharge besides. Nobody chose it. A generated board should not hand anyone that.
VIA_HOLE_MM = 0.3
VIA_PAD_MM = 0.6
BOARD_THICKNESS_MM = 1.6

#: Rails the microcontroller module itself supplies, so a design made only of consumers still
#: has a source for them.
RAILS_THE_MODULE_PROVIDES = ("V33", "GND")


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
    suffix = ("  {/* %s */}" % note) if note else ""
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
    if not isinstance(current, (int, float)) or current <= 0:
        return None
    rise = ((rules.get("physics") or {}).get("trace_temperature_rise_c")
            or copper.DEFAULT_RISE_C)
    return copper.width_to_emit_mm(current, rise)


def power_connections(part_list):
    """
    Every module power pin that names a rail, as (part, supply, net): ONE walk of the lists.

    It was written four times — the source rule, the sink rule, the traces and the invented-rail
    report — each with its own `net_for` and `continue`, and G2 was fixed at some of them. An
    entry with no rail is not yielded; `power_pins_with_no_rail` is the one place that says so,
    and the generated file carries what it says.
    """
    for part in part_list:
        for supply in part.get("power") or []:
            net = net_for(supply)
            if net:
                yield part, supply, net


def net_for(supply):
    """
    The net a power pin belongs on.

    An INPUT joins the shared rail — several parts on V33, several pins on GND, which is the
    point of a rail. An OUTPUT gets its own net, because two outputs on one net is a short. That
    distinction did not exist here: both halves of a bridged class-D amplifier declared
    `"rail": "speaker"`, both were mapped to `net.SPEAKER`, and the generated board wired them
    together — printing the part file's own warning, "never ground either side", on the trace
    that did it.
    """
    net = net_name_for_rail(supply.get("rail"))
    if net and supply.get("direction") == "out":
        return net + POLARITY_SUFFIX.get(supply.get("polarity"), "")
    return net


def body_of(part):
    body = part.get("body_mm") or {}
    return (body.get("width", DEFAULT_BODY_MM[0]), body.get("height", DEFAULT_BODY_MM[1]))


def has_an_outline(part):
    """Whether anyone has ever recorded how big this part is."""
    body = part.get("body_mm") or {}
    return isinstance(body.get("width"), (int, float)) and isinstance(
        body.get("height"), (int, float))


def parts_without_a_pinout(part_list):
    """
    Parts that never say which pad is pin 1.

    Without it the generator numbered pads from the order the pins appear in the JSON file, which
    is not a fact about anything. Every trace to such a module lands wherever that order happened
    to put it, the board builds, the render looks right, and nothing works.
    """
    return [part["name"] for part in part_list if not part.get("pin_order")]


def parts_without_an_outline(part_list):
    """
    Parts whose size nobody has recorded.

    `body_of` substitutes DEFAULT_BODY_MM for these, which is how a rangefinder nobody had
    measured became 16 x 12 mm — and then `place()` proved the modules did not overlap, using a
    number that was invented two lines earlier. A layout is only as true as its smallest
    dimension, so this is a refusal rather than a default.
    """
    return [part["name"] for part in part_list if not has_an_outline(part)]


def parts_without_a_footprint(part_list):
    """
    Parts with no footprint recorded.

    This used to default to `pinrow4` — a guess dressed as a fact. The MAX98357A carrier has
    twelve pads in two rows and would have been emitted onto four in one row. Every pad past the
    fourth would simply not exist, and traces to them land on ports with no position, which is
    not a build error: it is a board with no routing at all.

    Four pads is also the least suspicious wrong answer available. A default of forty would have
    been caught the first time it ran; this one survived because the output looked plausible.
    """
    return [part["name"] for part in part_list if not part.get("footprint")]


def component_name(part):
    """
    What to call this instance in the emitted file.

    An explicit instance name wins. Without one the name comes from the part id, which is fine
    for one of a thing and catastrophic for five: a remote with five identical buttons emitted
    five components all called `TactileButton`, `tsci build` kept ONE of them, and the five
    distinct GPIOs `assign_pins` had carefully allocated were all wired to that survivor's single
    port. Five microcontroller pins shorted together, exit 0, no warning.
    """
    if part.get("_instance"):
        return part["_instance"]
    return "".join(word.capitalize() for word in part["id"].replace("_", "-").split("-"))


def placeholder_components(part_list):
    """
    Components whose footprint is a stand-in, by the name the emitted file gives them.

    Named HERE, with `component_name`, so the checker that later skips them is keyed by exactly
    the string that reaches the netlist — a second derivation of the name in `check_all` would
    be one more copy of a rule to drift.
    """
    return sorted(component_name(part) for part in placeholders(part_list))


def placeholders(part_list):
    """The parts whose footprint is a stand-in — the one filter, for the name list and the file."""
    return [part for part in part_list if parts_library.has_placeholder_footprint(part)]


def duplicate_component_names(part_list):
    """
    Names used more than once, which `tsci build` resolves by keeping one component.

    The independent safety net for the defect above: whatever route a design takes to two
    components of the same name, this catches it before anything is emitted.
    """
    seen, repeated = set(), []
    for part in part_list:
        name = component_name(part)
        if name in seen and name not in repeated:
            repeated.append(name)
        seen.add(name)
    return repeated


def place(board, part_list):
    """
    Somewhere for everything, and nothing on top of anything else.

    Deliberately simple: the module down the left, parts in a column to its right. It does not
    know which cable leaves where, which is exactly the kind of thing a person has to decide.
    """
    module_width = (board.get("physical") or {}).get("width_mm", 25)
    module_height = (board.get("physical") or {}).get("height_mm", 60)

    column_x = module_width + MARGIN_MM + GAP_MM
    widest = max([body_of(p)[0] for p in part_list] or [0])
    total_height = sum(body_of(p)[1] + GAP_MM for p in part_list)

    width = column_x + widest + MARGIN_MM
    height = max(module_height, total_height) + 2 * MARGIN_MM

    placements = {"Mcu": (-width / 2 + MARGIN_MM + module_width / 2, 0)}
    y = height / 2 - MARGIN_MM
    for part in part_list:
        part_height = body_of(part)[1]
        y -= part_height / 2
        placements[component_name(part)] = (-width / 2 + column_x + widest / 2, y)
        y -= part_height / 2 + GAP_MM
    return placements, width, height


def rails_without_a_source(part_list):
    """
    Rails that something consumes and nothing provides.

    A list of modules is a list of CONSUMERS. Nobody lists the battery connector among their
    parts, so a generated board wires a motor driver's VCC to a motor rail that has no other
    member — and a net with one member cannot be routed, so the board does not build.

    That is worth saying plainly rather than emitting a file that fails: the design genuinely
    needs a source for that rail and the module list did not contain one.
    """
    consumed, provided = set(), set()
    for _, power, net in power_connections(part_list):
        # An OUTPUT is not a rail anything has to source — the part IS the source. This branch
        # collected nothing until 2026-09-25, so the function returned every consumed rail
        # whether or not something fed it, and adding the connector that supplies a rail did
        # not stop it being reported as unsupplied. The name and the docstring were right about
        # the intent; the code only did the first half.
        if power.get("direction") == "out":
            provided.add(net)
        elif net not in RAILS_THE_MODULE_PROVIDES:
            consumed.add(net)
    return sorted(consumed - provided)


def outputs_with_nothing_on_them(part_list):
    """
    Nets a part drives that nothing on this board receives.

    The mirror of `rails_without_a_source`, and it has to be said too: a speaker is not a module,
    so nobody lists one, and the amplifier's two outputs each end up a net with one member. That
    is a net that cannot route, in a file whose header says every connection is derived and
    checked — and the errors a build then reports should be the ones this file predicted rather
    than a surprise.
    """
    driven, received = [], set(RAILS_THE_MODULE_PROVIDES)
    for part, power, net in power_connections(part_list):
        if power.get("direction") == "out":
            driven.append((net, part["name"], power["pin"]))
        else:
            received.add(net)
    # Same omission this function's twin had: it listed every driven net without ever asking
    # whether something on the board receives it. Adding the power inlet that feeds the motor
    # driver then produced a warning that the motor rail goes nowhere, naming the part it goes
    # to. A warning that fires on a correct design is worse than none — it is the reason people
    # stop reading them.
    return sorted(entry for entry in driven if entry[0] not in received)


def header_lines(board, part_list, placements, width, height):
    """The import, the file's account of itself, and the board with the microcontroller on it."""
    lines = [
        "import { %s } from \"./%s\"" % ((board["physical"]["footprint_export"],) * 2),
        "",
        "/**",
        " * %s — generated from a module list." % board["name"],
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

    # A warning on stderr is gone the moment the shell scrolls; the file is what someone opens in
    # six weeks. If a size was invented, the artifact says so where it cannot be missed.
    unsized = parts_without_an_outline(part_list)
    if unsized:
        lines += [
            " *",
            " * NOBODY HAS MEASURED: %s." % ", ".join(unsized),
            " * Each is drawn as a placeholder %g x %g mm and everything else is arranged around"
            % DEFAULT_BODY_MM,
            " * that, so 'nothing overlaps' here is evidence of nothing at all. Measure them, put",
            " * width and height in the part file with a source, and regenerate.",
        ]

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
        lines.append("    {/* %s */}" % part["name"])
        printed = parts_library.printed_names(part)
        if printed:
            # The silkscreen, kept where a person wiring the module will read it. `pin` is what
            # a selector can parse; `printed` is what is actually on the part, and losing the
            # second to satisfy the first is how an MP1584's IN+ became VIN with no record of it.
            lines.append("    {/* silkscreen: %s */}" % ", ".join(
                "%s is printed %s" % (wiring, label) for wiring, label in sorted(printed.items())))
        lines.append('    <chip name="%s" footprint="%s" pcbX={%g} pcbY={%g}'
                     % (name, part["footprint"], *placements[name]))
        lines.append("      pinLabels={{ %s }} />" % pin_labels)
    lines.append("")
    return lines


def signal_lines(part_list, assignments):
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
            wants[design_library.signal_name(part, need)] = (component_name(part), need["pin"])

    lines = ["    {/* Signals, each on the pin assign_pins.py chose and for the reason it gave. */}"]
    unclaimed = []
    for entry in assignments:
        target = wants.get(entry["signal"])
        if not target:
            unclaimed.append(entry)
            continue
        # The signal's own name, not just the module pin it lands on. Without it the file says
        # `.Mcu > .D3 -> .L9110sModule > .AIA` and nothing connects that back to MOTOR_IA or to
        # the reason the assigner chose D3.
        lines.append('    <trace from=".Mcu > .%s" to=".%s > .%s" />  {/* %s: %s */}'
                     % (entry["pin"], target[0], target[1], entry["signal"], entry["why"]))

    if unclaimed:
        lines += ["",
                  "    {/* ASSIGNED, AND CONNECTED TO NOTHING. The pin assigner placed these, and",
                  "        no part in the module list claims them, so this file cannot say what",
                  "        they reach. They are not optional — the design asked for them:"]
        for entry in unclaimed:
            lines.append("          - %s on %s (GPIO%s): %s"
                         % (entry["signal"], entry["pin"], entry["gpio"], entry["why"]))
        lines += ["        Add a part record for whatever each one drives, or wire it by hand.",
                  "        A schematic missing half its signals builds and routes cleanly. */}"]
    lines.append("")
    return lines


def mcu_power_lines(board, rules, unjustified):
    """
    The microcontroller's OWN supply pins.

    Omitted entirely until 2026-09-25, so a generated board's processor shared a net with none
    of its pins — no ground, no 3.3 V — while the modules around it were correctly wired to
    rails the MCU was not on. It built, it routed, and nothing reported it, because "is this
    component connected to anything" was a question no check asked.
    """
    lines = []
    for pad, supply in sorted((board.get("power_pads") or {}).items()):
        net = net_name_for_rail(supply.get("rail"))
        if not net:
            # Said, not skipped. This was `continue` — the silent drop G2 removed for module
            # pins, kept for the processor's own pads. The board contract now refuses a pad
            # with no rail; this is the generator refusing to hide one that reaches it anyway.
            lines.append("    {/* Mcu.%s NAMES NO RAIL in the board file's power_pads, so it is" % pad)
            lines.append("        wired to nothing. Add a rail to that entry. */}")
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
                     % (net, part_name, pin))
        lines.append("        A speaker, a motor or a connector is not a module, so nobody lists")
        lines.append("        one — whatever this drives has to be added, or the net has one")
        lines.append("        member and will not route. */}")
    for pin in power_pins_with_no_rail(part_list):
        lines.append("    {/* %s NAMES NO RAIL, so nothing can place it. A power pin with no" % pin)
        lines.append("        rail is not a pin on some default rail — it is a connection the part")
        lines.append("        file never stated. Add a `rail` to that entry. */}")
    invented = rails_not_established(part_list)
    if invented:
        lines.append("    {/* Rails this design INVENTED. Listed because a typo creates a net just")
        lines.append("        as easily as a new rail does — GROUDN is a fine net name and a")
        lines.append("        terrible ground. Check each one is intended:")
        for invented_net, pins in invented.items():
            lines.append("          net.%-12s from %s" % (invented_net, ", ".join(pins)))
        lines.append("     */}")
    for net in rails_without_a_source(part_list):
        lines.append("    {/* NOTHING ON THIS BOARD SOURCES net.%s. A module list is a list of" % net)
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
            % ", ".join("net." + net for net in sorted(unjustified)),
            "        They take the router's default, which is about 0.15 mm and good",
            "        for roughly 0.6 A. Nobody has stated what these rails carry, so",
            "        nothing here could size them. State `max_current_a` for each in",
            "        .spark/rules.json and regenerate; `check_physics` judges the",
            "        result by the same arithmetic that would have set it. */}"]


def power_lines(board, part_list, rules):
    """The power section. `unjustified` collects, across both trace loops, what could not be sized."""
    unjustified = set()
    lines = ["    {/* Power. Which rail each module pin belongs to comes from its part file. */}"]
    lines += mcu_power_lines(board, rules, unjustified)
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
        lines.append("          %s drawn as %s — %s"
                     % (component_name(part), part.get("footprint"), part.get("footprint_note")))
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
    lines = ["", "    {/* What these parts require of this board, from their part files.",
             "        None of it is done here — each one is a design decision:"]
    for part_name, text in requirements:
        lines.append("          - %s: %s" % (part_name, text))
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
             + signal_lines(part_list, assignments)
             + power_lines(board, part_list, rules)
             + stand_in_lines(part_list)
             + host_requirement_lines(part_list)
             + ["  </board>", ")"])
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="emit_board.py", description="Turn a module list and a pin map into a board file.")
    parser.add_argument("requirements")
    parser.add_argument("--project")
    parser.add_argument("--board")
    parser.add_argument("--assume-missing-sizes", action="store_true",
                        help="lay out around a guessed size for any part whose outline "
                             "nobody recorded, saying so in the generated file")
    args = parser.parse_args(argv)

    try:
        design = design_library.load(args.requirements, args.project, args.board)
        board, part_list = design.board, design.parts
        # The signals are the loader's — derived once, named per instance — so `assign_pins.py`
        # and this file cannot disagree about which signals a design has.
        assignments, _ = assign_pins.assign(board, design.signals)
    except (design_library.DesignError, assign_pins.Impossible) as broken:
        # Everything wrong with the INPUT is could-not-run: the file was never a design. Reading
        # it used to happen above this `try`, and a malformed file was a traceback with exit 1 —
        # which reads as "problems found" to anything that knows three outcomes.
        print("cannot emit a board: %s" % broken, file=sys.stderr)
        return EXIT_COULD_NOT_RUN

    if not (board.get("physical") or {}).get("footprint_export"):
        print("this board has no verified footprint, so a board file would reference nothing",
              file=sys.stderr)
        return EXIT_COULD_NOT_RUN

    repeated = duplicate_component_names(part_list)
    if repeated:
        print("two or more components would be called: %s\n"
              "  `tsci build` resolves that by keeping ONE of them, so every pin assigned to the "
              "others is wired to the survivor — five identical buttons became one component with "
              "five GPIOs shorted to a single port, and nothing said so.\n"
              "  Name each instance in the requirements file: "
              "{\"part\": \"tactile-button\", \"name\": \"BtnForward\"}."
              % ", ".join(repeated), file=sys.stderr)
        return EXIT_COULD_NOT_RUN

    unfootprinted = parts_without_a_footprint(part_list)
    if unfootprinted:
        print("no footprint recorded for: %s\n"
              "  Until 2026-09-25 these were emitted as `pinrow4`. A twelve-pad module on four "
              "pads is not a rough draft: the pads past the fourth have no position, so every "
              "trace to them is unroutable and the board comes out with no copper at all.\n"
              "  Record it in the part file — a footprinter string, a converted .kicad_mod, or "
              "jlcpcb:C<lcsc>." % ", ".join(unfootprinted), file=sys.stderr)
        return EXIT_COULD_NOT_RUN

    unpinned = parts_without_a_pinout(part_list)
    if unpinned:
        print("no pin_order recorded for: %s\n"
              "  Pads would be numbered from the order the pins appear in the part file, which "
              "is not a fact about the module. Every trace would land on whichever pad that "
              "order happened to choose.\n"
              "  Record pad 1..N by name, with a source — the silkscreen or the vendor drawing."
              % ", ".join(unpinned), file=sys.stderr)
        return EXIT_COULD_NOT_RUN

    unsized = parts_without_an_outline(part_list)
    if unsized and not args.assume_missing_sizes:
        print("no outline recorded for: %s\n"
              "  Every placement below would be arranged around an invented size, and the board "
              "would then be declared not to overlap on the strength of it.\n"
              "  Measure them and put width/height in the part file with a source, or pass "
              "--assume-missing-sizes to proceed with the guess declared in the output."
              % ", ".join(unsized), file=sys.stderr)
        return EXIT_COULD_NOT_RUN

    placements, width, height = place(board, part_list)
    # The rules come with the design, from the project it was resolved to. They were looked up
    # by the raw `--project` flag instead: None without the flag, so the documented invocation
    # emitted every power trace unsized, exit 0, and called the widths unjustified.
    sys.stdout.write(emit(board, part_list, assignments, placements, width, height,
                          design.rules))

    # To stderr, so it is visible even when stdout is being redirected into a file.
    placed = {entry["signal"] for entry in assignments}
    claimed = {design_library.signal_name(part, need)
               for part in part_list for need in part.get("needs") or []}
    for signal in sorted(placed - claimed):
        print("note: %s was assigned a pin and no part claims it, so nothing in the emitted "
              "board connects to it" % signal, file=sys.stderr)
    for net, part_name, pin in outputs_with_nothing_on_them(part_list):
        print("note: %s.%s drives net.%s and nothing on this board receives it — add whatever it "
              "drives, or that net has one member and will not route" % (part_name, pin, net),
              file=sys.stderr)
    for net in rails_without_a_source(part_list):
        print("note: nothing sources net.%s — add whatever supplies it, or that net has one "
              "member and the board will not route" % net, file=sys.stderr)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
