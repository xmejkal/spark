"""
The answer of deploy (P213 PR a; an OperationResult since P655): `deploy_result`, built from what the run found, and the
steps and words it shares with the look (`deploy_step`, `yes_rule`, `doctor_fix`; the look's items are in
spark.bench.look_at_board, P442). Every Finding carries a `code` from board_codes, the reason an agent decides on (P433).

Nothing here runs a command or prints. The status comes from the one Finding, chosen from the exit code the run already
decided, so the status and the exit code cannot disagree.
A step that needs the person (`needs_yes`) is a step Claude relays, never one it runs on its own: the token is
not the yes, and neither is "go ahead" in a chat.
"""

from pathlib import Path

from spark.bench import board_codes
from spark.bench import board_doctor
from spark.bench import board_look
from spark.bench import download_mode
from spark.records import board_records
from spark.bench.deploy_stages import DeployPhase
from spark.design import loader
from spark.core import codes, outcomes
from spark.core.result import Finding, NextStep, OperationResult
from spark.bench import ready_probe
from spark.records import store
from spark.bench.deploy_gate import NEXT_LOOK, NEXT_DEPLOY
from spark.firmware import sleep_calls

#: What the person must do first, said in a step's `why`.
YES_RULE = "the person types yes in their own terminal%s; the token and \"go ahead\" in a chat are not the yes"
#: What YES_RULE adds when a deploy grant can answer, and when only one given with --no-simulation can (P1029).
GRANT_CLAUSE = " (or a deploy grant stands)"
NO_SIMULATION_GRANT_CLAUSE = " (or a deploy grant given with --no-simulation stands)"
#: Why the person runs the grant line, and what it adds for an image that no simulation tested (P1029).
GRANT_STEP_WHY = "the person runs it once in their own terminal; it lets Claude erase ALL of the flash for N minutes (1 to 1440, 60 here)"
GRANT_STEP_NO_SIMULATION = ", and with --no-simulation, write firmware that no simulation tested"

#: A `fix` for each thing a deploy can wait for.
FIX_FOR_NEXT = {NEXT_DEPLOY: "the person runs data.run_in_terminal in their own terminal", NEXT_LOOK: "run look.py again"}
#: The board's state after a flash command failed, and after a crash once the flash finished (P655).
MAY_BE_ERASED, FLASHED_NOT_VERIFIED = "may_be_erased", "flashed_not_verified"

#: The words that fill board_codes.READY_UNKNOWN's fix (P1022), each from a fact of the DeployResult: the board's files
#: read or not (ReadyResult.files_read), what the console printed (DeployResult.console) and the facts file written or not.
FILES_READ = "The board's files were read, but mpremote did not start the firmware"
FILES_NOT_READ = "The board's files were not read"
CONSOLE_NOT_READ = "The board's console was not read, and spark did not see `ready`"
CONSOLE_SILENT = "The board's console printed nothing, so spark did not see `ready`"
CONSOLE_PRINTED = "The board's console printed `%s`, and no `ready`"
CONSOLE_READY = "The board's console printed `%s`, so the firmware started"
FACTS_WRITTEN = "The facts file spark.json was written and read back"
FACTS_NOT_WRITTEN = "The facts file spark.json was not written"
#: How many characters of a console line the fix quotes: the board's text reaches Claude, so it is short and plain.
QUOTE_LIMIT = 80


def quoted(line):
    """The console line `line` as the fix quotes it: no backtick, no control character, and at most QUOTE_LIMIT characters."""
    plain = "".join(character for character in line if character.isprintable() and character != "`")
    return plain if len(plain) <= QUOTE_LIMIT else plain[:QUOTE_LIMIT - 3] + "..."


def console_words(console):
    """What the fix says of the board's console after the flash: its ready line, else its first line, else that it printed
    nothing, or that it was not read (`console` None)."""
    if console is None:
        return CONSOLE_NOT_READ
    lines = [line.strip() for line in console.splitlines() if line.strip()]
    ready = [line for line in lines if download_mode.booted(line)]
    return CONSOLE_READY % quoted(ready[0]) if ready else CONSOLE_PRINTED % quoted(lines[0]) if lines else CONSOLE_SILENT


