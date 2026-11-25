"""
The spinner of the text view (P478): a frame and the seconds, drawn under a wait's line on a terminal with motion while
spark waits on work whose children are captured, and erased before the next line. `Spinner` is the seam: `NO_SPINNER`
draws nothing (a pipe, Claude's shell, TERM=dumb, --json) and `TerminalSpinner` draws. `cli.view_for` picks one, once.
"""

import threading

from spark.core.events import INDENT
from spark.core.renderers import paint_or_plain

# --- MVP ---
#: The frames on a stream that encodes the marks: cli-spinners' `dots`, the spinner rich's `Console.status` draws.
FRAMES = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
#: The frames on a stream that cannot encode them: cli-spinners' `line`.
ASCII_FRAMES = "|/-\\"
#: How often the spinner redraws, in seconds: presentation (cli-spinners' dots redraws every 80 ms), no board fact.
TICK_S = 0.1
#: How long a wait lasts before the spinner shows, in seconds, so a short wait draws none.
SHOW_AFTER_S = 1.0
#: ECMA-48: back to the row's start (CR) and erase the row (EL 2).
ERASE = "\r\x1b[2K"
#: DECTCEM: hide the cursor while the spinner is drawn, and show it again.
HIDE_CURSOR, SHOW_CURSOR = "\x1b[?25l", "\x1b[?25h"
#: The seconds after the frame: a measurement since the wait began, never a limit or an estimate.
SECONDS = " %d s"


class Spinner:
    """Strategy: what the text view draws under a wait's line while spark waits (P478). The base draws nothing, so a pipe,
    Claude's shell, TERM=dumb and --json get it as NO_SPINNER."""

    def start(self):
        """A wait begins: draw from now on, or nothing."""

    def stop(self):
        """The wait is over: erase what was drawn and show the cursor, or nothing."""


#: The Null Object of the seam: a Spinner that draws nothing.
NO_SPINNER = Spinner()


class TerminalSpinner(Spinner):
    """Strategy: the spinner of a terminal with motion. From SHOW_AFTER_S on, each tick of `ticker` redraws one row, a frame
    painted in the role `spinner` and the seconds since `start` in `quiet`, and hides the cursor. `stop` always stops the
    ticker first, also after a stop that a Ctrl-C cut, and only then erases the row and shows the cursor, so no tick draws
    after the erase. A stream that raises in a tick (a closed terminal) ends the drawing. `ticker` is any object with
    `start(tick)`, which calls `tick` every TICK_S from then on, and `stop()`, which returns only when no tick runs:
    ThreadTicker, or the tests' FakeTicker."""

    def __init__(self, stream, painter, style, clock, ticker):
        self.stream, self.painter, self.clock, self.ticker = stream, painter, clock, ticker
        self.frames = FRAMES if style.symbols else ASCII_FRAMES
        self.began, self.drawn, self.broken = 0.0, 0, False

    def start(self):
        self.stop()
        self.began, self.drawn = self.clock.monotonic(), 0
        self.ticker.start(self.tick)

    def stop(self):
        self.ticker.stop()
        if self.drawn:
            print(ERASE + SHOW_CURSOR, end="", flush=True, file=self.stream)
            self.drawn = 0  # only after the erase: a Ctrl-C in the write leaves it to the next stop

    def tick(self):
        """Redraw the row, unless the wait is shorter than SHOW_AFTER_S or the stream broke."""
        seconds = self.clock.monotonic() - self.began
        if seconds < SHOW_AFTER_S or self.broken:
            return
        row = paint_or_plain(self.painter, [[(INDENT, "fact"), (self.frames[self.drawn % len(self.frames)], "spinner"),
                                             (SECONDS % int(seconds), "quiet")]])
        try:
            print(ERASE + ("" if self.drawn else HIDE_CURSOR) + row, end="", flush=True, file=self.stream)
        except (OSError, ValueError):
            self.broken = True
            return
        self.drawn += 1


class ThreadTicker:
    """Adapter: a daemon thread of the OS that calls `tick` every TICK_S until `stop`. `stop` sets the thread's Event and
    joins it whenever it still holds the thread, and lets the thread go only after the join returned, so a stop that a
    Ctrl-C cut is joined by the next one. `start` stops a thread it still holds first."""

    def __init__(self):
        self.thread, self.stopped = None, threading.Event()

    def start(self, tick):
        self.stop()  # a reused ticker leaves no thread running
        self.stopped = threading.Event()
        self.thread = threading.Thread(target=self._loop, args=(tick, self.stopped), daemon=True)
        self.thread.start()

    @staticmethod
    def _loop(tick, stopped):
        while not stopped.wait(TICK_S):
            tick()

    def stop(self):
        if self.thread is None:
            return
        self.stopped.set()
        self.thread.join()
        self.thread = None
# --- end MVP ---
