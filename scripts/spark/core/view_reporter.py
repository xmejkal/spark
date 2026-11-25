"""
The text view of a run's events (P478): what a person reads on stdout while a CLI runs without --json. `TextViewReporter`
prints each LINE as `events.TerminalReporter` prints it, and a heading `[n/N] name` when a stage of the Operation's
`stages` begins, painted by the run's painter (P1032). A WAIT prints its line too, and its spinner draws under it until
the next event (slice 2). Under --json the events stay `TerminalReporter`'s, on stderr.
"""

from spark.core.events import BEGIN, LINE, WAIT, Reporter, event_lines
from spark.core.renderers import paint_or_plain
from spark.core.spinner import NO_SPINNER
from spark.core.text_guards import printable

# --- MVP ---
#: The heading of the nth of N stages: presentation, so the view makes it from the stage's name, never the Event.
HEADING = "[%d/%d] %s"


class TextViewReporter(Reporter):
    """Strategy: the text view's Reporter (P478). A BEGIN whose code is the name of the nth of the N `stages` prints the
    heading `[n/N] name` through `painter`, one blank line before it unless it is the first. A LINE or a WAIT prints at
    once as `event_lines` gives it, plain, and a WAIT then starts `spinner` (slice 2: NO_SPINNER draws nothing), which
    every next event and `finish` stop first. Any other kind prints nothing. It decides on kind and code, never on text."""

    def __init__(self, stream, painter, stages=(), spinner=NO_SPINNER):
        self.stream, self.painter, self.spinner = stream, painter, spinner
        self.names = [stage.name for stage in stages]
        self.headed = False

    def report(self, event):
        self.spinner.stop()  # the row goes before anything else prints
        if event.kind == BEGIN and event.code in self.names:
            self._heading(self.names.index(event.code) + 1, event.code)
        elif event.kind in (LINE, WAIT):
            print(event_lines(event), file=self.stream, flush=True)
        if event.kind == WAIT:
            self.spinner.start()

    def finish(self):
        self.spinner.stop()  # the run is over: no row and no hidden cursor stay

    def _heading(self, number, name):
        heading = paint_or_plain(self.painter, [[(printable(HEADING % (number, len(self.names), name)), "heading")]])
        print(("\n" if self.headed else "") + heading, file=self.stream, flush=True)
        self.headed = True
# --- end MVP ---
