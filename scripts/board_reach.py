"""
One try to reach a board: run a line of code on it, and cure it once when its USB output died at power-on (P251, #264).

A library. `reach` wraps the connection in a RetryingBoardConnection and returns a ReachResult that says whether the
board answered, what it printed, whether the first try failed, and the Cure when one ran. reach.py prints it.
"""

from collections import namedtuple

from board_connection import RAW_REPL_REFUSED, BoardCodeError, BoardUnreachableError, RetryingBoardConnection

#: The code a reach runs when it is given none: one line that prints `reached`.
PRINT_REACHED = 'print("reached")'
#: Why no cure ran although mpremote could not enter the raw REPL.
NO_PROBE = "no cure: mpremote is not a Python package here, so the console cannot be opened with DTR and RTS off"
#: The two causes a reach names when the board did not answer after a cure (D11).
BOTH_CAUSES = ("its USB output may still be dead, or its firmware does not read its console (code that never reads "
               "stdin keeps mpremote out)")

#: Result: `reached` is True when the board answered, `first_try_failed` when the first run did not, `cure` the
#: board_console.Cure when one ran, `why` what went wrong, else None.
ReachResult = namedtuple("ReachResult", "reached output first_try_failed cure why")


def reach(connection, probe, code=PRINT_REACHED, cure_first=False):
    """The ReachResult of running `code` through `connection`, with `probe` for the cure. With `cure_first`, the cure
    runs before one plain try: the bench's cold arm."""
    runner = connection if cure_first else RetryingBoardConnection(connection, probe)
    cure, reached, why = probe.cure() if cure_first else None, True, None
    try:
        output = runner.run_code(code)
    except BoardCodeError as raised:
        output, why = raised.output, "the code raised: %s" % raised
    except BoardUnreachableError as refused:
        output, reached, why = refused.output, False, str(refused)
    cure = cure if cure_first else runner.last_cure
    if not reached and cure is not None:
        first = "" if cure_first else "the first try: %s. " % RAW_REPL_REFUSED
        why = "%safter the cure: %s. So %s" % (first, why, BOTH_CAUSES)
    elif not reached and probe is None and RAW_REPL_REFUSED in why:
        why = "%s. %s" % (why, NO_PROBE)
    return ReachResult(reached, output, not reached or (cure is not None and not cure_first), cure, why)
