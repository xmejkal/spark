"""
Stops a bad input and gives the board file, from a pin map and a module list, with the notes about the design the file
cannot carry as a refusal. The build (`BuildService`) and the CLI `emit_board.py` ask it through `BoardEmitter` (P706).

This is the last step of "I have these modules, wire them up". Everything before it — which board,
what each module asks for, which pin each signal goes on — is settled by `board_records.py`,
`parts.py` and `assign_pins.py`. This turns that into tscircuit: `board_sections` writes each section, `power_rails`
answers for the rails, and `board_components` names and places the parts (P708).

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

from dataclasses import dataclass

from spark.design import pin_assigner
from spark.design import loader
from spark.design import design_codes
from spark.design import footprint_emitter

from spark.core.result import Refusal
from spark.design.board_components import (duplicate_component_names, parts_without_a_footprint,
                                           parts_without_a_pinout, parts_without_an_outline, place)
from spark.design.board_sections import emit
from spark.design.power_rails import (outputs_in_contention, outputs_with_nothing_on_them, pair_sides_without_a_driver,
                                      rails_without_a_source)

#: What this script prints for input it refuses, before any board is emitted; `check_spine` says the same (P407).
REFUSED_INPUT_MESSAGE = "cannot emit a board: %s"
#: The two stages that can refuse the input, named as the spine's stages are (P432): the design is read and its pins are
#: placed under the first, and the board's footprint is asked for under the second, in that order.
SCHEMATIC_STAGE = "schematic"
FOOTPRINT_STAGE = "footprint"


# --- MVP --- (P432, OC1) one order in which the input is refused, for `main` and the spine's build.
@dataclass(frozen=True)
class BoardInputs:
    """Value: what a build reads before it emits anything: the design, and the pin each of its signals was given."""

    design: object
    assignments: list


class RefusedInputError(Exception):
    """
    Error: the input was refused at `stage` (`SCHEMATIC_STAGE` or `FOOTPRINT_STAGE`) for `why`. `str()` is the line each
    caller prints: the schematic words around `why`, or `why` alone for a footprint gap, which has its own sentence (P407).
    `code` (design_codes) is the refused input's own: the DesignError's or the ImpossibleError's, or the footprint's (P700).
    """

    def __init__(self, stage, why, code):
        super().__init__(REFUSED_INPUT_MESSAGE % why if stage == SCHEMATIC_STAGE else why)
        self.stage = stage
        self.why = why
        self.code = code


def read_inputs(path, project, board_id=None):
    """
    The design at `path` and its pin assignments, or `RefusedInputError`: a fault in the requirements first, then pins that
    cannot be placed, then a board record that cannot give a footprint. A fault in the requirements is said before a gap in
    the board record, because a person who fixed the board would meet the typo next (P407). Prints nothing.
    """
    try:
        design = loader.load(path, project, board_id)
        board = design.board
        # The signals are the loader's — derived once, named per instance — so `assign_pins.py`
        # and this file cannot disagree about which signals a design has.
        assignments, _ = pin_assigner.assign(board, design.signals)
    except (loader.DesignError, pin_assigner.ImpossibleError) as broken:
        # Everything wrong with the INPUT is could-not-run: the file was never a design. Reading
        # it used to happen above this `try`, and a malformed file was a traceback with exit 1 —
        # which reads as "problems found" to anything that knows three outcomes.
        raise RefusedInputError(SCHEMATIC_STAGE, str(broken), broken.code) from broken
    no_footprint = footprint_emitter.why_no_footprint(board) or footprint_emitter.why_wrong_kind(board)  # --- MVP --- (P434): `place` does arithmetic on them
    if no_footprint:
        raise RefusedInputError(FOOTPRINT_STAGE, no_footprint, no_footprint.code)
    return BoardInputs(design, assignments)


# --- MVP --- (P700): what stops a board once its input is read, each with its code, so `main` only parses and prints.
#: Each gap in the part records, in the order it is said: what finds it, its code (design_codes) and its sentence.
PART_GAPS = (
    (duplicate_component_names, design_codes.NAME_USED_TWICE,
     "two or more components would be called: %s\n"
     "  A name written twice: `tsci build` keeps ONE of them, so every pin assigned to the others is wired to the "
     "survivor — five identical buttons became one component with five GPIOs shorted to a single port, and nothing "
     "said so. Two spellings (OpenLid / Openlid): spark's own naming puts an instance in capitals before its "
     "signals, so they are one signal, placed twice and traced to one pad from two GPIOs.\n  Name each instance in "
     "the requirements file: {\"part\": \"tactile-button\", \"name\": \"BtnForward\"}."),
    (parts_without_a_footprint, design_codes.NO_PART_FOOTPRINT,
     "no footprint recorded for: %s\n"
     "  Until 2026-09-25 these were emitted as `pinrow4`. A twelve-pad module on four pads is not a rough draft: the "
     "pads past the fourth have no position, so every trace to them is unroutable and the board comes out with no "
     "copper at all.\n  Record it in the part file — a footprinter string, a converted .kicad_mod, or jlcpcb:C<lcsc>."),
    (parts_without_a_pinout, design_codes.NO_PIN_ORDER,
     "no pin_order recorded for: %s\n"
     "  Pads would be numbered from the order the pins appear in the part file, which is not a fact about the "
     "module. Every trace would land on whichever pad that order happened to choose.\n  Record pad 1..N by name, "
     "with a source — the silkscreen or the vendor drawing."),
    (parts_without_an_outline, design_codes.NO_OUTLINE,
     "no outline recorded for: %s\n"
     "  Every placement below would be arranged around an invented size, and the board would then be declared not to "
     "overlap on the strength of it.\n  Measure them and put width/height in the part file with a source, or pass "
     "--assume-missing-sizes to proceed with the guess declared in the output."),
)


def board_file(inputs, assume_missing_sizes=False):
    """Value: (the board file's text, None), or (None, the Refusal that stops it): the first gap of PART_GAPS (no outline
    only without `assume_missing_sizes`), else a resistor `series_ohms` cannot size. The rules are the design's (A2)."""
    design, part_list = inputs.design, inputs.design.parts
    for find, code, sentence in PART_GAPS:
        found = find(part_list)
        if found and not (assume_missing_sizes and code == design_codes.NO_OUTLINE):
            return None, Refusal(sentence % ", ".join(found), code)
    placements, width, height = place(design.board, part_list)
    try:
        return emit(design.board, part_list, inputs.assignments, placements, width, height, design.rules), None
    except ValueError as refused:
        # a number the resistor needs is missing, or the pin cannot light it: the input's, not a traceback and exit 1 (F9)
        return None, Refusal(REFUSED_INPUT_MESSAGE % refused, design_codes.SERIES_RESISTOR_UNSIZED)
