"""
The board that a project's looks read before, kept in the person's store (P865, #1231), and the board question that a
touch asks before its read restarts the board (P892, #1266). The card calls that question a gate. Here it is "the board
question", because "the gate" is the deploy's token and yes (`deploy_gate`). Before a touch, `tell` compares the board on
USB with the kept board, so that a touch never restarts or stops another board without the person's yes. A touch is a
read (the look, the deploy and the grant) or code that runs on the board (reach and live, P892 part 2). After a yes and a
read, the look keeps the board with `KnownBoardStore.write`. No other touch keeps or replaces a board. `board_start` takes
`comparable_key` from here.

    KnownBoard          the kept board: its MAC as esptool printed it, and the key of a USB serial that names it
    KnownBoardStore     one record per project folder, in the store's `known-boards/`
    tell                same, other, none or cannot_tell, before a touch
    Touch               the rules and the words of one touch: LOOK asks in three states, the others in cannot_tell only
    KnownBoardService   `judge`: touch, stop, or ask the board question, by the state and the touch; `require` stops by an error
    BoardQuestionError  a stop of the board question: its Findings, its data and its lines
    differs             after a read: the MAC read is not the kept board's
    other_after         after a read: the `other_board` Finding when the MAC read is not the kept board's
    ComparingBoardReader  a BoardReader that stops after a read of a board that is not the kept one
    usb_key_to_keep     the key of the USB serial that a record may trust, after a read

Spark prints only the last two bytes of a MAC (`mac_ends`). The record holds the whole MAC, in the private store.
"""

import hashlib
import json
import re
from collections import namedtuple
from pathlib import Path

from spark.bench import board_codes
from spark.bench.board_look import NO_SERIAL, board_token, node_name
from spark.core import codes, outcomes
from spark.core.errors import SparkError
from spark.core.replies import PERSON, YES_NO, Question, RepliesStore
from spark.core.result import Finding
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
#: The keys of a touch's questions, under the touch's name and its key word, by the first 4 hex of sha256 of the serial's key
#: (or of the port with no serial, by its /dev/cu. name): a yes to touch a board, and the look's yes to read a board that is
#: not the kept one. A replies file's keys of one touch answer one run of it only.
TOUCH_KEY, SWITCH_BOARD = "%s.%s.%s", "%s.switch_board.%s"
#: The key words: a touch that reads the board, and one that runs code on it (P892 part 2).
READ_WORD, RUN_WORD = "read_board", "run_on_board"
#: The questions name the board as `port (product, MAC ends 34:56)`, or by its port alone when the list does not hold it.
READ_QUESTION = "Read the board on %s? It will restart: a running program stops, then starts again. Nothing is erased or written."
SWITCH_QUESTION = ("Read the board on %s in place of the kept board? It will restart: a running program stops, "
                   "then starts again. Nothing is erased or written.")
DEPLOY_QUESTION = "Read the board on %s? It will restart: a running program stops, then starts again. The erase asks its own yes later."
FIRST_WHY = "Spark has not read a board for this project before. After you say yes, it remembers this board and asks no more for it."
#: The sentence a CANNOT_TELL question adds when a board is kept: a yes to another board makes it the project's board.
REPLACE_WHY = " If it is another board, spark makes it this project's board in place of the old one."
#: The reasons of a CANNOT_TELL question: %s is the touch's `verb`, "reads it" or "runs code on it".
NO_SERIAL_WHY = "This board reports no USB serial, so spark cannot tell it from another board before it %s. It asks every time."
FIRMWARE_WHY = ("This board's USB serial is set by its firmware, so spark cannot tell it from another board before it %s. "
                "It asks every time.")
UNLISTED_WHY = ("The list of boards on USB does not hold this port, so spark cannot tell this board from another board before "
                "it %s. It asks every time.")
KEPT_FIRMWARE_WHY = "The kept board's USB serial was set by its firmware, so spark cannot tell this board from it before it %s."
SWITCH_WHY = "After you say yes, spark reads this board and keeps it as this project's board, in place of the kept one."
ANSWER_FIX = ('ask the person in this conversation, and name the port and the restart. Only after their yes to that, write '
              '{"replies": {"%s": true}} (the JSON value true) to a file of your own outside the project, and run the next step '
              'with that file in place of the placeholder <your replies file>. One yes is for one look. Never add --port to avoid the question: '
              'it asks all the same, except for a port the list does not hold or that shows no USB serial')
