"""
The follow-up (P1035, piece 3 of P793): what a frontend adds to the answer of a run that wrote to a project, after the
Operation's own. `run_operation` asks it (`RunOptions.follow_up`), and the flow fills it in, so the core imports nothing
of the flow.
"""

# --- MVP ---
#: One step as a person reads it: the line to run, then why. The flow's lines use it.
STEP_LINE = "  next: %s — %s"


class FollowUp:
    """Strategy: what a frontend adds to a run that wrote to a project (P1035): `steps(project)` gives the NextSteps that
    follow the Operation's own, and `line(step)` the line a person reads for each. The base adds nothing."""

    def steps(self, project):
        return []

    def line(self, step):
        return STEP_LINE % (step.op, step.why)
# --- end MVP ---
