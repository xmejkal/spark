"""
`parts.py --drawer-set`: drawer entries set from a JSON list, as an Operation on the core (P726 PR 3). It was `parts._op_drawer_set`.
Every write sets, never adds; with `--project`, an `is` may name a record in that project; all of it, or none when anything is
refused (§5.2). The CLI reads the file (or stdin for `-`) and hands the list in (`Argument.payload`).
"""

from spark.core.operation import COMMON_ARGUMENTS, JSON_DEST, READS, WRITES, Argument
from spark.records.answer_operation import ANSWER_ARGUMENTS
from spark.sourcing import drawer
from spark.sourcing.part_operation import PartOperation
from spark.sourcing.write_answers import drawer_answer


# --- MVP ---
class SetDrawer(PartOperation):
    """Operation: `drawer-set` as parts.py answers it: each change made or refused, the questions, what went on the shelf."""

    name = "drawer-set"
    data_keys = ('changes', 'questions', 'shelved')
    arguments = (Argument(("--drawer-set",), "items", str, "set drawer entries from a JSON list in FILE (- for stdin): every write sets, never adds; with --project, an `is` may "
                          "name a record in that project, such as one /spark:research just wrote; an entry may also say its about, description and tags",
                          metavar="FILE", payload=0),
                 ANSWER_ARGUMENTS["project"], ANSWER_ARGUMENTS["dry_run"], COMMON_ARGUMENTS[JSON_DEST])
    effects = (READS, WRITES)

    def effects_of(self, values):
        return (READS,) if values["dry_run"] else self.effects

    def build_answer(self, items, project, dry_run):
        return drawer_answer(*drawer.plan_set(items, project), dry_run)
# --- end MVP ---
