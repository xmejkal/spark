"""
The flow's reading of a check record (P1209, #1758): what a check Operation kept in `.spark/<op>.json`, said in one
sentence from the record alone, beside the deploy's reading (`deploy_reading`). It reads the record and its input files
and runs nothing: `flow.py show` never runs a check. The guide's `simulation` entry (`simulation_of`) is the free checks'
sentence, then why there is no simulation, and whether the page draws it grey: only where nothing more runs. A check
record whose files changed since reads as older, never as current. check-design (P1255) reuses `read_check` and `said_of`
with its own name and label.
"""

from spark.core.outcomes import NONE_RECORDED, NOT_CHECKED, OK, RECORDED
from spark.core.zone_time import day_and_time
from spark.firmware.firmware_check import CheckFirmware
from spark.firmware.project_secrets import is_secret_path
from spark.flow import flow_codes
from spark.records.check_record import CheckRecordStore

# --- MVP ---
#: The label of the free checks (P1208's word): the import check and the own tests together.
FREE_CHECKS_LABEL = "Free checks"
#: The sentence of a check record by its state, the label first.
NOT_RUN_YET = "%s: not run yet. Ask Claude to run them, for free."
NOT_READ = "%s: %s. Ask Claude to run them again."
OLDER = "%s, %s, on older %s: ask Claude to run them again."
CURRENT = "%s, %s: %s."
#: How the result lines of a current record, and the inputs of an older one, are joined.
LINES_JOIN, INPUTS_JOIN = "; ", " or "


def read_check(project, name):
    """The CheckRecord of the check `name` in `project`, its secrets files left out as the Operation leaves them out."""
    return CheckRecordStore(project, name, leave_out=is_secret_path).read()


def said_of(check, label):
    """One sentence of the CheckRecord `check`, with `label`, from the record alone: not run yet, not read and why, older
    (its time and its own inputs, no counts), or current (its time and its lines)."""
    if check.state == NONE_RECORDED:
        return NOT_RUN_YET % label
    if check.state == NOT_CHECKED:
        return NOT_READ % (label, check.why)
    if not check.current:
        return OLDER % (label, day_and_time(check.at), INPUTS_JOIN.join(check.inputs))
    return CURRENT % (label, day_and_time(check.at), LINES_JOIN.join(check.lines))


def is_current_ok(check):
    """True for a check record that is current and whose run was ok: nothing more for the free checks to do."""
    return check.state == RECORDED and check.current and check.status == OK


def simulation_of(project, firmware_written, no_model):
    """The guide's `simulation`: `{line, grey, check}`. `line` is the free checks' sentence, then NO_SIMULATION_NOW when
    `no_model`; with no firmware written and no record there is no free checks' part, and with neither part the line is
    None. `grey` is True only with `no_model` and no free checks' part or a current ok record: a failed, older or unread
    check is never grey. `check` is the record's reading as a dict."""
    check = read_check(project, CheckFirmware.name)
    free = said_of(check, FREE_CHECKS_LABEL) if firmware_written or check.state != NONE_RECORDED else None
    line = " ".join(part for part in (free, flow_codes.NO_SIMULATION_NOW if no_model else None) if part) or None
    grey = no_model and (free is None or is_current_ok(check))
    return {"line": line, "grey": bool(grey), "check": check.to_dict()}
# --- end MVP ---
