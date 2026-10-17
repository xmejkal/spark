"""
One try to reach a board: run a line of code on it, and cure it once when its USB output died at power-on (P251, #264).

A library. `reach` wraps the connection in a RetryingBoardConnection and returns a ReachResult that says whether the
board answered, what it printed, whether the first try failed, and the Cure when one ran. reach.py prints it.
"""

from collections import namedtuple

from board_console import PORT_BACK_S
from board_connection import RAW_REPL_REFUSED, BoardCodeError, BoardUnreachableError, RetryingBoardConnection

#: The code a reach runs when it is given none: one line that prints `reached`.
PRINT_REACHED = 'print("reached")'
#: Why no cure ran although mpremote could not enter the raw REPL.
NO_PROBE_MESSAGE = "no cure: mpremote is not a Python package here, so the console cannot be opened with DTR and RTS off"
#: The two causes a reach names when the board did not answer after a cure (D11).
BOTH_CAUSES_MESSAGE = ("its USB output may still be dead, or its firmware does not read its console (code that never reads "
               "stdin keeps mpremote out)")

#: Result: `reached` is True when the board answered (with PRINT_REACHED: printed `reached`), `first_try_failed`
#: when the first run did not answer (None with cure_first: there is no first try), `cure` the board_console.Cure when
#: one ran, `why` what went wrong, else None. `entered` is False only when mpremote said it could not enter the raw
#: REPL, so the code never ran. Any other failure may come after the code started (a timeout, a link that dropped),
#: so `entered` is True then, and P247 resets the board.
ReachResult = namedtuple("ReachResult", "reached output first_try_failed cure why entered")


def reach(connection, probe, code=PRINT_REACHED, cure_first=False):
    """The ReachResult of running `code` through `connection`, with `probe` for the cure. With `cure_first`, the cure
    runs before one plain try: the bench's cold arm."""
    runner = connection if cure_first else RetryingBoardConnection(connection, probe)
    cure, reached, why, entered = probe.cure() if cure_first else None, True, None, True
    try:
        output = runner.run_code(code)
    except BoardCodeError as raised:
        output, why = raised.output, "the code raised: %s" % raised
    except BoardUnreachableError as refused:
        output, reached, why, entered = refused.output, False, str(refused), RAW_REPL_REFUSED not in str(refused)
    if why is None and code == PRINT_REACHED and "reached" not in output.split():
        reached, why = False, "the board answered without printing reached: %s" % (output.strip() or "nothing")
    cure = cure if cure_first else runner.last_cure
    if not reached and cure is not None:
        error = why
        why = "%safter the cure%s: %s" % ("" if cure_first else "the first try: %s. " % RAW_REPL_REFUSED,
                                          why_of(cure), error)
        if RAW_REPL_REFUSED in error:
            why += ". So " + BOTH_CAUSES_MESSAGE
    elif not reached and probe is None and RAW_REPL_REFUSED in why:
        why = "%s. %s" % (why, NO_PROBE_MESSAGE)
    first_try_failed = None if cure_first else not reached or cure is not None
    return ReachResult(reached, output, first_try_failed, cure, why, entered)


def why_of(cure):
    """What went wrong in `cure`, as words after "after the cure", or ''."""
    said = ([] if cure.port_back else ["the port was not back in %d s" % PORT_BACK_S]) + \
           (["its read failed: %s" % cure.why] if cure.why else [])
    return " (%s)" % ", ".join(said) if said else ""
