"""
The live try (P247, #267): one gated call runs a short piece of code on the running board, says whether the board
ran it, and resets the board at the end (P235's D9).

A library: live.py only parses arguments, calls `LiveTryService` and prints.

    LiveTryResult    the answer code, why, what the board printed, the cure, the reset and two pin facts.
    LiveTryService   checks the grant (P253), refuses a restricted pin (P254), runs the code with one cure (P251),
                     and restarts the chip after any code that may have got in (P252's pick, a hard reset).

Nothing reaches the board without a grant: the grant check runs only `mpremote devs`, and every refusal comes before
the run. The reset runs unless mpremote said it could not enter the raw REPL, so code that never ends is stopped too.
A Ctrl-C during the run stops live.py before the reset.
"""

from collections import namedtuple

import board_reach
from board_connection import BoardUnreachableError
from board_grant import MESSAGE_FOR
from outcomes import EXIT_COULD_NOT_RUN, EXIT_OK, EXIT_PROBLEMS
from restricted_pins import RestrictedPins, whole_numbers_in

#: The answer codes. RAN: the board ran the code (an empty answer counts). RAISED: the board ran it and it raised.
#: NOT_REACHED: the board did not answer. The REFUSED_ codes: nothing was sent to the board.
RAN, RAISED, NOT_REACHED = "ran", "raised", "not_reached"
REFUSED_NO_GRANT, REFUSED_PIN, REFUSED_NO_PARSE = "refused_no_grant", "refused_pin", "refused_no_parse"
#: The exit code for each answer, from outcomes.py: a refusal or a raise is a problem found, as grant.py's refusals are.
EXIT_FOR_ANSWER = {RAN: EXIT_OK, RAISED: EXIT_PROBLEMS, REFUSED_NO_GRANT: EXIT_PROBLEMS, REFUSED_PIN: EXIT_PROBLEMS,
                   REFUSED_NO_PARSE: EXIT_PROBLEMS, NOT_REACHED: EXIT_COULD_NOT_RUN}
#: The reset codes: `mpremote reset` exited 0, or it did not. A result with no reset holds None.
RESET_DONE, RESET_FAILED = "done", "failed"
#: Added to `why` when the reset failed after code got into the board.
RESET_FAILED_MESSAGE = "the reset failed (%s), so the firmware may be stopped: press R or replug to run it"
#: What a person reads when the record names no restricted pin (`pins_checked` is False).
NO_RESTRICTED_PINS_MESSAGE = "the board record names no usb or flash pin, so the pin check had nothing to refuse"

#: Result: `answer` one of the answer codes, `grant_why` the grant's own WHY_ code when it refused, else None, `why` the
#: sentence (None after a clean run), `output` what the board printed, `cure` the board_console.Cure when one ran,
#: `reset` RESET_DONE, RESET_FAILED or None, `pins_checked` False when the record names no restricted pin,
#: `gpio_numbers_in_code` the whole numbers in the code that are a GPIO of this board. That list over-claims:
#: `print(1)` lists GPIO1.
LiveTryResult = namedtuple("LiveTryResult",
                           "answer grant_why why output cure reset pins_checked gpio_numbers_in_code")


def exit_code(result):
    """The exit code of a LiveTryResult: the answer's, but a failed reset can never read as a clean run."""
    return EXIT_COULD_NOT_RUN if result.reset == RESET_FAILED else EXIT_FOR_ANSWER[result.answer]


def gpio_numbers(board):
    """Every GPIO number a board record names: the values of `pins` and each `pin_roles` role's `gpio` list."""
    named = {gpio for gpio in (board.get("pins") or {}).values() if type(gpio) is int}
    for spec in (board.get("pin_roles") or {}).values():
        gpios = spec.get("gpio") if isinstance(spec, dict) else None
        named |= {gpio for gpio in gpios or () if type(gpio) is int}
    return named


class LiveTryService:
    """Service: one live try on the board on one port. `grants` is a board_grant.GrantService, `connection` a bare
    board_connection.BoardConnection on that port, `probe` its board_console.ConsoleProbe (or None for no cure),
    `board` the project's board record. RestrictedPins.from_board's BrokenRecordError and the grant check's LookStop pass up."""

    def __init__(self, grants, connection, probe, board):
        self.grants, self.connection, self.probe, self.board = grants, connection, probe, board

    def run(self, code, port, script="live.py"):
        """The LiveTryResult of running `code` on the board on `port`, after the grant and the pin check."""
        pins = RestrictedPins.from_board(self.board)
        facts = dict(pins_checked=not pins.has_none(),
                     gpio_numbers_in_code=sorted((whole_numbers_in(code) or set()) & gpio_numbers(self.board)))
        checked = self.grants.check(port, script)
        if not checked.granted:
            return LiveTryResult(REFUSED_NO_GRANT, checked.why, MESSAGE_FOR[checked.why], "", None, None, **facts)
        refused = pins.why_refused(code)
        if refused:
            answer = REFUSED_NO_PARSE if whole_numbers_in(code) is None else REFUSED_PIN
            return LiveTryResult(answer, None, refused, "", None, None, **facts)
        reached = board_reach.reach(self.connection, self.probe, code=code)
        answer = (RAISED if reached.why else RAN) if reached.reached else NOT_REACHED
        reset, why = None, reached.why
        if reached.entered:
            try:
                self.connection.reset()
                reset = RESET_DONE
            except BoardUnreachableError as failed:
                reset, why = RESET_FAILED, ". ".join(filter(None, [why, RESET_FAILED_MESSAGE % failed]))
        return LiveTryResult(answer, None, why, reached.output, reached.cure, reset, **facts)
