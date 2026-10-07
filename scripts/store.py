"""
Where spark keeps what it keeps, and how bytes get there (P88; docs/2026-10-04-store-design.md §6.1).

The person's store is one folder outside every repository: the kept documents, the catalog, the drawer, the
shelf, the history, the projects list, the tools list. Its place was spelled `Path.home() / ".local" / "share" / "spark"` in
two scripts and read once at import, so the suite kept away from the real one only by patching sixteen
constants by hand — and a test that forgot one would have written into the person's store. Now the home is
read on every call: SPARK_HOME, else XDG_DATA_HOME/spark, else ~/.local/share/spark.

This module owns *where* and *how bytes move*; `parts.py` owns what a record must be. It imports only the
standard library.
"""

import contextlib
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import threading
from pathlib import Path

try:
    import fcntl
except ImportError:  # spark installs on macOS and Linux (README); where there is no fcntl, a write takes no lock
    fcntl = None

#: The plugin's own folder: spark's library of parts and boards ships here, read-only.
PLUGIN = Path(__file__).resolve().parent.parent

#: The suite never touches the person's store (P88). A process running unittest gets a scratch one here, at
#: import, whatever SPARK_HOME it inherited (spark's own refusals tell people to set it), and every script it
#: starts inherits the scratch one. A test needing a store of its own patches the environment after import.
#: No script imports unittest — tests/test_store.py proves it — so a real run never takes this branch.
if "unittest" in sys.modules:
    os.environ["SPARK_HOME"] = tempfile.mkdtemp(prefix="spark-suite-")


def home():
    """The store's folder, read from the environment on every call (§6.1)."""
    if os.environ.get("SPARK_HOME"):
        return Path(os.environ["SPARK_HOME"])
    if os.environ.get("XDG_DATA_HOME"):
        return Path(os.environ["XDG_DATA_HOME"]) / "spark"
    return Path.home() / ".local" / "share" / "spark"


#: What lives under the home (§5.1); every path into the store is one of these.
#: `sources`: kept documents (P61, P62a) — ONE store outside the plugin, because a published plugin cannot carry
#: vendor documents; each file under its own checksum, so a record finds it without searching. A record holds the
#: pointer (`documents`), never the file.
#: `catalog`: everything research has read and not chosen (P83) — a candidate keeps its part facts (pinout, power,
#: body, the cited facts: the PO, 2026-10-04) and no seller listings, which go stale before anyone reads them (W21).
PLACES = {"sources": "sources", "catalog": "catalog", "downloads": "downloads", "tools": "tools.json",
          "drawer": "drawer", "drawer-import": "drawer-import", "shelf": "shelf", "projects": "projects.json",
          "history": "history.jsonl"}


def place(name):
    """The path of one of the store's places, under today's home."""
    return home() / PLACES[name]


def layers(kind, library, project=None, drafts=False):
    """
    Where records of one kind are read from, nearest first (§5.5): the project's own, the shelf (parts the person
    chose before, from any project), spark's library, then — only when drafts are asked for — the catalog.
    `library` is the plugin's folder for the kind, which the module that ships it names.
    """
    rows = [("project", Path(project) / kind)] if project else []
    rows += [("shelf", place("shelf"))] if kind == "parts" else []
    rows.append(("library", Path(library)))
    rows += [("catalog", place("catalog"))] if kind == "parts" and drafts else []
    return rows


def records(kind, library, project=None, drafts=False, skip=()):
    """{id: (layer, path)} for every record in every layer, the nearest winning — the one walk (§6.1)."""
    found = {}
    for layer, folder in reversed(layers(kind, library, project, drafts)):
        for path in sorted(folder.glob("*.json")) if folder.is_dir() else []:
            if path.name not in skip:
                found[path.stem] = (layer, path)
    return dict(sorted(found.items()))


#: The places only the person should see (§5.8): files 0600 in folders 0700, and never inside a git work tree,
#: where one `git add .` would publish them.
PRIVATE = ("drawer", "drawer-import", "shelf", "projects", "history")

#: A key names one file inside a place, and only that: lower-case letters, digits and '-'.
PLAIN = re.compile(r"[a-z0-9][a-z0-9-]*")

#: A character spark will not have in a file name it keeps: the C0 controls, DEL and the C1 controls (Unicode's Cc, as
#: `drawer.CONTROL` strips them from a label). A NUL byte is refused by the operating system itself, with an exception
#: nothing catches; a line break in a name breaks every listing that prints it.
CONTROL_CHARACTER = re.compile(r"[\x00-\x1f\x7f-\x9f]")


class StoreProblem(Exception):
    """A store spark cannot read, or a write it will not make. The message is the whole sentence."""


def slug(text):
    """A key made from words (§5.1): lower case, letters and digits joined by '-', at most 60 — never a raw label or SKU."""
    made = re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")[:60].rstrip("-")
    return made or "entry"


