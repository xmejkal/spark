"""
The reasons a record, a tool or the store refuses, each a Code with its meaning and its fix (P716, W6-R2, P935):
board_records' BoardError, tool_finder's ToolError and store's StoreError, wherever they are raised.

A leaf: it imports nothing of spark but `spark.core.codes`. Each refusal names its code, so an agent decides on the code
and never on the English sentence (no magic strings, P260). The three errors are `errors.CodedMessageError`s, so a raise
cannot leave its code out; a SparkError and `Finding.of` take the fix from the code. A variant is another Code of its
parent's word and meaning, named after it, with a fix of its own.

Two codes are equal literals of another leaf, with the same meaning: TOOL_MISSING is board_codes', firmware_codes' and
build_codes', and MISSING_FACT is board_codes', so `missing_facts` reads no bench leaf.
"""

from spark.core.codes import Code

# --- MVP ---
#: board_records: the project, the board selection and the board definitions.
NO_PROJECT_HERE = Code("no_project_here", "no folder up from here holds boards/active.json or .spark/, so there is no project to act on",
                       "run it from the project's folder, or run /spark:init there first")
BOARD_FILE_MISSING = Code("board_file_missing", "the board selection file, or a board definition file, is not there",
                          "pick a board with boards.py, or write the board definition the sentence names")
NO_BOARD_SELECTED = Code("no_board_selected", "the board selection names no board, or holds something that is not one board id",
                         "name one board id in requirements.json, as {\"board\": \"<id>\"} (parts.py --requirements "
                         "writes it), or in boards/active.json for a project with no requirements")
NO_BOARD_DEFINITION = Code("no_board_definition", "neither the project nor spark's library has a board definition of the id asked for",
                           "pick one of the board ids the sentence lists")
BOARD_CONTRACT_BROKEN = Code("board_contract_broken", "a board definition does not meet the board contract",
                             "fix each problem the sentence lists in the board definition, then run again")
NO_SUCH_FIELD = Code("no_such_field", "the board definition holds no field at the dotted path asked for",
                     "ask for a path the board definition holds")
#: tool_finder: the tools lists, a tool's entry, and what finding, installing or pinning a tool meets.
TOOLS_LIST_BROKEN = Code("tools_list_broken", "a tools file is not JSON, or not in the shape of a tools list: fix it or delete it",
                         "fix the tools file the sentence names, or delete it")
TOOL_ENTRY_BROKEN = Code("tool_entry_broken", "a tool's entry, in a tools file or given to --new, is not JSON or lacks what its kind needs",
                         "fix the entry as the sentence says, then run again")
UNKNOWN_TOOL = Code("unknown_tool", "no tools file names a tool or a role of this name", "tools.py lists the tools and roles by name")
CONTRACT_NOT_MET = Code("contract_not_met", "the tool does not say it meets the contract its role asks, so the step will not use it",
                        "pick a tool for the role that meets its contract")
TOOL_OFF = Code("tool_off", "the tool is turned off in a tools file", "turn the tool on with tools.py, or pick another for its role")
NEEDS_LOOP = Code("needs_loop", "a tool's needs go round in a loop", "remove one of the needs the sentence names from its entry")
TOOL_MISSING = Code("tool_missing", "a tool the step needs is missing or cannot be used",
                    "install the tool as the sentence says, then run again")
TOOL_TOO_OLD = Code("tool_too_old", "the tool is older than the oldest version spark runs",
                    "install a newer version as the sentence says, then run again")
NO_BUILD_FOR_PLATFORM = Code("no_build_for_platform", "the tool has no build for this machine",
                             "install the tool another way, or pick another for its role")
INSTALL_FAILED = Code("install_failed", "a tool was not installed: no way here, a sudo line, a command that failed or a wrong checksum",
                      "install it by hand as the sentence says, then run again")
PIN_REFUSED = Code("pin_refused", "a pin names a version with no digits, or one older than the oldest spark runs, so nothing was written",
                   "pin a version with digits, no older than the one the sentence names")
#: store, and the records read through it: a key, the store's folder, a record file, a URL and a kept document.
KEY_NOT_PLAIN = Code("key_not_plain", "a key is not plain (lower-case letters, digits and '-'), so it could leave its folder",
                     "use a key of lower-case letters, digits and '-' only")