#: The stops before a touch: the touch's `untouched` words come first and last.
OTHER_BEFORE_MESSAGE = "%s The board on %s (%s): its USB serial is not the kept board's (its MAC ends %s, kept since %s). %s"
OTHER_BEFORE_FIX = "plug in this project's board, or say yes to read this board"
#: The deploy's fixes (P892): the deploy asks only for a board it cannot tell, and sends another board to the look.
DEPLOY_ANSWER_FIX = ('ask the person in this conversation, and name the port and the restart. Only after their yes to that, write '
                     '{"replies": {"%s": true}} (the JSON value true) to a file of your own outside the project, and run the next '
                     'step with that file in place of the placeholder <your replies file>. One yes is for one deploy, and the erase '
                     'asks its own yes after the read. Never add --port to avoid the question: it asks all the same')
DEPLOY_OTHER_FIX = "plug in this project's board and run deploy.py again, or run look.py to read this board first"
DEPLOY_NO_FIX = "run deploy.py again when you want to deploy to this board"
#: A deploy with no board kept for the project stops before the read and sends the person to the look, which keeps one.
NO_KNOWN_MESSAGE = "%s The board on %s (%s): spark keeps no board for this project yet. %s"
NO_KNOWN_FIX = "run look.py: it asks once and keeps this board. If the look says `not kept`, repair what it names first"
OTHER_AFTER_MESSAGE = ("The board on %s (MAC ends %s) is not the kept board (its MAC ends %s, kept since %s). "
                       "It did restart: a read restarts the board.")
OTHER_AFTER_FIX = "plug in this project's board, then run look.py again"
#: The fix after a read on a listed --port that shows no USB serial: the look without --port asks, and a yes replaces the
#: board. On a port the list does not hold, the record to remove is named instead (OTHER_AFTER_UNLISTED_FIX).
OTHER_AFTER_PORT_FIX = "run look.py without --port and say yes to make this board the project's"
OTHER_AFTER_UNLISTED_FIX = ("plug in this project's board, then run look.py again. If this board replaces it, remove spark's "
                            "record of the old one, %s, then run look.py again and say yes")
NO_MESSAGE, NO_FIX = "You said no. The board was not read and nothing was kept.", "run look.py again when you want to read it"
#: The first and last words of a stop before the touch: a touch that reads, and one that runs code on the board.
NOT_READ, NOTHING_RAN = ("Not read.", "It did not restart."), ("Nothing ran on it.", "Its firmware runs on.")
#: The grant's words (P892 part 2): it reads the board, then asks its own yes.
GRANT_QUESTION = ("Read the board on %s for a grant? It will restart: a running program stops, then starts again. The grant "
                  "asks its own yes after the read.")
GRANT_NO_MESSAGE = "You said no. The board was not read and no grant was given."
GRANT_NO_FIX = "run grant.py again when you want a grant for this board"
GRANT_OTHER_FIX = "plug in this project's board and run grant.py again, or run look.py to read this board first"
GRANT_ANSWER_FIX = ('answer yes when grant.py asks in your terminal, or write {"replies": {"%s": true}} (the JSON value true) to a '
                    'file of your own outside the project and run grant.py again with --replies and that file. One yes is for '
                    'one grant, and the grant asks its own yes after the read. --port asks all the same')
GRANT_AFTER_FIX = "plug in this project's board and run grant.py again, or run look.py to make this board the project's"
#: The words of reach and live, which run code on the board and stop its firmware.
REACH_QUESTION = ('Run print("reached") on the board on %s? Its firmware stops, and it runs again only after you press R or '
                  "replug the board.")
LIVE_QUESTION = "Run the code on the board on %s? Its firmware stops while the code runs, and the board restarts at the end."
NOTHING_RAN_NO_MESSAGE = "You said no. Nothing ran on the board."
REACH_NO_FIX = "run reach.py again when you want to run its line on this board"
LIVE_NO_FIX = "run live.py again when you want to run the code on this board"
REACH_OTHER_FIX = "plug in this project's board and run reach.py again, or run look.py to read this board first"
LIVE_OTHER_FIX = "plug in this project's board and run live.py again, or run look.py to read this board first"
#: %s is the script, then %%s the key.
RUN_ANSWER_FIX = ("ask the person in this conversation, and name the port and that the board's firmware stops. Only after their "
                  'yes to that, write {"replies": {"%%s": true}} (the JSON value true) to a file of your own outside the project, '
                  "and run %s again with --replies and that file. One yes is for one run. Never add --port to avoid the "
                  "question: it asks all the same")
