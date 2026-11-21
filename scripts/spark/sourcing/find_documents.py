"""
`parts.py --find-documents`: a board's top view and dimension drawing, found on its maker's page by a vendor finder
(`vendor_documents`), kept in the person's store and listed in the board's `documents` (P952 #1358), all or nothing:
the record is written dry before any file is kept. It draws nothing and writes no `pictures` block: the top view is
what `--features-set` measures, and the drawing is what the outline cites. A file the record keeps already is not
fetched again, so a second run fetches nothing. It reaches the network through `fetch` (the store's one door), so it
declares `fetches`; the dry run reaches nothing.
"""

from collections import namedtuple

from spark.breadboard.picture_makers import Decline
from spark.core.operation import COMMON_ARGUMENTS, FETCHES, JSON_DEST, READS, WRITES, Argument
from spark.core.outcomes import add_env, step
from spark.records import board_records, store
from spark.records.answer_operation import ANSWER_ARGUMENTS
from spark.records.record_kind import Answer, _cannot, _parse, _problem
from spark.sourcing import datasheets, record_home, sourcing_codes
from spark.sourcing.keep_file import _documents_problems, document_listing
from spark.sourcing.part_operation import PartOperation
from spark.sourcing.research.research_source import DRAWING_TITLE_WORDS
from spark.sourcing.vendor_documents import DRAWING, FINDER_ORDER, FINDERS, TOP_VIEW, FoundFile

# --- MVP ---
#: The words in a `documents` key or title that name a kept file of each role, as research's drawing words do.
ROLE_WORDS = {TOP_VIEW: ("board overview", "board-overview"), DRAWING: DRAWING_TITLE_WORDS}
#: Each role's name in a line, and the data key it is answered under.
ROLE_NAMES = {TOP_VIEW: "top view", DRAWING: "dimension drawing"}
ROLE_KEYS = {TOP_VIEW: "top_view", DRAWING: "drawing"}
#: The code of a finder's Decline, by what it declined.
DECLINE_CODES = {None: sourcing_codes.NO_SKU, TOP_VIEW: sourcing_codes.NO_TOP_VIEW, DRAWING: sourcing_codes.NO_DIMENSION_DRAWING}
#: The note on a top view: spark reads its place on the page, never what it shows.
NOT_CHECKED_VIEW = ("spark did not check that this picture is a straight, component-side top view of your board's revision: "
                    "look at it before you measure it")
#: The why of the next step after a top view was kept, and after none was.
MEASURE_WHY = "measure the board's features on documents.%s in its pixels and write them (a board's measured features)"
PHOTO_WHY = ("a photo of the part: /spark:identify, then measure it with parts.py --features-set FILE --part %s --project ."
             " (no maker's page gave a top view)")


def kept_file(entry):
    """Whether a `documents` entry names a file the store holds under its sha256."""
    return board_records.names_a_kept_file(entry) and (store.place("sources") / entry["sha256"] / entry["file"]).is_file()


def held_key(documents, role):
    """The key of the first entry whose key or title names `role`'s words and whose file is kept, or, for the drawing,
    that is listed `kept: false` (a zip spark does not open); None when the record holds none."""
    for key, entry in documents.items():
        said = ("%s %s" % (key, entry.get("title") or "")).lower() if isinstance(entry, dict) else ""
        if any(word in said for word in ROLE_WORDS[role]) and (kept_file(entry) or (role == DRAWING and entry.get("kept") is False)):
            return key
    return None


def said_of(key, entry, new):
    """A role's answer: its key, URL, sha256, whether the store keeps it, and whether this run listed it."""
    return {"key": key, "url": entry.get("url"), "sha256": entry.get("sha256"), "kept": entry.get("kept") is not False, "new": new}


