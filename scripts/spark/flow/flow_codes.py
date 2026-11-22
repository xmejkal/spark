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
#: The needs and parts of a project whose needs.json holds no need and whose requirements.json stays: the last need was dropped (P984).
NO_NEED_LEFT_MESSAGE = "no need is left: the last one was dropped"
NO_PICK_BEHIND_MESSAGE = "no need or pick is behind the parts list"
PICKED_MESSAGE = "%d of %d needs picked"
#: The needs the person set aside (P977): they left them out of this board, so they do not count as open.
ASIDE_MESSAGE = "set aside: %s"
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
NO_FIRMWARE_MESSAGE = "No firmware/main.py yet. Ask Claude to write it in the chat."
TESTED_MESSAGE = "a passed run tested the current image"
NEWER_MESSAGE = "changed after the image: %s"
LOOK_FIRST_MESSAGE = "Ask Claude to look at the board first (/spark:deploy)."
#: What the simulate and deploy phases say (P979): the command's name and who acts, never a path or a placeholder, because the
#: page masks every path. Claude takes the full line from commands/build.md and commands/deploy.md.
NO_SIM_MESSAGE = "No simulation files yet (sim/wokwi.toml). Ask Claude to build the board."
NO_IMAGE_MESSAGE = "No firmware image yet. The scenario run makes one. To skip the simulation, ask Claude to deploy firmware/ untested."
IMAGE_UNTESTED_MESSAGE = "No run tested this image yet. To skip the simulation, ask Claude to deploy firmware/ untested."
DEPLOY_HINT = "Claude then gives you the deploy line. Run it in your terminal and type yes, unless you gave Claude a standing yes for this board."

#: The phases each kind of offer can make out of date (P829). An offer names one only when the phase holds something now
#: (`phase_readers.makes_stale`). The build makes none: the simulation's own staleness is P880's.
MAKES_STALE = {PICK: (REQUIREMENTS,), WRITE_REQUIREMENTS: (BUILD, BREADBOARD), BUILD_BOARD: ()}

#: The label of each offer, the words of its button (P829). <label> is the part's own name, in quotes, so a name that
#: starts with a digit never runs into a count.
PICK_LABEL = "Pick “%s” for %s"
DROP_LABEL = "Drop the %s need"
REQUIREMENTS_LABEL = "Write the parts list"
BUILD_LABEL = "Build the board"
#: The effect of each offer: plain sentences that name every write (P829, the PO, 2026-11-21). The real run on a copy of
#: button-light showed each one (docs/observations/rows/p829-run-request.md).
PICK_MESSAGE = "Saves “%s” as the pick for the %s need in this project."
RESERVE_MESSAGE = "Uses 1 of your %s “%s” for the %s."
RESERVE_MANY_MESSAGE = "Uses 1 of your “%s” for the %s."
RESERVE_UNKNOWN_MESSAGE = "Uses 1 of your “%s” for the %s, if you have one: spark does not know how many you have."
TO_GET_MESSAGE = "You have none, so it goes on the list to get."
#: A pick that `needs.plan_holds` refuses writes nothing, so it is no offer (P976). When another need's pick cannot get
#: its part, the need's says line holds the problem's own sentence once, and the need gets no offers. P993: it says that
#: no new pick can be saved, so it does not read as a refusal of the pick named above it: the need, the other needs, the
#: part's name and the problem's sentence.
NO_NEW_PICK_MESSAGE = "Spark can save no new pick for %s: the pick for %s cannot get “%s” (%s)."
#: The says line of a need with picks left out: how many more are not shown, and each pick its own part refuses, by
#: REFUSED_PART (P991 review, the PO: "even if taken"), "; " between two; then LIST_PICKS_MESSAGE. A count of 0 is left
#: out. The %s after a count is that count's word, from PICK_WORDS.
MORE_PICKS_MESSAGE = "Not shown for %s: %d more %s."
MORE_AND_REFUSED_MESSAGE = "Not shown for %s: %d more %s; refused: %s."
REFUSED_PICKS_MESSAGE = "Not shown for %s, refused: %s."
#: A refused pick: its name, "none free" or "too few free", and the other projects that hold it (HELD_BY).
REFUSED_PART = "“%s” (%s%s)"
NONE_FREE, TOO_FEW_FREE, HELD_BY = "none free", "too few free", ", held by %s"
LIST_PICKS_MESSAGE = "Claude can list them with parts.py --match."
PICK_WORDS = ("pick", "picks")
#: The says line of a need with candidates and none that holds its words or scores above 0: it gets no offers.
NO_PLAUSIBLE_MESSAGE = "No pick fits %s by its words. Ask Claude to run parts.py --match."
#: What a pick lets go (`needs.released_holds`): the hold of the need's old pick, or a hold no pick explained.
FREES_MESSAGE = "Frees what the old pick held."
FREES_UNPICKED_MESSAGE = "Frees a part this project held without a pick."
LIST_PROJECT_MESSAGE = "Adds this project to your list of projects."
PICK_HISTORY_MESSAGE = "May note the choice in your history."
#: A pick the parts list would refuse because spark has no board file for it (P991): the part by its name. The parts
#: list's own sentence starts with `need_requirements.NO_BOARD_FILE`.
NO_BOARD_FILE_MESSAGE = "Spark cannot build from this pick: it has no board file for “%s”."
#: A pick the parts list refuses because its record owes a fact the circuit needs (P993): the part by its name, the
#: needs that pick it ("“…” for screen"), and the facts it owes, so the person reads the blocker before any click.
OWED_MESSAGE = "%s still lacks what spark needs: %s. Ask Claude how to fill it in."
#: A pick the parts list takes though its record owes `simulation` (P996): a warning, never a blocker. The %s is the
#: part's name in quotes with its needs (PICKED_BY).
NO_STANCE_MESSAGE = ("Spark cannot simulate %s yet. The parts list and the build go on, and a deploy asks your yes for "
                     "firmware that no simulation tested.")