KEPT_MESSAGE = "kept: spark remembers the board on %s (MAC ends %s) as this project's board"
REPLACED_MESSAGE = "kept: the board on %s (MAC ends %s) is now this project's board, in place of the old one (MAC ended %s)"
NOT_KEPT_NO_MAC_MESSAGE, NOT_KEPT_MESSAGE = "not kept: the board's MAC could not be read", "not kept: %s"
#: The one answer that reads the board: a yes, `true` in a replies file.
YES = True


class Touch(namedtuple("Touch", "name asks trusts_port question no_fix other_fix answer_fix key_word untouched no_message verb after_fix")):
    """Value: one touch of a board that asks the board question before it touches the board (P892). `name` is the first word
    of its keys, `asks` the `tell` states it asks in (any other state but SAME stops with no question), and `trusts_port`
    touches a named --port that shows no USB serial with no question. The rest are its words: the question's text, the fixes
    of a no, of another board and of an open question, the key word of its question, the first and last words of a stop
    before the touch, the sentence of a no, the verb of its reasons, and the fix after a read of another board (None for a
    touch that never reads)."""

    @property
    def prefix(self):
        """The prefix of every key of this touch's questions: a run clears its keys in the replies file before it asks."""
        return self.name + "."


#: The look asks before every read of a board it does not know, and reads a named port with no serial as before. The
#: deploy asks only for a board it cannot tell before a read: another board, and no kept board, go to the look.
LOOK = Touch("look", (NONE, OTHER, CANNOT_TELL), True, READ_QUESTION, NO_FIX, OTHER_BEFORE_FIX, ANSWER_FIX,
             READ_WORD, NOT_READ, NO_MESSAGE, "reads it", OTHER_AFTER_FIX)
DEPLOY = Touch("deploy", (CANNOT_TELL,), False, DEPLOY_QUESTION, DEPLOY_NO_FIX, DEPLOY_OTHER_FIX, DEPLOY_ANSWER_FIX,
               READ_WORD, NOT_READ, NO_MESSAGE, "reads it", OTHER_AFTER_FIX)
#: The grant, reach and live ask as the deploy does (P892 part 2): only for a board they cannot tell, also on a named port.
GRANT = Touch(name="grant", asks=(CANNOT_TELL,), trusts_port=False, question=GRANT_QUESTION, no_fix=GRANT_NO_FIX,
              other_fix=GRANT_OTHER_FIX, answer_fix=GRANT_ANSWER_FIX, key_word=READ_WORD, untouched=NOT_READ,
              no_message=GRANT_NO_MESSAGE, verb="reads it", after_fix=GRANT_AFTER_FIX)
REACH = Touch(name="reach", asks=(CANNOT_TELL,), trusts_port=False, question=REACH_QUESTION, no_fix=REACH_NO_FIX,
              other_fix=REACH_OTHER_FIX, answer_fix=RUN_ANSWER_FIX % "reach.py", key_word=RUN_WORD, untouched=NOTHING_RAN,
              no_message=NOTHING_RAN_NO_MESSAGE, verb="runs code on it", after_fix=None)
LIVE = Touch(name="live", asks=(CANNOT_TELL,), trusts_port=False, question=LIVE_QUESTION, no_fix=LIVE_NO_FIX,
             other_fix=LIVE_OTHER_FIX, answer_fix=RUN_ANSWER_FIX % "live.py", key_word=RUN_WORD, untouched=NOTHING_RAN,
             no_message=NOTHING_RAN_NO_MESSAGE, verb="runs code on it", after_fix=None)
KEY_PREFIX = LOOK.prefix
#: The code of a state that a touch does not ask in: it stops before any read.
STOP_FOR = {OTHER: board_codes.OTHER_BOARD, NONE: board_codes.NO_KNOWN_BOARD}


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


