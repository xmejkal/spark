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

#: A fact nobody recorded.
UNKNOWN = "unknown"
IDEA_FACT = "Tell Claude your goal in the chat"
NEEDS_FACT = "%d need(s): %s"
NO_NEEDS_FACT = "no needs yet: Claude writes them from your goal"
PICKED_FACT = "%d of %d needs picked"
NO_REQUIREMENTS_FACT = "no requirements.json yet"
HAND_WRITTEN_FACT = "requirements.json, with no needs to compare it with"
REQUIREMENTS_STALE_FACT = "requirements.json differs from what the picks give"
NO_BUILD_FACT = "no build recorded yet"
BUILT_FACT = "the last build, %s: %s"
BUILD_STALE_FACT = "%s changed after the build"
MISSING_FACTS_FACT = "%d fact(s) the board record lacks, named in firmware/pins.py"
NO_SHEET_FACT = "no breadboard.md yet"
SHEET_STALE_FACT = "breadboard.md is from other requirements than requirements.json"
FIRMWARE_FACT = "firmware/main.py written %s"
NO_FIRMWARE_FACT = "no firmware/main.py yet"
TESTED_FACT = "a passed run tested the current image"
NEWER_FACT = "changed after the image: %s"
SCENARIO_LINE = "${CLAUDE_PLUGIN_ROOT}/scripts/run_scenario.py sim/scenarios/<name>.scenario.yaml uses Wokwi CI minutes"
LOOK_FIRST_FACT = "ask Claude to look first"
DEPLOY_LINE = "${CLAUDE_PLUGIN_ROOT}/scripts/deploy.py --dry-run"

#: The effect line of each offer.
PICK_EFFECT = "replaces the picks of need %s in needs.json"
OWNED_EFFECT = "you have %s"
OWNED_UNKNOWN_EFFECT = "how many you have is unknown"
HELD_EFFECT = "held by %s"
DROP_EFFECT = "drops need %s from needs.json and frees its holds"
REQUIREMENTS_EFFECT = "writes requirements.json; may shelve catalog records in your store"
BUILD_EFFECT = "builds the board and keeps its files in the project"
# --- end MVP ---
