"""
The live grant (P253, #265): one yes the person types in their own terminal for one board and a time limit (D12), after
one look at that board (D13). A later call finds the grant with no contact with the board.

A library: grant.py only parses arguments, calls `GrantService` and prints. board_live.py (P247, #267) checks the grant
before a live try, and P242 (#249) reuses the same record.

    Grant             the grant as the store keeps it: the board's MAC and token, who said yes, when, until when.
    GrantStore        reads and writes the store's grants place, one file per board by its MAC.
    GrantCheckResult  whether the board on USB has a grant now, and `why` not.
    GrantService      issues a grant after the look and the yes, and checks one with `mpremote devs` only.

How a later call knows the board with no look: on the ESP32-C6's built-in USB-Serial/JTAG, `mpremote devs` lists the
base MAC as the USB serial (bench P228). `devs` never opens the port, so the gadget keeps running. The grant is issued
only when that serial equals the MAC esptool read, so a board whose serial is not its MAC never gets one.
"""

import datetime
import getpass
import json
from collections import namedtuple
from pathlib import Path

import board_look
import store
from deploy_gate import GateClosedError, format_rerun_line
from outcomes import EXIT_COULD_NOT_RUN, EXIT_PROBLEMS

#: The grant as the store keeps it. The times are ISO 8601 in UTC, with the zone.
Grant = namedtuple("Grant", "mac board_token granted_by granted_at expires_at")
#: `granted` is True or False, `grant` the Grant found or None, `why` one of the WHY_ codes or None.
GrantCheckResult = namedtuple("GrantCheckResult", "granted grant why")
#: The longest grant, in minutes: one day. No D names a limit; this one keeps the time a date can hold (P253's review).
MAX_MINUTES = 24 * 60

WHY_NO_GRANT, WHY_EXPIRED, WHY_NO_ZONE, WHY_NOT_A_GRANT = "no grant", "expired", "no zone", "not a grant"
WHY_SERIAL_NOT_MAC, WHY_NO_MAC, WHY_BAD_MINUTES, WHY_ANSWERED_NO = "serial not mac", "no mac", "bad minutes", "answered no"
#: grant.py --check --json's `why` when it could not look: no board, two boards, a port not listed, no mpremote.
WHY_COULD_NOT_RUN = "could not run"
#: The command a person types for a grant, by grant.py's whole path, so it runs from any folder (P283).
GRANT_COMMAND = format_rerun_line(Path(__file__).resolve().parent / "grant.py", ["--minutes", "N"])
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
    WHY_ANSWERED_NO: "no grant: the person answered no",
}
#: The exit code for a code that is no refusal but a run that could not finish: 2, as outcomes.py says.
COULD_NOT_RUN_WHYS = (WHY_NO_MAC, WHY_BAD_MINUTES)


def mac_key(mac):
    """The MAC as the grant compares it: lower case, with no space around it."""
    return (mac or "").strip().lower()


def utc_now():
    """Now, in UTC with the zone."""
    return datetime.datetime.now(datetime.timezone.utc)


class GrantRefusedError(GateClosedError):
    """Error: no grant, for one of the WHY_ codes. Its exit code is 1, a refusal, as the deploy gate's stops are, or 2
    for a code in COULD_NOT_RUN_WHYS."""

    def __init__(self, why):
        super().__init__(MESSAGE_FOR[why], EXIT_COULD_NOT_RUN if why in COULD_NOT_RUN_WHYS else EXIT_PROBLEMS)
        self.why = why


class GrantStore:
    """Reads and writes the store's grants place: one JSON file per board, named by its MAC with dashes, for example
    grants/8c-bf-ea-cc-97-70.json. A new grant replaces the old one. Deleting the file ends the grant."""

    @staticmethod
    def key(mac):
        return store.slug(mac_key(mac))

    def save(self, grant):
        """Keep `grant`. Returns the file's path."""
        with store.locked():
            store.write_json("grants", self.key(grant.mac), grant._asdict())
        return store.place("grants") / (self.key(grant.mac) + ".json")

    def find(self, mac):
        """The Grant kept for this MAC, or None when there is none. GrantRefusedError(WHY_NOT_A_GRANT) when the file is
        there but holds no grant for this MAC."""
        path = store.place("grants") / (self.key(mac) + ".json")
        if not mac_key(mac) or not path.is_file():
            return None
        try:
            grant = Grant(**json.loads(path.read_text()))
        except (OSError, ValueError, TypeError):
            raise GrantRefusedError(WHY_NOT_A_GRANT)
        if mac_key(grant.mac) != mac_key(mac) or grant.board_token != board_look.board_token(mac_key(mac)):
            raise GrantRefusedError(WHY_NOT_A_GRANT)
        return grant


class GrantService:
    """Service: issues a grant after one look and the person's yes, and checks the grant of the board on USB.
    `finder` is a board_look.PortFinder, `reader` a board_look.BoardReader, `now` returns the time in UTC."""

    def __init__(self, finder, reader=None, grants=None, now=utc_now):
        self.finder, self.reader, self.grants, self.now = finder, reader, grants or GrantStore(), now

    def issue(self, port, minutes, consent, before_look=lambda: None, script="grant.py"):
        """The Grant kept for the board on USB (or on `port`) for `minutes` from the yes, after one look and a yes from
        `consent`. `before_look` runs just before the board restarts. Raises GrantRefusedError, board_look.LookStop, or
        GateClosedError when consent cannot ask. It saves nothing then."""
        if not 1 <= minutes <= MAX_MINUTES:
            raise GrantRefusedError(WHY_BAD_MINUTES)
        board = self.finder.require_one_board(script, port)
        consent.require_ready()
        before_look()
        mac = mac_key(self.reader.read(board.device).mac)
        if not mac:
            raise GrantRefusedError(WHY_NO_MAC)
        if mac_key(board.serial) != mac:
            raise GrantRefusedError(WHY_SERIAL_NOT_MAC)
        token = board_look.board_token(mac)
        if not consent.ask("let Claude run code on the board %s (token %s) for %d minutes from your yes?"
                           % (mac, token, minutes)):
            raise GrantRefusedError(WHY_ANSWERED_NO)
        now = self.now()
        grant = Grant(mac, token, getpass.getuser(), now.isoformat(timespec="seconds"),
                      (now + datetime.timedelta(minutes=minutes)).isoformat(timespec="seconds"))
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
        try:
            until = datetime.datetime.fromisoformat(grant.expires_at)
        except (TypeError, ValueError):
            return GrantCheckResult(False, grant, WHY_NOT_A_GRANT)
        if until.tzinfo is None:
            return GrantCheckResult(False, grant, WHY_NO_ZONE)
        now = self.now()
        if until - now > datetime.timedelta(minutes=MAX_MINUTES):
            return GrantCheckResult(False, grant, WHY_NOT_A_GRANT)
        if now >= until:
            return GrantCheckResult(False, grant, WHY_EXPIRED)
        return GrantCheckResult(True, grant, None)
