"""
The projects that are not spark's and record their deploys in spark's store (P920, #1302): each name once, with the text
that every worktree of the project shares (its origin) and the tool that deploys it.

A library, for `bench.py register` (it writes a name) and `bench.py record` (it reads one). The names live in one object
of a Storage (P1036), `{name: {origin, tool, registered}}`; on FileStorage it is the private file `registered-projects.json`
of the store. A name is taken when another origin holds it, or when the person's projects list names it, also when its
folder is gone.
"""

from collections import namedtuple

from spark.core.errors import SparkError
from spark.core.text_guards import CONTROL
from spark.records import records_codes
from spark.records import store
from spark.records.storage import FileStorage

# --- MVP ---
PLACE = "registered-projects"
#: The keys of one name's entry in the file, each a text.
FIELDS = ("origin", "tool", "registered")
NOT_REGISTERED_YET = "Not registered."


class RegisteredProject(namedtuple("RegisteredProject", "name origin tool registered")):
    """Value: one registered project: its `name` in the store, its `origin` (any text every worktree shares), the `tool`
    that deploys it, and when it was `registered`, with its zone."""


class RegisteredProjectStore:
    """
    Store: the registered projects, one object in its Storage (P1036; FileStorage, the default, keeps one private file in
    spark's store, 0600 and never inside a git work tree). `read` gives one by name, `register` writes one under the
    Storage's lock. An object that is no object of entries is store.StoreError `record_file_broken`; a name that is not
    plain or is taken is SparkError with its code and fix, and nothing is written.
    """

    def __init__(self, storage=None):
        self.storage = FileStorage() if storage is None else storage

    def read(self, name):
        """The RegisteredProject of `name`, or None when nobody registered it."""
        entry = self._read_all().get(name)
        return RegisteredProject(name, *(entry[field] for field in FIELDS)) if entry else None

    def register(self, name, origin, tool, at):
        """(the RegisteredProject of `name`, whether the file changed). The same name with the same origin changes nothing,
        and with another tool it replaces the tool: a name has one tool."""
        if not store.PLAIN.fullmatch(name):
            raise SparkError("%r is not a plain name (lower-case letters, digits and '-'). %s", name, NOT_REGISTERED_YET,
                             code=records_codes.KEY_NOT_PLAIN_REGISTERED)
        if any(not value.strip() or CONTROL.search(value) for value in (origin, tool)):  # a blank tool reads as spark's own deploy
            raise SparkError("the origin and the tool must be printable text, not blank. %s", NOT_REGISTERED_YET,
                             code=records_codes.BLANK_VALUE)
        with self.storage.locked():
            listed = self._read_all()
            kept = listed.get(name)
            if (kept and kept["origin"] != origin) or name in store.projects():
                raise SparkError("%s is taken in spark's store: another project holds it. %s", name, NOT_REGISTERED_YET,
                                 code=records_codes.NAME_TAKEN)
            if kept and kept["tool"] == tool:
                return RegisteredProject(name, *(kept[field] for field in FIELDS)), False
            listed[name] = dict(zip(FIELDS, (origin, tool, at)))
            self.storage.put(PLACE, None, listed)
        return RegisteredProject(name, origin, tool, at), True

    def _read_all(self):
        """{name: entry} of the Storage, or {} before the first name."""
        listed = self.storage.get(PLACE)
        if listed is None:
            return {}
        if not all(isinstance(entry, dict) and all(isinstance(entry.get(field), str) for field in FIELDS) for entry in listed.values()):
            raise store.StoreError("%s is not an object of registered projects: fix it by hand", self.storage.where(PLACE),
                                   code=records_codes.RECORD_FILE_BROKEN)
        return listed
# --- end MVP ---
