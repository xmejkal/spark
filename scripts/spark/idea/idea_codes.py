"""
The reasons a need cannot be dropped, each a Code with its meaning and its fix (P514, P853). A leaf: it imports nothing of
spark but `spark.core.codes`. The Operation names its code in a Finding or a SparkError, which takes the fix from it, and
`CODES` says in one sentence what each means. The codes every Operation can write are the core's.
"""

from spark.core.codes import Code

# --- MVP ---
NEED_UNKNOWN = Code("need_unknown", "the project has no need of that id: it never had one, or it is already dropped",
                    "drop a need that --needs lists")
NEEDS_UNREADABLE = Code("needs_unreadable", "the needs file or the drawer cannot be read, so nothing is dropped",
                        "drop the need again once the file is fixed")
DROP_UNWRITTEN = Code("drop_unwritten", "the drop could not be planned or written, so the same drop again finishes it",
                      "check the disk and the store folder, then run the same drop again: the drawer is written first "
                      "and the needs file last")

#: Each code and the one sentence that says what it means.
CODES = {code: code.meaning for code in (NEED_UNKNOWN, NEEDS_UNREADABLE, DROP_UNWRITTEN)}
# --- end MVP ---
