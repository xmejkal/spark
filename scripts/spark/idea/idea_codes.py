"""
The reasons a need cannot be dropped, or a held part cannot be moved to another project (P1124), each a Code with its meaning
and its fix (P514, P853). A leaf: it imports nothing of spark but `spark.core.codes`. The Operation names its code in a Finding or a SparkError, which takes the fix from it, and
`CODES` says in one sentence what each means. The codes every Operation can write are the core's.
"""

from spark.core import codes
from spark.core.codes import Code

# --- MVP ---
NEED_UNKNOWN = Code("need_unknown", "the project has no need of that id: it never had one, or it is already dropped",
                    "drop a need that --needs lists")
NEEDS_UNREADABLE = Code("needs_unreadable", "the needs file or the drawer cannot be read, so nothing is dropped",
                        "drop the need again once the file is fixed")
DROP_UNWRITTEN = Code("drop_unwritten", "the drop could not be planned or written, so the same drop again finishes it",
                      "check the disk and the store folder, then run the same drop again: the drawer is written first "
                      "and the needs file last")
MOVE_SAME_PROJECT = Code("move_same_project", "the move names one project twice, by its folder or by the name its holds go under, "
                         "so nothing moves", "name two projects: the one that holds the part, then the one that takes it")
MOVE_NOT_PICKED = Code("move_not_picked", "no need of the first project picks that part, so it has no hold to move",
                       "parts.py --needs <project> lists each need's pick: move a part that one of them picks")
MOVE_PART_OF_COUNT = Code("move_part_of_count", "the first project would let go more pieces than the second takes, and a move "
                          "of part of a count is not there yet", "pick the part for the second project with --pick, after "
                          "freeing what it needs with --needs-drop or --drawer-set")
MOVE_UNWRITTEN = Code("move_unwritten", "the move could not be read or written whole, so the same move again finishes it",
                      "check the disk and the store folder, then run the same move again: the drawer is written first and "
                      "the first project's needs.json last")
#: A variant of the core's BAD_ARGUMENT: the third value of --move-hold is no NEED=ID.
BAD_ARGUMENT_MOVE = Code(codes.BAD_ARGUMENT, codes.BAD_ARGUMENT.meaning, "give the need of the second project and the part as NEED=ID: "
                         "button=tactile-6mm")

#: Each code and the one sentence that says what it means.
CODES = {code: code.meaning for code in (NEED_UNKNOWN, NEEDS_UNREADABLE, DROP_UNWRITTEN, MOVE_SAME_PROJECT, MOVE_NOT_PICKED,
                                         MOVE_PART_OF_COUNT, MOVE_UNWRITTEN)}
# --- end MVP ---
