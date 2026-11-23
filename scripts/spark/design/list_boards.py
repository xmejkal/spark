"""
The list of the boards a project can switch to, as an Operation on the core (P707, N19): `boards.py --list` is its CLI. A
design Operation, because each row says whether the board stops the chain at the footprint stage (`footprint_emitter`), a
design fact (F12, C-7). It writes nothing.
"""

from spark.core.operation import JSON_DEST, COMMON_ARGUMENTS, READS, Argument, Operation
from spark.core.result import OperationResult
from spark.records import board_records
from spark.design import footprint_emitter

# --- MVP ---
#: One row of the text: the active mark, the id, the layer, and the stop line when the board stops at the footprint.
ROW_LINE = "  %s %s (%s)%s"

#: What --list prints, the paragraph of `boards.py --list --help` after its arguments, before the CLI's --json (P855).
DETAILS = """--list marks the project's board with * (requirements.json's board, else boards/active.json's) and says which board
stops the chain at the footprint stage (P121): its file lacks what the footprint is drawn from, and it is still a choice
for pin-map work. A requirements.json that cannot be read marks no board, and the list says why."""


class ListBoards(Operation):
    """
    Operation: every board available to a project, the project's own and spark's library, with the project's one marked and
    the one that stops the chain at the footprint stage said so, never hidden (F12: it is still a choice for pin-map work).
    A board file that cannot be read, or is not a JSON object, is listed and not said to stop: `boards.py --validate` names it.
    """

    name = "list-boards"
    summary = "Every board available to switch to."
    details = DETAILS
    arguments = (Argument(("--list",), "list", bool, "every board available to switch to"),
                 Argument(("--project",), "project", COMMON_ARGUMENTS["project"].kind, "the project to act on (default: found upwards)"),
                 COMMON_ARGUMENTS[JSON_DEST])
    effects = (READS,)

    def run(self, project, *, outside, list=True):
        project = project.resolve() if project else board_records.project_or_library()
        current, note = board_records.marked_board(project)  # None: nothing chosen, or requirements.json cannot be read
        rows, lines = [], []
        for board_id, (layer, path) in sorted(board_records.records(project).items()):
            try:
                board = board_records._read_json(path, "board definition")
            except board_records.BoardError:
                board = None
            stops = isinstance(board, dict) and footprint_emitter.footprint_stop_line(board) or ""
            rows.append({"id": board_id, "layer": layer, "active": board_id == current,
                         "stops_why": footprint_emitter.why_no_footprint(board) if stops else None})
            lines.append(ROW_LINE % ("*" if board_id == current else " ", board_id, layer, " " + stops if stops else ""))
        if not note:  # P988: a note only when said, so an intact project's envelope stays
            return OperationResult({"boards": rows}, lines=lines)
        said = board_records.NOT_MARKED % note
        return OperationResult({"boards": rows}, lines=["  " + said] + lines, notes=[said])
# --- end MVP ---
