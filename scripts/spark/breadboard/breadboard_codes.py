"""
The reasons breadboard.py writes no sheet, each a code with one sentence (P692, W6-B2).

A leaf: it imports nothing of spark. Each refusal names its code, so an agent decides on the code and never on the English
sentence (no magic strings, P260). A NotBuilt carries its code, and `sheet.refusal_code` gives the code of each error
`main` catches. breadboard.py has no `--json`, so the codes wait in the library for the Operation that comes later. A
drawing not written has its own codes, in drawing.CODES.

STORE_PROBLEM is also board_codes', as an equal literal in two leaves, with the same meaning.
"""


# --- MVP ---
#: NotBuilt: the built circuit is missing, stale, failed or cannot be read. Each asks to build again, but a failed
#: build first asks to fix what failed.
NOT_BUILT, BUILT_FROM_OTHER_REQUIREMENTS = "not_built", "built_from_other_requirements"
BUILD_FAILED, BUILD_UNREADABLE = "build_failed", "build_unreadable"
#: The errors from outside that main catches: each asks for another fix.
REQUIREMENTS_UNUSABLE, STORE_PROBLEM, FILE_UNUSABLE = "requirements_unusable", "store_problem", "file_unusable"

#: Each code and the one sentence that says what it means.
CODES = {
    NOT_BUILT: "nothing is built yet, or the build did not finish, so there is no circuit to wire",
    BUILT_FROM_OTHER_REQUIREMENTS: "the built circuit was built from other requirements than the file names now",
    BUILD_FAILED: "the last build failed, so its circuit is not a board to wire",
    BUILD_UNREADABLE: "the built circuit, or the record of what it was built from, cannot be read",
    REQUIREMENTS_UNUSABLE: "the requirements file cannot be loaded as a design: a part, a board or a field is wrong",
    STORE_PROBLEM: "spark's store cannot be read or written",
    FILE_UNUSABLE: "a file the sheet reads or writes cannot be opened: its path, its folder or its permissions",
}
# --- end MVP ---
