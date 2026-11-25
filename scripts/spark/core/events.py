"""
The event seam (P479, P507): how an Operation tells a reader what happens now, while it runs. An Operation reports an
`Event` through `outside.report`, and the frontend's `Reporter` decides what a reader sees. The result at the end stays
one `OperationResult`. Each later Reporter (colour, JSON lines, MCP progress) enters with its frontend.
"""

import sys
from collections import namedtuple

from spark.core.text_guards import guard_lines

# --- MVP ---
#: The kinds of an Event: a sentence the person reads now, a phase that begins now, and a wait that begins now.
LINE, BEGIN, WAIT = "line", "begin", "wait"
#: The indent of an event line on a terminal. It is presentation, so the terminal adds it, not the Event.
INDENT = "  "
#: The file descriptor of stderr, where a child's output goes under --json.
STDERR_FD = 2


class Event(namedtuple("Event", "kind code text raw", defaults=(False,))):
    """Value: one event of a run. `kind` is LINE, BEGIN or WAIT, `code` the snake_case code of the phase it is about, `text`
    for a LINE or a WAIT one line of words with no newline and no indent, None for a BEGIN. A BEGIN has no end: the next one
    or the result ends it. An Event of kind WAIT (P478) says that spark now waits on work whose children are captured, so
    nothing else writes to the terminal until the next event, which ends it. `raw` is True for a LINE that carries a line a
    person pastes, which Privacy leaves as it is (P677)."""

    __slots__ = ()

    @staticmethod
    def line(code, text, raw=False):
        """A LINE of `text`; a text that is not a string is a defect of the caller, refused here, never at the Reporter."""
        return Event._with_text(LINE, code, text, raw)

    @staticmethod
    def wait(code, text):
        """A WAIT whose `text` says what spark waits on (P478), refused as a LINE's is."""
        return Event._with_text(WAIT, code, text, False)

    @staticmethod
    def _with_text(kind, code, text, raw):
        """The Event of `kind` with `text`, or a TypeError that names the kind when `text` is not a string."""
        if not isinstance(text, str):
            raise TypeError("a %s needs its text as a string, not %s" % (kind.upper(), type(text).__name__))
        return Event(kind, code, text, raw)

    @staticmethod
    def begin(code):
        return Event(BEGIN, code, None)


class Reporter:
    """Strategy: what a reader sees of the events of a run. `report` returns nothing and never raises on a kind it does not
    know. A Reporter decides on `kind` and `code`, never on `text`."""

    def report(self, event):
        """Show `event`, or nothing: the base shows nothing."""

    def echo_fd(self):
        """The file descriptor a child's uncaptured stdout goes to, so it lands beside the events (E2), or None: as it is."""
        return None

    def mask(self, text):
        """`text` that the frontend writes beside the events, such as the yes question, as a reader may see it (P677)."""
        return text

    def finish(self):
        """The run is over: a Reporter puts the terminal back as it was (P478). The base has nothing to put back."""


class ReporterDecorator(Reporter):
    """Decorator: the base of a Reporter that wraps `inner` and adds one behaviour around it (P478). `report` passes each
    event on, and `finish`, `echo_fd` and `mask` are the inner one's, so a wrapped Reporter is finished too. `stream` is
    the inner one's, where the terminal consent asks."""

    def __init__(self, inner):
        self.inner = inner
        self.stream = getattr(inner, "stream", None)

    def report(self, event):
        self.inner.report(event)

    def finish(self):
        self.inner.finish()

    def echo_fd(self):
        return self.inner.echo_fd()

    def mask(self, text):
        return self.inner.mask(text)


def event_lines(event):
    """The text of the LINE `event` as a terminal shows it: guarded, and each of its lines indented by INDENT. Both the
    terminal's Reporters print it, so a LINE has one form (P478)."""
    return "\n".join(INDENT + line for line in guard_lines(event.text).split("\n"))


class TerminalReporter(Reporter):
    """Strategy: the CLI's Reporter. It prints a LINE at once, guarded and each of its lines indented, and nothing for a BEGIN, so every line
    keeps the bytes it had before the seam. Under --json it prints on stderr, so stdout holds the envelope alone."""

    def __init__(self, stream):
        self.stream = stream

    def report(self, event):
        if event.kind == LINE:
            print(event_lines(event), file=self.stream, flush=True)

    def echo_fd(self):
        """fd 2 when the events go to stderr (--json), so a child's output stays out of the envelope; None on stdout, as it is."""
        return None if self.stream is sys.stdout else STDERR_FD
# --- end MVP ---
