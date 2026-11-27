"""
The words of the flow reader (P825): the nine phases in order, the phase words beside the three outcomes, who does each
phase, the keys of its offers and its fixed sentences. A leaf: it imports nothing of spark. A phase word is never an
envelope's `status`, which stays ok, problems or could-not-run.
"""

from collections import namedtuple

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
#: The keys of the chat offers (P1122): the jobs only Claude does, asked in the chat, each with a tell and no step of spark's.
WRITE_FIRMWARE, RUN_SIMULATION, LOOK_AT_BOARD = "write-firmware", "run-simulation", "look-at-board"

#: The codes of the Findings: a phase that holds problems, and one that could not be read or whose last build could not run.
PHASE_PROBLEMS, PHASE_COULD_NOT_RUN = "phase_problems", "phase_could_not_run"

#: What a phase says when nobody recorded a value.
UNKNOWN = "unknown"
#: The idea phase (P1142): the brief's goal as the person wrote it, or the fact that the brief holds none. The instruction to
#: tell Claude the goal is IDEA_NOW's, the guide's NOW, and only while the idea is now.
GOAL_MESSAGE = "your goal is “%s”"
NO_GOAL_MESSAGE = "the brief holds no goal"
NEEDS_MESSAGE = "%d need(s): %s"
NO_NEEDS_MESSAGE = "no needs yet: Claude writes them from your goal"
#: The needs phase when the goal or the must lines changed after the needs were written (P1027): what changed, by
#: CHANGED_WORDS joined with " and ", then the review line. Spark edits none of them.
NEEDS_STALE_MESSAGE = "%s changed after the needs were written"
CHANGED_WORDS = {"goal": "the goal", "must": "the must lines"}
#: Read by the person and by Claude: who reviews, and how the mark clears.
NEEDS_REVIEW_MESSAGE = ("Claude goes through the needs and the must lines with you, and when they still fit, runs "
                        "parts.py --needs-set with []: spark changes none of them itself")
#: Said when the record or the brief cannot be read: the needs phase stays ok, with the reason.
BASIS_UNKNOWN_MESSAGE = "spark cannot tell whether the needs fit the goal: %s"
BASIS_BROKEN = ".spark/needs-basis.json cannot be read"
BRIEF_UNREADABLE = "the brief cannot be read (%s)"
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
REQUIREMENTS_EDITED_MESSAGE = "requirements.json was changed by hand after spark last wrote it, and differs from what the picks give"
NO_BUILD_MESSAGE = "no build recorded yet"
BUILT_MESSAGE = "the last build, %s: %s"
BUILD_STALE_MESSAGE = "%s changed after the build"
#: A record with `requirements: null` (P1095): the last build was the reference design, built from no requirements file.
REFERENCE_BUILD_MESSAGE = "the last build was spark's reference design, not %s"
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
#: The deploy phase after a deploy (P1043): what the newest board log in sim/runs/board/ says. Its time as written, the
#: image's first 12 hex digits, and the words of its verdict; then its cause, and last how many logs there are.
DEPLOYED_MESSAGE = "Last deploy %s, image %s: %s."
DEPLOYS_LOGGED = ("%d deploy logged.", "%d deploys logged.")
#: ON THE BOARD on the page (P1062, `deploy_reading.deployed_line`): the time read in the machine's zone and the verdict's words.
DEPLOYED_LINE = "Last deploy %s. %s."
#: The words of a verdict: ready seen and ready not seen read the files back; ready unknown by its cause's read-back.
#: NO_READ_BACK_WORDS are brief D10's words, exactly (the PO, 2026-11-23).
SEEN_WORDS = "written by the flasher, files read back, ready seen"
NOT_SEEN_WORDS = "written by the flasher, files read back, ready not seen"
NO_READ_BACK_WORDS = "written by the flasher, nothing read back, start not seen"
READ_BACK_WORDS = "written by the flasher, files read back, start not seen"
LOST_WORDS = "written by the flasher, files read back, ready printed, then the board was lost"
UNSURE_WORDS = "written by the flasher, start not confirmed"
#: The words of a flash that did not finish after the yes (P1092): an erase that did not connect leaves the board as it
#: was, so they say "may be erased", never "erased".
FLASH_NOT_FINISHED_WORDS = "flash not finished, nothing read back, the board may be erased"
#: The verdict of that flash in a board log: the bench's `board_log.FLASH_NOT_FINISHED`, an equal literal, as CAUSE_WORDS'
#: codes are, because this module imports nothing of spark. CHAT_NOW reads it.
FLASH_NOT_FINISHED = "flash not finished"
CAUSE_MESSAGE, NO_CAUSE_MESSAGE = "Cause in the log: %s.", "Cause not recorded."
#: The cause of a deploy that did not see ready, or of a flash that did not finish (P1092, P1096), by its code in the board
#: log's reason line (the bench's board_codes and the core's crash, as equal literals: this module imports nothing of spark): spark's words
#: for it, and whether spark read the board's files back (True, False, or None: the log cannot tell). A code not here
#: reads as not recorded. A crash and a Ctrl-C end a flash or a verify (P1110), so their words name no stage, and their
#: read-back is None: a flash not finished takes False from its verdict, and a verify's ready unknown cannot tell.
CAUSE_WORDS = {"files_unread": ("spark did not reach the board to read its files", False),
               "firmware_not_started": ("the command that starts the firmware failed", True),
               "no_files_named": ("the passed run's log names no files, so spark had none to read back", False),
               "board_lost": ("spark found no deepsleep call in firmware/, so it does not count the ready", True),
               "port_gone": ("the board's port was gone", None),
               "download_mode_stayed": ("the board stayed in download mode", None),
               "files_differ": ("the board's files are not the image's", True),
               "firmware_error": ("the firmware stopped with an error", True),
               "no_ready_line": ("the firmware printed no ready line", True),
               "flash_failed": ("a flash command failed", False),
               "grant_ended": ("your yes ended before the erase's retry", False),
               "crash": ("spark crashed during the deploy", None),
               "interrupted": ("a Ctrl-C interrupted the deploy", None)}
