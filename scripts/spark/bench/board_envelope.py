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

from spark.bench import board_doctor
from spark.records import board_records
from spark.bench.deploy_stages import DeployPhase
from spark.design import loader
from spark.core import outcomes
from spark.core.result import Finding, NextStep, OperationResult
from spark.bench import ready_probe
from spark.records import store
from spark.bench.deploy_gate import NEXT_LOOK, NEXT_DEPLOY

#: What the person must do first, said in a step's `why`.
YES_RULE = "the person types yes in their own terminal%s; the token and \"go ahead\" in a chat are not the yes"
#: What YES_RULE adds when a deploy grant may answer.
GRANT_CLAUSE = " (or a deploy grant stands)"

#: A `fix` for each thing a deploy can wait for.
FIX_FOR_NEXT = {NEXT_DEPLOY: "the person runs data.run_in_terminal in their own terminal", NEXT_LOOK: "run look.py again"}
#: The board's state after a flash command failed, and after a crash once the flash finished (P655).
MAY_BE_ERASED, FLASHED_NOT_VERIFIED = "may_be_erased", "flashed_not_verified"


def yes_rule(evidence):
    """YES_RULE for this evidence: the grant clause only where a grant may answer."""
    return YES_RULE % ("" if evidence.grant_refusal else GRANT_CLAUSE)


def deploy_argv(project, token, port, evidence):
    """The arguments of deploy.py for this board and image (not the script's name, as parts.py's steps)."""
    return ["--project", str(project), "--token", token or "", "--port", port] + evidence.argv()


def look_argv(project, port, evidence):
    """The arguments of look.py (the evidence's too, when there is one)."""
    return ["--project", str(project)] + (["--port", port] if port else []) + (evidence.argv() if evidence else [])


def dumps(envelope):
    """The envelope as the one compact line a script prints: `outcomes.dumps`."""
    return outcomes.dumps(envelope)


def look_step(project, port, evidence=None, why="read the board first: the board restarts while it is read"):
    """The step that runs look.py. It writes nothing. With no evidence, its arguments are the project's alone."""
    return outcomes.add_env(outcomes.step("look", look_argv(project, port, evidence), why), store.read_given_env())


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


def doctor_fix(doctor, places):
    """The `fix` of a DoctorProbeResult: its next step's sentence, naming the buttons as `places` does, or '' when there
    is no doctor result or it names no step."""
    return board_doctor.step_sentence(doctor.next_step, places) if doctor and doctor.next_step else ""


def _finding(reached, code):
    """The one Finding of a deploy run that did not reach ready, of the exit `code`'s severity: its subject is the stage, or
    `ready` once the board was read, its code the reason, its fix the doctor's step or the step of what it waits for."""
    result, doctor = reached.get("result"), reached.get("doctor")
    fix = (doctor_fix(doctor, board_records.ButtonPlaces.of_project(reached["project"])) if doctor
           else FIX_FOR_NEXT.get(reached.get("next_op"), ""))
    return Finding(outcomes.STATUS_FOR[code], "ready" if result else reached["stage"], reached.get("reason"), reached.get("refusal"), fix)


def _steps(reached):
    """The NextSteps of a deploy run: the look after a dry run or a stale look, the deploy line (and the grant line) the
    person runs when there was no terminal, the REPL to watch when ready is unknown."""
    result, evidence, next_op = reached.get("result"), reached["evidence"], reached.get("next_op")
    project, port = reached["project"], reached.get("port") or (reached["report"].port if reached.get("report") else None)
    following = []
    if reached.get("dry_run"):
        following = [look_step(project, port, evidence, "deploy.py --dry-run did not look at the board")]
    elif next_op == NEXT_LOOK:
        following = [look_step(project, port, evidence, "the look is missing or stale")]
    elif next_op == NEXT_DEPLOY:
        following = [deploy_step(project, reached.get("token"), port, evidence,
                                 "the person runs data.run_in_terminal in their own terminal: " + yes_rule(evidence))]
        if reached.get("grant_argv"):
            following.append(outcomes.add_env(outcomes.step("grant", reached["grant_argv"],
                                           "the person runs it once in their own terminal; it lets Claude erase ALL of the flash for N minutes (1 to 1440, 60 here)",
                                           effects=["writes"], needs_yes=True), store.read_given_env()))
    elif result and result.ready.verdict == ready_probe.UNKNOWN:
        stopped = bool(result.start and result.start.code)  # P462: the person has a step first
        gone = stopped and result.start.port is None  # no port to open: mpremote would choose a board of its own
        again = "read the board again with the REPL (data.repl_command): the firmware prints `ready`. Never deploy again for this"
        following = [] if gone else [outcomes.step("watch", list(result.repl_command),
                                   again + (". First the person does what data.person_action says" if stopped else ""),
                                   needs_person=True if stopped else None)]
    return [NextStep(**step) for step in following]


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
    return data


def deploy_result(reached, code, diagnostics=()):
    """
    The OperationResult of one deploy run. `reached` is the dict the run filled as it went (the keys read above: `project`,
    `evidence` and `stage` always, the rest optional), `code` the exit code it decided: 0 no Finding, 1 a problem, 2
    unchecked, so the status is the code's. The person's lines were Events, so `lines` is empty; `diagnostics` are the stderr lines.
    """
    plan = reached.get("plan")
    return OperationResult(deploy_data(reached), [] if code == outcomes.EXIT_OK else [_finding(reached, code)], _steps(reached),
                           diagnostics=list(diagnostics), notes=((list(plan.notes) if plan else []) + reached.get("notes", [])) or None)
