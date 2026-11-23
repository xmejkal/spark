"""
One Storage under the Stores (P1036, #1519; storage stage 1 of P1033, #1515).

A Store keeps one entity and its rules (`RegisteredProjectStore`, `DeployRecordStore`). A Storage holds JSON objects by
namespace and key and knows no entity: `FileStorage` keeps them in the person's store, through `store.write_json` only,
and `MemoryStorage` in this process's memory. A namespace is one place of the store behind the seam, by its
`store.PLACES` name; `NAMESPACES` lists them, and `OUTSIDE` names every other place, which every Storage refuses. The
words `namespace`, `key`, `get` and `put` follow LangGraph's `BaseStore`; its label rule is not copied, so every key
passes `store.PLAIN`.
"""

import contextlib
import json
import threading

from spark.records import records_codes
from spark.records import store

# --- MVP ---
PRIVATE, PUBLIC = "private", "public"
#: The store's places behind the seam (P1036).
NAMESPACES = ("registered-projects", "boards")
#: Every other place of the store, refused by every Storage: the grants (a put could make a valid deploy grant), the
#: launcher's text, the history's lines, the kept documents, the downloads, and the places that no Store moved yet.
OUTSIDE = ("sources", "catalog", "downloads", "tools", "drawer", "drawer-import", "shelf", "projects", "history",
           "grants", "known-boards", "launcher", "board-shelf")
#: For tests only: what `MemoryStorage.plant` keeps for an entry that cannot be read, as a folder in a file's place.
UNREADABLE = object()


def privacy_of(namespace):
    """PRIVATE when store.PRIVATE names the served `namespace`, else PUBLIC: the one class of a namespace."""
    require_namespace(namespace)
    return PRIVATE if namespace in store.PRIVATE else PUBLIC


def require_namespace(namespace):
    """ValueError for a namespace outside NAMESPACES. Only spark's code names a namespace, so it is a bug."""
    if namespace not in NAMESPACES:
        raise ValueError("%r is not behind the storage seam: storage.NAMESPACES lists the namespaces" % namespace)


def holds_one_file(namespace):
    """Whether the served `namespace` is one file (it takes the key None) rather than a folder of keys."""
    return store.PLACES[namespace].endswith(".json")


def require_served(namespace, key):
    """What every method checks first: ValueError for a namespace outside the seam or a key that does not fit it (a bug),
    store.StoreError `key_not_plain` for a key that is not plain (a person's input). Nothing is read or written."""
    require_namespace(namespace)
    if (key is None) != holds_one_file(namespace):
        raise ValueError("%r takes %s" % (namespace, "the key None" if holds_one_file(namespace) else "a key"))
    store.require_plain_key(namespace, key)


def parse_object(text, where):
    """The JSON object `text` holds. store.StoreError `record_file_broken` when it holds no JSON or no object."""
    try:
        parsed = json.loads(text)
    except (ValueError, RecursionError) as broken:
        raise store.StoreError("%s is not JSON (%s): fix it by hand", where, broken, code=records_codes.RECORD_FILE_BROKEN)
    if not isinstance(parsed, dict):
        raise store.StoreError("%s is not a JSON object: fix it by hand", where, code=records_codes.RECORD_FILE_BROKEN)
    return parsed