#: What the image the project holds now says of the last deploy (`deploy_reading.deploy_fact`): the image it wrote, a
#: different image, firmware/ changed after the image, or no image now. Any but the first makes the deploy stale.
DEPLOY_CURRENT, IMAGE_DIFFERS, FIRMWARE_NEWER, DEPLOY_NO_IMAGE = "current", "image-differs", "firmware-newer", "no-image"
FIRMWARE_NEWER_MESSAGE = "Your firmware changed after the image that the last deploy wrote."
OTHER_IMAGE_MESSAGE = "The last deploy wrote a different image from the one this project has now."
NO_IMAGE_NOW_MESSAGE = "This project has no image now."
#: The says line that opens a stale deploy, by its fact.
STALE_DEPLOY_SAYS = {FIRMWARE_NEWER: FIRMWARE_NEWER_MESSAGE, IMAGE_DIFFERS: OTHER_IMAGE_MESSAGE, DEPLOY_NO_IMAGE: NO_IMAGE_NOW_MESSAGE}

#: The phases each kind of offer can make out of date (P829). An offer names one only when the phase holds something now
#: (`phase_readers.makes_stale`). The build makes none: the simulation's own staleness is P880's.
MAKES_STALE = {PICK: (REQUIREMENTS,), WRITE_REQUIREMENTS: (BUILD, BREADBOARD), BUILD_BOARD: ()}

#: The label of each offer, the words of its button (P829). <label> is the part's own name, in quotes, so a name that
#: starts with a digit never runs into a count.
PICK_LABEL = "Pick “%s” for %s"
#: The why of a pick's step (P1030): a pick is the person's choice, so the step names the part and the need.
PICK_WHY = "The person's choice: “%s” for the %s need"
#: Between two labels, and two whys, of the picks of one page request (P1067): `flow.py run-request`'s answer and the step it
#: runs. No page word.
LABELS_JOIN = "; "
#: The why of the parts phase's own step (P1141), a pick for each open need while no one offer does the job.
PICK_OPEN_WHY = "The person's choice for each need: Claude fills each <part> with an id from parts.py --match, or the need is set aside."
DROP_LABEL = "Drop the %s need"
REQUIREMENTS_LABEL = "Write the parts list"
BUILD_LABEL = "Build the board"
WRITE_FIRMWARE_LABEL, RUN_SIMULATION_LABEL, LOOK_AT_BOARD_LABEL = "Write the firmware", "Run the simulation", "Look at the board"
#: Value: one kind of offer (P1115): the phase whose reader offers it, its label (the name of its button), whether the page
#: sends it from a button (`from_page`), and `tell`, one sentence for Claude that names the job, never the how, or None.
OfferKind = namedtuple("OfferKind", "phase label from_page tell")
#: The kinds of offer, in the order the design basis lists them (P1115): the one place a kind is spelled. A drop is asked in
#: the chat (P883), so the page never sends it, and it has no tell: its words are DROP_MESSAGE (P1118). A *chat offer* is a
#: kind with a tell (P1122): a job only Claude does, so the page never sends it either and shows its tell under ASK_CLAUDE.
OFFER_KINDS = {PICK: OfferKind(PARTS, PICK_LABEL, True, None),
               WRITE_REQUIREMENTS: OfferKind(REQUIREMENTS, REQUIREMENTS_LABEL, True, None),
               BUILD_BOARD: OfferKind(BUILD, BUILD_LABEL, True, None),
               NEEDS_DROP: OfferKind(NEEDS, DROP_LABEL, False, None),
               WRITE_FIRMWARE: OfferKind(FIRMWARE, WRITE_FIRMWARE_LABEL, False, "Write the firmware for this project's board."),
               RUN_SIMULATION: OfferKind(SIMULATE, RUN_SIMULATION_LABEL, False, "Help me run the simulation of this project."),
               LOOK_AT_BOARD: OfferKind(DEPLOY, LOOK_AT_BOARD_LABEL, False, "Look at this project's board with me.")}


