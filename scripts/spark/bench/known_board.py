"""
The board that a project's looks read before, kept in the person's store (P865, #1231). A library for
`look_at_board.LookAtBoard`: before a read, `tell` compares the board on USB with the kept board, so that the look never
restarts another board without the person's yes. After a yes and a read, `KnownBoardStore.write` keeps the board.
`board_start` takes `comparable_key` from here.

    KnownBoard        the kept board: its MAC as esptool printed it, and the key of a USB serial that names it
    KnownBoardStore   one record per project folder, in the store's `known-boards/`
    tell              same, other, none or cannot_tell, before a read
    usb_key_to_keep   the key of the USB serial that a record may trust, after a read

Spark prints only the last two bytes of a MAC (`mac_ends`). The record holds the whole MAC, in the private store.
"""

import hashlib
import json
import re
from collections import namedtuple
from pathlib import Path

from spark.bench import board_codes
from spark.bench.board_look import NO_SERIAL, board_token
from spark.core.errors import SparkError
from spark.core.replies import PERSON, YES_NO, Question
from spark.records import store

# --- MVP ---
#: What `tell` says before a read: the kept board is on USB, another board is, no board is kept, or the serial cannot say.
SAME, OTHER, NONE, CANNOT_TELL = "same", "other", "none", "cannot_tell"
#: The USB vendor id of Espressif's own USB (the ESP32-S3, C3 and C6): there the chip's firmware sets the USB serial. On a
#: bridge chip (CP2104 `10c4`, CH340 `1a86`) the bridge sets it, whatever the firmware.
ESPRESSIF_VENDOR = "303a"
#: The key characters of a MAC: six bytes, two hex digits each.
MAC_KEY_LENGTH = 12
#: The first 12 key characters of a serial that can be a MAC: hex digits only.
MAC_PART = "[0-9a-f]{12}"
#: The store's place of the records, and the version of a record's shape.
PLACE, SCHEMA = "known-boards", 1
UNREADABLE_FIX = "repair or remove that file (spark then asks once more), then run look.py again"
#: The keys of the look's questions, by the first 4 hex of sha256 of the serial's key (or of the port with no serial): a yes
#: to read a board, and a yes to read a board that is not the kept one. A replies file's look keys answer one look only.
READ_BOARD, SWITCH_BOARD, KEY_PREFIX = "look.read_board.%s", "look.switch_board.%s", "look."
READ_QUESTION = "Read the board on %s (%s, %s)? It will restart: a running program stops, then starts again. Nothing is erased or written."
SWITCH_QUESTION = ("Read the board on %s (%s, %s) in place of the kept board? It will restart: a running program stops, "
                   "then starts again. Nothing is erased or written.")
FIRST_WHY = "Spark has not read a board for this project before. After you say yes, it remembers this board and asks no more for it."
#: The sentence a CANNOT_TELL question adds when a board is kept: a yes to another board makes it the project's board.
REPLACE_WHY = " If it is another board, spark makes it this project's board in place of the old one."
NO_SERIAL_WHY = "This board reports no USB serial, so spark cannot tell it from another board before it reads it. It asks every time."
FIRMWARE_WHY = ("This board's USB serial is set by its firmware, so spark cannot tell it from another board before it reads it. "
                "It asks every time.")
KEPT_FIRMWARE_WHY = "The kept board's USB serial was set by its firmware, so spark cannot tell this board from it before it reads it."
SWITCH_WHY = "After you say yes, spark reads this board and keeps it as this project's board, in place of the kept one."
ANSWER_FIX = ('ask the person in this conversation, and name the port and the restart. Only after their yes to that, write '
              '{"replies": {"%s": true}} (the JSON value true) to a file of your own outside the project, and run the next step '
              'with that file in place of the placeholder <your replies file>. One yes is for one look. Never add --port to avoid the question: '
              'it asks all the same, except for a port the list does not hold or that shows no USB serial')