PICKED_BY = "%s for %s"
#: The says line that names a need's pick (P991): the need, then each pick's name in quotes (“…”), ", " between two.
PICKED_FOR_MESSAGE = "Picked for %s: %s."
DROP_MESSAGE = "To drop this need, tell Claude: “drop the %s need”."
REQUIREMENTS_MESSAGE = "Writes the parts list, requirements.json, from your picks. Parts you wrote there yourself stay."
SHELVE_MESSAGE = "May copy a part's record from spark's catalog into your store."
ORIGIN_MESSAGE = "Notes which parts spark wrote, in .spark/requirements-origin.json."
BUILD_MESSAGE = ("Saves its files in this project: the board file and its footprint, the dist folder with the schematic "
                 "and PCB pictures, the wiring sheet and its record, the breadboard picture, the Wokwi drawing "
                 "breadboard.json when Wokwi has a part for each part drawn, the pin map your firmware imports, the "
                 "simulation files, the build record in .spark/build.json and this page.")
REPLACE_MESSAGE = ("A board file spark wrote is replaced, and the old one is kept in .spark/previous. A board file you "
                   "changed is left alone.")
BUILD_REFUSED_MESSAGE = "If the parts list has a problem, the old wiring sheet, drawings, this page and the pin map are deleted."
#: A build whose board tool (tscircuit) is not installed does not finish: kept_files removes what described an earlier build.
NO_TOOL_MESSAGE = ("If the board tool is not installed, the board is not built, and the old wiring sheet, drawings and this "
                   "page are deleted.")
#: A parts list that says board_only and names no part: the build skips every stage but the board and the simulation.
BOARD_ONLY_BUILD_EFFECT = ("This board needs no parts, so nothing is built or wired. Saves the pin map your firmware "
                           "imports, the simulation files and the build record in .spark/build.json.")
DIST_REMOVED_MESSAGE = "This board needs no wiring, so the old dist folder is deleted."
BUILT_HISTORY_MESSAGE = "Notes the build in your history."
NO_SIMULATION_MESSAGE = "Runs no simulation and costs nothing."

#: The page's script (P829 PR 3): the kinds of offer the page sends from its buttons (a drop is asked in the chat, P883),
#: and every word the script shows. Python writes them into the page's inert words block; the script fills in only a
#: time, an offer's label or spark's own line. No word says "done" alone.
SENDABLE = (PICK, WRITE_REQUIREMENTS, BUILD_BOARD)
CONFIRM_STALE = "These steps may be marked out of date: %s."
SEND, CANCEL, COPY, WITHDRAW = "Send", "Cancel", "Copy", "Withdraw"
#: What Copy puts on the clipboard: the command that carries the request to spark.
PAGE_COMMAND = "/spark:page"
WAITING_SAYS = "Sent at %s. Nothing has run yet. To run it, type /spark:page in Claude Code."
#: Said once the delete is done: Claude may have started the request before it, so its answer still shows.
WITHDRAWN_SAYS = "Withdrawn. If Claude had already started it, its answer shows here."
#: A write the database refused: the page puts its state back.
NOT_SENT_SAYS = "Could not send. Nothing ran."
NOT_WITHDRAWN_SAYS = "Could not withdraw. The request still waits."
#: The intro of the published page, for its owner: the script puts it in place of PAGE_INTRO.
PUBLISHED_INTRO = "Where this project stands. Use a button to ask spark for a step; Claude runs it at your next /spark:page."
WAITING_FOR = "Waiting for Claude: %s."
PAGE_FROM = "Page from %s."
NEW_STATE = "Reload to see the new state."
#: What the page says when a step ran ok, by its kind: what it did and what is not done yet.
RAN_OK_SAYS = {PICK: "Saved as the pick. Nothing is built yet. " + NEW_STATE,
               WRITE_REQUIREMENTS: "The parts list is written. Nothing is built yet. " + NEW_STATE,
               BUILD_BOARD: "The board builds. It is not wired, not flashed and not simulated yet. " + NEW_STATE}