def kind_of(key):
    """The kind of an offer's key (P1134): the word before its first colon. A kind alone is a key with no colon."""
    return key.split(":", 1)[0]


def is_sendable(key):
    """True when the page sends the offer of `key` from a button (P1134): its kind's row in OFFER_KINDS says `from_page`.
    False for a drop, a chat offer and a kind spark does not know. The one rule of "can the page send it": the guide, the
    page, run_request and the design basis read it, and the last two add the page's allow-list of ops (STEP_OPERATIONS)."""
    kind = kind_of(key)
    return kind in OFFER_KINDS and OFFER_KINDS[kind].from_page


def in_chat(key):
    """True when `key` is of a kind spark knows and the page never sends (P1134): asked in the chat, never from the page."""
    return kind_of(key) in OFFER_KINDS and not is_sendable(key)


#: The kinds the page sends from its buttons (`is_sendable`).
SENDABLE = tuple(kind for kind in OFFER_KINDS if is_sendable(kind))

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
#: The line of a picked need (P991, P1135): each pick's name in quotes (“…”), ", " between two. The page and `show` put the
#: tick of an ok status before it. KEEP_PICK is the first radio of a picked need on the page, its picks the same way.
PICKED_SAID = "picked %s."
KEEP_PICK = "keep %s"
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
#: A refused parts list builds nothing: kept_files keeps the earlier sheet, drawings (P1093) and pin map (P1109).
BUILD_REFUSED_MESSAGE = ("If spark refuses the parts list, the old wiring sheet, drawings and pin map stay as an earlier "
                         "build's, and this page is deleted.")
#: The same for a board-only parts list, whose build deletes dist/ and the sheet (P236), and a refused one neither (P1109).
BOARD_ONLY_REFUSED_MESSAGE = ("If spark refuses the parts list, the old dist folder, wiring sheet, drawings and pin map stay "
                              "as an earlier build's, and this page is deleted.")
#: A build whose board tool (tscircuit) is not installed does not finish: kept_files keeps the earlier sheet and drawings,
#: named as an earlier build's (P1093), and removes the page.
NO_TOOL_MESSAGE = ("If the board tool is not installed, the board is not built, the old wiring sheet and drawings stay as an "
                   "earlier build's, and this page is deleted.")
#: A parts list that says board_only and names no part: the build skips every stage but the board and the simulation.
BOARD_ONLY_BUILD_EFFECT = ("This board needs no parts, so nothing is built or wired. Saves the pin map your firmware "
                           "imports, the simulation files and the build record in .spark/build.json.")
DIST_REMOVED_MESSAGE = "This board needs no wiring, so the old dist folder is deleted."
BUILT_HISTORY_MESSAGE = "Notes the build in your history."
NO_SIMULATION_MESSAGE = "Runs no simulation and costs nothing."
#: P1044: the witnesses that the person's breadboard can be wired, each with its day ("22 Nov 2026", `wired_board.day_of`).
#: The kept sheet's day is its file's last change, so the line says "dated", never "written", and what spark cannot see.
WIRED_SHEET_MESSAGE = "A wiring sheet dated %s is in the project. Spark cannot see whether you wired from it."
#: The newest board log's day: a log of ready not seen is still a board on the bench, so no word says the firmware ran.
WIRED_DEPLOY_MESSAGE = "Spark logged a deploy to a board on %s."
#: The step after the witnesses, in the parts phase's line: a condition for the person, never a claim that it is wired.
WIRED_STEP_MESSAGE = ("If you wired the board: a new pick needs a new build, and a new build can move pins. Compare the new "
                      "sheet with your wiring before power, and rewire what differs.")
