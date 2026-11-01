"""
The gate before deploy.py erases a board (P219): the look found no stop, the token is this board's and this image's,
and there is a yes. It is the only way to the erase (D8).

The yes is a strategy (`ConsentStrategy`). `TerminalConsentStrategy` asks in a real terminal only: a pipe, a
heredoc or Claude Code's `!` is none, so the person runs the line in their own terminal window.
`board_grant.StandingConsentStrategy` is the yes the person gave once, as a deploy grant (P242). Another way to say
yes (an MCP or web yes, D19) is another ConsentStrategy.
"""

import abc
import getpass
import sys

import board_codes
from store import format_rerun_line  # noqa: F401  (board_grant, grant and deploy take it from here)
from spark.core import outcomes
from spark.core.outcomes import EXIT_COULD_NOT_RUN, EXIT_PROBLEMS
from spark.core.text_guards import guard_lines, printable

#: How the store's record says a yes was given in a terminal: %s is the person's login name.
TYPED_BY = "typed in a terminal by %s"
NO_TERMINAL = "no terminal to ask you in. Run this line in your own terminal window (Claude Code's ! has none):\n  %s"

#: What an agent does next (P213), for a GateClosedError: `deploy.py`'s `--json` turns it into a step.
NEXT_DEPLOY, NEXT_LOOK = "deploy", "look"


# --- MVP ---
class GateClosedError(Exception):
    """Error: why the gate stays shut, and `code`, the exit code: 1 for a stop the look found, 2 for everything else.
    `reason` is the board_codes code that names why, a required keyword, so no raise site goes without one (P433).
    `next_op` is NEXT_DEPLOY (the person runs the deploy in their own terminal), NEXT_LOOK (the look is stale or missing)
    or None (nothing to do but read the sentence)."""

    def __init__(self, why, code=EXIT_COULD_NOT_RUN, next_op=None, *, reason):
        super().__init__(why)
        self.code = code
        self.next_op = next_op
        self.reason = reason
# --- end MVP ---


class ConsentStrategy(abc.ABC):
    """Strategy: how the person says yes to a question. A subclass supplies `ask`, which returns True for yes, and
    `who`, the phrase that tells the store's record whose yes it was."""

    @property
    @abc.abstractmethod
    def who(self):
        """Who said yes, as a phrase for the store's record, for example "typed in a terminal by ada"."""

    @abc.abstractmethod
    def ask(self, question):
        """True when the person said yes to `question`. It may raise GateClosedError when it cannot ask."""

    def require_ready(self):
        """Raises GateClosedError when it could not ask now, so a caller stops before it touches the board. The default
        can always ask."""


class TerminalConsentStrategy(ConsentStrategy):
    """Strategy: `yes` typed in a real terminal. With no terminal, GateClosedError gives `line`, the command to run
    in one."""

    def __init__(self, line, stdin=None, stdout=None, user_name=getpass.getuser):
        self.line, self.stdin, self.stdout = line, stdin or sys.stdin, stdout or sys.stdout
        self.user_name = user_name  # who types the yes: a test gives a name

    @property
    def who(self):
        return TYPED_BY % self.user_name()

    def require_ready(self):
        if not (self.stdin.isatty() and self.stdout.isatty()):
            raise GateClosedError(NO_TERMINAL % self.line, next_op=NEXT_DEPLOY, reason=board_codes.NO_TERMINAL)

    def ask(self, question):
        self.require_ready()
        self.stdout.write("%s type yes to go on: " % guard_lines(question))  # P423: the one place a person types yes
        self.stdout.flush()
        return self.stdin.readline().strip() == "yes"


# --- MVP ---
def say_last_deploy_in_question(last):
    """The words the deploy question puts in its erase sentence, for `last`, a deploy_record_store.LastDeploy.
    `board_look.say_last_deploy` says the same deploy in the look's words."""
    if last.state == outcomes.RECORDED:
        return printable("spark's store record names %s as its last deploy here, %s, %s" % (last.project, last.time_said(), last.verdict))
    if last.state == outcomes.NONE_RECORDED:
        return "spark's store record names no deploy here"
    return "spark did not read its record of this board: %s" % last.why
# --- end MVP ---


def require_open_gate(report, token, consent, image, caveats):
    """Returns None when the person said yes to erasing this board for `image`. Raises GateClosedError, which says why
    not. It never erases or writes. The `caveats` (LookReport.question_caveats) come first in the question."""
    if report.stops:
        raise GateClosedError("%s. not flashed." % "; ".join(stop.sentence for stop in report.stops), EXIT_PROBLEMS,
                              reason=report.stops[0].code)  # with two stops, the first one's code
    if not token:
        raise GateClosedError("run look.py first, then deploy.py --token <token>.", next_op=NEXT_LOOK,
                              reason=board_codes.TOKEN_MISSING)
    mine = report.token()
    if not mine:
        why = report.no_token_reason()
        raise GateClosedError("no token: %s. not flashed." % why.sentence, reason=why.code)
    theirs = (token.split("-", 1) + [""])[:2]
    changed = [what for what, given, read in zip(("the board", "the image"), theirs, mine.split("-")) if given != read]
    if changed:
        raise GateClosedError("%s changed since the look: run look.py again." % " and ".join(changed), next_op=NEXT_LOOK,
                              reason=board_codes.TOKEN_STALE)
    accepted = report.warnings + ["%s unknown (%s)" % each for each in report.unknown.items()]
    question = "erase ALL of this board's flash (%s) and write %s?" % (say_last_deploy_in_question(report.last_deploy), image)
    if accepted:
        question = "you accept: %s. %s" % ("; ".join(accepted), question)
    for caveat in reversed(caveats):
        question = "%s. %s" % (caveat, question)
    if not consent.ask(question):
        raise GateClosedError("not flashed: you answered no.", reason=board_codes.ANSWERED_NO)
