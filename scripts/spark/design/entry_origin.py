"""
Which entries of a project's requirements.json spark wrote for a pick (P877). A record beside the file, `.spark/requirements-origin.json`,
holds a row for each entry spark added and the sha256 of the `parts` list as spark last wrote it. An entry is spark's only when a row
holds it and the record still fits the file's `parts`; every other entry is the person's. `need_requirements.requirements` reads it,
and `parts.py --requirements` (`write_requirements`) names the entries written for a pick that is gone and removes them on the
person's yes, which it reads from the replies file of the run. The record also holds the sha256 of the whole file as spark wrote it, so that
`is_as_written` tells a file changed by hand after (P1140). Nothing here guesses: what spark cannot prove it wrote is the person's.
"""

import collections
import hashlib
import json
from pathlib import Path

from spark.build.build_record import STAGE_IN_THE_WAY, PreviousVersionFiles, StageTakenError
from spark.core.errors import SparkError
from spark.core.replies import RepliesStore
from spark.design import design_codes
from spark.records import store

# --- MVP ---
#: The record beside the requirements file, from the project's folder, and the keys it holds.
ORIGIN_FILE = Path(".spark") / "requirements-origin.json"
SCHEMA, PARTS_SHA256, CONTENT_SHA256, WRITTEN = 1, "parts_sha256", "content_sha256", "written"
#: Every reply key of this Operation starts with the first; the key of a removal starts with the second and ends in 8 hex digits.
KEY_PREFIX = "requirements."
REMOVE_KEY = KEY_PREFIX + "remove_entries."
#: Said, never a refusal: why every entry is read as the person's, and what a reply that fits no key leaves.
NOTE_CHANGED = "requirements-origin.json does not fit the parts of requirements.json as spark wrote them, so every entry is read as yours"
NOTE_BROKEN = "requirements-origin.json cannot be read as spark writes it, so every entry is read as yours"
NOTE_OTHER_KEY = "the replies file holds an answer for other entries or other bytes, so nothing was removed: the answer for these entries is %s"
NOTE_UNWRITTEN = "requirements-origin.json could not be written, so every entry is read as yours from the next run"
#: Why the previous version could not be kept, with the path from the project's folder.
KEEP_FAILED = "the previous version could not be kept: %s (%s)"

#: Value: one row of the record, the need an entry was added for and the entry as spark wrote it (a bare part id, or {part, name}).
WrittenEntry = collections.namedtuple("WrittenEntry", "need entry")
#: Value: an entry to remove, by its index in the file's `parts`, the row that proves it, and `shown`, {part, name} as `kept` shows it.
Gone = collections.namedtuple("Gone", "index row shown")


def form_of(entry):
    """An entry as one string, so two entries are equal when their JSON is: an entry the person changed is not its row's."""
    return json.dumps(entry, sort_keys=True, ensure_ascii=False)