#: The fixed sentences that open a pick's and a build's effect on a board that can be wired. They hold no date, so a newer
#: sheet or log never changes the fingerprint; only a witness that appears or goes away does.
WIRED_PICK_MESSAGE = ("If you wired the board, this pick needs a new build, and a new build can move pins: compare the new "
                      "sheet with your wiring before power, and rewire what differs.")
WIRED_BUILD_MESSAGE = ("If you wired the board, this build can move pins: compare the new sheet with your wiring before "
                       "power, and rewire what differs.")
#: The fixed sentence of each kind of offer that can move a pin.
WIRED_EFFECT = {PICK: WIRED_PICK_MESSAGE, BUILD_BOARD: WIRED_BUILD_MESSAGE}
#: The sentences that every pick of one project says alike (P1135): the Send box says them apart, after the pick's own, so a
#: Send of several picks says each once.
PROJECT_EFFECTS = (WIRED_PICK_MESSAGE, LIST_PROJECT_MESSAGE, PICK_HISTORY_MESSAGE)

#: The page's script (P829 PR 3): every word the script shows, for the kinds of offer the page sends (`SENDABLE`). Python
#: writes them into the page's inert words block; the script fills in only a time, an offer's label or spark's own line.
#: No word says "done" alone.
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
#: The last request under the NOW box (P1062): its time in the browser's zone and its label, then what the page says of it.
LAST_REQUEST_SAYS = "Your last request, %s: %s."
#: The last request's words when its offer is no longer on the page (the review of #1619): by its kind, else one sentence.
LAST_REQUEST_KINDS = {PICK: "a pick", WRITE_REQUIREMENTS: "the parts list", BUILD_BOARD: "the build"}
LAST_REQUEST_OTHER = "a step this page no longer offers"
#: Several picks in one Send (P1067, the P1038 design of 2026-11-23): each need's radios, "not now" first; the Send of the
#: picks named by the count and their needs (PICKS_SAID: one, many), with CHOOSE_FIRST under it while none is chosen; the
#: Send box's last line; the wait; an ok answer; and the last request's words when its picks left the page.
NOT_NOW = "not now"
PICKS_SAID = ("%d pick (%s)", "%d picks (%s)")
SEND_PICKS = "Send %s"
CHOOSE_FIRST = "Choose a part first."
PICKS_TOGETHER_MESSAGE = "Spark checks the picks together. If one fails, spark saves none."
WAITING_PICKS_SAYS = "Sent at %s: %s. Nothing has run yet. To run it, type /spark:page in Claude Code."
LAST_REQUEST_PICKS = "your picks"
#: The script's two joins (P1067): between the needs PICKS_SAID names, and between a pick's label and its words in the Send box.
NEEDS_JOIN, LABEL_JOIN = ", ", ": "
NEW_STATE = "Reload to see the new state."
#: What the page says when a step ran ok, by its kind: what it did and what is not done yet.
RAN_OK_SAYS = {PICK: "Saved as the pick. Nothing is built yet. " + NEW_STATE,
               WRITE_REQUIREMENTS: "The parts list is written. Nothing is built yet. " + NEW_STATE,
               BUILD_BOARD: "The board builds. It is not wired, not flashed and not simulated yet. " + NEW_STATE}
#: Several picks that ran ok (P1067): not a kind, so it stays out of RAN_OK_SAYS.
RAN_OK_PICKS_SAYS = "Saved as the picks. Nothing is built yet. " + NEW_STATE
#: A step of another kind that ran ok, with spark's own line (`ran <label>: ok`); the page sends no other kind today.
RAN_OTHER_SAYS = "Spark says: %s. " + NEW_STATE
#: The note after an ok answer that has one: a build that built while its simulation could not run (P1008), or the
#: notes of a parts-list write, such as the entries it kept that no pick explains (P1139).
RAN_NOTE_SAYS = "Note: %s."
RAN_PROBLEMS_SAYS = "Ran, with problems: %s. " + NEW_STATE
#: Said first of several picks that ran with problems (P1067): PickParts saves all of them or none.
NO_PICK_SAVED_SAYS = "No pick was saved."
COULD_NOT_RUN_SAYS = "Could not run: %s. " + NEW_STATE
#: What the page says of each refusal of `flow.py run-request`, by the code's name: nothing ran, in grey, never red.
REFUSED_SAYS = {"request_stale": "Nothing ran. The project changed after you clicked. Reload this page and click again.",
                "request_not_offered": "Nothing ran. This button is no longer offered. Reload the page.",
                "request_in_chat": "Nothing ran. This step is asked in the chat: tell Claude.",
                "request_malformed": "Nothing ran. The request could not be read. Reload the page and click again."}
