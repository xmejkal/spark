"""
The guide of a project (P977, #1407): from the Phases `show_flow.read_flow` gives, the phase the person acts on now, who
acts and one sentence for it, the phases done and later, the needs set aside, and why there is no simulation. It reads
and never writes. `flow.py show` and `flow.py page` answer it as `data.guide`.
"""

from collections import namedtuple
from pathlib import Path

from spark.breadboard import sheet
from spark.build import build_codes
from spark.build.build_record import BuildRecordStore
from spark.build.stages import SIMULATION
from spark.design import needs
from spark.firmware.project_image import DeployError, ProjectImage
from spark.flow import flow_codes
from spark.flow.phase_readers import REQUIREMENTS_FILE, counted, set_aside
from spark.core.errors import CodedMessageError
from spark.core.outcomes import COULD_NOT_RUN, OK, PROBLEMS, SKIPPED

# --- MVP ---
#: The codes of a simulation stage whose build counts as done (the PO, 2026-11-21): Wokwi has no model of the board.
NO_MODEL_CODES = (build_codes.BOARD_NOT_IN_WOKWI,)
#: What reading the wiring sheet can raise: its own refusals, and a circuit.json that is no JSON, holds a value of the
#: wrong type or shape, or is nested too deep (tests/test_flow_page.py's TheMissingWiringTest).
SHEET_UNREADABLE = sheet.REFUSALS + (ValueError, KeyError, TypeError, AttributeError, IndexError, RecursionError)
#: Value: what the runs say of the image (a fact of flow_codes, or None) and the name of a log that failed on it, or None.
ImageFact = namedtuple("ImageFact", "fact log")
NO_IMAGE_FACT = ImageFact(None, None)
#: What the image's runs say that leaves the simulate open: a run failed on it, firmware changed after it, or none ran.
OPEN_IMAGE_FACTS = (flow_codes.RUN_FAILED, flow_codes.IMAGE_OLDER, flow_codes.IMAGE_UNTESTED)


def readable(read, default):
    """What `read()` gives, or `default` when a file it reads cannot be read: the phase that reads it says why."""
    try:
        return read()
    except (CodedMessageError, OSError):
        return default


def stops_only_for_no_model(record):
    """True when the build `record`'s one stage that ended neither ok nor skipped is the simulation, with a code of
    NO_MODEL_CODES. An old record with no code is never counted as done."""
    stopped = [stage for stage in (record or {}).get("stages") or [] if stage.get("status") not in (OK, SKIPPED)]
    return [stage.get("name") for stage in stopped] == [SIMULATION.name] and stopped[0].get("code") in NO_MODEL_CODES


def no_model_phases(project, by_name):
    """The phases counted as done because Wokwi has no model of the board: a build that could not run for that alone,
    and after it a simulate with no status or not started. The build phase keeps could-not-run, so the exit stays 2.
    It reads .spark/build.json once more: a stage code on every Phase would change the phases' JSON contract."""
    build, simulate = by_name.get(flow_codes.BUILD), by_name.get(flow_codes.SIMULATE)
    if not build or build.status != COULD_NOT_RUN or not stops_only_for_no_model(readable(BuildRecordStore(project).read, None)):
        return set()
    return {flow_codes.BUILD} | ({flow_codes.SIMULATE} if simulate and simulate.status in (flow_codes.NOT_STARTED, None) else set())


def image_fact(project):
    """The ImageFact of the image sim/wokwi.toml names: RUN_FAILED with the first failed log's name, IMAGE_OLDER,
    IMAGE_UNTESTED or IMAGE_TESTED. NO_IMAGE_FACT when there is no image or a log cannot be read: the phase says why."""
    try:
        image = ProjectImage(project)
        failed = image.failed_runs()
        if failed:
            return ImageFact(flow_codes.RUN_FAILED, failed[0][0].name)
        if image.find_newer_files():
            return ImageFact(flow_codes.IMAGE_OLDER, None)
        return ImageFact(flow_codes.IMAGE_TESTED if image.find_passed_logs() else flow_codes.IMAGE_UNTESTED, None)
    except (DeployError, OSError):
        return NO_IMAGE_FACT


def is_open(phase, fact):
    """True when the person acts on `phase` before the next: a status that is neither ok nor None, or a simulate with no
    status whose image `fact` leaves it open."""
    return phase.status not in (OK, None) or (phase.phase == flow_codes.SIMULATE and fact.fact in OPEN_IMAGE_FACTS)


def now_phase(phases, no_model, fact, all_aside=False):
    """The phase to act on now: the first open one not counted as done, or the idea while no need is written, or the parts
    while every need is set aside (P980: there is no pick to write the parts list from). The deploy is never done here, so
    there is one; None only in a flow of other readers, which a test gives."""
    now = next((phase for phase in phases if phase.phase not in no_model and is_open(phase, fact)), None)
    if now and now.phase == flow_codes.REQUIREMENTS and now.status != COULD_NOT_RUN and all_aside:  # a broken file is not hidden
        return next((phase for phase in phases if phase.phase == flow_codes.PARTS), now)
    if now and now.phase == flow_codes.NEEDS and now.status == flow_codes.NOT_STARTED:
        return phases[0]
    return now


def count_steps(project):
    """The number of steps of the project's wiring sheet, or None when the build's files cannot give them."""
    try:
        return len(sheet.wiring_data(Path(project) / REQUIREMENTS_FILE).steps)
    except SHEET_UNREADABLE:
        return None


def is_sheet_current(project, by_name):
    """True when the wiring sheet is there and current: the breadboard phase has no status and breadboard.md is kept."""
    breadboard = by_name.get(flow_codes.BREADBOARD)
    return breadboard is not None and breadboard.status is None and (Path(project) / sheet.SHEET).is_file()


