"""
The reasons a build stops or an init cannot finish, each a Code with its meaning and its fix (P701, W6-U2, P935):
check_spine.py and init_project.py.

A leaf: it imports nothing of spark but `spark.core.codes`. Each refusal names its code, so an agent decides on the code
and never on the English sentence (no magic strings, P260). Each stage of the build that does not end ok carries its `code`
(a `StageEnding` of stages.BUILD_STAGES), a skip too (P936), the design's own when a design error stopped it
(design_codes); init_project returns a `Refusal` (`spark.core.result`). check_spine.py --json writes a stage's code in its
entry of `stages` (P936), and the breadboard sheet's `not written` entry's in `kept`. A `Finding.of` takes the fix from
its code.

Every code is a Code with its fix (P935 PR 5). Four are equal literals of another leaf, with the same meaning:
BOARD_UNUSABLE and NO_PROJECT_FOLDER are design_codes', TOOL_MISSING board_codes' and firmware_codes', INPUT_AMBIGUOUS
check_codes'. BOARD_UNUSABLE and INPUT_AMBIGUOUS hold the other leaf's fix too (a test pins each pair); NO_PROJECT_FOLDER
and TOOL_MISSING hold the build's own fix, because the build's step says more (row 12 of docs/observations/rows/p935-build.md).
"""

from spark.core.codes import Code

# --- MVP ---
#: BuildService: the requirements and the parts.
BOARD_UNUSABLE = Code("board_unusable", "the board the design names is unknown, or its record cannot be read or breaks the board contract",
                      "fix the board record the sentence names, or give a board id that boards.py --list shows")
BOARD_ONLY_WITH_PARTS = Code("board_only_with_parts", "the requirements say board_only and name parts too, so they say two things",
                             'in the requirements file, remove "board_only": true to build the parts, or remove the parts to build the '
                             "board alone, then build again")
NO_PARTS = Code("no_parts", "the requirements name no parts and do not say board_only, so there is nothing to build",
                'add the parts to the requirements file (`parts.py --requirements` writes them), or add "board_only": true if the '
                "project runs on the board alone, then build again")
#: A stage that crashed or ran past its limit, and the board emitter that refused or noted.
STAGE_CRASHED = Code("stage_crashed", "a stage of the build, or a file --keep writes, raised an error it did not expect",
                     "if the sentence names a file of yours, fix that file and build again. Otherwise report it at "
                     "https://github.com/xmejkal/spark/issues with the sentence and the command you ran")
STAGE_TIMED_OUT = Code("stage_timed_out", "a tool the build ran did not finish in its time limit",
                       "build again. If it runs past its limit again, report it at https://github.com/xmejkal/spark/issues "
                       "with the sentence and the command you ran")
SCHEMATIC_REFUSED = Code("schematic_refused", "the board emitter refused the design in its own words, such as a part with no outline",
                         "do what the sentence asks in the part record or the requirements file that it names, then build again")
SCHEMATIC_NOTED = Code("schematic_noted", "the board emitter wrote the board and said something about it, such as a size it assumed",
                       "tell the person each note. If a value the emitter assumed is wrong, write the right one in the part record "
                       "or the requirements file that the note names, then build again")
#: The build: the board engine, and what it built.
TOOL_MISSING = Code("tool_missing", "a tool the step needs is missing or cannot be used",
                    "ask the person to run /spark:setup, which installs the tool that the sentence names, then build again")
TOOL_CANNOT_BUILD = Code("tool_cannot_build", "the board engine cannot build even a trivial board from here, so the tool is broken, not the design",
                         "ask the person to run /spark:setup, or `npm i @tscircuit/cli` in the project folder, then build again")
DESIGN_NOT_BUILT = Code("design_not_built", "the board engine built no circuit from the design, or a circuit with errors in it",
                        "fix the first error or the engine's last lines that the sentence shows, in the requirements file or a part "
                        "record, then build again")
NOT_ROUTED = Code("not_routed", "the board built with no trace: one net could not be routed, so none was",
                  "build again with one part fewer to find the part whose net cannot be routed, then fix that part's record. If no "
                  "part is at fault, report it at https://github.com/xmejkal/spark/issues with the requirements file")
PART_STRANDED = Code("part_stranded", "a part of the built board reaches no ground, has an end on nothing, or is not on the net that feeds it",
                     "join the part that the sentence names to the net it is missing, in its record's pins or in the requirements "
                     "file, then build again")
#: The simulation project.
SIMULATION_FACT_MISSING = Code("simulation_fact_missing",
                               "a part or the board lacks the record the simulation is made from, or a part record cannot be read",
                               "add simulation.wokwi, or simulation.skip with a reason, to the record that the sentence names "
                               "(/spark:research finds the facts), then build again. The board built")
