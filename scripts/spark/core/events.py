"""
The event seam (P479, P507): how an Operation tells a reader what happens now, while it runs. An Operation reports an
`Event` through `outside.report`, and the frontend's `Reporter` decides what a reader sees. The result at the end stays
one `OperationResult`. Each later Reporter (colour, JSON lines, MCP progress) enters with its frontend.
"""

import sys
from collections import namedtuple

from spark.core.text_guards import guard_lines

# --- MVP ---
#: The kinds of an Event: a sentence the person reads now, and a phase that begins now.
LINE, BEGIN = "line", "begin"
#: The indent of an event line on a terminal. It is presentation, so the terminal adds it, not the Event.
INDENT = "  "


class Event(namedtuple("Event", "kind code text")):
    """Value: one event of a run. `kind` is LINE or BEGIN, `code` the snake_case code of the phase it is about, `text` for a
    LINE one line of words with no newline and no indent, None for a BEGIN. A BEGIN has no end: the next one or the result ends it."""

    __slots__ = ()

    @staticmethod
    def line(code, text):
        return Event(LINE, code, text)

    @staticmethod
    def begin(code):
        return Event(BEGIN, code, None)


class Reporter:
    """Strategy: what a reader sees of the events of a run. `report` returns nothing and never raises on a kind it does not
    know. A Reporter decides on `kind` and `code`, never on `text`."""

    def report(self, event):
        """Show `event`, or nothing: the base shows nothing."""


class TerminalReporter(Reporter):
    """Strategy: the CLI's Reporter. It prints a LINE at once, indented and guarded, and nothing for a BEGIN, so every line
    keeps the bytes it had before the seam. Under --json it prints on stderr, so stdout holds the envelope alone."""

    def __init__(self, stream):
        self.stream = stream

    @classmethod
    def for_json(cls, as_json):
        """The Reporter on stderr with --json and on stdout without, read at the call, so a redirected stream is the one used."""
        return cls(sys.stderr if as_json else sys.stdout)

    def report(self, event):
        if event.kind == LINE:
            print(guard_lines(INDENT + event.text), file=self.stream, flush=True)
# --- end MVP ---
