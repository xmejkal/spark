"""
The reasons a design cannot be loaded, placed or emitted, each a code with one sentence (P700, W6-D2): loader.load,
pin_assigner, board_emitter and footprint_emitter.

A leaf: it imports nothing of spark. Each refusal names its code, so an agent decides on the code and never on the English
sentence (no magic strings, P260). A refusal that raises gives its error a `code` (DesignError, ImpossibleError, RefusedInputError);
one that returns a sentence returns a `Refusal` (`spark.core.result`), a str with a `code`, so every text and JSON stays
byte-equal. No design CLI writes a code yet: the codes wait in the library for the Operation that comes later.

RULES_REFUSED is also check_codes', as an equal literal in two leaves, with the same meaning.
"""


# --- MVP ---
#: design.load: the requirements file, the project, and the records it names.
NO_REQUIREMENTS, REQUIREMENTS_UNREADABLE = "no_requirements", "requirements_unreadable"
REQUIREMENTS_FIELD_WRONG, NAME_USED_TWICE = "requirements_field_wrong", "name_used_twice"
NO_PROJECT_FOLDER, PART_UNUSABLE, BOARD_UNUSABLE = "no_project_folder", "part_unusable", "board_unusable"
RULES_REFUSED = "rules_refused"
#: assign_pins: an ImpossibleError, a signal no pin can take.
UNKNOWN_BUS, NOT_A_BUS_LINE, BUS_LINE_NOT_ON_BOARD = "unknown_bus", "not_a_bus_line", "bus_line_not_on_board"
UNKNOWN_NEED, NO_SUCH_PIN, NAMED_PIN_UNSUITABLE = "unknown_need", "no_such_pin", "named_pin_unsuitable"
PIN_TAKEN, NO_PIN_LEFT, SIGNAL_NAME_UNUSABLE = "pin_taken", "no_pin_left", "signal_name_unusable"
#: board_emitter: a part record lacks what a board is placed and traced from.
NO_PART_FOOTPRINT, NO_PIN_ORDER, NO_OUTLINE = "no_part_footprint", "no_pin_order", "no_outline"
SERIES_RESISTOR_UNSIZED = "series_resistor_unsized"
#: footprint_emitter, and board_emitter's footprint stage: the board record cannot give a footprint.
BOARD_LACKS_FOOTPRINT, BOARD_DISAGREES = "board_lacks_footprint", "board_disagrees"

#: Each code and the one sentence that says what it means.
CODES = {
    NO_REQUIREMENTS: "there is no requirements file at the path given",
    REQUIREMENTS_UNREADABLE: "the requirements file is not JSON, or it cannot be read",
    REQUIREMENTS_FIELD_WRONG: "a field of the requirements file is of the wrong kind, or names what no part or board has",
    NAME_USED_TWICE: "two parts or two signals of the design have one name, so the build would make them one",
    NO_PROJECT_FOLDER: "--project names no folder, or the folder a project is looked for from is gone",
    PART_UNUSABLE: "a part the design names is unknown, or its record cannot be read or breaks the part contract",
    BOARD_UNUSABLE: "the board the design names is unknown, or its record cannot be read or breaks the board contract",
    RULES_REFUSED: "the rules file cannot be used: it is not JSON, or a value is of the wrong kind or below its lowest",
    UNKNOWN_BUS: "a signal is on a bus spark does not know",
    NOT_A_BUS_LINE: "a signal on a bus is not one of that bus's lines",
    BUS_LINE_NOT_ON_BOARD: "a signal needs a bus line that the board labels no pin for",
    UNKNOWN_NEED: "a signal asks for something a pin cannot be asked for",
    NO_SUCH_PIN: "a signal names a pin the board does not bring out",
    NAMED_PIN_UNSUITABLE: "a signal names a pin that is a strapping pin, or that cannot do what the signal needs",
    PIN_TAKEN: "a signal names a pin another signal already holds",
    NO_PIN_LEFT: "no free pin of the board can do what a signal needs",
    SIGNAL_NAME_UNUSABLE: "a signal's name is no Python name, or a name the pin map gives the board's own part",
    NO_PART_FOOTPRINT: "a part record states no footprint",
    NO_PIN_ORDER: "a part record states no pin_order, so its pads cannot be numbered",
    NO_OUTLINE: "a part record states no outline, and --assume-missing-sizes was not given",
    SERIES_RESISTOR_UNSIZED: "a series resistor cannot be sized: a fact it needs is missing, or the pin cannot light the part",
    BOARD_LACKS_FOOTPRINT: "the board record lacks the facts its footprint is drawn from",
    BOARD_DISAGREES: "the board record disagrees with itself: a value of the wrong kind, or a pad order that does not fit",
}
# --- end MVP ---
