"""
The words of the flow reader (P825): the nine phases in order, the phase words beside the three outcomes, who does each
phase, the keys of its offers and its fixed sentences. A leaf: it imports nothing of spark. A phase word is never an
envelope's `status`, which stays ok, problems or could-not-run.
"""

# --- MVP ---
#: The nine phases of a project, in the order the person goes through them.
PHASES = ("idea", "needs", "parts", "requirements", "build", "breadboard", "firmware", "simulate", "deploy")
IDEA, NEEDS, PARTS, REQUIREMENTS, BUILD, BREADBOARD, FIRMWARE, SIMULATE, DEPLOY = PHASES

#: The phase words beside `outcomes`' ok, problems and could-not-run: nothing done yet, some of it done (some needs
#: picked, or a build with a skipped stage), and done before something it was made from changed.
NOT_STARTED, PARTIAL, STALE = "not-started", "partial", "stale"

#: Who does a phase: the person, Claude in the chat, or the person in their own terminal.
BY_YOU, BY_CLAUDE, BY_TERMINAL = "you", "claude", "your terminal"

#: The keys of the offers. A pick's key is `pick:<need>:<id or entry>` and a drop's `needs-drop:<need>`.
PICK, NEEDS_DROP, WRITE_REQUIREMENTS, BUILD_BOARD = "pick", "needs-drop", "requirements", "build"

#: The codes of the Findings: a phase that holds problems, and one that could not be read or whose last build could not run.
PHASE_PROBLEMS, PHASE_COULD_NOT_RUN = "phase_problems", "phase_could_not_run"

#: What a phase says when nobody recorded a value.
UNKNOWN = "unknown"
IDEA_MESSAGE = "Tell Claude your goal in the chat"
NEEDS_MESSAGE = "%d need(s): %s"
NO_NEEDS_MESSAGE = "no needs yet: Claude writes them from your goal"
#: The needs and parts of a project with requirements.json and no needs: nobody wrote needs, so nothing is open there.
HAND_WRITTEN_MESSAGE = "a hand-written project: requirements.json and no needs"
PICKED_MESSAGE = "%d of %d needs picked"
NO_REQUIREMENTS_MESSAGE = "no requirements.json yet"
NOTHING_TO_COMPARE_MESSAGE = "requirements.json, with no needs to compare it with, so spark did not judge it"
REQUIREMENTS_STALE_MESSAGE = "requirements.json differs from what the picks give"
NO_BUILD_MESSAGE = "no build recorded yet"
BUILT_MESSAGE = "the last build, %s: %s"
BUILD_STALE_MESSAGE = "%s changed after the build"
MISSING_FACTS_MESSAGE = "%d fact(s) the board record lacks, named in firmware/pins.py"
#: A build on the board alone (P878): its four skipped stages are final, so the build and the sheet say so and have no status.
BOARD_ONLY_BUILD_MESSAGE = "board only: nothing to wire, no board was built"
BOARD_ONLY_MESSAGE = "board only: nothing to wire"
#: The one cause of a skipped simulation stage today (`build_service`, P778).
SIMULATION_SKIPPED_MESSAGE = "every part is skipped from the simulation, so spark did not judge the diagram"
NO_SHEET_MESSAGE = "no breadboard.md yet"
SHEET_NOT_JUDGED_MESSAGE = "breadboard.md, spark does not judge the wiring"
SHEET_STALE_MESSAGE = "breadboard.md is from other requirements than requirements.json"
FIRMWARE_MESSAGE = "firmware/main.py written %s"
NO_FIRMWARE_MESSAGE = "no firmware/main.py yet"
TESTED_MESSAGE = "a passed run tested the current image"
NEWER_MESSAGE = "changed after the image: %s"
LOOK_FIRST_MESSAGE = "ask Claude to look at the board first"
#: The commands a phase names, as sentences, with ${CLAUDE_PLUGIN_ROOT} as written and never a resolved path.
SCENARIO_COMMAND = "run ${CLAUDE_PLUGIN_ROOT}/scripts/run_scenario.py sim/scenarios/<name>.scenario.yaml in your terminal: it uses Wokwi CI minutes"
DEPLOY_COMMAND = "then run ${CLAUDE_PLUGIN_ROOT}/scripts/deploy.py --dry-run in your terminal"

#: The phases each kind of offer may make out of date (P829). An offer names one only when the phase holds something now
#: (`phase_readers.makes_stale`). The build makes none: the simulation's own staleness is P880's.
MAKES_STALE = {PICK: (REQUIREMENTS,), WRITE_REQUIREMENTS: (BUILD, BREADBOARD), BUILD_BOARD: ()}

