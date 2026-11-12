"""
`parts.py --step`: a spine step of a project starts now, in this Claude Code session, as an Operation on the core (P726
PR 2). It was `part_handlers._op_step`. The cost line counts the step's transcript from here (C-2, C-17); a project not
yet on the person's list is listed. The dry run says what it would write and writes nothing.
"""

from spark.core import codes
from spark.core.operation import COMMON_ARGUMENTS, JSON_DEST, READS, WRITES, Argument
from spark.records import store
from spark.records.answer_operation import ANSWER_ARGUMENTS
from spark.records.record_kind import Answer, _cannot
from spark.sourcing import run_cost
from spark.sourcing.part_operation import PartOperation

# --- MVP ---
#: The sentence of a word that is no spine step.
NOT_A_STEP = "a step is one of %s (the spine, §2 of the store design)"


class MarkStep(PartOperation):
    """Operation: `step` as parts.py answers it: the event written to the history, or what a dry run would write, and the
    project listed when it was not; a word that is no step is a could-not-run item."""

    name = "step"
    arguments = (Argument(("--step",), "project_and_step", str,
                          "a spine step of a project starts now, in this Claude Code session — the cost line counts its transcript from here",
                          nargs=2, metavar=("PROJECT", "STEP")),
                 ANSWER_ARGUMENTS["dry_run"], COMMON_ARGUMENTS[JSON_DEST])
    effects = (READS, WRITES)

    def effects_of(self, values):
        return (READS,) if values["dry_run"] else self.effects

    def build_answer(self, project_and_step, dry_run):
        target, step = project_and_step
        if step not in run_cost.STEPS:
            return Answer(unchecked=[_cannot(NOT_A_STEP % ", ".join(run_cost.STEPS), code=codes.BAD_ARGUMENT)])
        listed = store.find_listed_name(target) is not None
        event = run_cost.step_event(store.plan_listed_name(target) if dry_run else store.add_project(target), step)
        if not dry_run:
            store.append_event(event)
        # C-17: what a step writes is said — a line in the person's history, with the session's id, and the project on their list
        return Answer({"step": event, "written": not dry_run},
                      ["  %s step %s of %s — a line in your history%s" % (
                          "would start" if dry_run else "started", step, event["project"],
                          ", with this Claude Code session's id" if event["session"] else run_cost.session_note())]
                      + ([] if listed else ["  %s %s on your projects" % ("would list" if dry_run else "listed", event["project"])]))
# --- end MVP ---