def ready_unknown_fix(result, places):
    """The fix of a ready_unknown deploy, the one text the CLI says and the JSON item carries (P1022): READY_UNKNOWN's
    template filled from the DeployResult `result` and the RESET place of `places` (a ButtonPlaces), or the fix of
    READY_UNKNOWN_NO_FILES when the passed run's log names no files."""
    if not result.facts["files"]:
        return board_codes.READY_UNKNOWN_NO_FILES.fix
    return board_codes.READY_UNKNOWN.fix % {
        "files": FILES_READ if result.ready.files_read else FILES_NOT_READ, "console": console_words(result.console),
        "facts": FACTS_WRITTEN if result.facts_line.written else FACTS_NOT_WRITTEN,
        "reset": places.reset, "orientation": places.orientation}


#: The fix of a look that finds no board while the project's firmware calls deepsleep (P1022 slice 3): an opening for each
#: code, then the deepsleep calls (at most two), the own-USB words, and the steps with the cable check last. In deep sleep
#: the chip's own USB-Serial/JTAG is off (ESP-IDF v5.5 docs/en/api-guides/usb-serial-jtag-console.rst lines 83 and
#: 101-107); a board behind a USB bridge chip stays on USB, so without the record's `usb` pin role the words are a
#: condition. In download mode the chip runs no program from flash (esptool v5.5.0 boot-mode-selection.rst line 64).
ASLEEP_OPENING = {board_codes.NO_PORT: "no board is on USB", board_codes.PORT_NOT_LISTED: "the port you named is not on USB"}
ASLEEP_KNOWS = "What spark knows: "
ASLEEP_FIX = (ASLEEP_KNOWS + "%(opening)s, and the project's firmware calls deepsleep (%(calls)s). %(usb)s What spark did "
              "not do: it read no board and wrote nothing. What to try, in order: 1. Hold the board's %(boot)s, press and "
              "release %(reset)s, then release BOOT%(orientation)s. The board should then wait in download mode: it runs no "
              "firmware, so it stays on USB. Run look.py again, and use the port it names. After a deploy from download "
              "mode, press %(reset)s once, with BOOT not held, so the firmware starts. 2. Or wait until the firmware wakes, "
              "and run look.py while it is awake. 3. If the board still does not show, check the cable: a data cable "
              "straight into the computer, not a hub that gives power only.")
OWN_USB_SLEEP = "In deep sleep the chip's own USB is off, so the board leaves USB with the cable in, until it wakes."
MAYBE_OWN_USB_SLEEP = ("If the board's USB is the chip's own (USB-Serial/JTAG), it is off in deep sleep, and the board "
                       "leaves USB with the cable in until it wakes.")
UNPARSED = "These files of firmware/ did not parse, so spark does not know whether they call deepsleep: %s."


def own_usb_of(project):
    """True when the project's board record has the pin role `usb` (board_rules: the chip's own USB D- and D+), so its USB
    plug is the chip's own and no USB bridge chip's. False when it has none or cannot be read."""
    try:
        roles = board_records.load(project).get("pin_roles")
    except (OSError, ValueError, AttributeError, board_records.BoardError):
        return False
    return isinstance(roles, dict) and isinstance(roles.get("usb"), dict)


def asleep_fix(project, reason, places):
    """The fix of a no_port or port_not_listed stop when the project's firmware calls deepsleep: ASLEEP_FIX, its buttons
    named as `places` (a ButtonPlaces) does; UNPARSED when no call was found and a file did not parse; else ''."""
    if reason not in ASLEEP_OPENING:
        return ""
    found = sleep_calls.deep_sleep_calls(project)
    if not found.places:
        return UNPARSED % ", ".join(found.unparsed) if found.unparsed else ""
    return ASLEEP_FIX % {"opening": ASLEEP_OPENING[reason], "calls": ", ".join(found.places[:2]), "boot": places.boot,
                         "usb": OWN_USB_SLEEP if own_usb_of(project) else MAYBE_OWN_USB_SLEEP,
                         "reset": places.reset, "orientation": places.orientation}


