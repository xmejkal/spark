"""
The board log (P1043): the file `sim/runs/board/<moment>.log` that a deploy writes after a flash, beside the run logs.
A library. `BoardLog` is its text and `write_board_log` writes it. Moved here from `deploy_service` unchanged.
"""

import collections


class BoardLog(collections.namedtuple("BoardLog", "moment port image_sha256 facts_line verdict sentence heard simulation")):
    """Value: the facts of the board's log after a flash. `heard` is the console text, then what the board printed."""

    def text(self):
        """The log file's text."""
        return "# deploy %s on %s\nimage sha256: %s\nsimulation: %s\n%s\n%s: %s\n\n%s\n" % (
            self.moment.isoformat(timespec="seconds"), self.port, self.image_sha256, self.simulation, self.facts_line,
            self.verdict, self.sentence, self.heard)


def write_board_log(project, log):
    """The board's log (a BoardLog) in sim/runs/board/ beside the run logs, whose *.log glob does not reach it. Returns
    its path."""
    path = project / "sim" / "runs" / "board" / ("%s.log" % log.moment.strftime("%Y-%m-%dT%H-%M-%S"))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(log.text())
    return path
