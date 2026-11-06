"""
The reasons a need cannot be dropped, each a code with one sentence (P514). A leaf: it imports nothing of spark. The Operation
names its code in a Finding, and `CODES` says in one sentence what each means. The codes every Operation can write are the core's.
"""

# --- MVP ---
#: The project has no need of that id: it never had one, or it is already dropped.
NEED_UNKNOWN = "need_unknown"
#: The needs file or the drawer cannot be read, so nothing is dropped.
NEEDS_UNREADABLE = "needs_unreadable"

#: Each code and the one sentence that says what it means.
CODES = {
    NEED_UNKNOWN: "the project has no need of that id: it never had one, or it is already dropped",
    NEEDS_UNREADABLE: "the needs file or the drawer cannot be read, so nothing is dropped",
}
# --- end MVP ---
