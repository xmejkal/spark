"""
The gate before deploy.py erases a board (P219): the look found no stop, the token is this board's and this image's,
and the person says yes. It is the only way to the erase (D8).

The yes is a strategy (`Consent`). `TerminalConsent` asks in a real terminal only: a pipe, a heredoc or Claude Code's
`!` is none, so the person runs the line in their own terminal window. A second way to say yes (an MCP or web yes,
D19) is another Consent.
"""

import sys

from outcomes import EXIT_COULD_NOT_RUN, EXIT_PROBLEMS

NO_TERMINAL = "no terminal to ask you in. Run this line in your own terminal window (Claude Code's ! has none):\n  %s"


class Closed(Exception):
    """Why the gate stays shut, and the exit code: 1 for a stop the look found, 2 for everything else."""

    def __init__(self, why, code=EXIT_COULD_NOT_RUN):
        super().__init__(why)
        self.code = code


class Consent:
    """How the person says yes to a question. True is yes."""

    def ask(self, question):
        raise NotImplementedError


class TerminalConsent(Consent):
    """`yes` typed in a real terminal. With no terminal, Closed gives `line`, the command to run in one."""

    def __init__(self, line, stdin=None, stdout=None):
        self.line, self.stdin, self.stdout = line, stdin or sys.stdin, stdout or sys.stdout

    def ask(self, question):
        if not (self.stdin.isatty() and self.stdout.isatty()):
            raise Closed(NO_TERMINAL % self.line)
        self.stdout.write("%s type yes to go on: " % question)
        self.stdout.flush()
        return self.stdin.readline().strip() == "yes"


def gate_open(report, token, consent, image):
    """Returns when the person said yes to erasing this board for `image`. Closed says why not."""
    if report.stops:
        raise Closed("%s. not flashed." % "; ".join(report.stops), EXIT_PROBLEMS)
    if not token:
        raise Closed("run look.py first, then deploy.py --token <token>.")
    mine = report.token()
    if not mine:
        raise Closed("no token: %s. not flashed." % report.no_token_reason())
    theirs = (token.split("-", 1) + [""])[:2]
    changed = [what for what, given, read in zip(("the board", "the image"), theirs, mine.split("-")) if given != read]
    if changed:
        raise Closed("%s changed since the look: run look.py again." % " and ".join(changed))
    accepted = report.warnings + ["%s unknown (%s)" % each for each in report.unknown.items()]
    question = "erase ALL of this board's flash and write %s?" % image
    if accepted:
        question = "you accept: %s. %s" % ("; ".join(accepted), question)
    if not consent.ask(question):
        raise Closed("not flashed: you answered no.")
