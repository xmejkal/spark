"""
The reasons a build stops or an init cannot finish, each a code with one sentence (P701, W6-U2): check_spine.py and
init_project.py.

A leaf: it imports nothing of spark. Each refusal names its code, so an agent decides on the code and never on the English
sentence (no magic strings, P260). Each stage of the build that does not end ok carries its `code` (stages.Stage),
the design's own when a design error stopped it (design_codes); init_project returns a `Refusal` (`spark.core.result`).
Only the breadboard sheet's `not written` entry writes its code into --json's `kept` today: the rest wait in the library
for the Operation that comes later.

Four codes are equal literals of another leaf, with the same meaning: BOARD_UNUSABLE and NO_PROJECT_FOLDER are
design_codes', TOOL_MISSING board_codes' and firmware_codes', INPUT_AMBIGUOUS check_codes'.
"""


# --- MVP ---
#: BuildService: the requirements and the parts.
BOARD_UNUSABLE, BOARD_ONLY_WITH_PARTS, NO_PARTS = "board_unusable", "board_only_with_parts", "no_parts"
#: A stage that crashed or ran past its limit, and the board emitter that refused or noted.
STAGE_CRASHED, STAGE_TIMED_OUT = "stage_crashed", "stage_timed_out"
SCHEMATIC_REFUSED, SCHEMATIC_NOTED = "schematic_refused", "schematic_noted"
#: The build: the board engine, and what it built.
TOOL_MISSING, TOOL_CANNOT_BUILD = "tool_missing", "tool_cannot_build"
DESIGN_NOT_BUILT, NOT_ROUTED, PART_STRANDED = "design_not_built", "not_routed", "part_stranded"
#: The simulation project.
SIMULATION_FACT_MISSING, CHIP_NOT_COMPILED = "simulation_fact_missing", "chip_not_compiled"
CONVERTER_LACKS_PART, NO_DIAGRAM, DIAGRAM_UNWIRED = "converter_lacks_part", "no_diagram", "diagram_unwired"
#: init_project.main.
NO_PROJECT_FOLDER, TOOLS_FILE_UNREADABLE = "no_project_folder", "tools_file_unreadable"
UNKNOWN_BOARD, NOTHING_TO_DO, INPUT_AMBIGUOUS = "unknown_board", "nothing_to_do", "input_ambiguous"
ANSWERS_UNUSABLE = "answers_unusable"

#: Each code and the one sentence that says what it means.
CODES = {
    BOARD_UNUSABLE: "the board the design names is unknown, or its record cannot be read or breaks the board contract",
    BOARD_ONLY_WITH_PARTS: "the requirements say board_only and name parts too, so they say two things",
    NO_PARTS: "the requirements name no parts and do not say board_only, so there is nothing to build",
    STAGE_CRASHED: "a stage of the build, or a file --keep writes, raised an error it did not expect",
    STAGE_TIMED_OUT: "a tool the build ran did not finish in its time limit",
    SCHEMATIC_REFUSED: "the board emitter refused the design in its own words, such as a part with no outline",
    SCHEMATIC_NOTED: "the board emitter wrote the board and said something about it, such as a size it assumed",
    TOOL_MISSING: "a tool the step needs is missing or cannot be used",
    TOOL_CANNOT_BUILD: "the board engine cannot build even a trivial board from here, so the tool is broken, not the design",
    DESIGN_NOT_BUILT: "the board engine built no circuit from the design, or a circuit with errors in it",
    NOT_ROUTED: "the board built with no trace: one net could not be routed, so none was",
    PART_STRANDED: "a part of the built board reaches no ground, has an end on nothing, or is not on the net that feeds it",
    SIMULATION_FACT_MISSING: "a part or the board lacks the record the simulation is made from, or a part record cannot be read",
    CHIP_NOT_COMPILED: "a custom chip the simulation needs has no compiled binary, or did not compile",
    CONVERTER_LACKS_PART: "the diagram converter has no Wokwi part for a component: its mapping lacks it, the design built",
    NO_DIAGRAM: "the diagram converter wrote no diagram",
    DIAGRAM_UNWIRED: "the diagram holds the parts and no wire joins them",
    NO_PROJECT_FOLDER: "--project names no folder, or the folder a project is looked for from is gone",
    TOOLS_FILE_UNREADABLE: "the project's tools file cannot be read, so nothing was written",
    UNKNOWN_BOARD: "--board names a board neither the project nor spark has",
    ANSWERS_UNUSABLE: "--answers names a file that is not a JSON object of the brief's fields: goal a text, must, prefer, "
                      "sellers and decided lists",
    NOTHING_TO_DO: "every file init writes is there already, and --force was not given",
    INPUT_AMBIGUOUS: "an input matched more than one file, and nothing chose between them",
}
# --- end MVP ---
