"""
The `--json` answer of deploy.py (P213 PR a): one `outcomes.envelope`, built from what the run found, and the steps and
words it shares with the look (`deploy_step`, `yes_rule`, `doctor_fix`; the look's items are in spark.bench.look_at_board,
P442). Every `problems` and `unchecked` item carries a `code` from board_codes, the reason an agent decides on (P433).

Nothing here runs a command or prints. The status comes from `outcomes.envelope`, and the problems and unchecked
items are chosen from the exit code the script already decided, so the status and the exit code cannot disagree.
A step that needs the person (`needs_yes`) is a step Claude relays, never one it runs on its own: the token is
not the yes, and neither is "go ahead" in a chat.
"""

import board_doctor
import boards
from spark.core import codes, outcomes
import ready_check
from deploy_gate import NEXT_LOOK, NEXT_DEPLOY

#: What the person must do first, said in a step's `why`.
YES_RULE = "the person types yes in their own terminal%s; the token and \"go ahead\" in a chat are not the yes"
#: What YES_RULE adds when a deploy grant may answer.
GRANT_CLAUSE = " (or a deploy grant stands)"

#: A `fix` for each thing a deploy can wait for.
FIX_FOR_NEXT = {NEXT_DEPLOY: "the person runs data.run_in_terminal in their own terminal", NEXT_LOOK: "run look.py again"}
#: The stages of a deploy, the last one reached is `data.stage`.
STAGE_PLAN, STAGE_LOOK, STAGE_GATE, STAGE_FLASH, STAGE_VERIFY = "plan", "look", "gate", "flash", "verify"
#: The board's state after a flash command failed.
MAY_BE_ERASED = "may_be_erased"


def yes_rule(evidence):
    """YES_RULE for this evidence: the grant clause only where a grant may answer."""
    return YES_RULE % ("" if evidence.grant_refusal else GRANT_CLAUSE)


def deploy_argv(project, token, port, evidence):
    """The arguments of deploy.py for this board and image (not the script's name, as parts.py's steps)."""
    return ["--project", str(project), "--token", token or "", "--port", port] + evidence.argv()


def look_argv(project, port, evidence):
    """The arguments of look.py."""
    return ["--project", str(project)] + (["--port", port] if port else []) + evidence.argv()


def dumps(envelope):
    """The envelope as the one compact line a script prints: `outcomes.dumps`."""
    return outcomes.dumps(envelope)


def look_step(project, port, evidence, why="read the board first: the board restarts while it is read"):
    """The step that runs look.py. It writes nothing."""
    return outcomes.step("look", look_argv(project, port, evidence), why)


def deploy_step(project, token, port, evidence, why):
    """The step that runs deploy.py: it erases ALL of the flash, so it needs the person's yes."""
    return outcomes.step("deploy", deploy_argv(project, token, port, evidence), why,
                         effects=["deletes", "writes"], needs_yes=True)


def bad_argument_envelope(tool, bad):
    """The envelope of a run that a bad argument stopped (outcomes.BadArgument `bad`): one unchecked item, and no data."""
    return outcomes.envelope(tool, tool, None, unchecked=[{"code": codes.BAD_ARGUMENT, "sentence": str(bad),
                                                           "fix": "%s.py --help lists the arguments" % tool}])


def doctor_fix(doctor, places):
    """The `fix` of a BoardDoctorResult: its next step's sentence, naming the buttons as `places` does, or '' when there
    is no doctor result or it names no step."""
    return board_doctor.step_sentence(doctor.next_step, places) if doctor and doctor.next_step else ""


def deploy_envelope(reached, code):
    """
    The envelope of one deploy run. `reached` is a dict main filled as it went (the keys read below: `evidence` always, the rest optional), `code` the
    exit code it returns: 0 no item, 1 `problems`, 2 `unchecked`, so the status is the code's.
    """
    report, result, plan, consent = reached.get("report"), reached.get("result"), reached.get("plan"), reached.get("consent")
    project, port = reached["project"], reached.get("port") or (report.port if report else None)
    evidence, next_op = reached["evidence"], reached.get("next_op")
    stage = reached["stage"]
    sentence, doctor = reached.get("refusal"), reached.get("doctor")
    fix = doctor_fix(doctor, boards.ButtonPlaces.of_project(project)) if doctor else FIX_FOR_NEXT.get(next_op, "")
    item = {"subject": "ready" if result else stage, "code": reached.get("reason"), "sentence": sentence, "fix": fix}
    ready = result.ready if result else None
    following = []
    if reached.get("dry_run"):
        following = [look_step(project, port, evidence, "deploy.py --dry-run did not look at the board")]
    elif next_op == NEXT_LOOK:
        following = [look_step(project, port, evidence, "the look is missing or stale")]
    elif next_op == NEXT_DEPLOY:
        following = [deploy_step(project, reached.get("token"), port, evidence,
                                 "the person runs data.run_in_terminal in their own terminal: " + yes_rule(evidence))]
        if reached.get("grant_argv"):
            following.append(outcomes.step("grant", reached["grant_argv"],
                                           "the person runs it once in their own terminal; it lets Claude erase ALL of the flash for N minutes (1 to 1440, 60 here)",
                                           effects=["writes"], needs_yes=True))
    elif result and result.ready.verdict == ready_check.UNKNOWN:
        again = "read the board again with the REPL (data.repl_command): the firmware prints `ready`. Never deploy again for this"
        following = [outcomes.step("watch", list(result.repl_command),
                                   again + (". First the person presses the board's %s" % boards.ButtonPlaces.of_project(project).reset if result.reset_seen is False else ""),
                                   needs_person=True if result.reset_seen is False else None)]
    data = {
        "stage": stage, "simulation": report.simulation if report else None, "dry_run": bool(reached.get("dry_run")), "token": reached.get("token"),
        "commands": [list(command) for command in plan.commands] if plan else None,
        "look": report.to_dict() if report else None,
        "yes": {"kind": reached["yes_kind"], "who": reached["who"]} if consent else None,
        "ready": {"verdict": ready.verdict, "sentence": ready.sentence} if ready else None,
        "facts_line": result.facts_line if result else None,
        "image_sha256": result.image_sha256 if result else None,
        "board_log": str(result.log_path) if result else None,
        "repl_command": list(result.repl_command) if result else None,
        "store_record": reached.get("store_record"), "store_record_error": reached.get("store_record_error"),
        "board_state": MAY_BE_ERASED if stage == STAGE_FLASH else None,
        "person_action": reached.get("person_action") if result and result.reset_seen is False else None,
        "run_in_terminal": reached.get("run_in_terminal"),
    }
    if doctor:  # P354: a look that esptool could not read, as look.py's envelope carries it
        data["doctor"] = board_doctor.as_dict(doctor)
    return outcomes.envelope("deploy", "deploy", data, [item] if code == outcomes.EXIT_PROBLEMS else (),
                             [item] if code == outcomes.EXIT_COULD_NOT_RUN else (), following,
                             notes=((list(plan.notes) if plan else []) + reached.get("notes", [])) or None)
