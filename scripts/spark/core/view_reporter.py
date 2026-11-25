"""
The text view of a run's events (P478): what a person reads on stdout while a CLI runs without --json. `TextViewReporter`
prints each LINE as `events.TerminalReporter` prints it, and a heading `[n/N] name` when a stage of the Operation's
`stages` begins, painted by the run's painter (P1032). Under --json the events stay `TerminalReporter`'s, on stderr.
"""

from spark.core.events import BEGIN, LINE, Reporter, event_lines
from spark.core.renderers import paint_or_plain
from spark.core.text_guards import printable

# --- MVP ---
#: The heading of the nth of N stages: presentation, so the view makes it from the stage's name, never the Event.
HEADING = "[%d/%d] %s"


class TextViewReporter(Reporter):
    """Strategy: the text view's Reporter (P478). A BEGIN whose code is the name of the nth of the N `stages` prints the
    heading `[n/N] name` through `painter`, one blank line before it unless it is the first. A LINE prints at once as
    `event_lines` gives it, plain. Any other kind prints nothing. It decides on kind and code, never on text."""

    def __init__(self, stream, painter, stages=()):
        self.stream, self.painter = stream, painter
        self.names = [stage.name for stage in stages]
        self.headed = False

    def report(self, event):
        if event.kind == BEGIN and event.code in self.names:
            self._heading(self.names.index(event.code) + 1, event.code)
        elif event.kind == LINE:
            print(event_lines(event), file=self.stream, flush=True)

    def _heading(self, number, name):
        heading = paint_or_plain(self.painter, [[(printable(HEADING % (number, len(self.names), name)), "heading")]])
        print(("\n" if self.headed else "") + heading, file=self.stream, flush=True)
        self.headed = True
# --- end MVP ---
