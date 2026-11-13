"""
The gate before deploy.py erases a board (P219): the look found no stop, the token is this board's and this image's,
and there is a yes. It is the only way to the erase (D8).

The yes is a strategy (`ConsentStrategy`), the `ReplyStrategy` that answers a yes or no question (`spark.core.replies`,
P737 R1). `TerminalConsentStrategy` asks in a real terminal only: a pipe, a heredoc or Claude Code's `!` is none, so the
person runs the line in their own terminal window.
`board_grant.StandingConsentStrategy` is the yes the person gave once, as a deploy grant (P242).
`RelayedConsentStrategy` is a yes that another program collected (an MCP or web yes, D19; P675): it makes a live grant
only, and it never opens the erase (decision 6 of the refactor plan, the PO's to change).
"""

import abc
import getpass

from spark.bench import board_codes
from spark.records.store import format_rerun_line  # noqa: F401  (board_grant, grant and deploy take it from here)
from spark.core import outcomes
from spark.core.outcomes import EXIT_COULD_NOT_RUN, EXIT_PROBLEMS
from spark.core.replies import AGENT, TYPED_BY, YES_NO, Reply, ReplyStrategy, Terminal
from spark.core.text_guards import printable

#: How the store's record says a yes was given in a terminal: %s is the person's login name.
NO_TERMINAL = "no terminal to ask you in. Run this line in your own terminal window (Claude Code's ! has none):\n  %s"

#: What an agent does next (P213), for a GateClosedError: `deploy.py`'s `--json` turns it into a step.
NEXT_DEPLOY, NEXT_LOOK = "deploy", "look"
#: The kinds of a yes: typed in a terminal, a standing deploy grant, or relayed by another program (never past the gate).
TYPED, GRANT, RELAYED = "typed", "grant", "relayed"
#: Why the gate refuses a yes that cannot open the erase (P675).
RELAYED_REFUSED = ("a yes given through another program cannot open the erase. Type yes in your own terminal, or give a "
                   "deploy grant there. not flashed.")


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


class ConsentStrategy(ReplyStrategy):
    """Strategy: how the person says yes to a question. A subclass supplies `ask`, which returns True for yes, `who`, the
    phrase that tells the store's record whose yes it was, and `yes_kind`, TYPED, GRANT or RELAYED (P655, P675).
    `opens_erase` says whether this yes can open the erase or make a deploy grant. It is False unless a subclass sets it,
    so a new kind stays shut until it chooses. The gate trusts the strategy's own attribute, so it guards against a
    frontend's mistake, not against code in the same process. As a `ReplyStrategy`, `reply` answers a YES_NO Question
    asked of a person, so a frontend can hand a consent as `OutsideWorld.replies` (P737 R1)."""

    opens_erase = False

    @property
    @abc.abstractmethod
    def yes_kind(self):
        """TYPED, GRANT or RELAYED: the kind of yes. A subclass sets it as a class attribute."""

    @property
    @abc.abstractmethod
    def who(self):
        """Who said yes, as a phrase for the store's record, for example "typed in a terminal by ada"."""

    @abc.abstractmethod
    def ask(self, question):
        """True when the person said yes to `question`. It may raise GateClosedError when it cannot ask."""

    def reply(self, question):
        """A YES_NO Question asked of a person: its Reply, `ask(question.text)` as the value and `who` as `answered_by`
        (P737 R1). Any other kind, or a question asked of AGENT, is None, so the question stays open: a consent asks a
        person for a yes or no only. A GateClosedError from `ask` propagates."""
        if question.kind != YES_NO or question.asked_of == AGENT:
            return None
        return Reply(question.key, bool(self.ask(question.text)), self.who)

    def require_ready(self):
        """Raises GateClosedError when it could not ask now, so a caller stops before it touches the board. The default
        can always ask."""

    def granted_by(self, user_name):
        """The name a grant keeps as `granted_by`: by default `user_name()`, the login of the person at this machine."""
        return user_name()


class TerminalConsentStrategy(ConsentStrategy):
    """Strategy: `yes` typed in a real terminal. With no terminal, GateClosedError gives `line`, the command to run
    in one. Anything but `yes` is a no, a closed input (Ctrl-C, Ctrl-D) too: the gate stays shut and says so."""

    yes_kind = TYPED
    opens_erase = True

    def __init__(self, line, stdin=None, stdout=None, user_name=getpass.getuser, mask=None):
        self.line, self.terminal = line, Terminal(stdin, stdout, mask)  # P677: `mask` is the run's Privacy, so the question shows no home path
        self.user_name = user_name  # who types the yes: a test gives a name

    @property
    def who(self):
        return TYPED_BY % self.user_name()

    def require_ready(self):
        if not self.terminal.live:
            raise GateClosedError(NO_TERMINAL % self.line, next_op=NEXT_DEPLOY, reason=board_codes.NO_TERMINAL)

    def ask(self, question):
        self.require_ready()
        return self.terminal.ask("%s type yes to go on: " % question) == "yes"  # P423: the one place a person types yes


# --- MVP ---
class RelayedConsentStrategy(ConsentStrategy):
    """Strategy: a yes that another program collected (P675). `ask_in_program(question)` takes the question text and
    asks the person in the program, as MCP's elicitation asks through the client (modelcontextprotocol.io, spec
    2025-06-18). Only an exact True is a yes. `person` and `program` name who said yes and through what. A frontend
    passes `make_consent=lambda line: RelayedConsentStrategy(person, program, ask)` to `build_outside_world`, and
    `line` goes unused. It makes a live grant only: `opens_erase` is False, so the deploy gate and a deploy grant
    refuse it. A blank name is a defect in the frontend: ValueError."""

    yes_kind = RELAYED
    opens_erase = False

    def __init__(self, person, program, ask_in_program):
        for name in (person, program):
            if not isinstance(name, str) or not name.strip():
                raise ValueError("a relayed yes names its person and its program, got %r" % (name,))
        self.person, self.program, self.ask_in_program = printable(person), printable(program), ask_in_program

    @property
    def who(self):
        return "given through %s by %s" % (self.program, self.person)

    def granted_by(self, user_name):
        return self.who  # the login at this machine is not who said yes

    def ask(self, question):
        return self.ask_in_program(question) is True
# --- end MVP ---


# --- MVP ---
def say_last_deploy_in_question(last):
    """The words the deploy question puts in its erase sentence, for `last`, a deploy_record_store.LastDeploy.
    `board_look.say_last_deploy` says the same deploy in the look's words."""
    if last.state == outcomes.RECORDED:
        return printable("spark's store record names %s as its last deploy here, %s, %s%s" % (last.project, last.time_said(), last.verdict,
                                                                                         last.banner_said()))
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
    if not consent.opens_erase:  # P675: after the token checks, so the line to rerun holds a token that passes them
        raise GateClosedError(RELAYED_REFUSED, next_op=NEXT_DEPLOY, reason=board_codes.RELAYED_YES_REFUSED)
    accepted = report.warnings + ["%s unknown (%s)" % each for each in report.unknown.items()]
    question = "erase ALL of this board's flash (%s) and write %s?" % (say_last_deploy_in_question(report.last_deploy), image)
    if accepted:
        question = "you accept: %s. %s" % ("; ".join(accepted), question)
    for caveat in reversed(caveats):
        question = "%s. %s" % (caveat, question)
    if not consent.ask(question):
        raise GateClosedError("not flashed: you answered no.", reason=board_codes.ANSWERED_NO)
