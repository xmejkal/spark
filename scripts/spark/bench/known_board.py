"""
The board that a project's looks read before, kept in the person's store (P865, #1231). A library for
`look_at_board.LookAtBoard`: before a read, `tell` compares the board on USB with the kept board, so that the look never
restarts another board without the person's yes. After a yes and a read, `KnownBoardStore.write` keeps the board.
`board_start` takes `_key` from here.

    KnownBoard        the kept board: its MAC as esptool printed it, and the key of a USB serial that names it
    KnownBoardStore   one record per project folder, in the store's `known-boards/`
    tell              same, other, none or cannot_tell, before a read
    usb_key_to_keep   the key of the USB serial that a record may trust, after a read

Spark prints only the last two bytes of a MAC (`mac_ends`). The record holds the whole MAC, in the private store.
"""

import hashlib
import json
from collections import namedtuple
from pathlib import Path

from spark.bench import board_codes
from spark.bench.board_look import NO_SERIAL
from spark.core.errors import SparkError
from spark.records import store

# --- MVP ---
#: What `tell` says before a read: the kept board is on USB, another board is, no board is kept, or the serial cannot say.
SAME, OTHER, NONE, CANNOT_TELL = "same", "other", "none", "cannot_tell"
#: The USB vendor id of Espressif's own USB (the ESP32-S3, C3 and C6): there the chip's firmware sets the USB serial. On a
#: bridge chip (CP2104 `10c4`, CH340 `1a86`) the bridge sets it, whatever the firmware.
ESPRESSIF_VENDOR = "303a"
#: The key characters of a MAC: six bytes, two hex digits each.
MAC_KEY_LENGTH = 12
#: The store's place of the records, and the version of a record's shape.
PLACE, SCHEMA = "known-boards", 1
UNREADABLE_MESSAGE = "spark's record of this project's board cannot be read: %s"
UNREADABLE_FIX = "repair or remove %s, then run look.py again"


def _key(text):
    """A serial or MAC as they are compared: lower case, with no colon."""
    return (text or "").lower().replace(":", "")


def serial_key(row):
    """The key of the USB serial of `row` (a board_look.Port), or "" when there is no row or the board reports no serial."""
    return "" if row is None or row.serial in ("", NO_SERIAL) else _key(row.serial)


def mac_ends(text):
    """The last two bytes of a MAC, or of a USB serial's MAC part, as `34:56`: the only part of a MAC that spark prints."""
    key = _key(text)
    return "%s:%s" % (key[8:10], key[10:12])


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
    if key == known.usb_key or key[:MAC_KEY_LENGTH] == _key(known.mac):
        return SAME
    return CANNOT_TELL if _vendor(row) == ESPRESSIF_VENDOR and known.usb_key is None else OTHER
# --- end MVP ---


def usb_key_to_keep(row, mac):
    """After a read that gave `mac`: the key of the serial of `row` when a record may trust it, else None. It may when the
    serial starts with that MAC (native USB, proven by the read), or when a bridge chip sets it (a vendor that is not
    Espressif's). A serial that a firmware sets is not trusted: a custom build gives every board that runs it one serial."""
    key = serial_key(row)
    return key if key and (key[:MAC_KEY_LENGTH] == _key(mac) or _vendor(row) != ESPRESSIF_VENDOR) else None


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
            if not isinstance(known.mac, str) or not _key(known.mac) or not isinstance(known.usb_key, (str, type(None))):
                raise TypeError(known)
        except (OSError, ValueError, RecursionError, KeyError, TypeError):
            raise SparkError(UNREADABLE_MESSAGE, path, code=board_codes.KNOWN_BOARD_UNREADABLE, fix=UNREADABLE_FIX % path)
        return known if known.project == str(Path(project).resolve()) else None

    def write(self, known):
        """Keep `known` as the board of its project, in place of the one kept before. Returns the record's path."""
        with store.locked():
            store.write_json(PLACE, self.find_path(known.project).stem, known.to_dict())
        return self.find_path(known.project)
