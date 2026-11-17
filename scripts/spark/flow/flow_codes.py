"""
The words of the flow reader (P825): the nine phases in order, the phase words beside the three outcomes, who does each
phase, the keys of its offers and its fixed sentences. A leaf: it imports nothing of spark. A phase word is never an
envelope's `status`, which stays ok, problems or could-not-run.
"""

# --- MVP ---
#: The nine phases of a project, in the order the person goes through them.
PHASES = ("idea", "needs", "parts", "requirements", "build", "breadboard", "firmware", "simulate", "deploy")
IDEA, NEEDS, PARTS, REQUIREMENTS, BUILD, BREADBOARD, FIRMWARE, SIMULATE, DEPLOY = PHASES

#: The phase words beside `outcomes`' ok, problems and could-not-run: nothing done yet, some of it done, and done before
#: something it was made from changed.
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
NOTHING_TO_COMPARE_MESSAGE = "requirements.json, with no needs to compare it with"
REQUIREMENTS_STALE_MESSAGE = "requirements.json differs from what the picks give"
NO_BUILD_MESSAGE = "no build recorded yet"
BUILT_MESSAGE = "the last build, %s: %s"
BUILD_STALE_MESSAGE = "%s changed after the build"
MISSING_FACTS_MESSAGE = "%d fact(s) the board record lacks, named in firmware/pins.py"
NO_SHEET_MESSAGE = "no breadboard.md yet"
SHEET_STALE_MESSAGE = "breadboard.md is from other requirements than requirements.json"
FIRMWARE_MESSAGE = "firmware/main.py written %s"
NO_FIRMWARE_MESSAGE = "no firmware/main.py yet"
TESTED_MESSAGE = "a passed run tested the current image"
NEWER_MESSAGE = "changed after the image: %s"
LOOK_FIRST_MESSAGE = "ask Claude to look at the board first"
#: The commands a phase names, as sentences, with ${CLAUDE_PLUGIN_ROOT} as written and never a resolved path.
SCENARIO_COMMAND = "run ${CLAUDE_PLUGIN_ROOT}/scripts/run_scenario.py sim/scenarios/<name>.scenario.yaml in your terminal: it uses Wokwi CI minutes"
DEPLOY_COMMAND = "then run ${CLAUDE_PLUGIN_ROOT}/scripts/deploy.py --dry-run in your terminal"

#: The effect line of each offer.
PICK_MESSAGE = "replaces the picks of need %s in needs.json"
OWNED_MESSAGE = "you have %s"
OWNED_UNKNOWN_MESSAGE = "how many you have is unknown"
HELD_MESSAGE = "held by %s"
DROP_MESSAGE = "drops need %s from needs.json and frees its holds"
REQUIREMENTS_MESSAGE = "writes requirements.json; may shelve catalog records in your store"
BUILD_MESSAGE = "builds the board and keeps its files in the project"

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
#: Said only when the breadboard picture is drawn: its jumpers carry their step's number and color (SvgBreadboardDiagram).
WIRING_PICTURE_INTRO = "In the Breadboard picture below, each jumper has its step's number and color: find the holes there."
WIRING_UNREADABLE = "The wiring could not be read from the build's files. Run the build again with --keep."
BREADBOARD_TITLE = "Breadboard"
ONE_AT_A_TIME = "One at a time: start at step 1"
STEP_OF = "Step %d of %d"
BACK, NEXT, ALL_STEPS, PICTURE = "Back", "Next", "All steps", "Picture"
BACK_LABEL, NEXT_LABEL = "Back to step %d", "Next: step %d"
# --- end MVP ---