class FindDocuments(PartOperation):
    """Operation: `find-documents` as parts.py answers it: the page read, the top view and the drawing each with its
    documents key (or null), the finders' declines, the URLs fetched and whether the record was written; a page or a file
    that does not answer is a could-not-run item; a board nobody has, a part's record, spark's library and each Decline
    are problems. `fetch` is the store's door (None: `store.fetch`), `finders` the finders in order (None: `FINDER_ORDER`)."""

    name = "find-documents"
    data_keys = ("record", "page", "top_view", "drawing", "declines", "fetched", "written")
    arguments = (Argument(("--find-documents",), "part_id", str, "find a DFRobot board's top view and dimension drawing on "
                          "the maker's wiki page by its sku, keep them in your store and list them in the board's documents; "
                          "it draws nothing, and a file the record keeps already is not fetched again", metavar="BOARD"),
                 ANSWER_ARGUMENTS["project"], ANSWER_ARGUMENTS["dry_run"], COMMON_ARGUMENTS[JSON_DEST])
    effects = (READS, WRITES, FETCHES)

    def __init__(self, fetch=None, finders=None):
        self._fetch = fetch
        self.finders = finders if finders is not None else [FINDERS[name]() for name in FINDER_ORDER]

    def effects_of(self, values):
        return (READS,) if values["dry_run"] else self.effects

    def run(self, *, outside, **values):
        """`AnswerOperation.run`, with today's date from the outside's clock: the `retrieved` of a kept file."""
        return super().run(outside=outside, **dict(values, today=outside.clock.now().date().isoformat()))

    def build_answer(self, part_id, project, dry_run, today):
        path, source = record_home.record_path(part_id, project, "board")
        record = _parse(path) if path is not None else None
        if not isinstance(record, dict):
            part, _ = record_home.record_path(part_id, project, "part")
            why = ("%s is a part's record: research.py keeps a module's Dimension drawing from its DFRobot wiki page "
                   "(/spark:research); --find-documents finds a board's" % part_id if part is not None
                   else "no record of a board called %r — `boards.py --list` finds what exists" % part_id)
            return Answer(problems=[_problem(part_id, why, code=sourcing_codes.NO_SUCH_PART)])
        if record_home.in_library(path):
            return Answer(problems=[record_home.library_problem(part_id)])
        finder = next((finder for finder in self.finders if finder.knows(record)), None)
        if finder is None:
            return self._declined(part_id, project, Decline("vendor", "no finder knows the vendor of %s: its vendor and sources "
                                                            "name no DFRobot page" % part_id, ("vendor", "sources")),
                                  sourcing_codes.NO_VENDOR_FINDER)
        documents = record.get("documents") if isinstance(record.get("documents"), dict) else {}
        held = {role: held_key(documents, role) for role in ROLE_KEYS}
        said = {role: said_of(key, documents[key], False) for role, key in held.items() if key is not None}
        page = finder.page_of(record)
        if page is None:
            return self._declined(part_id, project, finder.find(record, self._fetch_of()), DECLINE_CODES[None])
        if dry_run or all(held.values()):
            wanted = [ROLE_NAMES[role] for role, key in held.items() if key is None]
            lines = ["  would read %s for the %s" % (page, " and the ".join(wanted))] if wanted else []
            lines += ["  %s: documents.%s, kept already" % (ROLE_NAMES[role], said[role]["key"]) for role in said]
            return answer_of(part_id, project, page, said, KeepResult(lines=lines))
        try:
            found = finder.find(record, self._fetch_of())
        except store.StoreError as unreached:
            return Answer(unchecked=[_cannot(str(unreached), code=unreached.code)])
        return DocumentKeep(record, held, self._fetch_of(), today).run(part_id, project, (path, source), found, said)

    def _fetch_of(self):
        return self._fetch or store.fetch

    def _declined(self, part_id, project, decline, code):
        """The Answer of a Decline that stops the run: a problem with its code, and the photo step next."""
        return Answer({"record": part_id, "page": None, "top_view": None, "drawing": None, "declines": [_decline(decline)],
                       "fetched": [], "written": False}, problems=[_problem(part_id, decline.reason, code=code)],
                      next=[_photo_step(part_id, project)])


class KeepResult(namedtuple("KeepResult", "lines written fetched declines problems unchecked notes top_declined",
                            defaults=((), False, (), (), (), (), (), False))):
    """Result: what `DocumentKeep` did: the lines it says, whether the record was written, the URLs it fetched, the
    finder's declines and their problems, the files that did not answer, its notes, and whether the page gave no top view."""


def answer_of(part_id, project, page, said, kept):
    """The Answer of a run that read, or would read, the page: each role said, and the next step: measuring the kept top
    view, or the photo when the page gave none."""
    top = said.get(TOP_VIEW)
    notes = [{"subject": "documents.%s" % top["key"], "sentence": NOT_CHECKED_VIEW}] if top else []
    follow = [_measure_step(part_id, project, top["key"])] if top else ([_photo_step(part_id, project)] if kept.top_declined else [])
    return Answer({"record": part_id, "page": page, "top_view": top, "drawing": said.get(DRAWING),
                   "declines": [_decline(one) for one in kept.declines], "fetched": list(kept.fetched), "written": kept.written},
                  list(kept.lines), problems=list(kept.problems), unchecked=list(kept.unchecked), notes=notes + list(kept.notes), next=follow)