#: A step of another kind that ran ok, with spark's own line (`ran <label>: ok`); the page sends no other kind today.
RAN_OTHER_SAYS = "Spark says: %s. " + NEW_STATE
RAN_PROBLEMS_SAYS = "Ran, with problems: %s. " + NEW_STATE
COULD_NOT_RUN_SAYS = "Could not run: %s. " + NEW_STATE
#: What the page says of each refusal of `flow.py run-request`, by the code's name: nothing ran, in grey, never red.
REFUSED_SAYS = {"request_stale": "Nothing ran. The project changed after you clicked. Reload this page and click again.",
                "request_not_offered": "Nothing ran. This button is no longer offered. Reload the page.",
                "request_in_chat": "Nothing ran. A need is dropped in the chat: tell Claude which one.",
                "request_malformed": "Nothing ran. The request could not be read. Reload the page and click again."}
#: The mark of a request that ran nothing: a dash, grey.
NOT_RUN_MARK = "–"

#: The page of the project (P827): its code when the file cannot be written, the words a status has no word for, and the
#: bench note. This page does not look at the board, and the note says so.
PAGE_NOT_WRITTEN = "page_not_written"
OK_WORD = "ok"
NOT_CHECKED_WORD = "not checked by spark"
NOT_CHECKED_LEGEND = "spark does not judge this phase, so no mark says it is done"
BENCH_NOTE = "This page reads the project's files. It does not know whether the board is wired or flashed."
STANDS_AT_LINE = "The project stands at: %s."
#: The line under the page's title (P828 step 2, the PO, 2026-11-21: "it just doesn't guide a person"): what the page
#: is and how to act on it. From disk every action is a message to Claude.
PAGE_INTRO = "Where this project stands. This page only shows it. To change anything, tell Claude in the chat."
#: Said under the intro when the page holds wiring steps, so the wiring comes first and the phases are folded below it.
WIRING_FIRST = "Below: the wiring and its pictures, then each phase, folded: click one to read it."
NOTHING_OPEN_LINE = "No phase is open."
#: The guide on the page (P977 PR 2): the label of each line (NOW also names its phase, to tie it to the rail). The link to the
#: first wiring step is the wiring section's own (ONE_AT_A_TIME), drawn when the guide's now holds the wiring (`now.steps`).
GUIDE_NOW, GUIDE_DONE, GUIDE_LATER, GUIDE_SET_ASIDE = "NOW (%s)", "DONE", "LATER", "SET ASIDE"
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
ONE_AT_A_TIME = "One at a time: start at step %d"
STEP_OF = "Step %d of %d"
BACK, NEXT, ALL_STEPS, PICTURE = "Back", "Next", "All steps", "Picture"
BACK_LABEL, NEXT_LABEL = "Back to step %d", "Next: step %d"

#: The guide (P977, the PO, 2026-11-21: "nothing says what to do now"): one sentence for the phase to act on now, keyed by
#: (phase, status). Each names who acts. A phase and status with none here gets PROBLEMS_NOW or COULD_NOT_RUN_NOW.
IDEA_NOW = "Tell Claude your goal in the chat, in your own words."
PARTS_NOW = "%s no part yet: %s. Tell Claude a pick for each, or to set it aside."
ONE_NEED_HAS, MANY_NEEDS_HAVE = "1 need has", "%d needs have"
#: A phase in `later` whose status is ok: it is done now, and a change before it can make it stale (the PO's lens, PR 2 review).
LATER_BUT_DONE = " (done, may change)"
REQUIREMENTS_NOW = "Ask Claude in the chat to write the parts list from your picks."
#: Every need set aside (P980): the parts phase is ok, but the parts list has no pick to be written from.
ALL_ASIDE_NOW = "Every need is set aside, so no pick can make the parts list. Tell Claude which need to bring back, then pick a part."
#: What `done` says of a requirements file with no needs or picks behind it (P980). Not "hand-written" only: a project whose last need was dropped is the same.
REQUIREMENTS_NO_PICKS = "requirements (no needs or picks behind it)"
REQUIREMENTS_STALE_NOW = "Your picks changed. Ask Claude to write the parts list again."
BUILD_NOW = "Ask Claude in the chat to build the board. It takes seconds and costs nothing."
BUILD_STALE_NOW = "The parts list changed since the last build. Ask Claude to build again."
#: The NOW sentences that can carry the page's button (`flow_page.sendable_now`), each with what the published page says
#: in its place where its script adds the button (P993): the step, and to use the button. The page from disk, a viewer
#: who is not the owner and `flow.py show` keep the sentence that names Claude.
NOW_BUTTON = {REQUIREMENTS_NOW: "Write the parts list from your picks. Use the button.",
              REQUIREMENTS_STALE_NOW: "Your picks changed. Write the parts list again. Use the button.",
              BUILD_NOW: "Build the board. It takes seconds and costs nothing. Use the button.",
              BUILD_STALE_NOW: "The parts list changed since the last build. Build the board again. Use the button."}