def who_and_sentence(now, open_needs, fact):
    """(who acts, the sentence) of the phase to act on now: a simulate with no status by its ImageFact `fact`
    (flow_codes.IMAGE_NOW), else the phase's own `by` and its sentence by (phase, status) in flow_codes.NOW_SENTENCES,
    else the problems or could-not-run line."""
    if now.phase == flow_codes.SIMULATE and now.status is None:
        by, said = flow_codes.IMAGE_NOW[fact.fact]
        return by, said % fact.log if fact.fact == flow_codes.RUN_FAILED else said
    said = flow_codes.NOW_SENTENCES.get((now.phase, now.status))
    if said == flow_codes.PARTS_NOW:
        return [now.by], said % (flow_codes.ONE_NEED_HAS if len(open_needs) == 1 else flow_codes.MANY_NEEDS_HAVE % len(open_needs), ", ".join(open_needs))
    return [now.by], said or (flow_codes.PROBLEMS_NOW if now.status == PROBLEMS else flow_codes.COULD_NOT_RUN_NOW) % now.phase


def job_offer(now, by_name):
    """The key of the offer that does the job of the phase to act on now (flow_codes.JOB_OFFERS), or None."""
    holder, key = flow_codes.JOB_OFFERS.get(now.phase, (None, None))
    return key if holder in by_name and key in [offer.key for offer in by_name[holder].offers] else None


def now_of(now, by_name, open_needs, fact, count):
    """`{phase, by, says, offer, needs, steps}` of the phase to act on now. With `count`, the steps of a current wiring
    sheet beside firmware not started, it is two jobs, the person's and Claude's, and `steps` is that count (else None)."""
    by, says = ([flow_codes.BY_YOU, flow_codes.BY_CLAUDE], flow_codes.TWO_JOBS_NOW % count) if count is not None else \
        who_and_sentence(now, open_needs, fact)
    return {"phase": now.phase, "by": by, "says": says, "offer": job_offer(now, by_name),
            "needs": open_needs if now.phase == flow_codes.PARTS else [], "steps": count}


def label(phase, no_model):
    """The name the guide shows for `phase`: one counted as done because Wokwi has no model of the board says so."""
    if phase.phase in no_model:
        return flow_codes.BUILT_NO_SIMULATION if phase.phase == flow_codes.BUILD else flow_codes.SIMULATE_NO_MODEL
    return phase.phase


def has_no_picks(by_name):
    """True when the needs phase has no status: no needs are written, so the requirements have no picks behind them (a
    requirements.json written by hand, or a last need dropped). An unreadable needs.json gives could-not-run, so false."""
    needs_phase = by_name.get(flow_codes.NEEDS)
    return needs_phase is not None and needs_phase.status is None


def done_of(phases, at, no_model, wired, no_picks=False):
    """The names of the phases before `at`: a simulate with no model is later, and the breadboard is there only when
    `wired` (a current sheet once the wiring is no longer part of now), with what spark cannot see. With `no_picks`
    the needs and parts are left out (nobody did them) and the requirements say so (P980)."""
    done = []
    for phase in phases[:at]:
        if no_picks and phase.phase in (flow_codes.NEEDS, flow_codes.PARTS):
            continue
        if no_picks and phase.phase == flow_codes.REQUIREMENTS:
            done.append(flow_codes.REQUIREMENTS_NO_PICKS)
        elif phase.phase == flow_codes.BREADBOARD:
            done += [flow_codes.SHEET_UNSEEN] if wired else []
        elif not (phase.phase == flow_codes.SIMULATE and phase.phase in no_model):
            done.append(label(phase, no_model))
    return done


def guide_of(project, phases, steps=count_steps):
    """
    What the person does now, what is done, what comes later and what they set aside, from the Phases of `project`:
    `{"now": {phase, by, says, offer, needs, steps}, "done", "later", "set_aside", "no_simulation"}`. `steps` counts the wiring
    sheet's steps. The needs are read once more, by the parts phase's own rule (`counted`, `set_aside`).
    """
    by_name, listed = {phase.phase: phase for phase in phases}, readable(lambda: needs.read(project), [])
    no_model = no_model_phases(project, by_name)
    simulate = by_name.get(flow_codes.SIMULATE)
    fact = image_fact(project) if simulate and simulate.status is None and flow_codes.SIMULATE not in no_model else NO_IMAGE_FACT
    all_aside = bool(listed) and not counted(listed)
    now = now_phase(phases, no_model, fact, all_aside)
    at = phases.index(now) if now else len(phases)
    open_needs = [need["id"] for need in counted(listed) if not need.get("pick")]
    beside_sheet = now and now.phase == flow_codes.FIRMWARE and now.status == flow_codes.NOT_STARTED and is_sheet_current(project, by_name)
    count = steps(project) if beside_sheet else None
    two_jobs = count is not None  # no count: no two jobs, so the breadboard stays in done
    said = now_of(now, by_name, open_needs, fact, count) if now else None
    wired = is_sheet_current(project, by_name) and not two_jobs  # beside the firmware, the wiring is part of now
    later = [label(phase, no_model) + (flow_codes.LATER_BUT_DONE if index > at and phase.status == OK else "")
             for index, phase in enumerate(phases) if index > at or (phase.phase == flow_codes.SIMULATE and phase.phase in no_model)]
    return {"now": said, "done": done_of(phases, at, no_model, wired, has_no_picks(by_name)), "later": later,
            "set_aside": [need["id"] for need in set_aside(listed)],
            "no_simulation": flow_codes.NO_SIMULATION_NOW if flow_codes.BUILD in no_model else None}
# --- end MVP ---
