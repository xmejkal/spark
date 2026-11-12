"""
`parts.py --validate`: every record a project can build with, against the contract, as an Operation on the core (P726 PR 2).
It was `part_handlers._op_validate`. It writes nothing.
"""

import json

from spark.core.operation import COMMON_ARGUMENTS, JSON_DEST, Argument
from spark.records import records_codes, store
from spark.records.answer_operation import ANSWER_ARGUMENTS
from spark.records.record_kind import Answer, _cannot, _problem, _with_project
from spark.sourcing import part_records
from spark.sourcing.part_operation import PartOperation


# --- MVP ---
class ValidateParts(PartOperation):
    """Operation: `validate` as parts.py answers it: one line per record, ok or its problems, paged from `--from`; a file
    that is not JSON is a could-not-run item. The body calls `part_records.validate`, because its own dest is `validate`."""

    name = "validate"
    data_keys = ('checked',)
    arguments = (Argument(("--validate",), "validate", bool, "every record a project can build with, against the contract"),
                 ANSWER_ARGUMENTS["project"], ANSWER_ARGUMENTS["start"], COMMON_ARGUMENTS[JSON_DEST])

    def build_answer(self, project, start, validate=True):
        checked = []
        for part_id in part_records.available(project):
            path = part_records.definition_path(part_id, project)
            try:
                record = json.loads(path.read_text())
            except json.JSONDecodeError as bad:
                return Answer(unchecked=[_cannot("--validate: %s is not JSON: %s" % (path, bad), code=records_codes.FILE_REFUSED)])
            checked.append({"part": part_id, "path": str(path), "problems": part_records.validate(record, path)})
        shown, truncated = store.page_with_store(checked, start, "validate", ["--validate"] + _with_project(project))
        lines = []
        for one in checked:
            lines.append("  %-28s %s" % (one["part"], "ok" if not one["problems"] else "%d problem(s)" % len(one["problems"])))
            lines += ["      - %s" % problem for problem in one["problems"]]
        return Answer({"checked": shown}, lines, truncated=truncated,
                      problems=[_problem(one["part"], problem) for one in checked for problem in one["problems"]])
# --- end MVP ---
