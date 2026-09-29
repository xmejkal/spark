#!/usr/bin/env python3
"""
How much current a piece of copper carries, and how wide it has to be.

ONE definition of this arithmetic, because two things need it and they must not disagree:
`check_physics` judges a board by it, and `emit_board` sizes traces by it. They had separate
answers for a while — the generator had none at all and emitted the router's 0.15 mm default
everywhere, including on a car whose traction rail carries 2.9 A — and when the generator finally
learned to size a trace it did so by reaching into the checker with `importlib`. Two copies of one
formula is how a board passes its own tool and fails a fab; a module reaching into another by file
path is how that becomes impossible to test.

So this is a module with no dependencies and no side effects. Everything in it is arithmetic on
numbers, which makes it the one part of this plugin that can be checked against a table in a
handbook.

WHAT THE FORMULA IS, AND WHAT IT IS NOT

IPC-2221 external layer: `I = k * dT^0.44 * A^0.725`, with area in square mils. It gives the
current at which a trace reaches a stated temperature rise above ambient, for a LONG, UNIFORM,
unobstructed trace in still air. It is a limit, not a target.

It is wrong in both directions for the things real boards do. A trace buried between planes runs
hotter than it says. A sub-millimetre neck where a trace enters a pad runs COOLER, because the pad
is a lump of copper bonded to a barrel and it sinks the heat — which is why `sustained_width_mm`
exists rather than simply taking the narrowest segment anywhere.
"""

#: IPC-2221 external-layer constants: I = k * dT^0.44 * A^0.725, with A in square mils.
IPC_K_EXTERNAL = 0.048
IPC_DT_EXPONENT = 0.44
IPC_AREA_EXPONENT = 0.725

#: 1 oz/ft^2 finished copper, the default on every cheap 2-layer process.
COPPER_THICKNESS_MM = 0.035
MM_PER_MIL = 0.0254

#: The rise every trace-width calculator opens with, and what this plugin assumes when a project
#: does not say. Stated once so the generator and the checker cannot pick different ones.
DEFAULT_RISE_C = 10

#: Never ask for a trace narrower than this, whatever the arithmetic says.
#:
#: Taking the IPC minimum literally produced 0.12 mm for a 0.5 A logic rail — narrower than the
#: router's own 0.15 mm default and at the edge of what a cheap process etches repeatably
#: (JLCPCB's economy minimum is 0.127 mm and their recommendation is higher). Going below buys
#: nothing: a narrower trace is not cheaper, only more fragile.
MIN_TRACE_WIDTH_MM = 0.15

#: How much wider than the IPC minimum to ask for.
#:
#: Not padding for its own sake. IPC gives the width at which a trace REACHES a temperature rise,
#: etching tolerance eats into it, and a router necks a trace where it must fit. Asking 15 % wide
#: leaves the result above the limit rather than at it.
TRACE_WIDTH_MARGIN = 1.15

#: A run shorter than this is a neck, not a trace.
#:
#: Measured on a real generated board: asking for 1.50 mm produced 86 segments at 1.50 and six
#: between 0.12 mm and 0.85 mm LONG at 1.20 mm wide — every one of them the last step into a
#: 1.2 mm pad. Judging those by a formula for long uniform traces reports a board as unbuildable
#: because of copper that cannot get hot: the pad is a heatsink bonded to a plated barrel.
#:
#: The constriction is real and belongs to the PAD, which is `check_footprints`' subject, not the
#: trace's. Reporting it here as "your trace is too narrow" sends somebody to widen a trace that
#: is already wide enough.
NECK_LENGTH_MM = 1.0


def current_capacity_a(width_mm, rise_c=DEFAULT_RISE_C):
    """IPC-2221 external-layer current for a trace of this width."""
    area_mils2 = (width_mm / MM_PER_MIL) * (COPPER_THICKNESS_MM / MM_PER_MIL)
    return IPC_K_EXTERNAL * (rise_c ** IPC_DT_EXPONENT) * (area_mils2 ** IPC_AREA_EXPONENT)


def width_for_current_mm(current_a, rise_c=DEFAULT_RISE_C):
    """The narrowest trace that carries this current within a temperature rise."""
    area_mils2 = (current_a / (IPC_K_EXTERNAL * rise_c ** IPC_DT_EXPONENT)) ** (
        1 / IPC_AREA_EXPONENT)
    return area_mils2 * MM_PER_MIL * MM_PER_MIL / COPPER_THICKNESS_MM


def width_to_emit_mm(current_a, rise_c=DEFAULT_RISE_C):
    """
    The width to ASK a router for, or None when the default is already enough.

    Margin applied and floored at the process minimum, so the sizing only ever widens. None means
    "the default carries this" — emitting a thickness then would be a narrower number dressed as
    a decision.
    """
    if not isinstance(current_a, (int, float)) or current_a <= 0:
        return None
    wanted = width_for_current_mm(float(current_a), float(rise_c)) * TRACE_WIDTH_MARGIN
    return None if wanted <= MIN_TRACE_WIDTH_MM else wanted


def sustained_width_mm(segments):
    """
    The narrowest width this trace holds for long enough to matter, or None if it is all necks.

    `segments` is an iterable of `(width_mm, length_mm)`.

    The alternative — the narrowest width anywhere — is what a first version did, and it reported
    a correctly sized 2.9 A rail as unbuildable because of a 0.12 mm-long step into a pad. A neck
    that short cannot reach a steady temperature: it is bonded to a pad and a plated barrel, both
    of which are heatsinks. The constriction is real and it belongs to the pad, which is a
    footprint question, not a trace one.
    """
    runs = [width for width, length in segments
            if width and length is not None and length >= NECK_LENGTH_MM]
    return min(runs) if runs else None


def necks(segments):
    """The (width, length) pairs too short to judge as traces — reported, never silently dropped."""
    return [(width, length) for width, length in segments
            if width and length is not None and length < NECK_LENGTH_MM]