OTHER_BEFORE_MESSAGE = ("Not read. The board on %s (%s): its USB serial is not the kept board's (its MAC ends %s, kept since %s). "
                        "It did not restart.")
OTHER_BEFORE_FIX = "plug in this project's board, or say yes to read this board"
OTHER_AFTER_MESSAGE = ("The board on %s (MAC ends %s) is not the kept board (its MAC ends %s, kept since %s). "
                       "It did restart: a read restarts the board.")
OTHER_AFTER_FIX = "plug in this project's board, then run look.py again"
#: The fix after a read on a listed --port that shows no USB serial: the look without --port asks, and a yes replaces the
#: board. On a port the list does not hold, the record to remove is named instead (OTHER_AFTER_UNLISTED_FIX).
OTHER_AFTER_PORT_FIX = "run look.py without --port and say yes to make this board the project's"
OTHER_AFTER_UNLISTED_FIX = ("plug in this project's board, then run look.py again. If this board replaces it, remove spark's "
                            "record of the old one, %s, then run look.py again and say yes")
NO_MESSAGE, NO_FIX = "You said no. The board was not read and nothing was kept.", "run look.py again when you want to read it"
KEPT_MESSAGE = "kept: spark remembers the board on %s (MAC ends %s) as this project's board"
REPLACED_MESSAGE = "kept: the board on %s (MAC ends %s) is now this project's board, in place of the old one (MAC ended %s)"
NOT_KEPT_NO_MAC_MESSAGE, NOT_KEPT_MESSAGE = "not kept: the board's MAC could not be read", "not kept: %s"


def comparable_key(text):
    """A serial or MAC as they are compared: lower case, with no colon."""
    return (text or "").lower().replace(":", "")


def serial_key(row):
    """The key of the USB serial of `row` (a board_look.Port), or "" when there is no row or the board reports no serial."""
    return "" if row is None or row.serial in ("", NO_SERIAL) else comparable_key(row.serial)


def mac_ends(text):
    """The last two bytes of a MAC, or of a USB serial's MAC part, as `34:56`: the only part of a MAC that spark prints."""
    key = comparable_key(text)
    return "%s:%s" % (key[8:10], key[10:12])


def named(row):
    """How a question names the board on `row` before a read: `MAC ends 34:56` for a serial on Espressif's own USB with a
    MAC's length or more, `USB serial ends B3C4` for any other serial (a bridge's serial is no MAC), or `no USB serial`."""
    key = serial_key(row)
    if not key:
        return "no USB serial"
    return "MAC ends %s" % mac_ends(key) if _vendor(row) == ESPRESSIF_VENDOR and len(key) >= MAC_KEY_LENGTH else "USB serial ends %s" % row.serial[-4:]


def _firmware_set(row):
    """True when the serial of `row` is on Espressif's own USB and cannot be a MAC (not 12 hex digits first): its firmware set it."""
    return _vendor(row) == ESPRESSIF_VENDOR and not re.fullmatch(MAC_PART, serial_key(row)[:MAC_KEY_LENGTH])


def _why(state, row):
    """Why the look asks about the board on `row` in `state`: another board, no serial, a serial its firmware set, a first
    look, or (CANNOT_TELL with a MAC-shaped serial) a kept board whose serial its firmware set."""
    if state == OTHER:
        return SWITCH_WHY
    if not serial_key(row):
        return NO_SERIAL_WHY
    if _firmware_set(row):
        return FIRMWARE_WHY
    return FIRST_WHY if state == NONE else KEPT_FIRMWARE_WHY


def question_for(state, row, port, known):
    """The look's Question before it reads the board on `port`, listed as `row`: SWITCH_BOARD when `state` is OTHER, else
    READ_BOARD. Its `why` says why the look asks: a first look, no serial, or a serial that the board's firmware set; with a
    board `known`, a CANNOT_TELL `why` says that a yes to another board makes it the project's board."""
    key = serial_key(row)
    why = _why(state, row) + (REPLACE_WHY if state == CANNOT_TELL and known else "")
    text = (SWITCH_QUESTION if state == OTHER else READ_QUESTION) % (port, row.product, named(row))
    return Question((SWITCH_BOARD if state == OTHER else READ_BOARD) % board_token(key or port), text, YES_NO, PERSON, why)


