"""
The live grant (P253, #265): one yes the person types in their own terminal for one board and a time limit (D12), after
one look at that board (D13). A later call finds the grant with no contact with the board.

A library: grant.py only parses arguments, calls `GrantService` and prints. board_live.py (P247, #267) checks the grant
before a live try, and P242 (#249) reuses the same record.

    Grant             the grant as the store keeps it: the board's MAC and token, who said yes, when, until when.
    GrantStore        reads and writes the store's grants place, one file per board by its MAC.
    GrantCheckResult  whether the board on USB has a grant now, and `why` not.
    GrantService      issues a grant after the look and the yes, and checks one with `mpremote devs` only.
    StandingConsentStrategy   the yes a valid deploy grant gives deploy.py (P242, #249), in place of a yes typed per run.

Two scopes (P242): a live grant lets Claude run code on the board (`grants/<mac>.json`); a deploy grant lets Claude erase
it and write a passed image (`grants/<mac>-deploy.json`). Each reads only its own file, so one never opens the other.

How a later call knows the board with no look: on the ESP32-C6's built-in USB-Serial/JTAG, `mpremote devs` lists the
base MAC as the USB serial (bench P228). `devs` never opens the port, so the gadget keeps running. The grant is issued
only when that serial equals the MAC esptool read, so a board whose serial is not its MAC never gets one.
"""

import datetime
import getpass
import json
from collections import namedtuple
from pathlib import Path

import board_codes
import board_look
import store
from zone_time import say_in_local_zone, stamp  # the grant's times (P401 moved them out, to break an import cycle)
from deploy_gate import ConsentStrategy, GateClosedError, format_rerun_line
from outcomes import EXIT_COULD_NOT_RUN, EXIT_PROBLEMS

#: What a grant allows. A file with no `scope` (written before P242) is a live grant.
SCOPE_LIVE, SCOPE_DEPLOY = "live", "deploy"
SCOPES = (SCOPE_LIVE, SCOPE_DEPLOY)


class Grant(namedtuple("Grant", "mac board_token granted_by granted_at expires_at scope", defaults=(SCOPE_LIVE,))):
    """Value: the grant as the store keeps it. The times are ISO 8601 with the zone: the machine's zone since P291, UTC
    before."""

    __slots__ = ()

    def why_not_valid(self, now):
        """The WHY_ code that says this grant does not hold at `now` (a time with its zone), or None when it
        holds: a time of it is not a time or has no zone, it was given in the future, it lasts more than a day, or it
        has passed."""
        try:
            since = datetime.datetime.fromisoformat(self.granted_at)
            until = datetime.datetime.fromisoformat(self.expires_at)
            if since.tzinfo is None or until.tzinfo is None or now.tzinfo is None:
                return WHY_NO_ZONE
            if since > now or until - since > datetime.timedelta(minutes=MAX_MINUTES):
                return WHY_NOT_A_GRANT
            return WHY_EXPIRED if now >= until else None
        except (TypeError, ValueError):
            return WHY_NOT_A_GRANT


#: `consent` is the ConsentStrategy deploy.py uses, `why` the WHY_ code that says why it is not the standing yes (None
#: when it is).
DeployConsentResult = namedtuple("DeployConsentResult", "consent why")
#: `granted` is True or False, `grant` the Grant found or None, `why` one of the WHY_ codes or None.
GrantCheckResult = namedtuple("GrantCheckResult", "granted grant why")
#: The longest grant, in minutes: one day. No D names a limit; this one keeps the time a date can hold (P253's review).
MAX_MINUTES = 24 * 60