def inside_git(path):
    """The git work tree a path is or would be inside, or None — walked up from the path, which need not exist yet."""
    resolved = Path(path).resolve()
    for folder in [resolved, *resolved.parents]:
        if (folder / ".git").exists():
            return folder
    return None


def write_file(path, text, private=False):
    """
    A whole file (§6.1): written to `.part` and renamed, so a write that fails halfway leaves the old file whole and no
    `.part` behind — and only when the bytes differ, so a retried write changes nothing. A private file is 0600, and its
    `.part` is made new at 0600 before it holds a byte. Returns whether it changed.
    """
    path = Path(path)
    if path.is_file() and path.read_text(encoding="utf-8") == text:
        if private:
            os.chmod(path, 0o600)
        return False
    part = path.with_name(path.name + ".part")
    try:
        if private:
            # made new at 0600, so its bytes are never readable by others, not even for a moment — an old `.part` may be looser
            part.unlink(missing_ok=True)
            os.close(os.open(part, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600))
        part.write_text(text, encoding="utf-8")
        part.replace(path)
    except BaseException:
        part.unlink(missing_ok=True)
        raise
    return True


def write_json(name, key, data):
    """
    Put one JSON file into a place (§5.1) and say whether it changed. `key` names the file inside the place (None for a
    place that is itself a file). A private place is written 0600 in 0700 folders, never inside a git work tree.
    """
    target = _target(name, key)
    _make_ready(name, target)
    return write_file(target, json.dumps(data, indent=2, ensure_ascii=False) + "\n", name in PRIVATE)


#: The stores this process holds, as (thread, lock file) pairs: what makes `locked()` re-entrant for the thread that holds one.
_HELD = set()


@contextlib.contextmanager
def locked():
    """
    One writer at a time (§6.1): the store held from a write's plan to its last byte, so two agents writing at once cannot
    each write what the other never read — a part reserved twice, a count lost. The lock is a file in the system's temp
    folder named after this home, never in the store, so it is never a stray file in a repository; the operating system
    lets go of it when its holder exits. A `locked()` inside a `locked()` of the same store, in the same thread, passes
    through and only the outermost lets go: a second `flock` on a second open file would wait behind the first for ever.
    """
    named = hashlib.sha256(str(home().resolve()).encode()).hexdigest()[:16]
    lock_file = Path(tempfile.gettempdir()) / ("spark-%s.lock" % named)
    holder = (threading.get_ident(), lock_file)
    if holder in _HELD:
        yield
        return
    with open(lock_file, "a") as held:
        if fcntl:
            fcntl.flock(held, fcntl.LOCK_EX)
        _HELD.add(holder)
        try:
            yield
        finally:
            _HELD.discard(holder)


def _target(name, key):
    """Where a key goes inside a place (§5.1), refusing a key that is not plain."""
    if key is not None and not PLAIN.fullmatch(key):
        raise StoreProblem("%r is not a plain key — lower-case letters, digits and '-' — so it could leave %s" % (key, name))
    return place(name) / (key + ".json") if key is not None else place(name)


def _make_ready(name, target):
    """Refuse a private target inside git, make its parent folder, and tighten the folders to 0700 (§5.8) — before any bytes move."""
    private = name in PRIVATE
    if private and inside_git(target):
        raise StoreProblem("%s would be inside the git work tree at %s — what you own stays out of every repository; "
                           "point SPARK_HOME at a folder outside it" % (target, inside_git(target)))
    target.parent.mkdir(parents=True, exist_ok=True)
    if private:
        for folder in {home(), target.parent}:
            os.chmod(folder, 0o700)


def copy_folder(name, source, key):
    """Copy a folder into a place under a plain key, as `write_json` writes a file: the same key check and git refusal; in a private place every folder ends 0700 and every file 0600."""
    _target(name, key)  # the key check
    target = place(name) / key
    _make_ready(name, target)
    shutil.copytree(source, target, dirs_exist_ok=True)
    if name in PRIVATE:
        os.chmod(target, 0o700)
        for found in target.rglob("*"):
            os.chmod(found, 0o700 if found.is_dir() else 0o600)


def projects():
    """{name: folder} of the person's projects (§5.5), as /spark:init listed them."""
    path = place("projects")
    if not path.is_file():
        return {}
    try:
        listed = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as broken:
        raise StoreProblem("%s is not JSON (%s) — fix it, or delete it and run /spark:init in each project" % (path, broken))
    if not isinstance(listed, dict) or not all(isinstance(folder, str) for folder in listed.values()):
        raise StoreProblem("%s is not an object of project folders — fix it, or delete it and run /spark:init in each project" % path)
    return {name: Path(folder) for name, folder in listed.items()}


def project_name(folder):
    """The name a project's folder has on the person's list (§5.5), or None when it is not on it."""
    folder = Path(folder).resolve()
    return next((name for name, where in projects().items() if where.resolve() == folder), None)