def _vendor(row):
    return (row.usb or "").split(":")[0].lower()


class KnownBoard(namedtuple("KnownBoard", "project mac usb_key board answered_by at")):
    """Value: the board kept for one project folder. `project` is the resolved folder, `mac` the MAC as esptool printed it,
    `usb_key` the key of the USB serial when it names this board (usb_key_to_keep), else None. `board` is the board record's
    id, `answered_by` who said yes, `at` when it was kept, with its zone."""

    def to_dict(self):
        return dict(schema=SCHEMA, **self._asdict())


def tell(row, known):
    """Before a read: SAME when the Port `row` is the KnownBoard `known`, by the serial's key or its MAC part; NONE when no board
    is kept; CANNOT_TELL when there is no row (a --port that the list does not hold), the board reports no serial, or a board
    on Espressif's own USB shows a serial that its firmware set and the record trusts none; OTHER in every other case. An
    empty key never matches."""
    key = serial_key(row)
    if not key:
        return CANNOT_TELL
    if known is None:
        return NONE
    if key == known.usb_key or key[:MAC_KEY_LENGTH] == comparable_key(known.mac):
        return SAME
    return CANNOT_TELL if _vendor(row) == ESPRESSIF_VENDOR and known.usb_key is None else OTHER
# --- end MVP ---


def usb_key_to_keep(row, mac):
    """After a read that gave `mac`: the key of the serial of `row` when a record may trust it, else None. It may when the
    serial starts with that MAC (native USB, proven by the read), or when a bridge chip sets it (a vendor that is not
    Espressif's). A serial that a firmware sets is not trusted: a custom build gives every board that runs it one serial."""
    key = serial_key(row)
    return key if key and (key[:MAC_KEY_LENGTH] == comparable_key(mac) or _vendor(row) != ESPRESSIF_VENDOR) else None


class KnownBoardStore:
    """
    Store: the board kept for each project folder, one JSON file per folder in the store's private `known-boards/` (0600,
    never inside a git work tree). The file's name is 16 hex of sha256 of the resolved folder, so a moved project asks once
    more. `read` raises SparkError `known_board_unreadable` for a file it cannot use, and `write` raises store.StoreError
    when the store refuses the write. It writes through the store, under its lock, as DeployRecordStore does.
    """

    @staticmethod
    def find_path(project):
        """The path of the record of `project`."""
        return store.place(PLACE) / (hashlib.sha256(str(Path(project).resolve()).encode()).hexdigest()[:16] + ".json")

    def read(self, project):
        """The KnownBoard of `project`, or None when none is kept, or the record names another folder."""
        path = self.find_path(project)
        if not path.exists() and not path.is_symlink():
            return None
        try:
            kept = json.loads(path.read_text(encoding="utf-8"))
            known = KnownBoard(*(kept[field] for field in KnownBoard._fields))
            if not isinstance(known.mac, str) or not comparable_key(known.mac) or not isinstance(known.usb_key, (str, type(None))) \
                    or not isinstance(known.at, str):
                raise TypeError(known)
        except (OSError, ValueError, RecursionError, KeyError, TypeError):
            raise SparkError("spark's record of this project's board cannot be read: %s", path, code=board_codes.KNOWN_BOARD_UNREADABLE, fix=UNREADABLE_FIX)
        return known if known.project == str(Path(project).resolve()) else None

    def write(self, known):
        """Keep `known` as the board of its project, in place of the one kept before. Returns the record's path."""
        with store.locked():
            store.write_json(PLACE, self.find_path(known.project).stem, known.to_dict())
        return self.find_path(known.project)