def asleep_stop(stop, project, places):
    """(the sentence, the fix) of a LookStopError that no doctor answered: the asleep fix, and beside it on a no_port stop
    only NO_BOARD, because the fix holds the cable check as its last step. Else the stop's own sentence."""
    fix = asleep_fix(project, stop.reason, places)
    no_board = stop.reason == board_codes.NO_PORT and fix.startswith(ASLEEP_KNOWS)
    return (board_look.NO_BOARD if no_board else str(stop)), fix


def yes_rule(evidence, grant_may_answer):
    """YES_RULE for this evidence: a grant clause only where a deploy grant can answer (`grant_may_answer`: the caller's
    GrantService.refusal_of is None, P1029), the --no-simulation one for an image that no simulation tested."""
    return YES_RULE % ((NO_SIMULATION_GRANT_CLAUSE if evidence.grant_refusal else GRANT_CLAUSE) if grant_may_answer else "")


def deploy_argv(project, token, port, evidence):
    """The arguments of deploy.py for this board and image (not the script's name, as parts.py's steps)."""
    return ["--project", str(project), "--token", token or "", "--port", port] + evidence.argv()


def look_argv(project, port, evidence):
    """The arguments of look.py (the evidence's too, when there is one)."""
    return ["--project", str(project)] + (["--port", port] if port else []) + (evidence.argv() if evidence else [])


def look_step(project, port, evidence=None, why="read the board first: the board restarts while it is read", needs_person=None):
    """The step that runs look.py. It writes nothing. With no evidence, its arguments are the project's alone. `needs_person`
    is True after a deploy stopped at the board (P892): the look asks the person first."""
    return outcomes.add_env(outcomes.step("look", look_argv(project, port, evidence), why, needs_person=needs_person), store.read_given_env())


#: Why a finished build names the look step next (P517): the board is read, then the conversation writes the firmware.
WHY_FIRMWARE_NEXT = "first write firmware/main.py from pins.py"


def firmware_next_steps(code_ok, requirements_file):
    """The `next` of a build's verdict: the look step with the firmware to write, or [] unless the build is ok in a real project."""
    project = loader.project_for(requirements_file) if requirements_file else None
    return [look_step(project, None, why=WHY_FIRMWARE_NEXT)] if code_ok and project and not loader.is_library(project) else []


def next_text(steps):
    """The line that says the same steps to a person (nothing for none), built from their own arguments."""
    return "".join("  next: %s — %s\n" % (store.format_rerun_line(Path(__file__).parents[2] / ("%s.py" % each["op"]), each["argv"]), each["why"])
                   for each in steps)


def deploy_step(project, token, port, evidence, why):
    """The step that runs deploy.py: it erases ALL of the flash, so it needs the person's yes."""
    return outcomes.add_env(outcomes.step("deploy", deploy_argv(project, token, port, evidence), why,
                                          effects=["deletes", "writes"], needs_yes=True), store.read_given_env())


#: The placeholder of the agent's replies file in a step's arguments, and why the same deploy runs again after the person's
#: yes to the board question (P892, decision 5): it reads the board, then stops at the erase's own yes.
REPLIES_PLACEHOLDER = "<your replies file>"
ASK_AGAIN_WHY = ("the same deploy, after the person's yes to the board question in the conversation: it reads the board (a "
                 "restart), then waits for the erase's own yes. With no terminal and no deploy grant, the person's own run in a "
                 "terminal asks the board question once more and reads the board again")


def ask_again_step(project, token, port, evidence):
    """The step that runs the same deploy with the person's yes to the board question in a replies file (P892). It needs the
    person's yes to that question; the erase still asks its own, so it is no `needs_yes` step."""
    return outcomes.add_env(outcomes.step("deploy", deploy_argv(project, token, port, evidence) + ["--replies", REPLIES_PLACEHOLDER],
                                          ASK_AGAIN_WHY, effects=["deletes", "writes"], needs_person=True), store.read_given_env())