def add_project(folder, dry_run=False):
    """
    Put a project on the list under its folder's name — `name-2` when another folder that still exists has it. A folder
    already on the list keeps its name, however its path is spelled. Returns the name; a dry run only says it.
    """
    folder = Path(folder).resolve()
    named = project_name(folder)
    if named:
        return named
    listed = {name: str(where) for name, where in projects().items()}
    name, number = folder.name, 2
    while name in listed and Path(listed[name]).is_dir():
        name, number = "%s-%d" % (folder.name, number), number + 1
    listed[name] = str(folder)
    if not dry_run:
        write_json("projects", None, listed)
    return name


#: What makes two history lines one event (§5.7): a line whose key fields equal an earlier one's is not written again.
EVENT_KEYS = {"step": ("project", "step", "session", "start"), "reused": ("project", "need", "part", "board", "entry"),
              "passed_over": ("project", "need", "part", "board", "entry"), "built": ("project", "board", "parts")}


def events():
    """The history (§5.7), every line in order — [] before the first. A line that is not an event is named, never skipped."""
    path = place("history")
    said = []
    # Bytes, not text: str.splitlines() also cuts at U+2028, U+0085 and the like, which a reason may hold unescaped
    # (ensure_ascii=False), and one whole line would read as two broken ones. Bytes cut only at \n, \r and \r\n.
    for number, line in enumerate(path.read_bytes().splitlines() if path.is_file() else [], 1):
        try:
            event = json.loads(line.decode("utf-8"))
        except ValueError:  # not JSON, or not UTF-8 (UnicodeDecodeError is a ValueError)
            event = None
        if not (isinstance(event, dict) and isinstance(event.get("event"), str)):
            raise StoreProblem("%s line %d is not a history event — fix it by hand" % (path, number))
        said.append(event)
    return said


def _last_line_is_open(path):
    """Whether the file's last line has no newline — a hand edit can leave it so, and an append would glue itself onto it."""
    if not path.is_file() or path.stat().st_size == 0:
        return False
    with open(path, "rb") as history:
        history.seek(-1, os.SEEK_END)
        return history.read(1) != b"\n"


def append_event(event):
    """
    One event onto the history (§5.7) — not written when an event with the same key is there. Returns whether it was.
    Looking and appending are two steps, so the caller holds `locked()` across both (`parts.main` does).
    """
    keys = EVENT_KEYS[event["event"]]
    if any(other.get("event") == event["event"] and all(other.get(key) == event.get(key) for key in keys) for other in events()):
        return False
    target = place("history")
    _make_ready("history", target)
    end_last_line = "\n" if _last_line_is_open(target) else ""
    with open(target, "a", encoding="utf-8") as history:
        history.write(end_last_line + json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")
    os.chmod(target, 0o600)
    return True


def fetch(url, method="GET"):
    """
    spark's one door to the network (§6.5): one download — or, with HEAD, only whether the URL answers. Nothing else in
    spark's code opens a URL, and each call is counted from the session's transcript (§6.7). A URL that does not answer is
    a StoreProblem, never empty bytes.
    """
    import urllib.request
    try:
        with urllib.request.urlopen(urllib.request.Request(url, method=method, headers={"User-Agent": "spark"}), timeout=30) as answer:
            return answer.read()
    except Exception as unreachable:  # noqa: BLE001 — every way of not answering is the same answer here
        raise StoreProblem("%s does not answer (%s)" % (url, unreachable))


def file_name_problem(name):
    """
    Why `name` is not a plain file name — one name in the folder it is written to, not a path out of it, and with no
    control character in it — or None when it is one. `keep` refuses such a name; a caller that knows its names before it
    starts (`--fetch` does) asks first, so one bad name stops everything rather than the work half done.
    """
    if Path(name).name != name or name in ("", ".", ".."):
        return "%r is not a file name, so it could leave the store's sources" % name
    if CONTROL_CHARACTER.search(name):
        return "%r has a control character in it, so it is not a file name" % name
    return None


def keep(payload, name):
    """
    The document store's checked keep (§6.2): a file under its checksum, written to `.part`, read back and checked, then
    renamed — what does not match what was fetched is deleted and named, never kept. Returns the checksum. A name that is
    not a plain file name would leave the store's sources, and is refused. A keep that fails for any reason leaves no
    `.part` behind: `--kept` lists a file under `sources` that no record cites yet, so a stray one would read as kept.
    """
    problem = file_name_problem(name)
    if problem:
        raise StoreProblem(problem)
    digest = hashlib.sha256(payload).hexdigest()
    folder = place("sources") / digest
    folder.mkdir(parents=True, exist_ok=True)
    part = folder / (name + ".part")
    try:
        part.write_bytes(payload)
        if hashlib.sha256(part.read_bytes()).hexdigest() != digest:
            raise StoreProblem("%s was not kept: what was written is not what was fetched" % name)
        part.replace(folder / name)
    except BaseException:
        part.unlink(missing_ok=True)
        raise
    return digest
