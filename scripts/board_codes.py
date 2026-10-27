"""
The reasons a look or a deploy stops, or cannot check something, each a code with one sentence (P433, S2).

A leaf: it imports nothing of spark. `look.py --json` and `deploy.py --json` write a code in every `problems` and
`unchecked` item, so an agent decides on the code and never on the English sentence (no magic strings, P260). A raise
site names its code in `reason`, and `CODES` says in one sentence what each code means.

    the look's stops       a LookStop's `reason`: the look could not go on
    the look's findings    a Stop's code, and the code of a warning or an unchecked item of a LookReport
    the gate's refusals    a GateClosedError's `reason`: the deploy gate stays shut
    the grant's refusals   a GrantRefusedError's `reason`, from its WHY_ word (board_grant.CODE_FOR_WHY)
    deploy's own           what deploy.py reports when the image, the flash or the board's start fails
"""

# --- MVP ---
#: A LookStop's reason: the look could not go on.
LIST_FAILED, LIST_TIMEOUT = "list_failed", "list_timeout"
NO_PORT, PORT_NOT_LISTED, TWO_BOARDS = "no_port", "port_not_listed", "two_boards"
FLASHER_NOT_ESPTOOL, BOARD_NOT_READ, READ_TIMEOUT = "flasher_not_esptool", "board_not_read", "read_timeout"
NO_BOARD_NAMED, NO_BOARD_RECORD, TOOL_MISSING = "no_board_named", "no_board_record", "tool_missing"
#: A Stop's code: the look found something deploy.py will refuse.
CHIP_DIFFERS, FLASH_TOO_SMALL = "chip_differs", "flash_too_small"
#: The code of a warning, and of the unchecked items of a look.
FLASH_DIFFERS, FIELD_UNKNOWN = "flash_differs", "field_unknown"
NO_TOKEN, LAST_DEPLOY_NOT_CHECKED = "no_token", "last_deploy_not_checked"
#: A GateClosedError's reason: the deploy gate stays shut.
NO_TERMINAL, NO_LOOK, TOKEN_STALE = "no_terminal", "no_look", "token_stale"
ANSWERED_NO, GRANT_ENDED = "answered_no", "grant_ended"
#: A GrantRefusedError's reason, besides ANSWERED_NO.
NOT_A_GRANT, BAD_MINUTES, BAD_SCOPE = "not_a_grant", "bad_minutes", "bad_scope"
NO_MAC, SERIAL_NOT_MAC = "no_mac", "serial_not_mac"
#: What deploy.py reports on its own: the image, the flash, the board's start, and an argument it cannot run with.
IMAGE_REFUSED, FLASH_FAILED = "image_refused", "flash_failed"
READY_NOT_SEEN, READY_UNKNOWN = "ready_not_seen", "ready_unknown"
BAD_ARGUMENT = "bad_argument"

#: Each code and the one sentence that says what it means.
CODES = {
    LIST_FAILED: "mpremote could not list the boards on USB",
    LIST_TIMEOUT: "mpremote took too long to list the boards on USB",
    NO_PORT: "no board is on USB",
    PORT_NOT_LISTED: "the port that --port names is not in the list of boards on USB",
    TWO_BOARDS: "two or more boards are on USB and no --port says which",
    FLASHER_NOT_ESPTOOL: "the look reads a board with esptool only, and the project's flasher is another tool",
    BOARD_NOT_READ: "esptool could not read the board",
    READ_TIMEOUT: "esptool took too long to read the board",
    NO_BOARD_NAMED: "requirements.json names no board",
    NO_BOARD_RECORD: "the project has no board record for the board that requirements.json names",
    TOOL_MISSING: "a tool the step needs is missing or cannot be used",
    CHIP_DIFFERS: "the board's chip is not the chip of the project's board record",
    FLASH_TOO_SMALL: "the board's flash is smaller than the image",
    FLASH_DIFFERS: "the board's flash size is not the size the board record lists",
    FIELD_UNKNOWN: "the board or the record did not say a field, so the look could not compare it",
    NO_TOKEN: "the look gave no token",
    LAST_DEPLOY_NOT_CHECKED: "spark's record of the board's last deploy could not be read",
    NO_TERMINAL: "there is no terminal to ask the person's yes in",
    NO_LOOK: "deploy.py got no token, so no look came before it",
    TOKEN_STALE: "the board or the image is not the one the token names",
    ANSWERED_NO: "the person answered no",
    GRANT_ENDED: "the deploy grant ended before the erase",
    NOT_A_GRANT: "the store's grant file for the board is not a grant for it",
    BAD_MINUTES: "--minutes is not a whole number from 1 to 1440",
    BAD_SCOPE: "--scope is not a scope a grant has",
    NO_MAC: "the board's MAC could not be read",
    SERIAL_NOT_MAC: "the board's USB serial is not its MAC",
    IMAGE_REFUSED: "the evidence refuses the image, or the image changed",
    FLASH_FAILED: "a flash command failed, so the board may be erased and not written",
    READY_NOT_SEEN: "the board's files differ from the image, or the firmware printed no ready",
    READY_UNKNOWN: "the board could not be read after the flash, so ready is neither seen nor missing",
    BAD_ARGUMENT: "an argument that the script cannot run with",
}
# --- end MVP ---