#: A variant of KEY_NOT_PLAIN: a name a project registers in spark's store (`registered_project_store`).
KEY_NOT_PLAIN_REGISTERED = Code(KEY_NOT_PLAIN, KEY_NOT_PLAIN.meaning, "register a name such as pixel-games")
STORE_IN_REPOSITORY = Code("store_in_repository", "the store would be inside a git work tree, and what the person owns stays out of every repository",
                           "point SPARK_HOME at a folder outside every git work tree")
STORE_NOT_WRITABLE = Code("store_not_writable", "spark's store cannot be made or written where SPARK_HOME points",
                          "point SPARK_HOME at a folder you can write")
RECORD_FILE_BROKEN = Code("record_file_broken", "a file spark reads a record from is not JSON, or not in its shape: fix it by hand",
                          "fix the file the sentence names by hand, then run again")
NOT_A_BOARD_RECORD = Code("not_a_board_record", "the record a deploy is kept in is not a board record, so it was left as it is",
                          "move the file the sentence names away, then deploy again")
URL_REFUSED = Code("url_refused", "a URL's scheme, or the scheme it was redirected to, is not http or https, so spark does not open it",
                   "give an http or https URL")
URL_UNREACHABLE = Code("url_unreachable", "a URL does not answer", "run again when the URL answers")
FILE_NAME_REFUSED = Code("file_name_refused", "a document's file name could leave the sources, holds a control character or is too long to keep",
                         "keep the document under a short plain name")
DOCUMENT_NOT_KEPT = Code("document_not_kept", "what was written into the store is not what was fetched, so it was deleted",
                         "check the disk of spark's store, then fetch again")
#: answer_operation (P726), store, storage, keep_file, keep_picture, validate_parts and tool_finder (P1041): a file an
#: Operation reads or writes, a project's or the store's, that the disk refused or that is not JSON.
FILE_REFUSED = Code("file_refused", "a file the operation reads or writes could not be read or written, or is not JSON: the sentence names it",
                    "fix the file the sentence names, or its permissions, then run again")
#: missing_facts: a stage needs a fact the record lacks (P464). The fix is a template of the board's id.
MISSING_FACT = Code("missing_fact", "a stage needs a fact the record lacks, so it stopped short of guessing it",
                    "Tell it: write it with `parts.py --fact-set %s FILE --project .` from the project's folder, as {value, verified, source}. "
                    "Find it: run /spark:research. Or measure it on the bench.")
#: registered_project_store and bench.py record (P920): a name another project holds, and a name nobody registered. The
#: fix of NOT_REGISTERED is a template of the name, twice.
NAME_TAKEN = Code("name_taken", "another project holds this name in spark's store, so it was not registered",
                  "pick another name, then run bench.py register again")
NOT_REGISTERED = Code("not_registered", "no project registered this name in spark's store, so nothing was recorded",
                      "run bench.py register %s --origin <origin> --tool <tool> from spark's code once, then bench.py record %s again")
BLANK_VALUE = Code("blank_value", "a value the record needs is empty, only spaces, or holds a control character, so nothing was written",
                   "give the origin and the tool as text, such as --origin <the origin remote> --tool box.py, then run bench.py register again")
#: launcher (P920): the Python or the bench.py the launcher in spark's store runs is gone.
LAUNCHER_STALE = Code("launcher_stale", "the code the launcher in spark's store runs is gone, so nothing ran",
                      "run bench.py register <name> --origin <origin> --tool <tool> again from a spark checkout that stays: it writes "
                      "the launcher again")

#: Each code and the one sentence that says what it means.
CODES = {code: code.meaning for code in (
    NO_PROJECT_HERE, BOARD_FILE_MISSING, NO_BOARD_SELECTED, NO_BOARD_DEFINITION, BOARD_CONTRACT_BROKEN, NO_SUCH_FIELD,
    TOOLS_LIST_BROKEN, TOOL_ENTRY_BROKEN, UNKNOWN_TOOL, CONTRACT_NOT_MET, TOOL_OFF, NEEDS_LOOP, TOOL_MISSING, TOOL_TOO_OLD,
    NO_BUILD_FOR_PLATFORM, INSTALL_FAILED, PIN_REFUSED, KEY_NOT_PLAIN, STORE_IN_REPOSITORY, STORE_NOT_WRITABLE,
    RECORD_FILE_BROKEN, NOT_A_BOARD_RECORD, URL_REFUSED, URL_UNREACHABLE, FILE_NAME_REFUSED, DOCUMENT_NOT_KEPT,
    FILE_REFUSED, MISSING_FACT, NAME_TAKEN, NOT_REGISTERED, BLANK_VALUE, LAUNCHER_STALE)}
# --- end MVP ---
