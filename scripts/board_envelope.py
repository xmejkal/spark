"""
The `--json` answers of look.py and deploy.py (P213 PR a): one `outcomes.envelope` each, built from what the run found.

Nothing here runs a command or prints. The status comes from `outcomes.envelope`, and the problems and unchecked
items are chosen from the exit code the script already decided, so the status and the exit code cannot disagree.
A step that needs the person (`needs_yes`) is a step Claude relays, never one it runs on its own: the token is
not the yes, and neither is "go ahead" in a chat.
"""

import json

import board_doctor
import boards
import outcomes
import ready_check
from deploy_gate import NEXT_LOOK, NEXT_DEPLOY

#: What the person must do first, said in a step's `why`.
YES_RULE = "the person types yes in their own terminal (or a deploy grant stands); the token and \"go ahead\" in a chat are not the yes"
#: A `fix` for each thing a deploy can wait for.
FIX_FOR_NEXT = {NEXT_DEPLOY: "the person runs data.run_in_terminal in their own terminal", NEXT_LOOK: "run look.py again"}
#: The stages of a deploy, the last one reached is `data.stage`.
STAGE_PLAN, STAGE_LOOK, STAGE_GATE, STAGE_FLASH, STAGE_VERIFY = "plan", "look", "gate", "flash", "verify"
#: The board's state after a flash command failed.
MAY_BE_ERASED = "may_be_erased"


def deploy_argv(project, token, port, evidence):
    """The arguments of deploy.py for this board and image (not the script's name, as parts.py's steps)."""
    return ["--project", str(project), "--token", token or "", "--port", port] + evidence.argv()


def look_argv(project, port, evidence):
    """The arguments of look.py."""
    return ["--project", str(project)] + (["--port", port] if port else []) + evidence.argv()


def dumps(envelope):
    """The envelope as the one compact line a script prints."""
    return json.dumps(envelope, ensure_ascii=False, separators=(",", ":"))


def look_step(project, port, evidence, why="read the board first: the board restarts while it is read"):
    """The step that runs look.py. It writes nothing."""
    return outcomes.step("look", look_argv(project, port, evidence), why)


def deploy_step(project, token, port, evidence, why):
    """The step that runs deploy.py: it erases ALL of the flash, so it needs the person's yes."""
    return outcomes.step("deploy", deploy_argv(project, token, port, evidence), why,
                         effects=["deletes", "writes"], needs_yes=True)


def look_envelope(report, project, evidence):
    """The envelope of a LookReport. `problems` are its stops and its warnings (a field that differs), `unchecked` its
    unknown fields and a missing token: the lists LookReport.status counts. A token, whatever the status, brings the
    deploy step."""
    problems = [{"subject": "stop", "sentence": stop, "fix": "deploy.py will refuse"} for stop in report.stops]
    problems += [{"subject": "flash", "sentence": warning, "fix": "deploy.py asks the person to accept it"}
                 for warning in report.warnings]
    unchecked = [{"sentence": "%s unknown: %s" % each, "fix": "unknown is not a pass: deploy.py names it and asks the person"}
                 for each in report.unknown.items()]
    if report.no_token_reason():
        unchecked.append({"sentence": "no token: %s" % report.no_token_reason(), "fix": "fix that, then run look.py again"})
    token = report.token()
    following = [deploy_step(project, token, report.port, evidence,
                             "erases ALL of the flash, then writes the passed image. Relay the warnings first. " + YES_RULE)] if token else []
    return outcomes.envelope("look", "look", report.to_dict(), problems, unchecked, following)


def look_stop_envelope(sentence, doctor=None, places=boards.ButtonPlaces.EMPTY):
    """The envelope of a look that could not run: one unchecked item. `doctor` is the board doctor's BoardDoctorResult after
    a failed read, or None: its facts go in `data.doctor` and its next step for the person's hands is the `fix`, naming the
    buttons as `places` (ButtonPlaces) does."""
    fix = board_doctor.step_sentence(doctor.next_step, places) if doctor and doctor.next_step else ""
    return outcomes.envelope("look", "look", {"doctor": board_doctor.as_dict(doctor)} if doctor else None,
                             unchecked=[{"sentence": sentence, "fix": fix}])


def deploy_envelope(reached, code):
    """
    The envelope of one deploy run. `reached` is a dict main filled as it went (the keys read below, all optional), `code` the
    exit code it returns: 0 no item, 1 `problems`, 2 `unchecked`, so the status is the code's.
    """
    report, result, plan, consent = reached.get("report"), reached.get("result"), reached.get("plan"), reached.get("consent")
    project, port = reached["project"], reached.get("port") or (report.port if report else None)
    evidence, next_op = reached["evidence"], reached.get("next_op")
    stage = reached["stage"]
    sentence = reached.get("refusal")
    item = {"subject": "ready" if result else stage, "sentence": sentence, "fix": FIX_FOR_NEXT.get(next_op, "")}
    ready = result.ready if result else None
    following = []
    if reached.get("dry_run"):
        following = [look_step(project, port, evidence, "deploy.py --dry-run did not look at the board")]
    elif next_op == NEXT_LOOK:
        following = [look_step(project, port, evidence, "the look is missing or stale")]
    elif next_op == NEXT_DEPLOY:
        following = [deploy_step(project, reached.get("token"), port, evidence,
                                 "the person runs data.run_in_terminal in their own terminal: " + YES_RULE)]
        if reached.get("grant_argv"):
            following.append(outcomes.step("grant", reached["grant_argv"],
                                           "the person runs it once in their own terminal; it lets Claude erase ALL of the flash for N minutes (1 to 1440, 60 here)",
                                           effects=["writes"], needs_yes=True))
    elif result and result.ready.verdict == ready_check.UNKNOWN:
        again = "read the board again with the REPL (data.repl_command): the firmware prints `ready`. Never deploy again for this"
        following = [outcomes.step("watch", list(result.repl_command), again + (". First the person presses the board's %s" % boards.ButtonPlaces.of_project(project).reset if result.reset_seen is False else ""))]
    data = {
        "stage": stage, "dry_run": bool(reached.get("dry_run")), "token": reached.get("token"),
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
    return outcomes.envelope("deploy", "deploy", data, [item] if code == outcomes.EXIT_PROBLEMS else (),
                             [item] if code == outcomes.EXIT_COULD_NOT_RUN else (), following,
                             notes=((list(plan.notes) if plan else []) + reached.get("notes", [])) or None)