#: The refusals of a request of several picks (P1067): as REFUSED_SAYS, but one that spark no longer offers.
REFUSED_PICKS_SAYS = "Nothing ran. Spark no longer offers one of these picks. Reload this page."
REFUSED_PICKS = dict(REFUSED_SAYS, request_not_offered=REFUSED_PICKS_SAYS)
#: The mark of a request that ran nothing: a dash, grey.
NOT_RUN_MARK = "–"
#: The head of the NOW box's block of a chat offer (P1122): plain bold text, never a button. Under it the tell stands in a
#: code box, and the owner's page adds COPY beside it, which says COPIED_SAYS once it copied the tell. It never sends.
ASK_CLAUDE = "Ask Claude"
COPIED_SAYS = "Copied: paste it in Claude Code."

#: The page of the project (P827): its code when the file cannot be written, the words a status has no word for, and the
#: bench note. This page does not look at the board, and the note says so.
PAGE_NOT_WRITTEN = "page_not_written"
OK_WORD = "ok"
NOT_CHECKED_WORD = "not checked by spark"
NOT_CHECKED_LEGEND = "spark does not judge this phase, so no mark says it is done"
#: The design's meaning (P1043-D10) in words that name no phase (the review of #1579).
BENCH_NOTE = "This page reads the project's files and its board logs. It cannot see your wiring or what the board shows now."
STANDS_AT_LINE = "The project stands at: %s."
#: The line under the page's title (P828 step 2, the PO, 2026-11-21: "it just doesn't guide a person"): what the page
#: is and how to act on it. From disk every action is a message to Claude.
PAGE_INTRO = "Where this project stands. This page only shows it. To change anything, tell Claude in the chat."
#: The freshness line under the title (P1062, the P1038 design): the newest change of the fingerprint's files, read in the
#: machine's zone (`zone_time.day_and_time`), or the line for a page that knows no time.
FRESH_LINE = ("This page shows the project as its files last changed, %s. If you changed or deployed something after that, "
              "type /spark:page in the chat.")
FRESH_NONE = ("This page does not know when the project last changed. If you changed or deployed something, type "
              "/spark:page in the chat.")
NOTHING_OPEN_LINE = "No phase is open."
#: The guide on the page (P977 PR 2, P1062): the NOW box's heading (its phase and who acts, `now.by` joined by NOW_BY_JOIN),
#: ON THE BOARD and NEXT, then the muted lines' labels. The link to the first wiring step is the wiring section's own
#: (ONE_AT_A_TIME), drawn on NEXT when the guide's now holds the wiring (`now.steps`).
NOW_BY, NOW_BY_JOIN, ON_BOARD_LABEL, NEXT_ACT_LABEL = "NOW (%s), by %s", " and ", "ON THE BOARD", "NEXT"
#: GUIDE_NOW is the CLI's NOW line (`show_flow`).
GUIDE_NOW, GUIDE_DONE, GUIDE_LATER, GUIDE_SET_ASIDE = "NOW (%s)", "DONE", "LATER", "SET ASIDE"
#: The folds' headings (P1062): the parts, the wiring with its count of steps, the pictures, and the developer fold, always
#: closed, which holds the phases, each offer's key and effect, the marks and the record ids.
PARTS_HEADING, PICTURES_HEADING = "Parts", "Pictures"
WIRING_STEPS = ("Wiring: %d step", "Wiring: %d steps")
DEVELOPER_HEADING = "For developers: the phases, each offer's key and effect, the marks, the record ids"
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
#: (phase, status). Each names who acts. A phase and status with none here gets PROBLEMS_NOW or COULD_NOT_RUN_NOW. A stale parts list is
#: `STALE_REQUIREMENTS`'s (P1140).
IDEA_NOW = "Tell Claude your goal in the chat, in your own words."
PARTS_NOW = "%s no part yet: %s. Pick a part for each, or ask Claude to set one aside."
ONE_NEED_HAS, MANY_NEEDS_HAVE = "1 need has", "%d needs have"
REQUIREMENTS_NOW = "Ask Claude in the chat to write the parts list from your picks."
#: Every need set aside (P980): the parts phase is ok, but the parts list has no pick to be written from.
ALL_ASIDE_NOW = "Every need is set aside, so no pick can make the parts list. Tell Claude which need to bring back, then pick a part."
REQUIREMENTS_STALE_NOW = "Your picks changed. Ask Claude to write the parts list again."
REQUIREMENTS_EDITED_NOW = ("The parts list was changed by hand. Writing it again keeps its parts and puts back what your picks give. "
                           "Ask Claude to write it again, or to change your picks first.")
