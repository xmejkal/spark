"""
The flow's reading of a check record (P1209, #1758): what a check Operation kept in `.spark/<op>.json`, said in one
sentence from the record alone, beside the deploy's reading (`deploy_reading`). It reads the record and its input files
and runs nothing: `flow.py show` never runs a check. The guide's `simulation` entry (`simulation_of`) is the free checks'
sentence, then why there is no simulation, and whether the page draws it grey: only where nothing more runs. A check
record whose files changed since reads as older, never as current. check-design (P1255) reuses `read_check` and `said_of`
with its own name and label: `design_line` is the Design checks' line, which the build phase says, and `design_now_line`
is NOW's text of the design checks while no record is current (P1341).
"""

from spark.checks.check_design import CheckDesign
from spark.core.outcomes import NONE_RECORDED, NOT_CHECKED, OK, RECORDED
from spark.core.zone_time import day_and_time
from spark.firmware.firmware_check import CheckFirmware
from spark.firmware.pin_map_uses import PinMapUses
from spark.firmware.project_secrets import is_secret_path
from spark.flow import flow_codes
from spark.records.check_record import CheckRecordStore

# --- MVP ---
#: The label of the free checks (P1208's word): the import check and the own tests together.
FREE_CHECKS_LABEL = "Free checks"
#: The label of check-design's line (P1255), after its op: the build phase says it.
DESIGN_CHECKS_LABEL = "Design checks"
#: The sentence of a check record by its state, the label first.
NOT_RUN_YET = "%s: not run yet. Ask Claude to run them, for free."
NOT_READ = "%s: %s. Ask Claude to run them again."
OLDER = "%s, %s, on older %s: ask Claude to run them again."
CURRENT = "%s, %s: %s."
#: A current record of a run that did not end ok: its status word too, because its lines alone may show no failure
#: (`nothing_to_import` counts "0 of 0 imported"; the card's page-check step 7).
CURRENT_NOT_OK = "%s, %s, %s: %s. Ask Claude to go through them with you."
#: How the result lines of a current record, and the inputs of an older one, are joined.
LINES_JOIN, INPUTS_JOIN = "; ", " or "
#: NOW's text of the design checks (P1341), while no check-design record is current: a head by the record's state (none,
#: older, or unread with its why, in the shape of NOT_READ), the gloss and one ask. "The design checks" in full, never
#: "them" or "free": on the firmware's NOW the free checks are named just before it (THIN_MAIN_RULE).
DESIGN_NOT_RUN_NOW = "The design checks have not run yet."
DESIGN_OLDER_NOW = "The design checks ran before their files changed."
DESIGN_NOT_READ_NOW = "%s: %s."
DESIGN_GLOSS_NOW = "They compare the circuit with the facts of the board, its parts and the project's rules."
DESIGN_ASK_NOW = "Ask Claude to run the design checks."
#: The firmware's out-of-date sentence (P1270): what pins.py gained or lost since the record, the record's day. And NOW's text.
PIN_NAMES_CHANGED = "firmware/pins.py %s since the free checks read the pin names on %s."
PIN_NAMES_NOW = ("The pin names changed after the free checks last read them. Ask Claude to check the firmware's pin names "
                 "against the new pins.py, for free.")
GAINED_WORD, LOST_WORD, AND_WORD, CHANGES_JOIN = "gained %s", "lost %s", " and ", ", and "


def read_check(project, name):
    """The CheckRecord of the check `name` in `project`, its secrets files left out as the Operation leaves them out. The
    leave-out rule is the firmware's secrets rule (`project_secrets.is_secret_path`, P1060), the one `check-firmware` saves
    with. `check-design` saves with none (P1255): harmless only because none of its inputs is under firmware/, which a
    test pins."""
    return CheckRecordStore(project, name, leave_out=is_secret_path).read()


def said_of(check, label):
    """One sentence of the CheckRecord `check`, with `label`, from the record alone: not run yet, not read and why, older
    (its time and its own inputs, no counts), or current (its time and its lines, and its status when it is not ok)."""
    if check.state == NONE_RECORDED:
        return NOT_RUN_YET % label
    if check.state == NOT_CHECKED:
        return NOT_READ % (label, check.why)
    if not check.current:
        return OLDER % (label, day_and_time(check.at), INPUTS_JOIN.join(check.inputs))
    if check.status != OK:
        return CURRENT_NOT_OK % (label, day_and_time(check.at), check.status, LINES_JOIN.join(check.lines))
    return CURRENT % (label, day_and_time(check.at), LINES_JOIN.join(check.lines))


