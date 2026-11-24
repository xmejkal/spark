"""
Where a project stands as an Operation on the core (P825, #1183): each phase's reader in order, one line per phase, the
offers each phase holds, the guide (P977) and the step of its now: the now offer's (P1030), else the now phase's
(P1034, `phase_steps`). It reads and never writes. `flow.py show` is
its CLI. `reading_of` reads the flow once as a FlowReading, which `show` prints and the page (P827) draws (P1060); the
requests (P829) read the same phases.
"""

import datetime
from pathlib import Path

from spark.flow import deploy_reading, flow_codes, phase_steps
from spark.flow.fingerprint import FILES, fingerprint_of
from spark.flow.flow_reading import FlowReading
from spark.flow.guide import guide_of
from spark.flow.published_page import PublishedPageStore
from spark.flow.phase_readers import MARKS, READERS, DeployReader
from spark.records import store
from spark.core.operation import COMMON_ARGUMENTS, READS, Operation
from spark.core.outcomes import COULD_NOT_RUN, PROBLEMS
from spark.core.privacy import Privacy
from spark.core.result import Finding, OperationResult
from spark.core.text_guards import printable
from spark.core.zone_time import stamp

# --- MVP ---
#: One line of the guide, after the phases (P1030): its label, as the page writes it, and its items, comma apart.
GUIDE_LINE = "  %s: %s"
#: The NOW line's end: the key of the now offer, whose step `next` holds.
NOW_KEY = " [%s]"
#: The NOW line's end for a next-only step (P1034): its op, and NEEDS_YOU for a step that needs the person or their yes.
NOW_STEP, NEEDS_YOU = " [next: %s%s]", ", needs you"
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


def needs_you(step):
    """Whether a person reads `step` with NEEDS_YOU: it needs the person's hands or their yes (P1035 review, one rule)."""
    return bool(step.needs_person or step.needs_yes)


def now_tag(now, steps):
    """The end of the NOW line: the key of its offer, else the op of its first step (P1034), else nothing."""
    if now["offer"]:
        return NOW_KEY % now["offer"]
    return NOW_STEP % (steps[0].op, NEEDS_YOU if needs_you(steps[0]) else "") if steps else ""


def guide_lines(guide, steps=()):
    """The guide as a person reads it, in the page's words and order (P1030): NOW with the key of its offer or the op of
    its next-only step (`now_tag`), DONE, LATER, why there is no simulation, SET ASIDE. A list with no item draws no line,
    as on the page. Last, the line that says nothing is open (P1043): `guide.get`, as the page reads it."""
    now = guide["now"]
    lines = [GUIDE_LINE % (flow_codes.GUIDE_NOW % now["phase"], now["says"] + now_tag(now, steps))] if now else []
    lines += [GUIDE_LINE % (flow_codes.GUIDE_DONE, ", ".join(guide["done"]))] if guide["done"] else []
    lines += [GUIDE_LINE % (flow_codes.GUIDE_LATER, ", ".join(guide["later"]))] if guide["later"] else []
    lines += ["  " + guide["no_simulation"]] if guide["no_simulation"] else []
    lines += [GUIDE_LINE % (flow_codes.GUIDE_SET_ASIDE, ", ".join(guide["set_aside"]))] if guide["set_aside"] else []
    lines += ["  " + guide["no_open_phase"]] if guide.get("no_open_phase") else []
    return [printable(line) for line in lines]


def now_steps(project, phases, guide):
    """The `next` of `show`: the step of the offer the guide's now names (P1030), else the next-only step of the now
    phase (`phase_steps.steps_of`, P1034). An empty `next` means: read data.guide.now."""
    key = guide["now"]["offer"] if guide["now"] else None
    if key:
        return [offer.step for phase in phases for offer in phase.offers if offer.key == key]
    return phase_steps.steps_of(project, phases, guide)


def phases_of(project, readers=None, deploy=None):
    """The Phases of `project`, one per reader in the readers' order: the one source of the phases, for `show`, the page
    (P827) and a request (P829), which needs no guide. `readers` are the PhaseReaders a test swaps (None: `READERS`).
    With `deploy`, the run's DeployState, the deploy phase is read from it (P1043)."""
    readers = readers or READERS
    if deploy is not None:
        readers = [DeployReader(deploy) if isinstance(reader, DeployReader) else reader for reader in readers]
    return [reader.answer(project) for reader in readers]


