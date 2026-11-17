"""
Where a project stands as an Operation on the core (P825, #1183): each phase's reader in order, one line per phase, the
first phase still open, and the offers each phase holds. It reads and never writes. `flow.py show` is its CLI; the page
(P827) and the requests (P829) read the same answer.
"""

from pathlib import Path

from spark.flow import flow_codes
from spark.flow.phase_readers import MARKS, READERS
from spark.records import store
from spark.core.operation import COMMON_ARGUMENTS, READS, Operation
from spark.core.outcomes import COULD_NOT_RUN, OK, PROBLEMS
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


class ShowFlow(Operation):
    """
    Operation: where a project stands. It asks each PhaseReader in order and answers `data.phases` (each Phase as a dict)
    and `data.stands_at`, the first phase whose status is neither ok nor None. A phase that holds problems or could not run
    adds one Finding of that status, so the exit says so; every phase still answers. `readers` are the PhaseReaders a test
    swaps (None: `READERS`).
    """

    name = "show-flow"
    summary = "where a project stands, phase by phase from the idea to the deploy, with the offers of each phase"
    arguments = (COMMON_ARGUMENTS["project"]._replace(help="the project folder (default: here)"), COMMON_ARGUMENTS["json"])
    effects = (READS,)
    data_keys = ("phases", "stands_at")
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
        return OperationResult({"phases": [phase.to_dict() for phase in phases], "stands_at": stands_at}, findings, lines=lines)
# --- end MVP ---