def _why(state, row, verb):
    """Why a touch asks about the board on `row` in `state`: another board, a port the list does not hold (no `row`), no
    serial, a serial its firmware set, a first look, or (CANNOT_TELL with a MAC-shaped serial) a kept board whose serial
    its firmware set. `verb` is the touch's: "reads it" or "runs code on it"."""
    if state == OTHER:
        return SWITCH_WHY
    if row is None:
        return UNLISTED_WHY % verb
    if not serial_key(row):
        return NO_SERIAL_WHY % verb
    if _firmware_set(row):
        return FIRMWARE_WHY % verb
    return FIRST_WHY if state == NONE else KEPT_FIRMWARE_WHY % verb


def question_for(state, row, port, known, touch=LOOK):
    """The Question of `touch` before it touches the board on `port`, listed as `row` (None: a port the list does not hold,
    which the question names alone): SWITCH_BOARD when `state` is OTHER, else TOUCH_KEY with the touch's key word, under the
    touch's name. A board with no serial is keyed by the port's /dev/cu. name, so both names of one port give one key. Its
    `why` says why it asks: a first look, no serial, a serial that the board's firmware set, or a port the list does not
    hold. With a board `known`, a CANNOT_TELL `why` of a touch that asks for another board says that a yes to another board
    makes it the project's board."""
    key = serial_key(row)
    why = _why(state, row, touch.verb) + ((REPLACE_WHY if state == CANNOT_TELL and known else "") if OTHER in touch.asks else "")
    text = (SWITCH_QUESTION if state == OTHER else touch.question) % ("%s (%s, %s)" % (port, row.product, named(row)) if row else port)
    token = board_token(key or node_name(port))
    return Question(SWITCH_BOARD % (touch.name, token) if state == OTHER else TOUCH_KEY % (touch.name, touch.key_word, token),
                    text, YES_NO, PERSON, why)


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


def differs(known, mac):
    """After a read: True when a board is kept, a MAC was read, and the MAC is not the kept board's."""
    return bool(known and mac) and comparable_key(mac) != comparable_key(known.mac)


def other_after(known, port, mac, fix):
    """After a read of the board on `port` that gave `mac`: the `other_board` Finding with `fix` when that MAC is not the MAC
    of the KnownBoard `known`, else None. The board did restart. The deploy and the grant stop with it (P892)."""
    if not differs(known, mac):
        return None
    return Finding(outcomes.COULD_NOT_RUN, "board", board_codes.OTHER_BOARD, OTHER_AFTER_MESSAGE % (
        port, mac_ends(mac), mac_ends(known.mac), known.at[:10]), fix)


class KnownBoardResult(namedtuple("KnownBoardResult", "code state known reply question row")):
    """Result: what `KnownBoardService.judge` returns, what the board question let through (P892). `code` None: read the board. Else it is `needs_reply`,
    `answered_no`, `other_board` or `no_known_board`, and the touch stops before any read. `state` is `tell`'s, `known` the
    KnownBoard or None, `reply` the Reply of the yes or None when nobody was asked, `question` the Question asked or None,
    and `row` the listed Port or None."""

    def findings(self, touch):
        """The Findings of a stop, in the words of `touch`: a no, no kept board, or another board before the read, then the
        open question when there is one."""
        first, last = touch.untouched
        if self.code == board_codes.ANSWERED_NO:
            return [Finding(outcomes.COULD_NOT_RUN, self.question.key, board_codes.ANSWERED_NO, touch.no_message, touch.no_fix)]
        if self.code == board_codes.NO_KNOWN_BOARD:
            return [Finding(outcomes.COULD_NOT_RUN, "board", board_codes.NO_KNOWN_BOARD,
                            NO_KNOWN_MESSAGE % (first, self.row.device, named(self.row), last), NO_KNOWN_FIX)]
        found = [Finding(outcomes.COULD_NOT_RUN, "board", board_codes.OTHER_BOARD, OTHER_BEFORE_MESSAGE % (
            first, self.row.device, named(self.row), mac_ends(self.known.mac), self.known.at[:10], last), touch.other_fix)] if self.state == OTHER else []
        if self.code == codes.NEEDS_REPLY:
            found.append(Finding(outcomes.COULD_NOT_RUN, self.question.key, codes.NEEDS_REPLY, self.question.text, touch.answer_fix % self.question.key))
        return found

    def data(self, port):
        """The data of a stop on `port`: the open question, the port, the board's product (None with no row) and the kept board
        by its last two bytes."""
        return {"open": [self.question.to_dict()] if self.code == codes.NEEDS_REPLY else [], "port": port,
                "product": self.row.product if self.row else None,
                "known_board": {"state": self.state, "mac_ends": mac_ends(self.known.mac) if self.known else None}}