def doctor_fix(doctor, places):
    """The `fix` of a DoctorProbeResult: its next step's sentence, naming the buttons as `places` does, or '' when there
    is no doctor result or it names no step."""
    return board_doctor.step_sentence(doctor.next_step, places) if doctor and doctor.next_step else ""


def _finding(reached, code):
    """The one Finding of a deploy run that did not reach ready, of the exit `code`'s severity: its subject is the stage, or
    `ready` once the board was read, its code the reason, its fix the doctor's step, the fix the run said (P1022) or the
    step of what it waits for."""
    result, doctor = reached.get("result"), reached.get("doctor")
    fix = (doctor_fix(doctor, board_records.ButtonPlaces.of_project(reached["project"])) if doctor
           else reached.get("fix") or FIX_FOR_NEXT.get(reached.get("next_op"), ""))
    return Finding(outcomes.STATUS_FOR[code], "ready" if result else reached["stage"], reached.get("reason"), reached.get("refusal"), fix)


def _steps(reached):
    """The NextSteps of a deploy run: the look after a dry run or a stale look, the deploy line (and the grant line) the
    person runs when there was no terminal, the REPL to watch when ready is unknown."""
    result, evidence, next_op = reached.get("result"), reached["evidence"], reached.get("next_op")
    project, port = reached["project"], reached.get("port") or (reached["report"].port if reached.get("report") else None)
    following = []
    if reached.get("dry_run"):
        following = [look_step(project, port, evidence, "deploy.py --dry-run did not look at the board")]
    elif reached.get("reason") == codes.NEEDS_REPLY:  # P892: the board question is open
        following = [ask_again_step(project, reached.get("token"), port, evidence)]
    elif next_op == NEXT_LOOK:  # P892: after a stop at the board the look asks the person first
        why = reached.get("next_why")
        following = [look_step(project, port, evidence, why or "the look is missing or stale", bool(why) or None)]
    elif next_op == NEXT_DEPLOY:
        following = [deploy_step(project, reached.get("token"), port, evidence,
                                 "the person runs data.run_in_terminal in their own terminal: " + yes_rule(evidence, reached.get("grant_may_answer")))]
        if reached.get("grant_argv"):
            following.append(outcomes.add_env(outcomes.step("grant", reached["grant_argv"],
                                           GRANT_STEP_WHY + (GRANT_STEP_NO_SIMULATION if evidence.grant_refusal else ""),
                                           effects=["writes"], needs_yes=True), store.read_given_env()))
    elif result and result.ready.verdict == ready_probe.UNKNOWN:
        following = _unknown_steps(result, project, port, evidence)
    return [NextStep(**step) for step in following]


#: Why each step of a ready_unknown deploy whose board did not answer comes, in the fix's order (P1022).
UNKNOWN_LOOK_WHY = ("first: wait a minute, because a firmware that sleeps at start answers nothing. The look shows whether the "
                    "board is on USB and answers esptool. It restarts the board, and it reads no files and no ready")
UNKNOWN_LIVE_WHY = ("second: the person presses RESET once first. Then live.py asks the board to run one line and says whether "
                    "the board answers. On Espressif's USB-Serial/JTAG it opens the port as quietly as deploy.py's check does. "
                    "It needs a live grant: if it refuses, it prints the grant line the person runs in their own terminal. It "
                    "stops the firmware and resets the board after")
UNKNOWN_WATCH_WHY = ("last: the person opens the REPL (data.repl_command), presses Ctrl-C, then Ctrl-D, and the firmware prints "
                     "`ready`. On Espressif's USB-Serial/JTAG (303a:1001) mpremote's own open can leave the board deaf to spark "
                     "until the next flash. Never deploy again for this")
#: The line live.py runs: it holds no digit, so live.py lists no GPIO.
UNKNOWN_LIVE_CODE = "print('answer')"


