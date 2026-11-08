"""
The drop of a need as an Operation on the core (P514, #710): take a need and its pick out of `.spark/needs.json` and release
the holds of the project that only that pick explained, and no other hold. History events stay, and requirements.json, pins.py and the firmware
are not touched: when requirements.json still lists the dropped part, a note says who runs what. parts.py is its CLI.
"""

import drawer
from spark.design import needs
import store
from spark.core import outcomes
from spark.core.errors import SparkError
from spark.core.operation import COMMON_ARGUMENTS, READS, WRITES, Argument, Operation
from spark.core.result import Finding, OperationResult
from spark.idea import idea_codes

# --- MVP ---
#: The sentence of a need that is not there, with the ids that are.
NEED_UNKNOWN_SENTENCE = "no need called %s: it was never there or is already dropped. --needs lists them: %s"
NEED_UNKNOWN_FIX = "drop a need that --needs lists"
#: The fix of a needs file or a drawer that cannot be read.
UNREADABLE_FIX = "drop the need again once the file is fixed"
#: The fix of a plan or a write that failed: the drawer is written first and the needs file last, so a retry finishes it.
UNWRITTEN_FIX = "check the disk and the store folder, then run the same drop again: the drawer is written first and the needs file last"
#: A hold released: the line of a drop, and of its dry run.
RELEASE_LINE = "  %s %d of %d: %s — its need is dropped"
#: The note when requirements.json still lists a part whose need is dropped.
REQUIREMENTS_NOTE = ("requirements.json still lists %s: run parts.py --requirements %s or edit the file, then build. "
                     "If the firmware imported its signal, run import_firmware.py.")


class DropNeed(Operation):
    """
    Operation: drop one need of a project. It plans the project's holds again from the needs that stay and releases only the ones
    the dropped pick alone explained (the fall of the plan before against the plan after), then writes the drawer first and the needs file last, as `--pick` does, so a retry
    after a refused write finishes the rest. The dry run plans fully and writes nothing. A need that is not there is one
    problems Finding with the ids that are. `needs` and `drawer` are the collaborators a test swaps whole (None: the real ones).
    """

    name = "needs-drop"
    arguments = (COMMON_ARGUMENTS["project"]._replace(help="the project folder with .spark/needs.json (default: here)"),
                 Argument(("--need",), "need", str, "the id of the need to drop"),
                 Argument(("--dry-run",), "dry_run", bool, "say what would be dropped and released, and write nothing"),
                 COMMON_ARGUMENTS["json"])
    effects = (READS, WRITES)

    def __init__(self, needs_file=None, drawer_store=None):
        self.needs, self.drawer = needs_file or needs, drawer_store or drawer

    def effects_of(self, values):
        return (READS,) if values["dry_run"] else self.effects

    def run(self, project, need, dry_run, *, outside):
        try:
            current, entries = self.needs.read(project), self.drawer.entries()
        except store.StoreProblem as unreadable:
            raise SparkError("%s", unreadable, code=idea_codes.NEEDS_UNREADABLE, fix=UNREADABLE_FIX)
        try:
            name = store.plan_listed_name(project)
        except (OSError, store.StoreProblem) as failed:
            raise SparkError("the project's name could not be read: %s", failed, code=idea_codes.DROP_UNWRITTEN, fix=UNWRITTEN_FIX)
        ids = [each["id"] for each in current]
        dropped = next((each for each in current if each["id"] == need), None)
        if dropped is None:
            sentence = NEED_UNKNOWN_SENTENCE % (need, ", ".join(ids) or "none")
            return OperationResult({"project": name, "need": need, "needs": ids, "dropped": None, "released": [], "written": False},
                                   [Finding(outcomes.PROBLEMS, need, idea_codes.NEED_UNKNOWN, sentence, NEED_UNKNOWN_FIX)])
        after = [each for each in current if each["id"] != need]
        try:
            changes, released = self.needs.dropped_holds(name, current, after, entries)
            notes = [REQUIREMENTS_NOTE % (part, project) for part in self.needs.parts_left_listed(project, dropped, after)]
            lines = ["  %s %s: %s %s" % ("would drop" if dry_run else "dropped", need, dropped.get("does", ""), dropped.get("what", ""))]
            lines += [RELEASE_LINE % ("would release" if dry_run else "released", hold["was"] - hold["now"], hold["was"], hold["entry"])
                      for hold in released]
            lines += ["  " + note for note in notes]
            data = {"project": name, "need": need, "dropped": dropped, "released": released, "written": not dry_run}
            if not dry_run:
                self.drawer.apply(changes)
                self.needs.write(project, after)
        except (OSError, store.StoreProblem) as failed:
            raise SparkError("the drop of %s was not finished: %s", need, failed, code=idea_codes.DROP_UNWRITTEN, fix=UNWRITTEN_FIX)
        return OperationResult(data, lines=lines, notes=[{"subject": None, "sentence": note} for note in notes] or None)
# --- end MVP ---