WHY_NO_GRANT, WHY_EXPIRED, WHY_NO_ZONE, WHY_NOT_A_GRANT = "no grant", "expired", "no zone", "not a grant"
WHY_SERIAL_NOT_MAC, WHY_NO_MAC, WHY_BAD_MINUTES, WHY_ANSWERED_NO = "serial not mac", "no mac", "bad minutes", "answered no"
#: Why a deploy asks for a typed yes though a deploy grant may exist: the look is no match, its last deploy was not
#: checked, --ignore-older-runs or --no-simulation.
WHY_LOOK_NOT_MATCH, WHY_IGNORE_OLDER_RUNS = "look not a match", "ignore older runs"
WHY_LAST_DEPLOY_NOT_CHECKED = "last deploy not checked"
WHY_NO_SIMULATION = "no simulation"
WHY_BAD_SCOPE = "bad scope"
#: grant.py --check --json's `why` when it could not look: no board, two boards, a port not listed, no mpremote.
WHY_COULD_NOT_RUN = "could not run"
#: The command a person types for a grant, by grant.py's whole path, so it runs from any folder (P283).
GRANT_COMMAND = format_rerun_line(Path(__file__).resolve().parent / "grant.py", ["--minutes", "N"])
#: The questions a person answers when they give a grant: %s are the MAC, the token and the minutes.
LIVE_QUESTION = "let Claude run code on the board %s (token %s) for %d minutes from your yes?"
DEPLOY_QUESTION = ("let Claude erase ALL of the flash of the board %s (token %s) and write any passed image of any "
                   "project, with no yes from you for each deploy, for %d minutes from your yes?")
#: The command a person types for a deploy grant, by grant.py's whole path (P283).
DEPLOY_GRANT_COMMAND = format_rerun_line(Path(__file__).resolve().parent / "grant.py",
                                         ["--scope", SCOPE_DEPLOY, "--minutes", "N"])
#: The sentence a person reads for each code.
MESSAGE_FOR = {
    WHY_NO_GRANT: "no grant for this board: the person runs %s in their own terminal" % GRANT_COMMAND,
    WHY_EXPIRED: "the grant for this board ended: the person runs %s again" % GRANT_COMMAND,
    WHY_NO_ZONE: "the grant's time has no zone, so it was not trusted: the person runs %s again" % GRANT_COMMAND,
    WHY_NOT_A_GRANT: "the store's grant file for this board is not a grant for it, so it was not trusted",
    WHY_SERIAL_NOT_MAC: "the board's USB serial is not its MAC, so a later call could not tell it is the same board. "
                        "The grant works only on a board with a built-in USB port, like the ESP32-C6's",
    WHY_NO_MAC: "the board's MAC could not be read",
    WHY_BAD_MINUTES: "--minutes must be a whole number from 1 to %d" % MAX_MINUTES,
    WHY_BAD_SCOPE: "--scope must be %s" % " or ".join(SCOPES),
    WHY_ANSWERED_NO: "no grant: the person answered no",
    WHY_LOOK_NOT_MATCH: "the look is not a match (a warning, an unknown field or a stop), so a deploy grant does not "
                        "cover this deploy: the person types yes",
    WHY_LAST_DEPLOY_NOT_CHECKED: "spark could not check its record of this board's last deploy, so a deploy grant does "
                                 "not cover this deploy: the person types yes",
    WHY_IGNORE_OLDER_RUNS: "--ignore-older-runs is never covered by a deploy grant: the person types yes",
    WHY_NO_SIMULATION: "--no-simulation is never covered by a deploy grant: the person types yes",
}
#: The sentences for a missing, ended or untrusted deploy grant: they name the deploy grant's command, not the live one.
DEPLOY_MESSAGE_FOR = {
    WHY_NO_GRANT: "no deploy grant for this board: the person runs %s in their own terminal" % DEPLOY_GRANT_COMMAND,
    WHY_EXPIRED: "the deploy grant for this board ended: the person runs %s again" % DEPLOY_GRANT_COMMAND,
    WHY_NO_ZONE: "the deploy grant's time has no zone, so it was not trusted: the person runs %s again"
                 % DEPLOY_GRANT_COMMAND,
    WHY_NOT_A_GRANT: "the store's deploy grant file for this board is not a deploy grant for it, so it was not trusted"
                     ": the person runs %s again" % DEPLOY_GRANT_COMMAND,
}
#: The board_codes code for each WHY_ word that a GrantRefusedError is raised with (P433).
CODE_FOR_WHY = {WHY_NOT_A_GRANT: board_codes.NOT_A_GRANT, WHY_BAD_MINUTES: board_codes.BAD_MINUTES,
                WHY_BAD_SCOPE: board_codes.BAD_SCOPE, WHY_NO_MAC: board_codes.NO_MAC,
                WHY_SERIAL_NOT_MAC: board_codes.SERIAL_NOT_MAC, WHY_ANSWERED_NO: board_codes.ANSWERED_NO}
