"""
The reasons a record, a tool or the store refuses, each a code with one sentence (P716, W6-R2): boards.py's BoardError,
tools.py's ToolProblem and store.py's StoreProblem, wherever they are raised.

A leaf: it imports nothing of spark. Each refusal names its code, so an agent decides on the code and never on the English
sentence (no magic strings, P260). The three errors are `errors.CodedMessageError`s, so a raise cannot leave its
code out, and every text and exit code stays byte-equal. No records CLI writes a code yet: the codes wait in the library
for the Operation that comes later.

Two codes are equal literals of another leaf, with the same meaning: TOOL_MISSING is board_codes', firmware_codes' and
build_codes', and MISSING_FACT is board_codes', so `missing_facts` reads no bench leaf.
"""


# --- MVP ---
#: boards.py: the project, the board selection and the board definitions.
NO_PROJECT_HERE, BOARD_FILE_MISSING, NO_BOARD_SELECTED = "no_project_here", "board_file_missing", "no_board_selected"
NO_BOARD_DEFINITION, BOARD_CONTRACT_BROKEN, NO_SUCH_FIELD = "no_board_definition", "board_contract_broken", "no_such_field"
#: tools.py: the tools lists, a tool's entry, and what finding, installing or pinning a tool meets.
TOOLS_LIST_BROKEN, TOOL_ENTRY_BROKEN, UNKNOWN_TOOL = "tools_list_broken", "tool_entry_broken", "unknown_tool"
CONTRACT_NOT_MET, TOOL_OFF, NEEDS_LOOP = "contract_not_met", "tool_off", "needs_loop"
TOOL_MISSING, TOOL_TOO_OLD, NO_BUILD_FOR_PLATFORM = "tool_missing", "tool_too_old", "no_build_for_platform"
INSTALL_FAILED, PIN_REFUSED = "install_failed", "pin_refused"
#: store.py, and the records read through it: a key, the store's folder, a record file, a URL and a kept document.
KEY_NOT_PLAIN, STORE_IN_REPOSITORY, STORE_NOT_WRITABLE = "key_not_plain", "store_in_repository", "store_not_writable"
RECORD_FILE_BROKEN, NOT_A_BOARD_RECORD = "record_file_broken", "not_a_board_record"
URL_REFUSED, URL_UNREACHABLE = "url_refused", "url_unreachable"
FILE_NAME_REFUSED, DOCUMENT_NOT_KEPT = "file_name_refused", "document_not_kept"
#: missing_facts: a stage needs a fact the record lacks (P464).
MISSING_FACT = "missing_fact"

#: Each code and the one sentence that says what it means.
CODES = {
    NO_PROJECT_HERE: "no folder up from here holds boards/active.json or .spark/, so there is no project to act on",
    BOARD_FILE_MISSING: "the board selection file, or a board definition file, is not there",
    NO_BOARD_SELECTED: "the board selection names no board, or holds something that is not one board id",
    NO_BOARD_DEFINITION: "neither the project nor spark's library has a board definition of the id asked for",
    BOARD_CONTRACT_BROKEN: "a board definition does not meet the board contract",
    NO_SUCH_FIELD: "the board definition holds no field at the dotted path asked for",
    TOOLS_LIST_BROKEN: "a tools file is not JSON, or not in the shape of a tools list: fix it or delete it",
    TOOL_ENTRY_BROKEN: "a tool's entry, in a tools file or given to --new, is not JSON or lacks what its kind needs",
    UNKNOWN_TOOL: "no tools file names a tool or a role of this name",
    CONTRACT_NOT_MET: "the tool does not say it meets the contract its role asks, so the step will not use it",
    TOOL_OFF: "the tool is turned off in a tools file",
    NEEDS_LOOP: "a tool's needs go round in a loop",
    TOOL_MISSING: "a tool the step needs is missing or cannot be used",
    TOOL_TOO_OLD: "the tool is older than the oldest version spark runs",
    NO_BUILD_FOR_PLATFORM: "the tool has no build for this machine",
    INSTALL_FAILED: "a tool was not installed: no way here, a sudo line, a command that failed or a wrong checksum",
    PIN_REFUSED: "a pin names a version with no digits, or one older than the oldest spark runs, so nothing was written",
    KEY_NOT_PLAIN: "a key is not plain (lower-case letters, digits and '-'), so it could leave its folder",
    STORE_IN_REPOSITORY: "the store would be inside a git work tree, and what the person owns stays out of every repository",
    STORE_NOT_WRITABLE: "spark's store cannot be made or written where SPARK_HOME points",
    RECORD_FILE_BROKEN: "a file spark reads a record from is not JSON, or not in its shape: fix it by hand",
    NOT_A_BOARD_RECORD: "the record a deploy is kept in is not a board record, so it was left as it is",
    URL_REFUSED: "a URL's scheme, or the scheme it was redirected to, is not http or https, so spark does not open it",
    URL_UNREACHABLE: "a URL does not answer",
    FILE_NAME_REFUSED: "a document's file name could leave the sources, holds a control character or is too long to keep",
    DOCUMENT_NOT_KEPT: "what was written into the store is not what was fetched, so it was deleted",
    MISSING_FACT: "a stage needs a fact the record lacks, so it stopped short of guessing it",
}
# --- end MVP ---
