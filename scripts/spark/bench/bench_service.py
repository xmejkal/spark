"""
Each board on USB with what spark's store holds of it (P919, #1301): the deploys by project, the last deploy, the projects
that keep it and its grants. It runs only `mpremote devs` (`PortFinder.nodes`), which opens no port, and reads the three
stores. It writes nothing and gives no verdict: each value comes from a record or from the list.

    identify        the board's MAC and the kept records that name it, by known_board's rules
    deploys_from    the deploys grouped by project, the newest name first
    ConnectedBoard  one board on USB and its store parts
    BenchResult     the boards, and the kept files that cannot be read
    BenchService    `show`: the list, then the stores for each board
"""

from collections import namedtuple

from spark.bench import board_codes
from spark.bench import board_console
from spark.bench import board_grant
from spark.bench import known_board
from spark.bench.board_look import boards_of, port_of
from spark.core import outcomes
from spark.records.deploy_record_store import DeployRecordStore, LastDeploy

# --- MVP ---
#: Where the MAC came from: the USB serial's MAC part, or the kept record that names the board.
USB_SERIAL, KEPT_BOARD = "usb_serial", "kept_board"
#: The parts of a board that can be left unchecked: the keys of its data.
KEPT_FOR, LAST_DEPLOY, DEPLOYS_FROM, GRANTS = "kept_for", "last_deploy", "deploys_from", "grants"
#: A grant row's state: it holds now, it ended, there is none, its file cannot be used, its time has no zone, not checked.
LIVE, ENDED, NONE, NOT_A_GRANT, NO_ZONE, NOT_CHECKED = "live", "ended", "none", "not_a_grant", "no_zone", "not_checked"
#: The state for each answer of `Grant.why_not_valid`.
STATE_FOR_WHY = {None: LIVE, board_grant.WHY_EXPIRED: ENDED, board_grant.WHY_NO_ZONE: NO_ZONE,
                 board_grant.WHY_NOT_A_GRANT: NOT_A_GRANT}

#: Value: who the board on USB is. `mac` in the stores' form or None, `mac_from` USB_SERIAL, KEPT_BOARD or None, `board`
#: the kept record's board id or None, `kept_for` the KnownBoards that name it ([] none, None not known).
Identity = namedtuple("Identity", "mac mac_from board kept_for")
#: Value: one part of a board that was not checked: its key, the board_codes code, and the file to repair or None.
Unchecked = namedtuple("Unchecked", "part code path", defaults=(None,))


class GrantRow(namedtuple("GrantRow", "scope state granted_by granted_at expires_at", defaults=(None,) * 3)):
    """Value: one grant of a board, by its scope: its state, and the grant's fields when the store holds one."""


def identify(row, kept):
    """The Identity of the board on the Port `row`, from KeptBoards `kept`, with known_board's rules only. Each kept record
    that `tell` calls SAME names it. Two such records with two MACs (two clones with one serial) name no MAC. Else the
    MAC is the serial's MAC part (`mac_part_of`). `kept_for` is None when a kept file cannot be read, or when the store
    keeps boards, no record names this one, and its serial is none or one its firmware set (`serial_trusted` is False),
    else the matches."""
    matches = [known for known in kept.records if known_board.tell(row, known) == known_board.SAME]
    untrusted = bool(kept.records) and not known_board.serial_trusted(row)
    kept_for = None if kept.unreadable or (untrusted and not matches) else matches
    if matches:
        one = len({known_board.comparable_key(known.mac) for known in matches}) == 1
        return Identity(matches[0].mac, KEPT_BOARD, matches[0].board, kept_for) if one else Identity(None, None, None, kept_for)
    mac = known_board.mac_part_of(row)
    return Identity(mac, USB_SERIAL if mac else None, None, kept_for)


def deploys_from(entries):
    """The deploys grouped by `project`: one {project, deploys, last} per name, the name of the newest entry first. A
    name's `last` is the `deployed` text of its last entry, as stored: no time is parsed or compared."""
    counts, last = {}, {}
    for each in entries:
        counts[each["project"]] = counts.get(each["project"], 0) + 1
        last[each["project"]] = each["deployed"]
    names = dict.fromkeys(each["project"] for each in reversed(entries))
    return [{"project": name, "deploys": counts[name], "last": last[name]} for name in names]


