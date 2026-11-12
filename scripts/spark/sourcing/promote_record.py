"""
`parts.py --promote`: the catalog's record into the project's parts/, or the project's into the plugin's library, as an
Operation on the core (P726 PR 2). It was `part_handlers._op_promote`; `part_facts.promote` copies. The dry run says the
target and copies nothing.
"""

from spark.core import codes
from spark.core.operation import COMMON_ARGUMENTS, JSON_DEST, READS, WRITES, Argument
from spark.records.answer_operation import ANSWER_ARGUMENTS
from spark.records.record_kind import Answer, _cannot
from spark.sourcing.part_facts import promote
from spark.sourcing.part_operation import PartOperation

# --- MVP ---
#: The sentence of a promotion asked for with no project.
NEEDS_PROJECT = "--promote needs --project"


class PromoteRecord(PartOperation):
    """Operation: `promote` as parts.py answers it: where the record went, or would go; no project is a could-not-run
    item; a record nobody has, or a target that exists, is a problem on the id (`part_facts.promote`)."""

    name = "promote"
    data_keys = ('path', 'written')
    arguments = (Argument(("--promote",), "part_id", str, "catalog → the project's parts/, or the project's parts/ → the plugin's library",
                          metavar="PART"),
                 ANSWER_ARGUMENTS["project"], ANSWER_ARGUMENTS["dry_run"], COMMON_ARGUMENTS[JSON_DEST])
    effects = (READS, WRITES)

    def effects_of(self, values):
        return (READS,) if values["dry_run"] else self.effects

    def build_answer(self, part_id, project, dry_run):
        if not project:
            return Answer(unchecked=[_cannot(NEEDS_PROJECT, code=codes.BAD_ARGUMENT)])
        target = promote(part_id, project, dry_run=dry_run)
        return Answer({"path": str(target), "written": not dry_run},
                      ["  %s %s" % ("would promote to" if dry_run else "promoted to", target)])
# --- end MVP ---
