"""
Where a project stands as an Operation on the core (P825, #1183): each phase's reader in order, one line per phase, the
first phase still open, and the offers each phase holds. It reads and never writes. `flow.py show` is its CLI; the page
(P827) and the requests (P829) read the same answer.
"""

from pathlib import Path

from spark.breadboard import sheet
from spark.build import build_codes
from spark.build.build_record import BuildRecordStore
from spark.build.stages import SIMULATION
from spark.design import needs
from spark.flow import flow_codes
from spark.flow.fingerprint import fingerprint_of
from spark.flow.phase_readers import MARKS, READERS, REQUIREMENTS_FILE
from spark.records import store
from spark.core.errors import CodedMessageError
from spark.core.operation import COMMON_ARGUMENTS, READS, Operation
from spark.core.outcomes import COULD_NOT_RUN, OK, PROBLEMS, SKIPPED
from spark.core.privacy import Privacy
from spark.core.result import Finding, OperationResult
from spark.core.text_guards import printable

# --- MVP ---
#: The last line: the first phase still open. The deploy is never done here, so a project always has one.
STANDS_AT_LINE = "  stands at: %s"
#: How many offer keys a person's line shows; the rest are counted. The JSON holds them all.
OFFERS_SHOWN = 5
#: The Finding of a phase that holds problems or could not run: its first sentence, and where to look.
PHASE_SENTENCE = "%s: %s"
PHASE_FIX = "read what the phase says in data.phases"


def privacy_for(project):
    """The Privacy of a run on `project`: its path, the store's and the home folder's masked (P677)."""
    return Privacy.of(project, store.home(), Path.home(), ())


def phase_line(phase):
    """One phase as a person reads it: `  ✓ needs: 2 need(s): soil, wet (claude)`, where the mark alone says ok, then up
    to OFFERS_SHOWN offer keys and how many more, indented."""
    word = MARKS[phase.status][0]
    lines = ["  %s %s: %s (%s)" % (phase.mark, phase.phase, ", ".join(([word] if word else []) + phase.says), phase.by)]
    keys = [offer.key for offer in phase.offers]
    more = ["+%d more" % (len(keys) - OFFERS_SHOWN)] if len(keys) > OFFERS_SHOWN else []
    lines += ["      offers: %s" % ", ".join(keys[:OFFERS_SHOWN] + more)] if keys else []
    return [printable(line) for line in lines]


def read_flow(project, readers=None):
    """(the Phases of `project`, one per reader in the readers' order, and `stands_at`: the first phase whose status is
    neither ok nor None, else None). The one source of the phases, for `show` and for the page (P827). `readers` are
    the PhaseReaders a test swaps (None: `READERS`)."""
    phases = [reader.answer(project) for reader in readers or READERS]
    return phases, next((phase.phase for phase in phases if phase.status not in (OK, None)), None)


#: The codes of a simulation stage the guide passes (P977): the board has no Wokwi model, so the board is the test.
NO_WOKWI_CODES = (build_codes.BOARD_NOT_IN_WOKWI,)


def readable(read, default):
    """What `read()` gives, or `default` when a file it reads cannot be read: the phase that reads it says why."""
    try:
        return read()
    except (CodedMessageError, OSError):
        return default


def passes_build(record):
    """True when the build `record` could not run only because Wokwi has no model of its board: its one stage that ended
    neither ok nor skipped is the simulation, with a code of NO_WOKWI_CODES (P977). An old record with no code never passes."""
    stopped = [stage for stage in (record or {}).get("stages") or [] if stage.get("status") not in (OK, SKIPPED)]
    return [stage.get("name") for stage in stopped] == [SIMULATION.name] and stopped[0].get("code") in NO_WOKWI_CODES


def passed_phases(project, by_name):
    """The phases the guide passes (P977): a build that could not run only because Wokwi has no model of the board, and
    after it a simulate not started. Its phase status stays could-not-run, so the exit does not change."""
    build, simulate = by_name.get(flow_codes.BUILD), by_name.get(flow_codes.SIMULATE)
    if not build or build.status != COULD_NOT_RUN or not passes_build(readable(BuildRecordStore(project).read, None)):
        return set()
    return {flow_codes.BUILD} | ({flow_codes.SIMULATE} if simulate and simulate.status == flow_codes.NOT_STARTED else set())


def is_open(phase):
    """True when the person acts on `phase` before the next: a status that is neither ok nor None, or a simulate whose
    image no passed run tested."""
    return phase.status not in (OK, None) or (phase.phase == flow_codes.SIMULATE and phase.says[0] != flow_codes.TESTED_MESSAGE)


def now_phase(phases, passed):
    """The phase to act on now: the first open one the guide does not pass, or the idea while no need is written. The
    deploy is never done here, so there is one; None only in a flow of other readers, which a test gives."""
    now = next((phase for phase in phases if phase.phase not in passed and is_open(phase)), None)
    if now and now.phase == flow_codes.NEEDS and now.status == flow_codes.NOT_STARTED:
        return phases[0]
    return now


def count_steps(project):
    """The number of steps of the project's wiring sheet, or None when the build's files cannot give them."""
    try:
        return len(sheet.wiring_data(Path(project) / REQUIREMENTS_FILE).steps)
    except Exception:  # noqa: BLE001  a circuit.json can hold anything, as the page's wiring reads it
        return None