class ConnectedBoard(namedtuple("ConnectedBoard", "row identity last_deploy deploys_from grants unchecked")):
    """Value: one board on USB now. `row` is its board_look.Port, `identity` its Identity, `last_deploy` the LastDeploy,
    `deploys_from` the grouped deploys or None, `grants` its GrantRows (deploy, then live), `unchecked` its Unchecked parts."""

    def to_dict(self):
        mac, mac_from, board, kept_for = self.identity
        return {"device": self.row.device, "also_on": list(self.row.also_on),
                "usb_serial": self.row.serial if known_board.serial_key(self.row) else None, "usb_id": self.row.usb,
                "product": self.row.product, "mac": mac, "mac_from": mac_from, "board": board,
                KEPT_FOR: None if kept_for is None else [{"project": known.project, "at": known.at} for known in kept_for],
                LAST_DEPLOY: self.last_deploy.to_dict(), DEPLOYS_FROM: self.deploys_from,
                GRANTS: [grant._asdict() for grant in self.grants], "unchecked": [item.part for item in self.unchecked]}


class BenchResult(namedtuple("BenchResult", "boards kept_unreadable")):
    """Result: the ConnectedBoards in the order listed, and the path of each kept file that cannot be read (it can be any
    board's)."""


class BenchService:
    """
    Service: the boards on USB with their store parts. `finder` is a board_look.PortFinder (only `nodes` is asked), the
    stores are a KnownBoardStore, a DeployRecordStore and a GrantStore (None: the store's own), and `now` gives the time
    with its zone. `show` raises board_look.LookStopError when the list fails.
    """

    def __init__(self, finder, known=None, records=None, grants=None, now=board_console.SystemClock.now):
        self.finder, self.known, self.records = finder, known or known_board.KnownBoardStore(), records or DeployRecordStore()
        self.grants, self.now = grants or board_grant.GrantStore(), now

    def show(self):
        kept = self.known.read_all()
        return BenchResult([self._board(port_of(rows), kept) for rows in boards_of(self.finder.nodes())], kept.unreadable)

    def _board(self, row, kept):
        identity = identify(row, kept)
        unchecked = [] if identity.kept_for is not None else [
            Unchecked(KEPT_FOR, board_codes.KNOWN_BOARD_UNREADABLE if kept.unreadable else board_codes.CANNOT_TELL_BOARD)]
        mac = identity.mac
        if mac is None:
            unchecked += [Unchecked(part, board_codes.CANNOT_TELL_BOARD) for part in (LAST_DEPLOY, DEPLOYS_FROM, GRANTS)]
            last, grouped = LastDeploy(outcomes.NOT_CHECKED, why=board_codes.CODES[board_codes.CANNOT_TELL_BOARD]), None
        else:
            last, grouped, board, not_read = self._deploys(mac)
            unchecked += not_read
            identity = identity._replace(board=identity.board or board)
        grants = [self._grant(mac, board_grant.SCOPE_DEPLOY), self._grant(row.serial, board_grant.SCOPE_LIVE)]
        unchecked += [Unchecked(GRANTS, board_codes.NOT_A_GRANT, board_grant.GrantStore.path_of(key, grant.scope))
                      for key, grant in zip((mac, row.serial), grants) if grant.state == NOT_A_GRANT]
        return ConnectedBoard(row, identity, last, grouped, grants, unchecked)

    def _deploys(self, mac):
        """(the LastDeploy, the deploys by project or None, the deploy record's board id, the Unchecked parts) of `mac`."""
        last, deploys = self.records.read_last_deploy(mac), self.records.read_deploys(mac)
        grouped = {outcomes.RECORDED: deploys_from(deploys.entries), outcomes.NONE_RECORDED: []}.get(deploys.state)
        not_read = [Unchecked(part, board_codes.LAST_DEPLOY_NOT_CHECKED, self.records.find_path(mac))
                    for part, state in ((LAST_DEPLOY, last.state), (DEPLOYS_FROM, deploys.state)) if state == outcomes.NOT_CHECKED]
        return last, grouped, deploys.board, not_read

    def _grant(self, key, scope):
        """The GrantRow of `scope` kept under `key` (the MAC, or the USB serial for the live grant, as grant.py --check asks)."""
        if key is None:
            return GrantRow(scope, NOT_CHECKED)
        try:
            grant = self.grants.find(key, scope)
        except board_grant.GrantRefusedError:
            return GrantRow(scope, NOT_A_GRANT)
        if grant is None:
            return GrantRow(scope, NONE)
        return GrantRow(scope, STATE_FOR_WHY[grant.why_not_valid(self.now())], grant.granted_by, grant.granted_at, grant.expires_at)
# --- end MVP ---
