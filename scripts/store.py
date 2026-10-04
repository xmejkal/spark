"""
Where spark keeps what it keeps, and how bytes get there (P88; docs/2026-10-04-store-design.md §6.1).

The person's store is one folder outside every repository: the kept documents, the catalog, the drawer, the
shelf, the projects list, the tools list. Its place was spelled `Path.home() / ".local" / "share" / "spark"` in
two scripts and read once at import, so the suite kept away from the real one only by patching sixteen
constants by hand — and a test that forgot one would have written into the person's store. Now the home is
read on every call: SPARK_HOME, else XDG_DATA_HOME/spark, else ~/.local/share/spark.

This module owns *where* and *how bytes move*; `parts.py` owns what a record must be. It imports only the
standard library.
"""

import os
import sys
import tempfile
from pathlib import Path

#: The plugin's own folder: spark's library of parts and boards ships here, read-only.
PLUGIN = Path(__file__).resolve().parent.parent

#: The suite never touches the person's store (P88). A process running unittest that names no store of its
#: own gets a scratch one here, at import, and every script it starts inherits it through the environment.
#: No script imports unittest — tests/test_store.py proves it — so a real run never takes this branch.
if "unittest" in sys.modules and not os.environ.get("SPARK_HOME"):
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
          "drawer": "drawer", "drawer-import": "drawer-import", "shelf": "shelf", "projects": "projects.json"}


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