def design_line(project, built):
    """The Design checks' sentence (`said_of`) of the check-design record of `project`, or None with no record when
    `built` is False: a project with no board built has nothing to check yet. It reads the record and runs nothing."""
    check = read_check(project, CheckDesign.name)
    if not built and check.state == NONE_RECORDED:
        return None
    return said_of(check, DESIGN_CHECKS_LABEL)


def design_now_line(project, built):
    """NOW's text of the design checks (P1341): the head of the check-design record of `project` by its state (none, older
    or unread), the gloss and the ask. None when `built` is False, or for a current record at any status: the build row
    says its status (`design_line`). It reads the record and runs nothing."""
    check = read_check(project, CheckDesign.name)
    if not built or check.state == RECORDED and check.current:
        return None
    if check.state == NONE_RECORDED:
        head = DESIGN_NOT_RUN_NOW
    elif check.state == NOT_CHECKED:
        head = DESIGN_NOT_READ_NOW % (DESIGN_CHECKS_LABEL, check.why)
    else:
        head = DESIGN_OLDER_NOW
    return " ".join((head, DESIGN_GLOSS_NOW, DESIGN_ASK_NOW))


def is_current_ok(check):
    """True for a check record that is current and whose run was ok: nothing more for the free checks to do."""
    return check.state == RECORDED and check.current and check.status == OK


def read_firmware_check(project):
    """The CheckRecord of check-firmware in `project`: the one read per caller, handed on to what needs it (P1270)."""
    return read_check(project, CheckFirmware.name)


def missing_pin_line(project, check=None):
    """The pin map line (`PinMapUses.line_from`) of the current check-firmware record of `project` when it names a pin name that
    firmware/pins.py lacks, else None: no record, an older or unread one, one with no `pin_map` or one of another shape (P882). It
    reads the record, or takes `check`, the CheckRecord its caller read, and runs nothing."""
    check = check if check is not None else read_firmware_check(project)
    if check.state != RECORDED or not check.current:
        return None
    return PinMapUses.line_from(check.data.get("pin_map"), missing_only=True)


def names_said(names):
    """`names` as a list in words: "A", "A and B", "A, B and C"."""
    return AND_WORD.join([", ".join(names[:-1]), names[-1]] if len(names) > 1 else names)


def pin_names_line(project, check):
    """The sentence that firmware/pins.py gained or lost names (P1270), from `check`, the check-firmware CheckRecord: only
    for a recorded record that is older and whose `pin_map.names` differ from the names pins.py binds now
    (`PinMapUses.changed_since`). A pin that moved keeps its name, so it says nothing. None for no record, a current or an
    unread one, one from before `names`, and a firmware that does not parse (the free checks' line says why). It reads
    the firmware files with `ast` and runs nothing."""
    if check.state != RECORDED or check.current:
        return None
    changed = PinMapUses.read(project).changed_since(check.data.get("pin_map"))
    if not changed or not any(changed):
        return None
    said = [word % names_said(names) for word, names in zip((GAINED_WORD, LOST_WORD), changed) if names]
    return PIN_NAMES_CHANGED % (CHANGES_JOIN.join(said), day_and_time(check.at))


def simulation_of(project, firmware_written, no_model, check=None):
    """The guide's `simulation`: `{line, grey, check}`. `line` is the free checks' sentence, then NO_SIMULATION_NOW when
    `no_model`; with no firmware written and no record there is no free checks' part, and with neither part the line is
    None. `grey` is True only with `no_model` and no free checks' part or a current ok record: a failed, older or unread
    check is never grey. `check` is the record's reading as a dict."""
    check = check if check is not None else read_firmware_check(project)
    free = said_of(check, FREE_CHECKS_LABEL) if firmware_written or check.state != NONE_RECORDED else None
    line = " ".join(part for part in (free, flow_codes.NO_SIMULATION_NOW if no_model else None) if part) or None
    grey = no_model and (free is None or is_current_ok(check))
    return {"line": line, "grey": bool(grey), "check": check.to_dict()}
# --- end MVP ---
