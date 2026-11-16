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
#: The last line: the first phase still open, or none.
STANDS_AT_LINE = "  stands at: %s"
EVERY_PHASE_DONE_LINE = "  every phase is done"
#: The Finding of a phase that holds problems or could not run: its first fact, and where to look.
PHASE_SENTENCE = "%s: %s"
PHASE_FIX = "read the phase's facts in data.phases"


def privacy_for(project):
    """The Privacy of a run on `project`: its path, the store's and the home folder's masked (P677)."""
    return Privacy.of(project, store.home(), Path.home(), ())


def phase_line(phase):
    """One phase as a person reads it: `  ✓ needs: ok, 2 need(s): soil, wet (claude)`, then its offer keys indented."""
    said = ", ".join(([MARKS[phase.status][0]] if phase.status else []) + phase.facts)
    lines = ["  %s %s: %s (%s)" % (phase.mark, phase.phase, said, phase.by)]
    lines += ["      offers: %s" % ", ".join(offer.key for offer in phase.offers)] if phase.offers else []
    return [printable(line) for line in lines]


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
        phases = [reader.answer(project) for reader in self.readers]
        stands_at = next((phase.phase for phase in phases if phase.status not in (OK, None)), None)
        findings = [Finding(phase.status, phase.phase, flow_codes.PHASE_PROBLEMS if phase.status == PROBLEMS else flow_codes.PHASE_COULD_NOT_RUN,
                            PHASE_SENTENCE % (phase.phase, phase.facts[0]), PHASE_FIX)
                    for phase in phases if phase.status in (PROBLEMS, COULD_NOT_RUN)]
        lines = [line for phase in phases for line in phase_line(phase)]
        lines.append(STANDS_AT_LINE % stands_at if stands_at else EVERY_PHASE_DONE_LINE)
        return OperationResult({"phases": [phase.to_dict() for phase in phases], "stands_at": stands_at}, findings, lines=lines)
# --- end MVP ---
