"""
The parts on a board (P708): what each is called in the file, which part records lack a pinout, an outline or a footprint,
and where each goes on the first-draft layout.
"""

import re

from spark.design import loader
from spark.sourcing import part_facts


# --- MVP ---
#: Layout constants. Ordinal, not designed — they exist to produce something that does not
#: overlap, so the checks have a board to run on.
MARGIN_MM = 6
GAP_MM = 4
DEFAULT_BODY_MM = (16, 12)


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
    return [part for part in part_list if part_facts.has_placeholder_footprint(part)]


def duplicate_component_names(part_list):
    """
    Names used more than once — each clash as the spellings the design wrote, in their order: `BtnLeft` for a
    copy-pasted entry, `OpenLid / Openlid` for two that differ in capitals.

    The independent safety net for the defect above: whatever route a design takes to two components of one name, this
    catches it before anything is emitted. Two ways to be one name, two merges: an exact repeat is merged by
    `tsci build`, which keeps one component; two spellings are merged by spark's own `loader.signal_name`, which puts
    the instance in capitals, so `OpenLid` and `Openlid` were one signal, placed twice, and the generator traced two
    GPIOs to one pad — both chips emitted, exit 0 — while this compare, exact, saw two names (P163, #100). Compared as
    the build tells names apart, `loader.one_name`.
    """
    written, repeated = {}, set()  # {one name: [each spelling, once, as the design wrote it]}; the one names used twice
    for part in part_list:
        name = component_name(part)
        one = loader.one_name(name)
        if one in written:
            repeated.add(one)
            if name not in written[one]:
                written[one].append(name)
        else:
            written[one] = [name]
    return [" / ".join(written[one]) for one in written if one in repeated]


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

    passives = [name for part in part_list for host_part in part.get("host_parts") or []
                for name in host_part_names(part, host_part)]
    if passives:
        # A third column for the passives the records demand, so nothing sits on a module.
        passives_height = len(passives) * (PASSIVE_BODY_MM[1] + PASSIVE_GAP_MM)
        width += PASSIVE_BODY_MM[0] + GAP_MM
        height = max(height, passives_height + 2 * MARGIN_MM)

    placements = {"Mcu": (-width / 2 + MARGIN_MM + module_width / 2, 0)}
    y = height / 2 - MARGIN_MM
    for part in part_list:
        part_height = body_of(part)[1]
        y -= part_height / 2
        placements[component_name(part)] = (-width / 2 + column_x + widest / 2, y)
        y -= part_height / 2 + GAP_MM
    y = height / 2 - MARGIN_MM
    for name in passives:
        y -= PASSIVE_BODY_MM[1] / 2
        placements[name] = (-width / 2 + column_x + widest + GAP_MM + PASSIVE_BODY_MM[0] / 2, y)
        y -= PASSIVE_BODY_MM[1] / 2 + PASSIVE_GAP_MM
    return placements, width, height


#: A 0603 resistor's footprint, for the passives a record demands of its host.
PASSIVE_BODY_MM = (3.2, 1.6)
PASSIVE_GAP_MM = 2


def host_part_names(part, host_part):
    """The component name(s) a demanded passive gets: the instance, the kind, the pad."""
    pad = re.sub(r"[^A-Za-z0-9]", "", host_part["pin"])
    base = "%s%s%s" % (component_name(part), host_part["kind"].capitalize(), pad)
    if host_part["kind"] == "divider":
        return [base + "Top", base + "Bottom"]
    return [base]
# --- end MVP ---