class KnownBoardService:
    """
    Service: the board question (P892), before a touch reads the board on USB, which restarts it. `known_store` is the
    KnownBoardStore, `touch` the Touch whose rules and words it uses. `judge` reads the kept board, tells the board on USB,
    and lets the read go on, stops with no question, or asks.
    """

    def __init__(self, known_store, touch):
        self.known_store, self.touch = known_store, touch

    def judge(self, project, port, row, replies):
        """A KnownBoardResult for the board on `port` (None: the one board on USB), listed as the Port `row` (None: a --port
        that the list does not hold). SAME reads with no question, and so does a named port with no serial for a touch that
        trusts it. A state that the touch does not ask in stops with no question. Else `replies` (a ReplyStrategy's `reply`)
        answers: only the JSON value true is a yes, and any value that is no boolean leaves the question open. The SparkError
        of a kept record that cannot be read passes up."""
        known = self.known_store.read(project)
        state = tell(row, known)
        unseen = self.touch.trusts_port and port and not serial_key(row)  # a named port that the list holds with no serial, or not at all
        if state == SAME or unseen:
            return KnownBoardResult(None, state, known, None, None, row)
        if state not in self.touch.asks:
            return KnownBoardResult(STOP_FOR[state], state, known, None, None, row)
        asked = question_for(state, row, port or row.device, known, self.touch)
        reply = replies(asked)
        if reply is None or not isinstance(reply.value, bool):
            return KnownBoardResult(codes.NEEDS_REPLY, state, known, None, asked, row)
        return KnownBoardResult(None if reply.value is YES else board_codes.ANSWERED_NO, state, known, reply, asked, row)

    def require(self, project, port, row, replies, replies_file):
        """`judge` for a touch that stops by an error (P892 part 2). First the touch's keys in `replies_file` are set back to
        null: one yes answers one run, and nothing changes with no file. Then it returns the KnownBoardResult of a board that
        the touch may touch, or raises BoardQuestionError for a stop on `port` (None: the row's). The SparkError of a kept
        record or of a replies file that cannot be read passes up."""
        if replies_file:
            RepliesStore(replies_file).clear(self.touch.prefix)
        judged = self.judge(project, port, row, replies)
        if judged.code:
            raise BoardQuestionError.of(judged, self.touch, port or row.device)
        return judged


class BoardQuestionError(Exception):
    """Error: a stop of the board question before a touch (P892 part 2). `findings` are its Findings, `data` the open question,
    the port, the product and the kept board (KnownBoardResult.data, None after a read), and `lines` the sentences and fixes
    a person reads, then the question's why. It is no board_look.LookStopError and names no port to open, so no board doctor
    runs for it."""

    def __init__(self, findings, data, lines):
        super().__init__(findings[-1].sentence)
        self.findings, self.data, self.lines = findings, data, lines

    @property
    def code(self):
        """The code of the stop: its last Finding's."""
        return self.findings[-1].code

    @classmethod
    def of(cls, judged, touch, port):
        """The error of the KnownBoardResult `judged` of `touch`, a stop on `port`."""
        findings = judged.findings(touch)
        why = [judged.question.why] if judged.code == codes.NEEDS_REPLY else []
        return cls(findings, judged.data(port), [line for found in findings for line in (found.sentence, found.fix)] + why)


class ComparingBoardReader:
    """Decorator: a board_look.BoardReader whose `read(port)` reads the board, then raises BoardQuestionError when the MAC read
    is not the MAC of the board that `known_store` keeps for `project` (other_after, with the fix of `touch`). The board did
    restart. It keeps no state (P892 part 2): the grant's read stops before the grant's own yes."""

    def __init__(self, reader, known_store, touch, project):
        self.reader, self.known_store, self.touch, self.project = reader, known_store, touch, project

    def read(self, port):
        reading = self.reader.read(port)
        found = other_after(self.known_store.read(self.project), port, reading.mac, self.touch.after_fix)
        if found:
            raise BoardQuestionError([found], None, [found.sentence, found.fix])
        return reading
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