class DocumentKeep:
    """Service: the files a finder found that the record does not keep yet, fetched and listed in `documents`, the record
    written dry, then the files kept in the store, then the record written: all or nothing. A file whose URL the record
    lists is kept under that entry's file name; the same bytes are never listed twice; changed bytes at a listed URL are
    listed beside the old entry, with a note."""

    def __init__(self, record, held, fetch, today):
        documents = record.get("documents")
        self.before = documents if isinstance(documents, dict) else {}
        self.documents, self.held, self.fetch, self.today = dict(self.before), held, fetch, today
        self.payloads, self.fetched, self.notes, self.unchecked, self.problems, self.declines = [], [], [], [], [], []

    def run(self, part_id, project, home, found, said):
        for role, key in ROLE_KEYS.items():
            what = getattr(found, key)
            if self.held[role] is not None:
                continue
            if isinstance(what, FoundFile):
                listed = self._listed(what)
                if listed is not None:
                    said[role] = listed
            else:
                self.declines.append(what)
                self.problems.append(_problem(part_id, what.reason, code=DECLINE_CODES[role]))
        lines = ["  %s: documents.%s, %s <- %s" % (ROLE_NAMES[role], one["key"], _state(one), one["url"])
                 for role, one in said.items()]
        changes = self.documents != self.before
        try:
            if changes:
                dry = record_home.write_fields(part_id, home, {"documents": self.documents}, True, _documents_problems)
                if dry.problems:
                    return Answer(problems=dry.problems)
            for payload, name in self.payloads:
                datasheets.keep_in_store(payload, name)
            if changes:
                written = record_home.write_fields(part_id, home, {"documents": self.documents}, False, _documents_problems)
                if written.problems:
                    return Answer(problems=written.problems)
        except store.StoreError as refused:
            return Answer(unchecked=self.unchecked + [_cannot(str(refused), code=refused.code)])
        return answer_of(part_id, project, found.page, said, KeepResult(
            lines, changes, self.fetched, self.declines, self.problems, self.unchecked, self.notes, not isinstance(found.top_view, FoundFile)))

    def _listed(self, found):
        """The role's answer once `found` is listed (fetched first when the store does not keep it), or None when its
        file did not answer."""
        same_url = [(key, entry) for key, entry in self.documents.items() if isinstance(entry, dict) and entry.get("url") == found.url]
        kept = next(((key, entry) for key, entry in same_url if kept_file(entry)), None)
        if kept is not None:
            return said_of(kept[0], kept[1], False)
        if not found.keepable:
            return self._not_kept(found, same_url)
        try:
            payload = self.fetch(found.url)
        except store.StoreError as unreached:
            self.unchecked.append(_cannot(str(unreached), code=unreached.code))
            return None
        self.fetched.append(found.url)
        name = next((entry["file"] for _, entry in same_url if board_records.names_a_kept_file(entry)), None) or datasheets.document_name(found.url)
        digest = datasheets.keep_in_store(payload, name, dry_run=True)
        same_bytes = next((entry for entry in self.documents.values() if isinstance(entry, dict) and entry.get("sha256") == digest
                           and board_records.names_a_kept_file(entry)), None)
        name = same_bytes["file"] if same_bytes else name
        entry = datasheets.document_entry(found.url, digest, name, self.today, found.title)
        key, was, _, self.documents = document_listing({"documents": self.documents}, entry)
        self.payloads.append((payload, name))
        changed = [(old_key, old) for old_key, old in same_url if old.get("sha256") != digest and old.get("kept") is not False]
        if changed and was is None:
            self.notes.append({"subject": "documents.%s" % key, "sentence": "the file at %s changed since %s; the old entry %s "
                               "stays beside it" % (found.url, changed[0][1].get("retrieved"), changed[0][0])})
        return said_of(key, self.documents[key], was is None)

    def _not_kept(self, found, same_url):
        """A file of a kind the store does not keep (a zip): listed `kept: false` once, never fetched, and said."""
        if same_url:
            return said_of(same_url[0][0], same_url[0][1], False)
        key = datasheets.document_key(datasheets.document_name(found.url), self.documents)
        self.documents[key] = {"url": found.url, "kept": False, "title": found.title}
        self.notes.append({"subject": "documents.%s" % key, "sentence": "the %s is in a %s file that spark does not keep or open: "
                           "open it by hand" % (ROLE_NAMES[found.role], found.url.rsplit(".", 1)[-1].lower())})
        return said_of(key, self.documents[key], True)


def _state(said):
    """What became of a role's file, in words."""
    return ("kept and listed" if said["kept"] else "listed, not kept") if said["new"] else "kept already"


def _decline(decline):
    return {"maker": decline.maker, "reason": decline.reason, "missing": list(decline.missing)}


def _with_project(project):
    return ["--project", str(project)] if project else []


def _measure_step(part_id, project, key):
    return add_env(step("features-set", ["--features-set", "<file>", "--part", part_id] + _with_project(project), MEASURE_WHY % key,
                        ["writes"]), store.read_given_env())


def _photo_step(part_id, project):
    return add_env(step("features-set", ["--features-set", "<file>", "--part", part_id] + _with_project(project), PHOTO_WHY % part_id,
                        ["writes"], needs_person=True), store.read_given_env())
# --- end MVP ---