# --- end MVP ---


def design_notes(inputs):
    """
    The notes about a design that stop nothing, each one line led by `note: ` (P706): a pin no part claims, an output nothing
    receives, a rail nothing sources (one side of a driven pair in its own words, F15), and a rail two supplies drive. The
    build's `schematic-notes` stage and the CLI's stderr carry them; nothing here changes `inputs`.
    """
    part_list = inputs.design.parts
    placed = {entry["signal"] for entry in inputs.assignments}
    claimed = {loader.signal_name(part, need) for part in part_list for need in part.get("needs") or []}
    notes = ["note: %s was assigned a pin and no part claims it, so nothing in the emitted board connects to it" % signal
             for signal in sorted(placed - claimed)]
    notes += ["note: %s.%s drives net.%s and nothing on this board receives it — add whatever it drives, or that net has one "
              "member and will not route" % (part_name, pin, net) for net, part_name, pin in outputs_with_nothing_on_them(part_list)]
    pair_sides = pair_sides_without_a_driver(part_list)
    for net in rails_without_a_source(part_list):
        if net in pair_sides:  # F15: what drives a side of a pair is an amplifier, and a supply into it destroys it
            notes.append("note: nothing drives net.%s, one side of a driven pair — add what drives the pair (the amplifier this "
                         "terminal hangs off), never a supply, or that net has one member and the board will not route" % net)
            continue
        notes.append("note: nothing sources net.%s — add whatever supplies it, or that net has one member and the board will "
                     "not route" % net)
    for net, who in outputs_in_contention(part_list):
        notes.append("note: net.%s is driven by more than one supply (%s) — two supplies on one rail short into each other; "
                     "move one to its own rail or state the arrangement" % (net, ", ".join(who)))
    return notes


class BoardEmitter:
    """
    Service: the board file's three steps as one object, a facade (GoF) over this module's `read_inputs`, `board_file` and
    `design_notes`, so `BuildService` is given one collaborator and the CLI `emit_board.py` calls the same three (P706).
    It prints nothing, so it is no Renderer. `assume_missing_sizes` is the CLI's flag: lay out around a guessed size for a
    part whose outline nobody recorded, saying so in the file.
    """

    def __init__(self, assume_missing_sizes=False):
        self.assume_missing_sizes = assume_missing_sizes

    def read(self, path, project, board_id=None):
        """The design at `path` and its pin assignments (`BoardInputs`), or `RefusedInputError`."""
        return read_inputs(path, project, board_id)

    def emit(self, inputs):
        """(the board file's text, None), or (None, the Refusal that stops it)."""
        return board_file(inputs, self.assume_missing_sizes)

    def notes(self, inputs):
        """The design's notes, each one line."""
        return design_notes(inputs)
