"""
Where a project stands as an Operation on the core (P825, #1183): each phase's reader in order, one line per phase, the
offers each phase holds, the guide (P977) and its now offer's step (P1030). It reads and never writes. `flow.py show` is
its CLI; the page (P827) and the requests (P829) read the same phases.
"""

from pathlib import Path

from spark.flow import flow_codes
from spark.flow.fingerprint import fingerprint_of
from spark.flow.guide import guide_of, stands_at_of
from spark.flow.phase_readers import MARKS, READERS
from spark.records import store
from spark.core.operation import COMMON_ARGUMENTS, READS, Operation
from spark.core.outcomes import COULD_NOT_RUN, PROBLEMS
from spark.core.privacy import Privacy
from spark.core.result import Finding, OperationResult
from spark.core.text_guards import printable

# --- MVP ---
#: One line of the guide, after the phases (P1030): its label, as the page writes it, and its items, comma apart.
GUIDE_LINE = "  %s: %s"
#: The NOW line's end: the key of the now offer, whose step `next` holds.
NOW_KEY = " [%s]"
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


def guide_lines(guide):
    """The guide as a person reads it, in the page's words and order (P1030): NOW with the key of its offer, DONE, LATER,
    why there is no simulation, SET ASIDE. A list with no item draws no line, as on the page."""
    now = guide["now"]
    lines = [GUIDE_LINE % (flow_codes.GUIDE_NOW % now["phase"], now["says"] + (NOW_KEY % now["offer"] if now["offer"] else ""))] if now else []
    lines += [GUIDE_LINE % (flow_codes.GUIDE_DONE, ", ".join(guide["done"]))] if guide["done"] else []
    lines += [GUIDE_LINE % (flow_codes.GUIDE_LATER, ", ".join(guide["later"]))] if guide["later"] else []
    lines += ["  " + guide["no_simulation"]] if guide["no_simulation"] else []
    lines += [GUIDE_LINE % (flow_codes.GUIDE_SET_ASIDE, ", ".join(guide["set_aside"]))] if guide["set_aside"] else []
    return [printable(line) for line in lines]


def now_steps(phases, guide):
    """The `next` of `show`: the step of the offer the guide's now names, else none (P1030). A phase with no offer has no
    step yet (piece 2), so an empty `next` means: read data.guide.now."""
    key = guide["now"]["offer"] if guide["now"] else None
    return [offer.step for phase in phases for offer in phase.offers if offer.key == key]


def phases_of(project, readers=None):
    """The Phases of `project`, one per reader in the readers' order: the one source of the phases, for `show`, the page
    (P827) and a request (P829), which needs no guide. `readers` are the PhaseReaders a test swaps (None: `READERS`)."""
    return [reader.answer(project) for reader in readers or READERS]


def flow_and_guide(project, readers=None):
    """(the Phases of `project`, its guide, `guide.guide_of`): `show` and the page compute the guide once (P1030)."""
    phases = phases_of(project, readers)
    return phases, guide_of(project, phases)


def read_flow(project, readers=None):
    """(the Phases of `project`, and `stands_at`, the guide's now phase: `guide.stands_at_of`, the one rule, P1030)."""
    phases, guide = flow_and_guide(project, readers)
    return phases, stands_at_of(guide)


class ShowFlow(Operation):
    """
    Operation: where a project stands. It asks each PhaseReader in order and answers `data.phases` (each Phase as a dict),
    `data.stands_at`, the guide's now phase (`stands_at_of`, P1030), `data.fingerprint` (`fingerprint_of`, P829) and
    `data.guide` (`guide_of`, P977). Its lines end with the guide's, and `next` holds the now offer's step (P1030). A phase
    that holds problems or could not run adds one Finding of that status, so the exit says so; every phase still answers.
    `readers` are the PhaseReaders a test swaps (None: `READERS`).
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
        phases, guide = flow_and_guide(project, self.readers)
        stands_at = stands_at_of(guide)
        findings = [Finding(phase.status, phase.phase, flow_codes.PHASE_PROBLEMS if phase.status == PROBLEMS else flow_codes.PHASE_COULD_NOT_RUN,
                            PHASE_SENTENCE % (phase.phase, phase.says[0]), PHASE_FIX)
                    for phase in phases if phase.status in (PROBLEMS, COULD_NOT_RUN)]
        lines = [line for phase in phases for line in phase_line(phase)]
        lines += guide_lines(guide)
        data = {"phases": [phase.to_dict() for phase in phases], "stands_at": stands_at, "fingerprint": fingerprint_of(project, phases),
                "guide": guide}
        return OperationResult(data, findings, now_steps(phases, guide), lines=lines)
# --- end MVP ---