def parts_sha256(parts):
    """The sha256 of the canonical JSON of a `parts` list: a reformat of the file, or a key beside `parts`, leaves it the same."""
    return hashlib.sha256(json.dumps(parts, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


def rows_present(rows, parts):
    """The rows whose entry `parts` still holds, one row for each equal entry: a row of an entry the person deleted is gone."""
    room = collections.Counter(form_of(entry) for entry in parts)
    present = []
    for row in rows:
        if room[form_of(row.entry)] > 0:
            room[form_of(row.entry)] -= 1
            present.append(row)
    return present


class UnexplainedEntries(collections.namedtuple("UnexplainedEntries", "removable persons rows written note")):
    """
    Value: what the record says of the entries of the file that no pick explains. `removable` is the `Gone` entries spark
    wrote and no pick explains now; `persons` is the others, as `kept` shows them; `rows` is the rows the record held for this
    file, `written` the rows of the entries this run adds, and `note` why the rows were not read, or None. It only calculates.
    """

    @classmethod
    def find(cls, existing, merged, rows, note):
        """
        The value for the file's `existing` entries, the `merged` result of `need_requirements._merge_parts` (its `explained`
        indexes, `kept` and `written`), the record's `rows` and its `note`. For each entry form: `r` rows hold it, `k` entries equal
        to it are explained by a pick, `u` are not. The last `min(u, max(0, r - k))` of those are removable: a second copy by the
        person's hand stays when a pick explains the first.
        """
        unexplained = [number for number in range(len(existing)) if number not in merged.explained]
        shown, gone = dict(zip(unexplained, merged.kept)), []
        for form in dict.fromkeys(form_of(row.entry) for row in rows):
            mine = [row for row in rows if form_of(row.entry) == form]
            same = [number for number in range(len(existing)) if form_of(existing[number]) == form]
            free = [number for number in same if number not in merged.explained]
            count = min(len(free), max(0, len(mine) - (len(same) - len(free))))
            gone += [Gone(number, row, shown[number]) for number, row in zip(free[len(free) - count:], mine)]
        gone.sort()
        taken = {each.index for each in gone}
        return cls(tuple(gone), [shown[number] for number in unexplained if number not in taken], tuple(rows), tuple(merged.written), note)

    def without_removable(self, existing):
        """(the file's entries without the removable ones, the rows without theirs): what a yes leaves to merge the picks into."""
        gone = {each.index for each in self.removable}
        return [entry for number, entry in enumerate(existing) if number not in gone], self.rows_left()

    def rows_left(self):
        """The rows without the rows of the removable entries: after a no, they are the person's."""
        left = list(self.rows)
        for each in self.removable:
            left.remove(each.row)
        return left

    def disowned(self):
        """The value after a no: no entry is removable, and the rows of those entries are gone, so they are the person's."""
        return self._replace(removable=(), rows=tuple(self.rows_left()))

    def to_dicts(self):
        """`data.unexplained`: {part, name, need, code} for each removable entry."""
        return [dict(each.shown, need=each.row.need, code=design_codes.ENTRY_PICK_GONE) for each in self.removable]

    def key(self, content):
        """The reply key of these entries on a file of the bytes `content`: 8 hex digits of the sha256 of the bytes and the
        canonical JSON of the entries, so a yes fits neither other bytes nor other entries. None when none is removable."""
        if not self.removable:
            return None
        entries = json.dumps([each.row.entry for each in self.removable], sort_keys=True, ensure_ascii=False).encode("utf-8")
        return REMOVE_KEY + hashlib.sha256(content + entries).hexdigest()[:8]


class EntryOriginStore:
    """Store: the record `.spark/requirements-origin.json` of one project: `rows_of` reads the rows that can be trusted and `save`
    writes the record, through the store's one atomic write."""

    def __init__(self, project):
        self.path = Path(project) / ORIGIN_FILE

    def rows_of(self, existing):
        """(the rows, a note): the record's rows when it fits the file's `existing` entries, else none and why. A missing record
        gives none and no note; one that is no JSON of its shape gives `NOTE_BROKEN`; one whose hash is not the entries' gives
        `NOTE_CHANGED` when it held rows."""
        if not self.path.is_file():
            return [], None
        try:
            held = json.loads(self.path.read_text(encoding="utf-8"))
            rows, fits = [WrittenEntry(row["need"], row["entry"]) for row in held[WRITTEN]], held[PARTS_SHA256] == parts_sha256(existing)
        except (OSError, ValueError, KeyError, TypeError, RecursionError):
            return [], NOTE_BROKEN
        return (rows, None) if fits else ([], NOTE_CHANGED if rows else None)

    def is_as_written(self, held):
        """True when `held`, requirements.json as JSON, is the file spark last wrote (P1140). False when it changed after.
        None when spark cannot tell: no record, one with no CONTENT_SHA256 (written before P1140), or one that cannot be read."""
        try:
            written = json.loads(self.path.read_text(encoding="utf-8")).get(CONTENT_SHA256)
            return written == parts_sha256(held) if isinstance(written, str) else None
        except (OSError, ValueError, AttributeError, RecursionError):
            return None

    def save(self, content, rows):
        """Write the record of `content`, requirements.json as JSON, and its `rows`, with no rows too (P1139): then it says spark wrote
        no entry of these parts, and its hashes tell a later hand edit (P1140). OSError when it cannot."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        # parts_sha256 hashes the canonical JSON of any value: here the parts, and here the whole file
        record = {"schema": SCHEMA, PARTS_SHA256: parts_sha256(content["parts"]), CONTENT_SHA256: parts_sha256(content),
                  WRITTEN: [row._asdict() for row in rows]}
        store.write_file(self.path, json.dumps(record, indent=1, ensure_ascii=False) + "\n")


class EntryRemoval:
    """
    Adapter: the person's answer to the removal of the entries `found` names, and the previous version of the file (P877). It reads
    the `--replies` file the agent wrote, with `PreviousVersionFiles` and `RepliesStore` doing the writing. It reads nothing on a
    dry run, on a refused run, or when no entry is removable. Only the JSON `true` for `check` is a yes and `false` a no; a yes or a no
    sets every `requirements.` key back to null before anything changes. A yes stages the previous version at once; `agreed`
    says it worked, and `left` the why when it did not. `settle` puts the previous version in place and writes the record last,
    and `release` takes a stage away that no commit used.
    """

    def __init__(self, path, found, replies, dry_run):
        self.path, self.unexplained, self.held, self.previous = Path(path), found.unexplained, None, None
        self.check = None if found.problems or dry_run else found.unexplained.key(self.path.read_bytes() if self.path.is_file() else b"")
        self.verdict, self.stale, self.left, self.unwritten = None, False, None, False
        if self.check and replies:
            self._answer(replies)
        self.agreed = self.held is not None

    def _answer(self, replies):
        """Read the reply for `check`, set the run's keys back to null when it is a yes or no, and stage the previous version on a yes."""
        given = {key: reply for key, reply in self._load(replies).items() if key.startswith(REMOVE_KEY)}
        reply = given.get(self.check)
        if reply is None or not isinstance(reply.value, bool):
            self.stale = bool([key for key in given if key != self.check])
            return
        RepliesStore(replies).clear(KEY_PREFIX)
        self.verdict = reply.value
        if self.verdict:
            try:
                self.held = PreviousVersionFiles(self.path.parent).stage(self.path)
            except OSError as refused:
                where = self._relative(refused.filename)
                self.left = STAGE_IN_THE_WAY % where if isinstance(refused, StageTakenError) else KEEP_FAILED % (refused.strerror, where)

    def _relative(self, name):
        """`name` from the project's folder, as the previous version's path is said; as it is when it is not under it."""
        try:
            return str(Path(name).relative_to(self.path.parent))
        except ValueError:
            return str(name)

    @staticmethod
    def _load(replies):
        """The replies in the file; a file that cannot be read is a SparkError with this Operation's own fix."""
        try:
            return RepliesStore(replies).load()
        except SparkError as unreadable:
            raise SparkError.of_error(unreadable, code=design_codes.BAD_ARGUMENT_REQUIREMENTS_REPLIES, status=unreadable.status) from None

    def settle(self, found, dry_run):
        """After the file is written: put the staged previous version in place, then write the record last. Nothing on a dry run or
        a refused run. `found` is the `Requirements` the file was written from."""
        if dry_run or found.problems:
            return
        if self.held:
            kept, self.held = PreviousVersionFiles(self.path.parent).commit(self.held), None
            self.previous = str(Path(kept).relative_to(self.path.parent))
        now = found.unexplained
        try:
            EntryOriginStore(self.path.parent).save(found.content, rows_present(list(now.rows) + list(now.written), found.content["parts"]))
        except (OSError, ValueError):  # the record never fails the run: the file is written, and the entries read as the person's
            self.unwritten = True

    def release(self):
        """Remove the staged previous version when no commit used it; no error."""
        if self.held:
            self.held.remove()
# --- end MVP ---
