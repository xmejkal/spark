"""
The follow-up (P1035, piece 3 of P793): what a frontend adds to the answer of a run that wrote to a project, after the
Operation's own, and the file written again (PR 2). `run_operation` asks it (`RunOptions.follow_up`), and the flow
fills it in, so the core imports nothing of the flow. A step's line is `renderers.step_command`, the one builder, as a
`PastedLine`, so the mask keeps its real paths (P1256): a masked `--project <project>` is a redirection in a shell.
"""

from spark.core.privacy import PastedLine
from spark.core.renderers import step_command
from spark.core.text_guards import printable

# --- MVP ---
#: One step as a person reads it: the line to run, then why. The flow's lines use it.
STEP_LINE = "  next: %s — %s"


class FollowUp:
    """Strategy: what a frontend adds to a run that wrote to a project (P1035): `steps(project)` gives the NextSteps that
    follow the Operation's own, and `line(step)` the line a person reads for each: the step's command (`step_command`),
    then `mark(step)`, then why, as a PastedLine (P1256). `refresh(project, result)` (PR 2) writes
    again the file `refreshes` names, one the project already has, and gives the sentence that says so, or None when it
    wrote nothing; what it raises is the core's to report. The base adds nothing."""

    #: The file `refresh` writes again, named in its note and in the line of a refresh that failed: None in the base.
    refreshes = None

    def steps(self, project):
        return []

    def mark(self, step):
        """The words after the command of `step`, such as the flow's NEEDS_YOU: none in the base."""
        return ""

    def line(self, step):
        return PastedLine(STEP_LINE % (step_command(step) + self.mark(step), printable(step.why)))

    def refresh(self, project, result):
        return None
# --- end MVP ---
