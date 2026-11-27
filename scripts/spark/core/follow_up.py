"""
The follow-up (P1035, piece 3 of P793): what a frontend adds to the answer of a run that wrote to a project, after the
Operation's own, and the file written again (PR 2). `run_operation` asks it (`RunOptions.follow_up`), and the flow
fills it in, so the core imports nothing of the flow. A step's line is `step_line`: `renderers.step_command`, the one
builder, as a `PastedLine`, so the mask keeps its real paths (P1256): a masked `--project <project>` is a redirection in a
shell. Its why is unmasked too; spark's whys are fixed sentences and names, with no path.
"""

from spark.core.privacy import PastedLine
from spark.core.renderers import step_command
from spark.core.text_guards import printable

# --- MVP ---
#: One step as a person reads it: the line to run, then why. The flow's lines use it.
STEP_LINE = "  next: %s — %s"


def step_line(step, after=""):
    """The line a person reads for `step`, the follow-up's and the build's alike (P1256): its command (`step_command`),
    then `after`, then its why through `printable`, as a PastedLine."""
    return PastedLine(STEP_LINE % (step_command(step) + after, printable(step.why)))


class FollowUp:
    """Strategy: what a frontend adds to a run that wrote to a project (P1035): `steps(project)` gives the NextSteps that
    follow the Operation's own, and `line(step)` the line a person reads for each: `step_line`, with the words of
    `after_command(step)` after the command (P1256). `refresh(project, result)` (PR 2) writes
    again the file `refreshes` names, one the project already has, and gives the sentence that says so, or None when it
    wrote nothing; what it raises is the core's to report. The base adds nothing."""

    #: The file `refresh` writes again, named in its note and in the line of a refresh that failed: None in the base.
    refreshes = None

    def steps(self, project):
        return []

    def after_command(self, step):
        """The words after the command of `step`, such as the flow's NEEDS_YOU: none in the base."""
        return ""

    def line(self, step):
        return step_line(step, self.after_command(step))

    def refresh(self, project, result):
        return None
# --- end MVP ---