def now_sentence(project, now, by_name, open_needs, steps):
    """The sentence of the phase to act on now (flow_codes.NOW_SENTENCES), else the problems or could-not-run line. The
    firmware beside a current wiring sheet is two jobs, with the sheet's steps from `steps(project)`."""
    breadboard = by_name.get(flow_codes.BREADBOARD)
    sheet_current = breadboard is not None and breadboard.status is None and (Path(project) / sheet.SHEET).is_file()
    count = steps(project) if now.phase == flow_codes.FIRMWARE and now.status == flow_codes.NOT_STARTED and sheet_current else None
    if count is not None:
        return flow_codes.TWO_JOBS_NOW % count
    said = flow_codes.NOW_SENTENCES.get((now.phase, now.status))
    if said == flow_codes.PARTS_NOW:
        return said % (len(open_needs), ", ".join(open_needs))
    return said or (flow_codes.PROBLEMS_NOW if now.status == PROBLEMS else flow_codes.COULD_NOT_RUN_NOW) % now.phase


def job_offer(now, by_name):
    """The key of the offer that does the job of the phase to act on now (flow_codes.JOB_OFFERS), or None."""
    holder, key = flow_codes.JOB_OFFERS.get(now.phase, (None, None))
    return key if holder in by_name and key in [offer.key for offer in by_name[holder].offers] else None


def label(phase, passed):
    """The name the guide shows for `phase`: a passed build or simulate says why (P977)."""
    if phase.phase in passed:
        return flow_codes.BUILT_NO_SIMULATION if phase.phase == flow_codes.BUILD else flow_codes.SIMULATE_NO_MODEL
    return phase.phase


def guide_of(project, phases, steps=count_steps):
    """
    What the person does now, what is done, what comes later and what they set aside (P977), from the Phases of `project`:
    `{"now": {phase, by, says, offer, needs}, "done", "later", "set_aside", "no_simulation"}`. Done is every phase before
    now but the breadboard, which spark cannot judge, and a passed simulate, which is later. `steps` counts the wiring
    sheet's steps.
    """
    by_name, listed = {phase.phase: phase for phase in phases}, readable(lambda: needs.read(project), [])
    passed = passed_phases(project, by_name)
    now = now_phase(phases, passed)
    at = phases.index(now) if now else len(phases)
    open_needs = [need["id"] for need in listed if not need.get("pick") and not need.get("aside")]
    later_simulate = flow_codes.SIMULATE in passed
    done = [label(phase, passed) for phase in phases[:at]
            if phase.phase != flow_codes.BREADBOARD and not (phase.phase == flow_codes.SIMULATE and later_simulate)]
    later = [label(phase, passed) for index, phase in enumerate(phases)
             if index > at or (phase.phase == flow_codes.SIMULATE and later_simulate)]
    return {"now": {"phase": now.phase, "by": now.by, "says": now_sentence(project, now, by_name, open_needs, steps),
                    "offer": job_offer(now, by_name), "needs": open_needs if now.phase == flow_codes.PARTS else []} if now else None,
            "done": done, "later": later, "set_aside": [need["id"] for need in listed if need.get("aside")],
            "no_simulation": flow_codes.NO_SIMULATION_NOW if flow_codes.BUILD in passed else None}


class ShowFlow(Operation):
    """
    Operation: where a project stands. It asks each PhaseReader in order and answers `data.phases` (each Phase as a dict),
    `data.stands_at`, the first phase whose status is neither ok nor None, `data.fingerprint` (`fingerprint_of`, P829) and
    `data.guide` (`guide_of`, P977). A phase that holds problems or could not run
    adds one Finding of that status, so the exit says so; every phase still answers. `readers` are the PhaseReaders a test
    swaps (None: `READERS`).
    """

    name = "show-flow"
    summary = "Say where a project stands, phase by phase from the idea to the deploy, and what each phase offers next (P825)."
    arguments = (COMMON_ARGUMENTS["project"]._replace(help="the project folder (default: here)"), COMMON_ARGUMENTS["json"])
    effects = (READS,)
    data_keys = ("phases", "stands_at", "fingerprint", "guide")
    privacy_for = staticmethod(privacy_for)

    def __init__(self, readers=None):
        self.readers = readers or READERS

    def run(self, project, *, outside):
        phases, stands_at = read_flow(project, self.readers)
        findings = [Finding(phase.status, phase.phase, flow_codes.PHASE_PROBLEMS if phase.status == PROBLEMS else flow_codes.PHASE_COULD_NOT_RUN,
                            PHASE_SENTENCE % (phase.phase, phase.says[0]), PHASE_FIX)
                    for phase in phases if phase.status in (PROBLEMS, COULD_NOT_RUN)]
        lines = [line for phase in phases for line in phase_line(phase)]
        lines += [STANDS_AT_LINE % stands_at] if stands_at else []
        data = {"phases": [phase.to_dict() for phase in phases], "stands_at": stands_at, "fingerprint": fingerprint_of(project, phases),
                "guide": guide_of(project, phases)}
        return OperationResult(data, findings, lines=lines)
# --- end MVP ---