class Storage:
    """
    Strategy: JSON objects by namespace and key, for the Stores. `get` gives None when nothing is there, a new object on
    each call, or store.StoreError (`file_refused`, `record_file_broken`). `put` keeps an object and says whether it
    changed. `keys` lists a folder namespace's keys, `locked()` lets one writer at a time in, and `where` names the place
    in words for a person, never opened. A member gives `_read_text`, `_write`, `_keys`, `_where` and `locked`.
    """

    def get(self, namespace, key=None):
        """The JSON object at `namespace` and `key`, or None when nothing is there."""
        require_served(namespace, key)
        text = self._read_text(namespace, key)
        return None if text is None else parse_object(text, self._where(namespace, key))

    def put(self, namespace, key, value):
        """Keep the dict `value` at `namespace` and `key`, and say whether it changed. TypeError for a value that is no dict."""
        require_served(namespace, key)
        if not isinstance(value, dict):
            raise TypeError("a Storage keeps a JSON object, not %s" % type(value).__name__)
        return self._write(namespace, key, value)

    def keys(self, namespace):
        """The sorted keys of a folder namespace, [] before the first. ValueError for a namespace that is one file."""
        require_namespace(namespace)
        if holds_one_file(namespace):
            raise ValueError("%r is one file and has no keys" % namespace)
        return self._keys(namespace)

    def where(self, namespace, key=None):
        """Words for a person that name the place of `namespace` and `key`. Spark's code never opens them."""
        require_served(namespace, key)
        return self._where(namespace, key)


class FileStorage(Storage):
    """
    Adapter: the person's store as a Storage. It reads the file `store.find_file` names and writes only through
    `store.write_json`, so the git refusal, the 0700 folders, the 0600 files and the unchanged write stay store.py's. Its
    lock is `store.locked()`. It keeps no root: each call asks `store.home()`.
    """

    def _read_text(self, namespace, key):
        path = store.find_file(namespace, key)
        try:
            if not path.exists() and not path.is_symlink():
                return None
            return path.read_text(encoding="utf-8")
        except OSError as cannot:  # a folder in its place, or a file spark may not read
            raise store.StoreError("%s cannot be read (%s): fix it by hand", path, cannot, code=records_codes.FILE_REFUSED)
        except UnicodeDecodeError as broken:
            raise store.StoreError("%s is not UTF-8 text (%s): fix it by hand", path, broken, code=records_codes.RECORD_FILE_BROKEN)

    def _write(self, namespace, key, value):
        return store.write_json(namespace, key, value)

    def _keys(self, namespace):
        return sorted(found.stem for found in store.place(namespace).glob("*.json") if store.PLAIN.fullmatch(found.stem))

    def _where(self, namespace, key):
        return str(store.find_file(namespace, key))

    def locked(self):
        """One writer at a time: the store's one lock, re-entrant in one thread."""
        return store.locked()


class MemoryStorage(Storage):
    """
    Strategy: a Storage in this process's memory, for tests and an in-process run. It keeps the text `write_json` would
    write, so `put` says changed and unchanged as FileStorage does, and it touches no disk, environment or clock. Its
    lock is its own, re-entrant in one thread. `plant` keeps an entry that is broken or cannot be read, for tests.
    """

    def __init__(self):
        self._texts = {}
        self._lock = threading.RLock()

    def plant(self, namespace, key, data=UNREADABLE):
        """For tests only: keep `data` as it is at `namespace` and `key`: a text, bytes, or UNREADABLE."""
        require_served(namespace, key)
        self._texts[(namespace, key)] = data

    def _read_text(self, namespace, key):
        if (namespace, key) not in self._texts:
            return None
        data = self._texts[(namespace, key)]
        if data is UNREADABLE:
            raise store.StoreError("%s cannot be read (planted): fix it by hand", self._where(namespace, key),
                                   code=records_codes.FILE_REFUSED)
        if isinstance(data, bytes):
            try:
                return data.decode("utf-8")
            except UnicodeDecodeError as not_text:
                raise store.StoreError("%s is not UTF-8 text (%s): fix it by hand", self._where(namespace, key), not_text,
                                       code=records_codes.RECORD_FILE_BROKEN)
        return data

    def _write(self, namespace, key, value):
        text = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
        changed = self._texts.get((namespace, key)) != text
        self._texts[(namespace, key)] = text
        return changed

    def _keys(self, namespace):
        return sorted(key for kept, key in self._texts if kept == namespace)

    def _where(self, namespace, key):
        return "memory:%s" % namespace if key is None else "memory:%s/%s" % (namespace, key)

    @contextlib.contextmanager
    def locked(self):
        """One writer at a time in this process, re-entrant in one thread."""
        with self._lock:
            yield
# --- end MVP ---