def flow_and_guide(project, readers=None, deploy=None):
    """(the Phases of `project`, its guide, `guide.guide_of`): `show` and the page compute the guide once (P1030). The
    deploy's state is read once too (`deploy`, else here), and the deploy phase and the guide both take it (P1043)."""
    deploy = deploy or deploy_reading.read_deploy(project)
    phases = phases_of(project, readers, deploy)
    return phases, guide_of(project, phases, deploy=deploy)


def stamp_of(project):
    """`{"newest": time}`: the newest change time of the fingerprint's files in `project`, in the machine's zone
    (`zone_time.stamp`), or None when none is there. Python writes it, so the page stays the same bytes for the same flow
    (P829); the page carries it as data-written."""
    times = [path.stat().st_mtime for path in (Path(project) / name for name in FILES) if path.is_file()]
    return {"newest": stamp(datetime.datetime.fromtimestamp(max(times))) if times else None}


def reading_of(project, readers=None):
    """The FlowReading of `project`, the flow read once (P1060): its folder's name, the phases and the guide
    (`flow_and_guide`), the fingerprint, the deploy, the stamp and the Artifact the page is published as. `show` prints
    it and the page draws it. It adds no rule of its own. `readers` are the PhaseReaders a test swaps (None: `READERS`)."""
    deploy = deploy_reading.read_deploy(project)  # once: the phase, the guide and data.deploy agree (the review of #1579)
    phases, guide = flow_and_guide(project, readers, deploy)
    return FlowReading(Path(project).resolve().name, phases, guide, fingerprint_of(project, phases), deploy_reading.deploy_data(deploy),
                       stamp_of(project), PublishedPageStore(project).read())


def read_flow(project, readers=None):
    """(the Phases of `project`, and `stands_at`, the guide's now phase): a projection of `reading_of`, for the tests."""
    reading = reading_of(project, readers)
    return reading.phases, reading.stands_at


class ShowFlow(Operation):
    """
    Operation: where a project stands. Its data is the FlowReading of `reading_of` (P1060): `data.phases` (each Phase as a
    dict), `data.stands_at`, the guide's now phase (`stands_at_of`, P1030), `data.fingerprint` (`fingerprint_of`, P829),
    `data.guide` (`guide_of`, P977), `data.deploy`, the newest board log (`deploy_reading.deploy_data`, P1043), then
    `data.name`, `data.title` (the page's), `data.stamp` and `data.artifact`. Its lines end with the guide's, and `next`
    holds the now offer's step (P1030), else the now phase's next-only step (P1034). A phase
    that holds problems or could not run adds one Finding of that status, so the exit says so; every phase still answers.
    `readers` are the PhaseReaders a test swaps (None: `READERS`).
    """

    name = "show-flow"
    summary = "Say where a project stands, phase by phase from the idea to the deploy, and what each phase offers next (P825)."
    arguments = (COMMON_ARGUMENTS["project"]._replace(help="the project folder (default: here)"), COMMON_ARGUMENTS["json"])
    effects = (READS,)
    data_keys = ("phases", "stands_at", "fingerprint", "guide", "deploy", "name", "title", "stamp", "artifact")
    privacy_for = staticmethod(privacy_for)

    def __init__(self, readers=None):
        self.readers = readers or READERS

    def run(self, project, *, outside):
        reading = reading_of(project, self.readers)
        phases, guide = reading.phases, reading.guide
        findings = [Finding(phase.status, phase.phase, flow_codes.PHASE_PROBLEMS if phase.status == PROBLEMS else flow_codes.PHASE_COULD_NOT_RUN,
                            PHASE_SENTENCE % (phase.phase, phase.says[0]), PHASE_FIX)
                    for phase in phases if phase.status in (PROBLEMS, COULD_NOT_RUN)]
        steps = now_steps(project, phases, guide)
        lines = [line for phase in phases for line in phase_line(phase)]
        lines += guide_lines(guide, steps)
        data = reading.to_dict()
        return OperationResult(data, findings, steps, lines=lines)
# --- end MVP ---
