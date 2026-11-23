"""
The follow-up (P1035, piece 3 of P793): what a frontend adds to the answer of a run that wrote to a project, after the
Operation's own, and the file written again (PR 2). `run_operation` asks it (`RunOptions.follow_up`), and the flow
fills it in, so the core imports nothing of the flow.
"""

# --- MVP ---
#: One step as a person reads it: the line to run, then why. The flow's lines use it.
STEP_LINE = "  next: %s — %s"


class FollowUp:
    """Strategy: what a frontend adds to a run that wrote to a project (P1035): `steps(project)` gives the NextSteps that
    follow the Operation's own, and `line(step)` the line a person reads for each. `refresh(project, result)` (PR 2) writes
    again the file `refreshes` names, one the project already has, and gives the sentence that says so, or None when it
    wrote nothing; what it raises is the core's to report. The base adds nothing."""

    #: The file `refresh` writes again, named in its note and in the line of a refresh that failed: None in the base.
    refreshes = None

    def steps(self, project):
        return []

    def line(self, step):
        return STEP_LINE % (step.op, step.why)

    def refresh(self, project, result):
        return None
# --- end MVP ---