#: The label of each offer, the words of its button (P829). <label> is the part's own name.
PICK_LABEL = "Pick %s for %s"
DROP_LABEL = "Drop the %s need"
REQUIREMENTS_LABEL = "Write the parts list"
BUILD_LABEL = "Build the board"
#: The effect of each offer: plain sentences that name every write (P829; the PO, 2026-11-21). The real run on a copy of
#: button-light showed each one (docs/observations/rows/p829-run-request.md).
PICK_MESSAGE = "Saves %s as the pick for the %s need in this project."
RESERVE_MESSAGE = "Uses 1 of your %s %s for the %s."
RESERVE_MANY_MESSAGE = "Uses 1 of your %s for the %s."
RESERVE_UNKNOWN_MESSAGE = "Uses 1 of your %s for the %s, if you have one: spark does not know how many you have."
TO_GET_MESSAGE = "You have none, so it goes on the list to get."
#: A pick of a part that other projects hold all of is refused, and nothing is written (`needs.plan_holds`).
ALL_HELD_MESSAGE = "All your %s are used by %s, so spark refuses this pick and saves nothing."
LIST_PROJECT_MESSAGE = "Adds this project to your list of projects."
PICK_HISTORY_MESSAGE = "May note the choice in your history."
DROP_MESSAGE = "To drop this need, tell Claude: “drop the %s need”."
REQUIREMENTS_MESSAGE = "Writes the parts list, requirements.json, from your picks. Parts you wrote there yourself stay."
SHELVE_MESSAGE = "May copy a part's record from spark's catalog into your store."
ORIGIN_MESSAGE = "Notes which parts spark wrote, in .spark/requirements-origin.json."
BUILD_MESSAGE = ("Builds the board and saves its files in this project: the board file and its footprint, the dist folder "
                 "with the schematic and PCB pictures, the wiring sheet and its record, the breadboard picture, the pin map "
                 "your firmware imports, the simulation files, the build record in .spark/build.json and this page.")
REPLACE_MESSAGE = ("A board file spark wrote is replaced, and the old one is kept in .spark/previous. A board file you "
                   "changed is left alone.")
BUILD_REFUSED_MESSAGE = "If the parts list has a problem, the old wiring sheet, drawings, this page and the pin map are deleted."
#: A parts list that says board_only and names no part: the build skips every stage but the board and the simulation.
BOARD_ONLY_BUILD_EFFECT = ("This board needs no parts, so nothing is built or wired. Saves the pin map your firmware "
                           "imports, the simulation files and the build record in .spark/build.json.")
DIST_REMOVED_MESSAGE = "This board needs no wiring, so the old dist folder is deleted."
BUILT_HISTORY_MESSAGE = "Notes the build in your history."
NO_SIMULATION_MESSAGE = "Runs no simulation and costs nothing."

#: The page of the project (P827): its code when the file cannot be written, the words a status has no word for, and the
#: bench note. This page does not look at the board, and the note says so.
PAGE_NOT_WRITTEN = "page_not_written"
OK_WORD = "ok"
NOT_CHECKED_WORD = "not checked by spark"
NOT_CHECKED_LEGEND = "spark does not judge this phase, so no mark says it is done"
BENCH_NOTE = "This page reads the project's files. It does not know whether the board is wired or flashed."
STANDS_AT_LINE = "The project stands at: %s."
NOTHING_OPEN_LINE = "No phase is open."
NOT_DRAWN_HERE = "Not drawn here. The build draws it: run /spark:build --keep."
NO_PICTURE_FILE = "Not drawn: %s is not in the project yet. The build with --keep writes it."
UNREADABLE_PICTURE = "Not drawn: %s cannot be read."
NOT_DRAWN_BECAUSE = "Not drawn, because %s."

#: The wiring section of the page (P828, #1186): its heading, the sentence under it, and the words of the step links. A
#: step's label says where it goes, for a screen reader.
WIRING_HEADING = "Wiring"
WIRING_INTRO = "Read the lines before power first."
#: Said only when the breadboard picture is drawn: each jumper carries a pill with its step's number and the two pads it
#: joins (SvgBreadboardDiagram, P953).
WIRING_PICTURE_INTRO = ("In the Breadboard picture below, each jumper carries a pill with its step's number and the two "
                        "pads it joins: find the holes there.")
WIRING_UNREADABLE = "The wiring could not be read from the build's files. Run the build again with --keep."
BREADBOARD_TITLE = "Breadboard"
ONE_AT_A_TIME = "One at a time: start at step 1"
STEP_OF = "Step %d of %d"
BACK, NEXT, ALL_STEPS, PICTURE = "Back", "Next", "All steps", "Picture"
BACK_LABEL, NEXT_LABEL = "Back to step %d", "Next: step %d"
# --- end MVP ---