REQUIREMENTS_DIFFERS_NOW = "The parts list differs from what your picks give. Ask Claude to write it from your picks."
#: A stale parts list (P1140): (the phase line, the guide's sentence) by whether the file is as spark last wrote it
#: (`EntryOriginStore.is_as_written`): True the picks changed, False a hand edit, None spark cannot tell, so no cause.
STALE_REQUIREMENTS = {True: (REQUIREMENTS_STALE_MESSAGE, REQUIREMENTS_STALE_NOW),
                      False: (REQUIREMENTS_EDITED_MESSAGE, REQUIREMENTS_EDITED_NOW),
                      None: (REQUIREMENTS_STALE_MESSAGE, REQUIREMENTS_DIFFERS_NOW)}
BUILD_NOW = "Ask Claude in the chat to build the board. It takes seconds and costs nothing."
BUILD_STALE_NOW = "The parts list changed since the last build. Ask Claude to build again."
#: The NOW sentences that can carry the page's button (`page_sections.sendable_now`), each with what the published page says
#: in its place where its script adds the button (P993): the step, and to use the button. The page from disk, a viewer
#: who is not the owner and `flow.py show` keep the sentence that names Claude.
NOW_BUTTON = {REQUIREMENTS_NOW: "Write the parts list from your picks. Use the button.",
              REQUIREMENTS_STALE_NOW: "Your picks changed. Write the parts list again. Use the button.",
              REQUIREMENTS_EDITED_NOW: ("The parts list was changed by hand. Writing it again keeps its parts and puts back what your "
                                        "picks give. Use the button."),
              REQUIREMENTS_DIFFERS_NOW: "The parts list differs from what your picks give. Write it from your picks. Use the button.",
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
#: The NOW of an open deploy after a deploy (P1043): the job in words, by the status and the cause of the newest board
#: log (`deploy_reading.deploy_now`). No sentence claims what the board does now, and none names a path or a command.
DEPLOY_NO_START_NOW = ("Spark could not confirm that the firmware started after the last deploy. Ask Claude to look at "
                       "the board with you. If the look asks for it, run the deploy again in your terminal.")
DEPLOY_LOST_NOW = ("Spark saw ready after the last deploy, then lost the board, and cannot tell from here whether the "
                   "firmware still runs. If your gadget works, nothing is wrong. Else ask Claude to look at the board with you.")
DEPLOY_AWAY_NOW = "After the last deploy, %s. Ask Claude to look at the board with you."
DEPLOY_UNKNOWN_NOW = ("The log does not say whether the firmware started after the last deploy. Ask Claude to look at the "
                      "board with you.")
DEPLOY_PROBLEMS_NOW = "After the last deploy, %s. Ask Claude to go through the board log with you."
#: The NOW of a flash that did not finish (P1092): it wins over a stale image.
DEPLOY_NOT_FINISHED_NOW = ("The last flash did not finish, so the board may be erased. The board log says what failed. Ask "
                           "Claude to look at the board with you, then run the deploy again in your terminal.")
#: DEPLOY_PROBLEMS_NOW's words when the log records no cause (an old log whose files differed may have printed ready).
NO_READY_SEEN_WORDS = "spark did not see ready"
#: A stale deploy (P1043-D4): who acts first and the sentence, by its fact. Claude makes the image for firmware newer than
#: the image and for no image; the person runs the deploy of the image the project has now.
STALE_DEPLOY_NOW = {FIRMWARE_NEWER: ([BY_CLAUDE], FIRMWARE_NEWER_MESSAGE + " Ask Claude to make the image again and to look "
                                                  "at the board. Then run the deploy line in your terminal."),
                    DEPLOY_NO_IMAGE: ([BY_CLAUDE], NO_IMAGE_NOW_MESSAGE + " Ask Claude to make the image and to look at "
                                                   "the board. Then run the deploy line in your terminal."),
                    IMAGE_DIFFERS: ([BY_TERMINAL], OTHER_IMAGE_MESSAGE + " Ask Claude to look at the board, then run the "
                                                   "deploy line in your terminal.")}
#: The guide's one line when no phase is open: the deploy is ok (P1043, `guide.no_open_phase`).
NO_OPEN_PHASE_NOW = ("Nothing is waiting on you: the last deploy started the image this project holds now. Tell Claude what "
                     "to change next.")
#: The goal is in the brief and no need is written (P1142).
NEEDS_NOW = "Ask Claude in the chat to write the needs from your goal."
NEEDS_STALE_NOW = ("Your goal or must lines changed after the needs were written. "
                   "Ask Claude to go through the needs and the must lines with you.")
#: The idea phase after a need was dropped (P1027, slice 2): the ids, then what Claude asks and how it is taken back. No
#: record links a need to a must line, so Claude names the line in the chat.
NEEDS_DROPPED_MESSAGE = "needs dropped after the must lines were last gone through: %s"
MUST_ASK_MESSAGE = ("Claude asks you about each must line a dropped need served, and on your yes changes it in the brief: "
                    "git keeps each change, so it can be taken back. If the must lines still hold, Claude runs the "
                    "review: parts.py --needs-set with []")
IDEA_STALE_NOW = ("A need was dropped. Claude names it and the must lines it served: tell Claude whether they still "
                  "hold. Claude can change them for you.")
#: Why the brief step (`init_project.py --answers`) is the stale idea's step: it runs only on the person's yes.
BRIEF_WHY = ("On the person's yes: writes the must lines they agreed to into the brief, one commit when git holds it, "
             "so git revert --no-edit takes it back")
PROBLEMS_NOW = "The %s phase has problems. Ask Claude to go through them with you."
COULD_NOT_RUN_NOW = "The %s phase could not run. Ask Claude to read you why."
NOW_SENTENCES = {(IDEA, None): IDEA_NOW, (IDEA, STALE): IDEA_STALE_NOW,
                 (NEEDS, STALE): NEEDS_STALE_NOW,
                 (NEEDS, NOT_STARTED): NEEDS_NOW,
                 (PARTS, NOT_STARTED): PARTS_NOW, (PARTS, PARTIAL): PARTS_NOW, (PARTS, OK_WORD): ALL_ASIDE_NOW,
                 (REQUIREMENTS, NOT_STARTED): REQUIREMENTS_NOW,
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
#: SIMULATE_NOW while no scenario is written (P1034): Claude writes one first, and the terminal still runs it.
SCENARIO_FIRST_NOW = ("No scenario is written yet, so ask Claude to write one first. Then ask for the scenario command, and "
                      "run it in your terminal. It uses Wokwi CI minutes.")
#: The value a simulate's SCENARIO_FIRST_NOW is chosen by (P1133): no scenario is written. Its one CHAT_NOW row keeps the tell.
NO_SCENARIO = "no-scenario"
#: A simulate not started with no sim/wokwi.toml (P1034): the build writes it, so the sentence asks for the build.
NO_SIM_FILES = "no-sim-files"
SIM_FILES_NOW = "No simulation files yet (sim/wokwi.toml). Ask Claude to build the board again. It takes seconds and costs nothing."
#: Why a scenario run is the simulate's step (P1034): the person runs it, and it spends Wokwi CI minutes.
SCENARIO_WHY = ("The person runs it in their own terminal, with a Wokwi CI token in WOKWI_CLI_TOKEN. It spends Wokwi CI "
                "minutes, so ask before each run.")
#: Why the step names the placeholder scenario: no scenario is written yet, so Claude writes it first.
SCENARIO_FIRST_WHY = "Claude first writes the scenario from the person's words, in place of <name>. " + SCENARIO_WHY
#: Why the look is the deploy's step (P1034): the person wires and plugs the board in first.
LOOK_WHY = ("The person wires the breadboard and plugs the board into USB first. The look reads the board, and the board "
            "restarts while it is read.")
#: A build whose only stop is a board Wokwi has no model of is counted as done (the PO, 2026-11-21), and this says why.
NO_SIMULATION_NOW = "No simulation: Wokwi has no model of this board. You test it on the real board."
#: The station line (P1119): where a phase stands beside the phase to act on now, as the guide's `stations` gives it.
DONE_PLACE, NOW_PLACE, LATER_PLACE = "done", "now", "later"
#: A station's one note (P1119), or None: a requirements file with no needs or picks behind it (P980) and the needs and parts
#: nobody did then, a build or simulate counted as done because Wokwi has no model of the board, a breadboard before now with
#: a current sheet (spark cannot see the wires) or with none, and a later phase whose status is ok (a change before it can
#: make it stale, the PO's lens, P977 PR 2 review).
NO_PICKS_NOTE, NOT_DONE_NOTE, NO_MODEL_NOTE, UNSEEN_NOTE, NO_SHEET_NOTE, MAY_CHANGE_NOTE = (
    "no-picks", "not-done", "no-model", "unseen", "no-sheet", "may-change")
#: The notes that leave a phase out of DONE and LATER: nobody did it, or there is no current sheet to wire from.
LEFT_OUT_NOTES = frozenset((NOT_DONE_NOTE, NO_SHEET_NOTE))
#: The words of each other note, which DONE and LATER put after the phase (NOTED_PHASE): "requirements (no needs or picks
#: behind it)". The no-model note of the simulate has its own words (STATION_NOTES_BY_PHASE).
STATION_NOTES = {NO_PICKS_NOTE: "no needs or picks behind it", NO_MODEL_NOTE: "no simulation",
                 UNSEEN_NOTE: "spark cannot see it", MAY_CHANGE_NOTE: "done, may change"}
STATION_NOTES_BY_PHASE = {(NO_MODEL_NOTE, SIMULATE): "no Wokwi model of this board"}
NOTED_PHASE = "%s (%s)"
#: The plain name of each phase on the page's station line (P1119, the canvas of 2026-11-25). A phase not here shows its word.
PHASE_NAMES = {IDEA: "Idea", NEEDS: "Needs", PARTS: "Parts", REQUIREMENTS: "Parts list", BUILD: "Board files",
               BREADBOARD: "Wiring", FIRMWARE: "Firmware", SIMULATE: "Simulation", DEPLOY: "On the board"}
#: The steps spark does not have yet (P1102, P1119, the PO's "Nine plus three greyed"): (key, name, the person's moment,
#: hand-written). The station line greys them after the nine, and the design basis lists them.
UNBUILT_STEPS = (
    ("perfboard", "Perfboard", "At the bench with a soldering iron: the same circuit, soldered to last. Optional."),
    ("pcb", "PCB", "At the desk: a board to order, once the breadboard works."),
    ("case", "Case", "At the printer: a case for the board."),
)
NOT_BUILT = "not built"
#: The station line's name for a screen reader (P1119), and what each station says to it after its name: its place and its
#: status word, comma apart ("Wiring: now, not started"), since its mark is hidden from it.
STATIONS_LABEL = "Where the project stands"
STATION_SAID = ": %s"
#: The chat offer whose job the NOW sentence asks Claude for (P1122), by a NowSentence's `chosen_by` (P1133): (the now phase,
#: the value its picker chose the sentence by): a status, a simulate's image fact (IMAGE_NOW's keys), NO_SCENARIO, a stale
#: deploy's fact, the verdict of a flash that did not finish, or PROBLEMS or COULD_NOT_RUN for the sentences of those. Any
#: other is None, so no tell stands beside a sentence that asks for something else: a failed run, an image to make again,
#: problems or a run that could not run.
CHAT_NOW = {(FIRMWARE, NOT_STARTED): WRITE_FIRMWARE,
            (SIMULATE, NOT_STARTED): RUN_SIMULATION, (SIMULATE, IMAGE_UNTESTED): RUN_SIMULATION,
            (SIMULATE, NO_SCENARIO): RUN_SIMULATION,
            (DEPLOY, NOT_STARTED): LOOK_AT_BOARD, (DEPLOY, PARTIAL): LOOK_AT_BOARD, (DEPLOY, FLASH_NOT_FINISHED): LOOK_AT_BOARD,
            (DEPLOY, IMAGE_DIFFERS): LOOK_AT_BOARD}
#: Value: the NOW sentence a picker chose (P1133, `guide.who_and_sentence`, `deploy_reading.deploy_now`, `guide.requirements_now`): who acts (`by`), the
#: sentence (`says`), and `chosen_by`, the (phase, value) pair it chose the sentence by, never an actor, which
#: `guide.chat_offer_of` looks up in CHAT_NOW once, on the last sentence (`guide.now_of`).
NowSentence = namedtuple("NowSentence", "by says chosen_by")
# --- end MVP ---