def _unknown_steps(result, project, port, evidence):
    """The steps of a ready_unknown deploy (P462, P1022): the REPL to watch after the person's step or for a log that names
    no files, none when the port is gone, and the look, live.py and the REPL, in that order, when the board did not answer."""
    stopped = bool(result.start and result.start.code)  # P462: the person has a step first
    gone = stopped and result.start.port is None  # no port to open: mpremote would choose a board of its own
    if stopped or not result.facts["files"]:
        again = "read the board again with the REPL (data.repl_command): the firmware prints `ready`. Never deploy again for this"
        following = [] if gone else [outcomes.step("watch", list(result.repl_command),
                                   again + (". First the person does what data.person_action says" if stopped else ""),
                                   needs_person=True if stopped else None)]
        return following
    live = ["--project", str(project), "--port", port, "--code", UNKNOWN_LIVE_CODE]
    return [look_step(project, port, evidence, UNKNOWN_LOOK_WHY),
            outcomes.add_env(outcomes.step("live", live, UNKNOWN_LIVE_WHY, needs_person=True), store.read_given_env()),
            outcomes.step("watch", list(result.repl_command), UNKNOWN_WATCH_WHY, needs_person=True)]


#: The data keys whose paths Privacy leaves as they are (P677): the line a person pastes, the board log an agent opens,
#: and the commands a person runs (the flash commands, the REPL).
PASTED_KEYS = ("run_in_terminal", "board_log", "commands", "repl_command")


# --- Later, not MVP: a typed record of the run; `reached` is the dict the old main filled, kept so the goldens stay byte-equal ---
def deploy_data(reached):
    """The `data` of a deploy run, keys in the order the goldens hold: what the run reached, the look, the yes, the board
    after the flash, the records, and the board's state after a flash that failed."""
    report, result, plan, consent = reached.get("report"), reached.get("result"), reached.get("plan"), reached.get("consent")
    ready, stage = result.ready if result else None, reached["stage"]
    data = {
        "stage": stage, "simulation": report.simulation if report else None, "dry_run": bool(reached.get("dry_run")), "token": reached.get("token"),
        "commands": [list(command) for command in plan.commands] if plan else None,
        "look": report.to_dict() if report else None,
        "yes": {"kind": reached["yes_kind"], "who": reached["who"]} if consent else None,
        "ready": {"verdict": ready.verdict, "sentence": ready.sentence} if ready else None,
        "facts_line": result.facts_line if result else None,
        "image_sha256": result.image_sha256 if result else None,
        "board_log": str(result.log_path) if result else None,
        "repl_command": list(result.repl_command) if result and not (result.start and result.start.port is None) else None,
        "store_record": reached.get("store_record"), "store_record_error": reached.get("store_record_error"),
        "board_state": MAY_BE_ERASED if stage == DeployPhase.FLASH else None,
        "person_action": result.start.sentence if result and result.start and result.start.code else None,
        "run_in_terminal": reached.get("run_in_terminal"),
    }
    if reached.get("doctor"):  # P354: a look that esptool could not read, as look.py's envelope carries it
        data["doctor"] = board_doctor.as_dict(reached["doctor"])
    data.update(reached.get("board_question") or {})  # P892: open, port, product and known_board, only after a stop at the board
    return data


def deploy_result(reached, code):
    """
    The OperationResult of one deploy run. `reached` is the dict the run filled as it went (the keys read above: `project`,
    `evidence` and `stage` always, the rest optional), `code` the exit code it decided: 0 no Finding, 1 a problem, 2
    unchecked, so the status is the code's. The person's lines were Events, so `lines` is empty, and the stderr lines went to
    `add_diagnostics` (P938).
    """
    plan = reached.get("plan")
    found = [] if code == outcomes.EXIT_OK else reached.get("findings") or [_finding(reached, code)]  # P892: a stop at the board gives its own
    return OperationResult(deploy_data(reached), found, _steps(reached),
                           notes=((list(plan.notes) if plan else []) + reached.get("notes", [])) or None)
