"""
`parts.py --drawer-import`: an importer's payload applied to the drawer, as an Operation on the core (P726 PR 3). It was
`parts._op_drawer_import`. New entries, and counts by the re-import rule; the payload is kept in the store so a later import
can tell what shrank. The CLI reads the file and hands the payload in (`Argument.payload`).
"""

from spark.core.operation import COMMON_ARGUMENTS, JSON_DEST, READS, WRITES, Argument
from spark.records import store
from spark.records.answer_operation import ANSWER_ARGUMENTS
from spark.sourcing import drawer
from spark.sourcing.part_operation import PartOperation
from spark.sourcing.write_answers import drawer_answer


# --- MVP ---
class ImportDrawer(PartOperation):
    """Operation: `drawer-import` as parts.py answers it: the changes, the questions, what shrank since the last import."""

    name = "drawer-import"
    data_keys = ('changes', 'questions', 'shelved', 'smaller')
    arguments = (Argument(("--drawer-import",), "source_and_payload", str,
                          "apply an importer's payload (FILE, or - for stdin) to the drawer: new entries, and counts by the re-import rule",
                          nargs=2, metavar=("SOURCE", "FILE"), payload=1),
                 ANSWER_ARGUMENTS["dry_run"], COMMON_ARGUMENTS[JSON_DEST])
    effects = (READS, WRITES)

    def effects_of(self, values):
        return (READS,) if values["dry_run"] else self.effects

    def build_answer(self, source_and_payload, dry_run):
        source, payload = source_and_payload
        changes, questions, problems, smaller = drawer.plan_import(source, payload)
        answer = drawer_answer(changes, questions, problems, dry_run)
        if not problems and not dry_run:
            store.write_json("drawer-import", store.slug(source), drawer.kept_payload(payload))
        return answer._replace(data=dict(answer.data, smaller=smaller), lines=list(answer.lines) + ["  %s" % s for s in smaller])
# --- end MVP ---