#: The exit code for a code that is no refusal but a run that could not finish: 2, as outcomes.py says.
COULD_NOT_RUN_WHYS = (WHY_NO_MAC, WHY_BAD_MINUTES, WHY_BAD_SCOPE)


def mac_key(mac):
    """The MAC as the grant compares it: lower case, with no space around it."""
    return (mac or "").strip().lower()


def read_local_time():
    """Now, in the machine's zone, with the zone (P291): the zone a person reads, and a stored time carries it."""
    return datetime.datetime.now().astimezone()



class GrantRefusedError(GateClosedError):
    """Error: no grant, for one of the WHY_ codes. Its exit code is 1, a refusal, as the deploy gate's stops are, or 2
    for a code in COULD_NOT_RUN_WHYS."""

    def __init__(self, why):
        super().__init__(MESSAGE_FOR[why], EXIT_COULD_NOT_RUN if why in COULD_NOT_RUN_WHYS else EXIT_PROBLEMS,
                         reason=CODE_FOR_WHY[why])
        self.why = why


class GrantStore:
    """Reads and writes the store's grants place: one JSON file per board and scope, named by its MAC with dashes, for
    example grants/8c-bf-ea-cc-97-70.json (live) and grants/8c-bf-ea-cc-97-70-deploy.json (deploy). A new grant replaces
    the old one of its scope. Deleting the file ends the grant."""

    @staticmethod
    def key(mac, scope=SCOPE_LIVE):
        return store.slug(mac_key(mac)) + ("-deploy" if scope == SCOPE_DEPLOY else "")

    def save(self, grant):
        """Keep `grant`. Returns the file's path."""
        with store.locked():
            store.write_json("grants", self.key(grant.mac, grant.scope), grant._asdict())
        return store.place("grants") / (self.key(grant.mac, grant.scope) + ".json")

    def find(self, mac, scope=SCOPE_LIVE):
        """The Grant of this `scope` kept for this MAC, or None when there is none. GrantRefusedError(WHY_NOT_A_GRANT)
        when the file is there but holds no grant of this scope for this MAC."""
        path = store.place("grants") / (self.key(mac, scope) + ".json")
        if not mac_key(mac) or not path.is_file():
            return None
        try:
            grant = Grant(**json.loads(path.read_text()))
        except (OSError, ValueError, TypeError):
            raise GrantRefusedError(WHY_NOT_A_GRANT)
        if not isinstance(grant.mac, str) or grant.scope != scope or mac_key(grant.mac) != mac_key(mac) \
                or grant.board_token != board_look.board_token(mac_key(mac)):
            raise GrantRefusedError(WHY_NOT_A_GRANT)
        return grant


class StandingConsentStrategy(ConsentStrategy):
    """Strategy: the yes the person gave once in their own terminal, kept as a valid deploy `grant`. It answers yes to
    the deploy's question without asking, while the grant holds at `now()` (a time with its zone); once it ended, it raises
    GateClosedError, so the erase never runs on a stale yes."""

    def __init__(self, grant, now=read_local_time):
        self.grant, self.now = grant, now

    @property
    def who(self):
        return "standing yes typed by %s at %s, until %s" % (self.grant.granted_by, say_in_local_zone(
            self.grant.granted_at), say_in_local_zone(self.grant.expires_at))

    def require_ready(self):
        if self.grant.why_not_valid(self.now()):
            raise GateClosedError("the deploy grant ended before the erase. not flashed. The person runs %s again"
                                  % DEPLOY_GRANT_COMMAND, reason=board_codes.GRANT_ENDED)

    def ask(self, question):
        self.require_ready()
        return True