BUILD_PARTIAL_NOW = "The build stopped. Ask Claude what stopped it and what to do."
SHEET_NOW = "No wiring sheet yet. Ask Claude to build the board."
SHEET_STALE_NOW = "The wiring sheet is out of date. Ask Claude to build the board again."
#: The firmware with a current wiring sheet: two jobs in any order, and the count of the sheet's steps.
TWO_JOBS_NOW = ("Two jobs, in any order: wire the breadboard (%d steps, power off), and ask Claude to write the firmware. "
                "Spark cannot see your wiring.")
FIRMWARE_NOW = "Ask Claude in the chat to write the firmware for this board."
SIMULATE_NOW = "Ask Claude for the scenario command, and run it in your terminal. It uses Wokwi CI minutes."
#: The simulate phase's closing hint is the same sentence (P979).
SCENARIO_HINT = SIMULATE_NOW
DEPLOY_NOW = ("When the breadboard is wired, plug the board into USB. Ask Claude to look at it first, then run the deploy "
              "in your terminal.")
PROBLEMS_NOW = "The %s phase has problems. Ask Claude to go through them with you."
COULD_NOT_RUN_NOW = "The %s phase could not run. Ask Claude to read you why."
NOW_SENTENCES = {(IDEA, None): IDEA_NOW, (PARTS, NOT_STARTED): PARTS_NOW, (PARTS, PARTIAL): PARTS_NOW, (PARTS, OK_WORD): ALL_ASIDE_NOW,
                 (REQUIREMENTS, NOT_STARTED): REQUIREMENTS_NOW, (REQUIREMENTS, STALE): REQUIREMENTS_STALE_NOW,
                 (BUILD, NOT_STARTED): BUILD_NOW, (BUILD, STALE): BUILD_STALE_NOW, (BUILD, PARTIAL): BUILD_PARTIAL_NOW,
                 (BREADBOARD, NOT_STARTED): SHEET_NOW, (BREADBOARD, STALE): SHEET_STALE_NOW, (FIRMWARE, NOT_STARTED): FIRMWARE_NOW,
                 (SIMULATE, NOT_STARTED): SIMULATE_NOW, (DEPLOY, NOT_STARTED): DEPLOY_NOW}
#: What the runs say of the image a simulate with no status names (`ProjectImage`): a run on it did not pass, a file
#: under firmware/ changed after it, no run tested it, or a passed run tested it. The first three leave it open.
RUN_FAILED, IMAGE_OLDER, IMAGE_UNTESTED, IMAGE_TESTED = "run-failed", "image-older", "image-untested", "image-tested"
#: A run failed on the image: logs are one per scenario, so it names the failed log, never "the last run".
RUN_FAILED_NOW = "A run failed on this image (%s). Ask Claude to go through its log with you."
IMAGE_OLDER_NOW = "Your firmware changed after the image. Ask Claude to make the image again, then run the scenario."
#: Who acts on each fact, and its sentence: Claude reads a failed log and makes the image; the terminal runs a scenario.
IMAGE_NOW = {RUN_FAILED: ([BY_CLAUDE], RUN_FAILED_NOW), IMAGE_OLDER: ([BY_CLAUDE], IMAGE_OLDER_NOW),
             IMAGE_UNTESTED: ([BY_TERMINAL], SIMULATE_NOW)}
#: A build whose only stop is a board Wokwi has no model of is counted as done (the PO, 2026-11-21), and these say why.
NO_SIMULATION_NOW = "No simulation: Wokwi has no model of this board. You test it on the real board."
BUILT_NO_SIMULATION = "build (no simulation)"
SIMULATE_NO_MODEL = "simulate (no Wokwi model of this board)"
#: The breadboard in done, once the wiring is no longer part of now: the sheet is current, and spark cannot see the wires.
SHEET_UNSEEN = "breadboard (spark cannot see it)"
#: The offer that does the job of a phase to act on now: (the phase that holds it, its key).
JOB_OFFERS = {REQUIREMENTS: (REQUIREMENTS, WRITE_REQUIREMENTS), BUILD: (BUILD, BUILD_BOARD), BREADBOARD: (BUILD, BUILD_BOARD)}
# --- end MVP ---