CHIP_NOT_COMPILED = Code("chip_not_compiled", "a custom chip the simulation needs has no compiled binary, or did not compile",
                         "if the sentence says the chip has no compiled binary, ask the person to run /spark:setup. Otherwise fix the "
                         "error it shows in the chip's .chip.c beside its record. Then build again")
CONVERTER_LACKS_PART = Code("converter_lacks_part",
                            "the diagram converter has no Wokwi part for a component: its mapping lacks it, the design built",
                            "test that part on the bench. The design built. Report the component that the sentence names at "
                            "https://github.com/xmejkal/spark/issues so that the converter can map it")
NO_DIAGRAM = Code("no_diagram", "the diagram converter wrote no diagram",
                  "if the sentence names a file of yours, fix that file and build again. Otherwise report it at "
                  "https://github.com/xmejkal/spark/issues with the sentence and the command you ran")
DIAGRAM_UNWIRED = Code("diagram_unwired", "the diagram holds the parts and no wire joins them",
                       "report it at https://github.com/xmejkal/spark/issues with the requirements file: the converter wired "
                       "none of the parts")
#: The board's record names no Wokwi part (P977): no simulation can run, and the flow's guide passes such a build.
BOARD_NOT_IN_WOKWI = Code("board_not_in_wokwi", "the board's record names no Wokwi part, so Wokwi has no model of it and nothing is simulated",
                          "if Wokwi has a part for this board, write it in the board record's wokwi_part_type and build again. Else "
                          "test the firmware on the board itself: the board built")
#: A stage the build skipped, which is never ok and never a problem (P936, the PO 2026-11-20): it had nothing to do.
BOARD_ONLY = Code("board_only", "the requirements say board_only and name no part, so the project runs on the board alone "
                  "and this stage has nothing to wire", "nothing to fix: the firmware is written for the board alone; "
                  "firmware/pins.py, written with --keep, holds the pin map")
EVERY_PART_SKIPPED = Code("every_part_skipped", "every part's record skips the simulation (simulation.skip), so the diagram "
                          "holds none of the project's parts; the board built", "nothing to fix in the design: no simulation "
                          "shows these parts, so test them on the bench; each record's simulation.skip says why")
#: init_project.main.
NO_PROJECT_FOLDER = Code("no_project_folder", "--project names no folder, or the folder a project is looked for from is gone",
                         "give --project a folder that exists, or run init_project.py from the project folder")
TOOLS_FILE_UNREADABLE = Code("tools_file_unreadable", "the project's tools file cannot be read, so nothing was written",
                             "fix the tools file that the sentence names so that it holds JSON, or move it away, then run "
                             "init_project.py again")
UNKNOWN_BOARD = Code("unknown_board", "--board names a board neither the project nor spark has",
                     "give --board one of the boards that the sentence lists, then run init_project.py again")
NOTHING_TO_DO = Code("nothing_to_do", "every file init writes is there already, and --force was not given",
                     "nothing to fix: the project is set up. Give --force to merge what is derived into rules.json, which keeps "
                     "your answers")
INPUT_AMBIGUOUS = Code("input_ambiguous", "an input matched more than one file, and nothing chose between them",
                       "pick one of the files the sentence lists and give it with the flag the sentence names, then run again")
ANSWERS_UNUSABLE = Code("answers_unusable", "--answers names a file that is not a JSON object of the brief's fields: goal a text, must, prefer, "
                        "sellers and decided lists",
                        "fix the file that the sentence names: the answers must be one JSON object of the brief's fields that it "
                        "lists, or fix the brief that it names. Then run init_project.py again")

#: Each code and the one sentence that says what it means.
CODES = {code: code.meaning for code in (
    BOARD_UNUSABLE, BOARD_ONLY_WITH_PARTS, NO_PARTS, STAGE_CRASHED, STAGE_TIMED_OUT, SCHEMATIC_REFUSED, SCHEMATIC_NOTED,
    TOOL_MISSING, TOOL_CANNOT_BUILD, DESIGN_NOT_BUILT, NOT_ROUTED, PART_STRANDED, SIMULATION_FACT_MISSING, CHIP_NOT_COMPILED,
    BOARD_NOT_IN_WOKWI, CONVERTER_LACKS_PART, NO_DIAGRAM, DIAGRAM_UNWIRED, BOARD_ONLY, EVERY_PART_SKIPPED, NO_PROJECT_FOLDER,
    TOOLS_FILE_UNREADABLE, UNKNOWN_BOARD, ANSWERS_UNUSABLE, NOTHING_TO_DO, INPUT_AMBIGUOUS)}
# --- end MVP ---