def grant_may_cover(report, evidence):
    """True when a deploy grant can answer for this deploy: the look matched, its last deploy was checked, and the
    evidence allows a grant. consent_for_deploy refuses in the same cases, and deploy.py offers the grant line only here."""
    return (report.verdict == board_look.VERDICT_MATCH and not report.last_deploy_not_checked()
            and evidence.grant_refusal is None)


class GrantService:
    """Service: issues a grant after one look and the person's yes, and checks the grant of the board on USB.
    `finder` is a board_look.PortFinder, `reader` a board_look.BoardReader, `now` returns the time with its zone. A service that
    only builds the deploy consent (`consent_for_deploy`) needs neither finder nor reader, and `issue` and `check` need
    them."""

    def __init__(self, finder=None, reader=None, grants=None, now=read_local_time):
        self.finder, self.reader, self.grants, self.now = finder, reader, grants or GrantStore(), now

    def issue(self, port, minutes, consent, before_look=lambda: None, script="grant.py", scope=SCOPE_LIVE):
        """The Grant of `scope` kept for the board on USB (or on `port`) for `minutes` from the yes, after one look and
        a yes from `consent`. `before_look` runs just before the board restarts. Raises GrantRefusedError, board_look.LookStop, or
        GateClosedError when consent cannot ask. It saves nothing then."""
        if not 1 <= minutes <= MAX_MINUTES:
            raise GrantRefusedError(WHY_BAD_MINUTES)
        if scope not in SCOPES:
            raise GrantRefusedError(WHY_BAD_SCOPE)
        board = self.finder.require_one_board(script, port)
        consent.require_ready()
        before_look()
        mac = mac_key(self.reader.read(board.device).mac)
        if not mac:
            raise GrantRefusedError(WHY_NO_MAC)
        if scope == SCOPE_LIVE and mac_key(board.serial) != mac:  # a deploy grant is found by the look's MAC instead
            raise GrantRefusedError(WHY_SERIAL_NOT_MAC)
        token = board_look.board_token(mac)
        question = (DEPLOY_QUESTION if scope == SCOPE_DEPLOY else LIVE_QUESTION) % (mac, token, minutes)
        if not consent.ask(question):
            raise GrantRefusedError(WHY_ANSWERED_NO)
        now = self.now()
        grant = Grant(mac, token, getpass.getuser(), stamp(now), stamp(now + datetime.timedelta(minutes=minutes)), scope)
        self.grants.save(grant)
        return grant

    def check(self, port=None, script="grant.py"):
        """A GrantCheckResult for the board on USB (or on `port`). It runs only `mpremote devs`: no contact with the
        board. board_look.LookStop when the board cannot be found."""
        board = self.finder.require_one_board(script, port)
        try:
            grant = self.grants.find(board.serial)
        except GrantRefusedError as refused:
            return GrantCheckResult(False, None, refused.why)
        if grant is None:
            return GrantCheckResult(False, None, WHY_NO_GRANT)
        why = grant.why_not_valid(self.now())
        return GrantCheckResult(why is None, grant, why)

    def consent_for_deploy(self, report, evidence, fallback):
        """A DeployConsentResult for deploy.py: the StandingConsentStrategy when the look `report` is a match, deploy
        the `evidence` (an ImageEvidence) has no `grant_refusal` and a deploy grant holds for the look's MAC; else `fallback` (the terminal) and the
        WHY_ code that says why. A grant file that cannot be trusted is no grant."""
        try:
            grant = self.grants.find(report.reading.mac, SCOPE_DEPLOY)
        except GrantRefusedError as refused:
            return DeployConsentResult(fallback, refused.why)
        if grant is None:
            return DeployConsentResult(fallback, WHY_NO_GRANT)
        if report.verdict != board_look.VERDICT_MATCH:
            return DeployConsentResult(fallback, WHY_LOOK_NOT_MATCH)
        if report.last_deploy_not_checked():
            return DeployConsentResult(fallback, WHY_LAST_DEPLOY_NOT_CHECKED)
        if evidence.grant_refusal:
            return DeployConsentResult(fallback, evidence.grant_refusal)
        why = grant.why_not_valid(self.now())
        if why:
            return DeployConsentResult(fallback, why)
        return DeployConsentResult(StandingConsentStrategy(grant, self.now), None)
